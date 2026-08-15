# Full-validation DAG — the path to 100 % validation

The task graph for closing every closable row of the coverage map. This
file is the single source for the DAG; the statuses of the rows live in
`VALIDATION.md` §10 (the coverage map), the definition of done in
`trireme-simulation-plan.md` §21.1, the decision points in §21.3 and the
completion check in §21.4.

## 1. The graph

Twelve tasks (A–L); `X → Y` means X must be complete before Y starts.
Tasks with no incoming edges start now, in parallel. The layers are
strictly topological — nothing in a layer depends on anything below it.

```
Layer 0 — independent tasks (all start now):
   Level 1 (LL core):       G · H · I
   Level 2 (HL + harness):  B · C · D · E · F

Layer 1 — LL-truth convergence:
   H ─► R1 ──┐
   I ─► R2 ──┼──► J  ◄── B · E · F      J = regenerate the calibration
   (R1/R2 ─► L;                         (hl/calibrate.py), only after the
    R1 ─► J only if H closed)           LAST LL-truth change

Layer 2 — the acceptance run:
   J ─┐
   C ─┼─► K  ◄─ D                        K = full validation run
   B ─┘                                 (harness/run_validation.py)
   (K is re-run after every change; the acceptance K is the one on the
    pinned calibration after the last LL-truth change)

Layer 3 — the deliverables:
   K ─► A ─► L  ◄─ G · R1 · R2           L = the completion check
                                         (§21.1 definition of done)
```

## 2. The tasks

| Task | Feeds | Done when (exit criterion) |
| --- | --- | --- |
| B — settled-rate gate + tempo-loss curve | J, K | the comparator emits the rate_eff row; the exhausted-sprint tempo-loss scenario (oQ-14) passes within 1 spm; the tempo-loss curve is measured from the LL and in the calibration |
| C — drift-floor-corrected position gate | K | the position row is \|sep\| − drift_floor(run length); the plan §21.3 decision is recorded; the position gate passes |
| D — 3-NM cruise script | K | a ~40-min cruise in `examples/`; the t_3nm row exists and is within 1 % of the LL |
| E — back-tail per-state τ | J | the τ for back/hold measured from the LL's one-side-stopped decay (the cruise_turn 1440–1620 s bins) and in the calibration; the cruise_turn mean gate passes at K |
| F — turn-deceleration term | J | the turn-drag response measured from the LL's turn V(t) (G1-family: 6.0 → 5.4 kt over 54 s) and in the calibration; the sprint_turn mean gate passes at K |
| G — ch.7 Mark II triple check | L | the LL at hull = 1.08 vs the 7.0/7.5/8.0 kt references; coverage row 10.1.3 becomes validated, or the tension is documented with numbers |
| H — t_360 hypothesis test | R1 | the linear yaw-damping hypothesis (register C1) tested; t_360 closed, or locked as the sole open physics item with the test recorded (VALIDATION §7.2) |
| I — Mark IIb blade layer | R2 | the ch.9 (q/p)² turning-point law implemented; Gates 1/7 re-validated; oQ-18 documented as physical |
| R1 — L1 Gate-3 re-validation | L | Gate 3 re-validated on the changed LL (or “no change needed” recorded); the outcome lands in VALIDATION §3 |
| R2 — L1 Gates-1/7 re-validation | L | Gates 1/7 re-validated on the changed LL |
| J — regenerate the calibration | K | `hl/calibrate.py` re-run; the new calibration id pinned and recorded; every curve still measured — no hand-tuning |
| K — the acceptance run | A | `harness/run_validation.py` on the pinned calibration: no unannotated violations; the VALIDATION §9 tables refreshed |
| A — the annotated script run | L | the equivalence tables annotated with per-row tolerance sources and the calibration id |
| L — the completion check | — | plan §21.1 all clauses true: the coverage map shows only validated / open-with-locked-test / scoped; the suite green (VALIDATION §8) |

## 3. Structure rules

- **Convergence**: J waits for the *last* LL-truth change (R1/R2) — the
  acceptance K then runs once on the pinned calibration. H locked-open
  means no truth change: skip R1 → J and go straight to L via the doc row.
- **Critical path**: `I → R2 → J → K → A → L` (the Mark IIb blade layer is
  the largest implementation; B–F and G run in its shadow).
- **The loop guard**: after any LL or HL change, the pair J → K is the
  regeneration discipline — the verdicts come only from the harness on the
  pinned calibration.

## 4. Where the verdicts live

- Row statuses (validated / marginal / failed / never exercised / no
  anchor / scoped, each with its path): `VALIDATION.md` §10.
- The equivalence tables: `VALIDATION.md` §9 (refreshed by K).
- The definition of done and the completion check: plan §21.1/§21.4.
- The decision points (the position gate, the interpolated midpoints, the
  scoped rows): plan §21.3.
