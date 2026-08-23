# Next steps — the open work

Status 2026-08-23. Everything DONE lives in `completed-work.md` (the verdict
ledger). Context: the deep-dive in `comparison-with-ll.md`.

The standing rule: the gates are the posterior — nothing is promoted or
changed without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration; nothing is tuned silently (the oQ-18 discipline). Current
state: **the force-driven oar is the PROMOTED default (Stream A complete,
2026-08) and the hull is GROUNDED in the real Lines Plan (Stream C B1
complete, 2026-08-23)** — the stroke emerges from the demand + inertia +
blade force; the hull's lateral plane (A_lat 30.09 m² at trial WL 1.10 m),
CLR (0.93 m forward, x_clr 16.60 m from AP) and cross-flow J (23217 m⁵)
are now computed from `basis_hull_offsets.tsv` (LWL 32.35 m, 21 stations);
Omega = ½ρ·0.252·J = 3.00e6 (C_D 0.252, rectangular vs tapered
reconciliation, DECODE C9); the parametric hull_form (p=1.5,q=0.8) is
deleted. The kinematic layer stays as the labelled reference (force=False).

## The work streams

Two orthogonal tracks remain (Streams A, B and C B1 are done — see
`completed-work.md §7`, `§8` and `§9`). Within a stream the steps are a
sequence (a step gates the next); the streams themselves do not block
 each other — their cross-feed is information only (noted per step).
The E-tags (E1–E8) are the earlier section's names, kept for traceability.

Serial priority (simplest direction, one stream at a time): **C(b2/b3) → D → E** — C's remaining B2/B3 close the last lever/mass rows; D is the independent second opinions (D3 is a 1h decisive measurement, D1 is the heavy transcription); E is the portability scope decision.

### Stream C — the hull grounding: the real-lines program

The Plan-2 completion plus the lateral family (the drift item, the
per-station layer's grounding). The hull's class-A rows (A_lat, clr, J)
are now grounded in the real Lines Plan (B1 complete, 2026-08-23); the
parametric hull_form is deleted. Each remaining step: if the values move
→ the LL turn gates re-run + the HL re-calibration (the Plan-2 loop).

- **B1. DONE — the real-lines cross-flow audit (E1).** Grounded:
  A_lat 30.09 m² at trial WL 1.10 m (31.70 m² at design WL 1.15 m),
  x_clr 16.60 m from AP, CLR offset 0.93 m forward (x_clr−x_cg, x_cg at
  LCB 15.67 m even keel), J 23217 m⁵ (x_cg 15.67), Omega = ½ρ·0.252·J =
  3.00e6 (C_D 0.252, the rectangular 0.4/0.8 vs tapered 0.30
  reconciliation, DECODE C9; the parametric J 21144 at C_D 0.30 gave
  3.25e6 (=1.6% from fitted 3.20e6) is the documented reference). The
  fitted clr_offset +0.8 m and Taylor A_lat 35 m² are superseded; the
  real hull's lateral plane is 14% below Taylor (was 26–31% light on
  the parametric) and the CLR is 0.13 m forward of the fitted value —
  the W5 turns hold (G1 90.1 m +0.8%, F1 118.9 m +6.3%, tightest 62.1 m
  +0.1%) with no regression, the HL re-calibrated (calib-2026-08-23-
  9ebaf42.json, 876 s, cache ll_cache-9ebaf42.json). The drift-angle
  open item (1.4° vs 8–15°) is unchanged (the lateral distribution, not
  the area, drives it).
- **B2. The lateral strengthening + the sway re-calibration (A1's
  follow-ups).** The per-station layer's grounding: the station decode
  (the plan pins the thole arms — the register B6 material), the lateral
  model's strengthening (the drift item's own fix — would absorb the oar
  turns' counter), and the sway re-calibration with the layer as the
  default (the lever's elimination is the fitting reduction).
- **B3. The mass and Iz reconciliations (E2/E6) — grounded but not
  promoted.** The real hull gives M 40.95 t at trial WL 1.10 m (Vol
  39.95 m³) and 45.55 t at design WL 1.15 m (Vol 44.44 m³, the workbook's
  44.26 m³), M_app 45.05 t/50.11 t, Iz = m(L/3)² 4.76e6/5.30e6 (L=32.35 m,
  Rg L/3 from the 1:24-model pendulum). The LL's trial mass stays at the
  fitted 42.0 t / 4.0e6 (the 2.5% shift to 40.95 t moves F1 +1.6% to
  120.4 m, just over the 7% gate; the full-load 45.5 t moves F1 +7.6%
  to 120.4 m). The masses are now computed and exposed as M_REAL etc.
  in `crossflow.py`/`chain.py`; promotion is a gate-re-baselining step.

### Stream D — the second opinions (independent measurements of the same ship)

Inform Stream C; never block it (Stream A is done).

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
  with NO thalmian shortfall; our LL's sprint (force promoted: 7.65 kt
  @ 44.5 spm, 0.6 head-room; no-head-room 9.16 kt) uses the fitted
  head-room 0.6 at 44.5 spm. Run the LL with the thalmian factor 1.0:
  if the equilibrium approaches ~9.9, the whole sprint deficit is the
  head-room shape (the class-C row), not the blade law; if it stays
  ~8, the E/A5 family is the suspect. Either way the T1 ledger gets a
  verdict.

### Stream E — the portability program (the tuning rule's test)

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

## Kick-off (what is parallelizable now)

Serial priority is `C(b2/b3) → D → E`; if parallel, `B2` (the station
decode), `C3` (a measurement) and `C1` (the transcription) are all
independent starts; Streams C and D run independently. The full acceptance
+ the HL re-calibration re-run after every promoted change. Stream C B1
is done and the HL is re-calibrated on it (calib-2026-08-23-9ebaf42).

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
