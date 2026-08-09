# Taylor's Excel dynamics model + Kempf manoeuvre — research notes

Status flags: `[x]` = confirmed, `[?]` = unverified/unresolved.

Task brief: find the Excel dynamics-model workbook behind Andrew Taylor's chapter
"Battle Manoeuvres for Fast Triremes" and a primary source for the "Kempf manoeuvre"
rudder-drag method. Lane 5 = manoeuvring dynamics of the Olympias reconstruction.

---

## 1. The chapter and the Excel model

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

## 2. Availability of the Excel workbook — NOT public

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

## 3. "Kempf manoeuvre" — primary reference

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

## 4. Table 31.1 (p. 232) — full reconstruction by OCR [x]

The table body text is garbled even in the PDF text layer (glyphs in Private Use Area,
e.g. U+F001..), but a full-page render of book p. 232 (`tools/b232_6x.png`, 6x
render via pymupdf) read reliably with easyocr. Two independent renders (3x and 6x) agree.
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
- Machine-readable copy saved to `research/data/table31-1-taylor-model-parameters.csv`. [x]
- The text-layer numbers recorded earlier (`1.2 1.4`, `2.8`, `20% 45% 90%`, `9.6 9.8`, …)
  are NOT part of this table — they came from scrambled PUA glyphs and should be ignored. [x]

## 5. Full-read notes (ch.31, book pp.231–243, text from rankov2012.txt) [x]

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

## 6. Open questions / next steps for the orchestrator

- Get the workbook: contact Wolfson College archive or Andrew Taylor. [x: leads, unresolved]
- Full Table 31.1 reconstruction completed by OCR (see §4 + CSV artifact). [x]
  Remaining: reviewer/author sanity-check of the values against the printed book.
- Zig-zag data source Taylor used for Olympias: likely Lowry & Squire (1989) or Coates et al.
  (1990) — the chapter cites these. [?]
