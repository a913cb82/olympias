"""W5 re-run: Taylor ch.31 model vs trial turns F1-F6 and G1-G5.

ch.31 section 3 ("Actual turns fitted by the model") describes the eleven
trial turns QUALITATIVELY.  The raw per-turn numbers (entry speed, applied
rudder angle, turn diameter, turn duration) are only in Coates et al. (1990,
87-88) tables F and G - a print-only report (*The Trireme Trials 1988*,
ISBN 0946897212) that we do not hold.  We therefore cannot reproduce Taylor's
per-turn fit cell-by-cell; that is logged as an open item (physical archive).

What this script DOES is run the model over the F/G scenario space implied by
ch.31 section 3 and check it against every quantitative anchor that IS
published in the book and the trial reports:

  DIAMETERS (Taylor's own validation targets, ch.31 s6.2 - the tactical
  numbers the whole analysis rests on):
    - tightest Olympias turn   62 m  (also 1.9 lengths = 61.2 m, Morrison 1988)
    - fast anastrophe         145 m  at 9.5 kt, 22.5 deg rudder, full crew
    - tight anastrophe         80 m  at 6.5 kt, full rudder, one side stops

  YAW RATE / TURN TIME (independent trial observations):
    - Morrison 1988: one-side rowing, 1.9 lengths, 360 deg in 128 s
      -> average speed = pi*61.2/128 = 1.50 m/s = 2.91 kt, yaw 2.81 deg/s
    - 1990 trials video / CS Monitor 1988: ~2.6-3 deg/s for fast tight turns

The model reproduces all three DIAMETER anchors to within 7% (this is the
headline W5 validation, already in manoeuvre.md Part 3).  The yaw-rate /
360-deg-time anchors are NOT reproduced by the steady-state constant-speed
turn: the model's omega is set by torque balance at a FIXED speed, whereas
the observed turns decelerate (the chapter says the tightest turn "halves
speed"), and the observed 360-deg time is an average over the whole
decelerating turn.  That is a documented caveat, not a fitted correction.
"""

import math
import sys

sys.path.insert(0, ".")
from manoeuvre_model import mark_iib, olympias

RAD2DEG = 180.0 / math.pi
LWL = 32.2  # Olympias waterline length, m (Table 31.1 row 6)


def report(vessel, label, vkt, phi, fac, one_side, target=None, note=""):
    d, w, drift = vessel.steady_turn(vkt, phi, fac, one_side=one_side)
    yaw = w * RAD2DEG
    t360 = 360.0 / yaw if yaw > 0 else float("inf")
    s = (
        f"  {label:30s} v={vkt:4.1f}kt phi={phi:4.1f}deg one={int(one_side)}"
        f"  D={d:6.1f} m  yaw={yaw:4.2f} deg/s  360t={t360:4.0f} s"
        f"  drift={drift:4.1f} deg"
    )
    if target is not None:
        err = (d - target) / target * 100
        s += f"  [D vs {target:3.0f}: {err:+5.0f}%]"
    if note:
        s += f"  {note}"
    print(s)
    return d, yaw, t360


print("=" * 120)
print(
    "W5 re-run: Taylor ch.31 model vs trial turns F1-F6 (Hellenic Navy) and G1-G5 (Trust crew)"
)
print("=" * 120)
op = olympias()
mb = mark_iib()

print("\n[1] Published anchors")
print("  Diameters (Taylor s6.2 validation targets):")
print("    62 m tightest Olympias   (also 1.9 x 32.2 m LWL, Morrison 1988)")
print("    145 m fast anastrophe at 9.5 kt, 22.5 deg, full crew (Mark IIb)")
print("    80 m tight anastrophe at 6.5 kt, full rudder, one side stops (Mark IIb)")
print("  Yaw rate / time (independent trial observations):")
print("    Morrison 1988: 1.9 lengths, 360 deg in 128 s -> avg 2.91 kt, 2.81 deg/s")
print("    1990 video / CS Monitor 1988: ~2.6-3 deg/s fast tight turns")

print("\n[2] Diameter anchors (the W5 headline validation)")
report(
    op,
    "tightest Olympias",
    6.5,
    67.5,
    1.4,
    True,
    target=62,
    note="one side stops, full rudder",
)
report(
    mb,
    "fast anastrophe",
    9.5,
    22.5,
    3.25,
    False,
    target=145,
    note="Mark IIb, full crew",
)
report(
    mb,
    "tight anastrophe",
    6.5,
    67.5,
    3.25,
    True,
    target=80,
    note="Mark IIb, one side stops",
)

print("\n[3] G-series (Trust crew, ch.31 s3): flat measured oar thrust 4-7 kt,")
print("    constant effective thrust through the turn.  Full rudder on G1-G3.")
for label, vkt, phi, one in [
    ("G1 full rudder full crew", 6.0, 67.5, False),
    ("G2 (low entry speed)", 5.5, 67.5, False),
    ("G3 (not completed)", 6.0, 67.5, False),
    ("G4", 6.0, 45.0, False),
    ("G5", 6.0, 45.0, False),
]:
    report(op, label, vkt, phi, 1.4, one)

print("\n[4] F-series (Hellenic Navy, ch.31 s3): wider variety of rudder angles;")
print("    F1 smallest rudder angle; F5/F6 thranites only (half crew, lower thrust).")
for label, vkt, phi, one in [
    ("F1 smallest rudder angle", 6.0, 22.5, False),
    ("F2 (low entry speed)", 5.5, 45.0, False),
    ("F3 45 deg", 6.0, 45.0, False),
    ("F4 45 deg", 6.0, 45.0, False),
    ("F5 thranites only", 5.5, 67.5, False),
    ("F6 thranites only", 5.5, 67.5, False),
]:
    report(op, label, vkt, phi, 1.4, one)

print("\n[5] Yaw-rate / turn-time reconciliation (documented caveat)")
report(
    op,
    "Morrison 1988 360-deg turn",
    2.91,
    67.5,
    1.4,
    True,
    note="obs 360t=128 s @ 2.91 kt avg; model 360t=70 s (steady, one-side)",
)
report(
    op,
    "same turn, entry speed",
    6.5,
    67.5,
    1.4,
    True,
    note="steady at constant 6.5 kt -> 360t=60 s; observed turn decelerates",
)
print("  -> model omega is set at constant speed; the real tightest turn")
print("     halves speed (ch.31 s6.2), so its mean yaw rate is ~2.8-3 deg/s,")
print("     i.e. 360 deg in ~120-130 s.  The model's DIAMETER still matches")
print("     62 m; matching the time history would need a full time-domain yaw")
print("     integration with deceleration (not part of Taylor's Excel model).")

print("\n[6] G1/G2 drift angle (ch.31 s2.2/3)")
report(
    op,
    "G1 drift, force balance",
    6.0,
    67.5,
    1.4,
    False,
    note="reported 15 +/- 2 deg (Taylor prefers ~7.8 deg from time-delay)",
)
