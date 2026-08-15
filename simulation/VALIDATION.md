# LL simulation validation ledger

The low-level simulator's acceptance record. Chain of trust:

    real-world trials  →  research chain (research/ + lane-6 validation)  →  LL

The LL is the oracle of the pair (plan §6): it must satisfy the repository's
validated numbers, and this file records exactly how it does — gate by gate,
anchor by anchor, including the honest mismatches (§7). Confidence flags
follow the repo convention: `[x]` = reproduced against a cited anchor,
`[?]` = provisional/labelled, `[!]` = known mismatch, documented.

## 0. Reproduce everything (pytest)

```bash
cd simulation
../.venv/bin/python3 -m pytest          # all suites, one command: 103 checks
../.venv/bin/python3 -m pytest -v       # per-check names
../.venv/bin/python3 -m pytest ll/tests/test_gate5.py   # one suite
../.venv/bin/python3 ll/tests/test_gate5.py             # direct run also works
```

Suites: `tests/test_parser.py` (19) · `ll/tests/test_gate1..8.py`
(7/12/9/8/7/4/4/5) · `tests/test_research_chain.py` (12) ·
`hl/tests/test_hl_basics.py` (9 — the Phase-2 HL, §9) ·
`harness/tests/test_harness.py` (6 — the pair harness machinery, §9). Every
check asserts a documented anchor or a locked honest behaviour (e.g. oQ-18
shortfall, tempo loss, Mark IIb prop fraction, the HL's drift floor).

## 1. Gate 1 — one-oar physics vs the rigid-oar reference `[x]` (7 checks)

The time-stepped oar must reproduce the static rigid-oar model
(`research/lane-4-oars/rigid_oar_model.py`), itself validated against the
ch.7/ch.9 power chain.

| Quantity | LL | Anchor | Match |
| --- | --- | --- | --- |
| Agreement at the 4 Table 9.6 points | — | rigid model | < 0.5 % (typ. 0.1–0.2 %) |
| Mean handle force @ 7.2 kt / 28.8 spm | 223.5 N | 210–225 N cruise family (Table 3.2 couple) | ✓ |
| Mean handle force @ 8.2 kt / 36 spm | 208 N | cruise family | ✓ |
| Propulsive W/man @ 7.2 kt | 64.7 W | hull need 63.4 W | 102 % |
| dt convergence (600 vs 3000 steps) | — | — | < 0.3 % |
| Recovery / cycle wrap | — | — | zero force, clean |

## 2. Gate 2 — surge hull vs the ch.7/ch.9 speed-power chain `[x]` (12 checks)

| Rate | LL equilibrium | Anchor | Match |
| --- | --- | --- | --- |
| 25.5 spm | 6.89 kt | 7.0 kt (ch.7 ref, Mark II hull) | −1.6 % |
| 28.8 spm | **7.22 kt** | **7.2 kt (Table 9.6 / S6 anchor)** | **+0.3 %** |
| 32.3 spm | 7.58 kt | 8.0 kt (ch.7 ref) | −5.3 % |
| 36.0 spm | **7.98 kt** | **8.2 kt (Table 9.6)** | **−2.7 %** |
| 44.5 spm, 130 oars | 7.9–8.8 kt bracket | 8.2–8.4 kt trial | trial inside the bracket `[x]` |
| 44.5 spm, 170 oars | ~7.9 kt burst | (trial ~130 effective; the thalmians 'ineffective' at sprint) | overshoot closed by the per-tier head-room (Gate 6) `[x]` |

Also: full per-step coupling agrees with the mean-force equilibrium < 1 %;
settles from 0.9·V\* within ~24 s with no overshoot (measured settle_time,
current code); stroke-frequency surge ripple ≈ 0.2 kt (physical — the ship
surges each drive); monotonic rate curve; the oQ-18 Mark IIb shortfall
reproduced exactly (locked by test).

## 3. Gate 3 — 170-oar turns vs the W5 trial anchors `[x]` (9 checks)

| Scenario | LL diameter | Anchor | Match |
| --- | --- | --- | --- |
| G1 full rudder @ 6 kt | 89.7 m | 89.4 m | +0.3 % (sway-calibrated set) |
| F1 22.5° @ 6 kt | 117.4 m | 111.9 m | +4.9 % |
| Tightest, one side stops @ 6.5 kt | 67.7 m | 62 m | +9.2 % |
| Oar-only hold / back (no rudder) | 126.6 / 126.6 m | no trial anchors (oQ-3) | back ≡ hold at speed (the hold-brake degeneration, Gate 4) `[x]` |

Also: symmetric crew holds course within the physical per-stroke lateral
kick (test_trim: the blade's net Fy, heading drift < 15° in 5 min — an
untrimmed model behavior, see §9); the rudder-turn diameter is
speed-independent (Q ∝ v², ω ∝ v — why the steady model worked); the
time-domain 360° time exceeds the steady estimate (deceleration — the W5
caveat mechanism, now integrated).

## 4. Gate 4 — rower physiology vs the trial endurance record `[x]` (8 checks)

| Behaviour | LL | Trial observation | Match |
| --- | --- | --- | --- |
| Sustainable envelope (steady pressure, 30 min) | W′ full, speed stable @ 25.5/28.8 spm | 7 kt = 79.5 W handle = R&W's 80 W P_crit | ✓ (to 0.6 %) |
| Sprint @ 44.5 spm spoude | bursts **~45 s**, then fades | trials sustained 8.2–8.3 kt ~45 s | ✓ (W′ = 5 kJ anchor) |
| Rest start | short stretched strokes, Fh ≤ 700 N, 6.0 kt @ 30 s, 6.75 @ 60 s | Taylor bulk law: 9 kt @ 24 s | physiology governs the start `[x]` |
| Backing at speed | degenerates to hold-brake | (no data) | physical — flow drag > grip `[x]` |
| Asymmetric fatigue | exhausted side strokes slower → yaw 215° in 3 min | differential oar-work attested | consistent `[x]` |
| Tightest turn, long run | W′ drains → speed 6.6 → 4.4 kt | "halves speed" | mechanism emergent `[x]` |
| `rate 50` + exhausted | tempo lost, achieved 40 spm | — | oQ-14 answer: consequence + telemetry `[x]` |

## 5. Gate 5 — oar inertia vs Table 3.1 `[x]` (7 checks)

| Quantity | LL | Anchor | Match |
| --- | --- | --- | --- |
| Catch spikes @ t_rise 0.15 s, 28.8 spm | 116 / 215 / 156 N | oar_inertia.py (Table 3.1 MITs) | ± 2 % |
| Full-reversal spikes (ω_rec + ω_drive) | 146 / 270 / 197 N | — | documented `[x]` |
| Handiness | old-fir zygian / spruce **1.85×** | "old fir ≈ 2× spruce" (plan §6) | ✓ |
| Hull observables with the layer ON | unchanged | 4 Table 9.6 points | < 1 % (inertia is internal) |
| Momentum closure | net pulse impulse ≈ 0 / cycle | — | exact `[x]` |
| Couple anchor | 224 N @ anchored point | Table 3.2 (0.6 % chain check) | ± 3 % |
| **Force-driven companion** | drive time **0.43 s** | Table 9.6 0.43 s | essentially exact — kinematics ≡ forces + inertia |

## 6. Cross-cutting consistency (research-side anchors the LL inherits)

| Check | Result |
| --- | --- |
| Couple cross-check: 224 N × 1.092 m vs Table 3.2's 246 N·m | 0.6 % |
| P = 7.43·r origin: ¾-NM calibration 288 N @ 38.75 spm | 7.43 × 38.75 = 288 ✓ |
| R&W 80 W/man vs ch.7 79.5 W handle power @ 7 kt | 0.6 % |
| Lane-4 chain vs Shaw: 8.32-kt sprint, Table 9.7, ch.7 cruise | reproduced (research side) |
| F/G turn model vs tactical anchors 145/80/62 m | ≤ 7 % (research side) |
| Trial volume / light volume (hull) | 41.35 / 25.17 m³ (research side) |

## 7. The honest mismatch ledger `[!]` — where the LL does *not* match, and why

1. **Mark IIb under-predicts** (~30 % of hull need — oQ-18) — **resolved as
   an equivalence** (plan 15.2): Shaw's form k·(q/p)²·V²·sin²C with the actual
   turning point IS the flat-plate law (algebraic identity, locked); the
   slip-limit variant under-predicts (negative thrust) — the measured
   kinematics are the truth. **Task I (the blade layer, committed c7a6e97):
   the (q/p)² law is now implemented as the time-stepped ll/blade.py with
   the TURNING_POINT switch** — 'actual' (default) keeps the identity by
   construction (locked by ll/tests/test_blade_law.py); 'geometric' (the
   appendix d-formula, OFF) was tested and contradicts the measured Table
   9.6 kinematics — net negative at our points. **The cant is now in**
   (plan 16.1, Gate 7):
   the Mark IIb prop fraction 0.30 → 0.51–0.54 (~1.7×); the residual is the
   A5 area gap + the slip assumptions, quantified by the 'as-designed'
   scenario (area 1.3× + slip 1.2 → the chain's 9.7 kt). Locked by test:
   no silent tuning.
2. **Tightest-turn 360° time** — **closed by the sway DOF** (plan 15.3):
   the physical CLR restoring moment + the C3 lever decomposition (4.8 →
   1.8 m) + the ship's effective Ω 3.2e6: D = 67.8 m ✓ and the speed
   halves ✓; t_360 = 98 vs 128 s — **an OPEN discrepancy with no known
   cause**: the turn build-up (its share ~2 s, plan 17) and the yaw-
   induced oar/water differential (its share ~1 s, plan 18) were both
   implemented, measured and ruled out — real, right-direction, minor
   (~1–2 s of the ~30 s gap), their complexity reverted; the hold
   fraction, W' fade and sway physics are all in. The linear yaw-damping
   hypothesis (register C1's units hint — a kg·m²·s⁻¹ damper) was
   **tested and failed (task H, committed c7a6e97)**: any k that closes
   t_360 (98.2 → 128 s) grows every turn diameter out of its gate band
   (G1 111.5 m +24 %, F1 153.7 m +31 %, tightest 84.6 m +25 %) — the
   mechanism is forced (linear damping lowers ω everywhere, D = V/ω
   grows); the term `YAW_LIN_DAMP` sits OFF (0.0) with the negative
   result in its docstring. The discrepancy stays open with the tested
   hypothesis recorded — the one remaining Level-1 open physics item.
   The drift
   emerges (−2.2°) and the lateral velocity damps.
3. **Sprint t_drive gap** — **closed**: t_drive(44.5) = 0.371 s calibrated
   to the trial (8.30 kt at 130 oars, in the 8.2–8.4 band); the assumption
   is now a pinned, tagged schedule entry (register A8).
4. **2-parameter CP tension** — **resolved without a model change**: the
   ¾-NM's 4–5-kt tailwind (≈0.5–1.5 kW) puts the crew's true power at
   91–100 W/man, and W′ = 5 kJ predicts 4–7.5 min at that level — the
   observed 6.5 min sits inside the wind-uncertainty band (register D7).
5. **F/G per-turn raw data** unavailable (1990 report is print-only) —
   diameters validated, not cell-by-cell.
6. **t_rise = 0.15 s** provisional (register D10); **the C3 lever
   decomposition is in** (4.8 → 1.8 m — the physical oar-race arm, with the
   drift component folded into the sway calibration, plan 15.3); **per-tier
   factors done** (Gate 6: the thalmian head-room power factor + the feather
   clamp; sprint overshoot closed);
   **Mark IIb** diagnosed as the ch.9 turning-point (q/p)² blade law —
   implementation is the next blade-physics layer.

## 8. Status

- 103 checks green: the command language (19), the LL gates 1–8 (56), the
  research chain locks (12), the HL basics (9), the harness machinery (6).
- Every validated anchor the LL touches lands within 1–5 %, with outliers
  explained by documented physics or locked as open items.
- The LL is realistic *to the limit of the research chain* — and it knows
  where that limit is (this ledger is that knowledge).
- The HL (Phase 2) is validated against the LL through the shared harness —
  the equivalence record, the measured divergences and the HL-loose list:
  §9. The complete coverage inventory — every scenario's status and its
  path to full validation — is §10; the work plan and the definition of
  done are plan §21.

## 9. The HL vs the LL — the pair equivalence (Phase 2, through the harness)

The fast ship is validated *sideways* against the LL (plan §6, Level 2): one
command stream, both simulators, same starting state and event semantics
(`harness/run_validation.py` — the whole record reproduces with one
command). Calibration: `calib-2026-08-15-c7a6e97` (generated by
`hl/calibrate.py`, the LL protocols, LL commit c7a6e97; the residuals live
in the calibration file; the loop calibrate → validate → adjust ran six
rounds — each round found and fixed a real measurement/protocol bug, see
§9.3; the annotated per-row tolerance sources: `harness/equivalence-
annotated.md`).

### 9.1 The script set (plan §20) — Level-2 first tolerances

| script | mean speed | fatigue consumed | t_3nm | position sep | verdicts |
| --- | --- | --- | --- | --- | --- |
| long_cruise (20 min, steady) | +0.0 % | −0.021 pts | — | 0.015 NM | PASS |
| sprint_turn (25 min, 2 turns + bursts) | +1.0 % | −0.005 pts | — | 0.096 NM | PASS |
| wprime_burst (30 min, 2 bursts + recovery) | +0.5 % | −0.005 pts | — | 0.022 NM | PASS — the sway-transient closure (the settled cells + the V-ramp kick + the slow decay) |
| cruise_turn.txt (the sample script) | −0.0 % | −0.005 pts | — | 0.050 NM | PASS |
| three_nm_cruise (35 min, the 3-NM gate) | +0.0 % | −0.005 pts | −0.0 % | 0.043 NM | PASS — the t_3nm gate's first number |
| tempo_loss (exhausted sprint) | −0.2 % | −0.013 pts | — | 0.010 NM | PASS — the rate_eff row (the LL shows no tempo loss at the anchors; measured) |

### 9.2 The turn scenarios — D = |y| at 180° within 5 %

| scenario | D LL | D HL | diff | t180 LL / HL |
| --- | --- | --- | --- | --- |
| g1 (full rudder @ 6 kt) | 89.5 m | 90.2 m | +0.8 % | 54.0 / 49.0 s |
| f1 (22.5° @ 6 kt) | 116.8 m | 117.3 m | +0.4 % | 70.0 / 63.0 s |
| tightest (one side holds + full rudder) | 67.7 m | 66.9 m | −1.2 % | 51.0 / 49.0 s |
| oar-hold / oar-back (no rudder) | 127.0 / 127.0 m | 125.9 / 125.9 m | −0.8 % | 98.0 / 94.0 s |

### 9.3 The measured divergences — and why each stays (the HL-loose list)

The calibration loop (calibrate → validate → adjust) ran three rounds and
found three real protocol bugs along the way, each fixed by re-measuring,
never by tuning:

1. **The spoude-drain protocol** — a fixed-window slope measured ~0 W when
   the settle had already emptied the tank (the drains at 36/44.5 spm);
   fixed with a least-squares slope over the unsaturated window, and the
   spoude drains measured from the rest start (the scripts' context — the
   drain runs ~6 % higher there).
2. **The sub-spoude drains** — steady 36 / fast 32.3 drained (measured
   +19.1 / +16.2 W) but the low-preset protocol read 0 (the tank emptied
   during the settle); the direction probe (30 s from full) picks the right
   preset. The 44.5 spm levels turned out to drain hard (+71.8 steady /
   +103.6 fast W/man) — the bootstrap's 'balanced' reading was the
   empty-tank artifact.
3. **The oar-family frac-0 point** — must be helm midship; the LL treats
   an applied 0.0 helm as a residual 0.14-coefficient rudder (127.0 m vs
   104.6 m measured).
4. **The drift floor** `[x]` — the LL's symmetric crew carries an untrimmed
   lateral kick (the blade's net Fy, test_trim: heading drift < 15° in
   5 min; measured steady −0.016 rad/min at cruise). The HL is the trimmed
   ship (a helmsman would trim it, and the trials' turns were helmed), so
   the position separation grows at ~0.017 NM/min on straight runs —
   measured and locked by the harness tests (0.1–0.25 NM over 10 min), not
   matched silently. Re-open only if a scenario demands the untrimmed
   drift.
5. **The turn-heavy scripts' mean speed** `[!]` — sprint_turn +1.5 %,
   cruise_turn +1.2 % vs the 1 % gate, both quantified by the bins:

- the back-tail transition (cruise_turn's 1440–1620 s, +23 % in the bin):
  the LL's rate change re-plans the oar and the back-brake drives a deep
  undershoot with a ±50 % low-speed ripple; the HL's smooth chase (target
  0.91 kt, tau 20 s) cannot represent per-stroke transition dynamics — the
  HL's domain boundary, not a table error;
- the turn deceleration (sprint_turn's two helm turns): the LL loses ~0.3 kt
  more per turn (the sway-coupled lateral dynamics — the applied-rudder
  drag is in; the residual is the part the chase cannot absorb).

The per-state tau or a brake-aware decay are the named triggers if a
scenario demands the low-speed fidelity; until then the divergences are
measured, bounded and documented.

6. **The tank nets** `[x]` — drain/refill W/man measured at the anchor levels
   with the direction-probed, cap-safe protocol; the consumed-fatigue metric
   (the depletion integral, not the brittle endpoint W_frac) is the gate:
   −0.005 pts across all scripts (long_cruise −0.021 — the net's ±6 %
   phase-spread, within the measured residual).

## 10. Coverage map — what is validated, what is open, what is not

The complete inventory of validation scenarios and their status, with the
path each row takes to full validation (the work plan and the definition of
done: plan §21). Status legend: **validated** = inside its band, locked by a
test; **marginal** = outside its band, explained and locked; **failed** =
outside, open; **never exercised** = the gate has not produced a number;
**no anchor** = the trial data does not exist; **scoped** = outside the
current phase (Phase 4/5) or HL-loose by design with a named trigger.

### 10.1 Level 1 — real-world data vs the LL

| Scenario | Status | Ref | Path to full validation |
| --- | --- | --- | --- |
| One-oar physics at the 4 Table 9.6 points | validated (< 0.5 %, forces 224/208 N) | §1 | — |
| Cruise anchors, hull = 1.0 (28.8 → 7.2, 36 → 8.2 kt) | validated (+0.3 % / −2.7 %) | §2 | — |
| ch.7 cruise triple 25.5/32.3 (Mark II hull refs) | tension documented (task G: @hull=1.08 → −2.5 / −4.6 / −6.1 % vs 7.0/7.5/8.0; the gap grows with rate — the LL's rate curve is flatter than the ch.7 triple) | §2 | Table 9.6 hull=1.0 anchors remain the acceptance; the ch.7 triple is not reproducible — recorded, no further work |
| Sprint 44.5 spm (130 oars) | validated (trial 8.2–8.4 inside the 7.9–8.8 bracket; t_drive pinned, A8) | §2 | — |
| Rudder turns G1 / F1 | validated (+0.3 % / +4.9 %) | §3 | — |
| Tightest turn (one side stops) | marginal (+9.2 % vs the 62 m anchor) | §3 | documented; the anchor is the trial's 62 m |
| 360° turn time | open (locked test) — 98.2 vs 128 s; the linear yaw-damping hypothesis tested and FAILED (task H): any closing k blows G1/F1/tightest out of their bands (+24/+31/+25 %); `YAW_LIN_DAMP` OFF with the negative result recorded | §7.2 | the sole remaining Level-1 open physics item — stays on the open list with the tested hypothesis |
| Oar-only turns, backing, asymmetric fatigue | no anchor (oQ-3 — the 1990 report is print-only) | §3/§4 | physical consistency + the LL↔HL agreement are the acceptance; the anchors cannot exist |
| Physiology: sustainable envelope, sprint burst, rest start, tempo loss | validated | §4 | — |
| Oar inertia: catch spikes, handiness 1.85×, couple, drive time 0.43 s | validated | §5 | — |
| Mark IIb equivalence, cant, sway (Gates 6–8) | validated — oQ-18 resolved as physics (task I): the (q/p)² law at the actual turning point is an algebraic identity with the flat-plate law (locked by test_blade_law.py); the geometric variant tested and ruled out; the residual is the A5 area gap + slip | §6/§7.1 | — |
| Cross-cutting chain checks (couple, P = 7.43·r origin, R&W, F/G ≤ 7 %) | validated | §6 | — |

### 10.2 Level 2 — the LL vs the HL (calibration `calib-2026-08-15-c7a6e97`)

| Scenario | Status | Ref | Path to full validation |
| --- | --- | --- | --- |
| Turn diameters, all 5 scenarios | validated (±1.3 % max vs the 5 % gate) | §9.2 | — |
| Cruise means (long_cruise, wprime_burst) | validated (+0.0 % / +0.5 %) | §9.1 | — |
| Fatigue consumption, all 6 scripts | validated (−0.005 pts) | §9.1 | — |
| Mean speed, turn-heavy scripts (cruise_turn, sprint_turn) | validated — closed by the per-state τ (E) + the turn-deceleration term (F): −0.0 % / +1.0 % vs the 1 % gate | §9.1 | — |
| Position after course changes | validated on all 7 scripts (0.010–0.096 NM vs 0.1) — the §21.3 decision (the bias-yaw) landed and the wprime closure landed: the drift cells are the settled values (300-600 s; the 20-60 s window is the sway transient, 2-3x the settle), the V-ramp kick-transient is a measured curve, and the drift-scale decay is the measured |omega|-dependent tau | §9.3.4 | — |
| Time to 3 NM | validated — the first number: −0.0 % (three_nm_cruise, 35 min) | §6 | — |
| Settled stroke rate within 1 spm | validated — the rate_eff row on all 6 scripts (±0.0 spm); the tempo-loss curve measured: the LL shows NO tempo loss at the anchors (identity, recorded) | §6 | — |
| Numeric pressures / helm fractions between the anchors | interpolated, not gated | §19.1 | the gates are defined at the schema anchors; the interpolation residuals are recorded, not gated (scope decision, plan §21.3) |
| Waves, per-side pressure steering, exhausted-side yaw, tempo loss, Mark IIb rig, old-fir fleet, reduced crews, rates < 8 spm | scoped (Phase 4/5 or HL-loose with named triggers) | §19.1 | re-opened only when a scenario demands it (plan §21.3) |
