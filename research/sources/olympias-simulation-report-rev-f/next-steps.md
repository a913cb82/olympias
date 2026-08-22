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

**STATUS (2026-08): P1.1–P1.5 landed as a labelled layer** — `ll/oar.py`
force mode + `Ship(force=True)`, default OFF. The results: the emerging
drive times at the four Table 9.6 points 1.005/0.972/0.925/0.932 (the
Olympias pair ±5 %; the MarkIIb −7 %/−7 % — the A5 family); the emerging
thrust at 7.2 kt 0.976 × the kinematic; the sprint 7.72 kt vs the
kinematic's 7.45 (the trials 8.2–8.3 — the deficit reduced, not closed);
the cruise triple 6.55/7.03/7.50 kt — a FLAT −6.3 % (the kinematic's
deficit grows with rate — the T1 tension's shape changed, its size not —
the named suspects stand); the rest start 4.06 kt @ 10 s with the peak
handle force at the demand (the catch deadspot is gone — the oQ-13
ceiling's physical fix). The drive's key discovery: it SELF-BALANCES — the
oar settles where the blade drag absorbs the demand
(vn = −√(Fh·lin/(k·l_cp))), so the emerging stroke is the measured stroke
without a fitted timing schedule. P1.6 (the promotion — the full
acceptance, the turns, the HL re-calibration) and P1.7 (the docs) pending;
the MarkIIb force-mode equilibrium ~5 kt at 46.3 spm is the A5 gap
quantified from the force side (the demand caps the blade force — the
area fix alone can't bridge it).

Steps (phases; each ends at a gate, the full acceptance re-runs at P1.6):

- **P1.1 the force model** (research side): ✅ DONE — the minimum-shape constant demand (the B3 shape stays `[?]` — Figure 10).  Fh(θ, θ̇ | r, W_frac, tier) —
  the profile's work per stroke must equal the chain's (the mean pull
  7.43·r), so the emergent cycle-mean power reproduces P = 7.43·r by
  construction; the W′/pressure scaling from rower.py; the tier factors
  become force ceilings (the thalmian head-room EMERGES from the short-oar
  kinematics — measure, don't apply).
- **P1.2 the oar EOM layer** (`ll/oar.py` force mode): ✅ DONE — `ll/oar.py` force mode: the flip (pinned, the spike over t_rise), the drive (substeps at 1e-3), the recovery kinematic `[?]`.  the drive with the
  catch flip, the blade entry/exit conditions, the recovery phase (the
  feather clamp + the water exit — a new model, no anchor, flagged `[?]`;
  the kinematic recovery stays until the force recovery is measured);
  numerical: the catch's stiffness (the companion's dt 5e-5) — substep or
  implicit inside the ship's dt 0.05.
- **P1.3 the single-oar validation** (the Gate-5 upgrade): ✅ DONE — `ll/tests/test_force_drive.py` (F1-1..F1-7): the emerging drive times 1.005/0.972/0.925/0.932 × Table 9.6 (the Olympias pair ±5 %), the thrust 0.976, the work conservation, the deadspot-free start.  the emergent
  drive time at the 4 Table 9.6 points (tighten the ±15 % toward ±5 %),
  the emergent sweep (the rig's sweep), the mean handle force
  (223.5/208 N), the catch spikes (t_rise emerges — check vs Gate 5's
  116/215/156 N, ±2 %).
- **P1.4 the crew integration** (TierCrew/SideCrew): ✅ DONE — TierCrew/SideCrew/Ship force plumbing; hold/back states work (the backing force branch has the back-hold degeneracy); the thalmian factor scales the DEMAND at the source.  the force mode per
  tier, the pipe keeps the crew in phase; hold/back as grip-force states
  (the held blade's drag is the flat-plate law on a stationary blade; the
  grip strength stays the human constant); the start-from-rest — the
  catch flip at low V (the flip may not complete before blade re-entry;
  the fh_max clamp interacts) — measured.
- **P1.5 the ship gates**: 🟡 MEASURED, NOT YET GATED vs the trials — the sprint 7.72 kt (30 s) vs the trials 8.2–8.3 (the deficit reduced, not closed — the T1 family); the triple 6.55/7.03/7.50 (flat −6.3 %); the start 4.06 kt @ 10 s. Locked in `ll/tests/test_force_ship.py` (F2-1..F2-3) as the layer's own gates; the trials' acceptance at P1.6.  the sprint — 8.2–8.3 kt @ 44.5 spm / 130 oars
  with NO t_drive(44.5); the cruise pair (the hull=1.0 points); the T1
  measurement — the emergent rate→power curve vs the ch.7 triple (the
  named suspect: does the force layer fix the flatness? test_triple_lock
  moves or stays — no silent re-lock).
- **P1.6 the promotion**: ⬜ PENDING — the default flip, the turns (W5), the full acceptance, the HL re-calibration.  T_DRIVE/CALIBRATED_T_DRIVE become anchors
  (validation-only), the force mode becomes the default (labelled — the
  kinematic mode stays as the reference); the full acceptance — the LL
  gates, the HL re-calibration (calibrate.py), the harness, the annotated
  rows re-measured.
- **P1.7 the docs**: 🟡 PARTLY DONE — VALIDATION §5a/§8/§11-T1, CALIBRATION rows 1–2, this status block; the rest with P1.6.  CALIBRATION.md rows 1/2/4/12 statuses (t_drive
  eliminated; hold_frac/thalmian challenged), VALIDATION.md §2/§4/§5,
  next-steps.

### The P1.6 blockers — the single-default gate

The goal is ONE default we trust, not more optionality. The force layer
stays labelled-OFF until these are resolved (each: what it is, why it
blocks, the named suspects, the path):

1. **The turns (W5) are unmeasured in force mode — the hard gate.** The
   turn family (G1 89.4 m / F1 111.9 m / tightest 62 m — ±7 %/±7 %/±10 %)
   has only ever run on the kinematic oar; in force mode the turn speeds
   are emergent (the speed-holding rates shift), so the diameters will
   move — the question is how far. Prerequisite, not judgment: run the
   acceptance, see the numbers. (The t_360 −23 % open item is the same
   physics family and stays open either way.)
2. **The sprint — 7.72 kt vs the trials' 8.2–8.3 (−6 %).** The kinematic
   default already misses this (7.45 — the documented "LL's sprint
   deficit", the T1 family); the force layer improves it, not closes it.
   Suspects in order: the **thalmian head-room factor's `[?]` rate-shape**
   (the fitted 0.6 at 44.5 spm — the class-C row) and the **blade law's
   emergent efficiency** (the A5/E family — the flat-plate C_N·A is the
   chain's calibrated product, and the force balance exposes it). The
   candidate test: the B2 polar physics (the real blade's normal
   coefficient 1.37× the flat plate — a physics correction, not a knob).
3. **The cruise triple — the rate→power curve sits flat −6.3 % below the
   ch.7 reference.** The force-mode equilibrium 6.55/7.03/7.50 kt at
   25.5/28.8/32.3 spm (hull=1.08) vs the chain's 7/7.5/8. Two things are
   true at once: the **Table 9.6 acceptance pair holds** in force mode
   (7.2 kt @ 28.8 — the actual acceptance), and the Mark-II-reference
   triple is open either way (the kinematic's own lock is
   −2.5/−4.6/−6.1). The force layer changes the deficit's SHAPE (flat
   instead of growing) but not its size. The triple lock re-bases to the
   force values with the deficit's decomposition named (the Olympias
   rig's thrust share vs the Mark II's 55.6° sweep, plus the E family).
4. **The MarkIIb — the force mode caps at ~5.1 kt where the chain says
   9.7.** The demand force CAPS the blade force, so the measured 0.472 s
   drive and the chain's P = 344 N at 46.3 spm are mutually inconsistent
   at the 0.078 m² blade (the measured stroke implies the rowers pulled
   only ~150 N mean). The A5 as-designed fix (area 1.3× + slip 1.2) does
   NOT bridge it in force mode — the equilibrium stays ~5.1. The MarkIIb's
   LL gates break. Needs a decision: re-examine the MarkIIb's chain
   inputs (P/L/E at the sprint rate — the A5 register's tension, now
   force-side-quantified) or re-base its acceptance on the force physics.
5. **The mechanics of the switch** (not physics, but real): the triple
   lock and the G4 sprint tests lock the KINEMATIC values — they re-base;
   the HL re-calibration + the harness equivalence re-measurement (the
   Plan-2 loop, ~15 min); the carry-overs that stay fitted either way
   (class C, flagged): the flip's t_rise (the G5 convention), the
   kinematic recovery `[?]`, HOLD_FRAC's grip, the thalmian shape, and
   the Table 3.2 couple anchor now sits −4.5 % from the constant demand
   (the B3 profile shape `[?]` — the undecoded Figure 10 — is the named
   closing path).

Order of work: **measure the turns first** (an hour — the hard gate might
already fail, which changes everything), then **attack the sprint/triple
suspects** (the thalmian shape test + the B2 polar — physics, not
 tuning), then **decide the MarkIIb**, then promote. The force layer's
reason to exist — the timing schedule eliminated (the class-C row
retired), the physical start — does not change if the promotion waits
for the numbers.

Risks: the profile shape (Figure 10 block — the minimum-shape start);
the catch flip at low ship speed (the start-from-rest); the numerical
stiffness at catch; the recovery-phase model is unanchored; the T1
interaction — the emergent rate→power may move the ch.7 triple either
way (the gate decides, the lock follows the measurement).

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

## E. New sources — the Braithwaite design tool + the RINA paper (2026-08-22)

Two new primary-side resources arrived and were fully decoded:
- **`sources/galley-sizing-xlsm/`** — the author's oared-warship concept-design
  tool (every sheet to TSV, all 17 VBA routines to text, the raw offset table
  to `basis_hull_offsets.tsv`; `DECODE.md` in the directory). Contents: the
  **real Olympias offsets** (21 stations, LWL 32.35 m, from the Lines Plan),
  the hydrostatics (44.26 m³ @ Z 1.15, LCB 15.67 m from AP, WSA 130.5 m²,
  Cb 0.321, Cw 0.768), the **weight breakdown** (lightship 25.748 t @ VCG
  1.905 m, full load 45.5 t, oars 17 kg), the trials powering (the piecewise
  resistance fit, the 81 N→0 @ 18 kt thrust law, top speed 9.95 kt rudders
  up, the 830 J ram-failure energy), the **independent 3-DOF manoeuvring
  model** (Clarke–Gedling–Hine derivatives, the cross-flow yaw damper
  −ρ·CN·T·L⁴/64, Iz = m(L/3)², the Hoerner rudder + the trials parasitic
  drag, the 67°-rudder turn scenarios with trajectories), and the transformed
  designs (the pentaconter bireme).
- **`sources/warship-evolution-6th-bc/`** — the draft RINA IJME 2016 paper
  the tool serves (the study's write-up; text extracted; `DECODE.md`).

### What the new data already settled (validation wins)

- **Zero-speed thrust**: the trials' 81 N/oarsman vs the LL's equilibrium
  ~82 N/oar at 38.75 spm, V = 0 — two independent derivations agree. ✓
- **Lightship**: 25.748 t (scantlings + 1:24 model + inclining) confirms the
  chain's 25.798 t anchor to 50 kg; the full load 45.5 t sits in the 43–47 t
  family (register B1). ✓
- **The piecewise trials resistance fit** (40.2/75.2/88.6·V² — "cf ref 1
  p82") corroborated source-side (register B2); the rudder parasitic-drag
  law 137V²+0.65V corroborated in the workbook's VBA (register C3). ✓
- **The real lines**: the "no numerical offsets" caveat (register B6,
  offsets-eliav.md) is retired — the offset table is in hand, and the
  Plan-2 verdict's named gap ("the real lines are the path") is now
  concrete.

### The available next steps (ordered by impact)

**E1. The real-lines cross-flow audit — Plan 2's completion.**
Run the lane-5 audit on `basis_hull_offsets.tsv` (the parametric hull +
the assumed ram were the named gap): the lateral plane, A_lat, the CLR
and the cross-flow J from the actual sections. Targets: the fitted
clr_offset +0.8 m (the parametric hull computed AFT — the open item),
Taylor's A_lat 35 m² (the parametric hull was 26–31 % light), and the CN
split — the workbook's rectangular projection with CN 0.4 vs 0.8 vs our
tapered-plane C_D 0.30 should collapse to one value on the real plane.
If the values move: the LL turn gates re-run + the HL re-calibration
(the Plan-2 loop). The real plane also bears on the drift-angle open item
(the model's 1.4° vs the trials' 8–15° — the lateral force's distribution).

**E2. The mass reconciliation.** The LL's ship mass vs the workbook's
45.5 t full load / 25.75 t light — m_app and the turn physics follow.
(Register B1 already carries the numbers.)

**E3. The no-head-room sprint test — T1's decisive cheap measurement.**
The workbook's 9.95 kt is all-170 at the trials thrust law with NO
thalmian shortfall; our LL's sprint (7.45 kinematic / 7.72 force) uses the
fitted head-room 0.6 at 44.5 spm. Run the LL with the thalmian factor 1.0:
if the equilibrium approaches ~9.9, the whole sprint deficit is the
head-room shape (the class-C row), not the blade law; if it stays ~8, the
E/A5 family is the suspect. Either way the T1 ledger gets a verdict and
the P1.6 sprint blocker (blocker 2) a named direction.

**E4. The independent-model cross-check.** The VBA is fully decoded:
transcribe ManAcceleration / OarForces / RudderForces (CGH derivatives,
the CN yaw damper, the Hoerner rudder + the 137V²+0.65V parasitic drag,
the 81 N linear law) into a Python script and run the G1/F1/tightest
scenarios + the top-speed curve — compare trajectories, diameters and the
speed decay through the turns against the LL. A second trial-tuned model
of the same ship is the strongest available cross-check of the turn
physics (the W5 family — P1.6 blocker 1).

**E5. The resistance-fit reconciliation.** The trials piecewise runs
12–15 % below the chain law at 8–10 kt — same trials data, two fits.
Document the cause (loading condition, rudder contribution, the fit
families); analysis only — the chain law is trial-speed-validated and
stays unless a gate says otherwise.

**E6. The Iz reconciliation.** The workbook's Iz = m(L/3)² = 5.28e6
(Rg from the 1:24-model pendulum tests) vs the LL's Iz (register C10).

**E7. The portability milestone — the tuning rule's test.**
The workbook's pentaconter designs (monoreme: 25/side, LOA 31 m, 21 t,
GMT 0.643 m; bireme: LWL 17.2 m, B 2.8, T 0.759, 14.4 t — with the
Transform sheet's offsets and the author's powering/turn predictions)
are a NEW ship whose "plans" ARE held. Running our class-A machinery
from the pentaconter's offsets and comparing with the workbook's numbers
is the tuning rule's "for a new ship whose plans ARE held, class A
computes from day one" — made testable. Scope decision needed:
a research-side portability study vs a full LL scenario.

**E8. The remaining decode (low priority).** The paper's figures
(Figures 2/3/5, Tables 1/2 — image reading) and the workbook's 15
charts' plotted series.

### Interactions with the standing programs

- The Plan-2 verdict's honest negative (b) — the CLR/A_lat gap — is E1's
  direct target.
- The P1.6 blockers: the turns (blocker 1) gain E1 + E4; the sprint
  (blocker 2) gains E3 (the head-room test) — both land before the
  force-mode promotion.
- The MarkIIb (blocker 4) is unchanged: the workbook's linear thrust law
  is a different model family and does not resolve the P-law vs the
  0.472 s drive inconsistency (the same A5 tension, force-side-quantified).
- E2/E6 touch the turn physics (m_app, Iz) — run them with the gates.
