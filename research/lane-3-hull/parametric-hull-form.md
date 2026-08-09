# Parametric hull form (Step 1: W2)

Reconstruction of the Olympias underwater hull form from the anchors
available in the text, using a parametric circular-arc geometry.  This is
the geometry deliverable for Lane 3 (W2 hull form / resistance).

## Why parametric, not offsets

- Coates defines the sections in Plan 3 as circular arcs, but no numeric
  offsets appear in the text (the drawings are images; the assistant
  cannot rasterise them).
- Rather than fabricate a table of offsets, the hull is represented by a
  small parametric model with two free parameters `p` (waterline planform
  fullness) and `q` (rocker) plus the fixed anchors below.  `p` and `q`
  are fitted so that displacement matches the BMT trial and light-ship
  numbers.

## Fixed anchors

| Anchor | Value | Source |
|---|---|---|
| LWL | 32.2 m (32.08 m) | Taylor T31.1 / Poitiers |
| Waterline beam | 3.430 m | Poitiers model from Coates lines |
| Trial draft | 1.1 m | Taylor T31.1 |
| Trial displacement | 42.25 t (41.22 m3) | BMT ch.25, 80-kg crew |
| Light displacement | 25.80 t (25.17 m3) | BMT ch.25 |

## Geometry model

- Waterline half-breadth:  B(x) = Bmax * sin(pi x)^p ,  x in [0,1]
  (Bmax = 3.430/2 = 1.715 m).  p=1.5 gives full ends but slightly
  fuller middle than a sine.
- Rocker:  local draft d(x) = dmax * sin(pi x)^q .  q=0.8 raises the
  ends (reduces draft there) while keeping dmax = 1.1 m amidships.
- Transverse sections: circular arcs with the chord at the waterline and
  arc apex on the keel.  Section area = R^2(theta - sin theta)/2 with
  R = (B^2 + d^2)/(2d), theta = 2 asin(B/R).
- Volume, wetted surface and LCB integrated by 1D quadrature over x.

## Fit result

p = 1.5, q = 0.8, Bmax = 1.715 m

| Quantity | Model | Anchor / BMT | Error |
|---|---|---|---|
| Trial volume | 41.35 m3 | 41.22 m3 | +0.3% |
| Light volume | 25.17 m3 | 25.17 m3 | 0% |
| Light draft | 0.694 m | - | - |
| Wetted surface (trial) | 81.3 m2 | - | - |
| Wetted surface (light) | 71.0 m2 | - | - |
| Cb | 0.340 | - | - |
| Cwp | 0.556 | - | - |
| LCB (from stern) | 16.10 m | - | - |
| VCB above keel | 0.493 m | - | - |

Volume sensitivity: across p in {1.0,1.4,1.5,2.0} and q in {0.6,0.8,1.0}
the model spans 37-48 m3, wetted surface 75-85 m2.  The fit is robust:
no combination reaches 0.3% error except (1.5, 0.8), and that lands on
the trial anchor.

## Friction cross-checks

### vs Shaw's power law (155V^3 + 4.13V^5)

Skin friction (ITTC 1957, rho=1025, nu=1.14e-6) using the computed
wetted surface, compared to Shaw's total power at the same speed:

| Speed | Rf | Rf*V | Shaw W | friction fraction |
|---|---|---|---|---|
| 2.0 m/s | 378 N | 0.8 kW | 1.37 kW | 55% |
| 3.5 m/s | 1065 N | 3.7 kW | 8.82 kW | 42% |
| 4.3 m/s | 1561 N | 6.7 kW | 18.4 kW | 36% |

Caveat flagged in earlier work: at 6.8 kt (3.5 m/s) friction is only
42% of Shaw's total, which reads low against Coates ch.22 (skin
dominant below ~6 kt).  Two possibilities: (a) Shaw's law includes
bare-hull plus gear/rudder drag and does not equal the bare-hull
resistance curve alone; (b) the true wetted surface is larger than the
lean circular-arc estimate.

### vs Taylor bare-hull drag (T31.1 row 3: 40.2 v^2 N, v in kt)

This is the cleaner comparison because T31.1 explicitly gives bare-hull
drag.  The model reproduces the right physics split:

| Speed | Rf | % of Taylor Rt | wave residual | % |
|---|---|---|---|---|
| 4.0 kt | 398 N | 62% | 245 N | 38% |
| 5.0 kt | 602 N | 60% | 403 N | 40% |
| 6.0 kt | 844 N | 58% | 603 N | 42% |
| 6.7 kt | 1035 N | 57% | 769 N | 43% |
| 8.0 kt | 1439 N | 56% | 1134 N | 44% |
| 9.0 kt | 1791 N | 55% | 1466 N | 45% |

Friction stays dominant (55-62%) across 4-9 kt and the wave residual
grows with speed, exactly matching Coates' description that skin
resistance is dominant below ~6 kt and wave-making becomes equal only
near ~9 kt.  This gives confidence in the wetted-surface estimate
(~81 m2) - a larger hull would push friction above Taylor's bare-hull
number and force a negative wave residual.

## Stability mismatch (important)

| Quantity | Model | BMT ch.25 |
|---|---|---|
| VCB | 0.493 m | - |
| I_t | 38.5 m4 | - |
| BM | 0.935 m | ~2.2 m implied |
| KM | 1.428 m | 2.90 m |
| GM | -0.34 m (at KG 1.77) | 1.13 m |

The circular-arc waterplane (Cwp 0.556) is too lean: BMT's KM = 2.90 m
implies BM ~2.2 m, i.e. I_t ~93 m4, close to the rectangular-waterplane
value L*B^3/12 = 108 m4.  The real Olympias is fuller and flatter-
bottomed than a pure circular arc.

**Action for Lane 5 (manoeuvring): do NOT use model KM/GM.  Use the
measured BMT values KM = 2.90 m, GM = 1.13 m at the trial condition.**
The parametric hull is adequate for volume, wetted surface and
resistance, but the transverse stability inputs come from the BMT
stability report.

## Files

- `hull_form.py` - parametric model, fit, friction and stability checks
- `hull-form-summary.csv` - derived hydrostatics table
- `offsets-eliav.md` - displacement resolution (antecedent)
