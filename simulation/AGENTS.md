# simulation — the simulators

Two simulators of the Olympias-class trireme sharing one command language. Design:
`./trireme-simulation-plan.md` (gates, equivalence contract, open questions
oQ-1…21). The validated physics they must satisfy: `../research/AGENTS.md` and
`../research/trireme-rowing-simulation-research.md`.

**Chain of trust: real-world data → LL → HL.** The LL's acceptance record —
every gate, anchor, result and honest mismatch — lives in
[`VALIDATION.md`](VALIDATION.md) (reproduce: run all `ll/tests/`; the current
  check count lives in the ledger, not here).
- `ll/` (low-level) is the oracle — per-oar physics, validated against the
  research numbers.
- `hl/` (high-level, Phase 2 — plan §19) is a fast approximation; its response
  curves are machine-generated from LL runs (`hl/calibrate.py` →
  `hl/calibration/calib_<id>.json`, the ship's default via `curves.default()`),
  never hand-entered, and every HL result carries its tolerance source
  (the equivalence record: VALIDATION.md §9).
- `harness/` (Phase 3) runs the same command script on both simulators and
  produces the Level-2 equivalence tables (`run_validation.py`).

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
hl/         fast ship-level sim (Phase 2 — plan §19)
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

## Phase status

- [x] Step 0 — command language: schema v0.1, parser, sample script
- [x] Phase 1 Gate 1 — one-oar LL: time-stepped oar == rigid model at all four
      Table 9.6 points (< 0.5 %); mean handle force 224/208 N (cruise family);
      prop W/man 102 % at 7.2 kt
- [x] Phase 1 Gate 2 — hull surge (`ll/hull.py`): surge-only
      m_app·dV/dt = N·F_oars(t,V) − D(V), per-step coupling. Settles on the
      hull=1.0 anchors (7.22 kt @ 28.8, 7.98 kt @ 36); sprint (130 oars,
      44.5 spm) brackets the 8.2–8.4 kt trial over the unmeasured t_drive
      range — the empirical oQ-18 answer: the flat-plate 0.078 m2 law is
      sufficient for the Olympias rig (Mark IIb shortfall stands, separate).
      Findings: stroke surge ripple ~0.2 kt; start-from-rest needs the oQ-13
      force ceiling (crude clamp exists, demo only); Table 9.6 data gap at
      44.5 spm (uncertainties register A8).
- [x] Phase 1 Gate 3 — 170-oar surge+yaw ship (`ll/ship.py` + `rig.py`):
      time-domain turns reproduce the W5 anchors — G1 89.7 vs 89.4 m,
      F1 117.4 vs 111.9 m, tightest 67.7 vs 62 m — with the oQ-4
      hold-water brake (hold_frac = 0.05, two-anchor calibrated) and the
      sway-calibrated oar-race lever (the C3 decomposition: 4.8 → 1.8 m,
      plan 15.3). Oar-only turns measured at 126.6 m (hold ≡ back — the
      hold-brake degeneration at speed); back-water = force-limited
      (manoeuvre 5.x). First command-language → physics pipeline: the
      sample script runs end-to-end (`ll/run_turn.py script`); the
      start-from-rest is physiology-limited (Gate 4). The current
      per-anchor numbers: VALIDATION.md §3.
- [x] Phase 1 Gate 4 — rower physiology (`ll/rower.py`): peak
      ceiling Fh_max = 700 N + W' endurance tank (P_crit = 80 W/man, R&W
      ch.23 primary; W_max = 5 kJ anchored to the ch.9 four-run sprint,
      tau = 120 s) + stroke adaptation (demand-limited drive, sweep
      shortening, tempo loss).
      Findings: steady = sustainable envelope (W' full, 30-min runs);
      spoude = W'-limited burst (~40 s at 44.5 spm — the measured drain
      130 W/man — then fade to the P_crit level); rest start = short
      stretched strokes, Fh capped, launch slower than the bulk law
      (6.0 kt @ 30 s, measured); backing degenerates to the hold-brake at
      speed; exhausted side strokes slower -> differential yaw; tightest-
      turn W' drain narrows the halves-speed gap; rate 50 + exhausted =
      tempo lost (oQ-14: physical consequence, telemetry commanded vs
      achieved).
- [x] Phase 1 Gate 5 — oar inertia (`ll/oar.py` mit/t_rise):
      Fh = (Fn·l_cp + I·θ-ddot)/lin; catch spike + finish release as
      impulse-equivalent pulses (momentum closure exact; the flip energy
      ½Iω²·r/60 lives in the W' basis); Table 3.1 families via chain.py
      (spruce 9.7, old-zygian 18.0, old-thranite 13.1 kg·m²; tier-weighted
      9.7/14.7 per side); fleet = spruce | old-fir | none. Spikes reproduce
      oar_inertia.py (116/215/156 N, 1.85× handiness); hull observables
      unchanged (<1%); force-driven companion reproduces the Table 9.6
      drive time (0.43 s, essentially exact); ceiling holds both fleets.
      t_rise = 0.15 s provisional (register D10).
- [x] Phase 1 Gate 6 — per-tier crews (plan 15.1): SideCrew = 3
      TierCrews (31/27/27 per side, per-tier MIT + W′); the thalmian head-
      room as the ch.9 L-model power factor (0.9 cruise -> 0.6 sprint) with
      the feather clamp (the deadspot slips the blade); the thalmian share
      falls with rate (the trial character) and the 170-oar sprint
      overshoot closes (8.54 -> ~7.9 kt).
- [x] Plan 15.2 — Mark IIb resolved as an equivalence: Shaw's ch.9 form
      k·(q/p)²·V²·sin²C with the actual turning point reduces exactly to
      the flat-plate law (locked test); the slip-limit variant under-
      predicts (negative thrust — the measured kinematics are the truth);
      the residual is the A5 area gap + the slip assumptions.
- [x] Plan 16 — the cant term in (Gate 7): vn = V·cosC·cos(φ) −
      l_cp·ω (identity at Olympias by construction); the Mark IIb prop
      fraction 0.30 → 0.51–0.54; the 'as-designed' scenario (cant + area
      1.3× + slip 1.2) reproduces the chain's 9.7 kt at 46.3 spm.
- [x] Plan 15.3 — the sway DOF (Gate 8) — **the LL physics is
      complete**: surge+sway+yaw, the physical CLR restoring moment, the
      C3 lever decomposition (4.8 → 1.8 m), the C1 Ω reconciliation
      (ship 3.2e6 / steady model 5e6); diameters held (89.7/117.4/67.7 m),
      t_360 98 s vs 128 (open discrepancy, no known cause), the drift
      −2.2°, lateral damping clean.
- Plan 17 — the turn build-up was implemented, measured (~2 s of the
      ~28 s discrepancy — negligible) and reverted: it is NOT the cause of
      the t_360 residual, which is recorded as an open discrepancy with no
      known cause (a linear yaw-damping form is an untested hypothesis).
- Plan 18 — the yaw-induced oar/water differential was implemented,
      measured (inside oars ~3.15 % stronger — a yaw damper, per the
      correct sign; t_360 +1.0 s of the ~30 s gap) and reverted — real but
      far from the discrepancy's size, complexity not justified. The t_360
      remains the one open discrepancy, no known cause.
- [x] **Phase 2 — the HL** (plan §19): the curve-chasing fast ship
      (`hl/`) with its response curves machine-calibrated from the LL
      (`hl/calibrate.py` → `hl/calibration/calib-2026-08-15-b55e28f.json`;
      the loop ran three rounds, each fixing a real protocol bug —
      VALIDATION.md §9.3). The Level-2 equivalence through the harness:
      all five turns within ±1.3 %, fatigue −0.005 pts, the cruise gates
      inside on the non-turn scripts; the measured divergences (the drift
      floor, the back-tail transition, the turn deceleration) documented
      with their triggers — VALIDATION.md §9.
- [x] **Phase 3 — the harness core** (plan §20): `harness/script.py` +
      `comparator.py` + `run_validation.py` + the script set — the
      equivalence tables are the acceptance record (VALIDATION.md §9);
      the annotated script run is the remaining item.
- [ ] **Full validation** (plan §21, coverage map VALIDATION §10): the
      comparator's missing gates (settled rate, 3-NM), the turn-heavy
      mean-speed fixes, the ch.7 Mark II triple check, the t_360
      hypothesis, the Mark IIb blade layer.
- [ ] Phase 4 — crew & environment;  [ ] Phase 5 — oar-manoeuvres
