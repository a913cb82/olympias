# Deep dive — LL vs Richard Braithwaite's simulation on the same ship

Both models simulate the same hull (Olympias, LWL 32.35 m, 170 oars, trial draft 1.10 m) against the same trial report (Ref (1) — the 1988 trials, and Rankov 2012). Both integrate the same 3-DOF rigid-body equations in the ship frame with the same centripetal couplings:

```
m(u̇ − v·r) = X(U²) + Fx_oars + Fx_rudder + m·v·r
m(v̇ + u·r) = Yv·v + Yr·r − m·u·r + Fy_oars + Fy_rudder
I·ṙ = Nv·v + Nr·r + Nr2·r|r| + Q_oar + Q_rudder
```

Both use simple Euler. Both carry ≈46 tonnes apparent mass (LL: 1.10 × 40.95 t = 45.0 t; RB sheet: 1/(1−0.04−0.06·Cb) ≈ 1.07 × 45.38 t ≈ 48.6 t with `m_x=DISP·(0.04+0.06Cb)`). Both carry Iz ≈ 4–5.28×10⁶ kg·m² (Taylor 4e6, sheet `m(L/3)² = 5.28e6`).

The difference is what goes into X, Y, N and a, b, c.

---

## 1. Hull resistance — same tank data, different fits

**LL** (`ship.py` via `common/chain.py` hull_power):
- Chain law `W(V) = 155·V³ + 4.13·V⁵` watts, V in m/s (Shaw ch.7/ch.9, fitted to Grekoussis & Loukakis 1985 NTUA tow data, trial-validated via lane-4/lane-6). Drag `D(V)=W/V`. The 3-band Taylor table is kept as `VESSELS["Olympias"]` for the `rate_for_speed` helper, but the hull_advance path uses the chain law.
- ITTC alternative exists as `ship_drawings.hull_friction` (`Rf=0.5·ρ·V²·WSA·Cf`, `Cf=0.075/(log10Re−2)²`, WSA 130.5 m², `Re=V·LWL/ν`) + `Rw=5.3·V⁴` wave — matches chain ±0.5% at the triple speeds, so not the triple gap.

**Braithwaite** (report §5.1 + sheet `Powering`/`Manoeuvring`):
- Trials piecewise `40.2·V² (1–6 kt), 75.2·V²−1560 (7–8), 88.6·V²−2640 (9–10)` N, V in kt — the same 1988 tow trials, fitted as quadratics per speed band, taken directly from the trials table (DECODE.md).
- Fitted cubics for the sim: rudders-up `51.4·V³−76·V²+223·V`, rudders-down `38·V³+170·V²+25·V` (V in m/s) — linear regressions over 1–10 kt.
- In-code alternatives `Holtrop` (Holtrop-Mennen 1982, full viscous+wave, wave via `Rw/W=exp(m1·Fn^d+m2·cos(Λ·Fn⁻²))`) and `DelftResistance` (Keuning & Sonnenberg yacht series, 11 Fn × 9 coeff table). Holtrop underpredicts high-Fn for this Cb; Delft valid Fn 0.1–0.6 only.

**Numbers at cruise:**

| V | Chain W/V | RB raised cubic | RB piecewise | Diff cubic vs chain |
|---|---|---|---|---|
| 5 kt (2.57 m/s) | 1206 N | 946 N | 1043 N | −22% / −14% |
| 7 kt (3.60) | 2705 N | 2218 N | 2125 N | −18% / −21% |
| 8 kt (4.11) | 3810 N | 3214 N | 3211 N | −16% / −16% |
| 9 kt (4.63) | 5221 N | 4505 N | 4552 N | −14% / −13% |

RB drag is **10–22% lower** than the chain. Same data, different fits. The chain is the one the power chain closes on (`W_oar = n·P·L·r·E/60` needs ~9.7 kW at 7 kt; RB's drag would need ~8 kW). Nothing here is wrong — just two fits to noisy tank points. The workbook explicitly stores the trials piecewise, Holtrop, and Delft side-by-side and flags them as alternatives.

---

## 2. Blade and thrust — where the models diverge most

**LL** (`ll/blade.py` + `ll/oar.py` + `ll/rower.py`):

- Blade = flat plate, `Fn = ½·ρ·A·C_N·|vn|·vn`, `C_N=1.8` (Hoerner), `ρ=1025`, `A=0.078 m² = 0.113 geometric × 0.69 (immersion 0.85 × span 0.81)`. Force is the normal component only — drag-dominated, no lift.
- Two laws in one identity: Shaw ch.9's `(q/p)²` turning-point law at the *actual* turning point is algebraically `Fn = k·|vn|·vn` (`TURNING_POINT="actual"`, `p=−V·nx/ω`, `q=l_cp−p`, `vn=(V·nx+l_cp·ω)·slip`). The geometric variant (`TURNING_POINT="geometric"`, `p=Lplan/cos30°−0.953·cos(120C/B)`) is OFF — it gives net negative thrust at Table 9.6 points. A macon-polar variant (`BLADE_POLAR`) with `CL=sin2α, CD=2sin²α, Fn=k·2/CN·vm·vn` is also OFF. Both are kept as switches, tested, rejected for Olympias.
- One oar stepping (`ll/oar.py`): piecewise-linear in angle. Drive `C: +B/2→−B/2` at commanded `ωd=B/t_drive` (Table 9.6), recovery `−B/2→+B/2` at `ωr`. Force-driven mode (`force=True`, promoted) solves `I·θ̈=−dir·Fh·lin−Fn·l_cp` with demand `Fh` (chain `P=7.43·r` via `fh_demanded = FH_BURST·cosMean` at spoude else `7.43·r·PRESS·cosMean`, `cosMean=sin(B/2)/(B/2)`). Equilibrium `vn_eq=−dir·√(Fh·lin/(k·l_cp))`, catch flip pinned (`Fh_flip=MIT·(ωr+ωe)/(t_rise·lin)` ≤700 N), recovery kinematic, substep `h=0.001` with mean forces. MIT spruce 9.74 kg·m² (old-fir weighted 14.7: thranite 13.1, zygian 18.0, thalmian 13.1).
- Thrust slope: at fixed V, thrust per oar rises fast with rate; at fixed rate it falls steeply with V. The burst mean-force `170·T̄(V)=D(V)` via `equilibrium_speed` (bare-Oar bisection in `ship.py`) gives 7.22 kt at 28.8 spm (Table 9.6) — the burst V*.

**Braithwaite** (`OarForces` + report §3.2):

- Linear thrust `Thrust = press·0.5·n·maxT·(1−V_local/9.252)`, `maxT=5000/62=80.6 N/oar` (trials, ~81 N), `9.252=18·0.514` m/s (zero at 18 kt), `press∈[−1,1]`, `lever 5.2 m` (Olympias, vs `4.5` for Design). `V_local = u±lever·r` (port `u−lever·r`, stbd `u+lever·r`; all blades at x=0, no longitudinal spread, no `v`). Moment `±Thrust·lever`, `FY=0`, `MZ=sum`. Feeding at `FY=0` — turning is pure differential thrust + rudder, no blade sway.
- Detailed §3.2 oar (the Rev F rowing model): 4 phases — finish (constant `Mf`, parabola `θrel=At²+Bt+C`), recovery (cubic `At'³+Bt'²+Ct'+D`, `A=−2B/3tre, B=3θR/tre²`), catch (mirror), power (blade macro: `Pb=Pt+LO·(sinθ,side·cosθ)`, `Vb=LO·ω(cosθ,−side·sinθ)`, `Vw=(−u+side·cosθ·r,−v−sinθ·r)`, `Vbrel=Vb−Vw`, `α=acos(Vbrel·OA/|Vbrel|)` folded `[0,π/2]`, `CD=2sin²α, CL=sin2α` Caplan-Gardiner macon polars, `L=0.5·ρ·EffA·|Vbrel|²·CL`, `D=0.5·ρ·EffA·|Vbrel|²·CD`, `Fb`, `bladeMoment=Fb×(Pb−Pt)+side·I·ω̇`, `Fh=−side·bladeMom/Ii·cos(θ+...)`, foot `Ff=−Fh+Li·ω̇·cos·A·mr` with `mr=51.02 kg` (68% of 75 kg rower, Table p11). Work `ΔW=IL·Fh·cosθ·ω·dt`. Secant iteration for ω to match `M*=Mmax·(1−θrel²/(catchFactor·θR/2)²)`, `Mmax(V)` linear in ship speed (Hill-like), catchFactor; modes STOP/FOLLOW/TIMED, feather when `Fh>Mmax`.

**What's the same:** flat-plate `CD=2sin²α`, `CL=sin2α`, Hoerner law; rower moving mass `~51 kg` vs LL's MIT; 4-phase stroke with inertia at the ends; the `Press·(1−V/V0)` form is the linearization of the LL's flat-plate `|vn|·vn` near cruise.

**What's different:**
| | LL | Braithwaite |
|---|---|---|
| Law shape | quadratic `|vn|·vn` | linear `1−V/9.252` |
| Zero-thrust speed | implicit (blade outruns water, thrust→0 smoothly) | explicit 18 kt |
| Per-thrust at cruise | `Fn=½ρACN·vn|vn|` ~120–130 N peak | `81·(1−V/9.252)` ~45 N/oar at 7 kt (170×45=7650 N → vs drag 2705 N: surplus 4945 N → acceleration, not equilibrium at 7.2) |
| Local flow | aggregated `V∓ω·lever` (or per-station `(u−r·y, v+r·x)` with `stations=True`, OFF) | `V_local=u±lever·r` per side (all blades at x=0, no `v`) |
| Sway from oars | `Fy=−Fn·sinC` (port/starboard, geminated) | `FY=0` |
| Rower body | MIT only (oar), body work folded into `P=7.43r` chain | explicit `mr=51 kg` moving mass + footplate `Ff` |
| Blade ignition | instant in/out | instant in/out + feather beyond `Fh>Mmax` |

The linear 81-N law is a trials-fit straight line through (0 kt→81 N, 18 kt→0). The LL's quadratic law is fitted through the chain's speed anchors (7.2 kt @ 28.8 spm) and the flat-plate physics. At cruise they differ by a factor ~2 in per-oar thrust — but the LL's *mean* thrust after averaging over the drive matches the chain's `W_oar/V` (the 63 W/man check: `thrust·V ≈ W_hull/n`).

---

## 3. Crew and stamina

**LL** (`ll/rower.py` — TierCrew / SideCrew):

- Per-tier crews 31/27/27 per side (thranite/zygian/thalmian), each with its own `TierCrew` (own `Oar`, `W′` tank, `rate_eff`).
- `P_crit=80 W/man` (Rossiter & Whipp, Rankov ch.23), `W_max=6000 J` (≈5 kJ anchor, ch.9; force mode includes flip 6.0 kJ), `τ=120 s` refill, `Fh_MAX=700 N`, `Fh_BURST=330 N` (chain sprint 7.43·44.5), `T_REC_MIN=0.5 s`, `B_FLOOR_FRAC=0.4`, `HOLD_FRAC=0.08` (`0.69·2sin²18.9°/1.8`, `ALPHA_HOLD 18.9°`), `P_PER_SPM=7.43 N/spm`, `oar_absorbed=0.96r+0.016r²`, thalmian `power_factor 0.9→0.6` linear 32→44.5 spm (head-room).
- `fh_demanded = FH_BURST·cosMean` (spoude) else `7.43·r·PRESS·cosMean`; `cosMean=sin(B/2)/(B/2)`. Planned drive `w = min(ω_cmd, w_p, w_m)` where `w_p` is Fh_MAX limit, `w_m` is mean-force limit (or `P_crit·pf·60/(B·lin·r)` when `W≤0`), tempo slot `60/r−0.5`, feather if `V·sin(a)/a−l_cp·w>0`. `p_ext=fh_mean·B·lin·rate/60`, `p_gross=p_ext·scale+flip+absorbed`, `W' Ẇ = −(p−p_critG)` drain else `min(p_critG−p, Wmax/τ)` refill (`p_critG=P_crit+absorbed`). `SideCrew` weakest `rate_eff` governs, `W_frac=min W_frac`, `last_fh=max fh`.

**Braithwaite:**

- No stamina, no W′, no endurance. The rower is a force curve `Mmax(V)` linear in ship speed (Hill-like) and a catchFactor continuity term. The sheet's `OarForces` is just `press·(n/2)·maxT·(1−V_local/9.252)` — rate is outside the VBA; the report's §5.1 handles rate via the 4-phase timing (finish/recovery/power) and the secant `ω` solver, but no fatigue.

RB is a *kinematic* rower at fixed rate; LL is a *physiological* rower whose rate, force, and power emerge from tanks. Lane-4's power chain vs RB's linear 81 N is the cleanest statement of the same ship at different abstractions.

---

## 4. Hull sway and yaw damping

**LL** (`ship.py` hull_advance):

```
f_hull  = ρ·A_lat·|u|·v                    (Taylor ρ·A_lat·U²·sinβ, β small)
q_hull  = f_hull·clr_offset                  (0.93 m forward; G1/F1 W5 fit)
omega_drag = Ω·ω|ω|    Ω=0.5·ρ·CD·J = 3.00×10⁶  (CD 0.252, J 23217 m⁵ at Z=1.10)
v̇ = (Fy+F_rud+f_heel−f_hull)/m_app − u·ω
ω̇ = (Q+q_hull−Ω_drag)/I    I=4.76×10⁶  (m·(L/3)²)
drag = hull_power(|u|)/|u| + rud_drag + d_extra
u̇ = (Fx−drag)/m_app + v·ω
```
`dt=0.02 s`, lever `2.00 m = (31·2.7+27·2.0+27·1.2)/85` (thranite 2.7 from beam 5.45–5.6 m; zygian/thalmian 2.0/1.2 [?] pending Fig 16). Keleustes: `|rp−rs|>2.0 spm` for `>2·60/min(rp,rs)` → `rate=min`.

**RB** (`ManAcceleration`, Clarke-Gedling-Hine 1983 prime-I):

```
primes: −Y'_vd/(π(T/L)²)=1+0.16Cb·B/T−5.1(B/L)²  etc. (8 numbers)
dims: Yvd=Y'vd·0.5ρL³, Yrd=Y'rd·0.5ρL⁴, Nvd·0.5ρL⁴, Nrd·0.5ρL⁵;
      Yv·0.5ρUL², Yr·0.5ρUL³, Nv·0.5ρUL³, Nr·0.5ρUL⁴   (U=√(u²+v²))
surge m: DISP·(0.04+0.06Cb) → mSurge=DISP·(1+frac) (~7–10%)
coupled: det=(m−Yvd)(Iz−Nrd)−Yrd·Nvd, Cramer's rule:
fX=drag+m·v·r, fY=Yv·v+Yr·r−m·u·r, fZ=Nv·v+Nr·r+Nr2·r|r|, Nr2=−ρ·CN·T·L⁴/64
CN 0.8 in code (comment/paper say 0.40 → factor-2 dispute)
solved: u̇=fX/mSurge, v̇=((Iz−Nrd)fY+Yrd·fZ)/det, ṙ=(Nvd·fY+(m−Yvd)fZ)/det
Euler dt=1 s in sheet
```

**Direct comparison of the yaw damper:**

| | LL | RB |
|---|---|---|
| Form | `Ω·ω|ω|`, `Ω=0.5·ρ·CD·J`, `CD0.252`, `J=∫d|x−Xcg|³dx=23217` | `Nr2·r|r|`, `Nr2=−ρ·CN·T·L⁴/64`, `CN 0.8` (paper 0.4) |
| Physics | cross-flow integral over tapered lateral plane (d(x) from real offsets) | rectangular projection `T·L⁴/64` (RB) vs real `J` (LL) — same integral, different hull idealization |
| Value at trial | `Ω=3.00×10⁶` (fitted 3.20×10⁶ @ CD0.30; parametric 3.25×10⁶) — grounded from `basis_hull_offsets.tsv` | `ρ·0.8·T·L⁴/64 = 8.0×10⁶` (with paper 0.4 → 4.0×10⁶) — factor-2 dispute, rectangular vs tapered |
| How to reconcile | `J` from real offsets, `CD` via drag crisis (0.30–0.60) → 0.252 from rectangular/tapered DECODE C9 | replace rectangular `T·L⁴/64` by real `J` from the same offsets; settle CN 0.4 vs 0.8 — LL's `Ω` already is `J` at `CD=0.252` (DECODE C9: rectangular `CD0.30 → 3.25e6` vs real `CD0.252 → 3.00e6`, ×1.08) |
| Linear damping | Clarke `Yv·v, Yr·r, Nv·v, Nr·r` tried as `ll/clarke.py` — **rejected** (100× too much for Cb=0.32, L/B~8.7; merchant regressions Cb 0.5–0.8) | Clarke `Yv·v+Yr·r, Nv·v+Nr·r` built-in — **kept** (RB uses merchant regressions on a trireme hull too; same overprediction but not flagged) |
| Sway | linear `f_hull=ρ·A_lat·|u|·v`, `A_lat=30.09 m²` (Simpson 21 stations) | Clarke `Yv·v+Yr·r` + coupled mass matrix |
| Heel-coupled (step 3) | spike `experimental_coupling.py` OFF: `heel=atan((f_rud·arm_rud+f_hull·arm_lat)/(m·g·(GM−0.2)))`, `f_heel=K_heel·sin heel` (80 kN), `d_extra=base·K_drag·(sin²β+sin²heel)` (K=4) — negative result (G1 91.9→98.7, F1 121.0→133.5 at 80k, fixes drift 1.7°→3.5° but breaks diameters) | no heel coupling; GM/heeling is in report §3.5 text only |

The yaw-damper physics is the same cross-flow integral; the number differs because LL integrates the real tapered hull and RB approximates it as a rectangle. With the real offsets now in hand (`research/sources/galley-sizing-xlsm/basis_hull_offsets.tsv`, LWL 32.35 m, 21×27 Z/Y), the two should collapse to one value — that is the named reconciliation in `investigation/01-04`.

---

## 5. Rudder

**LL** (`ship.py` + `manoeuvre_model.py` VESSELS, Taylor ch.31):

- `VKT=|V|/KT`, `KT=0.51444`, `rud_drag=vessel.rudder_drag(vkt,φ,FAC)`,
  `f_rud=vessel.rudder_coeff(φ)·rud_drag`, `coeff=0.14+0.020φ−0.00015φ²` (40–80% of drag → lateral), `Q_rud=f_rud·lever_rudder` (14.9 m Olympias / 16.5 Mark IIb).
- Straight drag `RUDDER_DRAG_STRAIGHT=39.4 N/kt²` (`(79.6−40.2)V²`, measured with/without rudders), `FAC_FULL=1.4` at `67.5°` (straight+induced) → induced `15.8 N/kt²` → `η=0.045` (wake 0.5 × AR 0.6 × single 0.5 × ventilation 0.3). `FAC(φ)=1+0.4·CD(φ)/CD67.5`, `CD=2sin²φ` (Hoerner flat plate, kept but `FAC` is constant 1.4 to first order).
- Keel vert arms `arm_lat 1.46 / arm_rud 1.16 m`, GM `0.97 / 0.9 m` (Table 31.1).

**RB** (`RudderForces`, Hoerner aerofoil at the stock):

- Rudder position `posMag=√(X²+Y²)` (`X=−15 Olympias, −7.975 Design`), local flow `Vrx=u+posMag·cosα_rud·r, Vry=v+posMag·sinα_rud·r`, `Vmag`. Both rudders: `SA=2·Area` (0.75 m² each, 1.5×0.5; Design 0.25 m², 0.96×0.26). `Re=|u|·chord/ν` (`ν=1.188e-6`, uses `u` not `Vmag` — minor), `Cf=0.075/(log10Re−2)²`, `RV=0.5·ρ·u²·SA·Cf` (viscous).
- `AoA=acos((V·OA)/Vmag)`, flip if `>π/2`, `CD=2sin²AoA`, `CL=sin2AoA`, `L=0.5·ρ·A·Vmag²·CL`, `D=0.5·ρ·A·Vmag²·CD + 0.5·(137·u²+0.65·u)·SA/1.5 + RV` (parasitic `137V²+0.65V` is both rudders — powering fit → `/1.5` scales by area, `0.5` half at zero AoA). Resolve `Lx=L·Vry/Vmag` etc., flip `L` if needed, `RZ=RY·X−RX·Y`.

Both are Hoerner flat-plate `CL=sin2α, CD=2sin²α` — same foil theory, different bookkeeping. RB adds viscous `Cf` and a powering-fit parasitic (`137V²`) that LL models as `39.4·Vkt²` (same order: at 7 kt RB parasitic `137·3.6²+0.65·3.6=1778` vs LL straight `39.4·49=1931` — 8% apart, independent confirmation).

---

## 6. Integration and numerics

| | LL | RB |
|---|---|---|
| Timestep | `dt=0.02 s` in `Ship`, `dt=0.001 s` substep in force-driven oar (`ll/oar.py`), `burst: 600 vs 3000 steps <0.3%` | `dt=1 s` in the Manoeuvring sheet (circular 10-s blocks via `transfer`/`updata` macros `Ctrl+a/b`) |
| Blade stepping | mean over cycle: `Fx,V` averaged over `n_cycles=4` at `td/600`, bisection `0.5–6.5 m/s` × 50 iters for `V*` | per-timestep in the loop, Oar 4-phase `θrel(t)` parabola/cubic, secant iteration per step for ω |
| Stability | Surge ripple 0.2 kt p-p physical; sway yaw bias measured loose `−0.001 rad/s`; dt convergence 0.005 gate | no dt study shown |
| Interpolation | piecewise-linear with flat clamps (`_pwl`, `_d_inv_lin`) | `Interpolate` (Lagrange quadratic, discontinuous slopes by design) + `CUBIC` (natural spline, `y2(100)` globals) + `Lininterp`; `WLS` bisection with `3.14/180` π error 0.05% |
| Randomness | seeded `numpy` | none |

---

## 7. Validation and what remains open

**LL** (`simulation/docs/VALIDATION.md`, 159–162 checks green):

- Gate 1: one-oar <0.5% vs rigid_oar_model.py
- Gate 2: burst `170·T̄=D` at hull=1.0: 25.5/28.8/32.3/36.0 → 6.89/7.22/7.58/7.99 kt vs chain 7.0/7.2/8.0/8.2 at hull1.08 (−1.6/+0.3/−5.3/−2.7; fair hull1.0 +0.0/−0.2/−3.6). Force mode at hull1.0 6.65/7.13/7.62 vs Olympias chain 6.57/7.15/7.69 (+1.2/−0.2/−1.0). Sprint 44.5 @130 → 7.65 burst (LL) vs 8.2–8.4 trial.
- Gate 3: turns W5 grounded 40.95 t / 4.76e6 / 3.00e6 / 0.93 m / 2.00 m: G1 +2.4%, F1 +7.6% (gate 8%), tightest −2.7% → all pass; per-station inverted `g1 90→128/134, f1 118→232/264` (kept OFF).
- Gate 4: W′ physiology, tempo loss, backing degenerates to hold.
- Gates 5/5a/6–8: inertia, force-driven, per-tier, cant 0.30→0.51–0.54, sway 3-DOF.
- Level-2 HL: turn D <1.3%, t180 within 20%, settled orbit 1.03–1.09×.
- Open (3): t360 95s vs 128s (−26%, V̄ 3.99 vs 2.96 kt), drift 1.4° vs 7.8–15° (5–10×), cruise triple −2.5→−6% mixed / fair −0→−3.6%. Heel spike (step 3) negative: no single heel coupling closes drift+time without breaking G1/F1.

**Braithwaite (Rev F):**

- **No validation section.** §§6–7 are one-line stubs. The appendix's source code is absent. Calibration notes are scattered in prose: "Nr changed to a constant to give the observed turning rate at zero velocity" (the same quadratic-yaw choice LL makes), "calibrated: CN=0.40 reproduces turning circle" (code says 0.80). No plotted fits, no error metrics, no per-gate pass/fail. The report's numbers that would be validated — the stationary turn 3.5°/s at 27 spm (partial crew, 116 oars, faster than full-crew 2.81°/s), the zig-zag 8°→7°, the 9.95 kt topline — are anchors to check, not gates that pass.
- Where RB cites trial data (§5.1: 40.2V² etc., Table 3: 0.113 m², 30 kg·m²) it agrees with the LL's grounded values (RB `0.113` confirms LL's A5 gap `0.078 = 0.113×0.69`, `30 kg·m²` confirms Table 3.1's A-family cell — source-side anomaly).

**The three open items through both models:**

| Gap | LL | RB would say | Together |
|---|---|---|---|
| t360 (95→128) | settled V 3.4 kt vs trial 2.9 mean; YAW_LIN_DAMP tested & rejected (+24/31/25% on D); buildup ~2s, yaw/oar ~1s, Omega/C_D maxed | RB not re-validated on this scenario (70s sheet run: U 4→1.78 m/s, ψ 0.317 rad @15s, lever 5.2, CN 0.8); stationary anchor 3.5°/s (102.9 s) sits between LL 95s and trial 128s — between, not decisive | Both bracket the gap; RB's per-station flow suggests LL lever damping 400 kN·m·s explains the inverted station layer (not the t360 itself). The floor must be turn-specific (brake, W′/P_crit, or residual drag) without breaking the burst. |
| Drift (1.4→7.8) | `ρA_lat|U|v≈6900N` vs `mUω≈8192N`, need A_lat≈6m² for 8.5° vs real 30.09; Clarke `Yv·v+Yr·r` rejected 100× too large (Cb 0.32 vs merchant 0.5–0.8); heel spike G1 91.9→98.7 fails before drift 1.7→3.5° | RB uses Clarke `Yv·v+Yr·r, Nv·v+Nr·r` built-in (same merchant regressions, same overprediction but kept); RB's `Yv/(π(T/L)²)` for Olympias would be ~0.6×10⁵ — not checked vs LL's 1.8×10⁵ effective | Both live with a drift gap; LL's `f_hull` linear vs RB's coupled matrix differ, but neither reaches 7.8° without help. RB's coupled mass matrix is not the fix (LL rejected the same linear terms). |
| Triple (−0→−3.6 fair) | `E_eff 0.79→0.69` drops 13% vs constant 75.6%; burst via bare Oar, sustained via Ship P_crit ~6.1 kt; blade area ×1.45 closes low end | Linear `81(1−V/9.252)` vs LL `Fn=0.5ρACN·vn|vn|` — at 7.2 kt RB thrust 81·(1−7.2/18)=48.6 N/oar (vs LL's thrust ~17 N but W=thrust·V vs hull V scaling differs); RB's 9.95 kt topline (170×81=13.77 kN vs drag at 9.95) vs LL 7.22 at 28.8 shows the 81 N/oar is not comparable to LL's mean | RB's 81 N linear law cannot be compared thrust-per-oar to LL's cycle-mean — RB's is peak per side / LL's is cycle-mean. The triple investigation's Holtrop±0.5% at triple speeds rules out hull law as the cause in both. |

---

## 8. Takeaways

**Where RB helps LL:**
- Stationary-turn 3.5°/s / zig-zag 8/7° as boundary data (investigation/06).
- `0.113 m²` blade area as the independent confirm of the chain's `0.078` effective (immersion 0.85 × span 0.81).
- `30 kg·m²` zygian inertia confirming the A/B anomaly is source-side.
- Per-station `V_local=u±lever·r` and the `Figure 16` station plan as the unpacking path for the fitted lever's 4.8 m (if decoded: `media/image21.jpeg` at 2400 dpi, `sheet_Transform` offsets).

**Where LL helps RB:**
- The chain's `W(V)=155V³+4.13V⁵` as the trial-validated alternative to RB's 10–22% low cubic.
- Grounded `m/I/A_lat/J/Ω/lever` from the real offsets (`basis_hull_offsets.tsv`) that would let RB replace `T·L⁴/64` by real `J` and settle CN 0.4/0.8.
- The per-tier W′/tempo/feather model that RB lacks — the reason RB's sprint topline (9.95 kt, 170 oars, no limit) and LL's burst (7.65 kt, 170 oars, straight drag) differ (the `W′=6.0 kJ` re-anchor).

**What still can't be done with either model:**
- The three gaps are the same through both: t360's floor (turn-specific drag/thrust, not the burst), drift's missing lateral force (not A_lat, not Clarke, not simple heel), and the triple's rate-dependent `E_eff` (blade/timing, not hull). Neither model's sway or yaw physics closes them as written. The investigation's verdict stands: no single heel/damping/area fix closes drift+time without breaking diameters; the triple's remaining fair −0→−3.6% is the rate-dependent blade efficiency.

---

## How to reproduce (same code, same numbers)

```bash
# LL burst and turn (now all through ship.py — hull.py is deleted)
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import equilibrium_speed
from common.chain import KT
for r in [28.8, 32.3, 36.0]:
    print(r, round(equilibrium_speed('Olympias', r, hull=1.0)['V']/KT, 2))
"
python3 -c "
import sys; sys.path.insert(0,'simulation')
from ll.ship import Ship, rate_for_speed, run_turn
from common.chain import KT
s=Ship(rate=rate_for_speed('Olympias',6.0,n_oars=170), helm=('port',1.0)); s.V=6.0*KT; print(round(run_turn(s)['D'],1))
"

# RB powering (trials curve vs Holtrop): see Powering sheet rows 55-71 and VBA Holtrop/Delft — stored in simulation/hl/curves.py as the HL's VSTAR grid (8.540 kt at 44.5 spm, 9.80 at 50 spm, etc.)
```
