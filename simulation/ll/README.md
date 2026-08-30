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
  the water flow past the blade includes the ship's own speed. A faster
  ship means more water flow, which means the blade meets more resistance.

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
  follows the trial-validated power law: `W = 155V³ + 4.13V⁵` watts
  (where V is speed in knots). This law was measured in tank tests and
  confirmed at sea. The hull also has "added mass" — it drags along some
  of the surrounding water, so the effective mass is 1.10× the actual
  ship mass (41.0 tonnes).

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
| Oar inboard | 1.092 m | Measured from the Olympias rig |
| Oar outboard | 2.738 m | Measured from the Olympias rig |
| Sweep angles | 48.1° / 48.4° / 55.6° | Per-tier from the rig geometry |
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
measurements:

- **Cruise speeds**: 25.5 / 28.8 / 32.3 spm → 7.0 / 7.5 / 8.0 kt
  (Rankov 2012 ch.7)
- **Sprint**: 44.5 spm → 8.2–8.4 kt (ch.9, measured 8.2–8.3)
- **Turn diameters**: the F/G trial-turn families within ±7% (the two
  families of turns recorded in the sea trials)
- **One-oar forces**: mean handle force ≈ 210–225 N at cruise

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
../.venv/bin/python3 -m pytest ll/tests/   # all LL gates (8 suites)
../.venv/bin/python3 -m pytest ll/tests/test_gate1.py  # one gate
```

Gate 1: the oar at cruise. Gate 2: surge-only hull. Gate 3: 170-oar
ship turns. Gate 4: crew physiology. Gate 5: oar inertia. Gate 6:
hull grounding (real geometry). Gate 7: grounded chain. Gate 8:
cross-flow calibration. The full list with counts is in
`docs/VALIDATION.md`.
