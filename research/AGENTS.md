# research/ — the validated evidence base

Everything the simulators rely on, with provenance and confidence flags
(status legend: `[x]` confirmed from a cited source, `[?]` uncertain/conflicting).
The lanes below are complete as far as the sources permit; the still-open
external gaps are listed at the bottom. Read the playbooks in `tasks/`
*before* any extraction/decoding task.

Primary source book: **Rankov 2012** (*The Trireme Olympias: The Final
Report* — the sea trials and the design chapters, cited below as "ch.").
Its PDF lives in `sources/rankov2012.pdf` with a full text dump.

## Lane map

| Lane | Topic | Key files |
| --- | --- | --- |
| `lane-1-read` | Source reading notes | `shaw-ch7-ch9-2024.md` (Rankov ch.7–9 read in full) |
| `lane-2-waves` | Wave environment | `shaw-tables-81-82-wind-propulsion.md`, `carter-equations.md` (Shaw Tables 8.1–8.4, growth equations) |
| `lane-3-hull` | Hull form & resistance | `parametric-hull-form.md`, `hull-form-summary.csv`, `hull_form.py` (waterline length 32.2 m; 41.4 t trial / 25.2 t light displacement; the metacentric-height (KM) stability caveat on record), `braithwaite-workbook.md` (the real Lines-Plan offsets + hydrostatics + the weight breakdown — from the author's design tool; lightship 25.75 t confirms the 25.798 t anchor) |
| `lane-4-oars` | Oar rig, power, blade physics | `rig-geometry.md`, `oar-data.md` (Rankov Table 3.1/3.2 decoded), `lane4_propulsion.py` (the per-rower power law P = 7.43·r), `rigid_oar_model.py` (flat-plate per-stroke), `rigid-oar-refinement.md`, `oar_inertia.py` (Table 3.1 inertias, the catch-flip spike — the oar's snap at the start of the stroke), `braithwaite-workbook.md` (the trials thrust law 81 N→0 @ 18 kt — agrees with our zero-speed equilibrium; the trials resistance fit; the 9.95 kt no-head-room bound) |
| `lane-5-manoeuvre` | Turning | `manoeuvre-model.md`, `manoeuvre_model.py`, `fg-turns-rerun.md` (the F/G trial turns ≤ 7 %), `taylor-excel.md`, `clr-rotation.md` (the centre-of-lateral-resistance rotation), `braithwaite-workbook.md` (the independent 3-DOF model: CGH derivatives, the cross-flow yaw damper CN 0.4/0.8 `[?]`, Iz = m(L/3)², the Hoerner rudder + the trials parasitic drag) |
| `lane-6-validation` | Cross-cutting validation | `validation-table.md` (research side: bulk models vs trials), `uncertainties-register.md` (every `[?]` item, its impact), `primary-trial-data.md`, `validation_table.py`. The simulator's acceptance record is `../simulation/docs/VALIDATION.md` |
| `data/` | Decoded source tables | `shaw-table-3.1-oar-inertia.csv`, `shaw-table-3.2-stroke-rhythm.csv`, Shaw 8.x tables, Taylor parameters (`table31-1-taylor-model-parameters.csv`) |
| `tasks/` | Repeatable playbooks | PDF text extraction, subset-font decode, OCR table decoding, verify-decoded-tables |

## The validated chain (what the sims consume — via `../simulation/common/chain.py`)

Units: spm = strokes per minute; kt = knots; t = tonnes.

- Rig: tiers 62/54/54 (170 oars); interscalmium (oar-station spacing)
  0.888 m; inboard (pivot-to-handle) 1.092 m; sweeps (the oars' swing arcs)
  48.1/48.4/55.6°; blade 0.55 m; area 0.078 m².
- Power: the hull-power law W_hull = 155V³ + 4.13V⁵ (V in kt; ×1.08 Mark II
  rig variant); per-rower power P = 7.43·r W at rate r; efficiency
  E = 0.756–0.78; pull length per design (0.87/0.99 m for the Mark IIa/IIb rig variants, 0.78 m
  Olympias).
- Blade: the flat-plate normal force Fn = ½ρAC_N·|v_n|·v_n, C_N = 1.8; the
  blade's centre of pressure 0.26 m from the tip.
- Hull: apparent mass m_app = 1.10·m; the ship's net thrust 17.4 − 0.967·v kN at
  speed v; a 3-band drag law (piecewise over speed bands); the F/G turn model.
- Cruise 25.5/28.8/32.3 spm → 7/7.5/8 kt (Rankov ch.7); sprint 44.5 spm →
  8.2–8.4 kt (ch.9, measured 8.2–8.3).
- Oar inertias: the Table 3.1 ten-oar set (spruce 8.2 kg, old-fir zygian
  15.1 kg, thranite 11.0 kg hand mass); Table 3.2 couple/rhythm vs rate
  cross-checks (32 spm couple 246 N·m ↔ 225 N handle at 1.092 m inboard).

**Session markers**: provenance shorthands like "(S12)" in the lane
notes refer to the research session log S1–S16, which now lives in git
history (the file `research/trireme-rowing-simulation-research.md` up to
the 2026-08 restructure commit); the underlying sources are always cited
inline in the same sentences.

## Conventions

- **Confidence flags**: `[x]` confirmed directly from a cited source; `[?]`
  inferred/unverified/conflicting. Never upgrade a flag without the primary source.
- **Record as printed**: decoded tables keep source values even when inconsistent
  (the Table 3.1 old-zygian A/B anomaly — the oars' inertia term MIT =
  weight·(radius-of-gyration² + inboard²) checks out on 8 of 10 rows, and the
  two odd rows are recorded as printed, ≈ −9.7 % vs the 1.092 m relation) —
  flag in docs, never force consistency by editing values.
- **CSVs**: `#` comment lines allowed at top, then a plain header; readers filter
  comments.
- **Python**: use the repo-local venv `.venv/bin/python3` (numpy/scipy/matplotlib/
  pymupdf/PIL included). The OCR stack (easyocr+torch) is on-demand only — recipe
  in `tasks/AGENTS.md`. The old /tmp/opencode venv split is deprecated.
- **Rankov 2012 pages**: PDF page index = printed book page + 12.
- When a finding changes the chain, update: the relevant lane doc, the
  `uncertainties-register.md`, and — if a sim consumes it — `../simulation/common/chain.py`
  plus the affected gate tests.

## Open items

**Simulator-side** (mirror the simulation's open items): the crew endurance
model (how long a rate/pressure is sustainable) and the wave-added resistance
law (Phase 4); anastrophe (the ancient turn-by-oars manoeuvre) validation data
is thin — the LL validates qualitatively; the open physics rows live in
`../simulation/docs/VALIDATION.md` §10–§11 (the 360°-turn time, the drift
angle, the ch.7 cruise triple).

**External gaps** (archive requests only — nothing here blocks the sims):
- the raw towing-tank resistance points (Grekoussis & Loukakis 1985, NTUA —
  the National Technical University of Athens — tank report NAL 06-F-1985;
  hardcopy only; the law deduced from it is trial-validated);
- Taylor's Excel workbook behind Rankov ch.31 (Wolfson/Trireme Trust archive leads);
- the hull offsets from Coates Plans 2/7 (Trireme Trust archivist);
- the full BMT 1991 inclining-experiment report (TR01/R1952 — BMT Defence
  Services, the naval consultancy; the headline numbers are already in the
  Rankov ch.25 text);
- the A/B MIT anomaly (parked — only the 1994/1996 raw appendix could resolve);
- ANSUR 1988 (the US Army anthropometric survey) 50th-percentile ergonomics
  digits (flagged `[?]` in oar-data.md §6).
