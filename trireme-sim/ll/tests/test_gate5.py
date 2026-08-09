"""Gate 5 — the oar inertia layer (plan §13).

Run: python3 tests/test_gate5.py  (from trireme-sim/)

Gates (plan §13.4):
  G5-1 spike magnitudes reproduce oar_inertia.py (116 / 215 / 156 N at
        t_rise 0.15 s, 28.8 spm — the Table-1.092-m reference convention);
        the full-reversal physical values (w_rec + w_drive) reported.
  G5-2 handiness ratio: zygian/spruce ≈ 1.85x.
  G5-3 means preserved: the four Table 9.6 points within 1 % of the rigid
        model with the inertia layer ON (the inertia is internal to the
        rower-oar system — the hull observables are untouched).
  G5-4 energy closure: net inertia work over a cycle < 0.5 % of the cycle
        blade work (the oar returns to rest each cycle).
  G5-5 couple anchor: drive-mean Fh at 30 spm ≈ 225 N (Table 3.2) within 3 %.
  G5-6 ceiling interplay: total peak Fh (blade + spike) <= Fh_max through a
        spoude burst, both fleets.
  G5-7 companion (force-driven): with the demand handle force, the
        torque-balance ODE's emerging drive time within ±15 % of Table 9.6.
  G5-8 regression: the other suites stay green (run separately).
"""

import sys
import pytest
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT, RIGS, T_DRIVE, SPM, OAR_FAMILIES, OAR_TABLE31_LIN, rigid_stroke
from ll.oar import Oar, simulate
from ll.rower import Fh_MAX, SideCrew
from ll.hull import t_drive_for
from ll.ship import Ship

FAM = OAR_FAMILIES                       # mean MIT per family (kg m2)
SPIKE_REF = {"spruce": 116.0, "old-zygian": 215.0, "old-thranite": 156.0}
LIN_LL = RIGS["Olympias"]["lin"]         # the LL oar's inboard (0.957 m)


def spike(I, omega, t_rise, lin):
    return I * omega / (t_rise * lin)


# --- G5-1 / G5-2 spike magnitudes and handiness ---

def test_spike_reference():
    """Reproduce oar_inertia.py's numbers (Table-1.092-m reference) within 2 %.
    The physical full-reversal spike (w_rec + w_drive) is ~26 % higher."""
    td = T_DRIVE[("Olympias", 7.2)]
    omega_d = math.radians(48.1) / td          # 1.95 rad/s
    omega_r = math.radians(48.1) / (60.0 / 28.8 - td)
    for fam, ref in SPIKE_REF.items():
        got = spike(FAM[fam], omega_d, 0.15, OAR_TABLE31_LIN)
        assert abs(got / ref - 1) < 0.02, f"{fam}: {got:.0f} vs ref {ref}"
        full = spike(FAM[fam], omega_d + omega_r, 0.15, OAR_TABLE31_LIN)
        assert abs(full / ref - 1) > 0.2      # the reversal correction is real
    print(f"       full-reversal spikes (w_rec+w_drive): "
          f"{ {k: round(spike(FAM[k], omega_d+omega_r, 0.15, OAR_TABLE31_LIN)) for k in FAM} }")


def test_handiness():
    s_z = spike(FAM["old-zygian"], 1.95, 0.15, OAR_TABLE31_LIN)
    s_s = spike(FAM["spruce"], 1.95, 0.15, OAR_TABLE31_LIN)
    ratio = s_z / s_s
    assert abs(ratio - 1.85) < 0.06, f"zygian/spruce {ratio:.2f}"


# --- G5-3 means preserved with the layer ON ---

def test_means_preserved():
    for (rig_name, vkt), t_drive in T_DRIVE.items():
        rig = RIGS[rig_name]
        r = SPM[rig_name][vkt]
        V = vkt * KT
        ref = rigid_stroke(V, rig, r, t_drive=t_drive)
        oar = Oar(rig, r, t_drive, mit=FAM["old-zygian"], t_rise=0.15)
        got = simulate(oar, V, t_drive / 600, n_cycles=4)
        assert abs(got["mean_thrust"] / ref["mean_thrust"] - 1) < 0.01, \
            f"{rig_name}@{vkt}: thrust {got['mean_thrust']:.2f} vs {ref['mean_thrust']:.2f}"
        assert abs(got["mean_fh"] / ref["mean_fh"] - 1) < 0.01
        assert abs(got["eff"] / ref["eff"] - 1) < 0.01


# --- G5-4 energy closure ---

def test_energy_closure():
    """Momentum closure: the catch and release pulses deliver equal and
    opposite impulses (the oar returns to the same angular momentum each
    cycle). The flip ENERGY is accounted exactly in the W' basis
    (flip_power = 1/2·I·w_d^2·r/60) — the pulses are impulse-equivalent,
    not energy-shape-exact (documented in plan §13.2/13.4)."""
    oar = Oar(RIGS["Olympias"], 28.8, T_DRIVE[("Olympias", 7.2)],
              mit=FAM["old-zygian"], t_rise=0.15)
    V = 7.2 * KT
    oar.reset()
    l_cp = oar.rig["lout"] - (oar.rig["blade"] - 0.260)
    imp_net = 0.0
    imp_blade = 0.0
    while oar.cycle_no < 4:
        s = oar.step(0.001, V)
        fh_blade = abs(s.Fn) * l_cp / oar.rig["lin"]
        imp_net += (s.Fh - fh_blade) * 0.001        # the pulse impulses
        if s.immersed:
            imp_blade += fh_blade * 0.001
    assert abs(imp_net) < 0.005 * imp_blade, \
        f"net pulse impulse {imp_net:.1f} N.s vs blade {imp_blade:.0f} N.s"
    # the flip energy lives in the W' basis (per stroke):
    e_stroke = oar.flip_power(28.8) * 60.0 / 28.8
    assert abs(e_stroke - 0.5 * FAM["old-zygian"] * oar.omega_drive ** 2) < 1e-9


# --- G5-5 couple anchor ---

def test_couple_anchor():
    """Drive-mean handle force at the anchored point (28.8 spm / 7.2 kt —
    Table 9.6) stays on the Table 3.2 couple anchor: 224 N x 1.092 m =
    244.6 vs Table 3.2's 246 N m (0.6 % — plan §13.1); the cycle-mean adds
    the flip pulses."""
    td = T_DRIVE[("Olympias", 7.2)]
    oar = Oar(RIGS["Olympias"], 28.8, td, mit=FAM["spruce"], t_rise=0.15)
    res = simulate(oar, 7.2 * KT, td / 600, n_cycles=4)
    assert abs(res["mean_fh"] / 224.0 - 1) < 0.03, f"mean Fh {res['mean_fh']:.0f}"


# --- G5-6 ceiling interplay ---

def test_ceiling():
    for fleet in ("spruce", "old-fir"):
        ship = Ship(rate=44.5, fleet=fleet)
        ship.V = 8.5 * KT
        pk = 0.0
        for _ in range(3000):                     # 30 s burst
            fx = {}
            for side, crew in ship.crew.items():
                fx[side], fh, _ = crew.step(0.01, ship.V)
                pk = max(pk, fh)
            for crew in ship.crew.values():
                crew.end_of_step(0.01)
            ship._keleustes(0.01)
            vkt = abs(ship.V) / KT
            q, drag = (0.0, ship.vessel.rudder_straight * vkt * vkt)
            ship.hull_advance(0.01, ship.n_side * (fx["port"] + fx["star"]),
                              0.0, q, drag)
        assert pk <= Fh_MAX * 1.001, f"{fleet}: peak Fh {pk:.0f} N"


# --- G5-7 companion: force-driven drive time ---

def test_force_driven():
    """Companion (plan §13.2 Option A): solve I·theta_ddot = -Fh·lin + Fn·l_cp
    with a constant demanded handle force. The catch flip happens in the air
    (blade out — the spike spins the oar up), so the blade enters at ~full
    drive speed; the emerging effective-pull duration must sit near Table 9.6
    (±15 %). A parked blade would demand ~1 kN (the catch deadspot) — which is
    exactly why the flip-in-air is the physical entry."""
    rig = RIGS["Olympias"]
    lin, l_cp = rig["lin"], rig["lout"] - (rig["blade"] - 0.260)
    k = 0.5 * 1025.0 * rig["area"] * 1.8
    V = 7.2 * KT
    td_ref = T_DRIVE[("Olympias", 7.2)]
    fh_demand = 7.43 * 28.8                       # the chain's mean pull
    I = FAM["old-zygian"]
    dt = 5e-5
    B = math.radians(48.1)
    C, w, t, swept = B / 2, -B / td_ref, 0.0, 0.0   # blade enters at full speed
    while swept < B and t < 5.0:
        # vn = V·cosC + l_cp·w (w < 0 during the drive); the blade force on
        # the oar resists the aft sweep: I·w_dot = -Fh·lin - fn·l_cp
        vn = V * math.cos(C) + l_cp * w
        fn = k * vn * abs(vn)
        w += (-fh_demand * lin - fn * l_cp) / I * dt
        C += w * dt
        swept += -w * dt
        t += dt
    assert 0.85 * td_ref < t < 1.15 * td_ref, \
        f"force-driven drive {t:.2f} s vs Table 9.6 {td_ref:.2f} s"
    print(f"       force-driven drive time ≈ {t:.2f} s vs Table 9.6 {td_ref:.2f} s")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
