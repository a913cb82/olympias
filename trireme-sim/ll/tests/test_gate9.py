"""Gate 9 — the turn build-up (plan 17).

The helm and the oar-state transitions are no longer instant: the rudder
builds up like a human action (the helmsman's reaction + the tiller travel,
tau_rud, with a strength clamp — the rower-strength scale reused) and the
held blades' brake ramps over the oar-state transition (tau_hold — the
stroke finishes, the blades re-enter in the hold pose).

Honest finding from the calibration: the build-up's quantitative
contribution to the tightest t_360 is small (98 -> 100 s — the ramps
overlap the W' fade which dominates the timing). The residual to the
trial's 128 s is dominated by the yaw torque balance and the speed
profile (the trial's mean 2.96 kt vs our ~4.1 kt) — the next candidate is
a LINEAR yaw-damping term (register C1: the printed units fit a linear
coefficient) — documented, not fitted.

Gates: G9-1 the helm ramp; G9-2 the helmsman clamp; G9-3 the brake ramp;
G9-4 the adopted turns with the build-up; G9-5 regression.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT
from ll.ship import Ship, run_turn, rate_for_speed

R6 = rate_for_speed("Olympias", 6.0, n_oars=170)


def sprint_tightest(ship, max_t=600.0):
    ymax = 0.0
    while abs(ship.psi) < 2 * math.pi and ship.t < max_t:
        ship.step(0.02)
        ymax = max(ymax, abs(ship.y))
    return ymax, ship.t


def test_helm_ramp():
    """The rudder builds up (first-order with tau_rud): 95 % of the target
    within 3·tau_rud; the yaw rate grows gradually, not as a step."""
    s = Ship(rate=R6, helm=("port", 1.0))
    s.tau_rud = 3.0
    s.V = 6.0 * KT
    for _ in range(int(3 * 3.0 / 0.02)):        # 3·tau_rud
        s.step(0.02)
    assert abs(s.phi) > 0.95 * 67.5, f"phi {s.phi:.1f} deg after 3·tau_rud"
    # the yaw accelerates gradually: at t = tau_rud the rate is below steady
    s2 = Ship(rate=R6, helm=("port", 1.0))
    s2.tau_rud = 3.0
    s2.V = 6.0 * KT
    while s2.t < 3.0:
        s2.step(0.02)
    w_early = abs(s2.omega)
    while s2.t < 60:
        s2.step(0.02)
    assert w_early < abs(s2.omega) * 0.7, \
        f"early yaw {w_early:.4f} vs steady {abs(s2.omega):.4f} (must grow)"


def test_helmsman_clamp():
    """The helmsman's strength (the clamp method): the tiller load limits
    the rudder angle at high speed (the rudder yields); dormant at the
    Olympias's speeds. (The full-ship version decelerates before the phi
    settles — the clamp is speed-dependent, so the method is the unit.)"""
    s = Ship(rate=R6, helm=("port", 1.0))
    s.V = 6.0 * KT
    assert s._helm_clamp(67.5) == 67.5, "no clamp at 6 kt"
    s.V = 11.0 * KT
    clamped = s._helm_clamp(67.5)
    assert 30.0 < clamped < 55.0, f"clamp at 11 kt = {clamped:.1f} deg"
    s.V = 20.0 * KT
    assert s._helm_clamp(67.5) < 20.0, "hard clamp at 20 kt"


def test_brake_ramp():
    """The held blades' brake builds over tau_hold (no step)."""
    s = Ship(rate=44.5, oar_state=("row", "hold"), helm=("starboard", 1.0))
    s.V = 6.5 * KT
    while s.t < 1.0:                      # half of tau_hold = 2.0
        s.step(0.02)
    frac = s.crew["star"].tiers["thranite"].brake_frac
    target = 0.05
    assert 0.3 * target < frac < 0.9 * target, f"brake_frac {frac:.4f} mid-ramp"
    while s.t < 10.0:
        s.step(0.02)
    frac = s.crew["star"].tiers["thranite"].brake_frac
    assert abs(frac - target) < 0.01 * target, f"brake_frac {frac:.4f} settled"


def test_adopted_turns_with_buildup():
    """The build-up in: the diameters stay in their bands; the tightest
    t_360 = ~100 s vs the trial's 128 — the residual re-diagnosed (the
    yaw torque balance + the speed profile dominate; the build-up's share
    is small ~2 s), documented in plan 17."""
    s = Ship(rate=R6, helm=("port", 1.0))
    s.V = 6.0 * KT
    d_g1 = run_turn(s)["D"]
    assert 83.1 <= d_g1 <= 95.7, f"G1 {d_g1:.1f} m"
    s = Ship(rate=R6, helm=("port", 22.5 / 67.5))
    s.V = 6.0 * KT
    d_f1 = run_turn(s)["D"]
    assert 104.1 <= d_f1 <= 119.7, f"F1 {d_f1:.1f} m"
    s = Ship(rate=44.5, oar_state=("row", "hold"), helm=("starboard", 1.0))
    s.V = 6.5 * KT
    d_t, t360 = sprint_tightest(s)
    assert 55.8 <= d_t <= 68.2, f"tightest D {d_t:.1f} m"
    assert 90 <= t360 <= 115, f"t_360 = {t360:.0f} s"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
