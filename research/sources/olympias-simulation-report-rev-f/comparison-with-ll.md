# Braithwaite's 2-D rowing model vs the LL — a deep-dive comparison

The source document: R Braithwaite, "A 2-D Rowing Model Applied to the
Manoeuvring of the Trireme Reconstruction Olympias" (Rev F, created
2019-11-22, last modified 2026-03-16) — see `README.md` in this folder for
the provenance and the conversion caveats. This comparison is against the
LL (`simulation/ll/`), the per-oar oracle of this project's validated
chain. It is a comparison of METHODOLOGY (the report's equations, not its
code — the appendix is empty), and of the anchors each side cites.

Both documents model the same ship against the same primary sources (the
1988 sea-trials report — his Ref (1), our chain's trial anchor — and
Rankov 2012, his Refs (8)/(16), our ch.7/ch.9/ch.31 chain). The deep
difference is the philosophy: his report is a FORCE-DRIVEN model whose
validation was never written; the LL is a MEASURED-KINEMATICS model with a
physiology layer, validated by the gate structure (`simulation/docs/
VALIDATION.md` §1-8) — 141 checks, green.

| Topic | Braithwaite Rev F | The LL | The diff |
| --- | --- | --- | --- |
| Control philosophy | force control (solve the oar's angular velocity so the handle force matches a prescribed force curve) | kinematic control (the trials' measured drive/recovery timings; the physiology layer slows/shortens/feathers the stroke at force limits) | the two schools his §BACKGROUND names (kinematic: Alexander, Cabrera; force: Atkinson, Van Holst). He chose force; the chain chose measured kinematics |
| DOF | 3 (surge, sway, yaw) | 3 (surge, sway, yaw) | none (but see the added-mass and the local-flow rows) |
| Integration | simple Euler | fixed-step Euler (dt 0.01 s) | none |
| Added mass | 6-term mass matrix (m − X_u̇, m − Y_v̇, Y_ṙ, N_v̇, I − N_ṙ) from semi-empirical derivative estimates | scalar m_app = 1.10 × displacement (46.2 t — the trials' apparent mass) | matrix vs scalar; both end near the same 46 t |
| Hull forces | linear derivatives X_U u, Y_v v, N_r r with the u and r terms replaced by quadratics | Taylor ch.31 3-band drag + quadratic yaw resistance Ω·ω|ω| + CLR lateral force | his N_r "changed to a constant to give the observed turning rate at zero velocity" = our Ω·ω² choice, reached independently |
| Hull resistance | his fit to the trials' tow data: 51.4v³ − 76v² + 223v N (raised, v in m/s); trials' piecewise (40.2v² / 75.2v²−1560 / 88.6v²−2640, v in kt) | the chain's trial-validated hull-power law W = 155V³ + 4.13V⁵ (V in m/s), D = W/V; the LL's turn model uses the Taylor ch.31 bands | numerically: his raised cubic sits 10-20 % BELOW the chain law at cruise (2.2 kN vs 2.7 kN at 7 kt, 4.5 vs 5.2 kN at 9 kt) — the chain's law is the one the power chain (P = 7.43r × E) closes on; his is a raw tow fit. See §4 |
| Blade law | lift + drag, Caplan-Gardiner macon polars (CL/CD vs angle of attack, the lift-reversal handling) | flat-plate normal law Fn = ½ρAC_N·|v_n|·v_n, C_N = 1.8 — the locked identity with Shaw ch.9's (q/p)² turning-point law | polar vs normal-force. At the trireme's large angles of attack the normal-force law ≈ drag-dominated; the lift component is not modeled in the LL (the register A5 blade-area gap is the chain's compensating knob, see §10) |
| Blade flow in a turn | per-oar: the blade's relative velocity includes the ship's (u, v, r) at the blade centroid — the local flow at each station | aggregated: blade flow uses the hull speed V only; the yaw moment enters through the fitted oar-race lever (4.8 m, Taylor ch.31 row 10 — register C3 notes the lever folds in drift/lateral dynamics) | his is explicit per-oar local flow; the LL's lever is the validated lump. The report's Figure 16 (the station plan) is the C3/B6 material — see §10 |
| Stroke phases | 4: finish (constant handle moment, oar inertia in the dynamics, ω→0 solved), recovery (cubic), catch (mirror), power (force-curve-driven, secant iteration for ω) | 2 + corrections: drive and recovery at constant ω (the measured Table 9.6 timings); the inertia layer adds the catch-flip/finish-release impulses (Table 3.1 mit) + the flip power | both model the same mechanics (inertia at the stroke ends); his solves it inside the phase dynamics, the LL applies the prescribed kinematics + impulse pulses |
| Oar angular velocity | solved per step by secant iteration so the handle force matches the force curve (catchFactor continuity, max-force linear in ship speed — the Hill-like muscle factor) | commanded (measured) drive speed, reduced by the force ceiling (Fh_max), the mean-force target (7.43r / Fh_BURST), the tempo slot, or the feather limit | the deepest single diff: his rower is a force curve, ours is a power/endurance physiology with measured kinematics as the ceiling |
| Rower mass | explicit: 51.02 kg moving mass (0.547 of 75 kg), footplate forces from the handle acceleration along the footplate line | not modeled as a body (the oar's inertia only; the moving-mass work is inside the P = 7.43r chain) | his report itself notes the term is "considerably less significant in the case of Olympias" (fixed seats, small mass fraction) |
| Oar modes | stroke / follow / timed oars (blade clearances in a packed oar system) | the pipe: all oars in unison per side/tier; the weakest side governs the rate (keleustes call-down) | his cares about per-oar load differences in turns; the LL's per-tier split (31/27/27, thalmian power factor) is the same concern at the aggregated level |
| Rudder | full aerofoil: lift + drag at the stock, angle-of-attack handling identical to the oars, form resistance added | Taylor ch.31 empirical: straight drag (39.4/kt²), applied-helm factor (0.6-3.25×), lateral force = coeff(φ)·drag with coeff quadratic in φ, torque = lateral × lever (14.9 m); full helm 67.5° | aerofoil vs empirical; both anchored to the same trials and both turn-validated in ours |
| Crew physiology | none (no fatigue, no W′, no endurance) | the core of the LL: P_crit 80 W/man (R&W ch.23), W′ 5 kJ (ch.9-anchored), τ 120 s refill, Fh ceilings, rate call-downs, per-tier W′ tanks | his scope is performance kinematics; the LL's is the crew |
| Stationary turning | 3.5°/s at 27 spm, Zygian+Thranite only (Ref (1) p30) | the t_360 open item (VALIDATION §7.2): the model 98 s vs the trials ~128 s → 3.67 vs 2.81°/s | his anchor sits between: 3.5°/s → 102.9 s. Partial-crew (116 oars) yet FASTER than the full-crew trial's 2.81°/s — a useful boundary datum for the open item, see §10 |
| Zig-zag | helm 22.5°, first overshoot 8°, subsequent 7° (Ref (1) p30) | the harness zig-zag scenario: helm 22.5° port/starboard, mean +1.3 % annotated | the same source anchor, consistent |
| Validation | STUB — §6 (VALIDATION) and §7 (SOFTWARE ARCHITECTURE) are one line each; the calibration notes are scattered ("The value for Nr is …", "changed to a constant…") | the gate structure: research → LL gates 1-8 → HL equivalence (141 checks), every mismatch named, measured, locked | his report never closed its validation; ours is the acceptance record |

## 1. The two models' shared skeleton

Both integrate the same 3-DOF rigid-body equations in the ship frame with
the centripetal couplings — his eq. (3.6): m(u̇ − vr) = X_U u + X_u̇ u̇, etc.;
our `ll/ship.py::hull_advance`: u_dot = (Fx − D)/m_app + v·ω, v_dot = …
− u·ω, ω_dot = (Q − Ωω|ω|)/I. Both use simple Euler. Both carry the same
inertia about the z-axis (4×10⁶ kg m² — his Table 2 cites Taylor's model,
his Ref (16); our VESSELS.Olympias.I = 4×10⁶ from the same Table 31.1).
Both carry ≈46 t apparent mass (his Table 2: "Displacement (includes added
mass) 46 tonnes" from the trials report p21; our m_app = 1.10 × 42 t =
46.2 t, and the surge gate's 1.10 × 41.35 t trial displacement).

The differences start where the forces come from: his from semi-empirical
derivative estimates (Clarke-Gedling-Hine for merchant hulls, his Ref (9))
dimensionalised with the (u, r) quadratics; ours from the trial-validated
constants of the chain. Both are honest about the fit: he notes N_r was
"changed to a constant to give the observed turning rate at zero velocity"
— the same quadratic-yaw-resistance choice our Ω·ω|ω| makes (with the
sway-calibrated Ω = 3.2×10⁶; the vessel's own 5×10⁶ from Table 31.1).

## 2. The added-mass and the lateral model

His mass matrix is the full linear-theory set: (m − X_u̇), (m − Y_v̇), Y_ṙ,
N_v̇, (I − N_ṙ), with the off-diagonal couplings solved by inverting M. The
derivative magnitudes come from the merchant-ship approximations — an
honest first-principles estimate with no trial tuning. Ours is the scalar
apparent mass (1.10×, the trials' measured factor) plus the explicit
lateral balance: the CLR restoring moment (rho·A_lat·u²·sin β at the CLR,
0.8 m forward of the CG — sway-calibrated, plan 15.3, register C1) and the
quadratic yaw resistance. The two reduce to similar dynamics; the LL's
constants are measured, his are estimated. (His planned drift-angle fit —
"The value for Nr is …" — is exactly the open drift item, VALIDATION §11.3:
the model's 1.4° vs the trials' 8-15°.)

## 3. The oar: force-driven vs measured kinematics

The report's own §BACKGROUND frames the field's split: kinematic control
(prescribed oar angle) vs force control (prescribed handle force, the
angular velocity solved iteratively). He implements force control: the
stroke's phases are driven by the handle-force curve (a function of angle
and time, with the catchFactor continuity correction and the max-force
line that falls with ship speed — the Hill-like strain-rate factor), and
the oar's angular velocity is found per step by the secant method so the
blade moment balances the target handle force. The LL implements the other
school: the drive/recovery timing is the MEASURED Table 9.6 schedule (the
trials' actual strokes), and the crew model can only make the stroke
slower/shorter/feathered — never faster than what the trials recorded —
by the physiology limits: the peak handle force (Fh_max 700 N), the mean
force the power law commands (7.43·r, or the 330 N burst at spoude), the
tempo slot, and the feather dead-spot (when the blade cannot outrun the
water). The philosophical difference is which is the ceiling: his rower's
force curve IS the model; ours is a measured kinematics with the rower as
a constraint.

The blade laws are different in kind: his Caplan-Gardiner macon polars
(lift + drag vs the angle of attack, with the lift-reversal handling and
the π − α symmetry reset) describe a REAL blade; the LL's flat-plate normal
law (Fn = ½ρAC_N·|v_n|·v_n, C_N = 1.8) is the locked algebraic identity
with Shaw ch.9's (q/p)² turning-point law — a drag-only model, no lift
term. At the trireme's stroke the angle of attack swings through large
values where the macon's lift is small and the drag dominates; the two
families are not directly comparable (his polars would need the local
angles per station, ours is calibrated through the power chain). The
register's A5 blade-area gap (0.078 vs the ch.9 note's ×3.3) is the
compensating knob the chain keeps labelled — see §10 for his independent
0.113 m².

## 4. The hull-resistance cross-check

His fits to the SAME 1988 tow data (his §5.1.2) vs the chain's validated
power law:

| V (kt) | his raised cubic (N) | chain W/V (N) | diff |
| --- | --- | --- | --- |
| 5 | 946 | 1206 | −22 % |
| 7 | 2218 | 2705 | −18 % |
| 8 | 3214 | 3810 | −16 % |
| 9 | 4505 | 5221 | −14 % |

The chain's law is the one the power chain closes on (7 kt: 9.7 kW hull
need vs 170 × 79.5 W × E ≈ 9.7-10.4 kW propulsive — the ch.7 triple); his
cubic would demand only ~8 kW at 7 kt, which the crew model cannot
supply. The difference is not resolved here — his is a raw tow fit, the
chain's is the trial-validated power balance — but the numbers bracket the
same data and are recorded for the register's cross-checks. (His
trials-piecewise at 7 kt: 75.2·49 − 1560 = 2125 N — also below the chain,
which includes the "less disruptive rudders" of Taylor's Fig 31.1 curve.)

## 5. The turn model: local flow vs the fitted lever

His oar forces are computed per oar at its station, with the blade's
velocity relative to the water built from the ship's (u, v, r) at the
blade centroid — so in a turn the port and starboard blades see different
flows and the yaw moment emerges from the per-oar sums. The LL aggregates:
the blade flow uses the hull speed only, and the yaw moment is the
side-thrust difference times the fitted oar-race lever (4.8 m — Taylor
ch.31 row 10; the register C3 explicitly notes the lever likely folds in
stopped-blade drag and drift dynamics that a per-station model would make
explicit). The lever is turn-validated (the one-side-stops gates, ≤7 %),
so the LL is honest about the lump; his report is the design that would
unpack it — and its Figure 16 (the original oar configuration) plus his
oar-table geometry is the station-plan material the register B6 lists as
missing from our sources.

## 6. The oar-geometry cross-check (his Table 3 vs the chain)

| Quantity | his Table 3 (trials report) | the chain | note |
| --- | --- | --- | --- |
| Oar length overall | 4.220 m (4.000 short) | — | same family |
| Inboard to handle centre | 0.935 m (0.774 short); 1.05 to the handle | 1.092 m | 17 % longer in the chain — different measurement convention or source [?] |
| Blade area | 0.113 m² (0.109 thalmian) | 0.078 m² | his 1.45× larger — the register A5 blade-area gap's independent confirmation (§10) |
| Oar inertia about thole | 30 kg m² (zygian row) | Table 3.1 B-family, spruce fleet 9.7 | his 30 IS the Table 3.1 A-family zygian cell — the A/B anomaly's source-side value, recorded as printed |
| Rake | 4 / 8 / 9° | — (cant 0 on Olympias) | — |
| Angle θ | 32 / 24 / 13° | sweep 48.1 / 48.4 / 55.6° | his θ's meaning is unclear (mid-sweep angle from the keel?); his "stroke length 0.7 m vs 1.0 m achievable (butt end)" is the skilled-thranite record, p28 [?] |
| Blade CP | centre of blade, 0.297-0.363 m from the end | 0.26 m from the tip | close family |

## 7. The crew

His report has no physiology: the rower is the force curve and the moving
mass (51.02 kg, 0.547 of the 75 kg body, with the footplate reaction
forces — his Table 1). The LL's whole Phase-1 crew layer — P_crit, W′
tanks, refill, ceilings, tempo call-downs, the per-tier split with the
thalmian power factor — has no counterpart in his report (its scope is
performance analysis, its future-applications list is tactics and Mk II
design). This is not a disagreement; it is a scope gap: his model cannot
answer the endurance questions the LL's gates 4/6/7 are built on.

## 8. The turning anchors (what each cites from Ref (1) p30)

Both use the same source page for the zig-zag: helm 22.5°, first overshoot
8°, subsequent 7° — the harness scenario's numbers. His stationary-turn
note is the new material: "Stationary turning Zygian and Thranite only at
27 [spm] … 3.5 degrees/second". Context matters: the Zygian+Thranite pair
is 116 of the 170 oars — a partial-crew turn from rest — yet 3.5°/s is
FASTER than the full-crew 360° trial's implied 2.81°/s (128 s) and close
to the LL's 3.67°/s (98 s). The t_360 open item (VALIDATION §7.2) is the
model's turn-speed floor; this anchor is a boundary datum the item should
quote, but it does not by itself arbitrate the floor — the scenario
(partial crew, from rest, the low-speed oar-torque regime) is different
from the full-crew turn the item measures.

## 9. Validation: the stub vs the gates

His §6 (VALIDATION) and §7 (SOFTWARE ARCHITECTURE) are one-line headings;
the comparisons he planned — the resistance figures 13/14, the stationary
turn, the zig-zag overshoots, the speed/acceleration video record — are
the list of a planned section that was never written (the appendix's
source code is also absent). The LL is the opposite: every number in it
traces to a gate (the chain of trust), and every remaining mismatch is
named, measured, and locked in VALIDATION §11. The comparison's honest
verdict: his report is an unvalidated design study; the LL is a validated
implementation. Where they touch the same trials, they agree on the
anchors and bracket the open items — which is exactly what a sibling
model is good for.

## 10. What the report contributes to this project (the actionable items)

1. **The stationary-turn 3.5°/s at 27 spm (partial crew)** — a boundary
   datum for the t_360 open item (VALIDATION §7.2), quoted above.
2. **Blade area 0.113 m²** — an independent, source-side confirmation of
   the register A5 blade-area gap (the chain's 0.078): the original oars'
   blades were 1.45× larger than the law's implied area. The register
   should quote it.
3. **The oar-station configuration (his Figure 16 + Table 3)** — the
   station-plan material register B6 lists as missing; if the figure's
   station coordinates can be read off (image21.jpeg in media/), the
   oar-race lever's 4.8 m lump (register C3) could be unpacked.
4. **Oar inertia 30 kg m² (zygian)** — the Table 3.1 A-family value in the
   wild, confirming the A/B anomaly is source-side, not ours.
5. **His resistance cubics** — a second independent fit to the same tow
   data, 10-20 % below the chain law; recorded in §4 for the register.
6. **The drift-angle planned fit** ("The value for Nr is …") — his
   unfinished sentence is the same open item as our drift 1.4° vs 8-15°
   (VALIDATION §11.3); no resolution in the source.

None of these change the validated chain: the gates are the posterior, and
the report's numbers are quoted here as cross-checks and boundary data,
not as new anchors. If any is promoted (e.g. the 3.5°/s into the t_360
item's text), that is a research-lane decision to make explicitly.
