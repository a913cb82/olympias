# LL behavior-flag scoreboard (the realism-defaults goal)

Goal: every flag defaults to the more complex, more realistic value with
no regressions; regressions fixed by physics, never by simplification.
Both halves required: complexity WITHOUT realism is rejected too.

## Promoted / already realistic (no action)

| Flag | Default | Why it stands |
|---|---|---|
| `force` | `True` | The stroke emerges from demand + inertia + blade force; timing proven dead (lock test) |
| `fleet` | `'spruce'` | Measured 1994 oars; `old-fir`/`None` are research/reference variants |
| `TURNING_POINT` | `"actual"` | Flat-plate identity, locked; `"geometric"` contradicts Table 9.6 kinematics |
| `hold_frac` | calibrated default | Override is the simplification; default is the fitted crew constant |

## Blocked (named physics + unblocker, no regressions allowed)

| Flag | Realistic target | Gap | Unblocker |
|---|---|---|---|
| `stations` → `True` | Per-station positions/flows | Helm +43/+116%, hold −12% (mode-independent; rotation-specific, translation agrees 2%) | Wake-rotation deficit data (surveys/CFD); polar-partial (~−10%, Figure-10); slip unfittable |
| `hill_demand` → `True` | Force–velocity demand | F1 +0.8 m over band, t360 worse, sprint −0.8%; linear form VREF-insoluble | True hyperbolic Hill with published F0/vmax (unpublished); no compensator for F1 |
| `heel_coupling` → `True` | Heel → yaw moment | Excluded: runaway >200k, wrong-sign lateral, diameters blown | Yaw-moment-from-heel via Bonjean (unbuilt, unvalidated) |
| `BLADE_POLAR` → `True` | Angle-dependent blade force | +40% thrust (missing-stall artifact); chain flat-family calibration (A5) bars it | Stall-realistic Figure-10 polar + Shaw-level chain revision |

## Rejected (complexity without realism)

- Surge-only `stations` (2% gain, 10× cost — theater).
- Hold-feathering to close hold turns (circular — relocates the 0.08 fit).
- Slip ~0.8 fitted (uniform — breaks the 2% surge agreement).
- Linear damping for zigzag (structurally impossible — same-ω theorem).
- Symmetric body-overhead term (cancels by accounting identity).
- Blade added-mass (ideal 6–10×, unphysical energy, wrong-direction gaps).

## Declined implementations (correct, not worth it)

- Tier-aware lever (+6% vs several-× gap; churns W5+HL).
- Slender-body potential sidewash for stations (estimated 5–10% deficit → −10–20% damping: rigorous but partial, no promotion; separated part still needs data).
- Full original-rig variant (sub-band effects, W5+HL storm).
- Hull-law switch + HL recal (blocked on drift fix).

## Rule

Inventory audited 2026-09 and complete: scenario inputs (helm, rate,
pressure, state, n_oars, rig) and literature/data constants (CN, oar
families, vessel tables) are not behavior switches; the only module-
level switches are TURNING_POINT and BLADE_POLAR (both tabled above).
No flag moves while any validation gate regresses. Band-widening to pass
is gate-chasing, not promotion. Each blocked flag names its unblocker;
when new sources arrive (Figure-10 numbers, Plan 8, foil data, per-turn
effort, wake surveys), this table says exactly what to retry.
