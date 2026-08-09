"""One trireme oar, time-stepped (Phase 1 — the LL skeleton).

Kinematics (piecewise-linear in oar angle over the stroke cycle, matching the
rigid-oar model's convention):

  - drive:     C: +B/2 -> -B/2 at constant omega over t_drive (Table 9.6),
               blade immersed;
  - recovery:  -B/2 -> +B/2, blade out of water, no force.

Angle-based: the oar advances its angle at the *effective* omega each step, so
the physiology layer (ll/rower.py) can configure a force-limited stroke
(slower drive, shorter sweep, lost tempo) per catch via configure_stroke().
With the commanded kinematics configured (the default) the discretisation
reproduces the rigid-oar model exactly (Gate 1).

Force: flat-plate normal law (ll/blade.py). Massless lever for Gate 1; the
inertia layer (Table 3.1) lands later per the plan §5.

Deterministic: oar state is (C, in_drive, cycle_no) — a pure function of time.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ll.blade import blade_force


@dataclass(frozen=True)
class OarStep:
    """Per-step telemetry (deterministic, replayable)."""
    t: float             # seconds since the last catch
    C: float             # oar angle from athwartships (rad)
    omega: float         # angular rate (rad/s)
    immersed: bool
    vn: float            # normal flow at blade CP (m/s)
    Fn: float            # blade force magnitude (N)
    Fx: float            # force on hull, along keel (N)
    Fy: float            # force on hull, athwartships (N)
    Fh: float            # handle force (N)


class Oar:
    def __init__(self, rig: dict, r_spm: float, t_drive: float | None = None,
                 direction: int = 1, mit: float = 0.0, t_rise: float = 0.15):
        """direction = +1 forward stroke; -1 backing water (drive sweeps the
        other way — the blade force law then gives negative thrust naturally).

        mit: rotational inertia about the thole (kg m2, Table 3.1) — the
        inertia layer (Gate 5): at the catch the rower flips the oar from the
        recovery swing to the drive speed over t_rise (a handle-force spike);
        at the finish the oar's momentum assists (a release). The impulses
        are internal to the rower-oar system: the hull forces are unchanged.
        mit = 0 disables the layer (exact pre-Gate-5 behaviour)."""
        self.rig = rig
        self.dir = direction
        self.mit = mit
        self.t_rise = t_rise
        self.cycle = 60.0 / r_spm
        self.t_drive = t_drive if t_drive is not None else self.cycle * 0.333
        self.t_recovery = self.cycle - self.t_drive
        self.sweep = math.radians(rig["sweep"])          # commanded sweep B
        self.omega_cmd = self.sweep / self.t_drive        # commanded drive speed
        self.omega_rec_cmd = self.sweep / self.t_recovery
        # effective kinematics (the crew model may override per stroke)
        self.omega_drive = self.omega_cmd
        self.omega_recover = self.omega_rec_cmd
        self.sweep_eff = self.sweep
        self.C = self.dir * self.sweep / 2.0              # at the catch
        self.in_drive = True                              # first drive starts now
        self.t_since_catch = 0.0
        self.cycle_no = 0

    # ------------------------------------------------------------------
    def inertia_fh(self) -> float:
        """Handle-force contribution of the oar's rotational inertia (N):
        the catch flip (+I·(w_d+w_r)/(t_rise·lin), last t_rise of the cycle,
        blade out of the water) and the finish release (-same, first t_rise
        after the finish). Rectangular pulses delivering the exact impulse;
        net impulse over the cycle = 0 (energy closure)."""
        if self.mit <= 0.0:
            return 0.0
        if self.t_since_catch >= self.cycle - self.t_rise:
            return (self.mit * (self.omega_drive + self.omega_recover)
                    / (self.t_rise * self.rig["lin"]))
        if self.t_drive <= self.t_since_catch < self.t_drive + self.t_rise:
            return (-self.mit * (self.omega_drive + self.omega_recover)
                    / (self.t_rise * self.rig["lin"]))
        return 0.0

    def flip_power(self, rate_eff: float) -> float:
        """W/man the flip costs: 1/2·I·w_drive^2 per stroke (concentric;
        the finish braking is eccentric — cheaper — noted, not counted)."""
        if self.mit <= 0.0:
            return 0.0
        return 0.5 * self.mit * self.omega_drive ** 2 * rate_eff / 60.0

    def reset(self) -> None:
        self.omega_drive = self.omega_cmd
        self.omega_recover = self.omega_rec_cmd
        self.sweep_eff = self.sweep
        self.C = self.dir * self.sweep / 2.0
        self.in_drive = True
        self.t_since_catch = 0.0
        self.cycle_no = 0

    def configure_stroke(self, omega_drive: float, omega_recover: float,
                         sweep_eff: float) -> None:
        """Set the effective kinematics for the next drive (called at the
        catch by the crew model — ll/rower.py)."""
        self.omega_drive = omega_drive
        self.omega_recover = omega_recover
        self.sweep_eff = sweep_eff

    def step(self, dt: float, V: float) -> OarStep:
        C = self.C
        immersed = self.in_drive
        omega = (-self.dir * self.omega_drive if immersed
                 else self.dir * self.omega_recover)
        f = blade_force(C, omega, V, self.rig, immersed)
        # the inertia pulses (blade out of the water at the stroke ends)
        f["Fh"] = f["Fh"] + self.inertia_fh()
        # advance
        if self.in_drive:
            self.C -= self.dir * self.omega_drive * dt
            if self.dir * self.C <= -self.sweep_eff / 2:   # finish
                self.C = -self.dir * self.sweep_eff / 2
                self.in_drive = False
        else:
            self.C += self.dir * self.omega_recover * dt
            if self.dir * self.C >= self.sweep_eff / 2:    # catch
                self.C = self.dir * self.sweep_eff / 2
                self.in_drive = True
                self.cycle_no += 1
                self.t_since_catch = 0.0
        self.t_since_catch += dt
        return OarStep(t=self.t_since_catch - dt, C=C, omega=omega,
                       immersed=immersed, vn=f["vn"], Fn=f["Fn"], Fx=f["Fx"],
                       Fy=f["Fy"], Fh=f["Fh"])


def simulate(oar: Oar, V: float, dt: float, n_cycles: int) -> dict:
    """Run n_cycles at fixed hull speed V; return cycle-averaged quantities
    in the rigid-oar model's conventions (mean thrust over the full cycle,
    handle force RMS over the drive, ideal blade efficiency)."""
    oar.reset()
    Fx_sum = Fh2 = Ft = Th = 0.0
    fb_peak = 0.0
    while oar.cycle_no < n_cycles:
        s = oar.step(dt, V)
        if s.immersed:
            Fx_sum += s.Fx * dt
            Fh2 += s.Fh * s.Fh * dt
            Ft += s.Fx * V * dt
            Th += s.Fh * oar.omega_drive * oar.rig["lin"] * dt
            fb_peak = max(fb_peak, abs(s.Fn))
    return dict(
        mean_thrust=Fx_sum / (oar.cycle * n_cycles),
        mean_fh=math.sqrt(Fh2 / (oar.t_drive * n_cycles)),
        eff=Ft / Th if Th else float("nan"),
        fb_peak=fb_peak,
    )
