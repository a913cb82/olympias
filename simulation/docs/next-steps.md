# Next steps — the open work

Status 2026-08-29. Everything DONE lives in `completed-work.md` (the
verdict ledger). Context: the deep-dive in `comparison-with-ll.md`.

The standing rule: the gates are the posterior — nothing is promoted or
changed without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration; nothing is tuned silently (the oQ-18 discipline). Current
state: **the force-driven oar is the PROMOTED default (Stream A complete,
2026-08), the hull is FULLY GROUNDED in the real Lines Plan (Stream C
complete, 2026-08-29) and the research-chain rudder/blade/hull are now
grounded in geometry (Stream F complete, 2026-08-29)** — the stroke
emerges from the demand + inertia + blade force; the hull's lateral
plane, CLR, J, Omega, mass, inertia and yaw lever are all computed from
`basis_hull_offsets.tsv` (LWL 32.35 m, 21 stations); the blade's 0.078 m²
is now 0.113×0.69 (immersion×span), the rudder's 1.4 is straight+induced
at full helm (2×0.75 m², Hoerner η=0.045), the hull's drag is ITTC
friction from WSA 130.5 m² + wave k·V⁴ (k=5.3, Cp 0.691) within 5% of the
chain law. 9 fitted chain numbers → 6 fitted (3 hull/blade/rudder now
computed). The kinematic layer stays as the labelled reference
(force=False).

## The work streams

Streams A (force-driven oar), B (performance), C (hull grounding) and F
(physics grounding) are **complete** — see `completed-work.md §7`, `§8`,
`§9`/`§10–11` and `§12`.

Serial priority: **D → E**. The full acceptance + the HL re-calibration
re-run after every promoted change.

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
  F3 — F3's ITTC+wave already answers it: the low-speed 40.2V² IS the
  ITTC friction from WSA 130.5 (within 6% at 1-6 kt), the high-speed
  excess is the wave residual k·V⁴.
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

D1 (the transcription) and D3 (the sprint test) are independent starts
that can run in parallel. E1 (pentaconter) needs the remaining decode
(E2) first. The full acceptance + HL re-calibration after every change.

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
