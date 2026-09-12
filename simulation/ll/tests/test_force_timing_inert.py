"""Force-mode timing inertness — the fitted schedule is causally dead (goal lock).

The promoted default (Ship(force=True)) predicts speeds and turns WITHOUT
the trial-fitted timing schedule: Table 9.6 T_DRIVE and
CALIBRATED_T_DRIVE_44_5 enter Oar only as t_drive/omega_cmd, which the
force phase machine (Oar._step_force) never reads — the drive ends at the
finish angle under the EOM, the recovery runs at the plan's omega_recover
(from rate + T_REC_MIN), the flip spans t_rise (pressure physics). The
kinematic path (force=False) is the only reader, and stays as the labelled
reference layer.

This test proves it end-to-end: scaling every t_drive_for value by 1.5x
(including the calibrated 44.5-spm branch) must leave force-mode
trajectories byte-identical. If any leak is introduced, this fails.
"""

from common.chain import KT
from ll.ship import Ship
import ll.ship as shipmod


def _run(rate, pressure, helm, V0, until, td_scale):
    orig = shipmod.t_drive_for
    shipmod.t_drive_for = lambda rn, spm: (orig(rn, spm)[0] * td_scale, "scaled-test")
    try:
        s = Ship(rate=rate, pressure=pressure, helm=helm)
        s.V = V0
        while s.t < until:
            s.step(0.02)
        return s.V, s.x, s.y, s.psi, s.omega
    finally:
        shipmod.t_drive_for = orig


def test_force_timing_schedule_inert():
    # cruise + the calibrated sprint point (44.5 spm uses CALIBRATED_T_DRIVE)
    for rate, pressure in [(28.8, ("steady", "steady")), (44.5, ("spoude", "spoude"))]:
        base = _run(rate, pressure, ("midship", 0.0), 3.0 * KT, 60.0, 1.0)
        scaled = _run(rate, pressure, ("midship", 0.0), 3.0 * KT, 60.0, 1.5)
        for b, sc in zip(base, scaled):
            assert b == sc, f"rate {rate}: fitted timing leaks into force mode"


def test_force_timing_schedule_inert_turn():
    base = _run(28.8, ("steady", "steady"), ("port", 1.0), 6.0 * KT, 120.0, 1.0)
    scaled = _run(28.8, ("steady", "steady"), ("port", 1.0), 6.0 * KT, 120.0, 1.5)
    for b, sc in zip(base, scaled):
        assert b == sc, "fitted timing leaks into force-mode turns"
