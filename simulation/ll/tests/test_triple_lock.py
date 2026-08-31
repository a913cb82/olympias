"""The ch.7 triple lock (VALIDATION §11, task T1 — the M3 audit and the
2026-08 fair-rig correction).

Two comparisons, same LL, same rig (Olympias, arc 0.80 m at the handle):

  FAIR — Olympias rig vs Olympias chain (hull×1.0, L=0.89, E=0.756):
    the Olympias's OWN power chain, the apples-to-apples test.
    At 25.5 spm the LL lands exactly (6.89 vs 6.89, +0.0%); the
    rate-dependent growth (-0 → -2.2 → -3.6%) is the remaining gap —
    the blade/kinematics chain, not the hull factor (M3 audit).

  LEGACY — Olympias rig vs Mark II chain (hull×1.08, L=0.99, E=0.78):
    Shaw's ch.7 table is a Mark II design table (what a future canted
    ship could do, not what Olympias does). The extra -2.5% constant
    offset vs the fair test is the L/hull mismatch (0.99/0.89 vs 0.80
    arc, hull×1.08 vs ×1.0), not a model error.

This test locks both so a physics change that silently shifts the curve
fails. The fair triple is the primary gate; the legacy triple is the
published-reference lock.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from ll.ship import equilibrium_speed

# Legacy: Olympias rig at Mark II hull — Shaw's ch.7 table reference
TRIPLE_LEGACY = [(25.5, 6.83), (28.8, 7.15), (32.3, 7.51)]  # kt @ hull=1.08
# Fair: Olympias rig at its OWN chain — the apples-to-apples gate
TRIPLE_FAIR = [(25.5, 6.89), (28.8, 7.22), (32.3, 7.58)]  # kt @ hull=1.0


def _v_legacy(rate):
    r = equilibrium_speed("Olympias", rate, hull=1.08)
    return r["V"] / 0.514444


def _v_fair(rate):
    r = equilibrium_speed("Olympias", rate, hull=1.0)
    return r["V"] / 0.514444


@pytest.mark.parametrize("rate,ref", TRIPLE_LEGACY)
def test_triple_lock(rate, ref):
    """Legacy gate: Olympias rig vs Mark II chain (hull×1.08, L=0.99).
    Kept for regression — Shaw's ch.7 table reference."""
    v = _v_legacy(rate)
    assert abs(v - ref) < 0.05, f"{rate} spm: {v:.2f} kt vs the locked {ref:.2f}"


@pytest.mark.parametrize("rate,ref", TRIPLE_FAIR)
def test_triple_fair_lock(rate, ref):
    """Fair gate: Olympias rig vs Olympias chain (hull×1.0, L=0.89).
    At 25.5 spm the LL lands exactly; the -0→-3.6% growth is the
    rate-dependent blade/kinematics residual."""
    v = _v_fair(rate)
    assert abs(v - ref) < 0.05, f"{rate} spm: {v:.2f} kt vs the locked {ref:.2f}"


def test_triple_tension_sign():
    """The tension's shape is locked: the gap grows with rate (the LL's
    rate curve is flatter than the chain). Tested on the fair comparison
    where the constant rig-mismatch offset is removed."""
    # Fair chain speeds for L=0.89 E=0.756 at hull×1.0: 6.89/7.38/7.87 kt
    # (from W = 170×7.43r×0.89×r×0.756/60, inverted via W=155V³+4.13V⁵)
    fair_chain = {25.5: 6.89, 28.8: 7.38, 32.3: 7.87}
    v1 = _v_fair(25.5)
    v3 = _v_fair(32.3)
    gap25 = fair_chain[25.5] - v1
    gap32 = fair_chain[32.3] - v3
    assert gap32 > gap25 + 0.02, "the fair triple tension must grow with rate"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
