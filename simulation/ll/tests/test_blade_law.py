"""Blade-law gate — the ch.9 (q/p)^2 turning-point law (plan 15.2, task I).

The law (Shaw 2012 ch.9 p.79): Fn = k·(q/p)^2·V^2·cos^2C, with p the
thole -> instantaneous turning point (plan) and q the turning point -> blade
CP; the mean ideal efficiency is E = 1/(1 + q/p). Both turning-point
interpretations are locked here through the LL's blade_force:

  - "actual" (DEFAULT): p = -V·nx/omega (the kinematic turning point) =>
    v_n = omega·q => the flat-plate law IS the (q/p)^2 law, point by point
    (the research chain locks the algebra in test_turning_point_equivalence;
    this gate locks ll/blade.blade_force to the same identity).
  - "geometric" (OFF): Shaw's appendix d-formula turning point
    (d = 0.953·cos(120C/B), p = L_plan - d) with the deadpoint-stationary
    omega — net NEGATIVE thrust at all four Table 9.6 points (the measured
    kinematics are the truth; the slip limit is a lower bound, locked here
    and in tests/test_research_chain.py::test_slip_limit_is_a_lower_bound).

Gate-1/7 compatibility: the default law is numerically the flat-plate law
(the identity), so the validated anchors cannot drift under this layer.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import CN, KT, RHO, RIGS, SPM, T_DRIVE
from ll import blade
from ll.oar import Oar, simulate


def flat_form(C, omega, V, rig):
    """The direct flat-plate law (the rigid-oar convention)."""
    cf = math.cos(math.radians(rig.get("cant", 0.0)))
    nx = math.cos(C) * cf
    l_cp = rig["lout"] - (rig["blade"] - 0.260)
    return (V * nx + l_cp * omega) * rig.get("slip", 1.0)


def test_default_is_actual_turning_point():
    """The law's default must be the physical diagnosis: the ACTUAL turning
    point (the identity); the geometric slip limit stays OFF."""
    assert blade.TURNING_POINT == "actual"


def test_actual_turning_point_identity():
    """blade_force at the default law IS the flat-plate law point by point,
    and the (q/p)^2 form reproduces it: |Fn| = k·(q/p)^2·(V·nx)^2 with
    p = -V·nx·slip/omega, q = l_cp - p (the locked algebraic identity)."""
    for name, rig in RIGS.items():
        l_cp = rig["lout"] - (rig["blade"] - 0.260)
        k = 0.5 * RHO * rig["area"] * CN
        for C in (-0.5, -0.25, 0.0, 0.25, 0.5):
            for w in (1.0, 1.5, 2.0):
                for V in (2.0, 3.7, 5.0):
                    for slip in (1.0, 1.2):
                        rig_s = {**rig, "slip": slip}
                        f = blade.blade_force(C, -w, V, rig_s)
                        vn = flat_form(C, -w, V, rig_s)
                        assert f["vn"] == vn, f"{name} vn"
                        cf = math.cos(math.radians(rig.get("cant", 0.0)))
                        nx = math.cos(C) * cf
                        p = V * nx / w  # the actual turning point
                        q = l_cp - p
                        assert abs(f["p"] - p) < 1e-12 and abs(f["q"] - q) < 1e-12
                        assert abs(f["vn"] - slip * (-w) * q) < 1e-12 * max(
                            1.0, abs(f["vn"])
                        )
                        shaw = k * (q / p) ** 2 * (slip * V * nx) ** 2
                        assert abs(abs(f["Fn"]) - shaw) < 1e-9 * max(1.0, shaw)


def test_geometric_slip_limit_is_net_negative():
    """The appendix d-formula variant through the LL: net NEGATIVE thrust at
    all four Table 9.6 points (the crews sweep faster than the deadpoint-
    stationary speed — the measured kinematics are the truth; this is the
    plan 15.2 slip-limit lower bound, now locked at the LL level)."""
    for (name, vkt), td in T_DRIVE.items():
        rig = RIGS[name]
        r = SPM[name][vkt]
        V = vkt * KT
        flat = simulate(Oar(rig, r, td), V, td / 600, n_cycles=4)["mean_thrust"]
        blade.TURNING_POINT = "geometric"
        try:
            geom = simulate(Oar(rig, r, td), V, td / 600, n_cycles=4)["mean_thrust"]
        finally:
            blade.TURNING_POINT = "actual"
        assert geom < 0.0, f"{name}@{vkt} kt: geometric thrust {geom:.2f} N >= 0"
        assert geom < flat * 0.5, (
            f"{name}@{vkt} kt: slip limit {geom:.2f} not a lower bound of {flat:.2f}"
        )


def test_deadspot_qp_geometry():
    """The Mark IIb deadspot in the law's own quantities: at the chain's
    points the blade CP rides NEAR the actual turning point (small q/p — the
    blade outruns the water only marginally), deeper than the Olympias's."""
    for name, vkt, lo, hi in [
        ("Olympias", 7.2, 0.20, 0.35),
        ("MarkIIb", 7.5, 0.10, 0.25),
    ]:
        rig = RIGS[name]
        V = vkt * KT
        td = T_DRIVE[(name, vkt)]
        B = math.radians(rig["sweep"])
        w = B / td
        f = blade.blade_force(0.0, -w, V, rig)  # mid-stroke
        qp = f["q"] / f["p"]
        assert lo < qp < hi, f"{name}@{vkt} kt: q/p = {qp:.3f} outside [{lo}, {hi}]"
        assert f["q"] > 0.0  # CP outboard of the
        # turning point (deadspot)
    qp_ol = blade.blade_force(
        0.0,
        -math.radians(RIGS["Olympias"]["sweep"]) / T_DRIVE[("Olympias", 7.2)],
        7.2 * KT,
        RIGS["Olympias"],
    )
    qp_mb = blade.blade_force(
        0.0,
        -math.radians(RIGS["MarkIIb"]["sweep"]) / T_DRIVE[("MarkIIb", 7.5)],
        7.5 * KT,
        RIGS["MarkIIb"],
    )
    assert (qp_mb["q"] / qp_mb["p"]) < (qp_ol["q"] / qp_ol["p"])


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
