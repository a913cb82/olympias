"""Hull machinery is hull-generic (the portability path).

common.ship_drawings._compute_hull takes ANY offsets list — a new ship's
lines go through the same Simpson machinery as Olympias (lateral plane,
CLR, J, volume, waterplane). This test runs it on two synthetic hulls
with closed-form answers (rectangular sections, 201 stations):

  box:   constant draft T            -> A = L*T, J = T*L^4/32, Cw = 1
  parab: parabolic draft, pointed ends -> A = (2/3)*L*T, J = T*L^4/96

plus the taper helper (1.0 / 2/3). Guards the generalisation: the
machinery must stay correct for hulls shaped nothing like a trireme.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.ship_drawings import _compute_hull, hull_taper

L, B, T = 30.0, 4.0, 1.5
N = 201


def _box():
    return [
        (L * i / (N - 1), [(0.0, 0.0), (0.0, B / 2), (T, B / 2)])
        for i in range(N)
    ]


def _parab():
    offs = []
    for i in range(N):
        x = L * i / (N - 1)
        keel = T - T * 4 * (x / L) * (1 - x / L)
        offs.append((x, [(keel, 0.0), (keel, B / 2), (T, B / 2)]))
    return offs


def test_box_barge_closed_forms():
    h = _compute_hull(_box(), L, L / 2, T)
    assert abs(h["a_lat"] / (L * T) - 1) < 1e-9
    assert abs(h["x_clr"] - L / 2) < 1e-6
    assert abs(h["J"] / (T * L**4 / 32) - 1) < 1e-6
    assert abs(h["vol"] / (L * B * T) - 1) < 1e-9
    assert abs(h["bwl"] - B) < 1e-9
    assert abs(h["cw"] - 1.0) < 1e-9
    assert abs(hull_taper(h["a_lat"], L, T) - 1.0) < 1e-9


def test_parabolic_draft_closed_forms():
    h = _compute_hull(_parab(), L, L / 2, T)
    assert abs(h["a_lat"] / ((2 / 3) * L * T) - 1) < 1e-9
    assert abs(h["x_clr"] - L / 2) < 1e-6
    assert abs(h["J"] / (T * L**4 / 96) - 1) < 1e-6
    assert abs(h["vol"] / ((2 / 3) * L * B * T) - 1) < 1e-9
    assert 0.99 <= h["cw"] <= 1.0  # pointed ends cost 0.3%
    assert abs(hull_taper(h["a_lat"], L, T) - 2 / 3) < 1e-9
