# simulation — the two trireme models

Two computer models of the Olympias trireme. They share one command
language — the same script runs on both.

The evidence they must match is in `../research/README.md`.
The full acceptance record — every test, every result, every known gap —
is in [`docs/VALIDATION.md`](docs/VALIDATION.md).

## How the two models relate

```
                  ┌──────────┐
  command script →│   LL     │→ results (speed, position, forces)
                  │ (oracle) │
                  └──────────┘
                       │
                       │  builds the HL's lookup tables
                       ▼
                  ┌──────────┐
  command script →│   HL     │→ results (same format as LL)
                  │  (fast)  │
                  └──────────┘
                       │
                       │  harness compares
                       ▼
                  ┌──────────┐
                  │ agreement│→ pass or fail per test
                  │  check   │
                  └──────────┘
```

**LL** (`ll/`): Simulates 170 individual oars with real blade forces.
Slow (minutes per run) but physically accurate. Must match trial data.

**HL** (`hl/`): Treats the ship as one object with lookup tables (speed
at each stroke rate, turn size at each helm angle, and so on). Fast
(seconds per run). Its tables are made automatically from LL runs — never
edited by hand.

**Harness** (`harness/`): Runs the same script on both models and checks
they agree within set limits.

## Command language

Scripts are one command per line. `#` lines are comments. Format:
`<time_s> <verb> [args...]`

Four verbs:

| Verb | What it does | Example |
|---|---|---|
| `rate` | Set the stroke rate (strokes per minute) for the whole ship | `30 rate 28.8` |
| `oars` | Set what the oars are doing (per side or both) | `60 oars hold port` |
| `pressure` | Set how hard the crew pulls (per side or both) | `0 pressure steady` |
| `helm` | Set the steering oar angle | `0 helm port 1.0` |

Shorthand for rates: `slow` (24), `working` (30), `racing` (44).
Oar states: `row` (normal rowing), `hold` (blades held still as brakes),
`back` (rowing backwards), `bank` (oars lifted out of the water).
Effort levels: `rest`, `steady`, `fast`, `spoude` (all-out burst).

Full-rudder turn:
```
0 helm port 1.0        # hard to port, full rudder
0 rate 30
0 pressure steady
```

Tightest turn (one side holds water, other rows):
```
0 oars hold starboard   # starboard blades held as brakes
0 rate 44
0 pressure spoude
0 helm starboard 1.0
```

The full rules are in `commands/schema.json`.

## Running things

All commands from the `simulation/` folder. Python is always
`.venv/bin/python3` (from `simulation/`, that's `../.venv/bin/python3`).

### Tests

```bash
V=../.venv/bin/python3
$V -m pytest                       # all tests
$V -m pytest -v                    # with test names
$V -m pytest ll/tests/test_gate5.py  # one group of tests
```

How many tests and what each group checks is in `docs/VALIDATION.md`.

### LL runners

```bash
$V ll/run_one_oar.py               # one-oar table at 7.2 kt / 28.8 spm
$V ll/run_turn.py table            # turn scenarios vs trial data
$V ll/run_hull.py --table          # speed curve over stroke rates
```

### HL runners

```bash
$V hl/run_hl.py --turn table       # fast model turn scenarios
$V hl/calibrate.py                 # rebuild HL lookup tables from LL (~4 min)
```

### Harness

```bash
$V harness/run_validation.py       # HL vs LL comparison tables
```

### Replay in the browser

```bash
$V ui/serve.py                     # opens in your browser — replays computed runs
```

Nothing to install. The viewer is a single web page. After any LL or HL
change, rebuild the replay data: `$V ui/dump.py` (~1 min, 12 runs × 2 models).

## What each model must match

### LL vs the real trials

The LL must reproduce what was measured at sea, within set limits:

- **Cruising**: 25.5 / 28.8 / 32.3 strokes/min → 7 / 7.5 / 8 knots
  (Rankov 2012 ch.7)
- **Sprint**: 44.5 strokes/min → 8.2–8.4 knots (trials, ch.9)
- **Turns**: the F/G trial turn families (F1–F6, G1–G5) within ±7%
- **One oar**: average handle force about 210–225 newtons; the sharp
  force spike when the oar flips at the catch

These are checked in `ll/tests/test_gate*.py` (8 groups).

### HL vs the LL

The HL must agree with the LL on:

- Average speed over a 10-minute script: within 1%
- Stroke rate: within 1 stroke/min
- Time to cover 3 nautical miles: within 1%
- Turn sizes (G1, F1): within 5%
- Crew energy (W'): within 5%
- Final position after course changes: within 0.1 nautical miles
- Path shape (average gap between the two tracks): within 0.1 nautical miles

Every HL result notes which LL run it was checked against.
These are checked in `harness/tests/`.

### Keeping it honest

The HL is only allowed to be loose where `docs/VALIDATION.md §9.3`
says so. It is never hand-tuned to match old output — when the LL
changes, the HL is rebuilt from the LL's new numbers.

## Calibration (how the HL gets its tables)

`hl/calibrate.py` runs a set of LL scenarios and saves the results to
`hl/calibration/calib_<id>.json`. The newest file is always linked as
`latest.json`.

The tables cover: speed at each stroke rate, how effort level changes
speed, what happens when one side holds water, how fast the crew tires
and recovers, turn sizes at each helm angle, sideways drift, and how
quickly the ship speeds up or slows down.

After any LL change:
1. Run `$V hl/calibrate.py` (makes new tables, ~4 min)
2. Run `$V harness/run_validation.py` (checks HL vs LL)
3. Run `$V -m pytest` (full test suite)
4. Commit the new calibration file

The calibration file is saved in the repo — same LL always gives same
tables.

## What's in each folder

```
commands/    the command language (rules + script reader)
common/      chain.py — shared numbers (the single source of truth)
ll/          the LL model
  blade.py       blade force law (how the blade pushes water)
  oar.py         one oar's motion and forces
  ship.py        the 170-oar ship (forward + sideways + turning)
  experimental_coupling.py  heel+drag spike (OFF by default, step 3)
  rower.py       the crew (how hard they pull, how they tire)
  tests/         tests for each group
hl/          the HL model
  ship.py        the whole model (same commands as LL)
  curves.py      table loader + defaults
  calibrate.py   builds tables from LL runs
  calibration/   saved calibration files
  run_hl.py      demo runner
  tests/         HL tests
harness/     the comparison harness
  script.py      runs both models on one script
  comparator.py  comparison numbers + pass/fail table
  run_validation.py  the full script set + turn checks
  tests/         comparison tests
ui/          browser replay
  dump.py        makes the replay data
  viewer.html    the viewer (plain web page)
  serve.py       a tiny web server
  logs/          saved replay data
docs/        VALIDATION.md (what passes, what doesn't, and why)
             CALIBRATION.md (tuning notes)
             next-steps.md (what's still to do)
             completed-work.md (what's done)
```

## Rules

- **One copy of every number**: every constant comes from `common/chain.py`.
  A new number goes into the research first, then into chain.py.
- **Bad scripts fail fast**: unknown commands or bad arguments raise an
  error with the line number, before anything is simulated.
- **Same input → same output**: fixed time step, seeded random numbers,
  logged commands. The same script always gives the same answer.
