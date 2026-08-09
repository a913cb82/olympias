# Research: Substantive Maths for a Trireme Rowing Simulation

Research tracking for the mathematical/physical basis of a simulation of oared-warship
(Athenian trireme / Olympias reconstruction) performance, motivated by Richard Braithwaite's
software simulation of maneuvering of oared warships (see his build logs in this directory).

Goal: assemble the equations, coefficients, and data sources needed to model
(1) oar/rowing mechanics (force, leverage, stroke geometry, blade hydrodynamics),
(2) hull resistance and propulsion (drag, thrust, speed-power),
(3) ship maneuvering (turning, coefficients of motion, validation against sea trials).

Status legend: [x] done, [ ] pending, [?] uncertain / needs verification.

---

## ⚠️ Living document — update it as you go

This file is the **orchestrator's canonical, single-writer tracking document** for the whole
research effort. It is *not* a finished report: it is a living record that **must be updated as work
progresses**. Every session should leave it more accurate than it found it.

**Rules of engagement (mandatory, every session):**
1. **Whenever you learn something, record it here and in the relevant lane note** — do not wait
   for the end of the session. Tick boxes, add log sections (S8, S9, …), update the plan.
2. **Decoded/recovered numbers go to `research/data/*.csv`** (machine-readable, commented, with
   provenance) and are cited from the notes. Keep `/tmp/opencode` artifacts as scratch only (venvs,
   work-in-progress renders).
3. **Repeatable workflows are written up once in `research/tasks/`** (see the playbook index at the
   bottom of this file) so a later session can re-run them without re-learning. Add a new playbook
   the first time a task is done a second time; update one when a better way is found.
4. **Resolve open questions in place**: when an `[?]` is answered, strike it through and record the
   resolution in the note that raised it (e.g. §9/§10 of `carter-equations.md`).
5. **A lane note must carry provenance** (source / page / table / chapter), exact numbers with units,
   a [x]/[?] confidence flag, and its open questions — matching the log style below.

### Where things live (structure map)

```
trireme-rowing-simulation-research.md      ← THIS FILE: research plan + log (single-writer, by the orchestrator)
research/
├── lane-1-read/          # W1 prose notes (one .md per reader)
├── lane-2-waves/         # W4 notes + decoded-table derivations   (e.g. carter-equations.md)
├── lane-3-hull/          # W2 notes + resistance/offsets data
├── lane-4-oars/          # W3 notes
├── lane-5-manoeuvre/     # W5 notes + extracted workbook/csv
├── lane-6-validation/    # W6 validation table + uncertainties register
├── data/                 # shared machine-readable artifacts (CSV): table31-1, shaw-table-8.3, shaw-table-8.4
└── tasks/                # REPEATABLE-TASK PLAYBOOKS (how-to guides) — READ before doing the task
```

Read `research/tasks/README.md` first when starting any extraction/decoding task; read the relevant
lane note before starting a workstream. When a session ends, tick/append this file so the next
session picks up exactly where we left off.

---

## Research Plan

Roadmap for taking this from "a pile of sourced numbers" to a working, validated
oared-warship simulation. **Guiding principle: understand before coding** — every
equation traces to a source, every coefficient to a sea trial, a towing test, or a
Coates drawing, and nothing enters the model that we cannot defend in a written note.

### Why this is tractable (and who set the precedent)

- **Richard Braithwaite** has already built a software simulation of oared-warship
  manoeuvring, validated against Olympias sea trials, and keeps a 1:24 model (built to
  Coates' drawings, weighed throughout, within 2% of scaled lightship weight) precisely
  so it can supply simulation inputs such as **radius of gyration**.
- **Timothy Taylor (Rankov 2012 ch.31)** published a complete Excel dynamics model
  (drag, rudder, oar-turning-moment, yaw-resistance, heel) already validated against six
  trial turns. Our task is to *re-derive, verify, and re-implement* that model rather than
  invent one from scratch.
- **Rankov 2012 (The Trireme Olympias: The Final Report)** contains the primary trial
  data (speeds, turns, power, and Shaw's wave tables) — the PDF is already local
  (`sources/rankov2012.pdf` + extracted text).

### Data sources to assemble (from build-log bibliography + research notes)

| # | Source | Contents needed | Status |
|---|--------|-----------------|--------|
| D1 | Coates, Platis & Shaw, *Trireme Trials 1988* (Oxbow) | towing resistance vs speed, trial turns F/G tables, oar stats | [ ] source |
| D2 | Lowry & Squire (1989), Poros 1988 | acceleration/turning measurements | [ ] source |
| D3 | Shaw (ed.) *The Trireme Project* (1993) | oar slippage losses (53 W of 115 W), efficiency | [x] numbers in S6 |
| D4 | Rankov 2012 ch.31 (Taylor) | full dynamics model + Table 31.1 coefficients (PDF-garbled) | [ ] re-extract 31.1 |
| D5 | Rankov 2012 ch.23 (Rossiter & Whipp), ch.22 (Coates) | human power curves | [x] in S5/S6 |
| D6 | Rankov 2012 ch.8.x (Shaw wave tables) | H, L, C vs fetch/duration/windspeed | [x] Tables 8.3 & 8.4 decoded + verified (S7) |
| D7 | BMT Defence Services 1991 inclining-experiment report | displacement, c.g. heights, GM, radii of gyration | [ ] obtain |
| D8 | Trireme Trust drawings (Plans 2–9, 15, 26) | hull offsets/arcs, midship section, oar & rowing geometry | [ ] obtain offsets (Plan 2) |
| D9 | Morrisson & Coates, *The Athenian Trireme* (2nd ed. 2000) | ship particulars, design rationale | [x] partial in S1 |
| D10 | Olympias sea-trial aggregation (S1) | validation targets (speeds, turns, endurance) | [x] in S1 |

### Workstreams

**W1 — Source digitisation & table recovery** (current focus)
- [x] Extract Rankov 2012 full text (`sources/rankov2012.txt`).
- [x] Decode subset-font tables (custom cmap + glyph matching — *see Active TODOs below*).
      **DONE — resolved via the OCR route** (Tables 8.3/8.4, 9.1/9.2/9.6/9.7, 31.1 decoded;
      see `research/tasks/pdf-ocr-table-decoding.md`, S7/S8/S11).
- [x] Recover Taylor Table 31.1 (drag/rudder coefficients) — needs OCR or font decode.
      **DONE — full reconstruction by OCR in `lane-5-manoeuvre/taylor-excel.md` §4 + CSV
      `research/data/table31-1-taylor-model-parameters.csv` (S11).**
- [x] Reconcile Table 8.3 decoded values against Carter's relations (L = 1.56 T², C = 1.56 T)
      as an independent integrity check.
      **DONE — all 36 cells reproduce Carter's duration-limited equations with T_z
      convention + fully-developed caps (S7; `lane-2-waves/carter-equations.md` §10).**
- [x] **Read Shaw's three papers in full** (Rankov 2012 Part 2, "ch 7–9", pp. 62–81):
      (1) the Xenophon Anabasis cruising-speed argument (7–8 kts implied), (2) the
      Byzantium→Heraclea voyage and its sea-state/wave tables (pp. 68–75, incl. Table 8.3),
      (3) the Mark IIa/IIb rig redesign (interscalmium → 0.98 m, 18.4° skew). Feeds W3
      (rig geometry, stroke, lever ratios) and W4 (waves), and is the argument we are
      ultimately validating.
      **DONE — ch.7+ch.9 read in full and logged in `lane-1-read/shaw-ch7-ch9-2024.md` (S9);
      ch.8 tables decoded earlier (S7).**
- [x] **Read Taylor ch.31 in full** — "Battle Manoeuvres for Fast Triremes" (Rankov 2012
      pp. 268–77): the complete Excel dynamics model, its assumptions, and the six trial
      turns it validates against. S3 captures the headline numbers but the parameter
      derivation and Table 31.1 coefficients need a careful full read; feeds W5 directly.
      **DONE — full read logged in `lane-5-manoeuvre/taylor-excel.md` §5 and S8.** (Note:
      chapter is actually book pp.231–243, not 268–77 as the earlier plan text said.)

**W2 — Hull geometry & hydrostatics**
- [x] **Parametric hull form built** — `research/lane-3-hull/parametric-hull-form.md` +
      `hull_form.py`: circular-arc sections fitted to BMT trial (41.35 vs 41.22 m³, +0.3%)
      and light (25.17 m³, 0%) displacements; wetted surface 81.3 m² (trial) / 71.0 m²
      (light); Cb 0.340, Cwp 0.556, VCB 0.493 m, LCB 16.10 m from stern. Friction cross-check
      vs Taylor T31.1 bare-hull drag 40.2v² gives 55–62% skin / 38–45% wave residual across
      4–9 kt, matching Coates ch.22 (skin dominant <~6 kt). **Stability caveat**: model KM
      1.43 m under-predicts BMT 2.90 m (circular-arc waterplane too lean; real hull fuller/
      flatter-bottomed) — Lane 5 must use BMT KM/GM directly.
- [ ] Rebuild hull form from Plan 7 lines + Plan 2/3 offsets (the source Richard used to
      loft his model in AutoCAD). *(Numeric offsets not in text; parametric model is the
      working substitute.)*
- [x] **Resistance from towing tests (D1)** [x]: primary = Grekoussis & Loukakis 1985 NTUA
      NAL 06-F-1985; law 155V³+4.13V⁵ deduced from it and trial-validated; raw resistance
      points require physical archive access.

**W3 — Oar mechanics (the engine-to-propeller chain)**
- [x] **Speed→power chain implemented & verified** — `research/lane-4-oars/propulsion-models.md` +
      `lane4_propulsion.py`: W_hull = 155V³+4.13V⁵ (×1.08 Mark II), W = n·P·L·r·E/60, P = 7.43·r,
      E = 0.78. Reproduces Shaw's 8.32-kt sprint, Table 9.7 rates, ch.7 cruise rates, S6 62-W/man.
      **DONE (S10).** (This is the engine→propeller transfer; the per-stroke rigid-oar physics in
      the next items is the refinement layer on top.)
- [x] **Rig geometry from Plans 8 (midship section), 9 (stretcher), 15 (oars)**: three tiers
      (62/54/54, zygian oarports 1.0 m above water), thole-pin positions (thranite through both
      outrigger rails, thalmian inboard + large ports), lever ratios (thranite/zygian 2.817,
      thalmian 2.57–2.96), and the 800 mm design / ~720 mm achieved stroke — the beams at
      thalmian-head level are 10% closer than the 0.888 m interscalmium → 0.80 m gap = the
      design stroke; head-room caps real stroke → power losses. Sweep angles 48.1/48.4/55.6°
      (recomputed). See `research/lane-4-oars/rig-geometry.md`.
- [ ] Adopt the Baudouin & Hawkins / Caplan & Gardner / 2019 NJP rigid-oar framework (S2);
      fixed-seat constraint (max V̇O2 ≈ 65% of sliding-seat, S6) sets the force envelope.
- [ ] Oar inertia & blade data: 12.3 kg/oar full-size (model scales to 11.71 kg), blade
      geometry from Plan 15.
- [ ] Ergonomics: 50th-percentile US-marine body scaled to classical Greek male (~5'7")
      for reach/stroke limits (Richard's manikin method).

**W4 — Environment: Shaw's wave tables**
- [ ] Finish decoding all of Shaw's Tables (8.x): they give the sea state (H, L, C) for a
      given windspeed W, fetch, and duration — the environment that the hull+oar model
      must operate in, and the basis of his claimed trip performance.
- [ ] Verify asterisk rows = fully-developed sea (fetch/duration saturation), and use them
      as the asymptotic checks on any fetch-limited growth formula we adopt.

**W5 — Manoeuvring dynamics (re-implement Taylor ch.31)**
- [x] **Taylor's model re-implemented as a reference script** —
      `research/lane-5-manoeuvre/manoeuvre_model.py` + `manoeuvre-model.md`, from ch.31 text +
      OCR Table 31.1: m_app = 1.10·m, 3-band hull drag, thrust 17.4−0.967v kN, rudder lateral
      coeff 0.14+0.020Φ−0.00015Φ², rudder torque via lever (row 9), one-side-stops torque
      (row 10), yaw resistance Ωω², heel pendulum with GM−0.2 m. **Validated against §6 targets
      to ≤7% without fitting**: fast anastrophe 151.8 vs 145 m, tight 74.6 vs 80 m, Olympias
      64 vs 62 m, v 5.56/9.01/9.81 kt at 10/24/40 s (5.5/9.0/~9.9), braking 19 s/56 m
      (<20 s/<170 m), astern 9.38 vs 9.4 kt. Heel 4.0° vs stated 3.5° (over-predicts ~1°,
      flagged). Uses BMT KM/GM per S14 decision.
- [ ] If Taylor's Excel workbook is found (see Web searches), **extract the model from the
      sheet**: dump formulas, hard-coded coefficients, and initial conditions (openpyxl/xlrd),
      then transcribe into the reference implementation so the coefficients are taken verbatim
      rather than re-derived from the garbled PDF. *(Workbook not online — see S13 / taylor-excel.md.)*
- [x] Re-run against trial turns F1–F6, G1–G5 (D1) to confirm we reproduce his validation.
      **DONE — `research/lane-5-manoeuvre/fg-turns-rerun.md` + `fg_turns_rerun.py`.**
      Raw per-turn F/G data is print-only (Coates et al. 1990 tables F & G, *The Trireme Trials
      1988*, ISBN 0946897212 — not held / not online), so cell-by-cell fit check is not possible;
      instead the model was re-run over the scenario space ch.31 §3 describes and checked against
      every published anchor. All three diameter anchors reproduced to ≤7% (62→64, 145→152,
      80→75 m); scenario behaviour matches §3 (F1 smallest rudder → largest turn, etc.). Yaw-rate /
      360°-time (128 s observed vs 60 s steady-state) and drift (1.4° vs 7.8–15°) differ as
      documented caveats — both need time-domain/deceleration physics absent from Taylor's own
      steady-state Excel.**
- [x] Add Richard's alternative: rotation about centre of lateral resistance vs c.g.;
      quantify the difference (Taylor flags the UCL-model discrepancy here).
      **DONE — `research/lane-5-manoeuvre/clr-rotation.md` + `clr_rotation.py`.**
      Rotation about the CLR (0.5–2 m forward of c.g., the realistic band) changes turn
      diameters by ≤ ~5%; at x = 1.45 m the model reproduces both anastrophe targets to
      0.4%/0.1% (145.5 vs 145 m; 80.1 vs 80 m), better than the c.g.-axis baseline
      (+4.7%/−6.7%). Direction differs by turn type (rudder-dominated tighten; oar-stop
      turns widen). Supports Taylor's "close agreement" with the UCL CLR-axis model.**

**W6 — Validation & uncertainty**
- [x] **Validation table built** — `research/lane-6-validation/validation-table.md` +
      `validation_table.py`: maps every trial measurement to a model prediction. All
      steady-state speed targets reproduced within the ch.22 efficiency band (8.2–8.3 vs
      8.0–8.1 @ E 0.53–0.55; sprint 8.3 vs 8.2–8.3), all turn diameters ≤7% (152/75/64 vs
      145/80/62 m), braking 19 s/56 m, astern 9.4 kt, BMT volumes exact. Acceleration
      0→7 kt: trained-model 14 s vs 1988 trial 32 s (less-trained crew) — context row, not
      pass/fail.
- [x] Maintain an **uncertainties register**: every [?] number gets a flag, its source
      caveat, and its sensitivity in the model (e.g. GM −0.1 m Mark IIb change, hull weight
      debate, oar efficiency vs speed). **DONE (S13)** —
      `research/lane-6-validation/uncertainties-register.md` (25 items, A1–D5, each with
      [H]/[M]/[L] sensitivity). Row D6 added (S14): model KM under-predicts BMT 2.90 m;
      Lane 5 must use BMT KM/GM.
- [x] **Sensitivity pass** [x]: displacement ±2% → sprint ±0.5% (small; hull law
      trial-validated); GM 1.13→0.99→0.85 → heel 3.0→3.6→4.3° at fast anastrophe (diameter
      unchanged, yaw-driven); oar efficiency 40→54% → sustained 7.4→8.1 kt; crew count
      121→154 → 7.5→8.1 kt. **Dominant knobs: crew power/efficiency; second-order:
      displacement.** See `validation_table.py` sensitivity section.

### Parallelisable lanes (how work gets done)

Dependency logic:
- **W1 reading is the shared foundation** and can be split across readers with no conflict.
- **The three physics subsystems are pairwise independent** once their inputs are in hand:
  hull (W2) needs offsets/towing/BMT; oars (W3) needs Shaw rig data + oar searches;
  manoeuvring (W5) needs Taylor ch.31 + Excel + Kempf. None reads another's output.
- **Wave environment (W4)** is independent of hull/oars/manoeuvring — only needs the table
  decoding + Carter's equations.
- **Validation (W6)** is the converging lane: it only consumes numbers produced elsewhere
  (but its sea-trials search can start early).

```
              W1  READ + SOURCE (parallel: Shaw ∥ Taylor ch.31 ∥ trial reports)
              │
  ┌───────────┼───────────────┬────────────────┬─────────────┐
  ▼           ▼               ▼                ▼             ▼
 LANE2       LANE3           LANE4            LANE5        (LANE6 search starts)
 waves       hull+hydro      oars             manoeuvring
 (W4)        (W2)            (W3)             (W5)          ┐
  │           │               │                │            │
  └───────────┴───────┬───────┴────────────────┴────────────┘
                      ▼
               LANE6  VALIDATION + UNCERTAINTY REGISTER
```

**Lane 1 — Read & record (W1)** · parallel-safe, assign to N readers
- Shaw ch 7–9 read ‖ Taylor ch.31 read ‖ Rankov trial-report chapters read ‖ bibliography
  reconciliation. Each produces a write-up appended to the log; no inter-lane dependency.

**Lane 2 — Wave tables (W4 + current-session TODOs)** · serial within the lane
- H/L/C sub-header decode (TT293) → Table 8.3 CSV → C = √(1.56·L) integrity check →
  remaining Shaw tables → Carter's-equations search (external, runs while decoding).
- Critical path for W4; nothing else waits on it.

**Lane 3 — Hull & hydrostatics (W2)** · parallel with Lanes 4 & 5
- Searches (offsets ‖ BMT ‖ displacement ‖ Eliav & Helfman ‖ towing resistance) can all run
  concurrently; hull rebuild begins once offsets + resistance numbers land.

**Lane 4 — Oar mechanics (W3)** · parallel with Lanes 3 & 5
- Searches (oar data ‖ rowing-propulsion models) ‖ ergonomics data collection; rig model
  builds once the Shaw rig read (Lane 1) is available.

**Lane 5 — Manoeuvring (W5)** · parallel with Lanes 3 & 4
- Taylor Excel workbook search ‖ Kempf source ‖ ch.31 read (Lane 1); then workbook
  extraction → reference implementation → trial-turn re-run.

**Lane 6 — Validation (W6)** · converges last
- Sea-trials second-pass search (W6) runs early; the validation table + uncertainties
  register fill in as Lanes 2–5 produce numbers.

Execution model:
- Each lane is a self-contained unit suitable for a sub-agent; Lanes 2–5 are pairwise
  independent and run concurrently; Lane 6 aggregates.
- Concurrency note: the `tools/` extraction scripts are stateless per invocation, so
  Lanes 3–5's searches/reads don't contend with Lane 2's decode; only Lane 2 is inherently
  serial (each table needs its own cmap/glyph pass). Web searches are trivially parallel.

#### Where lane results are written (output protocol)

**Canonical file is single-writer.** `trireme-rowing-simulation-research.md` is edited *only by
the orchestrator* when merging a lane's completed work — never by sub-agents directly (avoids
concurrent-write conflicts and lost updates). Sub-agents therefore produce **lane notes + raw
artifacts**, and return a **structured summary** as their final message.

Directory layout (persistent, inside this repo):
```
~/projects/sandbox/trireme/
├── research/
│   ├── lane-1-read/          # Lane 1 prose notes (one .md per reader)
│   ├── lane-2-waves/         # Lane 2 notes + decoded-table artifacts
│   ├── lane-3-hull/          # Lane 3 notes + resistance/offsets data
│   ├── lane-4-oars/          # Lane 4 notes
│   ├── lane-5-manoeuvre/     # Lane 5 notes + extracted workbook/csv
│   ├── lane-6-validation/    # Lane 6 validation table + uncertainties register
│   └── data/                 # shared machine-readable artifacts (CSV, xlsx, decoded fonts)
├── sources/                  # primary-source PDFs + text dumps
├── tools/                    # decode/OCR scripts + fonts + renders
└── wayback/                  # MSW thread-21958 recovery tooling
```
Raw data artifacts (Table 8.3 CSV, extracted workbook, towing-resistance tables) go in
`research/data/` so multiple lanes can cite the same files.

Per-lane rules:
- Each sub-agent writes only inside its own lane directory; lane directories are disjoint, so
  N lanes can write in parallel with zero file contention.
- Prose notes are markdown; artifacts are CSV/JSON wherever possible (machine-checkable).
- Every note must carry **provenance**: source (URL / book / page / chapter / table), exact
  numbers with units, a [x]/[?] confidence flag, and open questions — matching the log style.
- The sub-agent's **final message** is the merge payload: a concise summary of findings +
  source list + confidence flags. The orchestrator folds it into the main .md as a new log
  section (S7, S8, …) and ticks the corresponding W/lane boxes.

In this session, artifacts were produced in `/tmp/opencode` (fonts, scripts,
page renders) and are now promoted into `sources/`, `tools/`, and `wayback/`; the venvs
stay in `/tmp/opencode`. Only *finished* deliverables (the decoded CSV, notes) belong in
`research/`.

### Web searches still to run

Open-source gaps that need lookup online (each tagged with the data source / workstream it feeds).
Parallel mapping: **Lane 3** = the W2 hull searches (towing, BMT, offsets, displacement, Eliav &
Helfman); **Lane 4** = the W3 oar searches (oar data, propulsion models); **Lane 5** = the W5
searches (Taylor Excel, Kempf); **Lane 2** = Carter's equations; **Lane 6** = sea-trials 2nd pass.
All searches are independent of each other and of the decode work.

- [x] **Carter's wave-growth equations** (W4/D6): **DONE (S7)** — identified as **D. J. T. Carter
      1982, "Prediction of wave height and period for a constant wind velocity using the JONSWAP
      results", *Ocean Eng.* 9(1), 17–33 (DOI 10.1016/0029-8018(82)90042-7)**; full reproduction in
      `research/lane-2-waves/carter-equations.md`. Table 8.3's 36 cells all reproduce.
- [ ] **Towing-tank resistance data** (W2/D1): Coates et al. 1988/1990 resistance-vs-speed
      curves and the parametric drag equations (Taylor's model cites p.54 of the 1990 report;
      values are garbled in our PDF) — search for the raw table or tank-test numbers.
      **Update (S12): confirmed a 1:10 hull model was tank-tested in Athens (NTUA ship tank,
      1985) as part of the design process (UChicago Animus retrospective); the tank-test numbers
      themselves remain to be pulled from Coates 1990 ch. — see S12.**
      **Update (S13): tank test identified by primary source = Grekoussis, C. & Loukakis, T.
      (1985) "Athenian Trireme Calm Water Tests Without Ram", NTUA Report No. NAL 06-F-1985
      (bibliography, ch.7 p.79: Shaw's W = 155V³+4.13V⁵ hull-power law was deduced from these
      bare-hull model tests; graph reproduced by Lowry & Squire 1988; resistance/speed curves
      published in Shaw 1993, The Trireme Project). Report not online (NTUA library/hardcopy);
      raw resistance points remain the one unrecovered element — the law itself is validated by
      trial speeds (8.32 vs 8.2–8.3 kt). See S13 + uncertainties register B2.**
- [ ] **Timothy Taylor's Excel dynamics model** (W5/D4): locate the actual spreadsheet behind
      ch.31 — check tDAR record 424186 for supplementary files, Trireme Trust archive, and
      ancientportsantiques.com (source of our PDF); if found, extract the workbook (see W5).
      **Update (S11): chapter identified = Andrew Taylor, ch.31, book pp.231–244 [x]; the Excel
      workbook itself not yet located online — Trireme Trust archive remains the best lead.**
- [x] **BMT 1991 inclining experiment / stability report** (W2/D7): "Report of inclining
      experiment and stability analysis of HM Olympias" — **CONFIRMED exists in the Trireme Trust
      archive (triremetrust.org.uk)**; also referenced in Rankov 2012 ch.25 as BMT (Defence
      Services) Ltd **report TR01/R1952, July 1990** — its headline numbers (light ship 25.798 t,
      VCG 1.575 m above USK, LCG 17.521 m from Station 23; GM 1.13 m at 42.25 t) are in the ch.25
      text (see S11). Only remaining need: archivist request for the full report.
- [ ] **Hull offsets & lines (Coates Plan 2 / Plan 7)** (W2/D8): whether the table of offsets
      is online (Trireme Trust archive, tDAR) vs must be requested from the archivist.
- [ ] **Olympias displacement / weight breakdown** (W1/D9): fill the S1 gap "displacement
      light ~ ? (need value)". **Update (S11): ch.25 gives light ship = 25.798 t (BMT inclining
      report) and trial condition = 42.25 t (crew 80 kg each); cross-check empty vs full-load
      figures still open but the primary anchors are now in hand.**
      **Update (S12): reconciled across sources — light 25.8 t (BMT/ch.25), trial-with-crew
      42.25 t (ch.25), "fully laden" 47 t (poster/Wikipedia, incl. rigging+oars+benches+stores),
      Osprey 42 t. See S12.**
- [x] **Olympias sea-trials data — second pass** (W6/D10): S1 [x] covers speeds/turns/
      endurance from aggregators. **DONE via primary source (Rankov 2012 ch.1.2, read in W1
      pass): GPS-calibrated speed data, Table 1.2.1 (spm→knots), 8.3 kt sustained / 8.9 kt peak
      suspect, 1992 crew ~154 (low 121), trials-day log. See S11.** The Coates/Platis/Shaw 1990
      volume (ISBN 0-946897-21-2, *The Trireme Trials 1988*) is confirmed to exist [x] as the
      remaining secondary source for the resistance/tank data (W2/D1).
- [x] **Kempf manoeuvre** (W5): source definition for the rudder-drag-increment method Taylor
      borrows (extra drag 1.4× at 67.5°, 0.6× at 45°, 0.2× at 22.5°) so we can cite a primary reference.
      **DONE (S12): "Kempf manoeuvre" = the standard zig-zag (Z-) manoeuvre trial (Kempf 1944,
      "Maneuvering Standards for Ships", *Hansa* 27/28; developed at HSVA 1930s with Krämer;
      Nomoto 1960 analysis). The 1.4/0.6/0.2 rudder-drag factors are Taylor's own calibration
      values, NOT a published "Kempf rudder-drag method" — they cannot be sourced externally;
      the model's turn-drag calibration (39.4v² Olympias straight-rudder) is already verified
      against ch.31 Table 31.1. See lane-5 §3.**
- [x] **Eliav & Helfman (2022)** (W2): pull full quantitative claims (empty hull ~25 t, MT vs
      laced joints, resistance penalty) for the uncertainty register.
      **DONE (S12): full PDF verified; empty 25 t (M&R 2000 p.210; earlier 21 t Coates 1990,
      23 t Coates 1999); laced hull −46% (FEA hogging, reserve 2.7); NO quantified resistance
      penalty (qualitative only); hypozomata 4×117 kg. See lane-3 §2.**
- [x] **Trireme-specific oar data** (W3): blade dimensions/mass and any force measurements from
      the trials (Richard's build log gives 12.3 kg/oar, 800 mm design stroke) — look for the
      source of the 12.3 kg figure and the oar balance point / blade area.
      **DONE (S12): oar lengths 9 cubits (3.99 m) & 9½ cubits (4.2 m, 0.444 m cubit; Osprey, from
      Zea/iconographic evidence) — cross-checked vs Shaw Tables 9.1/9.2 (2.817/2.80 m) [x];
      1987 oars were too light and were redesigned for 1990 (UChicago Animus) — the 12.3 kg/oar
      figure itself remains uncorroborated, flag for uncertainty register. Per-tier lever detail
      is in S9/S10.**
- [ ] **Rowing propulsion models & simulation papers** (W3/D9): oared-warship propulsion
      simulations built on Coates/Morrison design data — oar lengths and inboard/outboard lever
      ratios per tier, interscalmium, blade areas, stroke limits. Extends S2 (sport-rowing models)
      to trireme-specific dynamics; also pin down the design data in Morrisson & Coates (2000)
      and cross-check against Shaw's rig figures (Mark IIb: interscalmium 0.98 m, 18.4° skew).
      **Note (S10): the macro speed↔power chain is now implemented & verified
      (`lane-4-oars/propulsion-models.md`); this search now targets the *per-stroke* rigid-oar
      refinement (blade-force/angle detail) rather than the bulk transfer.**
      **Update (S12): external confirmation of the Mark II design targets — 18.4° cant → 9.7 kt
      short sprint, 7.5 kt sustained cruise (Trireme Trust "Lessons from Olympias" summary,
      ttrankov2.html). Matches S9/S10 IIb targets.**

### Active TODOs (current session — decoding Rankov 2012 tables)

- [x] Decode the H/L/C sub-header glyphs (TT293 font, uniF001/003/004) — interrupted; cmap
      lookup failed, retry via glyph art matching. **DONE — resolved via OCR route, not glyph
      matching** (see `research/tasks/pdf-ocr-table-decoding.md`).
- [x] Fix the "m7s" artifact → confirm TT292 glyph F016 is the `/` (slash) not `7`. **Moot —
      tables decoded via OCR, not the numeric glyph font.**
- [x] Produce a clean CSV of Table 8.3 (fetch × duration × {4.5, 5.0, 5.5 m/s} → H, L, C)
      and verify C = √(1.56·L) across all 36 cells. **DONE — `research/data/shaw-table-8.3-*.csv`;
      all 36 cells reproduce Carter's duration-limited equations (T_z convention, fully-developed
      caps). See S7.**
- [x] Locate and decode the remaining Shaw tables on pp.72–73 (durations, other windspeeds).
      **DONE — Table 8.4 (3-hour waves) decoded; also Tables 8.1/8.2 wind-propulsion (S7).**
      Tables 8.1/8.2 exact cells now recovered & verified cell-by-cell against the prose equations
      (`research/data/shaw-table-8.1-sail-force.csv`, `shaw-table-8.2-apparent-wind.csv`,
      note `research/lane-2-waves/shaw-tables-81-82-wind-propulsion.md`).**
- [x] Capture the paper's worked example (8.5 m/s wind → H≈1.4 m, L≈28 m at 200 km/12.6 h)
      as a reference check against the decoded table. **DONE — text captured in S7 and
      `carter-equations.md` §10.**

---

## Log of searches / findings

### S1 — Olympias sea trials data [x]
Search: "trireme Olympias sea trials data speed knots turning circle power"

Key sources and numbers:
- **Trireme Olympias: The Final Report. Sea Trials 1992-4, Conference Papers 1998** (ed. Boris Rankov, Oxbow 2012). ISBN 978-1-84217-434-0. tDAR id 424186. Contains papers highly relevant to a simulation:
  - "Human Mechanical Power Sustainable in Rowing a Ship for Long Periods of Time" (human-engine power data)
  - "Paleo-bioenergetics: clues to the maximum sustainable speed of a trireme under oar"
  - "Triereis Under Oar and Sail"
  - Papers by Timothy Shaw and John Coates on adjusting hull and oar-system to match implied ancient performance (basis of 2nd ed. The Athenian Trireme, 2000)
  - "modelling of battle manoeuvres based on the data produced by the trials of Olympias" ← most directly relevant
- **The Trireme Trust — Olympias Sea Trials** pages hosted by Anu Dudhia: https://eodg.atm.ox.ac.uk/user/dudhia/rowing/trireme/tttrials.html
- Sea trial performance data (from grokipedia / museumships / Wikipedia aggregations):
  - 1987 (Poros): max sprint 9 kts sustained ~1 min, 170 rowers @ 45 spm, measured by shore geodimeters; also 180° turn in ~1 min within 2.5 ship-lengths
  - 1988: 0→7 kts in 32 s (acceleration); one reported top 9.6 kts; turning radius ~60 m at half speed ≈ 1.5 ship-lengths
  - 1990 (Faliron Bay): avg 8.5 kts over 2 km; peak 8.9 kts; ramming runs up to 10 kts
  - 1992: 7–7.5 kts bursts @ 25–30 spm; sail-assisted ~5 kts
  - Turning: 180° in 60–63 s at full/moderate speed; diameter 62–120 m depending on conditions; 360° in ~128 s; bilge water adds ~8% to turning time
  - Endurance: 4 kts ~30 min (170 rowers, calm); 5–7 kts for 1–4 h with rests
- Olympias particulars: 37 m LOA, ~5 m beam (incl. outriggers), Douglas fir hull, bronze ram 200 kg, keel iroko, displacement light ~ ? (need value), 170 oarsmen (62 thranite + 54 zygian + 54 thalmian).

### S2 — Oar dynamics / rowing biomechanics equations [x]
Search: "rowing oar dynamics mathematical model equations blade force lever ratio"

Key papers (rowing = best-studied analogue for oar propulsion):
- **Baudouin & Hawkins (2002)** "A biomechanical review of factors affecting rowing performance", Br J Sports Med 36:396-402. Oar as 2nd-class lever; forces Fh (handle), Fb (blade), Fo (oarlock); inboard/outboard lever ratio governs gear. PDF: http://bionics.seas.ucla.edu/education/Rowing/Math_Model_2002_01.pdf
- **Cabrera, Ruina & Kleshnev (2006)** "A simple 1+ dimensional model of rowing mimics observed forces and motions", Human Movement Science 25:192-220. The standard 1D framework (used by many later works) for hull + oar dynamics.
- **Caplan & Gardner (2007a)** "A mathematical model of the oar blade-water interaction in rowing", J Sports Sci 25:1025-1034. Models blade lift+drag forces during drive; blade as hydrofoil.
- **Caplan & Gardner (2007b)** "A fluid dynamic investigation of the Big Blade and Macon oar blade designs", J Sports Sci 25:643-650. Measured C_L, C_D curves.
- **Coppel, Gardner, Caplan & Hargreaves (2009)** "Oar blade force coefficients and a mathematical model of rowing" (ISBS). Shows CFD-derived lift/drag coefficients predict boat speed within 1.33% vs experimental → validates using CFD coefficients.
- **Physics of rowing oars (2019)**, New Journal of Physics 21 (IOP). Rigid-oar dynamics, kinematics of blade/hull, α = L/ℓ (outboard/inboard ratio), pressure-drag vs added-mass regimes; characteristic scales V*, τ*; hull drag C_h, blade C_d, C_m. URL: https://iopscience.iop.org/article/10.1088/1367-2630/ab4226
- **6DOF rowing-boat model** (Formaggia / MOX-Politecnico di Milano 2009) — surge/heave/sway/pitch/roll/yaw with lever oar model, drag formulas, VOF/NS coupling. PDF: https://www.mate.polimi.it/biblioteca/add/qmox/19-2009.pdf
- Other classic models cited: Pope 1973; Sanderson & Martindale 1986; Millward 1987; Brearley & de Mestre 1996; Lazauskas 1997; Brearley, de Mestre & Watson 1998; Wellicome 1967 (hull resistance experiments on racing shells).
- Dudhia, "The physics of rowing" — https://www.atm.ox.ac.uk/rowing/physics (also hosts Trireme Trust trials page).

### S3 — Trireme dynamics model: Taylor, "Battle Manoeuvres for Fast Triremes" (Rankov 2012 ch.31) [x]
Search: "trireme Olympias maneuvering model simulation" → found chapter in **Trireme Olympias: The Final Report** (Oxbow 2012); full PDF obtained from https://www.ancientportsantiques.com/wp-content/uploads/Documents/AUTHORS/Rankov2012-TriremeOlympia.pdf (extracted text in sources/rankov2012.txt).

**This is the single most relevant existing model** — a published, Excel-based dynamics simulation of Olympias + a hypothetical "fast Mark IIb trireme", validated against six trial turns. Key contents:

Model architecture (built in Excel):
- **Linear forward motion**: apparent mass = 10% above displacement; drag from towing tests in Coates et al. 1990 p.54 (parametric equations, 3 speed bands); extra linear drag increment of 1.4× straight-rudder drag at 67.5° rudder, 0.6× at 45°, 0.2× at 22.5° (Kempf manoeuvre). Increased drag during turns from drift angle; resistance acts at angle of half the drift angle from perpendicular.
- **Rudder lateral force**: turning force = fraction of rudder's along-track drag; fraction from polynomial fit of rudder angle Φ (degrees): **Coefficient = 0.14 + 0.020Φ − 0.00015Φ²**. Rudder torque via distance from rudder to centre of mass.
- **Oar turning moment**: one side stops rowing; lever arm from centreline to halfway between outer oar tips and inner edge of thalmian blades.
- **Yaw resistance**: **Resisting torque = Ωω²** where Ω is an order-of-magnitude-scale constant ≈ moment of inertia; differs from UCL model (rotation about centre of lateral resistance vs. about vertical axis through centre of mass).
- **Heel**: max heel 3° (design constraint, oars can't work beyond it); heel from balancing rudder/lateral tipping moments vs. ship-as-pendulum with length = metacentric height; c.g. above keel measured; effective height 0.2 m lower for GM (crew lean).
- Water density 1025 kg/m³.
- **Validated against** Lowry & Squire (1988), Coates et al. (1990, 20–31, 69–89), Shaw (1993, 45–7); turns F1–F6, G1–G5 from Coates et al. tables F and G (pp. 87–88).
- Comparison with a **UCL (University College London, Mechanical Engineering) model** (Simon Rusling, Tristan Smith, pers. comm. 2006) gave close agreement — both fit the same sea-trial data.

Key quantitative results:
- **Efficiency**: Olympias consistently ~40% (range 39–43%) conversion of rower power (fixed-seat ergometer) to propulsive power (Taylor ch. on heel: 43%; Shaw: 39%).
- Power: Shaw (1990) projected 200 W/rower effective (thranite+zygian) for 6-min maximal effort → 23 kW / 116 rowers; Mark IIb at 60% efficiency → 300 W/rower, 51 kW / 170; model uses 40 kW sustained a few minutes.
- Mark IIb max speed: **9.9 knots** with effective oar thrust **7.8 kN** at that speed (drag–thrust intersection).
- Oar thrust vs speed (from Olympias acceleration runs, Shaw 1990): **Thrust (kN) = 17.4 − 0.967 × speed (knots)** — linear.
- Acceleration (Mark IIb): 0→5.5 kts in 10 s, 9 kts at 24 s, full speed ~40 s.
- Backwards rowing: 80% of forward thrust; reaches 9.4 kts stern-first.
- Turning: at 10 kts with max heel 3°, tightest turn ≈ 140 m diameter; "fast turn" (9.5 kts, 22.5° rudder) ≈ 145 m diameter; "tight turn" (one side stops, full rudder) ≈ 80 m at 6.5 kts; tightest recorded Olympias turn = 62 m diameter (halves speed, "slow/tight anastrophe"); fast turns 107–120 m diameter.
- Tactical outcomes: safe approach to isolated ship ≈ 160 m; to a rank ≈ 250 m (fast anastrophe); diekplous gap ≥ 150 m (130 m aggressive); 60 m cross-range immunity; files spaced 100 m.
- Mark IIb: +3 m length, displacement 44 t (+2 t), GM −0.1 m; wave-making resistance peaks at Froude-based speeds 6.5, 8.2, 10.6 knots; wetted surface drag ∝ length.
- Model parameters tabulated in Table 31.1 (garbled in PDF text extraction — need OCR or better source for exact drag coefficients).

Sources cited by the model (core validation datasets):
- Coates, Platis & Shaw (1990) *The Trireme Trials 1988*, Oxford: Oxbow.
- Lowry & Squire (1989) *Trireme Olympias: Extended Sea Trials Poros, 1988*, Cardiff.
- Shaw (ed.) (1993) *The Trireme Project*, Oxford: Oxbow.

### S4 — Hull resistance math for triremes [x]
- **Princeton HPT page** (https://swh.princeton.edu/~maelabs/hpt/his/hpt_10.htm): resistance = skin-friction drag (∝ V²) + wave-making; trireme "hull speed" condition; 7 kt cruise dominated by friction. Graphs from Coates, "The Trireme Sails Again," *Scientific American*, April 1989. (Graphs are GIFs; numbers not text.)
- **Eliav & Helfman (2022)** *International Journal of Nautical Archaeology* (PDF at ancientportsantiques.com): argues Olympias hull too heavy (empty ~25 t) → high resistance → poor speed under oar; MT (mortise-tenon) joints vs laced/light hulls; interscalmium and oar-system limits (Coates 2012a; Shaw 2000 pp.76-77). References: Cannon et al. (2019) "Development of a quantitative method for the assessment of historic ship performance" (Springer) — a useful modern method reference.
- Rankov ch.31 (S3) notes wave-making resistance is a minor component for Olympias; frictional dominant.

### S5 — Human power (the "engine"): Coates ch.22 "Human Mechanical Power Sustainable in Rowing a Ship" (Rankov 2012 pp.161-164) [x]
Read in full from sources/rankov2012.txt (p.161-164). This is the input-side physiology model.

Sustainable mechanical power for "an ordinary man" (Burlet et al. 1986, from Scherrer's Précis de Physiologie du Travail):
- 140 W for 10 h; 170 W for 4 h; 200 W for 1 h.
Monod's figures for "well trained athletes and extreme performances" (max possible durations, thermal eff. 20% assumed): 700 W for 10 h; 850 W for 4 h; 1000 W for 1 h.
Monod's tolerability guidance: >50% of aerobic power cannot be developed habitually; daily output ≤ 8400 kJ/day for professional work → 90 W gross sustained over 8 h; limit time gross power exceeds 280 W.

Thermal efficiency vs mechanical power (Galletti 1959, cyclists): 40 W→25%; 80 W→24%; 120 W→23.3%; 160 W→22.8%; 200 W→22.4%. (Daedalus Project measured 18–33.7% in volunteers.)

Max aerobic oxygen absorption: ~4.5 l O2/min fit young men; 3 l ordinary young men; 2 l women; ~¾ by age 60.

Speed ∝ (effective power)^(1/3) — Coates states ship speed "closely proportional to the cube root of the effective power" (resistance ∝ V³). So P ∝ V³, V ∝ P^(1/3).

Key worked example (Thucydides' Athens→Mytilene passage):
- ~6.2 knots for just under 30 h, under oars; effective propulsive power required by Olympias at 6.2 kts = **6.2 kW** (one rudder half-immersed, clean bottom, calm).
- With ⅔ of crew rowing in turns: 55 W effective/man, or 110 W mechanical/man at 50% propulsive efficiency; +20% for waves → **132 W/man mechanical**.
- Crew at 4 h row / 2 h rest regime: 69% of max aerobic output sustained for 4 h. MAO 3.1 l O2/min ≈ 250 W mechanical → 172 W sustained, margin of 40 W/man.
- Heat effects reduce power (up to 34% at 35°C; ~17% averaged over night/day).
- Untrained crew with MAO 3.1: only 29% of 250 W = 72 W → enough only for 5.1 kts; with MAO 4 l/min untrained → 96 W → 5.6 kts.
- Conclusion: trained crew (MAO 3.1) could sustain 6.2 kts; training is the critical factor.
- Mark IIb with a modern scratch crew (young fit untrained, MAO 3.1, ⅔ rowing): could maintain ~5.1 kts for 4 h.
- Olympias max sprint ~8.5 kts vs hoped-for 9.7 kts → 12% speed / ~33% power shortfall, attributed largely to the oar rig.
- Xenophon's Byzantium→Heraclea 129 nm "long day" under oar: feasible in ~20 h continuous under these assumptions.

### S6 — Paleo-bioenergetics (Rossiter & Whipp, Rankov ch.23 pp.165-168) [x]
Read in full from sources/rankov2012.txt. Upper bound on sustainable power per oarsman.

Key assumptions & values:
- Literary target: ~7 knots for ~18 h (Thucydides 3.49; 8.101; Xenophon Anabasis 6.4.2).
- Anaerobic (lactate) threshold for "standard" man ≈ 50% V̇O2max; elite endurance athletes up to 80%+.
- Modern sliding-seat junior-international oarsmen: lactate threshold ~30–35 ml O2/min/kg.
- Ancient Athenian stature assumed: 168 cm, 67 kg → lactate threshold ~2.0–2.3 l/min V̇O2.
- Of that: ~300 ml/min basal metabolism; ~400 ml/min "internal" power (moving body against gravity, body-swing). Remainder available for external power.
- O2 cost of modern sliding-seat rowing: ~14 ml O2/min per W output. → available sustained external power ~95–115 W (from 1.3–1.6 l/min).
- **Fixed-seat rowing limitation**: max V̇O2 during fixed-seat rowing only ~65% of sliding-seat; but lower O2 cost ~10–12 ml O2/min per W. Result: plausible sustainable external power only **~80 W/man at best**.
- To avoid glycogen depletion over ~18 h continuous row (400 g muscle + 50 g liver glycogen), average RER must stay ~≤0.74 (mostly fat). Work must stay below lactate threshold AND at low carbohydrate utilisation.
- Louis XIV galleys anecdote (Casson): 5 kts first hour → 4.5 kts second → 2 kts or slower after — attributed to acidosis + glycogen depletion.
- Sweat in Olympias rowers: 3–4 litres/day; mid-day ambient up to 35°C.
- Conclusion: max ~80 W/man external power sustainable; training critical.

Cross-check numbers for the simulation:
- Olympias at ~7.2 knots needed ~115 W/man total, of which only **62 W was propulsive**; **53 W lost in oar slippage and non-propulsive oar movement** (Shaw 1993) → propulsive efficiency of the oar system ≈ 62/115 ≈ 54% (at 7.2 kts). This matches the "~40% power to water at 8.5+ kts" theme — efficiency degrades as speed rises.
- Fixed-seat lab experiments: stroke 73 cm, 36 spm mimics Olympias; stroke 99 cm "free rating" 28 spm → O2-cost essentially unchanged (so Mk II longer-stroke gains are mechanical, not physiological).
- Mark IIb improvements (canted rig, longer stroke) target the 53 W/man losses.

### S7 — Shaw ch.8 wave tables decoded & verified (book pp.71–73 / PDF 83–85) [x]
Decoded via OCR route (see `research/tasks/pdf-ocr-table-decoding.md`); all values independently
reconstructed from Carter 1982 and cross-checked cell-by-cell. Artifacts:
`research/data/shaw-table-8.3-significant-waves.csv`, `research/data/shaw-table-8.4-three-hour-waves.csv`.
Full derivation and verification in `research/lane-2-waves/carter-equations.md` §10.

**Table 8.3 (p.72): significant wave height H, mean wavelength L, mean wave velocity C** — for
fetch ∈ {50, 100, 150, 200} km × duration ∈ {3.2, 6.3, 9.5, 12.6} h × W ∈ {4.5, 5.0, 5.5} m/s:
- Generating equations (duration-limited branch — always applies for these inputs; confirmed
  D < 1.167·X^0.7·W^−0.4): H = 0.0146·D^(5/7)·W^(9/7); T_z = 0.419·D^(3/7)·W^(4/7); L = 1.56·T_z²;
  C = 1.56·T_z. Fully-developed cap (asterisked cells): H = 0.0240·W², T_z = 0.566·W.
- **RESOLVED: Shaw used Carter's T_z (zero-up-crossing) period**, not T_m — L/C in the table match
  T_z exactly (T_m would inflate L by ×1.66, C by ×1.29, which the table does not show).
- All 36 cells match to printed precision. Example: (50, 3.2, 4.5) → 0.23, 4.1, 2.5;
  (200, 12.6, 5.5) → 0.73, 15.1, 4.9 (capped); range H 0.23–0.73 m, L 4.1–15.1 m, C 2.5–4.9 m/s.
- Caption details: asterisk = full development at given windspeed/duration/fetch; C measured relative
  to water moving at 0.5 m/s (1 knot); wave with C > 3.9 m/s (7.5 knots) overtakes the ship.
- W is wind **relative to the water** = true wind − 0.5 m/s favourable current (Shaw's assumed
  0.5 m/s (1 knot) current). True-wind equivalents: 5.0, 5.5, 6.0 m/s.

**Table 8.4 (p.73): "3 hour" heights** = Table 8.3 × {1.8 (H), 1.2 (L), 1.1 (C)} (Shaw: "for these
factors I am indebted to Carter"; ratios verified 1.78–1.83 / 1.21–1.22 / 1.07–1.12 across all 36
cells). Range H 0.42–1.31 m, L 5.0–18.3 m, C 2.8–5.3 m/s.

**Worked examples from the text (p.72–73):**
- 8.5 m/s (16.5 kt) wind relative to water at 200 km / 12.6 h → significant H ≈ 1.4 m, λ ≈ 28 m
  (proportional to Table 8.3 entries; the sail-propulsion-speed case: 8.5 m/s drives ship at
  3.9 m/s (7.5 kt) under sail alone).
- Same conditions, 3-hour height ≈ 2.5 m, λ ≈ 34 m (Table 8.4). Shaw: such a wave (λ ≈ waterline
  length ≈ 33 m, single-crest support) "would severely strain the ship"; significant-height waves
  would make rowing impossible; at 5.5 m/s waves reach ~1.3 m but λ ≈ 18 m keeps the hull on ≥2
  crests (survives, but rowing impossible).

**Tables 8.1/8.2 (p.71): wind propulsion** — sail force relative to true tailwind and required
oar-force balance; the formula for percentage of oar power provided by sail:
X = 100[(V − 3.9 − 0.5)/4.6]² (V = true windspeed, m/s). At 5 m/s true wind the relative wind is only
0.6 m/s → ~2% reduction in oarsmen's burden; ≥6 m/s gives 12%, ≥6.5 m/s 32%. Table 8.2 maps
true-windspeed to apparent-wind angle for course-offset manoeuvres (e.g. sailing up to 67° off the
apparent wind at ≤7° leeway needs >10 m/s true wind if wind at 90° to course, at ship speed 4.4 m/s).
Heel caution: 14 kt (7.2 m/s) steady beam wind heels Olympias ~8° (both sails) / 7° (without boat
sail) — putting thalmian oarports near the water (Morrison & Coates 1986, 223).

**Method note:** the decode scripts (glyph matching via DejaVu EDT) handle prose but *not* the numeric
table glyphs — OCR of 8x page crops is the reliable route for tables. Both recipes are written up in
`research/tasks/` (playbooks) for reuse.

### S8 — Taylor ch.31 "Battle Manoeuvres for Fast Triremes" read in full (book pp.231–243) [x]
Full read from rankov2012.txt (the chapter is book pp.231–243, *not* 268–77 as an earlier plan note
said). Detail logged in `lane-5-manoeuvre/taylor-excel.md` §5. Key additions beyond S3:

- **Model fitting details**: turns fitted = Coates et al. (1990, 87–88) tables F/G → F1–F6
  (Hellenic Navy crew, varied rudder angles, some thranites-only) and G1–G5 (Trust crew, flat
  thrust 4–7 kts). Entry speeds adjusted in model (G2/F2 low, F5/F6 low). Drift angle: G1/G2
  stated 15°±2° but time-delay method gives 3 s × 2.6 °/s = 7.8° — Taylor uses the lower value.
- **Heel model (§2.3)**: heel from balancing rudder + lateral-resistance tipping moments vs
  ship-as-pendulum of length = metacentric height; c.g. height above USK for lateral response;
  **0.2 m lower effective height for GM** (crew lean). Heel ≤ 3° (oar-rig constraint).
- **Mark IIb (§5)**: +3 m length, +2 t (→44 t), mast/yard/sail landed pre-battle, GM −0.1 m,
  draft same, beam slightly wider (still fits ship sheds), frictional drag ∝ length; wave-making
  peaks at 6.5/8.2/10.6 kts (Froude); optimised rudder drag = ¼ of Olympias straight-rudder value;
  applied-rudder drag factor 0.6–3.25× straight.
- **Oar thrust/power (§5.2)**: model assumes 40 kW effective sustained for minutes (all manoeuvres
  <2 min); max speed 9.9 kts at 7.8 kN; Thrust (kN) = 17.4 − 0.967 × speed (knots) [Shaw 1990, 25];
  Shaw's 200 W/rower (thranite+zygian, 23 kW/116) vs Mark IIb 60% rig → 300 W/rower (51 kW/170).
- **Manoeuvrability (§6)**: accel 0→5.5 kts/10 s, 9 kts/24 s, full ~40 s; backwards rowing 80%
  thrust → 9.4 kts stern-first; braking from 9.9 kts to stop in <20 s over ~170 m; tightest turn
  (10 kts, heel ≤3°) 140 m; fast anastrophe 145 m @ 9.5 kts; tight anastrophe 80 m @ 6.5 kts;
  Olympias tightest 62 m.
- **Tactical (§7)**: safe approach 160 m isolated / 250 m rank; diekplous gap ≥150 m (130 m
  aggressive); 60 m cross-front immunity; files at 100 m spacing; close to single rank ≤70 s.
- **UCL comparison**: Rusling & Smith (pers. com. 2006) close agreement (both fit same trial data).

### S9 — Shaw ch.7 + ch.9 read in full; oar-power model decoded & verified [x]
Full read of the two core oar-propulsion papers (book pp.67–75 and 76–81). Detail in
`research/lane-1-read/shaw-ch7-ch9-2024.md`; tables OCR'd and verified.

- **Ch.7 (Byzantium→Heraclea)**: Xenophon *Anab.* 6.4.2 "long day under oar" = 129 n.m. at
  sustained 7–8 kts under oar alone; sail ruled out (seas too great). Cruise rates: 25.5 spm
  @ 7 kt (115 W/man), 28.8 @ 7.5 kt (145 W), 32.3 @ 8 kt (180 W).
- **Ch.9 equations (all verified)**:
  - Hull power W = 155V³ + 4.13V⁵ (Olympias; ×1.08 Mark II).
  - Oar power W = n·P·L·r·E/60; mean pull **P = 7.43·r** N; E = 1/(1+q/p), Mark II E = 0.780.
  - Validation: 44.5 spm, ~130 rowers, E=0.730 → 18,152 W → 8.32 kts vs measured 8.2–8.3 kts.
- **Tables 9.1/9.2/9.6/9.7 decoded & verified** (OCR; L=0.87/0.99 m, r up to 49.4 spm, P up to
  367 N, pull durations 0.392–0.612 s). Artifacts: `research/data/t91_t92_ocr.txt`,
  `t96_ocr.txt`, `t97_ocr.txt`.
- **Design**: Mark IIb (canted rig 18.4°, tan=1/3) → 1.10 m chord at 0.98 m interscalmium, the
  preferred design (lower rates, lighter pulls, more normal rhythm than IIa).
- **Implication for sim**: the 44.5-spm → 8.3-kt sprint is the single cleanest
  experiment/theory cross-check in the literature; use as Lane-6 target.

### S10 — Lane-4 propulsion model implemented & verified [x]
First *runnable* physics artifact: `research/lane-4-oars/lane4_propulsion.py` (pure stdlib) +
`propulsion-models.md`. Implements the full engine→propeller chain and reproduces Shaw:
- **Sprint validation**: 130 rowers, 44.5 spm, E=0.730 → 18,152 W → **8.32 kts** (measured
  8.2–8.3). Calibration trial also recovers P = 288 N (k = P/r = 7.43).
- **Table 9.7** (Mark II rates): IIa 30.7/49.3 spm @ 228/366 N; IIb 28.8/46.2 spm @ 214/343 N —
  matches Shaw to rounding.
- **Ch.7 cruise**: rates 25.5/28.8/32.3 spm reproduced exactly; gross power/man 114/142/176 W
  (Shaw 115/145/180 — last two ~2–4 W higher, flagged for uncertainty register, likely rounding).
- **S6 cross-check** (independent of ch.7/9 power law): 7.2 kt, 170 men → 63 W/man propulsive,
  55% oar-system efficiency (S6 said ~62 W, ~54%).
- **W3 deliverable**: the speed↔power map (W_hull = 1.08·(155V³+4.13V⁵), P = 7.43·r, E = 0.78,
  L per design) is now fixed as the simulation's primary transfer; remaining W3 items are the
  per-stroke rigid-oar refinement layer.

### S11 — Web-search batch #2 results + primary reads (ch.1 GPS speeds, ch.25 stability) [x]
Batch of 4 searches (parallel) + 2 primary-text reads that landed in the same session.
- **Searches**:
  - **Carter 1982** = exact JONSWAP-formulae paper (already fully captured in S7/lane-2) [x]
  - **Coates, Platis & Shaw 1990**, *The Trireme Trials 1988* (Oxbow, ISBN 0-946897-21-2) exists [x]
    + Trireme Trust trials pages (1987/88/90/92 series) at https://eodg.atm.ox.ac.uk/user/dudhia/rowing/trireme/tttrials.html [x]
  - **Taylor ch.31** confirmed as **Andrew** Taylor (not Timothy), book pp.231–244 [x]; Excel
    workbook not found online — Trireme Trust archive is the next lead.
  - **BMT inclining/stability report** confirmed in Trireme Trust archive [x]; ch.25 text gives
    its substance (below).
- **Primary reads (Rankov 2012 PDF, prose extracts fine)**:
  - **ch.1.2 (Lipke/Ruddle/Weiskittel, 1992 trials + GPS)**: the 8.9 kt 1990 "record" was a single
    end-of-run reading; last-half average was **8.3 kt** (solid). 1992 GPS: 7.8–7.9 kt @ ~135
    rowers; peak 8.2 kt @ 121; authors claim **sustained 8.3 kt, brief peak ~8.5 kt** with
    confidence. 1988 geodimeter: burst 7.9 kt, runs mostly 7.3–7.5. **Table 1.2.1** = one
    acceleration run, spm→knots: 38→5.8, 41→6.0, 42→5.9, 43→6.2, 44→6.3, 45→6.6, 45→6.9,
    44→7.2, 45→7.4, 47→8.0, 46→8.1, …, 8.9 peak. 1992 crew ~154 (of 170), low 121 (8 Aug);
    rotation drill 40 min on / 20 min off. Voyage: Poros→Aegina 15.77 NM @ 3.7 kt into ≤10 kt
    wind; Aegina→Corinth 28.33 NM rowed in 9h38m @ 2.9 kt into ~20 kt headwind. **Feed: W6/D10
    (primary trial numbers now in hand), Lane-6 sprint target refined to 8.3 kt sustained.**
  - **ch.25 (Coates, bilge water/GM)**: inclining experiment **July 1990, BMT (Defence Services)
    Ltd report TR01/R1952**. Light ship: **25.798 t** (SG 1.025), VCG above USK **1.575 m**, LCG
    from displacement Station 23 **17.521 m**. Trial condition (crew 80 kg each): displacement
    **42.25 t**, KM 2.90 m, KG 1.77 m, **GM 1.13 m**. Solid-crew roll: GM→0.99 m (−0.14 m);
    leaning to double the roll: GM→0.85 m (−25%). Bilge to floor tops: +7.42 t (→49.67 t,
    +17.6%), sinks 6.7 cm, GM net ~0.99 m (free-surface loss offset by ballast — stability
    unaffected); sloshing power loss unmeasured. Bilge 0.6 m deep (free surface 3 m wide):
    +27 t (→69 t), sinks 25 cm, GM→0.66 m (−33%). **Feed: W1/D9 (light displacement now anchored
    25.798 t), W2/D7 (stability model), W6 (rowing ineffective if water > floor tops); bilge
    sloshing loss → uncertainty register.**
- **Feed for Lane-6 cross-checks**: Table 1.2.1 is a single **acceleration run**, so its
  mid-run speed-at-rate pairs under-predict steady-state — it must NOT be validated pointwise
  against the Lane-4 chain. Correct steady-state anchors: S10's 130 @ 44.5 spm → 8.32 kt, plus
  the 1992 GPS 2-min runs (@~135 → 7.8–7.9 kt; @121 → 8.2 kt peak). See lane-6 note §1.2.

### S12 — Web-search batch #3 results: Kempf, Eliav & Helfman, displacement, oar data [x]
Batch of 4 parallel searches (W5/W2/W1-D9/W3). Two were confirmations of already-captured
content; two produced new reconciliation/validation data.
- **Kempf manoeuvre (W5)** [x]: "Kempf manoeuvre" = the **standard zig-zag (Z-) manoeuvre**
  trial. Primary ref: **Kempf 1944, "Maneuvering Standards for Ships", *Hansa* 27/28**; HSVA
  Hamburg 1930s (Kempf & Krämer); analysis by **Nomoto 1960** (DTMB 1461). **Key negative
  finding: the 1.4×/0.6×/0.2× rudder-drag increments at 67.5°/45°/22.5° are Taylor's own
  calibration values, not a published Kempf method — no external primary source exists for
  them.** The model's turn drag (39.4v² straight-rudder, Olympias) is already verified against
  ch.31 Table 31.1 (row 4). Recorded in `lane-5-manoeuvre/taylor-excel.md` §3.
- **Eliav & Helfman 2022 (W2)** [x]: full PDF re-verified (ancientportsantiques.com). Confirms
  lane-3 record: empty 25 t (M&R 2000 p.210; 21 t Coates 1990, 23 t Coates 1999); laced hull
  −46% in FEA hogging test (reserve factor 2.7); **no quantified resistance penalty** — the
  "too heavy → slow" case is qualitative; hypozomata 4 ropes × 257 lb (117 kg). Abstract also
  confirms motivation: Olympias performance shortfall attributed in part to excessive weight.
- **Displacement reconciliation (W1/D9)** [x]:
  | Condition | Value | Source |
  |---|---|---|
  | Light ship | **25.798 t** | BMT inclining report (ch.25) |
  | Trial w/ crew (80 kg each) | **42.25 t** | ch.25 (KM 2.90, KG 1.77, GM 1.13 m) |
  | Trial full load | 42 t | Morrison et al. 2000 p.210 (via E&H); Osprey |
  | "Fully laden w/ crew" | **47 t** | Trireme Trust poster + Wikipedia + UChicago Animus |
  - Reading: 42.25 t = light ship + crew + trial outfit; the 47 t figure additionally includes
    the full naval outfit (rigging, masts, oars, benches, stores — E&H model ~4 t "extra", plus
    troops). Use 25.798 t light / 42.25 t trial as primary sim anchors; 47 t only for fully-
    laden "max capability" scenarios. Resolves the S1 "light ~ ?" gap.
- **Oar data (W3)** [x]: **oar lengths 9 cubits (3.99 m) & 9½ cubits (4.2 m)** on the 0.444 m
  cubit (Osprey "Machine of the Month", drawing on Zea sheds + iconography) — independent
  cross-check of Shaw's Tables 9.1/9.2 outboard lengths (2.817/2.80 m → ~6.3–6.4 cubits
  outboard). UChicago Animus: **1987 oars were "too light" and were redesigned for 1990** —
  explains variance in published oar masses; the 12.3 kg/oar figure remains uncorroborated
  (→ uncertainty register). 18.4° cant validated externally: Trireme Trust "Lessons from
  Olympias" gives **9.7 kt short sprint, 7.5 kt sustained cruise** for the Mark II design —
  consistent with S9/S10 targets.
- **Towing-tank (W2/D1) lead**: UChicago Animus retrospective confirms a **hull model tested in
  a ship tank in Athens** (NTUA) during design — primary resistance data behind Coates 1990
  ch. remains to be extracted from that chapter's text/tables (see W2/D1 next step).

### S13 — Uncertainties register + tank-test identification + Taylor-model external check [x]

Three-step session (steps 1–3 of the "next steps" list). Repo is consolidated (commits through
2e02774); all research now lives under `~/projects/sandbox/trireme/`.

1. **Uncertainties register created (W6)** [x]: `research/lane-6-validation/uncertainties-register.md`
   — 25 items A1–D5, each with value, flag, source, caveat, and [H]/[M]/[L] model sensitivity.
   [H] items: B1 (displacement — but primary anchors 25.798/42.25/43 t now solid), B2 (hull law —
   itself trial-validated 8.32 vs 8.2–8.3 kt), B4 (light-laced-hull scenario), C1 (Table 31.1
   row-12 units "kg m²" should be kg m² s⁻¹), D1 (8.9 kt peak suspect → use 8.2–8.3 sustained).
   Register replaces the scattered per-lane `[?]` flags as the single source of truth for
   uncertainty.
2. **Towing-tank identified (W2/D1)** [x]: primary reference = **Grekoussis, C. & Loukakis, T.
   (1985), "Athenian Trireme Calm Water Tests Without Ram", NTUA Report No. NAL 06-F-1985**
   (Rankov 2012 bibliography; ch.7 p.79: Shaw's **W = 155V³+4.13V⁵** hull-power law was deduced
   from these bare-hull model tests; graph reproduced by Lowry & Squire 1988; resistance/speed
   curves published in Shaw 1993, *The Trireme Project*). Ch.22 (Coates): power determined "with
   some certainty for calm water and wind by towing tests of a model and by towing the ship
   herself". **Report not online** (NTUA library/hardcopy) — raw resistance points remain the one
   unrecovered element; the law's shape is validated by trial speeds. Logged in lane-3 note (open
   item 7 → RESOLVED) and uncertainties register B2.
3. **Taylor Excel workbook (W5/D4) — conclusion confirmed** [x]: tDAR records 424186 (whole
   book) and 424277 (this chapter) are **citation-only**, "Center for Digital Antiquity does not
   have a copy"; ancientportsantiques.com hosts only the PDF; Trireme Trust archive catalogue
   (triremetrust.org.uk, now at Wolfson College) has no Excel entry. Best remaining leads:
   Wolfson archivist (archivist@wolfson.cam.ac.uk) or author Andrew Taylor. **External check of
   Taylor's model outputs** [x]: Alke Dominis blog ("what the diekplous are you talking about",
   2022) independently reproduces the chapter's tactical numbers — 0→full ~9.5 kt in ~40 s,
   reverse 80% of full speed, fast 180° turn @ full speed = 145 m diameter, tight turn @6–7 kt =
   60 m, diekplous gap ≥150 m (130 m aggressive) — all matching lane-5 note §6. Feed: W5/D4
   (workbook leads unchanged), W6 (tactical-turn validation targets independently confirmed).
   Also confirmed from the search: **Coates, Platis & Shaw 1990 (*Trireme Trials 1988*,
   ISBN 0-946897-21-2)** exists (OBNB); **Shaw 1993 (*The Trireme Project*, Oxbow,
   ISBN 9780946897582)** is the volume holding the published resistance/speed curve — both are
   physical-only acquisition targets.

### S14 — Parametric hull form built (W2) [x]

Step 1 of the "next steps" list. Cleanup of stale W1 checkboxes (decode tables, Table 31.1,
Table 8.3 reconcile — all done in S7/S11) committed separately.

- **Hull form (W2) built**: `research/lane-3-hull/hull_form.py` + `parametric-hull-form.md` +
  `hull-form-summary.csv`. Coates' sections are circular arcs (Plan 3) but no numeric offsets
  are in the text, so a parametric model is used: waterline half-breadth B(x)=Bmax·sin(πx)^p,
  rocker d(x)=dmax·sin(πx)^q, circular-arc sections. Fitted (p=1.5, q=0.8, Bmax=1.715 m =
  3.43 m beam) to reproduce both BMT displacements: trial 41.35 vs 41.22 m³ (+0.3%), light
  25.17 m³ (0%). Derived: wetted surface 81.3 m² (trial) / 71.0 m² (light), Cb 0.340, Cwp 0.556,
  VCB 0.493 m, LCB 16.10 m from stern, light draft 0.694 m.
- **Friction cross-checks** [x]: (a) vs Shaw's law — friction is 55%/42%/36% of W at
  2.0/3.5/4.3 m/s (read as low-ish, caveat logged); (b) vs Taylor T31.1 bare-hull 40.2v² —
  friction 55–62% and wave residual 38–45% across 4–9 kt, matching Coates ch.22 that skin
  dominates below ~6 kt with wave-making equalising near ~9 kt. This validates the ~81 m²
  wetted-surface estimate.
- **Stability mismatch** [x]: model KM = 1.428 m (BM 0.935 m, I_t 38.5 m⁴) under-predicts
  BMT KM = 2.90 m — the pure circular-arc waterplane (Cwp 0.556) is too lean; the real
  Olympias is fuller/flatter-bottomed. **Decision**: Lane 5 manoeuvring uses BMT measured
  KM 2.90 m / GM 1.13 m directly, not model KM. Logged in uncertainties register (new row).

### S15 — Parametric hull form + W5 manoeuvring model built [x]

Steps 1–2 of the next-steps list (Step 3 = W6 validation table, pending).

- **Step 1 (W2 hull form)** [x]: see S14 — parametric circular-arc hull fitted to BMT
  displacements, wetted surface validated vs Taylor drag, KM under-prediction flagged
  (commit 012d426).
- **Step 2 (W5 manoeuvring model)** [x]: `research/lane-5-manoeuvre/manoeuvre_model.py` —
  faithful re-implementation of Taylor ch.31 from chapter text + OCR Table 31.1. All §6
  targets reproduced to ≤7% with no fitting: turn diameters 151.8/74.6/64.0 m vs 145/80/62,
  acceleration 5.56/9.01/9.81 kt at 10/24/40 s, braking 19 s over 56 m, astern 9.38 kt.
  Heel over-predicts ~1° (4.0 vs 3.5° fast anastrophe; needs deck-crew mitigation).
  Uses BMT KM/GM per S14 decision. Committed with note `manoeuvre-model.md` + W5 checklist
  update.

### S16 — W6 validation table + sensitivity pass [x]

Step 3 of the next-steps list. Closes the W6 checklist.

- **Validation table** [x]: `research/lane-6-validation/validation_table.py` +
  `validation-table.md`. Maps every trial measurement to a prediction from the two
  validated models (lane-4 chain + lane-5 Taylor model + lane-3 hull). Results: all
  steady-state speeds within the ch.22 53–55% efficiency band (sustained 8.0–8.1 vs
  8.2–8.3 kt; GPS 135-rower 7.7–7.8 vs 7.8–7.9; sprint 8.3 vs 8.2–8.3), turns ≤7%
  (152/75/64 vs 145/80/62 m), braking 19 s/56 m, astern 9.4 kt, BMT volumes exact.
  Accel 0→7 kt: trained model 14 s vs 1988 trial 32 s (less-trained crew) = context row.
- **Sensitivity pass** [x]: displacement ±2% → sprint ±0.5% (second-order, hull law
  trial-validated); GM 1.13/0.99/0.85 → heel 3.0/3.6/4.3° at fast anastrophe (diameter
  unchanged — yaw-driven; GM sets heel limit only, matching Taylor's "deck-crew move"
  for the >3° cases); oar efficiency 40→54% → sustained 7.4→8.1 kt; crew 121→154 →
  7.5→8.1 kt. **Dominant knobs: crew power/efficiency (D4 [H]); displacement second-order.**
- Committed with validation-table.md + W6 checklist update.

---

## Task playbooks (repeatable workflows) — LIVE INDEX

The `research/tasks/` directory holds short how-to guides for tasks we repeat. **Read the relevant
playbook before starting the task** — they record the venv split, page-offset convention (book page
+ 12), and pitfalls. This index must be kept in sync with the actual files in `research/tasks/`:
when a playbook is added/renamed, update both this index and `research/tasks/README.md`.

| Playbook | Use it when |
|---|---|
| `pdf-text-extraction.md` | You need clean prose text from a PDF that extracts fine (`get_text()`). |
| `pdf-subset-font-decode.md` | Prose is rendered with subset TT fonts → PUA chars / `?` (use `decode_shaw.py`). |
| `pdf-ocr-table-decoding.md` | You need the **numbers inside a table** (OCR route — reliable for table digits). |
| `verify-decoded-tables.md` | Any decoded table must be independently reconstructed from source equations. |

**Process note:** the first time a task is done twice, write (or extend) a playbook for it. When a
better recipe is found, update the playbook — later sessions read it as gospel. Deliverables promoted
from `/tmp/opencode` scratch to `research/data/` must be logged in a new S-section here.
---
