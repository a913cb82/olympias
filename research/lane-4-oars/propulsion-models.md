# Lane 4 — Oar propulsion model (W3): speed→power chain, verified against Shaw

Reference implementation: `research/lane-4-oars/lane4_propulsion.py` (pure stdlib, runnable). All numbers
below are produced by that script and reproduce Shaw 2012 (Rankov, *Trireme Olympias: The Final
Report*) to the precision shown. This is the engine-to-propeller chain that the simulation will use.

## 1. The chain (equations)

Hull effective propulsive power (Olympias, rudders partly raised): **W = 155·V³ + 4.13·V⁵**, V m/s.
Mark IIa/IIb hulls: **×1.08** (greater length & displacement). `[x]`

Oar power balance (Shaw ch.9): **W = n·P·L·r·E/60**, where
- n = rowers in action
- P = mean pull at the butt (N), assumed ∝ rate: **P = 7.43·r**
- L = effective pull length at the butt (m): Olympias 0.89, Mark IIa 0.87, Mark IIb 0.99
- r = rate of striking (spm)
- E = mean ideal oar efficiency: Olympias full 0.756, two-level 0.719, sprint ~0.730, **Mark II 0.780**

Inverting (solve for r at target speed): r² = W·60 / (n·7.43·L·E).

Per-oarsman gross mechanical power = handle power + oar losses:
**gross = P·L·r/60 + (0.96·r + 0.016·r²)**, where 0.96r+0.016r² = power absorbed by the oar
(inertia + blade losses; Shaw ch.7). `[x]`

## 2. Verification — ch.9 sprint validation (the clean experiment/theory match)

- Calibration trial: 116 rowers, 6.8 kt (3.50 m/s), W = 12,100 W (rudders down, tailwind 4–5 kt),
  r = 38.75 spm, E = 0.719 → model gives **P = 288 N (64.7 lbf)**, implying k = P/r = 7.43. ✓ Shaw: 288 N.
- Four-run sprint: ~130 effective rowers, 44.5 spm, E = 0.730:
  W = 130·0.78·7.43·44.5²·0.730/60 = **18,152 W** → **4.284 m/s = 8.32 kts**.
  Measured: 8.2–8.3 kts. **Prediction matches experiment.** `[x]`

## 3. Verification — ch.9 Table 9.7 (Mark II rates of striking)

| design | V kt | W (W) | L (m) | r (spm) | P (N) | P (lbf) | P·r | r² |
|---|---|---|---|---|---|---|---|---|
| IIa | 7.5 | 13,462 | 0.87 | **30.7** | **228** | 51.3 | 7,002 | 942 |
| IIa | 9.7 | 34,693 | 0.87 | **49.3** | **366** | 82.3 | 18,044 | 2,429 |
| IIb | 7.5 | 13,462 | 0.99 | **28.8** | **214** | 48.1 | 6,153 | 828 |
| IIb | 9.7 | 34,693 | 0.99 | **46.2** | **343** | 77.2 | 15,857 | 2,134 |

Shaw (Table 9.7): IIa r = 30.7/49.4, P = 228/367 N; IIb r = 28.8/46.3, P = 214/344 N. W = 13,460/34,860.
Agreement to within rounding of the OCR'd table digits (1 spm ≈ 0.1, P within 1–2 N). `[x]`

## 4. Verification — ch.7 cruise rates (Mark II, E=0.78, n=170, L=0.99)

| V kt | W (W) | r (spm) | P (N) | handle (W) | oar_abs (W) | gross (W) | Shaw r / gross |
|---|---|---|---|---|---|---|---|
| 7.0 | 10,544 | **25.5** | 189 | 79.5 | 34.8 | 114 | 25.5 / 115 |
| 7.5 | 13,462 | **28.8** | 214 | 101.5 | 40.9 | 142 | 28.8 / 145 |
| 8.0 | 16,978 | **32.3** | 240 | 128.0 | 47.7 | 176 | 32.3 / 180 |

Rates of striking reproduce Shaw exactly. Gross per-man power: model 114/142/176 W vs Shaw
115/145/180 W (he quotes "to the nearest 5 W"). The last two are 2–4 W higher in Shaw than the
model; likely his intermediate rounding, **flag for uncertainty register** (small, ~2%). `[x]`

## 5. Verification — S6 cross-check (independent of Shaw's ch.7/9 power law)

Olympias ~7.2 kt, 170 men: W = 10,782 W → **63 W/man propulsive** (S6 quoted ~62 W);
oar-system efficiency 63/115 ≈ **55%** (S6 quoted ~54%). Agreement. `[x]`

## 6. Notes for the simulation

- Use **W_hull = 1.08·(155V³+4.13V⁵)** for Mark II (or 1.0 for Olympias) as the primary
  speed→power map. It is validated at 8.32 vs 8.2–8.3 kts measured.
- Use **P = 7.43·r** and **W = n·P·L·r·E/60** to convert crew effort → speed. E = 0.78 (Mark II)
  or 0.756/0.719 (Olympias, full / two levels).
- The **44.5-spm sprint → 8.3 kts** prediction is the Lane-6 cross-check target.
- Gross mechanical power per man: **114 W @ 7 kt, 142 W @ 7.5 kt, 176 W @ 8 kt** (model; Shaw
  115/145/180). Compare against S5/S6 sustainable-power envelope (80 W fixed-seat / 115–145 W
  ordinary-labourer long-endurance) to assess feasibility of the Heraclea passage.

## 7. Sources
- Shaw (2012) ch.7 (pp.63–67) and ch.9 (pp.76–81) in Rankov (ed.) *Trireme Olympias: The Final Report*.
- Lane-1 read note: `research/lane-1-read/shaw-ch7-ch9-2024.md`.
- OCR artifacts: `research/data/t91_t92_ocr.txt`, `t96_ocr.txt`, `t97_ocr.txt`.
- S5/S6 (physiology): main research md §§S5–S6.
