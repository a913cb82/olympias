# Lane 5 — the manoeuvring models & the trial-turn anchors

The turning physics: the reference implementation of Andrew Taylor's
dynamics model (Part 1), the research notes behind it — the Excel workbook
hunt, the Kempf manoeuvre source, the Table 31.1 OCR reconstruction
(Part 2) — the F1–F6/G1–G5 trial-turn re-run (Part 3), and the rotation-
about-CLR alternative (Part 4). Companion: `braithwaite-workbook.md` (the
independent 3-DOF model: CGH derivatives, the cross-flow yaw damper
CN 0.4/0.8 `[?]`, Iz = m(L/3)², the Hoerner rudder + the trials parasitic
drag) and `crossflow.py` (the Ω audit).
Status flags: `[x]` = confirmed, `[?]` = unverified/unresolved.
Merged 2026-08 from `manoeuvre-model.md` + `taylor-excel.md` +
`fg-turns-rerun.md` + `clr-rotation.md` (git history holds the split).

---

## Part 1 — W5 manoeuvring model: reference implementation

Reference implementation of Andrew Taylor's trireme dynamics model from
Rankov 2012 ch.31 ("Battle Manoeuvres for Fast Triremes"), built from the
chapter text and the OCR-verified Table 31.1 parameter set.  This is the
Lane 5 deliverable: a runnable model of the Olympias / Mark IIb manoeuvring
dynamics.

Script: `research/lane-5-manoeuvre/manoeuvre_model.py`
Parameters: `research/data/table31-1-taylor-model-parameters.csv`

### 1.1 Model physics (faithful to ch.31)

Forward surge:
```
m_app * dv/dt = Thrust(v) - hull_drag(v) - rudder_drag(v, Phi)
```
- `m_app = 1.10 * displacement` (apparent dynamical mass, §2.1; Table 31.1 row 2)
- hull drag in 3 speed bands (Table 31.1 row 3):
  - Mark IIb: 44.7v² (≤6.7 kt), 83.6v²−1733 (6.7–9), 98.4v²−2933 (>9)
  - Olympias: 40.2v² (≤6.7); higher bands not tabulated → 40.2v² held
- oar thrust linear in speed (§5.2): `Thrust (kN) = 17.4 − 0.967 v(kt)`
- straight-rudder drag included for straight-ahead equilibrium
  (Fig. 31.1 drag curve = "increased surface drag and less disruptive
  rudders"), which pins max speed at ~9.9 kt where thrust = 7.8 kN.

Applied rudder (§2.1, §5.1):
- along-track drag increment: factor × straight-rudder drag;
  factor 0.6 (22.5°) … 3.25 (67.5°) for Mark IIb; 1.4/0.6/0.2 for
  Olympias (the 1.4 at 67.5° is Taylor's Kempf-manoeuvre value).
- Olympias straight-rudder drag = (79.6−40.2)v² = 39.4v² N (row 4).

Turning (§2.2):
- rudder lateral force = coeff(Φ) × rudder along-track drag,
  `coeff = 0.14 + 0.020Φ − 0.00015Φ²` (fraction of along-track drag, 40–80%).
- rudder torque = lateral force × lever (C of M → rudder, row 9).
- one-side-stops torque = (T/2) × lever to oar race (row 10).
- yaw: `I dω/dt = Q_rudder + Q_oar − Ωω²`; steady
  `ω = √((Q_rudder+Q_oar)/Ω)`, `R = v/ω`.
  `Ω` (row 12) is a rotational-resistance coefficient, **units kg m² s**
  (units caveat C1 in the uncertainties register; resolved by the cross-flow
  audit — see `crossflow.py`).
- drift angle from lateral force balance:
  `ρ A_lat v² sin β + F_rud_lat = m_app v²/R`.

Heel (§2.3):
- tipping = rudder lateral force × arm_rud (row 14) + hull lateral reaction
  × arm_lat (row 13); restoring = m·g·GM_eff with GM_eff = GM − 0.2 m
  (crew lean into turn, c.g. at seat height).  Limit 3° (oar-rig).

### 1.2 Validation vs published targets (section 6)

| Quantity | Model | Target | Error |
|---|---|---|---|
| coeff(22.5°) | 0.514 | 0.40–0.80 band | ✓ |
| coeff(45°) | 0.736 | 0.40–0.80 band | ✓ |
| coeff(67.5°) | 0.807 | 0.40–0.80 band | ✓ (slightly >0.80) |
| Fast anastrophe D | 151.8 m | 145 m | +5% |
| Tight anastrophe D | 74.6 m | 80 m | −7% |
| Olympias tightest D | 64.0 m | 62 m | +3% |
| v at 10 s | 5.56 kt | 5.5 kt | +1% |
| v at 24 s | 9.01 kt | 9.0 kt | 0% |
| v at 40 s | 9.81 kt | ~9.9 kt | −1% |
| Braking stop | 19.0 s, 56 m | <20 s, <170 m margin | ✓ |
| Astern speed (60 s) | 9.38 kt | 9.4 kt | 0% |
| Heel fast anastrophe | ~4.0° | 3.5° stated (with deck-crew move to inside) | +0.5° |

The implementation reproduces all headline manoeuvrability numbers from
§6.1–6.2 to within ~7%, with the as-published parameter values — no fitting
was required.  This is strong evidence the model captures Taylor's
mechanics correctly.

### 1.3 Caveats

- **Yaw-rate / 360°-time**: the model's ω is fixed by torque balance at a
  *constant* speed, so it predicts ~60 s per 360° at 6.5 kt entry, whereas the
  observed tightest turn took 128 s.  ch.31 §6.2 states the tightest turn
  "halves speed"; at an average 2.91 kt the observed yaw is 2.81°/s (≈360° in
  128 s) — consistent with the trial reports' "2.6–3°/s".  Reproducing the
  time history would need a full time-domain yaw integration with
  deceleration, which Taylor's Excel (steady-state) model also did not
  provide.  The diameter, the quantity the tactical analysis uses, still
  matches.
- **Drift angles** computed (1.1–4.2°) are lower than the measured 7.8–15°
  the chapter quotes for full-rudder turns — the chapter itself notes the
  wide scatter (3 s × 2.6 °/s = 7.8° vs stated 15°±2°, "assume the lower
  value").  The model's drift comes out of the force balance; matching the
  measured drift would require a lower A_lat or a different lateral-force
  split.  Drift is secondary to the turn diameter, which is what the
  tactical numbers validate.
- **Heel slightly over-predicts** (4.0° vs 3.5° for the fast anastrophe,
  5.4° for the max-speed tight turn vs Taylor's "≤3° with deck-crew move
  to the inside beam").  The simplified lateral-force balance treats the
  hull reaction as acting through the arm_lat point; Taylor's Excel likely
  distributes the reaction differently.  Directionally correct and within
  ~1–2°; flagged rather than tuned.
- **Olympias drag above 6.7 kt**: Table 31.1 leaves the higher-band cells
  blank (pixel-confirmed); the model holds 40.2v².  The Olympias band-2/3
  formulas would come from the tank-test curves (see lane-3 `hull-form.md`).
- **Mark IIb thrust law** (17.4 − 0.967v) is used for Olympias too (§5.2
  says the chapter "adopted a similar relationship"; Table 31.1 does not
  tabulate a separate Olympias thrust law).  For an Olympias-specific
  acceleration study the lane-4 propulsion model (oar chain) should drive
  thrust instead.

---

## Part 2 — Taylor's Excel dynamics model + Kempf manoeuvre: research notes

Task brief: find the Excel dynamics-model workbook behind Andrew Taylor's chapter
"Battle Manoeuvres for Fast Triremes" and a primary source for the "Kempf manoeuvre"
rudder-drag method.

### 2.1 The chapter and the Excel model

- Source chapter: **Andrew Taylor**, "Battle Manoeuvres for Fast Triremes", in B. Rankov (ed.),
  *Trireme Olympias: The Final Report. Sea Trials 1992–4, Conference Papers 1998*,
  Oxbow Books, Oxford, 2012, pp. 231–243 (book pp. 231–244). ISBN 978-1-84217-434-0.
- The author is **Andrew Taylor** (rowing master on Olympias 1994; also wrote ch. 4,
  "The Slow Trireme Experience in Olympias in 1994"). The task brief said "Timothy Taylor";
  that is incorrect — Timothy Shaw is the other contributor. [x]
- Full book PDF is freely downloadable (whole book, 27.7 MB, 257 pp):
  https://www.ancientportsantiques.com/wp-content/uploads/Documents/AUTHORS/Rankov2012-TriremeOlympia.pdf [x]
- The dynamics model of Olympias and a proposed "Mark IIb fast trireme" was **built as
  Excel spreadsheets** — stated in the chapter (p. 232): "equations as a function of speed
  in three separate speed bands". [x]
- Model detail (from chapter text): oar thrust matched to sum of hull + straight-rudder
  drags at entry speed; linear drag increases with drift angle; water resistance acts at
  angle = half the drift angle; effective lateral cross-section ≈ wetted hull cross-section. [x]
- Figure 31.1 caption (p. 232): drag curve = parameterised summary of Shaw (1990) for
  Olympias with increased surface drag and less disruptive rudders; oar thrust linear,
  dropping to zero at 18 kts. [x]
- The 1.4 / 0.6 / 0.2 rudder-drag factors (at 67.5°/45°/22.5°) are Taylor's OWN model
  parameters ("An extra increment of linear drag equal to 1.4 times the straight rudder
  drag ... reduced to 0.6 ... and 0.2 ... when modelling the reported Kempf Manoeuvre"). [x]

### 2.2 Availability of the Excel workbook — NOT public

- tDAR record 424186 (whole book): **citation only**, no files:
  https://core.tdar.org/document/424186/trireme-olympias-the-final-report-sea-trials-1992-4-conference-papers-1998 [x]
  Note: `/book/424186` URL 404s; the valid path is `/document/424186/...`. [x]
- tDAR record 424277 (this chapter): **citation only**, "We do not have a copy of this
  document, it is a citation.": https://core.tdar.org/document/424277/battle-manoeuvres-for-fast-triremes [x]
- ancientportsantiques.com hosts ONLY the PDF; no supplementary files/Excel. [x]
- Trireme Trust archive (trust wound up 2017; archive now at Wolfson College, Cambridge,
  https://www.wolfson.cam.ac.uk/library/archives/trireme-trust). Searchable catalogue at
  triremetrust.org.uk. Searches: "Taylor" → 1 record (TT:419, 1994 sea-trials reports);
  "manoeuvre" → 0; "Excel" → 0; "computer" → TT:157, TT:293 (3D model, not Excel);
  "model" → 21 records (physical models). No Excel dynamics model in the catalogue. [x]
- Conclusion: the workbook is not online anywhere found. Most likely avenues to obtain:
  1. Wolfson College, Cambridge archive (Trireme Trust papers; archivist@wolfson.cam.ac.uk). [?]
  2. The author, Andrew Taylor (no public email found; may be reached via the Trireme Trust
     / Wolfson archive or via co-authors Shaw/Rankov). [?]
- [x] No forum/blog/other copy located via general web search.

### 2.3 "Kempf manoeuvre" — primary reference

In Taylor's chapter, "Kempf (or Zig-Zag) Manoeuvre" = the **standard zig-zag manoeuvre**
trial of naval architecture. It supplied data on how quickly Olympias entered/exited turns
(moment of inertia + rotational drag about the vertical axis). The 1.4/0.6/0.2 rudder-drag
factors are Taylor's calibration values, NOT a named published "Kempf rudder-drag method". [x]

Primary source for the Kempf (zig-zag) manoeuvre itself:
- **Kempf, G. 1944. "Maneuvering Standards for Ships." Deutsche Schiffahrts-Zeitschrift,
  Hansa, No. 27/28.** [x]
  Year confirmed as 1944 via two independent bibliographies:
  - Motora, S. & Couch, R.B. (1960s) bibliography of ship-manoeuvrability reports,
    Univ. of Michigan hdl 2027.42/96609. [x]
  - J-STAGE paper (Motora/Fujino 1970, on steering quality indices). [x]
- Supporting history: the zig-zag test was developed at HSVA (Hamburg) in the 1930s by
  Kempf (with Krämer) — "Standardmanövrierversuch ... von Kempf und Krämer bereits in den
  dreißiger Jahren initiiert" (German HSVA documentation). [x]
- Related Kempf papers found:
  - Kempf, G. & Hebecker, O. 1943. "Bordversuche zur Ermittlung der Manövrierfähigkeit von
    Schiffen. Der Standard-Manövrier- und Ausweichversuch." *Der Seewart* 1943(2). [x]
  - Nomoto, K. 1960. "Analysis of Kempf's Standard Maneuver Test and Proposed Steering
    Quality Indices." 1st Symposium on Ship Maneuverability, DTMB Report 1461. [x]
- Taylor's chapter bibliography (line ~857 of extracted text) lists only Coates et al.
  1990, Lowry & Squire 1989, and Shaw 1993 — **Kempf is not cited**. [x]

### 2.4 Table 31.1 (p. 232) — full reconstruction by OCR [x]

The table body text is garbled even in the PDF text layer (glyphs in Private Use Area,
e.g. U+F001..), but a full-page render of book p. 232 (6x render via pymupdf) read
reliably with easyocr. Two independent renders (3x and 6x) agree.
Header [x]: "Table 31.1. Model parameters used to fit the observed performance of Olympias
recorded during sea trials and to extend the model to predict the dynamics possible for an
optimised fast, Mark IIb trireme design."

Reconstructed rows (parameter | Olympias | Fast trireme | units):
1.  Mass of vessel                                     | 42.0   | 44.0   | tonnes
2.  Apparent dynamical mass for forward linear motion | 46.2   | 48.4   | tonnes
3.  Drag for bare hull (v in knots):
    - up to 6.7 knots                                 | 40.2 v² | 44.7 v² | N
    - 6.7–9.0 knots                                   | (blank) | 83.6 v² – 1733 | N
    - over 9.0 knots                                  | (blank) | 98.4 v² – 2933 | N
4.  Drag from straight rudders deflecting water in a turn | (79.6 – 40.2) v² | 10 v² | N
5.  Effective lateral cross-section deflecting water in a turn | 35 | 39 | m²
6.  Waterline length                                  | 32.2   | 35.2   | m
7.  Draft                                             | 1.1    | 1.1    | m
8.  Height of centre of gravity above keel (KG) for ship plus 200 crew | 1.94 | 1.9 | m
9.  Distance from centre of mass to the rudder (along centre line) | 14.9 | 16.5 | m
10. Lever arm from centre of mass to the centre of the oar race | 4.8 | 5.4 | m
11. Moment of inertia about vertical axis              | 4×10⁶  | 5×10⁶  | kg m²
12. Coefficient for resistance of water to angular velocity | 5×10⁶ | 6×10⁶ | kg m² [?]
13. Vertical lever arm from C of M to lateral resistance of water on ship's hull | 1.46 | 1.42 | m
14. Vertical lever arm from C of M to middle of rudder lateral resistance | 1.16 | 1.12 | m
15. Metacentric height                                | 0.97   | 0.9    | m

- The two Olympias cells for the 6.7–9.0 and over-9.0 drag bands are confirmed **blank**
  (pixel analysis of the render shows 0 dark pixels in those cells); only the Fast-trireme
  column carries the higher-band formulas. [x]
- Row 4 checks out against the chapter text: Olympias straight-rudder drag
  (79.6 – 40.2)v² = 39.4v² vs Fast 10v² ≈ 39.4/4 — matching the p. 234 statement that the
  fast hull's fully-immersed straight-rudder drag is one quarter of Olympias's. [x]
- Row 12 unit likely includes a per-second factor (kg m² s⁻¹ would be dimensionally correct
  for a rotational-resistance coefficient); printed cell reads "kg m²". [?]
  (Resolved by the cross-flow audit: Ω IS the quadratic pure-rotation moment — `crossflow.py`.)
- Machine-readable copy saved to `research/data/table31-1-taylor-model-parameters.csv`. [x]
- The text-layer numbers recorded earlier (`1.2 1.4`, `2.8`, `20% 45% 90%`, `9.6 9.8`, …)
  are NOT part of this table — they came from scrambled PUA glyphs and should be ignored. [x]

### 2.5 Full-read notes (ch.31, book pp.231–243, text from rankov2012.txt) [x]

Fitting observations and additional model detail from a complete read of the chapter:
- **Fitting data**: turns fitted = Coates et al. (1990, 87–88) tables F and G → F1–F6
  (Hellenic Navy crew) and G1–G5 (Trust crew). [x]
- **G1–G5 (Trust crew)**: flat measured oar-thrust curve over 4–7 kts → assumed constant
  effective thrust through the turn (unless heeled too much) or halved if the inside oar-bank
  stopped. G2/F2 entry speeds unusually low (crew assumed to have increased output in turn);
  G3 not completed (not useful for drift-angle analysis). [x]
- **F1–F6 (Hellenic Navy crew)**: wider variety of rudder angles; several trials with only
  thranites rowing (lower thrust). F1 (smallest rudder angle) entry thrust hard to reconcile
  with total drag — long turn duration likely reduced oar thrust. F5/F6 had slightly low
  entry speeds; half-crew could have increased effort. [x]
- **Drift angle**: steady-state turning achieved well before 90° of heading change; drift
  angle ≈ (time between ship's head and ship's track reaching 90°) × yaw rate. Stated drift
  angle for G1/G2 (full rudder, full crew) = 15° ± 2°; time-delay method gives 3 s × 2.6 °/s
  = 7.8° — Taylor assumes the lower value. [x]
- **Heel (2.3)**: heel = balancing rudder + lateral-resistance tipping moments against
  ship-as-pendulum with length = metacentric height. c.g. height above USK (under-side of
  keel) used for the lateral-resistance response; **0.2 m lower effective height** used for
  GM (crew lean into turn, c.g. at seat height). Heel ~3° max (oar-rig limit). [x]
- **Kempf (zig-zag) data**: the key source for how fast Olympias entered/exited turns
  (moment of inertia + rotational drag about vertical axis); advance/transfer of turning
  curves gave response data for unbalanced rudder torque and one-side-stops rowing. [x]
- **Mark IIb changes (5.1)**: +3 m length, +2 t displacement (42→44 t), main mast/yard/sail/
  gear landed before battle (not in mass balance), GM −0.1 m, draft unchanged, slightly wider
  beam (still fits ship-shed pillars), increased wetted surface → frictional drag ∝ length.
  Wave-making peaks at 6.5, 8.2, 10.6 kts (Froude-based), bracketing the 9–10 kt max and a
  low-resistance window at ~7.6 kt (Xenophon long-day row). Hull drag formulas = parametric
  equations from Coates et al. (1990, 74), presented in Table 31.1. [x]
- **Mark IIb rudder**: optimised rudder, minimum drag = ¼ of Olympias full value (≈ partially
  immersed at max speed); applied-rudder along-track drag factor 0.6–3.25× straight value. [x]
- **Mark IIb oar thrust (5.2)**: Shaw (1990, 29) projected 200 W/rower (thranite+zygian)
  for maximal 6-min effort = 23 kW / 116 rowers. Mark IIb at ~60% rig efficiency → 300 W/rower,
  51 kW / 170. Model assumes **40 kW sustained for a few minutes** (manoeuvres all < 2 min).
  Max speed 9.9 kts at effective oar thrust 7.8 kN (drag–thrust intersection, Fig. 31.1).
  Thrust–speed line: **Thrust (kN) = 17.4 − 0.967 × speed (knots)** (from Shaw 1990, 25). [x]
- **Manoeuvrability results (6)**: acceleration 0→5.5 kts in 10 s, 9 kts at 24 s, full speed
  ~40 s; backward rowing at 80% of forward thrust → 9.4 kts sternwards (hull drag same);
  braking routine: rudders flared 67.5° opposite → stop from 9.9 kts in <20 s over 170 m,
  backing at 9.4 kts after 60 s. Tightest turn at 10 kts with heel ≤ 3° = 140 m diameter;
  fast anastrophe (9.5 kts, 22.5° rudder) = 145 m; tight anastrophe (one side stops, full
  rudder) = 80 m at 6.5 kts; Olympias tightest recorded = 62 m (halves speed). [x]
- **Tactical numbers (7)**: safe approach to isolated ship 160 m (fast anastrophe) / 250 m to
  a rank; diekplous gap ≥ 150 m (130 m with aggressive turn); 60 m cross-front immunity
  (periplous around ends of a line); files spaced 100 m (enough room to turn in place);
  close into a single rank takes up to 70 s (file >5 ships can't react in time). Battle
  paradigm (8): fast fleet forces slow fleet into close rank, seeks diekplous, falls back
  via anastrophe, or periplous around ends; slow fleet forms kuklos (circle). [x]
- **UCL comparison (4)**: Simon Rusling & Tristan Smith (pers. com. 2006), Mechanical
  Engineering, UCL — more conventional approach, close agreement because both fit the same
  Olympias trial data. [x]
- **External confirmation of model outputs (S13)** [x]: Alke Dominis blog ("what the diekplous
  are you talking about", part 2, 2022) independently reproduces the chapter's tactical numbers
  from the published text — 0→full ~9.5 kt in ~40 s, reverse at 80% of full speed, fast 180° turn
  @ full speed = 145 m diameter, tight 180° turn @6–7 kt = 60 m, diekplous gap ≥150 m (130 m with
  aggressive turn). All match §6 above.

### 2.6 Open questions / next steps

- Get the workbook: contact Wolfson College archive or Andrew Taylor. [x: leads, unresolved]
- Full Table 31.1 reconstruction completed by OCR (see §2.4 + CSV artifact). [x]
  Remaining: reviewer/author sanity-check of the values against the printed book.
- Zig-zag data source Taylor used for Olympias: likely Lowry & Squire (1989) or Coates et al.
  (1990) — the chapter cites these. [?]

---

## Part 3 — W5 re-run: trial turns F1–F6 / G1–G5 — findings

Script: `research/lane-5-manoeuvre/fg_turns_rerun.py` (python3, stdlib only).

### 3.1 What we set out to check

ch.31 §3 says the model was fitted to the eleven trial turns in Coates et al.
(1990, 87–88) tables F & G (F1–F6 Hellenic Navy crew, G1–G5 Trust crew).
Task: re-run the model against those turns and document the match.

### 3.2 Data constraint (important)

The per-turn raw numbers (entry speed, applied rudder angle, turn diameter,
turn duration) appear ONLY in tables F & G of *The Trireme Trials 1988*
(Coates, Platis & Shaw, Oxbow 1990, ISBN 0946897212), pp. 87–88. [x]
That report is print-only; we do not hold a copy and no digitised copy was
found online (OBNB, tDAR, Trireme Trust archive catalogue, university
catalogues — all bibliographic records only).  ch.31 §3 reproduces only
*qualitative* per-turn notes.  **A cell-by-cell fit check against F/G is
therefore impossible from our sources.**  [x]

### 3.3 What we could validate (all anchors published in the book / trial reports)

The model reproduces every DIAMETER anchor to ≤7% (headline W5 validation):

| Anchor | Published | Model | Error |
|---|---|---|---|
| Tightest Olympias turn | 62 m (1.9 × 32.2 m LWL, Morrison 1988) | 64.0 m | +3% |
| Fast anastrophe (9.5 kt, 22.5°, Mark IIb) | 145 m | 151.8 m | +5% |
| Tight anastrophe (6.5 kt, full rudder, one side stops, Mark IIb) | 80 m | 74.6 m | −7% |

Scenario behaviour matches ch.31 §3 qualitatively: [x]
- F1 (smallest applied rudder angle, 22.5°) → largest diameter of the F set (111.9 m) ✓
- F2–F4 (45°) → 93.5 m ✓
- F5/F6 (thranites only, low entry speed) → 89.4 m @ 5.5 kt ✓
- G1–G3 (full rudder, full crew) → 89.4 m @ 6 kt, yaw 3.6–4.0°/s ✓
- G4/G5 (45°) → 93.5 m ✓

### 3.4 Documented discrepancies (caveats, not fitted)

1. **Yaw rate / 360°-time** [x] — model steady-state ω at constant speed gives
   ~60 s per 360° (6.5 kt entry), but Morrison 1988 measured 128 s for the
   1.9-length turn.  The observed turn halves speed (ch.31 §6.2), giving mean
   2.91 kt → 2.81°/s → 360° in ~128 s, matching the trial reports' ~2.6–3°/s.
   Matching the time history needs a full time-domain yaw integration with
   deceleration — Taylor's Excel model was steady-state too, so the diameter
   (which the tactical analysis uses) is the validated quantity.
2. **Drift angle** [x] — model force balance gives ~1.4° for G1/G2 vs the
   reported 15°±2° (Taylor himself reduces to ~7.8° via the time-delay
   method).  Known caveat (Part 1 §1.3); needs lower A_lat or a different
   lateral-force split to match, and drift is secondary to diameter.

### 3.5 Open items

- [ ] Per-turn F/G data (entry speed, rudder angle, diameter, duration for
      each of F1–F6, G1–G5): requires *The Trireme Trials 1988* (print-only,
      ISBN 0946897212).  Leads: Wolfson College archive (Trireme Trust
      papers), Oxbow out-of-print copies, university libraries (U. Crete
      catalogue record exists).  This is the same physical-archive path as
      the Taylor Excel workbook (Part 2 §2.2).
- [x] Independent anchors used here are logged in the main doc §6.2 and
      lane-6 `validation.md` Part 1 where relevant.

---

## Part 4 — W5 Richard's alternative: rotation about centre of lateral resistance vs c.g.

Script: `research/lane-5-manoeuvre/clr_rotation.py`.

### 4.1 Motivation

ch.31 §2.2 (book p.234) states Taylor modelled rotation about the vertical axis
**through the centre of mass (c.g.)** of the ship, and explicitly flags this
"is a principal difference from the UCL model" (Rusling & Smith, pers.
com. 2006), which rotated about the **centre of lateral resistance (CLR)**.

### 4.2 Model

Added `steady_turn_about_clr(vessel, v, phi, fac, one_side, x)` where `x` =
distance of the CLR **forward of the c.g.** (m).  Same physics as
`manoeuvre_model.steady_turn`; only the rotation-point choice changes:

- rudder lever arm: `L_rud = lever_rudder + x`  (rudder astern of c.g.)
- one-side oar lever: `L_oar = |lever_oar − x|`  (oar race forward of c.g.)
- the hull lateral (drift) force passes through the CLR, so it contributes no
  yaw moment about the CLR axis (in the c.g. model it enters only via the
  lateral force balance, which is unchanged).
- `Omega` (rotational resistance) and all drags kept at the trial-fitted
  values, isolating the pure geometric effect of the rotation point.
- `I` (moment of inertia) does not enter the steady-state turn, so the
  parallel-axis shift `I_clr = I + m·x²` affects only the transient, not the
  steady diameter reported here.

### 4.3 Realistic x (CLR forward of c.g.)

Olympias LCG = 17.5 m from the stern post (ch.25) on LWL 32.2 m → c.g. about
14.7 m from the bow.  With the ram and a long lateral plane, the CLR typically
sits ~0.5–2 m further forward, so **x ∈ [0.5, 2.0] m**.

### 4.4 Results (diameter, m)

| case | x = c.g. (Taylor) | x = 0.5 | x = 1.0 | x = 1.5 | x = 2.0 | published target |
|---|---|---|---|---|---|---|
| tightest Olympias [Oly] | 64.0 | 65.1 | 66.2 | 67.4 | 68.7 | 62 |
| fast anastrophe [MkIIb] | **151.8** | 149.5 | 147.4 | 145.3 | 143.4 | **145** |
| tight anastrophe [MkIIb] | **74.6** | 76.3 | 78.2 | 80.3 | 82.5 | **80** |
| G1 full rudder [Oly] | 89.4 | 87.9 | 86.5 | 85.2 | 83.9 | (print-only) |
| F1 small rudder [Oly] | 111.9 | 110.1 | 108.4 | 106.7 | 105.1 | (print-only) |

### 4.5 Findings

1. **The rotation-point choice is a second-order effect on turn diameter**:
   ≤ ~5% across the realistic x band.  This quantitatively supports Taylor's
   statement that his c.g.-axis model and the UCL CLR-axis model agreed
   closely (both fitted to the same Olympias trial data). [x]
2. **Direction of the effect differs by turn type** [x]:
   - rudder-dominated turns (fast anastrophe, G1, F1): moving the rotation
     point forward **lengthens** the rudder lever → tighter turn;
   - oar-one-side-stops turns (tight anastrophe): moving forward **shortens**
     the oar lever → wider turn.
3. **Best joint fit**: x = 1.45 m reproduces both anastrophe targets to
   0.4% / 0.1% (fast 145.5 vs 145 m; tight 80.1 vs 80 m), i.e. *slightly
   better* than the c.g.-axis model's +4.7% / −6.7%.  That x is squarely in
   the physically-plausible band, so a small CLR-forward-of-c.g. correction
   is consistent with the trial data — worth adopting as a refinement rather
   than a fundamental correction. [x] (The LL's fitted clr_offset +0.8 m is
   this family; the real-lines audit — simulation/docs/next-steps Stream B1 —
   is the named path to a computed value.)
4. **Caveat**: `Omega` was kept fixed.  A CLR-axis model would in principle
   re-fit `Omega` to the same trial turns; because the diameter change is
   small this would not alter the qualitative conclusion. The transient (and
   the zig-zag/entry behaviour) WOULD shift with the parallel-axis inertia
   change `I → I + m·x²` (≈ +2.2% at x = 1.45 m for m = 44 t) — noted, not
   modelled (Taylor's own model is steady-state). [x]

### 4.6 Bottom line

Richard's alternative (rotation about the CLR, UCL-style) changes predicted
turn diameters by ≤ ~5% for physically plausible CLR positions, and actually
improves agreement with the two anastrophe targets at x ≈ 1.4–1.5 m.  The
difference between Taylor's c.g.-axis and the UCL CLR-axis models is real but
small — consistent with the "close agreement" Taylor reports.  Adopt a small
forward CLR offset (x ≈ 1.4 m) as the default rotation axis in the reference
model, keeping the c.g.-axis as the published-baseline variant.
