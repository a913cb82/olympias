# simulation — the simulators

Two simulators of the Olympias-class trireme sharing one command language.
The validated physics they must satisfy: `../research/AGENTS.md` (the
evidence base and the validated chain). The acceptance record — every
gate, anchor, result and honest mismatch — lives in
[`docs/VALIDATION.md`](docs/VALIDATION.md) (reproduce: run all `ll/tests/`;
the current check count lives in the ledger, not here).

**Chain of trust: real-world data → LL → HL.** The LL is the oracle
(per-oar physics, validated against the research numbers); the HL is a
fast approximation whose response curves are machine-generated from LL
runs (`hl/calibrate.py` → `hl/calibration/calib_<id>.json`, the ship's
default via `curves.default()`), never hand-entered, and every HL result
carries its tolerance source (the equivalence record: VALIDATION §9).
`harness/` runs the same command script on both simulators and produces
the Level-2 equivalence tables (`run_validation.py`).

## Layout

```
commands/   schema + script parser (the frozen command language)
common/     chain.py — shared access to the research chain (single source of
            truth; no duplicated constants)
docs/       VALIDATION.md — the acceptance record (the LL gates §1–§8,
            the HL-vs-LL equivalence §9, the coverage map §10, the open
            items with their quantified causes §11)
ll/         per-oar reality-grade sim
  blade.py      flat-plate blade-force law
  oar.py        time-stepped one-oar kinematics + cycle averages
  run_one_oar.py   CLI runner (rig, V, spm, t-drive, dt)
  tests/test_gate*.py   per-gate acceptance suites (counts in VALIDATION)
hl/         fast ship-level sim
  ship.py       the whole simulator (curve-chasing; same command API as the LL)
  curves.py     Calibration + bootstrap + the calibration-file loader
  calibrate.py  the machine calibration run (LL protocols -> calib_<id>.json)
  calibration/  the committed calibration files (latest.json is the default)
  run_hl.py     demo runner (script / table / turns)
harness/    the pair harness
  script.py       one command stream, both simulators, 1 Hz telemetry
  comparator.py   the Level-2 metrics + the equivalence table
  run_validation.py  the script set + turn scenarios (VALIDATION §9)
  equivalence-annotated.md  the annotated script run (per-row tolerance
                            sources + the calibration id)
examples/   cruise_turn.txt + long_cruise / sprint_turn / wprime_burst
            + the zig-zag out-of-sample (the script set)
tests/      test_parser.py — command-language checks
```

## Design principles

1. **The chain of trust.** Everything is ultimately measured against
   reality: the LL must satisfy the repository's validated numbers
   (physics-anchored acceptance); the HL must stay within a documented
   tolerance of the LL (the equivalence contract); the HL's tolerance
   bands are annotated in its output ("±1 % of LL, calibration run X"),
   so its credibility ceiling is always visible.
2. **One command language, one clock, one contract.** Same script +
   same starting state + same environment → equivalent ship behaviour,
   with the LL as judge.
3. **Shared assets, no duplicated numbers.** Both simulators read the
   same data files (rig geometry, oar inertias, the power chain, the
   blade model, hull, manoeuvring, environment — all under `research/`);
   `common/chain.py` is the single source.
4. **Layered fidelity.** A faithful physics core plus an explicitly
   labelled "tuning" layer; tuning never silently overrides physics —
   every tunable is documented, logged, and swappable (oQ-18 is the
   standing example).
5. **Deterministic and replayable.** Fixed dt, seeded RNG, logged
   command stream; oar state is a pure function of the phase clock.
6. **The design questions oQ-1…oQ-21 are resolved or scoped to
   Phase 4/5**; the live open items (with causes and locks) are
   VALIDATION §10–§11.

## Command language (v1 — the battle set)

4 crew verbs, script format: one command per line, `#` comments,
comma- or space-separated: `<time_s> <verb> [args...]`
(the schema: `commands/schema.json`):

- `rate <spm|alias>` — ship-global cadence (aliases: slow 24 / working 30 / racing 44)
- `oars <row|hold|back|bank> [port|starboard]` — per side, default both; never per tier
- `pressure <rest|steady|fast|spoude|0-1> [port|starboard]` — effort per stroke
- `helm <port|starboard|midship> [fraction]`

`report`, `course`, `go`, `speed`, `anchor`, etc. were deliberately cut
(the dropped list with reasons is recorded in the schema).

## The pair contract (the equivalence gates)

**Level 1 — the LL vs reality (physics-anchored acceptance):**

- cruise rates: 25.5 / 28.8 / 32.3 spm at 7 / 7.5 / 8 kt (ch.7);
- sprint: 44.5 spm → 8.2–8.4 kt (ch.9, measured 8.2–8.3);
- manoeuvre: F1–F6 and G1–G5 turn diameters within ±7 % of the model;
- per-oar: mean handle force ≈ 210–225 N; catch-flip spike per
  `oar_inertia.py`; the old-fir ≈ 2× spruce handiness figure reproduced.

**Level 2 — the HL vs the LL (equivalence, first tolerances):**

- |mean speed difference| < 1 % over a 10-minute script including a
  sprint and a turn; settled stroke rate within 1 spm; time to 3 NM
  within 1 %; standard G1/F1 turn diameter within 5 %; accumulated
  crew fatigue within 5 %; final position within ~0.1 NM after course
  changes. Every HL result carries the tolerance source (the
  calibration run id).

**The honesty rule**: the HL stays loose only where documented
(VALIDATION §9.3 — the measured divergences and their triggers); the
HL is never hand-tuned to its own old numbers — it is re-fitted to the
LL's new truth.

## The calibration protocol (`hl/calibrate.py`)

The run regenerates the HL's response tables from LL protocols and
writes `hl/calibration/calib_<id>.json` (+ `latest.json`, the ship's
default): every table machine-measured with its residuals, the
protocols in the file's meta, the LL commit recorded. The loop's first
step: calibrate → `harness/run_validation.py` → adjust → repeat
(~4 min of LL protocols).

Measured tables: the spoude rate→speed row (the LL equilibrium over
8…50 spm); the steady/fast/empty pressure rows (300-s settles, tail
means); the hold/back rows (the back collapses at ≤ 24 spm — measured
separately); the W′-tank nets (short windows — the refill cap taints a
long one); the rudder/oar turn-diameter tables at the helm fractions;
the tau fits (tau_surge from the rest-start, tau_turn + the
two-timescale yaw-build per family); the drift cells (the untrimmed
yaw slope, pressure-dependent); the turn-drag curve and the asym nets.

**Regeneration rule**: when the LL gains fidelity, `calibrate.py
--regenerate` re-measures and rewrites the file; the tests run against
the pinned latest; no hand-edited numbers. The residual annotations
feed the "±X % of LL, calibration run #N" labels.

**Explicit non-goals** (complexity only if a gate fails): no per-tier
or per-side crew machinery; no force tables; no fitted constants beyond
the tables above; no changes to the LL. The triggers: 10-min mean > 1 %
→ per-rate tau_surge; sprint envelope misses → one fitted drain factor;
D > 5 % on any turn → tau_turn per family; fatigue > 5 % → a second W′
tank; position > 0.1 NM → sway/drift terms.

## Definition of done (what "100 % validation" means)

- **Level 1**: every anchor either passes its band, or sits on the
  open-items list with a named cause, a locking test and a path. No
  unexplained or silent mismatches.
- **Level 2**: all six gates above pass on the script set + the five
  turn scenarios, against the pinned calibration file.
- **Evidence**: the coverage map (VALIDATION §10) has no failed /
  never-exercised / not-implemented in-scope cells; `run_validation.py`
  prints no unannotated violations; the suite is green (the count lives
  in VALIDATION §8).

```bash
cd simulation
../.venv/bin/python3 -m pytest                    # green; count in VALIDATION §8
../.venv/bin/python3 harness/run_validation.py   # no unannotated violations
```

## Running (pytest)

```bash
V=../.venv/bin/python3               # from simulation/
$V -m pytest                         # all suites, one command (the current count
                                     # lives in VALIDATION, not here)
$V -m pytest -v                      # per-check names
$V -m pytest ll/tests/test_gate5.py  # one suite
$V ll/run_one_oar.py                 # one-oar table @ Olympias 7.2 kt / 28.8 spm
$V ll/run_one_oar.py --rig MarkIIb --v-kts 7.5 --spm 28.8 --t-drive 0.612
```

Suites: parser · gates 1–8 · research chain (`tests/test_research_chain.py` —
locks the research side itself) · HL basics (`hl/tests/`) · harness
(`harness/tests/`). Per-gate counts live in VALIDATION. Parser has
no CLI: `from commands.parser import parse_file, parse_script` — errors raise
`ScriptError` naming the offending line.

## Conventions

- **Deterministic and replayable**: fixed dt, seeded RNG, logged command stream;
  oar state is a pure function of the phase clock.
- **No duplicated numbers**: every constant comes from `common/chain.py`, which
  re-exports the research modules. A new constant lands in research first.
- **Honest layers**: the flat-plate law with blade area 0.078 m² under-predicts
  the Mark IIb points (~30 % of hull need — oQ-18; ch.9 notes Mark II needs ~×3.3
  area). The LL reproduces this shortfall exactly and test_gate1 fails if anyone
  tunes it silently. Don't fix it without updating the docs and the test.
- **Fail-fast scripts**: unknown verbs/out-of-range args raise `ScriptError`
  naming the line, before any run.
- Python: `.venv` at the repo root — from in here that is `../.venv/bin/python3`.

## Status (current state)

All three phases are complete: the LL is the validated oracle
(VALIDATION §1–§8 — the honest mismatch ledger §7), the HL is the
machine-calibrated fast ship, and the pair harness produces the Level-2
equivalence tables (VALIDATION §9) with the annotated script run in
`harness/equivalence-annotated.md`. The suite is green (141 checks; the
per-gate count lives in VALIDATION §8). The coverage map
(VALIDATION §10) shows only validated / open-with-locked-test /
annotated rows; the open items, their quantified causes and the
regression locks: VALIDATION §11.

Remaining: Phase 4 (crew & environment) and Phase 5 (oar-manoeuvres).
The loop discipline after any LL/HL change: `hl/calibrate.py` →
`harness/run_validation.py` → the full suite → the docs → commit.
