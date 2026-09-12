"""D1 stage-1: VBA-model vs LL static reconciliation (no integration).

The Braithwaite workbook's independent trial-tuned model
(research/lane-5-manoeuvre/braithwaite_model.py, ported from
vba_extracted.txt Modules 7/8) is compared against the LL's grounded
numbers WITHOUT running either model in time — dimensionalised
derivatives, the cross-flow damper, the rudder foil statics, the oar-law
anchors. Sign map: VBA sway/yaw are starboard+/clockwise+; the LL is
port+. Comparisons use magnitudes unless stated.

Verdicts locked here (measured 2026-09-12, posterior bands):
  (a) surge added mass: VBA 0.04+0.06*CB = 1.059 sits inside the
      independent band [1.02, 1.12] (spheroid bound 1.026, LL 1.10).
  (b) yaw-due-to-sway (CLR physics) AGREES within 35% — the restoring
      moment is robust across both derivations.
  (c) sway force DISAGREES ~11x (CGH Yv far below Taylor f_hull: CB 0.321
      is far outside Clarke's regression range — the workbook's own
      calibration absorbs it). Locked AS disagreement: do not "fix" by
      touching LL f_hull; the sway-force channel is the open drift item.
  (d) rudder straight drag agrees 8% (per-rudder x2 vs LL total).
  (e) applied-helm rudder forces diverge 2-7x (VBA flat plate at helm vs
      the LL's validated FAC/coeff) — stage 2 (VBA turn runs vs the
      trial-validated LL turns) must confront it.
  (f) cross-flow damper statics differ 2.5-5x (CN 0.4/0.8 vs taper-J);
      the VBA balance is linear-Nr-dominated, the LL's is cross-flow +
      CLR — static comparison cannot adjudicate the CN [?] flag; the
      trajectory comparison (stage 2) can.

Stage 2 (not here): integrate the VBA sim (transfer/updata scheme) and
run G1/F1/tightest + the top-speed curve against the LL.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "research" / "lane-5-manoeuvre"))

import braithwaite_model as vba
from common.chain import KT, VESSELS
from common import ship_drawings as sd

U6 = 6.0 * KT
LWL, BWL, T, CB = 32.35, 3.704, 1.10, sd.CB


def _ll_sway_moment_per_v():
    return sd.RHO * sd.A_LAT_TRIAL * U6 * sd.CLR_OFFSET_TRIAL


def test_surge_added_mass_band():
    c = vba.man_coefficients(LWL, BWL, T, sd.MASS_TRIAL, sd.IZ_TRIAL, CB, U6)
    assert abs(c["surge_frac"] - (0.04 + 0.06 * CB)) < 1e-9  # transcription
    assert 1.02 <= 1 + c["surge_frac"] <= 1.12  # spheroid 1.026 … LL 1.10


def test_yaw_moment_agrees_sway_force_does_not():
    c = vba.man_coefficients(LWL, BWL, T, sd.MASS_TRIAL, sd.IZ_TRIAL, CB, U6)
    yv_ll = sd.RHO * sd.A_LAT_TRIAL * U6
    nv_ll = _ll_sway_moment_per_v()
    assert 0.65 <= abs(c["Nv"]) / nv_ll <= 1.45  # CLR physics robust (1.27)
    assert 8.0 <= yv_ll / abs(c["Yv"]) <= 14.0  # structural gap (11.05)


def test_rudder_straight_agrees():
    f = vba.rudder_forces(-15.0, 0.0, 0.5, 0.75, 0.0, U6)
    ll_straight = sd.RUDDER_DRAG_STRAIGHT * 36.0
    assert abs(-2 * f["RX"] / ll_straight - 1) < 0.12  # 8% (per-rudder x2)


def test_rudder_applied_divergence_recorded():
    v = VESSELS["Olympias"]
    # 22.5 deg helm
    f22 = vba.rudder_forces(-15.0, 0.0, 0.5, 0.75, math.radians(22.5), U6)
    ll_drag22 = v.rudder_drag(6.0, 22.5, sd.RUDDER_FAC_FULL)
    ll_lat22 = v.rudder_coeff(22.5) * ll_drag22
    assert 1.4 <= (-2 * f22["RX"]) / ll_drag22 <= 2.1  # 1.74
    assert 4.0 <= (2 * f22["RY"]) / ll_lat22 <= 6.5  # 5.09
    # full helm
    f67 = vba.rudder_forces(-15.0, 0.0, 0.5, 0.75, math.radians(67.5), U6)
    ll_drag67 = v.rudder_drag(6.0, 67.5, sd.RUDDER_FAC_FULL)
    ll_lat67 = v.rudder_coeff(67.5) * ll_drag67
    assert 5.5 <= (-2 * f67["RX"]) / ll_drag67 <= 8.5  # 6.97
    assert 2.5 <= (2 * f67["RY"]) / ll_lat67 <= 4.0  # 3.24


def test_crossflow_static_gap_recorded():
    for cn, lo, hi in ((0.8, 4.5, 5.8), (0.4, 2.2, 2.9)):
        c = vba.man_coefficients(LWL, BWL, T, sd.MASS_TRIAL, sd.IZ_TRIAL, CB, U6, cn=cn)
        assert lo <= abs(c["Nr2"]) / sd.OMEGA_TRIAL <= hi  # 5.11 / 2.56


def test_oar_law_structure():
    z = vba.oar_forces(170, 4.8, 1.0, 1.0, 81.0, 9.252)
    assert z["surge"] == 0.0  # the 18-kt intercept
    assert z["sway"] == 0.0  # no sway force, by construction
    r = vba.oar_forces(170, 4.8, 1.0, 1.0, 81.0, 0.0)
    assert r["surge"] == 170 * 81.0  # the trials zero-speed anchor
    p = vba.oar_forces(170, 4.8, 1.0, 0.0, 81.0, 0.0)
    assert p["yaw"] < 0.0  # port-only pull yaws anticlockwise (VBA sign)


def test_port_self_checks():
    s = vba._self_check()
    assert s["oar_zero_at_intercept"] == 0.0
    assert s["rudder_zero_helm_lift"] == 0.0
    assert s["rudder_zero_helm_drag"] > 0.0
