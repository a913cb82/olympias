"""The Level-2 acceptance locked as tests (plan §21.2 task K → regression
protection): every script's gate rows and every turn scenario, asserted
exactly as harness/run_validation.py judges them. The calibration is the
pinned latest; a code or calibration change that moves any row outside
its tolerance fails here. Runtime ~6-7 min (the LL at dt 0.05).

Run: python3 -m pytest harness/tests/test_equivalence_gates.py -q
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from common.chain import KT
from commands.parser import parse_file
from harness.comparator import equivalence_table, metrics
from harness.script import run_both, turn_stream
from ll.ship import rate_for_speed

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"

SCRIPTS = [
    ("long_cruise", "examples/long_cruise.txt", 0.0),
    ("sprint_turn", "examples/sprint_turn.txt", 0.0),
    ("wprime_burst", "examples/wprime_burst.txt", 0.0),
    ("cruise_turn", "examples/cruise_turn.txt", 5.0 * KT),
    ("three_nm", "examples/three_nm_cruise.txt", 0.0),
    ("tempo_loss", "examples/tempo_loss.txt", 0.0),
]

GATE_KEYS = ("mean_speed_pct", "t_3nm_pct", "fatigue_consumed_delta",
             "rate_eff_delta", "position_sep")


@pytest.mark.parametrize("name,path,v0", SCRIPTS,
                         ids=[s[0] for s in SCRIPTS])
def test_script_gates(name, path, v0):
    cmds = parse_file(EXAMPLES / Path(path).name)
    out = run_both(cmds, V0=v0)
    m = metrics(out["ll"], out["hl"])
    rows = []
    for key in GATE_KEYS:
        row = m[key]
        if row["hl"] is None:
            continue
        rows.append(f"{key} {row['hl']:+.3f} (tol {row['tol']})")
        assert abs(row["hl"]) < row["tol"], \
            f"{name}: {key} {row['hl']:+.3f} vs tol {row['tol']}"
    assert rows, f"{name}: no gated rows"


TURNS = [
    ("g1", 6.0, 170, ("port", 1.0), ("row", "row"), 0.05),
    ("f1", 6.0, 170, ("port", 22.5 / 67.5), ("row", "row"), 0.05),
    ("tightest", 6.5, 85, ("starboard", 1.0), ("row", "hold"), 0.05),
    ("oar-hold", 6.5, 85, ("midship", 0.0), ("row", "hold"), 0.05),
    ("oar-back", 6.5, 85, ("midship", 0.0), ("row", "back"), 0.05),
]


@pytest.mark.parametrize("name,v0_kt,n_oars,helm,oar_state,tol", TURNS,
                         ids=[t[0] for t in TURNS])
def test_turn_gate(name, v0_kt, n_oars, helm, oar_state, tol):
    rate = rate_for_speed("Olympias", v0_kt, n_oars=n_oars)
    cmds = turn_stream(rate, helm, oar_state)
    out = run_both(cmds, V0=v0_kt * KT, until=600.0)
    m = metrics(out["ll"], out["hl"])
    d_ll, d_hl = m["turn_D"]["ll"], m["turn_D"]["hl"]
    assert abs(d_hl / d_ll - 1.0) < tol, \
        f"{name}: D {d_hl:.1f} vs LL {d_ll:.1f} " \
        f"({(d_hl / d_ll - 1.0) * 100:+.1f} % vs the {tol * 100:.0f} % gate)"


def test_three_nm_gate_first_number():
    """The 3-NM crossing time, the Level-2 gate's first number (task D):
    the LL 1718.0 s vs the HL 1717.5 s — locked against the original."""
    cmds = parse_file(EXAMPLES / "three_nm_cruise.txt")
    out = run_both(cmds, V0=0.0)
    m = metrics(out["ll"], out["hl"])
    t_ll = m["t_3nm"]["ll"]
    t_hl = m["t_3nm"]["hl"]
    assert abs(t_ll - 1718.0) < 2.0, f"the LL's 3-NM time moved: {t_ll}"
    assert abs(t_hl / t_ll - 1.0) < 0.01, \
        f"the HL's 3-NM time moved: {t_hl} vs {t_ll}"


def test_wprime_position_closure():
    """The wprime position row (the sway-transient closure, this session):
    the HL's drift + kick + slow-decay model reproduces the LL's path to
    0.022 NM — locked with a generous regression bound (the old value was
    0.217)."""
    cmds = parse_file(EXAMPLES / "wprime_burst.txt")
    out = run_both(cmds, V0=0.0)
    m = metrics(out["ll"], out["hl"])
    sep = m["position_sep"]["hl"]
    assert sep < 0.1, f"wprime position regressed: {sep:.3f} NM"
    assert sep < 0.06, f"wprime position drifted from the closure: {sep:.3f}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
