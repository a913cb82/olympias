# Lane 3 — Hull & Hydrostatics: the Braithwaite workbook — real lines + the weight breakdown

Source: `sources/galley-sizing-xlsm/` (the author's concept-design tool,
decoded in full — every sheet TSV + the VBA + the raw offsets in
`basis_hull_offsets.tsv`; see `sources/galley-sizing-xlsm/DECODE.md`) and the
companion RINA draft paper (`sources/warship-evolution-6th-bc/DECODE.md`).

**Headline: the Olympias offsets from the Lines Plan are now in hand** — the
route named in `offsets-eliav.md` (Wolfson archive / Plan 7) is superseded for
the numerical offsets; the archive still holds the full drawing pack.

## 1. The offsets

- The Basis Hull sheet holds the offset table: **21 stations × 27 Z/Y pairs,
  LWL 32.35 m** (spacing 1.6175 m), the design waterline at Z = 1.15 m.
  Extracted as-is to `sources/galley-sizing-xlsm/basis_hull_offsets.tsv`.
  `[x]` (the paper §3.3: "the design offsets for Olympias taken from the
  Lines Plan (4)"; the sheet's readme: offsets "entered for up to 21 sections
  … 27 pairs of Z and Y")
- The sheet's interpolation functions (CUBIC/Interpolate/CUBIC2) are the
  decode path: the raw table is rows 13–39 (columns B..AQ, (Z,Y) pairs per
  station); the display table rows 77–101 re-interpolates at equally spaced
  waterlines. `[x]` (formulas inspected)
- `[?]` Which lines revision — the Olympias "Lines of hull, form No. 7,
  mod. 2" (the archive's Plan 7)? The workbook's beam at the WL (3.704 m)
  differs from the Poitiers/CNRS digitisation (3.43 m, LWL 32.08) and our
  hull_form (3.43 m, 32.2 m) — see the table below. The draft paper's figure
  captions name the Lines Plan (ref 4) without a form number.

## 2. Hydrostatics (the workbook, at the design WL Z = 1.15 m)

LWL 32.35 m · BWL 3.704 m · displacement **44.26 m³ moulded** ·
LCB **15.67 m from AP** · LCF 15.25 m · VCB 0.846 m · BMT 1.967 m ·
BML 118.5 m · WSA **130.5 m²** · Cb 0.321 · Cp 0.691 · Cm 0.465 ·
Cw **0.768** · Cp(fwd/aft) 0.657 / 0.725. `[x]` (the sheet's hydrostatics
block, rows 218–260, Simpson's-rule integrals)

## 3. Our parametric hull vs the real lines

| Item | hull_form (chain) | Braithwaite workbook | Note |
| --- | --- | --- | --- |
| LWL | 32.2 m | 32.35 m | ~0.5 % `[?]` (draft/loading differences) |
| B at WL | 3.43 m | 3.704 m | 8 % wider `[?]` (lines revision or WL level) |
| Trial draft | 1.1 m | 1.15 m | `[?]` |
| Cb | 0.340 | 0.321 | 6 % finer real hull |
| **Cw** | 0.556 | **0.768** | **the real waterplane is far fuller** — our parametric ends are too fine |
| **WSA** | 81.3 m² (trial) | **130.5 m²** | **60 % more wetted area in the real lines** `[?]` (the WSA formula includes a skin factor Q6 — check the convention) |
| LCB | 16.10 m from stern | 15.67 m from AP | conventions differ `[?]` |
| Light displacement | 25.17 m³ / 25.798 t (the chain's anchor) | 25.75 t lightship | **agree to 50 kg** ✓ |
| Full-load / trial displacement | 41.35 m³ fitted to 42.25 t | 44.26 m³ @ 45.5 t full load | different load cases; the workbook's full load includes water + effects |

## 4. The weight breakdown (the scantlings + 1:24 model + inclining)

- **Lightship 25,748 kg @ VCG 1.905 m** (HULL 19.84 t @ 1.855, PROPULSION
  4.95 t @ 2.037, OUTFIT 0.45 t, ARMAMENT 0.225 t incl. the 200 kg ram).
  `[x]` — this **confirms the chain's light-displacement anchor (25.798 t)**
  and E&H's "empty weight 25 t" (Morrison et al. 2000 p. 210).
- **Full load 45,548 kg** (variable load 19.8 t: 170 oarsmen × 75 kg,
  water 2.8 t, crew effects 2.0 t). The workbook is self-consistent with the
  hydrostatics at Z = 1.15. vs Sleeswyk's 58 t fully-manned ancient estimate
  (offsets-eliav.md §2) — the 45.5 t is the Olympias as-built load case. `[?]`
  the LL's ship mass must be reconciled against 45.5 t (it drives m_app and
  the turn physics).
- Oars **17 kg each** (62×17 = 1054 kg) — matches the build log's "17 kg once
  the lead counterweight was added" (`rig-and-oars.md` §2.3). ✓
- "Adjustment to match inclined wt" 670 kg — the inclining-experiment
  reconciliation is inside the breakdown. `[x]`
- The weights scale with 24³ — the 1:24 model weighing the paper describes. `[x]`

## 5. Consequences for the chain

1. **Re-run the cross-flow audit on the real lines** (crossflow.py): the
   lateral plane, CLR and J from `basis_hull_offsets.tsv` — the fitted
   clr_offset (+0.8 m) and A_lat (35 m²) are now computable. The fuller real
   hull (B 3.704, deeper sections) will move both.
2. The Cw/WSA gaps (§3) say the parametric hull's fine ends are not the real
   ship — worth quantifying the resistance-form consequences (the hull law is
   trial-anchored, so the chain's numbers stand; the form factors are the
   open part).
3. Reconcile the LL's ship mass with 45.5 t full load.
