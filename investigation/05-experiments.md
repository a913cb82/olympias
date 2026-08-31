# Investigation 05 — Live Experiments and Measurements

All experiments run against the LL at commit 4b67934, dt=0.02, force=False
(kinematic blade) unless noted. Raw outputs for the claims in 01–04.

## E1: Cruise triple — fair rig comparison (the key finding)

The standard triple test (LL Olympias blade at hull×1.08 vs Mark II chain
L=0.99 E=0.78) mixes rigs. The Olympias geometric arc is 0.803 m vs Mark
II's 0.99 m — a 23% L mismatch baked into the comparison.

**Fair test: Olympias rig (arc 0.803) vs Olympias chain (L=0.89 E=0.756 hull×1.0):**

| Rate (spm) | Chain V (kt) | LL V (kt) | Gap |
|---|---|---|---|
| 25.5 | 6.889 | 6.892 | +0.0% |
| 28.8 | 7.382 | 7.221 | −2.2% |
| 32.3 | 7.870 | 7.583 | −3.6% |

**Standard (mixed) test: Olympias rig vs Mark II chain (L=0.99 E=0.78 hull×1.08):**

| Rate (spm) | Chain V (kt) | LL V (kt) | Gap |
|---|---|---|---|
| 25.5 | 7.010 | 6.832 | −2.5% |
| 28.8 | 7.509 | 7.159 | −4.7% |
| 32.3 | 8.003 | 7.520 | −6.0% |

The fair comparison shows: **at 25.5 spm the LL is perfect (+0.0%) against
its own chain**. The rate-dependent growth (−0→−3.6%) is the real blade-
model issue. The additional −2.5% constant offset in the mixed comparison
is the hull/rig mismatch (Mark II L=0.99 vs Olympias arc 0.80, hull×1.08
vs ×1.0).

**Conclusion**: Half the triple gap is a comparison artifact; the other
half (the rate-dependent −0→−3.6%) is the genuine open item.

## E2: Blade model internals at the triple points

At hull=1.0, Olympias rig:

| Rate | Ve (m/s) | Thrust/oar | Mean Fh | Blade eff | Chain P | Fh/P |
|---|---|---|---|---|---|---|
| 25.5 | 3.515 | 16.17 N | 224 N | 0.752 | 189 N | 1.18 |
| 28.8 | 3.683 | 18.18 N | 233 N | 0.758 | 214 N | 1.09 |
| 32.3 | 3.868 | 20.61 N | 246 N | 0.762 | 240 N | 1.02 |

Blade efficiency is ~0.75 at all rates (not rate-dependent). But
E_eff (chain sense: W×60/(P×L×r)) drops:

| Rate | E_eff (MkII L=0.99) | E_eff (Oly L=0.89) |
|---|---|---|
| 25.5 | 0.713 | 0.793 |
| 28.8 | 0.659 | 0.733 |
| 32.3 | 0.623 | 0.693 |

E_eff drops 13% from 25.5→32.3 in both bases while the blade's direct eff
stays flat. The rate dependence is in the HANDLE FORCE: Fh/P drops
1.18→1.02. At low rate the LL pulls harder than chain per stroke; at high
rate it converges — the power per spm is sub-quadratic.

At fixed V=3.6 m/s, thrust/oar vs rate:

| Rate | t_drive | Thrust | Eff | Fh | Chain P |
|---|---|---|---|---|---|
| 20.0 | 0.476s | 6.20 N | 0.819 | 105 N | 149 N |
| 25.5 | 0.447s | 13.85 N | 0.770 | 193 N | 189 N |
| 28.8 | 0.430s | 20.87 N | 0.741 | 266 N | 214 N |
| 32.3 | 0.412s | 30.92 N | 0.710 | 366 N | 240 N |
| 36.0 | 0.392s | 45.14 N | 0.676 | 502 N | 267 N |

At fixed V, thrust is SUPERLINEAR in rate (13.85→30.92 for 25.5→32.3 =
2.23× for 1.27× rate) while V at equilibrium also grows. The equilibrium
thrust (16.17→20.61 = 1.27× for 1.27× rate) shows the V-growth cancels
most of the superlinear thrust gain — the equilibrium is blade-limited.

Blade area sensitivity (at hull=1.08, standard comparison):

| Area factor | Area (m²) | 25.5 spm | 28.8 spm | 32.3 spm |
|---|---|---|---|---|
| ×0.80 | 0.0624 | −5.0% | −7.0% | −8.4% |
| ×1.00 | 0.0780 | −2.4% | −4.5% | −6.0% |
| ×1.20 | 0.0936 | −0.4% | −2.6% | −4.2% |
| ×1.45 | 0.1131 | +1.6% | −0.7% | −2.3% |
| ×2.00 | 0.1560 | +4.8% | +2.3% | +0.6% |

Area×1.45 (geometric, no correction) nearly closes the low-rate gap but
leaves −2.3% at high rate. Area alone is not rate-dependent enough.

## E3: Turn time — the settled-speed attractor

Tightest turn (44.5 spm sprint, 6.5 kt entry, full rudder + one side holds):

```
t=  0: V=6.50 kt  ω= 0.0°/s  β= —      (entry)
t= 10: V=4.95 kt  ω=-3.40°/s  β=1.7°
t= 20: V=4.36 kt  ω=-4.17°/s  β=2.4°
t= 30: V=4.24 kt  ω=-4.35°/s  β=2.4°   (approaching settle)
t= 60: V=3.75 kt  ω=-4.03°/s  β=2.9°
t= 90: V=3.43 kt  ω=-3.62°/s  β=2.8°   (settled, W' drained)
D=61.9 m  t360=94.7s  V_end=3.44 kt  V_mean=πD/t=3.99 kt
Trial: V_mean=π×62/128=2.96 kt
```

Forces at settle (V=3.43 kt=1.76 m/s):

| Force | Value |
|---|---|
| Hull drag D(V)=W/V | 524 N |
| Rudder drag (full helm FAC 1.4) | 650 N |
| Total drag | 1174 N |
| Hold brake (85×5.8×V²) | 1538 N |
| Rowing thrust (85×?, W' drained) | limited to P_crit |

Entry-speed independence — the settled speed is an attractor:

| V0 (kt) | V at 60s (kt) | ω (°/s) | D (m) | β (°) |
|---|---|---|---|---|
| 6.5 | 3.75 | −4.03 | 54.9 | 2.9 |
| 5.0 | 3.74 | −4.02 | 54.9 | 2.9 |
| 4.0 | 3.74 | −4.01 | 54.9 | 2.9 |
| 3.0 | 3.77 | −4.04 | 55.0 | 2.8 |

Regardless of entry speed, the turn settles to ~3.7 kt. The 30 s gap is
NOT about the entry transient — it's about the settled speed being ~0.5 kt
too high (3.5–3.8 vs trial's ~2.9).

### Tried: extra drag

| Extra constant drag | D (m) | t360 (s) | V_end (kt) |
|---|---|---|---|
| 0 N | 61.9 | 95 | 3.44 |
| 500 N | 60.5 | 97 | 3.16 |
| 1000 N | 59.0 | 99 | 3.14 |
| 2000 N | 55.4 | 101 | 2.80 |

| Extra k×V² drag (k at 2 m/s) | D (m) | t360 (s) | V_end (kt) |
|---|---|---|---|
| 0 N | 61.9 | 95 | 3.44 |
| 400 N | 60.6 | 97 | 3.26 |
| 1600 N | 57.2 | 101 | 3.12 |

Extra drag tightens D as it lengthens t — the diameter gate breaks before
time closes. Maximum with 2000N: t360=101s, still 27s short. **Drag alone
cannot close the gap** (confirms the earlier linear-damping rejection).

### Tried: degraded rowing

| Rowing rate | D (m) | t360 (s) | V_end (kt) |
|---|---|---|---|
| 44.5 | 61.9 | 95 | 3.44 |
| 30.0 | 61.7 | 99 | 3.72 |
| 25.0 | 61.5 | 105 | 3.41 |
| 20.0 | 61.3 | 112 | 3.18 |

| Initial W' fraction | D (m) | t360 (s) | V_end (kt) |
|---|---|---|---|
| 1.0 | 61.9 | 95 | 3.44 |
| 0.5 | 61.2 | 100 | 3.31 |
| 0.2 | 60.9 | 105 | 3.27 |
| 0.0 | 61.5 | 109 | 3.27 |

Maximum with depleted crew (W'=0): 109s. With low rate (20 spm): 112s.
Still 16–19s short of 128s. Neither alone closes the gap.

### Tried: W' sensitivity on tightest

| W' (J/man) | D (m) | t360 (s) | V_end (kt) |
|---|---|---|---|
| 3000 | 61.2 | 100 | 3.31 |
| 6000 | 61.9 | 95 | 3.44 |
| 10000 | 61.9 | 90 | 3.86 |
| 20000 | 61.9 | 90 | 4.16 |

Lower W' → longer time (less thrust) but only 5s per halving.

## E4: Drift angle — A_lat sensitivity

G1 full rudder @ 6 kt, rate from rate_for_speed:

| A_lat factor | A_lat (m²) | β (deg) | D (m) | V (kt) |
|---|---|---|---|---|
| ×1.0 | 30.1 | −1.70 | 82.9 | 5.34 |
| ×0.5 | 15.0 | −3.39 | 82.7 | 5.21 |
| ×0.3 | 9.0 | −5.65 | 82.5 | 5.04 |
| ×0.2 | 6.0 | −8.48 | 82.3 | 4.85 |

To get β≈8.5° (lower trial estimate): need A_lat≈6 m², 5× smaller than
real hull's 30.09 m². D barely changes (turn size not sensitive to A_lat)
but V drops 5.34→4.85 kt.

The real hull's A_lat=30.09 m² is from basis_hull_offsets.tsv (Simpson of
drafts at trial WL 1.10 m). Cannot be reduced without contradicting geometry.

At settle, force balance (G1):

| Term | Value |
|---|---|
| f_hull = ρA_lat\|U\|v | −6900 N |
| m×U×ω | +8192 N |
| f_rud (coeff 0.81 × rud_drag) | ~1274 N |
| Required: Fy_oars + f_rud ≈ f_hull + mUω → small residual |

f_hull nearly cancels mUω; the residual is Fy+f_rud. The steady drift is
the small residual between two large forces — sensitive to the numerator.

## E5: Rate-for-speed at the turn entry

The tightest turn uses rate_for_speed("Olympias", 6.5 kt, n_oars=85) to
find the rate whose thrust balances drag at entry. This gives ~31.5 spm
for 85 oars. But the trial's rate assignment for the tightest sprint is
unknown — the hold spectrum wasn't recorded.

If the trial used a different effective crew (not exactly 85 rowing), the
entry rate changes. The rate sensitivity table above (E3, degraded rowing)
shows that lower rate lengthens t_360 — but the trial was supposedly a
sprint (high rate, high effort).

## E6: Hull drag law at turn-relevant speeds

| Speed (kt) | W (W) | Drag D=W/V (N) |
|---|---|---|
| 2.0 | 174 | 169 |
| 3.0 | 606 | 393 |
| 4.0 | 1503 | 730 |
| 5.0 | 3103 | 1206 |
| 6.0 | 5715 | 1852 |
| 6.5 | 7522 | 2249 |

The hull drag law at 3.5 kt is only ~546N — very low. At the turn's
settled speed (3.4 kt), hull drag is a minor term vs rudder (650N) and
hold brake (1538N). This is why adding hull-proportional extra drag has
so little effect on t_360 — the hull drag at low speed is not the dominant
force.

## E7: Turn D vs hull law

At hull=1.0, G1 D=~91.5m (from crossflow analysis). With hull drag from
ITTC+wave (same as chain at cruise speeds), G1 would be nearly identical
— the turn diameter is set by Q/(Omega×V²) balance, not hull drag.

## E8: The stationary-turn second direction

From test_revf_anchors.py: stationary turn (Zygian+Thranite, 58 oars,
from rest at 27 spm) measured 3.5°/s vs LL 2.32°/s in-place (−34%) and
1.06°/s one-side (−70%).

This is the OPPOSITE error from t_360: at low speed/partial crew the LL
is too SLOW. Together with t_360 (too FAST at high speed/full crew), they
bracket the yaw physics — a speed- or crew-dependent error in the yaw
moment or damping.
