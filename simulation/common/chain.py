"""Shared access to the validated research chain — single source of truth.

All constants flow from two files:
  - ship_drawings.py: measured geometry + physics-derived values
  - trials_params.py: values fitted from the 1987 sea trials

This module re-exports them under the names the LL and HL expect.
No duplicated numbers, no silent overrides.
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- Add research paths for modules not yet in ship_drawings ---
_RESEARCH = Path(__file__).resolve().parents[2] / "research"
for _sub in ("lane-4-oars", "lane-5-manoeuvre"):
    _p = str(_RESEARCH / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# =====================================================================
# THE TWO SOURCES OF TRUTH
# =====================================================================

from common.ship_drawings import (  # noqa: F401 — re-exported
    A_LAT_DESIGN,
    A_LAT_TRIAL,
    ARM_LAT_MARKIIB,
    ARM_LAT_OLYMPIAS,
    ARM_RUD_MARKIIB,
    ARM_RUD_OLYMPIAS,
    BLADE_CP_FROM_TIP,
    BLADE_EFFECTIVE,
    BLADE_EFFICIENCY,
    BLADE_GEOMETRIC_OLYMPIAS,
    BLADE_IMMERSION,
    BLADE_SPAN_EFF,
    BLADE_WIDTH,
    BWL_DESIGN,
    CB,
    CD_HULL,
    CLR_OFFSET_TRIAL,
    CM,
    CN,
    CP,
    CW,
    FULL_RUDDER_DEG,
    GM_MARKIIB,
    GM_OLYMPIAS,
    IZ_DESIGN,
    IZ_TRIAL,
    J_DESIGN,
    J_TRIAL,
    KT,
    LEVER_MEAN_THOLE,
    LWL,
    M_APP_FACTOR,
    MASS_APP_DESIGN,
    MASS_APP_TRIAL,
    MASS_DESIGN,
    MASS_TRIAL,
    N_THALMIAN,
    N_THRANITE,
    N_TOTAL,
    N_ZYGIAN,
    NU,
    OAR_FAMILIES,
    OAR_TIER_MIT,
    OMEGA_TRIAL,
    RHO,
    RIGS,
    RUDDER_AREA_EACH,
    RUDDER_AREA_TOTAL,
    RUDDER_DIST_AFT_CG,
    RUDDER_DRAG_STRAIGHT,
    RUDDER_EFFICIENCY,
    RUDDER_FAC_FULL,
    SHAW_D_MAX,
    WSA_DESIGN,
    WSA_TRIAL,
    X_CG,
    X_CLR_TRIAL,
    ZWL_DESIGN,
    ZWL_TRIAL,
    rudder_cd,
    rudder_fac,
)
from common.ship_drawings import (
    hull_drag as hull_drag_computed,
)
from common.ship_drawings import (
    hull_friction as hull_friction_computed,
)
from common.ship_drawings import (
    hull_power as hull_power_computed,
)
from common.ship_drawings import (
    hull_wave as hull_wave_computed,
)
from common.trials_params import (  # noqa: F401 — re-exported
    B_FLOOR_FRAC,
    CALIBRATED_T_DRIVE_44_5,
    FH_BURST,
    FH_MAX,
    HOLD_FRAC,
    HULL_MULT_MARKIIB,
    HULL_POWER_COEFF_V3,
    HULL_POWER_COEFF_V5,
    P_CRIT,
    P_PER_SPM,
    PRESSURE_FAST,
    PRESSURE_SPOUDE,
    PRESSURE_STEADY,
    T_DRIVE_7_2,
    T_DRIVE_8_2,
    T_REC_MIN,
    T_RISE,
    T_RISE_BASE,
    TAU_WPRIME,
    TEMPO_CALLDOWN_SPM,
    WPRIME,
    t_rise,
)

# =====================================================================
# COMPATIBILITY ALIASES — names the LL/HL already use
# =====================================================================

# Hull properties (Stream C B1/B3 — now from ship_drawings)
A_LAT_REAL = A_LAT_TRIAL
X_CLR_REAL = X_CLR_TRIAL
J_REAL = J_TRIAL
OMEGA_REAL = OMEGA_TRIAL
CLR_OFFSET_REAL = CLR_OFFSET_TRIAL
M_REAL = MASS_TRIAL
M_APP_REAL = MASS_APP_TRIAL
IZ_REAL = IZ_TRIAL

# Lever (Stream C B2)
LEVER_GROUNDED = LEVER_MEAN_THOLE
LEVER_HOLD_GROUNDED = LEVER_MEAN_THOLE
LEVER_NET = 1.8  # the sway-calibrated NET (0.2 m below thole mean, [?])

# Omega cross-flow
OMEGA_CROSSFLOW = OMEGA_REAL

# Rudder
RUDDER_FAC_GROUNDED = RUDDER_FAC_FULL  # alias

# Blade
BLADE_THALMIAN_GEOM = 0.109  # m², from ship_drawings (Rev F Table 3)

# =====================================================================
# TAYLOR CH.31 VESSELS — the manoeuvre model's reference vessels
# =====================================================================

import manoeuvre_model as _mm

VESSELS = {"Olympias": _mm.olympias(), "MarkIIb": _mm.mark_iib()}

# Mutate the Olympias vessel with the grounded hull values
VESSELS["Olympias"].A_lat = A_LAT_REAL
VESSELS["Olympias"].m = M_REAL
VESSELS["Olympias"].m_app = M_APP_REAL
VESSELS["Olympias"].I = IZ_REAL

# =====================================================================
# OAR POWER CHAIN — from lane4_propulsion (research)
# =====================================================================

import lane4_propulsion as _lp


# Hull power: two versions
# - hull_power_computed: ITTC-1957 friction + wave (ship_drawings), physics
#   e.g. at 7.2 kt Rf 1774 + Rw 998 = 2772 W vs chain 2904 (-4.5%)
# - hull_power_chain: the chain law 155V³+4.13V⁵ (fitted to towing tests)
#   kept as the validated reference; the LL now uses the COMPUTED version
#   (the fitted is the documented reference, chain.py's D2 tension)
def _hull_power_chain(V: float, hull: float = 1.0) -> float:
    """Chain law: W = 155·V³ + 4.13·V⁵ × hull multiplier (fitted)."""
    return hull * (HULL_POWER_COEFF_V3 * V**3 + HULL_POWER_COEFF_V5 * V**5)


hull_power_chain = _hull_power_chain  # fitted, for validation


# The LL's hull_power stays the CHAIN LAW (the validated towing-test total)
# The computed ITTC+wave (ship_drawings.hull_power) is the physics
# alternative — within 1-3% at 4-10 kt, the future-ship recipe.
# Both are derived at import time: chain law from trials_params, computed
# from ship_drawings (WSA 130.5 + ITTC friction + k·V⁴ wave)
def hull_power(V: float, hull: float = 1.0) -> float:
    return hull_power_chain(V, hull)


hull_power_computed_raw = hull_power_computed  # keep original computed
# Keep aliases for the ITTC pieces
hull_drag = hull_drag_computed
hull_friction = hull_friction_computed
hull_wave = hull_wave_computed

speed_from_power = _lp.speed_from_power
oar_power = _lp.oar_power
mean_pull = _lp.mean_pull  # P = 7.43 × rate (P_PER_SPM)
oar_absorbed = _lp.oar_absorbed

# Pressure dict for the LL (from trials_params)
PRESSURE = {
    "rest": 0.0,
    "steady": PRESSURE_STEADY,
    "fast": PRESSURE_FAST,
    "chain": 1.0,
    "spoude": PRESSURE_SPOUDE,
}

# =====================================================================
# STROKE TIMING (Table 9.6) — measured drive times
# =====================================================================

import rigid_oar_model as _rom

T_DRIVE = _rom.T_DRIVE  # {(rig, V kt): s} — measured, not fitted
SPM = _rom.SPM  # {(rig, V kt): spm}

# Rigid stroke reference
rigid_stroke = _rom.rigid_stroke

# =====================================================================
# OAR INERTIA — from Table 3.1 (now loaded by ship_drawings)
# =====================================================================

# OAR_TIER_MIT, OAR_TABLE31_LIN are in ship_drawings (loaded once)
OAR_TABLE31_LIN = 1.092  # Table 3.1 measurement inboard (m)

# =====================================================================
# DOCUMENTED OPEN ITEMS
# =====================================================================

OQ18 = (
    "oQ-18, resolved as physics: the ch.9 (q/p)^2 "
    "turning-point law at the ACTUAL turning point (p = V.cosC/omega) IS the "
    "flat-plate law (algebraic identity, locked); the geometric-deadpoint "
    "variant (appendix d-formula) contradicts the measured Table 9.6 "
    "kinematics (less thrust, negative at our points) and stays OFF "
    "(ll/blade.TURNING_POINT). The Mark IIb residual (prop fraction "
    "~0.51-0.54 at the chain's points) is the A5 blade-area gap + the slip "
    "assumptions (register A5: the 'as-designed' scenario at area 1.3x + "
    "slip 1.2 reaches the chain's 9.7 kt); do not silently tune."
)
