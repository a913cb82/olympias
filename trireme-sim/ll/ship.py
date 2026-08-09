"""The 170-oar ship: surge + yaw (Phase 1 Gate 3).

States: V (surge), omega (yaw, + = bow to starboard), psi (heading), x, y
(track). Two oar instances (port/starboard — the pipe keeps the crew in
unison, and backing reverses one side's sweep) summed over 85 oars per side.

    m_app·dV/dt  = F_oars − D(V)
    I·d(omega)/dt = Q_oar + Q_rudder − Omega·omega·|omega|
    d(psi)/dt = omega;   dx/dt = V·cos psi;   dy/dt = V·sin psi

Per-side oar states (command language): row / hold / back / bank; per-side
pressure scales effort. Hold = trailing in v1 (near-zero force — the brake
spectrum is oQ-4); back = reversed sweep at 80 % astern (manoeuvre model 5.x).

Hull-side forces are the Taylor ch.31 set (turn-validated): 3-band drag,
straight-rudder drag at midship, applied-rudder drag + lateral force +
torque at helm. Oar yaw torque via the fitted oar-race lever (ll/rig.py).
The drag law is Taylor's for turns (the F/G domain); the ch.7 155-law is the
speed-power domain (Gate 2) — the two are documented companions, not the same
curve (see uncertainties register B2/C3 discussion).
"""

from __future__ import annotations

import math

from common.chain import CN, KT, RHO, RIGS, VESSELS
from ll.hull import t_drive_for
from ll.oar import Oar, simulate
from ll.rig import LEVER_OAR

# per-side oar states
BACK_FRACTION = 0.8        # astern thrust fraction, force-limited (manoeuvre 5.x)
HOLD_FRAC = 0.02           # hold-water brake fraction of full-square blade drag
                           # (provisional oQ-4 calibration: anchors the tightest
                           # turn 62 m + the "halves speed" observation)
FULL_RUDDER_DEG = 67.5     # "full rudder" in the trials
RUDDER_FAC = 1.4           # Olympias applied-rudder drag factor (W5 set)

# pressure levels: anchors relative to the validated chain (spoude = 1.0);
# endurance semantics arrive with Phase 4 (oQ-13)
PRESSURE = {"rest": 0.0, "steady": 0.7, "fast": 0.85, "spoude": 1.0}


class Ship:
    def __init__(self, rig_name: str = "Olympias", n_oars: int = 170,
                 rate: float = 28.8, pressure: tuple = ("spoude", "spoude"),
                 oar_state: tuple = ("row", "row"), helm: tuple = ("midship", 0.0)):
        self.rig_name = rig_name
        self.vessel = VESSELS[rig_name]        # Taylor ch.31 parameters
        self.lever = LEVER_OAR[rig_name]
        self.m_app = self.vessel.m_app
        self.I = self.vessel.I
        self.Omega = self.vessel.Omega
        self.n = n_oars
        self.n_side = n_oars // 2
        td, _ = t_drive_for(rig_name, rate)
        self.port_oar = Oar(RIGS[rig_name], rate, td, direction=1)
        self.star_oar = Oar(RIGS[rig_name], rate, td, direction=1)
        self.state = {"port": oar_state[0], "star": oar_state[1]}
        self.pressure = {"port": pressure[0], "star": pressure[1]}
        self.helm_dir, self.helm_frac = helm
        self.rate = rate
        self.hold_k = HOLD_FRAC * 0.5 * RHO * RIGS[rig_name]["area"] * CN  # N/(m/s)^2 per oar
        self.V = 0.0
        self.omega = 0.0
        self.psi = 0.0
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0

    # ------------------------------------------------------------------
    def _side_force(self, oar: Oar, dt: float, state: str, level: str) -> float:
        s = oar.step(dt, self.V)
        if state == "bank":                  # out of water: no force
            return 0.0
        if state == "hold":                  # trailing + calibrated brake (oQ-4)
            return -self.hold_k * self.V * abs(self.V)
        mult = PRESSURE[level]
        if state == "back":
            mult = -BACK_FRACTION * mult      # astern, force-limited (manoeuvre 5.x)
        return s.Fx * mult

    def step(self, dt: float) -> None:
        fx_p = self._side_force(self.port_oar, dt, self.state["port"], self.pressure["port"])
        fx_s = self._side_force(self.star_oar, dt, self.state["star"], self.pressure["star"])
        Fx = self.n_side * (fx_p + fx_s)
        Q_oar = self.n_side * self.lever * (fx_p - fx_s)      # + = starboard
        # rudder (Taylor ch.31 model; straight-rudder drag at midship)
        vkt = abs(self.V) / KT
        if self.helm_dir == "midship":
            rud_drag = self.vessel.rudder_straight * vkt * vkt
            Q_rud = 0.0
        else:
            phi = FULL_RUDDER_DEG * self.helm_frac
            rud_drag = self.vessel.rudder_drag(vkt, phi, RUDDER_FAC)
            Q_rud = self.vessel.rudder_coeff(phi) * rud_drag * self.vessel.lever_rudder
            if self.helm_dir == "port":
                Q_rud = -Q_rud
        drag = self.vessel.hull_drag(vkt) + rud_drag
        # integrate
        self.V += (Fx - drag) / self.m_app * dt
        self.omega += (Q_oar + Q_rud - self.Omega * self.omega * abs(self.omega)) / self.I * dt
        self.psi += self.omega * dt
        self.x += self.V * math.cos(self.psi) * dt
        self.y += self.V * math.sin(self.psi) * dt
        self.t += dt

    def apply(self, cmd) -> None:
        """Apply one parsed command (commands.parser.Command) to the ship."""
        if cmd.verb == "rate":
            self._set_rate(cmd.args[0])
        elif cmd.verb == "oars":
            state, side = cmd.args
            for s_ in self._sides(side):
                self.state[s_] = state
        elif cmd.verb == "pressure":
            level, side = cmd.args
            for s_ in self._sides(side):
                self.pressure[s_] = level
        elif cmd.verb == "helm":
            self.helm_dir, self.helm_frac = cmd.args

    @staticmethod
    def _sides(side: str) -> tuple:
        """Map the schema's side names onto the internal keys."""
        return ("port", "star") if side == "both" else (side.replace("starboard", "star"),)

    def _set_rate(self, rate: float) -> None:
        self.rate = rate
        td, _ = t_drive_for(self.rig_name, rate)
        for oar, side in ((self.port_oar, "port"), (self.star_oar, "star")):
            self._replace_oar(oar, side, rate, td)

    def _replace_oar(self, oar: Oar, side: str, rate: float, td: float) -> None:
        direction = oar.dir
        new = Oar(RIGS[self.rig_name], rate, td, direction=direction)
        if side == "port":
            self.port_oar = new
        else:
            self.star_oar = new

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
        return dict(t=self.t, V=self.V, omega=self.omega, psi=self.psi,
                    x=self.x, y=self.y, rate=self.rate,
                    state=dict(self.state), pressure=dict(self.pressure),
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
        res = simulate(Oar(RIGS[rig_name], rate, td), V, td / 600, n_cycles=4)
        return n_oars * PRESSURE[pressure] * res["mean_thrust"] - dragv(V_kt)

    lo, hi = 8.0, 50.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def run_turn(ship: Ship, dt: float = 0.01, max_t: float = 900.0,
             target_psi: float = math.pi) -> dict:
    """Run until |psi| >= target_psi (default half-circle); report the turn.

    D = 2·|y| at the target heading — exact for a circle, approximate for a
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
