# The trial-fitted constants audit

Every constant or variable that had to be **fitted from, or anchored to,
trials data** — what it stands in for, and what would eliminate it.
The porting question behind this list: a good low-level physics sim should
minimize the trial-anchored set, because a new hull (a monoreme, a bireme)
has no trials to fit against. The distinction that matters:

- **Fitted from trials** (§1) — the LL's values chosen so a trial number
  comes out. The porting blockers.
- **Inherited empirical laws** (§2) — literature/tank-test curves the LL
  uses; ship-specific ones are re-derivable from lines, physiology ones
  are universal.
- **Machine fits to the LL** (§3) — the HL's response curves. Fitted to
  the *oracle*, not to trials; they regenerate automatically
  (`hl/calibrate.py`) and are no porting concern.
- **Provisional placeholders** (§4) — flagged `[?]` values with no anchor
  at all; the honest gap list.

The acceptance record with the per-gate status of every fitted constant is
`docs/VALIDATION.md` §11.1; this document is the *elimination* view.

## 1. The LL constants fitted from trials data `[x]`

| # | Constant | What it does | Fitted to (the trial anchor) | Stands in for (the physics gap) | What would eliminate it | Generalizes from the full design? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `t_drive(44.5)` | how long each stroke's pull lasts at sprint rate | the ch.9 four-run sprint: 8.2–8.3 kt at 44.5 spm, ~130 effective oars (register A8; the Table 9.6 schedule has no 44.5 entry — extrapolation gave 0.347 s and a 7.9–8.8 kt bracket) | the stroke's effective-pull time at sprint rate — the oar's prescribed kinematics need a timing schedule | (a) the trial's stroke timing (the F/G print report — the standing blocked source), or (b) a **force-driven oar**: Gate 5 already proves drive time ≡ forces + inertia (0.43 s reproduced exactly), so a rower force model makes the whole timing schedule emergent | no — crew timing: emerges via the force-driven oar (plan 1) or stays a carried measurement |
| 2 | `T_DRIVE` Table 9.6 | the measured pull-duration schedule at the cruise rates | measured, not fitted — the trial stroke-timing record at the two cruise points | same gap as #1, at the measured points | same as #1 | no — same as #1 |
| 3 | `W_MAX` | each rower's anaerobic battery — how long a burst lasts before fatigue | the ch.9 four-run burst: ~45 s at 44.5 spm (excess ≈ 116.6 W/man × 45 s ≈ 5.2 kJ); the ¾-NM run implies up to ~9.5 kJ — the D6 CP tension | the rower's anaerobic capacity (W′) | a direct VO2/W′ physiology study (Phase 4) — **universal, not ship-specific** | yes (1) — universal physiology, carries as-is |
| 4 | `HOLD_FRAC` | how hard held oars brake the ship (fraction of a normal stroke's force) | the tightest turn: D = 62 m AND t_360 = 128 s (Morrison 1988; re-measured 0.05 → 0.08 after the sway DOF changed the turn physics) | the held blades' water grip, as a per-oar drag fraction of the free-oar force — an aggregate of grip force × blade hydro × flow | the F/G print report's hold spectrum, or a grip-force biomechanics model; the brake's yaw arm is already physical (`LEVER_HOLD` 1.5 m) | half (2+3) — the held blade's drag is computable (flat-plate law); the grip strength is crew behavior, carries as a human constant |
| 5 | the sway pair: `Omega` (computed), `clr_offset`, `lever` | the hull's turning resistance, the pivot (CLR) position, and the oars' turning arm | the W5 turn family: G1 89.4 m, F1 111.9 m, tightest 62 m, t_360 128 s (the `calibrate_sway.py` grid — one set fitting all four) | the hull's rotational resistance (the lumped Ω·ω² that cannot represent the CLR restoring moment), the CLR position, and the net oar-race lever | Ω: **DONE** (Plan 2, `research/lane-5-manoeuvre/crossflow.py`) — Ω = ½ρ·C_D·J with the drag-crisis C_D = 0.3 (literature, Re ~ 1e6) and J = ∫d·|x − x_cg|³dx over the parametric hull + the ram; the audit's closure: the fitted 3.2e6 equals the computation at 1.6 %, the turn gates hold unchanged (no regression), the C1 units caveat resolves. clr: the computed centroid is AFT of the c.g. (−0.2…−1.4 m vs the fitted +0.8 forward) — the parametric ends + the ram don't reproduce it; the real lines are the named path. lever: the A1 decomposition (4.8 = blade arm, 1.8 = net after the ~400 kN·m·s local-flow damping) | Ω **yes (2)** — computed; clr no — the hull-form ends (Wolfson Plan 7 / the Eliav CAD); lever yes (2) |
| 6 | `RUDDER_FAC` | the extra drag a turned rudder adds | the W5 turn set (applied-rudder along-track drag factor) | the rudder's added drag at an applied angle | the rudder plan + foil/tank data (the A3 aerofoil item: "the foil would replace the fitted coeff(φ) curve") | yes (2) — foil theory from the rudder plan |
| 7 | the rudder curve: coeff(φ), `rudder_straight` | how much of the rudder's drag turns into sideways force at each angle | ch.31 fitted to Olympias trials (independent confirmation exists: register C3's 137v² + 0.65v, +8–9 %) | the rudder's lateral-force-to-drag ratio vs angle | same as #6 | yes (2) — same as #6 |
| 8 | `m_app` | the water the hull drags along (added mass), as a fraction of ship mass | trial-measured (Taylor ch.31 §2.1) | the added mass the hull drags along | potential-flow added-mass computation from the lines — standard naval architecture, fully computable (the easiest elimination on this list) | yes (2) — potential flow from the lines |
| 9 | the hull law | the power the hull needs at each speed — the resistance curve | tank-tested (Grekoussis & Loukakis) + trial-validated (ch.7/ch.9) | the hull's resistance as a fitted curve | a resistance computation from the lines (series method/CFD) — the first thing a port must re-derive anyway | yes (2) — resistance series/CFD from the lines |
| 10 | the blade product C_N·A | the blade's push per unit water speed (force coefficient × area) | the ch.7/ch.9 power chain (the flat-plate shortfall absorbed in the calibrated product — the A5 family; Rev F B2: the real polar's normal coefficient is 1.37× the flat plate's) | 3D blade hydrodynamics/slip | the blade's measured polar (the F/G report's Figure 10 decode — blocked) or the B2 polar layer's full vector form | yes (2) — polar law from the blade geometry |
| 11 | `P = 7.43·r`, `E` | each rower's power at a given stroke rate, and the share that reaches the blade | ¾-NM calibration: 288 N @ 38.75 spm; ch.7 | the rower's power-vs-rate law and efficiency | physiology — **universal, ports unchanged** | yes (1) — universal physiology, carries as-is |
| 12 | `thal_main_power_factor` | the top bank's reduced power at high stroke rates | the ch.9 L-model: "the thalmian tier's power contribution fell sharply at higher speeds" `[?]` — the exact rate-shape unmeasured | the top bank's shortfall at high rates (short oars, crowded stations) | per-tier physics: the short-oar kinematics + the same rower physiology should produce the head-room | half (2+3) — the short-oar kinematics computable from the tier geometry; the physiological head-room is crew behavior |
| 13 | `LEVER_OAR` | the oars' turning moment arm for one-side pulls | fitted to the one-side-stops trial turns (W5, ≤ 7 %; Taylor Table 31.1 row 10) | the oar-race yaw lever for asymmetric forces (kept for the steady research model; the LL uses the sway trio's lever) | the per-station geometry (Coates Plan 8 — absent from our sources, register B6) + the A1 decomposition | yes (2) — station geometry |

The "Generalizes from the full design?" column's groups: **(1)** universal physiology — carries as-is, never re-fitted; **(2)** computable from the design via standard hydrodynamics/geometry; **(3)** crew behavior — not derivable from any design; carry as a human constant or make emergent (the force-driven oar); **(4)** ship hydrodynamics absent from the design document — needs a computation program (the cross-flow model/CFD).

The pattern: every row is a *prescribed-kinematics patch*. The LL gives
the oar a kinematic stroke (timing + sweep) and fits what the missing
dynamics would have produced: the timing (#1–#2), the grip (#4), the tier
effort (#12), the turn closure (#5–#7), the blade product (#10). Push the
physics one level deeper and the row disappears:

- **A rower force model** (forces instead of kinematics) eliminates #1,
  #2, #4, #12 and makes #3's W′ the only physiology input — Gate 5's
  force-driven companion (drive time 0.43 s ≡ forces + inertia) is the
  proof it works.
- **Hydrodynamics computed from the lines** (potential flow for #8,
  resistance series for #9, manoeuvring coefficients for #5, foil theory
  for #6–#7) eliminates the whole hull column — the standard naval-
  architecture route, and the port's real work.
- #10 is data-blocked (Figure 10 decode), not physics-blocked; #3 and
  #11 are universal physiology and should never be re-fitted per ship.

## 2. Inherited empirical laws (not sea-trial fits)

| Constant | What it does | Origin | Porting status |
| --- | --- | --- | --- |
| `P_CRIT` | the sustainable per-rower power output | Rossiter & Whipp (Rankov ch.23) | universal — ports unchanged |
| `TAU` | the W′ refill time constant | Monod/MacFarlane/Nadel family | universal |
| `Fh_BURST` | the max mean handle force in a sprint burst | the chain's sprint pull at 44.5 spm (derived) | derived — recomputes |
| `m_app`'s lateral/yaw siblings (`add_v`, `add_r`, `add_c`) | the lateral/yaw added-mass fractions (OFF by default) | Rev F B1, semi-empirical `[?]` | geometry-estimable from the lines |

## 3. The HL's machine fits (to the LL, not to trials)

`tau_surge`/`tau_turn`/`tau_exit`, `drift_tau_exp`, the turn-drag curve
(24 cells), the yaw-build + d-scales, the asym nets + net_fresh, the
d_oar_v fractional polynomial + v_flow + v_collapse, the drift cells,
the τ_hold rate table, SETTLED_D_RATIO. All are curve fits to LL
protocols, chosen by the curve-selection machinery (`hl/curvesel.py`)
with the acceptance gates as arbiter. For a port they are **free**: a new
LL automatically produces a new calibration (`hl/calibrate.py`, ~10 min)
and re-locked gates. They are fitting, but never trial-fitting — the LL
is their oracle.

## 4. Provisional placeholders `[?]` (no anchor)

| Constant | What it does | Status |
| --- | --- | --- |
| `t_rise` | the catch's force-rise time | provisional (register D10) — instrumented force traces would pin it |
| `Fh_MAX` | the peak handle-force ceiling (a demo-only clamp) | provisional, model-implied (oQ-13 clamp, demos only) |
| `YAW_LIN_DAMP` | the linear yaw-damping coefficient (the tested t_360 hypothesis) | OFF — tested and FAILED (breaks every diameter); the negative result recorded in `ll/ship.py` |

## 5. The honest bottom line

Nothing on this list is *irreducibly* trial-dependent in principle — the
physical ingredients (hull hydrodynamics, blade polars, oar kinematics,
human physiology) are all computable or measurable. What the trials
provide is **verification, not parameterization**. That is the direction
the "good physics-based sim" should push: fewer fitted constants, more
computed physics, trials as the gate. Until then, the porting reality:
a new hull with line plans only can be built from §2 + §3 + computed
versions of §1's hull rows (#5–#9), with the rig rows (#1, #2, #12)
from the ship's rig evidence and the human rows (#3, #4, #11) carried
as-is — and its Level-1 status honestly `[?]` where the anchors cannot
exist.
