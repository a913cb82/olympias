"""Plan 1, P1.5 probe: the force-driven SHIP measurements.

1. The cruise triple: the force-mode equilibrium speeds at the ch.7 rates
   (25.5/28.8/32.3 spm, hull=1.08, the chain demand 7.43·r) vs the chain's
   7/7.5/8 kt — the T1 measurement: does the force layer move the LL's
   rate->power curve?
2. The sprint: Ship(force=True) at 44.5 spm — the 30-s burst speed vs the
   kinematic's 7.45 kt (the trials: 8.2-8.3) — with the W' fade.
3. The rest start: the ship from V=0 — the first minutes.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "simulation"))

from common.chain import KT, OAR_FAMILIES, RIGS, SPM, T_DRIVE, hull_power
from ll.rower import TierCrew
from ll.ship import Ship

FAM = OAR_FAMILIES["old-zygian"]
DT = 0.005


def force_mean_thrust(rate, vkt, rig_name="Olympias", n_cycles=5):
    """Cycle-mean thrust per oar at fixed V (the force mode, chain demand).
    The t_drive arg is unused in force mode (the drive emerges)."""
    crew = TierCrew(rig_name, 1, rate, 0.43,
                    pressure="chain", mit=FAM, force=True)
    V = vkt * KT
    t = 0.0
    while t < (n_cycles - 1) * crew.oar.cycle:
        crew.step(DT, V)
        crew.end_of_step(DT)
        t += DT
    cyc0 = crew.oar.cycle_no
    fx = 0.0
    while crew.oar.cycle_no < cyc0 + 1:
        fx += crew.oar.step(DT, V).Fx * DT
    return fx / crew.oar.cycle


def force_equilibrium(rate, hull=1.08, n_oars=170):
    """Bisection: n_oars·T̄(V) = D(V) with the force-driven oar."""
    def g(V):
        return n_oars * force_mean_thrust(rate, V / KT) \
            - hull_power(V, hull) / max(V, 1e-6)
    lo, hi = 0.5, 6.5
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) / KT


print("=== 1. the force-mode cruise triple (hull=1.08, chain demand) ===")
print(f"{'rate':>6} {'V force':>8} {'chain':>6} {'gap':>7}")
for rate in (25.5, 28.8, 32.3):
    chain_v = {25.5: 7.0, 28.8: 7.5, 32.3: 8.0}[rate]
    v = force_equilibrium(rate)
    print(f"{rate:6.1f} {v:8.2f} {chain_v:6.1f} {(v/chain_v - 1)*100:6.1f}%")

print()
print("=== 2. the sprint (Ship force=True, 44.5 spm) ===")
def loop(ship, t_end, dt=0.01, v0_kt=0.0):
    ship.V = v0_kt * KT
    while ship.t < t_end:
        fx = {}
        for side, crew in ship.crew.items():
            fx[side], _, _, _ = crew.step(dt, ship.V)
        for crew in ship.crew.values():
            crew.end_of_step(dt)
        vkt = abs(ship.V) / KT
        q, drag, f_rud = 0.0, ship.vessel.rudder_straight * vkt * vkt, 0.0
        ship.hull_advance(dt, ship.n_side * (fx["port"] + fx["star"]),
                          ship.n_side * ship.lever * (fx["port"] - fx["star"]),
                          f_rud, q, drag)
        ship._keleustes(dt)
    return ship

for force in (False, True):
    s = loop(Ship(rate=44.5, force=force), 30, v0_kt=8.5)
    s9 = loop(Ship(rate=44.5, force=force), 900, v0_kt=8.5)
    print(f"  force={force}: V(30 s) {s.V/KT:5.2f} kt   V(900 s) {s9.V/KT:5.2f} kt   "
          f"W_frac {s9.crew['port'].W_frac:.2f}")

print()
print("=== 3. the rest start (Ship force=True, 44.5 spm) ===")
s = loop(Ship(rate=44.5, force=True), 600)
pk = 0.0
s2 = Ship(rate=44.5, force=True)
for t in range(60000):
    fx = {}
    for side, crew in s2.crew.items():
        fx[side], fh, _, _ = crew.step(0.01, s2.V)
        pk = max(pk, fh)
    for crew in s2.crew.values():
        crew.end_of_step(0.01)
    vkt = abs(s2.V) / KT
    q, drag, f_rud = 0.0, s2.vessel.rudder_straight * vkt * vkt, 0.0
    s2.hull_advance(0.01, s2.n_side * (fx["port"] + fx["star"]),
                    s2.n_side * s2.lever * (fx["port"] - fx["star"]),
                    f_rud, q, drag)
    s2._keleustes(0.01)
    if t % 1000 == 0:
        pass
print(f"  V(10 s) {s2.V/KT if False else ''}", end="")
# sample at 10 s / 60 s / 600 s
import collections
vs = []
s3 = Ship(rate=44.5, force=True)
for i in range(60000):
    fx = {}
    for side, crew in s3.crew.items():
        fx[side], fh, _, _ = crew.step(0.01, s3.V)
    for crew in s3.crew.values():
        crew.end_of_step(0.01)
    vkt = abs(s3.V) / KT
    q, drag, f_rud = 0.0, s3.vessel.rudder_straight * vkt * vkt, 0.0
    s3.hull_advance(0.01, s3.n_side * (fx["port"] + fx["star"]),
                    s3.n_side * s3.lever * (fx["port"] - fx["star"]),
                    f_rud, q, drag)
    s3._keleustes(0.01)
    if i in (1000, 6000, 60000 - 1):
        vs.append(s3.V / KT)
print(f"  V(10 s) {vs[0]:5.2f}  V(60 s) {vs[1]:5.2f}  V(600 s) {vs[2]:5.2f} kt")
print(f"  peak Fh (first drive) {pk:.0f} N (Fh_MAX {700})")
