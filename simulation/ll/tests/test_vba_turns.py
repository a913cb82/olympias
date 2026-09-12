"""D1 stage-2: VBA-model turn verdicts (independent model vs trials vs LL).

The validated port (research/lane-5-manoeuvre/braithwaite_model.py —
reproduces the sheet's stored 30 s run to 0.01%) runs G1/F1/tightest
analogues at both CN values. Pressures: 0.30 both sides (settles ~6 kt
straight — the cruise-effort mapping); tightest: port 0 / starboard 1
(the sheet's stored protocol, U0 = 4 m/s); helms in sheet radians.
VBA Y/Z signs are starboard+/clockwise+; magnitudes compared.

Protocols differ from the LL (sheet mass 45.38 t full load vs LL trial
40.95 t; lever 5.2 vs thole-mean 2.00; helm 67.0 vs 67.5 deg; no hold
brake; no sway oar force) — verdicts are directional, stated as such.

Verdicts locked here (measured 2026-09-12, posterior bands):
  (a) CN FLAG ADJUDICATED: CN = 0.4 (paper/comment) beats CN = 0.8 (code)
      on every turn (G1 100.7 vs 117.1; F1 134.9 vs 152.3; tightest 65.0
      vs 79.3 m) — the comment/paper value reproduces trials better.
  (b) Even CN = 0.4 turns WIDER than trials (+13/+21/+5%): the VBA model
      as-decoded lacks load-bearing turn physics (solved: its sway
      stiffness is ~11x weak, stage 1; no hold brake; huge helm drag).
      The LL's extra mechanisms (Taylor sway set, brake, validated FAC)
      are structurally necessary — corroborated by necessity.
  (c) BRACKET on the open t_360 item: tightest CN = 0.4 nails the half
      time (65 s vs ~64 implied) at +5% size; the LL nails the size
      (60.3 m) at ~75% time (too fast). Neither does both — the missing
      turn-speed physics sits between them.
  (d) top speed rudders-down 8.77 kt (CN-independent): coherent between
      the LL sprint (130 effective) and the workbook rudders-up 9.95.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "research" / "lane-5-manoeuvre"))

import braithwaite_model as vba

G67 = -1.1693705988362009  # sheet full helm, rad (67.0 deg)
G22 = -0.39269908169872414  # 22.5 deg
U6 = 6.0 * 0.51444


def _turn(out):
    for i, p in enumerate(out["psi"]):
        if abs(p) >= math.pi:
            return out["y"][i], out["t"][i], out["u"][i]
    raise AssertionError("no 180-deg crossing in window")


def test_port_reproduces_sheet():
    out = vba.simulate(4.0, t_end=30.0, cn=0.8)
    assert abs(out["x"][30] / 56.552596133878971 - 1) < 0.005
    assert abs(out["psi"][30] / 1.2037961904348116 - 1) < 0.005


def test_cn_flag_tightest():
    outs = {
        cn: vba.simulate(4.0, p_port=0.0, p_star=1.0, rudder_rad=G67,
                         t_end=900.0, cn=cn)
        for cn in (0.8, 0.4)
    }
    d08, t08, _ = _turn(outs[0.8])
    d04, t04, u04 = _turn(outs[0.4])
    assert 60.0 <= d04 <= 70.0  # 65.0 (+5% vs trials 62)
    assert 75.0 <= d08 <= 84.0  # 79.3 (+28%)
    assert d04 < d08  # the paper value wins on every turn
    assert 55.0 <= t04 <= 75.0  # 65 s vs ~64 implied (nails the time)


def test_cn_flag_g1_f1():
    for helm, anchor, lo04, hi04, lo08, hi08 in (
        (G67, 89.4, 95.0, 107.0, 110.0, 125.0),  # G1: 100.7 / 117.1
        (G22, 111.9, 128.0, 142.0, 145.0, 160.0),  # F1: 134.9 / 152.3
    ):
        outs = {
            cn: vba.simulate(U6, p_port=0.30, p_star=0.30, rudder_rad=helm,
                             t_end=900.0, cn=cn)
            for cn in (0.8, 0.4)
        }
        d08, _, _ = _turn(outs[0.8])
        d04, _, _ = _turn(outs[0.4])
        assert lo04 <= d04 <= hi04
        assert lo08 <= d08 <= hi08
        assert d04 < d08
        # wider than the trial anchor even at CN = 0.4 (structural verdict)
        assert d04 > anchor


def test_top_speed_and_effort_map():
    top = vba.simulate(0.5, p_port=1.0, p_star=1.0, rudder_rad=0.0, t_end=900.0)
    assert 8.5 <= top["u"][-1] / 0.51444 <= 9.0  # 8.77 rudders-down
    cruise = vba.simulate(0.5, p_port=0.30, p_star=0.30, rudder_rad=0.0, t_end=600.0)
    assert 5.8 <= cruise["u"][-1] / 0.51444 <= 6.2  # 5.99 (effort mapping)
