# HL — the fast trireme simulator

## What this is

A fast, simplified model of the same trireme. Instead of simulating 170
individual oars (which takes minutes), it treats the ship as **one
object** with pre-measured response curves. It runs in seconds.

The HL answers the same questions as the LL (how fast? how far? how
tight does it turn?) but uses lookup tables instead of physics. Those
tables are **generated automatically** from LL runs — never hand-edited.

## Why two simulators?

The LL is accurate but slow. The HL is fast but approximate. The pair
lets you:

- Run long scenarios quickly (HL) while knowing the physics are right (LL)
- Validate the HL against the LL so you can trust it
- Explore parameter space in minutes instead of hours

## How it works (the idea)

Think of the HL as a ship with a set of pre-measured performance charts:

- **Speed chart**: "at this stroke rate and pressure, the ship goes this
  fast" — measured by running the LL at each rate until it settles
- **Turn chart**: "at this helm angle, the ship turns with this diameter"
  — measured by running the LL in a steady turn at each angle
- **Fatigue chart**: "at this power level, the crew's energy reserve
  drains at this rate" — measured from short LL burst-and-rest runs
- **Approach constants**: "when you change the rate, the speed catches
  up with this time constant" — measured from the LL's rest-start
  transient

When you give the HL a command, it looks up the charts and applies
simple first-order dynamics — no oar physics, no blade forces, just
"the speed chases the chart value with a time constant of 20 seconds."

## The calibration (how the charts are made)

`calibrate.py` runs a standard set of LL scenarios and records the
results into a JSON file (`calibration/calib_<date>.json`). The process:

1. **Speed vs rate**: run the LL at 8–50 spm, measure the settled speed
   at each rate. This gives the V* curve.
2. **Pressure effects**: run at steady (0.7) and fast (0.85) pressure,
   measure the speed reduction at each rate.
3. **Hold/back modes**: run with one side holding water, measure the
   asymmetric speed and the turn diameter at various helm angles.
4. **Fatigue**: run short burst/rest cycles, measure how fast W' drains
   at each power level and how fast it refills.
5. **Turn diameters**: run steady turns at each helm fraction, measure
   the diameter for both the rudder family (both sides rowing) and the
   oar family (one side holding).
6. **Approach constants**: measure how long it takes the speed to settle
   after a rate change (tau_surge) and how long a turn takes to build
   (tau_turn).
7. **Drift**: measure the small steady yaw bias from the crew's
   asymmetry at each rate/pressure.

The calibration file is committed to the repo (deterministic — same LL
= same charts). It takes about 4 minutes to regenerate.

## What the HL knows (and what it doesn't)

**What's in the charts:**
- Equilibrium speed at every rate and pressure
- Turn diameter at every helm angle (rudder and oar families)
- W' drain/refill rates at every power level
- Approach time constants (tau_surge, tau_turn)
- Drift bias at every rate/pressure
- The tempo loss curve (exhausted crew can't hold the rate)

**What the HL doesn't model (honest loose spots):**
- Stroke-by-stroke force variation (the ripple in the LL's speed)
- Per-side W' tanks (the HL uses one shared tank; the LL has two)
- Sway dynamics in turns (the LL models lateral velocity; the HL
  folds it into the calibrated diameter)
- The catch-flip inertia spike (a per-stroke transient the LL captures)
- Per-oar blade forces (the HL has none — that's the whole point)

Each loose spot is documented and will only be revisited if a test
gate fails.

## The command language

The HL uses the **exact same command language** as the LL. A script
that runs on the LL runs identically on the HL:

```
0 helm port 1.0        # hard to port
0 rate 30
0 pressure steady
```

This makes the harness possible: run the same script on both sims,
compare the outputs.

## Where every number comes from

The HL has **no hardcoded physics**. Every number comes from one of
two sources:

1. **The calibration file** (`calibration/calib_*.json`) — generated
   from LL runs. This is the primary source.

2. **The bootstrap** (`curves.py`) — provisional defaults used before
   the first calibration run. These are also measured from the LL, just
   committed as Python constants instead of JSON.

The HL imports a few constants from the shared chain (`chain.py`):
KT (knots-to-m/s), RHO (water density), CN (blade coefficient), and
the rig geometry. These are the same numbers the LL uses.

## Key files

| File | What it does |
|---|---|
| `ship.py` | The whole simulator — same command API as the LL's Ship class |
| `curves.py` | The response curves — bootstrap defaults + JSON loader |
| `calibrate.py` | Machine calibration from LL runs (~4 min, writes JSON) |
| `calibration/` | Committed calibration files (latest.json is the default) |
| `run_hl.py` | Demo runner — run scripts or turn scenarios |

## What the HL must match (vs the LL)

The HL is validated against the LL, not against reality directly.
The tolerances:

| Metric | Tolerance | What it means |
|---|---|---|
| Mean speed | ±1% over 10 min | The ship goes the right speed on average |
| Stroke rate | ±1 spm | The ship rows at the commanded rate |
| Time to 3 NM | ±1% | The ship covers distance at the right rate |
| Turn diameter (G1, F1) | ±5% | The ship turns the right size circle |
| Crew fatigue (W') | ±5% | The energy model tracks the LL's tank |
| Final position | ±0.1 NM | After course changes, the ship ends up in the right place |
| Path gap | ±0.1 NM | The path shape matches, not just the endpoint |

Every HL result carries its tolerance source: "±X% of LL, calibration
run #N."

## Running

```bash
cd simulation
../.venv/bin/python3 hl/run_hl.py --turn table    # turn scenarios
../.venv/bin/python3 hl/run_hl.py script.txt      # run a script
../.venv/bin/python3 hl/calibrate.py              # regenerate charts (~4 min)
```

## Tests

```bash
../.venv/bin/python3 -m pytest hl/tests/   # HL basics
```

The HL's main validation is through the harness (`harness/`), which
runs the same script on both sims and checks agreement. See
`harness/README.md` for details.
