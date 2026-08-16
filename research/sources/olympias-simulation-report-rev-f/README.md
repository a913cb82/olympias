# Olympias Simulation Report Rev F — provenance

Source document: `Olympias-Simulation-Report-Rev-F.docx` (the repo's original
`Olympias Simulation Report Rev F (1).docx`, moved here on 2026-08-16).

## Document metadata (docProps/core.xml)

| Field | Value |
|---|---|
| Creator | RICHARD BRAITHWAITE |
| Last modified by | RICHARD BRAITHWAITE |
| Created | 2019-11-22 10:41 UTC |
| Modified | 2026-03-16 15:52 UTC |
| Revision | 30 |
| Title page | "A 2-D Rowing Model Applied to the Manoeuvring of the Trireme Reconstruction Olympias", R Braithwaite, 22 Nov 2019, Rev E → the file is Rev F (30th revision) |

## The extraction

- `report.md` — the converted document: paragraphs, tables, captions, image
  references (media/), and all 115 OMML equations inlined as linear text
  (`x_0 = x_OG + x cos ψ − y sin ψ` style; fractions as `(a)/(b)`, indices as
  `x_i`, powers as `x^2`). The Word table-of-contents field is skipped; the
  bibliography (`w:sdt` — the 17 references) is included after the body.
- `equations.txt` — the equations alone, for grep-able reference.
- `media/` — the 22 embedded images (jpeg/png/emf/wmf).
- `comparison-with-ll.md` — the deep-dive comparison with the low-level
  simulator's methodology.

Conversion route (no external tools; the venv has no docx library): the docx
is a ZIP; `word/document.xml` parsed with stdlib `xml.etree` (paragraphs,
styles, tables, images), plus an OMML→linear-text converter for the math.
Cross-checked against an independent plain-text dump (all 16 key numeric
probes matched in both routes).

## Known conversion caveats

- The equations are LINEAR approximations of the 2-D layout (no square-root
  bars, no big operators' geometry); accents/dots show as `[̇]`/`[̈]`
  suffixed markers; matrix rows are `[a b; c d]`.
- The source-code appendix is EMPTY in this docx — the heading
  "APPENDIX SOURCE CODE" has no content under it; the OLE objects
  (oleObject1-3.bin — old equation-editor compounds) are not decoded.
- Sections 6 (VALIDATION) and 7 (SOFTWARE ARCHITECTURE) are one-line stubs
  in the source; the report's validation was never written.
- Scanned-in figures (image1, image22…) are at their native resolution.

## The report's role in this project

The report is the author's own 2-D rowing/manoeuvring model of Olympias — the
same author whose archived build log lives in `recovery/`. It is NOT one of
the trial-data sources the validated chain is built on (Rankov 2012, the 1988
trials report); it is a sibling model. Its numbers that bear on the chain are
compared in `comparison-with-ll.md` (notably: the stationary-turn 3.5°/s at
27 spm anchor vs the t_360 open item, blade area 0.113 m² vs the chain's
0.078, inboard 1.05 vs 1.092 m).
