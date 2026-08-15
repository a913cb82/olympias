"""The fast high-level ship (plan §19, HL).

The whole simulator in one class. State: V, omega, psi, x, y, rate,
per-side pressure / oar state, helm, one W' tank. Dynamics:

  rowing    V chases the calibrated equilibrium with a first-order lag;
            one side stopped -> the (row, hold) equilibrium (the held
            blades' brake bites hard, ~3.7 kt, measured).
  not rowing  exact drag law: dV/dt = -(D(V) + held-blade brake)/m_app
            (rest/bank decay; hold/back brake — same ODE as the LL).
  yaw       omega chases 2V/D with a first-order lag; D from the
            calibrated families (rudder, or one-side-hold/back).
  crew      one W' tank: drains above P_crit, refills with tau; at zero
            the chase target drops to the P_crit ceiling.

Command API mirrors ll/ship.py exactly (apply / step / run_script / snap)
so the Phase-3 harness runs both simulators identically.

Known HL-loose spots (the honesty contract, plan §20): stroke ripple and
within-cycle force phase; per-side W' (one shared tank); exhausted-side
yaw drift; sway/drift in turns (folded into the calibrated D); tempo loss
(rate_eff = rate always); the applied-rudder drag (only its effect on the
turn diameter is in). Each is re-visited only if a gate proves it.
"""

from __future__ import annotations

import math

from common.chain import KT, VESSELS
from hl.curves import default
from ll.ship import RUDDER_FAC

OTHER = {"port": "star", "star": "port"}
HELM_SIDES = {"port": "port", "starboard": "star", "midship": "midship"}
DEFAULT_DT = 0.5          # plan §4: 0.5-1 s step


class Ship:
    def __init__(self, rig_name: str = "Olympias", n_oars: int = 170,
                 rate: float = 28.8, pressure=("spoude", "spoude"),
                 oar_state=("row", "row"), helm=("midship", 0.0),
                 fleet: str = "spruce", curves=None, dt: float = DEFAULT_DT):
        if rig_name != "Olympias":
            raise NotImplementedError(
                f"HL v1 supports the Olympias rig only ({rig_name})")
        self.curves = curves if curves is not None else default()
        self.vessel = VESSELS[rig_name]
        self.m_app = self.vessel.m_app
        self.n_side = n_oars // 2
        self.rate = rate
        self.pressure = {"port": pressure[0], "star": pressure[1]}
        self.oar_state = {"port": oar_state[0], "star": oar_state[1]}
        self.helm_dir, self.helm_frac = HELM_SIDES[helm[0]], float(helm[1])
        self.fleet = fleet          # stored; the bootstrap V* is the spruce LL
        self.dt = dt
        self.V = 0.0
        self.omega = 0.0
        self.psi = 0.0
        self.x = 0.0
        self.y = 0.0
        self.t = 0.0
        self.W = self.curves.w_max
        self.W_max = self.curves.w_max
        self.W_frac = 1.0

    # ------------------------------------------------------------------
    def step(self, dt: float) -> None:
        c = self.curves
        rowing = [s for s in ("port", "star")
                  if self.oar_state[s] == "row"
                  and c.resolve_pressure(self.pressure[s]) > 0.0
                  and self.rate > 0.5]

        # -- surge -----------------------------------------------------
        if rowing:
            p_eff = min(c.resolve_pressure(self.pressure[s]) for s in rowing)
            empty = self.W <= 0.0
            if len(rowing) == 2:
                vstar = c.vstar(self.rate, p_eff, empty)
            else:
                stopped = OTHER[rowing[0]]
                vstar = c.vasym(self.rate, p_eff, self.oar_state[stopped],
                                empty)
            self.V += (vstar - self.V) / c.tau_surge * dt
            # the applied rudder drag the chase target cannot know (the
            # calibrated V* rows are no-rudder equilibria): the LL loses
            # ~2 kt in a full-helm turn, the HL must too (harness finding)
            if (self.helm_dir != "midship" and self.helm_frac > 0.0
                    and self.V > 0.0):
                a_rud = ((RUDDER_FAC - 1.0) * self.vessel.rudder_straight
                         * (self.V / KT) ** 2 / self.m_app)
                self.V = max(0.0, self.V - a_rud * dt)
        else:
            vkt = abs(self.V) / KT
            rud_fac = RUDDER_FAC if (self.helm_dir != "midship"
                                     and self.helm_frac > 0.0) else 1.0
            drag = (self.vessel.hull_drag(vkt)
                    + rud_fac * self.vessel.rudder_straight * vkt * vkt)
            held = [s for s in ("port", "star")
                    if self.oar_state[s] in ("hold", "back")]
            if held and self.V > 0.0:
                drag += len(held) * self.n_side * c.hold_k * self.V * self.V
            a = -drag / self.m_app
            if a * dt <= -self.V:        # stop at rest; no reversal
                self.V = 0.0
            else:
                self.V += a * dt

        # -- yaw --------------------------------------------------------
        asym = [s for s in ("port", "star")
                if self.oar_state[s] in ("hold", "back")
                and self.oar_state[OTHER[s]] == "row"]
        if asym:
            side = asym[0]
            sign = 1.0 if side == "star" else -1.0     # turn toward the held side
            frac = self.helm_frac if self.helm_dir == side else 0.0
            wss = sign * 2.0 * self.V / c.d_oar(frac)
        elif self.helm_dir != "midship" and self.helm_frac > 0.0:
            sign = 1.0 if self.helm_dir == "star" else -1.0
            wss = sign * 2.0 * self.V / c.d_rudder(self.helm_frac)
        else:
            wss = 0.0
        self.omega += (wss - self.omega) / c.tau_turn * dt

        # -- crew tank ---------------------------------------------------
        # net = the measured drain/refill (W/man) at the anchor levels;
        # the refill is capped at W_max/tau as in the LL
        if rowing:
            net = c.net(self.rate, p_eff)
            if net > 0.0:
                self.W = max(0.0, self.W - net * dt)
            else:
                self.W = min(self.W_max, self.W + min(-net,
                                                      self.W_max / c.tau_w) * dt)
        else:
            self.W = min(self.W_max, self.W + min(c.p_crit,
                                                  self.W_max / c.tau_w) * dt)
        self.W_frac = self.W / self.curves.w_max

        # -- position ----------------------------------------------------
        self.psi += self.omega * dt
        self.x += self.V * math.cos(self.psi) * dt
        self.y += self.V * math.sin(self.psi) * dt
        self.t += dt

    # ------------------------------------------------------------------
    def apply(self, cmd) -> None:
        """Apply one parsed command (commands.parser.Command) to the ship."""
        if cmd.verb == "rate":
            self.rate = cmd.args[0]
        elif cmd.verb == "oars":
            state, side = cmd.args
            for s in self._sides(side):
                self.oar_state[s] = state
        elif cmd.verb == "pressure":
            level, side = cmd.args
            for s in self._sides(side):
                self.pressure[s] = level
        elif cmd.verb == "helm":
            direction, fraction = cmd.args
            self.helm_dir = HELM_SIDES[direction]
            self.helm_frac = float(fraction)

    @staticmethod
    def _sides(side: str) -> tuple:
        return ("port", "star") if side == "both" \
            else (HELM_SIDES[side],)

    def run_script(self, commands, dt: float | None = None,
                   until: float | None = None, V0: float = 0.0) -> None:
        """Run a parsed command stream; commands apply at their timestamps."""
        self.V = V0
        events = list(commands)
        idx = 0
        dt = self.dt if dt is None else dt
        t_end = until if until is not None \
            else (events[-1].time if events else 0.0) + 1e-6
        while self.t <= t_end:
            while idx < len(events) and events[idx].time <= self.t + 1e-6:
                self.apply(events[idx])
                idx += 1
            self.step(dt)

    # ------------------------------------------------------------------
    def snap(self) -> dict:
        crew = {}
        for side in ("port", "star"):
            crew[side] = dict(state=self.oar_state[side],
                              pressure=self.pressure[side],
                              rate_eff=self.rate, W_frac=self.W_frac,
                              limited="none")
        return dict(t=self.t, V=self.V, omega=self.omega, psi=self.psi,
                    x=self.x, y=self.y, rate=self.rate, crew=crew,
                    helm=(self.helm_dir, self.helm_frac),
                    calibration=self.curves.meta["id"])
