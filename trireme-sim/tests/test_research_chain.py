"""Research-chain regression locks (the source of truth the LL imports).

Every headline number of the research modules is asserted here so that a
change to the chain breaks these tests with precise diagnostics, before it
can propagate silently into the simulators. Anchors: lane-4 power chain
(ch.7/ch.9), rigid-oar model, Table 3.1 families, lane-5 manoeuvre model.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import (KT, RIGS, T_DRIVE, SPM, VESSELS, OAR_FAMILIES,
                          OAR_TABLE31_LIN, rigid_stroke, hull_power,
                          speed_from_power, oar_power, mean_pull, oar_absorbed)


# --- lane-4 power chain (ch.9 sprint, Table 9.7, ch.7 cruise) ---

def test_sprint_validation():
    """ch.9 four-run sprint: 130 rowers, 44.5 spm, E=0.730 -> 8.32 kt."""
    W = oar_power(130, mean_pull(44.5), 0.78, 44.5, 0.730)
    V = speed_from_power(W)
    assert abs(V / KT - 8.32) < 0.05, f"{V/KT:.2f} kt"


def test_mean_pull_law_origin():
    """P = 7.43·r: the 3/4-NM calibration (288 N @ 38.75 spm) is its origin."""
    assert abs(mean_pull(38.75) - 288.0) < 1.0
    assert abs(mean_pull(28.8) - 214.0) < 1.0


def test_ch7_cruise_rates():
    """25.5 / 28.8 / 32.3 spm at 7 / 7.5 / 8 kt (Mark II hull, L=0.99)."""
    for Vkt, r_shaw in [(7.0, 25.5), (7.5, 28.8), (8.0, 32.3)]:
        W = hull_power(Vkt * KT, hull=1.08)
        r = math.sqrt(W * 60.0 / (170 * 7.43 * 0.99 * 0.78))
        assert abs(r - r_shaw) < 0.3, f"{Vkt} kt: {r:.1f} vs {r_shaw}"


def test_table97_rates():
    """Mark IIa/IIb rates of striking at 7.5 & 9.7 kt."""
    for L, Vkt, r_shaw in [(0.87, 7.5, 30.7), (0.87, 9.7, 49.4),
                           (0.99, 7.5, 28.8), (0.99, 9.7, 46.3)]:
        W = hull_power(Vkt * KT, hull=1.08)
        r = math.sqrt(W * 60.0 / (170 * 7.43 * L * 0.780))
        assert abs(r - r_shaw) < 0.5, f"L={L} {Vkt} kt: {r:.1f} vs {r_shaw}"


def test_oar_absorbed():
    assert abs(oar_absorbed(25.5) - 34.8) < 0.3
    assert abs(oar_absorbed(32.3) - 47.7) < 0.3


# --- rigid-oar model (the four Table 9.6 points) ---

REF_MEANS = {
    ("Olympias", 7.2): (17.46, 223.7, 76.2),      # cant 0 — unchanged
    ("Olympias", 8.2): (18.37, 207.9, 79.1),
    # the Mark IIb WITH the 18.4-deg cant (plan 16.1): ~1.7x the thrust
    ("MarkIIb", 7.5): (10.40, 105.5, 81.8),
    ("MarkIIb", 9.7): (22.20, 181.3, 81.6),
}


def test_rigid_model_means():
    for (rig, vkt), (t_ref, fh_ref, eff_ref) in REF_MEANS.items():
        s = rigid_stroke(V=vkt * KT, rig=RIGS[rig], r_spm=SPM[rig][vkt],
                         t_drive=T_DRIVE[(rig, vkt)])
        assert abs(s["mean_thrust"] / t_ref - 1) < 0.01, f"{rig}@{vkt} thrust"
        assert abs(s["mean_fh"] / fh_ref - 1) < 0.01, f"{rig}@{vkt} Fh"
        assert abs(s["eff"] * 100 - eff_ref) < 0.5, f"{rig}@{vkt} eff"


def test_mark2_area_sensitivity():
    """oQ-18 with the cant (plan 16.1): the prop fraction rose from ~0.30
    to ~0.51 (the 18.4-deg cant term). The residual to the chain is the
    aggregate of the A5 area gap + the slip assumptions — locked so the
    documented shortfall cannot silently move."""
    s = rigid_stroke(V=7.5 * KT, rig=RIGS["MarkIIb"], r_spm=SPM["MarkIIb"][7.5],
                     t_drive=T_DRIVE[("MarkIIb", 7.5)])
    need = hull_power(7.5 * KT, hull=1.08) / 170.0
    ratio = s["mean_thrust"] * 7.5 * KT / need
    assert 0.45 < ratio < 0.60, f"Mark IIb prop fraction {ratio:.2f}"


# --- Table 3.1 oar inertia families ---

def test_oar_families():
    assert abs(OAR_FAMILIES["spruce"] - 9.7) < 0.2
    assert abs(OAR_FAMILIES["old-zygian"] - 18.0) < 0.3
    assert abs(OAR_FAMILIES["old-thranite"] - 13.1) < 0.3


def test_catch_spike_reference():
    """oar_inertia.py's 116 / 215 / 156 N at t_rise 0.15 s, 28.8 spm."""
    omega = math.radians(48.1) / T_DRIVE[("Olympias", 7.2)]
    for fam, ref in [("spruce", 116.0), ("old-zygian", 215.0),
                     ("old-thranite", 156.0)]:
        spike = OAR_FAMILIES[fam] * omega / (0.15 * OAR_TABLE31_LIN)
        assert abs(spike / ref - 1) < 0.02, f"{fam}: {spike:.0f} vs {ref}"


# --- lane-5 manoeuvre model (W5 anchors) ---

def test_manoeuvre_diameters():
    op, mb = VESSELS["Olympias"], VESSELS["MarkIIb"]
    d, _, _ = op.steady_turn(6.5, 67.5, 1.4, one_side=True)
    assert abs(d - 62) < 6, f"tightest {d:.1f} m"            # 64.0 vs 62
    d, _, _ = mb.steady_turn(9.5, 22.5, 3.25)
    assert abs(d - 145) < 12, f"fast anastrophe {d:.1f} m"   # 151.8 vs 145
    d, _, _ = mb.steady_turn(6.5, 67.5, 3.25, one_side=True)
    assert abs(d - 80) < 8, f"tight anastrophe {d:.1f} m"    # 74.6 vs 80


def test_manoeuvre_acceleration():
    mb = VESSELS["MarkIIb"]
    prof, hit55 = mb.simulate_forward(0.0, 40.0, stop_at=(10.0, 5.5))
    _, hit9 = mb.simulate_forward(0.0, 40.0, stop_at=(24.0, 9.0))
    assert hit55 is not None and hit55[0] < 10.5
    assert hit9 is not None and hit9[0] < 25.0
    assert abs(prof[-1][1] - 9.9) < 0.3


def test_ch9_efficiency_consistency():
    """ch.9 §3: 1/E = 1 + q/p with q/p proportional to 1/sqrt(n). The text
    states E(170) = 0.756 and that reducing to 116 rowers raises q/p by
    1.21 — giving E = 0.719, exactly the 3/4-NM calibration value."""
    qp170 = 1.0 / 0.756 - 1.0
    e116 = 1.0 / (1.0 + qp170 * 1.21)
    assert abs(e116 - 0.719) < 0.001, f"E(116) = {e116:.3f}"


def test_turning_point_equivalence():
    """Shaw's ch.9 force form k·(q/p)²·V²·sin²C with the ACTUAL turning
    point (p = V·cosC/omega, q = l_cp - p) reduces algebraically to the
    flat-plate law k·v_n² — the flat-plate law IS Shaw's form (the resolved
    mismatch #4). Numeric check over a grid."""
    rig = RIGS["Olympias"]
    l_cp = rig["lout"] - (rig["blade"] - 0.260)
    k = 0.5 * 1025.0 * rig["area"] * 1.8
    for C in (-0.4, -0.2, 0.0, 0.2, 0.4):
        for w in (1.0, 1.5, 2.0):
            for V in (2.0, 3.7, 5.0):
                vn = V * math.cos(C) - l_cp * w
                p = V * math.cos(C) / w          # the actual turning point
                q = l_cp - p
                shaw = k * (q / p) ** 2 * V * V * math.cos(C) ** 2
                assert abs(shaw - k * vn * vn) < 1e-9 * max(1.0, abs(shaw))


def test_slip_limit_is_a_lower_bound():
    """The geometric-deadpoint slip limit (omega = V·cosC/p(C), p = L_plan
    - d(C)) gives LESS thrust than the measured Table 9.6 kinematics — and
    can go negative: the trials' crews sweep faster than the slip limit, so
    the prescribed (measured) kinematics are the truth, not the slip limit."""
    def slip_thrust(rig_name, vkt, t_drive):
        rig = RIGS[rig_name]
        V = vkt * KT
        B = math.radians(rig["sweep"])
        w = B / t_drive
        dt = t_drive / 600
        l_cp = rig["lout"] - (rig["blade"] - 0.260)
        L_plan = rig["lout"] / math.cos(math.radians(30.0))
        k = 0.5 * 1025.0 * rig["area"] * 1.8
        Fx = 0.0
        C = B / 2
        for _ in range(600):
            d = 0.953 * math.cos(120.0 * C / B)
            p = L_plan - d
            omega_slip = V * math.cos(C) / p
            vn = V * math.cos(C) - l_cp * omega_slip
            Fx += -k * vn * abs(vn) * math.cos(C) * dt
            C -= w * dt
        return Fx / (60.0 / SPM[rig_name][vkt])
    for (rig, vkt), td in T_DRIVE.items():
        flat = rigid_stroke(V=vkt * KT, rig=RIGS[rig],
                            r_spm=SPM[rig][vkt], t_drive=td)["mean_thrust"]
        slip = slip_thrust(rig, vkt, td)
        assert slip < flat * 0.5, f"{rig}@{vkt}: slip {slip:.1f} vs flat {flat:.1f}"


def test_apparent_mass():
    for name in ("Olympias", "MarkIIb"):
        v = VESSELS[name]
        assert abs(v.m_app / v.m - 1.10) < 1e-6, name


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
