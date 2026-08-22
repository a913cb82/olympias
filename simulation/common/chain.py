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

# --- the computed cross-flow yaw damper (the Omega audit) ---
# Omega = ½·rho·C_D·J with C_D = 0.3 (the drag-crisis value for the smooth
# circular-arc sections at Re ~ 1e6) and J = ∫d·|x − x_cg|³dx over the
# parametric hull + the ram (crossflow.py) — the audit's closure: the
# trial-fitted 3.2e6 equals this at 1.6 % (the register C1 units caveat
# resolves: Omega IS the pure-rotation cross-flow moment). The fitted
# 3.2e6 stays the documented reference in the register.
OMEGA_CROSSFLOW = _cf.omega_crossflow(0.3)

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
