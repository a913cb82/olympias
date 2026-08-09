#!/usr/bin/env python3
"""W3 rigid-oar per-stroke refinement layer (lane-4).

Rigid-oar blade-force model over one drive stroke, following the flat-plate /
pressure-drag regime of the 2019 NJP "Physics of rowing oars" analysis and the
Baudouin & Hawkins (2002) 2nd-class-lever decomposition:

  - blade acts as a flat plate (trireme blades were near-flat spade/teardrop
    shapes, much lower camber than a modern Big Blade): the dominant blade force
    is the pressure (normal) force on the blade face
        Fn = 0.5 rho A C_N |v_n| v_n  (acting to oppose normal flow v_n)
    with C_N ~ 1.8 for a flat plate fully immersed (matches the Macon measured
    C_D max ~1.85 at 90 deg attack, Caplan & Gardner 2007b / Coppel 2009)
  - handle force from torque balance about the thole: Fh*lin = Fb*l_cp
  - rig geometry from W3 (rig-geometry.md), blade CP 260 mm from tip

Frame: x = along keel, bow = +x; y = athwartships. Oar axis u = (sin C, cos C),
C = oar angle from athwartships (+ = blade swept toward bow). During the drive
C goes +sweep/2 -> -sweep/2, omega = dC/dt < 0.

We resolve the per-stroke thrust, handle-force envelope and mean efficiency and
compare against the Shaw bulk lever-chain (lane4_propulsion.py). This is the
per-stroke refinement layer requested in main doc W3 item 147 / D9.
"""
import math

KT = 0.5148
RHO = 1025.0

# flat-plate normal (pressure) coefficient, fully immersed
CN = 1.8

RIGS = {
    # name: inboard plan, outboard plan, blade len, sweep B, blade area (m^2),
    # cant (sweep-plane tilt about the athwartships axis, deg; ch.9: the
    # Mark IIb rig is canted 18.4 deg = tan 1/3 — the flat-plate law gains
    # the cos(cant) flow correction, plan §16.1)
    "Olympias": dict(lin=0.957, lout=2.696, blade=0.55, sweep=48.1, area=0.078,
                     cant=0.0),
    "MarkIIb": dict(lin=1.061, lout=2.970, blade=0.55, sweep=55.6, area=0.078,
                    cant=18.4),
}
# Table 9.6: duration of the effective pull, s
T_DRIVE = {
    ("Olympias", 7.2): 0.430,
    ("Olympias", 8.2): 0.392,
    ("MarkIIb", 7.5): 0.612,
    ("MarkIIb", 9.7): 0.472,
}
SPM = {
    "Olympias": {7.2: 28.8, 8.2: 36.0},
    "MarkIIb": {7.5: 28.8, 9.7: 46.3},
}

def rigid_stroke(V, rig, r_spm, t_drive=None, n_pts=600):
    sweep = math.radians(rig["sweep"])
    lin, lout = rig["lin"], rig["lout"]
    area = rig["area"]
    l_cp = lout - (rig["blade"] - 0.260)   # CP from thole, plan
    cycle = 60.0 / r_spm
    if t_drive is None:
        t_drive = cycle * 0.333
    N = int(n_pts)
    dt = t_drive / N
    # constant angular speed through the drive (Caplan & Gardner use measured
    # omega ~ flat across the drive); blade is only immersed during the
    # effective pull, so no deadpoint taper
    omega_mean = sweep / t_drive

    Fx_sum = 0.0; Ft_sum = 0.0; Th_sum = 0.0; Fh_rms = 0.0; Fb_peak = 0.0
    Fx_neg = 0.0
    xs, Fx_arr, Fh_arr, Fb_arr, vn_arr = [], [], [], [], []
    for i in range(N):
        t = dt * i
        C = sweep / 2 - sweep * (i / (N - 1))
        w = -omega_mean
        ux, uy = math.sin(C), math.cos(C)
        cf = math.cos(math.radians(rig.get("cant", 0.0)))   # plan §16.1
        nx, ny = math.cos(C) * cf, -math.sin(C) * cf  # blade face normal (plan)
        # normal flow at the blade CP: the ship's flow on the canted normal
        # (V·nx) minus the blade's own speed along it (l_cp·w) — the direct
        # form, consistent with ll/blade.py (plan §16.1)
        vn = V * nx + l_cp * w
        # pressure force on water, opposes vn; on hull = reaction
        Fn = 0.5 * RHO * area * CN * abs(vn) * vn
        Fbx = -Fn * nx                                # force on hull, x
        Fby = -Fn * ny
        Fb = abs(Fn)                                # full blade force (the
                                                     # rower balances it in
                                                     # the plane, plan §16.1)
        Fh = abs(Fn) * l_cp / lin
        Fx_sum += Fbx * dt
        Ft_sum += Fbx * V * dt
        Th_sum += Fh * abs(w) * lin * dt
        Fh_rms += Fh * Fh * dt
        Fb_peak = max(Fb_peak, Fb)
        if Fbx < 0: Fx_neg += -Fbx * dt
        xs.append(C); Fx_arr.append(Fbx); Fh_arr.append(Fh)
        Fb_arr.append(Fb); vn_arr.append(vn)

    T_cycle = cycle
    mean_thrust = Fx_sum / T_cycle
    mean_fh = math.sqrt(Fh_rms / t_drive)
    eff = Ft_sum / (Th_sum + 1e-12)
    return dict(mean_thrust=mean_thrust, mean_fh=mean_fh, fb_peak=Fb_peak,
                eff=eff, neg_frac=Fx_neg / (Fx_sum + 1e-12),
                xs=xs, Fx=Fx_arr, Fh=Fh_arr)

def main():
    print("=" * 78)
    print("W3 rigid-oar per-stroke refinement (flat-plate blade-force model)")
    print("=" * 78)
    print(f"Blade C_N = {CN} (flat plate; = Macon C_Dmax ~1.85, C&G 2007b), "
          f"rho={RHO}")
    print(f"{'rig':9} {'V kt':>5} {'spm':>5} {'thrust/oar':>11} {'eff':>6} "
          f"{'mean Fh':>8} {'peak Fb':>8}  Shaw bulk E / P")
    for name, rig, Vkt, r_spm in [("Olympias", "Olympias", 7.2, 28.8),
                                   ("Olympias", "Olympias", 8.2, 36.0),
                                   ("Mark IIb", "MarkIIb", 7.5, 28.8),
                                   ("Mark IIb", "MarkIIb", 9.7, 46.3)]:
        V = Vkt * KT
        s = rigid_stroke(V, RIGS[rig], r_spm, t_drive=T_DRIVE[(rig, Vkt)])
        P = 7.43 * r_spm
        E_bulk = 0.756 if name == "Olympias" else 0.780
        hull = 1.0 if name == "Olympias" else 1.08
        W_hull = hull * (155.0 * V**3 + 4.13 * V**5)
        W_req = W_hull / 170.0          # propulsive W/man the hull needs
        W_rigid = s['mean_thrust'] * V  # propulsive W/man the rigid model gives
        print(f"{name:9} {Vkt:5.1f} {r_spm:5.1f} {s['mean_thrust']:11.1f} "
              f"{s['eff']*100:5.1f}% {s['mean_fh']:8.0f} {s['fb_peak']:8.0f}   "
              f"E={E_bulk*100:.1f}%, P={P:.0f} N")
        print(f"{'':9} {'':5} {'':5} {'':11} {'':6} {'':8} {'':8}   "
              f"prop W/man rigid {W_rigid:5.0f} vs hull need {W_req:5.0f} "
              f"({W_rigid/W_req*100:3.0f}%)")
    print()
    print("Blade-area sensitivity at the design cruise points (what blade area the")
    print("flat-plate model needs to meet hull requirement; ch.9 notes Mark II needs")
    print("different/larger blades than Olympias):")
    for name, rig, Vkt, r_spm in [("Olympias", "Olympias", 7.2, 28.8),
                                   ("Mark IIb", "MarkIIb", 7.5, 28.8)]:
        V = Vkt * KT
        hull = 1.0 if name == "Olympias" else 1.08
        W_req = hull * (155.0 * V**3 + 4.13 * V**5) / 170.0
        base_area = RIGS[rig]["area"]
        s = rigid_stroke(V, RIGS[rig], r_spm, t_drive=T_DRIVE[(rig, Vkt)])
        need = base_area * W_req / (s['mean_thrust'] * V)
        print(f"  {name:9} base area {base_area:.3f} m^2 -> required ~{need:.3f} m^2 "
              f"(x{need/base_area:.1f})")

if __name__ == "__main__":
    main()
