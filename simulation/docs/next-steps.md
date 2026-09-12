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
- **D3. The no-head-room sprint test — configuration entangled (2026-09).**
  The trials sprinted with rudders partly raised; the LL sailed full-down.
  Rudder-fraction sweep (scenario input, production Ship untouched): frac
  1.0 → V30 7.68 (rudders-down prediction), 0.5 → 8.21 (inside trials
  8.2-8.3 — bundles configuration with crew/law differences (LL rows
  148-effective vs Shaw's 130; (0.5, 148) and (~0.25, 130) both land on
  8.2, and the report's minimum-drag-near-quarter favours the latter
  pairing — corrected 2026-09, primary source ch.9). What stands: no
  unexplained residual inside EITHER consistent accounting; the chain law
  itself is the partly-raised curve (Shaw graph reading) while its P
  calibration was rudders-down (mixed conditions, validates within 1%). The thalmian head-room stays load-bearing
  on the crew side (8.21 needs it at frac 0.5); the workbook 9.95 ideal
  (170 full, rudders up) vs LL-up 8.85 keeps the T1 effective-rower
  question open. Locked: `test_sprint_partly_raised_config`.

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
  matches (60 m ✓); the *speed* doesn't. Floor arithmetic: fixed D +
  longer time ⟺ lower V AND lower yaw rate together (62 m / 128 s ⟺
  2.9 kt and 2.81°/s — the yaw balance closes consistently there, so the
  whole gap is the surge floor: 3.5 vs 2.9 kt, i.e. ~40% excess turn
  thrust/drag-equivalent). Measured exclusions (2026-09, no LL change):
  turn-rate protocol −30% rate → +7% time only (stiff floor); uniform drag
  ×2.5 shrinks D 62→42 m (wrong direction); hull-only drag ×3 buys +7%
  time (needs absurd ×8–10); stations oar-surge is −33% (wrong sign);
  drift/heel/K_drag drags all negligible or wrong-signed. W'-empty planner
  gives ~31 N/oar rate-invariantly — still ~2× the ~13 N/oar the 2.9 kt
  floor implies. Prime suspect reframed: the rate→spoude-pressure link —
  a 128 s turn cannot average above sustainable output (45 s W' battery),
  so turn pressure must sit near steady, not spoude; LL rows turns at
  sprint pressure by protocol. Needs per-turn effort data (Trials 1988
  F/G tables, item 3.5) or a universal sustained-turn easing rule. W'
  accounting audited and CLOSED (2026-09): absorbed cancels both sides
  (drain exactly p_ext+flip > 80 W); the (P_crit, W') pair is uniquely
  pinned by cruise-sustainable + 45 s-sprint anchors. Turn-pressure
  protocol excluded too: spoude-with-fade ≈ steady-sustained in total
  impulse (W' conservation — t360 95→98 s only). Rudder-angular drag
  (Taylor §5.1 0.6–3.25, lift decoupled): floors −8–18% with D held —
  viable SHAPE but MarkIIb-sized (needs Olympias foil, A3). Live lead:
  demand-law shape (P=7.43r assumed linear vs Table 3.2 couples falling
  215→172 N·m over 30–38 spm at fixed speed — different protocols,
  needs careful reading).
- **The zig-zag overshoots (11–13° vs 8/7°).** The model's heading
  carries ~5–6° too far past the ±20° targets. Same yaw-reversal family
  as the t_360.
- **The drift angle (1.4–2.9° vs 7.8°).** The model doesn't lean
  sideways enough. Register C5 holds both trial values: the stated
  15°±2° is scattered (its own method gives 3 s × 2.6°/s = 7.8°);
  Taylor takes the lower, method-backed 7.8° — so does this item (was
  quoted 8–15°). No A_lat/CLR adjustment holds the turns AND the wprime
  closure. Heel-spike exclusion (2026-09): a lateral-force heel
  formulation cannot reconcile drift with diameters (wrong-sign via CLR
  restore; the closest approach, 7.0° at 160k, blows every diameter
  +30–50%; runaway past ~200k) — see `ll/experimental_coupling.py`
  verdict; the missing term is a yaw moment from heel (Bonjean path).
  Heel itself is measured (3.5° stated, crew moved inside; 3° oar-rig
  limit) and its documented turn effect is thrust loss past the limit,
  not a side push (ch.31 §2.3 / G-turns notes) — consistent with the
  exclusion.
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

The force-mode profile shape (Figure 10 block — decoded 2026-09: the image
is a schematic, intercept/gradient values unpublished; the Hill
force-velocity structure corroborates force-driven demand conceptually —
the constant demand is the documented minimum-shape start; a
catch-concentrated profile would change the emerging drive times); the catch flip at low ship speed (the
start-from-rest); the numerical stiffness at catch; the kinematic
recovery `[?]` (the force recovery is unanchored); the sprint's residual
(the midship's straight-rudder drag — the trials' "partly raised" state —
D2's input); the HL's fatigue residual (the calibrated nets run ~8 %
under the force LL's actual drain through the turns — the annotated
gates); C_D's ±30 % band vs the gate widths; the LL's Ω folds in
the CLR restoring moment — the B1 swap must not double-count it.
