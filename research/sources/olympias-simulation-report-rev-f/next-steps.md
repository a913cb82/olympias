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

**B1. Scalar added mass vs the mass matrix.** His (m − X_u̇, m − Y_v̇, Y_ṙ,
N_v̇, I − N_ṙ) matrix with the sway-yaw COUPLING terms vs our scalar
m_app = 1.10 × displacement for both surge and sway. The off-diagonal
terms act exactly in the drift regime — our open item (1.4° vs the
trials' 8-15°). Test: estimate the derivative magnitudes (Clarke-Gedling-
Hine, his Ref 9, or our own A_lat/CLR parameters) and measure whether the
coupling moves the drift toward the trials.

**B2. Flat-plate normal law vs the lift+drag polars.** Evaluate the
Caplan-Gardiner macon polars (his Figure 8 — the CL/CD data is in media/)
at our stroke's angles of attack and quantify the lift's contribution to
the mean thrust and to the lateral force in turns. If the lift is < 5 %
at our angles, the choice is documented as negligible; if not, a labelled,
swappable lift term is the follow-up (the chain's C_N = 1.8 and the A5
area gap stay the compensating knobs unless a gate says otherwise).

**B3. Kinematic vs force control — a force-anchor cross-check.** His
force curve (catchFactor continuity, the max-force line falling with ship
speed — his Figure 10, the Hill-like strain-rate factor) vs our measured
kinematics + the Fh anchors. Compare his intercept/gradient against our
Fh_MAX 700 N / Fh_BURST 330 N. A cross-check only — the measured
kinematics stay the ceiling (the gates are built on them).

**B4. The turn model's drag law — a measured inconsistency.** Three drag
representations disagree at cruise speeds (measured here for the first
time): the chain law (W = 155V³ + 4.13V⁵, V in m/s → 2.70 kN at 7 kt), the
LL's turn-model Taylor bands (40.2v² → 1.97 kN, **−27 %**), and the trials'
raw piecewise as the report quotes it (75.2v² − 1560 → 2.13 kN, −21 %).
The turn gates pass with the 40.2v² law because the turn diameters are
torque-dominated — but the drag the turn model carries should be the
trial-validated one. Investigate whether switching the turn model to the
chain law (or the piecewise with its offsets) moves the turn gates and
the t_360 item, and record the verdict either way.

**B5. The rower's moving mass (expected: negligible, to be documented).**
His explicit 51.02 kg footplate model vs ours absent. The argument to
test: for the hull+crew as one rigid body the footplate/handle split is
internal — the hull's motion is unchanged (his own note: the ship is
treated as a rigid body including the oarsmen; fixed seats, small mass
fraction). Matters only for local loads and pitch, and we have no pitch
DOF. Verdict expected: investigated, negligible.

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
  replacement).
- The chain's hull-power law (155V³ + 4.13V⁵, V in m/s) — the power chain
  closes on it; his raw tow cubic (10-20 % below) stays a register
  cross-check.
- The report's unvalidated status: nothing is promoted to an anchor
  without the source's context being checked against the trials report
  itself (his Ref (1), which we still do not hold).
