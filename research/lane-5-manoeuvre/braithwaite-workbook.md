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

## D1 stage-1 verdict (2026-09-12): static VBA-vs-LL reconciliation

Port: `braithwaite_model.py` (this directory — faithful ManAcceleration /
OarForces / RudderForces, no re-interpretation); locks:
`simulation/ll/tests/test_vba_reconciliation.py`.

1. Surge added mass: VBA `0.04+0.06·CB` = **1.059** — inside the
   independent band [1.02, 1.12] (spheroid bound 1.026, LL measured 1.10).
2. Yaw-due-to-sway (CLR physics) **agrees within 27%** (|Nv| 113k vs
   LL 89k N·m/(m/s)) — the restoring moment is robust across derivations.
3. Sway force **disagrees ~11x** (CGH Yv vs Taylor f_hull): CB 0.321 is
   far outside Clarke's regression range — the workbook's calibration
   absorbs it. Regime evidence: the reference implementation (Fossen MSS
   SIMclarke83) demonstrates on a 100 m, Cb 0.80 ship; the trireme (32 m,
   Cb 0.32) is a different animal. This independently rediscovers the drift open item: the
   sway-force channel is THE uncertain channel. Locked as disagreement.
4. Rudder straight drag **agrees 8%** (per-rudder x2 = 1307 N vs LL
   1418 N @ 6 kt) — live corroboration of register C3.
5. Applied-helm rudder forces **diverge 2-7x** (VBA flat plate at helm vs
   LL validated FAC/coeff; VBA lift is coincidentally equal at 22.5/67.5
   by the sin2α symmetry) — stage 2 must run VBA turns: LL turns are
   trial-validated, VBA's are not yet.
6. Cross-flow statics: CN=0.4 → 2.56x LL Omega, CN=0.8 → 5.11x. The VBA
   balance is linear-Nr-dominated (−2.0e6·r dwarfs Nr2 at turn rates);
   the LL's is cross-flow + CLR. Static comparison CANNOT adjudicate the
   CN [?] flag — the trajectory comparison (stage 2) can.

Stage 2 (open): integrate the VBA sim (transfer/updata scheme), run
G1/F1/tightest + top-speed curve vs the LL.

## D1 stage-2 verdict (2026-09-12): VBA turn runs vs trials vs LL

`simulate()` in `braithwaite_model.py` (semi-implicit Euler, dt = 1 s —
the sheet's scheme) reproduces the stored Olympias 30 s run to **0.01%**
at CN = 0.8 (code value), closing two transcription questions en route:
drag = linear interpolation of the integer-kt trials table (sheet K to
0.2%; direct formula is 0.7% off), rudder called per-rudder x2 (t=0
forces exact), and the sheet passes Drag NEGATIVE despite the VBA header
calling it "(positive)". Locks: `simulation/ll/tests/test_vba_turns.py`.

Turn analogues (G1/F1: pressure 0.30 both sides settling ~6 kt, helms in
sheet radians; tightest: the stored port-0/starboard-1 protocol, U0 = 4):

| scenario | trials | LL | VBA CN=0.8 | VBA CN=0.4 |
|---|---|---|---|---|
| G1 D | 89.4 | 92.2 | 117.1 (+31%) | 100.7 (+13%) |
| F1 D | 111.9 | 121.4 | 152.3 (+36%) | 134.9 (+21%) |
| tightest D | 62 | 60.3 | 79.3 (+28%) | 65.0 (+5%) |
| tightest t180 | ~64 impl. | ~49 (fast) | 76 | 65 |
| top (rudd. down) | 8.2-8.3 | 7.67 V30 | 8.77 | 8.77 |

1. CN FLAG ADJUDICATED: 0.4 (paper/comment) beats 0.8 (code) on every
   turn — the comment value reproduces trials better. (The sheet's stored
   run used 0.8; the flag was code-vs-paper, now settled on trajectories.)
2. Even CN = 0.4 turns wide: the VBA model lacks load-bearing turn
   physics (11x-weak sway stiffness per stage 1, no hold brake, huge helm
   drag). The LL's Taylor sway set + brake + validated FAC are
   corroborated BY NECESSITY — an independent model without them fails
   the diameters it was calibrated for.
3. BRACKET on t_360: VBA/CN0.4 nails tightest time (65 vs ~64 s) at +5%
   size; LL nails size at ~75% time. Neither does both — the missing
   turn-speed physics sits between them (slow-wide vs fast-right).
4. Top speed rudders-down 8.77 (CN-independent) sits coherently between
   the LL 130-effective sprint and the workbook rudders-up 9.95.

Protocols differ (sheet full-load 45.38 t vs LL trial 40.95 t; lever 5.2
vs thole-mean 2.00; helm 67.0 vs 67.5 deg; no brake/sway-oar-force) —
verdicts directional. D1 COMPLETE (statics + trajectories).

## Rudder-drag three-way tension (2026-09-12, from the Rev-F text decode)

The Rev-F report quotes the Ref (1) towing fits verbatim (p74 lineage):
bare hull 40.2v² (0–6.7 kt) vs rudders-lowered 76.6v² — increment **36.4
N/kt²**. Two other lines give: VBA drag2 law 0.5·(137V²+0.65V)·(2A/1.5),
V in m/s → per-rudder ×2 = **36.6 N/kt²** (0.5% apart — same analysis);
Taylor Table 31.1 row 3 lineage: 79.6−40.2 = **39.4 N/kt²** (the LL's
value, turn-validated). So 2-vs-1 at ~36.5 vs 39.4 (8% tension).
Plausible cause for part of it: different conditions — Rev-F Table 2
uses draught 1.08 m / 46 t (incl. added mass) / LWL 33 m (GA drawing) /
beam 3.6 m (midship section), vs the LL's trial-WL lines (1.10 m,
40.95 t, LWL 32.35 m, BWL 3.704 m); a 4% drag-level difference between
conditions is unsurprising, and the LWL/beam/draught discrepancies are
their own evidence tension (lane-3 territory).
Verdict: LL stays at 39.4 — it is the turn-validated set (G1/F1/tightest
close on it in OUR condition); the 8% source tension is recorded, needs
Ref (1) p74 vs p82 to resolve. The D1 straight-drag lock (8%) now reads
as this same tension, not a shortfall.
