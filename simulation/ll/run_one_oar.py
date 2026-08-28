#!/usr/bin/env python3
"""Run one oar at a fixed hull speed and report the Gate-1 table.

Usage (from simulation/):
    python3 ll/run_one_oar.py [--rig Olympias|MarkIIb] [--v-kts 7.2] [--spm 28.8]
                              [--t-drive 0.430] [--dt 0.001] [--cycles 4]

Defaults reproduce the anchored Table 9.6 point (Olympias, 7.2 kt, 28.8 spm,
t_drive 0.430 s) and compare against the rigid-oar reference. Output uses the
rigid model's conventions: mean thrust per oar over the full cycle, handle
force RMS over the drive, ideal blade efficiency, peak blade force.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT, OQ18, RIGS, SPM, T_DRIVE, hull_power, rigid_stroke

from ll.oar import Oar, simulate


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--rig", default="Olympias", choices=sorted(RIGS))
    ap.add_argument("--v-kts", type=float, default=7.2)
    ap.add_argument("--spm", type=float, default=28.8)
    ap.add_argument(
        "--t-drive",
        type=float,
        default=None,
        help="effective pull time (s); default: Table 9.6 if known, else cycle/3",
    )
    ap.add_argument("--dt", type=float, default=0.001)
    ap.add_argument("--cycles", type=int, default=4)
    args = ap.parse_args()

    rig = RIGS[args.rig]
    t_drive = args.t_drive
    if t_drive is None:
        t_drive = T_DRIVE.get((args.rig, args.v_kts), 60.0 / args.spm / 3.0)
        src = "Table 9.6" if (args.rig, args.v_kts) in T_DRIVE else "cycle/3 (default)"
    else:
        src = "user"
    V = args.v_kts * KT

    got = simulate(Oar(rig, args.spm, t_drive), V, args.dt, args.cycles)

    print(
        f"rig       : {args.rig}  (lin {rig['lin']:.3f} m, lout {rig['lout']:.3f} m, "
        f"sweep {rig['sweep']:.1f} deg, area {rig['area']:.3f} m2)"
    )
    print(
        f"run       : {args.v_kts} kt ({V:.3f} m/s), {args.spm} spm, "
        f"t_drive {t_drive:.3f} s [{src}], dt {args.dt} s, {args.cycles} cycles"
    )
    print(f"mean thrust/oar : {got['mean_thrust']:7.2f} N")
    print(f"mean handle F   : {got['mean_fh']:7.1f} N  (RMS over drive)")
    print(f"peak blade F    : {got['fb_peak']:7.1f} N")
    print(f"blade eff       : {got['eff'] * 100:6.1f} %")

    need = hull_power(V, hull=1.0 if args.rig == "Olympias" else 1.08) / 170.0
    prop = got["mean_thrust"] * V
    print(
        f"prop W/man      : {prop:7.1f} W  vs hull need {need:7.1f} W "
        f"({prop / need * 100:5.1f} %)"
    )

    key = (args.rig, args.v_kts)
    if key in T_DRIVE and abs(SPM[args.rig][args.v_kts] - args.spm) < 0.01:
        ref = rigid_stroke(V, rig, args.spm, t_drive=t_drive)
        print(
            f"vs rigid model  : thrust {ref['mean_thrust']:6.2f} N "
            f"(d {abs(got['mean_thrust'] / ref['mean_thrust'] - 1) * 100:.2f} %), "
            f"Fh {ref['mean_fh']:6.1f} N (d {abs(got['mean_fh'] / ref['mean_fh'] - 1) * 100:.2f} %)"
        )
    if args.rig == "MarkIIb":
        print(f"note: {OQ18}")


if __name__ == "__main__":
    main()
