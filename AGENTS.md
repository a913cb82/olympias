# Trireme — Olympias performance: research + simulation

We are answering one question: **how fast and how agile was the Athenian
trireme?** Specifically the Olympias reconstruction — a full-scale replica
built in the 1980s and sea-trialled in 1987.

The project has two halves:

1. **`research/`** — the evidence base. Decoded trial data, hull geometry,
   oar physics, manoeuvre models. Everything here is traced to published
   sources (Rankov 2012, Carter, Morrison, the trial logs). This is the
   ground truth.

2. **`simulation/`** — two computer simulators that predict the ship's
   speed, power, and turning behaviour. They are tested against the
   research numbers, not against guesswork.

## The two simulators

| | LL (low-level) | HL (high-level) |
|---|---|---|
| What it does | Simulates every oar individually, 170 of them, with real blade forces | Treats the ship as one object with pre-measured response curves |
| Speed | Slow (minutes per scenario) | Fast (seconds per scenario) |
| Role | The **oracle** — must match trial data exactly | An **approximation** — must stay close to the LL |
| Where | `simulation/ll/` | `simulation/hl/` |

The HL's response curves are **machine-generated** from LL runs (not
hand-tuned). A harness (`simulation/harness/`) runs the same command
script on both simulators and checks they agree.

## The chain of trust

```
real-world trial data  →  research/  →  LL simulator  →  HL simulator
     (Rankov, etc.)      (evidence)     (oracle)         (fast copy)
```

Nothing is made up. Every number in the simulators can be traced back
to a research document, which traces back to a published source.

## Layout

```
research/                     the validated evidence base
  lane-1-read … lane-6        one topic per lane (oars, hull, waves, manoeuvre…)
  data/                       decoded source tables (CSV, # comments allowed)
  sources/                    source PDFs + build logs

simulation/                   the two simulators
  commands/                   the command language (how you tell the ship what to do)
  common/                     shared constants (chain.py — the single source of truth)
  ll/                         the LL — per-oar physics simulator
  hl/                         the HL — fast ship-level simulator
  harness/                    runs both sims on the same script and compares them
  docs/                       VALIDATION.md — the acceptance record
  ui/                         browser replay UI (replays computed runs, no install needed)
```

## Conventions

- **Python**: always use `.venv/bin/python3` — never the global Python.
- **CSVs**: `#` comment lines at top are allowed; readers must filter them.
- **Confidence flags** in research docs: `[x]` = confirmed, `[?]` = uncertain.
- **Record as printed**: decoded tables keep the source's values even where
  inconsistent — flag in docs, never alter to force consistency.
- **Determinism**: both simulators produce the same output every time for
  the same input (fixed time step, seeded random, logged commands).
- **Honest layers**: new physics is labelled and swappable. Tuning never
  silently overrides the validated chain.

## Quick commands

```bash
cd simulation
V=../.venv/bin/python3
$V -m pytest                    # run all tests — the count is in VALIDATION.md
$V ll/run_one_oar.py            # one-oar table at the cruise point
$V ll/run_turn.py table         # turn scenarios vs trial data
$V ll/run_hull.py --table       # speed curve over the stroke rates
$V hl/run_hl.py --turn table    # fast ship turn scenarios
$V hl/calibrate.py              # regenerate HL curves from LL (~4 min)
$V harness/run_validation.py    # check HL vs LL agreement
$V ui/serve.py                  # open the browser replay UI
```
