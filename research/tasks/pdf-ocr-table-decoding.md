# Playbook: extracting numbers from PDF tables (OCR route)

Applies when the table's body text is rendered with custom/subset fonts so that
`page.get_text()` returns PUA chars or `?` (e.g. Rankov 2012 Tables 8.1–8.4, 31.1).
The robust route is **render the table region at high resolution, then OCR with easyocr**.

## The working recipe

### 1. Render the table region (use `research-venv`, it has pymupdf)

Find the PDF page (remember: Rankov book page + 12 = PDF page index). Then render a
tight crop around the table at 8x with a clip rect:

```bash
cd tools
source ../.venv/bin/activate   # repo-local venv (from tools/)
python -c "
import pymupdf
doc = pymupdf.open('../sources/rankov2012.pdf')
page = doc[84]                      # book p.72, Table 8.3
pix = page.get_pixmap(matrix=pymupdf.Matrix(8,8),
                      clip=pymupdf.Rect(40, 96, 540, 185))   # x0,y0,x1,y1 in 1x page pts
pix.save('tools/t83_table_8x.png')
print('saved', pix.width, pix.height)
"
```

Tips for the clip rect:
- First run `python decode_shaw.py <page>` (text route) or `get_text('dict')` to find the table's
  y-range from the caption's y coordinate. Table 8.x bodies on p.72–73 sit in y≈96–185.
- **Caption-search method (ch.9 tables, book pp.76–81)**: the caption *is* in the readable text layer
  even when the body is garbled, so locate it with `page.search_for('Duration of the effective pull')`
  → get its y, then crop from ~10 pt below it. (Captions OCR as `Lable 9.0.`/`able 9.6.` in easyocr —
  the leading "T" is dropped; search the original string in the PDF, not the OCR.)
- If the crop is too tight, widen it; OCR is tolerant of extra text but not of clipped digits.
- 8x is a good balance; 6x also works. Very small digits benefit from 10x.

### 2. OCR it (use `venv`, it has easyocr + torch)

```bash
cd tools
source ../.venv-ocr/bin/activate   # on-demand OCR venv (recipe in tasks/AGENTS.md)
python -c "
import easyocr
reader = easyocr.Reader(['en'], gpu=False, verbose=False)
res = reader.readtext('t83_table_8x.png', detail=1, paragraph=False)
res.sort(key=lambda r:(round(r[0][0][1]/20), r[0][0][0]))   # row-major order
for box, txt, conf in res:
    print(f'[{int(box[0][0]):5},{int(box[0][1]):5}] {txt!r} {conf:.2f}')
"
```

### 3. Recover the table layout

OCR returns boxes sorted into rough rows; use the x-centre to assign columns.
Table 8.x structure: `Fetch (km) | Duration (hours)` then, per windspeed W,
three columns `H  L  C`. Each data row is `fetch, duration, {W=4.5: H L C}, {W=5.0: H L C}, {W=5.5: H L C}`.

## Known gotchas (learned the hard way)

- **The `?` glyphs from `decode_shaw.py` are expected for table bodies** — don't fight the font;
  OCR is the right tool here. `decode_shaw.py` only handles the prose (subset-TT text), and returns
  `'?'` for the numeric table font.
- **Two venvs**: `venv` (easyocr) and `research-venv` (pymupdf) are disjoint. Render then OCR in
  two steps, activating each venv. Importing pymupdf inside `venv` fails; importing easyocr inside
  `research-venv` fails.
- **Confidence flags are lower for rows of pure digits** (esp. `5`/`6` and `0`/`9`). Cross-check every
  cell against the source equations (see [verify-decoded-tables.md](verify-decoded-tables.md)) — a
  mismatch pinpoints OCR errors (e.g. `0.30` read as `0.3`, `5.2` vs `5.1`).
- **Full-page OCR times out / returns nothing** (easyocr on a 4763×6736 render exceeds 2 min and
  often yields zero boxes) — always crop to the table region, never OCR a whole page.
- **Long label cells can pull the header off-row**: in Table 9.7 the row `Duration of run, sec` lost
  its header row in OCR; the numeric columns still align. Reconstruct row headers from the prose
  when OCR mislabels (e.g. `Therefore nPr` is really `Pr` = P·r, and `therefore ×2` is `r²`).
- **Asterisks**: the tables mark fully-developed-sea cells with `*` (e.g. `0.49*`). easyocr sometimes
  drops the `*`; recover it from the verification pass (asterisked H equals the fully-developed cap).
- Column header glyphs (`H L C`, `W = 4.5 m/s`) OCR fine; the sub-header row may come out as one
  merged box per cell — acceptable, don't over-polish.
- Renders and OCR crops go in `tools/` (from repo root; `.cache/` inside `tools/` is gitignored) as
  scratch; **promote the clean CSV to
  `research/data/`** when done (see step 4).

## 4. Deliverable

Write a clean, commented CSV to `research/data/` (see existing examples:
`shaw-table-8.3-significant-waves.csv`, `shaw-table-8.4-three-hour-waves.csv`), including
source page, decode method, and the `*` (full-development) flag column.

## Reference values (already verified)

- Table 8.3 (book p.72): significant H, mean L, mean C vs fetch × duration × W∈{4.5, 5.0, 5.5} m/s.
- Table 8.4 (book p.73): "3-hour" H = Table 8.3 H × 1.8; L × 1.2; C × 1.1.
- Worked example (p.72–73): 8.5 m/s wind at 200 km / 12.6 h → significant H ≈ 1.4 m, λ ≈ 28 m;
  3-hour height ≈ 2.5 m, λ ≈ 34 m.
- W is wind **relative to the water** = true wind − 0.5 m/s (favourable current).
- Tables 9.1/9.2 (book pp.76–77): oar dimensions (lengths, horizontal projections in brackets) and
  interscalmium/chord-of-pull. Tables 9.6/9.7 (book pp.80–81): duration of pull; rates of striking.
  Verified against W = 170·P·L·r·0.78/60 and W = 1.08(155V³+4.13V⁵); OCR in
  `research/data/t91_t92_ocr.txt`, `t96_ocr.txt`, `t97_ocr.txt`.
