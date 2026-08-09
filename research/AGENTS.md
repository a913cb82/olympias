# research/ — the validated evidence base

Everything the simulators rely on, with provenance and confidence flags. The
top-level tracker is `./trireme-rowing-simulation-research.md` (status legend:
`[x]` done, `[ ]` pending, `[?]` uncertain). Read the playbooks in `tasks/`
*before* any extraction/decoding task.

## Lane map

| Lane | Topic | Key files |
| --- | --- | --- |
| `lane-1-read` | Source reading notes | `shaw-ch7-ch9-2024.md` |
| `lane-2-waves` | Wave environment | `shaw-tables-81-82-wind-propulsion.md`, `carter-equations.md` (Shaw Tables 8.1–8.4, growth equations) |
| `lane-3-hull` | Hull form & resistance | `parametric-hull-form.md`, `hull-form-summary.csv`, `hull_form.py` (LWL 32.2 m, 41.4 t trial / 25.2 t light; KM caveat on record) |
| `lane-4-oars` | Oar rig, power, blade physics | `rig-geometry.md`, `oar-data.md` (Rankov Table 3.1/3.2 decoded), `lane4_propulsion.py` (P = 7.43·r chain), `rigid_oar_model.py` (flat-plate per-stroke), `rigid-oar-refinement.md`, `oar_inertia.py` (Table 3.1 inertias, catch-flip) |
| `lane-5-manoeuvre` | Turning | `manoeuvre-model.md`, `manoeuvre_model.py`, `fg-turns-rerun.md` (F/G ≤ 7 %), `taylor-excel.md`, `clr-rotation.md` |
| `lane-6-validation` | Cross-cutting validation | `validation-table.md` (research side: bulk models vs trials), `uncertainties-register.md`, `primary-trial-data.md`, `validation_table.py`. The simulator's acceptance record is `../simulation/VALIDATION.md` (the LL side) |
| `data/` | Decoded source tables | `shaw-table-3.1-oar-inertia.csv`, `shaw-table-3.2-stroke-rhythm.csv`, Shaw 8.x tables, Taylor parameters (`table31-1-taylor-model-parameters.csv`) |
| `tasks/` | Repeatable playbooks | PDF text extraction, subset-font decode, OCR table decoding, verify-decoded-tables |

## The validated chain (what the sims consume — via `../simulation/common/chain.py`)

- Rig: tiers 62/54/54; interscalmium 0.888 m; inboard 1.092 m; sweeps
  48.1/48.4/55.6°; blade 0.55 m; area 0.078 m².
- Power: W_hull = 155V³ + 4.13V⁵ (×1.08 Mark II); P = 7.43·r; E = 0.756–0.78;
  pull length per design (0.87/0.99 m Mark IIa/IIb, 0.78 Olympias).
- Blade: Fn = ½ρAC_N·|v_n|·v_n, C_N = 1.8 (flat plate), blade CP 0.26 m from tip.
- Hull: m_app = 1.10·m; thrust 17.4 − 0.967·v kN; 3-band drag; F/G turn model.
- Cruise 25.5/28.8/32.3 spm → 7/7.5/8 kt (ch.7); sprint 44.5 spm → 8.2–8.4 kt
  (ch.9, measured 8.2–8.3).
- Oar inertias: Table 3.1 ten-oar set (spruce 8.2 kg, old fir zygian 15.1 kg,
  thranite 11.0 kg hand mass); Table 3.2 couple/rhythm vs rate cross-checks
  (32 spm couple 246 N·m ↔ 225 N handle at 1.092 m).

## Conventions

- **Confidence flags**: `[x]` confirmed directly from a cited source; `[?]`
  inferred/unverified/conflicting. Never upgrade a flag without the primary source.
- **Record as printed**: decoded tables keep source values even when inconsistent
  (Table 3.1 old-zygian A/B MIT anomaly ≈ −9.7 % vs the 1.092 m relation) — flag in
  docs, never force consistency by editing values.
- **CSVs**: `#` comment lines allowed at top, then a plain header; readers filter
  comments.
- **Python**: use the repo-local venv `.venv/bin/python3` (numpy/scipy/matplotlib/
  pymupdf/PIL included). The OCR stack (easyocr+torch) is on-demand only — recipe
  in `tasks/AGENTS.md`. The old /tmp/opencode venv split is deprecated.
- **Rankov 2012 pages**: PDF page index = printed book page + 12.
- When a finding changes the chain, update: the tracker, the relevant lane doc, the
  `uncertainties-register.md`, and — if a sim consumes it — `../simulation/common/chain.py`
  plus the affected gate tests.

## Open items (living; mirror plan oQ-* and §9.1)

- Crew endurance model (duration at rate/pressure) — Phase 4.
- Wave-added resistance law — Phase 4 (labelled approximation acceptable).
- Ergonomics digits: ANSUR 1988 50th-percentile values, Greek mean-height estimate
  (1.70 m) — flagged `[?]` pending primary-table reads.
- Anastrophe / turn-by-oars validation data — thin; LL validates qualitatively.
- A/B MIT anomaly — parked: only the 1994/1996 raw report appendix could resolve.
