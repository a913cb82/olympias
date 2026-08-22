# Lane 5 — Manoeuvring: the Braithwaite 3-DOF model — CGH derivatives, the cross-flow yaw damper, the rudder model

Source: `sources/galley-sizing-xlsm/` — the Manoeuvring + Simulation sheets
and the VBA `ManAcceleration`/`OarForces`/`RudderForces` (fully decoded in
`sources/galley-sizing-xlsm/DECODE.md`); the RINA draft paper's §3.6
(`sources/warship-evolution-6th-bc/DECODE.md`).

**Headline: an independent, trial-tuned 3-DOF model of the same ship — the
same cross-flow yaw-damping physics as our Plan 2 audit.**

## 1. The model (VBA `ManAcceleration` — the paper §3.6 in code)

- Equations (body-fixed, surge/sway/yaw):
  (m − Xu̇)·u̇ = X_ext + m·v·r
  (m − Yv̇)·v̇ − Yṙ·ṙ = Yv·v + Yr·r − m·u·r + Y_ext
  −Nv̇·v̇ + (Iz − Nṙ)·ṙ = Nv·v + Nr·r + **Nr|r|·r|r|** + N_ext
- Hull derivatives: **Clarke, Gedling & Hine (1983)**, prime-I system, all
  eight forms (Y'v̇ = −π(T/L)²(1+0.16·Cb·B/T−5.1(B/L)²); Y'ṙ; N'v̇; N'ṙ; and
  the damping Y'v, Y'r, N'v, N'r), dimensionalised ½ρ·U·Lⁿ. `[x]` (code read)
- Surge added mass Xu̇ = 0.04 + 0.06·CB (as the paper). The sway-yaw mass
  matrix solved by Cramer's rule.
- **Inertia Iz = m·(L/3)²** — the paper's "Rg = XX% LWL" from the 1:24 model
  pendulum tests; for the Olympias scenario: 45.38 t × (10.78 m)² =
  **5.28e6 kg·m²**. `[x]` (our LL's Iz — reconcile `[?]`)

## 2. The nonlinear yaw damper — the cross-flow audit's sibling

- `Nr2 = −ρ·CN·T·L⁴/64` — "the closed-form result of integrating the
  sectional cross-flow drag (½ρ·Cdc·(rx)|rx|·T) along a rectangular lateral
  projection from −L/2 to +L/2" (∫x|x|dx = L⁴/64; the sign convention makes
  the odd integral the L⁴/32-type result — the paper's draft has the factor
  loose, the code is the executable). `[x]`
- **CN = 0.4 in the paper text, CN = 0.8 in the code** (whose own comment
  says "Calibrated: CN = 0.40 reproduces Olympias sea trials turning
  circle"). `[?]` — flag: which value was used for the paper's turns?
- vs our audit (`crossflow.py`): the same ½ρ·C_D·∫d(x)·|x−X_cg|³dx family;
  our tapered-plane + ram integral closes the fitted Ω at C_D = 0.30;
  the workbook's rectangular projection with C_D = 0.4 gives
  ρ·0.4·T·L⁴/64 = 7.6e6 (2.3× our 3.25e6) and with 0.8 → 1.5e7.
  **With the real lines now in hand (lane-3/braithwaite-workbook.md), the
  rectangular projection can be replaced by the real sectional draughts and
  the CN question settled.**
- The turning scenarios the model was tuned to: the Olympias from 4 m/s
  (7.8 kt) with **both rudders 67°, rudders down, starboard pressure 1.0**,
  blade lever 5.2 m — trajectory stored (U decays 4 → ~1.78 m/s through the
  turn; heading 0.317 rad at 15 s). `[x]` (Manoeuvring/Simulation sheets)

## 3. The oar forces in the turn (VBA `OarForces`)

- Per-side thrust = pressure·(n/2)·81·(1 − V_local/9.252) with
  V_local = u ± lever·r — the differential thrust drives the yaw moment;
  **no sway force at all** (the turn is purely yaw-moment + the hull
  derivatives). vs our LL: per-side thrust with the blade law and the sway
  coupling from the hull's lateral force. The steering conventions differ;
  the trials turns are the common anchor.

## 4. The rudder model (VBA `RudderForces`)

- Flat-plate foil: **CL = sin(2αrel), CD = 2·sin²(αrel)** (Hoerner),
  resolved with the local flow at the rudder stock (u, v, r contributions);
  **plus the trials parasitic drag: 0.5·(137·V² + 0.65·V) N scaled by
  (2·A/1.5)** — the Olympias rudders' zero-angle drag ~ "half the total
  ship drag" (the paper §3.6). `[x]` — vs our rudder pair's drag: the
  137/0.65 law is a second, trials-derived fit of the same phenomenon —
  cross-check `[?]`.

## 5. The scenarios

- Olympias: 4 m/s entry, 67° both rudders, rudders down, starboard
  pressure 1.0 (the tight-turn case); the Design (pentaconter bireme):
  14.41 t, Iz 4.74e5, 50 rowers, 4.5 m lever, same rudder angle.
- The paper's designs chapter never filled in the bireme performance
  table (draft placeholders) — the workbook's trajectories are the
  numbers it intended.

## Consequences for the chain

1. The independent model confirms the cross-flow yaw-damping physics (the
   Plan-2 audit's family) and gives a second calibration point (CN ≈ 0.4,
   paper) for the C_D band.
2. With the real lines (lane-3), replace the rectangular projection in the
   workbook's closed form with the real lateral plane — the CN 0.4 vs 0.8
   split and our C_D = 0.30 should collapse to one value.
3. The rudder parasitic-drag law (137V² + 0.65V) is a trials-derived
   cross-check for our rudder pair's drag.
4. Iz = m(L/3)² = 5.28e6 is an independent inertia estimate — reconcile
   with the LL's Iz.
