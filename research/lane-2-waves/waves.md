# Lane 2 — the wave environment & wind propulsion

Research notes for the Olympias trireme reconstruction. Confidence flags:
`[x]` = confirmed from a cited source / verified reproduction; `[?]` =
uncertain/conflicting. Merged 2026-08 from `carter-equations.md` +
`shaw-tables-81-82-wind-propulsion.md` (both former lane files; git history
holds the split).

---

## Part 1 — Carter's wave-prediction equations (reproduction of Shaw's Table 8.3 inputs)

Primary source verified against the full text of the original paper (17-page
PDF obtained from the WaveLab reference archive, USGS GitLab).

### 1.1 Identity of "Carter's equations"

The equations Shaw calls "Carter's equations" are almost certainly those of:

**D. J. T. Carter, 1982, "Prediction of wave height and period for a constant wind velocity using the JONSWAP results", *Ocean Engineering* 9(1), 17–33. DOI 10.1016/0029-8018(82)90042-7** [x]
(also sometimes cited, with altered first word, as "Estimation of wave height and period...").

- Derived from the JONSWAP (Joint North Sea Wave Project, 1969, German Bight off Denmark) results of
  Hasselmann et al. (1973), specifically from the parametric-equation solutions of
  Hasselmann, Ross, Müller & Sell (1976, *J. Phys. Oceanogr.* 6, 200–228) for a **constant wind velocity**.
- Gives H and T as a function of wind speed (U₁₀), fetch (X), **or** duration (D). [x]
- The abstract explicitly says: "used to derive formulae for significant wave height and wave period in terms of
  the wind speed (assumed constant) and fetch or duration." [x]
- NOT the SMB (Sverdrup–Munk–Bretschneider) method per se — but Carter *compares* his fetch-limited heights with
  Bretschneider's SMB formula and finds "good agreement" (see §1.6). The SMB/Bretschneider (1973) and
  Darbyshire (1963) formulas are alternatives/checks, not what "Carter" means. [x]

### 1.2 The equations (Carter 1982, verbatim from original paper, Appendix A & Eqs 15–18)

**Definitions (Carter's own notation):**
| symbol | meaning | unit |
|---|---|---|
| H_s | significant wave height | m |
| T_m | period of the spectral peak | s |
| T_z | zero-up-crossing period | s |
| U | wind speed at 10 m above the sea surface | m/s |
| X | fetch | km |
| D | duration | h |

**Carter's convention:** H_s = 4√m₀ (m₀ = spectral variance), eq. (3) of the paper. [x]

**Fetch-limited case (use when D > criterion of eq. 18)**  [x]
```
H_s = 0.0163 · X^0.5 · U          (15a)
T_m = 0.566  · X^0.3 · U^0.4      (16a)
T_z = 0.439  · X^0.3 · U^0.4      (17a)
```
(verified in paper text; coefficients also reproduced independently by Hsu 2015 (T_m form, called T_p)
and OrcaFlex (T_z form).)

**Duration-limited case**  [x]
```
H_s = 0.0146 · D^(5/7) · U^(9/7)  (15b)
T_m = 0.540  · D^(3/7) · U^(4/7)  (16b)
T_z = 0.419  · D^(3/7) · U^(4/7)  (17b)
```

**Which regime applies (fetch-limited iff):**  [x]
```
D  >  1.167 · X^0.7 · U^−0.4      (18)
```
D in h, X in km, U in m/s. Otherwise use duration-limited (2b). Note: for an open sea such as the Aegean,
fetch-limited (2a) is the natural default for steady wind over a bounded basin.

**Fully developed sea (saturation) limits**  [x]
Beyond the sea/swell boundary (eq. 19) the sea is fully developed; Carter caps the growth as follows
(Appendix A of the paper):
```
H_s = 0.0248 · U^2   (fetch-limited growth cap; from 15a at X = 2.32U²)
H_s = 0.0240 · U^2   (duration-limited cap;   from 15b at D = 2.01U)
T_m = 0.728  · U     (both regimes)
T_z = 0.566  · U     (both regimes)
```
Paper text: "H_s ... = 0.0248U², which is very close to the Pierson–Moskowitz value for a fully-developed
sea of 0.02466U²" [x]. Pierson–Moskowitz (1964) fully developed values given in the paper: PM H_s = 0.02466·U² (eq. 4),
PM T_z = 0.558·U (eq. 8), PM T_m = 0.785·U (eq. 6). Note U is at 10 m; PM spectra are referenced to 19.5 m with
conversion U₁₀ = 0.93·U₁₉.₅. [x]

**Sea/swell boundary (eq. 19)**  [x]
Growing sea (not swell) requires:
```
(a) X ≥ 2.32 · U^2     (fetch-limited regime)
(b) D ≥ 2.01 · U       (duration-limited regime)
```
(equivalently the dimensionless peak frequency ν = U·f_m/g ≥ 0.14). Beyond these, use the caps above.

**Underlying dimensionless forms (Table 1, col. 6–7, Hasselmann 1976 parametric values)**  [x]
Dimensionless fetch ξ = gx/U², dimensionless duration δ = gd/U.
```
Peak frequency  : U·f_m/g = 2.84·ξ^(−1/3)          (fetch);   16.8·δ^(−4/7)        (duration)
Dimensionless H : H_s·g/U² = 1.6×10⁻²·ξ^(0.5)      (fetch);    1.6×10⁻²·δ^(5/7)      (duration)
```
(Table row for dimensionless height is OCR-garbled in the PDF; coefficients shown match the authoritative
published forms above.) [? on exact Table-1 notation, [x] on the resulting equations]

**Equivalence of fetch and duration (constant wind)**  [x]
A duration d_s equivalent to fetch x: d_s ≈ 63.3r, 50.5r, 66.2r depending on which spectral parameter is
equated (r = x^0.7/(g^0.3·U^0.4)); best approximate relation from energy-transport argument:
```
d_s ≈ 60.0 · r   (hours, with x in m, U in m/s)
```

**Spectrum-integrated (non-recommended) forms — do NOT use for prediction**  [x]
Carter warns it "would be a mistake to predict wave height from the spectrum" (eq. 5 gives ~0.7–1.0× the
recommended value). Given for completeness:
```
H_s = 0.02013 · X^0.55 · U^0.90   (eq. 5)   [? exponent on X read as 0.55 from OCR; consistent with R in eq. 20]
T_m = 0.605  · X^0.33 · U^0.33   (eq. 7)
T_z = 0.470  · X^0.33 · U^0.33   (eq. 10)   (T_z = 0.777·T_m, eq. 9)
```

### 1.3 Period-definition ambiguity — critical for reproducing Table 8.3

Carter publishes **two** periods: T_m (spectral peak) and T_z (zero-up-crossing), related by
**T_z = 0.777·T_m**, i.e. **T_m = 1.287·T_z** (eq. 9; for mean JONSWAP γ = 3.3). [x]

Secondary sources confirm the two coefficient sets:
- Hsu (NOAA Mariners Weather Log, Dec 2015) gives T_p = 0.566·X^0.3·U^0.4 and 0.540·D^3/7·U^4/7
  → T_p here ≡ Carter's T_m (spectral peak / "dominant" period). [x]
- OrcaFlex/Orcina docs (after Tucker 1991) give T_z = 0.439·X^0.3·U^0.4 and 0.419·D^3/7·U^4/7
  → ≡ Carter's T_z ("average zero up-crossing period"). [x]
- Both are internally consistent: 0.566/0.439 = 1.289; 0.540/0.419 = 1.289 ≈ 1.287. [x]

**RESOLVED [x]:** Shaw used **T_z (zero-up-crossing period)**, not T_m. Verified by reconstructing
Table 8.3 cell-by-cell from the duration-limited equations (15b/17b) with the fully-developed cap:
all 36 cells of H, L, C match the decoded table to the printed precision. See
`research/data/shaw-table-8.3-significant-waves.csv` and the verification note in Part 1 §1.10.
(Carter text ch.8 defines T as "the time that elapses between successive occasions on which the sea
surface rises above its mean level" — that is precisely the zero-up-crossing period.) The T_m variant
would give L and C larger by 1.66× and 1.29× respectively, which does not match the table.

### 1.4 Deep-water dispersion: L = 1.56·T² and C = 1.56·T  [x]

These are exactly the deep-water gravity-wave relations with g = 9.81 m/s²:
```
C = g·T/(2π) = 1.5614·T ≈ 1.56·T   (m/s)
L = C·T = g·T²/(2π) = 1.5614·T² ≈ 1.56·T²   (m)
```
- Consistency with deep-water dispersion: [x] (exact; ω² = gk, phase speed g/ω).
- Independently stated by Hsu (2015) eq. (9): L_p = (g/2π)·T_p² = 1.56·T_p². [x]
- Also used by Drennan, Taylor & Yelland (2005) and by OrcaFlex. [x]
- Implicit deep-water assumption: applies when water depth d > L/2 (strictly, dispersion ω² = gk·tanh(kd)
  → tanh(kd) ≈ 1 for d > ~L/2). For the Aegean (typical depths 100–2000 m, L ≲ 80 m) deep-water is a good
  approximation for all but very nearshore shallow patches. Carter's own deep-water criterion for the JONSWAP
  data: depth > g/(8π·f_m²) = quarter of the peak wavelength. [x]
- Group velocity (deep water): C_g = C/2 = 0.78·T — this is the speed at which wave *energy* travels and
  underlies the fetch/duration equivalence. [x]

### 1.5 Valid ranges and validity notes  [x]
- JONSWAP data domain: fetch ≤ 160 km; wind speed ≤ 15 m/s (some later measurements to ~20 m/s). [x]
- Deep water only: unaffected by the sea floor (criterion: depth > L_m/4, i.e. depth > g/(8π f_m²)). [x]
- Constant wind velocity, locally generated wind sea (offshore winds). Not for swell or for wind varying
  in time/space. [x]
- Carter notes extrapolation beyond the data range (larger fetch/duration, higher wind) gives heights
  "not dissimilar" from Bretschneider and approaching the Pierson–Moskowitz fully-developed value. [x]

### 1.6 Comparison formulas (for cross-checking Shaw's numbers)

**Bretschneider (1973) — SMB fetch-limited (Carter eq. 22)**  [x]
```
g·h_s/U^2 = 0.283 · tanh{ 0.0125·(g·x/U^2)^0.42 }
```
which reduces (x in m → X in km) to:
```
H_s = 0.0288 · U^2 · tanh{ 0.5935·(X/U^2)^0.40 }   (m, U in m/s, X in km)
```
Carter: agreement with his JONSWAP fetch-limited values is "good", except Bretschneider runs ~1 m higher at
short fetch + very high wind.

**Darbyshire (1963) (Carter eq. 21) — coastal and oceanic forms**  [? on exact converted coefficients]
```
Oceanic: H_s = 0.0132·X_o^0.5·U^0.5   with X_o = X^3 − 5.56X^2 + 223.2X
Coastal: H_s = 0.0630·X_c^0.5·U^0.5   with X_c ≈ 22.24X^2 ± 893X ± 509   (X in km)
```
Carter finds Darbyshire generally does not agree as well with JONSWAP, especially at low wind speeds.
(OCR of the polynomial coefficients is unreliable — treat as [?]; these are only for comparison anyway.)

### 1.7 Example numbers (Aegean-like, fetch-limited, steady wind)

U = 10 m/s, X = 50 km (deep water, duration > 1.167·50^0.7·10^−0.4 ≈ 13 h):
```
H_s = 0.0163·√50·10        ≈ 1.15 m
T_m = 0.566·50^0.3·10^0.4  ≈ 4.58 s
T_z = 0.439·50^0.3·10^0.4  ≈ 3.55 s
L = 1.56·T_z² ≈ 19.7 m (or 1.56·T_m² ≈ 32.7 m)
C = 1.56·T_z  ≈ 5.5 m/s  (or 1.56·T_m  ≈ 7.1 m/s)
```
Fully developed at U = 10 m/s: H_s ≈ 2.48 m, T_z ≈ 5.66 s (L ≈ 50 m), T_m ≈ 7.28 s.
These are the magnitudes Shaw's Table 8.3 should show.

### 1.8 Sources

Primary:
1. [x] **Carter, D. J. T. (1982).** "Prediction of wave height and period for a constant wind velocity using the
   JONSWAP results." *Ocean Engineering* 9(1): 17–33. DOI 10.1016/0029-8018(82)90042-7.
   - Full PDF text verified from: WaveLab reference archive, USGS GitLab —
     code.usgs.gov/wavelab/wavelab (file `documentation/references/Prediction of Wave Height and Period Jonswap.pdf`).
   - Journal page: sciencedirect.com/science/article/pii/0029801882900427.

Corroborating secondary sources (each independently gives the coefficient sets):
2. [x] **Hsu, S. A. (2015).** "Estimating wave height using wind speed during a tropical cyclone."
   *Mariners Weather Log* 59(3), NOAA. vos.noaa.gov/MWL/201512/waveheight.shtml.
   → gives H_s = 0.0163·X^0.5·U₁₀, T_p = 0.566·X^0.3·U₁₀^0.4 (fetch);
   H_s = 0.0146·D^5/7·U₁₀^9/7, T_p = 0.540·D^3/7·U₁₀^4/7 (duration);
   fetch-limited iff D > 1.167·X^0.7·U₁₀^−0.4; and L_p = 1.56·T_p².
3. [x] **Orcina (OrcaFlex documentation),** "Environment: Modelling design waves",
   orcina.com/webhelp/OrcaFlex — gives the same equations with T_z coefficients
   (0.439 fetch, 0.419 duration), after **Tucker, M. J. (1991).** "Waves in ocean engineering."
4. [x] **Hasselmann, K. et al. (1973).** "Measurements of wind-wave growth and swell decay during the Joint North
   Sea Wave Project (JONSWAP)." *Dtsch. Hydrogr. Z.* Suppl. A8(12).
5. [x] **Hasselmann, K., Ross, D. B., Müller, P. & Sell, W. (1976).** "A parametric wave prediction model."
   *J. Phys. Oceanogr.* 6: 200–228.
6. [x] **Pierson, W. J. & Moskowitz, L. (1964).** "A proposed spectral form for fully developed wind seas..."
   *J. Geophys. Res.* 69: 5181–5190.
7. [x] **Bretschneider, C. L. (1973).** "Prediction of waves and currents." Look Lab./Hawaii 3: 1–17.
8. [?] **Darbyshire, J. (1963).** "The one-dimensional wave spectrum in the Atlantic Ocean and in coastal waters."
   In *Ocean Wave Spectra — Proc. Conf.* Prentice-Hall. (converted coefficients uncertain)
9. [x] **Tucker, M. J. & Pitt, E. G. (2001).** *Waves in Ocean Engineering.* Elsevier — cites H_s ≈ 0.024·U² for FDS
   (Carter 1982 attribution), consistent with the caps above.

### 1.9 Open questions — resolved

1. [x] ~~**Period definition in Shaw's Table 8.3**~~ **RESOLVED: T_z.** T_m (peak, 0.566/0.540 set) vs T_z
   (zero-crossing, 0.439/0.419 set). Full Table 8.3 reconstruction (below) confirms T_z.
2. [x] ~~Fetch-limited vs duration-limited choice~~ **RESOLVED: duration-limited.** Shaw's Table 8.3 inputs
   (fetch X ≤ 200 km, duration D ≤ 12.6 h, W ≤ 5.5 m/s) all satisfy D < 1.167·X^0.7·U^−0.4 (e.g. X=200,
   U=5.5: threshold 24.1 h > 12.6 h), so the duration-limited branch (15b/17b) always applies; the
   duration-limited fully-developed cap (0.0240·U², T_z = 0.566·U) is reached at the asterisked cells.
3. [x] ~~Wind-speed reference height~~ **RESOLVED for Shaw's use:** Table 8.3's W is explicitly "the
   windspeed in m/s relative to the water" = true wind − 0.5 m/s favourable current (Shaw assumes a
   0.5 m/s (1 knot) current; C is likewise measured relative to the moving water). Shaw's W values
   (4.5/5.0/5.5) therefore correspond to true winds 5.0/5.5/6.0 m/s. Whether U should be treated as U₁₀
   or adjusted to another height is a separate, small effect.
4. [x] L = 1.56·T² and C = 1.56·T are confirmed as deep-water dispersion with g = 9.81 — no issue, provided the
   deep-water condition holds (fine in the Aegean away from shore).
5. [x] ~~Whether Shaw capped heights at the fully developed limit~~ **RESOLVED: yes.** Asterisked cells equal
   exactly the duration-limited caps H_s = 0.0240·U² (T_z = 0.566·U); see the Table 8.3 reconstruction.

### 1.10 Table 8.3 reconstruction & verification (Shaw 2012 p.72)

Full verification against `research/data/shaw-table-8.3-significant-waves.csv` (12 rows × 3 windspeeds):
- For each (fetch X km, duration D h, wind-relative-to-water W m/s) compute duration-limited values,
  then apply the fully-developed cap if exceeded:
```
H_s = 0.0146 · D^(5/7) · W^(9/7)          if H_s > 0.0240·W²:  H_s = 0.0240·W²
T_z = 0.419  · D^(3/7) · W^(4/7)          if capped:           T_z = 0.566·W
L   = 1.56 · T_z²
C   = 1.56 · T_z
```
- All 36 cells match the decoded table to the printed precision (e.g. X=50,D=3.2,W=4.5 →
  H=0.23, L=4.1, C=2.5; X=200,D=12.6,W=5.5 → capped H=0.73, L=15.1, C=4.9). Full H/L/C match table.
- Table 8.4 (3-hour waves) = Table 8.3 × {1.8, 1.2, 1.1} for H, L, C respectively (ratios verified 1.78–1.83,
  1.21–1.22, 1.07–1.12 across all 36 cells — consistent with Shaw's stated factors). Worked example in text:
  8.5 m/s wind at 200 km/12.6 h → 3-hour height 2.5 m, λ ≈ 34 m (Table 8.4) vs significant height ~1.4 m,
  λ ≈ 28 m (would-be Table 8.3 value).

### 1.11 Bottom line

Carter's equations (fetch-limited, U₁₀ at 10 m, X in km):
```
H_s = 0.0163 · X^0.5 · U        (m)
T   = 0.566  · X^0.3 · U^0.4    (m, s)   [T_m/peak]   or   T = 0.439·X^0.3·U^0.4  [T_z]
L   = 1.56 · T²                 (m)      [deep water]
C   = 1.56 · T                  (m/s)    [deep water]
```
Fully developed cap: H_s = 0.0248·U². These reproduce Carter's own examples and agree with two independent
secondary sources. **Shaw's Table 8.3 uses the duration-limited branch with T_z (zero-up-crossing) period
and the duration-limited cap H_s = 0.0240·U² — all 36 cells verified, see §1.10.**

---

## Part 2 — Shaw Tables 8.1 & 8.2 (wind propulsion): exact decoded values

Source: Rankov 2012 ch.8, book p.71 (PDF page 83). Text-layer glyphs are PUA (TT291/TT292/TT293)
and unmatchable by the DejaVu EDT matcher; tables were recovered by OCR (easyocr) of 6× page renders
(`../tools/decode_shaw.py` prints the region). Every cell is cross-checked against the equations in
the prose, so values are certain [x].

### 2.1 Table 8.1 — effect of a following wind on the oarsmen's burden

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

### 2.2 Table 8.2 — direction of the apparent wind for a following wind

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
- Consequence: the apparent wind is always well abaft the beam; even 10 m/s astern wind makes the
  apparent wind only 66° off the course. This bounds how far the sails can draw the ship off the
  true-wind line (the course-offset/leeway input).
- CSV: `research/data/shaw-table-8.2-apparent-wind.csv`.

### 2.3 Method note (for reuse)

- Text-layer decode (`../tools/decode_shaw.py`) resolves prose and captions but leaves table numerals as
  unmapped PUA glyphs (the subset Type0 TT fonts embed a different glyph set than the DejaVu reference).
- Reliable route: `pymupdf` render page 83 at zoom ~6 → OCR each table region with easyocr (`.venv`
  at the repo root for pymupdf; the on-demand OCR venv — see `research/tasks/AGENTS.md`); pin down
  columns by OCR'd header text and
  **verify every cell against the prose equation** — that turns OCR-suspect values into certain ones.
- Both tables required equation-driven verification because row/column boundaries are ambiguous in
  raw OCR output (e.g. Table 8.2's leftmost header cells 6 and 7 were missed by OCR; the equation
  fit confirms them).
