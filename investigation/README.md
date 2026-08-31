# Investigation — Three Open Items

Why the LL doesn't match the trials on three numbers, and what we've
measured trying to close each gap. Read in order; 04 ties the threads.

| File | Question | Gap | Verdict |
|---|---|---|---|
| [01](01-turn-time.md) | Why does the 360° turn take 95 s not 128 s? | −26% | Settled speed 0.5 kt too high; no single drag fix closes it |
| [02](02-drift-angle.md) | Why is drift 1.4° not 8–15°? | 5–10× | Needs 5× smaller A_lat or missing lateral force (heel?) |
| [03](03-cruise-triple.md) | Why is the speed-vs-rate curve flat (−2.4→−6.0%)? | Growing with rate | Half is rig mismatch; half is rate-dependent blade efficiency |
| [04](04-synthesis.md) | How do the three connect? | — | Drift→time coupling is the best cross-gap fix |
| [05](05-experiments.md) | What did we actually measure? | — | Raw experiment outputs for every claim in 01–04 |
| [06](06-step3-spike.md) | Does heel coupling close drift+time? | Spike | No — heel at 1.6° is too small; time CAN reach 128 s but breaks diameters |

## How to reproduce the experiments

Every number in 05 comes from a one-liner against the LL at 4b67934:

```bash
# Cruise triple (fair vs mixed comparison)
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
    print(f'{r}: chain {Vc/KT:.2f} vs LL {eq[\"V\"]/KT:.2f}  {(eq[\"V\"]-Vc)/Vc*100:+.1f}%')
"

# Turn time — the settled-speed attractor
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship; from common.chain import KT; import math
s=Ship(rate=44.5,oar_state=('row','hold'),helm=('starboard',1.0)); s.V=6.5*KT
ymax=0
while abs(s.psi)<2*math.pi: s.step(0.02); ymax=max(ymax,abs(s.y))
print(f'D={ymax:.1f} t={s.t:.0f} V_end={s.V/KT:.1f} V_mean={math.pi*ymax/s.t/KT:.1f}')
"

# Drift A_lat sensitivity
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship; from ll.ship import rate_for_speed
from common.chain import KT, A_LAT_TRIAL; import math
for f in [1.0,0.5,0.3,0.2]:
    s=Ship(rate=rate_for_speed('Olympias',6.0,n_oars=170),helm=('port',1.0)); s.V=6.0*KT
    s.vessel.A_lat=A_LAT_TRIAL*f
    for _ in range(int(60/0.02)): s.step(0.02)
    print(f'A_lat x{f}: beta={math.degrees(math.atan2(s.v,s.V)):.1f} D={2*abs(s.V)/abs(s.omega):.0f}')
"
```

## Key findings (one line each)

1. **Turn time**: The settled speed is an attractor (~3.7 kt regardless of
   entry). Extra drag of any amount tightens D as it lengthens t — maximum
   112s with degraded crew, still 16s short. Drift-induced + heel drag
   together might close it but are unmeasured.

2. **Drift**: Needs A_lat≈6 m² for β≈8.5° vs real 30.09 m². The force balance
   has two large opposing terms (f_hull vs mUω) whose small residual sets β
   — any missing lateral force (heel coupling, wind, nonlinear CY) could
   shift it. Turns still pass at any A_lat; the gap is isolated.

3. **Cruise triple**: Olympias rig vs Olympias chain at hull=1.0:
   25.5 spm is now perfect (+0.0%); the rate-dependent −0→−3.6% remains.
   The blade's E_eff drops 0.793→0.693 with rate while its direct eff stays
   ~0.75 — the rate dependence is in the handle force / power chain.

## Status

- Steps 1 and 2: model unchanged, gates tightened (the triple now has a
  fair lock; drift now has a delay-method lock).
- Step 3: one new module (`simulation/ll/experimental_coupling.py`, OFF
  by default) wired behind `Ship(heel_coupling=True)`. No existing gate
  is affected. See [06](06-step3-spike.md) for the negative result.
