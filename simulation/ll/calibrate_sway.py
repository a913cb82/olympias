#!/usr/bin/env python3
"""Plan 15.3: calibrate the sway parameters (Omega, CLR offset).

The acceptance: ONE parameter set satisfying BOTH the turn diameters
(G1 89.4 / F1 111.9 / tightest 62 m, within the gate bands) AND the
sprint-protocol tightest t_360 near the trial's 128 s. The sway's
physical restoring moment (the hull lateral resistance at the CLR) is
the term the lumped Omega·w^2 cannot represent; the pair fits both.

Usage (from simulation/): python3 ll/calibrate_sway.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT, VESSELS
from ll.ship import Ship, run_turn, rate_for_speed

D_G1, D_F1, D_T = 89.4, 111.9, 62.0
T360_T = 128.0


def sprint_tightest(ship, max_t=600.0):
    ymax = 0.0
    while abs(ship.psi) < 2 * math.pi and ship.t < max_t:
        ship.step(0.02)
        ymax = max(ymax, abs(ship.y))
    return ymax, ship.t


def turn(ship, V0_kt):
    ship.V = V0_kt * KT
    return run_turn(ship)


def score(omega, clr):
    r6 = rate_for_speed("Olympias", 6.0, n_oars=170)
    s = Ship(rate=r6, helm=("port", 1.0))
    s.clr_offset = clr
    d_g1 = turn(s, 6.0)["D"]
    s = Ship(rate=r6, helm=("port", 22.5 / 67.5))
    s.clr_offset = clr
    d_f1 = turn(s, 6.0)["D"]
    s = Ship(rate=44.5, oar_state=("row", "hold"), helm=("starboard", 1.0))
    s.clr_offset = clr
    s.V = 6.5 * KT
    d_t, t360 = sprint_tightest(s)
    sc = (abs(d_g1 - D_G1) / D_G1 + abs(d_f1 - D_F1) / D_F1
          + abs(d_t - D_T) / D_T + abs(t360 - T360_T) / T360_T)
    return sc, d_g1, d_f1, d_t, t360


def main():
    best = None
    print(f"{'Omega':>9} {'x_clr':>6} {'G1':>7} {'F1':>7} {'tD':>7} {'t360':>6} {'score':>7}")
    for omega in (2.5e6, 3.5e6, 4.5e6):
        for clr in (0.8, 1.2, 1.6, 2.0):
            orig = VESSELS["Olympias"].Omega
            VESSELS["Olympias"].Omega = omega
            try:
                sc, g1, f1, dt, t360 = score(omega, clr)
            finally:
                VESSELS["Olympias"].Omega = orig
            print(f"{omega/1e6:9.1f} {clr:6.2f} {g1:7.1f} {f1:7.1f} {dt:7.1f} {t360:6.0f} {sc:7.3f}")
            if best is None or sc < best[0]:
                best = (sc, omega, clr, g1, f1, dt, t360)
    print(f"\nbest: Omega = {best[1]/1e6:.2f} e6, x_clr = {best[2]:.2f} m -> "
          f"G1 {best[3]:.1f} (89.4), F1 {best[4]:.1f} (111.9), tightest D {best[5]:.1f} (62), "
          f"t_360 {best[6]:.0f} (128)")


if __name__ == "__main__":
    main()
