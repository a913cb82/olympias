# Playbook: verifying a decoded table against its source equations

Never trust decoded digits directly. Every table we extract (OCR or font route) must be
independently reconstructed from the source's published equations and cross-checked
cell-by-cell. A mismatch flags either an OCR error or a mis-read assumption.

## Steps

### 1. Identify the generating equations from the primary source
Read the surrounding prose (via `decode_shaw.py` / text dump) for the formulas. For Shaw's wave
tables these are Carter 1982 + deep-water dispersion — see `research/lane-2-waves/carter-equations.md`
for the full recipe. Note the *exact* inputs and their definitions from the caption (e.g. W is wind
**relative to the water**, C measured relative to water moving at 0.5 m/s).

### 2. Reconstruct every cell in one script
One-off python (any venv with numpy/math is fine). Loop the table's independent variables, compute
expected H/L/C, apply any caps, print side-by-side with the decoded values:

```bash
cd tools && source /tmp/opencode/venv/bin/activate    # venv stays in /tmp/opencode
python -c "
rows = [  # (fetch, duration, W=4.5:(H,L,C), W=5.0:(...), W=5.5:(...)) from decoded CSV
 (50,3.2, (0.23,4.1,2.5), (0.27,4.7,2.7), (0.30,5.2,2.9)),
 (200,12.6,(0.49,10.1,4.0),(0.60,12.5,4.4),(0.73,15.1,4.9)),
]
for (f,d,*ws) in rows:
    for W,(H,L,C) in zip([4.5,5.0,5.5], ws):
        Hs = 0.0146*d**(5/7)*W**(9/7); Tz = 0.419*d**(3/7)*W**(4/7)
        if Hs > 0.0240*W**2: Hs = 0.0240*W**2; Tz = 0.566*W     # fully-developed cap
        print(f'{f:>4} {d:>4} {W:>5} dec={H}/{L}/{C}  calc={Hs:.2f}/{1.56*Tz**2:.1f}/{1.56*Tz:.2f}')
"
```

### 3. Assess the match
- All cells within printing precision → table confirmed; assumptions validated.
- Systematic bias (e.g. L all ×1.66 off) → wrong period definition (T_m vs T_z) or a wrong cap —
  re-read the prose.
- Isolated mismatches → OCR mis-read of that cell (esp. `5`/`6`, `0`/`9`, dropped `*`). Re-OCR just
  that region or correct against the reconstruction.

### 4. Verify structural relations between tables
E.g. Table 8.4 H/L/C = Table 8.3 × 1.8/1.2/1.1 (Shaw states these factors). Compute ratios for all
cells and confirm they lie in the stated range. This catches whole-table mis-decodes.

### 5. Record the result in the notes
- Mark the open question resolved with `[x]` (e.g. "Shaw used T_z not T_m" — see `carter-equations.md`
  §3, §9).
- Add the reconstruction formula and verdict to the lane note's §10-style section so the derivation
  is replayable.

## Working reference values for Shaw's wave tables
- Duration-limited (always applies for Table 8.3 inputs; fetch-limited branch and caps in
  `carter-equations.md` §2): H_s = 0.0146·D^(5/7)·W^(9/7); T_z = 0.419·D^(3/7)·W^(4/7);
  fully-developed cap H_s = 0.0240·W², T_z = 0.566·W; L = 1.56·T_z²; C = 1.56·T_z.
- Verified spot checks (X, D, W → H, L, C): (50, 3.2, 4.5) → 0.23, 4.1, 2.5;
  (200, 12.6, 5.5) → 0.73, 15.1, 4.9 (capped).
