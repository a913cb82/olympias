# W5 re-run: trial turns F1–F6 / G1–G5 — findings

Status: `[x]` = confirmed, `[?]` = unresolved/needs data we don't hold.
Script: `research/lane-5-manoeuvre/fg_turns_rerun.py` (python3, stdlib only).

## What we set out to check

ch.31 §3 says the model was fitted to the eleven trial turns in Coates et al.
(1990, 87–88) tables F & G (F1–F6 Hellenic Navy crew, G1–G5 Trust crew).
Task: re-run the model against those turns and document the match.

## Data constraint (important)

The per-turn raw numbers (entry speed, applied rudder angle, turn diameter,
turn duration) appear ONLY in tables F & G of *The Trireme Trials 1988*
(Coates, Platis & Shaw, Oxbow 1990, ISBN 0946897212), pp. 87–88. [x]
That report is print-only; we do not hold a copy and no digitised copy was
found online (OBNB, tDAR, Trireme Trust archive catalogue, university
catalogues — all bibliographic records only).  ch.31 §3 reproduces only
*qualitative* per-turn notes.  **A cell-by-cell fit check against F/G is
therefore impossible from our sources.**  [x]

## What we could validate (all anchors published in the book / trial reports)

The model reproduces every DIAMETER anchor to ≤7% (headline W5 validation):

| Anchor | Published | Model | Error |
|---|---|---|---|
| Tightest Olympias turn | 62 m (1.9 × 32.2 m LWL, Morrison 1988) | 64.0 m | +3% |
| Fast anastrophe (9.5 kt, 22.5°, Mark IIb) | 145 m | 151.8 m | +5% |
| Tight anastrophe (6.5 kt, full rudder, one side stops, Mark IIb) | 80 m | 74.6 m | −7% |

Scenario behaviour matches ch.31 §3 qualitatively: [x]
- F1 (smallest applied rudder angle, 22.5°) → largest diameter of the F set (111.9 m) ✓
- F2–F4 (45°) → 93.5 m ✓
- F5/F6 (thranites only, low entry speed) → 89.4 m @ 5.5 kt ✓
- G1–G3 (full rudder, full crew) → 89.4 m @ 6 kt, yaw 3.6–4.0°/s ✓
- G4/G5 (45°) → 93.5 m ✓

## Documented discrepancies (caveats, not fitted)

1. **Yaw rate / 360°-time** [x] — model steady-state ω at constant speed gives
   ~60 s per 360° (6.5 kt entry), but Morrison 1988 measured 128 s for the
   1.9-length turn.  The observed turn halves speed (ch.31 §6.2), giving mean
   2.91 kt → 2.81°/s → 360° in ~128 s, matching the trial reports' ~2.6–3°/s.
   Matching the time history needs a full time-domain yaw integration with
   deceleration — Taylor's Excel model was steady-state too, so the diameter
   (which the tactical analysis uses) is the validated quantity.
2. **Drift angle** [x] — model force balance gives ~1.4° for G1/G2 vs the
   reported 15°±2° (Taylor himself reduces to ~7.8° via the time-delay
   method).  Known caveat in manoeuvre-model.md; needs lower A_lat or a
   different lateral-force split to match, and drift is secondary to diameter.

## Open items

- [ ] Per-turn F/G data (entry speed, rudder angle, diameter, duration for
      each of F1–F6, G1–G5): requires *The Trireme Trials 1988* (print-only,
      ISBN 0946897212).  Leads: Wolfson College archive (Trireme Trust
      papers), Oxbow out-of-print copies, university libraries (U. Crete
      catalogue record exists).  This is the same physical-archive path as
      the Taylor Excel workbook (W5/D4).
- [x] Independent anchors used here are logged in the main doc §6.2 and
      lane-6 `primary-trial-data.md` where relevant.
