# Investigation 07 — Ship vs hull.py on Straight Cruise

## Why this exists

The goal is one code path: every LL test should run through `Ship`, not
through the separate `hull.py` surge-only hull. `hull.py` would then be
deleted (and `clarke.py`, already unwired, alongside it). The question:
can `Ship` do what `hull.py` does?

## What hull.py tests

Gate 2 asks: "at steady rowing, what speed does the ship settle at?"
The reference is the mean-force equilibrium `170 × T̄(V) = D(V)` — bare
blade thrust vs hull drag, no crew, no stamina. At 28.8 spm the answer
is 7.22 kt (the Table 9.6 / S6 anchor, within 0.3% of the measured
7.2 kt). This is a BURST speed — what the blades can push if the crew
pulls steadily at that rate.

## What Ship does at the same rates

Ship at 28.8 spm (default `spoude` = full burst) accelerating from rest:

```
t=10s  V=5.91  W_thran=0.92  (burst, still have energy)
t=30s  V=6.64  W=0.75
t=60s  V=6.61  W=0.49  (peak — never reaches 7.22)
t=120s V=6.59  W=0.00  (exhausted, now at P_crit)
t=300s V=6.15  W=0.00  (settled, sustainable on P_crit alone)
```

Three speeds for the same rate, three different concepts:

| Speed | hull.py (bare) | Ship burst (60s peak) | Ship settled (W' drained) |
|---|---|---|---|
| 28.8 spm | 7.22 kt | 6.82 kt (−5.6%) | 6.06 kt (−16%) |
| 32.3 spm | 7.58 kt | 7.08 kt (−6.6%) | 6.13 kt (−19%) |
| 36.0 spm | 7.99 kt | 7.27 kt (−8.9%) | 6.13 kt (−23%) |
| 44.5 spm | 8.55 kt | 7.57 kt (−11%)  | 6.09 kt (−29%) |

Ship's BURST is 5–11% slow vs hull.py at every rate, and the gap grows
with rate. Ship's SUSTAINED (W' drained, P_crit only) is ~6.1 kt at every
rate — it cannot go faster sustainably at any rate.

## Why Ship is slow

Two causes, in order of size:

### Cause 1: W' drains at cruise (largest)

At 28.8 spm `spoude`, each thranite pulls ~124 W (p_ext). P_crit is
80 W. So the crew drains at 44 W/man. Over 60 s that is 2.6 kJ of the
6 kJ tank — visible in the W_frac trace above (0.92 at 10s → 0.49 at
60s → 0.00 at ~120s). Once W'=0 the rower is capped at P_crit, so thrust
drops and speed falls to the P_crit-limited ~6.1 kt.

At 36 spm the drain is even faster (higher p_ext). So higher rates
don't give much more speed — they just drain faster.

The trial says 28.8 spm → 7.2 kt was SUSTAINABLE (the 3-hour wave
watch, the table's rates). In Ship at 28.8 spoude it is NOT sustainable
— W' drains in ~2 minutes. At `steady` pressure (0.7×) W' stays full
(stable), but speed is only 5.36 kt at 28.8 — far too slow.

So: spoude is too hot at cruise, steady is too cold. Neither gives
7.2 kt sustainably.

### Cause 2: Thalmian power factor 0.9 (smaller, constant)

At low rate the thalmian tier is set to 90% power (head-room limit:
beams above their heads are 10% closer than the oar spacing — they hit
their heads at the stroke ends). This removes 10% of 54/170 = 3.2% of
total thrust. At 7.22 kt that is 93 N, shifting equilibrium down by
~0.1 kt. Real but not the main cause.

Measured: at Ve=3.71 m/s and rate 28.8, thranite/zygian plan thrust is
17.21 N/oar, thalmian is 15.49 (scaled by 0.9). Total Ship thrust at
that speed is 164.6 × thrust_per_oar vs hull.py's 170 × — a 3.2% gap.
The remaining ~2–8% of the burst gap is the force-model / W' interaction.

### What else is NOT the cause

- `fleet=None` (massless oars) gives 6.90 vs 7.22 — still 4.4% slow.
  So oar inertia is not the main cause.
- `force=True` vs `False` (force-driven vs kinematic) gives 6.42 vs
  6.14 — 4.6% apart. The force model's demand geometry vs the kinematic
  schedule is a real difference but not the main cause at cruise.
- `t_drive` interpolation: at 28.8 it is exact (0.430 s from Table 9.6),
  so not an interpolation error at that rate.

## The connection to turn time

The trial's tightest turn entry is at 6.5 kt sprint (the 360° / 128 s
measurement). In the model the sprint at 44.5 spm bursts to ~7.6 kt but
quickly W'-drains toward ~6.1 kt. Through the turn the rowing side
continues draining — by 60s into the turn the rowing side's W' is
depleted (as seen above). The post-drain speed (~3.4 kt in the turn,
~6.1 kt straight) is set by P_crit, not the burst.

If W' drains too fast at cruise, it also drains too fast in the turn —
the rowing side exhausts early and thrust drops to the P_crit floor
too soon. But the turn's problem is that the floor is TOO HIGH (3.4 kt
vs trial's ~2.9 kt mean) — the ship doesn't slow enough. So the cruise
W' problem (Ship too slow at cruise because W' drains) and the turn
W' problem (Ship too fast in the turn because the P_crit floor is too
high) are opposite directions. Fixing one may worsen the other — or
they may share a cause in the thrust/drag calibration.

## What fixing would require

To make Ship match hull.py's cruise anchors when every test goes
through Ship:

1. **Reconcile the cruise stamina**: Either
   - Raise P_crit (80 → ~100 W?) so 28.8 spm spoude is sustainable;
   - Lower p_ext at cruise (the oar-loss model `0.96r + 0.016r²` may
     over-count at moderate rates);
   - Or accept that Gate 2's 7.2 kt anchor is a short-window burst,
     not a settled speed — Gate 2 should measure peak burst, not
     600s settle.

2. **Fix the per-rate thrust slope**: The burst gap grows with rate
   (5%→11%). This is the same blade/kinematics flatness as the
   cruise-triple investigation (07 vs 03) — the blade's E_eff drops
   with rate.

3. **Retire or re-baseline Gate 2**: If Gate 2 becomes a Ship test,
   its acceptance values move (28.8 spm: 7.22 → ~6.8 burst / ~6.1
   settled, depending on which is gated). The choice of which to gate
   changes the story the test tells.

## How to reproduce

```bash
# Ship burst vs hull.py at any rate
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship; from ll.hull import equilibrium_speed as hull_eq
from common.chain import KT
for rate in [28.8, 32.3, 36.0]:
    heq = hull_eq('Olympias', rate, hull=1.0)
    ship = Ship(rate=rate)
    ship.V = 0.5
    peak = 0
    for _ in range(int(60/0.02)):
        ship.step(0.02)
        peak = max(peak, ship.V)
    print(f'{rate}: hull.py {heq[\"V\"]/KT:.2f} Ship-peak {peak/KT:.2f}  {(peak-heq[\"V\"])/heq[\"V\"]*100:+.1f}%')
"

# Ship W' drain at cruise
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship; from common.chain import KT
ship = Ship(rate=28.8)
ship.V = 5.0*KT
for _ in range(int(300/0.02)):
    ship.step(0.02)
    if ship.t % 30 < 0.02:
        print(f't={ship.t:.0f} V={ship.V/KT:.2f} W_thr={ship.crew_p.tiers[\"thranite\"].W_frac:.2f}')
"
```
