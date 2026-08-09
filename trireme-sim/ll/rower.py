"""Physiological rower model (Phase 1 Gate 4, plan §12).

One side's crew, aggregated (85 identical rowers in v1; per-tier factors
later). Three components, all anchored in the plan §12.1:

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

from common.chain import CN, RHO, RIGS
from ll.oar import Oar

# --- anchors (plan §12.1; provisional except P_CRIT) ---
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
HOLD_FRAC = 0.05        # hold-water brake fraction — two-anchor calibration
                        # (tightest turn: D = 61.3 m vs 62 anchor AND the speed
                        # halves to ~3.7 kt, matching the trial's mean 2.9 kt;
                        # t_360 residual 85 vs 128 s -> the fitted Omega yaw
                        # resistance question, register C1). f = 0.05 ~= held
                        # blades at ~12-13 deg to the flow.

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


class SideCrew:
    """One side's crew: owns the Oar, the stroke plan, and the W' tank."""

    def __init__(self, rig_name: str, n_side: int, rate: float, t_drive: float,
                 pressure: str = "spoude", state: str = "row",
                 direction: int = 1, mit: float = 0.0, t_rise: float = 0.15,
                 hold_frac: float = HOLD_FRAC):
        rig = RIGS[rig_name]
        self.rig_name = rig_name
        self.rig = rig
        self.n = n_side
        self.lin = rig["lin"]
        self.l_cp = rig["lout"] - (rig["blade"] - 0.260)
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
        self.oar = Oar(rig, rate, t_drive, direction=direction, mit=mit,
                       t_rise=t_rise)
        self.omega_cmd = self.oar.omega_cmd
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
                fh_avail = min(fh_avail,
                               self.P_crit * 60.0 / (B * lin * self.rate_cmd))
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
                fh_avail = min(fh_avail,
                               self.P_crit * 60.0 / (B * lin * self.rate_cmd))
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

        # achieved power (per man, cycle-averaged)
        p_ext = abs(fh_mean) * B_eff * lin * rate_eff / 60.0
        return StrokePlan(omega=w, sweep=B_eff, t_drive=t_drive,
                          omega_recover=w_rec, rate_eff=rate_eff,
                          fh_peak=fh_peak, fh_mean=fh_mean, p_ext=p_ext,
                          limited_by=limited)

    # ------------------------------------------------------------------
    def step(self, dt: float, V: float) -> tuple[float, float, float]:
        """Advance one step; returns (rowing force N/oar, fh_peak N,
        hold-brake force N/oar — split so the ship can use different yaw
        levers for the two: the brake is a keel-aligned drag at the oar
        stations (athwartships arm), not the fitted thrust lever."""
        if self.pressure == "rest":
            self.p_gross_current = 0.0
            self.plan = None
            return 0.0, 0.0, 0.0
        if self.state in ("bank", "hold"):
            self.p_gross_current = 0.0
            if self.state == "hold":
                brake = -self.hold_k * V * abs(V)
                return 0.0, 0.0, brake
            return 0.0, 0.0, 0.0
        # plan at the catch (first stroke, or the step after a catch crossing)
        if self.plan is None or (self.oar.in_drive
                                 and self.oar.t_since_catch <= dt + 1e-12):
            self.plan = self.plan_stroke(V)
            self.oar.configure_stroke(self.plan.omega, self.plan.omega_recover,
                                      self.plan.sweep)
            self.rate_eff = self.plan.rate_eff
        if self.plan.limited_by == "back-hold":
            # backing at speed degenerates: the crew can only check the
            # blade (the brake); the oar must not be stepped (a parked blade
            # would compute the full flow drag, not the held brake)
            self.p_gross_current = 0.0
            brake = -self.hold_k * V * abs(V)
            return 0.0, 0.0, brake
        s = self.oar.step(dt, V)
        self.p_gross_current = (self.plan.p_ext
                               + self.oar.flip_power(self.plan.rate_eff)
                               + oar_absorbed(self.plan.rate_eff))
        self.last_fh = s.Fh
        return s.Fx, s.Fh, 0.0

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
            self.oar = Oar(self.rig, self.rate_cmd, self.oar.t_drive,
                           direction=need_dir, mit=self.mit, t_rise=self.t_rise)
            self.omega_cmd = self.oar.omega_cmd
        else:
            self.oar.reset()
        self.plan = None

    def set_pressure(self, level: str) -> None:
        self.pressure = level
        if level == "rest":
            self.plan = None

    def set_rate(self, rate: float, t_drive: float) -> None:
        self.rate_cmd = rate
        self.oar = Oar(self.rig, rate, t_drive, direction=self.oar.dir,
                       mit=self.mit, t_rise=self.t_rise)
        self.omega_cmd = self.oar.omega_cmd
        self.rate_eff = rate
        self.plan = None
