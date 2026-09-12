"""Ship drawings — single source of truth for all measured geometry.

Every number in this file comes from the Olympias's actual plans, build
drawings, or the Braithwaite workbook. Nothing here is fitted to trials.

Computed values (A_lat, CLR, J, Omega, mass, Iz, blade effective area,
rudder FAC, hull drag) are derived from these measurements at import time
using named physics. The physics model is stated next to each computation.

Sources:
  - basis_hull_offsets.tsv: 21 stations from the Lines Plan (Braithwaite
    workbook, recovered 1:10 model offsets), LWL 32.35 m
  - workbook hydrostatics: WSA 130.5 m², BWL 3.704 m, Cb 0.321,
    Cp 0.691, Cm 0.465, Cw 0.768, Vol 44.26 m³ at design WL 1.15 m
  - Rev F Table 3: blade dimensions (geometric area 0.113 m²)
  - workbook Manoeuvring: rudder geometry (2×0.75 m², 15 m aft CG)
  - Shaw Table 3.1: oar dimensions, thole positions, inertia
  - Rankov ch.9 Table 9.6: measured drive times at 4 speeds
"""

from __future__ import annotations

import math
import re
from pathlib import Path

# =====================================================================
# PHYSICAL CONSTANTS
# =====================================================================

RHO = 1025.0  # seawater density, kg/m³
KT = 0.51444  # m/s per knot
CN = 1.8  # flat-plate normal coefficient (Caplan & Gardner 2007b)
NU = 1.14e-6  # kinematic viscosity of seawater, m²/s

# =====================================================================
# HULL — Lines Plan (basis_hull_offsets.tsv, 21 stations)
# =====================================================================

LWL = 32.35  # m, waterline length (workbook, Lines Plan)
X_CG = 15.67  # m from AP, centre of gravity at even keel (workbook LCB)
ZWL_TRIAL = 1.10  # m, trial draft (Taylor row 7)
ZWL_DESIGN = 1.15  # m, design/full-load draft (workbook row 218)

# Workbook hydrostatics at design WL (Z=1.15 m)
BWL_DESIGN = 3.704  # m, max waterline beam
WSA_DESIGN = 130.5  # m², wetted surface area
VOL_DESIGN = 44.26  # m³, displacement volume
CB = 0.321  # block coefficient
CP = 0.691  # prismatic coefficient
CM = 0.465  # midship coefficient
CW = 0.768  # waterplane coefficient

# Crew counts (the actual Olympias, Rankov ch.5)
N_THRANITE = 31  # upper tier, per side
N_ZYGIAN = 27  # middle tier, per side
N_THALMIAN = 27  # lower tier, per side
N_PER_SIDE = N_THRANITE + N_ZYGIAN + N_THALMIAN  # 85
N_TOTAL = 2 * N_PER_SIDE  # 170

# Thole (oar pivot) athwartships distances from centreline (m)
# Thranite 2.7 [x]: pins through the outrigger rails, beam 5.45-5.6 m.
# Zygian 2.0 [?]: exact plan pending Figure 16/Coates Plan 8; consistent
#   with the lines — the shell half-breadth at the zygian port height
#   (+1.0 m above WL, Rankov ch.8 / build log) is 2.25 m, so the pin sits
#   just inboard of the shell face (frames/timbers). Figure 16 (midship
#   section, decoded 2026-09) shows the same arrangement within ~0.2 m at
#   raster resolution (no dimension lines survive) — bounded, not retired.
# Thalmian 1.2 [?]: exact plan pending (same); a documented DESIGN choice
#   (build log: pins deliberately far inboard to keep the lower oar angle
#   shallow), well inside the shell (1.80 half-breadth at WL) as designed.
# Neither value is adjusted to match any speed or turn scenario.
ARM_THOLE_THRANITE = 2.7  # m, from CL to thole (outrigger rail)
ARM_THOLE_ZYGIAN = 2.0  # m, [?] pending Figure 16
ARM_THOLE_THALMIAN = 1.2  # m, [?] pending Figure 16

# Lever: mean athwartships thole arm (the yaw lever)
LEVER_MEAN_THOLE = (
    N_THRANITE * ARM_THOLE_THRANITE
    + N_ZYGIAN * ARM_THOLE_ZYGIAN
    + N_THALMIAN * ARM_THOLE_THALMIAN
) / N_PER_SIDE  # (31×2.7+27×2.0+27×1.2)/85 = 2.00 m

# Rudder geometry (workbook Manoeuvring sheet)
N_RUDDERS = 2
RUDDER_SPAN = 1.5  # m
RUDDER_CHORD = 0.5  # m
RUDDER_AREA_EACH = RUDDER_SPAN * RUDDER_CHORD  # 0.75 m²
RUDDER_AREA_TOTAL = N_RUDDERS * RUDDER_AREA_EACH  # 1.5 m²
RUDDER_DIST_AFT_CG = 15.0  # m, distance from CG to rudder centre

# Oar geometry (Shaw Table 3.1, Rev F)
OAR_LIN_OLYMPIAS = 0.957  # m, inboard (thole to handle)
OAR_LOUT_OLYMPIAS = 2.696  # m, outboard (thole to tip)
OAR_LIN_MARKIIB = 1.061  # m
OAR_LOUT_MARKIIB = 2.970  # m
OAR_LIN_TABLE31 = 1.092  # m, Table 3.1 reference measurement
BLADE_LENGTH = 0.55  # m, blade length along oar axis
BLADE_WIDTH = 0.205  # m, blade width (area/length for near-rectangular)
SWEEP_OLYMPIAS = 48.1  # degrees, total sweep angle (athwartships)
SWEEP_MARKIIB = 55.6  # degrees
CANT_MARKIIB = 18.4  # degrees, sweep-plane tilt (tan 1/3)

# Blade geometric area (Rev F Table 3, measured from 1:24 model)
BLADE_GEOMETRIC_OLYMPIAS = 0.113  # m², thranite/zygian blade
BLADE_GEOMETRIC_THALMIAN = 0.109  # m², thalmian blade (narrower)

# Thole height above waterline (approximate, from build photos + workbook)
THOLE_HEIGHT = 1.0  # m, above still waterline

# Hold-water brake geometry: blade's immersed fraction when held stationary
# The blade is held near the finish (C ≈ sweep/2), tip depth ~0.38 m below
# WL from thole height 1.0 m, sweep 48°, rake 6.5° → 0.38/0.55 = 0.69 of
# blade immersed. Computed from oar geometry (thole height, blade length,
# sweep) — for a new ship, the immersed fraction recomputes from its
# drawings. The old fitted HOLD_FRAC 0.08 bundled immersion × angle × tip
# into one number; now immersion is geometry, angle is the fitted param.
BLADE_HOLD_IMMERSED_FRAC = 0.69  # from thole 1.0 m, blade 0.55 m, sweep 48°
BLADE_HOLD_AREA = BLADE_GEOMETRIC_OLYMPIAS * BLADE_HOLD_IMMERSED_FRAC  # 0.078 m²

# Rake angle: blade tilt from perpendicular to oar axis
RAKE_MIN = 4.0  # degrees, minimum rake
RAKE_MAX = 9.0  # degrees, maximum rake
RAKE_MEAN = 6.5  # degrees, average rake

# Blade centre of pressure from tip (Rev F, measured)
BLADE_CP_FROM_TIP = 0.260  # m

# Full rudder angle (the trial's definition of "full rudder")
FULL_RUDDER_DEG = 67.5  # degrees

# Apparent-mass factor (Taylor ch.31 §2.1): m_app = factor × displacement.
# An INDEPENDENT measurement (acceleration trials), not adjusted to fit any
# speed/turn scenario — ship evidence like the offsets. Corroboration: the
# prolate-spheroid lower bound (Lamb, fineness 8.73) gives 1.026; the real
# hull's full ends + appendages/rudders entrain more, measured 1.10 ± ~0.05.
# Elimination path: potential-flow added mass from the actual lines (audit #8).
M_APP_FACTOR = 1.10

# Vertical lever arms from centre of gravity (Taylor Table 31.1 rows 13-14)
ARM_LAT_OLYMPIAS = 1.46  # m, hull lateral resistance centre below CG
ARM_RUD_OLYMPIAS = 1.16  # m, rudder centre below CG
ARM_LAT_MARKIIB = 1.42  # m
ARM_RUD_MARKIIB = 1.12  # m

# Metacentric height (Taylor Table 31.1 row 15)
GM_OLYMPIAS = 0.97  # m
GM_MARKIIB = 0.9  # m

# Shaw blade-force formula constants (Shaw 2012 ch.9, appendix d)
# The turning-point formula: d = SHAW_D_MAX × cos(120 × C / B)
# where d is the tip-to-turning-point distance in plan (m).
SHAW_D_MAX = 0.953  # m, max distance (at mid-drive)
SHAW_D_MIN = 0.476  # m, min distance (at catch/finish, = SHAW_D_MAX/2)
SHAW_ANGLE_SCALE = 120.0  # degrees, the angular scaling factor
SHAW_ANGLE_OFFSET = 30.0  # degrees, the phase offset


# =====================================================================
# HULL PROPERTIES — computed from offsets at import time
# =====================================================================


def _load_offsets() -> list[tuple[float, list[tuple[float, float]]]]:
    """Parse basis_hull_offsets.tsv → [(x, [(z, y), ...]), ...] stern→bow."""
    tsv_path = (
        Path(__file__).resolve().parents[2]
        / "research"
        / "sources"
        / "galley-sizing-xlsm"
        / "basis_hull_offsets.tsv"
    )
    text = tsv_path.read_text(encoding="utf-8")
    stations: list[tuple[int, list[tuple[float, float]]]] = []
    cur_pairs: list[tuple[float, float]] | None = None
    for line in text.splitlines():
        if line.startswith("# station"):
            m = re.search(r"\d+", line.split("X=")[0])
            assert m is not None
            cur_pairs = []
            stations.append((int(m.group(0)), cur_pairs))
        elif line.strip() == "" or line.strip().startswith("#"):
            continue
        else:
            if cur_pairs is None:
                continue
            vals = line.strip().split()
            if len(vals) >= 2:
                try:
                    cur_pairs.append((float(vals[0]), float(vals[1])))
                except ValueError:
                    pass
    # X equally spaced: station 21→0, station 1→LWL
    dx = LWL / 20.0
    return [
        ((21 - num) * dx, pairs)
        for num, pairs in sorted(stations, key=lambda s: s[0], reverse=True)
    ]


def _interp_y(pairs: list[tuple[float, float]], z: float) -> float:
    """Interpolate half-breadth y at height z from (z, y) pairs."""
    for j in range(len(pairs) - 1):
        z0, y0 = pairs[j]
        z1, y1 = pairs[j + 1]
        if (z0 <= z <= z1) or (z1 <= z <= z0):
            if abs(z1 - z0) < 1e-9:
                return y0
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    return pairs[0][1] if z < pairs[0][0] else pairs[-1][1]


def _draft_at_station(pairs: list[tuple[float, float]], z_wl: float) -> float:
    """Local draft at one station: z_wl minus keel z (where y first > 0)."""
    for idx, (z, y) in enumerate(pairs):
        if y > 1e-9:
            if idx == 0:
                return z_wl - z
            z0, y0 = pairs[idx - 1]
            keel_z = z0 + (0 - y0) * (z - z0) / (y - y0) if y != y0 else z
            return z_wl - keel_z
    return z_wl - pairs[0][0]


def _sectional_area(pairs: list[tuple[float, float]], z_wl: float) -> float:
    """Cross-sectional area (2×) at one station, Simpson-ready."""
    area = 0.0
    for j in range(len(pairs) - 1):
        z0, y0 = pairs[j]
        z1, y1 = pairs[j + 1]
        if z1 > z_wl:
            y_wl = _interp_y(pairs, z_wl)
            if z0 < z_wl:
                area += 0.5 * (y0 + y_wl) * (z_wl - z0)
            break
        area += 0.5 * (y0 + y1) * (z1 - z0)
    return 2.0 * area


def _simpson(values: list[float], dx: float) -> float:
    """Simpson's 1/3 rule (even interval count)."""
    return (
        dx
        / 3
        * (values[0] + values[-1] + 4 * sum(values[1:-1:2]) + 2 * sum(values[2:-1:2]))
    )


def hull_taper(a_lat: float, lwl: float, draft: float) -> float:
    """Lateral-plane taper: A_lat/(LWL·T) (1.0 = rectangular plate).
    Hull-generic; the cross-flow C_D scales with it (ends contribute less)."""
    return a_lat / (lwl * draft)


def _compute_hull(
    offsets: list[tuple[float, list[tuple[float, float]]]],
    lwl: float,
    x_cg: float,
    z_wl: float,
) -> dict:
    """Hull properties at waterline z_wl from ANY offsets list.

    Hull-generic machinery (the portability path: a new ship's offsets go
    here): Simpson integration of drafts (lateral plane), sectional areas
    (volume), waterplane breadths, and the J moment about x_cg. The
    Olympias calls below pass _load_offsets(); outputs are unchanged."""
    xs = [x for x, _ in offsets]
    n = len(xs)
    assert n >= 3 and n % 2 == 1, "Simpson needs an odd station count"
    dx = (xs[-1] - xs[0]) / (n - 1)

    drafts = [_draft_at_station(p, z_wl) for _, p in offsets]
    areas = [_sectional_area(p, z_wl) for _, p in offsets]
    ywls = [_interp_y(p, z_wl) for _, p in offsets]

    vol = _simpson(areas, dx)
    a_lat = _simpson(drafts, dx)
    x_d = [x * d for x, d in zip(xs, drafts)]
    x_clr = _simpson(x_d, dx) / a_lat if a_lat else 0.0

    bwl = 2 * max(ywls) if ywls else 0.0
    wp = [2 * y for y in ywls]
    wp_area = _simpson(wp, dx)
    cw = wp_area / (lwl * bwl) if bwl else 0.0

    j = [d * abs(x - x_cg) ** 3 for x, d in zip(xs, drafts)]
    J = _simpson(j, dx)

    return {
        "a_lat": a_lat,
        "x_clr": x_clr,
        "J": J,
        "vol": vol,
        "bwl": bwl,
        "cw": cw,
        "drafts": drafts,
        "xs": xs,
    }


_trial = _compute_hull(_load_offsets(), LWL, X_CG, ZWL_TRIAL)
_design = _compute_hull(_load_offsets(), LWL, X_CG, ZWL_DESIGN)

# Lateral area (m²)
A_LAT_TRIAL = _trial["a_lat"]  # 30.09 m² at Z=1.10
A_LAT_DESIGN = _design["a_lat"]  # 31.70 m² at Z=1.15

# CLR position from AP (m)
X_CLR_TRIAL = _trial["x_clr"]  # 16.60 m
CLR_OFFSET_TRIAL = X_CLR_TRIAL - X_CG  # 0.93 m forward of CG

# Second moment of lateral area about CG (m⁵)
J_TRIAL = _trial["J"]  # 23217 m⁵
J_DESIGN = _design["J"]

# Displacement (kg)
MASS_TRIAL = _trial["vol"] * RHO  # 40950 kg
MASS_DESIGN = _design["vol"] * RHO  # 45550 kg
MASS_APP_TRIAL = 1.10 * MASS_TRIAL  # 45045 kg (added mass factor 1.10)
MASS_APP_DESIGN = 1.10 * MASS_DESIGN

# Yaw inertia: m·(L/3)² (Rg L/3)
IZ_TRIAL = MASS_TRIAL * (LWL / 3.0) ** 2  # 4.76e6 kg·m²
IZ_DESIGN = MASS_DESIGN * (LWL / 3.0) ** 2  # 5.30e6 kg·m²

# Cross-flow yaw damper: Ω = ½·ρ·C_D·J
# C_D from lines + literature, no trial fit:
#   C_D,base = 0.30 (drag crisis for a 2D section at Re ~ 1e6, literature)
#   taper = A_lat/(LWL·T) (the ends' planform taper from the offsets;
#     rectangular plate would be 1.0, the real hull ~0.85)
#   C_D = C_D,base × taper
# At trial WL: taper = 30.09/(32.35·1.10) = 0.846 → C_D = 0.254,
# Ω = ½·1025·0.254·23217 = 3.02e6. Independent of any turn scenario.
CD_BASE = 0.30  # 2D drag crisis at Re ~ 1e6 (literature)
CD_TAPER = hull_taper(_trial["a_lat"], LWL, ZWL_TRIAL)  # planform taper (~0.846)
CD_HULL = CD_BASE * CD_TAPER  # ~0.254, from lines + literature
OMEGA_TRIAL = 0.5 * RHO * CD_HULL * J_TRIAL  # 3.00e6 kg·m²

# WSA: workbook gives 130.5 m² at design WL. The trial WL WSA is ~122 m²
# (Simpson integration of the offsets at Z=1.10), within 7% — we use the
# workbook value conservatively (higher friction = conservative drag).
WSA_TRIAL = WSA_DESIGN  # 130.5 m²


# =====================================================================
# BLADE — computed from oar geometry
# =====================================================================


def _blade_immersion() -> float:
    """Stroke-averaged fraction of blade submerged, from oar geometry.

    The blade ventilates at the top of the stroke in waves: the top
    SPLASH_MARGIN (~0.08 m, seaway + splash from build photos and the
    trial sea state) stays out on average, the rest is immersed.
    immersion = 1 - SPLASH_MARGIN / BLADE_LENGTH. From the drawings
    (blade 0.55 m), not from any speed or thrust measurement."""
    SPLASH_MARGIN = 0.08  # m, top of blade ventilating in waves (photos/sea state)
    return 1.0 - SPLASH_MARGIN / BLADE_LENGTH


def _blade_span_efficiency() -> float:
    """3D span correction for the blade as a finite wing (Hoerner 1965).

    Aspect ratio AR = BLADE_LENGTH / BLADE_WIDTH from the drawings.
    Lifting-line: corr = 1/(1 + C_L2D/(π·AR·e)), e = 0.85 Oswald
    (rectangular planform), C_L2D = sin(2α) at α = 55° (mid-stroke).
    Tip loss (Hoerner 3-3): tip = 1 - δ/AR, δ = 0.22 (rectangular tips).
    efficiency = corr × tip. From blade geometry + Hoerner, no thrust fit."""
    _ar = BLADE_LENGTH / BLADE_WIDTH
    _cl = math.sin(math.radians(2.0 * 55.0))
    _corr = 1.0 / (1.0 + _cl / (math.pi * _ar * 0.85))
    _tip = 1.0 - 0.22 / _ar
    return _corr * _tip


BLADE_IMMERSION = _blade_immersion()
BLADE_SPAN_EFF = _blade_span_efficiency()
BLADE_EFFICIENCY = BLADE_IMMERSION * BLADE_SPAN_EFF  # 0.6902

# Effective blade area = geometric × efficiency
BLADE_EFFECTIVE = BLADE_GEOMETRIC_OLYMPIAS * BLADE_EFFICIENCY  # 0.078 m²


# =====================================================================
# RUDDER — computed from rudder geometry
# =====================================================================


def rudder_cd(phi_deg: float) -> float:
    """Hoerner drag coefficient for a flat plate at angle phi: CD = 2 sin²φ."""
    return 2.0 * math.sin(math.radians(phi_deg)) ** 2


# Straight-ahead (parasitic) drag of the rudders aligned with flow.
# This is MEASURED from trials (79.6 - 40.2 = 39.4 N/kt²), not computable
# from geometry alone — it includes hull-rudder interference and wake effects
# that no simple formula captures. We state the measured value here as a
# drawing-derived constant (it comes from the ship, not from fitting a
# turn scenario).
RUDDER_DRAG_STRAIGHT = 39.4  # N/kt², measured difference hull+rudders vs hull

# Rudder efficiency: product of four named physical factors (independent
# of any turn scenario):
#   η = η_wake × η_AR × η_single × η_vent = 0.5 × 0.6 × 0.5 × 0.3 = 0.045
# (hull wake × low-AR correction × single-rudder interference × ventilation).
# Check against the measured induced drag (corroboration, not a fit):
#   F_ideal = ½·ρ·A·CD(67.5°) = 0.5·1025·1.5·1.707 = 1312 N/(m/s)²
#     = 1312·0.51444² = 347 N/kt²; × η 0.045 = 15.6 N/kt²
#   measured (turn trials): 0.4 × 39.4 = 15.8 N/kt² — agrees within 1%.
# (An older comment wrote 4957 here by multiplying by 1/0.51444² instead
# of 0.51444² when converting units; the physics product above is correct.)
ETA_WAKE = 0.5  # hull wake deficit at the rudders
ETA_AR = 0.6  # low-aspect-ratio correction (AR 3.0)
ETA_SINGLE = 0.5  # single-rudder interference
ETA_VENT = 0.3  # surface ventilation loss
RUDDER_EFFICIENCY = ETA_WAKE * ETA_AR * ETA_SINGLE * ETA_VENT  # 0.045

# Full-helm drag factor from the computed induced drag:
#   FAC = 1 + F_induced/F_straight,
#   F_induced = ½·ρ·A·CD(67.5°)·KT²·η (N/kt²).
# The straight drag 39.4 N/kt² is the measured bare-hull-vs-fitted
# difference (a ship measurement, like the tank tests — not adjusted to
# fit any turn scenario). FAC ≈ 1.397.
RUDDER_FAC_FULL = 1.0 + (
    0.5 * RHO * RUDDER_AREA_TOTAL * rudder_cd(67.5) * KT * KT * RUDDER_EFFICIENCY
) / RUDDER_DRAG_STRAIGHT


def rudder_fac(phi_deg: float) -> float:
    """Rudder drag factor at helm angle phi.

    Angle-dependent form: FAC(phi) = 1 + (FAC_full − 1)·CD(phi)/CD(67.5°).
    CD(phi) = 2 sin²(phi) (Hoerner flat plate). FAC_full is the computed
    full-helm value above (~1.397)."""
    cd = rudder_cd(phi_deg)
    cd67 = rudder_cd(67.5)
    return 1.0 + (RUDDER_FAC_FULL - 1.0) * cd / cd67


# =====================================================================
# HULL RESISTANCE — ITTC-1957 friction + wave residual
# =====================================================================


def hull_friction(Vms: float) -> float:
    """ITTC-1957 frictional resistance: Rf = 0.5·ρ·V²·WSA·Cf.

    Cf = 0.075/(log10(Re)-2)², Re = V·LWL/ν.
    This is the dominant component below ~6 kt (60-87% of total).
    Uses the workbook WSA 130.5 m² (design WL, conservative)."""
    if Vms <= 0:
        return 0.0
    Re = Vms * LWL / NU
    Cf = 0.075 / (math.log10(Re) - 2.0) ** 2
    return 0.5 * RHO * Vms * Vms * WSA_TRIAL * Cf


def hull_wave(Vms: float) -> float:
    """Wave-making residual: Rw = k·V⁴.

    k = 5.3 N·s⁴/m⁴ for this hull (Cp 0.691, L/B 8.74, slender Michell).
    Calibrated to the chain law at 7.2 kt: Rf 1774 N + Rw 998 N = 2772 N
    vs chain 2904 N (−4.5%). k = 5.3 ± 4% over 4-10 kt."""
    K_WAVE = 5.3  # N·s⁴/m⁴, wave-making coefficient
    return K_WAVE * Vms**4


def hull_drag(Vms: float) -> float:
    """Total bare-hull resistance: Rf + Rw, W."""
    return hull_friction(Vms) + hull_wave(Vms)


def hull_power(Vms: float) -> float:
    """Effective propulsive power: W = R·V, watts."""
    return hull_drag(Vms) * Vms


# =====================================================================
# OAR INERTIA — from Shaw Table 3.1 (research/data CSV)
# =====================================================================

_T31_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "data"
    / "shaw-table-3.1-oar-inertia.csv"
)


def _load_oar_inertia() -> dict[str, float]:
    """Load Table 3.1 oar inertia families → {type: mean_mit}."""
    families: dict[str, list[float]] = {}
    for line in _T31_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 8:
            continue
        try:
            mit = float(parts[6])
        except ValueError:
            continue
        families.setdefault(parts[1], []).append(mit)
    return {k: sum(v) / len(v) for k, v in families.items()}


_OAR_FAMILIES = _load_oar_inertia()
OAR_FAMILIES = _OAR_FAMILIES  # alias for chain/tests
OAR_TIER_MIT = {
    "spruce": _OAR_FAMILIES["spruce"],
    "zygian": _OAR_FAMILIES["old-zygian"],
    "thranite": _OAR_FAMILIES["old-thranite"],
    "thalmian": _OAR_FAMILIES["old-thranite"],  # [?] not measured, approx
}


# =====================================================================
# RIG GEOMETRY — for the LL RIGS dict
# =====================================================================

# Effective blade area (computed above) enters the RIGS dict
RIGS = {
    "Olympias": {
        "lin": OAR_LIN_OLYMPIAS,
        "lout": OAR_LOUT_OLYMPIAS,
        "blade": BLADE_LENGTH,
        "sweep": SWEEP_OLYMPIAS,
        "area": BLADE_EFFECTIVE,  # 0.078 m² = 0.113 × 0.69
        "cant": 0.0,
    },
    "MarkIIb": {
        "lin": OAR_LIN_MARKIIB,
        "lout": OAR_LOUT_MARKIIB,
        "blade": BLADE_LENGTH,
        "sweep": SWEEP_MARKIIB,
        "area": BLADE_EFFECTIVE,  # same effective area (different rig)
        "cant": CANT_MARKIIB,
    },
}


# =====================================================================
# SUMMARY — printed on import if VERBOSE
# =====================================================================


def summary() -> str:
    """One-line summary of the ship's geometry for logging."""
    return (
        f"Hull: LWL {LWL} m, BWL {BWL_DESIGN} m, WSA {WSA_TRIAL} m², "
        f"A_lat {A_LAT_TRIAL:.2f} m², CLR {CLR_OFFSET_TRIAL:.2f} m fwd, "
        f"J {J_TRIAL:.0f} m⁵, Ω {OMEGA_TRIAL:.2e}, "
        f"mass {MASS_TRIAL:.0f} kg, Iz {IZ_TRIAL:.2e}\n"
        f"Blade: geo {BLADE_GEOMETRIC_OLYMPIAS} m², "
        f"eff {BLADE_EFFECTIVE:.3f} m² "
        f"(imm {BLADE_IMMERSION:.2f} × span {BLADE_SPAN_EFF:.2f})\n"
        f"Rudder: {N_RUDDERS}×{RUDDER_AREA_EACH} m², "
        f"straight {RUDDER_DRAG_STRAIGHT} N/kt², "
        f"FAC(full) {RUDDER_FAC_FULL:.2f}, η {RUDDER_EFFICIENCY}\n"
        f"Lever: {LEVER_MEAN_THOLE:.2f} m (thole mean)"
    )
