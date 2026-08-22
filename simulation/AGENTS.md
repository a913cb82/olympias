# simulation — the simulators

Two simulators of the Olympias-class trireme sharing one command language.
The validated physics they must satisfy: `../research/AGENTS.md` (the
evidence base and the validated chain). The acceptance record — every
gate, anchor, result and honest mismatch — lives in
[`docs/VALIDATION.md`](docs/VALIDATION.md) (reproduce: run all `ll/tests/`;
the current check count lives in the ledger, not here).

**Chain of trust: real-world data → LL → HL.** The LL (low-level simulator —
per-oar physics) is the oracle: it must reproduce the research numbers
exactly. The HL (high-level simulator — one fast ship-level integrator) is
an approximation whose response curves are machine-generated from LL runs
(`hl/calibrate.py` → `hl/calibration/calib_<id>.json`, the ship's default
via `curves.default()`), never hand-entered, and every HL result carries
its tolerance source ("±X % of LL, calibration run #N" — the equivalence
record: VALIDATION §9). `harness/` runs the same command script on both
simulators and produces the Level-2 equivalence tables (`run_validation.py`).

## Layout

```
commands/   schema + script parser (the frozen command language)
common/     chain.py — shared access to the research chain (single source of
            truth; no duplicated constants)
docs/       VALIDATION.md — the acceptance record (the LL gates §1–§8,
            the HL-vs-LL equivalence §9, the coverage map §10, the open
            items with their quantified causes §11); CALIBRATION.md — the
            tuning ledger; next-steps.md — the open work (orthogonal
            streams); completed-work.md — the verdict ledger (everything
            done, with pointers)
ll/         the LL — per-oar reality-grade sim
  blade.py      the flat-plate blade-force law
  oar.py        time-stepped one-oar kinematics + cycle averages
  run_one_oar.py   CLI runner (rig, V, spm, t-drive, dt)
  tests/test_gate*.py   per-gate acceptance suites (counts in VALIDATION)
hl/         the HL — fast ship-level sim (a "curve-chasing" ship: it follows
            the pre-measured response tables instead of simulating each oar)
  ship.py       the whole simulator (same command API as the LL)
  curves.py     Calibration + bootstrap + the calibration-file loader
  calibrate.py  the machine calibration run (LL protocols -> calib_<id>.json)
  calibration/  the committed calibration files (latest.json is the default)
  run_hl.py     demo runner (script / table / turns)
harness/    the pair harness — same script, both ships, then compare
  script.py       one command stream, both simulators, 1 Hz telemetry
  comparator.py   the Level-2 metrics + the equivalence table
  run_validation.py  the script set + turn scenarios (VALIDATION §9)
  equivalence-annotated.md  the annotated script run (per-row tolerance
                            sources + the calibration id)
examples/   the script set: cruise_turn.txt + long_cruise / sprint_turn /
            wprime_burst / three_nm_cruise / tempo_loss / the zig-zag
            out-of-sample
ui/         the browser replay UI (zero dependencies, no build)
  dump.py       one-time: dumps deterministic 1 Hz telemetry logs of the
                script set + turn scenarios (harness run_both) to logs/
  viewer.html   the viewer — one self-contained file (vanilla JS + SVG)
  serve.py      stdlib HTTP server (python3 ui/serve.py opens the browser)
  logs/         the committed replay logs (<id>.<ll|hl>.json + index.json)
tests/      test_parser.py — command-language checks
```

## Design principles

1. **The chain of trust.** Everything is ultimately measured against
   reality: the LL must satisfy the repository's validated numbers
   (physics-anchored acceptance); the HL must stay within a documented
   tolerance of the LL (the equivalence contract); the HL's tolerance
   bands are annotated in its output, so its credibility ceiling is
   always visible.
2. **One command language, one clock, one contract.** Same script +
   same starting state + same environment → equivalent ship behaviour,
   with the LL as judge.
3. **Shared assets, no duplicated numbers.** Both simulators read the
   same data files (rig geometry, oar inertias, the power chain, the
   blade model, hull, manoeuvring, environment — all under `research/`);
   `common/chain.py` is the single source.
4. **Layered fidelity.** A faithful physics core plus an explicitly
   labelled "tuning" layer; tuning never silently overrides physics —
   every tunable is documented, logged, and swappable (oQ-18, one of
   the original design questions — the Mark IIb blade shortfall — is
   the standing example).
5. **Deterministic and replayable.** Fixed dt (time step), seeded RNG
   (random-number generator), logged command stream; oar state is a
   pure function of the phase clock.
6. **The design questions oQ-1…oQ-21 are resolved or scoped to
   Phase 4/5**; the live open items (with causes and locks) are
   VALIDATION §10–§11.

## Command language (v1 — the battle set)

Units: spm = strokes per minute; kt = knots.

4 crew verbs, script format: one command per line, `#` comments,
comma- or space-separated: `<time_s> <verb> [args...]`
(the schema: `commands/schema.json`):

- `rate <spm|alias>` — ship-global cadence (aliases: slow 24 / working 30 / racing 44)
- `oars <row|hold|back|bank> [port|starboard]` — per side, default both;
  never per tier (hold = hold water, the brake mode; back = back water)
- `pressure <rest|steady|fast|spoude|0-1> [port|starboard]` — effort per
  stroke (spoude = the maximum "burst" level)
- `helm <port|starboard|midship> [fraction]` — the steering oar

`report`, `course`, `go`, `speed`, `anchor`, etc. were deliberately cut
(the dropped list with reasons is recorded in the schema).

## The pair contract (the equivalence gates)

**Level 1 — the LL vs reality (physics-anchored acceptance; Rankov 2012):**

- cruise rates: 25.5 / 28.8 / 32.3 spm at 7 / 7.5 / 8 kt (ch.7);
- sprint: 44.5 spm → 8.2–8.4 kt (ch.9, measured 8.2–8.3);
- manoeuvre: the F/G trial-turn families (F1–F6, G1–G5 — the two turn
  sets recorded in the Olympias sea trials) within ±7 %;
- per-oar: mean handle force ≈ 210–225 N; the catch-flip inertia spike
  (the oar's snap at the start of the stroke) per `oar_inertia.py`;
  the old-fir ≈ 2× spruce handiness figure reproduced.

**Level 2 — the HL vs the LL (equivalence, first tolerances):**

- |mean speed difference| < 1 % over a 10-minute script including a
  sprint and a turn; settled stroke rate within 1 spm; time to 3 NM
  within 1 %; the standard G1/F1 turn diameters (full rudder at 6 kt /
  22.5° rudder at 6 kt) within 5 %; accumulated crew fatigue within
  5 %; final position within ~0.1 NM after course changes — and the
  path-gap gates (position_path: the mean per-sample separation < 0.1
  NM; position_max: the worst single-sample separation < 0.15 NM
  clean / 0.25 on the annotated cruise_turn — the final position alone
  can coincide while the paths diverge mid-run). Every HL result
  carries the tolerance source (the calibration run id).

**The honesty rule**: the HL stays loose only where documented
(VALIDATION §9.3 — the measured divergences and their triggers); the
HL is never hand-tuned to its own old numbers — it is re-fitted to the
LL's new truth.

## The calibration protocol (`hl/calibrate.py`)

The run regenerates the HL's response tables from LL runs and writes
`hl/calibration/calib_<id>.json` (+ `latest.json`, the ship's default):
every table machine-measured with its residuals, the protocols in the
file's meta, the LL commit recorded. The loop's first step: calibrate →
`harness/run_validation.py` → adjust → repeat (~4 min of LL protocols).

Measured tables:

- the spoude (burst) rate→speed row — the LL equilibrium over 8…50 spm;
- the steady/fast/empty pressure rows (300-s settles, tail means);
- the hold/back rows — the back-water mode collapses at ≤ 24 spm
  (measured separately);
- the W′ nets — W′ is each rower's short-term energy reserve (the burst
  tank); the nets measure its drain/refill (short windows — the refill
  cap taints a long one);
- the rudder/oar turn-diameter tables at the helm fractions;
- the tau fits — the time constants of the approach/decay curves
  (tau_surge from the rest-start; tau_turn + the two-timescale yaw-build
  per turn family: a fast approach plus the slow sway-coupled tail);
- the drift cells — the ship's small steady drift-turn at each speed and
  pressure (the untrimmed yaw slope);
- the turn-drag curve and the asym nets — the W′ drain when only one side
  is rowing (near zero: that side is barely working).

**Regeneration rule**: when the LL gains fidelity, `calibrate.py
--regenerate` re-measures and rewrites the file; the tests run against
the pinned latest; no hand-edited numbers. The residual annotations
feed the "±X % of LL, calibration run #N" labels.

**Explicit non-goals** (complexity only if a gate fails): no per-tier
or per-side crew machinery; no force tables; no fitted constants beyond
the tables above; no changes to the LL. The triggers: 10-min mean > 1 %
→ per-rate tau_surge; sprint envelope misses → one fitted drain factor;
turn diameter D > 5 % on any turn → tau_turn per family; fatigue > 5 %
→ a second W′ tank; position > 0.1 NM → sway/drift terms.

## Definition of done (what "100 % validation" means)

- **Level 1**: every anchor either passes its band, or sits on the
  open-items list with a named cause, a locking test and a path. No
  unexplained or silent mismatches.
- **Level 2**: all six gates above pass on the script set + the five
  turn scenarios, against the pinned calibration file.
- **Evidence**: the coverage map (VALIDATION §10 — every scenario's
  status) has no failed / never-exercised / not-implemented in-scope
  cells; `run_validation.py` prints no unannotated violations; the
  suite is green (the count lives in VALIDATION §8). An open row is
  "open-with-locked-test": open, but a regression test locks the
  numbers so it cannot silently worsen.

```bash
cd simulation
../.venv/bin/python3 -m pytest                    # green; count in VALIDATION §8
../.venv/bin/python3 harness/run_validation.py   # no unannotated violations
```

## Replay UI (browser)

The UI replays already-computed runs from their telemetry logs — no
simulation runs in the browser, nothing to install, no build step:

```bash
../.venv/bin/python3 ui/serve.py       # opens the viewer in your browser
```

The dropdown lists every run; each loads both sims' 1 Hz telemetry (the
same `harness/run_both` telemetry the validation uses — LL solid, HL
outline, toggle the comparison). Play/pause (space), 0.5–100× speed, a
scrubber, clickable command markers on the timeline (jump to the command
and its state), readouts (speed, rate, heading in compass degrees — north = 0°, matching the ship icon's facing — yaw, helm, per-side
state/pressure and the W′ meter). The map zooms with the wheel (around
the cursor) and pans by dragging (⤢ refits); the ship is drawn at its
TRUE world scale (37 m on the ground at every zoom level — no clamp,
so the ships keep growing honestly however far you zoom in) — the
turning circles are
the trial's measured diameters, and zooming into a turn shows the ship
in honest proportion to its circle. The ships carry their orders: oar
angle = state (row sweeps at the stroke rate, hold perpendicular, back
blades forward, bank raised), oar colour = pressure (rest grey → steady
green → fast amber → spoude red), the stern oar = helm deflection.

The logs live in `ui/logs/` and are committed (deterministic — no RNG in
the sims). Regenerate them after any LL/HL change:

```bash
../.venv/bin/python3 ui/dump.py        # everything (~1 min; 12 runs × 2 sims)
../.venv/bin/python3 ui/dump.py --only g1
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

- **Deterministic and replayable**: fixed dt (time step), seeded RNG,
  logged command stream; oar state is a pure function of the phase clock.
- **No duplicated numbers**: every constant comes from `common/chain.py`, which
  re-exports the research modules. A new constant lands in research first.
- **Honest layers**: the flat-plate law with blade area 0.078 m² under-predicts
  the Mark IIb rig's points (~30 % of hull need — oQ-18; Rankov ch.9 notes the
  Mark II needs ~×3.3 area). The LL reproduces this shortfall exactly and
  test_gate1 fails if anyone tunes it silently. Don't fix it without updating
  the docs and the test.
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
annotated (documented HL-loose) rows; the open items, their quantified
causes and the regression locks: VALIDATION §11.

Remaining: Phase 4 (crew & environment) and Phase 5 (oar-manoeuvres).
The loop discipline after any LL/HL change: `hl/calibrate.py` →
`harness/run_validation.py` → the full suite → the docs → commit.
