# Next steps — the open work

Status 2026-08-24. Everything DONE lives in `completed-work.md` (the verdict
ledger). Context: the deep-dive in `comparison-with-ll.md`.

The standing rule: the gates are the posterior — nothing is promoted or
changed without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration; nothing is tuned silently (the oQ-18 discipline). Current
state: **the force-driven oar is the PROMOTED default (Stream A complete,
2026-08)** — the stroke emerges from the rower's demand + the oar's
inertia + the blade's water force; the kinematic commanded-kinematics
mode stays as the labelled reference layer (force=False). Ω is computed
(the cross-flow audit); clr_offset/A_lat fitted (class-A — the real
lines are now in hand, Stream B1).

## The work streams

Five orthogonal tracks. Within a stream the steps are a sequence (a step
gates the next); the streams themselves do not block each other — their
cross-feed is information only (noted per step). The E-tags (E1–E8) are the
earlier section's names, kept for traceability.

### Stream A — the force-driven oar: the promotion sequence — DONE (2026-08)

The force mode is the promoted default (P1.6). The sequence's outcomes:

- **A1 — the turns in force mode ✓**: the W5 acceptance on the force
  layer: G1 90.3 m (+1.0 %), F1 118.2 m (+5.6 %), tightest 62.7 m
  (+1.1 %) — all within the bands.
- **A2 — the sprint and the cruise triple — investigated and resolved as
  the chain's L basis**: the force mode's emerging blade efficiency
  (0.758–0.775) matches the chain's E (0.756–0.78) to ~0.3 %; its
  pull length (the oar arc lin·B = 0.804, matching the shipboard
  measured strokes 0.75–0.85 and the sprint-validated effective chord
  0.78) sits ON the Olympias's own power chain (the hull=1.0 triple
  6.65/7.13/7.62 vs the chain's 6.57/7.15/7.69 — within ~1 %). The ch.7
  triple itself is Shaw's MARK II table (his ch.7 appendix: L = 0.99,
  E = 0.78, hull ×1.08 — `[x]`); the force mode's flat −6.3 % vs it is
  exactly that L basis — the Olympias's stroke is too short for 7–8 kt
  at those rates (ch.9's own claim). The demand now carries the chain's
  pull-length geometry (Fh = P·cosC_mean — the mean tangential
  projection; the EOM previously counted the full arc, ~3 % over). The
  sprint's named residual (−7 % at the 30-s point): the midship's
  straight-rudder drag (the turn-validated 39.4·V² — the ch.9's
  validation used the bare hull law) + the demand geometry; the W' was
  re-anchored to the force mode's excess (5.0 → 6.0 kJ — the same ch.9
  trial, the flip now counted) and the endurance holds ~45 s.
- **A3 — the MarkIIb — resolved**: the force mode reaches the chain's
  design speed at the full demand (9.58 kt vs Table 9.7's 9.7 —
  −1.2 %); the old "cap at 5.1" was the W'-drained state, not the
  physics. The kinematic's 6.06 shortfall (oQ-18) is gone in force
  mode; the A5 register's drive-time tension quantified (the emerging
  drive 0.41–0.43 s vs the measured 0.472 at the 0.078 m² blade — the
  B2 polar is the named closing path).
- **A4 — the promotion**: Ship's force default True; the full
  acceptance re-run (the LL gates, the HL re-calibration
  `calib-2026-08-22-0bdd860.json`, the harness); the backing's check
  (the moderate-speed full flat-plate — the kinematic's own parked-blade
  convention — with the trailing 8 % above the w_p threshold) landed as
  the shared back-hold; the stations layer stays kinematic by contract
  (its tests pass force=False explicitly).
- **A5 — the docs**: VALIDATION §5a/§10/§11, CALIBRATION rows 1/2/3/12,
  the registers — updated. The class-C carry-overs stay flagged: the
  flip's t_rise, the kinematic recovery `[?]`, HOLD_FRAC's grip, the
  thalmian shape, the B3 profile shape.

The kinematic mode remains the labelled reference layer (force=False —
its tests and the triple lock are untouched).

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

C3 (a measurement), B1 (the audit) and C1 (the transcription) are all
independent starts; Streams B and C run independently. The full acceptance
+ the HL re-calibration re-run after every promoted change.

## Risks (the named ones)

The B3 profile shape (Figure 10 block — the constant demand is the
documented minimum-shape start; a catch-concentrated profile would change
the emerging drive times); the catch flip at low ship speed (the
start-from-rest); the numerical stiffness at catch; the kinematic
recovery `[?]` (the force recovery is unanchored); the sprint's residual
(the midship's straight-rudder drag — the trials' "partly raised" state —
the C2 reconciliation's input); the HL's fatigue residual (the calibrated
nets run ~8 % under the force LL's actual drain through the turns — the
annotated gates); C_D's ±30 % band vs the gate widths; the LL's Ω folds in
the CLR restoring moment — the B1 swap must not double-count it.
