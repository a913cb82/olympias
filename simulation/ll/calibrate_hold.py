#!/usr/bin/env python3
"""Calibrate the hold-water brake fraction (HOLD_FRAC) against both trial
anchors.

The tightest Olympias turn (Morrison 1988): D = 62 m AND 360 deg in 128 s —
mean speed 2.9 kt, i.e. the speed HALVES from the 6.5-kt entry. The trial was
a max-effort sprint turn: the sprint protocol (44.5 spm spoude, W' fade) +
the held-blade brake. The brake's yaw arm is the athwartships station arm
(~1.5 m), NOT the fitted 4.8 m thrust lever (which folds in drift/lateral
dynamics — register C3 refinement).

Usage (from simulation/): python3 ll/calibrate_hold.py [--f-max 0.30]
"""

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT

from ll.ship import Ship

D_ANCHOR = 62.0  # m — tightest Olympias turn (Morrison 1988)
T360_ANCHOR = 128.0  # s — 360 deg turn time (Morrison 1988)


def run_turn_360(ship, dt=0.02, max_t=600.0):
    """Sprint-protocol tightest turn; return (D, t_360, V_360) with
    D = max|y| over the turn (the lateral excursion at 360 deg is ~0 for a
    closed circle)."""
    ymax = 0.0
    while abs(ship.psi) < 2 * math.pi and ship.t < max_t:
        ship.step(dt)
        ymax = max(ymax, abs(ship.y))
    return ymax, ship.t, ship.V / KT


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--f-max", type=float, default=0.30)
    ap.add_argument("--f-min", type=float, default=0.02)
    ap.add_argument("--steps", type=int, default=14)
    args = ap.parse_args()

    print(
        f"sprint protocol (44.5 spm spoude, W' fade, one side holds, "
        f"full rudder); anchors: D = {D_ANCHOR:.0f} m, t_360 = {T360_ANCHOR:.0f} s"
    )
    print(f"{'hold_frac':>9} {'D m':>7} {'t_360 s':>8} {'V_360 kt':>9} {'score':>7}")
    best = None
    for i in range(args.steps + 1):
        f = args.f_min + (args.f_max - args.f_min) * i / args.steps
        ship = Ship(
            rate=44.5, oar_state=("row", "hold"), helm=("starboard", 1.0), hold_frac=f
        )
        ship.V = 6.5 * KT
        D, t360, V = run_turn_360(ship)
        score = abs(D - D_ANCHOR) / D_ANCHOR + abs(t360 - T360_ANCHOR) / T360_ANCHOR
        print(f"{f:9.3f} {D:7.1f} {t360:8.1f} {V:9.2f} {score:7.3f}")
        if best is None or score < best[0]:
            best = (score, f, D, t360, V)
    print(
        f"\nbest: hold_frac = {best[1]:.3f} -> D = {best[2]:.1f} m "
        f"(anchor 62), t_360 = {best[3]:.1f} s (anchor 128), "
        f"V_360 = {best[4]:.2f} kt (trial mean 2.9)"
    )
    print("residual: t_360 caps near 85 s across the sweep — the fitted")
    print("Omega = 5e6 kg m2 s spins the ship ~1.5x too fast in the")
    print("decelerating-drift regime (register C1: Omega units/value flagged);")
    print("retuning Omega would break the diameter fits — kept as an open item.")


if __name__ == "__main__":
    main()
