"""HL basics: structure, anchors, turns, burst, performance (the calibration protocol — simulation/AGENTS.md).

Run: python3 hl/tests/test_hl_basics.py  (from simulation/)

Contract (Level 2 first tolerances, the pair contract (simulation/AGENTS.md)):
  - the HL chases the LL's equilibrium speeds (< 1 % mean over cruise runs);
  - G1/F1/tightest/oar turn diameters within 5 % of the current LL values;
  - the spoude burst drains W' and fades to the P_crit ceiling;
  - deterministic, fast (minutes of ship-time per second of wall-clock),
    command API identical to the LL's.
The comparison runs use the LL at dt = 0.05 to keep the suite quick.
"""

import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from common.chain import KT
from commands.parser import parse_file
from hl.ship import Ship as HLShip
from ll.ship import Ship as LLShip
from ll.hull import equilibrium_speed

LL_TURN_D = {"g1": 89.7, "f1": 117.4, "tightest": 67.7, "oar-hold": 126.6}

STEADY_ANCHORS = {25.5: 5.13, 28.8: 5.55, 32.3: 6.02}   # LL settled, kt


def _ll_anchor(r):
    return equilibrium_speed("Olympias", r)["V"]


def _ll_run(rate, pressure, t_end, dt=0.05, V0_frac=0.9):
    """LL ship run; 1 Hz samples over the whole run (comparable with the
    HL's coarse step)."""
    ll = LLShip(rate=rate, pressure=(pressure, pressure))
    ll.V = V0_frac * _ll_anchor(rate)
    t, next_s, Vs = 0.0, 0.0, []
    while t < t_end:
        ll.step(dt)
        t += dt
        if t >= next_s:
            Vs.append(ll.V)
            next_s += 1.0
    return Vs


def _hl_run(rate, pressure, t_end, V0_frac=0.9):
    ship = HLShip(rate=rate, pressure=(pressure, pressure))
    ship.V = V0_frac * _ll_anchor(rate)
    t, next_s, Vs = 0.0, 0.0, []
    while t < t_end:
        ship.step(0.5)
        t += 0.5
        if t >= next_s:
            Vs.append(ship.V)
            next_s += 1.0
    return Vs


# ---------------------------------------------------------------------------
def test_api_parity_with_ll():
    """The same constructor shape and command verbs the LL accepts."""
    hl = HLShip(rate=30.0, pressure=("steady", "spoude"),
                oar_state=("row", "hold"), helm=("port", 0.5))
    cmds = parse_file(Path(__file__).resolve().parents[2]
                      / "examples" / "cruise_turn.txt")
    hl.run_script(cmds, V0=5.0 * KT)
    s = hl.snap()
    for key in ("t", "V", "omega", "psi", "x", "y", "rate", "crew", "helm"):
        assert key in s
    assert set(s["crew"]) == {"port", "star"}
    for side in ("port", "star"):
        for key in ("state", "pressure", "rate_eff", "W_frac", "limited"):
            assert key in s["crew"][side]
    assert s["calibration"].startswith(("bootstrap", "calib-")), s["calibration"]


def test_determinism():
    a, b = HLShip(), HLShip()
    cmds = parse_file(Path(__file__).resolve().parents[2]
                      / "examples" / "cruise_turn.txt")
    a.run_script(cmds, V0=5.0 * KT)
    b.run_script(cmds, V0=5.0 * KT)
    sa, sb = a.snap(), b.snap()
    for key in ("V", "psi", "x", "y", "rate"):
        assert sa[key] == sb[key], key
    assert sa["crew"]["port"]["W_frac"] == sb["crew"]["port"]["W_frac"]


# ---------------------------------------------------------------------------
def test_cruise_steady_vs_ll():
    """Steady pressure is the sustainable envelope (W' stays full in both
    sims): settled means within 1.5 % of the LL at the ch.7 rates."""
    for r in (25.5, 28.8, 32.3):
        hVs = _hl_run(r, "steady", 300.0)
        lVs = _ll_run(r, "steady", 300.0)
        h_mean = sum(hVs[-100:]) / len(hVs[-100:])
        l_mean = sum(lVs[-100:]) / len(lVs[-100:])
        assert abs(h_mean / l_mean - 1.0) < 0.015, r


def test_cruise_steady_settles_at_ll_level():
    """The HL's steady row reproduces the LL's measured settled levels."""
    for r, anchor in STEADY_ANCHORS.items():
        ship = HLShip(rate=r, pressure=("steady", "steady"))
        ship.V = 0.9 * _ll_anchor(r)
        t = 0.0
        while t < 300.0:
            ship.step(0.5)
            t += 0.5
        assert abs(ship.V / KT / anchor - 1.0) < 0.01, r


def test_spoude_short_run_vs_ll():
    """Before the W' drain matters (60 s), spoude cruise tracks the LL
    within 3 % (the approach transient shapes differ — HL-loose)."""
    hVs = _hl_run(28.8, "spoude", 60.0)
    lVs = _ll_run(28.8, "spoude", 60.0)
    h_mean = sum(hVs) / len(hVs)
    l_mean = sum(lVs) / len(lVs)
    assert abs(h_mean / l_mean - 1.0) < 0.03


def test_cruise_vs_ll_10min():
    """|mean speed| < 1 % over a 10-minute steady cruise at 28.8 spm."""
    hVs = _hl_run(28.8, "steady", 600.0)
    lVs = _ll_run(28.8, "steady", 600.0)
    h_mean = sum(hVs) / len(hVs)
    l_mean = sum(lVs) / len(lVs)
    assert abs(h_mean / l_mean - 1.0) < 0.01


def test_sprint_burst():
    """44.5 spm spoude: W' drains (~38 s from the measured drain rate)
    then the speed fades to the measured P_crit row (~6.4 kt)."""
    ship = HLShip(rate=44.5)
    ship.V = 0.9 * ship.curves.vstar(44.5, 1.0)
    t, v_hist = 0.0, []
    while t < 300.0:
        ship.step(0.5)
        t += 0.5
        v_hist.append((t, ship.V / KT, ship.W_frac))
    t_drained = next((t_ for t_, v, w in v_hist if w <= 0.05), None)
    assert t_drained is not None and t_drained < 120.0, "W' must drain"
    assert 6.0 < v_hist[-1][1] < 8.0, "fade to the P_crit row"
    assert v_hist[-1][2] <= 0.05, "tank still empty at the end"


# ---------------------------------------------------------------------------
def test_turn_diameters():
    """D = |y| at 180 deg within 5 % of the current LL turn values."""
    from ll.ship import rate_for_speed
    for name, d_ref in LL_TURN_D.items():
        cfg = dict(V0=6.0, oar_state=("row", "row"), helm=("port", 1.0),
                   n_oars=170)
        if name == "f1":
            cfg["helm"] = ("port", 22.5 / 67.5)
        elif name == "tightest":
            cfg = dict(V0=6.5, oar_state=("row", "hold"),
                       helm=("starboard", 1.0), n_oars=85)
        elif name == "oar-hold":
            cfg = dict(V0=6.5, oar_state=("row", "hold"),
                       helm=("midship", 0.0), n_oars=85)
        rate = rate_for_speed("Olympias", cfg["V0"], n_oars=cfg["n_oars"])
        ship = HLShip(rate=rate, oar_state=cfg["oar_state"], helm=cfg["helm"])
        ship.V = cfg["V0"] * KT
        while abs(ship.psi) < math.pi and ship.t < 3600.0:
            ship.step(ship.dt)
        assert abs(ship.y) / d_ref - 1.0 < 0.05, f"{name}: {abs(ship.y):.1f} vs {d_ref}"


# ---------------------------------------------------------------------------
def test_script_smoke_and_perf():
    """The shared example script runs, deterministically, fast."""
    cmds = parse_file(Path(__file__).resolve().parents[2]
                      / "examples" / "cruise_turn.txt")
    t0 = time.time()
    ship = HLShip()
    ship.run_script(cmds, V0=5.0 * KT)
    wall = time.time() - t0
    s = ship.snap()
    assert s["t"] > 1700.0                       # the script ran to the end
    assert 0.0 <= s["V"] / KT <= 12.0
    assert 0.0 <= s["crew"]["port"]["W_frac"] <= 1.0
    assert wall < 1.0, f"10-min run took {wall:.1f} s"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
