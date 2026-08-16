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

**A1. Per-station oar model with local flow (unpack the 4.8 m lever).**
Today the oar yaw moment is the fitted oar-race lever (4.8 m, Taylor
ch.31 row 10) times the side-thrust difference, and the held-blade brake
uses a separate fitted arm (LEVER_HOLD 1.5 m) — the register C3 explicitly
flags the lever as a lump that folds in station arms, stopped-blade drag
and drift dynamics. The report gives the material to unpack it: Figure 16
(the original oar configuration — the station plan the register B6 lists
as missing) and Table 3 (per-tier geometry, including the SHORT oars at
the bow/stern — the stations with the longest yaw arms, which our rig does
not carry). The upgrade: place the 170 oars per the plan, compute each
blade's flow from the ship's (u, v, r) at its station, and let the yaw
moment and the brake emerge from the per-oar sums.

Acceptance: the one-side-stops gates stay ≤ 7 % — the computed sum must
reproduce the 4.8 m the fitted lever encodes — and the drift angle should
move toward the trials' 8-15° (the open item, VALIDATION §11.3). The
station decoding from image21.jpeg is a research task first.

**A2. The stroke phase structure.** His model puts the oar inertia inside
the stroke dynamics: the finish/catch are constant-moment phases solved so
the oar's angular velocity reaches zero at the stroke ends (ω(t) decelerates
into the finish, accelerates out of the catch); ours is a constant-ω drive
plus the Table 3.1 impulse corrections. The report's stroke-time budget
(p28, the skilled thranite) quantifies the difference: 1.8 s stroke at
33 spm, **0.7 s in the water** (fraction 0.39), 0.2 s catch+finish — vs our
Table 9.6 effective-pull 0.43 s at 28.8 spm (fraction **0.21**). The blade
spends ~2× longer in the water than the effective-pull time implies, with
weaker force at the stroke ends. Investigate a phase-based ω(t) profile
that reproduces the measured timings AND keeps the mean thrust and the
Gate-1 agreement with the rigid-oar reference (the effective time is the
chain's validated quantity; the in-water time is a different measurement —
the two must both be met).

**A3. The rudder as an aerofoil (low priority).** His full lift/drag foil
at the stock (his Figure 12) vs our Taylor empirical drag-fraction law.
Ours is calibrated and gate-passing; the foil only matters off-design
(reversals, the mixed-hold families). Needs the rudder's geometry from the
report before it can be costed.

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

**C1. The stationary-turn anchor (Ref (1) p30, via the report).**
"Stationary turning Zygian and Thranite only at 27 [spm] … 3.5 degrees/
second". A new scenario for the t_360 item (VALIDATION §7.2): the LL from
rest with the two lower tiers at 27 spm, measure the settled turn rate vs
3.5°/s. Context: the model's full-crew 360° is 98 s (3.67°/s) vs the
trial's ~128 s (2.81°/s); this anchor sits between (102.9 s) and is a
PARTIAL-crew turn — the source is ambiguous about one side (58 oars) or
both (116) [?] — the scenario should be built to show both readings.

**C2. The zig-zag overshoots (p30).** First overshoot 8°, subsequent 7°
past the 20° targets — a gate candidate we do not gate on today (the
zig-zag row is position/mean-gated, VALIDATION §9.3). The LL's overshoot
is measurable from the existing scenario; add the check if it discriminates.

**C3. The rudder-drag constant cross-check.** His "rudders only
137.0v² + 0.65v" (v in m/s) vs our rudder_straight 39.4 per kt²: measured
**+8-9 %** agreement at 5-8 kt — an independent confirmation of the
constant. Record in the register (lane-5, the rudder row).

**C4. The hull-resistance piecewise (p74).** The raw trials bands now
quoted in our sources: 40.2v² / 75.2v² − 1560 / 88.6v² − 2640 (rudders
raised, v in kt). Confirms the Taylor band base but shows the LL's current
band set has the −1560/−2640 offsets collapsed — feeds B4.

**C5. The oar table (Table 3).** Blade area 0.113 m² — the A5 register
entry's independent 1.45× confirmation (quote it in the register); oar
inertia 30 kg m² — the Table 3.1 A-family value in the wild (the A/B
anomaly is source-side); the short-oar geometry (4.0 m overall, 0.774 m
inboard) for A1; the blade-CP distances (0.297-0.363 m from the end vs our
0.26); the rake (4/8/9°); the θ column (32/24/13° — meaning unclear [?]).

**C6. The stroke-time budget (p28).** 1.8 s stroke, 0.7 s in water, 0.2 s
catch+finish, rhythm factor 2.6, stroke length 0.7 m vs the 1.0 m
achievable (butt end). Feeds A2; the handle-arc cross-check: our sweep
48.1° × lin 0.957 m = 0.80 m vs his 0.7 measured / 1.0 achievable — ours
sits between, consistent.

**C7. The thranite-only speed (p50).** "Speed = 3.3 knots" in the skilled-
thranite record — a partial-crew equilibrium cross-check (rate_for_speed
with n_oars = 62 at the record's ~33 spm vs 3.3 kt). The source's context
is loose [?] — verify the reading before building anything on it.

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
