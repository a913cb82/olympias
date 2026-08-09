# Trireme — Olympias-class trireme performance: research + simulation

An evidence-driven project on the performance of the Athenian trireme (Olympias
reconstruction): a **validated physics chain** (`research/`) feeding **two
simulators** (`trireme-sim/`) that share one commander command language.

Chain of trust: **real-world data → LL → HL**. The low-level simulator (LL, per-oar
physics) is the oracle against the validated numbers; the high-level simulator (HL,
fast ship-level) is an approximation validated against the LL. Full design:
`trireme-simulation-plan.md`.

## Layout

```
research/                        the validated evidence base (see research/AGENTS.md)
  lane-1-read … lane-6-validation   one topic per lane (oars, hull, waves, manoeuvre…)
  data/                            decoded source tables (CSV, # comments allowed)
  tasks/                           repeatable extraction/decoding playbooks
trireme-sim/                     the simulators (see trireme-sim/AGENTS.md)
  commands/  schema + script parser (Step 0, done)
  ll/        per-oar reality-grade sim — Phase 1 Gate 1 (one oar) done, Gate 2 (hull) next
  hl/        fast ship-level sim — not built yet (its curves come from LL runs)
sources/                         source PDFs (Rankov 2012, Carter, …)
tools/                           decode/OCR helpers + extracted text dumps
trireme-rowing-simulation-research.md   research tracker (status legend inside)
trireme-simulation-plan.md              the simulator plan (oQ-1…21, gates, contract)
```

## Key facts (validated chain, the acceptance floor)

- Rig: tiers 62/54/54, interscalmium 0.888 m, inboard 1.092 m, sweeps 48.1/48.4/55.6°,
  blade 0.55 m, area 0.078 m².
- Power: W_hull = 155V³ + 4.13V⁵ (×1.08 Mark II), P = 7.43·r, E = 0.756–0.78.
- Blade: Fn = ½ρAC_N·|v_n|·v_n, C_N = 1.8, blade CP 0.26 m from tip; m_app = 1.10·m.
- Cruise 25.5/28.8/32.3 spm → 7/7.5/8 kt; sprint 44.5 spm → 8.2–8.4 kt (measured);
  F/G turns validated ≤ 7 %.
- Command language: 4 crew verbs — `rate`, `oars`, `pressure`, `helm` (per-side
  scoping; see plan §3.2).

## Conventions (read before touching files)

- **Python**: use `/tmp/opencode/venv/bin/python3` (or `/tmp/opencode/research-venv`
  for pymupdf/PIL/scipy work) — never the global interpreter.
- **Markdown**: markdownlint autofixes on save — after writing a file, re-read it
  before further edits (content changes on disk).
- **CSVs**: `#` comment lines allowed at top, then a plain header; readers must
  filter comments.
- **Confidence flags** in research docs: `[x]` = confirmed from a cited source,
  `[?]` = uncertain/conflicting.
- **Record as printed**: decoded tables keep the source's values even where they are
  internally inconsistent (e.g. Table 3.1 A/B MIT anomaly) — flag in docs, never
  alter to force consistency.
- **Determinism**: simulators are deterministic/replayable (fixed dt, seeded RNG,
  logged command stream).
- **Honest layers**: new physics is labelled and swappable; tuning never silently
  overrides the validated chain (oQ-18 is the standing example).

## Status

- Research chain: validated for cruise/sprint/turn (ch.7/ch.9, F/G ≤ 7 %).
- Sim: Step 0 (schema + parser, 19 checks) and Phase 1 Gate 1 (one-oar LL vs rigid
  model, 7 checks) done. Next: Phase 1 Gate 2 — hull surge vs ch.7/ch.9.

## Quick commands

```bash
V=/tmp/opencode/venv/bin/python3
cd trireme-sim
$V tests/test_parser.py          # command-language checks (19)
$V ll/tests/test_gate1.py        # one-oar acceptance (7)
$V ll/run_one_oar.py             # one-oar table at the anchored cruise point
$V ll/run_one_oar.py --rig MarkIIb --v-kts 7.5 --spm 28.8 --t-drive 0.612   # oQ-18 point
```
