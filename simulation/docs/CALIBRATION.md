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

## 0. The tuning rule (portability acceptance)

The audit's acceptance criterion: a tuned value is acceptable iff it
corresponds to something the ship's plans would determine — "you can't
read the plan" is the only licence to tune. A tuned value that could not
theoretically be derived trivially from a plan is NOT acceptable and must
be eliminated. Four classes:

- **A — plan-trivial**: the value is geometry/area/hydrodynamics the plans
  determine directly (a dimension, an area, a centroid, a foil, an added
  mass, a resistance). Tuning is a legitimate placeholder for the unread
  drawing (the Coates plans sit in the Wolfson College archive); when the
  plans are readable, the value is computed, not tuned.
- **B — universal human**: physiology/behaviour, in no plan and needed by
  none — the same for every crew on every ship. Carried as-is, never
  re-tuned per ship; the rule governs ship-specific tuning only.
- **C — human-mixed**: the ship part is plan-derivable only through the
  universal human law (the stroke timing via forces + inertia — Gate 5's
  identity). Acceptable while the human law is universal; the timing row
  is the elimination target (Plan 1's force-driven oar).
- **D — violators**: ship-specific AND not plan-derivable — the audit's
  job is to find and eliminate these. The sole violator found: the fitted
  Ω (no drawing determines a lumped yaw-damper constant — its mysterious
  units were the symptom) — eliminated by Plan 2 (computed from the hull
  form at the drag-crisis C_D, crossflow.py).

Current status: no remaining tuned value violates the rule. For a new ship
whose plans ARE held, class A is computed from day one — the tuning burden
is an Olympias-specific accident (the archive drawings).

## 1. The LL constants fitted from trials data `[x]`

| # | Constant | What it does | Fitted to (the trial anchor) | Stands in for (the physics gap) | What would eliminate it | Generalizes from the full design? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `t_drive(44.5)` | how long each stroke's pull lasts at sprint rate | the ch.9 four-run sprint: 8.2–8.3 kt at 44.5 spm, ~130 effective oars (register A8; the Table 9.6 schedule has no 44.5 entry — extrapolation gave 0.347 s and a 7.9–8.8 kt bracket) | the stroke's effective-pull time at sprint rate — the oar's prescribed kinematics need a timing schedule | (a) the trial's stroke timing (the F/G print report — the standing blocked source), or (b) a **force-driven oar**: Gate 5 already proves drive time ≡ forces + inertia (0.43 s reproduced exactly), so a rower force model makes the whole timing schedule emergent — **DONE (P1.6, 2026-08 — Stream A)**: the force mode is the promoted default; the emerging drive times 1.005/0.972/0.925/0.932 × Table 9.6 at the four points; the schedule is now a validation anchor, not an input. **Causal lock (`ll/tests/test_force_timing_inert.py`): scaling every `t_drive_for` value 1.5× leaves force-mode cruise/sprint/turn trajectories byte-identical — the fitted schedule is causally dead in the promoted default** | no — crew timing: emerges via the force-driven oar (plan 1) or stays a carried measurement |
| 2 | `T_DRIVE` Table 9.6 | the measured pull-duration schedule at the cruise rates | measured, not fitted — the trial stroke-timing record at the two cruise points | same gap as #1, at the measured points | same as #1 — **DONE** (the force mode's emerging times match to the companion gate; the schedule is the anchor) | no — same as #1 |
| 3 | `W_MAX` | each rower's anaerobic battery — how long a burst lasts before fatigue | the ch.9 four-run burst: ~45 s at 44.5 spm (the force mode's excess — the chain's 116.6 W/man plus the flip's 16.8 — ≈ 133.4 W/man × 45 s ≈ 6.0 kJ); the ¾-NM run implies up to ~9.5 kJ — the D6 CP tension | the rower's anaerobic capacity (W′) | a direct VO2/W′ physiology study (Phase 4) — **universal, not ship-specific** | yes (1) — universal physiology, carries as-is |
| 4 | `HOLD_FRAC` | how hard held oars brake the ship (fraction of a normal stroke's force) | the tightest turn: D = 62 m AND t_360 = 128 s (Morrison 1988; re-measured 0.05 → 0.08 after the sway DOF changed the turn physics) | the held blades' water grip, as a per-oar drag fraction of the free-oar force — an aggregate of grip force × blade hydro × flow | the F/G print report's hold spectrum, or a grip-force biomechanics model; the brake's yaw arm is the grounded thole mean (`LEVER_HOLD` 2.00 m, Stream C B2) | half (2+3) — the held blade's drag is computable (flat-plate law); the grip strength is crew behavior, carries as a human constant |
| 5 | the sway set: `Omega`, `clr_offset`, `lever` (all grounded, Stream C) | the hull's turning resistance, the pivot (CLR) position, and the oars' turning arm | the W5 turn family: G1 89.4 m, F1 111.9 m, tightest 62 m, t_360 128 s (the `calibrate_sway.py` grid — one set fitting all four; the fitted values are the documented references) | the hull's rotational resistance, the CLR position, and the net oar-race lever | Ω: Plan 2 + taper grounding — Ω = ½ρ·C_D·J with C_D = 0.30 (drag-crisis literature) × taper A_lat/(LWL·T) = 0.846 from `basis_hull_offsets.tsv` (J = 23217 m⁵ at trial WL) → 3.02e6, from lines + literature, no turn fit. clr: **grounded** — Simpson centroid 16.60 m from AP minus LCB 15.67 m = +0.93 m forward (was fitted +0.8). lever: **grounded** — thole mean (31·2.7+27·2.0+27·1.2)/85 = 2.00 m (thranite from rail beam; zygian lines-consistent with shell 2.25 at port height; thalmian documented inboard design; exact plan pending Figure 16). The fitted NET 1.8 m (0.2 m damping correction) is the documented reference | **yes (2)** — all three computed from the lines; the Figure 16 decode refines (not replaces) the arms |
| 6 | `RUDDER_FAC` | the extra drag a turned rudder adds | the W5 turn set (applied-rudder along-track drag factor) | the rudder's added drag at an applied angle | **induced part grounded (Stream F + eta-product fix)**: FAC = 1 + ½ρ·A·CD(67.5°)·KT²·η/straight with η = 0.5·0.6·0.5·0.3 = 0.045 (wake×AR×single×vent, named physics) → 1.397, reproducing the measured 1.40 within 0.3% (corroboration, not a fit). The straight part (39.4 N/kt²) is an independent ship measurement (bare-vs-fitted difference, like a tank result); the full foil (coeff(φ) from rudder plans, A3) stays blocked on the rudder drawings | induced yes (2) — foil product; straight measured (ship evidence); full foil yes (2) when plans surface |
| 7 | the rudder curve: coeff(φ), `rudder_straight` | how much of the rudder's drag turns into sideways force at each angle | ch.31 fitted to Olympias trials (independent confirmation exists: register C3's 137v² + 0.65v, +8–9 %) | the rudder's lateral-force-to-drag ratio vs angle | same as #6 | yes (2) — same as #6 |
| 8 | `m_app` | the water the hull drags along (added mass), as a fraction of ship mass | trial-measured (Taylor ch.31 §2.1) — an independent acceleration measurement, not adjusted to fit any speed/turn scenario | the added mass the hull drags along | measured 1.10 ± ~0.05 (Lamb spheroid lower bound at fineness 8.73 is 1.026; full ends + appendages entrain more). Elimination path unchanged: potential-flow added-mass computation from the actual lines — standard naval architecture (the easiest elimination on this list) | measured (ship evidence, carries); computed yes (2) via potential flow |
| 9 | the hull law | the power the hull needs at each speed — the resistance curve | tank-tested on the 1:10 lines-plan model (Grekoussis & Loukakis) + trial-validated (ch.7/ch.9) — a measurement of the lines, like the offsets, not a sea-trial fit | the hull's resistance curve | computed cross-check in hand: ITTC-1957 friction (WSA 130.5) + k·V⁴ wave (k = 5.3) within ~1% of the tank law at cruise (Stream F). **Switch attempted and reverted (goal work)**: sailing the computed law is gate-free on every LL-vs-trial gate (cruise ±0.06%, G1/F1 +0/+0.01 m, burst −0.002 kt; trial-WSA ~122 variant puts F1 on the band edge) but destabilises the HL drift channel — drift cells ±10%, recal tau_exit 8→19 s, exponent 0.279→0.105, zigzag bin_rms 3.57 > 3.0, wprime bin_max 6.17 > 5.5. **Blocked on the drift open item (1.4° vs 8–15°)**, not on LL gates | tank law: measured (lines evidence, carries); computed ready (2), promotion awaits drift fix |
| 10 | the blade product C_N·A | the blade's push per unit water speed (force coefficient × area) | the ch.7/ch.9 power chain (the flat-plate shortfall absorbed in the calibrated product — the A5 family; Rev F B2: the real polar's normal coefficient is 1.37× the flat plate's) | 3D blade hydrodynamics/slip | **area grounded (Stream F + Hoerner fix)**: 0.113 × (1−0.08/0.55) × Hoerner(AR 2.68) = 0.0784, from oar geometry + seaway + Hoerner, reproducing the fitted 0.078 within 0.5% (corroboration). Open: the full vector polar form (B2 layer, OFF) and the Figure 10 decode — the remaining blade gap is the polar shape, not the area | area yes (2) — computed; polar shape yes (2) when Figure 10 decodes |
| 11 | `P = 7.43·r`, `E` | each rower's power at a given stroke rate, and the share that reaches the blade | ¾-NM calibration: 288 N @ 38.75 spm; ch.7 | the rower's power-vs-rate law and efficiency | physiology — **universal, ports unchanged** | yes (1) — universal physiology, carries as-is |
| 12 | `thal_main_power_factor` | the top bank's reduced power at high stroke rates | the ch.9 L-model: "the thalmian tier's power contribution fell sharply at higher speeds" `[?]` — the exact rate-shape unmeasured (the C3 measurement, 2026-08: the no-head-room sprint equilibrium 9.2 kt vs the workbook's 9.95 — the head-room explains part of the sprint deficit; the residual is the blade-law/demand family, the B2 polar) | the top bank's shortfall at high rates (short oars, crowded stations) | per-tier physics: the short-oar kinematics + the same rower physiology should produce the head-room | half (2+3) — the short-oar kinematics computable from the tier geometry; the physiological head-room is crew behavior |
| 13 | `LEVER_OAR` | the oars' turning moment arm for one-side pulls | fitted to the one-side-stops trial turns (W5, ≤ 7 %; Taylor Table 31.1 row 10) | the oar-race yaw lever for asymmetric forces — RETAINED REFERENCE, not on the LL runtime path (the LL uses the grounded thole mean 2.00 m, audit #5, and per-station blade sums) | resolved as decomposition (register C3): 4.8 = the blade-position arm (per-station mean 4.82 m); NET 1.8 = sway-calibrated; thole mean 2.00 + 0.2 m damping correction. The Figure 16 thole-plan decode refines the arms | reference (research steady model); live LL lever yes (2) |

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
| `t_rise` | the catch's force-reversal time | COMPUTED from oar physics: T_RISE_BASE = MIT·(ω_drive+ω_recover)/(F_flip·lin) at the design point (Table 3.1 MIT, sweep, FH_BURST demand), pressure-scaled (rowers flip at rowing effort: sprint 0.076 s, steady 0.109 s). Instrumented force traces would validate the flip profile, not pin the value |
| `Fh_MAX` | the peak handle-force ceiling (a demo-only clamp) | provisional, model-implied (oQ-13 clamp, demos only) |
| `YAW_LIN_DAMP` | the linear yaw-damping coefficient (the tested t_360 hypothesis) | REMOVED — tested and FAILED (breaks every diameter); the negative result: VALIDATION §7.2 + this table |

## 5. The honest bottom line

Nothing on this list is *irreducibly* trial-dependent in principle — the
physical ingredients (hull hydrodynamics, blade polars, oar kinematics,
human physiology) are all computable or measurable. What the trials
provide is **verification, not parameterization**. That is the direction
the "good physics-based sim" should push: fewer fitted constants, more
computed physics, trials as the gate. Until then, the porting reality:
a new hull with line plans only can be built from §2 + §3 + computed
versions of §1's hull rows (#5's Ω done — Plan 2; #6–#9 pending), with
the rig rows (#1, #2, #12) from the ship's rig evidence and the human rows
(#3, #4, #11) carried as-is — and its Level-1 status honestly `[?]` where
the anchors cannot exist. The acceptance rule is §0: tuned values are
placeholders for unread plans (class A) or carried humans (class B) —
never ship-specific empiricism (class D).
