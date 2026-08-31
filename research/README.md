# research/ — the evidence

Everything the models rely on, with sources and confidence flags.

- `[x]` = confirmed directly from a cited source
- `[?]` = uncertain, conflicting, or not yet verified

The lanes below cover every topic the models need. Nothing here blocks
the models — the gaps are about getting even better numbers, not about
missing foundations.

Primary source book: **Rankov 2012** (*Trireme Olympias: The Final
Report* — the sea trials and the design chapters, cited below as "ch.").
The PDF and a full text dump are in `sources/`.

## What's in each lane

| Lane | Topic | Key files |
|---|---|---|
| `lane-1-read` | Reading the trial reports | `shaw-ch7-ch9-2024.md` (Rankov ch.7–9 read in full) |
| `lane-2-waves` | Waves and weather | `waves.md` (Shaw Tables 8.1–8.4 — wave growth + wind tables) |
| `lane-3-hull` | Hull shape and resistance | `hull-form.md` (hull shape + offsets/Eliav & Helfman + stability notes), `hull-form-summary.csv`, `hull_form.py`, `braithwaite-workbook.md` (real hull offsets + water-plane numbers + weight breakdown — from the design tool; lightship 25.75 tonnes matches the 25.798-tonne anchor) |
| `lane-4-oars` | Oars, power, and blades | `rig-and-oars.md` (oar layout, Tables 3.1/3.2 decoded, the flat-plate blade model), `propulsion-models.md`, `lane4_propulsion.py` (power per rower: P = 7.43 × stroke rate), `rigid_oar_model.py`, `oar_inertia.py` (the force spike at the catch), `braithwaite-workbook.md` (trials thrust law, resistance curve, the 9.95-knot no-headroom bound) |
| `lane-5-manoeuvre` | Turning | `manoeuvre.md` (the reference turning model + Excel/Kempf notes + F/G re-run within 7% + CLR rotation), `manoeuvre_model.py`, `fg_turns_rerun.py`, `clr_rotation.py`, `crossflow.py` (the yaw-damping check), `braithwaite-workbook.md` (independent 3-direction model: CGH derivatives, cross-flow yaw damper, Hoerner rudder + trials drag) |
| `lane-6-validation` | Checking everything together | `validation.md` (trial data + model-vs-trial mapping + sensitivity), `uncertainties-register.md` (every `[?]` item and what it affects), `validation_table.py`. The models' acceptance record is `../simulation/docs/VALIDATION.md` |
| `data/` | Decoded source tables | `shaw-table-3.1-oar-inertia.csv`, `shaw-table-3.2-stroke-rhythm.csv`, Shaw 8.x tables, Taylor parameters (`table31-1-taylor-model-parameters.csv`) |
| `tasks/` | How-to guides | PDF text extraction, font decoding, OCR table decoding, checking decoded tables |

## The validated chain (what the models use via `../simulation/common/chain.py`)

Units: spm = strokes per minute; kt = knots; t = tonnes.

- Oar layout: 62/54/54 oars in three tiers (170 total); spacing between
  oar stations 0.888 m; handle-to-pivot 1.092 m; oar swing arcs
  48.1/48.4/55.6°; blade 0.55 m long; area 0.078 m².
- Power: hull needs W = 155V³ + 4.13V⁵ watts at speed V in kt (×1.08 for
  the Mark II rig variant); each rower produces P = 7.43 × rate watts;
  oar efficiency 0.756–0.78; pull length per design (0.87/0.99 m for
  Mark IIa/IIb, 0.78 m for Olympias).
- Blade: flat-plate force Fn = ½ρAC_N·|v_n|·v_n, C_N = 1.8; the blade's
  push centre is 0.26 m from the tip.
- Hull: effective mass is 1.10× real mass; net thrust 17.4 − 0.967·v
  kilonewtons at speed v; 3-band drag law; the F/G turn model.
- Cruising: 25.5/28.8/32.3 strokes/min → 7/7.5/8 knots (Rankov ch.7);
  sprint at 44.5 → 8.2–8.4 knots (ch.9, measured 8.2–8.3).
- Oar spin: the Table 3.1 ten-oar set (spruce 8.2 kg, old-fir middle tier
  15.1 kg, lower tier 11.0 kg as handle weight); Table 3.2 force/rhythm
  cross-checks (32 strokes/min: 246 N·m at the pivot ≈ 225 N at the
  handle with 1.092 m inboard lever).

## Rules

- **Confidence flags**: `[x]` confirmed from a cited source; `[?]` not
  yet verified or conflicting. Don't upgrade `[?]` to `[x]` without the
  primary source.
- **Record as printed**: if a decoded table looks inconsistent, keep the
  source's values and note the issue — don't edit numbers to make them match.
  Example: Table 3.1 rows A/B have an odd inertia value (about 10% off
  the 1.092 m relation) — recorded as printed, flagged.
- **CSVs**: `#` comment lines at the top are allowed; readers must skip them.
- **Python**: use the repo's own Python at `.venv/bin/python3` (has numpy,
  scipy, matplotlib, pymupdf, PIL, etc.). The heavy OCR tools (easyocr +
  torch) are installed separately when needed — recipe in `tasks/README.md`.
- **Rankov 2012 pages**: printed book page + 12 = PDF page number.
- When a finding changes the chain, update: the lane doc, the
  `uncertainties-register.md`, and — if a model uses it —
  `../simulation/common/chain.py` plus the affected tests.

## What's still open

**Model side** (see `../simulation/docs/VALIDATION.md` §10–§11 for the
full list): the crew stamina model, the wave drag law, and a few
turning scenarios where the model doesn't yet match the trials (360°
turn time, sideways lean, cruising at high stroke rates — all
documented with known causes).

**Source gaps** (need archive access — nothing here blocks the models):
- The raw towing-tank numbers (Grekoussis & Loukakis 1985, NTUA tank
  report NAL 06-F-1985; only on paper; the curve fitted from it is
  already confirmed at sea);
- Taylor's Excel workbook behind Rankov ch.31
  (Trireme Trust archive at Wolfson College, Cambridge);
- The hull offsets from Coates Plans 2/7 (same archive);
- The full BMT inclining report (TR01/R1952; headline numbers already
  in Rankov ch.25);
- Why Table 3.1 rows A/B look odd (only the raw 1994 appendix could
  explain);
- Body measurements for the rowers (flagged `[?]` in the oar data).
