"""Determinism lock (AGENTS.md: same input -> same output).

The LL contains no randomness (verified: no RNG in ll/common/hl-core),
so identical runs must be bit-identical. This guards the project rule
against future stochastic additions (crew variability, Monte Carlo):
any nondeterminism fails here loudly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT
from ll.ship import Ship


RATE_T = 19.81  # any turn rate works; holds 6 kt straight-line rate


def _run():
    s = Ship(rate=28.8, pressure=("steady", "steady"))
    s.V = 5.0 * KT
    while s.t < 60.0:
        s.step(0.02)
    s2 = Ship(rate=RATE_T, helm=("port", 1.0))
    s2.V = 6.0 * KT
    while s2.t < 60.0:
        s2.step(0.02)
    return s, s2


def test_determinism():
    a1, b1 = _run()
    a2, b2 = _run()
    for x, y in ((a1, a2), (b1, b2)):
        assert (x.V, x.x, x.y, x.psi, x.omega, x.t) == (
            y.V,
            y.x,
            y.y,
            y.psi,
            y.omega,
            y.t,
        )
        assert (x.rate, x.crew_p.W_frac) == (y.rate, y.crew_p.W_frac)
