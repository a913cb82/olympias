#!/usr/bin/env python3
"""Calibrate the 44.5-spm effective-pull time (T_DRIVE at the sprint rate).

Table 9.6 has no 44.5-spm entry (register A8), so the sprint prediction
spanned 7.9-8.8 kt. Single-point calibration: choose t_drive(44.5) so the LL
reproduces the trial's 8.2-8.3 kt at 44.5 spm with ~130 effective rowers
(ch.9). The trial speed is the anchor; t_drive is the unknown stroke
parameter.

Usage (from simulation/): python3 ll/calibrate_tdrive.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT

from ll.hull import equilibrium_speed

TARGET = 8.3  # kt — the ch.9 four-run sprint mean (8.2-8.3)


def main():
    lo, hi = 0.30, 0.45

    def v_star(td):
        return equilibrium_speed("Olympias", 44.5, n_oars=130, t_drive=td)["V"] / KT

    print(f"calibrating t_drive(44.5) so the LL hits {TARGET} kt @ 130 oars:")
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if v_star(mid) > TARGET:
            lo = mid
        else:
            hi = mid
    td = 0.5 * (lo + hi)
    print(
        f"  t_drive(44.5) = {td:.3f} s  ->  V* = {v_star(td):.2f} kt (target {TARGET})"
    )
    print("  vs the extrapolated 0.347 s (bracket 0.392 @ 36 spm .. 0.347);")
    print("  the calibrated 0.375 s = the value that reproduced the trial")
    print("  in the Gate-2 bracket analysis — now pinned instead of assumed.")


if __name__ == "__main__":
    main()
