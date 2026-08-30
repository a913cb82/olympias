# Repeatable task playbooks (how-to guides)

Short guides for tasks we repeat while extracting data from sources. Read the relevant playbook
*before* starting the task — each one records the pitfalls and the exact working recipe so a later
session doesn't re-learn them the hard way.

| Playbook | When to read |
|---|---|
| [pdf-ocr-table-decoding.md](pdf-ocr-table-decoding.md) | You need the **numbers inside a table** in a PDF where text extraction fails (subset/custom fonts, e.g. Rankov 2012 Tables 8.x, 31.1). |
| [pdf-subset-font-decode.md](pdf-subset-font-decode.md) | You need the **running prose text** of a PDF rendered with embedded subset TT (TrueType) fonts that `get_text()` returns as PUA (Private-Use-Area) characters / `?`. |
| [verify-decoded-tables.md](verify-decoded-tables.md) | You decoded numbers from a table and need to **independently check they are right** (reconstruction vs source equations). |
| [pdf-text-extraction.md](pdf-text-extraction.md) | Simple case: PDF text extracts fine — pull clean text/pages quickly. |

Working notes (persistent across sessions):
- Sources: `../sources/rankov2012.pdf` (+ `rankov2012.txt` full text dump), Carter 1982 PDF in
  `../sources/carter/`. Promoted deliverables live in this repo.
- **Venv: `.venv` at the repo root** (Python 3.10.12) has pymupdf + numpy + PIL + scipy +
  matplotlib — everything except OCR. Render/extract with `.venv/bin/python3`.
- **OCR (easyocr + torch) is on-demand only** — heavy; not installed into `.venv`. Recipe:
  `python3 -m venv .venv-ocr && .venv-ocr/bin/pip install easyocr torch` (render with
  `.venv`, OCR with `.venv-ocr`). The old `/tmp/opencode` venv pair is deprecated.
- Rankov 2012 page numbering: **PDF page index = printed book page + 12** (e.g. book p.72 = PDF page 84;
  book p.70 = PDF page 82). `decode_shaw.py` numbers by PDF page index (0-based pymupdf page).
- The glyph-cache (`../tools/.cache/glyph_map3.json`, gitignored) and the reconstructed fonts in
  `../tools/` are the accumulated decode state — keep them when re-running decodes.
