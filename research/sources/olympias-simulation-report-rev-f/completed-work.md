# Completed work — the verdict ledger

Everything moved OUT of `next-steps.md` (2026-08-22): the items that are
done, with their verdicts and where the detail lives. The open work is in
`next-steps.md` (priority order). Context for the A/B/C items: the deep-dive
in `comparison-with-ll.md` (the three baskets — A: LL realism upgrades,
B: differing choices to investigate, C: new data → new validation). The
standing rule was applied throughout: the gates are the posterior; the
measured values become validation references, never inputs; nothing is
promoted without the acceptance re-run (VALIDATION §0–8) and the HL
re-calibration.

## 1. The A/B/C investigations (all DONE)

**A1 — the per-station oar layer: BUILT, the decomposition CORRECTED, the
verdicts measured; the follow-ups remain open (see next-steps Stream B2).**
`ll/stations.py` + `Ship(stations=True)` — 170 oars at their stations, each
blade's flow from the ship's (u, v, r). Measured verdicts:
- the yaw moment's arm is the BLADE's position: the mean blade arm 4.82 m —
  the Taylor 4.8 IS the blade's arm; the LL's sway-calibrated 1.8 m is the
  NET (blade arm − the oars' local-flow damping ~400 kN·m·s at the g1
  settle). The register C3's earlier "physical arm 1.8" reading was the
  wrong decomposition — corrected.
- the layer's turn pattern is INVERTED vs the trials (helm turns WIDER:
  g1 90.1→128.0, f1 118.0→232.1; oar turns TIGHTER: tightest 62.5→57.4,
  oar-hold 102.9→81.4, oar-back 102.9→78.7); a real bug found and fixed
  (the held/back-hold stations' zero blade positions — the brake's moment
  silently dropped, minor); no (Ω, clr) resolves the inversion — the
  explicit local-flow damping ~9.8 kN·m at the settles (~73 % of the
  22.5°-helm rudder torque) eats the small-helm turns while the oar turns
  need the lateral strengthening (the drift item's direction); the
  damping's FORM matches the report's per-oar formula (his Vb = Lo·ω·cosθ
  and the water's (u, v, r) at the blade) — the mechanism's not a
  transcription error, its magnitude is the open question.
Detail: the register C3 row; `ll/tests/test_revf_layers.py`; VALIDATION.

**A2 — the stroke phase structure: DONE (the negative result).**
The trapezoidal drive profile (`ll/oar.py profile="trap"`) measured at the
cruise point: with the report's in-water fraction 0.39 (0.72 s) the mean
thrust is −35.5 N vs the chain's +17.5 N — the effective-pull (0.43 s) and
the kinematic in-water (0.7 s) are jointly incompatible with ANY trapezoid;
they imply a PEAKED mid-stroke ω(t) whose shape the available data does not
determine. The constant-ω + the effective-pull stays the validated
kinematics. The shape's measurement (a force-trace or blade-video record)
would be the unlock — not in our sources. Locked: `test_revf_layers.py`.

**A3 — the rudder as an aerofoil: DONE (blocked, named).** The report's
Figure 12 has NO printed dimensions (area, section, stock position); the
trials' rudder plans are not in our sources. The Taylor empirical model
stays gate-passing; closed unless the rudder plans surface.

**B1 — scalar added mass vs the mass matrix: DONE (the measured no-op).**
`Ship(mass_matrix=True)` (2×2 sway-yaw solve, add_v 0.9 / add_r 0.2 /
add_c 0.1 `[?]`): the g1's D shifts +2.3 %, the drift −1.5° → −1.4° — the
couplings act on the TRANSIENTS; the trial-measured scalar m_app (1.10×)
stays. Locked: `test_mass_matrix_noop`.

**B2 — flat-plate vs the lift+drag polars: DONE (the lift is NOT
negligible — the labelled polar variant's built).** The report's polars
decoded from the OMML: C_D = 2·sin²α, C_L = sin(2α). At our stroke the
angles run 54–58° where C_L ≈ 0.90–0.95 — the lift is ~55 % of the total
force; the polar's normal coefficient is 1.37× the flat plate's at the
median angle. `BLADE_POLAR` gives +40 % mean thrust at 7.2 kt — the
flat-plate's shortfall the calibrated C_N·A product absorbs (the A5
register family: the physical blade 0.113 m² + the polars would produce
~2× the chain's force). The full vector form is the noted refinement.
Locked: `test_polar_variant_thrust`.

**B3 — kinematic vs force control (the force-anchor cross-check): DONE
(the structure decoded, the values blocked).** The report's force-curve
structure recovered from the OMML: the target blade moment is a PARABOLA
of the relative oar angle with the catchFactor's continuity and the max
moment LINEAR in the ship speed. The quantitative intercept/gradient live
only in the raster Figure 10 (image12.png — no text layer) — the
cross-check is blocked on that decode `[?]`. Our anchors are trial-derived
— a cross-check only, the measured kinematics stay the ceiling.

**B4 — the turn model's drag law: DONE (the measured no-op).**
`Ship(drag_law=...)` (taylor/trials/chain) measured on the harness's five
cells: the D's shift ≤ 1.1 %; the tightest's t_360 unchanged (101 s either
way) — the turns run BELOW 6.7 kt where the laws agree on 40.2v², and the
chain law's drag is a small share of the turn's balance (the rudder's drag
dominates). The t_360's −23 % is NOT the drag law's. Locked:
`test_drag_law_noop`.

**B5 — the rower's moving mass: DONE (documented).** The report's own
equations confirm the handle/footplate forces are internal to the hull+crew
rigid body — the net hull force is the blade's alone; the moving-mass
inertial loads transfer through the footplate only as internal loads.
Negligible for the surge/sway/yaw. The register D10 has the
anthropometrics; the verdict's recorded, no code.

**B6 — aggregated tiers vs per-oar: overlaps A1** (the per-station flow and
the short oars at the extremes). No separate work.

**C1 — the stationary-turn anchor (Ref (1) p30): DONE.** The scenario's
built (both readings: the in-place turn — one side Z+T ahead vs the other's
back — and the one-side ahead-vs-rest) and locked in
`ll/tests/test_revf_anchors.py`. Verdicts: the in-place turn settles
**2.32°/s** (−34 % vs 3.5) and the one-side reading **1.06°/s** (−70 %) —
the model is too SLOW at low-speed partial crew (the SECOND direction of
the turn-speed family; the t_360 item is the model too FAST at full crew).
Register C7; VALIDATION §11.2/§11.3; no gate (it would fail).

**C2 — the zig-zag overshoots (p30): DONE.** A true Kempf zig-zag (helm
22.5, flips at the ±20° crossings) built and locked in
`test_revf_anchors.py`. Verdict: the LL overshoots **11.0° then 12.8–13.0°**
vs the trials' 8°/7° (+60–85 %) — the fishtail's reversal carries ~5–6° too
far (the t_360 family's dynamics). VALIDATION §11.2 T10 + §11.3 item 1b,
register C8; no gate (it would fail).

**C3 — the rudder-drag constant cross-check: DONE.** Measured +8–9 % at
5–8 kt — an independent confirmation of the 39.4/kt² constant; later
corroborated by the Braithwaite workbook's VBA (drag2 = 0.5·(137V²+0.65V)·
(2A/1.5)). Register C3; locked in `test_revf_anchors.py` (the 0–12 % band).

**C4 — the hull-resistance piecewise (p74): DONE.** The raw trials bands
(40.2v² / 75.2v²−1560 / 88.6v²−2640) in the register B2 row, with Rev F's
whole-range cubic (51.4v³−76v²+223v) and the measured 10–20 % gap vs the
chain law — later corroborated source-side by the workbook's Powering sheet
("cf ref 1 p82").

**C5 — the oar table (Table 3): DONE.** The blade area 0.113 m² is the
register A5 row's source-side anchor (the chain's 0.078 = 1.45× smaller);
the MOI 30 kg m² in the A9 row (the Table 3.1 A-family value in the wild —
the A/B anomaly is source-side); the short-oar geometry, the CP distances
and the rake in the A9 row for the per-station layer.

**C6 — the stroke-time budget (p28): DONE.** The in-water fraction 0.39 vs
the chain's effective-pull 0.21 at 28.8 spm in the register D10 row; the
handle-arc cross-check (0.80 m vs his 0.7 measured / 1.0 achievable) is
consistent. Feeds A2.

**C7 — the thranite-only speed (p50): DONE.** The LL's 62-oar equilibrium
at 33.3 spm: **4.31 kt** (+31 % vs the reported 3.3 kt). The record's
context is unresolved `[?]` — register D10 row as a loose cross-check only,
no gate.

## 2. Plan 1 — the force-driven oar: P1.1–P1.5 landed (a labelled layer)

The stroke (drive time, sweep, the ω profile) EMERGES from the rower's
applied force + the oar's inertia + the blade's water force; the measured
kinematics (Table 9.6's 0.43 s, the sweep) become the gates, not the
inputs. Status: `ll/oar.py` force mode + `Ship(force=True)`, default OFF;
the kinematic mode untouched.

**The key discovery:** the drive SELF-BALANCES — the oar settles at the
speed where the blade drag exactly absorbs the demand
(vn = −√(Fh·lin/(k·l_cp))), never a stall — so the emerging stroke IS the
measured stroke without a fitted timing schedule.

**The results** (locked in `ll/tests/test_force_drive.py` F1-1..F1-7 and
`ll/tests/test_force_ship.py` F2-1..F2-3; VALIDATION §5a, §8, §11-T1;
CALIBRATION rows 1–2 marked IN PROGRESS):
- the emerging drive times at the four Table 9.6 points
  **1.005/0.972/0.925/0.932** (the Olympias pair ±5 %; the MarkIIb −7 %/−7 %
  — the A5 family); the emerging thrust at 7.2 kt 0.976 × the kinematic;
- the sprint **7.72 kt** (30 s @ 44.5 spm) vs the kinematic's 7.45 (the
  trials 8.2–8.3 — the deficit reduced, not closed — the T1 family);
- the cruise triple **6.55/7.03/7.50 kt** — a FLAT −6.3 % vs the ch.7
  reference (the kinematic's deficit grows with rate: −2.5/−4.6/−6.1 — the
  T1 tension's shape changed, its size not);
- the rest start **4.06 kt @ 10 s** with the peak handle force at the
  demand (330 N) — the catch deadspot is gone (a parked blade would have
  demanded ~2 kN);
- the flip forces 263–390 N, all under Fh_MAX; the MarkIIb force-mode
  equilibrium ~5.1 kt at 46.3 spm — the A5 gap quantified from the force
  side (the demand caps the blade force; the area fix alone can't bridge
  it — recorded, not tuned).

**The phases:** P1.1 (the force model — the minimum-shape constant demand;
the B3 shape stays `[?]` — Figure 10) ✅; P1.2 (the oar EOM layer — the
flip, the drive substeps at 1e-3, the recovery kinematic `[?]`) ✅; P1.3
(the single-oar validation — the 4-point ±5 % gate) ✅; P1.4 (the crew
integration — TierCrew/SideCrew/Ship force plumbing, the thalmian factor
scales the DEMAND at the source) ✅; P1.5 (the ship gates — measured,
locked as the layer's own gates; the trials' acceptance at P1.6) 🟡.

The suite: 162 checks green (the kinematic default untouched).

## 3. Plan 2 — the cross-flow audit: verdict executed 2026-08-22

**Ω ELIMINATED — the audit closed.** `research/lane-5-manoeuvre/crossflow.py`
computes Ω = ½ρ·C_D·J (the drag-crisis C_D = 0.3, literature, Re ~ 1e6; the
parametric hull + the ram): the fitted 3.2e6 equals the computation at
1.6 % — the register C1 units caveat resolves (Ω IS the quadratic cross-flow
yaw moment). The computed Ω (3.25e6) is now the LL default; the turn gates
hold (g1 +0.9 %, f1 +5.6 %, tightest +1.0 % — no regression vs the fitted
3.2e6's +0.4/+5.1/+0.4 %); the HL re-calibrated
(`hl/calibration/calib-2026-08-22-ea571f9.json` — the tau_exit re-scan
19 → 8 s, drift_tau_exp 0.37; the zig-zag position rows re-annotated). The
suite was 152 checks green at that point.

**Two honest negatives recorded:**
(a) the CONSISTENT single-C_D cross-flow model (`sway="crossflow"`,
replacing the f_hull/q_hull/Ω trio with one distribution) FAILED the gates
— the turns widen +45–85 %: the quadratic form's net lateral force is ~13×
weaker than the Taylor f_hull at the LL's drift angles, so the drift
balloons to ~20–25° (the named suspect: the C_D split between the force and
the moment, or the real ends); the mode stays available but OFF.
(b) the CLR is NOT reproduced: the computed lateral-plane centroid is AFT
of the c.g. (−0.2…−1.4 m vs the fitted +0.8 forward) — the parametric ends
+ the ram's assumed plane are the gap; the real lines are the named path
(now in hand — see §4 and next-steps Stream B1). A_lat: the parametric hull
under-predicts Taylor's 35 m² by 26–31 % — same cause.

Detail: `crossflow.py`; VALIDATION §7.2/§9/§10.2/§11.1; CALIBRATION row 5;
the experiment `research/tools/scratch/plan2_sway_experiment.py`; the
commit efe1319.

## 4. The Braithwaite sources — what the new data settled (2026-08-22)

The design tool (`sources/galley-sizing-xlsm/`) and the RINA draft paper
(`sources/warship-evolution-6th-bc/`) — both fully decoded (DECODE.md in
each directory; the lane notes `lane-3/braithwaite-workbook.md`,
`lane-4/braithwaite-workbook.md`, `lane-5/braithwaite-workbook.md`).
Validation wins recorded:
- **Zero-speed thrust**: the trials' 81 N/oarsman vs the LL's equilibrium
  ~82 N/oar at 38.75 spm, V = 0 — two independent derivations agree.
- **Lightship**: 25.748 t (scantlings + 1:24 model + inclining) confirms
  the chain's 25.798 t anchor to 50 kg; the full load 45.5 t sits in the
  43–47 t family (register B1).
- **The piecewise trials resistance fit** (40.2/75.2/88.6·V² — "cf ref 1
  p82") corroborated source-side (register B2); the rudder parasitic-drag
  law 137V²+0.65V corroborated in the workbook's VBA (register C3).
- **The real lines**: the "no numerical offsets" caveat (register B6,
  offsets-eliav.md) is retired — the offset table is in hand
  (`basis_hull_offsets.tsv`, 21 stations, LWL 32.35 m), and the Plan-2
  verdict's named gap is now concrete.
- New register rows from the source: A10 (the 9.95 kt no-head-room bound),
  B8 (real lines vs the parametric hull: Cw 0.768 vs 0.556, WSA 130.5 vs
  81.3 m²), C9 (the author's CN 0.4/0.8 split), C10 (Iz = m(L/3)² = 5.28e6).

## 5. Standing choices (kept as-is — decisions, not tasks)

- The kinematic-control philosophy (the measured kinematics are the truth
  the gates are built on; the force-curve school is the cross-check, not
  the replacement) — until the force-driven oar (Plan 1) passes its
  promotion gates (next-steps Stream A4).
- The chain's hull-power law (155V³ + 4.13V⁵, V in m/s) — the power chain
  closes on it; the trials' raw piecewise (10–20 % below) stays a register
  cross-check (next-steps Stream C2).
- The report's unvalidated status: nothing is promoted to an anchor without
  the source's context being checked against the trials report itself (his
  Ref (1), which we still do not hold).
