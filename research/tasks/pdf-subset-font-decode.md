# Playbook: decoding subset-font prose from a PDF (glyph-matching route)

Applies when a PDF embeds **subset TrueType fonts** whose cmap is stripped, so ordinary
text extraction (`get_text()`) returns PUA codepoints (U+F000…) or `?`. We decode the prose
(general text) by raster-matching each embedded glyph against a reference font (DejaVu).
**This route is for running prose only — use OCR for tables** (see
[pdf-ocr-table-decoding.md](pdf-ocr-table-decoding.md)).

## The tool

`/tmp/opencode/decode_shaw.py` — the working decoder. It:
1. Opens `rankov2012.pdf` (path baked in at `DOC`).
2. For each requested page, extracts embedded subset TT fonts (names starting `TT…`).
3. Renders each PUA glyph (0xF000–0xF0FF) as a small 18×22 mask via `ft2font`, and matches it by
   chamfer/EDT distance against DejaVu reference masks (`REF_CHARS`).
4. Falls back to `' '` for blank glyphs and `'?'` for no-match; caches per-font mappings in
   `glyph_map3.json` keyed by font SHA-1.

Run it with PDF page indices (0-based, == book page + 12 for Rankov):

```bash
cd /tmp/opencode
source research-venv/bin/activate        # needs pymupdf, numpy, PIL, scipy, matplotlib
python decode_shaw.py 84 85              # print decoded text for book pp.72–73
python decode_shaw.py 84 | grep -vE "'\?\?\?+'"   # hide the undecodable table cells
```

## Interpreting the output

Each line: `y=<baseline> x=<bbox-x> 'text'` — left-to-right sorted spans per line, y ascending.
- Prose decodes cleanly; **table numbers come back as runs of `'?'`** — that's the numeric
  subset font, which this tool does not cover (use OCR).
- A lone `'???'`-free line with `y` just above the caption (e.g. y=77.4 on p.84) is the table
  caption — note its y to build the OCR clip rect.

## Extending / when to re-match a font

- New font not in cache: `classify_font()` runs automatically and appends to `glyph_map3.json`.
- If matches are wrong, raise/lower the acceptance threshold (`< 1.6` in `classify_font`):
  higher = more matches but more errors; lower = more `'?'`. The `REF_CHARS` set and `REF_FONTS`
  list (DejaVu) are editable if a glyph class isn't in the reference.
- Distance metric: `ndimage.distance_transform_edt(~m)`; the best match is the reference char
  minimising mean EDT over the unknown glyph's mask.

## Known limits / gotchas

- The numeric glyphs in tables (TT292/TT293 and the TT291t00 table font in `table_reconstruct.py`)
  are **not** decodable via this DejaVu matching — glyph art differs (e.g. TT292 `0xF016` is `/`,
  not `7`). OCR wins for tables.
- `rankov/` holds earlier per-page dump/glyph-match scripts and `font1.cff`; the reconstructed
  TT291t00 mapping (F001–F035) lives in `table_reconstruct.py` (doc[244], Taylor ch.31 table) —
  a good worked example of a hand-verified font map.
- Cache file `glyph_map3.json` is append-only state — preserve it between sessions.
- Remember the venv split: `research-venv` (pymupdf) for rendering/decoding; `venv` (easyocr)
  for OCR.
