"""The fast high-level ship (the calibration protocol (simulation/AGENTS.md), HL).

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

Known HL-loose spots (the honesty contract, the harness — simulation/AGENTS.md): stroke ripple and
within-cycle force phase; per-side W' (one shared tank); exhausted-side
rate call-down; sway in turns (folded into the calibrated D); tempo loss
(rate_eff = the measured empty-tank curve); the applied-rudder drag
(only its effect on the turn diameter is in). The straight-cruise drift
bias is measured (task C) — the HL carries it like the LL's untrimmed
ship. Each loose spot is re-visited only if a gate proves it.
"""

from __future__ import annotations

import math

from common.chain import KT, VESSELS
from hl.curves import default
from ll.ship import RUDDER_FAC

OTHER = {"port": "star", "star": "port"}
HELM_SIDES = {"port": "port", "starboard": "star", "midship": "midship"}
DEFAULT_DT = 0.5          # the HL design (simulation/AGENTS.md): 0.5-1 s step


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
        self.W = {"port": self.curves.w_max, "star": self.curves.w_max}
        self.W_max = self.curves.w_max
        self.W_frac = 1.0
        self.rate_eff = rate
        self._wss_prev = 0.0       # the previous turn target (release detect)
        self._exit_omega = 0.0     # the fishtail's decaying yaw rate
        self._yb_delay = 0.0       # the yaw-build's S-shape delay (K26)
        self._v_prev = 0.0         # the previous V (the ramp detect)

    # ------------------------------------------------------------------
    def step(self, dt: float) -> None:
        c = self.curves
        rowing = [s for s in ("port", "star")
                  if self.oar_state[s] == "row"
                  and c.resolve_pressure(self.pressure[s]) > 0.0
                  and self.rate > 0.5]

        # -- surge -----------------------------------------------------
        p_eff = min(c.resolve_pressure(self.pressure[s]) for s in rowing) \
            if rowing else 0.0
        if rowing:
            empty = self.W[rowing[0]] <= 0.0
            # the achieved rate: the exhausted crew loses tempo at high
            # rates (the LL's rower.py tempo branch — measured curve);
            # the chase and the tank net evaluate at the achieved rate,
            # exactly as the LL's equilibrium does
            r_eff = c.rate_eff(self.rate, empty)
            self.rate_eff = r_eff
            if len(rowing) == 2:
                vstar = c.vstar(r_eff, p_eff, empty)
                tau = c.tau_surge
            else:
                stopped = OTHER[rowing[0]]
                # the per-state lag (task E): the one-side-stopped decays
                # measured separately — the back collapse at low rate
                # (cruise_turn 1440 s bin) is much slower than the chase.
                # The back's FRESH phase decays like the hold (the
                # degeneration — the identical V/W traces, K22); the slow
                # tau_back applies only in the drained state (the K13
                # low-speed context)
                if self.oar_state[stopped] == "back" and empty:
                    # the drained decay: the power-limited COLLAPSE is
                    # fast above v_collapse (the oar-back's ~12-s drop
                    # after the tank empties); the low-speed drift below
                    # is the slow measured tau_back (the cruise_turn's
                    # 1440-s bin context, K13)
                    if self.V > c.v_collapse * KT:
                        tau = c.tau_hold(self.rate)
                    else:
                        tau = c.tau_back(self.rate)
                else:
                    tau = c.tau_hold(self.rate)
                vstar = c.vasym(r_eff, p_eff, self.oar_state[stopped],
                                empty)
            self.V += (vstar - self.V) / tau * dt
            # the applied rudder drag the chase target cannot know (the
            # calibrated V* rows are no-rudder equilibria): the LL loses
            # ~2 kt in a full-helm turn, the HL must too (harness
            # finding); turn_drag(frac) (task F -> T4) is the measured
            # sway-coupled residual the exact drag law misses, per helm
            # fraction (the LL's loss is nonlinear in helm)
            if (self.helm_dir != "midship" and self.helm_frac > 0.0
                    and self.V > 0.0):
                a_rud = ((RUDDER_FAC - 1.0)
                         + c.turn_drag(self.helm_frac, p_eff, r_eff)) \
                    * self.vessel.rudder_straight * (self.V / KT) ** 2 \
                    / self.m_app
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
            sign = -1.0 if side == "star" else 1.0    # turn toward the held side
            frac = self.helm_frac if self.helm_dir == side else 0.0
            # the oar-only turns (no helm) chase the measured speed-
            # dependent orbit (K22: the drained spiral — the LL's orbit
            # shrinks ~linearly with V); the helm-frac oar turns keep
            # the fixed d_oar cell (the rudder-dominated tightest)
            d = c.d_oar_v(self.V) if frac <= 0.0 else c.d_oar(frac)
            # the pressure scaling (the K27): the LL's oar-turn orbit
            # grows as the rowing side's effort falls (the measured
            # ~1/p_row — the weaker drive, the slower V, the larger
            # orbit — 1.36-1.38x at the steady rows vs 1/0.7); the
            # spoude-measured d_oar_v would run the cruise's
            # steady-rowed legs ~1.4x too tight
            if frac <= 0.0:
                if (self.helm_frac > 0.0 and self.helm_dir != "midship"
                        and self.oar_state[side] == "hold"):
                    # the mixed hold (the K28): the helm + the OPPOSITE-
                    # side hold — the LL's turn is the HELM's (the rudder
                    # dominates at speed, the hold's brake only widens
                    # the orbit — the measured d_mixed_hold family); the
                    # oar-only family would turn the wrong way
                    hs = -1.0 if self.helm_dir == "star" else 1.0
                    wss = hs * 2.0 * self.V / c.d_mixed_hold(self.V)
                else:
                    wss = sign * 2.0 * self.V * max(p_eff, 0.1) / d
            else:
                wss = sign * 2.0 * self.V / d
        elif self.helm_dir != "midship" and self.helm_frac > 0.0:
            sign = -1.0 if self.helm_dir == "star" else 1.0
            wss = sign * 2.0 * self.V / c.d_rudder(self.helm_frac)
        else:
            wss = 0.0
        turn_target = wss
        # the untrimmed lateral kick (task C): the LL's symmetric crew
        # carries a measured yaw bias — the HL carries it too, so the
        # position gate stays as-written (§21.3 decision). Not applied in
        # the one-side-stopped state (the oar-family D absorbs it).
        if rowing and not asym:
            drift = c.drift_bias(self.rate, p_eff, self.W_frac)
            # the V-ramp kick-transient (the wprime closure): while the
            # V is rising fast the LL's yaw rides below its settled
            # drift (the sway's excited state — measured curve); the
            # target floor applies during the ramp, then the slow
            # decay-side (below) relaxes it to the settle
            if self.V > 0.5 and (self.V - self._v_prev) / dt > 0.02:
                drift = min(drift, c.drift_kick(self.V))
            wss += drift
        # the fishtail (the sprint_turn follow-up): at the moment the turn
        # target disappears (the helm release), the LL keeps turning — the
        # sway-coupled exit decays slowly (measured tau_exit); the capture
        # is the yaw rate at the release, decayed in parallel, while the
        # drift build-up itself keeps the fast tau_turn
        if self._wss_prev != 0.0 and turn_target == 0.0:
            self._exit_omega = self.omega
        prev_target = self._wss_prev          # the delay trigger's reference
        self._wss_prev = turn_target
        if self._exit_omega:
            self._exit_omega *= math.exp(-dt / c.tau_exit)
            wss += self._exit_omega
            if abs(self._exit_omega) < 1e-4:
                self._exit_omega = 0.0
        # the sway's slow mode (the wprime closure): the LL's yaw rises
        # fast with the kick (tau_turn) but decays slowly to its drift
        # equilibrium — the measured |omega|-dependent tau: the turn-
        # scale fishtail (tau_exit, 19 s at ~0.1 rad/s) to the drift-
        # scale decay (the burst-path fit: ~50 s at ~0.001 rad/s):
        # tau = tau_exit * (0.1/|omega|)^drift_tau_exp (measured in
        # calibrate.measure_drift_tau). The slow side applies only at
        # the drift scale (|omega| < 0.005) — the turn-scale decay is
        # the capture's job (the double-decay overshoots the fishtail).
        # The turn APPROACH is also two-timescale (task T3): the fast
        # share A at the chase's tau, then the sway-coupled slow tail
        # (the measured yaw_build families — the HL's single-tau build
        # phased the turn's psi early and accumulated in the position
        # rows, the K16 finding)
        if (abs(wss) < abs(self.omega) * 0.99
                and abs(self.omega) < 0.005):
            tau_yaw = c.tau_exit * (0.1 / max(abs(self.omega), 1e-4)) \
                ** c.drift_tau_exp
        else:
            b = c.yaw_build(self.helm_frac, bool(asym))
            # the S-shape's delay (the K26): the LL's build is slow-early
            # (the yaw's inertia — a delayed exponential); the delay
            # re-arms when the turn target jumps; during the delay the
            # omega is frozen (no chase)
            if (abs(wss - prev_target) > 0.1 * abs(wss)
                    and abs(wss) > 1e-6):
                self._yb_delay = b.get("td", 0.0)
            if self._yb_delay > 0:
                self._yb_delay -= dt
                tau_yaw = None
            elif abs(wss - self.omega) > (1.0 - b["A"]) * abs(wss):
                tau_yaw = b["tf"]        # the fast rise (the fitted tau —
                # the K25 fix: this was the hardcoded tau_turn, so the
                # measured tf never applied and the builds ran ~2x fast)
            else:
                tau_yaw = b["ts"]          # the sway-coupled tail
        if tau_yaw is not None:
            self.omega += (wss - self.omega) / tau_yaw * dt
        self._v_prev = self.V

        # -- crew tank ---------------------------------------------------
        # net = the measured drain/refill (W/man) at the anchor levels;
        # the refill is capped at W_max/tau as in the LL. In the
        # one-side-stopped legs the rowing side's drain is measured
        # separately (task T4 follow-up): the LL's rowing side pulls
        # less at the low hold/back speeds (~28 W/man spoude vs the
        # symmetric ~68) — the symmetric net would drain the tank ~2.4x
        # too fast and drop the chase target early (the cruise_turn
        # fatigue/mean regressions, K13)
        # -- crew tank (per side, K22) --------------------------------
        # The LL's tanks are per side: the rowing side drains first (the
        # fresh nets), the backing side only after the V collapse unlocks
        # its blades (the flow limit at v_flow — the back stroke degener-
        # ates to a hold-brake at speed); the holding side never drains
        # (the passive brake). The symmetric state keeps both in lockstep.
        def drain(side, net, dt):
            if net > 0.0:
                return max(0.0, self.W[side] - net * dt)
            return min(self.W_max, self.W[side] + min(-net,
                                                      self.W_max / c.tau_w) * dt)
        if rowing:
            stopped = [s for s in ("port", "star")
                       if self.oar_state[s] in ("hold", "back")]
            if len(rowing) == 1 and stopped:
                row_side, stop_side = rowing[0], stopped[0]
                # the FRESH-phase drain is the commanded pull (the
                # measured net_fresh — the turns' full-tank entry); the
                # drained nets (net_asym ~ 0) apply only after the tank
                # empties (the K13 cruise_turn context, unchanged)
                row_net = c.net_asym(r_eff, p_eff,
                                     self.oar_state[stop_side]) \
                    if empty else c.net_fresh(r_eff, p_eff)
                self.W[row_side] = drain(row_side, row_net, dt)
                if self.oar_state[stop_side] == "back":
                    # the flow-limit gate: locked (net ~ 0) while the
                    # ship is fast; the unlocked drain (the fresh net)
                    # below v_flow; the drained net after its own empty
                    stop_net = c.net_asym(r_eff, p_eff, "back") \
                        if self.W[stop_side] <= 0.0 \
                        else (0.0 if self.V > c.v_flow * KT
                              else c.net_fresh(r_eff, p_eff))
                    self.W[stop_side] = drain(stop_side, stop_net, dt)
                else:
                    self.W[stop_side] = drain(stop_side, 0.0, dt)
            else:
                for side in rowing:
                    self.W[side] = drain(side, c.net(r_eff, p_eff), dt)
        else:
            for side in ("port", "star"):
                self.W[side] = drain(side, -c.p_crit, dt)  # refill at the cap
        self.W_frac = self.W[rowing[0]] / self.curves.w_max \
            if rowing else self.W["port"] / self.curves.w_max

        # -- position ----------------------------------------------------
        self.psi += self.omega * dt
        # the turn-sway's lateral displacement (the K25 addition): the
        # LL's crab (the measured drift angle, turn_beta) shifts its
        # path laterally — the HL has no sway DOF, so the path would
        # miss the crab (the |y| at 180 deg runs ~5-6 % high); the crab
        # ramps with the turn (|omega|/|wss|) and follows the turn's
        # sign convention (the beta's measured sign)
        v_sway = 0.0
        if abs(wss) > 1e-6:
            beta = c.turn_beta(self.helm_frac, self.oar_state[
                next((s for s in ("port", "star")
                      if self.oar_state[s] in ("hold", "back")), "port")],
                bool(asym))
            v_sway = self.V * math.tan(math.radians(beta)) \
                * min(1.0, abs(self.omega) / abs(wss))
        self.x += (self.V * math.cos(self.psi)
                   - v_sway * math.sin(self.psi)) * dt
        self.y += (self.V * math.sin(self.psi)
                   + v_sway * math.cos(self.psi)) * dt
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
                              rate_eff=self.rate_eff,
                              W_frac=self.W[side] / self.curves.w_max,
                              limited="none")
        return dict(t=self.t, V=self.V, omega=self.omega, psi=self.psi,
                    x=self.x, y=self.y, rate=self.rate, crew=crew,
                    helm=(self.helm_dir, self.helm_frac),
                    calibration=self.curves.meta["id"])
