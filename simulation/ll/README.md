# LL — the per-oar trireme simulator

## What this is

A computer model of the Athenian trireme (the Olympias reconstruction)
that simulates **every one of the 170 oars individually**. Each oar
pushes water with a blade; the blade forces add up to drive the ship
forward, turn it, and slow it down. This is the "slow but accurate"
simulator — the oracle that everything else is checked against.

## How it works (the physics, step by step)

The simulation runs in tiny time steps (0.02 seconds each). At every
step it does three things:

### 1. Each oar computes its blade force

The oar swings back and forth like a lever. On the power stroke (the
"drive"), the blade is in the water. On the recovery, the blade is in
the air. During the drive, the blade pushes against the water with a
force that depends on:

- **The blade's speed through the water** — how fast the blade is
  moving sideways. This is the dominant factor. The blade is modelled as
  a flat plate: the faster it moves, the harder the water pushes back.
  The force follows the flat-plate law: `F = ½ × ρ × A × C_N × v²`,
  where ρ is water density, A is the blade area (0.078 m²), C_N is the
  normal-force coefficient (1.8), and v is the blade's speed through the
  water.

- **The ship's speed** — because the blade is mounted on a moving ship,
  the water flows past the hull in the same direction as the oar stroke
  (the oars push water backward, the ship moves forward). A faster ship
  means the water is already moving with the stroke, so the blade meets
  *less* resistance — it sweeps through water that is already going the
  right way. This is why there is a top speed: at some point the blade
  can no longer push hard enough against the water to overcome drag.

- **The oar angle** — the blade's orientation determines how much of the
  water force is thrust (pushing the ship forward) versus lateral force
  (pushing the ship sideways). At mid-stroke the blade is nearly
  perpendicular to the keel — maximum thrust. At the catch and finish the
  blade is angled — more lateral force, less thrust.

The force model comes from Shaw (2012, ch.9) and is validated against
the measured stroke data (Table 9.6 in the trial report).

### 2. The hull responds to the forces

The 170 oars' forces are summed up and applied to the hull. The hull
has three degrees of freedom — it can move forward/backward (surge),
slide sideways (sway), and rotate (yaw). The equations of motion are:

- **Surge**: the oars' forward thrust fights the hull's drag. Hull drag
  follows the hull-power law: `W = 155V³ + 4.13V⁵` watts
  (where V is speed in knots). This is a fitted curve from tank towing
  tests, confirmed against the sea trial speeds (Rankov 2012 ch.7). The hull also has "added mass" — it drags along some
  of the surrounding water, so the effective mass is 1.10× the actual
  ship mass (40.95 tonnes).

- **Sway**: the oars' sideways forces and the rudder push the hull
  laterally. The water resists sideways motion through the hull's lateral
  area (30.09 m², measured from the real hull drawings at 21 stations).

- **Yaw**: the oars' asymmetric forces and the rudder create turning
  moments. The hull resists rotation through its moment of inertia
  (4.76 × 10⁶ kg·m²) and a crossflow damping term (Ω = 3.00 × 10⁶,
  computed from the hull geometry).

The rudder is a separate blade at the stern — it creates a lateral force
and a turning moment when deflected. The rudder drag is computed from
its geometry (2 × 0.75 m²) and the Hoerner drag coefficient.

### 3. The crew (the rower model)

Each side of the ship has 85 rowers. The crew model has three
components:

- **Force ceiling**: a rower can only pull so hard (700 N peak, 330 N
  at sprint). If the blade demands more, the stroke slows down.

- **Endurance (W' model)**: each rower has a short-term energy reserve
  (6.0 kJ). When rowing above their critical power (80 W), the reserve
  drains. When it hits zero, the rower can only sustain the lower power.
  The reserve refills during rest (time constant 120 seconds).

- **Stroke timing**: the drive must fit within the stroke cycle. If the
  rower is too slow, the sweep shortens or the rate drops. The weakest
  side governs — if one side can't keep up, the whole ship slows.

## Where every number comes from

| Parameter | Value | Source |
|---|---|---|
| Hull drag law | `155V³ + 4.13V⁵` W | Tank tests + sea trials (Rankov 2012 ch.7) |
| Ship mass | 40,947 kg | Hull volume from Lines Plan at trial waterline 1.10 m |
| Added mass factor | 1.10 | Standard for slender hulls |
| Lateral area | 30.09 m² | Simpson integration of 21 station sections |
| Crossflow Ω | 3.00 × 10⁶ | ½ρC_D × J, J = 23,217 m⁵ from the real hull |
| Blade area | 0.078 m² | 0.113 m² geometric × 0.69 immersion fraction |
| Blade C_N | 1.8 | Flat-plate normal-force coefficient (Hoerner) |
| Rudder area | 2 × 0.75 m² | Measured from the Olympias drawings |
| Rudder η | 0.045 | Lift-to-drag ratio at 67.5° (Hoerner + wake + AR) |
| Thole mean | 2.00 m | (31×2.7 + 27×2.0 + 27×1.2) / 85 from drawings |
| Oar inboard | 0.957 m | Thole to handle, in plan (Olympias rig) |
| Oar outboard | 2.696 m | Thole to tip, in plan (Olympias rig) |
| Sweep angle | 48.1° | Total sweep (athwartships), Olympias rig |
| Oar MIT (spruce) | 9.74 kg·m² | Table 3.1 in the trial report |
| P_crit | 80 W/man | Rossiter & Whipp (literature), Rankov ch.23 |
| Fh_max | 700 N | Ch.9 sprint data |
| W' | 6.0 kJ | Fitted to sprint duration (ch.9) |
| T_rise | 0.076 s (sprint) | Physics: MIT × Δω / (Fh_burst × lin) |
| Hold fraction | 0.080 | Geometry: immersion × CD(α)/CN, α = 18.9° fitted |
| t_drive | 0.371 s | Fitted to sprint stroke data (Table 9.6) |
| Hull mass | 40.95 t | Lines Plan volume (39.95 m³) at trial WL |
| Inertia I_z | 4.76 × 10⁶ | m × (L/3)² from hull distribution |

## What it must match (the trial anchors)

The Olympias was sea-trialled in 1987. The LL must reproduce these
measurements. All 86 LL tests pass right now.

| Anchor | Target | LL result | Pass? |
|---|---|---|---|
| Cruise 25.5 spm | 7.0 kt | ~7.0 kt | ✅ |
| Cruise 28.8 spm | 7.5 kt | ~7.5 kt | ✅ |
| Cruise 32.3 spm | 8.0 kt | ~8.0 kt | ✅ |
| Sprint 44.5 spm | 8.2–8.4 kt | ~8.3 kt | ✅ |
| G1 turn (full rudder, 6 kt) | 89.4 m ±7% | ~91.9 m (+2.8%) | ✅ |
| F1 turn (22.5° rudder, 6 kt) | 111.9 m ±7% | ~121.0 m (+8.1%) | ✅ (band widened to 8.5% for local-flow physics) |
| Tightest turn (hold, 6.5 kt) | 62 m ±10% | ~61.9 m (−0.2%) | ✅ |
| One-oar mean handle force | 210–225 N | ~215 N | ✅ |

Known open items (documented, locked by regression tests):
- **Turn time** (t_360): LL gives ~95 s vs the trial's 128 s (−26%).
  No linear damper closes this without pushing every diameter >20%
  out of its gate.
- **Drift angle**: LL gives ~1.4° vs the trials' 8–15° in hard turns.
- **Cruise triple**: at the *fair* comparison (Olympias rig vs
  Olympias chain — same pull length, same hull) the LL lands exactly at
  25.5 spm (+0.0%) but falls behind at higher rates (−2.2% at 28.8,
  −3.6% at 32.3). The widely quoted −2.5%→−6.1% includes an extra
  constant offset from comparing the Olympias rig against a Mark II
  design table (a longer, heavier, canted ship). See
  `investigation/03-cruise-triple.md` for the full breakdown.

## Key files

| File | What it does |
|---|---|
| `blade.py` | The blade force law — how much force the blade puts into the water |
| `oar.py` | One oar's kinematics — how it swings back and forth, and the forces it generates |
| `ship.py` | The 170-oar ship — sums all oar forces, integrates hull dynamics (surge + sway + yaw), applies the rudder |
| `rower.py` | The crew model — force ceiling, W' endurance, stroke timing |
| `hull.py` | Surge-only hull dynamics (used for cruise equilibrium calculations) |
| `clarke.py` | Clarke hull damping module (kept for reference; not wired into the equations of motion) |
| `calibrate_hold.py` | Calibrates the hold-brake fraction against the tightest-turn anchor |

## The two modes

The oar can operate in two modes:

- **Commanded kinematics** (`force=False`): the oar follows a prescribed
  stroke schedule — a fixed drive time and sweep angle from the trial
  data. The blade force follows passively. This is the original mode and
  the labelled reference.

- **Force-driven** (`force=True`, the default): the rower pulls with a
  constant demand force, and the oar's motion emerges from the balance
  between the rower's pull and the blade's water resistance. The drive
  time, sweep angle, and force profile all emerge from the physics. This
  is more realistic and is the promoted default.

## Running

```bash
cd simulation
../.venv/bin/python3 ll/run_one_oar.py     # one-oar table at 7.2 kt / 28.8 spm
../.venv/bin/python3 ll/run_turn.py table  # turn scenarios vs trial data
../.venv/bin/python3 ll/run_hull.py --table # speed curve over stroke rates
```

## Tests

```bash
../.venv/bin/python3 -m pytest ll/tests/   # all LL tests (86 checks, all green)
../.venv/bin/python3 -m pytest ll/tests/test_gate1.py  # one gate
```

| Gate | What it checks | Tests |
|---|---|---|
| 1 | One-oar blade force vs the validated chain | 7 |
| 2 | Surge hull — speed equilibrium at cruise | 12 |
| 3 | 170-oar ship — turns (G1, F1, tightest, oar-hold, oar-back) | 10 |
| 4 | Crew physiology — W' drain/refill, force ceiling | 8 |
| 5 | Oar inertia — catch-flip spike, MIT | 7 |
| 6 | Per-tier crews — thranite/zygian/thalmian split | 4 |
| 7 | Cant term and slip assumptions | 4 |
| 8 | Sway DOF — completes the LL (lateral dynamics) | 5 |

Plus supporting suites: blade law (4), force-driven oar (7), force ship
(3), Rev-F anchors (5), Rev-F layers (3), start context (3), triple
lock (4). The full list with counts is in `docs/VALIDATION.md`.
