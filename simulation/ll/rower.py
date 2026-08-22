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

import numpy as np

from common.chain import CN, OAR_TIER_MIT, RHO, RIGS
from ll.oar import Oar
from ll.stations import blade_pos, short_rig as stations_short_rig

# --- anchors (the LL gates (docs/VALIDATION.md); provisional except P_CRIT) ---
Fh_MAX = 700.0          # N peak handle force per rower
Fh_BURST = 330.0        # N max mean handle force (chain sprint pull at 44.5 spm;
                        # the W'-limited burst level, any rate)
P_CRIT = 80.0           # W/man external sustainable power (R&W ch.23, primary)
W_MAX = 6_000.0         # J/man anaerobic capacity — re-anchored to the ch.9 four-
                        # run sprint with the FORCE MODE's excess (the same trial:
                        # 8.2-8.4 kt sustained ~45 s at 44.5 spm; the chain's
                        # excess 116.6 W/man x 45 s ~= 5.2 kJ counted no oar
                        # inertia — the force mode's drive includes the flip's
                        # 16.8 W/man, so its excess is 133.4 W/man x 45 s ~=
                        # 6.0 kJ; the 3/4-NM 6.5-min run implies up to ~9.5 kJ —
                        # the register D6 tension unchanged)
TAU = 120.0             # s W' refill time constant
T_REC_MIN = 0.5         # s recovery floor (body mechanics)
B_FLOOR_FRAC = 0.4      # usable-stroke floor as a fraction of the sweep
HOLD_FRAC = 0.08       # hold-water brake fraction — the one-parameter
                        # scan vs the SAME two anchors (the tightest-turn
                        # D = 62 m and the trial's 'halves speed' ~3.25 kt):
                        # 0.08 lands D = 62.7 m (-0.5 % vs +9.2 % at 0.05)
                        # and the drained floor 3.22 kt (the trial's
                        # halving, vs 3.54 at 0.05). f = 0.08 ~= held
                        # blades at ~19-20 deg to the flow.

# pressure levels: anchors relative to the validated chain (spoude = 1.0);
# steady = sustainable envelope (<= P_crit), spoude = W'-limited burst;
# "chain" = the reference level itself (the demand = 7.43·r exactly — the
# force-driven layer's apples-to-apples comparison with the chain law)
PRESSURE = {"rest": 0.0, "steady": 0.7, "fast": 0.85, "chain": 1.0,
            "spoude": 1.0}


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
    fh_flip: float = 0.0        # N — the catch-flip force (force mode)
    omega_entry: float = 0.0    # rad/s — blade-entry |omega| (force mode)


class TierCrew:
    """One tier's crew on one side: owns the Oar, the stroke plan, and the
    W' tank. Parameterized by the tier size n, the oar inertia mit, and a
    sweep factor (the thalmian head-room stroke-length limit)."""

    def __init__(self, rig_name: str, n: int, rate: float, t_drive: float,
                 pressure: str = "spoude", state: str = "row",
                 direction: int = 1, mit: float = 0.0, t_rise: float = 0.15,
                 hold_frac: float = HOLD_FRAC, power_factor: float = 1.0,
                 stations: list | None = None, side: int = 1,
                 force: bool = False):
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
        self.force = force      # Plan 1: the force-driven oar (ll/oar.py)
        self.hold_frac = hold_frac
        self.hold_k = hold_frac * self.k
        if stations:
            self.oars = [Oar(rg, rate, t_drive, direction=direction,
                             mit=mit, t_rise=t_rise, force=force,
                             station=(st[0], st[1], side))
                         for rg, st in zip(self._rigs, stations)]
            self.oar = self.oars[0]
        else:
            self.oars = [Oar(rig, rate, t_drive, direction=direction,
                             mit=mit, t_rise=t_rise, force=force)]
            self.oar = self.oars[0]
        self.omega_cmd = self.oar.omega_cmd
        self._stations = []
        # the per-oar loop's aligned (oar, rig, station) triples — built
        # once (and on every oar rebuild) so the per-step loop has no
        # zipping or branch-of-station checks; station is None in the
        # aggregated mode
        self._pairs = self._make_pairs()
        # the vectorized kinematic-stations pass (the 170-oar layer's hot
        # path): the per-station geometry arrays + the shared blade-law
        # scalars. The tier's oars are PHASE-LOCKED (identical C/omega at
        # every step — the kinematics are per-tier, the flow is the only
        # per-station input), so the phase machine stays scalar on the
        # first oar and one numpy pass computes the per-station forces and
        # positions. The force mode is NOT phase-locked (each drive
        # integrates its own EOM) — it keeps the scalar loop.
        self._vgeo = None
        if stations:
            xs = np.array([st[0] for st in stations])
            ys = np.array([st[1] for st in stations])
            lout = np.array([rg["lout"] for rg in self._rigs])
            lin = np.array([rg["lin"] for rg in self._rigs])
            l_cp = lout - (rig["blade"] - 0.260)   # short oars keep the blade
            self._vgeo = (xs, ys, lout, lin, l_cp,
                          math.cos(math.radians(rig.get("cant", 0.0))),
                          rig.get("slip", 1.0))
        self.plan: StrokePlan | None = None
        self.rate_eff = rate
        self.W_frac = 1.0
        self.p_gross_current = 0.0
        self.last_fh = 0.0

    # ------------------------------------------------------------------
    def fh_demanded(self) -> float:
        """Commanded mean TANGENTIAL handle force per oar. The chain's
        P = 7.43 r is the mean pull at the BUTT (the keel-direction pull);
        the oar's torque comes from its tangential component, so the EOM's
        constant force is the pull's mean tangential projection —
        cosC_mean = sin(B/2)/(B/2) — exactly the chain's own geometry
        (L = lin·B·cosC_mean, the effective pull length; the Stream A2
        audit: the explicit EOM counted the full arc, ~3 % over the
        chain). steady/fast: the chain's P = 7.43 r law at that pressure
        (sustainable). spoude: the burst level (max mean pull, W'-limited,
        any rate — the ch.9 sprint)."""
        a = self.sweep_cmd / 2.0
        cos_c = math.sin(a) / a
        if self.pressure == "spoude":
            return Fh_BURST * cos_c
        return 7.43 * self.rate_cmd * PRESSURE[self.pressure] * cos_c

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

    def _make_pairs(self) -> list:
        """The aligned (oar, rig, station-geometry) triples for the per-step
        loop (the aggregated tier: one triple with station None)."""
        rigs = self._rigs or [self.rig]
        geom = self._stations_geom or [None]
        return list(zip(self.oars, rigs, geom))

    def _held_stations(self, brake: float) -> list:
        """The per-station tuples for the held/back-hold state: the brake
        at each held blade's position (the oar parked at its current C —
        the blade's reach y_b = y_t + lout·cos(C_eff) is the brake's
        yaw arm, r_blade x F). The tier's oars are phase-locked, so the
        first oar's C is every oar's C (the vectorized pass does not step
        the others)."""
        out = []
        C = self.oar.C
        for o, rg, st in self._pairs:
            if st is not None:
                x_b, y_b = blade_pos(st[0], st[1], self._side, rg["lout"],
                                     self._side * C)
            else:
                x_b = y_b = 0.0
            out.append((0.0, 0.0, brake, x_b, y_b))
        return out

    # ------------------------------------------------------------------
    def _plan_force(self, V: float, B: float, lin: float, l_cp: float,
                    k: float) -> StrokePlan:
        """Plan 1 (the force-driven oar): the drive's kinematics EMERGE —
        the plan predicts the in-water time from the drive equilibrium (the
        oar settles where the blade drag absorbs the demand:
        vn = -sqrt(Fh·lin/(k·l_cp)) — the self-balancing drive), sizes the
        catch flip (the spike force over t_rise, pinned at the catch), and
        fits the recovery into the rest of the cycle. The minimum-shape
        hypothesis: the constant demand (the chain's mean pull at the
        pressure/W' state); the B3 profile shape [?] (the undecoded Rev F
        Figure 10) would concentrate the force at the catch — the constant
        demand is the documented start (plan 1, next-steps.md)."""
        fh = self.fh_demanded() * self.power_factor
        if self.W <= 0.0:
            fh = min(fh, self.P_crit * self.power_factor * 60.0
                     / (B * lin * self.rate_cmd))
        cf = math.cos(math.radians(self.rig.get("cant", 0.0)))
        backing = self.state == "back"
        slot = 60.0 / self.rate_cmd - self.t_rec_min
        vn_eq = math.sqrt(fh * lin / (k * l_cp))      # |vn| at the balance
        a = B / 2.0
        cos_a = math.cos(a) * cf
        # the blade-entry speed (the equilibrium at the catch)
        w_entry = (V * cos_a + vn_eq) / l_cp
        if backing:
            w_entry = (vn_eq - V * cos_a) / l_cp
            if w_entry <= 0.05:
                # the flow drag exceeds the grip: backing degenerates to a
                # hold-brake (the rowers can only check the blade)
                fh_mean = self.k * l_cp / lin * V * V
                return StrokePlan(omega=0.0, sweep=B, t_drive=slot,
                                  omega_recover=B / self.t_rec_min,
                                  rate_eff=self.rate_cmd,
                                  fh_peak=fh_mean, fh_mean=fh_mean,
                                  p_ext=0.0, limited_by="back-hold")
        # the equilibrium drive time (closed form):
        #   t = 2·l_cp·∫_0^{B/2} dC / (V·cosC·cf + vn_eq)   (Simpson; the
        # backing integrand is the mirror 1/(vn_eq - V·cosC·cf), capped at
        # the entry value — the oar crosses the stall region at the demand)
        def t_eq(sweep: float) -> float:
            a2 = sweep / 2.0
            n = 40
            h = a2 / n

            def inv(c: float) -> float:
                den = V * math.cos(c) * cf + vn_eq
                if backing:
                    den = vn_eq - V * math.cos(c) * cf
                    if den <= 0.0:
                        # the stall region: the oar crosses it at the demand
                        return 5.0 / (vn_eq - V * cos_a)
                return 1.0 / max(den, 1e-9)

            s = inv(0.0) + inv(a2)
            for i in range(1, n):
                s += (4.0 if i % 2 else 2.0) * inv(a2 * i / n)
            return 2.0 * l_cp * s * h / 3.0
        t_drive = t_eq(B)
        t_flip = self.t_rise
        B_eff = B
        rate_eff = self.rate_cmd
        limited = "none"
        if t_flip + t_drive > slot:
            B_eff = B * (slot - t_flip) / t_drive
            if B_eff < self.B_floor:
                B_eff = self.B_floor
                t_drive = t_eq(B_eff)
                rate_eff = 60.0 / (t_flip + t_drive + self.t_rec_min)
                w_rec = B_eff / self.t_rec_min
                limited = "tempo"
            else:
                t_drive = t_eq(B_eff)
                w_rec = B_eff / (60.0 / self.rate_cmd - t_flip - t_drive)
        else:
            w_rec = B / (60.0 / self.rate_cmd - t_flip - t_drive)
        # the catch flip: the spike force delivering the reversal over t_rise
        # (the G5 convention, now a motion); capped at Fh_max — the entry
        # then follows the cap (the drive converges to the equilibrium)
        fh_flip = 0.0
        if self.mit > 0.0:
            fh_flip = self.mit * (w_rec + w_entry) / (self.t_rise * lin)
            if fh_flip > self.Fh_max:
                fh_flip = self.Fh_max
                w_entry = max(0.01, fh_flip * lin * self.t_rise / self.mit
                              - w_rec)
        fh_peak = max(fh, fh_flip)
        p_ext = fh * B_eff * lin * rate_eff / 60.0
        return StrokePlan(omega=w_entry, sweep=B_eff, t_drive=t_drive,
                          omega_recover=w_rec, rate_eff=rate_eff,
                          fh_peak=fh_peak, fh_mean=fh, p_ext=p_ext,
                          limited_by=limited,
                          fh_flip=fh_flip, omega_entry=w_entry)

    def plan_stroke(self, V: float) -> StrokePlan:
        """Plan the next drive at the catch, given current V and W' state."""
        B = self.sweep_cmd
        lin, l_cp, k = self.lin, self.l_cp, self.k
        slot = 60.0 / self.rate_cmd - self.t_rec_min
        backing = self.state == "back"

        if self.force:
            return self._plan_force(V, B, lin, l_cp, k)

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
        if self.plan is None or ((self.oar.in_drive or self.oar.in_flip)
                                 and self.oar.t_since_catch <= dt + 1e-12):
            self.plan = self.plan_stroke(V)
            if self.force:
                for o in self.oars:
                    o.configure_force(self.plan.fh_mean, self.plan.fh_flip,
                                      self.plan.omega_entry,
                                      self.plan.omega_recover,
                                      self.plan.sweep)
            else:
                for o in self.oars:
                    o.configure_stroke(self.plan.omega, self.plan.omega_recover,
                                       self.plan.sweep)
            self.rate_eff = self.plan.rate_eff
        if self.plan.limited_by == "back-hold":
            # backing at speed degenerates: the flow outruns the blade at
            # the demand — the crew can only CHECK the blade (the oar held
            # against the flow). While the drive could still advance at the
            # rowers' ceiling (the kinematic mode's w_p threshold — the
            # same band as its parked blade) the blades hold the FULL
            # flat-plate drag at the held angle (the plan's fh_mean is
            # this check's handle force); above it the blades trail (the
            # hold state's 8 % brake — the tightest-turn calibration, the
            # trailing blades at ~19-20 deg).
            self.p_gross_current = 0.0
            v_check = math.sqrt(self.Fh_max * self.lin
                                / (self.k * self.l_cp)) - 0.05 * self.l_cp
            if V < v_check:
                ca = math.cos(self.sweep_cmd / 2.0)
                brake = -self.k * V * V * ca * ca * ca
            else:
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
        scale = 1.0 if self.force else self.power_factor
        if self._vgeo is not None and not self.force \
                and ship_state is not None:
            fx, fy, fh = self._stations_step(dt, V, ship_state, scale)
        else:
            fx = fy = fh = 0.0
            out = []
            for o, rg, st in self._pairs:
                s = o.step(dt, V, ship_state)
                if st is not None:
                    x_b, y_b = blade_pos(st[0], st[1], self._side, rg["lout"],
                                         self._side * o.C)
                else:
                    x_b = y_b = 0.0
                out.append((s.Fx * scale, s.Fy * scale, 0.0, x_b, y_b))
                fx += s.Fx * scale
                fy += s.Fy * scale
                fh += s.Fh
            self._stations = out
        self.p_gross_current = (self.plan.p_ext * scale
                                + self.oar.flip_power(self.plan.rate_eff)
                                + oar_absorbed(self.plan.rate_eff))
        self.last_fh = fh / n * self.power_factor
        return (fx / n, fh / n * self.power_factor, 0.0, fy / n)

    def _stations_step(self, dt: float, V: float, ship_state: tuple,
                       scale: float) -> tuple[float, float, float]:
        """The vectorized kinematic-stations step: one numpy pass over the
        tier's stations, the phase machine scalar on the first oar (the
        oars are phase-locked — identical C and omega at every step, the
        per-station flow is the only difference). Returns the tier's sums
        (fx, fy, fh). Conventions match the scalar loop exactly: the
        blade FORCES sit at the pre-advance C (the step's start), the
        blade POSITIONS at the post-advance C (one dt later — the scalar
        loop reads o.C after o.step)."""
        xs, ys, lout, lin, l_cp, cf, slip = self._vgeo
        o0 = self.oar
        C0 = o0.C
        immersed = o0.in_drive
        pulse = o0.inertia_fh()            # the pre-state pulse (phase-locked)
        o0.step(dt, V, ship_state)         # the phase advance (scalar)
        v, r = ship_state
        side = self._side
        C_eff = side * C0
        nx = math.cos(C_eff) * cf
        ny = -math.sin(C_eff) * cf
        if immersed:
            omega = -o0.dir * o0.omega_drive
            vn = ((V - r * ys) * nx + (v + r * xs) * ny + l_cp * omega) * slip
            Fn = self.k * np.abs(vn) * vn
        else:
            Fn = np.zeros(len(xs))
        Fx = -Fn * nx
        Fy = -Fn * ny
        Fh = np.abs(Fn) * l_cp / lin + pulse
        C_adv = side * o0.C                # the post-advance position arm
        x_b = xs + lout * math.sin(C_adv)
        y_b = ys + lout * math.cos(C_adv)
        self._stations = list(zip((Fx * scale).tolist(),
                                  (Fy * scale).tolist(),
                                  [0.0] * len(xs),
                                  x_b.tolist(), y_b.tolist()))
        return (float((Fx * scale).sum()), float((Fy * scale).sum()),
                float(Fh.sum()))

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
                    mit=self.mit, t_rise=self.t_rise, force=self.force,
                    station=((st[0], st[1], self._side)
                             if self._stations_geom else None))
                for rg, st in zip(self._rigs or (self.rig,), self._stations_geom or (None,))]
            self.oar = self.oars[0]
            self.omega_cmd = self.oar.omega_cmd
            self._pairs = self._make_pairs()
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
                mit=self.mit, t_rise=self.t_rise, force=self.force,
                station=((st[0], st[1], self._side)
                         if self._stations_geom else None))
            for rg, st in zip(self._rigs or (self.rig,), self._stations_geom or (None,))]
        self.oar = self.oars[0]
        self.omega_cmd = self.oar.omega_cmd
        self._pairs = self._make_pairs()
        self.rate_eff = rate
        self.plan = None


# --- per-tier crew structure ---
TIER_SPLIT = {"thranite": 31, "zygian": 27, "thalmian": 27}   # per side


def thalmian_power_factor(rate: float) -> float:
    """Thalmian head-room factor (the ch.9 L-model: a reduced effective pull
    scales the POWER, not the kinematics): the manikin reaches 720 mm of the
    800 mm design stroke (0.9 — the rig's design stroke); 'the thalmian tier's power
    contribution fell sharply at higher speeds' (ch.9 p.77) — linear decline
    to 0.6 at 44.5 spm. Flag [?]: the exact rate-shape is unmeasured (the
    C3 measurement: the no-head-room sprint equilibrium 9.2 kt vs the
    workbook's 9.95 — the head-room explains part of the sprint deficit;
    the residual is the blade-law/demand family — Stream A2's named
    causes)."""
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
                 stations: dict | None = None, side: int = 1,
                 force: bool = False):
        self.rig_name = rig_name
        self.n = n_side
        self.state = state
        self.pressure = pressure
        self.rate_cmd = rate
        self.force = force      # Plan 1: the force-driven oars
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
                                 side=side, force=force),
            "zygian": TierCrew(rig_name, TIER_SPLIT["zygian"], rate,
                               t_drive, pressure, state, direction,
                               mit=mit["zygian"], t_rise=t_rise,
                               hold_frac=hold_frac, power_factor=1.0,
                               stations=stations and stations["zygian"],
                               side=side, force=force),
            "thalmian": TierCrew(rig_name, TIER_SPLIT["thalmian"], rate,
                                 t_drive, pressure, state, direction,
                                 mit=mit["thalmian"], t_rise=t_rise,
                                 hold_frac=hold_frac,
                                 power_factor=thalmian_power_factor(rate),
                                 stations=stations and stations["thalmian"],
                                 side=side, force=force),
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
