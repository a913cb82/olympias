"""Shared access to the validated research chain — single source of truth.

Every constant the simulators use lives in the research modules; this module
only re-exports them (plan §2.3: shared assets, no duplicated numbers).
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

# --- units / blade law ---
KT = _rom.KT                 # 0.5148 m/s per knot
RHO = _rom.RHO               # seawater density, kg/m3
CN = _rom.CN                 # flat-plate normal coefficient, 1.8

# --- rig geometry (plan §2.3) ---
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

# --- documented open items the sims must inherit honestly ---
OQ18 = (
    "oQ-18: the flat-plate law with blade area 0.078 m2 under-predicts the "
    "Mark IIb points (~30-32 % of hull need; ch.9 notes Mark II needs ~x3.3 "
    "area). The LL reproduces the rigid model exactly but inherits this "
    "known shortfall; do not silently tune."
)
