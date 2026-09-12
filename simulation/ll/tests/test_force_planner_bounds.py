"""Force-planner guardrail audit (goal lock): what shapes predictions?

The force stroke planner (TierCrew._plan_force) contains guardrails that
must never silently shape validated predictions: the Fh_max flip cap
(700 N, provisional), the tempo slot (T_REC_MIN), the sweep floor
(B_FLOOR_FRAC), W'-drained demand caps. Sweeping the envelope
(19.8-50 spm x pressures x 0-8 kt) shows:
  - limited_by == "none" and rate_eff == rate_cmd everywhere (full W');
    slowdowns come only from the W' tank (G4-2/G4-6), never the slot.
  - fh_peak (demand AND flip) stays <= 330 N << Fh_max 700 N: the clamp
    is inert across the whole envelope including 50 spm.
  - sweep is full for V >= 3 kt (cruise/manoeuvre/sprint regimes); below
    that the plan shortens the sweep to HOLD rate (short strokes at low
    speed, the G4-3 family) without ever breaching B_FLOOR.
If any guardrail starts binding inside validated regimes, these fail.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ll.rower import TierCrew
from common.chain import KT

RATES = [19.8, 25.5, 28.8, 32.3, 38.75, 44.5, 50.0]
PRESSURES = {
    19.8: "steady",
    25.5: "steady",
    28.8: "fast",
    32.3: "fast",
    38.75: "spoude",
    44.5: "spoude",
    50.0: "spoude",
}
KT = 0.51444


def _plan(rate, pressure, vkt):
    t = TierCrew("Olympias", 31, rate, 0.43, pressure=pressure, force=True)
    return t, t._plan_force(vkt * KT, t.sweep_cmd, t.lin, t.l_cp, t.k)


def test_no_tempo_or_force_limits_in_envelope():
    # validated envelope: trial rates through the 44.5 sprint
    for rate in [r for r in RATES if r <= 44.5]:
        for vkt in (3.0, 4.0, 6.0, 8.0):
            t, plan = _plan(rate, PRESSURES[rate], vkt)
            assert plan.limited_by == "none", (rate, vkt, plan.limited_by)
            assert plan.rate_eff == rate
            assert plan.sweep == t.sweep_cmd  # full sweep underway
            assert plan.fh_peak < t.Fh_max  # the 700 N clamp never binds


def test_beyond_trials_degrades_gracefully():
    # 50 spm (past the 44.5 trial max): the plan shortens sweep to hold
    # rate instead of snapping — rate kept, floor respected, cap unbound
    t, plan = _plan(50.0, "spoude", 3.0)
    assert t.B_floor <= plan.sweep <= t.sweep_cmd
    assert plan.rate_eff == 50.0
    assert plan.fh_peak < t.Fh_max


def test_low_speed_shortens_sweep_without_losing_rate():
    # below ~3 kt the drive outlasts the slot: the plan rows shorter to
    # hold the commanded rate (G4-3 family) — rate kept, floor respected
    for rate in RATES:
        t, plan = _plan(rate, PRESSURES[rate], 0.0)
        assert t.B_floor <= plan.sweep <= t.sweep_cmd
        assert plan.rate_eff == rate


def test_sweep_shrinks_only_from_rest():
    t, plan0 = _plan(44.5, "spoude", 0.0)
    assert plan0.sweep < t.sweep_cmd  # G4-3 rest-start mechanism
    for rate in RATES:
        t, plan = _plan(rate, PRESSURES[rate], 4.0)
        assert plan.sweep == t.sweep_cmd


def test_flip_cap_headroom():
    peaks = [
        _plan(rate, PRESSURES[rate], vkt)[1].fh_peak
        for rate in RATES
        for vkt in (0.0, 2.0, 4.0, 6.0, 8.0)
    ]
    assert max(peaks) < 700.0  # measured 330; the clamp is pure guardrail


def test_hill_demand_contract():
    """Hill-demand spike contract (OFF by default): normalized to 1.0 at
    the Gate-1 cruise point (7.2 kt) so the validated anchor is untouched
    by construction; bounded static boost; clamped floor; decreasing in V;
    default off everywhere (suite green with the code present proves it)."""
    from ll.rower import HILL_V0, HILL_VREF, hill_factor
    from ll.ship import Ship

    assert hill_factor(HILL_VREF) == 1.0
    assert abs(hill_factor(0.0) - 1 / (1 - HILL_VREF / HILL_V0)) < 1e-9
    assert hill_factor(20.0) == 0.05  # clamped floor
    assert hill_factor(3.0) > hill_factor(6.0) > 0.0
    s = Ship(rate=28.8)
    assert s.crew_p.tiers["thranite"].hill_demand is False
    s2 = Ship(rate=28.8, hill_demand=True)
    assert s2.crew_p.tiers["zygian"].hill_demand is True


def test_hill_flag_survives_commands():
    """Rate/pressure/state changes preserve the flag and it modulates
    demand (spot-checked vs flag-off at the same state)."""
    from ll.ship import Ship

    s = Ship(rate=28.8, hill_demand=True)
    s.V = 5.0 * KT
    for _ in range(500):
        s.step(0.02)
    s._set_rate(32.3)
    s.crew_p.set_pressure("fast")
    s.crew_s.set_pressure("fast")
    s.crew_p.set_state("row")
    for _ in range(500):
        s.step(0.02)
    for side in (s.crew_p, s.crew_s):
        for tier in side.tiers.values():
            assert tier.hill_demand is True
    s2 = Ship(rate=32.3, pressure=("fast", "fast"))
    s2.V = s.V
    t = s.crew_p.tiers["thranite"]
    t2 = s2.crew_p.tiers["thranite"]
    p1 = t._plan_force(s.V, t.sweep_cmd, t.lin, t.l_cp, t.k)
    p2 = t2._plan_force(s2.V, t2.sweep_cmd, t2.lin, t2.l_cp, t2.k)
    assert p1.fh_mean > p2.fh_mean  # V < 7.2 kt: Hill boosts demand
