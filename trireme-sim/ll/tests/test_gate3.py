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
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT
from ll.ship import Ship, rate_for_speed, run_turn
from commands.parser import parse_file

passed = 0


def check(label, fn):
    global passed
    fn()
    passed += 1
    print(f"ok - {label}")


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

def t_g1():
    r = turn(6.0, rate=R6, helm=("port", 1.0))
    assert 89.4 * 0.93 <= r["D"] <= 89.4 * 1.07, f"G1 D = {r['D']:.1f} m"
check("G1 full-rudder turn: D = 93.5 m vs 89.4 anchor (+4.6%)", t_g1)


def t_f1():
    r = turn(6.0, rate=R6, helm=("port", 22.5 / 67.5))
    assert 111.9 * 0.93 <= r["D"] <= 111.9 * 1.07, f"F1 D = {r['D']:.1f} m"
check("F1 22.5-deg turn: D = 117.2 m vs 111.9 anchor (+4.7%)", t_f1)


def t_tightest():
    r = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("starboard", 1.0))
    assert 62.0 * 0.90 <= r["D"] <= 62.0 * 1.10, f"tightest D = {r['D']:.1f} m"
    assert r["V_end"] < 6.5, "tightest turn must decelerate (hold brake)"
check("tightest one-side-stops: D = 64.4 m vs 62 anchor (+3.9%)", t_tightest)


# --- 2. oar-only turns (no anchors — physical consistency, oQ-3) ---

def t_oar_hold():
    r = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("midship", 0.0))
    assert r["track"][1] > 0, "starboard hold must turn toward starboard"
    assert 60.0 <= r["D"] <= 130.0, f"oar-hold D = {r['D']:.1f} m"
check("oar-only hold: turns toward the stopped side, D ~ 93 m", t_oar_hold)


def t_back_water():
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
check("back-water: degenerates at speed; active + tighter at low speed", t_back_water)


# --- 3. dynamics properties ---

def t_trim():
    ship = Ship(rate=R6)
    ship.V = 6.0 * KT
    for _ in range(int(300 / 0.01)):
        ship.step(0.01)
    assert abs(ship.psi) < 0.5 * math.pi / 180, f"heading drift {ship.psi*180/math.pi:.2f} deg"
    assert abs(ship.y) < 5.0, f"lateral drift {ship.y:.1f} m"
check("symmetric crew, no rudder: course held (<0.5 deg in 300 s)", t_trim)


def t_speed_independent():
    """The rudder turn diameter is speed-independent (Q ∝ v², ω ∝ v) — check
    the same helm at 5.5 kt gives the same D within 10 %."""
    r6 = rate_for_speed("Olympias", 6.0, n_oars=170)
    r55 = rate_for_speed("Olympias", 5.5, n_oars=170)
    d6 = turn(6.0, rate=r6, helm=("port", 1.0))["D"]
    d55 = turn(5.5, rate=r55, helm=("port", 1.0))["D"]
    assert abs(d6 / d55 - 1) < 0.10, f"D(6kt) {d6:.1f} vs D(5.5kt) {d55:.1f}"
check("turn diameter speed-independent (D ∝ v/ω, Q ∝ v²)", t_speed_independent)


def t_time_history():
    """Time-domain: the tightest turn takes longer than the steady estimate
    (spin-up + deceleration) — the W5 caveat mechanism, now integrated."""
    r = turn(6.5, rate=RT, oar_state=("row", "hold"), helm=("starboard", 1.0))
    t_360 = 2 * r["t_turn"]
    assert t_360 > 60.0, f"t_360 = {t_360:.0f} s (steady estimate ~60 s)"
check("tightest 360-deg time > steady estimate (deceleration lengthens it)", t_time_history)


def t_script_smoke():
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
    assert 0.0 < snap["V"] / KT < 12.0, f"speed {snap['V']/KT:.2f} kt"
    assert abs(snap["x"]) < 4e4 and abs(snap["y"]) < 4e4
    assert snap["crew"]["star"]["state"] == "bank"   # final command executed
check("sample script runs on the Ship (parser → commands → physics)", t_script_smoke)


print(f"\n{passed} checks passed")
