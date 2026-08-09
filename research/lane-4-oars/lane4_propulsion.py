#!/usr/bin/env python3
"""Lane-4 trireme oar-propulsion model (Shaw 2012 ch.7 + ch.9), verified.

Implements the full speed->power chain and its inverse, then reproduces:
  - ch.9 sprint validation  (44.5 spm, ~130 rowers, E=0.730 -> 8.32 kts)
  - ch.9 Table 9.7          (rates of striking for Mark IIa/IIb at 7.5 & 9.7 kts)
  - ch.7 cruise rates       (7 / 7.5 / 8 kts -> 25.5 / 28.8 / 32.3 spm)

All lengths m, speeds m/s (1 kt = 0.5148 m/s), power W.
"""
import math

KT = 0.5148

# ---- Hull power law -------------------------------------------------------
def hull_power(V, hull=1.0):
    """Effective propulsive power W required to drive hull at V m/s.
    hull=1.0 -> Olympias (rudders partly raised); 1.08 -> Mark IIa/IIb."""
    return hull * (155.0 * V**3 + 4.13 * V**5)

def speed_from_power(W, hull=1.0):
    """Invert hull_power by bisection (V ~ (W/155)^(1/3))."""
    lo, hi = 0.0, 20.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if hull_power(mid, hull) > W:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

# ---- Oar power chain ------------------------------------------------------
def oar_power(n, P, L, r, E):
    """W = n P L r E / 60  (Shaw ch.9). n rowers, P mean pull at butt (N),
    L effective pull length at butt (m), r spm, E mean ideal efficiency."""
    return n * P * L * r * E / 60.0

def mean_pull(r):
    """Mean pull P (N) at rate r (spm): P = 7.43 r."""
    return 7.43 * r

# ===========================================================================
# 1. ch.9 sprint validation: 116-rower sprint -> P=288 N; then 4-run sprint.
# ===========================================================================
def sprint_validation():
    print("=" * 68)
    print("1. ch.9 sprint validation")
    print("=" * 68)
    # (a) calibration trial: 116 rowers, 6.8 kt (3.50 m/s), W=12100 W, r=38.75, E=0.719
    W_cal = 12100.0
    n_cal, r_cal, E_cal, L_cal = 116, 38.75, 0.719, 0.78
    P_cal = W_cal * 60.0 / (n_cal * L_cal * r_cal * E_cal)
    print(f"(a) 116-rower sprint: P = {P_cal:5.0f} N  ({P_cal/4.448:4.1f} lbf)   [Shaw: 288 N / 64.7 lbf]")
    print(f"    implied mean-pull law constant k = P/r = {P_cal/r_cal:.3f}   [Shaw uses 7.43]")

    # (b) four-run sprint: ~130 effective, 44.5 spm, E=0.730, L=0.78 (Olympias)
    n4, r4, E4, L4 = 130, 44.5, 0.730, 0.78
    W4 = oar_power(n4, mean_pull(r4), L4, r4, E4)
    V4 = speed_from_power(W4)
    print(f"(b) 4-run sprint ({n4} rowers, {r4} spm, E={E4}):")
    print(f"    power = {W4:7.0f} W  ->  {V4:.3f} m/s = {V4/KT:.2f} kts   [Shaw: 18152 W -> 8.32 kts]")
    print(f"    measured: 8.2-8.3 kts.  PREDICTION MATCHES EXPERIMENT: {abs(V4/KT - 8.32) < 0.05}")

# ===========================================================================
# 2. ch.9 Table 9.7: rates of striking for Mark IIa / IIb
# ===========================================================================
def table_97():
    print()
    print("=" * 68)
    print("2. ch.9 Table 9.7 reproduction (Mark II hull, E=0.780, n=170)")
    print("=" * 68)
    print(f"{'design':6} {'V kt':>6} {'W W':>7} {'L m':>5} {'r spm':>7} {'P N':>6} "
          f"{'P lbf':>7} {'Pr N*spm':>9} {'r^2':>6}  {'vs Shaw'}")
    rows = []
    for hull, L, Vkt in [("IIa", 0.87, 7.5), ("IIa", 0.87, 9.7),
                         ("IIb", 0.99, 7.5), ("IIb", 0.99, 9.7)]:
        V = Vkt * KT
        W = hull_power(V, hull=1.08)
        # solve W = n P L r E / 60 with P = 7.43 r  ->  W = n 7.43 L r^2 E / 60
        r = math.sqrt(W * 60.0 / (170 * 7.43 * L * 0.780))
        P = mean_pull(r)
        rows.append((hull, Vkt, W, L, r, P))
        print(f"{hull:6} {Vkt:6.1f} {W:7.0f} {L:5.2f} {r:7.1f} {P:6.0f} {P/4.448:7.1f} "
              f"{P*r:9.0f} {r*r:6.0f}")
    print("Shaw IIa: W 13460/34860, L 0.87, r 30.7/49.4, P 228/367")
    print("Shaw IIb: W 13460/34860, L 0.99, r 28.8/46.3, P 214/344")

# ===========================================================================
# 3. ch.7 cruise rates (Olympias, Mark II hull, E=0.78, n=170, L=0.99)
# ===========================================================================
def oar_absorbed(r):
    """Power (W) absorbed by a trireme oar at rate r spm (Shaw ch.7):
    inertia + blade losses, i.e. the non-propulsive oar losses."""
    return 0.96 * r + 0.016 * r * r

def table_ch7():
    print()
    print("=" * 68)
    print("3. ch.7 cruise rates reproduction (Mark II hull, E=0.78, n=170, L=0.99)")
    print("    gross power/man = P*L*r/60 + oar_absorbed(r)   [handle power + oar losses]")
    print("=" * 68)
    print(f"{'V kt':>6} {'W W':>7} {'r spm':>7} {'P N':>6} {'handle':>8} {'oar_abs':>8} "
          f"{'gross W':>8}  vs Shaw r / gross")
    for Vkt, r_shaw, Wman_shaw in [(7.0, 25.5, 115), (7.5, 28.8, 145), (8.0, 32.3, 180)]:
        V = Vkt * KT
        W = hull_power(V, hull=1.08)
        r = math.sqrt(W * 60.0 / (170 * 7.43 * 0.99 * 0.78))
        P = mean_pull(r)
        handle = P * 0.99 * r / 60.0
        absorbed = oar_absorbed(r)
        Wman = handle + absorbed
        print(f"{Vkt:6.1f} {W:7.0f} {r:7.1f} {P:6.0f} {handle:8.1f} {absorbed:8.1f} "
              f"{Wman:8.0f}   Shaw: {r_shaw:4.1f} spm, {Wman_shaw} W")

def crosscheck_s6():
    print()
    print("=" * 68)
    print("4. S6 cross-check: Olympias ~7.2 kt, 170 men -> ~62 W propulsive/man")
    print("=" * 68)
    V = 7.2 * KT
    W = hull_power(V, hull=1.0)
    prop = W / 170.0
    eff = prop / 115.0          # S6: ~115 W/man gross at 7.2 kt
    print(f"7.2 kt: W_oly = {W:5.0f} W -> {prop:.0f} W/man propulsive "
          f"(S6 says ~62 W); oar-system eff {eff*100:.0f}% (S6 says ~54%)")
    # total system efficiency at 8.5+ kts should be lower
    V9 = 8.5 * KT
    print(f"8.5 kt: oar-system eff = {hull_power(V9,1.0)/170/176:.0%} "
          f"(S6: ~40% at 8.5+ kts theme)")

if __name__ == "__main__":
    sprint_validation()
    table_97()
    table_ch7()
    crosscheck_s6()
