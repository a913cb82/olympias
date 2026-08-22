"""Plan 1 — the force-driven oar, ship-level gates (P1.4/P1.5), the
PROMOTED default (Stream A, P1.6): the force mode IS the ship (the
kinematic commanded-kinematics mode stays as the labelled reference
layer). These tests lock the force-mode's emergent SHIP behaviour so a
physics change that silently shifts it fails:

  F2-1 the sprint: spoude at 44.5 spm from 8.5 kt — the 30-s burst holds
        >= 7.5 kt (the force mode's measured 7.65 vs the trials' 8.2-8.4
        — the sprint stays open with the named causes: the midship's
        straight-rudder drag + the demand geometry, VALIDATION §11),
        then the W' fades (V(900) < 0.9·V(30)).
  F2-2 the cruise triple (the T1 measurement, re-based to the OLYMPIAS's
        own chain): the force-mode equilibrium at 25.5/28.8/32.3 spm
        (hull=1.0 — the run_hull acceptance basis; the demand 7.43·r
        with the pull-length geometry cosC_mean) locks at
        6.65/7.13/7.62 kt — within ~1 % of the Olympias chain's
        (L=0.78, E=0.756: 6.57/7.15/7.69). The ch.7 triple itself is
        Shaw's MARK II table (his appendix: L=0.99, E=0.78, hull 1.08)
        — the Olympias's stroke is too short for it (ch.9's own claim);
        the force mode's flat -4.1 % at hull 1.0 / -6.3 % at 1.08 is
        that L basis, VALIDATION §11.
  F2-3 the rest start: from V=0 the first drives are slow (the equilibrium
        at low V — the catch deadspot is gone: the peak handle force stays
        at the demand), the launch is slower than the bulk-law envelope
        (Taylor's 5.5 kt @ 10 s), and the ship reaches cruise-ish.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from common.chain import KT, OAR_FAMILIES, hull_power
from ll.rower import TierCrew, Fh_MAX
from ll.ship import Ship

FAM = OAR_FAMILIES["old-zygian"]
DT = 0.005


def loop(ship, t_end, dt=0.01, v0_kt=0.0, on_step=None):
    """Step the ship (the G4 loop convention)."""
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
        if on_step:
            on_step(ship)
    return ship


# --- F2-1 the sprint burst + fade ---

def test_sprint_burst():
    s30 = loop(Ship(rate=44.5, force=True), 30, v0_kt=8.5)
    s = loop(Ship(rate=44.5, force=True), 900, v0_kt=8.5)
    assert s30.V / KT > 7.5, f"burst speed {s30.V/KT:.2f} kt"
    assert s.crew["port"].W_frac < 0.1, f"W_frac {s.crew['port'].W_frac:.2f}"
    assert s.V / KT < 0.9 * (s30.V / KT), \
        f"V(900) {s.V/KT:.2f} vs V(30) {s30.V/KT:.2f} — no fade"
    print(f"       force-mode sprint: V(30 s) {s30.V/KT:.2f} kt, "
          f"V(900 s) {s.V/KT:.2f} kt (kinematic: 7.45; trials 8.2-8.3)")


# --- F2-2 the cruise triple (the T1 measurement) ---

def force_mean_thrust(rate, vkt):
    crew = TierCrew("Olympias", 1, rate, 0.43,
                    pressure="chain", mit=FAM, force=True)
    V = vkt * KT
    t = 0.0
    while t < 4 * crew.oar.cycle:
        crew.step(DT, V)
        crew.end_of_step(DT)
        t += DT
    cyc0 = crew.oar.cycle_no
    fx = 0.0
    while crew.oar.cycle_no < cyc0 + 1:
        fx += crew.oar.step(DT, V).Fx * DT
    return fx / crew.oar.cycle


def force_equilibrium(rate, hull=1.0, n_oars=170):
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


TRIPLE = {25.5: 6.65, 28.8: 7.13, 32.3: 7.62}   # kt, hull=1.0 (measured)


def test_cruise_triple():
    for rate, ref in TRIPLE.items():
        v = force_equilibrium(rate)
        assert abs(v - ref) < 0.10, \
            f"{rate} spm: {v:.2f} kt vs the locked {ref:.2f}"
    # the T1 shape: the deficit is FLAT vs the ch.7 (the Mark II table)
    gaps = [8.0 - force_equilibrium(32.3, hull=1.08),
            7.0 - force_equilibrium(25.5, hull=1.08)]
    assert abs(gaps[0] - gaps[1]) < 0.5, \
        f"the deficit's rate-dependence changed: {gaps[0]:.2f} vs {gaps[1]:.2f} kt"
    print(f"       force-mode triple (hull=1.0): "
          f"{ {r: round(force_equilibrium(r), 2) for r in (25.5, 28.8, 32.3)} } kt "
          f"(the Olympias chain: 6.57/7.15/7.69 — within ~1 %; the ch.7's "
          f"7/7.5/8 is the Mark II table, the flat -4.1 % is the L basis)")


# --- F2-3 the rest start ---

def test_rest_start():
    ship = Ship(rate=44.5, force=True)
    pk = [0.0]
    vs = {}

    def obs(s):
        for crew in s.crew.values():
            pk[0] = max(pk[0], crew.last_fh)
        for tgt in (10, 60, 600):
            if abs(s.t - tgt) < 0.02:
                vs[tgt] = s.V / KT

    loop(ship, 600, v0_kt=0.0, on_step=obs)
    assert pk[0] <= Fh_MAX * 1.001, f"peak Fh {pk[0]:.0f} N"
    assert vs.get(10) is not None and vs[10] < 6.0, \
        f"launch too fast: V(10) {vs.get(10):.1f} kt (the bulk envelope 5.5)"
    assert vs.get(600) is not None and vs[600] > 3.0, \
        f"reaches cruise-ish: V(600) {vs.get(600):.1f} kt"
    print(f"       force-mode start: V(10) {vs.get(10):.2f}, "
          f"V(60) {vs.get(60):.2f}, V(600) {vs.get(600):.2f} kt, "
          f"peak Fh {pk[0]:.0f} N")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
