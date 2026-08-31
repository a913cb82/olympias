# How-to guides for repeated tasks

Short guides for jobs we do again and again while getting data out of
source documents. Read the right guide *before* starting the job — each
one lists the pitfalls and the exact steps so you don't re-learn them.

| Guide | When to read |
|---|---|
| [pdf-ocr-table-decoding.md](pdf-ocr-table-decoding.md) | You need **numbers from a table** in a PDF where copy-paste gives garbage (custom fonts, e.g. Rankov 2012 Tables 8.x, 31.1). |
| [pdf-subset-font-decode.md](pdf-subset-font-decode.md) | You need the **text** of a PDF whose embedded fonts make copy-paste return wrong characters. |
| [verify-decoded-tables.md](verify-decoded-tables.md) | You decoded numbers from a table and need to **check they are right** (re-derive from the source equations). |
| [pdf-text-extraction.md](pdf-text-extraction.md) | Simple case: the PDF's text copies cleanly — just grab it quickly. |

Working notes:

- Sources: `../sources/rankov2012.pdf` (+ `rankov2012.txt` text dump),
  Carter 1982 PDF in `../sources/carter/`.
- **Python**: `.venv` at the repo root (Python 3.10.12) has pymupdf, numpy,
  PIL, scipy, matplotlib — everything except OCR. Use `.venv/bin/python3`.
- **OCR** (easyocr + torch) is heavy and not in `.venv`. To use it:
  `python3 -m venv .venv-ocr && .venv-ocr/bin/pip install easyocr torch`
  (render with `.venv`, run OCR with `.venv-ocr`).
- Rankov 2012 page numbers: **PDF page = printed book page + 12** (e.g.
  book p.72 = PDF page 84). `decode_shaw.py` counts by PDF page index
  (0-based, as pymupdf does).
- The glyph cache (`../tools/.cache/glyph_map3.json`, not saved in git)
  and the rebuilt fonts in `../tools/` are the accumulated decode state —
  keep them when re-running decodes.
