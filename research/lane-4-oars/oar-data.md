# Lane 4 — Oars & Oar-Rig: Olympias geometry, mass, gearing, stroke, blades

Research notes, web-only + Rankov 2012 full-text PDF (extracted text at `sources/rankov2012.txt`).
Confidence flags: `[x]` = confirmed directly from a cited source (primary text read); `[?]` = inferred / unverified / conflicting.
Primary texts used: Rankov 2012 ch.1 (1992 trials report, Lipke/Howarth), ch.3 (1994 trials report, Shaw, incl. Appendices 1–3), ch.31 (Taylor); Braithwaite 1:24 build log (ModelShipWorld); Wikipedia Olympias infobox.

---

## 1. Oar inventory & count

- 170 oarsmen total: **62 thranites** (upper), **54 zygites** (middle), **54 thalamites** (lower). `[x]` (Wikipedia Olympias crew; matches Rankov 2012 throughout)
- Oar families in Olympias (build log, POST 71): thalmian 12 short + 42 long; zygian 6 short + 48 long; thranite 62. Short oars are at bow/stern where the hull narrows. `[x]`
- 42 main thalamian oars + 3 spares were modified in 1992; the 12 short thalamian oars in triads 1–3 bow and 28–29 stern were not. In practice triad 4 and stern triads 28–29 also needed short zygian oars. `[x]` (Rankov ch.1, pp.25,37)

## 2. Oar length

- Ancient naval inventories record oars of **9 and 9½ cubits**. `[x]` (build log, citing *The Athenian Trireme*)
- Olympias cubit = **0.444 m** → 9 cubits = **4.00 m**, 9½ cubits = **4.22 m**. `[x]` (build log; Osprey Olympias volume agrees: 3.99 m / 4.2 m)
- Olympias's existing spruce oars are **4.22 m long**; Shaw proposes a **4.66 m** design (9½ cubits of the *larger* 0.49 m cubit). `[x]` (Rankov ch.3 pp.48,60–61)
- Proposed 4.66 m oar split: **2½ cubits (1.225 m) inboard of the pin, 7 cubits (3.43 m) outboard**. `[x]` (Rankov ch.3 App.1, p.60)
- At the ends of the ship the available space forces shorter oars at every level (see §1). `[x]`
- **Ch.9 table (verified)**: Olympias overall **4.218 m** (3.653 m in plan), outboard **3.113 m**, blade **0.550 m**, inboard **1.105 m**, thole→neck **2.563 m**. Mark IIa/IIb: overall **4.655 m**, outboard **3.430 m**, blade 0.550 m, inboard **1.225 m** (=2½ cubits of 0.49 m), thole→neck **2.880 m**. (Table 9.1; "in plan" = ×cos 30°.) `[x]` (Rankov ch.9, p.76–77; OCR `research/data/t91_t92_ocr.txt`)

## 3. Oar mass / physical properties

### Full-size Olympias fir oars
- Douglas-fir oars (the originals): "weighed over 12 kg, increased to 17 kg once a lead counterweight was added inboard". `[x]` (build log POST 61 area, quoting model-scaled ship oars)
- **12.3 kg/oar** full-size: figure quoted in the build log for the real Olympias oars (the builder's 1:24 model oars scale to 11.71 g at 1:24³). `[?]` — source of the 12.3 kg value is not stated by the builder; likely from Shaw/Coates (The Trireme Project or the 1994 trials report). Rankov 2012 Table 3.1 holds the ten-oar measured table (fir + spruce) but the table body is corrupted in the PDF text layer. **Consistent with** ">12 kg"; treat 12.3 kg as plausible but not independently confirmed.

### 1994 measurements (Rankov ch.3 App.2, p.60–61) — verified
- 10 oars tested: **3 Douglas fir + 7 spruce**, by bifilar suspension + stopwatch (method: Lamb 1923, 158–9, 164).
- Inboard length taken as **3 ft 7 in = 1.092 m in all cases** — "found by the users of spruce oars to be the most convenient in Olympias." `[x]`
- Parameters recorded: overall weight, weight "in hand" (as though acting at the butt), C of G from thole, **MIT = moment of inertia about the thole** (a measure of handiness), **X = distance of centre of percussion from the blade tip** (best ≈ −0.15 m, i.e. within the blade ~6 in; Bourne 1925).
- Old fir oars and spruce oars 1 & 2 have squared looms; the others circular-section looms. `[x]`
- Conclusion: a spruce oar 4.66 m long "could weigh as little as 10 lbf" with **MIT kept as low as 8 kg-m²**. `[x]`

### Shaw's suggested specification for a 4.66 m spruce oar (Rankov ch.3 App.2, p.61) — verified
| property | value |
|---|---|
| Weight overall | **4.5 kgf (≈10 lbf)** |
| Weight "in hand" (at butt) | **2.0 kgf (≈4½ lbf)** |
| Gearing | **2.8** (2½ cubits inboard / 7 cubits outboard) |
| C of G | 0.544 m outboard of fulcrum; 2.886 m from blade tip |
| Centre of percussion | 0.15 m inside blade (from tip) |
| Radius of gyration² (≈ k²) | 1.488 m² (2.736 × 0.544) |
| MIT about thole | **≈ 8 kg-m²** = 4.5·(1.488 + 0.544²) |

"Gearing 2.8 is suitable for fast rowing on fixed seats, and does not entail too steeply-inclined a thranite oar." `[x]`

## 4. Lever ratios / gearing

- **Thranite / standard oars**: inboard 1.092 m (3 ft 7 in) used throughout Table 3.1; some positions preferred up to 1.105 m (3 ft 7½ in) with gearing **2.817**. `[x]` (Rankov ch.3)
- **Mark II design gearing**: 9½-cubit oars with **7 cubits outboard / 2½ cubits inboard → 2.80**. `[x]` (Rankov ch.9; "the ratio cannot be much less than this if the ships are to be fast")
- **Thalamian oars — gearing history** (Rankov ch.1 §1.4.2, p.38; blade centre of pressure assumed 260 mm from tip): `[x]`
  - As designed: **2.82**
  - As observed 1990: **2.57** (oars were operating ~70 mm further inboard than designed — handles too far inboard because of the swelling in the loom and the bevel on the carling block)
  - Moved outboard 40 mm from the 1990 position: **2.96** (the 40 mm change was the maximum achievable without cramping/body-misalignment; it noticeably increased thalamian work-load)
  - If the full 100 mm outboard move had been possible: **3.11**
- Zygian blades historically under-powered (blades unseen by rower, weak fork design); the thalmian/zygian blade-clash problem (copper strips added to thalmian blades damaged zygian forks). `[x]` (Rankov ch.1, pp.24–25)

## 5. Interscalmium (distance between thole-pins / rowing stations)

- **Olympias: 2 cubits × 0.444 m = 0.888 m (88.8 cm)**. `[x]` (Rankov 2012, intro/plan commentary: "interscalmium of 88.8 cm"; also build log)
- **Mark IIa proposal: 0.98 m** (2 × 0.49 m cubit). `[x]` (Rankov 2012, incl. ch.31 §5)
- The commonly quoted "≈0.94 m" for a trireme design has **no direct Olympias source** — the Olympias design value is 0.888 m and the Mark II is 0.98 m. 0.94–0.99 m is the range of measured interscalmia on *Roman* wrecks, not Olympias. `[?]` Flag: likely a conflation in the task spec; check any drawing that quotes 0.94 m before using it.
- Roman-wreck parallel ranges (for calibration only): Mainz-type galleys ~0.84–0.96 m; Oberstimm 0.94–0.99 m; Vechten/Yverdon/Herculaneum 0.92–1.125 m. `[?]` (secondary summary; needs the primary wreck reports if used)
- Vitruvius *De arch.* 1.2.4 says the interscalmium was 2 cubits (0.888 m for a 0.444 m cubit) — a standard unit of length in his list; see Rankov 2012 ch.29 area for the debate on whether the ancient unit was exactly 2 cubits. `[x]`

## 6. Stroke length (at the butt/handle)

### Olympias as-built / measured
- Design stroke **800 mm** (Coates midship-section, Plan 8; constrained by the thalmian tier head-room/beam). `[x]` (build log quoting the Plan 8 drawing)
- A 1:24 manikin at the thalmian position achieves **~720 mm** of the 800 mm design stroke (head-room limited). `[x]` (build log)
- Shipboard measurements: 1992 average stroke **82–85 cm** across the ship (1988: 75–77 cm); two triads reached **100 cm+**. `[x]` (Rankov 2012 ch.1 area; Lipke report). These are total butt travel, consistent with the 0.888 m interscalmium minus end clearance.

### Shaw's analytical stroke model (Rankov ch.3 App.3, p.62) — verified
- A 167 cm man on fixed thwarts, *unrestricted by the rig*, can pull a max stroke of **≈1.1 m** at the butt; ≈10% lost motion → **effective powered length ≈ 0.99 m**. `[x]`
- Inside an uncanted rig with interscalmium 0.98 m: total movement ≤ interscalmium minus clearance (≥0.15 m) and same 0.11 m end losses → **effective stroke restricted to ≈0.87 m**. `[x]`
- The two candidate effective strokes (0.99 m canted, 0.87 m straight) drive his 7½-kt table (see propulsion-models.md §2). `[x]`

### Mark II / canted rig
- Mark IIb allows the oar handle to pass alongside/outboard of the rower next aft (Fig. 3.3, canted & offset rig), giving the longer stroke; a 50% longer stroke (1.1 m total) vs Olympias is claimed. `[x]` (Rankov ch.3 p.47; ch.31 §5)
- At 7½ kt with 0.99 m effective stroke, mean angular velocity of the oar during the pull = 1.42 rad/s (0.87 m stroke → 1.45 rad/s). `[x]`
- **Ch.9 chord-of-pull table (verified)**: interscalmium / chord between deadpoints — Olympias 0.89 / 0.89 m; Mark IIa 0.98 / 0.98 m; **Mark IIb 0.98 / 1.10 m**. The 1.10 m chord comes from **canting the rig 18.4°** (tan = 1/3) — a longer effective chord without widening the interscalmium (which would weaken the hull). `[x]` (Rankov ch.9, Table 9.2; `research/data/t91_t92_ocr.txt`)
- **Effective sweep angle** in plan: Olympias ≈ **48.1°** (attained only with exceptional effort); Mark IIb larger. `[x]` (Rankov ch.9 p.78–79)

### Ch.9 analytical oar model (Shaw's full power/efficiency derivation)
- Effective pull length at the butt **L**: Olympias 0.89 m, Mark IIa **0.87 m**, Mark IIb **0.99 m**. `[x]` (Table 9.7)
- Instantaneous turning-point distance from tip: **d = 0.953·sin[120·(C−A)/B + 30°]**; effective outboard lever **p = L(plan) − d**. `[x]`
- Differential advance of tholepin per differential sweep: **ds = (L − d)·dC / sin C**, summed over C=A→A+B. `[x]` (Fig. 9.1)
- **Mean ideal oar efficiency E = 1/(1 + q/p)**, where q = blade centre-of-pressure → instantaneous turning-point distance, p = turning-point → thole distance. `[x]`
  - Olympias, all three levels (~170): **E = 0.756**
  - Olympias, two levels (n=116): **E = 0.719**
  - Olympias sprint, ~130 effective: **E = 0.730**
  - **Mark II design value (used in all tables): E = 0.780**
- q/p ∝ 1/√n (thrust/oar ∝ 1/n at fixed V and angles); 170→116 rowers raises q/p ×1.21. `[x]`

## 6b. Human power model (ch.9 — Shaw's validated derivation)

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

## 7. Blade shape & dimensions
- **Original Douglas-fir oars**: thranite & zygian oars had **spade-shaped blades** (spliced construction); **thalmian oars had narrower blades** (one-piece). `[x]` (build log POST 60)
- **Spruce redesign (1990)**: a **common teardrop-shaped blade** for all three levels. `[x]` (build log; Rankov ch.3)
- Blade-root shaft section is oval, **55 × 37 mm full-size** (builder's 1:24: 2.3 × 1.55 mm). `[x]` (build log POST 63)
- Naval-pattern trial oars (pre-Olympias rig tests) had blades **1500 × 150 mm**. `[x]` (build log)
- 1994 trial: thalmians rowed with **wide-bladed oars**, reaching the same efficiency as other levels (confirms the 1990 finding that narrow thalmian blades reduced their contribution). `[x]` (Rankov ch.4)
- Exact blade area for the Olympias rig: not recovered from text — the authoritative geometry is Coates **Plans 15 / 15d / 15e / 15g (oars)** in the Trireme Trust/Wolfson archive (see lane-3 note). `[?]`

## 8. Thole / oar-loop / attachment

- Oars are secured **forward of the thole-pin** by oar loops (forward of pin geometry per Rankov 1998 and build log). `[x]`
- Original loops: leather straps sewn into loops with a left/right twist over the tholepins; they stretched and stitching broke → tried leather laces, rawhide → final solution **rope grommets**. `[x]` (build log POST 77)
- Rope thole-straps are thicker than leather → **raise the pivot point** (and the handle/loom), which mattered for thalmian clearance against the zygian beam. `[x]` (Rankov ch.1 p.38–39)
- Thranite oar inclination: the oar slopes **≈30° to the horizontal** at the catch (with butt at shoulder level, straight arms); angle of attack 52.9° in plan; instantaneous turning point of the oar ~0.60 m up the shaft from the tip (2.83 m from the pin). `[x]` (Rankov ch.3 App.1, p.60)
- Clearance constraint: at top speed, 0.15 m clearance at the catch gives only ~0.109 s margin against hitting the rower next aft (App.1 calculation, 9.7 kt). `[x]`

## 9. What this means for the simulation

- Fixed seat → the rower's reach (~1.1 m max, ~0.99 m effective) exceeds Olympias's 0.888 m interscalmium: **stroke is rig-limited, not body-limited** on Olympias (this is the whole rationale for Mark II's 0.98 m + canting). `[x]`
- Thalmian tier is additionally power-starved by head-room (720/800 mm manikin stroke) and by narrow blades; both were corrected in the Mark II concept. `[x]`
- Oar dynamics inputs available now: length 4.22 m (or 4.66 m spec), inboard 1.092 m, gearing 2.8–2.96, MIT ≈ 8 kg-m², weight-in-hand 2.0 kgf, slip 0.49 m, blade CP ~260 mm from tip. `[x]`
- **Oar-propulsion chain now fully specified and implemented** (ch.9): W_hull = 155V³+4.13V⁵ (×1.08 Mark II) → n·P·L·r·E/60; P = 7.43·r; E = 0.780 (Mark II) / 0.756 full-crew Olympias; L = 0.89/0.87/0.99 m. Implemented + verified in `propulsion-models.md` and `lane4_propulsion.py` — reproduces Shaw's 8.32-kt sprint, Table 9.7 rates, ch.7 cruise rates, and the S6 62-W/man check. The 44.5-spm sprint → 8.3 kts match is our best cross-check target. `[x]`

## 10. Sources
- [x] **Rankov, B. (ed.) (2012).** *Trireme Olympias: The Final Report.* Oxbow. (PDF at ancientportsantiques.com; text at sources/rankov2012.txt) — ch.1 (1992 trials, Lipke/Howarth) pp.24–25, 37–39; ch.3 (1994 trials, Shaw, incl. Apps 1–3) pp.47–62; ch.7 (Shaw, Golden Horn→Heraclea) pp.63–67; ch.9 (Shaw, long-stroke design) pp.76–81; ch.31 (Taylor) pp.233–243.
- [x] **Braithwaite, R.** 1:24 Olympias build log, ModelShipWorld (local copy: trireme-olympias-build-log-richard-braithwaite.md), POSTs 60–72, 77 (oars) and 61 (oar mass).
- [x] **Wikipedia, "Olympias (trireme)"** — crew breakdown (62/54/54), 1987 trials, dimensions, power estimate.
- [x] **Morrison, Coates & Rankov (2000).** *The Athenian Trireme* (oar-loop/thole details; cubit basis; 9 & 9½ cubit oars).
- [?] Roman-wreck interscalmia (Mainz/Oberstimm/etc.): secondary summary only — obtain primary wreck reports if these enter the model.

## 11. Open questions
1. [?] Exact **Table 3.1** values for the ten 1994 oars (overall weight, weight-in-hand, MIT, X per oar) — table body corrupted in the PDF text layer; needed for a precise mass/inertia distribution.
2. [?] Origin of the "**12.3 kg/oar**" figure (build log quote) — likely Shaw/Coates 1990 or Trireme Trust newsletter; findable only in the physical book or newsletter.
3. [?] The "**0.94 m** interscalmium" in the task spec — no Olympias source found (0.888 m design, 0.98 m Mark II); likely Roman-wreck conflation.
4. [?] Blade areas (spade vs teardrop) and exact taper — only in Coates Plans 15/15d/15e/15g (Wolfson archive), not recovered as text.
5. [x] Ch.9 tables 9.1/9.2/9.6/9.7 are decoded (OCR) and all numerically verified against W=nPLrE/60 and W=1.08(155V³+4.13V⁵) — see `research/lane-1-read/shaw-ch7-ch9-2024.md` and `research/data/t9*_ocr.txt`. **Resolved.**
