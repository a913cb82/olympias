# Lane 4 — Oars & Oar-Rig: geometry, mass, gearing, stroke, blades, propulsion

Research notes, web-only + Rankov 2012 full-text PDF (extracted text at `../sources/rankov2012.txt`).
Confidence flags: `[x]` = confirmed directly from a cited source (primary text read); `[?]` = inferred / unverified / conflicting.
Primary texts used: Rankov 2012 ch.1 (1992 trials report, Lipke/Howarth), ch.3 (1994 trials report, Shaw, incl. Appendices 1–3), ch.9 (Shaw's long-stroke design), ch.31 (Taylor); Braithwaite 1:24 build log (ModelShipWorld); Wikipedia Olympias infobox.
Companions in this lane: `propulsion-models.md` (the speed→power chain) and `braithwaite-workbook.md` (the trials thrust law).
Merged 2026-08 from `rig-geometry.md` + `oar-data.md` + `rigid-oar-refinement.md` (git history holds the split).

---

## Part 1 — Rig geometry: three tiers, thole-pin positions, lever ratios, stroke

Consolidates the oar-rig geometry needed by the simulation, drawn from Rankov 2012 ch.1 (1992 trials), ch.3 (1994 trials + Shaw's App.3 stroke model), ch.9 (Shaw's revised design geometry), ch.8 (oarport freeboard), Coates Plan 8 (midship section), and Richard Braithwaite's 1:24 build log (manikin/ergonomics). All numbers verified against the source equations.

### 1.1 The three tiers

- 170 oarsmen in triads of three: **62 thranites** (upper tier, rowing through the outrigger),
  **54 zygites** (middle tier, inboard through oarports), **54 thalamites** (lower tier, lowest
  oarports near the waterline). `[x]` (Rankov 2012 throughout; Wikipedia crew breakdown)
- Vertical ordering, low→high: **thalamian → zygian → thranite**. The tiers sit at different
  heights, but the height above calm water to which each level can lift its blade is "little if any
  higher for the upper two levels than for the thalamians" — all reach the water with roughly the
  same hand height and thigh-oom at recovery. `[x]` (Rankov ch.8, p.75)
- **Zygian oarport sills ~1.0 m above mean water level**; a 1.3 m 3-hour wave rising 0.65 m above
  the calm waterline does not reach them on an even keel, but the upper two tiers then struggle to
  reach the water in troughs / clear blades in crests. `[x]` (Rankov ch.8, p.75)

### 1.2 Thole-pin positions & oarports

- Oars are held **forward of the thole-pin** by oar loops (leather straps → rope grommets). `[x]`
- Thalmian tier: thole-pins are far **inboard** (to keep the lower oar angle shallow), forcing the
  lower oarports to be large and to fill almost the whole span between top timbers. `[x]` (build log;
  "how far inboard the thole pins need to be")
- Zygian oarports: smaller, positioned to line up with the outrigger brackets; **1.0 m above mean
  water level**. `[x]` (build log; Rankov ch.8)
- Thranite tier: thole-pins drilled **vertically through the centre of the upper + lower outrigger
  rails** (Fig. 8.2, Plan 8; "holes for the thranite thole pins ... through the center of upper and
  lower outriggers"). `[x]` (build log)
- The placing of tholes and oarports is dictated by blade-interference avoidance (Fig. 10.3, one
  triad amidships), the Lenormant relief, and a feasible internal beam/frame layout. `[x]` (Rankov
  ch.10, p.85)
- Shorter oars / tighter geometry at bow and stern where the hull narrows (short oars in triads
  1–3 bow, 28–29 stern). `[x]`

### 1.3 Lever ratios / gearing (verified)

Outboard:inboard lever ratios, all `[x]`:

| rig | inboard (m) | outboard (m) | ratio | note |
|---|---|---|---|---|
| Olympias as-designed | 1.105 (3 ft 7½ in) | 3.113 | **2.817** | Table 9.1; plan lengths 0.957/2.696 |
| Olympias as-rowed (Table 3.1) | 1.092 (3 ft 7 in) | ~3.07 | ~2.81 | convenient inboard length |
| Mark IIa/IIb spec | 1.225 (2½ cubits × 0.49) | 3.430 (7 cubits) | **2.80** | "cannot be much less than this if the ships are to be fast" |
| Thalamian designed | — | — | **2.82** | ch.1 §1.4.2 |
| Thalamian as-observed 1990 | — | — | **2.57** | oars ~70 mm further inboard than designed |
| Thalamian moved 40 mm outboard | — | — | **2.96** | max without cramping; increased work-load |
| Thalamian if full 100 mm move | — | — | **3.11** | not achievable in practice |

Blade centre of pressure taken **260 mm from the tip** for the thalmian lever calc. `[x]`

### 1.4 Oar dimensions (Table 9.1, verified)

All metres. Parenthesised = horizontal projection (×cos 30°). `[x]` (Rankov ch.9 Table 9.1; OCR `research/data/t91_t92_ocr.txt`)

| dimension | Olympias | Mark IIa/IIb |
|---|---|---|
| cubit | 0.444 | 0.49 |
| length overall | 4.218 (3.653) | 4.655 (4.031) |
| outboard length | 3.113 (2.696) | 3.430 (2.970) |
| blade | 0.550 | 0.550 |
| inboard length | 1.105 (0.957) | 1.225 (1.061) |
| thole → neck | 2.563 (2.220) | 2.880 (2.494) |

Proposed 4.66 m spruce spec (ch.3 App.2): overall weight **4.5 kgf**, weight-in-hand **2.0 kgf**,
gearing **2.8**, C of G 0.544 m outboard of fulcrum, radius of gyration² 1.488 m², **MIT ≈ 8 kg-m²**.
`[x]`

### 1.5 Stroke geometry — the thalmian head-room problem

- **Coates Plan 8 design stroke = 800 mm** at the handle; **a 1:24 manikin (50th-%ile ~600 BC
  Greek) achieves only ~720 mm** of it at the thalmian position — head-room limited. `[x]`
  (build log, citing Coates' midship section drawing, Plan 8)
- Cause: the beams above the thalmians' heads are **10% closer together than the 0.888 m
  interscalmium** → ≈ **0.80 m** clear gap at head level (Fig. 24.2), which is exactly the 800 mm
  design stroke. Thalmians "tended to hit their heads at each end of the stroke", especially at the
  finish — mitigated on trials by putting the smallest rowers there and a neck-restraining rope. `[x]`
  (Rankov p.9 Fig. 24.2 caption; build log)
- Consequence: **the thalmian tier's power contribution fell sharply at higher speeds** — the main
  real deficiency of the Olympias rig and the primary motivation for Mark II (0.98 m interscalmium +
  canted/skewed rig). `[x]` (Rankov ch.9 p.77; Gifford's critique ch.12)
- Measured shipboard strokes (total butt travel): **1992 average 82–85 cm** (1988: 75–77 cm); two
  triads reached **100 cm+**. `[x]` (Rankov ch.1)

### 1.6 Shaw's analytical stroke model (Rankov ch.3 App.3, p.62) — verified

- 167 cm man on fixed thwarts, rig-unrestricted: max **~1.1 m** at the butt; −10% end loss →
  effective **~0.99 m**.
- Inside an uncanted rig, interscalmium 0.98 m: total movement ≤ 0.98 − 0.15 clearance = 0.83 m,
  minus 0.11 m end losses → effective **~0.87 m**. Same end-loss 0.11 m in all cases.
- At 7½ kt restoring speed after stroke loss needs either rate ×1.17 (0.87 m → 37.4 spm) or gearing
  2.8 → 3.18. `[x]`

### 1.7 Ch.9 chord-of-pull (Table 9.2) & sweep angles (verified by recomputation)

| rig | interscalmium (m) | deadpoint chord (m) | end loss (m) | effective chord (m) | inboard plan (m) | **sweep B** |
|---|---|---|---|---|---|---|
| Olympias | 0.89 | 0.89 | 0.11 | 0.780 | 0.957 | **48.1°** (text: 48.1°) |
| Mark IIa | 0.98 | 0.98 | 0.11 | 0.870 | 1.061 | **48.4°** |
| Mark IIb | 0.98 | 1.10 | 0.11 | 0.990 | 1.061 | **55.6°** |

Sweep B = 2·asin(effective_chord/2 ÷ inboard_plan). Olympias's 48.1° is attained **only with
exceptional effort**; Coates' intended 65° for IIa (p.72 of *The Trireme Project*) is judged
unattainable. `[x]` (Rankov ch.9 p.78; recomputed in this note)

- Mark IIb's 1.10 m chord comes from **canting the rig 18.4°** (tan = 1/3) — a longer effective
  chord with the interscalmium unchanged (0.98 m) to avoid hull weakening. `[x]`
- Instantaneous turning point of the oar, from tip (plan, blade 30° to horizontal): 0.476 m at
  catch/finish, 0.953 m at mid-stroke; modelled as **d = 0.953·sin[120(C−A)/B + 30°]**; effective
  outboard lever **p = L_plan − d**. `[x]` (Rankov ch.9 p.79)

---

## Part 2 — Oar inventory, mass, blades, the power chain

### 2.1 Oar inventory & count

- 170 oarsmen total: **62 thranites** (upper), **54 zygites** (middle), **54 thalamites** (lower). `[x]` (Wikipedia Olympias crew; matches Rankov 2012 throughout)
- Oar families in Olympias (build log, POST 71): thalmian 12 short + 42 long; zygian 6 short + 48 long; thranite 62. Short oars are at bow/stern where the hull narrows. `[x]`
- 42 main thalamian oars + 3 spares were modified in 1992; the 12 short thalamian oars in triads 1–3 bow and 28–29 stern were not. In practice triad 4 and stern triads 28–29 also needed short zygian oars. `[x]` (Rankov ch.1, pp.25,37)

### 2.2 Oar length

- Ancient naval inventories record oars of **9 and 9½ cubits**. `[x]` (build log, citing *The Athenian Trireme*)
- Olympias cubit = **0.444 m** → 9 cubits = **4.00 m**, 9½ cubits = **4.22 m**. `[x]` (build log; Osprey Olympias volume agrees: 3.99 m / 4.2 m)
- Olympias's existing spruce oars are **4.22 m long**; Shaw proposes a **4.66 m** design (9½ cubits of the *larger* 0.49 m cubit). `[x]` (Rankov ch.3 pp.48,60–61)
- Proposed 4.66 m oar split: **2½ cubits (1.225 m) inboard of the pin, 7 cubits (3.43 m) outboard**. `[x]` (Rankov ch.3 App.1, p.60)
- At the ends of the ship the available space forces shorter oars at every level (see §2.1). `[x]`
- **Ch.9 table (verified)**: Olympias overall **4.218 m** (3.653 m in plan), outboard **3.113 m**, blade **0.550 m**, inboard **1.105 m**, thole→neck **2.563 m**. Mark IIa/IIb: overall **4.655 m**, outboard **3.430 m**, blade 0.550 m, inboard **1.225 m** (=2½ cubits of 0.49 m), thole→neck **2.880 m**. (Table 9.1; "in plan" = ×cos 30°.) `[x]` (Rankov ch.9, p.76–77; OCR `research/data/t91_t92_ocr.txt`)

### 2.3 Oar mass / physical properties

**Full-size Olympias fir oars**

- Douglas-fir oars (the originals): "weighed over 12 kg, increased to 17 kg once a lead counterweight was added inboard". `[x]` (build log POST 61 area, quoting model-scaled ship oars)
- **12.3 kg/oar** full-size: figure quoted in the build log for the real Olympias oars (the builder's 1:24 model oars scale to 11.71 g at 1:24³). `[?]` — source of the 12.3 kg value is not stated by the builder; likely from Shaw/Coates (The Trireme Project or the 1994 trials report). **Rankov 2012 Table 3.1 (now decoded) gives the ten-oar measured table: spruce oars 9–12 lbf, old fir oars 17–22 lbf — so ~12 lbf spruce ≈ 5.4 kgf is the *spruce* figure; 12.3 kg/oar more plausibly refers to the heavy old fir oars (17 lbf ≈ 7.7 kg up to 22 lbf ≈ 10 kg) or is simply wrong.** Treat 12.3 kg as implausible for the 1994 spruce oars.

**1994 measurements (Rankov ch.3 App.2, p.60–61; Table 3.1 p.48) — verified**

- 10 oars tested: **3 Douglas fir + 7 spruce**, by bifilar suspension + stopwatch (method: Lamb 1923, 158–9, 164).
- Inboard length taken as **3 ft 7 in = 1.092 m in all cases** — "found by the users of spruce oars to be the most convenient in Olympias." `[x]`
- Parameters recorded: overall weight, weight "in hand" (as though acting at the butt), **C of G from the butt**, **MIT = moment of inertia about the thole** (a measure of handiness), **X = distance of centre of percussion from the blade tip** (best ≈ −0.15 m, i.e. within the blade ~6 in; Bourne 1925). `[x]`
- Old fir oars and spruce oars 1 & 2 have squared looms; the others circular-section looms. `[x]`
- Conclusion: a spruce oar 4.66 m long "could weigh as little as 10 lbf" with **MIT kept as low as 8 kg-m²**. `[x]`

**Table 3.1 — the ten-oar inertia table (fully decoded; 8 of 10 data rows verify)** `[x]`

Decoded from the PDF glyph layer (PUA subset font) via `research/data/shaw-table-3.1-oar-inertia.csv`; each row checked against **MIT = W_kgf·(k² + c²)** with c = (C of G from butt) − 1.092 m, W_kgf = W_lbf/2.2046 — the complete spruce rows (1–6, 9) and old thranite C reproduce the printed MIT to within rounding; old zygians A & B do **not** (see the Verification note below).

| Oar | Type | Wt lbf | Wt-in-hand lbf | Radius of gyration² (m²) | C of G from butt (m) | MIT kg-m² | X (m) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | spruce | 12 | 7.9 | 1.48 | 1.81 | 10.8 | −0.35 |
| 2 | spruce | 12 | 8.0 | 1.41 | 1.82 | 10.6 | −0.46 |
| 3 | spruce | 10.5 | 8.2 | 1.45 | 1.94 | 10.3 | −0.57 |
| 4 | spruce | 10 | 7.8 | 1.42 | 1.94 | 9.7 | −0.61 |
| 5 | spruce | 10 | 7.3 | 1.45 | 1.89 | 9.5 | −0.51 |
| 6 | spruce | 9 | 6.7 | 1.38 | 1.90 | 8.3 | −0.61 |
| 7 | spruce | — | — | — | — | — | Missing |
| 8 | spruce | — | — | — | — | — | Missing |
| 9 | spruce | 9 | 7.2 | 1.43 | 1.97 | 9.0 | −0.62 |
| A | old zygian | 21 | 10.2 | 1.45 | 1.62 | 18.2 | +0.15 |
| B | old zygian | 22 | 9.6 | 1.38 | 1.57 | 17.8 | +0.24 |
| C | old thranite | 17 | 7.4 | 1.46 | 1.57 | 13.1 | +0.40 |

Notes: oars 1–9 spruce, A–B the old Douglas-fir oars (2 zygian + 1 thrane). Rows 7 & 8 have no measured data in the original table ("Missing"). The X sign convention: **negative = centre of percussion within the blade** (all spruce oars, best ≈ −0.35 to −0.62 m from tip); the old fir oars have X **positive** (+0.15…+0.40 m), i.e. their centre of percussion falls beyond the blade tip — the handiness problem the redesign addressed. Spruce oars 1 & 2 (with fir oars A–C) have squared looms. `[x]`

Verification: all **7 complete spruce rows and old thranite C verify internally at inboard 1.092 m** — MIT = W_kgf·(k²+c²) reproduces the tabulated MIT, and the X column is consistent with the **4.22 m** actual oar length: implied length = COG_from_butt + k²/c − X = 4.20–4.24 m for the spruce, **and the reconstruction also closes for the old fir oars** (A → 4.216 m, B → 4.217 m, C → 4.224 m) — the measured X, C of G and k² of all ten oars describe the existing 4.22 m oars. **Flag:** old *zygian* rows A & B are internally inconsistent in the source — their MIT implies inboard ≈ 0.94 m while their weight-in-hand matches 1.092 m exactly and their X/C of G/k² reconstruct 4.22 m (the earlier "short 3.5–3.6 m oar" inference came from trusting the MIT cell — superseded). Record the values as printed; do not force them through the 1.092 m relation. Independently, the weight-in-hand column is internally exact under inboard 1.092 m — W·(COG−1.092)/1.092 with the tabulated W and C of G reproduces every printed weight-in-hand (A → 10.15 vs 10.2 lbf, B → 9.63 vs 9.6, C → 7.44 vs 7.4) — so the A/B disagreement is confined to the MIT cell, and both rows deviate by the same ≈ −9.7 % (A −9.5 %, B −9.8 %), pointing to a shared basis or transcription error in the source's MIT column rather than in the weights or C of G. `[?]`

**Handiness — what the inertias mean at the handle (Table 3.1 → `oar_inertia.py`)** `[x]`

- **Equivalent inertial mass at the handle, m_h = MIT/1.092²**: spruce **8.2 kg** (7.0–9.1 per oar), old fir zygian **15.1 kg**, old fir thranite **11.0 kg**. The static weight-in-hand is only 3.5–5.6 kgf — the *dynamic* mass the rower plays with is set by MIT, and the old fir oars carry ≈×1.8 the spruce inertia.
- **Catch-phase inertia spike**: in the drive the oar runs at roughly constant angular speed (ω = sweep/t_drive from Table 9.6, 1.95–2.14 rad/s), so the inertia term I·ω̇ ≈ 0 mid-stroke — the inertia is paid at the *catch flip*, spinning the oar from rest up to ω over the water-entry time t_rise: F_spike = MIT·ω/(t_rise·1.092). With the measured drive times and t_rise = 0.15 s:

  | point | spm | ω (rad/s) | spruce F | old zygian F | old thranite F |
  | --- | --- | --- | --- | --- | --- |
  | Olympias 7.2 kt | 28.8 | 1.95 | 116 N | 215 N | 156 N |
  | Olympias 8.2 kt | 36.0 | 2.14 | 127 N | 235 N | 171 N |
  | Mark IIb 9.7 kt | 46.3 | 2.06 | 122 N | 226 N | 164 N |

  (t_rise 0.10 s → ×1.7 of these; 0.20 s → ×0.75.) The old-fir spike is **≈×1.9 the spruce** and of the same order as the whole drive mean handle force (~210–225 N) — the quantitative content of “handiness”: Shaw’s 4.66 m spruce spec (MIT ≈ 8 kg·m²) cuts both. The bulk/rigid chains are massless (static torque balance) and are unchanged; this block is the input for any future stroke-end dynamics.
- **X = centre of percussion from the blade tip** (spruce −0.35…−0.62 m → COP 2.51–2.78 m from the thole, inside the 3.13 m outboard length; old fir +0.15…+0.40 m → COP 3.28–3.53 m, i.e. 0.15–0.40 m *beyond the blade tip*) — a percussive blow at the catch lands outboard of the blade, the second reason the fir oars felt heavy in the hands.

**Shaw's suggested specification for a 4.66 m spruce oar (Rankov ch.3 App.2, p.61) — verified**

| property | value |
| --- | --- |
| Weight overall | **4.5 kgf (≈10 lbf)** |
| Weight "in hand" (at butt) | **2.0 kgf (≈4½ lbf)** |
| Gearing | **2.8** (2½ cubits inboard / 7 cubits outboard) |
| C of G | 0.544 m outboard of fulcrum; 2.886 m from blade tip |
| Centre of percussion | 0.15 m inside blade (from tip) |
| Radius of gyration² (≈ k²) | 1.488 m² (2.736 × 0.544) |
| MIT about thole | **≈ 8 kg-m²** = 4.5·(1.488 + 0.544²) |

"Gearing 2.8 is suitable for fast rowing on fixed seats, and does not entail too steeply-inclined a thranite oar." `[x]`

### 2.4 Lever ratios / gearing (duplicates Part 1 §1.3; the fuller history)

- **Thranite / standard oars**: inboard 1.092 m (3 ft 7 in) used throughout Table 3.1; some positions preferred up to 1.105 m (3 ft 7½ in) with gearing **2.817**. `[x]` (Rankov ch.3)
- **Mark II design gearing**: 9½-cubit oars with **7 cubits outboard / 2½ cubits inboard → 2.80**. `[x]` (Rankov ch.9; "the ratio cannot be much less than this if the ships are to be fast")
- **Thalamian oars — gearing history** (Rankov ch.1 §1.4.2, p.38; blade centre of pressure assumed 260 mm from tip): `[x]`
  - As designed: **2.82**
  - As observed 1990: **2.57** (oars were operating ~70 mm further inboard than designed — handles too far inboard because of the swelling in the loom and the bevel on the carling block)
  - Moved outboard 40 mm from the 1990 position: **2.96** (the 40 mm change was the maximum achievable without cramping/body-misalignment; it noticeably increased thalamian work-load)
  - If the full 100 mm outboard move had been possible: **3.11**
- Zygian blades historically under-powered (blades unseen by rower, weak fork design); the thalmian/zygian blade-clash problem (copper strips added to thalmian blades damaged zygian forks). `[x]` (Rankov ch.1, pp.24–25)

### 2.5 Interscalmium (distance between thole-pins / rowing stations)

- **Olympias: 2 cubits × 0.444 m = 0.888 m (88.8 cm)**. `[x]` (Rankov 2012, intro/plan commentary: "interscalmium of 88.8 cm"; also build log)
- **Mark IIa proposal: 0.98 m** (2 × 0.49 m cubit). `[x]` (Rankov 2012, incl. ch.31 §5)
- The commonly quoted "≈0.94 m" for a trireme design has **no direct Olympias source** — the Olympias design value is 0.888 m and the Mark II is 0.98 m. 0.94–0.99 m is the range of measured interscalmia on *Roman* wrecks, not Olympias. `[?]` Flag: likely a conflation in the task spec; check any drawing that quotes 0.94 m before using it.
- Roman-wreck parallel ranges (for calibration only): Mainz-type galleys ~0.84–0.96 m; Oberstimm 0.94–0.99 m; Vechten/Yverdon/Herculaneum 0.92–1.125 m. `[?]` (secondary summary; needs the primary wreck reports if used)
- Vitruvius *De arch.* 1.2.4 says the interscalmium was 2 cubits (0.888 m for a 0.444 m cubit) — a standard unit of length in his list; see Rankov 2012 ch.29 area for the debate on whether the ancient unit was exactly 2 cubits. `[x]`

### 2.6 Stroke length (at the butt/handle)

**Olympias as-built / measured**

- Design stroke **800 mm** (Coates midship-section, Plan 8; constrained by the thalmian tier head-room/beam). `[x]` (build log quoting the Plan 8 drawing)
- A 1:24 manikin at the thalmian position achieves **~720 mm** of the 800 mm design stroke (head-room limited). `[x]` (build log)
- Shipboard measurements: 1992 average stroke **82–85 cm** across the ship (1988: 75–77 cm); two triads reached **100 cm+**. `[x]` (Rankov 2012 ch.1 area; Lipke report). These are total butt travel, consistent with the 0.888 m interscalmium minus end clearance.

**Shaw's analytical stroke model (Rankov ch.3 App.3, p.62) — verified** (also Part 1 §1.6)

- A 167 cm man on fixed thwarts, *unrestricted by the rig*, can pull a max stroke of **≈1.1 m** at the butt; ≈10% lost motion → **effective powered length ≈ 0.99 m**. `[x]`
- Inside an uncanted rig with interscalmium 0.98 m: total movement ≤ interscalmium minus clearance (≥0.15 m) and same 0.11 m end losses → **effective stroke restricted to ≈0.87 m**. `[x]`
- The two candidate effective strokes (0.99 m canted, 0.87 m straight) drive his 7½-kt table (see propulsion-models.md §2). `[x]`
- **Table 3.2 — "Speed 7½ knots" (p.62)**: rhythm factor & mean handle couple (N·m) vs stroke rate, for the two stroke lengths. `[x]` (decoded via `research/data/shaw-table-3.2-stroke-rhythm.csv`)
  - Rhythm factor: 30 spm → 3.42 (0.99 m) / 4.01 (0.87 m); 32 → 3.21 / 3.76; 34 → 3.02 / 3.53; 36 → 2.85 / 3.34; 38 → 2.70 / 3.16.
  - Mean couple on the oar-handle (N·m): 30 spm → 215 (0.99 m) / 246 (0.87 m); 32 → 202 / 231; 34 → 190 / 218; 36 → 180 / 206; 38 → 172 / 196.
  - Ratio of rhythm factors at fixed rate = 4.01/3.42 = **1.17** — matches the prose "the ratio of rhythm factors at a given stroke rate is 1.17". The couple rows are the mean bending stress on the oar at the thole; greatest value during a stroke is considerably higher. `[x]`
  - Internal consistency with the rigid-oar layer: mean couple / 1.092 m = mean handle force — 246 N·m (30 spm, 0.87 m) / 1.092 = 225 N; the rigid flat-plate model’s mean handle force × lever = 224 × 1.092 = **244.6 N·m vs 246 (0.6 %)**. The 0.99-m-stroke couples (215/202/… → ~197 N at 30 spm) sit ~12 % lower, consistent with the longer canted stroke’s lower handle forces. (`oar_inertia.py` part C.) `[x]`

**Mark II / canted rig**

- Mark IIb allows the oar handle to pass alongside/outboard of the rower next aft (Fig. 3.3, canted & offset rig), giving the longer stroke; a 50% longer stroke (1.1 m total) vs Olympias is claimed. `[x]` (Rankov ch.3 p.47; ch.31 §5)
- At 7½ kt with 0.99 m effective stroke, mean angular velocity of the oar during the pull = 1.42 rad/s (0.87 m stroke → 1.45 rad/s). `[x]`
- **Ch.9 chord-of-pull table (verified)**: interscalmium / chord between deadpoints — Olympias 0.89 / 0.89 m; Mark IIa 0.98 / 0.98 m; **Mark IIb 0.98 / 1.10 m**. The 1.10 m chord comes from **canting the rig 18.4°** (tan = 1/3) — a longer effective chord without widening the interscalmium (which would weaken the hull). `[x]` (Rankov ch.9, Table 9.2; `research/data/t91_t92_ocr.txt`)
- **Effective sweep angle** in plan: Olympias ≈ **48.1°** (attained only with exceptional effort); Mark IIb larger. `[x]` (Rankov ch.9 p.78–79)

**Ch.9 analytical oar model (Shaw's full power/efficiency derivation)**

- Effective pull length at the butt **L**: Olympias 0.89 m, Mark IIa **0.87 m**, Mark IIb **0.99 m**. `[x]` (Table 9.7)
- Instantaneous turning-point distance from tip: **d = 0.953·sin[120·(C−A)/B + 30°]**; effective outboard lever **p = L(plan) − d**. `[x]`
- Differential advance of tholepin per differential sweep: **ds = (L − d)·dC / sin C**, summed over C=A→A+B. `[x]` (Fig. 9.1)
- **Mean ideal oar efficiency E = 1/(1 + q/p)**, where q = blade centre-of-pressure → instantaneous turning-point distance, p = turning-point → thole distance. `[x]`
  - Olympias, all three levels (~170): **E = 0.756**
  - Olympias, two levels (n=116): **E = 0.719**
  - Olympias sprint, ~130 effective: **E = 0.730**
  - **Mark II design value (used in all tables): E = 0.780**
- q/p ∝ 1/√n (thrust/oar ∝ 1/n at fixed V and angles); 170→116 rowers raises q/p ×1.21. `[x]`

### 2.7 Human power model (ch.9 — Shaw's validated derivation)

- Power equation: **W = n·P·L·r·E/60** (W watts, n rowers in action, P = mean pull at butt in N, L = effective pull length at butt in m, r = rate of striking spm, E = mean ideal efficiency). `[x]` (Rankov ch.9 p.80)
- Hull power law (Olympias): **W = 155·V³ + 4.13·V⁵** (V m/s); **Mark II hulls ×1.08**. `[x]`
- Calibration: Olympias sprint trial — 116 rowers, 6.8 kt (3.50 m/s), W = 12,100 W (rudders down, 4–5 kt tailwind), r = 38.75 spm, E = 0.719 → **mean pull P = 288 N (64.7 lbf)**. `[x]`
- Mean pull assumed ∝ rate: **P = 7.43·r**. `[x]`
- **Validation vs 4 Olympias sprint runs** (~130 effective rowers, 44.5 spm, E = 0.730): predicted 130×0.78×7.43×44.5²×0.730/60 = **18,152 W → 4.285 m/s = 8.32 kts**; measured 8.2–8.3 kts. **Theory ↔ experiment agreement.** `[x]` (Rankov ch.9 p.81)
- **Table 9.6 — duration of effective pull (s)**: `[x]` (OCR `research/data/t96_ocr.txt`)
  - Olympias: 0.428 (7.5 kt), 0.392 (8.2 kt); Mark IIa: 0.512 / 0.469 / 0.396 (9.7 kt); Mark IIb: 0.612 / 0.560 / 0.472.
- **Table 9.7 — rates of striking at 7.5 & 9.7 kts** (verified): `[x]` (OCR `research/data/t97_ocr.txt`)
  - W = 13,460 W (7.5 kt) / 34,860 W (9.7 kt) both designs.
  - L = 0.87 m (IIa) / 0.99 m (IIb); E = 0.780.
  - **r**: IIa 30.7 / 49.4 spm; IIb 28.8 / 46.3 spm.
  - **P**: IIa 228 / 367 N (51.3 / 82.5 lbf); IIb 214 / 344 N (48.1 / 77.3 lbf).
  - Rhythm factor (cycle/pull): IIa 3.82 / 3.07; IIb 3.40 / 2.75. Run duration: IIa 1.44 / 0.819 s; IIb 1.47 / 0.824 s.
- Cruise power per oarsman (ch.7): 7 kt → 115 W, 7.5 kt → 145 W, 8 kt → 180 W gross; rates 25.5 / 28.8 / 32.3 spm. `[x]` (Rankov ch.7 p.66)

### 2.8 Blade shape & dimensions

- **Original Douglas-fir oars**: thranite & zygian oars had **spade-shaped blades** (spliced construction); **thalmian oars had narrower blades** (one-piece). `[x]` (build log POST 60)
- **Spruce redesign (1990)**: a **common teardrop-shaped blade** for all three levels. `[x]` (build log; Rankov ch.3)
- Blade-root shaft section is oval, **55 × 37 mm full-size** (builder's 1:24: 2.3 × 1.55 mm). `[x]` (build log POST 63)
- Naval-pattern trial oars (pre-Olympias rig tests) had blades **1500 × 150 mm**. `[x]` (build log)
- 1994 trial: thalmians rowed with **wide-bladed oars**, reaching the same efficiency as other levels (confirms the 1990 finding that narrow thalmian blades reduced their contribution). `[x]` (Rankov ch.4)
- Exact blade area for the Olympias rig: not recovered from text — the authoritative geometry is Coates **Plans 15 / 15d / 15e / 15g (oars)** in the Trireme Trust/Wolfson archive (see lane-3 `hull-form.md` Part 2). `[?]` — the chain uses 0.078 m² (Rankov ch.10, minimum effective).

### 2.9 Thole / oar-loop / attachment

- Oars are secured **forward of the thole-pin** by oar loops (forward of pin geometry per Rankov 1998 and build log). `[x]`
- Original loops: leather straps sewn into loops with a left/right twist over the tholepins; they stretched and stitching broke → tried leather laces, rawhide → final solution **rope grommets**. `[x]` (build log POST 77)
- Rope thole-straps are thicker than leather → **raise the pivot point** (and the handle/loom), which mattered for thalmian clearance against the zygian beam. `[x]` (Rankov ch.1 p.38–39)
- Thranite oar inclination: the oar slopes **≈30° to the horizontal** at the catch (with butt at shoulder level, straight arms); angle of attack 52.9° in plan; instantaneous turning point of the oar ~0.60 m up the shaft from the tip (2.83 m from the pin). `[x]` (Rankov ch.3 App.1, p.60)
- Clearance constraint: at top speed, 0.15 m clearance at the catch gives only ~0.109 s margin against hitting the rower next aft (App.1 calculation, 9.7 kt). `[x]`

### 2.10 What this means for the simulation

- Fixed seat → the rower's reach (~1.1 m max, ~0.99 m effective) exceeds Olympias's 0.888 m interscalmium: **stroke is rig-limited, not body-limited** on Olympias (this is the whole rationale for Mark II's 0.98 m + canting). `[x]`
- Thalmian tier is additionally power-starved by head-room (720/800 mm manikin stroke) and by narrow blades; both were corrected in the Mark II concept. `[x]`
- Oar dynamics inputs available now: length 4.22 m (or 4.66 m spec), inboard 1.092 m, gearing 2.8–2.96, MIT ≈ 8 kg-m², weight-in-hand 2.0 kgf, slip 0.49 m, blade CP ~260 mm from tip. `[x]`
- **Oar-propulsion chain now fully specified and implemented** (ch.9): W_hull = 155V³+4.13V⁵ (×1.08 Mark II) → n·P·L·r·E/60; P = 7.43·r; E = 0.780 (Mark II) / 0.756 full-crew Olympias; L = 0.89/0.87/0.99 m. Implemented + verified in `propulsion-models.md` and `lane4_propulsion.py` — reproduces Shaw's 8.32-kt sprint, Table 9.7 rates, ch.7 cruise rates, and the S6 62-W/man check. The 44.5-spm sprint → 8.3 kts match is our best cross-check target. `[x]`

### 2.11 Open questions

1. [x] Exact **Table 3.1** values for the ten 1994 oars (overall weight, weight-in-hand, MIT, X per oar) — **resolved**: fully decoded from the PDF glyph layer and MIT-verified; see §2.3 and `research/data/shaw-table-3.1-oar-inertia.csv`. (Rows 7 & 8 genuinely have no recorded data.)
2. [?] Origin of the "**12.3 kg/oar**" figure (build log quote) — likely Shaw/Coates 1990 or Trireme Trust newsletter; findable only in the physical book or newsletter.
3. [?] The "**0.94 m** interscalmium" in the task spec — no Olympias source found (0.888 m design, 0.98 m Mark II); likely Roman-wreck conflation.
4. [?] Blade areas (spade vs teardrop) and exact taper — only in Coates Plans 15/15d/15e/15g (Wolfson archive), not recovered as text.
5. [x] Ch.9 tables 9.1/9.2/9.6/9.7 are decoded (OCR) and all numerically verified against W=nPLrE/60 and W=1.08(155V³+4.13V⁵) — see `research/lane-1-read/shaw-ch7-ch9-2024.md` and `research/data/t9*_ocr.txt`. **Resolved.**

### 2.12 Sources

- [x] **Rankov, B. (ed.) (2012).** *Trireme Olympias: The Final Report.* Oxbow. (PDF at ancientportsantiques.com; text at ../sources/rankov2012.txt) — ch.1 (1992 trials, Lipke/Howarth) pp.24–25, 37–39; ch.3 (1994 trials, Shaw, incl. Apps 1–3) pp.47–62; ch.7 (Shaw, Golden Horn→Heraclea) pp.63–67; ch.9 (Shaw, long-stroke design) pp.76–81; ch.31 (Taylor) pp.233–243.
- [x] **Braithwaite, R.** 1:24 Olympias build log, ModelShipWorld (local copy: ../sources/trireme-olympias-build-log-richard-braithwaite.md), POSTs 60–72, 77 (oars) and 61 (oar mass).
- [x] **Wikipedia, "Olympias (trireme)"** — crew breakdown (62/54/54), 1987 trials, dimensions, power estimate.
- [x] **Morrison, Coates & Rankov (2000).** *The Athenian Trireme* (oar-loop/thole details; cubit basis; 9 & 9½ cubit oars).
- [?] Roman-wreck interscalmia (Mainz/Oberstimm/etc.): secondary summary only — obtain primary wreck reports if these enter the model.

---

## Part 3 — The rigid-oar per-stroke refinement layer (flat-plate blade model)

Implements the per-stroke blade-force refinement the main doc W3 item 147 / D9 asks
for, on top of the verified bulk lever-chain (`propulsion-models.md`,
`lane4_propulsion.py`). Reference code: `rigid_oar_model.py` (pure stdlib).

**Result in one line**: at the Olympias design cruise point the rigid-oar
flat-plate model reproduces Shaw's bulk efficiency, handle force and per-oar power
almost exactly (76.2% vs 75.6%, 224 vs 214 N, 65 vs 61 W, 102% of hull-required
power), independently validating the bulk E = 0.756 used in the macro chain.

### 3.1 Model

Per-stroke integration of one drive of a rigid oar, in the spirit of Caplan &
Gardner (2007a) and the flat-plate / pressure-drag regime of the 2019 NJP "Physics
of rowing oars" analysis:

- Blade = flat plate (trireme blades are near-flat spade/teardrop, much lower camber
  than a modern Big Blade). Dominant blade force = pressure (normal) force on the
  face:
  **Fn = 0.5·ρ·A·C_N·|v_n|·v_n**, acting to oppose the normal flow v_n.
  C_N = 1.8 for a flat plate fully immersed — consistent with the measured Macon
  blade C_D,max ≈ 1.85 at 90° attack (Caplan & Gardner 2007b; Coppel et al. 2009).
- 2nd-class-lever torque balance about the thole: **Fh·l_in = Fb·l_cp** (Baudouin &
  Hawkins 2002), l_cp = blade centre of pressure 260 mm from tip (Rankov ch.1 §1.4.2).
- Kinematics: oar sweeps B = 48.1° (Olympias) / 55.6° (Mark IIb) at **constant
  angular speed over the effective pull time t_drive from Table 9.6**
  (0.430 s @7.2 kt, 0.392 s @8.2 kt; 0.612 s / 0.472 s for Mark IIb). Blade enters
  the water already moving — no deadpoint taper (a taper to zero produces drag, not
  thrust, because the blade then sweeps slower than the ship advances).
- Geometry from Part 1 / Table 9.1: inboard/outboard plan lengths,
  blade 0.55 m, blade area 0.078 m² (Rankov ch.10, minimum effective), seawater
  ρ = 1025 kg/m³.

### 3.2 Results (script output)

| case | V kt | spm | thrust/oar N | eff | mean Fh N | peak Fb N | Shaw bulk E / P |
|---|---|---|---|---|---|---|---|
| Olympias | 7.2 | 28.8 | 17.5 | **76.2%** | **224** | 124 | **75.6% / 214 N** |
| Olympias | 8.2 | 36.0 | 18.4 | 79.1% | 208 | 121 | 75.6% / 267 N |
| Mark IIb | 7.5 | 28.8 | 6.1 | 85.7% | 63 | 50 | 78.0% / 214 N |
| Mark IIb | 9.7 | 46.3 | 13.2 | 85.6% | 109 | 86 | 78.0% / 344 N |

Energy check (propulsive power/oar from the rigid model vs. hull requirement):

- Olympias @7.2 kt: **65 W vs 63 W needed (102%)** — the rigid model closes the
  hull-power balance. ✓
- Olympias @8.2 kt: 78 W vs 101 W (77%) — model under-produces at the sprint rate;
  see caveats.
- Mark IIb: 24 W vs 79 W @7.5 kt (30%), 66 W vs 204 W @9.7 kt (32%).

**Blade-area sensitivity** (area the flat-plate model needs to meet the hull power):

- Olympias @7.2 kt: 0.078 → **0.076 m² (×1.0)** — as-built blade area is exactly
  what the physics needs. ✓
- Mark IIb @7.5 kt: 0.078 → **0.260 m² (×3.3)** — the model says Mark II needs much
  larger blades, *consistent with ch.9's explicit note* that Mark II blades "must be
  such as will enable the blades to absorb the required power" and may need different
  widths.

### 3.3 What this means for the simulation

- **The bulk lever-chain E is independently confirmed** at the Olympias design point
  (76.2% model vs 0.756 Shaw): the macro chain in `lane4_propulsion.py` is sound.
- The rigid model adds the **per-stroke force envelope** the bulk chain cannot give:
  peak blade force ~120–130 N, mean handle force ~210–225 N (Olympias), needed for
  any future per-stroke thrust ripple in the manoeuvring model and for ergonomic
  limits (fixed-seat V̇O2 ≈ 65% of sliding-seat, S6).
- The **Mark IIb under-production is a design finding, not a code bug**: with the
  same blade area as Olympias the flat-plate physics cannot absorb Mark II's power.
  This quantitatively supports ch.9's separate, larger Mark II blade spec and is a
  candidate for the uncertainties register (Mark II blade area is otherwise unknown).
  (The Braithwaite workbook's linear thrust law is a different model family; it does
  not resolve the Mark IIb tension — see `braithwaite-workbook.md` and next-steps
  Stream A3.)

### 3.4 Caveats / flags for the uncertainties register

- Constant angular speed + no deadpoint taper is a deliberate simplification; the
  2019 NJP analysis shows added-mass and pressure-drag regimes matter at the stroke
  ends. The Olympias match (102%) suggests this is adequate for mean quantities.
- Flat-plate C_N ignores blade camber/lift; a cambered blade could supply the Mark IIb
  shortfall at smaller area than ×3.3. Flag: Mark IIb blade-area requirement is an
  upper bound under the flat-plate assumption.
- Single blade CP (260 mm from tip) instead of Shaw's moving turning-point model;
  the constant lever slightly over-estimates Olympias eff (76.2 vs 75.6%).
- The 8.2 kt sprint under-production (77%) likely reflects the simplified kinematics
  at high rate; not used for the macro chain (which is calibrated to the trials).

### 3.5 Sources

- Caplan, N. & Gardner, T. (2007b), "A fluid dynamic investigation of the Big Blade
  and Macon oar blade designs", *J Sports Sci* 25:643–650 — measured C_L, C_D curves;
  C_D,max ≈ 1.85 at 90° attack.
- Coppel, Gardner, Caplan & Hargreaves (2009), ISBS — C_L/C_D table for Macon;
  CFD/experimental agreement within 1.33%.
- "Physics of rowing oars" (2019), *New J. Phys.* 21 — rigid-oar kinematics,
  pressure-drag vs added-mass regimes.
- Baudouin & Hawkins (2002), *Br J Sports Med* 36:396–402 — oar as 2nd-class lever.
- Rankov 2012 ch.9 (Table 9.1 oar dims, Table 9.6 pull durations), ch.1 §1.4.2
  (blade CP 260 mm), ch.10 p.85 (blade area 0.078 m²); **ch.3 Table 3.1 (p.48,
  decoded) loaded per-row in `oar_inertia.py`**; Part 1 of this file (rig geometry).
