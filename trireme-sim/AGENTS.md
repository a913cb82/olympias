# trireme-sim — the simulators

Two simulators of the Olympias-class trireme sharing one command language. Design:
`../trireme-simulation-plan.md` (gates, equivalence contract, open questions
oQ-1…21). The validated physics they must satisfy: `../research/AGENTS.md` and
`../trireme-rowing-simulation-research.md`.

**Chain of trust: real-world data → LL → HL.**
- `ll/` (low-level) is the oracle — per-oar physics, validated against the
  research numbers.
- `hl/` (high-level, not built yet) is a fast approximation; its response curves
  are generated from LL runs (`calibrate()`), never hand-entered, and every HL
  result carries its tolerance source.

## Layout

```
commands/   schema + script parser (Step 0, done)
common/     chain.py — shared access to the research chain (single source of
            truth; no duplicated constants)
ll/         per-oar reality-grade sim
  blade.py      flat-plate blade-force law
  oar.py        time-stepped one-oar kinematics + cycle averages
  run_one_oar.py   CLI runner (rig, V, spm, t-drive, dt)
  tests/test_gate1.py   Gate-1 acceptance (7 checks)
hl/         fast ship-level sim (Phase 2 — from LL runs)
harness/    script runner + compare + calibrate (Phase 3)
cli/        CLI driver (Phase 3)
examples/   cruise_turn.txt — sample command script
tests/      test_parser.py — command-language checks (19)
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

## Running

```bash
V=/tmp/opencode/venv/bin/python3
$V tests/test_parser.py            # 19 command-language checks
$V ll/tests/test_gate1.py          # 7 one-oar acceptance checks
$V ll/run_one_oar.py               # one-oar table @ Olympias 7.2 kt / 28.8 spm
$V ll/run_one_oar.py --rig MarkIIb --v-kts 7.5 --spm 28.8 --t-drive 0.612
```

(Parser has no CLI: `from commands.parser import parse_file, parse_script` —
errors raise `ScriptError` naming the offending line.)

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
- Python: `/tmp/opencode/venv/bin/python3` only.

## Phase status

- [x] Step 0 — command language: schema v0.1, parser, sample script (19 checks)
- [x] Phase 1 Gate 1 — one-oar LL: time-stepped oar == rigid model at all four
      Table 9.6 points (< 0.5 %); mean handle force 224/208 N (cruise family);
      prop W/man 102 % at 7.2 kt (7 checks)
- [ ] Phase 1 Gate 2 — hull surge (`ll/hull.py`): settles on ch.7 cruise curve
      (25.5/28.8/32.3 → 7/7.5/8 kt) and ch.9 sprint (44.5 → 8.2–8.4 kt); the
      oQ-18 question gets its empirical answer here
- [ ] Phase 2 — HL from LL;  [ ] Phase 3 — harness;  [ ] Phase 4 — crew & environment;
      [ ] Phase 5 — oar-manoeuvres
