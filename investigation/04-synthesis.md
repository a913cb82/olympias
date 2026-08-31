# Investigation 04 — Synthesis: How the Three Gaps Connect

## Summary of gaps

| # | Name | Trial | LL | Gap | Type |
|---|---|---|---|---|---|
| 1 | Turn time t_360 | 128 s | 95 s | −26% | Time — too fast |
| 2 | Drift angle β | 8–15° | 1.4° | 5–10× | Angle — too small |
| 3 | Cruise triple | 7.0/7.5/8.0 kt | 6.83/7.16/7.52 | −2.4/−4.5/−6.0% | Speed — too slow at high rate |

All three have been open since the earliest validation. All have had
multiple hypotheses tested and rejected. The honest-ledger approach
documents them rather than tuning them away.

## How they might connect

### Connection A: Drift ↔ Turn Time (H1, H4 from 01)

The drift and time gaps share the hull's lateral dynamics:

```
Drift β depends on: Fy_oars + f_rud vs f_hull(=ρA_latUv) + mUω
Turn time depends on: thrust vs drag(V) + yaw dynamics (Omega, Q)
```

If drift is too small, the model is missing drift-induced drag (H1a in 01:
D_drift ∝ sin²β). But at β=1.4°, D_drift is negligible — paradoxically,
fixing drift to 8–15° WOULD add measurable drag that could slow the turn.

Coupling chain:
1. Fix drift (e.g., heel-coupled lateral force or reduced A_lat) → β→8°
2. Drift-induced drag appears: D_extra ~ ½ρV²A_lat×sin²β ~ 3% at 8°
3. Plus rudder inflow correction (H1e): rudder sees oblique inflow → more drag
4. Turn's settled speed drops → t_360 lengthens toward 128 s

This is the most promising cross-gap fix: one physics change (drift) fixes
two gaps (drift + time).

### Connection B: Blade physics ↔ Cruise Triple (standalone H1–H4 from 03)

The cruise triple is an independent axis: it's about the STRAIGHT-AHEAD
blade model vs the chain's power law. It doesn't involve turning, sway, or
rudder. The likely causes are:

- Blade area correction (0.69 factor) may be too aggressive
- Chain uses Mark II L=0.99 vs LL's Olympias arc 0.80
- Rate-dependent efficiency or sweep effects

The triple gap does NOT connect to the other two except through the shared
blade model: if blade area is increased to fix the triple, turn thrust also
increases, potentially affecting the time gap (more thrust → faster turn →
worse time gap). So fixing the triple by increasing blade effectiveness
would WORSEN the time gap — a tension.

### Connection C: Rate dependence (03 ↔ 01)

Both the triple gap and the rate-sensitivity of t_360 (19.9 spm→112s,
44.5→95s) show rate-dependent physics. The rower's power chain rate
dependence (P=7.43r, L×r×E, t_drive interpolation) is common to both.

If t_drive interpolation is wrong at high rates (H3a in 03), it affects
both the cruise speed and the turn's rowing thrust → both gaps shift.

### Connection D: The stationary-turn second direction (01 §H3)

The LL turns too FAST at full crew (95 vs 128s) but too SLOW at partial
crew from rest (2.32 vs 3.5°/s, −34%). This brackets the yaw physics: the
model's yaw rate is too insensitive to crew count / speed. The two errors
suggest:

- At high speed + full crew: yaw moment too large (or damping too small)
- At low speed + partial crew: yaw moment too small (or damping too large)

A speed-dependent or crew-dependent correction could fix both — e.g., the
oar's yaw moment depends on blade immersion/angle which differs at low vs
high speed.

## Priority ranking of hypotheses

### Tier 1 — Most promising (test first)

| Hypothesis | Fixes | Effort | Risk |
|---|---|---|---|
| Heel-coupled lateral force (fixes drift → adds turn drag → fixes time) | Drift + Time | Medium | Low — heel already partially modelled |
| Drift-induced drag D(β) in turns | Time (if drift fixed) | Low | Low — simple addition |
| Match rig to chain for triple (use Olympias chain for Olympias rig) | Triple | Low | None — just a comparison fix |
| Blade area ×1.2–1.45 sweep | Triple | Low | Medium — re-grounds geometry |

### Tier 2 — Worth testing

| Hypothesis | Fixes | Effort | Risk |
|---|---|---|---|
| Rate-dependent sweep or t_drive | Triple | Low | Low |
| Degraded thrust in tight turns (oar angle/immersion) | Time | Medium | Medium |
| Rudder inflow correction at drift | Drift + Time | Low | Low |
| Clarke sway derivatives (Yv) for drift | Drift | Low | Low — just Yv |

### Tier 3 — Larger scope

| Hypothesis | Fixes | Effort | Risk |
|---|---|---|---|
| Full roll DOF (4-DOF hull) | Drift + Time | High | High — new dynamics |
| Nonlinear lateral resistance CY(β) | Drift | Medium | May worsen gap |
| Wave-making in turns | Time | Medium | Unmeasured |

## Concrete next steps

### Step 1: Quick experiments (no model change, ~1 day)

1. **Heel→drift estimate**: compute heel angle at G1/tightest from the
   BMT GM data; parameterize lateral force as F_heel = k×heel; sweep k
   to find what closes drift; check turn time impact.

2. **Direct drag measurement for t_360**: add a trial drag term
   D_extra = k×V² in the tightest scenario; find k that gives 128s;
   compare k to physical estimates (heel 5%, drift 3%, wave, etc.).

3. **Rig-matched triple**: run the triple with (a) Olympias chain
   (L=0.89, E=0.756) and (b) MarkIIb rig (55.6°, cant 18.4°) to see
   which closes the rate-dependent gap.

4. **Rate/thrust decomposition**: at each triple point, report every
   term in the power chain separately (handle power, blade eff, thrust,
   hull drag) to isolate which term carries the rate dependence.

### Step 2: Targeted model changes (~1 week each)

5. **Add drift-induced drag** to hull_advance: D_total = D(V) + D_drift(β)
   where D_drift = ½ρV²A_front×sin²β or D(V)×k×sin²β.

6. **Add heel-coupled sway force** to the lateral balance: Fy_heel =
   f(heel_angle) from hydrostatic heel data.

7. **Fix triple comparison** to use matching rig parameters.

### Step 3: Larger investigations (weeks)

8. **Cross-flow re-audit** with the real hull offsets: the current Omega
   3.00e6 uses C_D=0.252 from the rectangular-vs-tapered reconciliation.
   The real hull's J and A_lat are now grounded — re-derive Omega from
   first principles with the real hull's sectional drafts.

9. **Captive-model-test or CFD** for CY(β) at β=0–15° — the definitive
   measurement for the drift model.

10. **Braithwaite VBA transcription** (Stream D1) — the independent model's
    sway/yaw predictions for the same scenarios, as a cross-check.

## Decision tree

```
Is the triple gap just a chain mismatch (Olympias blade vs Mark II chain)?
├── YES (test Step 1.3 shows Mark II rig closes gap) → Fix comparison, close T1
└── NO (gap persists with matched rig) → Blade model rate dependence is real
    └── Is it area, timing, or efficiency?
        ├── Test blade area sweep (Step 1.3)
        ├── Test t_drive sensitivity
        └── Instrument power chain per term (Step 1.4)

Is the drift gap fixable within the 2-D sway model?
├── YES (heel or A_lat sweep gives 8° without breaking D gates) → Implement
└── NO (no 2-D fix holds D + wprime) → Need roll DOF or new lateral physics
    └── Does fixing drift also close t_360?
        ├── YES → Two gaps with one fix (best outcome)
        └── NO → t_360 needs its own drag mechanism

Is t_360's remaining gap (after drift fix if any) closable?
├── YES (extra drag of known magnitude matches a physical estimate) → Implement
└── NO (no physical drag of that magnitude exists) → Document as open
```
