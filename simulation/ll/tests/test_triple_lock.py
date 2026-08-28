"""The ch.7 triple lock (VALIDATION §11, task T1 — the M3 audit).

The LL's rate curve is flatter than the ch.7 triple (25.5/28.8/32.3 spm ->
7/7.5/8 kt, Mark II hull): at hull=1.08 the LL gives 6.83/7.15/7.51 kt
(-2.5/-4.6/-6.1 %). The M3 audit (2026-08) ruled out the speed-dependent
Mark II uplift as the cause (it moves the reference the WRONG way: the
corrected hull needs less power, so the residuals become -2.7/-5.1/-6.8 %)
and located the deficit in the LL's rate->power shape (per-man gross
110/129/152 W vs the chain's 115/145/180, growing with rate; E_g flat at
51.5-52.3 % vs the 53-55 % band) — the blade/kinematics chain, not the
hull factor. The Table 9.6 hull=1.0 pair remains the acceptance; the
triple tension stays open with the cause named. This test locks the
current truth so a physics change that silently shifts the curve fails.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from ll.hull import equilibrium_speed

TRIPLE = [(25.5, 6.83), (28.8, 7.15), (32.3, 7.51)]  # kt @ hull=1.08


def _v(rate):
    r = equilibrium_speed("Olympias", rate, hull=1.08)
    return r["V"] / 0.514444


@pytest.mark.parametrize("rate,ref", TRIPLE)
def test_triple_lock(rate, ref):
    v = _v(rate)
    assert abs(v - ref) < 0.05, f"{rate} spm: {v:.2f} kt vs the locked {ref:.2f}"


def test_triple_tension_sign():
    """The tension's shape is locked: the gap grows with rate (the LL's
    rate curve is flatter than the ch.7 triple)."""
    v1 = _v(25.5)
    v3 = _v(32.3)
    gap25 = 7.0 - v1
    gap32 = 8.0 - v3
    assert gap32 > gap25 + 0.02, "the triple tension must grow with rate"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
