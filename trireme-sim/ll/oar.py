"""One trireme oar, time-stepped (Phase 1 — the LL skeleton).

Kinematics (piecewise-linear in oar angle over the stroke cycle, matching the
rigid-oar model's convention):

  - drive:     C: +B/2 -> -B/2 at constant omega over t_drive (Table 9.6),
               blade immersed;
  - recovery:  -B/2 -> +B/2 over t_cycle - t_drive, blade out of water,
               no force.

Force: flat-plate normal law (ll/blade.py). Massless lever for Gate 1; the
inertia layer (Table 3.1) lands after the gate per the plan §5.

Deterministic: oar state is (phase, cycle_no) — a pure function of time.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ll.blade import blade_force


@dataclass(frozen=True)
class OarStep:
    """Per-step telemetry (deterministic, replayable)."""
    t: float             # seconds into the cycle
    C: float             # oar angle from athwartships (rad)
    omega: float         # angular rate (rad/s)
    immersed: bool
    vn: float            # normal flow at blade CP (m/s)
    Fn: float            # blade force magnitude (N)
    Fx: float            # force on hull, along keel (N)
    Fy: float            # force on hull, athwartships (N)
    Fh: float            # handle force (N)


class Oar:
    def __init__(self, rig: dict, r_spm: float, t_drive: float | None = None):
        self.rig = rig
        self.cycle = 60.0 / r_spm
        self.t_drive = t_drive if t_drive is not None else self.cycle * 0.333
        self.t_recovery = self.cycle - self.t_drive
        self.sweep = math.radians(rig["sweep"])
        self.omega_drive = self.sweep / self.t_drive        # magnitude, rad/s
        self.omega_recover = self.sweep / self.t_recovery
        self.phase = 0.0
        self.cycle_no = 0

    def reset(self) -> None:
        self.phase = 0.0
        self.cycle_no = 0

    def _angle(self) -> float:
        if self.phase < self.t_drive:
            return self.sweep / 2 - self.omega_drive * self.phase
        return -self.sweep / 2 + self.omega_recover * (self.phase - self.t_drive)

    def step(self, dt: float, V: float) -> OarStep:
        immersed = self.phase < self.t_drive
        C = self._angle()
        omega = -self.omega_drive if immersed else self.omega_recover
        f = blade_force(C, omega, V, self.rig, immersed)
        self.phase += dt
        if self.phase >= self.cycle:
            self.phase -= self.cycle
            self.cycle_no += 1
        return OarStep(t=self.phase - dt, C=C, omega=omega, immersed=immersed,
                       vn=f["vn"], Fn=f["Fn"], Fx=f["Fx"], Fy=f["Fy"], Fh=f["Fh"])


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
