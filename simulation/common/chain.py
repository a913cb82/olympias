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

import rigid_oar_model as _rom  # noqa: E402
import lane4_propulsion as _lp  # noqa: E402
import manoeuvre_model as _mm  # noqa: E402
import crossflow as _cf  # noqa: E402  (Plan 2: the cross-flow yaw audit)

# --- units / blade law ---
KT = _rom.KT                 # 0.5148 m/s per knot
RHO = _rom.RHO               # seawater density, kg/m3
CN = _rom.CN                 # flat-plate normal coefficient, 1.8

# --- rig geometry (2) ---
RIGS = _rom.RIGS             # Olympias / MarkIIb: lin, lout, blade, sweep, area

# --- stroke timing (Table 9.6: duration of the effective pull, s) ---
T_DRIVE = _rom.T_DRIVE       # {(rig, V kt): s}
SPM = _rom.SPM               # {(rig, V kt): spm}

# --- validated reference models ---
rigid_stroke = _rom.rigid_stroke          # static per-stroke reference
hull_power = _lp.hull_power               # W hull needs at V (m/s); hull=1.08 Mark II
speed_from_power = _lp.speed_from_power
oar_power = _lp.oar_power                 # W = n P L r E / 60
mean_pull = _lp.mean_pull                 # P = 7.43 r  (N at butt)
oar_absorbed = _lp.oar_absorbed           # non-propulsive oar losses, W

# --- Taylor ch.31 manoeuvring vessels (turn-validated parameters) ---
VESSELS = {"Olympias": _mm.olympias(), "MarkIIb": _mm.mark_iib()}

# --- the real hull (Stream C B1/B3) — grounded from basis_hull_offsets.tsv ---
# A_lat, x_clr, J, Vol, mass and Iz are now computed from the Lines Plan
# (Braithwaite workbook, 21 stations, LWL 32.35 m) via crossflow.py's
# real-hull Simpson integration. The trial draft ZWL=1.10 m (Taylor row 7)
# gives the LL's trial mass; ZWL=1.15 m is the design/full-load WL.
# Omega = ½·rho·C_D·J with C_D = 0.27 (the lower edge of the 0.30–0.60
# drag-crisis band, rectangular vs tapered reconciliation, DECODE.md C9)
# reproduces the fitted 3.25e6 (=C_D 0.25–0.27) within the band and holds
# the W5 turn gates (G1/F1/tightest) without regression; the parametric
# hull_form (p=1.5,q=0.8) is deleted.
A_LAT_REAL = _cf.A_LAT_REAL              # 30.09 m² at trial WL 1.10
X_CLR_REAL = _cf.X_CLR_REAL              # 16.60 m from AP
J_REAL = _cf.J_REAL                      # 23217 m⁵ (x_cg 15.67)
OMEGA_REAL = _cf.OMEGA_REAL              # 3.21e6 (C_D 0.27)
CLR_OFFSET_REAL = _cf.CLR_OFFSET_REAL    # 0.93 m forward (x_clr - 15.67)
M_REAL = _cf.M_REAL                      # 40950 kg (trial)
M_APP_REAL = _cf.M_APP_REAL              # 45045 kg
IZ_REAL = _cf.IZ_REAL                    # 4.76e6 kg·m²  (m·(L/3)²)
# Design WL for reference
A_LAT_DESIGN = _cf.A_LAT_DESIGN
J_DESIGN = _cf.J_DESIGN
M_REAL_DESIGN = _cf.M_REAL_DESIGN        # 45550 kg
IZ_REAL_DESIGN = _cf.IZ_REAL_DESIGN

# Vessel overrides — the LL now sails the real hull for the lateral
# plane. The research model (manoeuvre_model.olympias) stays as Taylor's
# Table 31.1 for reference; the LL's Vessel is mutated only for A_lat
# (the lateral area that enters f_hull). Mass and I stay at the trial
# values (42.0 t / 4.0e6) — the full-load mass/Iz (45.5 t / 5.30e6) are
# kept as design references; the trial draft 1.10 m gives 40.95 t/4.76e6
# but the turn gates hold at the trial mass, so B3 is recorded as
# grounded but not promoted (the light/full reconciliation, DECODE B3).
VESSELS["Olympias"].A_lat = A_LAT_REAL
# Keep m/m_app/I/Omega at Taylor's trial values for the LL's turn gates;
# the real hull's masses are exposed as M_REAL etc. for the weight audit.
# (If the gates are re-baselined at the full-load mass, set below.)
# VESSELS["Olympias"].m = M_REAL  etc. — not promoted (see above).

# --- the computed cross-flow yaw damper (the Omega audit, now grounded) ---
# Omega = ½·rho·C_D·J with C_D = 0.27 (real hull, J=23217). The parametric
# hull + ram gave 3.25e6 at C_D 0.30 (=1.6% from fitted 3.20e6, register C1);
# the real hull gives 3.21e6 at C_D 0.27, and 3.00e6 at C_D 0.25 which also
# holds the gates with margin. The fitted 3.20e6 stays the documented
# reference in the register.
OMEGA_CROSSFLOW = OMEGA_REAL

# --- Table 3.1 oar inertia families (shared asset; research/data CSV) ---
def _load_table31():
    rows = []
    path = Path(__file__).resolve().parents[2] / "research" / "data" \
        / "shaw-table-3.1-oar-inertia.csv"
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
            rows.append(dict(oar=parts[0], typ=parts[1], mit=mit))
    return rows


_T31 = _load_table31()
OAR_FAMILIES = {}          # typ -> mean MIT about the thole (kg m2)
for _r in _T31:
    OAR_FAMILIES.setdefault(_r["typ"], []).append(_r["mit"])
OAR_FAMILIES = {k: sum(v) / len(v) for k, v in OAR_FAMILIES.items()}
# tier labels: the old-fir oars' measured tier (Table 3.1); the thalmian
# tier was not measured (rows 7-8 blank) — the thranite value is used as a
# documented approximation for the shorter thalmian oars
OAR_TIER_MIT = {"spruce": OAR_FAMILIES["spruce"],
                "zygian": OAR_FAMILIES["old-zygian"],
                "thranite": OAR_FAMILIES["old-thranite"],
                "thalmian": OAR_FAMILIES["old-thranite"]}
OAR_TABLE31_LIN = 1.092    # Table 3.1 measurement inboard (m) — the reference
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
