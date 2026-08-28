"""Harness checks: the comparator math, determinism, and Level-2 sanity on
short scripts (the harness — simulation/AGENTS.md).

Run: python3 harness/tests/test_harness.py  (from simulation/)

The harness must be deterministic and its metric computations exact: the
turn diameter from |y| at 180 deg, the 3-NM crossing time, the position
separation. The Level-2 tolerances themselves are judged by
harness/run_validation.py against the full script set (that run is the
acceptance record, docs/VALIDATION.md §9) — the tests here lock the machinery.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from commands.parser import parse_file
from common.chain import KT
from harness.comparator import _cumulative_distance, _interp_cross, metrics
from harness.script import run_both, turn_stream
from ll.ship import rate_for_speed

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


# ---------------------------------------------------------------------------
def test_interp_cross_exact():
    rows = [{"t": 1.0, "psi": 0.5}, {"t": 2.0, "psi": 1.0}, {"t": 3.0, "psi": 1.5}]
    t_c, v = _interp_cross(rows, "psi", 1.0)
    assert t_c == 2.0 and v == 1.0
    t_c, v = _interp_cross(rows, "psi", 0.75)
    assert abs(t_c - 1.5) < 1e-12 and abs(v - 0.75) < 1e-12


def test_turn_diameter_circle():
    """A pure circle: |y| at 180 deg is the diameter, exactly."""
    D = 90.0
    V = 6.0 * KT
    omega = 2.0 * V / D
    rows, t, psi = [], 0.0, 0.0
    while t < 200.0:
        rows.append({"t": t, "psi": psi, "y": (D / 2.0) * (1.0 - math.cos(psi))})
        t += 1.0
        psi -= omega  # turning port
    _t_c, y_c = _interp_cross(rows, "psi", math.pi, out_key="y")
    assert abs(y_c - D) < 0.1  # 1 Hz interpolation of a quadratic arc


def test_cumulative_distance():
    rows = [{"t": i, "V": 3.0} for i in range(10)]
    d = _cumulative_distance(rows)
    assert d[-1] == 30.0


# ---------------------------------------------------------------------------
def test_run_both_deterministic():
    cmds = parse_file(EXAMPLES / "long_cruise.txt")
    a = run_both(cmds, V0=0.0)
    b = run_both(cmds, V0=0.0)
    for sim in ("ll", "hl"):
        for ra, rb in zip(a[sim], b[sim]):
            for key in ("t", "V", "psi", "x", "y"):
                assert ra[key] == rb[key], (sim, key)
    assert a["meta"]["calibration"].startswith(("bootstrap", "calib-"))


def test_long_cruise_level2():
    """The sustainable envelope: W' full, stable speed, inside the gates.
    Position (task C): the LL's untrimmed lateral kick is a measured,
    calibrated bias — the HL carries it now (the §21.3 decision), so the
    position gate passes as-written; the separation locks small (< 0.1 NM
    over 10 min), not at the old drift floor."""
    cmds = parse_file(EXAMPLES / "long_cruise.txt")
    out = run_both(cmds, V0=0.0, until=600.0)
    m = metrics(out["ll"], out["hl"])
    assert abs(m["mean_speed_pct"]["hl"]) < 0.01
    assert m["fatigue"]["ll"] > 0.95 and m["fatigue"]["hl"] > 0.95
    sep = m["position_sep"]["hl"]
    assert sep < 0.1, f"position gate moved: {sep:.2f} NM"
    # and the tables carry the tolerance source label
    from harness.comparator import equivalence_table

    table = equivalence_table(out["ll"], out["hl"], out["meta"])
    assert out["meta"]["calibration"] in table and "PASS" in table


def test_turn_stream_runs():
    """A g1-style stream through the harness: D metric on both sims."""
    rate = rate_for_speed("Olympias", 6.0, n_oars=170)
    out = run_both(turn_stream(rate, ("port", 1.0)), V0=6.0 * KT, until=300.0)
    m = metrics(out["ll"], out["hl"])
    d_ll, d_hl = m["turn_D"]["ll"], m["turn_D"]["hl"]
    assert abs(d_ll - 89.7) < 1.0  # the LL's own anchor
    assert abs(d_hl / d_ll - 1.0) < 0.05  # the Level-2 gate


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
