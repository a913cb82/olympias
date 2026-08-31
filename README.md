# Trireme — how fast and how agile was the Athenian trireme?

We are answering one question: **how fast and how agile was the Athenian
trireme?** The test case is the Olympias — a full-scale replica built in
the 1980s and sea-trialled in 1987.

The project has two halves:

1. **`research/`** — the evidence. Decoded trial data, hull shape, oar
   physics, turning models. Every number traces back to a published source
   (Rankov 2012, the trial logs, the hull drawings). This is the ground
   truth.

2. **`simulation/`** — two computer models of the ship. They predict
   speed, power, and turning, and are tested against the research numbers.

## The two models

| | LL (low-level) | HL (high-level) |
|---|---|---|
| What it does | Simulates every oar individually (170 of them) with real blade forces | Treats the ship as one object with pre-measured response curves |
| Speed | Slow — minutes per run | Fast — seconds per run |
| Job | The **oracle** — must match trial data | An **approximation** — must stay close to the LL |
| Where | `simulation/ll/` | `simulation/hl/` |

The HL's response curves are made automatically from LL runs — no hand
tuning. A harness (`simulation/harness/`) runs the same command script
on both models and checks they agree.

## How trust flows

```
trial data  →  research/  →  LL model  →  HL model
(Rankov etc)   (evidence)   (oracle)     (fast copy)
```

Every number in the models traces back to a research document, which
traces back to a published source. Nothing is made up.

## Layout

```
research/                     the evidence base
  lane-1-read … lane-6-validation       one topic per lane (oars, hull, waves, turns…)
  data/                       decoded source tables (CSV, # comments allowed)
  sources/                    source PDFs and build logs

simulation/                   the two models
  commands/                   the command language (how you tell the ship what to do)
  common/                     shared numbers (chain.py — the single source of truth)
  ll/                         the LL model (per-oar physics)
  hl/                         the HL model (fast ship-level model)
  harness/                    runs both models on the same script and compares
  docs/                       VALIDATION.md — the full acceptance record
  ui/                         browser replay (replays computed runs, nothing to install)
```

## Rules

- **Python**: always use `.venv/bin/python3` — never the system Python.
- **CSVs**: `#` comment lines at the top are allowed; readers must skip them.
- **Confidence flags** in research docs: `[x]` = confirmed from a cited
  source, `[?]` = uncertain or conflicting.
- **Record as printed**: decoded tables keep the source's values even where
  they look inconsistent — note the issue, don't edit the numbers to make
  them match.
- **Same input → same output**: both models give the same answer every time
  for the same input (fixed time step, seeded random numbers, logged
  commands).
- **No silent tuning**: new physics is labelled and swappable. Tuning
  never quietly overrides the validated chain.

## Quick commands

```bash
cd simulation
V=../.venv/bin/python3
$V -m pytest                    # run all tests
$V ll/run_one_oar.py            # one-oar table at the cruise point
$V ll/run_turn.py table         # turn scenarios vs trial data
$V ll/run_hull.py --table       # speed curve over stroke rates
$V hl/run_hl.py --turn table    # fast model turn scenarios
$V hl/calibrate.py              # rebuild HL curves from LL (~4 min)
$V harness/run_validation.py    # check HL vs LL agreement
$V ui/serve.py                  # open the browser replay
```
