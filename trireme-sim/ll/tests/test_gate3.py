"""Gate 3 — 170-oar surge+yaw ship against the turn validation chain.

Run: python3 tests/test_gate3.py  (from trireme-sim/)

Contract (plan §6 Level 1; W5 fg-turns-rerun anchors ≤7 %; plan §5):
  - Rudder turns (G1 89.4 m @ 6 kt full rudder; F1 111.9 m @ 22.5°) reproduced
    by the time-domain integrator within 7 %.
  - One-side-stops tightest turn (62 m @ 6.5 kt, full rudder) within 10 %,
    with the provisional hold-water brake (oQ-4, hold_frac=0.02 anchored to
    this diameter; the speed history needs the trial's rate + hold spectrum).
  - Oar-only turns: physically consistent (hold turns toward the stopped side,
    back-water turns tighter and decelerates; no trial anchors exist — oQ-3).
  - Yaw trim: symmetric crew holds course.
  - The model's steady turn diameter is speed-independent for the rudder term
    (Q ∝ v², ω ∝ v) — checked explicitly.
"""

import sys
import pytest
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT
from ll.ship import Ship, rate_for_speed, run_turn
from commands.parser import parse_file

R6 = rate_for_speed("Olympias", 6.0, n_oars=170)     # full-crew balance @ 6 kt
RT = rate_for_speed("Olympias", 6.5, n_oars=85)      # one-side balance @ 6.5 kt


def turn(V0_kt, **kw):
    ship = Ship(**kw)
    ship.V = V0_kt * KT
    return run_turn(ship)


def speed_after_kt(V0_kt, t_end, **kw):
    ship = Ship(**kw)
    ship.V = V0_kt * KT
    for _ in range(int(t_end / 0.01)):
        ship.step(0.01)
    return ship.V / KT


# --- 1. rudder turns (W5 anchors) ---

def test_g1():
    r = turn(6.0, rate=R6, helm=("port", 1.0))
    assert 89.4 * 0.93 <= r["D"] <= 89.4 * 1.07, f"G1 D = {r['D']:.1f} m"


def test_f1():
    r = turn(6.0, rate=R6, helm=("port", 22.5 / 67.5))
    assert 111.9 * 0.93 <= r["D"] <= 111.9 * 1.07, f"F1 D = {r['D']:.1f} m"


def test_tightest():
    r = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("starboard", 1.0))
    assert 62.0 * 0.90 <= r["D"] <= 62.0 * 1.10, f"tightest D = {r['D']:.1f} m"
    assert r["V_end"] < 6.5, "tightest turn must decelerate (hold brake)"


def test_tightest_sprint_protocol():
    """The trial's tightest turn was a max-effort sprint (Morrison 1988:
    D = 62 m AND 360 deg in 128 s — mean speed 2.9 kt, the speed halves).
    The sprint protocol + W' fade + the two-anchor hold fraction reproduce
    the diameter and the halving; the t_360 residual (85 vs 128 s) is the
    fitted-Omega yaw-resistance question (register C1), documented, not
    retuned."""
    ship = Ship(rate=44.5, oar_state=("row", "hold"), helm=("starboard", 1.0))
    ship.V = 6.5 * KT
    ymax = 0.0
    while abs(ship.psi) < 2 * math.pi:
        ship.step(0.02)
        ymax = max(ymax, abs(ship.y))
    assert 62.0 * 0.90 <= ymax <= 62.0 * 1.10, f"D = {ymax:.1f} m"
    assert ship.V / KT < 4.0, f"speed must halve: V_360 = {ship.V/KT:.2f} kt"
    assert 70 <= ship.t <= 110, f"t_360 = {ship.t:.0f} s (residual band)"


# --- 2. oar-only turns (no anchors — physical consistency, oQ-3) ---

def test_oar_hold():
    r = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("midship", 0.0))
    assert r["track"][1] > 0, "starboard hold must turn toward starboard"
    assert 60.0 <= r["D"] <= 130.0, f"oar-hold D = {r['D']:.1f} m"


def test_back_water():
    """Backing degenerates to the hold-brake at speed (the flow drag exceeds
    the rower's grip — the physiology); at low speed it is active and turns
    tighter than hold while decelerating."""
    r_hold = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("midship", 0.0))
    r_back = turn(6.5, rate=RT, oar_state=("row", "back"), helm=("midship", 0.0))
    assert r_back["track"][1] > 0
    assert abs(r_back["D"] / r_hold["D"] - 1) < 0.15, \
        f"back @6.5kt D {r_back['D']:.1f} must ~= hold D {r_hold['D']:.1f} (degenerates)"
    rl_hold = turn(2.0, rate=RT, oar_state=("row", "hold"), helm=("midship", 0.0))
    rl_back = turn(2.0, rate=RT, oar_state=("row", "back"), helm=("midship", 0.0))
    assert rl_back["D"] < rl_hold["D"], f"low-speed back D {rl_back['D']:.1f} < hold {rl_hold['D']:.1f}"
    # active backing cancels much of the forward thrust: the ship stays slow
    # (the forward-stroke side still dominates, so it does not stop)
    v_hold = speed_after_kt(2.0, 120, rate=RT, oar_state=("row", "hold"),
                            helm=("midship", 0.0))
    v_back = speed_after_kt(2.0, 120, rate=RT, oar_state=("row", "back"),
                            helm=("midship", 0.0))
    assert v_back < 0.6 * v_hold, f"V@120s back {v_back:.2f} vs hold {v_hold:.2f} kt"


# --- 3. dynamics properties ---

def test_trim():
    """With the sway DOF the symmetric crew still holds course, within the
    physical per-stroke lateral kick (the blade's net Fy — the finish side
    dominates) that a real helmsman would trim: no divergent instability
    (the lateral velocity damps), small heading drift over 5 min."""
    ship = Ship(rate=R6)
    ship.V = 6.0 * KT
    while ship.t < 300:
        ship.step(0.01)
    assert abs(ship.v) < 0.02, f"lateral velocity {ship.v:.3f} m/s (must damp)"
    assert abs(ship.psi) < 15.0 * math.pi / 180, \
        f"heading drift {ship.psi*180/math.pi:.1f} deg (physical Fy kick)"


def test_speed_independent():
    """The rudder turn diameter is speed-independent (Q ∝ v², ω ∝ v) — check
    the same helm at 5.5 kt gives the same D within 10 %."""
    r6 = rate_for_speed("Olympias", 6.0, n_oars=170)
    r55 = rate_for_speed("Olympias", 5.5, n_oars=170)
    d6 = turn(6.0, rate=r6, helm=("port", 1.0))["D"]
    d55 = turn(5.5, rate=r55, helm=("port", 1.0))["D"]
    assert abs(d6 / d55 - 1) < 0.10, f"D(6kt) {d6:.1f} vs D(5.5kt) {d55:.1f}"


def test_time_history():
    """Time-domain: the tightest turn takes longer than the steady estimate
    (spin-up + deceleration) — the W5 caveat mechanism, now integrated."""
    r = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("starboard", 1.0))
    t_360 = 2 * r["t_turn"]
    assert t_360 > 60.0, f"t_360 = {t_360:.0f} s (steady estimate ~60 s)"


def test_script_smoke():
    """The sample command script runs end-to-end on the Ship (first full
    command-language → LL pipeline). Start near cruise: rest-start needs the
    oQ-13 force ceiling (Gate-2 note)."""
    cmds = parse_file(Path(__file__).resolve().parents[2] / "examples" / "cruise_turn.txt")
    ship = Ship()
    ship.run_script(cmds, dt=0.02, V0=5.0 * KT)
    snap = ship.snap()
    for k, v in snap.items():
        if isinstance(v, float):
            assert math.isfinite(v), f"non-finite {k}"
    # the ship may end slightly astern after the back-water manoeuvre (the
    # sway + the astern thrust) — the speed magnitude must stay sane
    assert abs(snap["V"] / KT) < 12.0, f"speed {snap['V']/KT:.2f} kt"
    assert abs(snap["x"]) < 4e4 and abs(snap["y"]) < 4e4
    assert snap["crew"]["star"]["state"] == "bank"   # final command executed


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
