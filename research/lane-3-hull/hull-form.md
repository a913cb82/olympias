# Lane 3 — the hull form & the offsets hunt

The underwater hull geometry: the parametric reconstruction (Part 1, the
Step-1/W2 deliverable), the offsets availability + Eliav & Helfman weight
study (Part 2), and — since 2026-08-22 — the real Lines-Plan offsets from
the Braithwaite design workbook (`braithwaite-workbook.md` in this lane;
the raw table: `sources/galley-sizing-xlsm/basis_hull_offsets.tsv`).
Confidence flags: `[x]` = confirmed from a cited source; `[?]` = inferred /
unverified / conflicting. Merged 2026-08 from `parametric-hull-form.md` +
`offsets-eliav.md` (git history holds the split).

---

## Part 1 — Parametric hull form (Step 1: W2)

Reconstruction of the Olympias underwater hull form from the anchors
available in the text, using a parametric circular-arc geometry.  This is
the geometry deliverable for Lane 3 (W2 hull form / resistance).

### 1.1 Why parametric, not offsets

- Coates defines the sections in Plan 3 as circular arcs, but no numeric
  offsets appear in the text (the drawings are images; the assistant
  cannot rasterise them).
- Rather than fabricate a table of offsets, the hull is represented by a
  small parametric model with two free parameters `p` (waterline planform
  fullness) and `q` (rocker) plus the fixed anchors below.  `p` and `q`
  are fitted so that displacement matches the BMT trial and light-ship
  numbers.
- **Update 2026-08-22**: the offset TABLE itself is no longer missing —
  the Braithwaite workbook holds it (see the lane header). The parametric
  hull remains the chain's hydrostatics source where the real table has
  not been re-integrated; register B8 records the real-vs-parametric
  differences (Cw 0.768 vs 0.556, WSA 130.5 vs 81.3 m²).

### 1.2 Fixed anchors

| Anchor | Value | Source |
|---|---|---|
| LWL | 32.2 m (32.08 m) | Taylor T31.1 / Poitiers |
| Waterline beam | 3.430 m | Poitiers model from Coates lines |
| Trial draft | 1.1 m | Taylor T31.1 |
| Trial displacement | 42.25 t (41.22 m3) | BMT ch.25, 80-kg crew |
| Light displacement | 25.80 t (25.17 m3) | BMT ch.25 |

### 1.3 Geometry model

- Waterline half-breadth:  B(x) = Bmax * sin(pi x)^p ,  x in [0,1]
  (Bmax = 3.430/2 = 1.715 m).  p=1.5 gives full ends but slightly
  fuller middle than a sine.
- Rocker:  local draft d(x) = dmax * sin(pi x)^q .  q=0.8 raises the
  ends (reduces draft there) while keeping dmax = 1.1 m amidships.
- Transverse sections: circular arcs with the chord at the waterline and
  arc apex on the keel.  Section area = R^2(theta - sin theta)/2 with
  R = (B^2 + d^2)/(2d), theta = 2 asin(B/R).
- Volume, wetted surface and LCB integrated by 1D quadrature over x.

### 1.4 Fit result

p = 1.5, q = 0.8, Bmax = 1.715 m

| Quantity | Model | Anchor / BMT | Error |
|---|---|---|---|
| Trial volume | 41.35 m3 | 41.22 m3 | +0.3% |
| Light volume | 25.17 m3 | 25.17 m3 | 0% |
| Light draft | 0.694 m | - | - |
| Wetted surface (trial) | 81.3 m2 | - | - |
| Wetted surface (light) | 71.0 m2 | - | - |
| Cb | 0.340 | - | - |
| Cwp | 0.556 | - | - |
| LCB (from stern) | 16.10 m | - | - |
| VCB above keel | 0.493 m | - | - |

Volume sensitivity: across p in {1.0,1.4,1.5,2.0} and q in {0.6,0.8,1.0}
the model spans 37-48 m3, wetted surface 75-85 m2.  The fit is robust:
no combination reaches 0.3% error except (1.5, 0.8), and that lands on
the trial anchor.

### 1.5 Friction cross-checks

**vs Shaw's power law (155V^3 + 4.13V^5)**

Skin friction (ITTC 1957, rho=1025, nu=1.14e-6) using the computed
wetted surface, compared to Shaw's total power at the same speed:

| Speed | Rf | Rf*V | Shaw W | friction fraction |
|---|---|---|---|---|
| 2.0 m/s | 378 N | 0.8 kW | 1.37 kW | 55% |
| 3.5 m/s | 1065 N | 3.7 kW | 8.82 kW | 42% |
| 4.3 m/s | 1561 N | 6.7 kW | 18.4 kW | 36% |

Caveat flagged in earlier work: at 6.8 kt (3.5 m/s) friction is only
42% of Shaw's total, which reads low against Coates ch.22 (skin
dominant below ~6 kt).  Two possibilities: (a) Shaw's law includes
bare-hull plus gear/rudder drag and does not equal the bare-hull
resistance curve alone; (b) the true wetted surface is larger than the
lean circular-arc estimate.

**vs Taylor bare-hull drag (T31.1 row 3: 40.2 v^2 N, v in kt)**

This is the cleaner comparison because T31.1 explicitly gives bare-hull
drag.  The model reproduces the right physics split:

| Speed | Rf | % of Taylor Rt | wave residual | % |
|---|---|---|---|---|
| 4.0 kt | 398 N | 62% | 245 N | 38% |
| 5.0 kt | 602 N | 60% | 403 N | 40% |
| 6.0 kt | 844 N | 58% | 603 N | 42% |
| 6.7 kt | 1035 N | 57% | 769 N | 43% |
| 8.0 kt | 1439 N | 56% | 1134 N | 44% |
| 9.0 kt | 1791 N | 55% | 1466 N | 45% |

Friction stays dominant (55-62%) across 4-9 kt and the wave residual
grows with speed, exactly matching Coates' description that skin
resistance is dominant below ~6 kt and wave-making becomes equal only
near ~9 kt.  This gives confidence in the wetted-surface estimate
(~81 m2) - a larger hull would push friction above Taylor's bare-hull
number and force a negative wave residual.

### 1.6 Stability mismatch (important)

| Quantity | Model | BMT ch.25 |
|---|---|---|
| VCB | 0.493 m | - |
| I_t | 38.5 m4 | - |
| BM | 0.935 m | ~2.2 m implied |
| KM | 1.428 m | 2.90 m |
| GM | -0.34 m (at KG 1.77) | 1.13 m |

The circular-arc waterplane (Cwp 0.556) is too lean: BMT's KM = 2.90 m
implies BM ~2.2 m, i.e. I_t ~93 m4, close to the rectangular-waterplane
value L*B^3/12 = 108 m4.  The real Olympias is fuller and flatter-
bottomed than a pure circular arc.

**Action for Lane 5 (manoeuvring): do NOT use model KM/GM.  Use the
measured BMT values KM = 2.90 m, GM = 1.13 m at the trial condition.**
The parametric hull is adequate for volume, wetted surface and
resistance, but the transverse stability inputs come from the BMT
stability report.

### 1.7 Files

- `hull_form.py` — the parametric model, fit, friction and stability checks
- `hull-form-summary.csv` — the derived hydrostatics table
- `braithwaite-workbook.md` — the real Lines-Plan offsets + hydrostatics
  (Part 2's hunt concluded)

---

## Part 2 — Coates' offsets availability + Eliav & Helfman (2022)

> **UPDATE 2026-08-22 — the numerical offsets are now in hand.** The
> Braithwaite design workbook (`sources/galley-sizing-xlsm/`) contains the
> Olympias offset table from the Lines Plan (21 stations × 27 Z/Y pairs,
> LWL 32.35 m) — extracted to `sources/galley-sizing-xlsm/basis_hull_offsets.tsv`,
> analysed in `braithwaite-workbook.md` (this lane). The Wolfson-archive route
> below remains the path for the full drawing pack (Plan 7 etc.), but the
> offset TABLE itself is no longer missing.

Research notes, web-only. All web access 2026-08-08.

### 2.1 Availability of Coates' hull offsets / lines plan for Olympias

**Where the drawings physically are**
- The Trireme Trust was wound up in 2018; the full archive (John Coates' original plans, specification, construction notebooks, correspondence, sea-trials docs) is deposited **in perpetuity at Wolfson College, Cambridge**. Enquiries to College Archivist, Wolfson College, Barton Rd, Cambridge CB3 9BB — **archivist@wolfson.cam.ac.uk**; catalogue searchable online at triremetrust.org.uk. `[x]` (triremetrust.org.uk; wolfson.cam.ac.uk/library/archives/trireme-trust)
- Visits to view physical documents can be arranged at the Wolfson archive. `[x]` (archive search page)
- Copyright: Wolfson College claims world copyright over all archive material; reproduction requires prior written consent. `[x]`

**Online catalogue (triremetrust.org.uk — plans & technical drawings)**
- The "plans & technical drawings" category lists **24 records**: Plan GA1, GA2, GA3 (general arrangement), **Plan 7 "Trieres — Lines of hull, form No. 7, outside plank, mod. 2"**, Plan 8 (mid section), Plan 9 (foot stretcher), Plan 10 (stern), Plan 11 (fore end), Plan 12 (stern profile/plan), Plan 13 (run of planking), Plan 14 (scarfs), Plans 15/15d/15e/15g (oars), Plan 20 (ram), Plan 21 (decks), Plan 22 (lines of stern), Plan 23 (quarter deck), Plan 24/24a (rudder bearings), Plan 25 (hypozoma tensioning), Plan 26 (trierarch's chair), Plan 27 (gunwales). `[x]` (fetch of catalogue page)
- **Plan 7 (Lines of hull) IS confirmed in the online catalogue**, with a small thumbnail. `[x]`
- **A "Plan 2: Table of Hull Offsets" does NOT appear in the online catalogue's plans list.** `[?]` — Either it is indexed under a different identity number/keyword, is a number from a different drawing set (e.g. the Coates/Morrison 1986 build set or the *An Athenian Trireme Reconstructed* figure set), or is only held physically. The catalogue's keyword search requires JavaScript and could not be exercised via URL; the archivist must be asked directly for the exact catalogue reference for "Table of Hull Offsets" (Coates). `[?]`
- Only thumbnails are online; **no full-resolution lines plan or offset table is downloadable** from the Trust site. `[x]`
- Third-party evidence that the full drawing set can be obtained from the archive: a ModelShipWorld build log (R. Braithwaite, 1/24 Olympias) reports obtaining prints of the drawings from the Trireme Trust in 2006, and later a **CD with the drawings in electronic (TIFF) format**; contact named there is Jude Brimmer (Trireme Trust USA). `[?]` (forum report, date unknown for current validity)

**tDAR record 424186 (Trireme Olympias: The Final Report)**
- Record exists (citation), ISBN 978-1-84217-434-0, Oxbow 2012, EXARC collection. **Explicitly states: "We do not have a copy of this document, it is a citation." — no PDF, no supplementary files (no drawings, no spreadsheets) attached to the tDAR record.** `[x]` (tDAR page fetch)
- Bottom line: tDAR 424186 is NOT a source for offsets or supplementary data. `[x]`

**Digitally-published sources that DO contain Coates' lines (not the offset table)**
- *Trireme Olympias: The Final Report* (Rankov ed., Oxbow 2012) is freely available as a PDF at ancientportsantiques.com: https://www.ancientportsantiques.com/wp-content/uploads/Documents/AUTHORS/Rankov2012-TriremeOlympia.pdf. Frontispiece = "Plan, elevation and cross-sections of Olympias (Drawing: John Coates)"; **Fig. 17.1 "Lines of hull of Olympias (Drawing: John Coates)"** is a line-drawing reproduction (low-res raster, no numerical offsets). `[x]`
- Eliav & Helfman built their CAD hull from "line drawings of Olympias, orthographic views and her given dimensions (Coates et al., 1990, pp. 2–3; Coates, 2012b, p. 136; Morrison et al., 2000, p. 194)". `[x]` (their Methods)
- Wave-resistance modelling paper (arxiv 1905.13024, Univ. Poitiers/CNRS, ~2019-20): "The geometry of the reduced model was based on the hull lines of the trireme Olympias generously provided by the Trireme Trust"; Coates' drawn hull lines were digitised by Christian Oddon (Cabinet Mauric); at waterline: model LWL 32.08 m, beam 3.43 m, draft 1.05 m. `[x]` — indicates the Trust will supply lines to serious researchers.

**Bottom line on offsets**
Offsets / lines plan are **not freely downloadable** (pre-2026-08-22 state; now superseded by the workbook's table — see the lane header). The authoritative path for the full drawing pack is: (a) online catalogue record for Plan 7 (lines of hull) + request copies from **archivist@wolfson.cam.ac.uk** (mention the specific Coates "Table of Hull Offsets" and "Lines of Hull, form No. 7" and the tDAR-exposed Final Report); (b) older practice: Trireme Trust supplied TIFF CDs of the drawing set. Alternatively, the digitised hull lines may be recoverable from the Poitiers/CNRS Actium modelling team (they already hold a numerical lines representation). `[x]/[?]`

### 2.2 Eliav & Helfman (2022) — full quantitative claims

**Ref:** Eliav, J., & Helfman, N. (2022). Lightweight Construction of an Athenian Trireme: A Feasibility Study. *International Journal of Nautical Archaeology* 51(1), 187–194. DOI 10.1080/10572414.2022.2088216. Published online 17 Aug 2022.
**Full-text PDF verified** (downloaded + text-extracted): https://www.ancientportsantiques.com/wp-content/uploads/Documents/ETUDESarchivees/Navires/Documents/Trireme-Eliav2022.pdf `[x]`

**Weight claims (the "Olympias too heavy" thesis)**
- **Empty weight of Olympias (all personnel & equipment removed) = 25 metric tons** (Morrison, Coates & Rankov 2000, p. 210). `[x]`
- Earlier estimates: **21 tons** (Coates, Platis & Shaw 1990, p. 64) and **23 tons** (Coates 1999, p. 107). `[x]`
- After sea trials, designers concluded Olympias should have been **~3 m longer**, which would make her "even heavier" (Coates 2012a). `[x]`
- E&H judgement: 25 t "or even more in the longer version" is **too heavy for a trireme**; there are grounds for considering it excessive. `[x]`
- Reference hull weight breakdown (Morrison et al. 2000, p. 210): the **basic hull** ("a shell ... lightly stiffened over its entire length but with substantial members at the keel and ... round its rim") = **15 tons**; total empty ship 25 t (i.e. ~10 t of outfitting/gear). `[x]`
- Note (Sleeswyk, in Rankov 2012, Ch. 15/24 area): estimate of an *ancient* empty hull of **35 t** based on ram weight ~290 kg and a fully manned & provisioned ship of 58 t (water 8 t, crew+marines 15 t) — i.e. some argue the ancient trireme was *heavier* than Olympias, not lighter. Steffy's rule of thumb: 0.75–1 t of hull per metre of length. Olympias = 25 t / 36.8 m = **0.68 t/m**. `[x]` (Rankov 2012 PDF, "Olympias and her critics" area)

**Mortise-and-tenon vs laced (sewn) construction**
- Olympias was built with **thick planks joined edge-to-edge by pegged mortise-and-tenon (MT) joints**, method taken from Kyrenia & Marsala wrecks (Morrison et al. 2000, p. xx). `[x]`
- MT "dictates" hull weight because planks must be thick enough to hold edge joints. `[x]`
- Laced/sewn construction coexisted with MT in the Mediterranean (6th–4th c. BC wrecks: Gela, Bon Porté 1, Jules Verne 7 & 9, Ma'agan Mikhael parallels); both methods plausibly applied to triremes (Hale 2009 asserts laced). `[x]`
- **E&H FEA result: a laced hull with Olympias' shape/dimensions passes a quasi-static hogging test and is ~46% lighter than the MT hull** (8.1 t modelled laced vs 15 t comparable Olympias basic hull); abstract states "weight reduction of almost 50%". `[x]`
- Laced model: shell **20 mm thick**, keel **173 mm wide × 378 mm high** (same width as Olympias keel, +100 mm height), frames **75 mm square** (same as Olympias), **32 frames**, gunwales **260 × 210 mm**. `[x]`
- Materials assumed: planks of *Abies cephalonica* (fir), keel/frames/wales of *Quercus petraea* (white oak). `[x]`
- Load case: hogging on a wave of length = ship waterline length, height **0.85 m** trough-to-crest (same as used by Olympias designers). Max stresses at 0% shell shear contribution: **tension in gunwale 11.5 MPa, compression in keel 8.9 MPa**; reserve factor 2.7 vs Eurocode 5 requirements 2.3 (permanent) / 1.8 (short-term). `[x]`

**Resistance / speed consequences (the "too heavy → slow" argument)**
- **E&H give NO quantified resistance penalty or speed-loss figure.** Their argument is qualitative: Olympias "fell considerably short of the assumed performance of ancient triremes as deduced from documented voyages"; the standard explanations (short *interscalmium* ~0.88–0.98 m, rower fitness/skill) address only the oar system, "the other is resistance. **High resistance, a direct result of excessive weight, could well be part of the problem.**" `[x]`
- Beaching argument: a ship as heavy as Olympias makes daily beaching "somewhere between formidable and non-feasible"; lighter triremes would make the frequent beaching in the sources more plausible. `[x]`
- Historical context: Aeschylus *Persians* 337–343 (10 fast Greek vs 207 fast Persian triremes); Xenophon *Anabasis* 6.4.2 (Byzantium→Heraclea voyage) may refer to *light* triremes, narrowing the gap to Olympias' performance. `[x]`
- Payload used in FEA: crew of 200 = **15 t**, water+supplies = **2 t**, total 17 t (matches Olympias trials: **42 t displacement − 25 t empty = 17 t**); plus 4 t for rigging/oars/benches. `[x]`
- Hypozomata: 4 ropes, each **257 lb (117 kg)**, ~**280–340 ft** long, anchor spacing 32–34 m, ~80 m loop; hemp rope 2 1/16 in diameter; breaking strength 198 kN per rope, 1600 kN for four; assumed working load 480 kN (30%). `[x]`

**Caveats for the sim (important)**
- E&H used Olympias as the *only* existing reference for trireme weight and the validity anchor for structural strength requirements — i.e. their 25 t IS the Olympias figure the Lane-3 hull model should reproduce. `[x]`
- Their laced-hull weight is a *feasibility-study* number under conservative assumptions (assumed zero shell shear contribution), not a definitive ancient hull weight. `[x]`

### 2.3 Published hull-form numbers (usable as sim targets)

| Parameter | Value | Source | Flag |
|---|---|---|---|
| Length overall (as built) | **36.8 m** | Grimm via UChicago Animus ("36.8 meters long"); grokipedia "36.8 m" | `[x]` secondary |
| Length incl. ram | **36.9 m** | Morrison, Coates & Rankov 2000, p. 208, Fig. 61 (cited in E&H 2022); Wikipedia; Greek navy (36.9 m) | `[x]` |
| Design length (ram excl.) | max 36 m | Shaw, via UChicago Animus | `[x]` secondary |
| Beam (incl. outriggers) | **5.5 m** | Morrison et al. 2000 Fig. 61 (via E&H); Wikipedia; Greek navy | `[x]` |
| Beam (alt.) | **5.45 m** | grokipedia (hull measures ~36.8 × 5.45 m) | `[?]` |
| Draft | **1.25 m** | Wikipedia; Greek navy; Grimm | `[x]` |
| Displacement empty | **25 t** (earlier 21 t / 23 t) | Morrison et al. 2000 p.210; Coates 1990 p.64; Coates 1999 p.107 (via E&H) | `[x]` |
| Displacement, trial full load | **42 t** | Morrison et al. 2000 p.210 (via E&H) | `[x]` |
| Displacement, fully manned (pop.) | **47 t** | Wikipedia; Grimm | `[x]` secondary |
| Displacement (Greek navy) | 35 t | armyrecognition/HN (inconsistent, likely light ship sans gear) | `[?]` |
| Waterline length / beam / draft (model for wave-resistance) | **LWL 32.08 m, beam 3.43 m, draft 1.05 m** | arxiv 1905.13024 (Poitiers/CNRS, from Coates' lines) | `[x]` (model-scale derived) |
| Weight per metre (hull) | 0.68 t/m (25 t/36.8 m); Steffy's ancient range 0.75–1 t/m | E&H; Steffy via Rankov 2012 | `[x]` |
| Ram weight | 200 kg (bronze copy; Piraeus original ~290 kg est.) | Wikipedia; Rankov 2012 | `[x]` |
| Oars/crew | 170 oars, 3 banks (62 thranites / 54 zygites / 54 thalamites); crew of 200 in antiquity | Wikipedia; grokipedia | `[x]` |

### 2.4 Sources & confidence

1. Trireme Trust archive search & plans catalogue — triremetrust.org.uk (Wolfson College). Plans list (24 records) fetched 2026-08-08. `[x]`
2. Wolfson College, Trireme Trust Archive page — wolfson.cam.ac.uk/library/archives/trireme-trust. `[x]`
3. tDAR 424186 — core.tdar.org/document/424186. "We do not have a copy of this document, it is a citation." `[x]`
4. Rankov, B. (ed.) 2012, *Trireme Olympias: The Final Report* — full PDF, ancientportsantiques.com (Rankov2012-TriremeOlympia.pdf). `[x]`
5. Eliav, J. & Helfman, N. 2022, IJNA 51(1) 187–194, DOI 10.1080/10572414.2022.2088216 — full PDF, ancientportsantiques.com; full text extracted & verified. `[x]`
6. Morrison, J.S., Coates, J.F., Rankov, N.B. 2000, *The Athenian Trireme* 2nd ed., CUP — cited indirectly via E&H/Wikipedia; not directly verified online. `[?]`
7. Wave-resistance paper — arxiv.org/pdf/1905.13024 (hull lines from Trireme Trust; LWL 32.08 m etc.). `[x]`
8. Wikipedia "Olympias (trireme)" — 36.9/5.5/1.25, 47 t, ram 200 kg. `[x]` (secondary)
9. UChicago Animus "The Theseus Complex" (2025) — Grimm: 36.8 m LOA, 5.5 m beam, 1.25 m draft, 47 t full / 25 t empty; design max 36 m excl. ram. `[x]` (secondary, college journal)
10. grokipedia "Olympias (trireme)" — 36.8 × 5.45 m, 25 t light / ~44 t full; hull dims from Zea slipways. `[?]` (AI-generated mirror — treat as tertiary)
11. ModelShipWorld build log (R. Braithwaite) — TIFF CD of drawings previously obtainable from Trireme Trust. `[?]`
12. armyrecognition.com (Hellenic Navy) — 36.9 m, 5.5 m, 1.25 m, 35 t. `[?]` (displacement conflicts with 42–47 t elsewhere)

### 2.5 Open questions / next actions (status as of the 2026-08-22 update)

1. **Confirm "Plan 2: Table of Hull Offsets" reference** — email archivist@wolfson.cam.ac.uk requesting (a) exact archive reference & any digital copy of Coates' Table of Hull Offsets and Lines of Hull (Plan 7 / "form No. 7"), (b) reproduction/citation terms. `[?]` — now only for the full drawing pack; the offset table is in hand.
2. tDAR 424186 carries **no** digital files — confirmed; do not waste further time there. `[x]`
3. Ask whether the Poitiers/CNRS Actium team (or Trireme Trust) will share the **digitised numerical hull lines** (they hold an exact CAD of Coates' lines; Eliav & Helfman also hold a CAD of the same geometry). `[?]`
4. Reconcile displacement spread: 25 t empty (Morrison 2000) vs 35 t (HN) vs 47 t full (Wikipedia) — decide which is the sim's hydrostatics baseline; note E&H's trial value of 42 t.
   **RESOLVED (S12)** — primary anchors now in hand from the BMT inclining report via ch.25:
   light ship **25.798 t** (VCG 1.575 m USK, LCG 17.521 m fr. Stn 23), trial w/ crew (80 kg each)
   **42.25 t** (GM 1.13 m). The 47 t "fully laden" figure additionally includes the full naval
   outfit (rigging, masts, oars, benches, stores + troops); 35 t (HN) is inconsistent — drop it.
   Sim baselines: 25.8 t light / 42.25 t trial / 47 t only for fully-laden max-capability
   scenarios. See main md S11/S12.
5. **Towing-tank resistance data (W2/D1)** — a 1:10 hull model was tank-tested at **NTUA
   (Athens) ship tank** during design (confirmed via UChicago Animus retrospective, S12); the
   primary resistance-vs-speed numbers live in Coates 1990 (Taylor ch.31 cites its p.54) — next
   action: extract from the Coates 1990 text/tables in our Rankov 2012 PDF (ch. on design) or
   the 1990 volume, rather than searching the open web.
   **RESOLVED (S13)**: primary tank-test identified = **Grekoussis, C. & Loukakis, T. (1985),
   "Athenian Trireme Calm Water Tests Without Ram", NTUA Report No. NAL 06-F-1985** — Shaw's
   W = 155V³+4.13V⁵ law was deduced from these bare-hull model tests (Rankov 2012 ch.7 p.79);
   resistance/speed curves also published in Shaw 1993 (*The Trireme Project*). Report is not
   online; raw resistance points remain unrecovered → uncertainties register B2.
6. No published **numerical offset table** is openly available — expect to derive offsets from Fig. 17.1 / frontispiece of the Final Report PDF (low-res) or from the archive originals; a DWL draft ~1.05–1.25 m and beam ~5.5 m bound the reconstruction.
   **RESOLVED (2026-08-22)** — the Braithwaite workbook's `basis_hull_offsets.tsv` holds the table.
7. E&H give no quantitative resistance penalty — Lane 3 must compute resistance itself (e.g. from hull form) rather than adopt a literature figure; their weight delta (laced 8.1 t vs MT basic 15 t, ~46–50% lighter) is the anchor for "light vs heavy trireme" scenarios.
