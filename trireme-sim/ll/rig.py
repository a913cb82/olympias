"""Oar-race yaw lever (Gate 3) — the validated torque scale for turning.

The per-oar station plan (Coates Plan 8) is not in our sources (uncertainties
register B6). Taylor's fitted oar-race lever (Table 31.1 row 10: 4.8 m
Olympias, 5.4 m Mark IIb) is the validated yaw-moment scale for
side-asymmetric oar forces:

    Q_oar = (n/2) · lever · (fx_port − fx_starboard)     [M_z > 0 = starboard]

which reproduces the one-side-stops trial turns (W5, ≤7 %). For mirrored
station distributions (which the rig is), side asymmetry in force is captured
exactly by this single parameter.

Open item (uncertainties register C3): the physical decomposition of the
4.8 m — the pure-surge athwartships arms are only ~1.5-2 m (outrigger
offsets), so the fitted lever likely folds in stopped-blade drag and drift
dynamics that a future sway/hold-water model would make explicit. The fitted
value is used as-is; do not re-derive silently.
"""

LEVER_OAR = {"Olympias": 4.8, "MarkIIb": 5.4}   # Table 31.1 row 10, m
