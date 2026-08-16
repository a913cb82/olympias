"""The Level-2 acceptance locked as tests (the definition of done (simulation/AGENTS.md) task K → regression
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
    ("long_cruise", "examples/long_cruise.txt", 0.0, (),
     {}, dict(mean_speed_pct=0.01, t_3nm_pct=0.01,
              fatigue_consumed_delta=0.05, rate_eff_delta=1.0,
              position_sep=0.1, bin_max=5.0, bin_rms=3.0)),
    ("sprint_turn", "examples/sprint_turn.txt", 0.0, (),
     dict(position_sep=0.30),       # annotated: the turn-phase composition
     dict(mean_speed_pct=0.01, t_3nm_pct=0.01,
          fatigue_consumed_delta=0.05, rate_eff_delta=1.0,
          bin_max=5.0, bin_rms=3.0)),
    ("wprime_burst", "examples/wprime_burst.txt", 0.0, (),
     {}, dict(mean_speed_pct=0.01, t_3nm_pct=0.01,
              fatigue_consumed_delta=0.05, rate_eff_delta=1.0,
              position_sep=0.1, bin_max=5.0, bin_rms=3.0)),
    ("cruise_turn", "examples/cruise_turn.txt", 5.0 * KT, (7,),
     dict(mean_speed_pct=0.035, fatigue_consumed_delta=0.20,
          bin_max=50.0, bin_rms=20.0),   # annotated: the back-tail boundary
     dict(rate_eff_delta=1.0, position_sep=0.1)),
    ("three_nm", "examples/three_nm_cruise.txt", 0.0, (),
     {}, dict(mean_speed_pct=0.01, t_3nm_pct=0.01,
              fatigue_consumed_delta=0.05, rate_eff_delta=1.0,
              position_sep=0.1, bin_max=5.0, bin_rms=3.0)),
    ("tempo_loss", "examples/tempo_loss.txt", 0.0, (),
     {}, dict(mean_speed_pct=0.01, t_3nm_pct=0.01,
              fatigue_consumed_delta=0.05, rate_eff_delta=1.0,
              position_sep=0.1, bin_max=5.0, bin_rms=3.0)),
    ("zigzag", "examples/zigzag.txt", 0.0, (),
     dict(mean_speed_pct=0.025, position_sep=0.45),  # annotated: the
     # out-of-sample's composition (the fishtail-reversal mix)
     dict(fatigue_consumed_delta=0.05, rate_eff_delta=1.0,
          bin_max=5.0, bin_rms=3.0)),
]


@pytest.mark.parametrize("name,path,v0,exclude,annotated,clean", SCRIPTS,
                         ids=[s[0] for s in SCRIPTS])
def test_script_gates(name, path, v0, exclude, annotated, clean):
    cmds = parse_file(EXAMPLES / Path(path).name)
    out = run_both(cmds, V0=v0)
    m = metrics(out["ll"], out["hl"], exclude_bins=exclude)
    for key, tol in clean.items():
        row = m[key]
        if row["hl"] is None:
            continue
        assert abs(row["hl"]) < tol, \
            f"{name}: {key} {row['hl']:+.3f} vs tol {tol}"
    for key, bound in annotated.items():
        row = m[key]
        if row["hl"] is None:
            continue
        assert abs(row["hl"]) < bound, \
            f"{name}: {key} {row['hl']:+.3f} vs the annotated bound {bound}"


TURNS = [
    ("g1", 6.0, 170, ("port", 1.0), ("row", "row"), 0.05),
    ("f1", 6.0, 170, ("port", 22.5 / 67.5), ("row", "row"), 0.05),
    ("tightest", 6.5, 85, ("starboard", 1.0), ("row", "hold"), 0.05),
    ("oar-hold", 6.5, 85, ("midship", 0.0), ("row", "hold"), 0.05),
    ("oar-back", 6.5, 85, ("midship", 0.0), ("row", "back"), 0.05),
]

# The settled orbit after the turn (the K20 finding, from the replay
# UI's oar-back view, closed by K22): all five turns now track the
# LL's settled orbit within ~1.1x — the oar-back's drained spiral is
# reproduced by the measured speed-dependent orbit (d_oar_v) plus the
# per-side tank sequence (mean D over t in [250, 350]: g1 84.8/88.0, f1
# 111.2/114.2, tightest 58.6/62.7, oar-hold 95.3/103.5, oar-back
# 40.4/43.0 — VALIDATION §9.3 item 7).
SETTLED_D_RATIO = {"g1": 1.30, "f1": 1.30, "tightest": 1.30,
                   "oar-hold": 1.30, "oar-back": 1.30}


def _settled_d_ratio(rows_ll, rows_hl, t0=250.0, t1=350.0) -> float:
    """Mean orbit diameter (2V/|omega|) over the settled window, HL/LL."""
    def mean_d(rows):
        ds = [2 * r["V"] / max(abs(r["omega"]), 1e-9)
              for r in rows if t0 <= r["t"] <= t1]
        return sum(ds) / len(ds)
    return mean_d(rows_hl) / mean_d(rows_ll)


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
    # the turn timing (task T3): t180 within the measured 20 % band —
    # the HL is systematically faster through the turn (the V(t)
    # fidelity; the measured residuals 7-17 % — the timing-loose row,
    # VALIDATION §11.4 T3)
    t_ll = _t180(out["ll"])
    t_hl = _t180(out["hl"])
    assert abs(t_hl / t_ll - 1.0) < 0.20, \
        f"{name}: t180 {t_hl:.0f} vs LL {t_ll:.0f} " \
        f"({(t_hl / t_ll - 1.0) * 100:+.0f} % vs the 20 % band)"
    # the settled orbit after the turn: the clean turns track the LL's
    # orbit within the 1.30x bound; oar-back is the annotated row at
    # 4.00x (the drained spiral — the documented HL-loose boundary,
    # VALIDATION §9.3 item 7 / §11.3 item 5)
    ratio = _settled_d_ratio(out["ll"], out["hl"])
    bound = SETTLED_D_RATIO[name]
    assert ratio < bound, \
        f"{name}: settled-orbit D ratio {ratio:.2f}x vs the " \
        f"{bound:.2f}x bound"
    # the crew fatigue through the turn (the K20 follow-up): the LL's
    # rowing side drains its W' in ~90 s of the one-side-stopped turn;
    # the HL's fresh-phase net (the measured net_fresh table) must keep
    # the depletion within 5 % of the LL's on every turn scenario
    fd = metrics(out["ll"], out["hl"])["fatigue_consumed_delta"]["hl"]
    assert fd is not None and abs(fd) < 0.05, \
        f"{name}: fatigue depletion delta {fd:+.3f} vs the 0.05 gate"


def _t180(rows):
    for r in rows:
        if abs(r["psi"]) >= math.pi:
            return r["t"]
    return float("nan")


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


SWEEP = [
    ("27spm steady", 27.0, "steady", ("midship", 0.0)),
    ("30spm steady", 30.0, "steady", ("midship", 0.0)),
    ("34spm fast", 34.0, "fast", ("midship", 0.0)),
    ("25.5 steady", 25.5, "steady", ("midship", 0.0)),
    ("32.3 spoude", 32.3, "spoude", ("midship", 0.0)),
    ("28.8 helm 1/3", 28.8, "steady", ("port", 1 / 3)),  # annotated:
    # the sustained-helm state (the turn-drag decel-fit leaves the
    # sustained floor +2.4 % — measured, documented)
]


ANNOTATED_SWEEP = {"28.8 helm 1/3": 0.035}


@pytest.mark.parametrize("name,rate,pressure,helm", SWEEP,
                         ids=[s[0] for s in SWEEP])
def test_sweep_midpoints(name, rate, pressure, helm):
    """The interpolation midpoints (task T6): the cells between the
    calibration's anchor rates/pressures, gated at the standard L2-1/L2-6
    tolerances. The M6 audit found the linear interpolation up to +4.6 %
    fast at the midpoints (the LL's non-monotone steady curve + the
    nonlinear helm drag); the calibration now carries the midpoint rows
    (PRESSURE_RATES extended) and the per-helm turn-drag curve — the
    gates hold on the locked subset."""
    import tempfile
    lines = ["0, rate, %g" % rate, "0, pressure, %s" % pressure]
    if helm[0] != "midship":
        lines.append("0, helm, %s, %g" % helm)
    lines.append("240, pressure, rest")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(lines) + "\n")
        p = f.name
    try:
        cmds = parse_file(Path(p))
        # the settled-state comparison (the interpolation's the target,
        # not the physiology-limited start — the 240-s cell's mean is
        # start-dominated otherwise): V0 = the LL's settled speed at the
        # cell (a 300-s settle, both sims)
        from ll.ship import Ship as LLShip
        v0_ship = LLShip(rate=rate, pressure=(pressure, pressure))
        while v0_ship.t < 300.0:
            v0_ship.step(0.05)
        out = run_both(cmds, V0=v0_ship.V)
        m = metrics(out["ll"], out["hl"])
        ms = m["mean_speed_pct"]["hl"]
        tol = ANNOTATED_SWEEP.get(name, 0.01)
        assert ms is not None and abs(ms) < tol, \
            f"{name}: mean {ms * 100:+.1f} % vs the {'annotated bound ' if tol > 0.01 else '1 % gate'}{tol * 100:.1f} %"
        sep = m["position_sep"]["hl"]
        assert sep < 0.1, f"{name}: position {sep:.3f} NM"
    finally:
        import os
        os.unlink(p)
