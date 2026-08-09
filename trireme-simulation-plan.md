# Trireme Simulation Pair — Plan (first draft)

Two simulators of the Olympias-class trireme, sharing one command language:

1. **High-level simulator (HL)** — the whole ship as one entity: hull dynamics, speed,
   helm, crew condition; runs courses over hours of operation. **Goal: fast and
   efficient** — an approximate ship that answers "what can the ship do?" in seconds.
2. **Low-level simulator (LL)** — the physical system: hull forces plus **every oar and
   rower individually** (170 oars), with blade hydrodynamics, oar inertia,
   catch/drive/recovery timing, per-rower output. **Goal: as close to reality as the
   research permits** — and its purpose is to probe and **sanity-check the high-level
   simulator**.

Both must accept the **same commander commands** and interpret them with equivalent
intent: whatever a trireme commander can order (stroke rhythm, oar state, helm, sprint,
rest, hold or back water), either simulator must execute faithfully — one at ship level,
the other at the level of every oar.

Status: **draft v0.4.** Step 0 (command language scaffold, `trireme-sim/`) is
implemented and tested; open questions are numbered oQ-1…oQ-21 in §10 and flagged
inline; research gaps are tracked in §9. Nothing here is accepted research until it
has a source citation or a validated run.

---

## 1. Purpose and goals

- **The two goals are different by design.**
  - *HL — speed and efficiency.* A fast, cheap ship-level integrator: seconds per
    simulated hour, suitable for plans, what-ifs, trip times, and interactive command
    drills. It trades micro-detail for computation: v (m/s) from mv-dot = F, without 170
    blade force calculations.
  - *LL — fidelity.* A slow, faithful physics sandbox: every oar, every blade, every
    rower, at sub-stroke resolution. It is exactly as expensive as it needs to be to be
    right. It exists to produce *truth* — to the limit of the repository's validated
    data — and to **catch mistakes in the HL**: when the HL says 6.9 kt at `rate 30`,
    the LL must be able to confirm or refute that number.
- **The shared command language binds them**: a command script (interactive or replayed)
  must run on both simulators and produce consistent, auditable outcomes.
- **Grounding**: both are built on the validated research chain in this repository (§5).
  The LL may add physics; the HL may cut physics; neither may contradict the validated
  numbers without a documented reason.

## 2. Design principles

1. **Two audiences, two fidelity contracts.** Everything is ultimately measured against
   reality; the chain of trust is:
   - the **LL is the oracle** — it must satisfy the repository's validated numbers and
     any trials data (physics-anchored acceptance, §6);
   - the **HL is an oracle-to-LL approximation** — it must stay within a documented
     tolerance of the LL on equivalent inputs (equivalence contract, §6);
   - the HL's tolerance bands are **annotated in its output** ("±1 % of LL, recorded at
     calibration run X"), so a user of the HL always knows its credibility ceiling.
2. **One command language, one clock, one contract.** Same script + same starting state +
   same environment → equivalent ship behaviour, with the LL as judge.
3. **Shared assets.** Both simulators link the same data files; no duplicated numbers:
   - rig geometry — `research/lane-4-oars/rig-geometry.md`: tiers 62/54/54, thole-pin
     positions, interscalmium 0.888 m, inboard 1.092 m (along the oar), sweeps
     48.1 / 48.4 / 55.6°, blade 0.55 m, blade area 0.078 m²;
   - oar inertia — `research/data/shaw-table-3.1-oar-inertia.csv` (MIT, k², centre of
     gravity, X per oar; see `research/lane-4-oars/oar_inertia.py`);
   - power chain — `research/lane-4-oars/lane4_propulsion.py`: W_hull = 155V³ + 4.13V⁵
     (×1.08 Mark II), P = 7.43·r, E = 0.756–0.78, pull length per design;
   - per-stroke blade model — `research/lane-4-oars/rigid_oar_model.py`: flat-plate
     normal force Fn = 0.5·ρ·A·C_N·|v_n|·v_n, C_N = 1.8;
   - hull — `research/lane-3-hull/`: parametric form (LWL 32.2 m, displacement 41.4 t
     trial / 25.2 t light; KM caveat on record);
   - manoeuvring — `research/lane-5-manoeuvre/manoeuvre-model.md`: apparent mass
     1.10·m, thrust 17.4 − 0.967·v kN, 3-band drag, rudder model, F1–F6 and G1–G5 turns
     validated within 7%;
   - environment — `research/lane-2-waves/`: Shaw Tables 8.1–8.4 (wave height, length,
     celerity vs windspeed, fetch, duration) and Carter's growth equations.
4. **Layered fidelity.** A faithful physics core plus an explicitly labelled "tuning"
   layer for playability. Tuning never silently overrides physics: every tunable is
   documented, logged, and swappable.
5. **Deterministic and replayable.** Seeded RNG, logged command stream, logged state; a
   "ghost" mode replays any script identically.
6. **Anciently auditable.** Every command mapping to an attested or plausible ancient
   practice where evidence exists; the mapping table is itself a deliverable (oQ-3).

## 3. The command language — the core deliverable

### 3.1 Requirements

- One vocabulary for both simulators; the LL adds detail, never verbs the commander
  cannot give.
- Complete enough for the operational phases that matter: cruise, sprint, turn
  (rudder and oar-assisted), come to a halt, emergency.
- Composable: a rhythm (cadence) layer, an oar-state layer (global or per side), and a
  helm layer (rudder only, oars only, or both).
- Typed arguments (number, enumeration, side, bearing) with sensible defaults: "just
  sprint" must not require a form.
- A human, a script, and later an AI, all speak the same vocabulary.
- **v1 interface: CLI only** — commands arrive as a timestamped text file (one
  command per line: time, verb, args); output is text. No GUI, no web console
  (see §3.5 for the file format).

### 3.2 Proposed vocabulary (v1) — the battle set

Filter: what can a trierarch **shout**, and what can 170 rowers **act on**, in the din
of battle? The rhythm comes from the pipe (*auloi*), the keleustēs relays short shouts
bank by bank, and the helmsman works the rudders. Anything that cannot be heard once
and executed without a manual is out. Result: **4 crew verbs**, down from 14. Status
output is the CLI's business, not the commander's — no `report` verb (dropped list).

| verb | arguments | the shout | what the crew does | notes |
| --- | --- | --- | --- | --- |
| `rate` | spm (0–50); aliases slow/working/racing | "σπούδην!" (pipe speeds up) | every rower takes the cadence: cycle = 60/spm, drive/recovery split (Table 9.6 ≈ 33–45 %) | ship-global: both sides listen to the same pipe — no per-side rate |
| `oars` | state: row / hold / back / bank; optional side (port \| starboard; default both) | "καθίετε!" (oars down), "ἔχε!" (hold!), "πρύμναν ἀνακρούου!" (back water!), "ἄρατε κώπας!" (oars up!) | per-side blade hydro regime: driving / stopped / backing / out of water | per side, never per tier: a side's tiers share one state — their blades share that side's water (per-tier states would collide). Tiers differ in phasing and reach, not in commanded state |
| `pressure` | rest / steady / fast / spoude, or 0–1; optional side (default both) | "σπουδῇ!" (with haste!) | effort per stroke on the given side: scale the mean handle-force profile, P = 7.43·r·pressure | per-side effort is a steering tool — one side pulling harder turns the ship (differential oar-work) |
| `helm` | port / starboard / midship; fraction optional | "πηδάλιον ἐπὶ δεξιά!" (helm to starboard!) | the helmsman puts the rudders over (F/G-validated rudder model) | oar-assisted turns are expressed via per-side `oars`, not here |


Scoping: `rate` is ship-global; `oars` and `pressure` take an optional `port` /
`starboard` (default: both); `helm` is the rudder. There is no per-tier scope — the
tiers of a side always share a state.

**Dropped from the v0 list, and why** (replacement in parentheses):

- `speed` — nobody shouts a knots target at a battle; rate + pressure *produce* speed.
  Derived output only (oQ-2 resolved).
- `go` — redundant: the phase clock starts at the first rowing command (`rate` > 0 or
  `oars row`); the keleustēs' "ready … pull!" is modelled, not spoken. Determinism
  rule: all blades begin at the catch (§3.3).
- `course` — the commander doesn't shout bearings in battle; holding a heading is the
  helmsman's context, supplied as scenario input (oQ-6). A benchmark script that needs
  a course to hold reads it from the scenario, not from a verb.
- `report` — status is the CLI's business, not the commander's: the driver prints an
  end-of-run summary (and can sample at fixed times via a flag); telemetry never
  enters the shared language.
- `oar-assist` — redundant: turn-by-oars is exactly per-side `oars hold/back/bank`.
  (oQ-7 resolved: no named attack verb either — a ram run is `rate 44` + `pressure
  spoude`, steered with `helm`.)
- `rest` — a consequence, not a command: `oars bank` (+ `rate 0`). A resting half-bank
  is `oars bank` + side (oQ-8 partly resolved).
- `crew` — watch planning is scenario state, not battle vocabulary; crew condition
  stays an internal model (oQ-15).
- `sea` — the environment is input, not an order: a shared file both sims read (oQ-5
  resolved).
- `anchor` — not worrying about anchoring for now: coming to a halt is `oars bank`;
  dropping the anchor stone is ship state, not a rower action.
- `stop` — covered: `oars bank` ends rowing; the end of the script ends the run.
- `trailing` / `feathered` oar states — not distinctly executable mid-battle: the
  feather is part of the recovery, trailing ≈ hold or bank.

### 3.3 Rhythm and cadence

- `rate` is a cadence imposed on all rowers: cycle period, drive/recovery split (Table
  9.6 effective-pull times ≈ 33–45 % of the cycle), and a phase clock for synchronisation
  and cueing (pipe/drum analogue).
- The LL consumes the cadence as a schedule; the HL treats it as a scalar indexing
  response curves.
- **Starting is implicit — there is no `go`**: the phase clock begins at the first
  rowing command (`rate` > 0 or `oars row`), all blades at the catch. The keleustēs'
  count-in is modelled, not a verb.
- oQ-12: also expose stroke *shape* (long/medium/short)? Real range: up to 1.1 m
  unrestricted, ~0.99 m effective (canted), 0.87 m (straight rig). A `stroke-length`
  command in v2 would parameterise blade immersion time and pull length.

### 3.4 Manoeuvring by oars

- The LL must support **turn on the oars**: one side rows while the other holds or
  backs (`oars hold|back <side>`) → asymmetric thrust → yaw; hold water on one side
  to brake-turn. The *anastrophe* family (quick reversal) = `oars back` on one side
  while the other rows.
- The mapping from one commander order to per-side steps is a design target and a prime
  validation case against the F/G-turn records.

### 3.5 Script file format (v0) — the CLI input

No fancy UI for now: the commander's orders arrive in a **plain-text file**, one
command per line, `#` comments allowed, timestamps in seconds from script start:

```
# time_s, verb, args...        (comma- or space-separated as you prefer)
0, rate, 30
600, pressure, spoude
900, rate, 44
1020, helm, port
1200, oars, hold starboard
1260, oars, back starboard
1440, rate, 24
1500, pressure, steady, port
1800, oars, bank
```

- The schema parser (`commands/schema.json`) validates every line before the run:
  unknown verbs, bad arguments, out-of-range rates are rejected up front
  (deterministic, no silent mid-run surprises).
- Commands at the same timestamp apply in file order; the file is read once into an
  event list and consumed on the shared clock.
- The same file drives the HL, the LL and the harness — one script, two ships.
- A later v2 nicety: an interactive stdin loop ("type a command, advance time") —
  not needed for v1.
- No `stop` or `anchor` in v1: coming to a halt is `oars bank`; the run ends when the
  script ends. Starting is implicit (§3.3). The CLI prints the status summary at the
  end of the run — there is no `report` verb.

## 4. High-level simulator — the fast and efficient one

- **State**: position, heading, speed, effective rate, held course (scenario input),
  crew condition, environment, position in the command sequence.
- **Dynamics** (reduced set, per validated chain):
  - forward: m_app·dv/dt = Thrust(V, r, pressure) − hull_drag(V) − wave_penalty, using
    the P = 7.43·r chain mapped to hull force (W = n·P·L·r·E/60 via
    `lane4_propulsion.py`);
  - steering: yaw from rudder + optional oar moment (`manoeuvre_model.py`).
- **Response curves instead of per-oar work**: cruise rate → speed (ch.7: 25.5 / 28.8 /
  32.3 spm at 7 / 7.5 / 8 kt), sprint (44.5 spm → 8.2–8.4 kt; measured 8.2–8.3), turn
  diameter from the F/G sets. **These curves are regenerated periodically from LL runs**
  (calibration, §6) so the HL stays honest as the LL advances.
- **Crew model**: cumulative man-hours, fatigue → power ceiling (gross 115 / 145 / 180
  W/man at 7 / 7.5 / 8 kt; fixed-seat ≈ 60–65 % of VO2max).
- **Step**: 0.5–1 s. **Outputs**: telemetry + commander summary. **Performance target**:
  ≪ real time (minutes of ship-time per second of wall-clock).
- **Implied accuracy**: label every result with the tolerance band derived from the last
  calibration (e.g. "speed ±1.5 % vs LL of calibration run #47"). A fast simulator that
  forgets its own error bars is only a number machine.

## 5. Low-level simulator (the reality-grade one)

- **Entities**: the hull (surge + yaw first; sway / pitch / heave later, oQ-10),
  170 rowers / 170 oars (id ↔ tier per rig geometry), the rudder per manoeuvre model.
- **Per-oar loop** (dt ≈ 0.01–0.05 s):
  1. cadence phase from `rate` and stroke length (catch, drive, finish, recover);
  2. blade state from `oars` → hydro regime (row / hold / back / banked);
  3. blade force from the flat-plate model: Fn = 0.5·ρ·A·C_N·|v_n|·v_n at the blade
     centre of pressure (0.26 m from tip), including the phase where the blade would
     otherwise outrun the ship (drag, not thrust — the "deadspot" regime);
  4. handle force: F_handle·l_in = F_blade·l_cp + I_thole·θ-ddot (inertia live from
     Table 3.1 per oar; the catch-flip spike from `oar_inertia.py`);
  5. rower output: mean-force × stroke-shape profile, capped by crew state and VO2;
  6. sum all 170 oar forces and moments onto the hull (per-side sums → yaw);
  7. hull update: surge/sway/yaw, resistance, rudder, waves at each blade.
- **Per-tier heterogeneity** — capability only, never commanded state: the tiers of a
  side always share one state (their blades share that side's water). Thranite/zygian/
  thalamite stroke limits (e.g., thalmian head-room limit ≈ 720 mm vs 800 mm design),
  oar-inertia families (spruce vs old firs — handiness), per-oar fatigue.
- **Waves**: water velocity at each blade from the shared environment; wave induced
  drag/thrust content comes out of the flat-plate force law naturally.
- **Speed budget**: 170 oars is feasible in Python at the dt above; per-tier symmetry
  can collapse the cost for straight-line runs where the tiers are identical, reserving
  per-oar spread for manoeuvres (oQ-19).
- **Truth role**: the LL is the pair's measuring instrument. Its outputs (per-oar force
  history, wave-riding energy, turn rate in plane, achieved rates) are what the HL is
  charged with getting approximately right, and what any new validation data
  (wind-tunnel, tank, or trials) first confronts.

## 6. The pair contract — equivalence, calibration, and honesty

**The chain of trust: real-world data → LL → HL.** The LL is validated *down* to the
repository's numbers and trial records (reality); the HL is validated *sideways* against
the LL (approximation); the HL's error is then quantified, not hand-waved.

**Level 1 — LL vs reality (physics-anchored acceptance):**

- cruise rates: 25.5 / 28.8 / 32.3 spm at 7 / 7.5 / 8 kt (ch.7);
- sprint: 44.5 spm → 8.2–8.4 kt (ch.9, measured 8.2–8.3);
- manoeuvre: F1–F6 and G1–G5 turn diameters within ±7 % of the model;
- per-oar: mean handle force ≈ 210–225 N; catch-flip spike per `oar_inertia.py`; the
  old-fir ≈ 2× spruce handiness figure reproduced.

**Level 2 — HL vs LL (equivalence, first tolerances to refine):**

- |mean speed difference| < 1 % over a 10-minute script including a sprint and a turn;
- settled stroke rate within 1 spm;
- time to 3 NM within 1 % (held course supplied as scenario input, oQ-6);
- standard G1/F1 turn diameter within 5 %;
- accumulated crew fatigue within 5 %;
- final position within ~0.1 NM after course changes.
Every HL result carries the tolerance source (calibration run id).

**Harness**: `script.py` runs the same command script on both simulators with the same
seeded environment and starting state, then produces the equivalence table above.

**Calibration**: HL response curves are regenerated from LL steady-state runs
(`calibrate()`); when the LL gains fidelity, the HL curves are refreshed and the
tolerance annotations updated. The HL is never hand-tuned to old self-numbers; it is
re-fitted to the LL's new truth.

## 7. Architecture sketch (python, matching the repo)

```
trireme-sim/
  commands/       # the language: schema + parser + examples
    schema.json   # verbs, args, enums — single source of truth
  common/         # shared rig/oar/sea assets (rig.py, oar_data.py, waves.py)
  hl/             # fast high-level simulator (§4)
  ll/             # per-oar low-level simulator (§4b)
    oar.py, rower.py, blade.py, hull.py, rudder.py
  harness/        # script loader, runner, comparator, calibrate (§6)
  cli/            # CLI driver: run a script file (§3.5) on hl|ll, print text output
```

- Determinism: fixed dt, fixed ordering, seeded RNG; state is a plain record for
  snapshots. Runs log the command stream and per-entity telemetry.

## 8. Roadmap (draft)

0. **Phase 0 — command language & contract.** Freeze the verb set (§3.2: 4 crew
   verbs), write the schema, settle the remaining semantics (oQ-4) and freeze the
   §3.5 script-file format. Deliverable: `commands/schema.json` v0.1 + a sample
   script.
1. **Phase 1 — LL first.** Get the per-oar sandbox working and validated against ch.9
   tables (blade forces, drive times, hand-rule). This is the truth engine; best to own
   it before the HL extrapolates from it.
2. **Phase 2 — HL from LL.** Build the fast ship-level integrator, but generate its
   response curves **from the LL**, not from hand-entered numbers; ships first
   consistency gates vs ch.7 cruise and ch.9 sprint.
3. **Phase 3 — the pair harness.** Run the same scripts on both; produce the first
   equivalence table; fix the biggest violations; document where HL must stay loose.
4. **Phase 4 — crew & environment.** Fatigue, VO2 ceiling, sea state as driven inputs;
   long-run scenarios; reach limits from `oar-data.md` §6.
5. **Phase 5 — oar-manoeuvres.** Anastrophe family, banked turns, backing; validate
   against recorded turn data.
6. **Later/optional** — visuals; faster core (Rust/C); historical scenario pack; AI
   commander emitting the same language (major goal; the vocabulary v1 is designed for
   it).

## 9. Risks and unknowns

- **Blade deadspot energetics** — LL must not overcount energy; rigid-model mean-quantity
  match is the guard (also its own journal risk).
- **Per-oar cost** — Python budget for 170 oars (oQ-19); symmetry reduction decisions.
- **Rower model least validated** — force curves from S6, ch.7; per-stroke shape assumed;
  keep in the uncertainties register and label clearly in LL outputs.
- **Displacement spread** 25 / 42 / 47 t in research — freeze one (default trial 41.4 t),
  document (part of oQ-15).
- **Turn data** — F/G sets are 6–6.5 kt and specific water; turn-by-oars data are
  thinner (oQ-3).
- **HL "good-enough" set**: the HL approximation must not drift silently over long
  scripts; the equivalence table is checked on every calibration.

### 9.1 Research gaps vs implementation readiness

**Verdict: nothing here blocks Phases 1–3.** The LL skeleton, the HL-from-LL build and
the pair harness consume only the validated chain (§2.3); the acceptance floor becomes
executable fixtures in `ll/tests/`. The gaps below all bite in Phase 4 or later, or are
parked items that do not affect the build.

| gap | needed by | status | what would close it |
| --- | --- | --- | --- |
| **Crew endurance/duration model** — how long a given `rate`+`pressure` is sustainable before output drops | Phase 4 crew model; HL long-run scenarios | open — power-at-rate (115/145/180 W/man) and VO2 ceiling exist, but no validated duration curve | primary-source work: ch.7/9 Olympias sustained-run records; S6 fixed-seat ergometer studies |
| **Wave-induced added resistance** — drag penalty of a sea state at a heading | Phase 4 environment | open — Shaw tables give sea *states*, not resistance penalties | standard naval-architecture added-resistance estimate as labelled tuning (layered fidelity), or dedicated research if fidelity demands |
| **Ergonomics digits** — ANSUR 1988 50th-percentile values; Greek mean height ≈ 1.70 m | Phase 4 / oQ-13 (reach, stroke length) | flagged [?] in `trireme-rowing-simulation-research.md` | focused primary-table read (DTIC ADA225094) |
| **Turn-by-oars (anastrophe) quantitative data** | Phase 5 oar-manoeuvres | thin — F/G sets are rudder turns at 6–6.5 kt | qualitative validation vs ancient descriptions + physics consistency; F/G sets remain the quantitative floor |
| **A/B MIT anomaly** (Table 3.1, confined to the MIT cell, ≈ −9.7 % deviation) | none | resolved as recorded-as-printed, flagged in `oar-data.md` | only the physical 1994/1996 report raw appendix could settle it; parked |
| **Taylor Excel workbook** (yaw-resistance coefficient 5×10⁶–6×10⁶ kg·m² [?]) | Phase 5 yaw fidelity (nice-to-have) | leads exist (Wolfson archive) | contact archivist@wolfson.cam.ac.uk; not required — F/G turns validated ≤ 7 % cover the turn model |

Two expectations that shape the build:

- **Phases 1–3 need no new research by design** — the HL's response curves come from LL
  runs, and the LL reproduces numbers we already hold.
- **The LL generates the next research questions.** oQ-18 is the first example: whether
  the flat-plate law + deadspot reproduces 8.2–8.4 kt at 44.5 spm *without* the ×3.3
  Mark IIb tuning is answered by running Gate 2, not by reading. New gaps discovered in
  runs go into this table with their closing evidence.

## 10. Open questions (first pass, oQ-1…oQ-21)

**Command language**

- oQ-1 — **Resolved (for now): 4 crew verbs (§3.2).** Can it go below 4 without
  losing an attested capability?
- oQ-2 — **Resolved: `rate` + `pressure` are the power controls** (pipe + shout);
  `speed` is a derived output, not a verb.
- oQ-3 — Attested-ancient mapping: which commands map to attested signals (*keleustēs*
  signals, "bend to the oars", "hold water", "back water", *anastrophe*)? Deliverable:
  the mapping table; a "historic mode" accepts attested phrases as aliases.
- oQ-4 — Oar-state semantics: is "hold water" one hydro state or a spectrum (flat,
  crossed, partly)? The per-oar specs the LL must implement.
- oQ-5 — **Resolved: the environment is input, not a verb** — a shared file both sims
  read (oQ-16 covers where it lives; format still open).
- oQ-6 — **Resolved for v1: one console, the battle commander's voice.** Helmsman
  context (a course to hold) and watch/keleustēs duties are scenario state, not
  verbs.
- oQ-7 — **Resolved for v1: no named attack verb**; a ram run is compositional
  (`rate 44` + `pressure spoude`, steered with `helm`). Revisit only if diekplous/periplous
  formations need distinct behaviour.
- oQ-8 — **Partly resolved:** a resting half-bank is expressed as per-side `oars bank`;
  the watch/fatigue *scheduling* model stays an internal question (oQ-15).

**Physics / model**

- oQ-9 — Blade hydro fidelity: flat-plate (validated for mean quantities) vs needing
  added-mass/stall detail (v1 → flat + explicitly labelled taper; goal: equal the
  rigid-model numbers).
- oQ-10 — Hull DOF: surge + yaw first; when do we add heave/pitch for wave-blade
  interaction?
- oQ-11 — Blade ends: re-immersion/stroke-ends energetics without breaking the drive
  ("blade in quiet water at the catch").
- oQ-12 — Stroke shape (`stroke-length` command in v2? /long/short mapping to the
  0.99 vs 0.87 m effective lengths).
- oQ-13 — Rower capability constants and ceiling (fixed-seat limits; per-standard
  sustained VO2).
- oQ-14 — Impossible-command behaviour: hard error vs warning+clamp? (must match in
  both simulators).
- oQ-15 — Freeze displacement/mass baseline; define the internal crew-condition model
  (no `crew` verb in v1).
- oQ-16 — Where does the environment state live? (recommend a shared `common/` environment entity)
  — one entity for both sims.
- oQ-17 — Role model detail: trierarch-permission split for the console; what the
  keleustes can order vs the helmsman.
- oQ-18 — Sprint-regime honesty: flat-plate with 0.078 m² under-estimates pressure at
  8.3 kt (Mark IIb needs ×3.3 area per ch.9 note) — tune above the documented band,
  or stay strict and journal.
- oQ-19 — LL budget: run length and dt targets, wall-clock budget, tier-symmetry plan.
- oQ-20 — **Resolved ('no fancy UI'): v1 is a CLI** — timestamped text script (§3.5)
  in, text summary out. Only remaining question: the interactive "type a command,
  advance time" stdin loop — a v2 nice-to-have or never?

**The pair**

- oQ-21 — How fast does HL need to be relative to LL, and how tight should its LL error
  band be before "sanity checks" stop being meaningful? (e.g. 0.5 % vs 5 % per row;
  the answer drives Phase 2/HL approximating architecture.)

## 11. Definitions of key terms

- **cadence** — the rhythmic schedule for all rowers: rate (spm) fixes cycle period,
  drive and recovery time; carries phase synchronisation.
- **pressure** — multiplier on the mean pull relative to the nominal schedule
  P = 7.43·r·pressure.
- **oar state** — the four blade states a rower can execute: `row` (driving),
  `hold` (blade stopped in water — a brake), `back` (driven the other way),
  `bank` (out of water). The feather is part of the recovery, not a separate command.
  Scoped per side (default both); the tiers of a side always share a state.
- **anastrophe** — the ordered, quick-reversal turn; in commands it is a combination
  (one bank holding / banked), not a primitive.
- **oracle** (in this plan) — the simulator that other things are judged against: the
  LL is the oracle vs reality; the HL is judged against the LL.
- **scenario input** — world state the sims read but nobody shouts: sea state, start
  position and heading, the helmsman's held course. Lives in `common/`; never in the
  verb set.


## 12. Phase 1 Gate 4 — the rower physiology layer (oQ-13): **implemented**

`ll/rower.py` (SideCrew) + `ll/ship.py` integration, 8 Gate-4 checks, all 55
checks green (commit 438585a). Replaced the crude demo clamp with a
physiological rower: peak force ceiling, endurance/fatigue, and their effect
on stroke length and rate. Resolves oQ-13, answers oQ-14 (impossible commands
→ physical consequence + telemetry), and unlocks rest-starts, honest backing,
sprint time-history, and asymmetric-side behaviour.

### 12.1 The anchors (all from our own chain, all consistent)

| Quantity | Value | Source | Status |
| --- | --- | --- | --- |
| Sustainable external power P_crit | **≈ 80 W/man** | Rossiter & Whipp, Rankov ch.23 (verified in our text dump: "maximum estimate of ~80 W per oarsman … for external power production", below lactate threshold, RER ≤ 0.74) | `[x]` primary |
| Self-check | 7-kt cruise = 79.5 W handle power (ch.7, 25.5 spm) | matches R&W to 0.6 % | `[x]` |
| Gross at 7 kt | 115 W/man (80 external + 34.8 oar-absorbed) | ch.7 | `[x]` |
| Sprint external power | ~190 W/man @ 44.5 spm (L = 0.78 Olympias); ~240 W (L = 0.99 Mark IIb) | ch.9 | `[x]` |
| Sprint gross | ~265–320 W/man (D4 "300 W/rower Mark IIb short sprint") | register D4 | `[x]`/`[?]` |
| Anaerobic capacity W′ | **5 kJ/man in use** — anchored | ch.9 four-run sprint: 8.2–8.3 kt sustained ~45 s at 44.5 spm → excess 116.6 W/man × 45 s ≈ 5.2 kJ; ¾-NM 6.5-min run implies ~9.5 kJ (2-parameter CP tension — register D7) | `[x]` anchor / tension noted |
| Peak handle force Fh_max | **700 N in use** (model-implied) | chain max mean pull 330 N × peak ≈ 2×; no force traces in our sources (ch.4 ergometer = 6-min power tests only; S6 = session marker, not a source) — register D8 | `[?]` |
| Recovery floor | ~0.5 s (in use) | body mechanics | `[?]` |
| W′ refill time constant | **120 s in use** (provisional) | literature band ~1–3 min; ch.22 sources (Monod/MacFarlane/Nadel, Daedalus) constrain long-term endurance only — register D9 | `[?]` |

### 12.2 The model (per side in v1 — the Ship's existing structure)

1. **Command → demanded mean handle force**: steady/fast = P = 7.43·r·pressure
   (unchanged chain); **spoude = the burst level Fh_BURST = 330 N** (the chain's
   sprint mean pull at 44.5 spm — the W′-limited maximum at any rate). The
   demand sets the drive ω via the blade resistance (the stroke follows the
   force), not the other way round.
2. **Instantaneous ceiling**: Fh_max (per-rower equal in v1; per-tier factors
   as parameters — the thalmian head-room limit already lives in the rig data).
3. **Endurance state**: a W′ tank per side — drains when gross power exceeds
   P_crit_gross (= 80 W + oar_absorbed(r)), refills at rest with time constant
   τ. Available mean force = f(W′ state).
4. **Stroke adaptation at fixed tempo** (the pipe is master): Fh_max →
   ω_max(V) → B_eff = min(B, ω_max·t_drive) — the stroke shortens, not the
   tempo. If B_eff < B_floor (~40 % of B) the rate is unattainable at that
   pressure → achieved rate falls; the **weakest side governs** the common
   rate.
5. **Power accounting**: P_external = Fh·B_eff·lin·r/60 (the oar-level form of
   the L·P·r chain); gross = external + oar_absorbed(r); W′ drains on gross
   excess.
6. **Backing**: force-limited weak backing (the 12× problem disappears — the
   ceiling governs ω, exactly as in the start).
7. **Hold**: the calibrated 2 % brake stays (isometric fatigue cost = v2).

### 12.3 What this changes in the ship

- `Ship` gains per-side: B_eff, achieved_rate, W′ state; telemetry reports
  **commanded vs achieved** for rate and pressure (oQ-14's answer: physical
  consequence + explicit report — never an error, never a silent clamp).
- The crude `--fh-max` clamp is deleted; `ll/rower.py` replaces it.
- `rate` remains a demand; achieved tempo is output, not input. (The
  equivalence contract's "settled stroke rate within 1 spm" needs care when
  the crew legitimately falls off tempo — HL must mirror the physiology or the
  tolerance applies to achieved rate.)

### 12.4 Command semantics become physiological

- `pressure steady` = sustainable (P ≤ P_crit; the ch.7 cruise envelope);
- `pressure spoude` = W′-limited burst (the ch.9 sprint is its anchor);
- `fast` between; `rest` = minimal. Schema numeric anchors replaced.

### 12.5 Validation gates — **all passing (8 checks, `ll/tests/test_gate4.py`)**

- G4-1 ✓ sustained: steady = the sustainable envelope — W′ full, speed stable
  over 30 min at 25.5/28.8 spm.
- G4-2 ✓ sprint: spoude bursts (W′ drains in ~90 s), speed fades toward the
  sustainable cruise — the trials' time-history.
- G4-3 ✓ rest start: short stretched strokes (sweep shrinks to ~57 %, drive
  stretches to the tempo slot); peak Fh ≤ 700 N; launch **slower than Taylor's
  bulk law** (7.2 kt @ 30 s vs 9 kt @ 24 s) — the physiology governs the start.
- G4-4 ✓ backing: **degenerates to the hold-brake at speed** (the flow drag
  exceeds the rower's grip); active + weak at low speed.
- G4-5 ✓ asymmetric: exhausted side strokes slower (mean-limited) → differential
  thrust → yaw (~215° in 3 min at 40 spm); tiny deadspot refills snap the W′
  step-function back to full demand (classic critical-power behaviour).
- G4-6 ✓ tightest-turn re-check: W′ drains at sprint effort → speed fades to
  ~4.4 kt from 6.6 kt peak — the "halves speed" mechanism, now emergent.
- G4-7 ✓ impossible command: `rate 50` + exhausted from rest → tempo lost
  (achieved ~40 spm), telemetry shows commanded vs achieved — oQ-14's answer.
- G4-8 ✓ regression: 19 + 7 + 12 + 9 checks green with the physiology on.

Implementation notes: the Oar became angle-based (effective ω per catch);
the keleustes call-down re-syncs both sides at the weaker side's rate; two
real bugs fixed en route (stale t_drive in the sweep-shortening branch;
pressure now scales force through the demand).

### 12.6 Research to run alongside (small, mostly in-house)

1. [x] Extract R&W ch.23 and pin the 80 W context — done during planning
   ("maximum estimate of ~80 W per oarsman … for external power production",
   below lactate threshold, RER ≤ 0.74; self-consistent with ch.7 to 0.6 %).
2. [x] **Ch.9 four-run sprint durations → W′**: each run sustained max speed
   ~45 s (8.2/8.3 kt) → W′ = 5 kJ/man (sim burst window now ~43 s, matching);
   the ¾-NM 6.5-min calibration run (104.3 W/man, P = 288 N = 7.43·38.75 ✓)
   implies up to ~9.5 kJ — 2-parameter CP tension recorded (register D7).
3. [x] **"S6" identified**: a session marker (paleo-bioenergetics session),
   not a force-curve source. Ch.4 ergometer tests report 6-min POWER outputs
   (16–29 % efficiency) but no force traces → Fh_max = 700 N stays
   model-implied (chain max mean pull 330 N × peak ≈ 2×), register D8.
4. [x] **W′ refill τ**: ch.22's Monod/MacFarlane/Nadel/Daedalus sources
   constrain long-term endurance (4-h-on/2-h-off shifts) and the
   "2-min ≈ 1.2× 6-min" power rule (ch.4), not W′-kinetics; τ = 120 s stays
   literature-based (register D9).
5. [ ] Per-tier stroke factors: thalmian head-room already quantified
   (effective L); per-tier Fh factor = open (v2).

### 12.7 Deliverables

`ll/rower.py` (Fh_max, P_crit, W′, τ; per-side aggregates), `ll/ship.py`
per-side stroke adaptation + weakest-governs + telemetry, physiological
pressure anchors in `schema.json`, `ll/tests/test_gate4.py`, register rows
(W′, τ, Fh_max status), oQ-13/14 resolution notes.

## 13. Phase 1 Gate 5 — the oar inertia layer: **implemented**

`ll/oar.py` (mit/t_rise) + `common/chain.py` (Table 3.1 families) +
`ll/ship.py` (fleet), 7 Gate-5 checks, all 62 checks green.
The massless lever becomes a rigid body about the thole:

    Fh = (Fn·l_cp + I_thole·θ-ddot) / lin

which adds the catch-phase inertia spike (spinning the oar from rest to the
drive speed over the water-entry time t_rise), the finish-phase release (the
oar's momentum assists), and the handiness differences between the Table 3.1
oar families. The research is done — this gate wires it into the LL.

### 13.1 The research (done, decoded & verified)

- Table 3.1 (ten oars, MIT about the thole): family means — **spruce 9.7,
  old-zygian 18.0, old-thranite 13.1 kg·m²** (m_hand 8.2 / 15.1 / 11.0 kg at
  1.092 m). A/B MIT anomaly recorded as printed (register; zygian mean uses
  the printed values).
- `oar_inertia.py` spike formula: F_spike = I·ω/(t_rise·lin). At the 28.8-spm
  drive (ω = 1.95 rad/s), t_rise 0.15 s: **spruce ≈ 116 N, old-zygian ≈ 215 N,
  old-thranite ≈ 156 N** — 52–96 % of the 224 N mean handle force; the
  zygian/spruce ratio 1.85× is the "old fir ≈ 2× spruce handiness" (plan §6
  Level-1 acceptance).
- Flip energy per stroke ½·I·ω² → the extra metabolic cost of flipping the
  heavy oars: spruce ≈ 9 W/man, old-zygian ≈ 16 W/man at 28.8 spm (≈ 7 W/man
  handiness penalty) — the W′ tank must pay it.
- Couple cross-check (Table 3.2) stands at 0.6 % — the mean handle force must
  survive the layer.

### 13.2 Implementation design — two options

**Option B — hybrid (recommended for the LL):** keep the validated prescribed
kinematics, add smooth catch/finish transitions (finite t_rise) and the
inertia torque term in Fh. The spike emerges from θ-ddot at the catch; the net
inertia work over a cycle ≈ 0 (energy-conserving). The means stay within the
Gate-1 tolerance of the rigid model — the layer is a labelled refinement, not
a re-anchoring. The rise transitions must preserve the swept angle (the
constant-ω mid-drive shortens by the rise times).

**Option A — force-driven (companion validation):** solve the torque-balance
ODE I·θ-ddot = τ_rower(t) − τ_blade(θ, ω) with the physiology's demand force
profile; the emerging drive time must land near Table 9.6 — validating that
the measured kinematics are consistent with the rower forces + inertia. A
companion script, not the LL's production path.

### 13.3 The layer in the LL

- `ll/oar.py`: `mit` parameter; rise-time transitions (t_rise 0.10–0.20 s
  band, 0.15 s nominal — source flag, §13.5); Fh = (Fn·l_cp + I·θ-ddot)/lin;
  `simulate()` gains an inertial variant.
- `common/chain.py`: load the Table 3.1 CSV (shared asset — the oar families
  and their tier labels: old-zygian → zygian tier, old-thranite → thranite).
- `ll/ship.py` / `rower.py`: the fleet = per-family assignment (v1 scenarios:
  all-spruce = the 1994 setup; old-fir mixed = the 1990 setup); the force
  ceiling applies to the **total** instantaneous Fh (blade + spike — separate
  instants: catch spike vs mid-drive blade peak); the W′ drain includes the
  flip energy ½·I·ω²·r/60 per man.

### 13.4 Validation gates — **all passing (7 checks, `ll/tests/test_gate5.py`)**

- G5-1 ✓ spikes reproduce `oar_inertia.py` (116 / 215 / 156 N at t_rise
  0.15 s, 28.8 spm — the Table-1.092-m reference) within 2 %; the physical
  full-reversal values (ω_rec + ω_drive) reported: 146 / 270 / 197 N.
- G5-2 ✓ handiness: zygian/spruce spike 1.85× (the §6 Level-1 acceptance).
- G5-3 ✓ hull observables unchanged with the layer ON (< 1 % at the four
  Table 9.6 points) — the inertia is internal to the rower-oar system.
- G5-4 ✓ momentum closure: net pulse impulse ≈ 0 per cycle; the flip energy
  (½·I·ω_drive²·r/60) is accounted exactly in the W′ basis — the pulses are
  impulse-equivalent, not energy-shape-exact (rectangular, documented).
- G5-5 ✓ couple anchor: drive-mean Fh at the anchored point 224 N ± 3 %.
- G5-6 ✓ ceiling: total peak Fh ≤ Fh_max through a 30-s burst, both fleets
  (the spike and the blade peak are sequential, not summed).
- G5-7 ✓ companion (Option A): the force-driven ODE with the chain's mean
  pull reproduces the Table 9.6 drive time — 0.43 s vs 0.43 s, essentially
  exact: the prescribed kinematics are consistent with forces + inertia.
- G5-8 ✓ regression: 19 + 7 + 12 + 9 + 8 checks green with the layer on;
  fleet = None restores the massless behaviour.

Design notes: the fleet's per-side MIT is the tier-weighted mean (spruce
9.7 kg·m²; old-fir (31·13.1 + 27·18.0 + 27·13.1)/85 = 14.7); the flip pulses
sit outside the effective pull (the catch flip in the air — blade out), so
the drive and its means are untouched by construction.

### 13.5 Open items

- t_rise source: 0.10–0.20 s band is the plausible water-entry / flip time
  (the 1994 trials describe the hands "coming up hard at the end of the
  recovery" — line 3262 of the txt dump); no measured value — `[?]`
  (register D10). 0.15 s nominal in use.
- Fleet assignment: the 1994 trials' tier→oar mapping (spruce new-builds vs
  the old-fir oars' tier labels in Table 3.1) — check the ch.4/ch.3 text.
- Recovery-phase inertia (the swing reversal costs the rower work both ways;
  the finish braking is eccentric — cheaper): v1 counts the concentric flip
  energy, notes the eccentric part.
- The A/B anomaly stays recorded-as-printed (the zygian family inherits it).

## 14. Mismatch-closure roadmap (VALIDATION.md §7) — status

| # | Mismatch | Path | Status |
| --- | --- | --- | --- |
| 1 | Tightest-turn 360°-time (73 vs 128 s) | **done** (15.3): two-lever decomposition + hold fraction 0.05 + the sprint protocol + the sway DOF — the physical CLR restoring moment + the C3 lever (4.8 → 1.8 m) + the ship's effective Ω 3.2e6 (C1 reconciled): D = 67.8 m ✓, the speed halves ✓, t_360 = 98 s vs 128 — the ~23 % residual is the turn's build-up (the trial's entry vs the instant hard-over), documented | [x] — residual documented as the build-up |
| 2 | Sprint t_drive data gap (A8) | **done**: t_drive(44.5) = 0.371 s calibrated to the trial speed (8.30 kt at 130 oars — IN the 8.2–8.4 band); wired into t_drive_for as a tagged entry; matches the bracket analysis's 0.375 estimate | [x] |
| 3 | 2-parameter CP tension (D7) | **done (no model change)**: the ¾-NM's 4–5-kt tailwind gives ~0.5–1.5 kW assistance (the ch.4 1.3–4.4 kW band is for a 10–15-kt wind) → true crew power 91–100 W/man → W′ = 5 kJ predicts 4–7.5 min; the observed 6.5 min sits inside the band. The 2-min rule and the 45-s sprint also check out | [x] |
| 4 | Mark IIb shortfall (oQ-18) | **resolved as an equivalence** (15.2): Shaw's form k·(q/p)²·V²·sin²C with the ACTUAL turning point (p = V·cosC/ω) reduces algebraically to the flat-plate law — the flat-plate law IS Shaw's force form (locked as a test). The geometric-deadpoint slip limit (ω = V·cosC/p(C)) gives less thrust than the measured Table 9.6 kinematics (negative at our points) — the prescribed (measured) kinematics are the truth. The shortfall is therefore the UNKNOWN Mark II blade area (register A5 — our RIGS uses the Olympias 0.078 m²; the ch.9 ×3.3 note is the design's requirement, i.e. the Mark II's actual blade area ~0.26 m²). Closure: the A5 data (Coates plans) or the 'Mark IIb as designed' scenario at 0.26 m² | [x] resolved — A5 data gap named |
| 5 | Per-tier factors (v2) | **done** (Gate 6, 4 checks): SideCrew = 3 TierCrews (31/27/27, per-tier MIT + W′); the thalmian head-room as the ch.9 L-model power factor (0.9 cruise → 0.6 sprint, shape [?]) + the feather clamp; the thalmian share falls with rate (0.34 → 0.30) and the 170-oar sprint overshoot closes (8.54 → ~7.9 kt) | [x] |
| 6 | Archival (F/G raw data, Plan 8 stations, trials video) | Wolfson archive / Oxbow / Actium team; t_rise from film | background |

## 15. Closure work plan for the remaining mismatches

Sequenced by dependency: per-tier crews first (self-contained, may close the
170-oar overshoot), then the turning-point blade law (its forces feed the
sway work), then the sway DOF (its acceptance is the Ω reconciliation). The
archival trio is background. An item closes when its gates pass AND its
VALIDATION.md ledger row moves from [!] to [x] with the residual documented.

### 15.1 #5 — per-tier crews (**done**, Gate 6, 4 checks)

- SideCrew = three TierCrews (31/27/27 per side; per-tier MIT and W′
  tanks; the ship's per-oar-average API unchanged).
- Thalmian head-room as the **ch.9 L-model power factor** (a reduced pull
  scales the POWER, not the kinematics — a kinematic sweep cut dragged the
  tier into the deadspot and broke the cruise anchors; the L-model + the
  **feather clamp** (the deadspot slips the blade — "ineffective", not
  drag) reproduce the trial character). Factor 0.9 at cruise (720/800 mm
  manikin ratio), linear to 0.6 at 44.5 spm — shape flagged `[?]`.
- Findings: the thalmian share falls 0.34 → 0.30 from cruise to sprint
  (time-averaged — the W′-boundary surging averages out); the 170-oar
  sprint overshoot closes: bare-oar 8.54 → ~7.9 kt burst (below the trial
  band's top — the 130-effective + ineffective-thalmian reality now both
  represented).
- The W′ P_crit availability scales with the power factor (a reduced tier
  sustains factor × P_crit) — without it the tier oscillates at the W′
  boundary.

### 15.2 #4 — the turning-point blade law (**resolved as an equivalence**)

1. **Appendix decoded**: the d-formula is correct as printed (A = the catch
   angle: 0.477 at catch/finish, 0.953 at mid ✓ — the earlier 'cos vs
   sin+30°' flag was a convention error, resolved); p = L_plan − d.
2. **The unification**: k·(q/p)²·V²·sin²C with the ACTUAL turning point
   (p = V·cosC/ω, q = l_cp − p) reduces algebraically to the flat-plate law
   k·v_n² — **the flat-plate law IS Shaw's force form** (numeric identity
   locked as a research-chain test). The geometric-deadpoint slip limit
   (ω = V·cosC/p(C), p = L_plan − d) gives less thrust than the measured
   Table 9.6 kinematics — negative at all four points (the crews sweep
   ~30 % faster than the deadpoint-stationary speed): the prescribed
   (measured) kinematics are the truth, the slip limit is a lower bound
   (locked as a test).
3. **The Mark IIb conclusion**: the shortfall is NOT a law error — it is
   the UNKNOWN Mark II blade area (register A5: our RIGS uses the Olympias
   0.078 m² for the Mark IIb; the ch.9 ×3.3 note is the design requirement
   ≈ 0.26 m² of actual Mark II blade). Closure: the A5 data (Coates
   plans / archival) or the documented 'Mark IIb as designed' scenario.
4. No BLADE_LAW flag needed — the flat-plate law is confirmed; the prop-
   fraction gate stays locked (the 0.078-area Mark IIb is 'Olympias blades
   on a Mark II rig', a scenario, not a model error).

### 15.3 #1 — the sway DOF (**done**, Gate 8, 5 checks) — the LL is complete

- The hull is now surge + sway + yaw: the per-oar Fy sums into the sway
  (the crew returns it), the rudder's lateral force enters, and the hull's
  lateral resistance (ρ·A_lat·|u|·v, A_lat = 35 m²) acts at the CLR
  (x_clr = 0.8 m forward of the CG) producing the physical restoring
  moment the lumped Ω·ω² cannot represent. The ship-frame dynamics with
  the centripetal couplings.
- The calibration (calibrate_sway.py) revealed the reconciliation:
  with the sway explicit, the fitted 4.8 m lever double-counted the
  lateral dynamics — the lever drops to the physical athwartships arm
  (1.8 m, the C3 decomposition completed) and the ship's effective Ω
  becomes 3.2e6 (the vessel's 5e6 stays for the steady research model —
  C1 reconciled).
- Acceptance: the diameters held (G1 89.7 / F1 117.4 / tightest 67.8 m,
  all in their bands) AND the sprint-protocol t_360 = 98 s vs the trial's
  128 — the ~23 % residual is the turn's build-up (the trial's entry vs
  the instant hard-over), documented, not parameter-fittable within the
  physical ranges.
- The drift emerges: −2.2° mid-turn (between the Taylor balance's 1.4°
  and the reported 15°); the lateral velocity damps (no divergent
  instability); the trim shows the physical per-stroke Fy kick a real
  helmsman would trim (gate-3 trim updated to the physical band).
- 88 tests green — the LL's physics is complete.

### 15.4 Archival items (background, anytime — **no email outreach**)

- The print-only F/G report: Oxbow out-of-print copies, the U. Crete
  catalogue record, the Actium/CNRS team — only if they surface without an
  email campaign.
- The 1990 trials video → t_rise from film (the catch-flip time), if the
  footage surfaces in our own sources.
- Acceptance: the per-turn F/G data (per-angle rudder drag factors), the
  station plan (sway moments, C3 closure), a measured t_rise.

### 15.5 Sequence

1. #5 per-tier crews — self-contained quick win.
2. #4 blade law — its forces feed #1's sway.
3. #1 sway DOF — the Ω reconciliation is its acceptance.
4. Archival — background; the emails first.

## 16. Cant + slip-assumption fixes for the Mark IIb (plan)

The Mark IIb shortfall (oQ-18) is the aggregate of missing physics at its
points, expressed as the ×3.3 area-equivalent (register A5). Two named
mechanisms to incorporate into the LL code.

### 16.1 The cant term — **implemented** (Gate 7, 4 checks; commit …)

RIGS gained `cant` (0.0 / 18.4); the blade law and the rigid reference
use vn = V·cosC·cos(φ) − l_cp·ω with the thrust carrying cosφ (identity at
φ = 0 by construction). The Mark IIb prop fraction rose ~0.30 → **0.51–0.54**
(~1.7× — the deadspot shallows). The OQ18 lock, the research-chain band
and the Gate-1 band all moved TOGETHER with the docs.

The Mark IIb rig is canted 18.4° (tan = 1/3): the oar's sweep plane is tilted
about the athwartships axis, so the blade-face normal is not horizontal. The
flat-plate law gains a geometry term:

    vn = V·cosC·cos(φ) − l_cp·ω        (φ = cant angle; 0 for Olympias)
    Fx = −Fn·cosC·cos(φ)               (the thrust component of the normal)

- The rig dicts gain `cant_deg`: 0.0 (Olympias), 18.4 (Mark IIb) — the
  bladeless change: φ = 0 ⇒ cosφ = 1 ⇒ the Olympias law is IDENTICAL (the
  validated anchors are untouched by construction — a strong property).
- At the Mark IIb's deep deadspot (vn ≈ −0.53 at mid, 9.7 kt): the flow
  reduction deepens vn to ≈ −0.76 → force ×~2 (the deadspot shallows — the
  blade outruns the water more easily). Expected: the prop fraction
  ~30 % → ~55–65 %.
- The handle force lever (l_cp/lin) and the Fy unchanged in v1; the vertical
  force component Fz = Fn·sinφ (a small heel moment) is v2.

### 16.2 The slip-assumption analysis — **implemented** (the scenario knob)

The slip-factor is a rig key (default 1.0 — identity); the sensitivity
(G7-3): prop fraction 0.51 → 0.85 at f = 1.3 (monotonic, ~f²). The
**"Mark IIb as designed" scenario** (G7-4): cant + area 1.3× (the A5
estimate) + slip 1.2 → the equilibrium at 46.3 spm lands on the chain's
9.7 kt — every factor labelled, the slip ~1.2 is the aggregate of the
unmodelled taper and attack-angle dynamics, NOT a blade dimension.

The model's slip = vn from the prescribed (measured) ω — proven right at the
Olympias points (15.2). The Mark IIb's residual after the cant is exactly
the ch.9 caveat zone ("if he has assumed too little slip on the blades…").
Tools:

- A **slip-sensitivity diagnostic**: thrust vs a slip-factor f
  (Fn = k·|vn·f|·(vn·f), f = 1.0 at Olympias — the validated anchor; the
  Mark IIb's residual → the required f). This quantifies how much data would
  pin the slip, without adopting a value.
- A **documented scenario knob**: the "Mark IIb as designed" scenario =
  cant (16.1) + a modest area increase (A5 estimate 1.2–1.5×, NOT 3.3×) +
  the residual slip-factor f ≈ 1.1–1.2 — every factor labelled, none
  silent. The knob is Mark-IIb-scenario-scoped, never a global retune.

### 16.3 The payoff: a usable Mark IIb for the tactical layer

The manoeuvre model's anastrophes run at 9.7 kt (the Mark IIb) — the LL's
Mark IIb needs a consistent thrust to be usable there. The scenario's
acceptance: the equilibrium at 46.3 spm lands near the chain's 9.7 kt
(Table 9.7) — then the turn gates at the Mark IIb points open up.

### 16.4 Validation gates — **all passing (4 checks, `ll/tests/test_gate7.py`) + regression**

- G7-1 ✓ the cant's measured effect: 0.51 with vs 0.30 without (ratio
  1.7×, asserted); the identity at φ = 0 (< 1e-9 — the Olympias anchors
  untouched by construction).
- G7-2 ✓ (folded into the research-chain + Gate-1 bands, moved together
  with the OQ18 doc): the Mark IIb prop fraction now 0.51–0.54, locked.
- G7-3 ✓ the slip sensitivity: 0.51 → 0.85 at f = 1.3 (monotonic ~f²,
  diagnostic only).
- G7-4 ✓ the as-designed scenario: cant + area 1.3× + slip 1.2 → the
  equilibrium at 46.3 spm lands on the chain's 9.7 kt.
- G7-5 ✓ regression: 79 + 4 = 83 tests.

### 16.5 Sequence and dependencies

1. 16.1 the cant term (a day — the law change + the re-locks).
2. 16.2 the sensitivity + the scenario knob (the diagnostics + docs).
3. **Before 15.3 (the sway DOF)**: the cant changes the blade forces the
   sway consumes — land 16.1 first.
4. The A5 data (Coates plans, archival) would pin the real area and shrink
   the slip-factor to zero — the background path.

## 17. The turn build-up — **investigated, ruled out, reverted**

Implemented the build-up (the helm as a human action: tau_rud lag + the
helmsman's strength clamp; the held blades' brake ramp tau_hold) and
measured its contribution: **~2 s of the ~28 s discrepancy** (98 → 100 s)
— negligible, the ramps overlap the W' fade which dominates the timing.

**Conclusion**: the build-up is NOT the cause of the t_360 discrepancy
(100 vs the trial's 128 s). The code was reverted (no complexity for a
ruled-out mechanism); the timings would be physical to include later, but
only if a discrepancy worth their magnitude appears.

**The t_360 residual is an OPEN discrepancy with no known cause.** The
candidates examined and their status: the hold fraction (calibrated, two-
anchor), the W' fade (in), the sway/CLR physics (in), the turn build-up
(implemented, tested, ruled out). A linear yaw-damping form (register C1's
units hint — the printed 'kg m²' fits a linear coefficient) is an untested
hypothesis, not a cause.

## Next actions

- [x] Freeze the **verb set** (§3.2: 4 crew verbs). oQ-1, 2, 5, 6, 7 resolved; only
      oQ-4 remains for the schema round.
- [x] Freeze `commands/schema.json` v0.1 + parser + sample script (`trireme-sim/`;
      parser: 19 checks passing, fail-fast + deterministic).
- [x] **Phase 1 Gate 1 — LL one-oar skeleton** (`trireme-sim/ll/`): time-stepped oar
      with the flat-blade law; reproduces the rigid model at all four Table 9.6
      points (<0.5 %), mean handle force 224/208 N in the cruise family,
      prop W/man 102 % at 7.2 kt, dt-converged, oQ-18 shortfall inherited
      honestly (7 checks).
- [x] **Phase 1 Gate 2 — hull surge** (`ll/hull.py`, 12 checks): per-step
      coupling settles on the hull=1.0 anchors — 7.22 kt @ 28.8 spm,
      7.98 kt @ 36 spm; sprint (130 oars, 44.5 spm) brackets the 8.2–8.4 kt
      trial over the unmeasured t_drive range (data gap — uncertainties
      register A8). oQ-18 answered empirically for the Olympias rig: the
      flat-plate 0.078 m2 law suffices there (Mark IIb shortfall stands).
      Stroke surge ripple ≈ 0.2 kt; start-from-rest deferred to the oQ-13
      force ceiling (crude provisional clamp exists for demos).
- [x] **Phase 1 Gate 3 — 170-oar surge+yaw ship** (`ll/ship.py`, `rig.py`, 9
      checks): time-domain turns reproduce the W5 anchors within 5 % (G1
      93.5 m vs 89.4; F1 117.2 vs 111.9; tightest 64.4 vs 62). oQ-4 gets its
      first quantitative answer: hold-water = trailing + a 2 % brake
      fraction calibrated to the tightest-turn diameter (the speed history
      still needs the trial's rate + the hold spectrum). Oar yaw uses
      Taylor's fitted lever 4.8 m (decomposition open — register C3);
      back-water = force-limited 80 % astern (manoeuvre 5.x). Sample script
      runs end-to-end: first command-language → LL pipeline.
- [x] **Phase 1 Gate 4 — rower physiology layer** (plan §12, 8 checks):
      `ll/rower.py` — Fh_max 700 N, P_crit 80 W/man (R&W ch.23, primary),
      W′ 10 kJ (provisional), per-side stroke adaptation (demand-limited
      drive, sweep shortening, tempo loss with weakest-side-governs),
      commanded-vs-achieved telemetry. Findings: steady = sustainable
      envelope; spoude = W′-limited burst (~90 s); rest start = short
      stretched strokes, launch slower than the bulk law; backing
      degenerates to a hold-brake at speed; exhausted-side yaw; tightest
      turn halves speed after the burst; rate 50 + exhausted = tempo lost.
      Research subtasks now: ch.9 sprint durations → W′; S6 force-curve
      source → Fh_max; τ (plan §12.6).
- [ ] Sketch the HL tolerance/labels format (§4 / §6 annotations).
