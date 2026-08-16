"""Gate 4 — the rower physiology layer (plan §12).

Run: python3 tests/test_gate4.py  (from simulation/)

Gates (plan §12):
  G4-1 sustained cruise: steady pressure keeps W' full and speed stable
        (25.5/28.8 spm are the sustainable envelope — P_crit, R&W ch.23).
  G4-2 sprint: spoude at 44.5 spm bursts (W' drains), then the power fades
        toward the sustainable cruise — the time-history the trials show.
  G4-3 rest start: short slow strokes (sweep shrinks, drive stretches), peak
        handle force <= Fh_max, no absurd acceleration.
  G4-4 backing: degenerates to the hold-brake at speed (telemetry locked).
  G4-5 asymmetric: an exhausted side strokes slower -> differential thrust ->
        yaw; telemetry shows the mean-limited stroke.
  G4-6 tightest-turn long run: W' drains at sprint effort -> speed fades
        (the "halves speed" mechanism).
  G4-7 impossible command: rate 50 from rest with W' = 0 -> tempo is lost
        (achieved < commanded; oQ-14's answer: physical consequence).
"""

import sys
import pytest
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT
from ll.ship import Ship, rate_for_speed
from ll.rower import Fh_MAX

def loop(ship, t_end, dt=0.01, v0_kt=0.0, on_step=None):
    """Step the ship with a per-step callback(crews, ship) — the crews are
    stepped first so the callback sees the current plan/force telemetry."""
    ship.V = v0_kt * KT
    while ship.t < t_end:
        fx = {}
        for side, crew in ship.crew.items():
            fx[side], _, _, _ = crew.step(dt, ship.V)
        for crew in ship.crew.values():
            crew.end_of_step(dt)
        q, drag, f_rud = rudder_q(ship)
        ship.hull_advance(dt, ship.n_side * (fx["port"] + fx["star"]),
                          ship.n_side * ship.lever * (fx["port"] - fx["star"]),
                          f_rud, q, drag)
        ship._keleustes(dt)
        if on_step:
            on_step(ship)
    return ship


def rudder_q(ship):
    """Current rudder torque, drag and lateral force from the helm state."""
    vkt = abs(ship.V) / KT
    if ship.helm_dir == "midship":
        return 0.0, ship.vessel.rudder_straight * vkt * vkt, 0.0
    phi = 67.5 * ship.helm_frac
    drag = ship.vessel.rudder_drag(vkt, phi, 1.4)
    f_rud = ship.vessel.rudder_coeff(phi) * drag
    q = f_rud * ship.vessel.lever_rudder
    if ship.helm_dir == "port":
        f_rud = -f_rud
        q = -q
    return q, drag, f_rud


# --- G4-1 sustained cruise ---

def test_sustained():
    for rate, wmin, vlo, vhi in [(25.5, 0.9, 4.0, 6.5), (28.8, 0.8, 4.5, 7.0)]:
        s = loop(Ship(rate=rate, pressure=("steady", "steady")), 1800, v0_kt=6.0)
        assert s.crew["port"].W_frac > wmin, \
            f"{rate} spm: W_frac {s.crew['port'].W_frac:.2f}"
        assert vlo < s.V / KT < vhi, f"{rate} spm: V {s.V/KT:.2f} kt"


# --- G4-2 sprint burst + fade ---

def test_sprint():
    s30 = loop(Ship(rate=44.5), 30, v0_kt=8.5)
    s = loop(Ship(rate=44.5), 900, v0_kt=8.5)
    assert s.crew["port"].W_frac < 0.1, f"W_frac {s.crew['port'].W_frac:.3f}"
    # the trials sustained 8.2-8.3 kt for ~45 s before fading; with
    # W' = 5 kJ the sim's burst window is ~43 s, then the speed decays
    assert s.V / KT < 0.9 * (s30.V / KT), \
        f"V(900) {s.V/KT:.2f} vs V(30) {s30.V/KT:.2f} kt"
    # the burst with the thalmian head-room (0.6 at 44.5) + the W' fade:
    # still well above the sustainable cruise, and the fade follows
    assert s30.V / KT > 7.8, f"burst speed {s30.V/KT:.2f} kt"


def test_sprint_peak():
    pk = [0.0]

    def obs(ship):
        for crew in ship.crew.values():
            pk[0] = max(pk[0], crew.last_fh)

    loop(Ship(rate=44.5), 30, v0_kt=8.5, on_step=obs)
    assert pk[0] <= Fh_MAX * 1.001, f"peak Fh {pk[0]:.0f} N > {Fh_MAX}"


# --- G4-3 rest start ---

def test_rest_start():
    ship = Ship(rate=44.5)
    stats = dict(pk=0.0, min_sweep=9.9, first=None, v10=None, v600=None)

    def obs(s):
        for crew in s.crew.values():
            stats["pk"] = max(stats["pk"], crew.last_fh)
            if crew.plan:
                stats["min_sweep"] = min(stats["min_sweep"], crew.plan.sweep)
                if stats["first"] is None:
                    stats["first"] = crew.plan
        if abs(s.t - 10) < 0.02:
            stats["v10"] = s.V / KT
        if abs(s.t - 600) < 0.02:
            stats["v600"] = s.V / KT

    loop(ship, 600, v0_kt=0.0, on_step=obs)
    assert stats["pk"] <= Fh_MAX * 1.001, f"peak Fh {stats['pk']:.0f} N"
    assert stats["min_sweep"] < 0.85 * math.radians(48.1), \
        f"min sweep {math.degrees(stats['min_sweep']):.1f} deg (stroke shortens at rest)"
    assert stats["first"] is not None and stats["first"].t_drive > 0.848, \
        "drive stretches at rest (tempo slot preserved)"
    # the physiology start is SLOWER than the bulk-law launch (Taylor's
    # validated acceleration is 5.5 kt @ 10 s, 9 kt @ 24 s); the ceiling
    # must keep it below that envelope, not below some arbitrary bound
    assert stats["v10"] is not None and stats["v10"] < 8.0, \
        f"launch too fast: V(10) {stats['v10']:.1f} kt (Taylor: 5.5 @ 10 s)"
    assert stats["v600"] is not None and stats["v600"] > 3.0, \
        f"reaches cruise-ish: V(600) {stats['v600']:.1f} kt"


# --- G4-4 backing telemetry ---

def test_back_hold():
    rt = rate_for_speed("Olympias", 6.5, n_oars=85)
    s = loop(Ship(rate=rt, oar_state=("row", "back"), helm=("midship", 0.0)),
             20, v0_kt=6.5)
    assert s.crew["star"].plan is not None
    assert s.crew["star"].plan.limited_by == "back-hold"


# --- G4-5 asymmetric (one side exhausted) ---

def test_asymmetric():
    s = Ship(rate=40.0)
    for t in s.crew["star"].tiers.values():
        t.W = 0.0                       # the starboard crew is exhausted
    max_gap = [0.0]

    def obs(ship):
        wp = ship.crew["port"].plan.omega if ship.crew["port"].plan else 0.0
        ws = ship.crew["star"].plan.omega if ship.crew["star"].plan else 0.0
        max_gap[0] = max(max_gap[0], wp - ws)

    loop(s, 180, v0_kt=5.0, on_step=obs)
    assert abs(s.psi) > 30.0 * math.pi / 180, f"psi {math.degrees(s.psi):.0f} deg"
    assert s.crew["star"].W_frac < 0.01, f"W_frac {s.crew['star'].W_frac:.4f}"
    # the exhausted side stroked slower (mean-limited) at some point — the
    # differential thrust that produced the yaw; a tiny deadspot refill may
    # snap it back (classic W' step behaviour), so check the max gap
    assert max_gap[0] > 0.1, f"no stroke-omega gap seen ({max_gap[0]:.3f})"


# --- G4-6 tightest long run ---

def test_tightest_long():
    rt = rate_for_speed("Olympias", 6.5, n_oars=85)
    s = Ship(rate=rt, oar_state=("row", "hold"), helm=("starboard", 1.0))
    s.V = 6.5 * KT
    vmax = 0.0
    while s.t < 900:
        s.step(0.01)
        vmax = max(vmax, s.V)
    assert s.crew["port"].W_frac < 0.1, f"W_frac {s.crew['port'].W_frac:.2f}"
    assert s.V / KT < 0.85 * vmax / KT, f"V(900) {s.V/KT:.2f} vs peak {vmax/KT:.2f} kt"


# --- G4-7 impossible command ---

def test_impossible_rate():
    s = Ship(rate=50.0)
    for side in ("port", "star"):
        for t in s.crew[side].tiers.values():
            t.W = 0.0                   # both crews exhausted
    first = {}

    def obs(ship):
        for side, crew in ship.crew.items():
            if side not in first and crew.plan:
                first[side] = crew.plan

    loop(s, 30, v0_kt=0.0, on_step=obs)
    assert first, "no stroke plan seen"
    plan = next(iter(first.values()))
    assert plan.limited_by == "tempo", f"limited_by {plan.limited_by}"
    assert plan.rate_eff < 50.0, f"achieved rate {plan.rate_eff:.1f} (cmd 50)"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
