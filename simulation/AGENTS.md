# simulation — the two simulators

This directory contains two computer simulators of the Olympias trireme.
They share one command language — the same script runs on both.

The ground truth they must satisfy: `../research/AGENTS.md` (the evidence
base). The acceptance record — every gate, every result, every honest
mismatch — lives in [`docs/VALIDATION.md`](docs/VALIDATION.md).

## How the two simulators relate

```
                  ┌──────────┐
  command script →│   LL     │→ telemetry (speed, position, forces)
                  │ (oracle) │
                  └──────────┘
                       │
                       │  machine-calibrates
                       ▼
                  ┌──────────┐
  command script →│   HL     │→ telemetry (same format as LL)
                  │  (fast)  │
                  └──────────┘
                       │
                       │  harness compares
                       ▼
                  ┌──────────┐
                  │ agreement│→ pass/fail per gate
                  │  check   │
                  └──────────┘
```

**LL** (`ll/`): Simulates 170 individual oars with real blade forces.
Slow (minutes per run) but physically accurate. Must match trial data.

**HL** (`hl/`): Treats the ship as one object with pre-measured response
curves (speed vs stroke rate, turn diameter vs helm angle, etc.). Fast
(seconds per run). Its curves are generated automatically from LL runs,
never hand-edited.

**Harness** (`harness/`): Runs the same command script on both sims and
checks they agree within documented tolerances.

## Command language

Scripts are one command per line. `#` lines are comments. Format:
`<time_s> <verb> [args...]`

The four crew verbs:

| Verb | What it does | Example |
|---|---|---|
| `rate` | Set the stroke rate (spm) for the whole ship | `30 rate 28.8` |
| `oars` | Set what the oars are doing (per side or both) | `60 oars hold port` |
| `pressure` | Set effort level (per side or both) | `0 pressure steady` |
| `helm` | Set the steering oar angle | `0 helm port 1.0` |

Rates accept aliases: `slow` (24), `working` (30), `racing` (44).
Oar states: `row` (normal), `hold` (brake), `back` (reverse), `bank`
(raised out of water). Pressure levels: `rest`, `steady`, `fast`,
`spoude` (maximum burst).

Full-rudder turn example:
```
0 helm port 1.0        # hard to port, full deflection
0 rate 30
0 pressure steady
```

One-side-hold tightest turn:
```
0 oars hold starboard   # hold water on starboard side only
0 rate 44
0 pressure spoude
0 helm starboard 1.0
```

The schema is at `commands/schema.json`.

## Running things

All commands from the `simulation/` directory. Python is always
`.venv/bin/python3` (from `simulation/`, that's `../.venv/bin/python3`).

### Tests

```bash
V=../.venv/bin/python3
$V -m pytest                       # all tests, one command
$V -m pytest -v                    # with test names
$V -m pytest ll/tests/test_gate5.py  # one suite
```

The test count and per-gate breakdown live in `docs/VALIDATION.md`,
not here.

### LL runners

```bash
$V ll/run_one_oar.py               # one-oar table at 7.2 kt / 28.8 spm
$V ll/run_turn.py table            # turn scenarios vs trial data
$V ll/run_hull.py --table          # speed curve over stroke rates
```

### HL runners

```bash
$V hl/run_hl.py --turn table       # fast ship turn scenarios
$V hl/calibrate.py                 # regenerate HL curves from LL (~4 min)
```

### Harness

```bash
$V harness/run_validation.py       # HL vs LL equivalence tables
```

### Replay UI

```bash
$V ui/serve.py                     # opens browser — replays computed runs
```

No install, no build. The viewer is a single HTML file. Regenerate logs
after any LL/HL change: `$V ui/dump.py` (~1 min, 12 runs × 2 sims).

## The pair contract (what each simulator must match)

### LL vs reality

The LL must reproduce the trial data within its stated bands:

- **Cruise**: 25.5 / 28.8 / 32.3 spm → 7 / 7.5 / 8 kt (Rankov 2012 ch.7)
- **Sprint**: 44.5 spm → 8.2–8.4 kt (sea trials, ch.9)
- **Turns**: the F/G trial-turn families (F1–F6, G1–G5) within ±7 %
- **One-oar**: mean handle force ≈ 210–225 N; catch-flip inertia spike

These are tested in `ll/tests/test_gate*.py` (8 gates).

### HL vs LL

The HL must agree with the LL on:

- Mean speed over a 10-min script: within 1 %
- Settled stroke rate: within 1 spm
- Time to 3 nautical miles: within 1 %
- Turn diameters (G1, F1): within 5 %
- Crew fatigue (W'): within 5 %
- Final position after course changes: within ~0.1 NM
- Path gap (mean per-sample separation): within 0.1 NM

Every HL result carries its tolerance source ("±X% of LL, calibration
run #N"). These are tested in `harness/tests/`.

### The honesty rule

The HL stays loose only where documented (in `docs/VALIDATION.md §9.3`).
It is never hand-tuned to match its own old output — when the LL changes,
the HL is re-calibrated to the LL's new truth.

## Calibration (how the HL gets its curves)

`hl/calibrate.py` runs a standard set of LL scenarios and writes the
results to `hl/calibration/calib_<id>.json`. The latest file is always
symlinked as `latest.json`.

The measured tables include: speed vs stroke rate, pressure effects,
hold/back modes, W' drain/refill, turn diameters at various helm angles,
drift angles, and time constants for the approach/decay curves.

After any LL change:
1. Run `$V hl/calibrate.py` (generates new curves, ~4 min)
2. Run `$V harness/run_validation.py` (checks HL vs LL)
3. Run `$V -m pytest` (full suite)
4. Commit the new calibration file

The calibration file is committed (deterministic — same LL = same curves).

## Layout detail

```
commands/    schema + script parser
common/      chain.py — shared constants (the single source of truth)
ll/          the LL simulator
  blade.py       flat-plate blade force law
  oar.py         one-oar kinematics + cycle averages
  ship.py        170-oar ship (surge + sway + yaw)
  clarke.py      Clarke hull damping module (kept for reference, not wired)
  rower.py       crew physiology (W' energy, fatigue)
  tests/         per-gate acceptance suites
hl/          the HL simulator
  ship.py        the whole simulator (same command API as LL)
  curves.py      calibration loader + bootstrap
  calibrate.py   machine calibration from LL
  calibration/   committed calibration files
  run_hl.py      demo runner
  tests/         HL basics
harness/     the pair comparison harness
  script.py      runs both sims on one command stream
  comparator.py  Level-2 metrics + equivalence table
  run_validation.py  the script set + turn scenarios
  tests/         equivalence gates
ui/          browser replay UI
  dump.py        generates telemetry logs
  viewer.html    self-contained viewer (vanilla JS + SVG)
  serve.py       stdlib HTTP server
  logs/          committed replay logs
docs/        VALIDATION.md (acceptance record)
             CALIBRATION.md (tuning ledger)
             next-steps.md (open work)
             completed-work.md (verdict ledger)
```

## Conventions

- **No duplicated numbers**: every constant comes from `common/chain.py`.
  A new constant lands in research first, then chain.py exports it.
- **Fail-fast scripts**: unknown verbs or out-of-range arguments raise
  `ScriptError` with the line number, before any simulation runs.
- **Deterministic**: fixed time step (dt), seeded RNG, logged command
  stream. The same script always produces the same output.
