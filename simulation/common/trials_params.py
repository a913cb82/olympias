"""Trials-fitted parameters — every value tuned to match the 1987 sea trials.

These are the numbers that cannot be computed from the ship's drawings.
They describe how the crew performed (effort, physiology) and how the
blade brakes when held stationary. Each is documented with the specific
trial(s) it was fitted to.

IMPORTANT: changing any value here must be followed by:
  1. Run the test suite: python3 -m pytest simulation -q
  2. Re-calibrate HL: python3 simulation/hl/calibrate.py
  3. Re-run validation: python3 simulation/harness/run_validation.py
"""

# =====================================================================
# CREW EFFORT — pressure levels (fitted to ch.7 cruise points)
# =====================================================================

# The chain law says: P = 7.43 × rate (N mean pull at the handle).
# At cruise (7-8 kt) the crew doesn't row at full chain pressure — they
# row at a fraction. The pressure levels reproduce the observed speeds:
#
# P = 7.43 × rate × pressure_factor
#
# Sources:
#   steady = 0.70: the sustainable cruising effort (≤ P_crit = 80 W/man,
#     Rossiter & Whipp, Rankov ch.23). Reproduces 7.0 kt at 25.5 spm.
#   fast = 0.85: the faster cruise (still below full sprint). Reproduces
#     7.5 kt at 28.8 spm.
#   spoude = 1.00: full sprint effort (the chain law itself). Reproduces
#     8.2-8.4 kt at 44.5 spm.
PRESSURE_STEADY = 0.70  # sustainable cruise (fitted to 7.0 kt @ 25.5 spm)
PRESSURE_FAST = 0.85  # fast cruise (fitted to 7.5 kt @ 28.8 spm)
PRESSURE_SPOUDE = 1.00  # full sprint (= chain law, no fit)

# =====================================================================
# ROWER PHYSIOLOGY — fitted to ch.9 sprint trial
# =====================================================================

# Drive time: how long each stroke's blade pushes water.
# From Table 9.6: measured drive times at 4 speeds for Olympias and Mark IIb.
# The LL uses the value at the cruise point (7.2 kt) for all speeds,
# adjusting sweep angle to fit the slot.
T_DRIVE_7_2 = 0.430  # s, at 7.2 kt cruise (Rankov Table 9.6)
T_DRIVE_8_2 = 0.392  # s, at 8.2 kt sprint (Rankov Table 9.6)

# Anaerobic capacity: how much energy a rower can expend above P_crit
# before they must slow down.
# Fitted to the ch.9 sprint: ~45 s at 44.5 spm reaching 8.2-8.4 kt.
# Chain excess 116.6 W/man × 45 s = 5.2 kJ (no inertia);
# force mode excess 133.4 W/man × 45 s = 6.0 kJ (includes flip).
# The ¾-NM run at 8.2 kt implies up to ~9.5 kJ (register D6 tension).
WPRIME = 6000.0  # J/man, anaerobic capacity

# W' refill time constant (Monod/MacFarlane/Nadel family)
TAU_WPRIME = 120.0  # s

# Peak handle force ceiling: the blade may not demand more than a rower
# can pull — the drive slows if exceeded.
FH_MAX = 700.0  # N per rower (provisional, model-implied from ch.9 sprint)

# Max mean handle force (the W'-limited burst level at any rate)
FH_BURST = 330.0  # N, chain sprint pull at 44.5 spm

# Minimum recovery time (body mechanics floor)
T_REC_MIN = 0.5  # s

# Usable-stroke floor as fraction of full sweep
B_FLOOR_FRAC = 0.4

# =====================================================================
# HOLD-WATER BRAKE — fitted to tightest turn + speed halving
# =====================================================================

# When blades are held stationary in the water (no rowing), they act as
# flat-plate brakes. The brake fraction is the fraction of the full blade
# area that effectively produces drag at the held angle (~19-20°).
#
# Fitted to TWO simultaneous anchors (one-parameter scan):
#   1. Tightest turn D = 62 m (halves speed, full rudder, one side stops)
#   2. Speed halving: 6.5 → ~3.25 kt (the trial's "halves speed")
#
# At hold_frac = 0.08: D = 62.7 m (−0.5% vs 62 m anchor),
#                       floor speed 3.22 kt (vs 3.25 target)
# At hold_frac = 0.05: D = 67.7 m (+9.2%), floor 3.54 kt (too gentle)
HOLD_FRAC = 0.08  # brake fraction (~19-20° blade angle to flow)

# =====================================================================
# CALIBRATED DRIVE TIME — beyond Table 9.6 (register A8)
# =====================================================================

# t_drive(44.5 spm) = 0.371 s: calibrated so the LL reproduces the ch.9
# four-run sprint (8.2-8.3 kt at 44.5 spm, ~130 effective rowers).
# The Gate-2 bracket analysis pointed to this value, now pinned
# (calibrate_tdrive.py).
CALIBRATED_T_DRIVE_44_5 = 0.371  # s, at 44.5 spm sprint

# =====================================================================
# ROWER PHYSIOLOGY — literature values (not fitted to Olympias)
# =====================================================================

# Critical power: the sustainable aerobic ceiling (Rossiter & Whipp,
# Rankov ch.23). Not fitted to Olympias — a general exercise-physiology
# constant. Self-consistent with ch.7: 7 kt ≈ 79.5 W handle.
P_CRIT = 80.0  # W/man external sustainable power

# Catch-flip duration: the time to reverse the oar from recovery to drive
# speed (pinned at the catch, the spike force over t_rise).
#
# COMPUTED FROM PHYSICS (not fitted):
#   T_RISE = MIT × (omega_drive + omega_recover) / (F_flip × lin)
#
# At the design point (cruise, 28.8 spm, 7.2 kt, steady pressure 0.70):
#   MIT = 9.74 kg·m² (spruce, Table 3.1)
#   omega_drive = sweep/t_drive = 0.840/0.430 = 1.952 rad/s
#   omega_recover = sweep/t_recovery = 0.840/1.653 = 0.508 rad/s
#   F_flip = pressure × FH_BURST (rower flips at their rowing effort)
#   At sprint (pressure=1.0): F_flip=330 N, T_RISE=0.076 s
#   At steady (pressure=0.70): F_flip=231 N, T_RISE=0.109 s
#   At fast (pressure=0.85): F_flip=281 N, T_RISE=0.089 s
#
# The flip force at T_RISE_BASE (0.076 s, sprint) equals FH_BURST.
# At cruise, the rower flips at 70% capacity (longer T_RISE).
import math as _math

from common.ship_drawings import (
    OAR_TIER_MIT as _MIT,
)
from common.ship_drawings import (
    RIGS as _RIGS,
)

_rig = _RIGS["Olympias"]
_sweep_rad = _math.radians(_rig["sweep"])
_t_drive_cruise = 0.430  # s at 7.2 kt (Table 9.6)
_cycle_cruise = 60.0 / 28.8  # s at 28.8 spm
_t_rec_cruise = _cycle_cruise - _t_drive_cruise
_omega_drive = _sweep_rad / _t_drive_cruise
_omega_recover = _sweep_rad / _t_rec_cruise
T_RISE_BASE = (
    _MIT["spruce"] * (_omega_drive + _omega_recover) / (330.0 * _rig["lin"])
)  # 0.076 s at sprint (pressure=1.0)


def t_rise(pressure: float) -> float:
    """Catch-flip duration for the current pressure level.

    The flip force scales with the rowing effort: F_flip = pressure × FH_BURST.
    At sprint (1.0): T_RISE=0.076 s; at steady (0.70): 0.109 s; at fast (0.85): 0.089 s.
    """
    p = max(0.1, pressure)  # avoid division by zero for 'rest' (0.0)
    return T_RISE_BASE / p


# Default: the steady value (the most common rowing pressure)
T_RISE = t_rise(0.70)  # 0.109 s at steady cruise

# =====================================================================
# CREW COORDINATION — estimated
# =====================================================================

# Tempo call-down: the sustained per-side rate gap (spm) that triggers
# the keleustes to call down both sides to the weaker rate. Estimated
# from the crew's ability to maintain asymmetry; not directly measured.
TEMPO_CALLDOWN_SPM = 2.0  # spm

# =====================================================================
# CHAIN LAW SLOPE — the reference rowing power
# =====================================================================

# P = 7.43 × rate (N mean pull at the handle per rower)
# This is the "chain law" — the reference power curve that the pressure
# levels scale. It comes from the calibrated 116-rower trial (ch.9):
#   W = 12100 W, n = 116, r = 38.75 spm, L = 0.78 m, E = 0.719
#   → P = 12100 × 60 / (116 × 0.78 × 38.75 × 0.719) = 287 N
#   → P/rate = 287/38.75 = 7.40 ≈ 7.43 (the small difference is
#     rounding in the original Shaw calculation)
P_PER_SPM = 7.43  # N/(spm·man), the chain law slope

# =====================================================================
# HULL POWER — the chain law (kept as reference, ITTC+wave is alternative)
# =====================================================================

# The chain law: W = 155·V³ + 4.13·V⁵ (V in m/s).
# Calibrated to the Grekoussis & Loukakis 1985 towing tests (1:10 model).
# The ITTC+wave computation (ship_drawings.hull_power) gives within 5%.
# This value is KEPT as the validated total; the ITTC+wave is the
# cross-check and the future-ship recipe.
HULL_POWER_COEFF_V3 = 155.0  # W·s³/m³, wave-dominant term
HULL_POWER_COEFF_V5 = 4.13  # W·s⁵/m⁵, prismatic correction

# Mark IIb hull multiplier (rudders fully deployed vs partly raised)
HULL_MULT_MARKIIB = 1.08

# =====================================================================
# SUMMARY
# =====================================================================


def summary() -> str:
    """One-line summary of the fitted parameters for logging."""
    return (
        f"Trials-fitted: t_drive {T_DRIVE_7_2} s, W' {WPRIME:.0f} J, "
        f"hold {HOLD_FRAC}, steady {PRESSURE_STEADY}, fast {PRESSURE_FAST}, "
        f"P/rate {P_PER_SPM}"
    )
