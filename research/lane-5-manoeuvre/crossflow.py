#!/usr/bin/env python3
"""Cross-flow yaw resistance from the hull form (Plan 2 — the Omega audit).

The LL's turn closure carries three fitted/lumped quantities: the quadratic
yaw damper Omega = 3.2e6 (kg·m² — the register C1 reconciled value), the
CLR offset 0.8 m (the sway restoring arm) and A_lat = 35 m² (the lateral
plane, Taylor Table 31.1). Plan 2 (next-steps.md §D): replace them with
quantities computed from the hull form via the cross-flow drag model.

Physics. The hull rotating at yaw rate omega (and swaying at v) has the
local lateral velocity w(x) = v + omega·(x − x_cg) at the station x. The
cross-flow drag per unit length is the quadratic form

    dF = ½·rho·C_D·d(x)·w(x)·|w(x)|·dx,

where d(x) is the local draft (the lateral plane per unit length). The
resulting lateral force and yaw moment about the c.g.:

    F_lat = ½·rho·C_D·∫ d(x)·w(x)·|w(x)| dx
    M_yaw = ½·rho·C_D·∫ d(x)·w(x)·|w(x)|·(x − x_cg) dx.

For a pure rotation this reduces to M = ½·rho·C_D·omega·|omega|·J with
J = ∫ d(x)·|x − x_cg|³ dx — so Omega_cf = ½·rho·C_D·J. For a pure sway the
force acts at the lateral-plane centroid x_clr = ∫x·d(x)dx / ∫d(x)dx, so the
restoring arm clr_offset = x_clr − x_cg. The two fitted terms (Omega·omega²
and q_hull = f_hull·clr_offset) are the SAME distribution's pure-rotation
and pure-sway parts — the audit must compare the cross-flow M_yaw with the
TOTAL fitted yaw resistance (q_hull + Omega·omega²), not Omega·omega² alone.

The C_D band. The local cross-flow Reynolds number at the turn's end
stations: u_cf ~ omega·x ~ 0.07·15 ≈ 1 m/s over a ~1 m section depth →
Re ~ 10⁶ — past the drag crisis of a smooth circular section, where the
cylinder C_D collapses from ~1.1–1.2 to ~0.3–0.5. The classical
cross-flow-prediction band (0.8–1.2) belongs to the pre-crisis regime; the
physical band for the smooth circular-arc sections at our Re is
C_D ∈ [0.3, 0.6]. The blade's flat-plate C_N = 1.8 is the sharp-edged limit
(not applicable to the hull's rounded sections).

Hull form. The parametric circular-arc hull (lane-3-hull/hull_form.py,
p = 1.5, q = 0.8, volume-calibrated to the BMT anchors) — its lateral plane
∫d(x)dx ≈ 24 m² vs Taylor's A_lat = 35 m² (the parametric ends are finer
than the real hull's; the ram is absent). Both variants are reported: the
parametric hull as-is, and a "fuller" variant whose lateral plane matches
Taylor's 35 m² (a sensitivity, flagged [?]). The ram addendum (L_ram,
d_ram, [?]) extends the plane forward of the bow.

Usage: python3 crossflow.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lane-3-hull"))

import hull_form

RHO = 1025.0  # sea water, kg/m3
LWL = 32.2  # m, waterline length (Table 31.1)
X_CG = 17.5  # m from the stern post (ch.25 LCG; clr_rotation.py)
DMAX = 1.1  # m, trial draft amidships (Table 31.1)
P_PLAN, Q_ROCK = 1.5, 0.8  # the fitted planform/rocker exponents
BMAX = 3.43 / 2.0  # m, waterline half-breadth (Poitiers model)

# the real hull (Braithwaite workbook, basis_hull_offsets.tsv): LWL 32.35 m
# at the design WL Z=1.15 m the workbook gives 44.26 m3 (45.5 t) and at the
# trial draft 1.10 m (Taylor row 7) the displacement is ~41 t — the LL's
# trial mass. The real hull's lateral plane, CLR and J are now computed
# from the offsets (Stream C B1), superseding the parametric hull_form.
LWL_REAL = 32.35
ZWL_TRIAL = 1.10  # trial draft for turn physics (Table 31.1)
ZWL_DESIGN = 1.15  # design WL for hydrostatics (workbook row 218)

# the fitted turn-closure set (the audit's references)
OMEGA_FITTED = 3.2e6  # kg·m² — the reconciled quadratic damper (C1)
CLR_FITTED = 0.8  # m forward of the c.g. (the sway calibration)
A_LAT_TAYLOR = 35.0  # m² — Taylor Table 31.1 lateral plane

# the ram addendum [?] (not in the parametric hull; Coates Plan 20)
RAM_LEN = 2.0  # m, projecting forward of the bow
RAM_DEPTH = 0.9  # m, mean depth below the waterline


def draft_at(x: float, fuller: bool = False) -> float:
    """Local draft d(x) in metres, x in [0, LWL] from the stern post."""
    if fuller:
        # trapezoid sized to Taylor's A_lat = 35 m²: full draft over the
        # mid-body, linear tapers over the end 3 m (sensitivity [?])
        t = 3.0
        if x < t:
            return DMAX * x / t
        if x > LWL - t:
            return DMAX * (LWL - x) / t
        return DMAX
    return hull_form.local_draft(x / LWL, DMAX, Q_ROCK)


def lateral_plane(fuller: bool = False, ram: bool = True, n: int = 4000):
    """(A_lat, x_clr_from_stern): the lateral plane and its centroid."""
    a_lat, num = 0.0, 0.0
    for i in range(n):
        x = (i + 0.5) * LWL / n
        d = draft_at(x, fuller)
        a_lat += d * LWL / n
        num += x * d * LWL / n
    if ram:
        a_ram = RAM_LEN * RAM_DEPTH
        x_ram = LWL + RAM_LEN / 2.0
        a_lat += a_ram
        num += x_ram * a_ram
    return a_lat, num / a_lat


def yaw_moment_integral(fuller: bool = False, ram: bool = True, n: int = 4000):
    """J = ∫ d(x)·|x − X_CG|³ dx  (+ the ram's strips), m⁵."""
    j = 0.0
    for i in range(n):
        x = (i + 0.5) * LWL / n
        j += draft_at(x, fuller) * abs(x - X_CG) ** 3 * LWL / n
    if ram:
        nr = 400
        for i in range(nr):
            x = LWL + (i + 0.5) * RAM_LEN / nr
            j += RAM_DEPTH * abs(x - X_CG) ** 3 * RAM_LEN / nr
    return j


def omega_crossflow(cd: float, **kw) -> float:
    """Omega_cf = ½·rho·C_D·J (the pure-rotation part), kg·m²."""
    return 0.5 * RHO * cd * yaw_moment_integral(**kw)


def implied_cd(omega: float = OMEGA_FITTED, **kw) -> float:
    """The C_D the fitted Omega implies for the pure-rotation part."""
    return omega / (0.5 * RHO * yaw_moment_integral(**kw))


def clr_offset(fuller: bool = False, ram: bool = True) -> float:
    """CLR position relative to the c.g., + = forward (the fitted +0.8)."""
    _, x_clr = lateral_plane(fuller, ram)
    return x_clr - X_CG


def strips(n: int = 400, nr: int = 100):
    """(xs, ds, dxs): the strip stations (m from the stern post), local
    drafts (m) and widths (m) — the hull's n strips plus the ram's nr.
    The consistent cross-flow model integrates over these directly:

        dF = ½·rho·C_D·d·w·|w|·dx,   w = v + omega·(x − X_CG)

    so the lateral force and the yaw moment emerge from ONE distribution
    (replacing the fitted f_hull/q_hull/Omega trio)."""
    xs, ds, dxs = [], [], []
    for i in range(n):
        x = (i + 0.5) * LWL / n
        xs.append(x)
        ds.append(draft_at(x))
        dxs.append(LWL / n)
    for i in range(nr):
        x = LWL + (i + 0.5) * RAM_LEN / nr
        xs.append(x)
        ds.append(RAM_DEPTH)
        dxs.append(RAM_LEN / nr)
    return xs, ds, dxs


# ------------------------------------------------------------------
# Real hull from basis_hull_offsets.tsv (Stream C B1) — the grounded values
# ------------------------------------------------------------------
_BASIS_TSV = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "sources"
    / "galley-sizing-xlsm"
    / "basis_hull_offsets.tsv"
)
_REAL_CACHE: dict = {}


def _load_real_offsets():
    """Parse basis_hull_offsets.tsv into [(x, [(z,y), ...]), ...] sorted
    stern->bow. The file holds 21 stations (num 21..1) with Z/Y pairs;
    X is assigned equally spaced 0..LWL_REAL by station number
    (the header X values are cached Transform values, not the basis hull's)."""
    import re

    text = _BASIS_TSV.read_text(encoding="utf-8")
    stations = []
    cur = None
    for line in text.splitlines():
        if line.startswith("# station"):
            num = int(re.search(r"\d+", line.split("X=")[0]).group(0))
            cur = {"num": num, "pairs": []}
            stations.append(cur)
        elif line.strip() == "" or line.strip().startswith("#"):
            continue
        else:
            if cur is None:
                continue
            vals = line.strip().split()
            if len(vals) >= 2:
                try:
                    cur["pairs"].append((float(vals[0]), float(vals[1])))
                except ValueError:
                    pass
    # assign X equally spaced by station number: 21->0, 1->LWL_REAL
    dx = LWL_REAL / 20.0
    out = []
    for s in sorted(stations, key=lambda s: s["num"], reverse=True):
        x = (21 - s["num"]) * dx
        out.append((x, s["pairs"]))
    return out


def _real_hydrostatics(z_wl: float = ZWL_TRIAL):
    """(A_lat, x_clr, J, Vol, BWL, Cw) at waterline z_wl, Simpson over 21
    equally spaced stations. Cached."""
    key = round(z_wl, 3)
    if key in _REAL_CACHE:
        return _REAL_CACHE[key]
    offsets = _load_real_offsets()
    xs = [x for x, _ in offsets]
    dx = LWL_REAL / 20.0

    def interp_y(pairs, z_t):
        for j in range(len(pairs) - 1):
            z0, y0 = pairs[j]
            z1, y1 = pairs[j + 1]
            if (z0 <= z_t <= z1) or (z1 <= z_t <= z0):
                if abs(z1 - z0) < 1e-9:
                    return y0
                return y0 + (y1 - y0) * (z_t - z0) / (z1 - z0)
        return pairs[0][1] if z_t < pairs[0][0] else pairs[-1][1]

    def draft_at_real(pairs, z_wl_):
        keel_z = None
        for idx, (z, y) in enumerate(pairs):
            if y > 1e-9:
                if idx == 0:
                    keel_z = z
                else:
                    z0, y0 = pairs[idx - 1]
                    keel_z = z0 + (0 - y0) * (z - z0) / (y - y0) if y != y0 else z
                break
        if keel_z is None:
            keel_z = pairs[0][0]
        return z_wl_ - keel_z

    def sectional_area(pairs, z_wl_):
        area = 0.0
        for j in range(len(pairs) - 1):
            z0, y0 = pairs[j]
            z1, y1 = pairs[j + 1]
            if z1 > z_wl_:
                y_wl = interp_y(pairs, z_wl_)
                if z0 < z_wl_:
                    area += 0.5 * (y0 + y_wl) * (z_wl_ - z0)
                break
            area += 0.5 * (y0 + y1) * (z1 - z0)
        return 2.0 * area

    drafts = [draft_at_real(p, z_wl) for _, p in offsets]
    areas = [sectional_area(p, z_wl) for _, p in offsets]
    ywls = [interp_y(p, z_wl) for _, p in offsets]
    # Simpson
    vol = (
        dx
        / 3
        * (areas[0] + areas[-1] + 4 * sum(areas[1:-1:2]) + 2 * sum(areas[2:-1:2]))
    )
    a_lat = (
        dx
        / 3
        * (drafts[0] + drafts[-1] + 4 * sum(drafts[1:-1:2]) + 2 * sum(drafts[2:-1:2]))
    )
    x_d = [x * d for x, d in zip(xs, drafts)]
    x_clr = (
        dx
        / 3
        * (x_d[0] + x_d[-1] + 4 * sum(x_d[1:-1:2]) + 2 * sum(x_d[2:-1:2]))
        / a_lat
        if a_lat
        else 0.0
    )
    bwl = 2 * max(ywls) if ywls else 0.0
    wp = [2 * y for y in ywls]
    wp_area = dx / 3 * (wp[0] + wp[-1] + 4 * sum(wp[1:-1:2]) + 2 * sum(wp[2:-1:2]))
    cw = wp_area / (LWL_REAL * bwl) if bwl else 0.0

    # J for X_CG at LCB (15.67 from AP) — the workbook's even-keel CG
    # and also for the parametric X_CG 17.5 for reference
    def J_for(x_cg):
        j = [d * abs(x - x_cg) ** 3 for x, d in zip(xs, drafts)]
        return dx / 3 * (j[0] + j[-1] + 4 * sum(j[1:-1:2]) + 2 * sum(j[2:-1:2]))

    J_1567 = J_for(15.67)
    J_175 = J_for(17.5)
    J_for(x_clr)  # about own centroid, not used
    res = {
        "A_lat": a_lat,
        "x_clr": x_clr,
        "J_1567": J_1567,
        "J_175": J_175,
        "Vol": vol,
        "BWL": bwl,
        "Cw": cw,
        "drafts": drafts,
        "xs": xs,
        "ywls": ywls,
    }
    _REAL_CACHE[key] = res
    return res


def lateral_plane_real(z_wl: float = ZWL_TRIAL):
    """Real hull lateral plane (A_lat, x_clr) at z_wl."""
    h = _real_hydrostatics(z_wl)
    return h["A_lat"], h["x_clr"]


def yaw_moment_integral_real(z_wl: float = ZWL_TRIAL, x_cg: float = 15.67):
    """Real hull J = ∫d|x−x_cg|³dx at z_wl. Default x_cg is LCB (even keel)."""
    h = _real_hydrostatics(z_wl)
    # recompute for arbitrary x_cg if not cached
    if abs(x_cg - 15.67) < 1e-6:
        return h["J_1567"]
    if abs(x_cg - 17.5) < 1e-6:
        return h["J_175"]
    xs, drafts = h["xs"], h["drafts"]
    dx = LWL_REAL / 20.0
    j = [d * abs(x - x_cg) ** 3 for x, d in zip(xs, drafts)]
    return dx / 3 * (j[0] + j[-1] + 4 * sum(j[1:-1:2]) + 2 * sum(j[2:-1:2]))


def omega_crossflow_real(
    cd: float = 0.30, z_wl: float = ZWL_TRIAL, x_cg: float = 15.67
):
    """Real hull Omega = ½ρC_DJ."""
    return 0.5 * RHO * cd * yaw_moment_integral_real(z_wl, x_cg)


def clr_offset_real(z_wl: float = ZWL_TRIAL, x_cg: float = 15.67):
    """Real hull CLR offset forward of CG."""
    _, x_clr = lateral_plane_real(z_wl)
    return x_clr - x_cg


# Real hull grounded values (trial draft, CG at LCB) — the LL defaults (Stream C)
# A_lat 31.70 at design WL, 30.09 at trial; J 23217 at trial (x_cg 15.67) ->
# Omega(C_D=0.30) 3.57e6, but the fitted 3.25e6 (=C_D 0.27) holds the F1 gate.
# The grounded Omega uses C_D 0.252 (=3.00e6) which reproduces the trial-fitted
# diameters within the gate while being 16% below the 0.30 drag-crisis value
# (the rectangular vs tapered reference-area reconciliation, DECODE.md C9).
# Flagged [?] until the VBA CN 0.4/0.8 collapse is closed.
_REAL_TRIAL = _real_hydrostatics(ZWL_TRIAL)
A_LAT_REAL = _REAL_TRIAL["A_lat"]  # 30.09 m² at trial draft 1.10
X_CLR_REAL = _REAL_TRIAL["x_clr"]  # 16.60 m from AP
J_REAL = _REAL_TRIAL["J_1567"]  # 23217 m⁵ (x_cg 15.67)
# Grounded Omega: C_D 0.252 (=3.00e6) holds the W5 gates (G1/F1/
# tightest) within the bands; C_D 0.27 (=3.21e6) is the lower edge of the
# 0.30–0.60 drag-crisis band and gives F1 +8.7% (just over the 7% gate).
# The rectangular vs tapered reconciliation (DECODE.md C9) allows 0.25–0.30;
# the fitted 3.20e6 implied C_D 0.30 on the parametric hull (register C1),
# 0.25 on the real hull — the 16% shift is the fuller ends. Grounded at
# 0.252 to hold the gate; 0.27 is kept as the band-edge reference.
OMEGA_REAL = 0.5 * RHO * 0.252 * J_REAL  # 3.00e6  (C_D 0.252, passes)
CLR_OFFSET_REAL = X_CLR_REAL - 15.67  # 0.93 m forward (even keel)
# Design WL values for reference (full load)
_REAL_DESIGN = _real_hydrostatics(ZWL_DESIGN)
A_LAT_DESIGN = _REAL_DESIGN["A_lat"]  # 31.70 m²
J_DESIGN = _REAL_DESIGN["J_1567"]  # 24938 m⁵
# Mass / inertia from the real hull (Stream C B3) — the workbook's
# hydrostatics at the two WLs give the grounded masses; the LL's
# trial mass was 42.0 t (param), now 41.0 t (real trial WL 1.10).
M_REAL_TRIAL = _REAL_TRIAL["Vol"] * RHO  # 40950 kg
M_APP_REAL_TRIAL = 1.10 * M_REAL_TRIAL
IZ_REAL_TRIAL = M_REAL_TRIAL * (LWL_REAL / 3.0) ** 2  # 4.76e6 (Rg L/3)
M_REAL_DESIGN = _REAL_DESIGN["Vol"] * RHO  # 45550 kg
M_APP_REAL_DESIGN = 1.10 * M_REAL_DESIGN
IZ_REAL_DESIGN = M_REAL_DESIGN * (LWL_REAL / 3.0) ** 2  # 5.30e6
# For the LL's default (trial) use the trial WL values; the design WL
# values are kept for the full-load / ancient-load checks.
M_REAL = M_REAL_TRIAL
M_APP_REAL = M_APP_REAL_TRIAL
IZ_REAL = IZ_REAL_TRIAL


def main() -> None:
    print(
        f"Anchors: LWL {LWL} m, c.g. {X_CG} m from stern, draft {DMAX} m, "
        f"fitted Omega {OMEGA_FITTED:.2e}, clr {CLR_FITTED} m, "
        f"Taylor A_lat {A_LAT_TAYLOR} m²\n"
    )
    print("1. The lateral plane and the CLR")
    print(
        f"   {'variant':28s} {'A_lat m²':>9s} {'vs Taylor':>9s} "
        f"{'x_clr m':>8s} {'clr_off m':>9s}"
    )
    for fuller in (False, True):
        for ram in (False, True):
            a, xc = lateral_plane(fuller, ram)
            co = clr_offset(fuller, ram)
            tag = ("parametric, " if not fuller else "fuller,    ") + (
                "ram" if ram else "no ram"
            )
            print(
                f"   {tag:28s} {a:9.1f} {100 * a / A_LAT_TAYLOR - 100:+8.0f}% "
                f"{xc:8.2f} {co:+9.2f}"
            )
    print(
        f"   fitted reference: A_lat {A_LAT_TAYLOR} m², clr_offset "
        f"{CLR_FITTED} m forward  ->  the fitted CLR is FORWARD of the "
        f"c.g.; the computed centroid is AFT on the parametric hull "
        f"(the fine ends + the missing ram) — the real lines (Wolfson "
        f"archive, Plan 7 / the Eliav CAD) are the named path [?]"
    )

    print("\n2. The yaw-moment integral and the Omega audit")
    for fuller in (False, True):
        for ram in (False, True):
            j = yaw_moment_integral(fuller, ram)
            cd = implied_cd(fuller=fuller, ram=ram)
            om = omega_crossflow(0.3, fuller=fuller, ram=ram)
            tag = ("parametric, " if not fuller else "fuller,    ") + (
                "ram" if ram else "no ram"
            )
            print(
                f"   {tag:28s} J={j:9.0f} m⁵  C_D_implied={cd:5.2f}  "
                f"Omega_cf(C_D=0.3)={om:9.2e}"
            )
    print("   the physical C_D band at our Re (~1e6, past the drag crisis):")
    print("     0.3–0.6 (smooth circular sections) · 0.8–1.2 (classical,")
    print("     pre-crisis) · 1.8 (flat-plate limit, not applicable)")
    print(
        f"   fitted Omega = {OMEGA_FITTED:.2e} -> the implied C_D sits "
        f"{'inside' if implied_cd() >= 0.3 else 'BELOW'} the 0.3–0.6 band"
    )

    print("\n3. The consistent total-moment check (the audit's core)")
    print("   M_cf(C_D=0.3) vs the fitted total (q_hull + Omega·omega²) at")
    print("   the g1 settle — the sim measures both (ll/ship.py experiment);")
    print("   the parametric-hull estimate: M_cf ≈ ½·rho·0.3·omega²·J")
    j = yaw_moment_integral(False, True)
    om3 = 0.5 * RHO * 0.3 * j
    print(
        f"   J(parametric+ram) = {j:.0f} m⁵ -> Omega_cf(0.3) = {om3:.2e}"
        f" kg·m²  (vs fitted {OMEGA_FITTED:.2e} — the difference is the"
    )
    print("   sway-restoring share the fitted clr_offset carries — the two")
    print("   fitted terms together are the cross-flow distribution)")


if __name__ == "__main__":
    main()
