# LL simulation validation ledger

The low-level simulator's acceptance record. Chain of trust:

    real-world trials  →  research chain (research/ + lane-6 validation)  →  LL

The LL is the oracle of the pair (the pair contract — simulation/AGENTS.md): it must satisfy the repository's
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
| Handiness | old-fir zygian / spruce **1.85×** | "old fir ≈ 2× spruce" (the pair contract — simulation/AGENTS.md) | ✓ |
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
  path — is §10; the definition of done is simulation/AGENTS.md.
- The 2026-08 critical review (methodology + coverage) is executed — the
  verdicts, the constants ledger and the open items in plain language: §11.

## 9. The HL vs the LL — the pair equivalence (Phase 2, through the harness)

The fast ship is validated *sideways* against the LL (the pair contract, Level 2 — simulation/AGENTS.md): one
command stream, both simulators, same starting state and event semantics
(`harness/run_validation.py` — the whole record reproduces with one
command). Calibration: `calib-2026-08-16-2e9f24c` (generated by
`hl/calibrate.py`, the LL protocols, LL commit c7a6e97; the residuals live
in the calibration file; the loop calibrate → validate → adjust ran six
rounds — each round found and fixed a real measurement/protocol bug, see
§9.3; the annotated per-row tolerance sources: `harness/equivalence-
annotated.md`).

### 9.1 The script set — Level-2 first tolerances

(calibration `calib-2026-08-16-2e9f24c`; the 2026-08 review wave: the
hold_frac re-measurement, the per-helm x per-pressure x per-rate
`turn_drag` curve, the settled-orbit asym nets, the two-timescale
yaw-build. Rows marked **annotated** are the measured HL-loose
boundaries with named causes — §11.2.)

| script | mean speed | fatigue consumed | t_3nm | position sep | verdicts |
| --- | --- | --- | --- | --- | --- |
| long_cruise (20 min, steady) | +0.0 % | −0.021 pts | — | 0.074 NM | PASS |
| sprint_turn (25 min, 2 turns + bursts) | +0.7 % | −0.005 pts | — | 0.148 NM | **annotated** — the turn-phase composition at the d-scaled cells + the fishtail's tau_exit pair (the curve-selection calibration's re-scan; §11.2) |
| wprime_burst (30 min, 2 bursts + recovery) | −0.1 % | −0.005 pts | — | 0.091 NM | PASS — the sway-transient closure holds |
| cruise_turn.txt (the sample script) | −1.9 % | −0.142 pts | — | 0.069 NM ✓ | **annotated** on the mean/fatigue only — the position row CLOSED by the K28 mixed-hold fix (0.194 → 0.069; §11.2) |
| three_nm_cruise (35 min, the 3-NM gate) | +0.0 % | −0.005 pts | −0.0 % | 0.017 NM | PASS — the t_3nm gate's first number |
| tempo_loss (exhausted sprint) | −0.1 % | −0.013 pts | — | 0.007 NM | PASS |
| zig-zag (out-of-sample, task T10) | +1.3 % | −0.000 pts | — | 0.136 NM | **annotated** — the reversal-mix composition at the curve-selection calibration (the pair re-scan 8.0/0.552; the mean +1.3 % stays; §11.2) |

### 9.2 The turn scenarios — D = |y| at 180° within 5 %

| scenario | D LL | D HL | diff | t180 LL / HL |
| --- | --- | --- | --- | --- |
| g1 (full rudder @ 6 kt) | 90.1 m | 90.6 m | +0.5 % | 55.0 / 52.0 s |
| f1 (22.5° @ 6 kt) | 118.3 m | 118.0 m | −0.2 % | 71.0 / 67.0 s |
| tightest (one side holds + full rudder) | 62.5 m | 62.5 m | +0.1 % | 52.0 / 50.0 s |
| oar-hold / oar-back (no rudder) | 102.7 / 102.7 m | 101.5 / 101.4 m | −1.2 / −1.3 % | 87.0 / 86.0 · 86.0 s |

The turn timing (t180) is gated at ±20 % (task T3 — the measured
timing-loose band: the HL is systematically fast in the D-matched turns;
the worst row is −11 % (the oar turns) after the K23 re-fit).

The *settled orbit* after the turn (the K20 finding, from the replay
UI's oar-back view — CLOSED by K22): all five turns track the LL's
settled orbit within 1.03–1.09× (mean D = 2V/|omega| over
t ∈ [250, 350] — g1 84.8/88.0 m, f1 111.2/114.2 m, tightest 58.6/62.7 m,
oar-hold 95.3/103.5 m, oar-back 40.4/43.0 m — the drained spiral
reproduced, §9.3 item 7).

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

7. **The oar-back settled orbit** `[x]` — CLOSED (K22). The LL's
   one-side-back turn: while W′ lasts it holds V ≈ 3.5–4 kt and
   D ≈ 90–103 m; then the tanks empty in sequence (the rowing side at
   ~68 W/man by t ≈ 90 s; the backing side only AFTER — its back stroke
   is flow-limited at speed, the peak-force cap degenerates it toward a
   hold-brake, p_ext ≈ 0 — and only the V collapse unlocks its pull,
   empty by t ≈ 180 s); V collapses into the multi-stable low-speed
   band (1.1–2.6 kt) and the back side's yaw moment keeps turning the
   slow ship, so D shrinks to 17–45 m (the drained spiral). The HL now
   reproduces it with measured pieces: the per-side tanks (the rowing
   side drains at the full-drain-mean fresh nets, the backing side is
   V-gated at v_flow 3.0 kt — the flow-limit unlock — and drains after;
   the sequence matches within ~10 s), the fresh chase target = the
   hold's settle (the fresh-phase identity — the identical V/W traces)
   with the fast hold-tau above v_collapse 1.5 kt and the slow tau_back
   below (the cruise_turn's drift context), and the speed-dependent
   orbit (d_oar_v: the drained cells measured 18.3 → 55.2 m at 1.0 →
   2.5 kt, the fresh plateau anchored to the half-circle gate cell).
   Result: the oar-back D −3.3 %, t180 −17 %, the settled orbit
   40.4/43.0 m (1.06× — was 2.56×), the depletion delta −0.006. The
   remaining residual: the LL's low-speed oscillation (the W′ refill
   cycles — the multi-stable family) is mean-tracked, not reproduced.
   Locked: `SETTLED_D_RATIO` (1.30 clean on all five turns) + the
   per-turn depletion gate in
   harness/tests/test_equivalence_gates.py.

## 10. Coverage map — what is validated, what is open, what is not

The complete inventory of validation scenarios and their status, with the
path each row takes to full validation (the work plan and the definition of
done: simulation/AGENTS.md). Status legend: **validated** = inside its band, locked by a
test; **marginal** = outside its band, explained and locked; **failed** =
outside, open; **never exercised** = the gate has not produced a number;
**no anchor** = the trial data does not exist; **scoped** = outside the
current phase (Phase 4/5) or HL-loose by design with a named trigger.

### 10.1 Level 1 — real-world data vs the LL

| Scenario | Status | Ref | Path to full validation |
| --- | --- | --- | --- |
| One-oar physics at the 4 Table 9.6 points | validated (< 0.5 %, forces 224/208 N) | §1 | — |
| Cruise anchors, hull = 1.0 (28.8 → 7.2, 36 → 8.2 kt) | validated (+0.3 % / −2.7 %) | §2 | — |
| ch.7 cruise triple 25.5/32.3 (Mark II hull refs) | **open-with-locked-test** — the LL's rate curve is flatter than the ch.7 triple: @hull=1.08 → −2.5 / −4.6 / −6.1 % vs 7.0/7.5/8.0 (the gap grows with rate); @hull=1.0 the 32.3 point is −5.3 %. The Table 9.6 hull=1.0 pair remains the acceptance. The cause is named (the LL's rate→power shape — per-man gross 110/129/152 W vs the chain's 115/145/180, the blade/kinematics chain, not the hull factor; the uplift correction moves the reference the wrong way) | §2 + §11.2 | open — the rate→power shape quantified and locked (`test_triple_lock.py`) |
| Sprint 44.5 spm (130 oars) | validated (trial 8.2–8.4 inside the 7.9–8.8 bracket; t_drive pinned, A8) | §2 | — |
| Rudder turns G1 / F1 | validated (+0.3 % / +4.9 %) | §3 | — |
| Tightest turn (one side stops) | **validated** — the hold_frac re-measurement (0.05 → 0.08, task T2): D 62.6 m vs the 62 m anchor (+1.0 %, was +9.2 %) AND the drained floor 3.22 kt ≈ the trial's halved 3.25 (was 3.54); the oar-hold/back rows re-measured (103.5 m, no anchor) | §3 + §11.2 | — |
| 360° turn time | open (locked test) — 98.2 vs 128 s; the linear yaw-damping hypothesis tested and FAILED (task H): any closing k blows G1/F1/tightest out of their bands (+24/+31/+25 %); `YAW_LIN_DAMP` OFF with the negative result recorded. The 128 s is trial-derived ('halves speed' → mean 2.91 kt → 2.81°/s) — the LL's turn-speed loss (−32 %) is the remaining target (T2); the turn build-up (~2 s) and the yaw/oar differential (~1 s) are ruled out (the verdicts: §7.2) | §7.2 + §11.2 | open — the cause quantified (the turn-speed floor: the LL's ~3.2 vs the trial's implied ~2.9 kt); a measured mechanism, or stays open |
| Oar-only turns, backing, asymmetric fatigue | no anchor (oQ-3 — the 1990 report is print-only) | §3/§4 | physical consistency + the LL↔HL agreement are the acceptance; the anchors cannot exist |
| Lateral drift angle during full-rudder turns (G1/G2) | open-with-locked-test — the LL's time-domain β measured (the corrected direction convention, K24): −1.50° (G1) / −1.18° (F1) / +2.24° (tightest) vs the reported 15°±2° / Taylor's 7.8° — the ~10× gap confirmed; the A_lat/clr adjustment options must hold the turns AND the wprime closure — no change made (the gap quantified, the row open) | register C5 + §11.2 | a measured A_lat/clr adjustment that holds all gates, or the row stays open |
| Start from rest (0→7 kt) | context, locked by test (M4) — the physiology-limited LL: 5.81 kt @ 30 s, 6.93 @ 60 s, 7.0 kt at 62.2 s — SLOWER than both references (the Taylor trained model ~14 s, the 1988 less-trained trial 32 s, register D5): a documented context gap (the force-ceiling/t_rise provisionality, D10), not a gate | §4 + §11.2 | the envelope is locked by `ll/tests/test_start_context.py` |
| Physiology: sustainable envelope, sprint burst, rest start, tempo loss | validated | §4 | — |
| Oar inertia: catch spikes, handiness 1.85×, couple, drive time 0.43 s | validated | §5 | — |
| Mark IIb equivalence, cant, sway (Gates 6–8) | validated — oQ-18 resolved as physics (task I): the (q/p)² law at the actual turning point is an algebraic identity with the flat-plate law (locked by test_blade_law.py); the geometric variant tested and ruled out; the residual is the A5 area gap + slip | §6/§7.1 | — |
| Cross-cutting chain checks (couple, P = 7.43·r origin, R&W, F/G ≤ 7 %) | validated | §6 | — |

### 10.2 Level 2 — the LL vs the HL (calibration `calib-2026-08-16-2e9f24c`)

| Scenario | Status | Ref | Path to full validation |
| --- | --- | --- | --- |
| Turn diameters, all 5 scenarios | validated (±1.3 % max vs the 5 % gate); the turn *time* (t180) is informational — the HL is systematically fast (oar-hold 98 vs 85 s, −13 %) — the yaw build-up fix + the t180 gate: §11.2. The settled orbit after the turn tracks within 1.09× on all five turns (the oar-back's drained spiral reproduced, §9.3 item 7) | §9.2 | — |
| Cruise means (long_cruise, wprime_burst) | validated (+0.0 % / +0.5 %) | §9.1 | — |
| Fatigue consumption, all 6 scripts | validated (−0.005 pts) | §9.1 | — |
| Mean speed, turn-heavy scripts (cruise_turn, sprint_turn) | sprint_turn **validated** (+0.7 % — the T4 turn-drag curve); cruise_turn **annotated** (−1.9 % — the back-tail boundary: the multi-stable low-speed state, §11.2; the named trigger: a brake-aware decay) | §9.1 + §11.2 | — |
| Position after course changes | clean on six of seven scripts (long 0.063, wprime 0.079, three_nm 0.063, tempo 0.001, cruise_turn 0.063 ✓ — the K28 mixed-hold fix closed it, zig-zag 0.010 ✓ — the K29 tau_exit re-scan); **annotated** on the sprint_turn (0.280 — the fishtail pair's cost, §11.2). The drift cells are dt-sensitive (the validation dt pinned — T7) | §9.3.4 + §11.2 | — |
| Time to 3 NM | validated — the first number: −0.0 % (three_nm_cruise, 35 min) | §6 | — |
| Settled stroke rate within 1 spm | identity at the anchors — the rate_eff row on all 6 scripts is ±0.0 spm by construction (the HL's achieved rate = the commanded rate; the LL shows NO tempo loss at 25.5–50 spm, measured incl. rate 50 — the loss region is rate 50 + exhausted as a start transient) | §6 + §11.2 | — |
| Numeric pressures / helm fractions between the anchors | interpolated, not gated — the sweep grid closed this: the interpolation midpoints measured + gated at the standard tolerances (the LL's steady curve is non-monotone — the 30-spm dip) | AGENTS (the HL) + §11.2 | the gates are defined at the schema anchors; the interpolation residuals are recorded, not gated (a scope decision) |
| Waves, per-side pressure steering, exhausted-side yaw, tempo loss, Mark IIb rig, old-fir fleet, reduced crews, rates < 8 spm | scoped (Phase 4/5 or HL-loose with named triggers) | AGENTS (the HL) | re-opened only when a scenario demands it |

## 11. The open items and the honest verdicts

The 2026-08 critical review (methodology + coverage) found 5 Level-1
items, 3 Level-2 items and 6 strengthening gates; the measurement wave
(M1–M8) and the task wave (T1–T10, the DAG's second half)
are complete, and the outcomes are the verdicts below (the process, in
detail, is in git). The §10 coverage map carries each row's current
status; this section is the ledger: every fitted constant with its
anchor, every verdict with its lock, and the open items in plain
language.

### 11.1 The calibration constants (measured, audited)

Every fitted constant, its anchor, its independence, and the
measurement that could replace it.

| Constant | Layer | Serves (anchor) | Independence | Replaceable by |
| --- | --- | --- | --- | --- |
| t_drive(44.5) = 0.371 s | LL | the sprint speed (8.30 in the 8.2–8.4 band, register A8) | speed only, not turns | the trial's stroke timing (print-only F/G report) |
| W′ = 5 kJ/man | LL | the 45-s burst duration (ch.9 four-run) | burst scale only | a direct VO2/W′ study (Phase 4) |
| hold_frac = 0.08 | LL | the tightest-turn D + the oar-hold family — RE-MEASURED (0.05 → 0.08) after the sway DOF changed the turn physics: closes the tightest D (62.6 m, +1.0 %, was +9.2 %) and lands the drained floor 3.22 kt ≈ the trial's halved 3.25 | oar-hold turns only | the F/G print report's hold spectrum |
| sway trio: Ω 3.2e6, clr 0.8, lever 1.8 | LL | G1/F1 D + approach t_360 | turns + the drift cells | Taylor Table 31.1 (the units caveat, C1) + Coates plans |
| tau_surge / tau_turn / tau_exit / drift_tau_exp | HL | the LL's settle/start/turn/burst paths (machine fits); tau_exit 10 s + drift_tau_exp 0.498 (K23 — the fishtail re-fitted as the scan over tau on the HL's RESPONSE vs the LL's decay, judged by the position rows it gates — the raw LL-fit ignored the HL's chase lag, making the effective decay ~1.7× too slow; the consistent (tau, exponent) pair ships together) | HL only | the same LL protocols (re-fitted, never hand-set) |
| the turn-drag curve | HL | the LL's turn V(t) per helm-fraction × pressure × rate (24 measured cells — the k falls with rate; the steady turns lose 3× more at the G1 anchor) | HL only | re-measured per protocol change |
| the yaw-build + the d-scales | HL | the LL's ω approach per family, chosen by the general curve selection (hl/curvesel.py: the nested families fitted by continuous least squares, the AIC per cell, the window-LOOCV stability reported, the acceptance gates as the arbiter — the sprint/zig-zag position check rejected the delayed family, whose 1-s hard freeze phases the turn positions) — the per-fraction helm cells + the per-scenario D-compensation d-scales (the target's scale, the chosen build untouched) | HL only | re-fitted from the LL's ω(t) |
| the static tables' fractional polynomials | HL | the d_oar_v's drained part is an FP2 (V^0.5, V^3 — the AIC'd powers over the standard set) fitted to the LL's oar-back samples, the plateau anchored to the d_oar(0) gate cell | HL only | re-fitted from the LL's samples |
| the asym nets + net_fresh | HL | the one-side-stopped legs' W′ drain: the drained nets ≈ 0 (the settled orbit, K13) AND the fresh nets (the full-drain means — tier W / time to empty, the W_frac min basis: spoude 36.3/51.8/68.3/85.7/126.0 at 25.5/28.8/32.3/36/44.5; back ≡ hold) | HL only | re-measured per protocol change |
| d_oar_v + v_flow + v_collapse | HL | the oar-family orbit vs speed (drained cells 18.3/25.9/41.5/55.3 m at 1.0/1.5/2.0/2.5 kt + the gate-anchored 103.5 plateau); the backing blades' flow-limit unlock at v_flow 3.0 kt; the drained-collapse/fast-drift boundary at v_collapse 1.5 kt (K22) | the oar turns only | re-measured per protocol change |
| the drift cells | HL | the LL's untrimmed yaw slope (pressure-dependent) | position gate only; dt-sensitive (the validation dt is pinned at 0.05) | re-measured per dt/protocol change |

### 11.2 The verdicts and the open rows

Every exit criterion included its regression lock; the suite is green
(141 checks, §8).

| Task | Verdict |
| --- | --- |
| T1 — the ch.7 triple | open-with-locked-test — the cause named: the LL's rate→power shape (per-man gross 110/129/152 W vs the chain's 115/145/180, the gap growing with rate; E_g flat 51.5–52.3 % vs the 53–55 % band — the blade/kinematics chain, not the hull factor; the speed-dependent uplift moves the reference the wrong way). Lock: `ll/tests/test_triple_lock.py` |
| T2 — the tightest turn + t_360 | part-closed — the hold_frac re-measurement (0.05 → 0.08) closes the tightest D (62.6 m, +1.0 %, was +9.2 %) and lands the drained floor (3.22 kt ≈ the halved 3.25); the t_360 stays open with the cause quantified: the turn-time = π·D/V̄ is the surge problem (the LL's turn-mean 3.8 kt vs the trial's 2.91; every mechanism measured and excluded — the W′ drain, the rudder drag, the hold brake, the linear yaw damping). The Rev F stationary-turn anchor adds the SECOND direction (register C7): the trials' partial-crew turn from rest at 27 spm = 3.5°/s vs the LL's 2.32°/s in-place (−34 %) / 1.06°/s one-side (−70 %) — the model is now too SLOW at low-speed partial crew (the t_360 is too FAST at full crew); the turn-speed family's envelope is measured, the mechanisms still open (the yaw build's reversal + the sway damping at low V) |
| T3 — the turn timing | the t180 row is gated at ±20 % (the measured timing-loose band: the HL systematically fast in the D-matched turns, the worst row −6 % after the K29 hold-decay re-measurement at the tightest's true usage (the HL's hold-state V collapsed too slowly — the wss = 2V/d ran 1.4× high in the first 10 s; the τ_hold is now a rate table 18.0 s @ 31.5 / 28.0 s @ 44); the K27: the oar-only d_oar_v is scaled by the rowing side's pressure — the LL's oar orbit grows as the effort falls (measured ~1/p_row), so the cruise's steady-rowed back leg no longer runs ~2× fast in yaw) |
| T4 — the turn-state drag | landed — the per-helm × per-pressure × per-rate curve (the k falls with rate) + the settled-orbit asym nets; the sprint_turn mean +1.0 % → +0.7 % |
| T5 — the bin gate | landed — `bin_max` 5 % / `bin_rms` 3 % in the comparator + the violation set; the cruise_turn's back-tail bin scoped |
| T6 — the sweep gate | landed — the PRESSURE_RATES extended to the midpoints (the LL's steady curve is non-monotone — the 30-spm dip) + the locked 6-cell sweep test |
| T7 — the dt-lock | landed — the drift cells are dt-sensitive (+120–1025 % at dt 0.1–0.2); the validation dt pinned at 0.05 |
| T8 — the drift angle | open-with-locked-test — the LL's time-domain β measured (the corrected direction convention, K24): −1.50° (G1) / −1.18° (F1) / +2.24° (tightest) vs the reported 15°±2° / Taylor's 7.8°; no A_lat/clr adjustment holds the turns AND the wprime closure — the gap is quantified, the row open |
| T9 — the rate_eff identity | measured, not assumed — the settled crew-level achieved rate = the commanded rate at all anchors incl. rate 50; the tempo loss is a start transient only |
| T10 — the zig-zag (out-of-sample) | landed + part-closed — found the steady-turns' deceleration (fixed by T4); the reversal-mix's position row CLOSED by the K29 tau_exit re-scan (0.186 → 0.010, clean — the sprint's row re-annotated 0.280 as the pair's cost); the mean +1.3 % residual stays (the annotated mean row). The Rev F Kempf overshoots add a NEW honest row (register C8): the LL's zig-zag (helm 22.5, steady 28.8, ±20° targets) overshoots 11.0° then 12.8–13.0° vs the trials' 8°/7° (+60–85 %) — the fishtail's reversal carries ~5–6° too far (the yaw momentum decays too slowly — the same family as the t_360's dynamics); locked in `ll/tests/test_revf_anchors.py` |

**The open rows (K19, the final acceptance)**: the t_360 (−23 %, the
named cause: the turn-speed floor — the trial's implied ~2.9 vs the
LL's ~3.2) + the Rev F stationary-turn second direction (−34/−70 %
at partial crew, low speed), the zig-zag overshoots (11–13° vs the
trials' 8/7 — the fishtail's too-long reversal), the drift angle
(1.4° vs 7.8–15°, the quantified gap), the ch.7 triple
(−2.5/−4.6/−6.1 %, the rate→power shape), and the Level-2
annotated boundaries (measured, named, locked): the cruise_turn back-tail
(mean −1.9 %, fatigue −0.142 — the multi-stable low-speed state: the
orbits 0.83–1.38 kt, the ±40 % per-stroke ripple, the V-dependent
refill cycles), the turn-mixed scripts' positions (sprint 0.148,
zig-zag 0.136 — the curve-selection calibration's pair re-scan). All
five turns PASS (±1.3 %; the tightest 62.5/62.5 — the +9.2 % row
closed); the t180's inside the ±20 % band (the worst row +2 % — the
continuous two-timescale fits tightened the old −6 %).

The curve-selection machinery (hl/curvesel.py) is the general recipe
for every fitted curve: the nested families by continuous least
squares, the AIC per cell (the deterministic oracle's parsimony), the
window LOOCV's stability report (the hand-window fragility gone), and
the acceptance gates as the final arbiter — the yaw-build's selection
is checked on the sprint/zig-zag position rows before acceptance (the
delayed family — the AIC's shape pick, rms ~0.001 — is gate-rejected:
the 1-s hard freeze phases the turn positions, the measured verdict
0.782 vs the two-timescale baseline's 0.304 NM), and the d_oar_v's
drained part is an AIC'd fractional polynomial (V^0.5, V^3).

The K28/K29 follow-up (the UI scenario survey's finds) is CLOSED:
the mixed-hold state (the helm + the OPPOSITE-side hold — the HL's
frac=0 dropped the helm and turned the wrong way; the measured
d_mixed_hold family: the turn is the HELM's throughout, the D 85 m at
5.65 kt growing to the 305.7-m settle at the 3.0-kt cap — the cruise's
position row closed 0.194 → 0.063) and the hold-state V-collapse (the
τ_hold re-measured at the tightest's true usage — a rate table 18.0 s
@ 31.5 / 28.0 s @ 44; the t180 gaps halved, the worst row −12 % → −6 %;
the tau_exit re-scan closed the zig-zag's out-of-sample position row
0.186 → 0.010 at the sprint's annotated cost 0.280).

The K20/K21/K22 follow-up (the replay UI's oar-back view) is CLOSED:
the oar-back's drained spiral and the per-side tank sequence are now
reproduced by measured pieces (§9.3 item 7 — the per-side tanks, the
v_flow-gated backing drain, the fresh chase target, the fast/slow
drained taus above/below v_collapse, the speed-dependent d_oar_v
orbit). The turn scenarios' settled orbits all sit within 1.03–1.09×
(the oar-back 40.4/43.0 m, was 2.56×) and the depletion deltas at
−0.004/−0.006 — locked in `test_equivalence_gates` (SETTLED_D_RATIO
1.30 clean on all five turns + the per-turn depletion gate). The
remaining residual: the LL's low-speed W′ refill oscillation is
mean-tracked, not reproduced (the multi-stable family, §11.3 item 4).

### 11.3 The open items, in plain language

The short version of §11.2 for a reader who wants the story, not the
ledger. Every item below is open with its cause measured and a named
suspect; none is unexplained, and each has a regression lock.

**1. The 360° turn takes 98 s; the trial's took 128 s (−23 %).**
The turn *size* matches (62 m ✓) — the *speed* doesn't. Turn time =
distance ÷ speed, and the LL's tightest turn runs at ~3.8 kt mean vs
the trial's ~2.9 kt (+28 %): the model's ship simply does not slow down
enough in the turn (its speed floor there is ~0.5 kt too high). Every
suspect was measured and excluded: the crew-fatigue drain (65 vs
68 W/man — not elevated), the rudder drag (makes the turn size wrong —
the wrong direction), the hold brake (fixes the size, not the speed),
the yaw damping (breaks everything else). Named suspect: the turn's
speed floor itself — the one number left unexplained. The Rev F
stationary-turn anchor (3.5°/s at 27 spm, Zygian+Thranite only, from
rest) adds the family's SECOND direction: the model turns 2.32°/s
in-place (−34 %) and 1.06°/s one-side (−70 %) — too SLOW at partial
crew, low speed, while too FAST at full crew. The envelope between the
two regimes is measured; the mechanism (the yaw build's reversal +
the sway damping at low V) is the next suspect for the whole family.

**1b. The zig-zag overshoots are ~13°; the trials' were 8° then 7°.**
The model's heading carries ~5–6° too far past the ±20° targets before
the reversed helm takes hold (11.0° first, then 12.8–13.0°): the turn's
momentum decays too slowly — the same yaw-reversal softness as the
t_360 family. The Kempf scenario (helm 22.5, flip at the ±20°
crossings) is locked in `ll/tests/test_revf_anchors.py`; the mismatch
is recorded, the cause named, the fix (if any) must preserve the
turn-size gates.

**2. The hull's drift angle in a hard turn is 1.4°; the trials report
8–15°.**
The model's ship doesn't lean sideways into its turns as much as the
real one. A fix would have to preserve the validated turn sizes AND
the straight-line drift behavior at once; none found, so the gap is
recorded with the candidates named (A_lat, the CLR position).

**3. The model's cruise power curve is flatter than the reference
chain (−2.5/−4.6/−6.1 % at the three cruise rates).**
At the same stroke rate the model's rowers deliver 4–15 % less power
per man than the ch.7 chain expects, and the gap grows with rate —
the model produces less thrust per stroke at high rates. The hull
factor is not the cause (a more accurate one makes the gap worse);
the named suspect is the oar/blade power chain at high rates.

**4. The cruise_turn script's slow-speed backing phase (mean −1.7 %,
fatigue −0.14).**
At the low backing speeds the LL's speed oscillates wildly (0.8–1.4 kt
depending on how the state is entered), so no single-value model can
match it. The fast sim's fatigue tank also behaves differently there
(the rowers' demand drops below the refill threshold — the tank
refills and re-drains, which the fast sim doesn't track).

**5. The one-side-back turn's long tail (oar-back) — CLOSED.**
The story (still true of the LL): the rowing side's tank empties in
~90 s, the ship slows, the backing blades unlock (they were
flow-limited at speed — the rowers could not pull them against the
flow), the backing side's tank empties by ~180 s, and the backing push
keeps turning the slow ship — the circle shrinks from ~100 m to
~20–45 m, wobbling on the energy-refill cycles. The fast sim now
reproduces it: per-side tanks (the same sequence), a speed-dependent
turn model (the circle shrinks with speed) and the measured fresh
targets and taus. The turn's size (−3.3 %), timing (−17 %), settled
orbit (1.06×) and fatigue (depletion −0.006) all sit inside the gates;
the only residual is the low-speed wobble itself — the fast sim tracks
its mean, not its oscillation (same family as item 4).

**5. The sprint_turn script's final position is 0.2 NM off.**
Small turn-timing differences (the heading drifts ~0.4 rad through the
turns) plus the wiggly turn-exit behavior add up over the 25-minute
script. The drift-model interpolation at the turn-mixed states is the
named suspect.

**6. The zig-zag stress-test script (+1.3 % speed, 0.32 NM position).**
A scenario we invented to stress untested combinations (quick helm
reversals). It shows the same turn-timing drift as #5, amplified by
the rapid direction changes — the fast sim's turn-exit model can't
follow the LL's oscillatory fishtail through a reversal.
