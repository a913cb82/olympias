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
