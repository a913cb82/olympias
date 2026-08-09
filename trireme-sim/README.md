# trireme-sim

Two simulators of the Olympias-class trireme sharing one command language — the
design lives in `../trireme-simulation-plan.md`; the validated physics chain it
must satisfy lives in `../trireme-rowing-simulation-research.md` (and
`research/`).

## Step 0 (done): the command language

- `commands/schema.json` — v0.1, the 4 crew verbs: `rate`, `oars`, `pressure`,
  `helm` (scoping: `rate`/`helm` ship-global; `oars`/`pressure` per side,
  default both; no per-tier state).
- `commands/parser.py` — fail-fast, deterministic parser for the §3.5 script
  format (one command per line, `#` comments, comma- or space-separated:
  `<time_s> <verb> [args...]`).
- `examples/cruise_turn.txt` — sample script (cruise → burst → sprint →
  oar-assisted turn → ease → halt).
- `tests/test_parser.py` — 19 checks; run: `python3 tests/test_parser.py`.

## Layout (plan §7)

```
commands/   schema + parser          (done)
common/     shared rig/oar/sea assets (TODO)
ll/         per-oar reality-grade sim (Phase 1 Gate 1 done: one-oar, 30-spm flat-blade loop vs rigid model)
hl/         fast ship-level sim      (Phase 2 — from LL runs)
harness/    script runner + compare + calibrate (Phase 3)
cli/        CLI driver               (Phase 3)
```
