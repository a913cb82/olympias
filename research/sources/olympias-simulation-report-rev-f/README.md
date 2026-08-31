# Olympias Simulation Report Rev F — what it is

Source file: `Olympias-Simulation-Report-Rev-F.docx` by Richard Braithwaite
(22 Nov 2019, 30th revision).

| Field | Value |
|---|---|
| Author | RICHARD BRAITHWAITE |
| Created | 2019-11-22 |
| Last modified | 2026-03-16 |
| Title | "A 2-D Rowing Model Applied to the Manoeuvring of the Trireme Reconstruction Olympias" |

## What's in this folder

- `report.md` — the document converted to text: paragraphs, tables,
  captions, image references, and all 115 equations written as plain text
  (`x_0 = x_OG + x cos ψ − y sin ψ` style). The table of contents and
  bibliography are included.
- `equations.txt` — just the equations, easy to search.
- `media/` — the 22 embedded images (jpeg/png/emf/wmf).
- `comparison-with-ll.md` — how this report's model compares to the
  project's LL model (notably: the stationary-turn 3.5°/s anchor, blade
  area 0.113 m² vs the chain's 0.078, inboard 1.05 vs 1.092 m).

How the conversion was done: the docx file is a ZIP; `word/document.xml`
was parsed with Python's built-in XML tools (paragraphs, styles, tables,
images), plus a math converter for the equations. Checked against a second
independent text dump — all 16 key numbers matched both ways.

## Things to know about the conversion

- Equations are written flat (no square-root bars, no big-operator shapes);
  accents show as `[̇]`/`[̈]` markers; matrices are `[a b; c d]`.
- The source-code appendix is empty in the original file — the heading
  exists but nothing is under it.
- Sections 6 (VALIDATION) and 7 (SOFTWARE ARCHITECTURE) are one-line
  stubs in the original.
- Scanned figures (image1, image22…) are at their original resolution.

## How this report relates to the project

This is the author's own 2-D rowing and turning model of Olympias — the
same author whose build log is in `recovery/`. It is NOT one of the
trial-data sources the research chain is built on (Rankov 2012, the 1988
trials report); it is a sibling model. Numbers from it that affect the
chain are compared in `comparison-with-ll.md`.
