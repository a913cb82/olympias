"""Physiological rower model (Phase 1 Gate 4, the LL gates (docs/VALIDATION.md)).

One side's crew, aggregated (85 identical rowers in v1; per-tier factors
later). Three components, all anchored in the the LL gates (docs/VALIDATION.md):

  - Peak force ceiling Fh_max: the blade may not demand more handle force
    than a rower can pull — the drive slows (omega_p).
  - Endurance: critical-power model — a W' tank (anaerobic capacity) drains
    when gross power exceeds P_crit_gross, refills at rest; while W' > 0 the
    rower delivers the commanded power, when empty only P_crit (omega_m).
  - Stroke adaptation at fixed tempo: the drive fits its slot
    (cycle - t_rec_min); if it cannot, the sweep shortens; below the floor
    the rate falls (achieved rate < commanded) — the weakest side governs.

Anchors: P_crit = 80 W/man external (Rossiter & Whipp, Rankov ch.23, primary
— verified in our text dump); self-consistent with ch.7 (7 kt = 79.5 W
handle). Fh_max = 700 N and W_max = 10 kJ/man provisional (model-implied;
ch.9 sprint durations and the S6 force source pending — uncertainties
register). tau = 120 s refill (Monod/MacFarlane/Nadel family).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from common.chain import CN, OAR_TIER_MIT, RHO, RIGS
from ll.oar import Oar
from ll.stations import short_rig as stations_short_rig

# --- anchors (the LL gates (docs/VALIDATION.md); provisional except P_CRIT) ---
Fh_MAX = 700.0          # N peak handle force per rower
Fh_BURST = 330.0        # N max mean handle force (chain sprint pull at 44.5 spm;
                        # the W'-limited burst level, any rate)
P_CRIT = 80.0           # W/man external sustainable power (R&W ch.23, primary)
W_MAX = 5_000.0         # J/man anaerobic capacity — anchored to the ch.9 four-run
                        # sprint (8.2-8.3 kt sustained ~45 s at 44.5 spm:
                        # excess 116.6 W/man x 45 s ~= 5.2 kJ); the 3/4-NM 6.5-min
                        # run implies up to ~9.5 kJ — 2-parameter CP tension,
                        # uncertainties register D6
TAU = 120.0             # s W' refill time constant
T_REC_MIN = 0.5         # s recovery floor (body mechanics)
B_FLOOR_FRAC = 0.4      # usable-stroke floor as a fraction of the sweep
HOLD_FRAC = 0.08       # hold-water brake fraction — re-measured 2026-08 (the
                        # sway DOF, plan 15.3, changed the turn physics; the
                        # original 0.05 two-anchor value predates it). The
                        # one-parameter scan vs the SAME anchors (the
                        # tightest-turn D = 62 m and the trial's 'halves
                        # speed' ~3.25 kt): 0.08 lands D = 62.7 m (-0.5 % vs
                        # +9.2 % at 0.05) and the drained floor 3.22 kt (the
                        # trial's halving, vs 3.54 at 0.05). f = 0.08 ~=
                        # held blades at ~19-20 deg to the flow.

# pressure levels: anchors relative to the validated chain (spoude = 1.0);
# steady = sustainable envelope (<= P_crit), spoude = W'-limited burst
PRESSURE = {"rest": 0.0, "steady": 0.7, "fast": 0.85, "spoude": 1.0}


def oar_absorbed(r: float) -> float:
    """Non-propulsive oar losses, W/man (lane-4 chain)."""
    return 0.96 * r + 0.016 * r * r


@dataclass
class StrokePlan:
    """The effective stroke the crew can actually row (per drive)."""
    omega: float          # effective drive speed (rad/s)
    sweep: float          # effective sweep (rad)
    t_drive: float        # drive duration (s)
    omega_recover: float  # recovery speed (rad/s)
    rate_eff: float       # achieved rate (<= commanded when tempo is lost)
    fh_peak: float        # N (<= Fh_max)
    fh_mean: float        # N mean over the drive
    p_ext: float          # W/man external (cycle-averaged)
    limited_by: str       # none | peak | mean | tempo | back-hold


class TierCrew:
    """One tier's crew on one side: owns the Oar, the stroke plan, and the
    W' tank. Parameterized by the tier size n, the oar inertia mit, and a
    sweep factor (the thalmian head-room stroke-length limit)."""

    def __init__(self, rig_name: str, n: int, rate: float, t_drive: float,
                 pressure: str = "spoude", state: str = "row",
                 direction: int = 1, mit: float = 0.0, t_rise: float = 0.15,
                 hold_frac: float = HOLD_FRAC, power_factor: float = 1.0,
                 stations: list | None = None, side: int = 1):
        rig = RIGS[rig_name]
        self.rig_name = rig_name
        self.rig = rig
        self.n = n
        # the per-station layer (ll/stations.py): stations = the tier's
        # [(x, y, short)] — one Oar per station, the short oars scaled
        self._stations_geom = stations
        self._side = side
        self._rigs = ([stations_short_rig(rig) if st[2] else rig
                      for st in stations] if stations else None)
        self.power_factor = power_factor   # the ch.9 L-model: a reduced
                                           # effective pull scales the POWER,
                                           # not the kinematics
        self.lin = rig["lin"]
        self.l_cp = rig["lout"] - (rig["blade"] - 0.260)
        # k of the (q/p)^2 turning-point blade law (ll/blade.py): the closed
        # forms below are that law at the ACTUAL turning point — the
        # flat-plate identity (blade.TURNING_POINT == "actual", the default)
        self.k = 0.5 * RHO * rig["area"] * CN            # N/(m/s)^2 per blade
        self.sweep_cmd = math.radians(rig["sweep"])
        self.B_floor = B_FLOOR_FRAC * self.sweep_cmd
        self.t_rec_min = T_REC_MIN
        self.Fh_max = Fh_MAX
        self.P_crit = P_CRIT
        self.W = W_MAX
        self.W_max = W_MAX
        self.tau = TAU
        self.hold_k = HOLD_FRAC * self.k                 # brake N/(m/s)^2 per oar
        self.hold_frac = HOLD_FRAC
        self.rate_cmd = rate
        self.pressure = pressure
        self.state = state
        self.mit = mit
        self.t_rise = t_rise
        self.hold_frac = hold_frac
        self.hold_k = hold_frac * self.k
        if stations:
            self.oars = [Oar(rg, rate, t_drive, direction=direction,
                             mit=mit, t_rise=t_rise,
                             station=(st[0], st[1], side))
                         for rg, st in zip(self._rigs, stations)]
            self.oar = self.oars[0]
        else:
            self.oars = [Oar(rig, rate, t_drive, direction=direction,
                             mit=mit, t_rise=t_rise)]
            self.oar = self.oars[0]
        self.omega_cmd = self.oar.omega_cmd
        self._stations = []
        self.plan: StrokePlan | None = None
        self.rate_eff = rate
        self.W_frac = 1.0
        self.p_gross_current = 0.0
        self.last_fh = 0.0

    # ------------------------------------------------------------------
    def fh_demanded(self) -> float:
        """Commanded mean handle force per oar. steady/fast: the chain's
        P = 7.43 r law at that pressure (sustainable). spoude: the burst
        level (max mean pull, W'-limited, any rate — the ch.9 sprint)."""
        if self.pressure == "spoude":
            return Fh_BURST
        return 7.43 * self.rate_cmd * PRESSURE[self.pressure]

    def _fh_moments(self, V: float, omega: float, sweep: float,
                    backing: bool = False) -> tuple[float, float]:
        """Mean and peak handle force over a drive arc (closed form)."""
        a = sweep / 2.0
        cos_mean = math.sin(a) / a
        cos2_mean = (sweep + math.sin(sweep)) / (2.0 * sweep)
        fac = self.k * self.l_cp / self.lin
        if backing:                      # vn = V cosC + l_cp w  (blade forward)
            v2_mean = V * V * cos2_mean + 2.0 * V * self.l_cp * omega * cos_mean \
                + self.l_cp * self.l_cp * omega * omega
            v2_peak = (V + self.l_cp * omega) ** 2
        else:                            # vn = V cosC - l_cp w  (|vn| max at C=0)
            v2_mean = V * V * cos2_mean - 2.0 * V * self.l_cp * omega * cos_mean \
                + self.l_cp * self.l_cp * omega * omega
            v2_peak = (self.l_cp * omega - V) ** 2
        return fac * v2_mean, fac * v2_peak

    def _omega_for_mean(self, V: float, sweep: float, fh_target: float,
                        backing: bool = False) -> float:
        """Root of fh_mean(V, w) = fh_target; NaN if unreachable."""
        a = sweep / 2.0
        cos_mean = math.sin(a) / a
        cos2_mean = (sweep + math.sin(sweep)) / (2.0 * sweep)
        disc = V * V * cos_mean * cos_mean - V * V * cos2_mean \
            + fh_target * self.lin / (self.k * self.l_cp)
        if disc < 0:
            return float("nan")
        if backing:
            return (-V * cos_mean + math.sqrt(disc)) / self.l_cp
        return (V * cos_mean + math.sqrt(disc)) / self.l_cp

    def _held_stations(self, brake: float) -> list:
        """The per-station tuples for the held/back-hold state: the brake
        at each held blade's position (the oar parked at its current C —
        the blade's reach y_b = y_t + lout·cos(C_eff) is the brake's
        yaw arm, r_blade x F)."""
        from ll.stations import blade_pos
        out = []
        for o, rg, st in zip(self.oars, self._rigs or (self.rig,),
                             self._stations_geom or (None,)):
            if o.station is not None:
                x_b, y_b = blade_pos(st[0], st[1], self._side, rg["lout"],
                                     self._side * o.C)
            else:
                x_b = y_b = 0.0
            out.append((0.0, 0.0, brake, x_b, y_b))
        return out

    # ------------------------------------------------------------------
    def plan_stroke(self, V: float) -> StrokePlan:
        """Plan the next drive at the catch, given current V and W' state."""
        B = self.sweep_cmd
        lin, l_cp, k = self.lin, self.l_cp, self.k
        slot = 60.0 / self.rate_cmd - self.t_rec_min
        backing = self.state == "back"

        if backing:
            # vn = V cosC + l_cp w; the peak limit binds hard at speed
            w_p = (math.sqrt(self.Fh_max * lin / (k * l_cp)) - V) / l_cp
            if w_p <= 0.05:
                # the flow drag exceeds the grip: backing degenerates to a
                # hold-brake (the rowers can only check the blade)
                fh_mean = self.k * l_cp / lin * V * V
                return StrokePlan(omega=0.0, sweep=B, t_drive=slot,
                                  omega_recover=B / self.t_rec_min,
                                  rate_eff=self.rate_cmd,
                                  fh_peak=fh_mean, fh_mean=fh_mean,
                                  p_ext=0.0, limited_by="back-hold")
            fh_avail = self.fh_demanded()
            if self.W <= 0.0:
                # the L-model: a reduced pull scales the sustainable POWER
                # too (the tier sustains power_factor x P_crit)
                fh_avail = min(fh_avail, self.P_crit * self.power_factor * 60.0
                               / (B * lin * self.rate_cmd))
            w_m = self._omega_for_mean(V, B, fh_avail, backing=True)
            if math.isnan(w_m):
                w_m = 0.0
            w = min(self.omega_cmd, w_p, w_m)
            if w < self.omega_cmd:
                limited = "peak" if w == w_p else "mean"
            else:
                limited = "none"
            fh_mean, fh_peak = self._fh_moments(V, w, B, backing=True)
        else:
            w_p = (V + math.sqrt(self.Fh_max * lin / (k * l_cp))) / l_cp
            fh_avail = self.fh_demanded()
            if self.W <= 0.0:
                fh_avail = min(fh_avail, self.P_crit * self.power_factor * 60.0
                               / (B * lin * self.rate_cmd))
            w_m = self._omega_for_mean(V, B, fh_avail)
            if math.isnan(w_m):
                w_m = 0.0
            w = min(self.omega_cmd, w_p, w_m)
            if w < self.omega_cmd:
                limited = "peak" if w == w_p else "mean"
            else:
                limited = "none"
            fh_mean, fh_peak = self._fh_moments(V, w, B, backing=False)

        # tempo: fit the drive into its slot; shorten the sweep if needed
        t_drive = B / w if w > 1e-9 else slot
        if t_drive > slot:
            B_eff = w * slot
            t_drive = B_eff / w                          # the shortened sweep
            if B_eff < self.B_floor:
                B_eff = self.B_floor                      # tempo is lost
                t_drive = B_eff / w
                rate_eff = 60.0 / (t_drive + self.t_rec_min)
                w_rec = B_eff / self.t_rec_min
                limited = "tempo"
            else:
                rate_eff = self.rate_cmd
                w_rec = B_eff / (60.0 / self.rate_cmd - t_drive)
        else:
            B_eff = B
            rate_eff = self.rate_cmd
            w_rec = B / (60.0 / self.rate_cmd - t_drive)

        # feather clamp: the deadspot — if the blade cannot outrun the water
        # (the mean normal flow at the blade stays positive at the plan's
        # omega), the rowers slip the blade: zero contribution, as the trials
        # observed ("the thalmian tier's power contribution fell sharply at
        # higher speeds")
        a = B_eff / 2.0
        vn_mean = V * (math.sin(a) / a) - l_cp * w
        if vn_mean > 0.0 and not backing:
            return StrokePlan(omega=w, sweep=B_eff, t_drive=t_drive,
                              omega_recover=w_rec, rate_eff=rate_eff,
                              fh_peak=0.0, fh_mean=0.0, p_ext=0.0,
                              limited_by="feathered")
        # achieved power (per man, cycle-averaged)
        p_ext = abs(fh_mean) * B_eff * lin * rate_eff / 60.0
        return StrokePlan(omega=w, sweep=B_eff, t_drive=t_drive,
                          omega_recover=w_rec, rate_eff=rate_eff,
                          fh_peak=fh_peak, fh_mean=fh_mean, p_ext=p_ext,
                          limited_by=limited)

    # ------------------------------------------------------------------
    def step(self, dt: float, V: float,
            ship_state: tuple | None = None) -> tuple[float, float, float]:
        """Advance one step; returns (rowing force N/oar, fh_peak N,
        hold-brake force N/oar — split so the ship can use different yaw
        levers for the two: the brake is a keel-aligned drag at the oar
        stations (athwartships arm), not the fitted thrust lever."""
        if self.pressure == "rest":
            self.p_gross_current = 0.0
            self.plan = None
            self._stations = [(0.0, 0.0, 0.0, 0.0, 0.0) for _ in self.oars]
            return 0.0, 0.0, 0.0, 0.0
        if self.state in ("bank", "hold"):
            self.p_gross_current = 0.0
            if self.state == "hold":
                brake = -self.hold_k * V * abs(V)
                self._stations = self._held_stations(brake)
                return 0.0, 0.0, brake, 0.0
            self._stations = [(0.0, 0.0, 0.0, 0.0, 0.0) for _ in self.oars]
            return 0.0, 0.0, 0.0, 0.0
        # plan at the catch (first stroke, or the step after a catch crossing)
        if self.plan is None or (self.oar.in_drive
                                 and self.oar.t_since_catch <= dt + 1e-12):
            self.plan = self.plan_stroke(V)
            for o in self.oars:
                o.configure_stroke(self.plan.omega, self.plan.omega_recover,
                                   self.plan.sweep)
            self.rate_eff = self.plan.rate_eff
        if self.plan.limited_by == "back-hold":
            # backing at speed degenerates: the crew can only check the
            # blade (the brake); the oar must not be stepped (a parked blade
            # would compute the full flow drag, not the held brake)
            self.p_gross_current = 0.0
            brake = -self.hold_k * V * abs(V)
            self._stations = self._held_stations(brake)
            return 0.0, 0.0, brake, 0.0
        if self.plan.limited_by == "feathered":
            for o in self.oars:                   # cadence continues, no force
                o.step(dt, V, ship_state)
            self.p_gross_current = 0.0
            self.last_fh = 0.0
            self._stations = [(0.0, 0.0, 0.0, 0.0, 0.0) for _ in self.oars]
            return 0.0, 0.0, 0.0, 0.0
        n = len(self.oars)
        fx = fy = fh = 0.0
        out = []
        for o, rg, st in zip(self.oars, self._rigs or (self.rig,),
                             self._stations_geom or (None,)):
            s = o.step(dt, V, ship_state)
            if o.station is not None:
                from ll.stations import blade_pos
                x_b, y_b = blade_pos(st[0], st[1], self._side, rg["lout"],
                                     self._side * o.C)
            else:
                x_b = y_b = 0.0
            out.append((s.Fx * self.power_factor, s.Fy * self.power_factor,
                        0.0, x_b, y_b))
            fx += s.Fx * self.power_factor
            fy += s.Fy * self.power_factor
            fh += s.Fh
        self._stations = out
        self.p_gross_current = (self.plan.p_ext * self.power_factor
                               + self.oar.flip_power(self.plan.rate_eff)
                               + oar_absorbed(self.plan.rate_eff))
        self.last_fh = fh / n * self.power_factor
        return (fx / n, fh / n * self.power_factor, 0.0, fy / n)

    def end_of_step(self, dt: float) -> None:
        """W' tank update (drain on gross excess, refill at rest)."""
        p_crit_g = self.P_crit + oar_absorbed(self.rate_eff)
        p = self.p_gross_current
        if p > p_crit_g:
            self.W = max(0.0, self.W - (p - p_crit_g) * dt)
        else:
            self.W = min(self.W_max,
                         self.W + min(p_crit_g - p, self.W_max / self.tau) * dt)
        self.W_frac = self.W / self.W_max

    def set_state(self, state: str) -> None:
        """Command-language state change; restarts the oar at the catch.
        Backing needs the reversed-sweep oar (direction = -1)."""
        self.state = state
        need_dir = -1 if state == "back" else 1
        if need_dir != self.oar.dir:
            self.oars = [
                Oar(rg, self.rate_cmd, self.oar.t_drive, direction=need_dir,
                    mit=self.mit, t_rise=self.t_rise,
                    station=((st[0], st[1], self._side)
                             if self._stations_geom else None))
                for rg, st in zip(self._rigs or (self.rig,), self._stations_geom or (None,))]
            self.oar = self.oars[0]
            self.omega_cmd = self.oar.omega_cmd
        else:
            for o in self.oars:
                o.reset()
        self.plan = None

    def set_pressure(self, level: str) -> None:
        self.pressure = level
        if level == "rest":
            self.plan = None

    def set_rate(self, rate: float, t_drive: float) -> None:
        self.rate_cmd = rate
        self.oars = [
            Oar(rg, rate, t_drive, direction=self.oar.dir,
                mit=self.mit, t_rise=self.t_rise,
                station=((st[0], st[1], self._side)
                         if self._stations_geom else None))
            for rg, st in zip(self._rigs or (self.rig,), self._stations_geom or (None,))]
        self.oar = self.oars[0]
        self.omega_cmd = self.oar.omega_cmd
        self.rate_eff = rate
        self.plan = None


# --- per-tier crew structure (plan 15.1) ---
TIER_SPLIT = {"thranite": 31, "zygian": 27, "thalmian": 27}   # per side


def thalmian_power_factor(rate: float) -> float:
    """Thalmian head-room factor (the ch.9 L-model: a reduced effective pull
    scales the POWER, not the kinematics): the manikin reaches 720 mm of the
    800 mm design stroke (0.9 — the rig's design stroke); 'the thalmian tier's power
    contribution fell sharply at higher speeds' (ch.9 p.77) — linear decline
    to 0.6 at 44.5 spm. Flag [?]: the exact rate-shape is unmeasured."""
    if rate <= 32.0:
        return 0.9
    return max(0.6, 0.9 - 0.3 * (rate - 32.0) / 12.5)


class SideCrew:
    """One side's crew: three TierCrews (thranite 31 / zygian 27 / thalmian
    27 per side). Exposes the single-crew API — the returned forces are
    per-oar averages over the side's 85 rowers, so the ship's math is
    unchanged; the tier split lives inside (per-tier W', rate, power)."""

    def __init__(self, rig_name: str, n_side: int, rate: float, t_drive: float,
                 pressure: str = "spoude", state: str = "row",
                 direction: int = 1, fleet: str = "spruce",
                 t_rise: float = 0.15, hold_frac: float = HOLD_FRAC,
                 stations: dict | None = None, side: int = 1):
        self.rig_name = rig_name
        self.n = n_side
        self.state = state
        self.pressure = pressure
        self.rate_cmd = rate
        if fleet == "spruce":
            mit = {t: OAR_TIER_MIT["spruce"] for t in TIER_SPLIT}
        elif fleet == "old-fir":
            mit = {"thranite": OAR_TIER_MIT["thranite"],
                   "zygian": OAR_TIER_MIT["zygian"],
                   "thalmian": OAR_TIER_MIT["thranite"]}
        else:
            mit = {"thranite": 0.0, "zygian": 0.0, "thalmian": 0.0}
        self.tiers = {
            "thranite": TierCrew(rig_name, TIER_SPLIT["thranite"], rate,
                                 t_drive, pressure, state, direction,
                                 mit=mit["thranite"], t_rise=t_rise,
                                 hold_frac=hold_frac, power_factor=1.0,
                                 stations=stations and stations["thranite"],
                                 side=side),
            "zygian": TierCrew(rig_name, TIER_SPLIT["zygian"], rate,
                               t_drive, pressure, state, direction,
                               mit=mit["zygian"], t_rise=t_rise,
                               hold_frac=hold_frac, power_factor=1.0,
                               stations=stations and stations["zygian"],
                               side=side),
            "thalmian": TierCrew(rig_name, TIER_SPLIT["thalmian"], rate,
                                 t_drive, pressure, state, direction,
                                 mit=mit["thalmian"], t_rise=t_rise,
                                 hold_frac=hold_frac,
                                 power_factor=thalmian_power_factor(rate),
                                 stations=stations and stations["thalmian"],
                                 side=side),
        }
        self.rate_eff = rate
        self.W_frac = 1.0
        self.last_fh = 0.0
        self.plan = None
        self._geom = ([(st[0], st[1]) for t in self.tiers.values()
                       for st in (t._stations_geom or [])]
                      if stations else [])

    def step(self, dt: float, V: float,
            ship_state: tuple | None = None) -> tuple[float, float, float, float]:
        fx = br = fy = 0.0
        fh = 0.0
        self._stations = []
        for t in self.tiers.values():
            f, h, b, y = t.step(dt, V, ship_state)
            fx += t.n * f
            br += t.n * b
            fy += t.n * y
            fh = max(fh, h)
            self._stations.extend(t._stations)
        self.last_fh = fh
        weakest = min(self.tiers.values(), key=lambda t: t.rate_eff)
        self.plan = weakest.plan
        self.rate_eff = weakest.rate_eff
        return fx / self.n, fh, br / self.n, fy / self.n

    def end_of_step(self, dt: float) -> None:
        for t in self.tiers.values():
            t.end_of_step(dt)
        self.W_frac = min(t.W_frac for t in self.tiers.values())

    def set_state(self, state: str) -> None:
        self.state = state
        for t in self.tiers.values():
            t.set_state(state)

    def set_pressure(self, level: str) -> None:
        self.pressure = level
        for t in self.tiers.values():
            t.set_pressure(level)

    def set_rate(self, rate: float, t_drive: float) -> None:
        self.rate_cmd = rate
        self.tiers["thalmian"].power_factor = thalmian_power_factor(rate)
        for t in self.tiers.values():
            t.set_rate(rate, t_drive)
        self.rate_eff = rate

    def tier_telemetry(self) -> dict:
        return {
            name: dict(W_frac=t.W_frac, rate_eff=t.rate_eff,
                       p_ext=t.plan.p_ext * t.power_factor if t.plan else 0.0,
                       power_factor=t.power_factor,
                       limited=t.plan.limited_by if t.plan else "parked")
            for name, t in self.tiers.items()
        }
