# W5 manoeuvring model — reference implementation (Step 2)

Reference implementation of Andrew Taylor's trireme dynamics model from
Rankov 2012 ch.31 ("Battle Manoeuvres for Fast Triremes"), built from the
chapter text and the OCR-verified Table 31.1 parameter set.  This is the
Lane 5 deliverable: a runnable model of the Olympias / Mark IIb manoeuvring
dynamics.

Script: `research/lane-5-manoeuvre/manoeuvre_model.py`
Parameters: `research/data/table31-1-taylor-model-parameters.csv`

## Model physics (faithful to ch.31)

Forward surge:
```
m_app * dv/dt = Thrust(v) - hull_drag(v) - rudder_drag(v, Phi)
```
- `m_app = 1.10 * displacement` (apparent dynamical mass, §2.1; Table 31.1 row 2)
- hull drag in 3 speed bands (Table 31.1 row 3):
  - Mark IIb: 44.7v² (≤6.7 kt), 83.6v²−1733 (6.7–9), 98.4v²−2933 (>9)
  - Olympias: 40.2v² (≤6.7); higher bands not tabulated → 40.2v² held
- oar thrust linear in speed (§5.2): `Thrust (kN) = 17.4 − 0.967 v(kt)`
- straight-rudder drag included for straight-ahead equilibrium
  (Fig. 31.1 drag curve = "increased surface drag and less disruptive
  rudders"), which pins max speed at ~9.9 kt where thrust = 7.8 kN.

Applied rudder (§2.1, §5.1):
- along-track drag increment: factor × straight-rudder drag;
  factor 0.6 (22.5°) … 3.25 (67.5°) for Mark IIb; 1.4/0.6/0.2 for
  Olympias (the 1.4 at 67.5° is Taylor's Kempf-manoeuvre value).
- Olympias straight-rudder drag = (79.6−40.2)v² = 39.4v² N (row 4).

Turning (§2.2):
- rudder lateral force = coeff(Φ) × rudder along-track drag,
  `coeff = 0.14 + 0.020Φ − 0.00015Φ²` (fraction of along-track drag, 40–80%).
- rudder torque = lateral force × lever (C of M → rudder, row 9).
- one-side-stops torque = (T/2) × lever to oar race (row 10).
- yaw: `I dω/dt = Q_rudder + Q_oar − Ωω²`; steady
  `ω = √((Q_rudder+Q_oar)/Ω)`, `R = v/ω`.
  `Ω` (row 12) is a rotational-resistance coefficient, **units kg m² s**
  (units caveat C1 in the uncertainties register).
- drift angle from lateral force balance:
  `ρ A_lat v² sin β + F_rud_lat = m_app v²/R`.

Heel (§2.3):
- tipping = rudder lateral force × arm_rud (row 14) + hull lateral reaction
  × arm_lat (row 13); restoring = m·g·GM_eff with GM_eff = GM − 0.2 m
  (crew lean into turn, c.g. at seat height).  Limit 3° (oar-rig).

## Validation vs published targets (section 6)

| Quantity | Model | Target | Error |
|---|---|---|---|
| coeff(22.5°) | 0.514 | 0.40–0.80 band | ✓ |
| coeff(45°) | 0.736 | 0.40–0.80 band | ✓ |
| coeff(67.5°) | 0.807 | 0.40–0.80 band | ✓ (slightly >0.80) |
| Fast anastrophe D | 151.8 m | 145 m | +5% |
| Tight anastrophe D | 74.6 m | 80 m | −7% |
| Olympias tightest D | 64.0 m | 62 m | +3% |
| v at 10 s | 5.56 kt | 5.5 kt | +1% |
| v at 24 s | 9.01 kt | 9.0 kt | 0% |
| v at 40 s | 9.81 kt | ~9.9 kt | −1% |
| Braking stop | 19.0 s, 56 m | <20 s, <170 m margin | ✓ |
| Astern speed (60 s) | 9.38 kt | 9.4 kt | 0% |
| Heel fast anastrophe | ~4.0° | 3.5° stated (with deck-crew move to inside) | +0.5° |

The implementation reproduces all headline manoeuvrability numbers from
§6.1–6.2 to within ~7%, with the as-published parameter values — no fitting
was required.  This is strong evidence the model captures Taylor's
mechanics correctly.

## F1–F6 / G1–G5 trial-turn re-run

ch.31 §3 fits the model to the eleven trial turns of Coates et al. (1990,
87–88) tables F & G (F1–F6 Hellenic Navy crew, G1–G5 Trust crew).  The raw
per-turn data (entry speed, applied rudder angle, diameter, duration) is
**print-only** (*The Trireme Trials 1988*, ISBN 0946897212 — we do not hold
it), so a cell-by-cell fit check is impossible from our sources.  What we
can do — and did (`fg_turns_rerun.py`) — is run the model over the scenario
space ch.31 §3 describes and check every quantitative anchor published in the
book/trial reports:

| Quantity | Model | Published anchor | Note |
|---|---|---|---|
| Tightest Olympias turn | **64.0 m** (6.5 kt, 67.5°, one-side stops) | **62 m**; also 1.9×32.2 m LWL (Morrison 1988) | **+3%** — headline validation |
| Fast anastrophe D | **151.8 m** (9.5 kt, 22.5°, Mark IIb) | **145 m** | **+5%** |
| Tight anastrophe D | **74.6 m** (6.5 kt, 67.5°, one-side, Mark IIb) | **80 m** | **−7%** |
| G1–G3 full rudder | 89.4 m (6 kt), yaw 3.6–4.0°/s | — (raw data in print report) | consistent with §3 |
| G4/G5 45° | 93.5 m | — | larger than full-rudder, as expected |
| F1 (22.5°) | 111.9 m | §3: "smallest applied rudder angle" | largest diameter of F set ✓ |
| F2–F4 (45°) | 93.5 m | §3 notes 45°-angle turns | ✓ |
| F5/F6 thranites-only | 89.4 m (5.5 kt, 67.5°) | §3: lower thrust, low entry speed | ✓ |
| 360° time (Morrison 1988) | 60 s @ 6.5 kt steady | **128 s** (avg 2.91 kt, 2.81°/s) | see caveat below |
| Yaw rate fast tight turns | 3.2–6.0°/s (steady) | ~2.6–3°/s observed | see caveat below |
| G1/G2 drift angle | 1.4° (force balance) | 15°±2° reported (Taylor uses ~7.8°) | known caveat (below) |

**Conclusion:** the model reproduces all three DIAMETER anchors to ≤7% — the
headline W5 validation — and its scenario space behaves consistently with
ch.31 §3 (smaller rudder angle ⇒ larger turn; full rudder + one-side-stops ⇒
tightest).  This is what the tactical numbers (145/80/62 m) rest on.

## Caveats

- **Yaw-rate / 360°-time**: the model's ω is fixed by torque balance at a
  *constant* speed, so it predicts ~60 s per 360° at 6.5 kt entry, whereas the
  observed tightest turn took 128 s.  ch.31 §6.2 states the tightest turn
  "halves speed"; at an average 2.91 kt the observed yaw is 2.81°/s (≈360° in
  128 s) — consistent with the trial reports' "2.6–3°/s".  Reproducing the
  time history would need a full time-domain yaw integration with
  deceleration, which Taylor's Excel (steady-state) model also did not
  provide.  The diameter, the quantity the tactical analysis uses, still
  matches.
- **Drift angles** computed (1.1–4.2°) are lower than the measured 7.8–15°
  the chapter quotes for full-rudder turns — the chapter itself notes the
  wide scatter (3 s × 2.6 °/s = 7.8° vs stated 15°±2°, "assume the lower
  value").  The model's drift comes out of the force balance; matching the
  measured drift would require a lower A_lat or a different lateral-force
  split.  Drift is secondary to the turn diameter, which is what the
  tactical numbers validate.
- **Heel slightly over-predicts** (4.0° vs 3.5° for the fast anastrophe,
  5.4° for the max-speed tight turn vs Taylor's "≤3° with deck-crew move
  to the inside beam").  The simplified lateral-force balance treats the
  hull reaction as acting through the arm_lat point; Taylor's Excel likely
  distributes the reaction differently.  Directionally correct and within
  ~1–2°; flagged rather than tuned.
- **Olympias drag above 6.7 kt**: Table 31.1 leaves the higher-band cells
  blank (pixel-confirmed); the model holds 40.2v².  The Olympias band-2/3
  formulas would come from the tank-test curves (see S13 / lane-3 note).
- **Drift angles** computed (0.8–2.0°) are lower than the measured 7.8–15°
  the chapter quotes for full-rudder turns — the chapter itself notes the
  wide scatter (3 s × 2.6°/s = 7.8° vs stated 15°±2°, "assume the lower
  value").  The model's drift comes out of the force balance; matching the
  measured drift would require a lower A_lat or a different lateral-force
  split.  Drift is secondary to the turn diameter, which is what the
  tactical numbers (145/80/62 m) validate.
- **Mark IIb thrust law** (17.4 − 0.967v) is used for Olympias too (§5.2
  says the chapter "adopted a similar relationship"; Table 31.1 does not
  tabulate a separate Olympias thrust law).  For an Olympias-specific
  acceleration study the lane-4 propulsion model (oar chain) should drive
  thrust instead.

## Files

- `manoeuvre_model.py` — Vessel class + Mark IIb / Olympias instances,
  steady-turn, forward-surge, braking and heel checks.
- `research/data/table31-1-taylor-model-parameters.csv` — verified parameters.
- `taylor-excel.md` — research notes, Table 31.1 reconstruction, Kempf source,
  external confirmation (S13).
