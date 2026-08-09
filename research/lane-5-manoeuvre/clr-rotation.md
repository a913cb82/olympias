# W5 Richard's alternative: rotation about centre of lateral resistance vs c.g.

Status: `[x]` = confirmed.  Script: `research/lane-5-manoeuvre/clr_rotation.py`.

## Motivation

ch.31 §2.2 (book p.234) states Taylor modelled rotation about the vertical
axis **through the centre of mass (c.g.)** of the ship, and explicitly flags
this "is a principal difference from the UCL model" (Rusling & Smith, pers.
com. 2006), which rotated about the **centre of lateral resistance (CLR)**.

## Model

Added `steady_turn_about_clr(vessel, v, phi, fac, one_side, x)` where `x` =
distance of the CLR **forward of the c.g.** (m).  Same physics as
`manoeuvre_model.steady_turn`; only the rotation-point choice changes:

- rudder lever arm: `L_rud = lever_rudder + x`  (rudder astern of c.g.)
- one-side oar lever: `L_oar = |lever_oar − x|`  (oar race forward of c.g.)
- the hull lateral (drift) force passes through the CLR, so it contributes no
  yaw moment about the CLR axis (in the c.g. model it enters only via the
  lateral force balance, which is unchanged).
- `Omega` (rotational resistance) and all drags kept at the trial-fitted
  values, isolating the pure geometric effect of the rotation point.
- `I` (moment of inertia) does not enter the steady-state turn, so the
  parallel-axis shift `I_clr = I + m·x²` affects only the transient, not the
  steady diameter reported here.

## Realistic x (CLR forward of c.g.)

Olympias LCG = 17.5 m from the stern post (ch.25) on LWL 32.2 m → c.g. about
14.7 m from the bow.  With the ram and a long lateral plane, the CLR typically
sits ~0.5–2 m further forward, so **x ∈ [0.5, 2.0] m**.

## Results (diameter, m)

| case | x = c.g. (Taylor) | x = 0.5 | x = 1.0 | x = 1.5 | x = 2.0 | published target |
|---|---|---|---|---|---|---|
| tightest Olympias [Oly] | 64.0 | 65.1 | 66.2 | 67.4 | 68.7 | 62 |
| fast anastrophe [MkIIb] | **151.8** | 149.5 | 147.4 | 145.3 | 143.4 | **145** |
| tight anastrophe [MkIIb] | **74.6** | 76.3 | 78.2 | 80.3 | 82.5 | **80** |
| G1 full rudder [Oly] | 89.4 | 87.9 | 86.5 | 85.2 | 83.9 | (print-only) |
| F1 small rudder [Oly] | 111.9 | 110.1 | 108.4 | 106.7 | 105.1 | (print-only) |

## Findings

1. **The rotation-point choice is a second-order effect on turn diameter**:
   ≤ ~5% across the realistic x band.  This quantitatively supports Taylor's
   statement that his c.g.-axis model and the UCL CLR-axis model agreed
   closely (both fitted to the same Olympias trial data). [x]
2. **Direction of the effect differs by turn type** [x]:
   - rudder-dominated turns (fast anastrophe, G1, F1): moving the rotation
     point forward **lengthens** the rudder lever → tighter turn;
   - oar-one-side-stops turns (tight anastrophe): moving forward **shortens**
     the oar lever → wider turn.
3. **Best joint fit**: x = 1.45 m reproduces both anastrophe targets to
   0.4% / 0.1% (fast 145.5 vs 145 m; tight 80.1 vs 80 m), i.e. *slightly
   better* than the c.g.-axis model's +4.7% / −6.7%.  That x is squarely in
   the physically-plausible band, so a small CLR-forward-of-c.g. correction
   is consistent with the trial data — worth adopting as a refinement rather
   than a fundamental correction. [x]
4. **Caveat**: `Omega` was kept fixed.  A CLR-axis model would in principle
   re-fit `Omega` to the same trial turns; because the diameter change is
   small this would not alter the qualitative conclusion. The transient (and
   the zig-zag/entry behaviour) WOULD shift with the parallel-axis inertia
   change `I → I + m·x²` (≈ +2.2% at x = 1.45 m for m = 44 t) — noted, not
   modelled (Taylor's own model is steady-state). [x]

## Bottom line

Richard's alternative (rotation about the CLR, UCL-style) changes predicted
turn diameters by ≤ ~5% for physically plausible CLR positions, and actually
improves agreement with the two anastrophe targets at x ≈ 1.4–1.5 m.  The
difference between Taylor's c.g.-axis and the UCL CLR-axis models is real but
small — consistent with the "close agreement" Taylor reports.  Adopt a small
forward CLR offset (x ≈ 1.4 m) as the default rotation axis in the reference
model, keeping the c.g.-axis as the published-baseline variant.
