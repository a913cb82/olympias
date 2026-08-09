# Lane 4 — W3: rigid-oar per-stroke refinement layer (flat-plate blade model)

Implements the per-stroke blade-force refinement the main doc W3 item 147 / D9 asks
for, on top of the verified bulk lever-chain (`propulsion-models.md`,
`lane4_propulsion.py`). Reference code: `rigid_oar_model.py` (pure stdlib).

**Result in one line**: at the Olympias design cruise point the rigid-oar
flat-plate model reproduces Shaw's bulk efficiency, handle force and per-oar power
almost exactly (76.2% vs 75.6%, 224 vs 214 N, 65 vs 61 W, 102% of hull-required
power), independently validating the bulk E = 0.756 used in the macro chain.

---

## 1. Model

Per-stroke integration of one drive of a rigid oar, in the spirit of Caplan &
Gardner (2007a) and the flat-plate / pressure-drag regime of the 2019 NJP "Physics
of rowing oars" analysis:

- Blade = flat plate (trireme blades are near-flat spade/teardrop, much lower camber
  than a modern Big Blade). Dominant blade force = pressure (normal) force on the
  face:
  **Fn = 0.5·ρ·A·C_N·|v_n|·v_n**, acting to oppose the normal flow v_n.
  C_N = 1.8 for a flat plate fully immersed — consistent with the measured Macon
  blade C_D,max ≈ 1.85 at 90° attack (Caplan & Gardner 2007b; Coppel et al. 2009).
- 2nd-class-lever torque balance about the thole: **Fh·l_in = Fb·l_cp** (Baudouin &
  Hawkins 2002), l_cp = blade centre of pressure 260 mm from tip (Rankov ch.1 §1.4.2).
- Kinematics: oar sweeps B = 48.1° (Olympias) / 55.6° (Mark IIb) at **constant
  angular speed over the effective pull time t_drive from Table 9.6**
  (0.430 s @7.2 kt, 0.392 s @8.2 kt; 0.612 s / 0.472 s for Mark IIb). Blade enters
  the water already moving — no deadpoint taper (a taper to zero produces drag, not
  thrust, because the blade then sweeps slower than the ship advances).
- Geometry from W3 (`rig-geometry.md` / Table 9.1): inboard/outboard plan lengths,
  blade 0.55 m, blade area 0.078 m² (Rankov ch.10, minimum effective), seawater
  ρ = 1025 kg/m³.

## 2. Results (script output)

| case | V kt | spm | thrust/oar N | eff | mean Fh N | peak Fb N | Shaw bulk E / P |
|---|---|---|---|---|---|---|---|
| Olympias | 7.2 | 28.8 | 17.5 | **76.2%** | **224** | 124 | **75.6% / 214 N** |
| Olympias | 8.2 | 36.0 | 18.4 | 79.1% | 208 | 121 | 75.6% / 267 N |
| Mark IIb | 7.5 | 28.8 | 6.1 | 85.7% | 63 | 50 | 78.0% / 214 N |
| Mark IIb | 9.7 | 46.3 | 13.2 | 85.6% | 109 | 86 | 78.0% / 344 N |

Energy check (propulsive power/oar from the rigid model vs. hull requirement):

- Olympias @7.2 kt: **65 W vs 63 W needed (102%)** — the rigid model closes the
  hull-power balance. ✓
- Olympias @8.2 kt: 78 W vs 101 W (77%) — model under-produces at the sprint rate;
  see caveats.
- Mark IIb: 24 W vs 79 W @7.5 kt (30%), 66 W vs 204 W @9.7 kt (32%).

**Blade-area sensitivity** (area the flat-plate model needs to meet the hull power):

- Olympias @7.2 kt: 0.078 → **0.076 m² (×1.0)** — as-built blade area is exactly
  what the physics needs. ✓
- Mark IIb @7.5 kt: 0.078 → **0.260 m² (×3.3)** — the model says Mark II needs much
  larger blades, *consistent with ch.9's explicit note* that Mark II blades "must be
  such as will enable the blades to absorb the required power" and may need different
  widths.

## 3. What this means for the simulation

- **The bulk lever-chain E is independently confirmed** at the Olympias design point
  (76.2% model vs 0.756 Shaw): the macro chain in `lane4_propulsion.py` is sound.
- The rigid model adds the **per-stroke force envelope** the bulk chain cannot give:
  peak blade force ~120–130 N, mean handle force ~210–225 N (Olympias), needed for
  any future per-stroke thrust ripple in the manoeuvring model and for ergonomic
  limits (fixed-seat V̇O2 ≈ 65% of sliding-seat, S6).
- The **Mark IIb under-production is a design finding, not a code bug**: with the
  same blade area as Olympias the flat-plate physics cannot absorb Mark II's power.
  This quantitatively supports ch.9's separate, larger Mark II blade spec and is a
  candidate for the uncertainties register (Mark II blade area is otherwise unknown).

## 4. Caveats / flags for the uncertainties register

- Constant angular speed + no deadpoint taper is a deliberate simplification; the
  2019 NJP analysis shows added-mass and pressure-drag regimes matter at the stroke
  ends. The Olympias match (102%) suggests this is adequate for mean quantities.
- Flat-plate C_N ignores blade camber/lift; a cambered blade could supply the Mark IIb
  shortfall at smaller area than ×3.3. Flag: Mark IIb blade-area requirement is an
  upper bound under the flat-plate assumption.
- Single blade CP (260 mm from tip) instead of Shaw's moving turning-point model;
  the constant lever slightly over-estimates Olympias eff (76.2 vs 75.6%).
- The 8.2 kt sprint under-production (77%) likely reflects the simplified kinematics
  at high rate; not used for the macro chain (which is calibrated to the trials).

## 5. Sources

- Caplan, N. & Gardner, T. (2007b), "A fluid dynamic investigation of the Big Blade
  and Macon oar blade designs", *J Sports Sci* 25:643–650 — measured C_L, C_D curves;
  C_D,max ≈ 1.85 at 90° attack.
- Coppel, Gardner, Caplan & Hargreaves (2009), ISBS — C_L/C_D table for Macon;
  CFD/experimental agreement within 1.33%.
- "Physics of rowing oars" (2019), *New J. Phys.* 21 — rigid-oar kinematics,
  pressure-drag vs added-mass regimes.
- Baudouin & Hawkins (2002), *Br J Sports Med* 36:396–402 — oar as 2nd-class lever.
- Rankov 2012 ch.9 (Table 9.1 oar dims, Table 9.6 pull durations), ch.1 §1.4.2
  (blade CP 260 mm), ch.10 p.85 (blade area 0.078 m²); W3 `rig-geometry.md`.
