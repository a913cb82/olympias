# Investigation 08 — Straight vs Turn Through the Same Code

## Why this exists

Straight-line cruising and turning used two separate code paths:

- **Straight**: `hull.py` — `170 × T̄(V) = D(V)` bisection with a bare
  `Oar`, no crew, no stamina. The burst answer: "what speed at this
  rate if the blades push that hard?" At 28.8 spm: **7.22 kt** (matches
  the trial's 7.2 kt ✅).

- **Turn**: `ship.py` — `Ship.hull_advance` with 170 crewed oars
  (per-tier power, W' stamina, force ceiling), sway (v), yaw (omega),
  rudder, and crossflow damping. The settled turn speed at the
  tightest sprint is ~3.4 kt (vs trial's ~2.9 kt mean — too fast, the
  95 s vs 128 s gap).

If the hull law, blade law, or drag is duplicated, a fix in one path
won't reach the other. The straight-vs-turn gaps may share a cause
(the same blade/hull mechanism), so they must use the same code.

## What changed

All forward-only helpers (`t_drive_for`, `drag_force`,
`equilibrium_speed`, `SurgeHull`, `run_cruise`) moved from `hull.py`
into `ship.py`. `hull.py` is deleted; `clarke.py` (tried and rejected —
100× too much damping for this slender hull) is also deleted.

One place for each physics:

| Physics | Code | Used by |
|---|---|---|
| Blade force | `ll/oar.py` + `ll/blade.py` (flat plate, `Fn = k·|vn|·vn`) | burst equilibrium, Ship |
| Hull drag | `common/chain.py` hull_power + `ship.py` drag_force | burst, Ship, calibration |
| Hull dynamics | `ship.py` Ship.hull_advance (3-DOF) + SurgeHull (1-DOF) | turns, Gates 3–8 |
| Stroke timing | `ship.py` t_drive_for (Table 9.6) | burst, Ship, rate_for_speed |

`SurgeHull` stays in `ship.py` as the straight-line special case:
`Ship` with `v = omega = 0`, same `m_app·dV/dt = N·F_oars − D(V)`.
Gate 2 asks "burst speed at this rate, no crew?" — that is
`equilibrium_speed` (bare-Oar bisection, same blade as Ship uses).
For "crewed straight cruise, with stamina?" — run a `Ship` symmetrically.

## What the numbers say now (all through ship.py)

| Rate | Burst V* (bare Oar, fresh) | Gate 2 anchor | Match |
|---|---|---|---|
| 25.5 spm | 6.89 kt | 7.0 kt (ch.7 Mark II) | −1.6% |
| 28.8 spm | **7.22 kt** | **7.2 kt (Table 9.6)** | **+0.3%** |
| 32.3 spm | 7.58 kt | 8.0 kt (ch.7 Mark II) | −5.3% |
| 36.0 spm | 7.99 kt | 8.2 kt (Table 9.6) | −2.7% |

The burst answers are unchanged — same physics, new home.

| Scenario | What Ship gives | Trial | Match |
|---|---|---|---|
| Straight 28.8 spm (burst, fresh) | 7.22 kt | 7.2 kt | ✅ |
| Straight 28.8 spm (sustained, 10 min) | ~6.1 kt | "sustainable"? | different question — see below |
| G1 turn (6 kt entry, full rudder) | 91.9 m | 89.4 m | +2.8% ✅ |
| Tightest sprint (6.5 kt entry) | D=61.9 m, t_360=95 s | D=62 m, t=128 s | D ✅, time −26% ❌ |
| Drift (G1) | 1.6° | 7.8–15° | 5–10× ❌ |

## Burst vs sustained — why Ship settles lower

At 28.8 spm `spoude` (full burst) each thranite pulls ~84 W (handle
power). P_crit is 80 W. So the crew drains at 4 W/man — slowly
(27 minutes to empty). But during the straight-line acceleration from
rest, V is lower, thrust is higher, power is higher, and W' drains
faster — the 60 s to reach cruise already costs ~half the tank.

After 10 minutes of burst rowing, W' is empty and the crew is capped
at P_crit — the ship settles to ~6.1 kt, the sustainable speed at
P_crit. This is EXPECTED: 7.2 kt at 28.8 spm spoude is a BURST, not a
forever speed (Rankov ch.7's 7.0–8.0 kt at 25.5–32.3 spm are Mark II
design numbers at hull×1.08, L=0.99 — a longer ship).

For sustainable cruise, use `spoude` at a lower rate or `steady`
pressure (0.7×) — or accept that 7.2 kt at 28.8 spm is the burst speed
Gate 2 tests, and the settled speed is a different question (Gate 4).

## Straight too fast, turn too fast — same cause?

Ship's straight burst is accurate (7.22 vs 7.2). In turns the ship is
too fast (3.4 kt settled vs trial's ~2.9 kt). The turn's settled speed
is set by: one side rowing vs hold brake + hull drag + rudder drag.
That balance is NOT the same as straight-line thrust vs drag — it
involves the brake fraction, crossflow yaw damping, and the one-side
thrust. A single fix (e.g., the blade producing more thrust at low V,
or the hull having less drag in turns) could affect both — but the
straight burst is already accurate, so any fix that helps turns must
not break it. The turn-specific knobs (brake, Omega, P_crit floor) are
where the turn time gap must be closed.

## For a new ship

All geometry-dependent physics (mass, lateral area, CLR, J, Omega,
blade area, rudder, oar layout) comes from the drawings
(`ship_drawings.py`). The hull/drag/blade law in `ship.py` reads from
`chain.py` — same code, different numbers. No duplicated constants.

## How to reproduce (all through ship.py)

```bash
# Burst equilibrium (Gate 2) — now in ship.py, not hull.py
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import equilibrium_speed
from common.chain import KT
for r in [25.5, 28.8, 32.3, 36.0]:
    eq = equilibrium_speed('Olympias', r, hull=1.0)
    print(f'{r} spm: {eq[\"V\"]/KT:.2f} kt')
"

# Straight vs turn, same Ship
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship, rate_for_speed, run_turn
from common.chain import KT
# Straight: burst equilibrium at 28.8
from ll.ship import equilibrium_speed
print('Straight burst:', equilibrium_speed('Olympias', 28.8, hull=1.0)['V']/KT)
# Straight: crewed ship from rest
s = Ship(rate=28.8); s.V = 0.5
for _ in range(int(600/0.02)): s.step(0.02)
print('Straight crewed (600s):', s.V/KT)
# Turn
R6 = rate_for_speed('Olympias', 6.0, n_oars=170)
print('G1 entry rate:', R6)
s = Ship(rate=R6, helm=('port',1.0)); s.V = 6.0*KT
print('G1 turn:', run_turn(s)['D'])
"
```
