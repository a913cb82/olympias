# Lane 4 — Oars & Propulsion: the Braithwaite workbook — the trials thrust law, the resistance fits, the top speed

Source: `sources/galley-sizing-xlsm/` (the author's design tool, fully
decoded — the Powering sheet + the VBA `OarForces`/`Holtrop`/`HoltropV`/
`DelftResistance`; see `sources/galley-sizing-xlsm/DECODE.md`) and the RINA
draft paper (`sources/warship-evolution-6th-bc/DECODE.md`).

## 1. The trials thrust law — independent agreement with our chain

- The workbook's oar model (VBA `OarForces` + the Powering sheet):
  **mean thrust 81 N/oarsman at zero speed, falling linearly to zero at
  18 kts (9.252 m/s)**, applied per side with the local blade speed
  (u ± lever·r) — "calculated for Olympias at different speeds using
  acceleration trial data" (the paper §3.6). `[x]`
- Our LL's force-mode equilibrium at V = 0, 38.75 spm: **~82 N/oar** —
  two independent derivations from the same trials agree. ✓
- The shape differs: the workbook's linear fall vs our blade-law equilibrium
  (the self-balancing drive). The 18-kt zero-crossing vs our curve `[?]`
  (the extrapolation above the trial speeds).

## 2. The trials bare-hull resistance fit vs our hull law

- The Powering sheet's trials column ("cf ref 1 p82" — the Trireme Trust
  Trials 1988 report): **R = 40.2·V²** (V in kt, 1–6 kt), **75.2·V² − 1560**
  (7–8 kt), **88.6·V² − 2640** (9–10 kt) N. `[x]`
- Our chain's law W = 155V³ + 4.13V⁵ (V in m/s) at the same speeds:
  | V | trials fit | our law | ratio |
  | --- | --- | --- | --- |
  | 8 kt | 3253 N | 3808 N | 0.85 |
  | 10 kt | 6220 N | 6994 N | 0.89 |
  Same trials data, two fits — the chain's law sits 12–15 % above the
  workbook's bare-hull fit `[?]` (loading condition, the rudder
  contribution, the fit families differ — reconcile).
- Holtrop (the workbook's VBA): 2322 N @ 8 kt, 3514 N @ 10 kt — 71 % / 56 %
  of the trials fit — **the workbook's own data shows Holtrop under-
  predicting at the top speeds**; the paper's "Holtrop was a close match"
  holds only in the mid-range.

## 3. Top speed — 9.95 kt vs our sprint

- The workbook's Powering: **top speed 9.95 kt (rudders up)** — all 170
  oarsmen at the 81 N law against the trials resistance. `[x]`
- Our LL: sprint 7.72 kt (force mode) / 7.45 kt (kinematic) with the
  **130-effective-rower** head-room; the trials' measured 8.2–8.4 kt
  (Rankov ch.9). The gap between 9.95 and 8.2–8.4 is the **effective-rower
  question**: the workbook applies the full 170 × 81 N with no thalmian
  shortfall — T1-family material. The measured trials number (8.2–8.4) is
  the anchor; the workbook's 9.95 is the no-head-room bound.

## 4. Oar and rig values

- **Oar 17 kg each** (62×17 = 1054 kg in the Weight sheet) — confirms
  oar-data.md's "17 kg once the lead counterweight was added". ✓
- Blade lever (the blade CoP's distance from the centreline, the turn
  model): 4.5 m (the pentaconter design) / 5.2 m (the Olympias scenario)
  vs our ~4.8 m — ballpark agreement. ✓
- The workbook's oar thrust is applied at x = LWL/2 with the lever ±4.5–5.2 m
  — a two-point oar model (the paper §3.6), no per-oar kinematics.

## 5. The ram (context)

- "Energy to cause failure in Olympias structure" = **830 J** (Ref 2 p 220)
  → minimum ramming speed **0.37 kt** relative. `[x]` — context for the
  ramming-tactics background (the paper's subject), not part of the chain.

## Consequences for the chain

1. The 81 N/oar agreement validates the LL's zero-speed thrust anchor.
2. The resistance-fit family (40.2/75.2/88.6·V²) is a second fit of the same
   trials data — the 12–15 % offset vs the chain law should be reconciled
   (loading condition, rudder drag inclusion).
3. The 9.95 kt bound sharpens the sprint question: the effective-rower
   head-room is the whole gap between the workbook's bound and the trials.
