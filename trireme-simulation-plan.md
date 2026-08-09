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

Status: **first draft.** Every section is a proposal for the next discussion round; open
questions are numbered oQ-1…oQ-21 in §10 and flagged inline. Nothing here is accepted
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
- Complete enough for real operational phases: cruise, sprint, turn, land, anchor, rest,
  emergency.
- Composable: a rhythm (cadence) layer, an oar-state layer (global or per side), and a
  helm layer (rudder only, oars only, or both).
- Typed arguments (number, enumeration, side, bearing) with sensible defaults: "just
  sprint" must not require a form.
- A human, a script, and later an AI, all speak the same vocabulary.

### 3.2 Proposed vocabulary (v1) — to be argued down or up

Each command has: (a) the commander's intent; (b) a nominal expansion into physical
directives; (c) the expected consequence both simulators must satisfy (equivalence
contract §6).

| verb | arguments | intent | physical expansion | flags |
| --- | --- | --- | --- | --- |
| `rate` | spm (0–50) | set the stroke cadence | per rower: cadence, cycle = 60/spm, phase offsets | rhythm/pipe-drum analogue |
| `pressure` | 0–1, or named (resting/steady/fast/sprint) | work per stroke | scale the mean handle-force profile, P = 7.43·r·pressure | vs `speed` autopilot: oQ-2 |
| `speed` | knots target | captain's intent ("make good X kt") | guidance derives rate + pressure | oQ-2 decides if it exists |
| `oars` | rowing / banked / holding / backing / trailing / feathered | blade-water state | per-oar blade pose & hydro regime | hold-water & back-water are the hard cases; LL behaviour is the validation target |
| `oars` side/level | e.g. bank starboard; thranites rest | asymmetric or tier-specific states | per-bank oar state | feeds turn-by-oars |
| `rudder` | left/right, angle 0–22° | helm order | rudder force (F/G validated) | also "no rudder — oars only" |
| `oar-assist` | on/off, side | combine oars with rudder for steering | uneven port/starboard stroke shaping | how anastrophe is expressed (oQ-3) |
| `course` | bearing or waypoint | navigation goal | same guidance loop in both | helmsman's layer? (oQ-6) |
| `sea` | state (height, length) or look up Shaw tables | environment | wave drag; per-blade water speeds | shared environment entity (oQ-5) |
| `crew` | effective fraction / watch plan | crew condition ceiling | HL: aggregate; LL: per-rower | semantics to freeze (oQ-15) |
| `rest` | full or rest a half-bank | way off the oars | feathered blades up, no work | |
| `anchor` | location | approach and stop | hold + back sequence | |
| `go` / `stop` | — | master start / stop, sync | global phase reset; "ready … pull" | |
| `report` | — | status: speed, rate, position, ETA, force envelope | both output a summary | the commander console |

### 3.3 Rhythm and cadence

- `rate` is a cadence imposed on all rowers: cycle period, drive/recovery split (Table
  9.6 effective-pull times ≈ 33–45 % of the cycle), and a phase clock for synchronisation
  and cueing (pipe/drum analogue).
- The LL consumes the cadence as a schedule; the HL treats it as a scalar indexing
  response curves.
- oQ-12: also expose stroke *shape* (long/medium/short)? Real range: up to 1.1 m
  unrestricted, ~0.99 m effective (canted), 0.87 m (straight rig). A `stroke-length`
  command in v2 would parameterise blade immersion time and pull length.

### 3.4 Manoeuvring by oars

- The LL must support **turn on the oars**: one bank rows, the other banks/holds →
  asymmetrical thrust → yaw; "hold water" on one side to brake-turn; the attestable
  *anastrophe* family (oQ-3).
- The mapping from one commander order to per-bank steps is a design target and a prime
  validation case against the F/G-turn records.

## 4. High-level simulator — the fast and efficient one

- **State**: position, heading, speed, effective rate, course, crew condition, environment,
  position in the command sequence.
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
  2. blade state from `oars` → hydro regime (driving / stopped / backing / out of water);
  3. blade force from the flat-plate model: Fn = 0.5·ρ·A·C_N·|v_n|·v_n at the blade
     centre of pressure (0.26 m from tip), including the phase where the blade would
     otherwise outrun the ship (drag, not thrust — the "deadspot" regime);
  4. handle force: F_handle·l_in = F_blade·l_cp + I_thole·θ-ddot (inertia live from
     Table 3.1 per oar; the catch-flip spike from `oar_inertia.py`);
  5. rower output: mean-force × stroke-shape profile, capped by crew state and VO2;
  6. sum all 170 oar forces and moments onto the hull (per-side sums → yaw);
  7. hull update: surge/sway/yaw, resistance, rudder, waves at each blade.
- **Per-tier heterogeneity**: thranite/zygian/thalamite stroke limits (e.g., thalmian
  head-room limit ≈ 720 mm vs 800 mm design), oar-inertia families (spruce vs old firs —
  handiness), per-oar fatigue.
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
- time to 3 NM within 1 %;
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
  ui/             # commander console — thin CLI now, richer later
```

- Determinism: fixed dt, fixed ordering, seeded RNG; state is a plain record for
  snapshots. Runs log the command stream and per-entity telemetry.

## 8. Roadmap (draft)

0. **Phase 0 — command language & contract.** Freeze the verbs (§3.2), write the schema,
   fix the equivalence targets (oQ-1, 2, 4, 5, 7 here). Deliverable: `schema.json` v0.1.
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
- **HL "good-enough" set**: the HL e-approx must not drift silently over long scripts;
  the equivalence table is checked on every calibration.

## 10. Open questions (first pass, oQ-1…oQ-21)

**Command language**

- oQ-1 — How granular must the vocabulary be? Start at 14 verbs (§3.2); 8-verb minimum?
- oQ-2 — Who controls power: commander gives `rate` (drum style) or `speed` (autopilot),
  and who converts? Does `speed` exist in v1 at all?
- oQ-3 — Attested-ancient mapping: which commands map to attested signals (*keleustēs*
  signals, "bend to the oars", "hold water", "back water", *anastrophe*)? Deliverable:
  the mapping table; a "historic mode" accepts attested phrases as aliases.
- oQ-4 — Oar-state semantics: is "hold water" one hydro state or a spectrum (flat,
  crossed, partly)? The per-oar specs the LL must implement.
- oQ-5 — Is the environment a command or an injected input? Both must use the shared
  sea entity.
- oQ-6 — Who is "the commander"? Trierarch alone, or + helmsman + keleutes (roles with
  different permissions)? Affects which verb belongs in the commander console.
- oQ-7 — Is a named attack order needed ("ram that ship" -> final burst) or are
  rate + pressure + course sufficient?
- oQ-8 — Half-ships / watch changes: attested [7]? How to model a half-bank that rests
  mid-trip? [?]

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
- oQ-15 — Freeze displacement/mass baseline and `crew` semantics (fraction vs schedule).
- oQ-16 — Where does the environment state live? (recommend a shared `common/` environment entity)
  — one entity for both sims.
- oQ-17 — Role model detail: trierarch-permission split for the console; what the
  keleustes can order vs the helmsman.
- oQ-18 — Sprint-regime honesty: flat-plate with 0.078 m² under-estimates pressure at
  8.3 kt (Mark IIb needs ×3.3 area per ch.9 note) — tune above the documented band,
  or stay strict and journal.
- oQ-19 — LL budget: run length and dt targets, wall-clock budget, tier-symmetry plan.
- oQ-20 — UI/console priority: headless → thin CLI → web/API; what is the commander
  console for each?

**The pair**

- oQ-21 — How fast does HL need to be relative to LL, and how tight should its LL error
  band be before "sanity checks" stop being meaningful? (e.g. 0.5 % vs 5 % per row;
  the answer drives Phase 2/HL approximating architecture.)

## 11. Definitions of key terms

- **cadence** — the rhythmic schedule for all rowers: rate (spm) fixes cycle period,
  drive and recovery time; carries phase synchronisation.
- **pressure** — multiplier on the mean pull relative to the nominal schedule
  P = 7.43·r·pressure.
- **oar state** — `rowing`, `banked` (out of water), `holding` (stopped in water),
  `backing` (driven the other way), `trailing` (feathered, loose), `feather` (flat on
  the recovery — meaningful for the trireme's near-flat blades).
- **anastrophe** — the ordered, quick-reversal turn; in commands it is a combination
  (one bank holding / banked), not a primitive.
- **oracle** (in this plan) — the simulator that other things are judged against: the
  LL is the oracle vs reality; the HL is judged against the LL.

## Next actions for the next session

1. Argue the **command list** (§3.2) and the blocking questions oQ-1, oQ-2, oQ-4, oQ-5,
   oQ-7.
2. Freeze `commands/schema.json` v0.1.
3. Stand the **“LL first”** skeleton: `ll/` per-oar loop with the flat-blade law running
   a fixed 30-spm line, compared to the rigid-model numbers — before any HL work.
4. Sketch the HL tolerance/labels format (§4 / §6 annotations).
