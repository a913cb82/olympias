# Next steps — the open work, in priority order

Status 2026-08-22. Everything DONE lives in `completed-work.md` (the verdict
ledger — the A/B/C investigations, Plan 1's landed layer, Plan 2's verdict,
the Braithwaite sources' wins, the standing choices). Context: the deep-dive
in `comparison-with-ll.md`.

The standing rule: the gates are the posterior — nothing is promoted or
changed without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration; nothing is tuned silently (the oQ-18 discipline). Current
state: the kinematic default, 162 checks green; the force-driven oar is a
labelled layer, OFF; Ω is computed (the cross-flow audit), clr_offset/A_lat
fitted (class-A, blocked on the real lines — now in hand, #2 below).

## The priority order

**1. The turns in force mode — the hard gate (P1.6 blocker 1). ~1 h.**
The W5 turn family (G1 89.4 m / F1 111.9 m / tightest 62 m — ±7 %/±7 %/
±10 %) has only ever run on the kinematic oar; in force mode the turn
speeds are emergent (the speed-holding rates shift), so the diameters will
move — the question is how far. Prerequisite, not judgment: run the
acceptance, see the numbers; the result decides whether the promotion is
even on the table. (The t_360 −23 % open item is the same physics family
and stays open either way.)

**2. E1 — the real-lines cross-flow audit (Plan 2's completion).**
Run the lane-5 audit on `basis_hull_offsets.tsv` (the parametric hull + the
assumed ram were the named gap): the lateral plane, A_lat, the CLR and the
cross-flow J from the actual sections. Targets: the fitted clr_offset
+0.8 m (the parametric hull computed AFT), Taylor's A_lat 35 m² (the
parametric hull was 26–31 % light), and the CN split — the workbook's
rectangular projection with CN 0.4 vs 0.8 vs our tapered-plane C_D 0.30
should collapse to one value on the real plane. If the values move: the LL
turn gates re-run + the HL re-calibration (the Plan-2 loop). The real plane
also bears on the drift-angle open item (the model's 1.4° vs the trials'
8–15°).

**3. E3 — the no-head-room sprint test (T1's decisive cheap measurement).**
The workbook's 9.95 kt is all-170 at the trials thrust law with NO thalmian
shortfall; our LL's sprint (7.45 kinematic / 7.72 force) uses the fitted
head-room 0.6 at 44.5 spm. Run the LL with the thalmian factor 1.0: if the
equilibrium approaches ~9.9, the whole sprint deficit is the head-room
shape (the class-C row), not the blade law; if it stays ~8, the E/A5 family
is the suspect. Either way the T1 ledger gets a verdict and the sprint
blocker (#9) a named direction.

**4. E4 — the independent-model cross-check.**
The workbook's VBA is fully decoded: transcribe ManAcceleration /
OarForces / RudderForces (Clarke–Gedling–Hine derivatives, the CN yaw
damper, the Hoerner rudder + the 137V²+0.65V parasitic drag, the 81 N
linear law) into a Python script and run the G1/F1/tightest scenarios +
the top-speed curve — compare trajectories, diameters and the speed decay
through the turns against the LL. A second trial-tuned model of the same
ship is the strongest available cross-check of the turn physics (#1's
family).

**5. E2 + E6 — the mass and Iz reconciliations.**
The LL's ship mass vs the workbook's 45.5 t full load / 25.75 t light
(m_app and the turn physics follow); Iz = m(L/3)² = 5.28e6 (Rg from the
1:24-model pendulum tests) vs the LL's Iz. Run with the gates.

**6. E5 — the resistance-fit reconciliation. Analysis only.**
The trials piecewise (40.2/75.2/88.6·V²) runs 12–15 % below the chain law
at 8–10 kt — same trials data, two fits. Document the cause (loading
condition, rudder contribution, the fit families); the chain law is
trial-speed-validated and stays unless a gate says otherwise.

**7. A1's follow-ups — the per-station layer's grounding.**
The layer is built with measured verdicts (completed-work §1): the
follow-ups are the station decode (the plan pins the thole arms — the
register B6 material), the lateral model's strengthening (the drift item's
own fix — would absorb the oar turns' counter), and the sway
re-calibration with the layer as the default (the lever's elimination is
the fitting reduction).

**8. The MarkIIb decision (P1.6 blocker 4).**
The force mode caps at ~5.1 kt where the chain says 9.7: the demand force
CAPS the blade force, so the measured 0.472 s drive and the chain's
P = 344 N at 46.3 spm are mutually inconsistent at the 0.078 m² blade (the
measured stroke implies ~150 N mean pull). The A5 as-designed fix (area
1.3× + slip 1.2) does NOT bridge it in force mode. Needs a decision:
re-examine the MarkIIb's chain inputs (P/L/E at the sprint rate — the A5
register's tension, force-side-quantified) or re-base its acceptance on
the force physics. (The workbook's linear thrust law is a different model
family and does not resolve this.)

**9. The sprint and the cruise triple (P1.6 blockers 2–3).**
With #3 measured and the B2 polar physics tested (the real blade's normal
coefficient 1.37× the flat plate — a physics correction, not a knob), the
remaining deficits' decompositions land here: the sprint 7.72 kt vs the
trials' 8.2–8.3 (−6 %) and the triple 6.55/7.03/7.50 — a flat −6.3 % (the
Table 9.6 acceptance pair HOLDS in force mode — 7.2 kt @ 28.8). The locks
re-base to the force values with the deficits named, never silently.

**10. P1.6 the promotion.** T_DRIVE/CALIBRATED_T_DRIVE become anchors
(validation-only); the force mode becomes the default (labelled — the
kinematic mode stays as the reference); the full acceptance — the LL gates
(#1, #9), the HL re-calibration (calibrate.py), the harness, the annotated
rows re-measured. The class-C carry-overs stay flagged either way: the
flip's t_rise (the G5 convention), the kinematic recovery `[?]`,
HOLD_FRAC's grip, the thalmian shape, and the Table 3.2 couple anchor now
sits −4.5 % from the constant demand (the B3 profile shape `[?]` — the
undecoded Figure 10 — is the named closing path).

**11. P1.7 the docs.** CALIBRATION.md rows 1/2/4/12 statuses (t_drive
eliminated; hold_frac/thalmian challenged); VALIDATION.md §2/§4/§5; the
registers.

**12. E7 — the portability milestone (scope decision needed).**
The workbook's pentaconter designs (monoreme: 25/side, LOA 31 m, 21 t,
GMT 0.643 m; bireme: LWL 17.2 m, B 2.8, T 0.759, 14.4 t — with the
Transform sheet's offsets and the author's powering/turn predictions) are
a NEW ship whose "plans" ARE held. Running our class-A machinery from the
pentaconter's offsets and comparing with the workbook's numbers is the
tuning rule's "for a new ship whose plans ARE held, class A computes from
day one" — made testable. A research-side portability study vs a full LL
scenario: a decision.

**13. E8 — the remaining decode (low priority).** The paper's figures
(Figures 2/3/5, Tables 1/2 — image reading) and the workbook's 15 charts'
plotted series.

## Risks (the promotion path's named ones)

The profile shape (Figure 10 block — the minimum-shape start); the catch
flip at low ship speed (the start-from-rest); the numerical stiffness at
catch; the recovery-phase model is unanchored; the T1 interaction — the
emergent rate→power may move the ch.7 triple either way (the gate decides,
the lock follows the measurement); C_D's ±30 % band vs the gate widths;
the LL's Ω folds in the CLR restoring moment — the #2 swap must not
double-count it.
