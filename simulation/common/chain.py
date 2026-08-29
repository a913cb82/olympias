"""Shared access to the validated research chain — single source of truth.

Every constant the simulators use lives in the research modules; this module
only re-exports them (2: shared assets, no duplicated numbers).
"""

import sys
from pathlib import Path

_RESEARCH = Path(__file__).resolve().parents[2] / "research"
for _sub in ("lane-4-oars", "lane-5-manoeuvre"):
    _p = str(_RESEARCH / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import crossflow as _cf
import lane4_propulsion as _lp
import manoeuvre_model as _mm
import rigid_oar_model as _rom

# --- units / blade law ---
KT = _rom.KT  # 0.5148 m/s per knot
RHO = _rom.RHO  # seawater density, kg/m3
CN = _rom.CN  # flat-plate normal coefficient, 1.8

# --- rig geometry (2) ---
RIGS = _rom.RIGS  # Olympias / MarkIIb: lin, lout, blade, sweep, area

# --- stroke timing (Table 9.6: duration of the effective pull, s) ---
T_DRIVE = _rom.T_DRIVE  # {(rig, V kt): s}
SPM = _rom.SPM  # {(rig, V kt): spm}

# --- validated reference models ---
rigid_stroke = _rom.rigid_stroke  # static per-stroke reference
hull_power = _lp.hull_power  # W hull needs at V (m/s); hull=1.08 Mark II
speed_from_power = _lp.speed_from_power
oar_power = _lp.oar_power  # W = n P L r E / 60
mean_pull = _lp.mean_pull  # P = 7.43 r  (N at butt)
oar_absorbed = _lp.oar_absorbed  # non-propulsive oar losses, W

# --- Taylor ch.31 manoeuvring vessels (turn-validated parameters) ---
VESSELS = {"Olympias": _mm.olympias(), "MarkIIb": _mm.mark_iib()}

# --- the real hull (Stream C B1/B3) — grounded from basis_hull_offsets.tsv ---
# A_lat, x_clr, J, Vol, mass and Iz are now computed from the Lines Plan
# (Braithwaite workbook, 21 stations, LWL 32.35 m) via crossflow.py's
# real-hull Simpson integration. The trial draft ZWL=1.10 m (Taylor row 7)
# gives the LL's trial mass; ZWL=1.15 m is the design/full-load WL.
# Omega = ½·rho·C_D·J with C_D = 0.252 (rectangular vs tapered
# reconciliation, DECODE.md C9) gives 3.00e6 on the real hull (J=23217)
# and holds the W5 turn gates (G1/F1/tightest) without regression; the
# parametric hull+ram gave 3.25e6 at C_D 0.30 (=1.6% from fitted 3.20e6,
# register C1) and 3.21e6 at C_D 0.27 — the fitted 3.20e6 implied C_D 0.30
# on the parametric hull, 0.25 on the real hull (the fuller ends). The
# parametric hull_form (p=1.5,q=0.8) is deleted.
A_LAT_REAL = _cf.A_LAT_REAL  # 30.09 m² at trial WL 1.10
X_CLR_REAL = _cf.X_CLR_REAL  # 16.60 m from AP
J_REAL = _cf.J_REAL  # 23217 m⁵ (x_cg 15.67)
OMEGA_REAL = _cf.OMEGA_REAL  # 3.00e6 (C_D 0.252, grounded)
CLR_OFFSET_REAL = _cf.CLR_OFFSET_REAL  # 0.93 m forward (x_clr - 15.67)
M_REAL = _cf.M_REAL  # 40950 kg (trial)
M_APP_REAL = _cf.M_APP_REAL  # 45045 kg
IZ_REAL = _cf.IZ_REAL  # 4.76e6 kg·m²  (m·(L/3)²)
# Design WL for reference
A_LAT_DESIGN = _cf.A_LAT_DESIGN
J_DESIGN = _cf.J_DESIGN
M_REAL_DESIGN = _cf.M_REAL_DESIGN  # 45550 kg
IZ_REAL_DESIGN = _cf.IZ_REAL_DESIGN

# Vessel overrides — the LL now sails the REAL hull (Stream C B1/B3
# grounded): A_lat, mass and Iz are the Lines-Plan values at the trial
# WL (LWL 32.35 m, Vol 39.95 m³ at Z=1.10). The research model
# (manoeuvre_model.olympias) stays as Taylor's Table 31.1 for reference;
# the LL's Vessel is mutated for the trial mass (40.95 t, M_app 45.05 t)
# and Iz 4.76e6 (m·(L/3)², Rg L/3) — the fitted 42.0 t / 4.0e6 is the
# documented reference (B3: the 2.5%/19% shift moves F1 +1.6% to 120.4 m,
# just over the 7% gate; the full-load 45.55 t / 5.30e6 is kept as the
# design reference, DECODE B3). Stream C finish: 3 fitted lateral+masses
# (Omega, CLR, mass) → 0 fitted (all computed from the Lines Plan).

# --- the grounded oar lever (Stream C B2) — the NET athwartships arm ---
# The fitted 1.8 m (sway-calibrated, p.15.3) is the NET yaw arm after the
# lateral dynamics (the hull's sway restoring + the per-station local-flow
# damping ~400 kN·m·s) are folded in. The physical thole mean is
# (31·2.7+27·2.0+27·1.2)/85 = 2.00 m (thranite 2.7 m grounded from beam
# 5.45–5.6 m, the outrigger rails; zygian 2.0 / thalmian 1.2 [?] pending
# Figure 16) and the blade mean is 4.82 m (the Taylor 4.8 confirmed as
# the BLADE arm, register C3). The NET 1.8 m sits 0.2 m below the thole
# mean — the 10% correction is the hull/or damping the sway now models
# explicitly. With the hull grounded (A_lat, CLR, Omega, mass/Iz) the NET
# lever's fitted residual is 0.2 m (was 3.0 m vs the blade arm) — the
# remaining fitted hull param is now 0 (the lever is the thole-mean
# geometry, the 0.2 m is the documented damping correction, not a free
# fit). The LEVER_HOLD brake arm is the same thole mean at the held
# angle (cos 90° = 0 → y_b = y_t), so 2.00 m as well (was 1.5 m fitted).
# Flagged [?] until the zygian/thalmian arms are pinned by Figure 16.
LEVER_MEAN_THOLE = (31 * 2.7 + 27 * 2.0 + 27 * 1.2) / 85.0  # 2.00 m
LEVER_NET = 1.8  # the sway-calibrated NET (the 0.2 m correction, [?])
LEVER_GROUNDED = LEVER_MEAN_THOLE  # 2.00 m — the grounded hull's lever
LEVER_HOLD_GROUNDED = LEVER_MEAN_THOLE  # 2.00 m — the held-blade brake
# For the closed gate the NET 1.8 m is kept as the validated value; the
# grounded 2.00 m is the documented geometry and the B2 trial (tightest
# 63.1→60.3 m, still within the 10% band, G1/F1 unchanged — the
# symmetric turns use no lever). Promotion of the grounded 2.00 m is the
# B2 gate-re-baselining step (see next-steps B2).
VESSELS["Olympias"].A_lat = A_LAT_REAL
VESSELS["Olympias"].m = M_REAL
VESSELS["Olympias"].m_app = M_APP_REAL
VESSELS["Olympias"].I = IZ_REAL

# --- the computed cross-flow yaw damper (the Omega audit, now grounded) ---
# Omega = ½·rho·C_D·J with C_D = 0.252 (real hull, J=23217 → 3.00e6).
# The parametric hull+ram gave 3.25e6 at C_D 0.30 (=1.6% from fitted
# 3.20e6, register C1); the real hull gives 3.21e6 at C_D 0.27. The
# fitted 3.20e6 stays the documented reference in the register.
OMEGA_CROSSFLOW = OMEGA_REAL


# --- Table 3.1 oar inertia families (shared asset; research/data CSV) ---
def _load_table31():
    rows = []
    path = (
        Path(__file__).resolve().parents[2]
        / "research"
        / "data"
        / "shaw-table-3.1-oar-inertia.csv"
    )
    with open(path, encoding="utf-8") as fh:
        for line in fh:
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
            rows.append({"oar": parts[0], "typ": parts[1], "mit": mit})
    return rows


_T31 = _load_table31()
OAR_FAMILIES = {}  # typ -> mean MIT about the thole (kg m2)
for _r in _T31:
    OAR_FAMILIES.setdefault(_r["typ"], []).append(_r["mit"])
OAR_FAMILIES = {k: sum(v) / len(v) for k, v in OAR_FAMILIES.items()}
# tier labels: the old-fir oars' measured tier (Table 3.1); the thalmian
# tier was not measured (rows 7-8 blank) — the thranite value is used as a
# documented approximation for the shorter thalmian oars
OAR_TIER_MIT = {
    "spruce": OAR_FAMILIES["spruce"],
    "zygian": OAR_FAMILIES["old-zygian"],
    "thranite": OAR_FAMILIES["old-thranite"],
    "thalmian": OAR_FAMILIES["old-thranite"],
}
OAR_TABLE31_LIN = 1.092  # Table 3.1 measurement inboard (m) — the reference
# spike convention; the LL oar uses its own lin

# --- documented open items the sims must inherit honestly ---
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
