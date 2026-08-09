# Repeatable task playbooks (how-to guides)

Short guides for tasks we repeat while extracting data from sources. Read the relevant playbook
*before* starting the task — each one records the pitfalls and the exact working recipe so a later
session doesn't re-learn them the hard way.

| Playbook | When to read |
|---|---|
| [pdf-ocr-table-decoding.md](pdf-ocr-table-decoding.md) | You need the **numbers inside a table** in a PDF where text extraction fails (subset/custom fonts, e.g. Rankov 2012 Tables 8.x, 31.1). |
| [pdf-subset-font-decode.md](pdf-subset-font-decode.md) | You need the **running prose text** of a PDF rendered with embedded subset TT fonts that `get_text()` returns as PUA chars / `?`. |
| [verify-decoded-tables.md](verify-decoded-tables.md) | You decoded numbers from a table and need to **independently check they are right** (reconstruction vs source equations). |
| [pdf-text-extraction.md](pdf-text-extraction.md) | Simple case: PDF text extracts fine — pull clean text/pages quickly. |

Working notes (persistent across sessions):
- Sources: `/tmp/opencode/rankov2012.pdf` (+ `rankov2012.txt` full text dump), Carter 1982 PDF in
  `/tmp/opencode/carter/`. **`/tmp/opencode` is scratch — it may be wiped; promoted deliverables live
  under `~/projects/sandbox/research/`.**
- Two venvs in `/tmp/opencode`: `venv` has **easyocr + torch**; `research-venv` has **pymupdf + numpy
  + PIL + scipy + matplotlib**. Neither venv has all packages — **render with `research-venv`, OCR with
  `venv`** (or install into one). This split has bitten us repeatedly.
- Rankov 2012 page numbering: **PDF page index = printed book page + 12** (e.g. book p.72 = PDF page 84;
  book p.70 = PDF page 82). `decode_shaw.py` numbers by PDF page index (0-based pymupdf page).
- The full-page glyph-cache `glyph_map3.json` and the reconstructed fonts in `/tmp/opencode/rankov/`
  are the accumulated decode state — keep them when re-running decodes.
