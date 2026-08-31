# Investigation 01 — Turn Time: 95 s vs 128 s (−26%)

## The gap

| Quantity | Trial | LL | Error |
|---|---|---|---|
| Tightest sprint turn D (360° extent) | 62 m | 61.9 m | −0.2% ✅ |
| Tightest sprint turn t_360 | 128 s | 94.7 s | −26% ❌ |
| Mean speed over turn (πD/t) | 2.96 kt | 3.99 kt | +35% |

The **size** matches. The **time** doesn't. The LL's ship is ~1 kt too fast
on average through the turn (3.99 kt mean vs 2.96 kt implied by the trial).

The trial's 128 s is itself derived, not directly measured:
Morrison 1988 reports D = 1.9×LWL = 61 m and "halves speed" (6.5→~3.25 kt).
At mean 2.91 kt (half of entry, halved again by deceleration), yaw rate
is V/R = 1.50/31 = 0.048 rad/s = 2.8°/s → 360° in 128 s. The reports also
quote measured yaw 2.6–3.0°/s, consistent.

A second anchor sharpens the family: the **stationary turn** (Zygian +
Thranite only, 58 oars, from rest at 27 spm) measured **3.5°/s** but the LL
gives 2.32°/s in-place (−34%) and 1.06°/s one-side (−70%). Here the model
is **too slow** at low speed, partial crew — the opposite direction from the
sprint turn (too fast at full crew). The two regimes bracket the physics.

## What the LL actually does through the turn

Measured at dt=0.02, rate=44.5 spm sprint, 6.5 kt entry, full rudder + one
side holds:

```
t=  0: V=6.50 kt  omega= 0.0°/s  (entry)
t= 10: V=4.95 kt  omega=-3.40°/s  beta=1.7°
t= 20: V=4.36 kt  omega=-4.17°/s  beta=2.4°
t= 30: V=4.24 kt  omega=-4.35°/s  beta=2.4°  ← approaching settle
t= 60: V=3.75 kt  omega=-4.03°/s  beta=2.9°
t= 90: V=3.43 kt  omega=-3.62°/s  beta=2.8°  ← settled (W' drained)
```

Forces at settle (V=3.43 kt = 1.76 m/s):

| Force | Value | Notes |
|---|---|---|
| Hull drag D(V) = W/V | 524 N | W=155V³+4.13V⁵, V=1.76 m/s |
| Rudder drag (full helm, FAC 1.4) | 650 N | (79.6−40.2)→39.4 Vkt² × FAC |
| **Total drag** | **1174 N** | what must be overcome |
| Rowing thrust (85 oars, but W' drained) | ~85×~? | crew exhausted, limited to P_crit |
| Hold brake (85 oars × hold_k×V²) | 85×18.1 = 1538 N | hold_k=5.8, V²=3.10 |

The rowing side is **exhausted** at settle: thranite/zygian W_frac=0.00,
thalmian 0.39. The burst at 44.5 spm drains the 6 kJ tank in ~60 s.

The ship settles at V≈3.4–3.8 kt regardless of entry speed (tested V0 =
3.0→6.5 kt all converge to ~3.7 kt). The settled speed is an **attractor**
set by the balance: exhausted-rowing thrust + hold brake vs hull+rudder drag.

## What has been tried and ruled out

| Hypothesis | Test | Result | Verdict |
|---|---|---|---|
| Linear yaw damping (YAW_LIN_DAMP) | Added k×omega term | Any k closing t_360 blows all D out of gates (+24/+31/+25%) | ❌ Rejected |
| Turn build-up (helm not instant) | Measured approach transient | Only ~2 s of the 30 s gap | ❌ Too small |
| Yaw-induced oar/water differential | Local flow V∓omega×lever | Only ~1 s; reverted as too complex for too little | ❌ Too small |
| Hold fraction | 0.05→0.08 (re-measured) | Fixes D (62.6 m) but not time | ❌ Fixes size not time |
| W' fade | Included (drains in ~60 s) | Already in model; see below | Partial |
| Sway DOF (CLR restoring + Omega) | Full 3-DOF hull | Brought D to correct; time still 98 s | ❌ Not enough |
| Crossflow Omega variation | C_D 0.252→0.30 (3.0→3.57e6) | Shifts D slightly, not time | ❌ Wrong knob |
| Clarke hull derivatives | Full CGH set | 100× too large for slender hull | ❌ Rejected |

## Experiments run in this investigation

### Rate sensitivity (same turn, different rates)

| Rate (spm) | D (m) | t_360 (s) | V_end (kt) |
|---|---|---|---|
| 19.9 | 61.3 | 112.4 | 3.21 |
| 25.0 | 61.5 | 104.6 | 3.41 |
| 31.5 | 61.7 | 97.2 | 3.76 |
| 44.5 | 61.9 | 94.7 | 3.44 |

Lower rate → longer t_360 (closer to 128 s!). Rate 19.9 at 112 s is the
closest. But the trial's tightest was a **sprint** (max effort, inferred
high rate), not a cruise. If the trial crew rowed at ~20 spm effective (due
to exhaustion/confusion in the tight turn), the time gap shrinks.

### W' sensitivity (same turn, different anaerobic capacity)

| W' (J/man) | D (m) | t_360 (s) | V_end (kt) |
|---|---|---|---|
| 3000 | 61.2 | 100.3 | 3.31 |
| 6000 (current) | 61.9 | 94.7 | 3.44 |
| 10000 | 61.9 | 89.7 | 3.86 |
| 20000 | 61.9 | 89.6 | 4.16 |

Smaller W' → longer t_360 (more exhausted → less thrust → slower → longer).
But W'=3000 only gains 6 s; even W'=0 wouldn't reach 128 s. The exhausted
thrust floor (P_crit=80W) still pushes the ship at ~3.3 kt.

### The settled-speed attractor

Regardless of entry speed (3.0–6.5 kt), the tightest turn always settles
to ~3.7 kt. This means the 30 s gap is NOT about the entry transient —
it's about the **settled speed being too high by ~0.5 kt** (3.5–3.8 vs
trial's ~2.9).

## Hypotheses for the remaining gap

### H1: Missing drag in the turn (most likely family)

The model has: hull drag (W/V) + rudder drag (FAC×straight). What's missing
when the ship is turning + drifting + heeling?

**H1a — Drift-induced hull drag.**
When β≠0, the hull presents oblique flow. Additional drag ≈ D(V)×sin²β or
½ρV²×A_front×sin²β. At β=2.8°, sin²=0.24% — negligible. But if β were 10°,
sin²=3% → at 3.5 kt this adds ~20 N. Not enough alone, but:
- If β SHOULD be 10° (see drift investigation), this drag IS missing
- The drift and time gaps may be coupled

**H1b — Heel-induced drag.**
The ship heels ~3° in the turn (BMT GM=1.13m, tipping from rudder + hull
lateral forces). Heel increases wetted surface and creates asymmetric form
drag. Estimate: +5–10% drag for 3° heel on a slender hull. At 3.5 kt:
~30–60 N extra. Small but in the right direction.

**H1c — Wave-making in the turn.**
The tight turn displaces water laterally, generating additional wave drag
beyond the calm-water W(V) law. The W(V) law was measured in straight
towing — the turn's curvature adds a component not in the model.

**H1d — Oar-hull interaction drag.**
85 oars dragging through water create turbulence and wake that increases
effective hull drag. The hold brake models only the blade's own drag, not
the wake interaction with the hull. 85 blades × 0.018 m² effective each
× dynamic pressure at 1.76 m/s = 85×0.018×1587Pa×0.078... this IS the hold
brake already. But the INTERACTION (wake × hull) could be additional.

**H1e — Rudder-hull interaction.**
The rudder drag model (straight 39.4V² + induced) assumes the hull's flow
is uniform at the rudder. In a tight turn with drift, the inflow to the
rudder is oblique, potentially increasing drag beyond the FAC model. The
rudder at full helm + 2.8° drift + yaw rate gives inflow angle ≈ 67.5° +
drift correction + yaw-induced crossflow at the stern (15m × omega =
15×0.063 = 0.95 m/s lateral). At V=1.76 m/s, crossflow/V = 54% → inflow
angle changes significantly.

**H1f — Turbulent separation / form drag at low speed.**
At very low speed (2–3 kt), the hull's Reynolds number drops and the
flow may separate differently in a turn vs straight ahead. The drag law
W/V assumes attached flow; separated flow has higher drag.

### H2: Over-predicted thrust in the turn

**H2a — Rowers can't pull effectively in a tight turn.**
The ship heels, yaws, and drifts — rowers on the inside/outside of the
turn have different oar angles, blade depths, and body positions. The LL
assumes both sides row identically (one side holds). But the rowing side's
oars on the outside of a tight turn may have reduced efficiency (different
blade immersion, oar angle, body mechanics).

**H2b — W' drain is too slow / P_crit too high.**
If the real crew exhausted faster (smaller W' or higher P_crit threshold),
they'd produce less thrust at settle → lower speed → longer time. But
experiments show even W'=3000 only adds 6 s. The exhausted floor (P_crit
=80W) rate-limits this.

**H2c — The sprint rate is wrong.**
If the trial crew didn't sustain 44.5 spm through the 128 s turn but
dropped to ~20 spm (coordination breakdown in a tight turn), the thrust
would be much lower (rate 19.9 thrust at 3.5 kt: much less than at 44.5).
The LL assumes constant 44.5 spm throughout. The trial reports say
"the tightest turn... halved speed" — but don't state the rate through
the turn. Perhaps the inside crew stopped AND the outside crew's rate
dropped.

### H3: The measurement itself

**H3a — The 128 s includes the entry transient.**
Taylor's "halves speed" derivation assumes the 128 s is the steady turn.
But if the trial's timing started before the helm was fully over (approach
+ helm application + settle), the "turn time" includes the entry phase
where speed is still high, making the mean speed lower but the diameter
measurement also affected. The LL's run_turn starts at full helm instantly.

**H3b — The trial's rate through the turn unknown.**
The t_360 test assumes the rate that gives 6.5 kt entry speed for the
given n_oars=85 configuration (rate_for_speed at 6.5 kt → ~31.5 spm for
one-side balance). But the trial's rate assignment for this turn is
uncertain — the hold spectrum wasn't recorded (register from test_gate3).

### H4: Coupled drift-time mechanism

The drift angle gap (1.4° vs 8–15°) and the time gap may share a cause:
if the model's drift is too small, the associated drift-induced drag IS
missing (H1a), and the rudder's effective angle is wrong (H1e). Fixing
drift might simultaneously fix time.

---

## What to try next

### Quick experiments (no code change, just parameter sweeps)

1. **Sweep P_crit and W' together**: What (P_crit, W') pair gives t_360=128s?
   — The rate 19.9 result (112 s) suggests rate matters more than W'.
2. **Measure what extra drag gives 128 s**: Add a constant or V²-proportional
   drag term in the tightest scenario; find the magnitude that closes the gap;
   compare to physical estimates (heel 5%, drift 3%, wave, etc.).
3. **Run with degraded rowing side**: What if the rowing side's rate drops
   to 20–25 spm after 30 s? Does t_360 reach 128?
4. **Measure the stationary-turn speed**: Why does the LL turn too slowly
   at low speed/partial crew (the opposite error)? This constrains the
   damping/drag models.

### Model changes (ranked by promise)

1. **Drift-induced drag**: Add D_drift = k_drift × ½ρV²×A_lat×sin²β or
   D_drift = D(V)×f(β). Simplest to implement, couples with drift fix.
2. **Heel-induced drag**: Parameterize from heel angle (already computed
   in manoeuvre_model.py but not in Ship).
3. **Turn-curvature wave drag**: Additional resistance proportional to
   (V²/R) or ω² — dimensionally a lateral-acceleration drag.
4. **Degraded thrust in turns**: Reduce rowing efficiency when
   beta or omega exceeds a threshold (oar immersion/angle effect).
5. **Rate decay in turns**: Model the crew losing stroke rate in a tight
   turn (coordination breakdown).

### Measurements needed

- The real drag through a tight turn: not available (would need a captive
  model test at non-zero drift and yaw rate).
- The trial's actual stroke rate through the 360° turn (not recorded).
- Bilge-water sloshing effect on drag (mentioned in BMT report, unmeasured).
