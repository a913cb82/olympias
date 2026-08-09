# Shaw Tables 8.1 & 8.2 (wind propulsion): exact decoded values

Lane 2 / W4, Olympias trireme reconstruction — research notes.
Source: Rankov 2012 ch.8, book p.71 (PDF page 83). Text-layer glyphs are PUA (TT291/TT292/TT293)
and unmatchable by the DejaVu EDT matcher; tables were recovered by OCR (easyocr) of 6× page renders
(`tools/decode_shaw.py` prints the region; renders `/tmp/opencode/p84_tables_6x.png`). Every cell is
cross-checked against the equations in the prose, so values are certain [x].

---

## Table 8.1 — effect of a following wind on the oarsmen's burden

Column heads (OCR): "True speed of tailwind (m/s) | Relative speed of tailwind (m/s) |
Propulsive force of the sails as a percentage of that required to maintain the ship's speed at
7.5 knots (3.9 m/s) | Balance to be provided by the oars (percent)".

| True tailwind V (m/s) | Relative wind (m/s) | Sail force X (%) | Oar balance (%) |
|---|---|---|---|
| 5.0  | 0.6 | 2   | 98 |
| 5.5  | 1.1 | 6   | 94 |
| 6.0  | 1.6 | 12  | 88 |
| 7.0  | 2.6 | 32  | 68 |
| 8.0  | 3.6 | 61  | 39 |
| 9.0  | 4.6 | 100 | 0  |

- Relative wind = V − 4.4 m/s, where 4.4 = ship 3.9 m/s (7.5 kt) + 0.5 m/s (1 kt) favourable current.
- **Verified [x]:** every X = 100·((V−4.4)/4.6)² to the printed integer:
  V=5 → 1.7 (2), 5.5 → 5.7 (6), 6 → 12.1 (12), 7 → 32.0 (32), 8 → 61.2 (61), 9 → 100.0 (100).
  Oar balance = 100 − X (printed 98/94/88/68/39/0).
- Table 8.1 demonstrates: with a following wind the *relative* wind is small, so the sails help
  surprisingly little — ~2% of the oarsmen's burden at 5 m/s true wind; 12% at 6 m/s; ~1/3 at 7 m/s.
- CSV: `research/data/shaw-table-8.1-sail-force.csv`.

## Table 8.2 — direction of the apparent wind for a following wind

Column heads (OCR): "True wind speed (m/s)" | "Apparent wind direction, degrees from the ship's
course". The ship is moving at 4.4 m/s (8.5 kt) past the land; the wind blows from astern.

| True wind V (m/s) | Apparent wind direction from course (deg) |
|---|---|
| 6  | 53.7 |
| 7  | 57.8 |
| 8  | 61.2 |
| 9  | 63.9 |
| 10 | 66.3 |

- **Verified [x]:** apparent-wind angle = atan(V / 4.4) exactly:
  atan(6/4.4)=53.7°, atan(7/4.4)=57.8°, atan(8/4.4)=61.2°, atan(9/4.4)=63.9°, atan(10/4.4)=66.3°.
- Consequence (used in main doc): the apparent wind is always well abaft the beam; even 10 m/s astern
  wind makes the apparent wind only 66° off the course. This bounds how far the sails can draw the
  ship off the true-wind line, and is the input for the course-offset/leeway reasoning in S7.
- CSV: `research/data/shaw-table-8.2-apparent-wind.csv`.

---

## Method note (for reuse)

- Text-layer decode (`tools/decode_shaw.py`) resolves prose and captions but leaves table numerals as
  unmapped PUA glyphs (the subset Type0 TT fonts embed a different glyph set than the DejaVu reference).
- Reliable route: `pymupdf` render page 83 at zoom ~6 → OCR each table region with easyocr (the
  `research-venv` + `venv` pair in `/tmp/opencode`); pin down columns by OCR'd header text and
  **verify every cell against the prose equation** — that turns OCR-suspect values into certain ones.
- Both tables required equation-driven verification because row/column boundaries are ambiguous in
  raw OCR output (e.g. Table 8.2's leftmost header cells 6 and 7 were missed by OCR; the equation
  fit confirms them).
