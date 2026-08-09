"""Gate 7 — the cant term and the slip assumptions (plan 16).

Run: pytest ll/tests/test_gate7.py  (or the full suite)

16.1: the 18.4-deg cant enters the flat-plate law (vn = V·cosC·cos(phi) -
l_cp·omega; identity at phi = 0 — the Olympias anchors untouched by
construction). The Mark IIb prop fraction rose ~0.30 -> ~0.51-0.54.

16.2: the slip-factor (a rig key, default 1.0 — identity) is the documented
scenario knob: the 'Mark IIb as designed' scenario = cant + a modest area
increase (1.3x, the A5 estimate) + the residual slip factor, reproducing
the chain's 9.7 kt at 46.3 spm.

Gates: G7-1 the cant's measured effect (with vs without, ~1.7x);
G7-3 the slip sensitivity (monotonic, no adoption);
G7-4 the as-designed equilibrium lands on 9.7 kt.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT, RIGS, T_DRIVE, SPM, hull_power
from ll.oar import Oar, simulate

MIIB = RIGS["MarkIIb"]


def prop_fraction(rig, vkt, r_spm):
    td = T_DRIVE[("MarkIIb", vkt)]
    res = simulate(Oar(rig, r_spm, td), vkt * KT, td / 600, n_cycles=4)
    need = hull_power(vkt * KT, hull=1.08) / 170.0
    return res["mean_thrust"] * vkt * KT / need


def test_cant_effect_measured():
    """The cant's measured improvement at the Mark IIb points (~1.7x)."""
    with_cant = prop_fraction(MIIB, 7.5, SPM["MarkIIb"][7.5])
    no_cant = prop_fraction({**MIIB, "cant": 0.0}, 7.5, SPM["MarkIIb"][7.5])
    assert 0.45 < with_cant < 0.60, f"with cant {with_cant:.2f}"
    assert 0.25 < no_cant < 0.35, f"without cant {no_cant:.2f}"
    assert 1.5 < with_cant / no_cant < 2.0, f"cant ratio {with_cant/no_cant:.2f}"


def test_identity_at_olympias():
    """The cant path is identity at phi = 0: the Olympias means unchanged
    (the four-point agreement with the reference already covers this; here
    explicitly: a cant=0 rig copy gives identical means to the rig)."""
    rig = RIGS["Olympias"]
    for (rig_name, vkt), td in T_DRIVE.items():
        if rig_name != "Olympias":
            continue
        r = SPM[rig_name][vkt]
        a = simulate(Oar(rig, r, td), vkt * KT, td / 600, 4)
        b = simulate(Oar({**rig, "cant": 0.0}, r, td), vkt * KT, td / 600, 4)
        assert abs(a["mean_thrust"] / b["mean_thrust"] - 1) < 1e-9


def test_slip_sensitivity():
    """The slip-factor sensitivity at the Mark IIb 7.5-kt point: the prop
    fraction rises monotonically with the slip (the force ~ f^2); the
    diagnostic only — no value is adopted here."""
    fracs = {}
    for f in (1.0, 1.1, 1.2, 1.3):
        fracs[f] = prop_fraction({**MIIB, "slip": f}, 7.5, SPM["MarkIIb"][7.5])
    assert fracs[1.0] < fracs[1.1] < fracs[1.2] < fracs[1.3], fracs
    assert fracs[1.3] > 0.75
    print(f"       slip sensitivity: { {k: round(v, 2) for k, v in fracs.items()} }")


def test_as_designed_equilibrium():
    """The 'Mark IIb as designed' scenario: cant + area 1.3x (the A5
    estimate, not 3.3x) + the residual slip factor -> the equilibrium at
    46.3 spm lands on the chain's 9.7 kt (Table 9.7). Every factor is
    labelled: the slip ~1.2 is the aggregate of the unmodelled taper and
    attack-angle dynamics (register A5), NOT a blade dimension."""
    rig = {**MIIB, "area": MIIB["area"] * 1.3, "slip": 1.2}
    r_spm = SPM["MarkIIb"][9.7]
    td = T_DRIVE[("MarkIIb", 9.7)]

    def drag(V):
        return hull_power(V, hull=1.08) / V

    def g(V):
        res = simulate(Oar(rig, r_spm, td), V, td / 600, 4)
        return 170.0 * res["mean_thrust"] - drag(V)

    lo, hi = 2.0, 8.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    Ve = 0.5 * (lo + hi) / KT
    assert 9.5 < Ve < 9.9, f"as-designed equilibrium {Ve:.2f} kt (target 9.7)"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__]))
