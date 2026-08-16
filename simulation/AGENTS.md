# simulation — the simulators

Two simulators of the Olympias-class trireme sharing one command language. Design:
`./trireme-simulation-plan.md` (gates, equivalence contract, open questions
oQ-1…21). The validated physics they must satisfy: `../research/AGENTS.md`
(the evidence base and the validated chain).

**Chain of trust: real-world data → LL → HL.** The LL's acceptance record —
every gate, anchor, result and honest mismatch — lives in
[`VALIDATION.md`](VALIDATION.md) (reproduce: run all `ll/tests/`; the current
  check count lives in the ledger, not here).
- `ll/` (low-level) is the oracle — per-oar physics, validated against the
  research numbers.
- `hl/` (high-level, Phase 2 — plan §18) is a fast approximation; its response
  curves are machine-generated from LL runs (`hl/calibrate.py` →
  `hl/calibration/calib_<id>.json`, the ship's default via `curves.default()`),
  never hand-entered, and every HL result carries its tolerance source
  (the equivalence record: VALIDATION.md §9).
- `harness/` (Phase 3) runs the same command script on both simulators and
  produces the Level-2 equivalence tables (`run_validation.py`).
- the current state — every row's status (validated / open-with-
  locked-test / annotated) and the open items with their causes — lives
  in VALIDATION.md §10–§11; the definition of done is plan §21.

## Layout

```
commands/   schema + script parser (the frozen command language)
common/     chain.py — shared access to the research chain (single source of
            truth; no duplicated constants)
ll/         per-oar reality-grade sim
  blade.py      flat-plate blade-force law
  oar.py        time-stepped one-oar kinematics + cycle averages
  run_one_oar.py   CLI runner (rig, V, spm, t-drive, dt)
  tests/test_gate*.py   per-gate acceptance suites (counts in VALIDATION.md)
hl/         fast ship-level sim (Phase 2 — plan §18)
  ship.py       the whole simulator (curve-chasing; same command API as the LL)
  curves.py     Calibration + bootstrap + the calibration-file loader
  calibrate.py  the machine calibration run (LL protocols -> calib_<id>.json)
  calibration/  the committed calibration files (latest.json is the default)
  run_hl.py     demo runner (script / table / turns)
harness/    the pair harness (Phase 3)
  script.py       one command stream, both simulators, 1 Hz telemetry
  comparator.py   the Level-2 metrics + the equivalence table
  run_validation.py  the script set + turn scenarios (VALIDATION.md §9)
examples/   cruise_turn.txt + long_cruise / sprint_turn / wprime_burst
            (the plan §20 script set)
tests/      test_parser.py — command-language checks
```

## Command language (v1 — the battle set)

4 crew verbs, script format in plan §3.5 (one command per line, `#` comments,
comma- or space-separated: `<time_s> <verb> [args...]`):

- `rate <spm|alias>` — ship-global cadence (aliases: slow 24 / working 30 / racing 44)
- `oars <row|hold|back|bank> [port|starboard]` — per side, default both; never per tier
- `pressure <rest|steady|fast|spoude|0-1> [port|starboard]` — effort per stroke
- `helm <port|starboard|midship> [fraction]`

`report`, `course`, `go`, `speed`, `anchor`, etc. were deliberately cut — the
dropped list with reasons is plan §3.2.

## Running (pytest)

```bash
V=../.venv/bin/python3               # from simulation/
$V -m pytest                         # all suites, one command (the current count
                                     # lives in VALIDATION.md, not here)
$V -m pytest -v                      # per-check names
$V -m pytest ll/tests/test_gate5.py  # one suite
$V ll/run_one_oar.py                 # one-oar table @ Olympias 7.2 kt / 28.8 spm
$V ll/run_one_oar.py --rig MarkIIb --v-kts 7.5 --spm 28.8 --t-drive 0.612
```

Suites: parser · gates 1–8 · research chain (`tests/test_research_chain.py` —
locks the research side itself) · HL basics (`hl/tests/`) · harness
(`harness/tests/`). Per-gate counts live in VALIDATION.md. Parser has
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
(VALIDATION.md §1–§8 — the honest mismatch ledger §7), the HL is the
machine-calibrated fast ship (plan §18–§19), and the pair harness
produces the Level-2 equivalence tables (VALIDATION.md §9) with the
annotated script run in `harness/equivalence-annotated.md`. The suite
is green (141 checks; the per-gate count lives in VALIDATION.md §8).
The coverage map (VALIDATION.md §10) shows only validated /
open-with-locked-test / annotated rows; the open items, their quantified
causes and the regression locks: VALIDATION.md §11.

Remaining: Phase 4 (crew & environment) and Phase 5 (oar-manoeuvres) —
both scoped in plan §8. The loop discipline after any LL/HL change:
`hl/calibrate.py` → `harness/run_validation.py` → the full suite → the
docs → commit.
