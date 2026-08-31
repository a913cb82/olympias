# Investigation 02 — Drift Angle: 1.4° vs 8–15°

## The gap

| Scenario | Trial (reported) | Trial (time-delay method) | LL | Gap |
|---|---|---|---|---|
| G1 full rudder @ 6 kt | 15°±2° | 7.8° (3 s × 2.6°/s) | 1.4–1.7° | 5–10× |
| F1 22.5° @ 6 kt | similar | ~7° | 1.3° | ~5× |
| Tightest (hold + full rudder) | not reported | — | 2.8° | — |

Taylor himself notes the scatter: the heading-vs-track 90° delay method
gives 3 s × 2.6°/s = 7.8° for the same G1/G2 turns reported as 15°±2°,
and says "assume the lower value." Even the lower 7.8° is ~5× the LL's
1.4°. The gap is real even at the conservative end.

Drift β = arctan(v/U) where v = lateral velocity, U = forward speed.
The ship's velocity vector is offset from the keel by β — the hull
"crabs" sideways through the water.

## What the LL computes

The sway dynamics (Ship.hull_advance):

```
f_hull  = RHO × A_lat × |U| × v          (lateral hull resistance)
q_hull  = f_hull × clr_offset             (restoring yaw moment)
v_dot   = (Fy_oars + f_rud − f_hull)/m_app − U×omega
omega_dot = (Q + q_hull − Omega×omega×|omega|)/I
```

At steady turn (v_dot≈0, omega_dot≈0):

```
Fy_oars + f_rud = f_hull + m_app×U×omega    (lateral force balance)
Q + q_hull = Omega×omega²                    (yaw moment balance)
```

Where:
- Fy_oars = lateral oar force (blade Fy averaged over stroke)
- f_rud = rudder lateral force = coeff(Φ)×rudder_drag(Φ)
- f_hull = RHO×A_lat×|U|×v (Taylor's linear form, row 5 of Table 31.1)
- m_app×U×omega = centripetal force required to turn

### Force magnitudes at G1 settle (U=5.34 kt=2.75 m/s, omega=3.8°/s=0.066 rad/s)

| Term | Value | Notes |
|---|---|---|
| f_hull = 1025×30.09×2.75×(−0.081) | −6900 N | restoring (opposes drift) |
| m×U×omega = 45042×2.75×0.066 | +8192 N | centripetal (outward) |
| f_hull + m×U×omega | +1292 N | net that Fy+f_rud must provide |
| Rudder lateral f_rud | ~? | coeff(67.5)=0.81 × rud_drag |
| Fy_oars | small | varies through stroke |

So f_hull nearly cancels the centripetal term; the residual (~1300 N) is
provided by rudder+oars.

### Why the drift is small

v = (Fy_oars + f_rud − m×U×omega) / (RHO×A_lat×U)

With A_lat=30.09 m²:
- RHO×A_lat×U = 1025×30.09×2.75 = 84800 N/(m/s) — the "lateral stiffness"
- Net lateral force available ≈ 1000–2000 N
- v = 1000/84800 = 0.012 m/s → β = 0.25° ... but LL gives 1.7°

The numbers above are approximate (the actual balance includes v-dependence
in f_hull itself, so it's implicit). The measured v=0.081 m/s gives
f_hull=6900 N, suggesting the lateral forces ARE larger.

## Experiments run in this investigation

### A_lat sensitivity (G1, same rudder/rate)

| A_lat factor | A_lat (m²) | β (deg) | D (m) | V (kt) |
|---|---|---|---|---|
| ×1.0 | 30.1 | −1.70 | 82.9 | 5.34 |
| ×0.5 | 15.0 | −3.39 | 82.7 | 5.21 |
| ×0.3 | 9.0 | −5.65 | 82.5 | 5.04 |
| ×0.2 | 6.0 | −8.48 | 82.3 | 4.85 |

To get β≈8.5° (matching the lower trial estimate), need A_lat≈6 m² —
**5× smaller** than the real hull's 30.09 m². Diameter barely changes
(82.9→82.3 m), so turns would still pass, but V drops 5.34→4.85 kt.

The real hull's lateral area IS 30.09 m² (from basis_hull_offsets.tsv,
Simpson integration of drafts at trial WL 1.10 m, verified against workbook
LWL 32.35 m). It cannot be reduced.

### The Taylor A_lat vs the real hull

Taylor Table 31.1 row 5 says A_lat=35 m² for Olympias. The real hull gives
30.09 m² at trial WL — 14% less. Using Taylor's 35 m² would make drift
even SMALLER (∝ 1/A_lat), worsening the gap. The grounded 30.09 is already
the best we have.

## Why A_lat cannot be the fix — and what could be

### The lateral stiffness problem

The hull's lateral resistance f_hull = RHO×A_lat×|U|×v is **linear in v**
and proportional to U. At U=2.75 m/s and A_lat=30 m², the coefficient is
~85000 N per m/s of drift. To get β=10° (v=U×tan10°=0.48 m/s), need
f_hull=40994 N applied laterally. The available lateral forces (rudder +
oars + centripetal) seem insufficient.

But wait — the centripetal term m×U×omega IS the dominant lateral force:
at G1 settle: m×U×omega = 45042×2.75×0.066 = 8192 N outward, while
f_hull = 6900 N inward. The steady drift is the SMALL residual between
two large opposing forces. A small change in either shifts β significantly:

```
v = (Fy_oars + f_rud − m×U×omega) / (−RHO×A_lat×U)  [sign convention]
```

So the question is not "is A_lat too large?" but "is the numerator
(Fy_oars + f_rud − m×U×omega) too small?"

### Hypothesis H1: Missing lateral force

**H1a — Oar lateral force (Fy_oars).**
The blade produces lateral force Fy = −Fn×sin(C). At C=0 (mid-stroke),
sin(C)=0 → no lateral force. At the catch/finish (C=±24°), sin(±24°)=
±0.41. Averaged over the drive: mean sin(C) depends on the sweep shape.
For symmetric rowing (both sides), Fy cancels between port and starboard
— net Fy_oars≈0 in straight flight and rudder turns. But in the tightest
turn (one side rows, one holds), the rowing side's blade does produce net
lateral force. In G1 (both sides row + rudder), Fy_oars is small.

How large IS Fy_oars at G1? Let's measure it — the per-stroke Fy ripple
causes the heading oscillation ("fishttail") but the mean may be near zero.

**H1b — Rudder lateral force too small.**
f_rud = coeff(Φ)×rud_drag, coeff(Φ)=0.14+0.020Φ−0.00015Φ².
At Φ=67.5°: coeff=0.81. Rud_drag at 5.34 kt: 39.4×5.34²×1.4 ≈ 1573 N.
So f_rud = 0.81×1573 = 1274 N lateral. Is this too small?
- Taylor's coefficient was fitted to match diameters, not drift
- The Hoerner lift model gives CL=sin(2α), which at 67.5° gives CL=sin(135°)=0.707
- With η=0.045, flat-plate lift = 0.5×ρ×A×CL×V²×η = 0.5×1025×1.5×0.707×7.56×0.045 = 185 N
  — much smaller than the row-5 based estimate! There's a factor-of-several
  discrepancy between Hoerner lift and Taylor's coeff method.

**H1c — Hull lateral force model is wrong.**
The Taylor form f_hull = ρA_lat×U×v is a LINEAR damping (first-order in v).
But real hull lateral resistance at finite drift angle is NONLINEAR:
F_hull(β) = ½ρV²×A_lat×CY(β) where CY(β) includes a quadratic term:
CY = CY_β×β + CY_β|β|×β|β| (crossflow drag). At β=1.7°, linear dominates.
At β=10°, the nonlinear term matters. The linear model may under-predict
the hull's lateral force at moderate drift, requiring less β for the same
force... no, that would make β SMALLER, not larger.

Wait — the linear model says f_hull ∝ U×v = U²×tan(β) ≈ U²×β for small β.
The nonlinear model says f_hull ∝ V²×(CY_β×β + CY_β|β|×β²). For the same
β, nonlinear gives MORE force → LESS drift needed → smaller β. So a
nonlinear hull model would make the gap WORSE (predict even less drift).

Unless the linear coefficient CY_β is OVERESTIMATED — i.e., A_lat=30 m²
implies too much lateral stiffness. But A_lat is from geometry...

**H1d — The hull's lateral centre (CLR) position.**
The LL uses clr_offset=0.93 m (x_clr 16.60 from AP, CG at LCB 15.67).
Taylor Table 31.1 row 13 says the lateral resistance acts at arm 1.46 m
below CG vertically, but the along-keel position of CLR isn't tabulated
separately — the LL assumes the lateral force acts through the CLR's
along-keel position. If the CLR is further aft (less forward of CG),
the restoring yaw moment q_hull = f_hull×clr_offset would be smaller →
less yaw damping → tighter turns at the same drift → but drift itself
comes from the lateral balance, not the yaw balance.

### Hypothesis H2: The measurement includes something beyond steady drift

**H2a — Heel-induced drift.**
The ship heels ~3° in a hard turn. A heeled hull has asymmetric waterplane
and lateral plane — the underwater shape becomes asymmetric, generating
additional lateral force (hull asymmetry drift). This is NOT in the sway
model at all — it assumes an even-keel hull.

**H2b — Wave/heel coupling.**
The heeled hull's wave-making is asymmetric, adding a drift component.
Again not modelled.

**H2c — Transient vs steady measurement.**
The trial's 15° was measured as the angle between the ship's HEAD (heading)
and TRACK (Course Over Ground) reaching 90° at different times — delay ×
yaw rate. But this includes the heading change DURING the delay, not just
steady drift. Taylor's time-delay method (3 s × 2.6°/s = 7.8°) corrects for
this but still gives ~8° vs our 1.4°. The measurement method itself has
±50% uncertainty (stated as 15°±2° vs 7.8° for the same turn).

**H2d — Wind and current effects.**
The trials' measured drift includes wind leeway (wind pushes the ship
sideways) and possible current shear. The LL models calm water only.

### Hypothesis H3: The force balance is fundamentally different

**H3a — Added mass in sway.**
The LL uses m_app = 1.10×m for surge but the same m_app for sway (dividing
Fy/f_rud/f_hull by m_app in v_dot). But sway added mass differs from surge:
Y_vdot is typically much larger (the hull's sway added mass ≈ 0.5–1.0×
displacement for a slender hull, vs 0.10 for surge). The row shows:
`(m − Yv̇)·v̇ − Yṙ·ṙ = Yv·v + Yr·r − m·U·r + Y_ext` — the Braithwaite VBA
solves the full mass matrix with Yv̇, Yṙ, Nv̇, Nṙ. The LL lumps all lateral
inertia into m_app=1.10m, potentially under-damping sway.

This affects TRANSIENT drift (how quickly β builds) more than steady β,
but could affect the heading-vs-track measurement if the turn hasn't fully
settled.

**H3b — The hull's sway damping Yv.**
Taylor's linear form f_hull = ρA_latUv implies Yv = −ρA_latU (= −84800 at
G1). The Braithwaite VBA uses Clarke derivatives: Yv = Y'v×½ρUL with
Y'v from the empirical formulas. For Olympias (Cb=0.32, T/L, B/L), Clarke
gives Yv ≈ −80000 at U=1 — similar! But the VBA was rejected because its
yaw damping (Nr) was 100× too large. Its Yv might be more relevant.

**H3c — Roll-sway coupling.**
The LL has no roll DOF. A heeling hull changes both the lateral area and
the sway-yaw coupling through the roll angle. The BMT data gives GM=1.13m
and heel ~3° — the hull heel changes the effective lateral area and adds
a roll-induced sway force.

---

## What to try next

### Quick experiments

1. **Measure Fy_oars and f_rud at each turn scenario** — are they as small
   as the balance suggests? Is there a missing ~40 kN?
2. **Try reducing A_lat dramatically** — yes it gives drift but drops V;
   quantify: does A_lat=6 m² + adjusted hull drag still hold D gates?
3. **Add heel-induced side force**: parameterize as F_heel = k_heel×heel_angle
   and sweep k_heel to see what closes the drift gap.
4. **Compare with the Braithwaite VBA's sway prediction** — does its full
   mass matrix + Clarke Yv give different drift?
5. **Measure the transient drift** — how does β(t) evolve from turn entry
   to settle? Does the heading-vs-track delay method measure something
   different from steady-state β?

### Model changes (ranked)

1. **Heel-coupled lateral force** — if heel generates lateral force, it
   adds to f_rud without needing to change A_lat.
2. **Nonlinear lateral resistance** — probably makes things worse (more
   stiffness), but worth quantifying.
3. **Roll DOF** — full 4-DOF (surge+sway+yaw+roll) with heel dynamics
   coupled to sway. Complex but physically motivated.
4. **Reconcile the force magnitudes** — the Hoerner lift vs Taylor coeff
   discrepancy for rudder lateral force needs resolution.
5. **Wind/current leeway** — add as external drift if trial data has wind.

### Measurements needed

- The hull's lateral force vs drift angle at various speeds (captive model
  test / CFD at β=0–15°). This directly gives CY(β) and settles whether
  A_lat=30 m² is the right stiffness.
- Heel's effect on lateral force (heeled hull captive test).
- Trial wind/current data for the G1/F1 turns (was there wind leeway?).
