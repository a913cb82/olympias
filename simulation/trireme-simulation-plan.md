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

Status: **all three phases complete.** The LL is the validated oracle
(VALIDATION.md §1–§8, the honest mismatch ledger §7); the HL is the
machine-calibrated fast ship (§18–§19); the pair harness produces the
Level-2 equivalence tables (VALIDATION.md §9) with the annotated run in
`harness/equivalence-annotated.md`. The current state — what is
validated, what is open with a named cause and a lock — lives in
VALIDATION.md §10–§11. Open questions are numbered oQ-1…oQ-21 in §10 and
flagged inline; research gaps are tracked in §9. Nothing here is accepted
research until it has a source citation or a validated run.

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
(`hl/calibrate.py` — the machine calibration run, §19); when the LL gains
fidelity, the curves are refreshed and the tolerance annotations updated. The
HL is never hand-tuned to old self-numbers; it is re-fitted to the LL's new
truth.

## 7. Architecture sketch (python, matching the repo)

```
simulation/
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
   script. **DONE** (Step 0; 19 parser checks).
1. **Phase 1 — LL first.** Get the per-oar sandbox working and validated against ch.9
   tables (blade forces, drive times, hand-rule). This is the truth engine; best to own
   it before the HL extrapolates from it. **DONE** (Gates 1–8; 88 tests; the LL is
   the oracle).
2. **Phase 2 — HL from LL.** Build the fast ship-level integrator, but generate its
   response curves **from the LL**, not from hand-entered numbers; ships first
   consistency gates vs ch.7 cruise and ch.9 sprint. **DONE** — the fast ship with the machine-measured curves (§19); the Level-2 equivalence is the acceptance record (VALIDATION §9).
3. **Phase 3 — the pair harness.** Run the same scripts on both; produce the first
   equivalence table; fix the biggest violations; document where HL must stay loose.
   **DONE** — the harness runs the script set + the turn scenarios and prints the equivalence tables (VALIDATION §9); the annotated run: `harness/equivalence-annotated.md`.
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
| **Ergonomics digits** — ANSUR 1988 50th-percentile values; Greek mean height ≈ 1.70 m | Phase 4 / oQ-13 (reach, stroke length) | flagged [?] in `research/lane-4-oars/oar-data.md` §6 | focused primary-table read (DTIC ADA225094) |
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


## 12. The LL's layers — what the phases left behind

The LL is complete and is the oracle. The layer designs below were
implemented and gate-validated in Phase 1; the gate records (anchors,
checks, the honest ledger) live in VALIDATION.md §1–§7, and the design
detail lives in the code (`ll/rower.py`, `ll/blade.py`, `ll/ship.py`).

- **Gate 4 — the rower physiology layer** (oQ-13): the physiological
  rower — peak-force ceiling, endurance/fatigue, the W′ burst tank
  (8 checks, `ll/tests/test_gate4.py`).
- **Gate 5 — the oar-inertia layer**: Table 3.1 inertias drive the
  catch-flip dynamics (7 checks, `ll/tests/test_gate5.py`); the A/B MIT
  anomaly stays recorded-as-printed.
- **Gate 6 — per-tier crews** (4 checks).
- **Gate 7 — the cant term** for the Mark IIb geometry (4 checks).
- **Gate 8 — the sway DOF**: the coupled sway/yaw drift state that the
  wprime closure and the turn physics rest on (5 checks).

## 13. Two investigated-and-reverted hypotheses

The turn build-up (§17 below was investigated, ruled out and reverted)
and the yaw-induced oar/water differential were both tested against the
turn anchors and rejected — the verdicts are in VALIDATION.md §7.2 with
the numbers; the terms stayed OFF (0.0) in `ll/ship.py`.

## 14. The mismatch-closure roadmap — all landed

Every planned closure of the LL's mismatch ledger (VALIDATION.md §7)
landed: the per-tier crews (Gate 6), the turning-point blade law
(resolved as an equivalence — the (q/p)² law is an algebraic identity
with the flat-plate law at the actual turning point, `ll/blade.py`),
and the sway DOF (Gate 8). The Mark IIb blade-area gap (×3.3) is a
research-side finding, not a blade-law error (oQ-18, resolved-as-physics
in `chain.py`).

## 15. The LL is the oracle

No further LL changes are planned outside measured mechanisms: the
Level-1 open items (t_360, the drift angle, the ch.7 triple — the
open-with-locked-test rows, VALIDATION.md §11.2) each have a named
cause and a locking test, and each would enter through a re-measurement,
never a tuning pass.

## 16. The turn build-up — investigated, ruled out, reverted

The yaw build-up hypothesis (the slow 3–5 s ω rise into the turns) was
tested against the G1/F1 anchors and rejected — see VALIDATION.md §7.2
and the yaw-build term the HL uses (the two-timescale approach, §19).

## 17. The yaw-induced oar/water differential — investigated, ruled out, reverted

Same verdict as §16: the per-stroke yaw differential does not close the
t_360 row and breaks the diameters; the terms are OFF with the negative
result in the code's docstrings.

## 18. Phase 2 — the HL (the fast ship-level integrator)

**Complete** — `hl/ship.py` (the whole simulator), `hl/curves.py` (the
Calibration + the calibration-file loader), `hl/calibrate.py` (the
machine calibration run, §19), `hl/run_hl.py`. The HL is a
curve-chasing ship, deliberately minimal (plan §2.1: complexity only
when a gate proves it necessary): every response curve is machine-
measured from LL runs, never hand-entered, and every HL output carries
its tolerance label ("±X % of LL, calibration run #N").

**The response-curve set** (each generated by an LL protocol, refit by
`hl/calibrate.py`):

- cruise: rate → speed over the rowing range — the ch.7 triple
  (25.5 / 28.8 / 32.3 spm → 7 / 7.5 / 8 kt) plus the full LL curve
  between and beyond;
- sprint: rate 44.5 → the 8.2–8.4 kt band, plus the W′ burst envelope
  (spoude duration, speed-over-time, recovery);
- steering: helm → yaw rate / turn diameter per speed (the G1/F1
  protocols at the cruise speeds, the tightest-turn family), per
  helm-fraction and per pressure (the measured k falls with rate);
- pressure: the steady / rest / spoude envelopes — the P_crit-limited
  sustainable speeds, per-side pressure as the steering tool;
- fatigue: man-hours → power-ceiling decay for long runs;
- the drift cells (the pressure-dependent untrimmed yaw slope), the
  turn-drag curve, the asym nets (the one-side-stopped legs drain ≈ 0),
  the two-timescale yaw-build (the sway-coupled slow mode).

**Acceptance** (the Level-2 first tolerances, §6): |mean speed| < 1 %
over a 10-minute script including a sprint and a turn; settled rate
within 1 spm; G1/F1 turn diameter within 5 %; accumulated fatigue within
5 %; final position within ~0.1 NM after course changes. Performance
target: minutes of ship-time per second of wall-clock. Gates: a
`tests/test_hl_*.py` suite locking each curve against its LL calibration
run and the Level-2 tolerances.

## 19. The calibration protocol (`hl/calibrate.py`)

The calibration run regenerates the same table structure the bootstrap
fills, from LL protocols, and writes `hl/calibration/calib_<id>.json`
(+ `latest.json`, the ship's default): every table machine-measured with
its residuals, the protocols documented in the file's meta, the LL
commit recorded. The run (~4 min of LL protocols) is the loop's first
step: calibrate → `harness/run_validation.py` → adjust → repeat.

| Table | LL protocol (all exist today) | Notes |
| --- | --- | --- |
| V* spoude row | `ll.hull.equilibrium_speed` over the rate grid (8…50 spm, step 2) | the spoude+full-W' row == the bare commanded oar at cruise |
| steady / fast rows | LL ship 300-s settle at the pressure (1 Hz samples, tail mean) | the sustainable envelope; tail-mean — a single sample is biased by the surge ripple ±0.1 kt |
| empty row | LL ship, tiers' W preset 0, settle | the P_crit-limited level |
| hold / back rows | LL ship (row, hold / row, back), settle, at spoude and steady | the back collapses at ≤ 24 spm — measured separately |
| tank nets | LL W'-drain/refill slopes at the anchor levels (low preset, short window) | + = drain, − = refill; the refill cap taints a long window |
| D rudder | `ll/run_turn.py` at helm_frac {1/3, 1/2, 2/3, 1} | extends the interpolation midpoints |
| D oar | `ll/run_turn.py` oar-hold at helm_frac {0, 1/2, 1} | the tightest family midpoints |
| tau_surge | least-squares fit of the HL's V(t) to the LL rest-start (0…120 s) | one scalar; per-rate only if a gate fails |
| tau_turn | fit so the HL's |y| at 180 deg matches the LL's per family | the D gate is the judge; the yaw-build two-timescale (A, tf, ts) per family |
| spoude power | LL W'-drain runs over the rate grid | the tank's burst level |
| residuals | every table stores its max/mean |deviation| vs the raw LL points | → the tolerance labels |

**File schema** (`hl/calibration/calib_<id>.json`):

```json
{
  "id": "calib-<date>-<ll-commit>",
  "ll_commit": "...", "date": "...",
  "config": {"rig": "Olympias", "fleet": "spruce", "hull": 1.0, "n_oars": 170},
  "protocols": {"vstar": "ll.hull.equilibrium_speed", "d_rudder": "ll/run_turn.py ..."},
  "tables": {"vstar": {"rates": [...], "kt": [...]}, "steady": ..., "d_rudder": ...,
              "p_spoude": ...},
  "scalars": {"tau_surge": ..., "tau_turn": ..., "w_max": 5000, "p_crit": 80, "tau_w": 120},
  "residuals": {"vstar_max_pct": ..., "d_rudder_max_pct": ..., "tau_surge_rms": ...}
}
```

**Regeneration rule**: when the LL gains fidelity, `calibrate.py --regenerate`
re-measures and rewrites the file; the tests run against the pinned latest; no
hand-edited numbers. The residual annotations feed the "±X % of LL, calibration
run #N" labels every HL output carries.

**Explicit non-goals** (complexity only if a gate fails): no per-tier or per-side
crew machinery; no sway DOF; no force tables; no fitted constants beyond the
tables above; no changes to the LL. The triggers: 10-min mean > 1 % → per-rate
tau_surge; sprint envelope misses → one fitted drain factor; D > 5 % on any turn
→ tau_turn per family; fatigue > 5 % → a second W' tank (per side); position
> 0.1 NM → sway/drift terms.

## 20. Phase 3 — the pair harness

**Complete** — `harness/script.py` (one command stream, both simulators,
1 Hz telemetry), `harness/comparator.py` (the Level-2 metrics: the mean
is the distance/time integral — the sample-mean aliases the low-speed
per-stroke ripple; the fatigue gate is the consumption integral),
`harness/run_validation.py` (the script set + the turn scenarios →
equivalence tables + violations; the T5 bin gates), the script set in
`examples/` (incl. the T10 zig-zag out-of-sample). The acceptance record
is VALIDATION.md §9; the annotated script run with the per-row tolerance
sources: `harness/equivalence-annotated.md`.


## 21. The path to full validation — and how we know when it is reached

The coverage map (VALIDATION.md §10) is the master inventory: every
scenario, its status, and the path each row takes. This section is the work
plan for closing every closable row and the definition of done.

### 21.1 Definition of done (what "100 % validation" means)

- **Level 1 (real → LL)**: every anchor either passes its band, or sits on
  the open-items list with a named cause, a locking test and a path (the
  t_360; the no-anchor items). No unexplained or silent mismatches.
- **Level 2 (LL → HL)**: all six §6 gates pass on the defined script set +
  the five turn scenarios, against the pinned calibration file; the
  tolerance source is the calibration id on every output.
- **Evidence**: the coverage map has no failed / never-exercised /
  not-implemented cells in the in-scope rows; `harness/run_validation.py`
  prints no unannotated violations; the suite is green (the count lives in
  VALIDATION §8).

### 21.2 The task DAG — executed (2026-08-15)

The task graph for closing every closable row — tasks A–L (B settled-rate
gate, C drift-floor position gate, D 3-NM script, E back-tail τ, F turn
deceleration, G ch.7 triple check, H t_360 hypothesis test, I Mark IIb
blade layer, R1/R2 re-validations, J calibration, K acceptance run,
A annotated run, L the completion check) — was executed in full; every
task's verdict landed in VALIDATION §10/§11 (the acceptance run K19 on
`calib-2026-08-15-c243c01`). The open items that survived the DAG are the
open-with-locked-test rows of §21.1's Level-1 list.
### 21.3 Decision points (recorded here when taken)

- **The position gate** (coverage row 10.2.5): **decision taken 2026-08-15
  (task C)** — the bias-yaw: the measured drift is pressure-dependent
  (spoude −0.0010 vs steady −0.0003 rad/s, flat over rate), so the
  single-scalar floor (the original default) cannot represent it; the HL
  now carries the measured drift table (`curves.drift_bias`), matching
  the LL's untrimmed truth, and the gate stays as-written (0.1 NM). The
  residual (the table's interpolation vs the scripts' state mixes, the
  turn-phase interplay) lands in the net separation at K.
- **The interpolated midpoints** (coverage row 10.2.8): the gates are
  defined at the schema's anchor levels; the numeric-pressure and
  helm-fraction interpolations carry recorded residuals, not gates.
- **The scoped rows** (coverage row 10.2.9): waves/environment and
  oar-manoeuvres get their own gates when Phases 4/5 are built; per-side
  pressure steering, exhausted-side yaw, tempo loss, the Mark IIb rig, the
  old-fir fleet, reduced crews and rates < 8 spm re-open only via their
  named triggers (§18).

### 21.4 The completion check

The review-driven next-step plan (the ch.7 triple tension, the t_360 turn
drag, the drift angle, the knob audit, the gate-edge rows, the
strengthening gates a–f) is executed — the verdicts, the constants
ledger and the open items are recorded in VALIDATION §11, and the
coverage-map statuses there are authoritative. The completion check
below is the definition of done.

```bash
cd simulation
../.venv/bin/python3 -m pytest                    # green; count in VALIDATION §8
../.venv/bin/python3 harness/run_validation.py   # no unannotated violations
```

plus the coverage map (VALIDATION §10) showing only **validated** /
**open-with-locked-test** / **scoped** cells in the in-scope rows.
