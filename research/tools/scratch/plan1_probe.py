"""Plan 1, P1.1/P1.2 probe: the force-driven drive under the minimum-shape
(constant demand) hypothesis — the companion's physics, measured.

For each Table 9.6 point: the drive EOM
    I·w_dot = -Fh·lin - Fn·l_cp,  Fn = k·|vn|·vn,  vn = V·cosC + l_cp·w
with the blade entering at the kinematic drive speed (the catch flip done
in the air). Reports the emerging drive time, the stall (the moment the
blade stops outrunning the water: vn = 0), the positive-thrust fraction of
the drive, the emerging mean thrust vs the kinematic model's, the handle
work, and the finish speed.

The verdict this probe produces: whether the constant-demand shape is a
viable minimum for the LL force mode, or whether the force must be
concentrated at the catch (the B3 shape) for the thrust to survive.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "simulation"))

from common.chain import KT, RIGS, T_DRIVE, SPM, OAR_FAMILIES, rigid_stroke

POINTS = [("Olympias", 7.2), ("Olympias", 8.2),
          ("MarkIIb", 7.5), ("MarkIIb", 9.7)]
FLEET = "old-zygian"          # the companion's family
I = OAR_FAMILIES[FLEET]
DT = 5e-5


def force_drive(rig_name, vkt, dt=DT):
    rig = RIGS[rig_name]
    lin, l_cp = rig["lin"], rig["lout"] - (rig["blade"] - 0.260)
    k = 0.5 * 1025.0 * rig["area"] * 1.8
    V = vkt * KT
    td_ref = T_DRIVE[(rig_name, vkt)]
    r = SPM[rig_name][vkt]
    fh = 7.43 * r                       # the chain's mean pull (demand)
    B = math.radians(rig["sweep"])
    C, w, t, swept = B / 2, -B / td_ref, 0.0, 0.0
    t_stall = None
    thrust_pos = 0.0
    fx_sum = 0.0
    fn_peak = 0.0
    while swept < B and t < 5.0:
        vn = V * math.cos(C) + l_cp * w
        fn = k * vn * abs(vn)
        if t_stall is None and vn >= 0.0 and t > 1e-6:
            t_stall = t
        fx = -fn * math.cos(C)          # force on hull along keel
        if fx > 0:
            thrust_pos += fx * dt
        fx_sum += fx * dt
        fn_peak = max(fn_peak, abs(fn))
        w += (-fh * lin - fn * l_cp) / I * dt
        C += w * dt
        swept += -w * dt
        t += dt
    w_finish = -w
    return dict(t=t, t_stall=t_stall, w_finish=w_finish, fx_sum=fx_sum,
                thrust_pos=thrust_pos, fn_peak=fn_peak, fh=fh, td_ref=td_ref,
                B=B, lin=lin)


print(f"force-driven drive (minimum shape: Fh = 7.43·r constant), I = {I:.1f} kg·m²")
print(f"{'point':14} {'t_drive':>8} {'vs T9.6':>8} {'stall t':>8} "
      f"{'finish w':>9} {'Fx mean':>8} {'Fx+ frac':>8} {'Fh mean':>8}")
for name, vkt in POINTS:
    d = force_drive(name, vkt)
    # the kinematic reference at the same point
    rig = RIGS[name]
    ref = rigid_stroke(vkt * KT, rig, SPM[name][vkt], t_drive=d["td_ref"])
    # cycle-mean thrust (the drive's share over the full cycle)
    cycle = 60.0 / SPM[name][vkt]
    fx_mean = d["fx_sum"] / cycle
    fx_ref = ref["mean_thrust"]
    print(f"{name+' @'+str(vkt):14} {d['t']:8.3f} {d['t']/d['td_ref']:8.3f} "
          f"{str(d['t_stall']):>8} {d['w_finish']:9.2f} {fx_mean:8.1f} "
          f"{d['thrust_pos']/max(d['fx_sum'],1e-9):8.2f} {d['fh']:8.0f}   "
          f"[kinematic Fx/cycle {fx_ref:.1f}]")
