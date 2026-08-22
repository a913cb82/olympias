# Next steps from the Rev F comparison

Planned work from `comparison-with-ll.md` (the deep-dive against
Braithwaite's report). Three baskets: **A — LL realism upgrades** (physics
the report has and we lack), **B — differing choices to investigate** (which
of our simplifications actually matter), **C — new data from the report →
new validation** (anchors we did not have before). The standing rule for
every item: the gates are the posterior — nothing is promoted or changed
without re-running the acceptance (VALIDATION §0-8) and nothing is tuned
silently (the oQ-18 discipline). Items are ordered by expected impact.

## A. LL realism improvements

**A1. Per-station oar model with local flow (unpack the 4.8 m lever).
— the layer built; the decomposition CORRECTED; the layer's net pattern
inverted vs the trials (the over-damping, named) — the follow-up's the
grounding + the damping's verification.**
The layer's built: `ll/stations.py` + the ship's `stations=True` mode —
170 oars at their stations (interscalmium 0.888, the thole arms grounded
in the outrigger beam 2.7/2.1/1.5 m [?], the short oars at the bow/stern
ends per Rev F Table 3), each blade's flow from the ship's (u, v, r) at
its station, the yaw moment from the per-oar sums at the BLADE positions.
The measured verdicts (the realism direction's CONFIRMED, the
completion's open):
- the yaw moment's arm is the blade's position (r_blade x F — the oar
  and the rower are internal to the hull): the mean blade arm's **4.82 m
  — the Taylor 4.8 IS the blade's arm**, and the LL's sway-calibrated
  1.8 m is the NET (blade arm − the oars' local-flow damping, measured
  ~400 kN m s at the g1 settle). The register C3's earlier 'physical
  athwartships arm 1.8' reading was the wrong decomposition — corrected.
- BUT the layer's turn pattern is INVERTED vs the trials (measured on
  the harness's own cells at the current sway set): the helm turns
  WIDER (g1 90.1 → 128.0, f1 118.0 → 232.1) while the oar turns come
  out TIGHTER (tightest 62.5 → 57.4, oar-hold 102.9 → 81.4, oar-back
  102.9 → 78.7). The investigation (per the 'realism making results
  worse = investigate' rule):
  - a REAL BUG found and fixed: the held/back-hold stations' tuples
    carried zero blade positions — the brake's moment (−y_b·br) was
    silently dropped (minor in effect: the brake's the small term);
  - the re-tuning check: no (Ω, clr) resolves the inversion — the helm
    turns'd need Ω DOWN (the explicit local-flow damping ~9.8 kN·m at
    the settles — ~73 % of the 22.5°-helm rudder torque — eats the
    small-helm turns) while the oar turns'd need it UP (the rowing
    side's 4.8-arm counter's under-absorbed — the lateral's too weak,
    the SAME direction as the open drift item: the model's 1.4° vs the
    trials' 8-15°);
  - the damping's form matches the report's per-oar formula (his
    Vb = Lo·ω·cosθ and the water's (u, v, r) at the blade — the same
    local flow), so the mechanism's not a transcription error; its
    MAGNITUDE's the open question — the outside blades bite harder,
    and the aggregated's net-arms (1.8/1.5) + the calibrated Ω had
    absorbed that share.
The follow-ups (what the layer needs to become a clean win): the
station decode (B6 — Figure 16's plan pins the arms), the lateral
model's strengthening (A_lat/clr — the drift item's own fix — would
absorb the oar turns' counter), and the sway re-calibration with the
layer as the default (the lever's elimination is the fitting
reduction).

**A2. The stroke phase structure. — DONE (the negative result)**
The trapezoidal drive profile's built (`ll/oar.py profile="trap"` — the
ramps at the catch/finish, the sweep conserved) and measured at the
cruise point (7.2 kt, 28.8 spm): with the report's in-water fraction 0.39
(0.72 s) the mean thrust's **−35.5 N vs the chain's +17.5 N** — the same
sweep over a longer in-water time forces a lower mean ω, and the blade
cannot outrun the water during the ramps (the vn turns positive — the
blade dragged forward). The two measurements are jointly incompatible
with ANY trapezoid: the effective-pull (the chain's 0.43 s — the force's
equivalent rectangle) and the kinematic in-water (the report's 0.7 s)
imply a PEAKED mid-stroke ω(t) (~1.5-2× the mean) whose shape the
available data does not determine (the Table 9.6's the effective time,
not the ω(t) shape). The constant-ω + the effective-pull stays the
validated kinematics; the negative result's locked
(`ll/tests/test_revf_layers.py`). The shape's measurement (a force-trace
or blade-video record) would be the unlock — not in our sources.

**A3. The rudder as an aerofoil (low priority). — DONE (blocked, named)**
The report's Figure 12 shows the rudder's location diagrammatically with
NO printed dimensions (the area, section, stock position); the trials'
rudder plans are not in our sources. The aerofoil upgrade is not
implementable from the report — the Taylor empirical model stays
gate-passing. The blocker's named; the item's closed unless the rudder
plans surface.

## B. Differing choices — investigate the impact

**B1. Scalar added mass vs the mass matrix. — DONE (the measured no-op)**
The labelled option's built (`Ship(mass_matrix=True)` — the 2×2 sway-yaw
solve with the semi-empirical added masses, add_v 0.9 / add_r 0.2 /
add_c 0.1 [?]) and measured: the g1's D shifts +2.3 % and the drift
−1.5° → −1.4° — the couplings act on the TRANSIENTS, the drift is a
steady-state balance. The trial-measured scalar m_app (1.10×) stays;
the option's locked (`test_mass_matrix_noop`).

**B2. Flat-plate normal law vs the lift+drag polars. — DONE (the lift is
NOT negligible — the labelled polar variant's built)**
The report's polars decoded from the docx's OMML: **C_D = 2·sin²α,
C_L = sin(2α)**. Measured at our stroke: the angles of attack run 54-58°
(the mean 58°, median 54°), where C_L ≈ 0.90-0.95 — the lift is ~55 % of
the total force — and the polar's normal coefficient (2 sin α = 1.62) is
**1.37× the flat plate's** (1.8 sin²α = 1.19) at the median angle. The
labelled variant (`BLADE_POLAR` — the normal-component form) gives +40 %
mean thrust at 7.2 kt — the flat-plate's a drag-only approximation whose
shortfall the calibrated C_N·A product absorbs (the A5 register's family:
the physical blade's 0.113 m² + the polars would produce ~2× the chain's
force). The full vector form (the lift ⊥ flow, the drag ∥ flow — the
report's Fb(x)/Fb(y)) is the noted refinement. Locked
(`test_polar_variant_thrust`).

**B3. Kinematic vs force control — a force-anchor cross-check. — DONE
(the structure decoded, the values blocked)**
The report's force curve's structure recovered from the OMML: the target
blade moment's a PARABOLA of the relative oar angle — maximum moment ·
(1 − θ_rel²/(catchFactor·range/2)²) — with the catchFactor's continuity
(1/(1 − moment_at_catch/maximum)) and the max moment LINEAR in the ship
speed (the Hill-like strain-rate factor). The quantitative intercept/
gradient live only in the raster Figure 10 (image12.png — no text layer;
the OCR stack's not installed) — the cross-check's blocked on that decode
[?]. The forms differ (his speed-dependent max vs our flat Fh_BURST 330 N
mean + the W′-limited); our anchors're trial-derived — a cross-check only,
the measured kinematics stay the ceiling.

**B4. The turn model's drag law — a measured inconsistency. — DONE (the
measured no-op — the concern dissolves)**
The labelled option's built (`Ship(drag_law=...)` — taylor/trials/chain)
and measured on the harness's five cells: the D's shift ≤ 1.1 % across
the laws and the tightest's t_360's unchanged (101 s either way). The
reason: the turns run BELOW 6.7 kt, where the taylor band set and the
trials' raw piecewise agree on 40.2v² (the collapsed −1560/−2640 offsets
only matter above 6.7 kt — the turns never go there), and the chain law's
drag at the turn speeds is a small share (the rudder's drag dominates the
turn's balance). The t_360's −23 % is NOT the drag law's — the item stays
open with this lever measured and excluded. Locked (`test_drag_law_noop`).

**B5. The rower's moving mass (expected: negligible, to be documented).
— DONE (documented)**
The argument's confirmed by the report's own equations: his F_sys =
thole's + footplate's reactions with the handle/footplate forces internal
to the hull+crew rigid body (his note: "the ship as a rigid body including
the mass of the oars and oarsmen") — the net hull force is the blade's
alone, and the moving-mass inertial loads (the 51.02 kg, A = 0.547)
transfer through the footplate only as internal loads. They matter for
the local loads and the pitch (no pitch DOF) — negligible for the
surge/sway/yaw. The register D10's already got the anthropometrics; the
verdict's recorded, no code.

**B6. Aggregated tiers vs per-oar.** Overlaps A1 — the per-station flow
and the short oars at the extremes. No separate work.

## C. New data from the report → new validation

**C1. The stationary-turn anchor (Ref (1) p30, via the report). — DONE**
The scenario's built (both readings: one side's Z+T ahead vs the other's
back — the in-place turn — and the one-side ahead-vs-rest reading) and
locked in `ll/tests/test_revf_anchors.py`. The measured verdicts: the
in-place turn settles **2.32°/s** (−34 % vs 3.5) and the one-side reading
**1.06°/s** (−70 %). The model is now too SLOW at low-speed partial crew —
the SECOND direction of the turn-speed family (the t_360 item is the
model too FAST at full crew). Recorded as the register C7 row + the
VALIDATION §11.2/§11.3 rows; no gate (it would fail) — the item joins the
turn-speed family's ledger as the envelope datum.

**C2. The zig-zag overshoots (p30). — DONE** A true Kempf zig-zag (helm
22.5, flips at the ±20° crossings — the harness's zigzag script is a
fixed-time sequence, NOT the trial's manoeuvre) built and locked in
`ll/tests/test_revf_anchors.py`. The measured verdict: the LL overshoots
**11.0° then 12.8–13.0°** vs the trials' 8°/7° (+60–85 %) — the
fishtail's reversal carries ~5–6° too far (the yaw momentum decays too
slowly — the t_360 family's dynamics). A NEW honest row (VALIDATION
§11.2 T10 + §11.3 item 1b, register C8); no gate (it would fail).

**C3. The rudder-drag constant cross-check. — DONE** Measured +8–9 % at
5–8 kt — an independent confirmation of the 39.4/kt² constant. Recorded
in the register C3 row + locked in `test_revf_anchors.py` (the 0–12 %
band).

**C4. The hull-resistance piecewise (p74). — DONE** The raw trials bands
(40.2v² / 75.2v² − 1560 / 88.6v² − 2640) now quoted in the register B2
row, with Rev F's whole-range cubic (51.4v³ − 76v² + 223v) and the
measured 10–20 % gap vs the chain law. The band set's collapsed offsets
are the B4 investigation's input (see B4).

**C5. The oar table (Table 3). — DONE** The blade area 0.113 m² is now
the register A5 row's source-side anchor (the chain's 0.078 = 1.45×
smaller); the MOI 30 kg m² recorded in the new A9 row (the Table 3.1
A-family value in the wild — the A/B anomaly is source-side); the short-
oar geometry, the CP distances and the rake are in the A9 row for A1.

**C6. The stroke-time budget (p28). — DONE** The in-water fraction
0.39 vs the chain's effective-pull 0.21 at 28.8 spm is recorded in the
register D10 row; the handle-arc cross-check (our 0.80 m vs his 0.7
measured / 1.0 achievable) is consistent. Feeds A2.

**C7. The thranite-only speed (p50). — DONE** The LL's 62-oar (thranites
both sides) equilibrium at 33.3 spm: **4.31 kt** (+31 % vs the reported
3.3 kt). The record's context (which crew/sides/rate) is unresolved [?] —
recorded in the register D10 row as a loose cross-check only, no gate.

## Kept as-is (choices that stay unless a gate says otherwise)

- The kinematic-control philosophy (measured kinematics are the truth the
  gates are built on; his force-curve school is the cross-check, not the
  replacement) — with the follow-on: the force-driven-oar plan (Plan 1, §D)
  revisits it with the measured kinematics as the force layer's acceptance
  gates rather than its inputs.
- The chain's hull-power law (155V³ + 4.13V⁵, V in m/s) — the power chain
  closes on it; his raw tow cubic (10-20 % below) stays a register
  cross-check.
- The report's unvalidated status: nothing is promoted to an anchor
  without the source's context being checked against the trials report
  itself (his Ref (1), which we still do not hold).

## D. The fitted-constant elimination program (port-readiness)

From the trial-fitted audit (`simulation/docs/CALIBRATION.md`): with the
full ship design in hand, the fitted set shrinks to the human layer (which
carries as-is) plus two elimination targets — the crew timing (Plan 1) and
the hull's rotational resistance (Plan 2). The standing rule for both: the
gates are the posterior; the measured values become validation references,
never inputs; nothing is promoted without the acceptance re-run (VALIDATION
§0–8) and the HL re-calibration.

**Plan 1 — the force-driven oar (eliminates T_DRIVE + t_drive(44.5) +
t_rise; challenges hold_frac's grip part + the thalmian factor).**

Goal: the stroke (drive time, sweep, the ω profile) emerges from the
rower's applied force + the oar's inertia + the blade's water force; the
measured kinematics (Table 9.6's 0.43 s, the sweep) become the gates, not
the inputs. What exists: the Gate-5 companion (`test_gate5.py::
test_force_driven`) — I·θ̈ = −Fh·lin − Fn·l_cp with a constant demand
Fh = 7.43·r reproduces the drive time essentially exactly (0.43 s, gate
±15 %); its key physical insight: the catch flip happens in the air, so the
blade enters at ~full drive speed. All inputs exist: RIGS geometry, Table
3.1 MITs, the flat-plate blade law, P = 7.43·r, the W′/pressure/tier
scaling, the feather clamp. The force-profile shape: the Rev F B3 structure
(parabolic target moment, catchFactor continuity, max moment linear in
ship speed) — the intercept/gradient live only in raster Figure 10 (decode
blocked), so the start is the minimum-shape assumption (the constant
demand), the B3 shape flagged `[?]` until the decode.

Steps: (1) the force model — Fh(θ, θ̇ | r, W_frac, tier), research side;
(2) `ll/oar.py` force mode — the oar EOM with the catch flip, the blade
entry/exit, the recovery phase (the feather drag — a new model, no anchor,
flagged); (3) the single-oar validation — the emergent drive time at the 4
Table 9.6 points (tighten the ±15 % toward ±5 %), the emergent sweep, the
mean handle force (223.5/208 N), the catch spike vs Gate 5 (t_rise now
emerges from the blade's entry at full ω); (4) the crew integration — the
force mode inside TierCrew/SideCrew, hold/back as grip-force states (the
held blade's drag is the flat-plate law on a stationary blade; the grip
strength stays the human constant); (5) the sprint gate — 8.2–8.3 kt @
44.5 spm / 130 oars with NO t_drive(44.5); (6) measure the emergent
rate→power curve — the T1 open item's named suspect (the blade/kinematics
chain): does the force layer fix the ch.7 triple?; (7) retire the schedule
(T_DRIVE becomes anchors), re-run the gates, re-calibrate the HL, update
CALIBRATION.md rows 1/2/4/12.

Risks: the profile shape (Figure 10 block); the catch flip at low ship
speed (the start-from-rest — the flip may not complete before blade
re-entry; the fh_max clamp interacts); the numerical stiffness at catch
(the companion's dt 5e-5 — the force layer must substep or go implicit
inside the ship's dt 0.05); the recovery-phase model is unanchored.

**Plan 2 — the manoeuvring hydrodynamics: Ω (and clr) from the hull form.**

Goal: the fitted Ω 3.2e6 and clr_offset 0.8 are replaced by computed
cross-flow-drag quantities from the hull form — the turn closure needs no
trials, and the port gains its "from the lines" path. Physics: Ω·ω² is the
lumped yaw moment of the hull's cross-flow drag — the local lateral
velocity ω·x at station x gives M = ½ρ·ω|ω|·∫C_D(x)·d(x)·|x|³ dx, so
Ω = ½ρ∫C_D·d·|x|³ dx; the same integral's centroid is the CLR (→
clr_offset); the sway-force integral is the lateral resistance (the drift
family). The A1 measured damping (~400 kN·m·s at the g1 settle) is the
same physics at the blade level — the two decompositions must reconcile.
What exists: the parametric circular-arc hull (`research/lane-3-hull/
hull_form.py` — LWL 32.2 m, B_wl 3.43 m, T 1.1 m, volume-calibrated to the
BMT anchors; `local_draft(x)` is the integrand's geometry);
`clr_rotation.py`'s x ∈ [0.5, 2.0] m band; the fitted set to close against.

Steps: (1) the cross-flow module (`research/lane-5-manoeuvre/crossflow.py`)
— Ω(x_rot, C_D) and the CLR from the hull form, C_D from the circular-arc
sections (the 2D cylinder-in-crossflow band ~1.0–2.0, the arc depth, the
ram/keel addenda), the C_D band reported rather than a single number; (2)
the audit closure — invert the fitted Ω to its implied effective C_D:
inside the physical band = the fit was physics all along (register C1's
units caveat resolved); outside = the CLR-restoring decomposition absorbs
something else — investigate; (3) the rotation-point cross-check vs
`clr_rotation.py`'s band; (4) the LL swap + the turn gates (G1/F1/tightest/
t_360) — the fitted set becomes the reference; a miss names its suspects
(C_D, the draft distribution, the sway decomposition), recorded, not
retuned; (5) m_app as the sibling — potential-flow added mass from the
same hull form (CALIBRATION row 8's elimination); (6) the port deliverable
— `manoeuvre_hydro.py`: hull form in, (Ω, clr, m_app, lateral damping)
out, the Olympias validation its test case.

Risks: C_D's ±30 % band vs the gate widths; the LL's Ω folds in the CLR
restoring moment — the swap must not double-count it; the t_360 / Rev F
stationary-turn family is the same physics, so the computation may move
either direction (measure, don't assume); the hull form is parametric, not
the true offsets (the Wolfson archive's Plan 7 / Table of Hull Offsets and
the Eliav CAD are the upgrade paths — flagged `[?]` until then).

Verdict (executed 2026-08-22): **Ω ELIMINATED — the audit closed.**
`crossflow.py` computes Ω = ½ρ·C_D·J (the drag-crisis C_D = 0.3,
literature, Re ~ 1e6; the parametric hull + the ram): the fitted 3.2e6
equals the computation at 1.6 % — the register C1 units caveat resolves
(Ω IS the quadratic cross-flow yaw moment). The computed Ω is now the LL
default; the turn gates hold (g1 +0.9 %, f1 +5.6 %, tightest +1.0 % — no
regression vs the fitted 3.2e6's +0.4/+5.1/+0.4 %), the suite is green
(152 checks), the HL re-calibrated (calib-2026-08-22-ea571f9; the
tau_exit re-scan 19 → 8 s, the zig-zag position rows re-annotated 0.465).
Two honest negatives recorded: (a) the CONSISTENT single-C_D cross-flow
model (replacing the f_hull/q_hull/Ω trio with one distribution) FAILED
the gates — the turns widen +45–85 %: the quadratic form's net lateral
force is ~13× weaker than the Taylor f_hull at the LL's drift angles, so
the drift balloons to ~20–25° (the named suspect: the C_D split between
the force and the moment, or the real ends); the consistent mode stays
available as `sway="crossflow"` but OFF. (b) The CLR is NOT reproduced:
the computed lateral-plane centroid is AFT of the c.g. (−0.2…−1.4 m vs
the fitted +0.8 forward) — the parametric ends + the ram's assumed plane
are the gap; the real lines (Wolfson/Eliav) are the named path. A_lat:
the parametric hull under-predicts Taylor's 35 m² by 26–31 % — same
cause. The m_app sibling (potential-flow added mass) untouched.

Order and interaction: Plan 2 first (self-contained — the turn physics
stays put while measuring), then Plan 1 (the philosophy layer) against the
new baseline; the full acceptance and the HL calibration re-run after
each. The two interact through the turns (per-oar yaw moments vs the
hull's yaw resistance) — the Plan-2 verdicts are Plan 1's starting
baseline.
