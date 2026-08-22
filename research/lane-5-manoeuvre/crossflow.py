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

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lane-3-hull"))

import hull_form  # noqa: E402

RHO = 1025.0            # sea water, kg/m3
LWL = 32.2              # m, waterline length (Table 31.1)
X_CG = 17.5             # m from the stern post (ch.25 LCG; clr_rotation.py)
DMAX = 1.1              # m, trial draft amidships (Table 31.1)
P_PLAN, Q_ROCK = 1.5, 0.8      # the fitted planform/rocker exponents
BMAX = 3.43 / 2.0       # m, waterline half-breadth (Poitiers model)

# the fitted turn-closure set (the audit's references)
OMEGA_FITTED = 3.2e6    # kg·m² — the reconciled quadratic damper (C1)
CLR_FITTED = 0.8        # m forward of the c.g. (the sway calibration)
A_LAT_TAYLOR = 35.0     # m² — Taylor Table 31.1 lateral plane

# the ram addendum [?] (not in the parametric hull; Coates Plan 20)
RAM_LEN = 2.0           # m, projecting forward of the bow
RAM_DEPTH = 0.9         # m, mean depth below the waterline


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


def main() -> None:
    print(f"Anchors: LWL {LWL} m, c.g. {X_CG} m from stern, draft {DMAX} m, "
          f"fitted Omega {OMEGA_FITTED:.2e}, clr {CLR_FITTED} m, "
          f"Taylor A_lat {A_LAT_TAYLOR} m²\n")
    print("1. The lateral plane and the CLR")
    print(f"   {'variant':28s} {'A_lat m²':>9s} {'vs Taylor':>9s} "
          f"{'x_clr m':>8s} {'clr_off m':>9s}")
    for fuller in (False, True):
        for ram in (False, True):
            a, xc = lateral_plane(fuller, ram)
            co = clr_offset(fuller, ram)
            tag = ("parametric, " if not fuller else "fuller,    ") + \
                  ("ram" if ram else "no ram")
            print(f"   {tag:28s} {a:9.1f} {100*a/A_LAT_TAYLOR-100:+8.0f}% "
                  f"{xc:8.2f} {co:+9.2f}")
    print(f"   fitted reference: A_lat {A_LAT_TAYLOR} m², clr_offset "
          f"{CLR_FITTED} m forward  ->  the fitted CLR is FORWARD of the "
          f"c.g.; the computed centroid is AFT on the parametric hull "
          f"(the fine ends + the missing ram) — the real lines (Wolfson "
          f"archive, Plan 7 / the Eliav CAD) are the named path [?]")

    print("\n2. The yaw-moment integral and the Omega audit")
    for fuller in (False, True):
        for ram in (False, True):
            j = yaw_moment_integral(fuller, ram)
            cd = implied_cd(fuller=fuller, ram=ram)
            om = omega_crossflow(0.3, fuller=fuller, ram=ram)
            tag = ("parametric, " if not fuller else "fuller,    ") + \
                  ("ram" if ram else "no ram")
            print(f"   {tag:28s} J={j:9.0f} m⁵  C_D_implied={cd:5.2f}  "
                  f"Omega_cf(C_D=0.3)={om:9.2e}")
    print("   the physical C_D band at our Re (~1e6, past the drag crisis):")
    print("     0.3–0.6 (smooth circular sections) · 0.8–1.2 (classical,")
    print("     pre-crisis) · 1.8 (flat-plate limit, not applicable)")
    print(f"   fitted Omega = {OMEGA_FITTED:.2e} -> the implied C_D sits "
          f"{'inside' if implied_cd() >= 0.3 else 'BELOW'} the 0.3–0.6 band")

    print("\n3. The consistent total-moment check (the audit's core)")
    print("   M_cf(C_D=0.3) vs the fitted total (q_hull + Omega·omega²) at")
    print("   the g1 settle — the sim measures both (ll/ship.py experiment);")
    print("   the parametric-hull estimate: M_cf ≈ ½·rho·0.3·omega²·J")
    j = yaw_moment_integral(False, True)
    om3 = 0.5 * RHO * 0.3 * j
    print(f"   J(parametric+ram) = {j:.0f} m⁵ -> Omega_cf(0.3) = {om3:.2e}"
          f" kg·m²  (vs fitted {OMEGA_FITTED:.2e} — the difference is the")
    print("   sway-restoring share the fitted clr_offset carries — the two")
    print("   fitted terms together are the cross-flow distribution)")


if __name__ == "__main__":
    main()
