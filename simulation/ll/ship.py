"""The 170-oar ship: surge + sway + yaw with the physiological crew (Gates 3-4).

States: V (surge), omega (yaw, + = bow to port), psi (heading), x, y
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

from common.chain import (
    CLR_OFFSET_REAL,
    KT,
    OMEGA_CROSSFLOW,
    RHO,
    RIGS,
    VESSELS,
    hull_power,
)

from ll.hull import t_drive_for
from ll.oar import simulate
from ll.rower import HOLD_FRAC as HOLD_FRAC_DEFAULT
from ll.rower import PRESSURE, SideCrew

FULL_RUDDER_DEG = 67.5  # "full rudder" in the trials
RUDDER_FAC = 1.4  # Olympias applied-rudder drag factor (W5 set)
LEVER_HOLD = 1.5  # m — yaw arm of the held blades' keel-aligned drag
# (mean athwartships oar-station arm; the fitted
# 4.8 m thrust lever folds in drift/lateral
# dynamics and must NOT apply to the brake —
# register C3 refinement)
TEMPO_CALLDOWN_SPM = 2.0  # sustained per-side rate gap that triggers a call-down


class Ship:
    def __init__(
        self,
        rig_name: str = "Olympias",
        n_oars: int = 170,
        rate: float = 28.8,
        pressure: tuple = ("spoude", "spoude"),
        oar_state: tuple = ("row", "row"),
        helm: tuple = ("midship", 0.0),
        fleet: str = "spruce",
        hold_frac: float | None = None,
        stations: bool = False,
        force: bool = True,
    ):
        # hold_frac default: the calibrated value (ll/rower.HOLD_FRAC)
        """fleet: 'spruce' (all tiers, MIT 9.7 — the 1994 setup) or
        'old-fir' (thranites 13.1, zygians 18.0, thalmians 13.1 approx —
        Table 3.1 tier labels). None: massless oars (pre-Gate-5).

        force: the PROMOTED default (Stream A, P1.6 — the force-driven
        oar): the stroke emerges from the rower's demand + the oar's
        inertia + the blade's water force; the timing schedule becomes
        validation anchors. The kinematic commanded-kinematics mode
        (force=False) stays as the labelled reference layer (the
        per-station layer ll/stations.py is kinematic-only — its tests
        pass force=False explicitly)."""
        self.rig_name = rig_name
        self.vessel = VESSELS[rig_name]  # Taylor ch.31 parameters
        # The grounded hull (Stream C B1/B3): A_lat, J, Omega, m_app and Iz
        # are now from the real Lines Plan (basis_hull_offsets.tsv, LWL
        # 32.35 m, trial WL 1.10 m). The parametric hull_form (p=1.5,q=0.8)
        # is deleted; the fitted 4.8 m lever is decomposed to the physical
        # 1.8 m athwartships arm (register C3) and the sway-calibrated
        # CLR restoring moment is now the computed x_clr−x_cg.
        self.lever = 1.8
        # Omega: the grounded cross-flow pure-rotation moment
        # (common.chain.OMEGA_REAL = ½·rho·0.27·J_REAL, J=23217 at trial WL,
        # x_cg at LCB 15.67 m; C_D 0.27 is the lower edge of the 0.30–0.60
        # drag-crisis band, rectangular vs tapered reconciliation, DECODE C9).
        # The parametric 3.25e6 at C_D 0.30 (=1.6% from fitted 3.20e6) is the
        # documented reference in the register.
        self.Omega = OMEGA_CROSSFLOW
        self.m_app = self.vessel.m_app
        self.I = self.vessel.I
        self.n = n_oars
        self.n_side = n_oars // 2
        self.rate = rate
        self.fleet = fleet
        td, _ = t_drive_for(rig_name, rate)
        self.mit = (
            {"spruce": 9.7, "old-fir": 14.7, None: 0.0}[fleet]
            if fleet in ("spruce", "old-fir", None)
            else 9.7
        )
        # the per-station layer (ll/stations.py — the Rev F A1 item):
        # 170 oars at their stations, the yaw moment from the per-oar
        # sums with the local (u, v, r) flow; swappable, the aggregated
        # validated default stays
        self.stations = stations
        side_layout = None
        if stations:
            from ll.stations import station_layout

            base = station_layout()
            side_layout = {
                "port": {t: [(x, y, s) for x, y, s in base[t]] for t in base},
                "star": {t: [(x, -y, s) for x, y, s in base[t]] for t in base},
            }
        self.crew = {
            "port": SideCrew(
                rig_name,
                self.n_side,
                rate,
                td,
                pressure=pressure[0],
                state=oar_state[0],
                fleet=fleet,
                hold_frac=hold_frac if hold_frac is not None else HOLD_FRAC_DEFAULT,
                stations=side_layout and side_layout["port"],
                side=1,
                force=force,
            ),
            "star": SideCrew(
                rig_name,
                self.n_side,
                rate,
                td,
                pressure=pressure[1],
                state=oar_state[1],
                fleet=fleet,
                hold_frac=hold_frac if hold_frac is not None else HOLD_FRAC_DEFAULT,
                stations=side_layout and side_layout["star"],
                side=-1,
                force=force,
            ),
        }
        # cached refs — the per-step hot path (the dict stays for the
        # command-application API)
        self.crew_p, self.crew_s = self.crew["port"], self.crew["star"]
        self.helm_dir, self.helm_frac = helm
        # The hull's drag: the trial-validated chain law
        # W = 155V^3 + 4.13V^5 (V in m/s) — the tank-tested Grekoussis &
        # Loukakis power law the whole chain closes on.
        self.V = 0.0
        self.v = 0.0  # sway (lateral velocity, + = port)
        self.omega = 0.0
        self.psi = 0.0
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0
        self._tempo_violation = 0.0
        # The centre of lateral resistance, forward of the CG (m) — now
        # grounded: x_clr 16.60 m from AP at trial WL 1.10 (real hull
        # Simpson), x_cg at LCB 15.67 m (even keel) => 0.93 m forward.
        # The fitted 0.8 m (calibrate_sway.py) is the documented reference.
        self.clr_offset = CLR_OFFSET_REAL

    # ------------------------------------------------------------------
    def step(self, dt: float) -> None:
        ship_state = (self.v, self.omega) if self.stations else None
        fx_p, _peak_p, br_p, fy_p = self.crew_p.step(dt, self.V, ship_state)
        fx_s, _peak_s, br_s, fy_s = self.crew_s.step(dt, self.V, ship_state)
        self.crew_p.end_of_step(dt)
        self.crew_s.end_of_step(dt)
        Fx = self.n_side * (fx_p + fx_s + br_p + br_s)
        if self.stations:
            # the per-station sums: the yaw moment and the lateral force
            # emerge from the per-oar sums at the BLADE positions (the
            # oar and the rower are internal to the hull — the net
            # moment is r_blade x F) with the local (u, v, r) flow
            Fy_oars = 0.0
            Q_oar = 0.0
            for crew in (self.crew_p, self.crew_s):
                for fxi, fyi, bri, x_b, y_b in crew._stations:
                    Fy_oars += fyi
                    Q_oar += x_b * fyi - y_b * fxi - y_b * bri
        else:
            Fy_oars = self.n_side * (fy_p + fy_s)  # net lateral oars
            # rowing asymmetry: the physical athwartships arm (C3);
            # held-blade brake: the athwartships station arm (LEVER_HOLD)
            Q_oar = self.n_side * (
                self.lever * (fx_s - fx_p) + LEVER_HOLD * (br_s - br_p)
            )  # + = port (psi +)
        # rudder (Taylor ch.31 model; straight-rudder drag at midship)
        vkt = abs(self.V) / KT
        if self.helm_dir == "midship":
            rud_drag = self.vessel.rudder_straight * vkt * vkt
            f_rud = 0.0
            Q_rud = 0.0
        else:
            phi = FULL_RUDDER_DEG * self.helm_frac
            rud_drag = self.vessel.rudder_drag(vkt, phi, RUDDER_FAC)
            f_rud = self.vessel.rudder_coeff(phi) * rud_drag
            if self.helm_dir == "starboard":
                f_rud = -f_rud
            Q_rud = f_rud * self.vessel.lever_rudder
        self.hull_advance(dt, Fx, Fy_oars, f_rud, Q_oar + Q_rud, rud_drag)
        self._keleustes(dt)

    def hull_advance(
        self,
        dt: float,
        Fx: float,
        Fy_oars: float,
        f_rud: float,
        Q: float,
        rud_drag: float,
    ) -> None:
        """Integrate the 3-DOF hull state (surge + sway + yaw) from the
        summed forces. The hull's lateral resistance acts at the centre of
        lateral resistance (CLR, forward of the CG): its moment OPPOSES the
        yaw — the physical restoring term the lumped Omega·w^2 cannot
        represent (register C1). Ship-frame dynamics with the centripetal
        couplings:"""
        u = self.V
        v = self.v
        f_hull = RHO * self.vessel.A_lat * abs(u) * v  # Taylor: rho A_lat u^2 sin(beta)
        q_hull = f_hull * self.clr_offset  # restoring (+ = port)
        omega_drag = self.Omega * self.omega * abs(self.omega)
        v_dot = (Fy_oars + f_rud - f_hull) / self.m_app - u * self.omega
        omega_dot = (Q + q_hull - omega_drag) / self.I
        abs(u) / KT
        drag = hull_power(abs(u)) / max(abs(u), 1e-6)
        drag += rud_drag
        u_dot = (Fx - drag) / self.m_app + v * self.omega
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
        c_p, c_s = self.crew_p, self.crew_s
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
        return (
            ("port", "star") if side == "both" else (side.replace("starboard", "star"),)
        )

    def _set_rate(self, rate: float) -> None:
        self.rate = rate
        td, _ = t_drive_for(self.rig_name, rate)
        for crew in self.crew.values():
            crew.set_rate(rate, td)

    def run_script(
        self, commands, dt: float = 0.02, until: float | None = None, V0: float = 0.0
    ) -> None:
        """Run a parsed command stream; commands apply at their timestamps."""
        self.V = V0
        events = list(commands)
        idx = 0
        t_end = (
            until if until is not None else (events[-1].time if events else 0.0) + 1e-6
        )
        while self.t <= t_end:
            while idx < len(events) and events[idx].time <= self.t + 1e-6:
                self.apply(events[idx])
                idx += 1
            self.step(dt)

    # ------------------------------------------------------------------
    def snap(self) -> dict:
        c = {}
        for side, crew in self.crew.items():
            c[side] = {
                "state": crew.state,
                "pressure": crew.pressure,
                "rate_eff": crew.rate_eff,
                "W_frac": crew.W_frac,
                "sweep": crew.plan.sweep if crew.plan else 0.0,
                "limited": crew.plan.limited_by if crew.plan else "parked",
            }
        return {
            "t": self.t,
            "V": self.V,
            "omega": self.omega,
            "psi": self.psi,
            "x": self.x,
            "y": self.y,
            "rate": self.rate,
            "crew": c,
            "helm": (self.helm_dir, self.helm_frac),
        }


_RATE_LAST: dict[tuple, tuple[float, float]] = {}


def rate_for_speed(
    rig_name: str, V_kt: float, pressure: str = "spoude", n_oars: int = 170
) -> float:
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

    key = (rig_name, pressure, n_oars)
    lo, hi = 8.0, 50.0
    n_iter = 50
    if key in _RATE_LAST:
        prev_V, prev_rate = _RATE_LAST[key]
        if abs(V_kt - prev_V) < 2.0:
            lo = max(8.0, prev_rate - 6.0)
            hi = min(50.0, prev_rate + 6.0)
            if g(lo) < 0:
                lo = 8.0
            if g(hi) > 0:
                hi = 50.0
            n_iter = 35
    for _ in range(n_iter):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            hi = mid
        else:
            lo = mid
    rate = 0.5 * (lo + hi)
    _RATE_LAST[key] = (V_kt, rate)
    return rate


def _crew_oar(rig_name: str, rate: float, td: float):
    """A bare commanded-kinematics oar for the mean-force equilibrium helpers."""
    from ll.oar import Oar

    return Oar(RIGS[rig_name], rate, td)


def run_turn(
    ship: Ship, dt: float = 0.02, max_t: float = 900.0, target_psi: float = math.pi
) -> dict:
    """Run until |psi| >= target_psi (default half-circle); report the turn.

    D = |y| at the target heading — exact for a circle, approximate for a
    decelerating spiral (the trials' crews held thrust, so the turns stayed
    near-circular; the model's D is speed-independent for the rudder term).
    """
    tgt = abs(target_psi)
    while abs(ship.psi) < tgt and ship.t < max_t:
        ship.step(dt)
    sign = 1.0 if ship.omega >= 0 else -1.0
    return {
        "D": abs(ship.y),
        "t_turn": ship.t,
        "psi": ship.psi,
        "V_end": ship.V / KT,
        "omega": ship.omega * sign,
        "track": (ship.x, ship.y),
    }
