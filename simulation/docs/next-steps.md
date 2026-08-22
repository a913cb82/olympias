# Next steps — the open work

Status 2026-08-24. Everything DONE lives in `completed-work.md` (the verdict
ledger). Context: the deep-dive in `comparison-with-ll.md`.

The standing rule: the gates are the posterior — nothing is promoted or
changed without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration; nothing is tuned silently (the oQ-18 discipline). Current
state: the kinematic default, 159 checks green; the force-driven oar is a
labelled layer, OFF; Ω is computed (the cross-flow audit); clr_offset/A_lat
fitted (class-A — the real lines are now in hand, Stream B1).

## The work streams

Five orthogonal tracks. Within a stream the steps are a sequence (a step
gates the next); the streams themselves do not block each other — their
cross-feed is information only (noted per step). The E-tags (E1–E8) are the
earlier section's names, kept for traceability.

### Stream A — the force-driven oar: the promotion sequence

The goal (the single default we trust): the stroke emerges from the rower's
force + the oar's inertia + the blade's water force; the timing schedule
becomes validation anchors. The stream's gates consume Streams B/C's
verdicts as information, never as prerequisites.

- **A1. The turns in force mode — the hard gate (was the P1.6 blocker 1;
  ~1 h).** Run the W5 acceptance (G1 89.4 m / F1 111.9 m / tightest 62 m —
  ±7 %/±7 %/±10 %) on the force layer: the turn speeds are emergent, so the
  diameters will move — the question is how far. The result decides whether
  the promotion is even on the table. (The t_360 −23 % open item is the
  same physics family and stays open either way; B1/C1 inform this.)
- **A2. The sprint and the cruise triple (the blockers 2–3).** With C3's
  verdict and the B2 polar physics tested (the real blade's normal
  coefficient 1.37× the flat plate — a physics correction, not a knob),
  the remaining deficits' decompositions land here: the sprint 7.72 kt vs
  the trials' 8.2–8.3 (−6 %) and the triple 6.55/7.03/7.50 kt — a flat
  −6.3 % (the Table 9.6 acceptance pair HOLDS in force mode — 7.2 kt @
  28.8). The locks re-base to the force values with the deficits named,
  never silently.
- **A3. The MarkIIb decision (the blocker 4).** The force mode caps at
  ~5.1 kt where the chain says 9.7 — the demand force CAPS the blade force:
  the measured 0.472 s drive and the chain's P = 344 N at 46.3 spm are
  mutually inconsistent at the 0.078 m² blade (the measured stroke implies
  ~150 N mean pull). The A5 as-designed fix (area 1.3× + slip 1.2) does NOT
  bridge it in force mode. Decide: re-examine the MarkIIb's chain inputs
  (P/L/E at the sprint rate — the A5 register's tension, force-side-
  quantified) or re-base its acceptance on the force physics. (The
  workbook's linear thrust law is a different model family — it does not
  resolve this.)
- **A4. The promotion (P1.6).** T_DRIVE/CALIBRATED_T_DRIVE become anchors
  (validation-only); the force mode becomes the default (labelled — the
  kinematic mode stays as the reference); the full acceptance — the LL
  gates (A1/A2), the HL re-calibration (calibrate.py), the harness, the
  annotated rows re-measured. The class-C carry-overs stay flagged either
  way: the flip's t_rise (the G5 convention), the kinematic recovery `[?]`,
  HOLD_FRAC's grip, the thalmian shape, and the Table 3.2 couple anchor now
  sits −4.5 % from the constant demand (the B3 profile shape `[?]` — the
  undecoded Figure 10 — is the named closing path).
- **A5. The docs (P1.7).** CALIBRATION.md rows 1/2/4/12 statuses (t_drive
  eliminated; hold_frac/thalmian challenged); VALIDATION.md §2/§4/§5; the
  registers.

### Stream B — the hull grounding: the real-lines program

The Plan-2 completion plus the lateral family (the drift item, the
per-station layer's grounding). Computes the class-A rows (A_lat, clr)
that Stream A's turns depend on. Each step: if the values move → the LL
turn gates re-run + the HL re-calibration (the Plan-2 loop).

- **B1. The real-lines cross-flow audit (E1).** The lateral plane, A_lat,
  the CLR and the cross-flow J from
  `research/sources/galley-sizing-xlsm/basis_hull_offsets.tsv` (the
  parametric hull + the assumed ram were the named gap). Targets: the
  fitted clr_offset +0.8 m (the parametric hull computed AFT), Taylor's
  A_lat 35 m² (the parametric hull was 26–31 % light), and the CN split —
  the workbook's rectangular projection with CN 0.4 vs 0.8 vs our
  tapered-plane C_D 0.30 should collapse to one value on the real plane.
  Also bears on the drift-angle open item (the model's 1.4° vs the trials'
  8–15° — the lateral force's distribution).
- **B2. The lateral strengthening + the sway re-calibration (A1's
  follow-ups).** The per-station layer's grounding: the station decode
  (the plan pins the thole arms — the register B6 material), the lateral
  model's strengthening (the drift item's own fix — would absorb the oar
  turns' counter), and the sway re-calibration with the layer as the
  default (the lever's elimination is the fitting reduction).
- **B3. The mass and Iz reconciliations (E2/E6).** The LL's ship mass vs
  the workbook's 45.5 t full load / 25.75 t light (m_app and the turn
  physics follow); Iz = m(L/3)² = 5.28e6 (Rg from the 1:24-model pendulum
  tests) vs the LL's Iz. Cheap; run with the gates.

### Stream C — the second opinions (independent measurements of the same ship)

Inform Streams A and B; never block them.

- **C1. The independent-model cross-check (E4).** Transcribe the decoded
  VBA (ManAcceleration / OarForces / RudderForces — the Clarke–Gedling–
  Hine derivatives, the CN yaw damper, the Hoerner rudder + the 137V²+
  0.65V parasitic drag, the 81 N linear law) into a Python script; run the
  G1/F1/tightest scenarios + the top-speed curve; compare trajectories,
  diameters and the speed decay through the turns against the LL. A second
  trial-tuned model of the same ship is the strongest available cross-check
  of the turn physics (A1's family).
- **C2. The resistance-fit reconciliation (E5).** The trials piecewise
  (40.2/75.2/88.6·V²) runs 12–15 % below the chain law at 8–10 kt — same
  trials data, two fits. Document the cause (loading condition, rudder
  contribution, the fit families). Analysis only — the chain law is
  trial-speed-validated and stays unless a gate says otherwise.
- **C3. The no-head-room sprint test (E3) — T1's decisive cheap
  measurement.** The workbook's 9.95 kt is all-170 at the trials thrust law
  with NO thalmian shortfall; our LL's sprint (7.45 kinematic / 7.72 force)
  uses the fitted head-room 0.6 at 44.5 spm. Run the LL with the thalmian
  factor 1.0: if the equilibrium approaches ~9.9, the whole sprint deficit
  is the head-room shape (the class-C row), not the blade law; if it stays
  ~8, the E/A5 family is the suspect. Either way the T1 ledger gets a
  verdict — A2's first input.

### Stream D — the portability program (the tuning rule's test)

A larger scope; the kick-off is a decision.

- **D1. The pentaconter milestone (E7).** The workbook's pentaconter
  designs (monoreme: 25/side, LOA 31 m, 21 t, GMT 0.643 m; bireme: LWL
  17.2 m, B 2.8, T 0.759, 14.4 t — with the Transform sheet's offsets and
  the author's powering/turn predictions) are a NEW ship whose "plans" ARE
  held: run the class-A machinery from its offsets and compare with the
  workbook's numbers — the tuning rule's "for a new ship whose plans ARE
  held, class A computes from day one" made testable. Scope decision: a
  research-side portability study vs a full LL scenario.
- **D2. The remaining decode (E8).** The paper's figures (Figures 2/3/5,
  Tables 1/2 — image reading) and the workbook's 15 charts' plotted series
  — feeds D1's inputs and C1's fidelity.

### Stream E — the performance stream (engineering hygiene)

No physics: speed of the simulators and the suite. Behaviour-neutral by
construction — every step re-verifies the trajectories byte-identical to
HEAD before it ships (the probes and the 159-check suite). The landed
passes (2026-08-24) are recorded in completed-work §6 (suite 318 → 237 s;
the stations layer's tests −53 %); only the open levers follow, in
measured-priority order:

- **F1. The suite's time step (the biggest remaining lever).** The gates
  are kt/%-tolerances; the long settle tests (300–900 s sims at dt = 0.01,
  some already at 0.02) dominate the suite's 237 s. Doubling dt for the
  long runs halves their cost; the LL has a dt-convergence gate
  (test_dt_convergence) — measure each scenario family's deviation at
  0.02 against the gate widths BEFORE switching any. The fixed-step rule
  is about replayability (determinism), not the value.
- **F2. hl/calibrate.py's LL cells.** The `_LL_CACHE` is per-process —
  every ~12-min run re-derives the yaw-gate and pressure-cell rows.
  Persist the cached rows keyed by the LL commit (a JSON beside the
  calibration) and/or parallelize the independent cell grid (multiprocess).
- **F3. pytest-xdist for the suite.** The suite is ~95 % CPU-bound LL
  runs, the tests are self-contained — `pytest -n auto` splits them
  across cores (a dev convenience; determinism is per-test).
- **F4. The bisection helpers** (`rate_for_speed`, `run_hull`): 50
  iterations × 4-cycle sims per call — warm-start from the previous
  rate's root (the curves are smooth). Minor; only if F1–F3 land.

## Kick-off (what is parallelizable now)

A1 (an hour — the hard gate), C3 (a measurement), B1 (the audit) and C1
(the transcription) are all independent starts; Streams B and C run while
Stream A waits on its gates. The full acceptance + the HL re-calibration
re-run after every promoted change.

## Risks (the named ones)

The profile shape (Figure 10 block — the minimum-shape start); the catch
flip at low ship speed (the start-from-rest); the numerical stiffness at
catch; the recovery-phase model is unanchored; the T1 interaction — the
emergent rate→power may move the ch.7 triple either way (the gate decides,
the lock follows the measurement); C_D's ±30 % band vs the gate widths;
the LL's Ω folds in the CLR restoring moment — the B1 swap must not
double-count it.
