#!/usr/bin/env python3
"""HL-vs-LL validation through the shared harness (the calibration protocol (simulation/AGENTS.md)).

Usage (from simulation/):
    python3 harness/run_validation.py             # the whole script set + turns
    python3 harness/run_validation.py --script examples/sprint_turn.txt
    python3 harness/run_validation.py --turns    # the five turn scenarios only

Runs each script on both simulators with the same commands, state and event
semantics, computes the Level-2 metrics (harness/comparator.py), and prints
the equivalence table per script plus the summary verdicts. The LL is the
oracle: any violation is either fixed in the HL or documented as an
HL-loose place (the HL — simulation/AGENTS.md) — the honesty contract is a code requirement.
"""

import argparse
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT
from commands.parser import parse_file
from harness.comparator import equivalence_table, metrics
from harness.script import run_both, turn_stream
from ll.ship import rate_for_speed

SCRIPTS = [
    ("long cruise (20 min, steady)", "examples/long_cruise.txt", 0.0, ()),
    ("sprint + turns (25 min)", "examples/sprint_turn.txt", 0.0, ()),
    ("W' burst + recovery (30 min)", "examples/wprime_burst.txt", 0.0, ()),
    ("sample cruise_turn.txt", "examples/cruise_turn.txt", 5.0 * KT,
     (7,)),           # the scoped back-tail bin (the HL's domain boundary)
    ("3-NM cruise (35 min)", "examples/three_nm_cruise.txt", 0.0, ()),
    ("tempo loss (exhausted sprint)", "examples/tempo_loss.txt", 0.0, ()),
    ("zig-zag (out-of-sample, task T10)", "examples/zigzag.txt", 0.0, ()),
]

TURNS = [
    ("g1", 6.0, 170, ("port", 1.0), ("row", "row")),
    ("f1", 6.0, 170, ("port", 22.5 / 67.5), ("row", "row")),
    ("tightest", 6.5, 85, ("starboard", 1.0), ("row", "hold")),
    ("oar-hold", 6.5, 85, ("midship", 0.0), ("row", "hold")),
    ("oar-back", 6.5, 85, ("midship", 0.0), ("row", "back")),
]


def run_script_table(path: str, V0: float, until=None,
                     exclude_bins=()) -> tuple[dict, str]:
    cmds = parse_file(Path(__file__).resolve().parents[1] / path)
    t0 = time.time()
    out = run_both(cmds, V0=V0, until=until)
    table = equivalence_table(out["ll"], out["hl"], out["meta"], title=path)
    m = metrics(out["ll"], out["hl"], exclude_bins=exclude_bins)
    return m, table + f"  ({time.time()-t0:.0f} s wall)\n"


def run_turn_table(name: str, V0_kt: float, n_oars: int, helm: tuple,
                   oar_state=("row", "row")) -> str:
    rate = rate_for_speed("Olympias", V0_kt, n_oars=n_oars)
    cmds = turn_stream(rate, helm, oar_state)
    out = run_both(cmds, V0=V0_kt * KT, until=600.0)
    m = metrics(out["ll"], out["hl"])
    t_ll = _turn_time(out["ll"])
    t_hl = _turn_time(out["hl"])
    d_ll, d_hl = m["turn_D"]["ll"], m["turn_D"]["hl"]
    pct = (d_hl / d_ll - 1.0) * 100.0 if d_ll else float("nan")
    ok = abs(d_hl / d_ll - 1.0) < 0.05 if d_ll else False
    return (f"| {name:9s} | {rate:6.1f} | {d_ll:7.1f} | {d_hl:7.1f} | "
            f"{pct:+5.1f} % | {t_ll:5.1f} | {t_hl:5.1f} | "
            f"{'PASS' if ok else 'VIOLATION'} |\n")


def _turn_time(rows):
    for r in rows:
        if abs(r["psi"]) >= math.pi:
            return r["t"]
    return float("nan")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--script", default=None, help="one script path")
    ap.add_argument("--turns", action="store_true", help="turn scenarios only")
    args = ap.parse_args()

    print(f"calibration: run_both -> {run_both([], V0=0.0)['meta']['calibration']}\n")

    violations = []
    if not args.turns:
        scripts = SCRIPTS
        if args.script:
            scripts = [("script", args.script, 5.0 * KT, ())]
        for title, path, v0, exclude_bins in scripts:
            m, table = run_script_table(path, v0, exclude_bins=exclude_bins)
            # the turn_D rows are meaningful only on the dedicated turn
            # scenarios (a mid-script crossing is contaminated by the LL's
            # untrimmed lateral drift — its own table is below)
            lines = [ln for ln in table.splitlines()
                     if not ln.startswith("| turn_D")]
            print("\n".join(lines))
            for key in ("mean_speed_pct", "t_3nm_pct",
                        "fatigue_consumed_delta", "rate_eff_delta",
                        "position_sep", "position_path",
                        "position_max", "bin_max", "bin_rms"):
                row = m[key]
                if row["hl"] is not None and abs(row["hl"]) >= row["tol"]:
                    note = ""
                    if key == "position_sep":
                        note = " (the HL carries the measured drift bias; " \
                               "the residual is the path fidelity)"
                    violations.append(f"{path}: {key} {row['hl']:+.3f} "
                                      f"(tol {row['tol']}){note}")

    print("| scenario | rate | D LL m | D HL m | diff | t180 LL s | t180 HL s | verdict |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for name, v0, n_oars, helm, oar_state in TURNS:
        s = run_turn_table(name, v0, n_oars, helm, oar_state)
        print(s, end="")
        if "VIOLATION" in s:
            violations.append(f"turn {name}: D out of the 5 % gate")

    print("\nviolations: " + ("none — all Level-2 first tolerances inside"
                              if not violations else "; ".join(violations)))


if __name__ == "__main__":
    main()
