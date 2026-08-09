"""Gate 2 — surge hull against the validated chain.

Run: python3 tests/test_gate2.py  (from trireme-sim/)

Contract (plan §6, Level 1; plan next-actions Gate 2):
  - The coupled surge integrator settles on the hull=1.0 anchors: 7.2 kt @
    28.8 spm (Table 9.6 / S6), 8.2 kt @ 36 spm (Table 9.6).
  - Sprint (44.5 spm, ~130 effective rowers): the LL prediction brackets the
    8.2-8.4 kt trial over the unmeasured t_drive range (data gap: Table 9.6
    lacks a 44.5-spm entry) — the empirical oQ-18 answer for the Olympias
    rig (flat-plate 0.078 m2 is sufficient here; the Mark IIb shortfall is a
    separate, documented item).
  - Full per-step coupling agrees with the mean-force equilibrium (<1 %).
  - Regime honesty: near-cruise only; the start-from-rest transient demands
    inhuman handle forces under prescribed kinematics (oQ-13) — locked by
    test; the force-ceiling path is demo-only.
"""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT, OQ18
from ll.hull import run_cruise, equilibrium_speed, SurgeHull
from ll.oar import Oar
from common.chain import RIGS
from ll.hull import t_drive_for

# --- 1. equilibrium at the anchored points ---

def test_anchor_288():
    eq = equilibrium_speed("Olympias", 28.8)
    assert 6.84 <= eq["V"] / KT <= 7.56, f"V* = {eq['V']/KT:.2f} kt @ 28.8 spm"


def test_table96_36():
    eq = equilibrium_speed("Olympias", 36.0)
    assert 7.79 <= eq["V"] / KT <= 8.61, f"V* = {eq['V']/KT:.2f} kt @ 36 spm"


def _v_star(spm, n_oars, t_drive):
    from ll.hull import drag_force
    from ll.oar import simulate

    def g(V):
        res = simulate(Oar(RIGS["Olympias"], spm, t_drive), V, t_drive / 600,
                       n_cycles=4)
        return n_oars * res["mean_thrust"] - drag_force(V)
    lo, hi = 0.5, 6.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def test_sprint_brackets_trial():
    """ch.9 sprint (44.5 spm, ~130 effective rowers) measured 8.2-8.4 kt.
    Table 9.6 has no 44.5-spm entry, so t_drive is a data gap; over the
    plausible range (0.347 s extrapolated .. 0.392 s at 36 spm) the LL
    prediction spans ~7.9-8.8 kt and the trial band lies inside it.
    This is the empirical oQ-18 answer for the Olympias rig: the flat-plate
    0.078 m2 law brackets the sprint trial; the spread is the data gap."""
    lo = _v_star(44.5, 130, 0.392) / KT
    hi = _v_star(44.5, 130, 0.347) / KT
    assert hi > 8.4 and lo < 8.2, f"bracket [{lo:.2f}, {hi:.2f}] kt must span 8.2-8.4"
def test_sprint_default_locked():
    """Lock the default (extrapolated t_drive) result so a silent change to
    the t_drive policy fails here until the docs change."""
    eq = equilibrium_speed("Olympias", 44.5, n_oars=130)
    assert 8.5 <= eq["V"] / KT <= 9.0, f"sprint V* = {eq['V']/KT:.2f} kt"


def test_sprint_170_overshoot():
    """The full 170-oar crew exceeds the trial band — the ch.9 trial was
    rowed by ~130; the difference is crew count, not physics."""
    eq = equilibrium_speed("Olympias", 44.5, n_oars=170)
    assert eq["V"] / KT > 8.6


def test_cruise_monotonic():
    Vs = [equilibrium_speed("Olympias", r)["V"] for r in (25.5, 28.8, 32.3, 36.0, 44.5)]
    assert all(b > a for a, b in zip(Vs, Vs[1:])), Vs


# --- 2. full per-step coupling ---

def test_coupling_agreement():
    out = run_cruise("Olympias", 28.8, t_end=300.0)
    d = abs(out["V_settled"] / out["eq"]["V"] - 1)
    assert d < 0.01, f"settled {out['V_settled']/KT:.3f} kt vs eq {out['eq']['V']/KT:.3f} kt"
    assert out["V_settled"] / KT <= 7.56


def test_settling():
    out = run_cruise("Olympias", 28.8, t_end=600.0)
    assert out["settle_time"] is not None and out["settle_time"] < 300, out["settle_time"]
    # no mean-overshoot beyond 0.5% of V* (the trailing mean is ripple-free)
    vmax = max(out["wmean"]) / KT
    assert vmax < out["V_settled"] / KT * 1.005, f"mean overshoot to {vmax:.2f} kt"


def test_ripple():
    """Stroke-frequency surge: the ship surges each drive and eases in the
    recovery. Expected ~0.1-0.25 kt p-p; must stay small vs V* (physical)."""
    out = run_cruise("Olympias", 28.8, t_end=300.0)
    assert out["ripple"] / KT < 0.35, f"ripple {out['ripple']/KT:.2f} kt"
    assert out["ripple"] / KT > 0.05, f"ripple suspiciously small {out['ripple']/KT:.3f} kt"


def test_dt_convergence():
    a = run_cruise("Olympias", 28.8, t_end=120.0, dt=0.01)
    b = run_cruise("Olympias", 28.8, t_end=120.0, dt=0.005)
    assert abs(a["V_settled"] / b["V_settled"] - 1) < 0.005


# --- 3. regime honesty ---

def test_rest_demands_ceiling():
    """At low speed, prescribed kinematics demand inhuman handle forces —
    the start-from-rest transient needs the oQ-13 rower ceiling (Phase 4)."""
    rig = RIGS["Olympias"]
    td, _ = t_drive_for("Olympias", 28.8)
    oar = Oar(rig, 28.8, td)
    hull = SurgeHull()
    out = hull.run(oar, V0=0.5, t_end=5.0, dt=td / 600)
    assert out["peak_fh"] > 1000, f"peak Fh {out['peak_fh']:.0f} N"


def test_start_ceiling_smoke():
    """Provisional demo only: force-ceiling clamp lets the ship launch from
    rest without inhuman forces. No acceptance band (oQ-13)."""
    out = run_cruise("Olympias", 28.8, t_end=600.0, fh_max=700.0, v0=0.0)
    assert out["peak_fh"] <= 700.0 * (1 + 1e-9)
    assert out["V_settled"] / KT > 6.0, f"only {out['V_settled']/KT:.2f} kt after 600 s"


print(f"note: {OQ18}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
