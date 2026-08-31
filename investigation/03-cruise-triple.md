# Investigation 03 — Cruise Triple: −2.4 / −4.5 / −6.0% (−6.3% at hull 1.08)

## The gap

The ch.7 cruise triple (Rankov 2012 ch.7, Table 7.3) says:

| Speed | Rate (spm) | Chain says | LL gives (hull 1.08) | Gap |
|---|---|---|---|---|
| 7.0 kt | 25.5 | 7.0 kt | 6.83 kt | −2.4% |
| 7.5 kt | 28.8 | 7.5 kt | 7.16 kt | −4.5% |
| 8.0 kt | 32.3 | 8.0 kt | 7.52 kt | −6.0% |

The gap **grows with rate**: the LL's speed-vs-rate curve is flatter than
the chain's. At low rate the error is −2.4%; at high rate it's −6.0%.
The LL under-produces at high rates relative to Shaw's chain.

The inverse view (what rate does the LL need for each ref speed):

| Target | Chain rate | LL rate needed | Extra |
|---|---|---|---|
| 7.0 kt | 25.5 spm | 27.2 spm | +1.7 spm |
| 7.5 kt | 28.8 spm | 32.1 spm | +3.3 spm |
| 8.0 kt | 32.3 spm | 36.7 spm | +4.4 spm |

The chain law (Shaw ch.9):

    W_hull = 155V³ + 4.13V⁵          (Olympias, V in m/s, bare hull)
    W_hull × 1.08                     (Mark II hull — longer, more wetted area)
    W_oar  = n × P × L × r × E / 60  (propulsive power per oar × n oars)
    P      = 7.43 × r                 (mean pull at butt, N)
    L      = 0.99 m                   (Mark II effective pull, Shaw Table 9.7)
    E      = 0.780                    (Mark II mean ideal efficiency)

At equilibrium: W_hull = W_oar. Inverting gives r² = W×60/(n×7.43×L×E),
so r ∝ √W and V ∝ r^(2/3) (since W ∝ V³ dominant). Shaw's table reproduces
exactly: at hull×1.08, L=0.99, E=0.78, the rates 25.5/28.8/32.3 give
W=10518/13429/16935 W → predicted r=25.4/28.7/32.3 ✓.

## What the LL computes at each triple point

The LL's surge-hull equilibrium (170 oars, bare blade model, SurgeHull):

| Rate | Ve (m/s) | Thrust/oar (N) | Mean Fh (N) | Blade eff | Chain P (N) | Fh/P |
|---|---|---|---|---|---|---|
| 25.5 | 3.515 (6.83 kt) | 16.17 | 224 | 0.752 | 189 | 1.18 |
| 28.8 | 3.683 (7.16 kt) | 18.18 | 233 | 0.758 | 214 | 1.09 |
| 32.3 | 3.868 (7.52 kt) | 20.61 | 246 | 0.762 | 240 | 1.02 |

The blade's direct efficiency (thrust×V / handle_power) is ~0.75 at all
rates — barely changes. But the HANDLE FORCE ratio Fh_LL / P_chain drops:
1.18→1.09→1.02. At low rate the LL pulls 18% harder than chain's P=7.43r;
at high rate only 2% harder. The LL's power production per spm grows more
slowly than the chain's quadratic.

### The effective efficiency (chain sense)

If we write the LL's output in chain form W = n×P_chain×L×r×E_eff/60:

    E_eff = W_LL × 60 / (P_chain × L × r)

| Rate | E_eff (MkII L=0.99) | E_eff (Oly L=0.89) |
|---|---|---|
| 25.5 | 0.713 | 0.793 |
| 28.8 | 0.659 | 0.733 |
| 32.3 | 0.623 | 0.693 |

E_eff DROPS with rate: 0.713→0.659→0.623 (MkII basis) or
0.793→0.733→0.693 (Olympias basis). Chain assumes constant 0.78/0.756.
The LL says the blade gets LESS efficient at higher rates, while Shaw
says efficiency is constant. The E_eff drop is −13% from 25.5 to 32.3,
almost exactly the triple gap.

### Why does E_eff drop?

Chain: W_chain = n×7.43×r × L × r × E/60 = n×7.43×L×E/60 × r² — quadratic in r.
LL: W_LL = n × thrust(V,r) × V, where thrust depends on blade physics.

At fixed V, thrust grows rapidly with rate (at V=3.6 m/s: 13.85N→30.92N
from 25.5→32.3, superlinear). But at equilibrium, V ALSO grows with rate,
and thrust drops sharply with V (at 28.8 spm: 45.9N at 3.0 m/s → 18.2N at
3.68 m/s → 9.6N at 4.0 m/s). The equilibrium is where these two effects
balance. The blade's thrust-vs-V curve has a steep negative slope that
flattens the V-vs-rate response.

### The ITTC+Wave hull law — eliminated

At the triple speeds:

| Speed | Chain W | ITTC+Wave W | Diff |
|---|---|---|---|
| 7.0 kt | 10518 W | 10472 W | −0.4% |
| 7.5 kt | 13429 W | 13425 W | −0.0% |
| 8.0 kt | 16935 W | 17016 W | +0.5% |

The two hull laws agree to ±0.5% in the triple range. The M3 audit's
conclusion stands: hull factor is not the cause.

## Experiments run in this investigation

### Blade area sensitivity

| Area factor | Area (m²) | 25.5 spm | 28.8 spm | 32.3 spm |
|---|---|---|---|---|
| ×0.80 | 0.0624 | 6.65 (−5.0%) | 6.97 (−7.0%) | 7.33 (−8.4%) |
| ×1.00 | 0.0780 | 6.83 (−2.4%) | 7.16 (−4.5%) | 7.52 (−6.0%) |
| ×1.20 | 0.0936 | 6.97 (−0.4%) | 7.30 (−2.6%) | 7.67 (−4.2%) |
| ×1.45 | 0.1131 | 7.11 (+1.6%) | 7.45 (−0.7%) | 7.82 (−2.3%) |
| ×1.50 | 0.1170 | 7.14 (+2.0%) | 7.47 (−0.4%) | 7.84 (−2.0%) |
| ×2.00 | 0.1560 | 7.34 (+4.8%) | 7.67 (+2.3%) | 8.05 (+0.6%) |

Increasing blade area raises all speeds and somewhat flattens the gap
growth (area×1.45: +1.6/-0.7/-2.3% — gap range 3.9% vs current 3.6%).
Area×1.45 IS the geometric area (0.113 m²) without the 0.69 efficiency
correction — i.e., removing the immersion×span correction entirely.

Area×2.0 (implausible — twice a modern Big Blade) gives near-perfect
triple at high rate but +4.8% at low rate.

### The pull-length (L) question

| Quantity | Value | Notes |
|---|---|---|
| Geometric arc at handle | 0.803 m | lin 0.957 × sweep 48.1° (0.84 rad) |
| Shaw Olympias effective L | 0.89 m | chord minus end losses (S6) |
| Shaw Mark IIb effective L | 0.99 m | canted chord (ch.9) |
| Ratio Shaw/MkII / geometric | 1.23 | Mark II L is 23% longer than LL's arc |

The LL's blade model sweeps the FULL 48.1° arc (0.803 m at handle).
Shaw's "effective pull" L=0.99 m for Mark IIb is 23% longer than this.
The difference: Shaw's L includes the cant geometry (18.4° tilt, tan=1/3)
which extends the chord without increasing interscalmium, plus end-loss
corrections that the LL doesn't model.

But the triple test uses the **Olympias** rig (sweep 48.1°, hull×1.08 is
the Mark II hull factor applied to the Olympias blade for comparison with
Shaw's ch.7 which uses L=0.99). The 0.803 vs 0.99 comparison is between
the Olympias geometric arc and the Mark II effective pull — they SHOULD
differ. The fair comparison is Olympias arc 0.803 vs Shaw Olympias 0.89
(11% longer), which is the end-loss correction.

If the LL effectively has L≈0.80 but Shaw's Olympias chain uses L=0.89,
the LL should give LOWER speed than chain at the same rate — which it
does (−2.4% to −6.0%). But the gap grows with rate, so L alone (a constant
ratio) can't explain the rate-dependent part.

### The rate-dependent gap

The fixed ratios (L difference, area scaling) shift the triple uniformly
or with mild rate dependence. The GROWING gap (−2.4→−6.0%) requires a
rate-dependent mechanism. Candidates:

1. **Stroke timing**: t_drive gets shorter at higher rates (0.447→0.412s
   from 25.5→32.3). At shorter t_drive, the blade sweeps faster (omega =
   sweep/t_drive: 1.88→2.04 rad/s). At higher omega, the blade outruns the
   water more (vn = V−l_cp×omega more negative), which SHOULD increase
   thrust, not decrease. But the ship's higher V at higher rate partially
   cancels this.

2. **Sweep/end-loss at high rate**: At high rate, the interscalmium
   constraint is tighter (fixed 0.888 m between stations). Shaw notes
   Olympias achieves 48.1° "only with exceptional effort." At 32.3 spm the
   rowers may shorten their sweep (less than 48.1°) due to fatigue/rig
   interference, reducing L. The LL assumes full sweep at all rates.

3. **Blade efficiency vs rate**: The E_eff drop (0.713→0.623) is the
   measured rate dependence. In the blade model this arises because at
   higher V the blade's slip ratio changes — the advance per stroke vs
   slip. The flat-plate law's functional form may have rate dependence
   that Shaw's constant E=0.78 averages over.

4. **Oar inertia / flip cost**: At higher rates the catch-flip inertia
   spike grows (116N at 28.8 → higher at 32.3 per oar_inertia.py). While
   hull observables are stated as "unchanged" with inertia ON, the flip
   power (½Iω²×rate/60) does consume some of the rower's output that Shaw's
   "oar absorbed" term (0.96r+0.016r²) may not fully capture at high rates.

## Hypotheses

### H1: Blade area / efficiency correction is too aggressive

The 0.078 m² effective area = 0.113 geometric × 0.69 (immersion 0.85 ×
span 0.812). If either factor is too low, the blade under-produces:

- **Immersion 0.85**: average fraction of blade submerged. At low rate
  (lower V, more time per stroke) the blade may be deeper. At high rate
  (higher V, hull rises on wave-making), less immersed. A rate-dependent
  immersion would make the gap grow with rate.

- **Span efficiency 0.812**: from Hoerner AR=2.68. This is for steady flow;
  the unsteady per-stroke flow may have different effective AR (added mass
  regime at stroke ends increases effective force).

Experiments show area×1.2 closes the low-rate gap but not the high-rate
gap fully — area alone doesn't fix the rate dependence.

### H2: The chain's L and E are for Mark II, not Olympias

The ch.7 triple uses Mark II parameters (L=0.99, E=0.78, hull×1.08) but the
LL simulates the Olympias rig (sweep 48.1°→ arc 0.80, blade 0.078).
Comparing the LL's Olympias blade at hull×1.08 against the Mark II chain
is mixing rigs. The proper comparison:

| Comparison | LL rig | Chain rig | Meaning |
|---|---|---|---|
| Current triple test | Olympias (0.803) | Mark II (0.99) | Mixed — 23% L mismatch |
| Fair Olympias test | Olympias (0.803) | Olympias (0.89) | 11% mismatch |
| Fair Mark II test | Mark II (cant 18.4°, 55.6°) | Mark II (0.99) | Should use Mark IIb rig |

The "flat hull×1.08" approach (using Olympias blade + Mark II hull) was
justified as isolating the hull factor. But the blade rig SHOULD match
the chain's rig for a fair test. Running the triple with the MarkIIb rig
would test whether the cant geometry closes the gap.

### H3: Stroke kinematics at high rates

**H3a — t_drive interpolation.**
The LL's t_drive at 25.5/28.8/32.3 uses linear interpolation between
Table 9.6 measured points. But the real t_drive-vs-rate curve may not be
linear — at high rates the drive shortens less than linearly (rowers can't
accelerate the oar arbitrarily fast). If t_drive at 32.3 should be longer
than 0.412s, the blade would sweep slower → less thrust per stroke → but
also less power demanded. The interpolated t_drive may be too optimistic
at high rates (too short → too fast sweep).

**H3b — Sweep shortening at high rates.**
The Mark IIb cant (18.4°) gives 55.6° sweep vs Olympias's 48.1°. The LL
uses 48.1° at all rates. At 32.3 spm the crew may not achieve the full
48.1° due to rig interference / fatigue.

**H3c — The slip/lift regime.**
At higher rates, the oar's angular velocity increases while V also
increases. The blade's effective angle of attack and slip ratio change.
The flat-plate law (Fn = k|vn|vn) assumes pure normal drag; at different
slip ratios the lift component (omitted) may matter differently. The
"slip assumptions" flagged in the uncertainties register.

### H4: Over-constrained chain — the chain itself may not be self-consistent

The chain law W=155V³+4.13V⁵ was fitted to NTUA towing data (Grekoussis &
Loukakis 1985). The power law P=7.43r was fitted to the 116-rower trial
(6.8 kt, 38.75 spm, E=0.719). These two fits use DIFFERENT data sets that
were never cross-validated at the triple rates. The triple IS that cross-
validation — and it doesn't close perfectly.

Shaw himself notes the Mark II stroke is needed partly BECAUSE the
Olympias stroke is too short for 7–8 kt at those rates at fixed-seat
effort (ch.9). The triple uses Mark II L=0.99 for this reason. Applying
Mark II L to Olympias speeds conflates a design aspiration (what a future
ship could do) with a validation target (what Olympias did).

The M3 audit found: per-man gross 110/129/152W vs chain's 115/145/180W,
the gap growing with rate; Eg flat 51.5–52.3% vs 53–55% band. The blade
model's Eg is flatter and slightly lower than measurement.

---

## What to try next

### Quick experiments

1. **Run triple with MarkIIb rig** (sweep 55.6°, cant 18.4°, lin 1.061):
   does the cant close the rate-dependent gap? This is the fair comparison.
2. **Sweep t_drive at each triple rate**: measure how sensitive the
   equilibrium speed is to t_drive; compare interpolated vs measured values
   if Table 9.6 has non-obvious rate dependence.
3. **Decompose the power chain**: at each rate, report separately:
   handle power, blade efficiency, thrust×V, and compare each to chain's
   corresponding quantity to isolate where the rate dependence lives.
4. **Test rate-dependent blade area**: if immersion drops with speed (hull
   rise), parameterize area(V) and see if the gap closes.
5. **Check force-driven mode's triple**: does it give a different
   rate dependence? (The force mode's demand geometry may interact with rate
   differently than the kinematic blade model.)

### Model changes (ranked)

1. **Use matching rig for chain comparison** — Olympias triple vs Olympias
   chain (L=0.89, E=0.756) rather than Mark II (L=0.99, E=0.78). Simplest
   to test, fixes the conceptual mismatch.
2. **Rate-dependent sweep or L** — if the measured sweep drops at high
   rates (rig interference), parameterize sweep(rate).
3. **Unsteady blade efficiency** — add an AR or immersion correction that
   varies with rate/speed.
4. **Re-examine t_drive interpolation** — use measured values only, or
   fit a non-linear t_drive(rate) curve.

### Measurements needed

- t_drive at 25.5/28.8/32.3 spm (only 28.8 and 36.0 are in Table 9.6 for
  Olympias). The interpolated values are unmeasured.
- Blade immersion vs speed (does the blade rise at high speed?).
- The sweep achieved at each rate (is 48.1° maintained at 32.3 spm?).
- Mark IIb blade dimensions (still in Wolfson archive, Plans 15x).
