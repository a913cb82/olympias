"""Oar-race yaw lever — RETAINED REFERENCE (not on the LL runtime path).

Taylor's fitted oar-race lever (Table 31.1 row 10: 4.8 m Olympias,
5.4 m Mark IIb) reproduced the one-side-stops trial turns (W5, ≤7 %) as

    Q_oar = (n/2) · lever · (fx_starboard − fx_port)     [M_z > 0 = port]

Status (register C3, Stream C B2): the 4.8 IS the blade-position arm — the
per-station layer measures mean blade arm 4.82 m — while the LL runtime
uses the grounded thole mean 2.00 m (common.chain.LEVER_GROUNDED: the NET
aggregated lever after local-flow damping) and per-station blade sums
(ll/stations.py). The 4.8 stays here as the steady-research-model fitted
reference and the decomposition record (blade 4.82 = Taylor 4.8; NET 1.8
sway-calibrated; thole mean 2.00 + 0.2 m damping correction). The per-oar
station plan (Coates Plan 8) is not in our sources (register B6); the
Figure 16 thole-plan decode refines the arms, not this reference.
Do not re-derive silently."""

LEVER_OAR = {"Olympias": 4.8, "MarkIIb": 5.4}  # Table 31.1 row 10, m
