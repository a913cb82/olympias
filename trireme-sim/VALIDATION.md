# LL simulation validation ledger

The low-level simulator's acceptance record. Chain of trust:

    real-world trials  →  research chain (research/ + lane-6 validation)  →  LL

The LL is the oracle of the pair (plan §6): it must satisfy the repository's
validated numbers, and this file records exactly how it does — gate by gate,
anchor by anchor, including the honest mismatches (§7). Confidence flags
follow the repo convention: `[x]` = reproduced against a cited anchor,
`[?]` = provisional/labelled, `[!]` = known mismatch, documented.

## 0. Reproduce everything

```bash
V=../.venv/bin/python3        # from trireme-sim/
$V tests/test_parser.py       # command language ......... 19 checks
$V ll/tests/test_gate1.py     # one-oar physics ..........  7 checks
$V ll/tests/test_gate2.py     # surge hull ............... 12 checks
$V ll/tests/test_gate3.py     # turns ....................  9 checks
$V ll/tests/test_gate4.py     # rower physiology .........  8 checks
$V ll/tests/test_gate5.py     # oar inertia ..............  7 checks
# total 62 checks; every check asserts a documented anchor or a locked
# honest behaviour (e.g. oQ-18 shortfall, tempo loss).
```

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
| 44.5 spm, 170 oars | 9.02 kt | (trial was ~130 rowers) | crew-count effect, documented `[!]` |

Also: full per-step coupling agrees with the mean-force equilibrium < 1 %;
settles from 0.9·V\* within 300 s with no overshoot; stroke-frequency surge
ripple ≈ 0.2 kt (physical — the ship surges each drive); monotonic rate
curve; the oQ-18 Mark IIb shortfall reproduced exactly (locked by test).

## 3. Gate 3 — 170-oar turns vs the W5 trial anchors `[x]` (9 checks)

| Scenario | LL diameter | Anchor | Match |
| --- | --- | --- | --- |
| G1 full rudder @ 6 kt | 93.5 m | 89.4 m | +4.6 % |
| F1 22.5° @ 6 kt | 117.2 m | 111.9 m | +4.7 % |
| Tightest, one side stops @ 6.5 kt | 64.4 m | 62 m | +3.9 % |
| Oar-only hold / back (no rudder) | 92.7 / 54.5 m | no trial anchors (oQ-3) | physically consistent `[x]` |

Also: symmetric crew holds course (< 0.5° in 300 s); the rudder-turn diameter
is speed-independent (Q ∝ v², ω ∝ v — why the steady model worked); the
time-domain 360° time exceeds the steady estimate (deceleration — the W5
caveat mechanism, now integrated).

## 4. Gate 4 — rower physiology vs the trial endurance record `[x]` (8 checks)

| Behaviour | LL | Trial observation | Match |
| --- | --- | --- | --- |
| Sustainable envelope (steady pressure, 30 min) | W′ full, speed stable @ 25.5/28.8 spm | 7 kt = 79.5 W handle = R&W's 80 W P_crit | ✓ (to 0.6 %) |
| Sprint @ 44.5 spm spoude | bursts **~45 s**, then fades | trials sustained 8.2–8.3 kt ~45 s | ✓ (W′ = 5 kJ anchor) |
| Rest start | short stretched strokes, Fh ≤ 700 N, 7.2 kt @ 30 s | Taylor bulk law: 9 kt @ 24 s | physiology governs the start `[x]` |
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

1. **Mark IIb under-predicts** (~30 % of hull need — oQ-18; ch.9 notes Mark II
   needs ~×3.3 blade area). Locked by test: no silent tuning.
2. **Tightest-turn 360° time** ~73 s vs Morrison's 128 s — the real turn
   halved speed harder; needs the hold-water spectrum (oQ-4) + the trial's
   unknown rate.
3. **Sprint default 8.76 kt** vs 8.2–8.4 — a data gap: Table 9.6 has no
   44.5-spm effective-pull entry (register A8); the trial lies inside the
   model's t_drive bracket.
4. **2-parameter CP tension**: W′ = 5 kJ fits the 45-s sprint; the ¾-NM
   6.5-min run implies ~9.5 kJ (register D7) — a 3-parameter model would fit
   both.
5. **F/G per-turn raw data** unavailable (1990 report is print-only) —
   diameters validated, not cell-by-cell.
6. **t_rise = 0.15 s** provisional (register D10); **lever 4.8 m**
   decomposition open (register C3); **per-tier factors** v2 (plan §12.6).

## 8. Status

- 62 checks green across the 5 gates + the command language.
- Every validated anchor the LL touches lands within 1–5 %, with outliers
  explained by documented physics or locked as open items.
- The LL is realistic *to the limit of the research chain* — and it knows
  where that limit is (this ledger is that knowledge).
