#!/usr/bin/env python3
"""Surge-hull runs (Phase 1 Gate 2).

Usage (from simulation/):
    python3 ll/run_hull.py                       # anchored run @ 28.8 spm
    python3 ll/run_hull.py --table               # equilibrium table over rates
    python3 ll/run_hull.py --spm 44.5 --oars 130 # ch.9 sprint configuration
    python3 ll/run_hull.py --fh-max 700 --v0 0   # start-from-rest demo (provisional)

The hull is surge-only: m_app·dV/dt = N·F_oars(t,V) − D(V), Olympias rig,
hull = 1.0 (validated anchor). Targets are the hull=1.0 points: Table 9.6
(7.2 kt @ 28.8 spm, 8.2 kt @ 36 spm) and the ch.9 sprint (8.2–8.4 kt @
44.5 spm, ~130 effective rowers). ch.7 cruise rates (25.5/32.3) are Mark II
hull — printed as reference only, not acceptance.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT, OQ18

from ll.hull import equilibrium_speed, run_cruise

TARGETS = {
    25.5: (7.0, "ch.7 ref (Mark II hull)"),
    28.8: (7.2, "Table 9.6 / S6 anchor"),
    32.3: (8.0, "ch.7 ref (Mark II hull)"),
    36.0: (8.2, "Table 9.6"),
    44.5: (8.3, "ch.9 sprint (130 rowers)"),
}


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--spm", type=float, default=28.8)
    ap.add_argument("--oars", type=int, default=170)
    ap.add_argument("--t-end", type=float, default=600.0)
    ap.add_argument("--dt", type=float, default=0.01)
    ap.add_argument(
        "--fh-max",
        type=float,
        default=None,
        help="provisional rower force ceiling, N (oQ-13; demo only)",
    )
    ap.add_argument("--v0", type=float, default=None, help="start speed, kt")
    ap.add_argument("--table", action="store_true", help="equilibrium table over rates")
    args = ap.parse_args()

    if args.table:
        print(
            f"{'rate':>6} {'t_drive':>8} {'V* kt':>8} {'settled':>8} {'ripple':>8} "
            f"{'target':>8}  note"
        )
        for r, (tgt, note) in sorted(TARGETS.items()):
            eq = equilibrium_speed("Olympias", r, n_oars=args.oars)
            out = run_cruise("Olympias", r, t_end=300.0, dt=args.dt)
            print(
                f"{r:6.1f} {eq['t_drive']:8.3f} {eq['V'] / KT:8.2f} "
                f"{out['V_settled'] / KT:8.2f} {out['ripple'] / KT:8.2f} "
                f"{tgt:8.1f}  {note}"
            )
        print(f"\nnote: {OQ18}")
        return

    v0 = None if args.v0 is None else args.v0 * KT
    out = run_cruise(
        "Olympias",
        args.spm,
        t_end=args.t_end,
        dt=args.dt,
        fh_max=args.fh_max,
        n_oars=args.oars,
        v0=v0,
    )
    eq = out["eq"]
    print(
        f"run       : {args.spm} spm, {args.oars} oars, Olympias rig, hull=1.0, "
        f"t_end {args.t_end:.0f} s, dt {args.dt} s"
    )
    print(f"t_drive   : {eq['t_drive']:.3f} s [{out['t_drive_src']}]")
    print(
        f"mean-force equilibrium V* : {eq['V'] / KT:6.2f} kt  "
        f"(thrust/oar {eq['thrust_oar']:.2f} N, mean Fh {eq['mean_fh']:.0f} N)"
    )
    print(
        f"full-run settled V        : {out['V_settled'] / KT:6.2f} kt  "
        f"(coupling agreement {abs(out['V_settled'] / eq['V'] - 1) * 100:.2f} %)"
    )
    print(f"stroke surge ripple (p-p) : {out['ripple'] / KT:6.2f} kt")
    print(f"settle time (1 % band)    : {out['settle_time']:6.0f} s")
    print(f"peak handle force         : {out['peak_fh']:6.0f} N")
    if args.spm in TARGETS:
        tgt, note = TARGETS[args.spm]
        print(
            f"target                    : {tgt:6.1f} kt  ({note})  "
            f"[{out['V_settled'] / KT / tgt * 100:5.1f} %]"
        )
    if args.fh_max:
        print(
            "note: force ceiling (oQ-13) is a crude provisional clamp — "
            "kinematics unchanged; demo only"
        )


if __name__ == "__main__":
    main()
