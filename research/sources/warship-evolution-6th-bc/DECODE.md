# Decode: "Warship Evolution in the 6th Century BC rev e.docx"

Source: `Warship Evolution in the 6th Century BC rev e.docx` (772 KB, Word 2007+,
author RICHARD BRAITHWAITE — recovered to `extracted/`; text to `document.txt`).

## What it is

A **draft RINA paper** (the journal template is still partly inside the document):
*"Modelling Oared Warship Performance During the Evolution of the Athenian
Trireme"* — R C Braithwaite (Babcock International, retired), RINA IJME
Vol 158 Part A2, DOI 10.3940/rina.ijme.2016.a2 (headers dated 2016/2021).
The companion study to the Olympias simulation report: it develops
**pentaconter monoreme / bireme / trireme+ designs from the Olympias basis**
using an integrated concept-design tool — **the same tool as the workbook
`Galley sizing Y.xlsm`** (the two files are one project).

## What the paper says (the physics, as drafted)

- **The 3-DOF manoeuvring model** (§3.6): surge/sway/yaw with Clarke–Gedling–Hine
  (1983) regressions for the hull derivatives, **plus a nonlinear yaw-damping
  term**:
  `Nr|r| = −(1/64)·ρ·CN·T·L⁴` — "the closed-form result of integrating the
  sectional cross-flow drag (½ρ·Cdc(rx)|rx|T) along a rectangular lateral
  projection" — **the same cross-flow integral family as our Plan 2 audit
  (`research/lane-5-manoeuvre/crossflow.py`)**. The paper states `CN was set
  at 0.4 to tune the model to the turning circles achieved by Olympias in her
  sea trials`. `[?]` the workbook code uses **CN = 0.8** (Module7) — the paper
  text and the code disagree; both inside/outside our C_D band [0.3, 0.6] —
  see the workbook DECODE.
- **Oar thrust model**: mean oar thrust from the acceleration-trial data,
  **max 81 N/oarsman at zero speed, linear fall to zero at 18 kts**
  (9.252 m/s). Applied at two points (port/starboard), x = LWL/2, y = ± the
  mean oar-race lever; magnitude scaled by the **local blade water speed**
  (ship speed + yaw contribution) — the differential-thrust steering.
- **Rudder model**: flat plates on circular shafts; lift `CLi = sin(2αrel)`,
  induced drag `CDi = 2·sin²(αrel)` (Hoerner); a parasitic `CD0` because the
  Olympias rudders' zero-angle drag was ~**half the total ship drag** (the
  trials' figure).
- **Resistance**: measured in the 1988 trials (rudders up/down); the Holtrop &
  Mennen method for destroyer hullforms with no immersed transom matched the
  Olympias and is used for the new designs.
- **Added mass**: `Xu̇ = 0.04 + 0.06·CB` (matches the workbook code).
- **The design tool** (§3.1–3.4): single-screen inputs; the Weight Module
  balanced against the Hull Geometry Module's displacement; the hull module
  contains **the Olympias offsets from the Lines Plan** (ref 4), scaled/
  Lackenby-transformed for the designs; weights from the **Olympias scantlings
  list and drawing pack** (2/3-digit breakdown), **confirmed by weighing the
  components of a 1:24 scale model**, verified against the **inclining
  experiment report**; radius of gyration from the 1:24 model pendulum tests
  (`Rg = XX% LWL` — the workbook uses **L/3**).
- **Design assumptions** (§5.1): interscalmium 888 mm (cubit 444 mm), L/D ≤ 15,
  GMT ≥ 0.5 m, oar length 4.2 m (9.5 cubits).
- **The pentaconter monoreme** (§5.2): 25 oarsmen/side @ 888 mm → LOA 31.0 m,
  BOA 4.0 m, depth 2.05 m, **draft 0.980 m, displacement 21.0 t, GMT 0.643 m**.
- **Trireme+** (§5.4): a (fictitious) 170+6-oar variant — the workbook's
  "Design" column holds a **pentaconter bireme** instead (26+24 rowers,
  14.4 t).

## Placeholders / gaps in the draft

- Figure 2 (design process), Figure 5 (arrangements), Table 1 (design
  particulars), Table 2 (design performance) are **undecoded** (the 5 embedded
  images `figures/image1–5`; `hdphoto1.wdp` is a Windows HD Photo, undecoded).
  The image viewer model was unavailable at decode time.
- "PLACEHOLDER describe development from monoreme through bireme to trireme…",
  "(REFS?)", "XXX" values, empty nomenclature entries.
- The bireme section body is missing (only the heading remains); the paper's
  bireme design exists in the workbook.

## Cross-references to our chain (what it validates / challenges)

| Item | This paper/workbook | Our chain | Status |
| --- | --- | --- | --- |
| Yaw damper | Cross-flow integral, CN = 0.4 (text) / 0.8 (code) | Ω = ½ρ·0.3·J computed (3.25e6) | Same physics family; C_D in [0.3, 0.6] ✓; the 0.4 vs 0.8 split `[?]` |
| Zero-speed thrust | 81 N/oarsman (trials, acceleration data) | LL equilibrium ~82 N/oar at 38.75 spm, V=0 | Independent derivations agree ✓ |
| Thrust-speed law | Linear to 0 @ 18 kt | Blade-law equilibrium (self-balancing) | Shape differs; the 18 kt crossing vs our curve `[?]` |
| Resistance | Trials fit 40.2·V² / 75.2·V²−1560 / 88.6·V²−2640 (kt); Holtrop | 155V³+4.13V⁵ (V in m/s — the trial-validated law) | Cross-check pending (see the workbook DECODE) |
| Top speed (rudders up) | 9.95 kt (all 170 at 81 N) | LL sprint 7.72–8.3 kt (thalmic head-room) | The 130-effective-rowers vs 170-at-81N difference — T1 material |
| Inertia | Rg = L/3 | LL: fitted / hull-derived `[?]` | Cross-check pending |
| Olympias mass | 45.5 t full load (scantlings + 1:24 model + inclining) | LL ship mass `[?]` | **Must reconcile** — see the workbook DECODE |
| Hull lines | The Lines Plan offsets (in the workbook) | Parametric hull_form | **The real lines — the Plan-2 named path** |

## Next steps (suggested)

1. Port the workbook's Olympias offsets into the hull-form tooling and re-run
   the cross-flow audit (CLR, A_lat, J) on the REAL lines — the item Plan 2
   named as blocked on the Wolfson archive.
2. Reconcile the full-load mass (45.5 t) with the LL's ship mass.
3. Re-run the author's 3-DOF model (its VBA is fully decoded) on the G1/F1
   turn scenarios as an independent simulator cross-check.
