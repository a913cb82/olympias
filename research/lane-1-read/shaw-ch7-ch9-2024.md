# Lane 1 read note — Shaw, ch.7 "From the Golden Horn to Heraclea" & ch.9 "Towards a Revised Design of a Greek Trireme... a Long Stroke" (Rankov 2012)

Read from `../sources/rankov2012.txt` (book pp.63–67 = ch.7, pp.68–75 = ch.8 Wind & Waves, pp.76–81 = ch.9). These papers are the numerical core of the oar-propulsion lane: they contain the speed–power law, the human-power model, and the oar-efficiency/geometry data used in all Mark II design tables. (Ch.8's wave tables were decoded separately — see S7 and `lane-2-waves/carter-equations.md`.)

**Conventions**: cubit values (0.444 m Olympias, 0.49 m Mark II); "in plan" = horizontal projection = actual × cos 30° (oars inclined 30° to horizontal); page numbers are book pages. **Page-mapping**: txt PAGE line number = book page + 13.

---

## Ch.7 — From the Golden Horn to Heraclea (book pp.63–67)

Task: does Xenophon's *Anabasis* 6.4.2 ("a long day under oar" from Byzantium to Heraclea) fit physical possibility? 129 sea miles (incl. 16.4 n.m. Bosporus) under oar alone.

### Voyage numbers
- Bosporus: 16.4 n.m. (strong currents/eddies — see Table 7.1; sailing time 5 h 30 m to 8 h, with rest).
- Black Sea leg: **113 n.m.** (210 km), SW/WSW course from the Bosporus mouth to Heraclea (Eregli). `[x]`
- Total: **~129 n.m.** in a "long day".
- "Long day" interpreted as **14–16½ h** (summer), not 24 h. `[x]`
- Speeds under oar (relative to water): **7, 7.5, 8 kts**. At 129 n.m. + current: durations **17 h 50 m / 16 h 50 m / 15 h 50 m** including 1 h rest — all fit "a long day". `[x]` (Table 7.3)
- Assumed helpful current **0.5 m/s** (Black Sea anticlockwise coastal current, 0.25–0.75 kts) — the EB (Eastern Balkans?) value used in his durations. `[x]` (Table 7.4)

### Environment (Black Sea coast, spring–autumn)
- Wind: prevailing NE; **>50% of observations wave height ≤0.5 m** in spring/autumn, >64% in summer; **≤2.5 m in <10%** of obs. `[x]` (Table 7.2)
- Swell: mostly NW/NE; ~50% ≤1 m; occasional ≥2 m. `[x]`
- Air temp 25–30 °C max daily; relative humidity morning ~85% → afternoon ~70%. `[x]`
- → Sea "smooth or slight" the majority of days; passage feasible without sail. `[x]`

### Power model (the key equations)
- Hull resistance / required power (Olympias, rudders partly raised): **W = 155·V³ + 4.13·V⁵** (V in m/s, W in watts). `[x]` — same law as ch.9.
- Oar absorbed power per equation (rates of striking table): **oar power absorbed = 0.96·r + 0.016·r²** (r in spm). `[x]`
- Given W and power/oar → rates of striking required at cruise: `[x]`

| speed | rate r (spm) | gross power/oarsman |
|---|---|---|
| 7.0 kts | **25.5** | 115 W |
| 7.5 kts | **28.8** | 145 W |
| 8.0 kts | **32.3** | 180 W |

- Mean ideal oar efficiency used: **0.78**. `[x]`
- Appendix (ch.7): rates computed from **n·P·r·L·E/60 = 1.08·(155V³ + 4.13V⁵)** with n = 170, P = 7.43r, L = 0.99 m, E = 0.78 (Mark II design values; +8% power for length/displacement). `[x]`

### Conclusions (ch.7)
- 7.5 kts @ 28.8 spm ≈ 145 W/oarsman sustained for 16–17 h is at/above the limit for ordinary crews; a *good* crew at 7 kts (115 W) is comfortable. `[x]`
- Sail impossible: >7 kts ship speed needs wind strong enough to build seas too great for rowing or the hull. `[x]`
- → Xenophon's passage requires a trireme **capable of sustained 7–8 kts under oar** — a necessary authenticity criterion for any reconstruction. `[x]`

---

## Ch.9 — Towards a Revised Design: advantages of a long stroke (book pp.76–81)

Claim: Olympias's stroke is too short to cruise at 7–8 kts sustainably. Fix = Mark IIa (0.98 m interscalmium, straight rig) and Mark IIb (**canting/skewing the rig by 18.4°**, tan = 1/3) for a longer chord. This is the design the second edition / Mark II tables are based on.

### Oar geometry (Table 9.1, verified) — lengths in m; (brackets = horizontal projection = ×cos 30°)
| | Olympias | Mark IIa / IIb |
|---|---|---|
| cubit | 0.444 m | 0.49 m |
| length overall | 4.218 (3.653) | 4.655 (4.031) |
| length outboard | 3.113 (2.696) | 3.430 (2.970) |
| length of blade | 0.550 (0.476) | 0.550 (0.476) |
| length inboard | 1.105 (0.957) | 1.225 (1.061) |
| thole→neck | 2.563 (2.220) | 2.880 (2.494) |

- Olympias inboard: 3 ft 7–8 in ≈ **1.105 m**, outboard:inboard = **2.817**. `[x]`
- Mark II: 9½-cubit oars, **7 cubits out / 2½ cubits in** → ratio **2.80**; 2½ cubits (0.49 m) = 4 ft 0.2 in. `[x]`
- Ratios verified: 4.218 = 9.5×0.444 ✓; 4.655 = 9.5×0.49 ✓; projections = ×cos 30° ✓.

### Stroke model (Table 9.2)
| | Interscalmium (m) | Chord between deadpoints (m) |
|---|---|---|
| Olympias | 0.89 | 0.89 |
| Mark IIa | 0.98 | 0.98 |
| Mark IIb | 0.98 | **1.10** |

- The 1.10 m chord of Mark IIb is the whole point of the 18.4° skew — a longer effective chord **without** increasing interscalmium (which would weaken the hull). `[x]`
- Effective sweep angle: Olympias ~48.1° (only with exceptional effort); Mark IIb larger. `[x]`

### Oar efficiency / advance model (the maths)
- Plan geometry: blade center-of-pressure distance q from the instantaneous turning point; oar effective outboard lever p = L − d (L = outboard length in plan). `[x]`
- d (distance tip→turning point) varies as a sine through the stroke: **d = 0.953·sin[120·(C−A)/B + 30°]** (C = instantaneous angle of attack, A = angle at catch, B = sweep). `[x]`
- Differential advance per differential angle: **ds = (L − d)·dC / sin C**; summed from C=A to A+B. `[x]` (Fig. 9.1)
- **Mean ideal efficiency E = 1 / (1 + q/p)**. `[x]`
  - Olympias full crew (3 levels, n≈170): **E = 0.756**
  - 2 levels only (n=116): **E = 0.719**
  - Sprint with ~130 effective: **E = 0.730**
  - Mark II design value used throughout: **E = 0.780**
- q/p scaling: thrust/oar ∝ 1/n → q/p ∝ 1/√n; 170→116 raises q/p ×1.21. `[x]`

### Power & rates (Tables 9.6, 9.7, verified)
Power equation: **W = n·P·L·r·E/60** (P = mean pull at butt N, L = effective pull length at butt m, r = spm). `[x]`

- Olympias sprint trial: 116 rowers, 6.8 kts (3.50 m/s), W=12,100 W, r=38.75 spm, E=0.719 → **P = 288 N (64.7 lbf)**. `[x]`
- Mean pull assumed ∝ rate: **P = 7.43·r**. `[x]`
- Validation vs 4 sprint runs (44.5 spm, ~130 rowers, E=0.730): predicted **18,152 W → 4.285 m/s = 8.32 kts**; measured 8.2–8.3 kts. **Theory matches experiment.** `[x]`
- **Table 9.6 — duration of effective pull (s)**: Olympias 0.428 (7.5 kt) / 0.392 (8.2 kt); Mark IIa 0.512 / 0.469 / 0.396 (9.7 kt); Mark IIb 0.612 / 0.560 / 0.472. `[x]`
- **Table 9.7 — rates of striking etc. at 7.5 & 9.7 kts** (Mark IIa / IIb): `[x]`
  - W: 13,460 W (7.5 kt) / 34,860 W (9.7 kt) — same for both (W=1.08·(155V³+4.13V⁵)).
  - Effective pull length L: IIa **0.87 m**, IIb **0.99 m**.
  - E = 0.780.
  - r: IIa **30.7 / 49.4 spm**; IIb **28.8 / 46.3 spm**.
  - P: IIa **228 / 367 N** (51.3 / 82.5 lbf); IIb **214 / 344 N** (48.1 / 77.3 lbf).
  - Rhythm factor (cycle/pull): IIa 3.82 / 3.07; IIb 3.40 / 2.75. Duration of run: IIa 1.44 / 0.819 s; IIb 1.47 / 0.824 s.
- All rows verified against W = 170·P·L·r·0.78/60 and W = 1.08(155V³+4.13V⁵): IIa 7.5 kt: 170·228·0.87·30.7·0.78/60 = 13,458 W ≈ 13,460 ✓; 9.7 kt: 34,858 ✓. IIb: 13,484/34,847 ✓. (See OCR files `research/data/t91_t92_ocr.txt`, `t96_ocr.txt`, `t97_ocr.txt`.)

### Design conclusions (ch.9)
- Mark IIa requires higher rates, heavier pulls, and higher rhythm factors than Mark IIb → "artificial" feel; fixed-seat rhythm factors tend to be lower than on slides. `[x]`
- Mark IIb (canted rig, 18.4°, tan=1/3) with L=0.99 m stroke gives a more normal fixed-seat rhythm at both cruise and sprint; **the case for Mark IIb over IIa is strong**. `[x]`
- Oxford Olympic VIII 1960 (long slides): rhythm factors ~2.7 at 35 spm — context for fixed-seat values 2.75–3.82. `[x]`

---

## Implications for the simulation (Lanes 3/4/6)

1. **Hull power law**: use W = 155V³ + 4.13V⁵ (V m/s) for Olympias; **×1.08 for Mark II** hulls. This is the primary validated speed→power map (8.32 vs 8.2–8.3 kts measured). `[x]`
2. **Human engine**: P = 7.43·r N at the butt; W_man = P·L·r/60·E. At cruise 7.5 kt/28.8 spm → 145 W/oarsman gross. Sustainable ~115–145 W for many hours. `[x]`
3. **Oar efficiency**: E depends on number of active rowers and geometry: 0.756 (full) / 0.719 (2 levels) / 0.780 (Mark II design). Use the Mark II 0.78 in the model. `[x]`
4. **Stroke geometry**: effective pull length at butt L = 0.89 m (Olympias), 0.87 m (IIa), 0.99 m (IIb); duration of pull (s) scales with L and speed (Table 9.6). `[x]`
5. **Cross-check target**: at 44.5 spm the model must reproduce ~8.3 kts for a 130-rower, 3-level sprint (the one clean experiment/theory validation in the whole literature). `[x]`

## Sources
- Shaw, J.T. (2012) "From the Golden Horn to Heraclea" (ch.7, book pp.63–67) and "Towards a Revised Design of a Greek Trireme of the Fourth Century BC: advantages of a long stroke" (ch.9, book pp.76–81), in Rankov (ed.) *Trireme Olympias: The Final Report*. Oxbow.
- OCR artifacts: `research/data/t91_t92_ocr.txt` (Tables 9.1/9.2), `research/data/t96_ocr.txt` (Table 9.6), `research/data/t97_ocr.txt` (Table 9.7).
