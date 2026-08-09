#!/usr/bin/env python3
"""W3 oar-inertia layer (lane-4) — feeds Rankov 2012 Table 3.1 into the rigid-oar
refinement.

The rigid-oar model (`rigid_oar_model.py`) and the bulk lever chain
(`lane4_propulsion.py`) are both *massless* oar models: torque balance about the
thole is static (Fh*lin = Fb*Lcp). Table 3.1 supplies the measured rotational
inertia about the thole (MIT, kg-m^2), C of G and centre of percussion per oar,
which is what makes an oar "handy". This layer:

  A. Quantifies handiness per oar (and per family) from the measured Table:
     MIT, the equivalent mass felt at the handle (MIT/lin^2), and the
     centre-of-percussion-from-the-blade-tip distance X (tabulated).
  B. Adds the *catch-phase* inertia spike: at the stroke flip the oar's
     rotational inertia must be spun from rest up to the drive angular speed
     omega over the water-entry (t_rise), so the handle must additionally
     supply  F_spike = I_thole * omega_drive / (t_rise * lin).
     This term is zero in the static chain and grows with omega = sweep/t_drive
     (Table 9.6 measured drive durations).
  C. Cross-checks Table 3.2's "mean handle couple" rows: couple / 1.092 m is a
     mean handle force and should sit on the rigid model's 224 N value.

Inputs: research/data/shaw-table-3.1-oar-inertia.csv (comment lines + plain
header, as per repo convention).
Outputs: console report only; the doc numbers are copied into oar-data.md §6 /
rigid-oar-refinement.md by hand.
"""

import csv
import math
import os
import sys

LIN = 1.092          # inboard length, m (3 ft 7 in — "in all cases", Table 3.1)
LBF = 2.2046         # kgf per lbf

# rigid-oar model kinematics: (name, rate spm, effective pull duration s)
# from Table 9.6 — omega_drive = sweep_rad / t_drive
DRIVES = [("Olympias", 28.8, 0.430, 48.1),   # 7.2 kt
          ("Olympias", 36.0, 0.392, 48.1),   # 8.2 kt
          ("MarkIIb", 46.3, 0.472, 55.6)]    # 9.7 kt (sprint)

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "data", "shaw-table-3.1-oar-inertia.csv")


def safe_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def load_table31(path):
    """Rows for the oars that have measured data (rows 7/8 blank in source)."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return []
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 8 or not (parts[0].isdigit() or parts[0].isupper()):
            continue
        w, wm = safe_float(parts[2]), safe_float(parts[3])
        k2, cg, mit, x = (safe_float(parts[4]), safe_float(parts[5]),
                          safe_float(parts[6]), safe_float(parts[7]))
        if None in (w, k2, cg, mit, x):
            continue   # blank rows 7 & 8
        Wkgf = w / LBF
        rows.append(dict(oar=parts[0], typ=parts[1], Wkgf=Wkgf,
                         wih_lbf=wm, k2=k2, cog=cg, mit=mit, X=x))
    return rows


def catch_spike(I, omega, t_rise):
    """Peak handle force (N) to spin the oar's inertia I (kg-m2 about the thole)
    up to drive speed omega (rad/s) in t_rise s, at the inboard lever."""
    return I * omega / (t_rise * LIN)


def main():
    rows = load_table31(CSV)
    if not rows:
        sys.exit("load_table31 returned no rows")

    print("=" * 88)
    print("W3 oar-inertia layer (Rankov 2012 Table 3.1 -> rigid-oar chain)")
    print("=" * 88)
    print(f"inboard {LIN} m (3 ft 7 in, all cases); MIT = I about the thole")
    hdr = (f"{'oar':>3} {'type':>11} {'W kgf':>6} {'k2 m2':>6} {'COG m':>6} "
           f"{'MIT':>6} {'m_hand kg':>9} {'X m':>6} {'L_imp m':>8}")
    print(hdr)
    print("-" * 88)
    for r in rows:
        m_hand = r["mit"] / LIN ** 2            # equivalent mass at the handle
        c = r["cog"] - LIN
        L = r["cog"] + r["k2"] / c - r["X"]     # implied total length, m
        print(f"{r['oar']:>3} {r['typ']:>11} {r['Wkgf']:6.2f} "
              f"{r['k2']:6.2f} {r['cog']:6.2f} {r['mit']:6.1f} "
              f"{m_hand:9.1f} {r['X']:>+5.2f} {L:8.2f}")

    # family means
    fam = {}
    for r in rows:
        key = ("fir-zygian" if r["typ"] == "old-zygian" else
               "fir-thranite" if r["typ"] == "old-thranite" else "spruce")
        fam.setdefault(key, []).append(r)
    print("\nfamily  n  mean W (kgf)  mean MIT (kg-m2)  m_hand (kg at 1.092 m)")
    for key in ("spruce", "fir-zygian", "fir-thranite"):
        rs = fam[key]
        w = sum(r["Wkgf"] for r in rs) / len(rs)
        mit = sum(r["mit"] for r in rs) / len(rs)
        print(f"  {key:>12} {len(rs):>2} {w:>9.1f} {mit:>14.1f} "
              f"{mit / LIN ** 2:>12.1f}")

    print("\nCatch-phase inertia spike at the oar (Table 9.6 drive kinematics):")
    spr = [r for r in rows if r["typ"] == "spruce"]
    zyg = [r for r in rows if r["typ"] == "old-zygian"]
    thr = [r for r in rows if r["typ"] == "old-thranite"]
    I = {k: sum(r["mit"] for r in rs) / len(rs)
         for k, rs in [("spruce", spr), ("zygian", zyg), ("thranite", thr)]}
    hdr2 = (f"{'case':>22} {'rate':>5} {'omega':>6} | " +
            " | ".join(f"{k:>18}" for k in ("spruce", "zygian", "thranite")))
    print(hdr2)
    print("-" * 88)
    for name, r_spm, t_drive, sweep_deg in DRIVES:
        omega = math.radians(sweep_deg) / t_drive
        cells = []
        for k in ("spruce", "zygian", "thranite"):
            cells.append(" ".join(f"{catch_spike(I[k], omega, tr):5.0f}"
                                  for tr in (0.10, 0.15, 0.20)))
        print(f"{name:>22} {r_spm:5.1f} {omega:5.2f} | "
              + " | ".join(cells))
    print("   (t_rise 0.10 / 0.15 / 0.20 s;  mean drive handle force is "
          "~210-225 N)")

    print("\nCross-check Table 3.2 mean handle couple = mean Fh * 1.092 m:")
    print(f"{'spm':>4} {'0.99m':>8} {'0.87m':>8} {'Fh87 N':>8} {'7.43*r':>7}")
    for r, c99, c87 in [(30, 215, 246), (32, 202, 231), (34, 190, 218),
                        (36, 180, 206), (38, 172, 196)]:
        print(f"{r:>4} {c99:>8} {c87:>8} {c87 / LIN:>8.1f} {7.43 * r:>7.1f}")
    print("rigid-model mean Fh = 224 N x 1.092 m = 244.6 N.m vs Table 3.2's")
    print("246 N.m at 30 spm / 0.87 m: 0.6% agreement.")


if __name__ == "__main__":
    main()