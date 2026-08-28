"""Plan 1 — the force-driven oar layer, single-oar validation (P1.3).

The drive's kinematics EMERGE from the torque-balance EOM (ll/oar.py
force mode): I·theta_ddot = -dir·Fh·lin - Fn·l_cp with the constant demand
Fh = 7.43·r at the "chain" pressure level (the reference level — the LL's
pressure dict, rower.py). The oar settles where the blade drag absorbs the
demand (the drive equilibrium vn = -sqrt(Fh·lin/(k·l_cp)) — the measured
stroke IS the force-balanced stroke: the G5-7 companion's physics, now in
the LL). The catch flip (pinned at the catch, the spike force over t_rise)
delivers the blade entry at the equilibrium speed.

Gates (Plan 1, P1.3 — next-steps.md §D):
  F1-1 the emerging drive time at the four Table 9.6 points within ±15 %
        (the G5-7 companion's gate); the Olympias pair within ±5 % (the
        minimum-shape target).
  F1-2 the emerging cycle-mean thrust at the 7.2 kt point within ±10 % of
        the kinematic reference (the force-driven drive self-organizes
        onto the measured stroke).
  F1-3 the flip: the entry at the equilibrium speed (the drive's mean
        |vn| near -vn_eq), the flip force <= Fh_max.
  F1-4 the cycle timing: flip + drive + recovery = the commanded cycle
        (within 1 % — the tempo is held at the chain demand).
  F1-5 the work conservation: the demand's handle work per drive =
        fh·lin·B_eff (the p_ext formula's identity, within 2 %).
  F1-6 the ceiling: peak handle force (demand or flip) <= Fh_max.
  F1-7 the start from rest: the first drive at V = 0 completes under the
        demand (the catch deadspot is gone — the parked blade would demand
        ~2 kN in the kinematic model; oQ-13's physical fix) with the peak
        handle force <= Fh_max.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from common.chain import KT, OAR_FAMILIES, RIGS, SPM, T_DRIVE, rigid_stroke
from ll.rower import Fh_MAX, TierCrew

FAM = OAR_FAMILIES["old-zygian"]
POINTS = [("Olympias", 7.2), ("Olympias", 8.2), ("MarkIIb", 7.5), ("MarkIIb", 9.7)]
DT = 0.005


def run_crew(
    name: str, vkt: float, n_cycles: int = 6, pressure: str = "chain"
) -> tuple:
    """Run the force-mode single-oar crew at fixed V; return
    (oar, plan, steps of the last cycle)."""
    r = SPM[name][vkt]
    td = T_DRIVE[(name, vkt)]
    crew = TierCrew(name, 1, r, td, pressure=pressure, mit=FAM, force=True)
    V = vkt * KT
    t = 0.0
    while t < (n_cycles - 1) * crew.oar.cycle:
        crew.step(DT, V)
        crew.end_of_step(DT)
        t += DT
    cyc0 = crew.oar.cycle_no
    steps = []
    while crew.oar.cycle_no < cyc0 + 1:
        steps.append(crew.oar.step(DT, V))
    return crew.oar, crew.plan, steps, V


# --- F1-1 the emerging drive times ---


def test_drive_times():
    for name, vkt in POINTS:
        oar, _plan, _, _V = run_crew(name, vkt)
        td_ref = T_DRIVE[(name, vkt)]
        ratio = oar.t_drive_last / td_ref
        assert 0.85 < ratio < 1.15, (
            f"{name}@{vkt}: drive {oar.t_drive_last:.3f} vs {td_ref:.3f} "
            f"({ratio:.3f}) — outside the ±15 % companion gate"
        )
        if name == "Olympias":
            assert abs(ratio - 1) < 0.05, (
                f"{name}@{vkt}: drive {ratio:.3f} — outside the ±5 % target"
            )
    print(
        f"       force-driven drive times (chain demand): "
        f"{ {f'{n}@{v}': round(run_crew(n, v)[0].t_drive_last / T_DRIVE[(n, v)], 3) for n, v in POINTS} }"
    )


# --- F1-2 the emerging thrust at the 7.2 point ---


def test_thrust_7_2():
    oar, _plan, steps, V = run_crew("Olympias", 7.2)
    ref = rigid_stroke(
        V, RIGS["Olympias"], SPM["Olympias"][7.2], t_drive=T_DRIVE[("Olympias", 7.2)]
    )
    cyc = oar.cycle
    fx_mean = sum(s.Fx * DT for s in steps) / cyc
    assert abs(fx_mean / ref["mean_thrust"] - 1) < 0.10, (
        f"emerging mean thrust {fx_mean:.1f} N/oar vs kinematic {ref['mean_thrust']:.1f}"
    )
    print(
        f"       emerging mean thrust at 7.2: {fx_mean:.2f} N/oar vs "
        f"kinematic {ref['mean_thrust']:.2f} ({fx_mean / ref['mean_thrust']:.3f})"
    )


# --- F1-3 the flip and the entry ---


def test_flip_entry():
    for name, vkt in POINTS:
        _oar, plan, _, V = run_crew(name, vkt)
        rig = RIGS[name]
        k = 0.5 * 1025.0 * rig["area"] * 1.8
        l_cp = rig["lout"] - (rig["blade"] - 0.260)
        vn_eq = math.sqrt(plan.fh_mean * rig["lin"] / (k * l_cp))
        assert plan.fh_flip <= Fh_MAX * 1.001, (
            f"{name}@{vkt}: flip force {plan.fh_flip:.0f} N > Fh_max"
        )
        # the entry is the equilibrium at the catch (within 3 %)
        cf = math.cos(math.radians(rig.get("cant", 0.0)))
        w_eq_catch = (V * math.cos(math.radians(rig["sweep"]) / 2) * cf + vn_eq) / l_cp
        assert abs(plan.omega_entry / w_eq_catch - 1) < 0.03, (
            f"{name}@{vkt}: entry {plan.omega_entry:.2f} vs equilibrium "
            f"{w_eq_catch:.2f}"
        )
        # the drive's mean normal flow sits at the equilibrium (within 15 %)
        vn_mean = sum(abs(s.vn) * DT for s in _last_drive_steps(name, vkt)) / max(
            T_DRIVE[(name, vkt)], 1e-9
        )
        assert abs(vn_mean / vn_eq - 1) < 0.15, (
            f"{name}@{vkt}: drive mean |vn| {vn_mean:.2f} vs equilibrium {vn_eq:.2f}"
        )


def _last_drive_steps(name, vkt):
    """Run the crew and collect one steady drive's per-step samples."""
    r = SPM[name][vkt]
    td = T_DRIVE[(name, vkt)]
    crew = TierCrew(name, 1, r, td, pressure="chain", mit=FAM, force=True)
    V = vkt * KT
    t = 0.0
    while t < 5 * crew.oar.cycle:
        crew.step(DT, V)
        crew.end_of_step(DT)
        t += DT
    cyc0 = crew.oar.cycle_no
    out = []
    while crew.oar.cycle_no < cyc0 + 1:
        s = crew.oar.step(DT, V)
        if s.immersed:
            out.append(s)
    return out


# --- F1-4 the cycle timing ---


def test_cycle_timing():
    for name, vkt in POINTS:
        oar, plan, _, _ = run_crew(name, vkt)
        r = SPM[name][vkt]
        pull = plan.t_drive + oar.t_rise
        rec = plan.sweep / plan.omega_recover
        assert abs(pull + rec - 60.0 / r) / (60.0 / r) < 0.01, (
            f"{name}@{vkt}: flip+drive+recovery {pull + rec:.3f} vs cycle {60.0 / r:.3f}"
        )
        assert abs(plan.rate_eff - r) < 0.01, (
            f"{name}@{vkt}: achieved rate {plan.rate_eff} vs commanded {r}"
        )


# --- F1-5 the work conservation ---


def test_work_conservation():
    for name, vkt in POINTS:
        oar, plan, steps, _ = run_crew(name, vkt)
        w_handle = sum(
            s.Fh * abs(s.omega) * oar.rig["lin"] * DT for s in steps if s.immersed
        )
        w_ref = plan.fh_mean * oar.rig["lin"] * plan.sweep
        assert abs(w_handle / w_ref - 1) < 0.02, (
            f"{name}@{vkt}: handle work {w_handle:.1f} J vs fh·lin·B {w_ref:.1f} J"
        )


# --- F1-6 the ceiling (single-oar) ---


def test_ceiling_single_oar():
    for name, vkt in POINTS:
        _oar, plan, _, _ = run_crew(name, vkt)
        assert max(plan.fh_mean, plan.fh_flip) <= Fh_MAX * 1.001, (
            f"{name}@{vkt}: peak {max(plan.fh_mean, plan.fh_flip):.0f} N > Fh_max"
        )


# --- F1-7 the start from rest (the deadspot is gone) ---


def test_start_from_rest():
    """The first drive from V = 0 under the demand: the flow drags the
    parked blade (the catch deadspot — ~2 kN in the kinematic model), the
    oar accelerates through the slip speed and settles at the equilibrium —
    the drive completes with the handle force at the demand, not the
    deadspot's ~2 kN."""
    r = SPM["Olympias"][7.2]
    crew = TierCrew(
        "Olympias",
        1,
        r,
        T_DRIVE[("Olympias", 7.2)],
        pressure="chain",
        mit=FAM,
        force=True,
    )
    oar = crew.oar
    V = 0.0
    t = 0.0
    peak = 0.0
    while oar.cycle_no < 1 and t < 10.0:
        _, fh, _, _ = crew.step(DT, V)
        crew.end_of_step(DT)
        peak = max(peak, fh)
        t += DT
    # the first drive completed
    assert oar.t_drive_last > 0.0, "the first drive from rest never finished"
    # and the handle force stayed at the demand (no deadspot spike)
    assert peak <= Fh_MAX * 1.001, f"peak Fh {peak:.0f} N at the start"
    print(
        f"       first drive from rest: {oar.t_drive_last:.3f} s "
        f"(the kinematic deadspot would demand ~2 kN; the demand "
        f"{crew.plan.fh_mean:.0f} N holds)"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
