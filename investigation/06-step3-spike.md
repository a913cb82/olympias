# Step 3 Spike — Heel-Coupled Drift + Drag (OFF by Default)

## What was tried

A swappable physics module (`ll/experimental_coupling.py`) wired into
`Ship` behind `heel_coupling=True` (default OFF — no existing gate
affected). Three coupled effects:

1. **Heel angle** from the roll balance (Taylor ch.31 §2.3):
   `heel = atan(tipping / (m·g·GM_eff))`,
   `tipping = f_rud·arm_rud + f_hull·arm_lat`, `GM_eff = GM − 0.2`
   (crew lean into turn). At G1 forces: heel ≈ 1.6° (BMT GM=0.97 m).

2. **Heel-coupled sideways force**: `F_heel = K_heel × sin(heel)`.
   The heeled hull's asymmetry pushes sideways. `K_heel` swept.

3. **Extra drag from drift + heel**: `D_extra = D(V) × K_drag ×
   (sin²(beta) + sin²(heel))`. Swept; the hull working at an angle
   or heeled over drags more.

Rudder inflow correction (drift + yaw crossflow at stern ≈ 1 m/s at
4°/s) is second-order on the rudder's own drag and was not included —
the first two items dominate the force magnitudes.

## Results

### Baseline (OFF) — for reference

```
G1  91.9 m (target 89.4 ±7%)  drift −1.70°  (target 7.8–15°)
F1 121.0 m (target 111.9 ±8.5%)  drift −1.28°
Tightest 61.9 m (target 62 ±10%)  t_360 = 95 s  (target 128 s)  drift 2.51°
```

### Sweep: K_heel × K_drag

```
K_heel  K_drag |   G1     F1  tight  t_360 | b_G1   heel_G1  b_tight  V_end
     0     2.0 | 91.9  121.0   61.9    95  | −1.70   −1.59     2.51   3.44  OK
     0     8.0 | 91.8  121.0   61.8    95  | −1.70   −1.59     2.53   3.44  OK
 40000     0.0 | 94.5  125.8   63.2    98  | −1.94   −1.85     3.11   3.45  F1!
 80000     0.0 | 98.7  133.5   65.5   102  | −2.28   −2.20     3.92   3.36  G1!
 80000     4.0 | 98.7  133.5   65.4   102  | −2.28   −2.19     3.84   3.36  G1!
120000     0.0 |106.7  148.2   69.8   111  | −2.76   −2.71     4.92   3.40  G1!
160000     0.0 |126.2  183.8   81.4   134  | −3.49   −3.47     6.51   3.32  G1!
```

### What it tells us

**K_drag alone does almost nothing** — at beta=1.7°, sin²=0.00088, so even
K_drag=8 adds only ~0.7% extra drag. The drift has to be large first for
drift-induced drag to matter. This is circular: drag needs drift, drift
needs the lateral force.

**K_heel moves t_360 in the right direction** — at K_heel=160000,
t_360 reaches 134 s (overshoots 128 s!) — the coupling CAN close the time
gap. But at the cost of G1 blowing to 126 m (+41%, far outside the ±7%
gate). The trade-off is steep: every second gained on t_360 costs ~1 m
of G1 diameter.

**Drift barely moves** — even at K_heel=160000 (extreme), G1 drift only
goes −1.7°→−3.5°. The heel angle itself is only ~1.6° at G1 (GM is well-
measured), so geometric heel effects (tilted hull changing A_lat or
wetted area) are tiny at these angles (<2% change).

**Geometric heel effects are negligible** — at 1.6° heel,
A_lat_eff ≈ A_lat × cos(heel) ≈ 0.9996 × A_lat. Even parameterised as
A_lat × (1 − K×|heel|) with K=4, the reduction is only 11%. The hull
tilt at 1–3° is too small to matter geometrically.

## Verdict

The simple heel-coupled model **does not cleanly close the gaps**:

- Drift: 1.7°→3.5° even at extreme K_heel — still 2–4× short of 7.8–15°.
  The heel force direction also widens turns (F_heel opposes rudder),
  so pushing K_heel harder to get drift breaks the diameter gates.

- Time: t_360 CAN reach 128 s but only by breaking every diameter gate.
  The K_drag term that should couple drift→drag→time is negligible at
  current small angles.

- The heel itself (~1.6° at G1, ~3° at tightest) is well-constrained by
  the measured GM — it won't get larger without contradicting the BMT
  stability data.

## What this rules out and where to look next

**Ruled out for now:**
- Simple heel→side-force + sin² drag as a clean coupled fix. The
  magnitudes don't work without breaking other gates.

**Still worth trying (not covered by this spike):**
- A non-heel lateral force — e.g., the hull's form asymmetry at drift
  (the bow/stern sections have different lateral resistance) or a wind
  leeway term. These would add lateral force without the heel's yaw-
  moment penalty.
- Degraded thrust in turns — rowers losing efficiency at heel/drift
  (oar immersion, body mechanics). This slows the turn without widening
  it (less thrust → lower speed → longer t_360, but also tighter turns
  at lower speed — opposite to the heel effect). Would need to be
  parameterised as thrust × (1 − K×|heel|) or rate-dependent.
- A different heel formulation where the heeled hull's CLR shifts
  (changing the yaw balance independently of the lateral balance).

**The honest bottom line:** the three gaps are not trivially coupled
through heel. Each has a separate character: drift is a lateral-force
shortfall, time is a speed-floor issue, and the triple is a rig-
comparison artifact (half) plus rate-dependent efficiency. Fixing them
may need separate mechanisms, not one.

## How to reproduce

```bash
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship, rate_for_speed
from common.chain import KT
import math
R6 = rate_for_speed('Olympias', 6.0, n_oars=170)
s = Ship(rate=R6, helm=('port',1.0), heel_coupling=True,
         heel_params=dict(K_heel=80000, K_drag=4.0))
s.V = 6.0*KT
from ll.ship import run_turn
print('G1:', run_turn(s)['D'])
s2 = Ship(rate=R6, helm=('port',1.0), heel_coupling=True,
          heel_params=dict(K_heel=80000, K_drag=4.0))
s2.V = 6.0*KT
while s2.t < 60: s2.step(0.02)
print('drift:', math.degrees(math.atan2(s2.v,s2.V)))
"
```

## Files

- `simulation/ll/experimental_coupling.py` — the spike module (imported
  only when Ship(heel_coupling=True)).
- `simulation/ll/ship.py` — Ship.__init__ gains heel_coupling +
  heel_params; hull_advance gains the three coupled terms (all guarded
  by `if self.heel_coupling`).
