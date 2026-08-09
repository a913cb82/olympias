# Uncertainties register (W6) — every [?] number, its source caveat, and its model sensitivity

Lane 6 ("validation"), Olympias trireme reconstruction — research notes.
Central register for all numbers flagged `[?]` or "uncorroborated" across the lanes. Format per row:
**value / flag / source / caveat / model sensitivity**. Sensitivity convention: [H] = materially
changes a headline prediction if wrong; [M] = changes a secondary prediction; [L] = cosmetic.
Compiled 2026-08-09 (S13) from lane notes; keep this in sync whenever a `[?]` is resolved.

---

## A. Oars & propulsion (Lane 4)

| # | Item | Value | Flag | Source | Caveat | Sens. |
|---|------|-------|------|--------|--------|-------|
| A1 | Oar mass (real Olympias fir oars) | **12.3 kg/oar** | `[?]` | Braithwaite build log (source of value not stated) | Likely Shaw/Coates 1990 or Trireme Trust newsletter; consistent with ">12 kg, +17 kg w/ counterweight" but not independently confirmed. Rankov Table 3.1 (10-oar measured table) is the authoritative source but its body is corrupted in the PDF text layer. | [L] shaft inertia / blade-loss term only (0.96r+0.016r²), ±few % |
| A2 | Gross per-man power, ch.7 cruise | model **114/142/176 W** vs Shaw **115/145/180 W** | `[?]` | Shaw ch.7 p.66 (gross, "nearest 5 W") vs our ch.9 chain | Shaw's last two values 2–4 W higher; likely his intermediate rounding. ~2% discrepancy. | [L] crew-feasibility margin only |
| A3 | "0.94 m" interscalmium | **0.94–0.99 m** | `[?]` | task spec (Roman-wreck range) | No Olympias source: Olympias design = 0.888 m, Mark II = 0.98 m. Conflation with Mainz/Oberstimm/Vechten/Yverdon/Herculaneum wreck measurements. Do NOT use for Olympias. | [M] stroke-length/rig geometry |
| A4 | Table 3.1 ten-oar measured values (overall weight, weight-in-hand, MIT, X per oar) | (missing) | `[?]` | Rankov ch.3 App.2, table body corrupted in PDF text layer | Needed for precise mass/inertia distribution; only text-layer prose recovered (fir+spruce, 10 oars, 1.092 m inboard all cases). | [L] per-oar dynamics detail |
| A5 | Blade areas (spade vs teardrop) + exact taper | (missing) | `[?]` | only Coates Plans 15/15d/15e/15g (Wolfson archive) | Not recovered as text; needed if blade-force/angle refinement is built. | [M] per-stroke rigid-oar refinement only |
| A6 | Roman-wreck interscalmia (parallels) | Mainz 0.84–0.96, Oberstimm 0.94–0.99, Vechten/Yverdon/Herculaneum 0.92–1.125 m | `[?]` | secondary summary (Bockius via build log) | For calibration only; get primary wreck reports if they enter the model. | [L] |
| A7 | Ch.9 Table 9.6/9.7 decoded rates (30.7/49.4, 28.8/46.3 spm; P 228/367, 214/344 N) | verified to OCR precision | `[?]` (minor) | OCR of corrupted table body | Agreement to ~0.1 spm / 1–2 N; digit-level OCR uncertainty on `5/6`, `0/9`. | [L] |
| A8 | Table 9.6 effective-pull time at 44.5 spm | **missing — no entry** | `[?]` (data gap) | Shaw ch.9 Table 9.6 (Olympias entries: 0.430 s @ 28.8 spm, 0.392 s @ 36 spm) | Surfaced by Gate 2: the LL sprint prediction (130 oars) spans 7.9–8.8 kt over the plausible t_drive range (0.347 s extrapolated … 0.392 s); the ch.9 trial band 8.2–8.4 kt lies inside (t_drive ≈ 0.375 s reproduces it exactly). Default (extrapolated) gives 8.76 kt — locked by test. | [M] sprint-regime predictions |

## B. Hull & hydrostatics (Lane 3)

| # | Item | Value | Flag | Source | Caveat | Sens. |
|---|------|-------|------|--------|--------|-------|
| B1 | Displacement reconciliation | light **25.798 t** (BMT inclining), trial w/crew **42.25 t** (80 kg each), fully manned **43 t** (ch.22), "fully laden" **47 t** (poster/Wikipedia), Osprey **42 t**, HN **35 t** | `[x]` (25.798/42.25/43); `[?]` (47 t, 42 t, 35 t) | ch.25 Appendix (BMT TR01/R1952); ch.22; Trireme Trust poster; Wikipedia; Osprey | 42.25→43 t gap ≈ 0.75 t rounding/outfit. 47 t adds full naval outfit (rigging, masts, oars, benches, stores, troops). **35 t (HN) inconsistent — dropped.** Sim anchors: 25.8 light / 42.25 trial / 47 max-capability only. | [H] displacement is the primary hydrostatics driver (draft, KM/GM, W=155V³+4.13V⁵ validity) |
| B2 | Tank-test provenance of hull power law | W = 155V³+4.13V⁵ from **Grekoussis & Loukakis 1985, NTUA Report NAL 06-F-1985** (bare-hull calm-water tests, no ram); graph reproduced by Lowry & Squire 1988; resistance/speed curves published in Shaw 1993 (*The Trireme Project*) | `[x]` (existence+attribution); `[?]` (raw numbers) | Rankov 2012 ch.7 p.79 & ch.22; bibliography | Report not online (NTUA library/hardcopy); raw resistance table & scale factor unrecovered. The 155V³+4.13V⁵ fit itself is validated against trial speeds (8.32 vs 8.2–8.3 kt), so the *shape* is solid; only the raw tank points are missing. | [H] if the law's coefficients are wrong; currently well-validated |
| B3 | Mark II hull resistance uplift | **×1.08** (Shaw ch.7: "about 8% more"); Coates ch.22: ~7% higher at low speed, ~5% at sprint | `[x]`/`[?]` | ch.7 p.79; ch.22 | Two slightly different figures (8% constant vs 7→5% speed-dependent); Shaw's ×1.08 is a convenient constant and is used in the model. | [M] Mark II speed predictions only |
| B4 | Eliav & Helfman laced-hull weight delta | laced MT hull ~**8.1 t** vs basic ~15 t (~46–50% lighter); empty hull 25 t (M&R 2000); no **quantified resistance penalty** | `[x]` (weights) / `[?]` (resistance) | E&H 2022 PDF; M&R 2000 p.210 | The "laced = much lighter/slower" case is **qualitative** in E&H; no ΔC_d given. Lane 3 must compute any resistance effect itself from hull form. | [H] for the "light laced trireme vs heavy Olympias" scenario; [L] for the Olympias baseline |
| B5 | 35 t displacement (Hellenic Navy) | 35 t | `[?]` (inconsistent) | armyrecognition/HN page | Conflicts with 42–47 t elsewhere; likely light ship sans gear or error. Dropped from sim anchors. | [L] (not used) |
| B6 | Beam/draft spread | LOA 36.8–37 m, beam 5.45–5.6 m, draft 1.05–1.25 m | `[?]` (secondary range) | Wikipedia, HN, grokipedia (tertiary), E&H | No published numerical offset table; derive offsets from Fig.17.1/frontispiece (low-res) or archive originals. | [M] hydrostatics + drag |
| B7 | Deck load effect on GM (crew lean / movement) | solid-crew roll GM 1.13→0.99 m; leaning to double roll →0.85 m | `[x]` | ch.25 | Stability numbers from BMT inclining are solid; the two crew-movement cases are design-rule estimates. | [M] heel/roll model |

## C. Manoeuvring (Lane 5)

| # | Item | Value | Flag | Source | Caveat | Sens. |
|---|------|-------|------|--------|--------|-------|
| C1 | Table 31.1 row 12 units (resistance to angular velocity) | printed **"kg m²"** | `[?]` | Taylor ch.31 Table 31.1 (OCR) | Dimensionally should be **kg m² s⁻¹** (a rotational-resistance coefficient); printed cell omits the per-second factor. Value 5×10⁶ / 6×10⁶. | [H] yaw-rate dynamics if units wrong; values fit trials, so the *number* is right, only the printed unit label is off |
| C2 | Taylor's Excel workbook | not located online | `[?]` (leads, unresolved) | tDAR 424186/424277 (citation only); ancientportsantiques.com (PDF only); Trireme Trust archive catalogue (no Excel) | Best leads: Wolfson College archive (archivist@wolfson.cam.ac.uk) or author Andrew Taylor. Model outputs independently confirmed by Alke Dominis blog (0→9.5 kt ~40 s, 145 m fast turn @9.5 kt 22.5°, 60 m tight turn @6–7 kt, diekplous gap ≥150 m/130 m). | [L] (chapter text already fully reconstructed in lane-5 note) |
| C3 | Olympias Table 31.1 turn drag (row 4) | straight-rudder drag **39.4v²** N (79.6−40.2) | `[x]` | Table 31.1 + ch.31 text (p.234) | Verified against the "¼ of Olympias" fast-hull statement (10v² ≈ 39.4/4). | [L] |
| C4 | Zig-zag (Kempf) data source Taylor used | (unspecified) | `[?]` | ch.31 cites Lowry & Squire 1989, Coates et al. 1990, Shaw 1993 | Likely those volumes' turn tables F/G; not directly confirmed which supplied the Kempf-response data. | [L] |
| C5 | Drift angle G1/G2 | 15°±2° (reported) vs 7.8° (time-delay method); Taylor assumes lower | `[x]`/`[?]` | ch.31 §2 | Method choice affects fitted lateral-drag coefficients. | [M] turn-diameter predictions |
| C6 | Mark IIb GM change | −0.1 m (vs Olympias 1.13 m trial) | `[x]` | ch.31 §5.1 | Used in heel limit (≤3°) & lateral-resistance lever arms. | [M] Mark IIb turns/heel |

## D. Sea trials / validation (Lane 6)

| # | Item | Value | Flag | Source | Caveat | Sens. |
|---|------|-------|------|--------|--------|-------|
| D1 | 8.9 kt peak (1990) | 8.9 kt single end-of-run reading; last-half avg **8.3 kt**; GPS-verified sustained **8.3 kt**, brief peak ~8.5 | `[x]` | ch.1.2 (Lipke/Ruddle/Weiskittel) | The 8.9 "record" is **suspect** (one reading); don't use as a steady-state target. Also 1988 burst 7.9, runs 7.3–7.5. S1 9.0/9.6 kt aggregator figures are suspect-peak class. | [H] as the headline validation target — use 8.2–8.3 sustained |
| D2 | Table 1.2.1 (spm→knots, 1992) | single **acceleration run**, 38→47 spm, 5.8→8.9 kt | `[x]` | ch.1.2 Table 1.2.1 | Mid-run speed-at-rate pairs **under-predict steady state**; must NOT be compared pointwise to the steady-state model. Use S10 sprint (130@44.5→8.32 kt) and 1992 GPS 2-min runs (135→7.8–7.9, 121→8.2) instead. | [M] if misused; correct anchors in lane-6 note §1.2 |
| D3 | Bilge-sloshing power loss (fore-and-aft with stroke) | **unmeasured** | `[?]` | ch.25 (bilge-water section) | Only GM/sinkage effects quantified (stable up to floor tops: +7.42 t, GM≈0.99 m unchanged). Sloshing with the stroke rhythm is a real but unquantified drag on the oarcycle. | [M] degraded-state performance; [L] intact baseline |
| D4 | Crew power envelope (S5/S6) | 80 W fixed-seat; 115–145 W long-endurance (ordinary labourer); 300 W/rower Mark IIb short sprint | `[x]`/`[?]` | Rossiter & Whipp ch.23; Coates ch.22; Monod/MacFarlane/Nadel (via Coates) | 53–55% rowing efficiency (Shaw, calm) used throughout. Cross-source variance in what "sustainable" means. | [H] endurance/cruise predictions |
| D5 | 1988 acceleration data (0→7 kt in 32 s) | 0→7 kt in 32 s (1988, less-trained crew) | `[x]` | S1 aggregator | Validate against Taylor's rotational-inertia model, not the steady-state chain. Taylor model: 0→5.5 kt in 10 s, 9 kt at 24 s, full ~40 s (for a trained crew). | [M] |
| D6 | Hull-form transverse stability (model KM) | model KM 1.428 m (BM 0.935 m, I_t 38.5 m⁴) vs BMT KM 2.90 m, GM 1.13 m | `[x]` BMT; `[x]` model caveated | S14 parametric hull vs ch.25 | Circular-arc waterplane (Cwp 0.556) is too lean — real Olympias fuller/flatter-bottomed. **Decision: Lane 5 manoeuvring uses BMT KM/GM directly, never model KM.** Model is adequate for volume/wetted surface/resistance only. | [M] Mark IIb turns/heel |

---

## Bottom line / reading

- **[H] items to watch when numbers collide**: B1 (displacement), B2 (hull law — but already trial-validated), B4 (light-hull scenario), C1 (yaw-drag units), D1 (speed target — resolved to 8.3 kt).
- All `[H]` sensitivities for the *Olympias baseline* are already pinned by primary-source values (BMT inclining, ch.1.2 GPS, ch.9 sprint validation); the remaining uncertainty lives in the *Mark II / light-hull scenario* space and in raw-but-unrecovered source tables (A4, A5, B2 raw points).
- When any `[?]` here is resolved (archivist reply, 1990 volume, NTUA report), strike the row through and log the resolution in a new S-section in the main research md.
