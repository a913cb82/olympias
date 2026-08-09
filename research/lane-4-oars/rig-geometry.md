# Lane 4 — W3 Rig geometry: three tiers, thole-pin positions, lever ratios, stroke

Consolidates the oar-rig geometry needed by the simulation, drawn from Rankov 2012 (*Trireme
Olympias: The Final Report*) ch.1 (1992 trials), ch.3 (1994 trials + Shaw's App.3 stroke model),
ch.9 (Shaw's revised design geometry), ch.8 (oarport freeboard), Coates Plan 8 (midship section),
and Richard Braithwaite's 1:24 build log (manikin/ergonomics). All numbers verified against the
source equations. Complement to `oar-data.md` (oar inventory/mass/blades) and `propulsion-models.md`
(speed→power chain).

Confidence flags: `[x]` confirmed from primary text; `[?]` inferred/unverified.

---

## 1. The three tiers

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

## 2. Thole-pin positions & oarports

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

## 3. Lever ratios / gearing (verified)

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

## 4. Stroke geometry — the thalmian head-room problem

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

### Shaw's analytical stroke model (Rankov ch.3 App.3, p.62) — verified
- 167 cm man on fixed thwarts, rig-unrestricted: max **~1.1 m** at the butt; −10% end loss →
  effective **~0.99 m**.
- Inside an uncanted rig, interscalmium 0.98 m: total movement ≤ 0.98 − 0.15 clearance = 0.83 m,
  minus 0.11 m end losses → effective **~0.87 m**. Same end-loss 0.11 m in all cases.
- At 7½ kt restoring speed after stroke loss needs either rate ×1.17 (0.87 m → 37.4 spm) or gearing
  2.8 → 3.18. `[x]`

### Ch.9 chord-of-pull (Table 9.2) & sweep angles (verified by recomputation)

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

## 5. Oar dimensions (Table 9.1, verified)

All metres. Parenthesised = horizontal projection (×cos 30°). `[x]` (Rankov ch.9 Table 9.1; OCR
`research/data/t91_t92_ocr.txt`)

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

## 6. Summary for the simulation

- **Lever ratio per tier**: thranite/zygian ≈ **2.8–2.82** (model default 2.817, Olympias design);
  thalmian effective **2.57–2.96** depending on position — the 2.96 setting is the realistic upper
  bound and increased thalmian work.
- **Stroke (effective pull length L at the butt)**: Olympias **0.89 m** (design 0.80 m, manikin
  ~0.72 m, observed 0.82–0.85 m — rig/head-room limited); Mark IIa **0.87 m**; Mark IIb **0.99 m**.
  `[x]` (Table 9.7)
- **Sweep angles**: Olympias 48.1°, IIa 48.4°, IIb 55.6°.
- **Tier heights**: zygian oarports 1.0 m above calm water; upper tiers cannot lift blades much
  higher than thalmians (hand-height constraint).
- The thalmian head-room limit is captured in the model as a reduced effective L (and hence power)
  for the lower tier at high rates; Mark II removes it (0.98 m + 18.4° cant).

## 7. Sources
- [x] Rankov 2012 ch.1 §1.4.2 (thalamian levers) pp.37–39; ch.3 App.2/3 (oar spec, stroke model)
  pp.60–62; ch.8 p.75 (oarport freeboard); ch.9 pp.76–81 (Tables 9.1, 9.2, sweep model); ch.10 p.85
  (Fig. 10.3 triad arrangement); Fig. 24.2 caption p.9 (thalamian-head beams 10% closer than 0.888 m).
- [x] Braithwaite build log: Plan 8 midship section extract; 800 mm design / ~720 mm manikin stroke;
  thole-pin placement; outrigger thole drilling; thalmian head-room GIF discussion.
- [x] Recomputation in this note: sweep angles (48.1/48.4/55.6°), lever ratios, 0.80 m head-gap
  (0.888 × 0.90).
