"""Gate 1 — the LL one-oar skeleton against the validated chain.

Run: python3 tests/test_gate1.py  (from trireme-sim/)

Contract (plan §6, Level 1 + §5 note):
  - The time-stepped oar reproduces the rigid-oar model (rigid_stroke) at the
    four Table 9.6 operating points within 0.5 % (same physics, cleaner
    integration).
  - Physics-anchored bands: mean handle force in the cruise family
    (224 N @ 7.2 kt/28.8 spm, 208 N @ 8.2 kt/36 spm); propulsive W/man matches
    the hull need at the anchored point.
  - oQ-18 inherited honestly: the Mark IIb shortfall must persist exactly as
    the rigid model predicts it (any "fix" without documentation fails here).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import RIGS, T_DRIVE, SPM, KT, hull_power, rigid_stroke, OQ18
from ll.oar import Oar, simulate

passed = 0


def check(label, fn):
    global passed
    fn()
    passed += 1
    print(f"ok - {label}")


def rel(a, b):
    return abs(a / b - 1.0)


# --- 1. agreement with the rigid-oar reference at all four Table 9.6 points ---

def t_agreement():
    for (rig_name, vkt), t_drive in T_DRIVE.items():
        rig = RIGS[rig_name]
        r = SPM[rig_name][vkt]
        V = vkt * KT
        ref = rigid_stroke(V, rig, r, t_drive=t_drive)
        dt = t_drive / 600
        got = simulate(Oar(rig, r, t_drive), V, dt, n_cycles=4)
        assert rel(got["mean_thrust"], ref["mean_thrust"]) < 0.005, \
            f"{rig_name}@{vkt}kt thrust {got['mean_thrust']:.3f} vs {ref['mean_thrust']:.3f}"
        assert rel(got["mean_fh"], ref["mean_fh"]) < 0.005, \
            f"{rig_name}@{vkt}kt Fh {got['mean_fh']:.1f} vs {ref['mean_fh']:.1f}"
        assert rel(got["eff"], ref["eff"]) < 0.005
        assert rel(got["fb_peak"], ref["fb_peak"]) < 0.01, \
            f"{rig_name}@{vkt}kt peak {got['fb_peak']:.1f} vs {ref['fb_peak']:.1f}"
check("time-stepped oar == rigid model at all 4 Table 9.6 points (<0.5%)", t_agreement)


# --- 2. physics-anchored bands (cruise family) ---

def t_handle_force_band():
    rig = RIGS["Olympias"]
    for vkt, r, lo, hi in [(7.2, 28.8, 210.0, 225.0), (8.2, 36.0, 200.0, 215.0)]:
        t_drive = T_DRIVE[("Olympias", vkt)]
        got = simulate(Oar(rig, r, t_drive), vkt * KT, t_drive / 600, n_cycles=4)
        assert lo <= got["mean_fh"] <= hi, \
            f"{vkt} kt {r} spm: mean Fh {got['mean_fh']:.1f} N outside [{lo}, {hi}]"
check("mean handle force in the cruise family (224/208 N)", t_handle_force_band)


def t_power_anchor():
    """At the anchored point the oar must supply ~the hull need (rigid: 102 %)."""
    rig = RIGS["Olympias"]
    vkt, r = 7.2, 28.8
    V = vkt * KT
    t_drive = T_DRIVE[("Olympias", vkt)]
    got = simulate(Oar(rig, r, t_drive), V, t_drive / 600, n_cycles=4)
    prop_per_man = got["mean_thrust"] * V
    need_per_man = hull_power(V, hull=1.0) / 170.0
    ratio = prop_per_man / need_per_man
    assert 0.95 <= ratio <= 1.10, f"prop W/man {prop_per_man:.1f} vs hull need {need_per_man:.1f}"
check("propulsive W/man matches hull need at 7.2 kt (102%)", t_power_anchor)


# --- 3. integration behaviour ---

def t_convergence():
    rig = RIGS["Olympias"]
    t_drive = T_DRIVE[("Olympias", 7.2)]
    coarse = simulate(Oar(rig, 28.8, t_drive), 7.2 * KT, t_drive / 600, 4)
    fine = simulate(Oar(rig, 28.8, t_drive), 7.2 * KT, t_drive / 3000, 4)
    assert rel(fine["mean_fh"], coarse["mean_fh"]) < 0.003
    assert rel(fine["mean_thrust"], coarse["mean_thrust"]) < 0.003
check("dt convergence: 600 vs 3000 steps/drive < 0.3%", t_convergence)


def t_recovery_zero_force():
    oar = Oar(RIGS["Olympias"], 28.8, T_DRIVE[("Olympias", 7.2)])
    any_force = False
    while oar.cycle_no < 2:
        s = oar.step(T_DRIVE[("Olympias", 7.2)] / 600, 7.2 * KT)
        if not s.immersed:
            assert s.Fx == 0.0 and s.Fh == 0.0 and s.vn == 0.0
        else:
            any_force = True
    assert any_force
check("recovery: blade out of water, zero force", t_recovery_zero_force)


def t_cycle_wrap():
    oar = Oar(RIGS["Olympias"], 28.8, T_DRIVE[("Olympias", 7.2)])
    dt = oar.cycle / 300.0
    prev = oar.in_drive
    n_cycles = 0
    for _ in range(2000):
        oar.step(dt, 7.2 * KT)
        if not prev and oar.in_drive:          # catch crossing
            assert abs(oar.C - oar.sweep / 2) < 1e-9
            assert abs(oar.t_since_catch - dt) < 1e-9
            n_cycles += 1
        prev = oar.in_drive
    assert n_cycles >= 1
    assert abs(n_cycles - 2000 * dt / oar.cycle) < 2   # quantization bound
check("cycle wrap: angle restarts at the catch", t_cycle_wrap)


# --- 4. oQ-18 inherited honestly (documented, not silent) ---

def t_mark2_shortfall_persists():
    """The Mark IIb under-prediction must match the rigid model exactly.
    If a future 'fix' changes it, this test fails until the docs change too."""
    for (rig_name, vkt), t_drive in T_DRIVE.items():
        if rig_name != "MarkIIb":
            continue
        rig = RIGS[rig_name]
        r = SPM[rig_name][vkt]
        V = vkt * KT
        ref = rigid_stroke(V, rig, r, t_drive=t_drive)
        got = simulate(Oar(rig, r, t_drive), V, t_drive / 600, n_cycles=4)
        assert rel(got["mean_thrust"], ref["mean_thrust"]) < 0.005
        need = hull_power(V, hull=1.08) / 170.0
        assert got["mean_thrust"] * V / need < 0.35, \
            "Mark IIb shortfall changed — update OQ18 documentation first"
check("oQ-18 shortfall reproduced exactly (no silent tuning)", t_mark2_shortfall_persists)

print(f"\n{passed} checks passed")
print(f"note: {OQ18}")
