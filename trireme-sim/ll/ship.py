"""The 170-oar ship: surge + yaw with the physiological crew (Gates 3-4).

States: V (surge), omega (yaw, + = bow to starboard), psi (heading), x, y
(track). Two SideCrews (port/starboard, 85 rowers each) own the oars, the
per-side oar state / pressure from the command language, the stroke plan
(force ceiling + W' endurance -> stroke length / rate), and the W' tanks.

    m_app·dV/dt  = F_oars − D(V)
    I·d(omega)/dt = Q_oar + Q_rudder − Omega·omega·|omega|

Per-side states: row / hold / back / bank; hold = trailing + calibrated 2 %
brake (oQ-4); back = physiology-limited (degenerates to a hold-brake at
speed); rate is ship-global — the pipe — and the keleustes calls down the
rate when one side cannot hold the tempo (weakest side governs).

Hull-side forces are the Taylor ch.31 set (turn-validated): 3-band drag,
straight-rudder drag at midship, applied-rudder drag + lateral force +
torque at helm. Oar yaw torque via the fitted oar-race lever (ll/rig.py).
"""

from __future__ import annotations

import math

from common.chain import KT, RHO, RIGS, VESSELS
from ll.hull import t_drive_for
from ll.oar import simulate
from ll.rig import LEVER_OAR
from ll.rower import HOLD_FRAC as HOLD_FRAC_DEFAULT, PRESSURE, SideCrew

FULL_RUDDER_DEG = 67.5     # "full rudder" in the trials
RUDDER_FAC = 1.4           # Olympias applied-rudder drag factor (W5 set)
LEVER_HOLD = 1.5           # m — yaw arm of the held blades' keel-aligned drag
                           # (mean athwartships oar-station arm; the fitted
                           # 4.8 m thrust lever folds in drift/lateral
                           # dynamics and must NOT apply to the brake —
                           # register C3 refinement)
TEMPO_CALLDOWN_SPM = 2.0   # sustained per-side rate gap that triggers a call-down


class Ship:
    def __init__(self, rig_name: str = "Olympias", n_oars: int = 170,
                 rate: float = 28.8, pressure: tuple = ("spoude", "spoude"),
                 oar_state: tuple = ("row", "row"), helm: tuple = ("midship", 0.0),
                 fleet: str = "spruce", hold_frac: float | None = None):
        # hold_frac default: the calibrated value (ll/rower.HOLD_FRAC)
        """fleet: 'spruce' (all tiers, MIT 9.7 — the 1994 setup) or
        'old-fir' (thranites 13.1, zygians 18.0, thalmians 13.1 approx —
        Table 3.1 tier labels). None: massless oars (pre-Gate-5)."""
        self.rig_name = rig_name
        self.vessel = VESSELS[rig_name]        # Taylor ch.31 parameters
        # The sway-calibrated values (plan 15.3, calibrate_sway.py): the
        # physical oar-race lever (~the athwartships arm — the fitted 4.8 m
        # folded in the lateral dynamics the sway now models explicitly,
        # register C3) and the effective yaw resistance with the physical
        # CLR restoring moment in (register C1). The vessel's own Omega
        # (5e6) and LEVER_OAR (4.8) stay for the steady research model.
        self.lever = 1.8
        self.Omega = 3.2e6
        self.m_app = self.vessel.m_app
        self.I = self.vessel.I
        self.n = n_oars
        self.n_side = n_oars // 2
        self.rate = rate
        self.fleet = fleet
        td, _ = t_drive_for(rig_name, rate)
        self.mit = ({"spruce": 9.7, "old-fir": 14.7, None: 0.0}[fleet]
                    if fleet in ("spruce", "old-fir", None) else 9.7)
        self.crew = {
            "port": SideCrew(rig_name, self.n_side, rate, td,
                             pressure=pressure[0], state=oar_state[0],
                             fleet=fleet,
                             hold_frac=hold_frac if hold_frac is not None else HOLD_FRAC_DEFAULT),
            "star": SideCrew(rig_name, self.n_side, rate, td,
                             pressure=pressure[1], state=oar_state[1],
                             fleet=fleet,
                             hold_frac=hold_frac if hold_frac is not None else HOLD_FRAC_DEFAULT),
        }
        self.helm_dir, self.helm_frac = helm
        self.phi = 0.0          # current rudder angle (signed, + = starboard)
        self.tau_rud = 3.0      # s — the helm build-up: the helmsman's
                                # reaction + the tiller travel (plan 17) [?]
        self.tiller_lever = 0.15  # the rudder's balance: the tiller load =
                                # f_rud x lever (the Olympias rudders were
                                # balanced; [?] — the trials video / Coates
                                # plans would pin it)
        self.helm_force_max = 700.0   # the helmsman's holding force, N —
                                # the rower-strength scale reused (plan 17)
        self.V = 0.0
        self.v = 0.0            # sway (lateral velocity, + = starboard)
        self.omega = 0.0
        self.psi = 0.0
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0
        self._tempo_violation = 0.0
        # the centre of lateral resistance, forward of the CG (m) — the
        # sway-calibrated value (plan 15.3); Coates plans would pin it [?]
        self.clr_offset = 0.8

    # ------------------------------------------------------------------
    def step(self, dt: float) -> None:
        fx_p, peak_p, br_p, fy_p = self.crew["port"].step(dt, self.V)
        fx_s, peak_s, br_s, fy_s = self.crew["star"].step(dt, self.V)
        for crew in self.crew.values():
            crew.end_of_step(dt)
        Fx = self.n_side * (fx_p + fx_s + br_p + br_s)
        Fy_oars = self.n_side * (fy_p + fy_s)             # net lateral oars
        # rowing asymmetry: the physical athwartships arm (C3);
        # held-blade brake: the athwartships station arm (LEVER_HOLD)
        Q_oar = self.n_side * (self.lever * (fx_p - fx_s)
                               + LEVER_HOLD * (br_p - br_s))  # + = starboard
        self._ease_helm(dt)
        # rudder (Taylor ch.31 model; the ACTUAL rudder angle — the helm
        # builds up like a human action, plan 17)
        vkt = abs(self.V) / KT
        if abs(self.phi) < 1e-9:
            rud_drag = self.vessel.rudder_straight * vkt * vkt
            f_rud = 0.0
            Q_rud = 0.0
        else:
            phi_mag = abs(self.phi)
            rud_drag = self.vessel.rudder_drag(vkt, phi_mag, RUDDER_FAC)
            f_rud = self.vessel.rudder_coeff(phi_mag) * rud_drag
            if self.phi < 0:
                f_rud = -f_rud
            Q_rud = f_rud * self.vessel.lever_rudder
        self.hull_advance(dt, Fx, Fy_oars, f_rud, Q_oar + Q_rud, rud_drag)
        self._keleustes(dt)

    def _helm_target(self) -> float:
        """The commanded rudder angle (signed): full rudder = 67.5 deg."""
        if self.helm_dir == "midship":
            return 0.0
        phi = FULL_RUDDER_DEG * self.helm_frac
        return -phi if self.helm_dir == "port" else phi

    def _helm_clamp(self, phi_mag: float) -> float:
        """The helmsman's strength (the rower-strength scale reused): the
        tiller load (f_rud x the rudder's balance lever) cannot exceed his
        holding force — the rudder YIELDS at high speed.
        coeff(phi) = 0.14 + 0.02·phi - 0.00015·phi^2 (Taylor 2.2)."""
        if phi_mag <= 0.0:
            return 0.0
        vkt = abs(self.V) / KT
        K = (self.vessel.rudder_straight * RUDDER_FAC * vkt * vkt
             * self.tiller_lever)
        if K <= 0.0:
            return phi_mag
        target = self.helm_force_max / K
        if target >= 0.806:               # >= coeff(67.5): no clamp
            return phi_mag
        # solve 0.00015·phi^2 - 0.02·phi + (target - 0.14) = 0 (the rising
        # branch of the coeff quadratic, phi in [0, 67.5])
        disc = 0.0004 - 0.0006 * (target - 0.14)
        if disc <= 0.0:
            return 0.0
        return (0.02 - math.sqrt(disc)) / 0.0003

    def _ease_helm(self, dt: float) -> None:
        """The rudder builds up like a human action: the first-order lag
        (the helmsman's reaction + the tiller travel, tau_rud) AND the
        strength clamp (the rudder yields to the water load at speed)."""
        target = self._helm_target()
        clamped = self._helm_clamp(abs(target))
        target = math.copysign(clamped, target)
        self.phi += (target - self.phi) * min(1.0, dt / self.tau_rud)

    def hull_advance(self, dt: float, Fx: float, Fy_oars: float, f_rud: float,
                     Q: float, rud_drag: float) -> None:
        """Integrate the 3-DOF hull state (surge + sway + yaw) from the
        summed forces. The hull's lateral resistance acts at the centre of
        lateral resistance (CLR, forward of the CG): its moment OPPOSES the
        yaw — the physical restoring term the lumped Omega·w^2 cannot
        represent (plan 15.3; register C1). Ship-frame dynamics with the
        centripetal couplings:"""
        u = self.V
        v = self.v
        f_hull = RHO * self.vessel.A_lat * abs(u) * v      # Taylor: rho A_lat u^2 sin(beta)
        q_hull = f_hull * self.clr_offset                  # restoring (+ = starboard)
        drag = self.vessel.hull_drag(abs(u) / KT) + rud_drag
        u_dot = (Fx - drag) / self.m_app + v * self.omega
        v_dot = (Fy_oars + f_rud - f_hull) / self.m_app - u * self.omega
        omega_dot = (Q + q_hull - self.Omega * self.omega * abs(self.omega)) / self.I
        self.V += u_dot * dt
        self.v += v_dot * dt
        self.omega += omega_dot * dt
        self.psi += self.omega * dt
        self.x += (u * math.cos(self.psi) - v * math.sin(self.psi)) * dt
        self.y += (u * math.sin(self.psi) + v * math.cos(self.psi)) * dt
        self.t += dt

    def _keleustes(self, dt: float) -> None:
        """Weakest side governs: if one side cannot hold the tempo for more
        than a couple of cycles, the pipe calls the lower rate on both sides."""
        c_p, c_s = self.crew["port"], self.crew["star"]
        if c_p.state != "row" or c_s.state != "row":
            self._tempo_violation = 0.0
            return
        rp, rs = c_p.rate_eff, c_s.rate_eff
        if abs(rp - rs) > TEMPO_CALLDOWN_SPM:
            self._tempo_violation += dt
            if self._tempo_violation > 2.0 * 60.0 / max(min(rp, rs), 1.0):
                r_new = min(rp, rs)
                td, _ = t_drive_for(self.rig_name, r_new)
                c_p.set_rate(r_new, td)
                c_s.set_rate(r_new, td)
                self.rate = r_new
                self._tempo_violation = 0.0
        else:
            self._tempo_violation = 0.0

    # ------------------------------------------------------------------
    def apply(self, cmd) -> None:
        """Apply one parsed command (commands.parser.Command) to the ship."""
        if cmd.verb == "rate":
            self._set_rate(cmd.args[0])
        elif cmd.verb == "oars":
            state, side = cmd.args
            for s_ in self._sides(side):
                self.crew[s_].set_state(state)
        elif cmd.verb == "pressure":
            level, side = cmd.args
            for s_ in self._sides(side):
                self.crew[s_].set_pressure(level)
        elif cmd.verb == "helm":
            self.helm_dir, self.helm_frac = cmd.args

    @staticmethod
    def _sides(side: str) -> tuple:
        """Map the schema's side names onto the internal keys."""
        return ("port", "star") if side == "both" else (side.replace("starboard", "star"),)

    def _set_rate(self, rate: float) -> None:
        self.rate = rate
        td, _ = t_drive_for(self.rig_name, rate)
        for crew in self.crew.values():
            crew.set_rate(rate, td)

    def run_script(self, commands, dt: float = 0.01, until: float | None = None,
                   V0: float = 0.0) -> None:
        """Run a parsed command stream; commands apply at their timestamps."""
        self.V = V0
        events = list(commands)
        idx = 0
        t_end = until if until is not None else (events[-1].time if events else 0.0) + 1e-6
        while self.t <= t_end:
            while idx < len(events) and events[idx].time <= self.t + 1e-6:
                self.apply(events[idx])
                idx += 1
            self.step(dt)

    # ------------------------------------------------------------------
    def snap(self) -> dict:
        c = {}
        for side, crew in self.crew.items():
            c[side] = dict(state=crew.state, pressure=crew.pressure,
                           rate_eff=crew.rate_eff, W_frac=crew.W_frac,
                           sweep=crew.plan.sweep if crew.plan else 0.0,
                           limited=crew.plan.limited_by if crew.plan else "parked")
        return dict(t=self.t, V=self.V, omega=self.omega, psi=self.psi,
                    x=self.x, y=self.y, rate=self.rate, crew=c,
                    helm=(self.helm_dir, self.helm_frac))


def rate_for_speed(rig_name: str, V_kt: float, pressure: str = "spoude",
                   n_oars: int = 170) -> float:
    """Rate whose rowing oars' mean thrust balances Taylor drag (bare hull +
    straight rudder at midship) at V_kt — the speed-holding rate for turns.
    n_oars: 170 for full-crew turns, 85 for one-side-stops (oar-only turns)."""
    vessel = VESSELS[rig_name]
    V = V_kt * KT

    def dragv(vkt: float) -> float:
        return vessel.hull_drag(vkt) + vessel.rudder_straight * vkt * vkt

    def g(rate: float) -> float:
        td, _ = t_drive_for(rig_name, rate)
        res = simulate(_crew_oar(rig_name, rate, td), V, td / 600, n_cycles=4)
        return n_oars * PRESSURE[pressure] * res["mean_thrust"] - dragv(V_kt)

    lo, hi = 8.0, 50.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _crew_oar(rig_name: str, rate: float, td: float):
    """A bare commanded-kinematics oar for the mean-force equilibrium helpers."""
    from ll.oar import Oar
    return Oar(RIGS[rig_name], rate, td)


def run_turn(ship: Ship, dt: float = 0.01, max_t: float = 900.0,
             target_psi: float = math.pi) -> dict:
    """Run until |psi| >= target_psi (default half-circle); report the turn.

    D = |y| at the target heading — exact for a circle, approximate for a
    decelerating spiral (the trials' crews held thrust, so the turns stayed
    near-circular; the model's D is speed-independent for the rudder term).
    """
    tgt = abs(target_psi)
    while abs(ship.psi) < tgt and ship.t < max_t:
        ship.step(dt)
    sign = 1.0 if ship.omega >= 0 else -1.0
    return dict(D=abs(ship.y), t_turn=ship.t, psi=ship.psi,
                V_end=ship.V / KT, omega=ship.omega * sign,
                track=(ship.x, ship.y))
