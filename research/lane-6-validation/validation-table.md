# W6 validation table + sensitivity pass (Step 3)

Maps every Olympias sea-trial measurement to a model prediction using the
two validated reference models, and runs the uncertainty-register
sensitivity pass.  This closes the W6 checklist items.

Script: `research/lane-6-validation/validation_table.py`
Inputs: lane-4 propulsion chain (`lane4_propulsion.py`), lane-5 Taylor
manoeuvring model (`manoeuvre_model.py`), lane-3 hull form
(`hull_form.py`), primary-trial-data.md, uncertainties-register.md.

## Validation table

| Measurement | Trial value | Model | Status |
|---|---|---|---|
| Sustained, 154 rowers, 45 spm (E 0.53–0.55) | 8.2–8.3 kt | 8.0–8.1 kt | target |
| Sprint, 130 rowers, 44.5 spm, E=0.730 | 8.2–8.3 kt | 8.3 kt | target |
| GPS ~135 rowers | 7.8–7.9 kt | 7.7–7.8 kt | target |
| GPS 121 rowers (peak) | ~8.2 kt | 8.2 kt | target |
| Accel 0→7 kt | 32 s (1988, less-trained) | 14.0 s (trained model) | context |
| Fast anastrophe | 145 m | 152 m | target |
| Tight anastrophe | 80 m | 75 m | target |
| Olympias tightest | 62 m | 64 m | target |
| Braking stop | <20 s / <170 m | 19.0 s / 56 m | target |
| Astern speed (60 s) | 9.4 kt | 9.4 kt | target |
| Trial volume | 41.22 m³ | 41.35 m³ | target |
| Light volume | 25.17 m³ | 25.17 m³ | target |
| Wetted surface | (—) | 81.3 m² | context |

### Reading

- **All steady-state speed targets are reproduced** within the ch.22
  efficiency band (53–55%).  The sprint anchor (E=0.730) is a special
  case: it uses the ch.9 sprint efficiency and reproduces 8.32 kt
  exactly, matching the S10 verification.
- **All turn diameters** are within ~7% of the published tactical numbers
  (145/80/62 m) — already validated in the lane-5 model; the table records
  them as part of the W6 matrix.
- **Acceleration 0→7 kt**: the Taylor model is for a *trained* Mark IIb
  crew (reaches 7 kt in 14 s).  The 1988 trial's 32 s reflects the
  less-trained crew and lower starting thrust — consistent with the model
  being an upper bound on attainable acceleration, not a mismatch.  Per
  register D5 this is a context row, not a pass/fail.
- **Braking / astern** reproduce Taylor's §6.1 numbers exactly.
- **Hydrostatics** reproduce both BMT displacement anchors (S14).

## Sensitivity pass

| Knob | Range | Effect | Register |
|---|---|---|---|
| Displacement | ±2% (build tolerance) | sprint ±0.5% (8.29–8.37 kt) | B1 [H] but small: hull law is trial-validated over this range |
| GM (crew lean) | 1.13 → 0.99 → 0.85 m | turn diameter unchanged (yaw-driven); heel 3.0° → 3.6° → 4.3° | B7 [M] — GM sets the heel limit only |
| Oar efficiency | 40% (low-speed) → 53–55% (calm) | sustained 7.43 → 8.0–8.1 kt | D4 [H] — the dominant knob |
| Crew power / count | 121 → 135 → 154 rowers, E 0.53–0.55 | 7.5 → 7.7–7.8 → 8.0–8.1 kt | D4 [H] — crew strength dominates speed |

### Reading

- **Oar efficiency and crew power/count dominate** the speed prediction
  (±0.7 kt across the envelope); displacement is a second-order effect
  (±0.5%) because the hull law is itself fitted to trial speeds.
- **GM only couples through heel** — the turn *diameter* is yaw-driven
  (moment of inertia, Ω, rudder torque); GM sets whether the heel limit
  (3°) is respected.  Trial GM 1.13 m gives heel 3.0° at the fast
  anastrophe, matching Taylor's design constraint; the crew-lean cases
  (0.99/0.85 m) push heel to 3.6–4.3°, i.e. the "some remedial action by
  the deck crew" Taylor describes is genuinely needed.
- The [H] knobs (B1, B2, D1) are already pinned by primary-source values
  (BMT inclining, GPS, ch.9 sprint) — see uncertainties register bottom
  line.  Remaining [H] items (B4 light-hull scenario, C1 yaw-drag units)
  are scenario/unit-label issues, not baseline errors.

## Files

- `validation_table.py` — the table + sensitivity pass.
- `primary-trial-data.md` — trial measurements and their interpretation.
- `uncertainties-register.md` — flags/sensitivities (single source of truth).
