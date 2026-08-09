#!/usr/bin/env python3
"""Turn scenarios for the 170-oar ship (Phase 1 Gate 3).

Usage (from simulation/):
    python3 ll/run_turn.py [scenario]     # g1 | f1 | tightest | oar-hold | oar-back | script
    python3 ll/run_turn.py --table        # all scenarios

Protocols: full-crew turns run at the speed-holding rate for the entry speed;
the one-side-stops turn at the one-side balance rate (85 oars). Anchors from
the W5 validation (fg-turns-rerun.md): G1 89.4 m, F1 111.9 m, tightest 62 m.
"""

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT
from ll.ship import Ship, rate_for_speed, run_turn
from commands.parser import parse_file

SCENARIOS = {
    "g1":        dict(V0=6.0, rate=lambda: rate_for_speed("Olympias", 6.0, n_oars=170),
                      helm=("port", 1.0), note="vs 89.4 m"),
    "f1":        dict(V0=6.0, rate=lambda: rate_for_speed("Olympias", 6.0, n_oars=170),
                      helm=("port", 22.5 / 67.5), note="vs 111.9 m"),
    "tightest":  dict(V0=6.5, rate=lambda: rate_for_speed("Olympias", 6.5, n_oars=85),
                      oar_state=("row", "hold"), helm=("starboard", 1.0), note="vs 62 m"),
    "oar-hold":  dict(V0=6.5, rate=lambda: rate_for_speed("Olympias", 6.5, n_oars=85),
                      oar_state=("row", "hold"), helm=("midship", 0.0), note="no anchor"),
    "oar-back":  dict(V0=6.5, rate=lambda: rate_for_speed("Olympias", 6.5, n_oars=85),
                      oar_state=("row", "back"), helm=("midship", 0.0), note="no anchor"),
}


def run_one(name: str) -> None:
    cfg = SCENARIOS[name]
    kw = {k: v for k, v in cfg.items() if k not in ("V0", "note", "rate")}
    kw["rate"] = cfg["rate"]()
    ship = Ship(**kw)
    ship.V = cfg["V0"] * KT
    r = run_turn(ship)
    print(f"{name:10s} D={r['D']:7.1f} m  t_180={r['t_turn']:6.1f} s  "
          f"V0={cfg['V0']:.1f} -> V_end={r['V_end']:4.2f} kt  {cfg['note']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", nargs="?", default="table", choices=list(SCENARIOS) + ["table", "script"])
    args = ap.parse_args()
    if args.scenario == "script":
        cmds = parse_file(Path(__file__).resolve().parents[1] / "examples" / "cruise_turn.txt")
        ship = Ship()
        ship.run_script(cmds, dt=0.02, V0=5.0 * KT)
        s = ship.snap()
        print(f"script cruise_turn.txt: t={s['t']:.0f} s  pos=({s['x']:.0f}, {s['y']:.0f}) m  "
              f"V={s['V']/KT:.2f} kt  heading={math.degrees(s['psi'])%360:.0f} deg  "
              f"crew={ {k: v['state'] for k, v in s['crew'].items()} }")
        return
    if args.scenario == "table":
        for name in SCENARIOS:
            run_one(name)
        return
    run_one(args.scenario)


if __name__ == "__main__":
    main()
