"""The start-from-rest locked-context row (VALIDATION §10.1, task M4):
the physiology-limited LL start vs the trial band.

Measured 2026-08 (the M4 audit): the LL reaches 5.81 kt @ 30 s,
6.93 kt @ 60 s, 7.0 kt at 62.2 s (28.8 spm spoude, 170 oars, dt 0.05).
References: Taylor's trained-crew bulk model 0->7 kt in ~14 s (register
D5); the 1988 less-trained trial 0->7 kt in 32 s. The LL is the SLOWEST
of the three — the physiology layer (the Fh<=700 N ceiling, the short
stretched strokes, t_rise 0.15 s provisional, register D10) governs the
start and the 1988 comparison is a documented context gap, not a gate.
The lock asserts the envelope so a physics change that shifts the start
silently fails here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from ll.ship import Ship

DT = 0.05


def start_trace(dt=DT):
    ship = Ship(rate=28.8, pressure=("spoude", "spoude"), n_oars=170)
    marks, t7 = {}, None
    n = int(200 / dt)
    for i in range(n):
        ship.step(dt)
        t = (i + 1) * dt
        vkt = ship.V / 0.514444
        if t7 is None and vkt >= 7.0:
            t7 = t
        for m in (30, 60):
            if m not in marks and t >= m:
                marks[m] = vkt
        if t >= 120:
            break
    return marks, t7


def test_start_30s():
    marks, _ = start_trace()
    assert 5.0 < marks[30] < 6.6, f"V@30s moved: {marks[30]:.2f} kt"


def test_start_60s():
    marks, _ = start_trace()
    assert 6.4 < marks[60] < 7.4, f"V@60s moved: {marks[60]:.2f} kt"


def test_time_to_7kt_band():
    marks, t7 = start_trace()
    # the chain-law baseline (2026-08): the LL's spoude start peaks at
    # ~6.6 kt and never reaches 7 — the chain drag (the tank-tested
    # law, now the default) EXPOSES the LL's thrust deficit (the T1
    # open item — the rate→power curve is flatter than the chain's;
    # the old 40.2v^2 proxy masked it). The bands are the measured
    # state; the context gap (the 1988 trial's 0->7 in 32 s) stays
    # documented: the LL is slower either way.
    assert 5.2 < marks[30] < 6.2, f"V@30s moved: {marks[30]:.2f} kt"
    assert 6.2 < marks[60] < 7.0, f"V@60s moved: {marks[60]:.2f} kt"
    assert t7 is None or t7 > 32.0, "the LL start must stay slower than the 1988 trial"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
