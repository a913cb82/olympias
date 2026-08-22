"""Surge-only hull dynamics (Phase 1 Gate 2).

State: V (m/s), x along the keel. Equation of motion:

    m_app · dV/dt = N · F_oars(t, V) − D(V)

  - F_oars: per-step force from N time-stepped oars in unison (the pipe keeps
    the crew together; surge-only, so all oars share the same phase and the
    sum is N × one oar's force — exact, not an approximation).
  - D(V) = W_hull(V)/V from the validated power law (hull = 155V³ + 4.13V⁵,
    ×1.08 for the Mark II hull).
  - m_app = 1.10 × 41.35 t trial displacement (2).

Regime honesty: prescribed-kinematics oars are only physically valid where the
required handle force is humanly plausible (near cruise). At low ship speed the
blade sweeps through nearly still water and demands >1 kN handle force — beyond
any rower. The start-from-rest transient therefore needs a rower force ceiling
(oQ-13, Phase 4); `fh_max` provides a crude labelled clamp (force-limited
blade, kinematics unchanged) for demos only — Gate-2 acceptance uses the
no-ceiling regime near cruise.
"""

from __future__ import annotations

from common.chain import RIGS, T_DRIVE, SPM, hull_power
from ll.oar import Oar, simulate

M_TRIAL = 41.35e3          # kg — trial displacement (2)
M_APP_FACTOR = 1.10        # apparent-mass factor (2)
N_OARS = 170               # Olympias oar count


# Calibrated entries beyond Table 9.6 (register A8):
# t_drive(44.5) = 0.371 s chosen so the LL reproduces the ch.9 four-run
# sprint (8.2-8.3 kt at 44.5 spm, ~130 effective rowers) — the value the
# Gate-2 bracket analysis already pointed to, now pinned (calibrate_tdrive.py).
CALIBRATED_T_DRIVE = {("Olympias", 44.5): 0.371}


def t_drive_for(rig_name: str, spm: float) -> tuple[float, str]:
    """Effective-pull time for rate spm (Table 9.6): exact at the rig's measured
    points, calibrated beyond them (CALIBRATED_T_DRIVE), linear
    interpolation/extrapolation otherwise, flagged."""
    if (rig_name, spm) in CALIBRATED_T_DRIVE:
        return CALIBRATED_T_DRIVE[(rig_name, spm)], "calibrated"
    pts = sorted((SPM[rn][vkt], td) for (rn, vkt), td in T_DRIVE.items()
                 if rn == rig_name)
    for r, td in pts:
        if abs(r - spm) < 0.01:
            return td, "exact"
    if spm < pts[0][0]:
        (r1, td1), (r2, td2) = pts[0], pts[1]
        kind = "extrapolated"
    elif spm > pts[-1][0]:
        (r1, td1), (r2, td2) = pts[-2], pts[-1]
        kind = "extrapolated"
    else:
        for (r1, td1), (r2, td2) in zip(pts, pts[1:]):
            if r1 <= spm <= r2:
                break
        kind = "interpolated"
    return td1 + (td2 - td1) * (spm - r1) / (r2 - r1), kind


def drag_force(V: float, hull: float = 1.0) -> float:
    """Resistance force (N) from the validated power law."""
    return 0.0 if V < 0.05 else hull_power(V, hull) / V


def equilibrium_speed(rig_name: str, spm: float, n_oars: int = N_OARS,
                      hull: float = 1.0, t_drive: float | None = None) -> dict:
    """Mean-force equilibrium: solve n_oars·T̄(V) = D(V) by bisection.
    T̄(V) is the time-stepped oar's cycle-mean thrust at fixed V (Gate-1 oar).
    t_drive: override the Table 9.6 schedule (calibration use — A8)."""
    td, _ = (t_drive_for(rig_name, spm) if t_drive is None
             else (t_drive, "override"))

    def g(V: float) -> float:
        res = simulate(Oar(RIGS[rig_name], spm, td), V, td / 600, n_cycles=4)
        return n_oars * res["mean_thrust"] - drag_force(V, hull)

    lo, hi = 0.5, 6.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    Ve = 0.5 * (lo + hi)
    res = simulate(Oar(RIGS[rig_name], spm, td), Ve, td / 600, n_cycles=4)
    return dict(V=Ve, thrust_oar=res["mean_thrust"], mean_fh=res["mean_fh"],
                t_drive=td)


class SurgeHull:
    """Per-step coupling: oar forces and drag recomputed at the current V."""

    def __init__(self, m_trial: float = M_TRIAL, m_app_factor: float = M_APP_FACTOR,
                 hull: float = 1.0, n_oars: int = N_OARS,
                 fh_max: float | None = None):
        self.m = m_app_factor * m_trial
        self.hull = hull
        self.n_oars = n_oars
        self.fh_max = fh_max          # provisional rower ceiling (oQ-13); None = off
        self.V = 0.0

    def run(self, oar: Oar, V0: float, t_end: float, dt: float,
            sample_dt: float = 0.1) -> dict:
        """Integrate from V0 for t_end s at step dt. Returns the fine timeline
        (10 Hz by default), settled speed (mean over the final stroke cycle),
        stroke-frequency ripple (p-p over that cycle), settle time (1 % band),
        and peak handle/blade forces."""
        self.V = V0
        oar.reset()
        t = next_s = 0.0
        ts: list[float] = []
        Vs: list[float] = []
        peak_fh = 0.0
        while t < t_end:
            s = oar.step(dt, self.V)
            fx, fh = s.Fx, s.Fh
            if self.fh_max is not None and fh > self.fh_max and s.immersed:
                scale = self.fh_max / fh          # force-limited blade (crude)
                fx *= scale
                fh *= scale
            peak_fh = max(peak_fh, fh)
            self.V += (self.n_oars * fx - drag_force(self.V, self.hull)) / self.m * dt
            t += dt
            if t >= next_s:
                ts.append(t)
                Vs.append(self.V)
                next_s += sample_dt

        # settled speed + ripple over the final stroke cycle (fine samples);
        # settle detection on a trailing mean (10 s window) so the
        # stroke-frequency surge ripple (~2-3 % of V*) does not defeat it
        cyc = oar.cycle
        tail = [v for t, v in zip(ts, Vs) if t >= t_end - cyc]
        V_settled = sum(tail) / len(tail)
        ripple = (max(tail) - min(tail))
        win = max(1, int(10.0 / sample_dt))
        wmean = [sum(Vs[max(0, i - win + 1):i + 1]) / min(i + 1, win)
                 for i in range(len(Vs))]
        smin, smax = [0.0] * len(wmean), [0.0] * len(wmean)
        mn = mx = wmean[-1]
        for i in range(len(wmean) - 1, -1, -1):
            mn = min(mn, wmean[i])
            mx = max(mx, wmean[i])
            smin[i], smax[i] = mn, mx
        tol = 0.005 * V_settled
        settle_time = None
        for i, t in enumerate(ts):
            if t >= 20.0 and smax[i] - smin[i] < tol and abs(wmean[i] - V_settled) < tol:
                settle_time = t
                break
        return dict(ts=ts, Vs=Vs, V_settled=V_settled, ripple=ripple,
                    settle_time=settle_time, peak_fh=peak_fh, wmean=wmean)


def run_cruise(rig_name: str, spm: float, t_end: float = 600.0, dt: float = 0.01,
               fh_max: float | None = None, n_oars: int = N_OARS,
               v0: float | None = None) -> dict:
    """Convenience: equilibrium speed, then a full coupled run from 0.9·V*."""
    eq = equilibrium_speed(rig_name, spm, n_oars=n_oars)
    td, tsrc = t_drive_for(rig_name, spm)
    oar = Oar(RIGS[rig_name], spm, td)
    hull = SurgeHull(n_oars=n_oars, fh_max=fh_max)
    out = hull.run(oar, v0 if v0 is not None else 0.9 * eq["V"], t_end, dt)
    out["eq"] = eq
    out["t_drive_src"] = tsrc
    return out
