"""The Rev F anchors (the trials-report data via Braithwaite Rev F,
research/sources/olympias-simulation-report-rev-f/): the stationary
turn, the Kempf zig-zag overshoots, the thranite-only equilibrium, and
the rudder-drag cross-check. These are LOCKS on the measured state, not
acceptance gates — the anchor rows they compare to are mismatches
(recorded in VALIDATION §11.2/§11.3), so a change here means the turn
physics moved and the ledger rows must be re-measured.
"""

import math

from ll.ship import Ship


def _two_tier(ship, side, rowing, state="row"):
    """The Zygian+Thranite-only configuration: the thalmian tier rests
    on the rowing side(s)."""
    c = ship.crew[side]
    if not rowing:
        c.set_pressure("rest")
        return
    c.tiers["thalmian"].set_pressure("rest")


def _settled_turn(rate, port_act, star_act, t_end=600.0):
    """The settled yaw rate for a partial-crew turn from rest.
    port_act/star_act: ("row", True/False) or ("hold", ...) etc."""
    s = Ship(
        rate=rate, pressure=("spoude", "spoude"), oar_state=(port_act[0], star_act[0])
    )
    _two_tier(s, "port", port_act[1])
    _two_tier(s, "star", star_act[1])
    while s.t < t_end:
        s.step(0.02)
    return abs(s.omega) * 57.2958, s.V / 0.514444


def _kempf_overshoots(n_flips=8, t_end=3600.0):
    """The LL's Kempf zig-zag (helm 22.5, steady 28.8, targets ±20°):
    the heading overshoots past the targets. Returns the list."""
    s = Ship(rate=28.8, pressure=("steady", "steady"))
    s.V = 0.0
    while s.t < 600.0:
        s.step(0.02)
    s.helm_dir, s.helm_frac = "port", 22.5 / 67.5
    TARGET = math.radians(20.0)
    flips, overs, run_max, prev_psi = 0, [], 0.0, 0.0
    start_t = s.t
    while s.t < start_t + t_end and flips < n_flips:
        s.step(0.02)
        p = s.psi
        if s.helm_dir == "port" and prev_psi < TARGET and p >= TARGET:
            flips += 1
            if flips >= 2:
                overs.append(math.degrees(run_max) - 20.0)
            run_max = 0.0
            s.helm_dir = "starboard"
        elif s.helm_dir == "starboard" and prev_psi > -TARGET and p <= -TARGET:
            flips += 1
            if flips >= 2:
                overs.append(math.degrees(run_max) - 20.0)
            run_max = 0.0
            s.helm_dir = "port"
        run_max = max(run_max, abs(p))
        prev_psi = p
    return overs


def test_stationary_turn_in_place():
    """Rev F C7: one side's Z+T ahead vs the other's Z+T back at 27 spm —
    the in-place reading. Locked at the FORCE mode's measured 2.06 deg/s
    (the grounded hull + lever 2.00 m: thole mean 31·2.7+27·2.0+27·1.2/85;
    was 1.75 deg/s at NET 1.8 m, the trial's anchor 3.5 — the mismatch
    row, VALIDATION §11.2, re-measured with the grounded lever + force
    mode: the 0.31 deg/s increase is the 11% lever increase)."""
    om, v = _settled_turn(27.0, ("row", True), ("back", True))
    assert abs(om - 2.06) < 0.15, f"in-place stationary turn {om:.2f} deg/s"
    assert 1.0 < v < 3.0


def test_stationary_turn_one_side():
    """Rev F C7: one side's Z+T ahead vs rest — the 1.13 deg/s reading
    (was 1.06 at NET 1.8 m; the grounded 2.00 m adds 0.07 deg/s, still
    within the old 0.15 band — the re-measure)."""
    om, _v = _settled_turn(27.0, ("row", True), ("row", False))
    assert abs(om - 1.13) < 0.15, f"one-side stationary turn {om:.2f} deg/s"


def test_kempf_overshoots():
    """Rev F C8: the force mode's Kempf zig-zag overshoots — 9.2 then
    ~14.0-14.4 vs the trials' 8/7 (the mismatch row, VALIDATION §11.2 —
    the first overshoot now closes, +10 % vs the kinematic's +38 %; the
    later overshoots stay ~+80 %). Stream C B2 (grounded lever 2.00 m:
    9.2→9.2 first, 14.0→14.0 later — the lever 1.8→2.0 adds <0.1 deg; B3
    was 8.8/12.8 →9.2/14.0 for the mass shift)."""
    overs = _kempf_overshoots(n_flips=6)
    assert len(overs) >= 4
    assert abs(overs[0] - 9.2) < 1.0, f"first overshoot {overs[0]:.1f}"
    assert all(abs(o - 14.0) < 1.2 for o in overs[1:]), overs


def test_thranite_only_equilibrium():
    """Rev F D10: thranites only (62 oars) at 33.3 spm — the LL settles
    4.26 kt (grounded hull+lever: was 4.19 at NET 1.8, the lever does not
    affect the straight-line equilibrium — the 0.06 kt is the grounded
    mass/Iz re-measure, B3) vs the record's loose 3.3 kt reading [+?];
    a lock on the measured state, not a gate."""
    s = Ship(rate=33.3, pressure=("spoude", "spoude"), oar_state=("row", "row"))
    for side in ("port", "star"):
        for t in ("zygian", "thalmian"):
            s.crew[side].tiers[t].set_pressure("rest")
    while s.t < 900.0:
        s.step(0.02)
    assert abs(s.V / 0.514444 - 4.26) < 0.1


def test_rudder_drag_cross_check():
    """Rev F C3: the trials' rudder-only fit 137v² + 0.65v (v in m/s) vs
    our rudder_straight 39.4 per kt² — measured +8-9 % at 5-8 kt; an
    independent confirmation of the constant."""
    from common.chain import VESSELS

    v = VESSELS["Olympias"]
    for kt in (5.0, 7.0, 8.0):
        vms = kt * 0.514444
        theirs = 137.0 * vms * vms + 0.65 * vms
        ours = v.rudder_straight * kt * kt
        assert 0.0 < (ours - theirs) / theirs < 0.12, (
            f"rudder drag @{kt} kt: ours {ours:.0f} vs theirs {theirs:.0f}"
        )
