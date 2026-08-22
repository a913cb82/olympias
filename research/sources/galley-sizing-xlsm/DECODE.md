# Decode: "Galley sizing Y.xlsm"

Source: `Galley sizing Y.xlsm` (693 KB, Excel 2007+ with VBA). Author:
**Richard Braithwaite** (the "Readme" sheet + the comment authors). The
concept-design tool behind the RINA draft paper (see
`warship-evolution-6th-bc/DECODE.md`). Decoded artifacts in this directory:
`sheet_<name>.tsv` (every cell: ref, formula, cached value), `vba_extracted.txt`
(all 17 VBA routines), `basis_hull_offsets.tsv` (the raw Olympias offset
table), `extracted/` (the OOXML package).

## Sheets

| Sheet | Content |
| --- | --- |
| Readme | Tool documentation: hull transformations (linear L/B, separate depth/draught scaling, Cp fore/aft, LCB swing factor, midship-section factor), the basis-hull input format (up to 21 sections × 27 Z/Y pairs, chines at odd nodes), the interpolation functions (CUBIC cubic splines; Interpolate Lagrange-quadratic with discontinuous slopes; CUBIC2 lines-plan variant), references (Coates/Platis/Shaw Trireme Trust Trials 1988; Rankov Final Report 1998) |
| Input | The current design (a **pentaconter bireme**: 26 zygian + 24 thalmian rowers, LWL 17.2 m, BWL 2.8 m, T 0.759 m, 14.41 t displacement vs 14.48 t weight — "BALANCED DESIGN"); thole heights, blade lever 4.5 m, 2 rudders (0.25 m², 0.96×0.26 m), resistance method Holtrop, outrigger/stern-platform/canopy flags |
| Weight | The **Olympias weight breakdown** (the base design): HULL 19.84 t (VCG 1.855 m), PROPULSION 4.95 t (2.037), OUTFIT 0.45 t, ARMAMENT 0.225 t (ram 200 kg), VARIABLE LOAD 19.8 t (170 oarsmen × 75 kg, water 2.8 t, crew effects 2.0 t) → **lightship 25.75 t @ VCG 1.905 m; full load 45.5 t**. Scaled with 24³ (the 1:24 model), "Adjustment to match inclined wt" 670 kg; oars 17 kg each; rudders+tillers 144.6 kg; hypozomata 100 kg |
| Powering | Ship data (Olympias: LWL 32.35, B 3.7, T 1.15, 44.26 m³, WSA 130.5 m², Cb 0.321, Cp 0.691, Cm 0.465, Cw 0.768); the **trials bare-hull resistance** ("cf ref 1 p82"): 40.2·V² (1–6 kt), 75.2·V²−1560 (7–8), 88.6·V²−2640 (9–10) N, V in kt; the ITTC-1957 Cf column; the Holtrop column; the **thrust law** (81 N/oar → 13.71 kN at 0 kt, linear to 0 @ 18 kt); **top speed 9.95 kt (rudders up)**; ram: 830 J structure-failure energy (Ref 2 p220) → min ramming speed 0.37 kt |
| Manoeuvring | The **3-DOF sim in spreadsheet form** (1 s timestep, 10 s blocks): Olympias scenario — L 32.35, B 3.704, T 1.15, m 45.38 t, **Iz = m·(L/3)² = 5.28e6 kg·m²**, Cb 0.321, 170 rowers, blade lever 5.2 m, 2 rudders (0.75 m², 1.5×0.5 m, 15 m aft of CG), **rudder angle 67°, rudders down, U₀ = 4 m/s, starboard pressure 1.0**; the Design scenario (pentaconter bireme: 14.41 t, Iz 4.74e5, 50 rowers, blade lever 4.5 m, rudders 0.25 m² @ 7.98 m aft, same 67°); trajectories (CG X/Y/heading, u/v/r) |
| Simulation | The stored trajectories for both designs (Olympias: turn from 4 m/s with both rudders 67° down — U decays 4 → ~1.78 m/s through the turn; heading 0.317 rad at 15 s); the Design's parallel run |
| Basis Hull | **The Olympias offsets from the Lines Plan** (21 stations × 27 Z/Y pairs, LWL 32.35 m, spacing 1.6175 m; `basis_hull_offsets.tsv`); Bonjean/VMOM/HMOM/girth per station; **hydrostatics at the design WL (Z = 1.15 m)**: displacement 44.26 m³ moulded, LCB 15.67 m from AP, LCF 15.25 m, VCB 0.846, BMT 1.967, BML 118.5, WSA 130.5 m², Cw 0.768, Cp(f/a) 0.657/0.725, Cb 0.321, Cm 0.465 |
| Transform | The transformed design hull (the pentaconter bireme's offsets + hydrostatics: 14.06 m³, WSA 49.2 m², LCB 8.40 m from AP, LCF 8.30 m, Cb 0.363, Cw 0.661, VCB 0.525, BMT 1.55, BML 38.1) |
| Lines | Chart sheet: "LINES FOR TRANSFORMED DESIGN" (the body plan of the design) |

## VBA (17 routines — `vba_extracted.txt`)

- **Module7 — the physics sim** (the paper §3.6, in code):
  - `ManAcceleration(...)` — 3-DOF (surge/sway/yaw) with the Clarke–Gedling–
    Hine (1983) prime-I derivatives (Y'v̇, Y'ṙ, N'v̇, N'ṙ, Y'v, Y'r, N'v, N'r —
    the full Clarke et al. forms), dimensionalised ρ/2·U·Lⁿ; the coupled
    sway-yaw mass matrix solved by Cramer's rule; surge added mass
    Xu̇ = 0.04 + 0.06·CB; **the nonlinear cross-flow yaw damper:
    Nr2 = −ρ·CN·T·L⁴/64 with CN = 0.8** (comment: "Calibrated: CN = 0.40
    reproduces Olympias sea trials turning circle" — the code value 0.8 and
    the comment/paper value 0.4 disagree `[?]`).
  - `OarForces(oarNumber, bladeLever, portPressure, starboardPressure,
    maxThrust, u, v, r, Output)` — per-side thrust =
    pressure·(n/2)·maxThrust·(1 − V_local/9.252), V_local = u ± lever·r;
    yaw moment = ±thrust·lever; **no sway force** (turns are differential-
    thrust driven).
  - `RudderForces(...)` — the flat-plate foil: CL = sin(2α), CD = 2·sin²α
    (Hoerner), lift/drag resolved to X/Y with the sign checks; **the parasitic
    drag from the Olympias trials: drag2 = 0.5·(137·V² + 0.65·V) scaled by
    area/1.5** (the "half the total ship drag at zero angle" figure).
  - `Holtrop(...)`, `HoltropV(...)` — full Holtrop–Mennen (viscous +
    wave-making, no bulb/transom); `DelftResistance(...)` — the Delft
    systematic yacht series (Keuning & Sonnenberg 1998), 11 Froude stations
    with the A0–A8 polynomial tables (Fn 0.10–0.60).
  - `CUBIC/SPLINE/SPLINT/CUBIC2` (Numerical-Recipes splines), `Interpolate`
    (Lagrange quadratic), `Lininterp`, `WLS` (waterline-section tangent
    finder), `transfer`/`updata` (sim↔sheet macros, Ctrl+a / Ctrl+b).

## The physics, compared with our chain

| Item | This workbook | Our chain | Status |
| --- | --- | --- | --- |
| Yaw damper | −ρ·CN·T·L⁴/64, CN 0.4–0.8 `[?]` | ½ρ·C_D·J, C_D = 0.30 (drag crisis) | Same cross-flow physics; the rectangular-projection coefficient vs our tapered-plane J — a reconciliation is now possible with the real offsets |
| Zero-speed thrust | 81 N/oar (trials) | ~82 N/oar (LL equilibrium @ 38.75 spm) | ✓ agree |
| Resistance | Trials fit ~40.2–88.6·V² (N, kt); Holtrop underpredicts at high speed | 155V³+4.13V⁵ (V in m/s) | The workbook's trials curve vs our law: at 8 kt 3.25 kN vs 3.81 kN (~85 %); at 10 kt 6.22 vs 6.99 (~89 %) — **same trials data, different fits — cross-check and reconcile** |
| Top speed | 9.95 kt (170 × 81 N) | 8.2–8.3 kt sprint (130 effective) | The effective-rower question (thalmian head-room) — T1 material |
| Mass | 45.5 t full load | LL ship mass (chain) `[?]` | **Reconcile** — the LL's mass drives m_app and the turn physics |
| Inertia | Iz = m(L/3)² = 5.28e6 | LL's Iz `[?]` | Reconcile |
| Lines | Real offsets (Lines Plan) | Parametric hull_form | **The Plan-2 named path — real CLR/A_lat/J now computable** |
| Hull derivatives | CGH regressions | LL: fitted sway pair | Independent derivation — cross-check |
| Oar blade lever | 4.5–5.2 m (CoP from CL) | ~4.8 m (chain) | ✓ ballpark |

## Flags

- `[?]` CN = 0.4 (paper text) vs 0.8 (code) — which value reproduces the
  trials turns? (The code's own comment says 0.40.)
- `[?]` The workbook's basis hull (LWL 32.35 m, BWL 3.70 m) vs our hull_form
  (LWL 32.2 m, BWL 3.43 m) — two line sets; the difference matters for the
  CLR/A_lat audit.
- `[?]` The 40.2·V² fit at 1–6 kt is purely quadratic — the trials curve
  below 6 kt is thin; our 155V³+4.13V⁵ covers the same points differently.
- `[?]` The workbook's "Design" is a pentaconter bireme (the paper §5.2's
  monoreme block was never filled in).
- The full load (45.5 t) at the design WL (Z 1.15 m, 44.26 m³ moulded +
  skin) is self-consistent in the workbook; our chain's mass needs checking
  against it.

## Next steps (suggested)

1. Port `basis_hull_offsets.tsv` into the hull tooling (`hull_form.py`
   companion or a lane-3 note): recompute the lateral plane, CLR, A_lat and
   the cross-flow J from the REAL lines — closing Plan 2's named gap.
2. Reconcile the mass (45.5 t) and Iz (m·(L/3)²) with the LL's values.
3. Re-run the workbook's ManAcceleration/OarForces/RudderForces model on our
   turn scenarios (the VBA is fully decoded) as an independent simulator.
4. Read the 15 chart objects (the workbook's charts of resistance/thrust/
   trajectories) when a spreadsheet reader is available.
