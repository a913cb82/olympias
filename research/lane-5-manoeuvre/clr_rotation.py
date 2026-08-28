"""W5 Richard's alternative: rotation about the centre of lateral resistance.

Taylor ch.31 models yaw as rotation about the vertical axis through the
ship's centre of mass (c.g.); he explicitly flags (s2.2, book p.234) that
this "is a principal difference from the UCL model" (Rusling & Smith, pers.
com. 2006), which rotated about the centre of lateral resistance (CLR).

This module adds the CLR variant and quantifies the difference for the same
physics, so the only change is the rotation-point choice:

  - rudder lever arm:   L_rud  = lever_rudder + x   (rudder astern of c.g.)
  - one-side oar lever: L_oar  = |lever_oar - x|    (oar race fwd of c.g.)
  - hull lateral force passes through the CLR -> contributes no yaw moment
  - Omega (rotational resistance) kept at the trial-fitted value, isolating
    the pure geometric effect of the rotation-point choice.
  - I not needed (steady-state turn), so the parallel-axis inertia shift is
    noted but does not affect the steady diameter.

x = distance of CLR forward of the c.g. (m, +ve forward).  Realistic band:
Olympias LCG ~17.5 m from the stern post (ch.25) on LWL 32.2 m -> c.g. about
14.7 m from the bow; with the ram and long lateral plane the CLR sits ~0.5-2 m
further forward, so x in [0.5, 2.0] m.
"""

import math
import sys

sys.path.insert(0, ".")
from manoeuvre_model import mark_iib, olympias

RAD2DEG = 180.0 / math.pi
KT2MS = 0.514444
RHO = 1025.0


def steady_turn_about_clr(vessel, vkt, phi_deg, along_factor, one_side, x):
    """Steady turn with rotation about the CLR, x metres forward of the c.g.

    Returns (diameter_m, yaw_rate_dps, drift_deg)."""
    L_rud = vessel.lever_rudder + x
    L_oar = abs(vessel.lever_oar - x)
    f_rud = vessel.rudder_coeff(phi_deg) * vessel.rudder_drag(
        vkt, phi_deg, along_factor
    )
    q_rud = f_rud * L_rud
    q_oar = 0.5 * vessel.thrust(vkt) * L_oar if one_side else 0.0
    omega = math.sqrt(max(q_rud + q_oar, 0.0) / vessel.Omega)
    v = vkt * KT2MS
    R = v / omega
    need = vessel.m_app * v * v / R - f_rud
    arg = max(min(need / (RHO * vessel.A_lat * v * v), 1.0), -1.0)
    drift = math.degrees(math.asin(arg)) if v > 0 else 0.0
    return 2.0 * R, omega * RAD2DEG, drift


if __name__ == "__main__":
    print("Richard's alternative (rotation about CLR) vs Taylor (rotation about c.g.)")
    print("=" * 100)
    print(
        f"{'case':32s} {'x=c.g.':>13s} {'x=0.5':>12s} {'x=1.0':>12s} {'x=1.5':>12s} {'x=2.0':>12s}"
    )
    cases = [
        ("tightest Olympias [Oly]", olympias(), 6.5, 67.5, 1.4, True),
        ("fast anastrophe [MkIIb]", mark_iib(), 9.5, 22.5, 3.25, False),
        ("tight anastrophe [MkIIb]", mark_iib(), 6.5, 67.5, 3.25, True),
        ("G1 full rudder [Oly]", olympias(), 6.0, 67.5, 1.4, False),
        ("F1 small rudder [Oly]", olympias(), 6.0, 22.5, 1.4, False),
    ]
    for label, ves, vkt, phi, fac, one in cases:
        d0, y0, _ = ves.steady_turn(vkt, phi, fac, one_side=one)
        row = [f"{d0:6.1f}m/{y0 * RAD2DEG:4.2f}"]
        for x in (0.5, 1.0, 1.5, 2.0):
            d, y, _ = steady_turn_about_clr(ves, vkt, phi, fac, one, x)
            row.append(f"{d:6.1f}/{y:4.2f}")
        print(f"  {label:30s} {' | '.join(row)}")
    print("\n  diameter / yaw-rate (dps); x = CLR distance forward of c.g. (m).")
    print("  Effect of the rotation-point choice: <= ~5% on diameter across the")
    print("  realistic x band - and it moves the anastrophe diameters toward the")
    print("  published 145 / 80 m targets (fast anastrophe 151.8 -> ~143-149 m;")
    print("  tight anastrophe 74.6 -> ~76-83 m).  Consistent with Taylor's own")
    print("  statement that his c.g.-axis model and the UCL CLR-axis model agreed")
    print("  closely because both were fitted to the same trial data.")
