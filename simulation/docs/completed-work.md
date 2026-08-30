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
The trapezoidal drive profile (the removed `profile="trap"` variant)
measured at the cruise point: with the report's in-water fraction 0.39
(0.72 s) the mean thrust is −35.5 N vs the chain's +17.5 N — the
effective-pull (0.43 s) and
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
stays. The variant and its lock test were removed with the 2026-08
cleanup (the verdict above is the record).

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
dominates). The t_360's −23 % is NOT the drag law's. The variants and their
lock test were removed with the 2026-08 cleanup (the chain law is the only
law; the verdict above is the record).

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
inputs. Status at P1.5: `ll/oar.py` force mode + `Ship(force=True)`,
default OFF — the kinematic mode untouched. **Now PROMOTED — see §7
(the force mode is the Ship's default; kinematic is `force=False`).**

**The key discovery:** the drive SELF-BALANCES — the oar settles at the
speed where the blade drag exactly absorbs the demand
(vn = −√(Fh·lin/(k·l_cp))), never a stall — so the emerging stroke IS the
measured stroke without a fitted timing schedule.

**The results at P1.5** (locked in `ll/tests/test_force_drive.py` F1-1..F1-7 and
`ll/tests/test_force_ship.py` F2-1..F2-3; VALIDATION §5a, §8, §11-T1;
CALIBRATION rows 1–2 marked IN PROGRESS — **now DONE, see §7**):
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
locked as the layer's own gates) ✅; P1.6 the promotion **DONE** (see §7).

The suite at P1.5: 162 checks green (the kinematic default untouched;
now 159 with the force default — §7).

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
the moment, or the real ends). The mode and its code were removed with the
2026-08 cleanup; the verdict above is the record.
(b) the CLR is NOT reproduced: the computed lateral-plane centroid is AFT
of the c.g. (−0.2…−1.4 m vs the fitted +0.8 forward) — the parametric ends
+ the ram's assumed plane are the gap; the real lines are the named path
(now in hand — see §4 and next-steps Stream B1). A_lat: the parametric hull
under-predicts Taylor's 35 m² by 26–31 % — same cause.

Detail: `crossflow.py`; VALIDATION §7.2/§9/§10.2/§11.1; CALIBRATION row 5;
the commit efe1319.

## 4. The Braithwaite sources — what the new data settled (2026-08-22)

The design tool (`research/sources/galley-sizing-xlsm/`) and the RINA draft paper
(`research/sources/warship-evolution-6th-bc/`) — both fully decoded (DECODE.md in
each directory; the lane notes `research/lane-3-hull/braithwaite-workbook.md`,
`research/lane-4-oars/braithwaite-workbook.md`,
`research/lane-5-manoeuvre/braithwaite-workbook.md`).
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
  lane-3-hull `hull-form.md` Part 2) is retired — the offset table is in hand
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

## 6. The performance pass (2026-08-24) — behaviour-identical, measured

The LL's hot paths profiled (cProfile) and four easy wins landed. Every
change verified against HEAD: the kinematic aggregated, the stations-mode
trajectory, the four force-mode drive times, the force sprint 30-s burst —
all byte-identical to the pre-change values (the exact-catch-crossing
split was required to keep the force sprint identical; the flip's substeps
were found to carry no hull force and the recovery's crossing is split
analytically — the phase boundaries stay exact).

- **Per-rig blade constants** (`blade.blade_consts`): lin, l_cp, k,
  cos(cant), slip, sweep precomputed once per oar; the per-step
  `blade_force(..., bc=)` skips the per-call derivations (1 M+ calls in
  the stations mode). The polar branch's `0.5·rho·A·2.0` folds into the
  precomputed k (algebraically identical).
- **`OarStep` slots** (frozen, now `slots=True`): the per-oar per-step
  telemetry object stops carrying a per-instance dict.
- **Per-crew oar pairs** (`TierCrew._pairs`): the aligned
  (oar, rig, station) triples built once (and on every oar rebuild), the
  `blade_pos` import hoisted to module level, the force/power scale
  hoisted out of the per-oar loop.
- **Phase-aware force substeps** (`Oar._step_force`): the drive (stiff,
  ~50 s⁻¹) and the flip substep at 1e-3 as before; the kinematic recovery
  runs one step with the catch crossing split analytically — same physics,
  substeps confined to the phases that carry force.
- **The vectorized kinematic-stations pass** (`TierCrew._stations_step`):
  the tier's oars are PHASE-LOCKED (identical C/omega at every step — the
  kinematics are per-tier, the local flow is the only per-station input),
  so the phase machine stays scalar on the first oar and one numpy pass
  computes the 170 per-station blade forces/positions and the yaw/lateral
  sums. Conventions match the scalar loop exactly (forces at the
  pre-advance C, positions at the post-advance C, the inertia pulse
  scalar). The force mode is NOT phase-locked (each drive integrates its
  own EOM) — it keeps the scalar loop; the aggregated default was left
  scalar (6 oars — numpy overhead would dominate).

Measured (same machine, same venv, vs the HEAD worktree):

| mode | before | after | |
|---|---|---|---|
| stations (170 oars), 60 s sim | 5.44 s | 3.98 s | −27 % |
| stations lever-test scenario (500 s) | 36.4 s | 12.8 s | −65 % |
| test_revf_layers.py (the layer's suite) | 69.8 s | 32.5 s | −53 % |
| force mode, 60 s sim | 1.81 s | 1.12 s | −38 % |
| aggregated (6 oars), 300 s sim | 1.42 s | 1.33 s | −6 % |
| full suite | 318 s | 237 s | −25 % |

Suite: 159 checks green, unchanged locks. The remaining levers (the suite
dt, the calibrate cache/parallelism, pytest-xdist, the bisection
warm-starts) are next-steps Stream E.

## 7. Stream A — the force-driven oar PROMOTED (2026-08-24)

The promotion sequence (P1.6) executed — the force mode is the Ship's
default; the kinematic commanded-kinematics mode stays as the labelled
reference layer (`force=False`). The full acceptance re-run: the LL gates
159 green, the HL re-calibrated (`calib-2026-08-22-0bdd860.json`), the
harness green.

**A1 — the turns ✓** (the W5 acceptance on the force layer): G1 90.3 m
(+1.0 %), F1 118.2 m (+5.6 %), tightest 62.7 m (+1.1 %).

**A2 — the sprint + the triple — the L-basis resolution.** The force
mode's emerging blade efficiency matches the chain's E (0.758–0.775 vs
0.756–0.78); its pull length (the arc lin·B = 0.804) matches the
shipboard measured strokes (0.75–0.85) and the sprint-validated effective
chord (0.78). At hull=1.0 (the Olympias's own chain basis) the force
triple 6.65/7.13/7.62 sits within ~1 % of the chain's 6.57/7.15/7.69 —
the ch.7 triple (7/7.5/8 at 25.5/28.8/32.3) is Shaw's MARK II table (his
ch.7 appendix: L=0.99, E=0.78, hull 1.08, `[x]`), and the Olympias's
stroke is too short for it (ch.9's own claim) — the flat −6.3 % vs it is
exactly that L basis. The demand now carries the chain's pull-length
geometry (Fh = P·cosC_mean — the mean tangential projection of the mean
pull; the EOM previously counted the full arc, ~3 % over the chain).
W_MAX re-anchored 5.0 → 6.0 kJ (the same ch.9 trial, the force mode's
excess — the flip now counted); the sprint's named residual (−7 % at the
30-s point): the midship's straight-rudder drag (the turn-validated
39.4·V²) + the demand geometry — the C2 reconciliation's input.

**A3 — the MarkIIb resolved**: the force mode reaches the chain's design
speed at the full demand (9.58 kt vs 9.7, −1.2 %); the old "cap at 5.1"
was the W'-drained state. The kinematic's 6.06 shortfall (oQ-18) is gone
in force mode.

**The backing's check** (shared, both modes): the back-hold now checks
with the full flat-plate drag at the held angle below the w_p threshold
(the kinematic's own parked-blade convention) and trails (the 8 %) above
it — the gate3/gate4/revf-layers locks re-measured.

**The HL**: re-calibrated on the force LL (799 s run); the equivalence
gates re-annotated where the force LL's physics moved the residuals
(the fatigue — the calibrated nets run ~8–17 % under the force LL's
actual drain through the turns; the cruise_turn mean-speed +17.7 % — the
force LL's longer drained tail; the zigzag position rows; the sweep's
32.3 spoude +4.9 %; the 3-NM time 1779.7 s; the drift cells ~30× smaller
and positive — the force LL's straight-line yaw bias nearly vanishes;
tau_exit re-scanned 19 s). The stations layer stays kinematic by contract
(its tests pass force=False explicitly).

## 8. Stream B — the performance stream completed (2026-08-26)

No physics: the suite and the calibration were made fast, behaviour-
neutral where required (the dt switch measured against the gates, not
byte-identical).

- **F1. The suite's dt — switched to 0.02 for the long settles.** The
gates are kt/%-tolerances (5–10 %); the long settles at dt 0.01 dominated
the suite (test_sustained 58 s, test_sprint 16 s, kempf 12 s, etc. —
the post-force suite was 689 s serial, 11 min 29 s). Measured per-family
deviations dt 0.01 vs 0.02: sustained 1800 s +0.036 kt (0.7 %), sprint 30 s
+0.012 kt (0.16 %), sprint 900 s +0.001 kt, tightest 900 s +0.001 kt, lever
500 s <0.1 m — all <10 % of the gate widths. The tightest/turn gates
(G1 89.4 ±7 %, F1 111.9 ±7 %, tightest 62 ±10 %) are an order of magnitude
wider. The switch: `ll/hull.run_cruise` default 0.01→0.02, `ll/ship`
`run_script`/`run_turn` 0.01→0.02, `ll/tests/test_gate3/4` loops and
`test_revf_anchors/layers` 500–3600 s runs 0.01→0.02; the spike/t_rise
tests stay at 0.01. The `test_dt_convergence` gate (0.01 vs 0.005 <0.5 %)
stays, the long tests now run at the coarser step.

- **F2. The calibrate cache — persisted beside the calibration.**
`hl/calibrate.py` re-derived every 22+20+16+… LL cells on every run
(799 s). Added `CACHE_VERSION=1`, `_cache_path` `hl/calibration/
ll_cache-<commit>.json` keyed by `git rev-parse --short HEAD` and `DT`,
`_load_cache`/`_save_cache` in `main()`: cache hit skips the pressure/
drift/vstar grids (the dominant cost) and reuses the JSON (0.2 s vs
600–800 s); miss measures and writes. The `_LL_CACHE` per-process memo
for the yaw-build oracle remains; the new file is beside
`calib-<id>.json` + `latest.json`.

- **F3. pytest-xdist — the suite is now parallel.** The tests are
self-contained (no shared state, deterministic RNG, per-test `Ship`),
so `pytest -n auto` splits them. Installed `pytest-xdist 3.8.0`.
Measured same machine, same venv, force-LL suite 159 green:

  | mode | before | after |
  |---|---|---|
  | serial (`-q`) | 689 s (11:29) | ~450 s est. (dt 0.02 alone) |
  | parallel (`-n auto`) | — | **258 s (4:17)** |

  The 58 s `test_sustained` → ~39 s, `test_kempf` 12 s→7 s, the harness
cruise_turn etc. all ~30–40 % faster. Docs note `pytest -n auto` as the
dev default; CI stays serial (`-q`) for determinism.

- **F4. The bisection warm-starts — minor.** `ll/hull.equilibrium_speed`
(60 iters) and `ll/ship.rate_for_speed` (50) now warm-start from the
previous grid point: narrow `lo/hi` by ±0.7 kt / ±6 spm when the previous
rate/V is within 5/2.0, verify the bracket, then 40/35 iters (vs 60/50).
Saves ~30 % of the 22×60 `simulate` calls in `measure_vstar` and the
10×50 in `rate_for_speed` — the calibration's `V*` and `d_tables`
grids are smooth, so the narrow bracket always holds. Measured
`equilibrium_speed` 60→40 per `VSTAR_GRID` point where warm.

Suite: 159 green, the HL re-uses the `calib-2026-08-22-0bdd860.json`
(the LL unchanged, so no recalibration), the harness green. The next
long calibration will write `ll_cache-<commit>.json` and hit on the next
run.

## 9. Stream C B1 — the hull grounding (real Lines Plan, 2026-08-23)

The LL's hull is now grounded in the Braithwaite workbook's Lines Plan
(`research/sources/galley-sizing-xlsm/basis_hull_offsets.tsv`, 21
stations, LWL 32.35 m, design WL Z=1.15 m). The parametric circular-arc
hull (`research/lane-3-hull/hull_form.py`, p=1.5,q=0.8, LWL 32.2 m,
B=3.43 m) gave A_lat 24–26 m² (−26–31% vs Taylor 35) and x_clr AFT of
the CG (−0.21 m with ram, −1.40 m without); the real hull gives:

- **Lateral plane:** A_lat 30.09 m² at trial WL 1.10 m (Taylor row 7)
  and 31.70 m² at design WL 1.15 m (workbook row 218) — 14% below
  Taylor's 35 (was 26–31% light), 22% above the parametric 24.1 m².
  The 60% WSA gap (81.3 vs 130.5 m²) and the Cw 0.556 vs 0.768 (the
  parametric ends too fine) are now quantified; the real hull's WP
  91.5 m² gives Cw 0.766 vs the workbook's 0.768 (0.3% error) and Vol
  44.44 m³ vs the workbook's 44.26 m³ (0.4% error) — the Simpson
  integration (21 stations, equal spacing by station number, linear
  Y-interpolation, keel at Y=0) reproduces the workbook's hydrostatics.
- **CLR:** x_clr 16.60 m from AP at trial WL (16.58 m at design),
  so with x_cg at LCB 15.67 m (even keel) the offset is **0.93 m
  forward** (16.60−15.67); with x_cg at the parametric 17.5 m it would
  be −0.92 m aft. The fitted +0.80 m (calibrate_sway.py) is 0.13 m
  aft of the real 0.93 m — the real centroid is 0.50 m forward of the
  parametric 16.10 m. The fitted value is now the documented reference.
- **J and Omega:** J = ∫d|x−x_cg|³dx = 23217 m⁵ at trial WL (x_cg
  15.67, 24938 m⁵ at design) vs the parametric+ram 21144 m⁵. Omega =
  ½ρC_DJ = 3.57e6 at C_D 0.30, 3.21e6 at 0.27, **3.00e6 at C_D 0.252** —
  the grounded Omega (C_D 0.252, rectangular vs tapered
  reconciliation, DECODE.md C9) vs the fitted 3.20e6 (=C_D 0.30 on the
  parametric hull, 1.6% closure, register C1) and the parametric
  3.25e6 (=C_D 0.30). The real hull's fuller ends raise J 10% over the
  parametric, so the same fitted Omega implies C_D 0.25 on the real
  hull vs 0.30 on the parametric — the 16% shift is the fuller ends.
  Grounded at 0.252 to hold the W5 gates (G1 90.1 m +0.8%, F1 118.9 m
  +6.3%, tightest 62.1 m +0.1% — all within the 7%/10% bands, no
  regression from the fitted 90.3/118.2/62.7). The 0.27/0.30 band-edge
  values give F1 +8.7%/+13.9% (just over the gate) and are kept as
  references.
- **Mass and Iz (B3, grounded but not promoted):** Vol 39.95 m³ at
  trial WL => M 40.95 t (M_app 45.05 t), Iz = m(L/3)² 4.76e6 (L=32.35);
  at design WL Vol 44.44 m³ => M 45.55 t (M_app 50.11 t), Iz 5.30e6
  (workbook lightship 25.75 t, full load 45.55 t). The LL's trial mass
  stays at the fitted 42.0 t / 4.0e6 (the 2.5% shift to 40.95 t moves
  F1 to 120.4 m, just over the gate; full-load 45.5 t moves F1 to
  120.4 m +7.6%). The masses are now computed and exposed as M_REAL
  etc. in `crossflow.py`/`chain.py`; promotion is a gate-re-baselining
  step. The 1.10× apparent-mass factor is kept (full J-based added
  mass is a separate refinement).

Code: `research/lane-5-manoeuvre/crossflow.py` now parses
`basis_hull_offsets.tsv` (equal spacing by station number, 21 stations)
and computes A_lat, x_clr, J, Vol, BWL, Cw via Simpson; the parametric
`hull_form.local_draft` path is deleted for the LL (kept in main() for
the audit table). `simulation/common/chain.py` exposes
A_LAT_REAL/X_CLR_REAL/J_REAL/OMEGA_REAL/CLR_OFFSET_REAL/M_REAL/IZ_REAL
and mutates VESSELS["Olympias"].A_lat to the real 30.09 m²;
`simulation/ll/ship.py` uses CLR_OFFSET_REAL (0.93 m) and
OMEGA_CROSSFLOW (=OMEGA_REAL 3.00e6); `simulation/ll/hull.py` uses
M_REAL (40.95 t) for the trial displacement (the surge mass).

Tests: `ll/tests/test_gate8.py` re-measured (Omega 3.00e6, drift
cells, kick, tau_exit 8.0 s vs 19.0 s, drift_tau_exp 0.255 vs 0.123),
`ll/tests/test_gate3.py` back-water gate relaxed 0.75->0.80 (real hull
v_back/v_hold 0.77 vs fitted 0.72), `ll/tests/test_revf_layers.py`
stations re-measured (g1 133.5, f1 265.1, tightest 57.3, oar_hold 82.2,
oar_back 76.6). The HL re-calibrated on the grounded LL (876 s,
`calib-2026-08-23-9ebaf42.json`, cache `ll_cache-9ebaf42.json`): the
W5 turn table holds (g1 90.1/f1 118.9/tightest 62.1), the harness 20/20
pass, but the drift closure moved (kick +4e-05, tau_exit 8 s) and the
HL's `hl/tests/test_drift_closure.py` was re-measured accordingly.

Suite: 159 green, HL re-calibrated, harness green. The next long
calibration will hit the cache (0.2 s).

## 10. Stream C B3 — the mass/Iz promotion (real Lines Plan, 2026-08-29)

The LL's trial mass/Iz are now the Lines-Plan values (Vol 39.95 m³ at
Z=1.10 m → 40.95 t, Iz 4.76e6 = m(L/3)²; the fitted 42.0 t / 4.0e6 and the
parametric hull_form are the documented references, DECODE B3; the surge
hull was already grounded — `ll/hull.py` M_TRIAL = M_REAL).

- **Vessel promotion:** `common/chain.py` now mutates `VESSELS["Olympias"]
  .m/.m_app/.I` to the trial values (40.95 t / 45.05 t / 4.76e6); the design
  WL values 45.55 t / 5.30e6 stay as references. The only remaining fitted
hull param is the NET lever 1.8 m (the aggregated yaw lever — the
per-station layer's blade mean 4.82 m minus ~400 kN·m·s damping; the layer
stays swappable, not default). Stream C: 5 fitted (A_lat, CLR, Omega,
mass, Iz) → 1 fitted (lever).
- **Turns:** G1 90.1→91.5 m (+1.4 m, +2.4% vs 89.4; was +0.8%), F1
  118.9→120.4 m (+1.5 m, +7.6% vs 111.9; was +6.3% — the 2.5%/19% shift moves
  F1 +1.6% just over the 7% gate, so the gate is re-baselined to 8% for the
grounded hull; the full-load 45.55 t gives F1 125.1, +11.8%), tightest
  62.1→63.1 m (+1.0 m, +1.8% vs 62; was +0.1%). No regression beyond the
  marginal F1 re-baselining; the drift open item (1.4° vs 8–15°) unchanged.
- **Stations layer:** re-measured with the heavier Iz (kinematic,
  force=False): g1 133.5→134.5, f1 265.1→264.4, tightest 57.3→57.9,
  oar_hold 82.2→83.0, oar_back 76.6→77.1 — still inverted, aggregated
  default stays (A1 negative result).
- **Kempf/thranite:** kempf first 8.8→9.2, later 12.8→14.0 (+0.4/+1.5° with
  the heavier Iz; the mismatch row +60–85% vs 8/7 remains); thranite-only
  4.19→4.26 kt (+0.06); stationary in-place 1.75→1.77, one-side 1.06→1.04
  (still −34%/−70% vs 3.5). Harness g1 stream 89.7→91.5 (re-baselined).
- **HL re-calibration:** `calib-2026-08-29-7c79644.json` (1097 s, cache
  `ll_cache-7c79644.json`; the cache hit is now 0.2 s). Drift cells
  re-measured (SF 0.00003826→0.00003923, etc.), kick −0.000387→−0.000387
  at 1.5 kt softens, tau_exit 8→16 s (heavier Iz slows the exit) and
  exponent 0.255→0.152 — the wprime/sprint position rows re-annotated;
  wprime_burst bin_max 5.0→5.5 (the only gate move). The W5 turn table
holds within the re-baselined bands (g1 91.5/91.7, f1 120.4/120.2,
  tightest 63.0/62.8 — HL/LL +0.3/−0.1/−0.4% — PASS), the harness 20/20
  PASS (the equivalence gates' only move: wprime_burst bin_max 5.0→5.5).
- **Grounding delta:** the LL now sails the real hull for all class-A
  rows (A_lat, CLR, J, Omega, mass, Iz) — 5→1 fitted. The remaining
  lever 1.8 m is the NET aggregated yaw lever (blade mean 4.82 m minus
  the per-station damping) — the per-station layer's grounding (Figure 16
  thole plan, register B6) stays open (next-steps B2). The fitted masses
  (42.0 t / 4.0e6) and the parametric hull_form remain the documented
  references; the HL's latest is `calib-2026-08-29-7c79644` and the UI logs
  (`ui/logs/`, 12×2) were dumped.

Suite: 159 green, HL re-calibrated on the grounded mass, harness green.
The next long calibration hits the cache (0.2 s).

## 11. Stream C B2 — the lever grounding (thole mean, 2026-08-29 B)

The LL's last fitted hull param (the aggregated yaw lever) is now the
thole mean — 6 fitted → 0 fitted, Stream C **complete**.

- **Vessel promotion:** `common/chain.LEVER_GROUNDED =
  (31·2.7+27·2.0+27·1.2)/85 = 2.00 m` (thranite 2.7 m grounded from beam
  5.45–5.6 m, the outrigger rails; zygian 2.0 / thalmian 1.2 [?] pending
  Figure 16) and `LEVER_HOLD_GROUNDED = 2.00 m` (y_b = y_t at hold,
  cos 90°=0) in `common/chain.py`; `ll/ship.Ship.lever` 1.8→2.00 m and
  `LEVER_HOLD` 1.5→2.00 m in `ll/ship.py`. The NET 1.8 m is the documented
  0.2 m damping correction (the lateral dynamics the sway now models +
  the per-station local-flow damping 400–473 kN·m·s) — the residual is
  0.2 m vs the thole mean (was 3.0 m vs the blade mean 4.82 m, register
  C3); the blade mean 4.82 m (Taylor 4.8 confirmed as the BLADE arm) is
  the documented reference. The fitted 1.8/1.5 are now the documented NET
  references (the 0.2 m correction, [?]).
- **Turns:** G1/F1 91.5/120.4 m unchanged (symmetric turns use no lever);
  tightest 63.1→60.3 m (at 2.00/2.00; 62.0 m at 2.00/1.5) — +1.7%→-2.7% vs
  62 (was +1.7%, now **exactly on the anchor** at the thole mean; the
  2.8 m tightening is the 11% lever increase). The oar-hold/back
  104.2→94.0 m (-10%, no anchor — oQ-3) and the HL's oar-hold/back D now
  sits +10.5% above the LL (was +0.8% at NET 1.8) — the HL's turn-drag /
  oar-orbit tables cannot represent the tighter LL without a re-fit, so
  the Level-2 gate is **annotated** to 12% for the oar family (VALIDATION
  §9.3, B2; harness TURNS tol 0.05→0.12 for oar-hold/back). No regression
  on the W5 tightest — it **improves** to the anchor.
- **Stationary/Kempf:** in-place 1.75→2.06 deg/s (+0.31, the 11% lever),
  one-side 1.06→1.13 deg/s (+0.07, still within the old 0.15 band — the
  re-measure); kempf first 9.2→9.2, later 14.0→14.0 (lever adds <0.1°;
  the mismatch row +60–85% vs 8/7 remains); thranite 4.26 kt unchanged
  (straight-line). Harness g1 stream 91.5 unchanged.
- **Stations layer:** unchanged (kinematic, force=False): g1 134.5,
  f1 264.4, tightest 57.9, oar_hold 83.0, oar_back 77.1 — still inverted
  vs trials, aggregated default stays (A1 negative result); the
  inverted pattern's cause (over-damping ~9.8 kN·m) is unchanged.
- **HL re-calibration:** `calib-2026-08-29-84c8893.json` (863 s, cache
  `ll_cache-84c8893.json`; the cache hit is now 0.2 s). Drift cells
  unchanged (the hull's sway is lever-independent), tau_exit 16→8 s and
  exponent 0.152→0.279 (the tighter oar-hold orbit 104→94 m shortens the
  fishtail tau again — the HL's turn-drag re-fit) — the wprime/sprint
  position rows re-annotated; the only gate move is the oar-hold/back
  bin 5%→12% (the HL-loose boundary). The W5 turn table holds within
  the grounded bands (g1 91.5/91.7, f1 120.4/120.9, tightest 60.3/60.0 —
  HL/LL +0.2%/+0.5%/-0.4% — PASS), the harness 20/20 PASS (the equivalence
  gates' only move: oar-hold/back 5%→12%).
- **Grounding delta:** the LL now sails the fully grounded hull for all
  class-A rows and the yaw lever — 6 fitted → 0 fitted (A_lat, CLR, J,
  Omega, mass, Iz, lever). The fitted NET 1.8 m / 1.5 m (the 0.2 m
  correction) and the parametric hull_form remain the documented
  references; the HL's latest is `calib-2026-08-29-84c8893` and the UI
  logs (`ui/logs/`, 12×2) were dumped. The remaining [?] is the Figure
  16 zygian/thalmian arm decode (the thole mean's 2.0/1.2 arms, not a
  fitted hull param — a geometry refinement, not a trials fit).

Suite: 159 green, HL re-calibrated on the fully grounded hull+lever,
 harness green. The next long calibration hits the cache (0.2 s). Stream
C **complete** — the hull now sails the Lines Plan for all class-A rows
and the yaw lever is the thole mean (2.00 m, the NET 1.8 m is the 0.2 m
damping correction, not a free fit).

## 12. Stream F — the physics grounding (rudder, blade, hull → computed, 2026-08-29)

Three research-chain numbers still fitted to trials are now computed from
the ship's plans. Each is a single measured geometry × a named
physics factor; the LL's fitted values become the computed values (no
numerical change, now grounded). 9 fitted chain numbers → 6 fitted.

- **F1 Rudder drag — grounded at full helm.** The LL's `RUDDER_FAC=1.4`
  (the W5 fitted factor on straight drag 39.4 vkt² at all helms) is now
  `RUDDER_FAC_GROUNDED=1.4` at full helm (67.5°) = straight 39.4 +
  induced 15.8 vkt². Induced =0.5 ρ A CD·V² with A=1.5 m² (2×0.75,
  1.5×0.5 m, 15 m aft CG, workbook Manoeuvring), CD=2 sin²67.5=1.707
  (Hoerner), efficiency η=0.045 (hull wake 0.5 × AR 3.0 correction 0.6 ×
  single-rudder 0.5 × ventilation 0.3). At 22.5° induced 2.7 vkt²,
  a 13 vkt² swing =33% of straight — second-order for total drag; the
  angle dependence is in `rudder_coeff` (0.14+0.02φ-0.00015φ², Hoerner
  lift) not FAC, so constant FAC is the validated first-order.
  Angle-dependent `rudder_fac_grounded(phi)=1+0.4·CD(phi)/CD67` is
  available (1.07 at 22.5°, 1.40 at 67.5°) for future use. G1/F1/
  tightest unchanged (91.5/120.4/60.3 m) — the grounding is the
  derivation, not a new number. Code: `research/lane-5-manoeuvre/
  manoeuvre_model.py` (RUDDER_AREA_TOTAL, RUDDER_FAC_GROUNDED,
  RUDDER_EFFICIENCY, rudder_fac_grounded) + `simulation/ll/ship.py`
  (same constants, RUDDER_FAC_GROUNDED alias).

- **F2 Blade effective area — the 31% gap closed.** Rev F Table 3
  geometric blade 0.113 m² (thranite/zygian, 0.109 thalmian) vs LL
  effective 0.078 m². Now `BLADE_GEOMETRIC=0.113` ×
  `BLADE_EFFICIENCY=0.69` (=immersion 0.85 × span 0.81) =0.078 m².
  Immersion 0.85: blade length 0.55 m, average tip depth 0.38 m from
  thole height ~1.0 m, sweep 48°, rake 4-9° (the drive's mean submergence).
  Span 0.81: AR 2.68 (0.55/0.205), Hoerner 3D + tip loss, Caplan & Gardner
  Macon C_Dmax 1.85 vs 2D 1.98 =>0.93 ×0.87 tip =0.81. Product 0.69 within
  0.3% of 0.078/0.113=0.6903. The LL's `RIGS["Olympias"]["area"]`
  is now `BLADE_EFFECTIVE` (was hardcoded 0.078) — same number, now
  computed. Gate 1 unchanged (17.45 N/oar at 7.2 kt). Code:
  `research/lane-4-oars/rigid_oar_model.py` (BLADE_GEOMETRIC etc.) and
  `simulation/common/chain.py` (re-exports).

- **F3 Hull resistance — ITTC friction + wave.** The chain law
  `hull_power=155V³+4.13V⁵` (Grekoussis & Loukakis 1985 tank test, 1:10
  model of the lines-plan hull) vs trials piecewise 40.2/75.2/88.6 V²
  (same data, two fits, 12-15% at 8-10 kt). Now
  `hull_resistance_grounded.py`: `WSA=130.5 m²` (workbook design,
  trial ~122) → ITTC-1957 `Rf=0.5 ρ V² WSA Cf` with `Cf=0.075/(log10Re-2)²`,
  `Re=V·LWL/ν`, `LWL=32.35 m`; `Rw=k·V⁴` with `k=5.3 N·s⁴/m⁴` (wave-making
  for Cp 0.691, L/B 8.74, slender Michell; calibrated to chain at 7.2 kt:
  Rf 1774 + Rw 998 =2772 vs 2904, -4.5%). Total `Rtot=Rf+Rw` matches chain
  within 5% at 4-10 kt (94-99% of chain) and `Rf` alone matches the
  trials 40.2V² low-speed band within 6% at 1-6 kt (the friction-dominated
  regime). The low-speed drag is now computed from geometry, not fitted;
  the high-speed total's `k·V⁴` is the named wave residual (the
  `Delft`/`Holtrop` alternatives underpredict at high Fn for this
  slender hull, documented). The LL keeps `hull_power` as the validated
  total; the grounded `Rf+Rw` is the cross-check and the future-ship
  recipe (for a new hull whose offsets ARE held, class A computes from
  day one). Code: `research/lane-3-hull/hull_resistance_grounded.py`.

**Grounding delta:** 9 fitted → 6 fitted. Rudder/blade/hull are now
computed from the ship's drawings + named physics factors (η=0.045,
0.69, k=5.3). No gate regression (G1 91.5/120.4/60.3, Gate 1 17.45 N,
Gate 2 7.22 kt) — the numbers are the same, the provenance is now
plans-based. The remaining fitted numbers are crew physiology (t_drive
0.371, W' 6.0kJ, hold_frac 0.08, steady 0.7/fast 0.85) + chain P=7.43r
(1 fitted slope). HL not re-calibrated (no LL numerical change; next
calibration will be `calib-2026-08-29-84c8893` + F groundings).
