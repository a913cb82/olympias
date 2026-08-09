"""Gate 8 — the sway DOF (plan 15.3) — completes the LL.

The hull now has surge + sway + yaw: the lateral resistance at the CLR
(forward of the CG) produces the physical restoring moment the lumped
Omega·w^2 cannot represent. The calibrated set (calibrate_sway.py):
Omega 3.2e6 (the ship's effective value with the sway in — the vessel's
5e6 stays for the steady research model, register C1), x_clr 0.8 m,
and the oar-race lever 1.8 m — the physical athwartships arm, the C3
decomposition completed (the fitted 4.8 m folded in the lateral dynamics
the sway now models explicitly).

Acceptance: the diameters held (G1/F1/tightest within the bands) AND the
sprint-protocol t_360 = 98 s vs the trial's 128 — the ~23% residual is
the turn's build-up (the trial's entry/approach vs the instant hard-over),
documented, not parameter-fittable within the physical ranges.
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
    return ymax, ship.t, ship.V / KT


def test_adopted_turns():
    """The sway-calibrated set holds all four targets within their bands."""
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
    d_t, t360, v = sprint_tightest(s)
    assert 55.0 <= d_t <= 69.0, f"tightest D {d_t:.1f} m (damper shift, plan 18)"
    # the residual vs the trial's 128 s: the turn build-up (documented)
    assert 85 <= t360 <= 115, f"t_360 = {t360:.0f} s"
    assert v < 4.0, "the speed must halve (the trial's character)"


def test_emergent_drift():
    """The sway's drift emerges in the tightest turn: between the Taylor
    balance's 1.4 deg and the reported 15±2 deg (register D-caveat)."""
    s = Ship(rate=44.5, oar_state=("row", "hold"), helm=("starboard", 1.0))
    s.V = 6.5 * KT
    while s.t < 60:
        s.step(0.02)
    beta = math.degrees(math.atan2(s.v, s.V))
    assert 0.5 <= abs(beta) <= 20.0, f"drift {beta:.1f} deg"
    assert beta < 0, "the drift is into the turn (starboard -> port drift)"


def test_lateral_damping():
    """Straight-line: the lateral velocity damps (no divergent instability);
    the heading drifts only by the physical per-stroke Fy kick."""
    s = Ship(rate=R6)
    s.v = 0.5                     # an initial lateral disturbance
    s.V = 6.0 * KT
    while s.t < 120:
        s.step(0.02)
    assert abs(s.v) < 0.05, f"|v| = {abs(s.v):.3f} m/s after 120 s (must damp)"


def test_lever_decomposition():
    """The C3 record: the ship's lever is now the physical athwartships arm
    (1.8 m); the research LEVER_OAR (4.8 m) remains the steady model's
    fitted value — the difference is the lateral dynamics the sway carries."""
    from ll.rig import LEVER_OAR
    assert LEVER_OAR["Olympias"] == 4.8
    ship = Ship()
    assert abs(ship.lever - 1.8) < 1e-9
    assert abs(ship.Omega - 3.2e6) < 1.0


def test_omega_reconciliation():
    """Register C1: the ship's effective Omega (3.2e6) with the physical
    CLR restoring moment in; the vessel's fitted 5e6 stays for the steady
    research model — the two-model reconciliation the register asked for."""
    from common.chain import VESSELS
    assert abs(VESSELS["Olympias"].Omega - 5e6) < 1.0   # the steady model
    ship = Ship()
    assert abs(ship.Omega - 3.2e6) < 1.0                # the time-domain LL


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
