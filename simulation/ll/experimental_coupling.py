"""Step 3 spike — heel-coupled drift + drag coupling (OFF by default).

The investigation (investigation/01-04) found the three open items may be
coupled: if the ship leans (heels) into a turn, the lean creates a
sideways push that could explain the extra drift, and both the lean and
the drift create extra drag that could slow the turn.

This module is a *spike* — a cheap experiment behind a flag, not a
promoted layer. It adds three things when Ship(heel_coupling=True):

  1. Heel angle from the roll balance (Taylor ch.31 §2.3):
     heel = atan(tipping / (m·g·GM_eff))
     tipping = f_rud·arm_rud + f_hull·arm_lat,  GM_eff = GM − 0.2 m
     (crew lean into the turn — Taylor §2.3).

  2. A heel-coupled sideways force: the heeled hull's asymmetry pushes
     the ship sideways. Parameterised as F_heel = K_heel × sin(heel)
     (swept — no first-principles value exists).

  3. Extra drag from drift + heel: D_extra = D(V) × K_drag ×
     (sin²(beta) + sin²(heel)) — the hull working at an angle and heeled
     over drags more. K_drag swept.

The rudder inflow correction (drift + yaw crossflow at the stern,
≈15 m × omega ≈ 1 m/s lateral at 4°/s) is a second-order effect on
the rudder's own drag and is not included in this spike — the first
two items dominate the force magnitudes.

Usage:
  Ship(heel_coupling=True, heel_params=dict(K_heel=80000, K_drag=4.0))
  or with defaults: Ship(heel_coupling=True)

To measure: run the G1/F1/tightest turns + the 360° time and compare
drift and t_360 against the OFF baseline. The flag is OFF by default
so no existing gate is affected.

MEASURED VERDICT (2026-09, K sweep — heel EXCLUDED in this form):
  tightest protocol (44.5, row/hold, starboard full, V0 6.5; beta @60s):
  Kh/Kd | beta | heel | G1 (83-96) | F1 (104-121) | T (56-68)
  0 (OFF) | +2.85 | +1.41 | 92.2 | 121.4 | 62.0
  80k / * | +4.02 | +1.99 | 99.0 | 133.9 | 65.5  (F1 breaks)
  160k /* | +7.0 | +3.4 | 126.6 | 184.3 | 81.1  (all blown)
  320k /* | -15..-24 | -31..-36 | 64/44/40 | 67/45/41 | 43/39/37 (runaway)
  K_drag 0/4/8 moves nothing (4th digit) — the extra-drag path cannot
  move t_360 at these magnitudes (~38 N vs kN balances).
  Criterion (pre-registered): drift in [8, 15] with diameters held — NOT
  MET anywhere: +1.2 deg drift already costs F1 +12 m; +4 deg costs +52%.
  (Re-anchored 2026-09 per register C5: the method-backed target is 7.8°,
  15±2° scattered — exclusion stands a fortiori: the closest approach,
  7.0° at 160k, blows every diameter +30–50%.)
  Mechanism: any pure-sway heel push raises v, which raises f_hull, which
  raises the CLR restoring moment — diameters widen with the WRONG SIGN
  for a lateral-force fix. The missing term is a YAW MOMENT from heel
  (canted-hull force has an arm; this spike applies none) — needs
  heel-dependent hydrostatics (workbook Bonjean curves), not fitted K.
  Above ~200k the quasi-static balance runs away (heel-v feedback, no
  roll dynamics): valid only for heel <~ 4 deg. K_heel/K_drag stay swept
  placeholders; DO NOT promote on fitted gains.

  Documented heel-turn couplings (Rankov ch.4, primary): turns roll to the
  OUTSIDE; heel develops fully within ~one stroke of helm application
  (quasi-static treatment OK); below ~100 m diameter the inside blades
  lift out (immersion asymmetry, thrust-side — distinct from the excluded
  lateral-force path above; unmodeled, gate-safe to omit only while
  G1/F1 hold their bands). Roll to fractions of a degree was never
  instrumented (one-off wale readings only) — no dynamic heel data exists.
  Naive immersion coupling KILLED 2026-09 (do not build): 1-2 deg heel at
  4.5 m blade reach shifts immersion +-30-50 pct (vs the measured ~10 pct
  per deg from the K sweep) — rowers compensate ~3/4 by skill, and the
  compensation gain is unmeasured (fitting it to diameters = ship-fit).
  Geometry cross-check: inside blades lift at ~0.28/4.5 = 3.6 deg
  (thranite first, longest reach) ~= the stated 3-deg oar-rig limit.
  Needs instrumented heel + blade-depth data, not lines. Roll balance
  VALIDATED open-loop 2026-09 (K terms zeroed): g1/f1/tightest heel
  1.6/1.3/1.2 deg matches trials ~1-2 deg with outside-roll signs -
  independent check on grounded GM/arms. K=0 is bit-identical to
  heel-off (telemetry-only); the flag's behavioral content is all
  in the excluded/killed couplings.
"""

from __future__ import annotations

import math

# Defaults — swept to find what moves the gaps without breaking D gates.
# These are NOT tuned; they are starting points for the sweep in
# investigation/01 and 02.
DEFAULT_K_HEEL: float = 80000.0  # N per sin(heel) — lateral force from heel
DEFAULT_K_DRAG: float = 4.0  # multiplier on D(V)×sin² — extra drag
DEFAULT_GM: float = 0.97  # m, Olympias GM (Table 31.1 row 15)
DEFAULT_GM_EFF_OFFSET: float = 0.20  # m, crew lean (Taylor §2.3)
DEFAULT_ARM_LAT: float = 1.46  # m, hull lateral arm (Table 31.1 row 13)
DEFAULT_ARM_RUD: float = 1.16  # m, rudder arm (Table 31.1 row 14)
G: float = 9.81  # m/s²


def heel_angle(
    f_rud: float,
    f_hull: float,
    m: float,
    gm: float = DEFAULT_GM,
    arm_lat: float = DEFAULT_ARM_LAT,
    arm_rud: float = DEFAULT_ARM_RUD,
    gm_offset: float = DEFAULT_GM_EFF_OFFSET,
) -> float:
    """Heel angle in radians from the roll balance (Taylor §2.3).

    tipping = f_rud × arm_rud + f_hull × arm_lat  (both lateral forces)
    restoring = m × g × (GM − 0.2)
    heel = atan(tipping / restoring)
    """
    gm_eff = gm - gm_offset
    if gm_eff <= 0:
        return 0.0
    tipping = f_rud * arm_rud + f_hull * arm_lat
    return math.atan(tipping / (m * G * gm_eff))


def heel_lateral_force(
    heel: float,
    k_heel: float = DEFAULT_K_HEEL,
) -> float:
    """Sideways force from the heeled hull (parameterised).

    The heeled waterplane is asymmetric; the tilted hull displaces water
    sideways. No first-principles value — K_heel is swept.
    """
    return k_heel * math.sin(heel)


def extra_drag(
    V: float,
    beta: float,
    heel: float,
    k_drag: float = DEFAULT_K_DRAG,
    base_drag: float = 0.0,
) -> float:
    """Extra hull drag from drift + heel.

    D_extra = D(V) × K_drag × (sin²(beta) + sin²(heel))

    At small angles both terms are tiny; at beta=8° the drift term alone
    is K_drag × 0.019 × D(V). With K_drag=4 and D(V)=500N at 3.5 kt,
    that is ~38 N — small but in the right direction. The value is
    swept; the point of the spike is to find what magnitude moves t_360
    from 95s toward 128s.
    """
    if base_drag <= 0:
        return 0.0
    return base_drag * k_drag * (math.sin(beta) ** 2 + math.sin(heel) ** 2)
