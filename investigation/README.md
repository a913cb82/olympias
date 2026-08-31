# Investigation — three gaps between the model and the trials

The LL model matches most trial data. Three numbers don't match yet.
These notes explain each gap, what causes it, and what was tried.

| File | Question | Gap | Finding |
|---|---|---|---|
| [01](01-turn-time.md) | Why does the 360° turn take 95 s not 128 s? | −26% | The ship settles at 3.7 knots regardless of entry — 0.5 knots too fast. No single drag fix closes it. |
| [02](02-drift-angle.md) | Why is the sideways lean 1.4° not 8–15°? | 5–10× | Would need 5× less sideways area to match. Points to a missing sideways push (hull tilt, wind, etc.). |
| [03](03-cruise-triple.md) | Why is the speed-vs-rate curve flat? | Grows with rate | Half is a comparison mix-up (wrong ship's table); half is the blade losing efficiency at high rates. |
| [04](04-synthesis.md) | How do the three relate? | — | Fixing the lean could add drag that also slows the turn — one fix, two gaps. |
| [05](05-experiments.md) | What did we measure? | — | Raw numbers for every claim in 01–04 (all reproducible). |
| [06](06-step3-spike.md) | Does hull tilt fix lean + time? | Experiment | No — tilt at 1.6° is too small. Time CAN reach 128 s but breaks turn sizes. |

## How to reproduce the key numbers

```bash
# Cruise triple — fair vs mixed comparison
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.hull import equilibrium_speed
from common.chain import KT
for r in [25.5,28.8,32.3]:
    eq = equilibrium_speed('Olympias',r,hull=1.0)
    P=7.43*r; Wc=170*P*0.89*r*0.756/60
    lo,hi=0.5,6.0
    for _ in range(50):
        m=(lo+hi)/2
        W=155*m**3+4.13*m**5
        lo,hi=(m,hi) if W<Wc else (lo,m)
    Vc=(lo+hi)/2
    print(f'{r}: chain {Vc/KT:.2f} vs model {eq[\"V\"]/KT:.2f}  {(eq[\"V\"]-Vc)/Vc*100:+.1f}%')
"

# Turn time
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship; from common.chain import KT; import math
s=Ship(rate=44.5,oar_state=('row','hold'),helm=('starboard',1.0)); s.V=6.5*KT
ymax=0
while abs(s.psi)<2*math.pi: s.step(0.02); ymax=max(ymax,abs(s.y))
print(f'size={ymax:.1f}m  time={s.t:.0f}s  avg speed={math.pi*ymax/s.t/KT:.1f} knots')
"

# Sideways lean — try different hull areas
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship; from ll.ship import rate_for_speed
from common.chain import KT, A_LAT_TRIAL; import math
for f in [1.0,0.5,0.3,0.2]:
    s=Ship(rate=rate_for_speed('Olympias',6.0,n_oars=170),helm=('port',1.0)); s.V=6.0*KT
    s.vessel.A_lat=A_LAT_TRIAL*f
    for _ in range(int(60/0.02)): s.step(0.02)
    print(f'area x{f}: lean={math.degrees(math.atan2(s.v,s.V)):.1f}°  turn={2*abs(s.V)/abs(s.omega):.0f}m')
"
```

## Main takeaways

1. **Turn time**: the settled speed is stuck at ~3.7 knots no matter how
   the turn starts. Adding drag tightens the turn as it lengthens time —
   at most 112 seconds with a tired crew, still 16 short. The lean and
   hull-tilt drag together might help but are unmeasured.

2. **Sideways lean**: needs a sideways area of ~6 m² to get 8.5° vs the
   real 30.09 m². The lean is the small leftover between two large
   opposing forces (hull resistance vs the need to turn) — anything that
   adds a sideways push could shift it. Turns still pass at any area;
   the gap is isolated.

3. **Cruising at high stroke rates**: the model lands perfectly at low
   rate (+0.0%) — the gap only grows at higher rates (−3.6% at the top).
   The blade's efficiency drops 0.79→0.69 with rate while its raw
   efficiency stays ~0.75 — the rate effect is in the power chain.

## Current state

- The cruise triple has a fair-weather test (Olympias rig vs Olympias
  numbers at hull×1.0) alongside the Mark II reference. The lean has a
  test that checks both measurement methods agree.
- One experimental module (`simulation/ll/experimental_coupling.py`,
  OFF by default) holds the hull-tilt spike behind
  `Ship(heel_coupling=True)`. No existing test is affected.
