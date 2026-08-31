# LL — the per-oar trireme model

A computer model of the Olympias trireme that simulates **every one of
the 170 oars individually**. Each oar pushes water with a blade; the
blades add up to drive the ship forward, turn it, and slow it down. This
is the "slow but accurate" model — the reference that everything else is
checked against.

## How it works

The model runs in tiny time steps (0.02 seconds each). At every step it
does three things:

### 1. Each oar pushes water

The oar swings back and forth like a lever. On the power stroke (the
"drive"), the blade is in the water. On the recovery, the blade is in
the air.

During the drive, the blade pushes against the water. The force depends
on three things:

- **How fast the blade moves sideways** — the main factor. The blade
  is a flat plate: the faster it moves, the harder the water pushes
  back. The formula is `F = ½ × ρ × A × C_N × v²`, where ρ is water
  density, A is the blade area (0.078 m²), C_N is 1.8, and v is the
  blade's speed through the water.

- **How fast the ship is moving** — the blade sits on a moving ship,
  so the water already flows past the hull in the same direction as
  the stroke. A faster ship means the blade meets *less* resistance —
  it sweeps through water already going the right way. At some speed
  the blade can't push hard enough to overcome drag — that's the top
  speed.

- **The oar's angle** — at mid-stroke the blade faces straight
  backwards (maximum forward push). Near the catch and finish it is
  angled, so more of the force goes sideways.

The force model comes from Shaw (2012, ch.9) and matches the measured
stroke data in the trial report (Table 9.6).

### 2. The hull moves

The 170 oars' forces are added up and applied to the hull. The hull can
move in three ways — forward/backward (surge), sideways (sway), and
turning (yaw):

- **Surge** (forward): the oars' forward push fights the hull's drag.
  Hull drag follows `W = 155V³ + 4.13V⁵` watts (V in knots) — a curve
  fitted to tank towing tests and confirmed at sea (Rankov 2012 ch.7).
  The hull also drags along some surrounding water, so its effective
  mass is 1.10× the real ship mass (40.95 tonnes).

- **Sway** (sideways): the oars' sideways forces and the rudder push
  the hull sideways. The water resists this through the hull's sideways
  area (30.09 m², measured from the real hull drawings at 21 stations).

- **Yaw** (turning): uneven forces and the rudder make the hull turn.
  The hull resists turning through its spin inertia (4.76 × 10⁶ kg·m²)
  and a crossflow drag term (Ω = 3.00 × 10⁶, computed from the hull
  shape).

The rudder is a blade at the stern — it makes a sideways force and a
turning moment when tilted. Its drag comes from its size (2 × 0.75 m²)
and the Hoerner flat-plate formula.

### 3. The crew rows

Each side has 85 rowers. The crew model has three parts:

- **Force limit**: a rower can only pull so hard (700 newtons peak,
  330 at sprint). If the blade needs more, the stroke slows down.

- **Stamina (W' model)**: each rower has a short-term energy reserve
  (6.0 kilojoules). Rowing above 80 watts drains it; when it hits zero,
  the rower can only manage 80 watts. It refills during rest (about 2
  minutes to refill).

- **Stroke timing**: the power stroke must fit in the stroke cycle. If
  the rower is too slow, the sweep shortens or the stroke rate drops.
  The weaker side sets the pace — if one side can't keep up, the whole
  ship slows.

## Where every number comes from

| Number | Value | Source |
|---|---|---|
| Hull drag | `155V³ + 4.13V⁵` watts | Tank tests + sea trials (Rankov 2012 ch.7) |
| Ship mass | 40,947 kg | Hull volume from the Lines Plan at waterline 1.10 m |
| Added mass | 1.10× ship mass | Standard for slender hulls |
| Sideways area | 30.09 m² | Measured from 21 hull sections |
| Crossflow Ω | 3.00 × 10⁶ | ½ρC_D × J, J = 23,217 m⁵ from the real hull |
| Blade area | 0.078 m² | 0.113 m² geometric × 0.69 in-water fraction |
| Blade C_N | 1.8 | Flat plate (Hoerner) |
| Rudder | 2 × 0.75 m² | Measured from the Olympias drawings |
| Rudder efficiency | 0.045 | At 67.5° rudder (Hoerner + wake + shape effects) |
| Thole spacing | 2.00 m | Average from drawings: (31×2.7 + 27×2.0 + 27×1.2) / 85 |
| Oar inboard | 0.957 m | Pivot to handle, flat projection (Olympias rig) |
| Oar outboard | 2.696 m | Pivot to tip, flat projection |
| Sweep | 48.1° | Total swing, Olympias rig |
| Oar spin inertia | 9.74 kg·m² | Table 3.1 in the trial report (spruce oars) |
| Max sustainable power | 80 W per rower | Exercise research (Rossiter & Whipp, Rankov ch.23) |
| Max pull | 700 N | Sprint data, ch.9 |
| Energy reserve W' | 6.0 kJ per rower | Fitted to sprint length (ch.9) |
| Catch-flip time | 0.076 s (sprint) | Physics: inertia × speed change / (force × lever) |
| Hold-brake fraction | 0.080 | In-water fraction × drag ratio at 18.9° blade angle |
| Drive time | 0.371 s | Fitted to stroke data (Table 9.6) |

## What the model must match

The Olympias was sea-trialled in 1987. The LL must reproduce what was
measured. All current LL tests pass.

| What was measured | Target | What the LL gives | Result |
|---|---|---|---|
| Cruising at 25.5 strokes/min | 7.0 knots | about 7.0 knots | ✅ |
| Cruising at 28.8 strokes/min | 7.5 knots | about 7.5 knots | ✅ |
| Cruising at 32.3 strokes/min | 8.0 knots | about 8.0 knots | ✅ |
| Sprint at 44.5 strokes/min | 8.2–8.4 knots | about 8.3 knots | ✅ |
| G1 turn (full rudder, 6 knots) | 89.4 m (±7%) | about 91.9 m (+2.8%) | ✅ |
| F1 turn (22.5° rudder, 6 knots) | 111.9 m (±8.5%) | about 121 m (+8%) | ✅ |
| Tightest turn (one side holds, 6.5 knots) | 62 m (±10%) | about 61.9 m | ✅ |
| Average handle force | 210–225 newtons | about 215 newtons | ✅ |

### Known gaps (the model doesn't match here yet)

These are real differences between the model and the trials. Each is
documented and has a test that locks the current value so it can't
silently get worse.

- **360° turn time**: the model takes about 95 seconds; the trials took
  128 seconds (−26%). The model's turn is the right size but too fast.
  No simple drag tweak closes the gap without breaking other tests.

- **Sideways lean (drift)**: in a hard turn the model's hull leans
  1–2° sideways; the trials measured 8–15°. The trials reported two
  numbers for the same turns (15° and 7.8°); the model gives about 1.6°
  either way it is measured — about 5× less than even the lower trial
  number.

- **Cruising at high stroke rates**: at the *fair* comparison (Olympias
  rig tested against Olympias numbers — same oar length, same hull) the
  model lands exactly at 25.5 strokes/min but falls behind at higher
  rates (−2.2% at 28.8, −3.6% at 32.3). The often-quoted −6% comes from
  testing the Olympias rig against a different ship's design table (a
  longer, heavier, tilted-oar ship) — that adds a constant offset.

## Files

| File | What it does |
|---|---|
| `blade.py` | How the blade pushes water |
| `oar.py` | One oar's swing and forces |
| `ship.py` | The 170-oar ship (adds up oar forces, moves the hull, steers) |
| `rower.py` | The crew (force limit, stamina, stroke timing) |
| `hull.py` | Forward-only hull motion (for cruising calculations) |
| `clarke.py` | An alternative hull model (kept for reference, not used) |

## Two ways to row

The oar has two modes:

- **Scheduled** (`force=False`): the oar follows a fixed timetable — a
  set drive time and sweep angle from the trial data. The blade force
  follows from the motion.

- **Force-driven** (`force=True`, the default): the rower pulls with a
  set force and the oar's motion comes from the balance between the
  pull and the water resistance. More realistic — the drive time and
  sweep emerge from the physics.

## Running

```bash
cd simulation
../.venv/bin/python3 ll/run_one_oar.py     # one-oar table at 7.2 kt / 28.8 spm
../.venv/bin/python3 ll/run_turn.py table  # turn scenarios vs trial data
../.venv/bin/python3 ll/run_hull.py --table # speed curve over stroke rates
```

## Tests

```bash
../.venv/bin/python3 -m pytest ll/tests/   # all LL tests (all should pass)
../.venv/bin/python3 -m pytest ll/tests/test_gate1.py  # one group
```

| Group | What it checks | Tests |
|---|---|---|
| 1 | One-oar blade force | 7 |
| 2 | Forward hull — speed at cruise | 12 |
| 3 | 170-oar ship — turns (G1, F1, tightest, hold, back) | 10 |
| 4 | Crew stamina — energy drain/refill, force limit | 8 |
| 5 | Oar spin inertia — catch spike, handiness | 7 |
| 6 | Per-tier crews (upper/middle/lower tier differences) | 4 |
| 7 | Tilted-oar and slip effects | 4 |
| 8 | Sideways motion — the full 3-direction hull | 6 |

Plus: blade law (4), force-driven oar (7), force ship (3), trial
anchors (5), per-station oar layout (3), start from rest (3), cruise
triple lock (7). The full list with counts is in `docs/VALIDATION.md`.
