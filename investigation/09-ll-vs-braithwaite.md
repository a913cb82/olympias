# How this project and Richard Braithwaite's model compare

Two separate teams built computer models of the same ship — the Olympias
trireme (a full-size replica of an ancient Greek warship, 32 m long, 170
oars, built in the 1980s and tested at sea in 1987–88). Both tried to
answer the same question: how does this ship move, and how does it turn?

Both had the same measurements to work from: the 1988 sea-trials report
(the detailed record of how the real replica performed) and the later
Rankov 2012 book that collected all the trial data. But they made very
different choices about how to describe the physics — and those choices
explain where each model succeeds and where it still falls short.

Both models treat the ship as a rigid body that can move in three ways:

- **Surge** — moving forward or backward along its length.
- **Sway** — sliding sideways.
- **Yaw** — spinning (turning) like a top.

The underlying motion equations are the same (Newton's laws in the ship's
own frame, with the coupling between forward speed and turning that makes
a moving ship behave differently from a stationary one). Both step forward
in time using the same simple method (Euler). Both give the ship about
46 tonnes of "apparent mass" — the hull drags along surrounding water, so
it behaves as if it were ~10% heavier than its real weight.

What differs is what they put into those equations.

---

## 1. How the hull resists moving through water

When any ship moves, the water resists it. The two models fitted curves
to the same towing-tank measurements (a 1:10 scale model pulled through
still water in Athens in 1985), but came up with different curves.

**This project's model (LL)** uses a single smooth formula:

`Power needed = 155·V³ + 4.13·V⁵` watts, where V is speed in metres per
second. Drag (the force holding the hull back) is that power divided by
speed. The formula was fitted to the tank data and then checked against
what the real ship actually achieved at sea — the crew's power at
cruising rates should be enough to reach the measured cruising speeds, and
it is.

There is also an alternative in the code that builds drag from first
principles: skin friction (how sticky the water is on the hull's wet
surface, 130.5 m² — calculated from the real hull drawings) plus wave
drag (`5.3·V⁴`). At cruising speeds this matches the smooth formula
within half a percent, so it doesn't explain any of the open gaps.

**Braithwaite's model** uses the same tank data but fitted it as three
separate quadratic curves, one per speed range: `40.2·V²` at 1–6 knots,
`75.2·V² − 1560` at 7–8 knots, `88.6·V² − 2640` at 9–10 knots (V in knots),
and also fitted single cubic curves for the simulation. In his code he
also keeps two textbook formulas as alternatives (Holtrop-Mennen for
merchant ships and the Delft yacht series), but they are not tuned for a
slender trireme hull and underpredict the drag at high speeds.

**How they compare at cruising speeds:**

| Speed | This project | Braithwaite (smooth fit) | Difference |
|---|---|---|---|
| 5 knots | 1,206 N | 946 N | Braithwaite 22% lower |
| 7 knots | 2,705 N | 2,218 N | 18% lower |
| 8 knots | 3,810 N | 3,214 N | 16% lower |
| 9 knots | 5,221 N | 4,505 N | 14% lower |

Same data, different curves through the scatter. The gap is 10–22% —
not huge, but it means Braithwaite's ship needs less power to go the same
speed. His raw numbers would make the ship look faster than the trials
say it was, unless the oar thrust is also lower (which it is — see next
section). Nothing is "wrong" — just two curve fits through noisy points.
His workbook stores all three fits side by side.

---

## 2. How the oars push — where the models differ most

This is the biggest single difference.

**This project (LL)** treats each blade as a flat plate. The water pushes
on the blade with a force proportional to the square of how fast the blade
slices sideways through the water:

`Blade force = ½ × water density × blade area × 1.8 × (speed through water)²`

Blade area is 0.078 m² (the real blade is 0.113 m², but only ~85% is
underwater on average and the narrow shape is ~81% as effective as a
wide one — `0.113 × 0.85 × 0.81 = 0.078`). The speed through water
combines the ship's forward speed and the oar's own swing speed. The oar
swings through 48.1° at a measured rhythm (Table 9.6: 0.43 s in the water
at 28.8 strokes per minute). The drive and recovery alternate: blade in
the water (push), blade in the air (no push).

There is a detailed force-driven mode where the rower's pull (chain law:
average pull `7.43 × stroke rate` newtons) and the oar's own spin
inertia (9.74 kg·m² for spruce oars) are balanced — the oar settles at
the speed where water resistance exactly absorbs the rower's pull. That
mode reproduces the measured stroke timings within 5%.

Two alternative blade laws are kept as switches but switched off: one
puts the pivot at a geometric spot on the oar shaft (gives net negative
thrust — wrong for this ship), the other adds a lift component from real
blade shape (matters ~55% at some angles, but the chain's calibration
already absorbs the difference).

**Braithwaite's model** uses a simpler straight line:

`Thrust = how hard the crew pulls × 81 newtons per oar × (1 − ship speed / 18 knots)`

81 N per oar (~5000/62) comes from the trials; 18 knots is where
thrust would drop to zero if you kept going (the blade outruns the
water). `how hard` is 0–1 (a pressure factor), `V_local = forward speed
± lever × spin rate` gives port/starboard blades different flows in a
turn. All blades on one side are at the same point (x=0, no spread
along the hull, no sideways velocity). The blade makes no sideways force
(`FY=0`) — turning comes only from one side pulling harder plus the
rudder.

His detailed Rev F oar (§3.2) adds a full 4-phase stroke: the finish
(parabolic angle), recovery (cubic), catch (mirror), and power (blade macro
with lift + drag from real blade shape, rower's 51 kg moving body, footplate
forces, and a Hill-like max-force curve that falls with ship speed — solved
by iterating the oar's spin until the handle force matches the target).

**What they share:** Both use the same flat-plate drag law (`drag = 2·sin²
angle`) and the same lift law (`lift = sin(2·angle)`) for the blade;
both model the 4-phase stroke with inertia at the ends; both include the
rower's moving body (~51 kg).

**Where they differ:**
- LL: thrust grows as `speed²` (quadratic), built from the flat-plate law
  at each blade angle. Braithwaite: `1 − speed/18` (linear) through
  (0→81 N, 18→0). At 7 knots they give very different per-oar pushes —
  but LL's is a cycle-average, Braithwaite's is a per-side aggregate, so
  the raw numbers aren't directly comparable. The *mean* push over a cycle
  that balances hull drag at cruise is similar in both (they must be, or
  the ship wouldn't move).
- LL: blade flow includes `V·cos(angle) + lever·spin` plus, when the
  per-station layer is on, the hull's `v` and `r` at that blade's
  position. Braithwaite: `V_local = forward speed ± lever × spin` per side
  (no `v`, no spread along the hull).
- LL: blade makes a sideways force; Braithwaite: `FY=0`.
- LL: rower's body inertia is oar-only (the body's work is folded into
  the `7.43 × rate` power chain). Braithwaite: explicit 51 kg (68% of
  a 75 kg rower) with footplate forces.

---

## 3. The crew — one model has stamina, the other doesn't

**This project (LL)** has a full crew model. Each side has 85 rowers in
three tiers (upper/middle/lower: 31/27/27, with the lower tier at 90–60%
power because the beams above their heads are lower than the oar spacing —
they hit their heads at the stroke ends).

Each tier has its own:

- **Energy tank (W')**: 6,000 joules. Rowing above 80 watts per person
  drains it; below 80 watts or at rest it refills (time constant 2
  minutes). When empty, the rower can only manage 80 watts. This sets
  how long a burst lasts (~45 s at 44.5 strokes/min → 8.2–8.4 knots).
- **Force ceiling**: 700 N peak, 330 N mean at burst. If the blade needs
  more, the stroke slows down.
- **Timing rules**: the drive must fit in the cycle (`60/rate − 0.5 s`
  recovery minimum); if not, the sweep shortens; below 40% sweep the
  rate drops. A feather check: if the blade can't outrun the water, the
  stroke contributes nothing. The weaker side sets the pace for both
  sides (the caller on the ship calls the rate down when one side can't
  keep up).

**Braithwaite** has no stamina or energy tank. The rower is a force curve
`Mmax(V)` that falls linearly with ship speed (like a muscle's
force-velocity curve) plus a continuity fix near the catch. The
spreadsheet's `OarForces` is just `pressure × (n/2) × 81 × (1−V/18)`;
rate lives in the 4-phase timing and the per-step secant solver for the
oar's spin, but no fatigue.

So Braithwaite's ship can row at any rate forever; this project's ship
gets tired. For short validations (a few minutes) this doesn't matter.
For anything longer it does — it's why Braithwaite's top speed with all
170 oars is 9.95 knots (no limit) while this project bursts at 7.65 kt
(170 oars, hull drag alone) and settles near 6.1 kt on the sustainable
80 W floor.

---

## 4. How the hull resists turning

Both ask: "what slows the ship's spin?"

**This project** uses a single quadratic drag:

`spin drag = Ω × spin rate × |spin rate|`

with `Ω = 0.5 × water density × drag coefficient × J`, where `J` is the
integral of `water depth × |distance from centre|³` along the hull — a
number computed directly from the real hull drawings (LWL 32.35 m,
21 stations × 27 depth/width points, J = 23,217 m⁵ at trial waterline).
The drag coefficient is 0.252 (from the drag-crisis value 0.30 for a
smooth round hull, corrected for the difference between a rectangular
and tapered hull shape). So `Ω = 3.00×10⁶` — measured (fitted 3.20
at 0.30, the rectangular-tapered reconciliation is ×1.08).

Sideways: `sideways hull force = density × sideways area × |forward
speed| × sideways speed`, with sideways area A_lat = 30.09 m² (measured
from the 21 hull sections). A restoring moment `sideways force × 0.93 m`
(the centre of sideways resistance is 0.93 m forward of the centre of
mass, also from the hull drawings) opposes the turn. An experimental
heel-coupled spike (hull tilt adds a sideways push and extra drag) is
kept OFF — it moves drift 1.7°→3.5° but breaks the turn-size tests.

A Clarke-type linear sway/yaw model (8 hull derivatives for merchant
ships) was tried as `ll/clarke.py` and **rejected** — it gives 100× too
much damping for this long thin hull (designed for short fat merchant
ships with block coefficient 0.5–0.8, not a trireme at 0.32).

**Braithwaite** uses the same physics but through the coupled mass-matrix
route (Clarke-Gedling-Hine 1983, 8 prime-system numbers):

```
-Y'_vd/(π(T/L)²)=1+0.16·Cb·B/T−5.1(B/L)²  ... 8 equations ...
Dims: Yvd=Y'vd·0.5ρL³, Nr2=−ρ·CN·T·L⁴/64
U=√(u²+v²) for damping
Surge added mass: DISP·(0.04+0.06·Cb) → ~7–10%
det=(m−Yvd)(Iz−Nrd)−Yrd·Nvd, Cramer's rule:
fX=drag+m·v·r, fY=Yv·v+Yr·r−m·u·r, fZ=Nv·v+Nr·r+Nr2·r|r|
```

The yaw damper `Nr2 = −ρ·CN·T·L⁴/64` is the same cross-flow integral as
this project's `Ω` — just approximated as a rectangle (`T·L⁴/64`) instead
of the real tapered hull (`J`). The coefficient is the same factor-2
argument: the code uses 0.8, the paper/comment says 0.40. With T=1.15 m,
L=32.35 m, that is `ρ·0.8·T·L⁴/64 = 8.0×10⁶` (or 4.0 at 0.4) — rectangular
vs this project's `3.00×10⁶` real-J value. With the real hull offsets now
in hand, the two should collapse to one number by replacing `T·L⁴/64` with
`J`.

Crucially, Braithwaite **keeps** the Clarke linear terms (`Yv·v+Yr·r,
Nv·v+Nr·r`) that this project rejected — same merchant-ship regressions,
same overprediction for a trireme, but not flagged in his code.

| Question | This project | Braithwaite |
|---|---|---|
| Yaw damping form | `Ω·ω\|ω\|` (cross-flow integral over real hull) | `Nr2·r\|r\|` (rectangle approximation, same physics) |
| Value | 3.00×10⁶ (grounded from real hull, neutral fit) | 8.0×10⁶ at CN0.8 / 4.0 at CN0.4 (rectangular) |
| Linear terms | Tried, rejected (100× too much) | Kept (same regressions, not flagged) |
| Sideways | `ρ·A_lat·\|u\|·v`, A_lat 30.09 from hull | `Yv·v+Yr·r` + coupled mass matrix |
| Heel effect on turning | OFF spike (negative result) | Not modelled (GM/heel only in prose) |

---

## 5. The rudder — same idea, different bookkeeping

Both use the same flat-plate foil theory.

**This project** (Taylor ch.31, empirical):
- Straight drag `39.4·V²` newtons (V in knots) — measured by towing with
  and without rudders. Applied helm multiplies by 1.4 at full (67.5°) →
  induced `15.8·V²`; efficiency `0.045` (wake × shape × single-rudder ×
  ventilation ≈ 0.5×0.6×0.5×0.3). Lateral force is a fraction of drag:
  `0.14+0.020·angle−0.00015·angle²` (40–80% → sideways). Turning moment
  is that force × 14.9 m (distance from centre to rudder). Angle
  dependence is in the lateral fraction, not in the drag factor (which
  stays 1.4 to first order). Keel arms `arm_lat 1.46 m / arm_rud 1.16 m`
  and stability `GM 0.97 m` from Table 31.1.

**Braithwaite** (Hoerner flat-plate at the rudder stock):
- Position `√(X²+Y²)` (`X=−15 m` for Olympias), local flow
  `Vrx=u+pos·cos(rudder angle)·r, Vry=v+pos·sin·r`, both rudders
  `Area 0.75 m²` each (1.5×0.5 m), `CL=sin(2·AoA), CD=2·sin²AoA`,
  `Lift=0.5·ρ·Area·V²·CL`, `Drag=0.5·ρ·Area·V²·CD + 0.5·(137·V²+0.65·V)·
  Area/1.5 + viscous`, moment `RY·X − RX·Y`. The parasitic
  `137·V²+0.65·V` is the same "half the ship's drag at zero angle"
  figure — just written as a fitted curve.

Same `CL=sin2α, CD=2sin²α`. At 7 knots Braithwaite's parasitic
`137·3.6²=1778 N` vs this project's straight `39.4·49=1931 N` — 8% apart,
independent confirmation of the same tow measurement.

---

## 6. How time is stepped

| | This project | Braithwaite |
|---|---|---|
| Time step | 0.02 s (ship), 0.001 s inside the force-driven oar | 1 s (spreadsheet, 10-s blocks stepped by copy-paste macros Ctrl+A/B) |
| Oar stepping | Average over 4 cycles at `t_drive/600`, bisection 0.5–6.5 m/s × 50 tries for the burst speed | 4-phase angle curves (parabolas/cubics), secant iteration per step for the oar's spin |
| Stability checks | Surge ripple 0.2 knots physical; dt convergence <0.3% gate | No dt study shown |
| Interpolation | Straight lines with flat ends (if outside the table, use the nearest value) | Lagrange quadratic (curved, slopes jump at mid-intervals) + natural cubic splines; one bisection uses `3.14` for π (0.05% error) |

---

## 7. How each model is checked

**This project** has 159–162 automated checks (the gate structure). Every
number must land within a set band or the test fails:

- One-oar: within 0.5% of the rigid-oar reference; handle force 223 N at
  cruise, thrust and efficiency checked.
- Surge: burst speed 6.89/7.22/7.58/7.99 knots vs chain 7.0/7.2/8.0/8.2 at
  hull 1.08 (−1.6/+0.3/−5.3/−2.7%; fair hull 1.0 +0.0/−0.2/−3.6). Force
  mode at hull 1.0 6.65/7.13/7.62 vs Olympias chain 6.57/7.15/7.69
  (+1.2/−0.2/−1.0). Sprint 44.5 at 130 oars bursts near 7.65 vs
  trial 8.2–8.4.
- Turns: G1 +2.4%, F1 +7.6% (gate widened 7→8.5% for the grounded mass),
  tightest −2.7% — all pass. Per-station inverted (G1 90→128/134,
  F1 118→232/264) kept OFF — doesn't give the right pattern.
- HL vs LL (calibration `calib-2026-08-29-84c8893`): turn size error
  <1.3%, turn time within 20%, settled orbit 1.03–1.09×, cruise mean
  +0.0–0.7%.

**Braithwaite (Rev F):** Sections 6 (Validation) and 7 (Software
Architecture) are one-line stubs. The appendix's code is absent.
Calibration is a few lines of prose scattered through the text: "Nr
changed to a constant to give the observed turning rate at zero
velocity" (the same quadratic-yaw choice this project makes), "calibrated:
CN = 0.40 reproduces turning circle" (code says 0.80). No plotted fits,
no error numbers, no pass/fail bands. The report's checkable anchors —
stationary turn 3.5°/s at 27 strokes/min (116 oars), zig-zag 8° then 7°,
top speed 9.95 knots with all 170 oars — are numbers to compare, not
tests that pass.

---

## 8. The three open gaps — seen through both models

| Gap | This project | Braithwaite would say | Together |
|---|---|---|---|
| **Full 360° turn too fast** (95 s vs 128 s, −26%) | Settled speed 3.4 knots vs trial's 2.9 mean. Tested: linear yaw drag tested and rejected (breaks every turn size by +24–31%); turn build-up ~2 s, yaw/oar differential ~1 s — both too small; heel spike 95→102 s then breaks diameters. | Not re-tested on this scenario (his sheet runs 70 s: 4→1.78 m/s, heading 0.317 rad at 15 s with lever 5.2, CN 0.8). His stationary anchor 3.5°/s (102.9 s for a full circle) sits *between* this project's 95 s and the trial's 128 s — between, not decisive. | Both bracket the gap. Braithwaite's per-station flow hints that the fitted lever's missing 400 kN·m·s of damping explains the inverted station layer — but not this speed floor. The fix must be turn-specific (brake, crew floor `P_crit`, or residual drag) without breaking the burst that already works. |
| **Sideways lean too small** (1.4° vs 7.8–15°, 5–10× low) | Hull sideways resistance `ρ·A_lat·\|U\|·v ≈ 6900 N` vs the need to turn `m·U·ω ≈ 8192 N` — need area ≈6 m² for 8.5° vs real 30.09 m² (measured from 21 hull sections). Clarke-type linear terms gave 100× too much for this hull — rejected. Heel spike moves 1.7°→3.5° but breaks diameters. | Uses the same Clarke merchant-ship formulas (same 100× overprediction, but kept). No drift number given; the same physics can't reach 7.8° without help either. | Both have a drift gap. This project's linear sideways model vs Braithwaite's coupled mass matrix give different numbers but neither reaches 7.8° alone. The coupled mass matrix is not the fix (this project rejected the same terms). |
| **Cruise speed falls behind at high stroke rates** (−0→−3.6% fair; −2.5→−6% against the Mark II table) | Efficiency per oar drops 0.79→0.69 with rate while the simple model assumes constant 0.76; burst from bare oar, sustained from crewed Ship settles at `P_crit ≈ 6.1 knots` at any rate. Blade area ×1.45 closes the low end. | Linear `81·(1−V/18)` vs this project's `½ρACN·v·\|v\|` — at 7.2 knots: 48.6 N/oar vs ~17 N cycle-mean. Not comparable — his is peak per side, this project's is cycle-average. His top speed 9.95 knots (170×81 N vs drag at 9.95) vs this project's 7.22 at 28.8 show the 81 N figure is a different abstraction. Holtrop check rules out hull drag as the cause in both. | Not the hull. The gap lives in the blade/timing — not in which hull-drag curve you pick. |

---

## 9. What each model gives the other

**Where Braithwaite helps this project:**

- Stationary turn 3.5°/s and zig-zag 8°→7° as extra boundary data.
- Blade area 0.113 m² — independent confirmation that the effective
  0.078 m² is `0.113 × 0.69` (85% underwater × 81% shape efficiency) and
  that the lift the flat-plate law leaves out (~55% at some angles) is
  being absorbed by the calibration.
- Oar inertia 30 kg·m² (zygian) confirming the Table 3.1 anomaly is in
  the source, not a copy error.
- The per-station `V_local = forward speed ± lever × spin` flow and the
  Figure 16 oar-station plan — a path to unpack the fitted 4.8 m lever
  into per-station blade positions (if the figure is decoded at high
  resolution).

**Where this project helps Braithwaite:**

- The chain's `W(V) = 155V³ + 4.13V⁵` as the trial-checked alternative to
  his 10–22% low cubic.
- Real hull numbers from the actual drawings (mass, area, `J`, `Ω`,
  lever) that would let him replace `T·L⁴/64` by real `J` and settle the
  0.4 vs 0.8 coefficient dispute.
- The per-tier energy/tempo/feather model he doesn't have — why his 170-
  oar top speed (9.95 knots, no limit) and this project's burst (7.65
  knots, hull drag only) differ (the 6.0 kJ energy-tank re-anchor).

**What neither can do yet:**

The three gaps are the same through both lenses. No single tweak to
heel, damping, or blade area closes the full 360° speed floor and the
sideways lean without breaking the turn sizes that already pass; the
cruise triple's remaining −0→−3.6% is the rate-dependent blade
efficiency. The verdict from the investigations stands: the gaps need
separate, turn-specific fixes — not one knob.

---

## How to check the numbers yourself

```bash
# Burst speed and turn (now all through ship.py — hull.py is deleted)
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import equilibrium_speed
from common.chain import KT
for r in [28.8, 32.3, 36.0]:
    print(r, round(equilibrium_speed('Olympias', r, hull=1.0)['V']/KT, 2))
"
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship, rate_for_speed, run_turn
from common.chain import KT
s=Ship(rate=rate_for_speed('Olympias',6.0,n_oars=170), helm=('port',1.0)); s.V=6.0*KT; print(round(run_turn(s)['D'],1))
"
```

Braithwaite's powering numbers (trials curve vs Holtrop) are in the
`Powering` sheet rows 55–71 and the VBA `Holtrop`/`Delft` routines — the
fast model's `VSTAR` grid (8.540 knots at 44.5 spm, 9.80 at 50 spm, …)
in `simulation/hl/curves.py` stores the LL's side of the comparison.
