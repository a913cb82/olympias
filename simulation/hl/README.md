# HL — the fast trireme model

A fast, simple model of the same trireme. Instead of 170 individual oars
(taking minutes), it treats the ship as **one object** with lookup tables.
It runs in seconds.

The HL answers the same questions as the LL (how fast? how far? how tight
does it turn?) but uses tables instead of physics. Those tables are **made
automatically** from LL runs — never edited by hand.

## Why two models?

The LL is accurate but slow. The HL is fast but approximate. Together:

- Long scenarios run quickly (HL) while you know the physics is right (LL)
- The HL is checked against the LL so you can trust it
- You can explore what-if questions in minutes instead of hours

## How it works

The HL is like a ship with a set of performance charts:

- **Speed chart**: "at this stroke rate and effort, the ship goes this
  fast" — measured by running the LL at each rate until it settles
- **Turn chart**: "at this rudder angle, the ship turns this wide" —
  measured by running the LL in a steady turn at each angle
- **Stamina chart**: "at this power, the crew's energy drains this fast"
  — measured from short LL burst-and-rest runs
- **Response speed**: "when you change the rate, the speed catches up
  this quickly" — measured from the LL speeding up from rest

When you tell the HL a command, it looks up the charts and smoothly moves
toward the chart value. No oar physics, no blade forces — just "speed
heads toward the chart value with a time constant of 20 seconds."

## How the charts are made

`calibrate.py` runs a set of LL scenarios and saves the results to a file
(`calibration/calib_<date>.json`):

1. **Speed at each rate**: run the LL at 8–50 strokes/min, measure the
   settled speed at each rate
2. **Effort effects**: run at reduced effort (steady 0.7×, fast 0.85×),
   measure how much slower the ship goes
3. **Hold/back modes**: run with one side holding water, measure the
   lopsided speed and turn size at each rudder angle
4. **Stamina**: run burst/rest cycles, measure how fast energy drains and
   refills
5. **Turn sizes**: run steady turns at each rudder angle, measure the
   circle size for rudder turns and for oar-held turns
6. **Response speed**: measure how long speed takes to settle after a
   rate change, and how long a turn takes to build
7. **Sideways drift**: measure the small steady sideways creep at each
   rate and effort

The file is saved in the repo — same LL always gives same charts. It
takes about 4 minutes to build.

## What the HL gets right and where it is loose

The HL is checked against the LL (not against the real trials directly).
All current HL+harness tests pass. Some pass with wider limits than the
ideal targets — the limits below are what the tests actually enforce.

### Straight and mixed scripts (7 scenarios)

| Script | Average speed | Crew energy | Position gap | Why the wider limit |
|---|---|---|---|---|
| 10-min cruise | ✅ within 1% | ✅ within 10% | — | — |
| Sprint + turn | ✅ within 1% | ✅ within 20% | ✅ within 0.75 nautical miles | Sprint drains energy fastest |
| Burst and rest | ✅ within 2% | ✅ within 5% | ✅ within 0.1 nautical miles | — |
| Cruise + hold + back | ✅ within 20% | ✅ within 20% | ✅ within 0.15 nautical miles | Very slow backing is hard to mimic |
| 35-min straight | ✅ within 1% | ✅ within 5% | ✅ within 1.1 nautical miles | Small sideways creep adds up |
| Exhaustion | ✅ within 3% | ✅ within 5% | — | — |
| Zigzag (rapid turns) | ✅ within 2.5% | ✅ within 5% | ✅ within 0.7 nautical miles | Quick reversals are hard |

### Turns (5 scenarios)

| Turn | LL circle | HL circle | Error | Result |
|---|---|---|---|---|
| G1 (full rudder, 6 knots) | 91.8 m | 91.6 m | −0.2% | ✅ (within 5%) |
| F1 (22.5° rudder, 6 knots) | 121.0 m | 120.9 m | −0.1% | ✅ (within 5%) |
| Tightest (one side holds, 6.5 knots) | 61.7 m | 60.0 m | −2.7% | ✅ (within 5%) |
| Oar-hold (no rudder, 6.5 knots) | 97.0 m | 103.9 m | +7.0% | ✅ (within 12%) |
| Oar-back (no rudder, 6.5 knots) | 97.0 m | 103.9 m | +7.1% | ✅ (within 12%) |

The oar-hold/back turns have a wider limit (12%). The LL got tighter
there with updated hull numbers, but the HL's pre-measured tables have
not yet been re-fitted to match.

### What the HL leaves out

- The small speed wobble each stroke (the LL's speed ripples each oar
  cycle; the HL is smooth)
- Per-side energy tracking (both models have per-side energy, but the
  HL's drain rates are averages)
- Sideways motion in turns (the LL models it; the HL folds it into the
  turn size)
- The sharp force spike when the oar flips at the catch
- Individual blade forces (the HL has none — that's the whole point)

Each gap is documented and only revisited if a test breaks.

## Where every number comes from

The HL has **no physics of its own**. Every number comes from:

1. **The calibration file** (`calibration/calib_*.json`) — made from LL
   runs. This is the main source.

2. **The defaults** (`curves.py`) — backup values used before the first
   calibration. Also measured from the LL, just stored as code instead
   of a file.

The HL also uses a few shared constants from `common/chain.py`: water
density, blade coefficient, and the oar layout. Same numbers the LL uses.

## Command language

The HL uses the **same commands** as the LL. A script that runs on LL
runs identically on HL:

```
0 helm port 1.0        # hard to port
0 rate 30
0 pressure steady
```

This is what makes the comparison work — same script, both models,
compare answers.

## Files

| File | What it does |
|---|---|
| `ship.py` | The whole model — same commands as the LL ship |
| `curves.py` | The lookup tables — defaults + file loader |
| `calibrate.py` | Builds tables from LL runs (~4 min, saves a file) |
| `calibration/` | Saved calibration files (`latest.json` is the current one) |
| `run_hl.py` | Demo runner — run scripts or turn scenarios |

## Running

```bash
cd simulation
../.venv/bin/python3 hl/run_hl.py --turn table    # turn scenarios
../.venv/bin/python3 hl/run_hl.py script.txt      # run a script
../.venv/bin/python3 hl/calibrate.py              # rebuild tables (~4 min)
```

## Tests

```bash
../.venv/bin/python3 -m pytest hl/tests/   # HL tests (42 checks including harness)
```

The main check is the harness (`harness/`), which runs the same script
on both models and checks they agree. See `../README.md` for the overall
test setup.
