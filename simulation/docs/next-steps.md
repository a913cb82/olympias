# Next steps — the open work

Status 2026-08-29. Everything DONE lives in `completed-work.md` (the
verdict ledger). Context: the deep-dive in `comparison-with-ll.md`.

The standing rule: the gates are the posterior — nothing is promoted or
changed without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration; nothing is tuned silently (the oQ-18 discipline). Current
state: **the force-driven oar is the PROMOTED default (Stream A complete,
2026-08) and the hull is FULLY GROUNDED in the real Lines Plan (Stream C
complete, 2026-08-29)** — the stroke emerges from the demand + inertia +
blade force; the hull's lateral plane, CLR, J, Omega, mass, inertia and
yaw lever are all computed from `basis_hull_offsets.tsv` (LWL 32.35 m,
21 stations). 6 fitted hull params → 0 fitted. The kinematic layer stays
as the labelled reference (force=False).

## The work streams

Streams A (force-driven oar), B (performance) and C (hull grounding) are
**complete** — see `completed-work.md §7`, `§8`, `§9` and `§10–11`.

Serial priority: **F → D → E**. F replaces three fitted research-chain
numbers with physics computed from the ship's plans. D and E are
independent. The full acceptance + the HL re-calibration re-run after
every promoted change.

### Stream F — the physics grounding (replace fitted chain numbers with plans-based physics)

Three constants in the LL's chain are still fitted to trials data rather
than computed from the ship's plans. Each is physically calculable from
geometry we now hold. The goal: replace the fitted values with
computations and validate against the trials. Each item is independent
and can be done in any order; F1 is smallest, F2 is the most diagnostic,
F3 is the largest.

- **F1. Rudder drag — replace the fitted constant with geometry.**
  The LL's rudder drag currently uses a fixed multiplier
  `RUDDER_FAC = 1.4` on the straight-rudder drag (39.4/kt²) at all
  helm angles. Taylor's text says the factor varies 0.6 (22.5°) to 3.25
  (67.5°); our single constant was tuned to the W5 turns. The rudder
  geometry is known: **2 rudders, 0.75 m² each (1.5×0.5 m), 15 m aft
  of CG** (workbook Manoeuvring sheet). The VBA already uses Hoerner
  flat-plate: `CL = sin(2α), CD = 2sin²(α)` plus a parasitic drag
  `0.5·(137V² + 0.65V) · area/1.5` (the "half total ship drag" figure,
  DECODE §VBA). **Plan:** compute the angle-dependent drag from rudder
  area, Hoerner CD, and the parasitic term; replace `RUDDER_FAC` with a
  function of helm angle; re-run G1/F1/tightest.
  **Acceptance:** G1, F1 and tightest diameters stay within the
  existing gates (±7%/8%/10%) using ONLY the measured rudder geometry —
  no new constants tuned to the turns.

- **F2. Blade effective area — diagnose the 31% gap.**
  The real blade is **0.113 m²** (Rev F Table 3, DECODE A5); the LL uses
  an "effective" area **0.078 m²** — 31% smaller. This absorbs slip,
  partial immersion, and lift/drag effects into one number. The Rev F
  report already has the blade polars (`CL = sin(2α), CD = 2sin²(α)`,
  the macon blade — DECODE B2): at the trireme's 54–58° angles of
  attack, `CL ≈ 0.90–0.95` and the lift is ~55% of total force. Using
  the true 0.113 m² with the polar gives +40% mean thrust (locked in
  `test_polar_variant_thrust`). **Plan:** compute the effective immersed
  area from the oar geometry (sweep 48°, rake, the blade's submersion
  at each station from the hull offsets at trial WL 1.10 m); the
  projection of the blade area onto the plane perpendicular to the flow
  gives the geometric effective area. Compare with 0.078 m². If the
  geometric projection matches, the gap is pure geometry. If not, the
  residual diagnoses the slip/ventilation model.
  **Acceptance:** the true blade area (0.113 m²) enters the blade law
  with an explicit, computable correction derived from oar geometry and
  hull offsets (not fitted to trials), and the one-oar thrust at the 4
  Table 9.6 points stays within ±15% (the existing Gate 1 band).

- **F3. Hull resistance — compute from the lines plan.**
  The LL uses `hull_power = 155V³ + 4.13V⁵` (the chain law, calibrated
  to the ¾-NM towing trials). The trials piecewise
  (`40.2/75.2/88.6·V²` N at V in kt, "cf ref 1 p82") runs 12–15%
  below the chain law at 8–10 kt — same data, two fits (D2).
  The workbook already has a **full Holtrop-Mennen implementation**
  (VBA `Holtrop`/`HoltropV`) and the ITTC-1957 friction line. We hold
  the lines plan (`basis_hull_offsets.tsv`, 21 stations) and the
  workbook hydrostatics: `LWL 32.35 m, BWL 3.704 m, WSA 130.5 m²,
  Cb 0.321, Cp 0.691, Cm 0.465, Cw 0.768, Vol 44.26 m³`. **Plan:**
  implement Holtrop-Mennen (or ITTC-1957 friction + form factor) from
  the lines plan in Python; compute R(T) at the trial speeds; compare
  with the trials piecewise AND the chain law.
  **Acceptance:** the computed resistance at the trial speeds matches at
  least one of the two existing fits (chain law OR trials piecewise)
  within 10%, and the reason for any remaining discrepancy is
  documented and named.

**Stream F done when:** all three items pass their individual criteria,
the full test suite is green, and the HL is re-calibrated on the
updated chain.

### Stream D — the second opinions (independent measurements of the same ship)

- **D1. The independent-model cross-check.** Transcribe the decoded
  VBA (ManAcceleration / OarForces / RudderForces — the Clarke–Gedling–
  Hine derivatives, the CN yaw damper, the Hoerner rudder + the 137V²+
  0.65V parasitic drag, the 81 N linear law) into a Python script; run the
  G1/F1/tightest scenarios + the top-speed curve; compare trajectories,
  diameters and the speed decay through the turns against the LL. A second
  trial-tuned model of the same ship is the strongest available cross-check
  of the turn physics.
- **D2. The resistance-fit reconciliation.** The trials piecewise
  (40.2/75.2/88.6·V²) runs 12–15 % below the chain law at 8–10 kt — same
  trials data, two fits. Document the cause (loading condition, rudder
  contribution, the fit families). Analysis only — the chain law is
  trial-speed-validated and stays unless a gate says otherwise. Overlaps
  F3 — if F3 computes resistance from the lines plan, D2's question is
  answered as a by-product.
- **D3. The no-head-room sprint test — T1's decisive cheap
  measurement.** The workbook's 9.95 kt is all-170 at the trials thrust law
  with NO thalmian shortfall; our LL's sprint (force promoted: 7.65 kt
  @ 44.5 spm, 0.6 head-room; no-head-room 9.16 kt) uses the fitted
  head-room 0.6 at 44.5 spm. Run the LL with the thalmian factor 1.0:
  if the equilibrium approaches ~9.9, the whole sprint deficit is the
  head-room shape, not the blade law; if it stays ~8, the blade-law
  family is the suspect. Either way the T1 ledger gets a verdict.

### Stream E — the portability program (the tuning rule's test)

A larger scope; the kick-off is a decision.

- **E1. The pentaconter milestone.** The workbook's pentaconter
  designs (monoreme: 25/side, LOA 31 m, 21 t, GMT 0.643 m; bireme: LWL
  17.2 m, B 2.8, T 0.759, 14.4 t — with the Transform sheet's offsets and
  the author's powering/turn predictions) are a NEW ship whose "plans" ARE
  held: run the class-A machinery from its offsets and compare with the
  workbook's numbers — the tuning rule's "for a new ship whose plans ARE
  held, class A computes from day one" made testable. Scope decision: a
  research-side portability study vs a full LL scenario.
- **E2. The remaining decode.** The paper's figures (Figures 2/3/5,
  Tables 1/2 — image reading) and the workbook's 15 charts' plotted series
  — feeds E1's inputs and D1's fidelity.

### Open physics items (not tuned, not fitted — measured gaps)

These are not parameters to fit; they are open questions about the
physics that remain unresolved.

- **The 360° turn time (98 s vs 128 s, −23 %).** The turn *size*
  matches (60 m ✓); the *speed* doesn't. Every suspect was measured and
  excluded. Named cause: the turn-speed floor — the model's ~3.2 kt vs
  the trial's ~2.9 kt.
- **The zig-zag overshoots (11–13° vs 8/7°).** The model's heading
  carries ~5–6° too far past the ±20° targets. Same yaw-reversal family
  as the t_360.
- **The drift angle (1.4° vs 8–15°).** The model doesn't lean sideways
  enough. No A_lat/CLR adjustment holds the turns AND the wprime closure.
- **The ch.7 cruise triple (−2.5/−4.6/−6.1 %).** The model's rowers
  deliver less power per stroke at high rates. The blade/kinematics chain
  is the named suspect.
- **The per-station inverted pattern (g1 134 vs 91, f1 264 vs 120).**
  The per-station layer's turn pattern is inverted vs trials. The
  over-damping (~9.8 kN·m) is the measured gap. The layer stays swappable
  (`Ship(stations=True)`), not default.

## Kick-off

F1 (rudder geometry), F2 (blade area) and F3 (hull resistance) are
independent starts. D1 (the transcription) and D3 (the sprint test) are
also independent. E1 (pentaconter) needs the remaining decode (E2) first.
The full acceptance + HL re-calibration after every change. F3 overlaps
D2 — if F3 computes resistance from the lines plan, D2 is answered as a
by-product.

## Risks

The force-mode profile shape (Figure 10 block — the constant demand is
the documented minimum-shape start; a catch-concentrated profile would
change the emerging drive times); the catch flip at low ship speed (the
start-from-rest); the numerical stiffness at catch; the kinematic
recovery `[?]` (the force recovery is unanchored); the sprint's residual
(the midship's straight-rudder drag — the trials' "partly raised" state —
D2's input); the HL's fatigue residual (the calibrated nets run ~8 %
under the force LL's actual drain through the turns — the annotated
gates); C_D's ±30 % band vs the gate widths; the LL's Ω folds in
the CLR restoring moment — the B1 swap must not double-count it.
