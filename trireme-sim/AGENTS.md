# trireme-sim — the simulators

Two simulators of the Olympias-class trireme sharing one command language. Design:
`../trireme-simulation-plan.md` (gates, equivalence contract, open questions
oQ-1…21). The validated physics they must satisfy: `../research/AGENTS.md` and
`../trireme-rowing-simulation-research.md`.

**Chain of trust: real-world data → LL → HL.** The LL's acceptance record —
every gate, anchor, result and honest mismatch — lives in
[`VALIDATION.md`](VALIDATION.md) (reproduce: run all `ll/tests/`, 62 checks).
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

## Running (pytest)

```bash
V=../.venv/bin/python3               # from trireme-sim/
$V -m pytest                         # all suites: 71 checks, one command
$V -m pytest -v                      # per-check names
$V -m pytest ll/tests/test_gate5.py  # one suite
$V ll/run_one_oar.py                 # one-oar table @ Olympias 7.2 kt / 28.8 spm
$V ll/run_one_oar.py --rig MarkIIb --v-kts 7.5 --spm 28.8 --t-drive 0.612
```

Suites: parser (19) · gates 1-5 (7/12/9/8/7) · research chain (12, in
`tests/test_research_chain.py` — locks the research side itself). Parser has
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

## Phase status

- [x] Step 0 — command language: schema v0.1, parser, sample script (19 checks)
- [x] Phase 1 Gate 1 — one-oar LL: time-stepped oar == rigid model at all four
      Table 9.6 points (< 0.5 %); mean handle force 224/208 N (cruise family);
      prop W/man 102 % at 7.2 kt (7 checks)
- [x] Phase 1 Gate 2 — hull surge (`ll/hull.py`, 12 checks): surge-only
      m_app·dV/dt = N·F_oars(t,V) − D(V), per-step coupling. Settles on the
      hull=1.0 anchors (7.22 kt @ 28.8, 7.98 kt @ 36); sprint (130 oars,
      44.5 spm) brackets the 8.2–8.4 kt trial over the unmeasured t_drive
      range — the empirical oQ-18 answer: the flat-plate 0.078 m2 law is
      sufficient for the Olympias rig (Mark IIb shortfall stands, separate).
      Findings: stroke surge ripple ~0.2 kt; start-from-rest needs the oQ-13
      force ceiling (crude clamp exists, demo only); Table 9.6 data gap at
      44.5 spm (uncertainties register A8).
- [x] Phase 1 Gate 3 — 170-oar surge+yaw ship (`ll/ship.py` + `rig.py`, 9
      checks): time-domain turns reproduce the W5 anchors within 5 % —
      G1 93.5 vs 89.4 m, F1 117.2 vs 111.9 m, tightest 64.4 vs 62 m — with
      the oQ-4 hold-water brake (hold_frac = 0.02, diameter-anchored) and
      Taylor's fitted oar-race lever (4.8 m; decomposition open, register
      C3). Oar-only turns (hold/back per side) physically consistent;
      back-water = force-limited 80 % astern (manoeuvre 5.x). First
      command-language → physics pipeline: the sample script runs end-to-end
      (`ll/run_turn.py script`); rest-start still needs the oQ-13 ceiling.
- [x] Phase 1 Gate 4 — rower physiology (`ll/rower.py`, 8 checks): peak
      ceiling Fh_max = 700 N + W' endurance tank (P_crit = 80 W/man, R&W
      ch.23 primary; W_max = 10 kJ, tau = 120 s — provisional) + stroke
      adaptation (demand-limited drive, sweep shortening, tempo loss).
      Findings: steady = sustainable envelope (W' full, 30-min runs);
      spoude = W'-limited burst (~90 s then fade); rest start = short
      stretched strokes, Fh capped, launch slower than the bulk law;
      backing degenerates to the hold-brake at speed; exhausted side
      strokes slower -> differential yaw; tightest-turn W' drain narrows
      the halves-speed gap; rate 50 + exhausted = tempo lost (oQ-14:
      physical consequence, telemetry commanded vs achieved).
- [x] Phase 1 Gate 5 — oar inertia (`ll/oar.py` mit/t_rise, 7 checks):
      Fh = (Fn·l_cp + I·θ-ddot)/lin; catch spike + finish release as
      impulse-equivalent pulses (momentum closure exact; the flip energy
      ½Iω²·r/60 lives in the W' basis); Table 3.1 families via chain.py
      (spruce 9.7, old-zygian 18.0, old-thranite 13.1 kg·m²; tier-weighted
      9.7/14.7 per side); fleet = spruce | old-fir | none. Spikes reproduce
      oar_inertia.py (116/215/156 N, 1.85× handiness); hull observables
      unchanged (<1%); force-driven companion reproduces the Table 9.6
      drive time (0.43 s, essentially exact); ceiling holds both fleets.
      t_rise = 0.15 s provisional (register D10).
- [x] Phase 1 Gate 6 — per-tier crews (plan 15.1, 4 checks): SideCrew = 3
      TierCrews (31/27/27 per side, per-tier MIT + W′); the thalmian head-
      room as the ch.9 L-model power factor (0.9 cruise -> 0.6 sprint) with
      the feather clamp (the deadspot slips the blade); the thalmian share
      falls with rate (the trial character) and the 170-oar sprint
      overshoot closes (8.54 -> ~7.9 kt).
- [x] Plan 15.2 — Mark IIb resolved as an equivalence: Shaw's ch.9 form
      k·(q/p)²·V²·sin²C with the actual turning point reduces exactly to
      the flat-plate law (locked test); the slip-limit variant under-
      predicts (negative thrust — the measured kinematics are the truth);
      the shortfall is the unknown Mark II blade area (register A5, ~0.26
      m² as designed) — a data gap, not a law error.
- [ ] Phase 2 — HL from LL;  [ ] Phase 3 — harness;  [ ] Phase 4 — crew & environment;
      [ ] Phase 5 — oar-manoeuvres
