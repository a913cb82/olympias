# Playbook: quick clean text extraction from a PDF

Use this when the PDF text extracts fine (no subset/custom fonts in the region of interest).
For Rankov 2012 chapter prose this is often all you need; the PUA/subset fonts only appear in
specific tables and some headers.

## One-shot text dump

```bash
cd ../tools
source ../../.venv/bin/activate   # repo-local venv (from research/tasks/)
python -c "
import pymupdf
doc = pymupdf.open('../../sources/rankov2012.pdf')
for pno in range(82, 88):                    # book pp.70-76
    print(f'\n===== PDF PAGE {pno} =====')
    print(doc[pno].get_text())
"
```

`rankov2012.txt` (already produced) is the full-document dump with `===== PAGE n =====` markers —
grep it directly before re-extracting:

```bash
grep -n "PAGE 244" ../../sources/rankov2012.txt    # Taylor ch.31 table page
```

## Page-number mapping (Rankov 2012)
PDF page index (0-based) = printed book page + 12. Check the running header
(`decode_shaw.py <page>` prints the header line, e.g. `y=44.8 'Timothy Shaw' / '72'`).

## Rendering a page image (for OCR or eyeball)
```bash
source ../../.venv/bin/activate   # repo-local venv (from research/tasks/)
python -c "
import pymupdf
doc = pymupdf.open('../../sources/rankov2012.pdf')
page = doc[84]
pix = page.get_pixmap(matrix=pymupdf.Matrix(6,6))     # 6x full page
pix.save('p84_6x.png')
# or a cropped region:
pix = page.get_pixmap(matrix=pymupdf.Matrix(8,8), clip=pymupdf.Rect(40,96,540,185))
pix.save('t83_table_8x.png')
"
```

## Gotchas
- `get_text()` on a page mixing prose + subset fonts returns `?`/PUA for the table glyphs; the
  prose columns are still clean.
- Don't trust the PDF's own page labels — verify with the running header text.
- Text dump and renders go in `research/sources/` / `research/tools/` (repo-relative); copy
  needed pages/values into notes.
