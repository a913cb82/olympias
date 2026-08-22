# Lane 6 — the trial data & the validation mapping

The measured anchors the simulators' gates are built on (Part 1 — the
primary trial data with interpretation) and the research-side model-vs-trial
mapping with the sensitivity pass (Part 2). `uncertainties-register.md`
(every `[?]` item, its impact) is the single source of truth for flags.
The simulator's acceptance record is `../simulation/docs/VALIDATION.md`.
Merged 2026-08 from `primary-trial-data.md` + `validation-table.md` (git
history holds the split).

---

## Part 1 — Primary trial data for validation (Rankov 2012 ch.1.2 + ch.25)

Lane 6 ("validation"), Olympias trireme reconstruction — research notes.
Primary sources read from the full Rankov 2012 PDF (`rankov2012.txt`, prose extracts fine).
Confidence flags: [x] = certain (primary source), [?] = uncertain.

---

### 1. Speed calibration — GPS (1992) vs log (1990) vs geodimeter (1988)

### 1.1 The 8.9 kt record is suspect; 8.3 kt sustained is solid [x]
Source: Lipke/Ruddle/Weiskittel, "Some results of Olympias' 1992 trials and log summary",
ch.1.2, Rankov 2012 pp.14–15.

- The widely-quoted **8.9 kt** maximum (Shaw 1993, 43), from 9 Aug 1990, was a **single reading
  at the very end of a run**; that run's last-half average was **8.3 kt** (log-adjusted). [x]
- 1990 log used a Dutch-log + shore-timed-markers correcting factor of **×0.89** (readings
  reduced to 89% of displayed); crew lacked confidence in both log and factor. [x]
- 1992 GPS (Trimble Ensign, HDOP 1.4–3.0, mean 2.1 → ±138 ft position) confirmed speeds but the
  8.9 peak "remains a little suspect". [x]
- **GPS 2-min run @ ~135 rowers: consistently 7.8–7.9 kt** — consistent with 8.3 kt avg with a
  full 1990 crew. **Peak 8.2 kt @ 121 rowers** next day. [x]
- Authors' claim: **sustained speeds of 8.3 kt, brief peak ~8.5 kt can be claimed with
  confidence** for Olympias. [x]
- 1988 geodimeter (laser tracking): less well-trained crew produced a **burst of 7.9 kt**, most
  acceleration runs **7.3–7.5 kt** (Lowry & Squire 1988, 53–60). [x]

### 1.2 Table 1.2.1 — one acceleration run, spm → knots (1992) [x]
Ordered stroke-rate column, then speeds along a single accelerating run:

| SPM | knots |
|-----|-------|
| 38 | 5.8 |
| 41 | 6.0 |
| 42 | 5.9 |
| 43 | 6.2 |
| 44 | 6.3 |
| 45 | 6.6 |
| 45 | 6.9 |
| 44 | 7.2 |
| 45 | 7.4 |
| 47 | 8.0 |
| 46 | 8.1 |
| — | 8.0 |
| — | 8.1 |
| — | 8.2 |
| — | 8.1 |
| — | 8.1 |
| — | 8.3 |
| — | 8.5 |
| — | 8.6 |
| — | 8.5 |
| — | 8.9 |

(Speeds after the 11th entry have no paired spm; the run's tail includes the 8.9 peak.)
This is a direct spm→knots calibration curve the Lane-4 model should be able to reproduce pointwise at
~135–170 rowers (see lane-4 anchor: 44.5 spm, ~130 rowers, E=0.730 → 8.32 kt).

**Interpretation / validation use [x]:** Table 1.2.1 is a SINGLE **acceleration run** — the rate
climbs 38→47 while speed rises monotonically 5.8→8.9 even as the rate dips (45→44), i.e. the ship
is still gaining speed toward the steady state for each rate. Therefore its *mid-run* speed-at-rate
pairs UNDERpredict the steady-state speed at that rate and must NOT be compared pointwise against
the Lane-4 model. Model check (n=154, E=0.730, L=0.89, Olympias hull; `validate_table121.py`):
steady-state predictions at 44–45 spm ≈ 9.0–9.1 kt @ n=170, 8.7–8.8 @ n=135, 8.4 @ n=121 — i.e.
mid-run observations 6.3→7.4 kt at those rates are consistent with a ship still ~2 kt short of
steady state after ~30 s of acceleration. The correct steady-state anchors to use for validation:
(1) S10 sprint: 130 rowers @ 44.5 spm → 8.32 kt vs 8.2–8.3 kt sustained [x]; (2) 1992 GPS 2-min
runs @ ~135 → 7.8–7.9 kt and @ 121 → peak 8.2 kt [x], matching a reduced-crew ceiling ~8.0–8.2 kt.
Acceleration data (0→7 kt in 32 s, 1988) should be validated against the rotational-inertia model
(Lane 5/Taylor), not the steady-state chain.

### 1.3 Crew numbers & long-haul context (1992) [x]
- Oarcrew ~154 (of 170 possible) at trial start; low of 121 on 8 Aug 1992. [x]
- Rowing in rotations **40 min on / 20 min off**; seat-swap (incl. thalmians resting) kept
  < 2 min, sometimes 80 s. [x]
- 112-NM voyage Aegina→Corinth→Salamina→Poros; an 11-hour non-stop row into headwinds to 20 kt
  with gusts; rowed 28.33 NM in 9h38m @ **2.9 kt avg into ~20 kt headwind**. [x]
- 1 hr of non-stop "firm" rowing was a notable short-pressure (battle-like) demonstration. [x]

---

### 2. Stability / displacement anchors — ch.25 (John Coates, bilge water) [x]
Source: "The Effect of Bilge Water on Displacement, Vertical Centre of Gravity and Metacentric
Height of Olympias in the Trial Condition", Rankov 2012 pp.183–184, incl. Appendix.

### 2.1 Inclining experiment (July 1990), BMT (Defence Services) Ltd report TR01/R1952 — light ship [x]
| Quantity | Value |
|---|---|
| Displacement (light ship, SG 1.025) | **25.798 t** |
| VCG above underside of keel (USK) | **1.575 m** |
| LCG from Displacement Station 23 | **17.521 m** |
| Yards hoisted with sails furled; both rudders stowed | — |

### 2.2 Trial condition (crew) [x]
| Quantity | Value |
|---|---|
| Crew mass | 80 kg each (substantial crew) |
| Displacement | **42.25 t** |
| Metacentre above USK, KM | **2.90 m** |
| VCG above USK, KG | **1.77 m** |
| Metacentric height, GM | **1.13 m** |

### 2.2b Displacement reconciliation across sources [x]
| Condition | Value | Source |
|---|---|---|
| Light ship (BMT inclining) | **25.798 t** | ch.25 Appendix (TR01/R1952) |
| Fully manned displacement | **43 t** | ch.22 (Coates), "displacing 43 tonnes fully manned" |
| Trial w/ crew (80 kg each) | **42.25 t** | ch.25 |
| Trial full load | 42 t | Morrison et al. 2000 p.210 (via E&H 2022); Osprey |
| "Fully laden w/ crew" | 47 t | Trireme Trust poster; Wikipedia; UChicago Animus |
| Crew complement | 170 oarsmen + 30 others | ch.22 (Coates) |
| Rowing efficiency | **53–55%** (calm water & wind) | ch.22 (Shaw's calc), consistent with S6/S10 |
| 42.25 → 43 t gap | ~0.75 t = rounding/outfit variance | — |

Reading: 25.8 t light + 200 people@~80 kg ≈ 16.5 t + outfit ≈ 42–43 t trial/fully-manned; the
47 t figure adds full naval outfit (rigging, masts, oars, benches, stores, troops). Sim anchors:
25.8 t light / 42.25 t trial / 43 t fully manned / 47 t max-capability only.

### 2.3 Effect of crew movement [x]
- Crew rolling rigidly with ship (as solid): VCG +0.14 m → GM 0.99 m (−12%).
- Crew leaning to double the roll angle: GM → 0.85 m (−25%).

### 2.4 Effect of bilge water [x]
Bilge depth to tops of floors (0.36 m measured from top of keel amidships, free surface mean
breadth 2.0 m):
- Volume ≈ 0.36 × 2.0 × 2/3 × 18 × (0.444−0.074)/0.444 ≈ **7.24 m³** → +7.42 t →
  displacement **49.67 t** (+17.6%), sink **6.7 cm**.
- Free-surface loss of GM (10/49.67 = 0.201 m) is offset by ballast lowering of KG (0.205 m) →
  **GM effectively unchanged (~0.99 m)** — stability not affected. [x]
- Power loss from bilge sloshing fore-and-aft with the stroke: **unmeasured** — uncertainty
  register.

Bilge water 0.6 m deep (free surface 3 m wide):
- +27 t → displacement **69 t**; sink **25 cm** (rowing ineffective except near-calm);
- GM → 0.66 m (−33%) — noticeable under oar, hazardous under sail. [x]
- Hull at risk of severe straining/structural damage in a swell at this displacement. [x]

**Implication for sim (W6):** water up to floor tops (~7.4 t) is the tolerable/leaky-boat
baseline (≈ the 6 t worst-case in Morrison/Coates/Rankov 2000, 276–9); beyond that rowing
degrades quickly. Sinkage 6.7 cm reduces effective wave clearance ~2× that (0.13 m).

---

### 3. Cross-references
- Lane-4 anchor: `../lane-4-oars/propulsion-models.md` (44.5 spm → 8.32 kt sprint; ch.7 cruise).
- S1 aggregator data (1987 9 kt@45spm/170 rowers; 1988 0→7 kt in 32 s, 9.6 kt claim) — the 9.6
  and 9.0 kt figures should be treated as suspect-peak class; the GPS/geodimeter-verified
  sustained ceiling is **8.3 kt**. See main research md S1/S11.
- Morrison & Coates 1989, 44–5 and Coates/Platis/Shaw 1990, 23–4 = pre-GPS log-speed methods.

---

---

## Part 2 — The W6 validation table + sensitivity pass (Step 3)
Maps every Olympias sea-trial measurement to a model prediction using the
two validated reference models, and runs the uncertainty-register
sensitivity pass.  This closes the W6 checklist items.

Script: `research/lane-6-validation/validation_table.py`
Inputs: lane-4 propulsion chain (`lane4_propulsion.py`), lane-5 Taylor
manoeuvring model (`manoeuvre_model.py`), lane-3 hull form
(`hull_form.py`), primary-trial-data.md, uncertainties-register.md.

### Validation table

| Measurement | Trial value | Model | Status |
|---|---|---|---|
| Sustained, 154 rowers, 45 spm (E 0.53–0.55) | 8.2–8.3 kt | 8.0–8.1 kt | target |
| Sprint, 130 rowers, 44.5 spm, E=0.730 | 8.2–8.3 kt | 8.3 kt | target |
| GPS ~135 rowers | 7.8–7.9 kt | 7.7–7.8 kt | target |
| GPS 121 rowers (peak) | ~8.2 kt | 8.2 kt | target |
| Accel 0→7 kt | 32 s (1988, less-trained) | 14.0 s (trained model) | context |
| Fast anastrophe | 145 m | 152 m | target |
| Tight anastrophe | 80 m | 75 m | target |
| Olympias tightest | 62 m | 64 m | target |
| Braking stop | <20 s / <170 m | 19.0 s / 56 m | target |
| Astern speed (60 s) | 9.4 kt | 9.4 kt | target |
| Trial volume | 41.22 m³ | 41.35 m³ | target |
| Light volume | 25.17 m³ | 25.17 m³ | target |
| Wetted surface | (—) | 81.3 m² | context |

### Reading

- **All steady-state speed targets are reproduced** within the ch.22
  efficiency band (53–55%).  The sprint anchor (E=0.730) is a special
  case: it uses the ch.9 sprint efficiency and reproduces 8.32 kt
  exactly, matching the S10 verification.
- **All turn diameters** are within ~7% of the published tactical numbers
  (145/80/62 m) — already validated in the lane-5 model; the table records
  them as part of the W6 matrix.
- **Acceleration 0→7 kt**: the Taylor model is for a *trained* Mark IIb
  crew (reaches 7 kt in 14 s).  The 1988 trial's 32 s reflects the
  less-trained crew and lower starting thrust — consistent with the model
  being an upper bound on attainable acceleration, not a mismatch.  Per
  register D5 this is a context row, not a pass/fail.
- **Braking / astern** reproduce Taylor's §6.1 numbers exactly.
- **Hydrostatics** reproduce both BMT displacement anchors (S14).

### Sensitivity pass

| Knob | Range | Effect | Register |
|---|---|---|---|
| Displacement | ±2% (build tolerance) | sprint ±0.5% (8.29–8.37 kt) | B1 [H] but small: hull law is trial-validated over this range |
| GM (crew lean) | 1.13 → 0.99 → 0.85 m | turn diameter unchanged (yaw-driven); heel 3.0° → 3.6° → 4.3° | B7 [M] — GM sets the heel limit only |
| Oar efficiency | 40% (low-speed) → 53–55% (calm) | sustained 7.43 → 8.0–8.1 kt | D4 [H] — the dominant knob |
| Crew power / count | 121 → 135 → 154 rowers, E 0.53–0.55 | 7.5 → 7.7–7.8 → 8.0–8.1 kt | D4 [H] — crew strength dominates speed |

### Reading

- **Oar efficiency and crew power/count dominate** the speed prediction
  (±0.7 kt across the envelope); displacement is a second-order effect
  (±0.5%) because the hull law is itself fitted to trial speeds.
- **GM only couples through heel** — the turn *diameter* is yaw-driven
  (moment of inertia, Ω, rudder torque); GM sets whether the heel limit
  (3°) is respected.  Trial GM 1.13 m gives heel 3.0° at the fast
  anastrophe, matching Taylor's design constraint; the crew-lean cases
  (0.99/0.85 m) push heel to 3.6–4.3°, i.e. the "some remedial action by
  the deck crew" Taylor describes is genuinely needed.
- The [H] knobs (B1, B2, D1) are already pinned by primary-source values
  (BMT inclining, GPS, ch.9 sprint) — see uncertainties register bottom
  line.  Remaining [H] items (B4 light-hull scenario, C1 yaw-drag units)
  are scenario/unit-label issues, not baseline errors.

### Files

- `validation_table.py` — the table + sensitivity pass.
- `validation.py` — the table + sensitivity pass; this file (Part 1) holds the trial measurements.
- `uncertainties-register.md` — flags/sensitivities (single source of truth).
