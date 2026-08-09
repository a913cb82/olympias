#!/usr/bin/env python3
"""Parametric circular-arc hull model for Olympias (Lane 3, W2).

Coates defined Olympias' hull sections as circular arcs (Plan 3, "Table of
Hull Circular Arcs"): each station is a circular segment from keel to the two
gunwale corners at the waterline.  We reconstruct the underwater hull
parametrically from the firm dimensional anchors:

    LWL     32.2 m   (Taylor Table 31.1 row 6; Poitiers/CNRS model 32.08 m)
    B_wl     3.43 m  (Poitiers/CNRS model waterline beam, from Coates' lines)
    T_ams    1.1 m   (Taylor Table 31.1 row 7 "Draft")

and calibrate the waterline planform (pointed ends) so the volume at trial
condition matches the BMT displacement anchors:

    light   25.798 t  ->  25.17 m3 @ SG 1.025   (ch.25 inclining report)
    trial   42.25 t   ->  41.22 m3 @ SG 1.025   (ch.25, crew 80 kg each)

Pure stdlib.  Run: python3 hull_form.py
"""
import math

G = 9.81
RHO = 1025.0          # sea water kg/m3 (SG 1.025)
LWL = 32.2            # m, waterline length (Taylor Table 31.1)
DRAFT_AMS = 1.1       # m, design draft amidships (Table 31.1)
TRIAL_VOL = 42.25e3 / RHO   # m3  (= 41.22)
LIGHT_VOL = 25.798e3 / RHO  # m3  (= 25.17)


def segment_area(B, d):
    """Area of a circular segment: chord 2B (half-breadth B at waterline),
    sagitta d (depth below waterline), i.e. a Coates circular-arc section."""
    if B <= 0 or d <= 0:
        return 0.0, 0.0, 0.0
    R = (B * B + d * d) / (2.0 * d)
    # guard: chord must not exceed diameter
    if B >= R:
        B = R * 0.999999
        R = (B * B + d * d) / (2.0 * d)
    theta = 2.0 * math.asin(min(B / R, 1.0))
    area = R * R * (theta - math.sin(theta)) / 2.0
    perimeter = R * theta                       # arc length (wetted)
    return area, perimeter, R


def waterline_half_breadth(x, Bmax, p):
    """Half-breadth at waterline at fractional station x in [0,1].
    sin(pi*x)^p -> fine pointed ends, peak amidships."""
    return Bmax * (math.sin(math.pi * x) ** p)


def local_draft(x, dmax, q):
    """Local depth below waterline at station x.  dmax amidships; keel rocker
    brings it to zero at stem & stern (pointed ends)."""
    return dmax * (math.sin(math.pi * x) ** q)


def integrate(Bmax, p, q, dmax=DRAFT_AMS, n=400):
    """Integrate section areas/perimeters along the waterline -> volume + wetted area."""
    vol, wsa = 0.0, 0.0
    lcb_num = 0.0
    for i in range(n):
        x = (i + 0.5) / n                      # midpoint
        B = waterline_half_breadth(x, Bmax, p)
        d = local_draft(x, dmax, q)
        area, peri, _ = segment_area(B, d)
        vol += area * (LWL / n)
        wsa += peri * (LWL / n)
        lcb_num += area * x * (LWL / n)
    lcb = lcb_num / vol if vol else 0.0
    return vol, wsa, lcb


def waterplane_moment_inertia(Bmax, p, dmax, n=400):
    """Transverse (roll) second moment of area of the waterplane about centreline.

    I_t = (2/3) * integral of w(x)^3 dx over the waterline.
    """
    It = 0.0
    for i in range(n):
        x = (i + 0.5) / n
        B = waterline_half_breadth(x, Bmax, p)
        It += B ** 3
    return (2.0 / 3.0) * (LWL / n) * It


def solve_draft_for_volume(target_vol, Bmax, p, q, lo=0.1, hi=2.0):
    """Find amidships draft giving target volume (for light ship)."""
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        vol, _, _ = integrate(Bmax, p, q, dmax=mid)
        if vol > target_vol:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def vcb_and_lcb(Bmax, p, q, dmax, nx=240, nz=240):
    """Vertical and longitudinal centre of buoyancy via strip integration.

    Each transverse section is a circular-arc segment: chord at the waterline
    (z=d), arc apex on the keel (z=0).  Circle centre sits on the symmetry axis
    at z = R - d, so the local half-breadth at height z is
        w(z) = sqrt(R^2 - (z - (R-d))^2),   0 <= z <= d.
    Integrates w(z) over z (nz layers) then over x (nx stations).
    Returns (vcb above keel/apex line, lcb fraction from stern).
    """
    vol = 0.0
    vcb_num = 0.0
    lcb_num = 0.0
    for i in range(nx):
        x = (i + 0.5) / nx
        B = waterline_half_breadth(x, Bmax, p)
        d = local_draft(x, dmax, q)
        if d <= 0 or B <= 0:
            continue
        R = (B * B + d * d) / (2.0 * d)
        c = R - d                      # circle centre height above keel
        area = 0.0
        zbar_num = 0.0
        for j in range(nz):
            z1 = d * j / nz
            z2 = d * (j + 1) / nz
            zm = 0.5 * (z1 + z2)
            w2 = R * R - (zm - c) ** 2
            if w2 < 0:
                continue
            w = math.sqrt(w2)
            da = 2.0 * w * (z2 - z1)
            area += da
            zbar_num += da * zm
        vol += area
        vcb_num += area * (zbar_num / area)
        lcb_num += area * x
    return vcb_num / vol, lcb_num / vol


def block_coeff(vol, Bmax, dmax):
    return vol / (LWL * 2.0 * Bmax * dmax)


def main():
    # --- Calibrate Bmax so trial volume matches BMT anchor.
    # Start from the Poitiers waterline beam (2*Bmax = 3.43 m) and the
    # midship-section block shape; tune the planform exponent p.
    # p=1.0 -> elliptical planform (C_wp = 2/pi ~ 0.64); p=2 -> more pointed.
    print(f"Anchors: LWL={LWL} m, draft_ams={DRAFT_AMS} m, "
          f"trial vol={TRIAL_VOL:.2f} m3, light vol={LIGHT_VOL:.2f} m3\n")
    for p in (1.0, 1.4, 2.0):
        for q in (0.6, 0.8, 1.0):
            Bmax = 3.43 / 2.0
            vol, _, _ = integrate(Bmax, p, q)
            print(f"p={p:<4} q={q:<4} Bmax={Bmax:.3f} m -> vol={vol:.2f} m3 "
                  f"(trial target {TRIAL_VOL:.2f}) err={100*(vol-TRIAL_VOL)/TRIAL_VOL:+.1f}%")

    # --- Pick p,q that put trial volume within ~1% of target.
    best = None
    for p in (1.0, 1.1, 1.2, 1.3, 1.4, 1.5):
        for q in (0.7, 0.8, 0.9, 1.0):
            vol, wsa, lcb = integrate(3.43 / 2.0, p, q)
            err = abs(vol - TRIAL_VOL) / TRIAL_VOL
            if best is None or err < best[0]:
                best = (err, p, q, vol, wsa, lcb)
    err, p, q, vol, wsa, lcb = best
    Bmax = 3.43 / 2.0
    print(f"\nBest fit: p={p}, q={q}, Bmax={Bmax:.3f} m (2*Bmax={2*Bmax:.3f} m)")
    print(f"  trial volume   {vol:8.2f} m3  vs target {TRIAL_VOL:.2f} m3 "
          f"({100*err:+.1f}%)")
    print(f"  wetted surface {wsa:8.2f} m2")
    print(f"  LCB (from stern) {lcb*LWL:8.2f} m  (fraction {lcb:.3f})")

    # --- Derived hydrostatics at trial condition.
    Cb = block_coeff(vol, Bmax, DRAFT_AMS)
    Cwp = (sum(2 * waterline_half_breadth((i+0.5)/400, Bmax, p) * LWL/400
               for i in range(400))) / (LWL * 2 * Bmax)
    print(f"\nBlock coeff Cb = {Cb:.3f}")
    print(f"Waterplane area coeff Cwp = {Cwp:.3f}")

    # --- Light ship: solve for the draft that gives light volume.
    T_light = solve_draft_for_volume(LIGHT_VOL, Bmax, p, q)
    v_light, wsa_light, _ = integrate(Bmax, p, q, dmax=T_light)
    print(f"\nLight ship: draft = {T_light:.3f} m -> vol {v_light:.2f} m3 "
          f"({v_light*RHO/1000:.2f} t), wetted {wsa_light:.1f} m2")

    # --- Vertical centre of buoyancy (above baseline / keel underside) + KM.
    vcb, _ = vcb_and_lcb(Bmax, p, q, DRAFT_AMS)
    print(f"\nVCB above keel (baseline) at trial condition = {vcb:.3f} m")
    It = waterplane_moment_inertia(Bmax, p, DRAFT_AMS)
    BM = It / TRIAL_VOL                        # metacentric radius
    KM = vcb + BM                              # metacentre height above keel
    print(f"  waterplane I_t = {It:6.1f} m4 ;  BM = {BM:.3f} m ;  "
          f"KM (model) = {KM:.3f} m")
    print(f"  BMT ch.25 trial: KM = 2.90 m, KG = 1.77 m -> GM = 1.13 m "
          f"(model GM = {KM - 1.77:.2f} m)")

    # --- Weight check via wetted-surface friction (ITTC 1957 line):
    # Cf = 0.075/(log10(Re)-2)^2 ;  Rf = 0.5*rho*V^2*S*Cf.  Report at 3.5 m/s.
    for V in (2.0, 3.5, 4.3):
        Re = V * LWL / 1.14e-6
        Cf = 0.075 / (math.log10(Re) - 2.0) ** 2
        Rf = 0.5 * RHO * V * V * wsa * Cf
        print(f"  friction @ {V:4.1f} m/s: Cf={Cf:.5f}  Rf={Rf:8.0f} N "
              f"({Rf*V/1000:6.1f} kW)")
        # Shaw's law: W = 155V^3 + 4.13V^5
        W_shaw = 155 * V ** 3 + 4.13 * V ** 5
        print(f"      Shaw W = {W_shaw:8.0f} W  -> friction is "
              f"{100*Rf*V/W_shaw:.0f}% of total")

    # --- Cross-check vs Taylor Table 31.1 bare-hull drag 40.2 v^2 (v knots).
    # Skin fraction should be dominant below ~6.7 kt and ~equal to wave-making
    # near ~9 kt (Coates ch.22).
    print("\nTaylor bare-hull drag cross-check (T31.1 row 3: 40.2 v^2 N, v kt):")
    for vkt in (4.0, 5.0, 6.0, 6.7, 8.0, 9.0):
        V = vkt * 0.514444
        Re = V * LWL / 1.14e-6
        Cf = 0.075 / (math.log10(Re) - 2.0) ** 2
        Rf = 0.5 * RHO * V * V * wsa * Cf
        Rt = 40.2 * vkt * vkt
        Rw = max(Rt - Rf, 0.0)
        print(f"  {vkt:4.1f} kt: Rf={Rf:6.0f} N ({100*Rf/Rt:4.0f}%), "
              f"wave residual={Rw:6.0f} N ({100*Rw/Rt:4.0f}%)  "
              f"[Taylor Rt={Rt:.0f} N]")

    # --- Save machine-readable summary.
    with open("research/lane-3-hull/hull-form-summary.csv", "w") as f:
        f.write("parameter,value,unit,source\n")
        f.write(f"LWL,{LWL},m,Taylor T31.1 / Poitiers 32.08\n")
        f.write(f"B_wl,{2*Bmax:.3f},m,Poitiers model from Coates lines\n")
        f.write(f"draft_trial,{DRAFT_AMS},m,Taylor T31.1\n")
        f.write(f"draft_light,{T_light:.3f},m,computed from light vol 25.798 t\n")
        f.write(f"planform_p,{p},-,fitted\n")
        f.write(f"rocker_q,{q},-,fitted\n")
        f.write(f"vol_trial,{vol:.2f},m3,fitted to 42.25 t\n")
        f.write(f"vol_light,{v_light:.2f},m3,fitted to 25.798 t\n")
        f.write(f"wetted_trial,{wsa:.1f},m2,computed\n")
        f.write(f"wetted_light,{wsa_light:.1f},m2,computed\n")
        f.write(f"Cb_trial,{Cb:.3f},-,computed\n")
        f.write(f"Cwp,{Cwp:.3f},-,computed\n")
        f.write(f"LCB_from_stern,{lcb*LWL:.2f},m,computed\n")
    print("\nwrote research/lane-3-hull/hull-form-summary.csv")


if __name__ == "__main__":
    main()
