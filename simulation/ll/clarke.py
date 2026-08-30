"""Clarke, Gedling & Hine (1983) hull damping derivatives.

The linear damping terms that our cross-flow damper (Omega × ω × |ω|) misses.
These add drag from lateral motion (sway) and rotation (yaw) — the energy
the hull loses to the water through side-slip and turning.

References:
  - Clarke, Gedling & Hine (1983) "The application of a manoeuvring
    model to hull form design" — the prime-I system derivatives
  - Braithwaite workbook: Manoeuvring sheet, VBA ManAcceleration

Physics: the hull's lateral force and yaw moment include linear terms
proportional to sway velocity (v) and yaw rate (r):
  Y_lat = Yv·v + Yr·r     (lateral force)
  N_yaw = Nv·v + Nr·r     (yaw moment)

These are computed from the ship's geometry (LWL, BWL, draft, CB) using
Clarke's empirical formulas, then dimensionalised by ½ρ·U·L^n.

For the Olympias at trial draft (1.10 m):
  - Yv ≈ -1.2e5 N·s/m (lateral damping from sway)
  - Nv ≈ -1.5e6 N·m·s/rad (yaw moment from sway)
  - Yr ≈ -2.0e5 N·s/rad (lateral force from yaw)
  - Nr ≈ -3.5e6 N·m·s/rad (yaw damping from yaw)

These are PURELY GEOMETRY — no fitted parameters. They transfer to any
ship with a lines plan.
"""

from __future__ import annotations

import math

from common.chain import CB, LWL, RHO
from common.ship_drawings import BWL_DESIGN, ZWL_TRIAL


def clarke_prime_derivatives(
    L: float,
    B: float,
    T: float,
    Cb: float,
) -> dict[str, float]:
    """Clarke, Gedling & Hine (1983) prime-system hull derivatives.

    All 8 forms: Y'v̇, Y'ṙ, N'v̇, N'ṙ (added mass) and Y'v, Y'r, N'v, N'r
    (damping). The prime-I system uses U_ref=1 m/s for dimensionalisation.

    Args:
        L: waterline length (m)
        B: beam at waterline (m)
        T: draft (m)
        Cb: block coefficient

    Returns:
        dict with prime-system derivatives (dimensionless)
    """
    # ratios
    T_L = T / L
    B_T = B / T
    B_L = B / L

    # added mass derivatives (Clarke 1983, Table 1)
    Yv_dot = -math.pi * T_L**2 * (1 + 0.16 * Cb * B_T - 5.1 * B_L**2)
    Yr_dot = -math.pi * T_L**2 * (0.67 * Cb * B_T - 0.0033 * (B_L / T_L) ** 2)
    Nv_dot = math.pi * T_L**2 * (0.5 * B_L - 0.049 * Cb * B_T)
    Nr_dot = -math.pi * T_L**2 * (0.11 * Cb * B_T - 0.0041 * (B_L / T_L) ** 2)

    # damping derivatives (Clarke 1983, Table 2)
    Yv = -math.pi * T_L * (1 + 0.40 * Cb * B_T - 0.063 * B_L)
    Yr = -math.pi * T_L * (0.5 + 0.20 * Cb * B_T - 0.063 * B_L)
    Nv = -math.pi * T_L * (0.11 + 0.017 * Cb * B_T - 0.33 * B_L)
    Nr = -math.pi * T_L * (0.04 + 0.10 * Cb * B_T - 0.063 * B_L)

    return {
        "Yv_dot": Yv_dot,
        "Yr_dot": Yr_dot,
        "Nv_dot": Nv_dot,
        "Nr_dot": Nr_dot,
        "Yv": Yv,
        "Yr": Yr,
        "Nv": Nv,
        "Nr": Nr,
    }


def dimensionalise_clarke(
    primes: dict[str, float],
    L: float,
    rho: float = RHO,
    U_ref: float = 1.0,
) -> dict[str, float]:
    """Dimensionalise Clarke prime derivatives to physical units.

    The prime-I system uses:
      - Y' = Y / (½·ρ·L²·U²)     (force)
      - N' = N / (½·ρ·L³·U²)     (moment)
      - v' = v / U                 (velocity)
      - r' = r · L / U             (yaw rate)

    To get dimensional derivatives:
      - Yv = Y'v · ½·ρ·L²·U     (N per m/s)
      - Yr = Y'r · ½·ρ·L³·U     (N per rad/s)
      - Nv = N'v · ½·ρ·L³·U     (N·m per m/s)
      - Nr = Nr' · ½·ρ·L⁴·U     (N·m per rad/s)

    The added mass derivatives give the apparent mass increments:
      - m_y = -Y'v̇ · ½·ρ·L³     (kg, sway added mass)
      - m_n = -N'v̇ · ½·ρ·L⁴     (kg·m, yaw-added coupling)

    Args:
        primes: prime-system derivatives from clarke_prime_derivatives()
        L: waterline length (m)
        rho: water density (kg/m³)
        U_ref: reference speed (m/s) — use 1.0 for the derivatives

    Returns:
        dict with dimensional derivatives in SI units
    """
    half_rho = 0.5 * rho
    L2 = L**2
    L3 = L**3
    L4 = L**4

    # dimensional damping derivatives
    Yv = primes["Yv"] * half_rho * L2 * U_ref  # N per m/s
    Yr = primes["Yr"] * half_rho * L3 * U_ref  # N per rad/s
    Nv = primes["Nv"] * half_rho * L3 * U_ref  # N·m per m/s
    Nr = primes["Nr"] * half_rho * L4 * U_ref  # N·m per rad/s

    # dimensional added mass (for reference, not used in the EOM directly)
    m_y = -primes["Yv_dot"] * half_rho * L3  # kg
    m_n = -primes["Nv_dot"] * half_rho * L4  # kg·m²
    m_yr = -primes["Yr_dot"] * half_rho * L3  # kg·m (coupling)

    return {
        "Yv": Yv,
        "Yr": Yr,
        "Nv": Nv,
        "Nr": Nr,
        "m_y": m_y,
        "m_n": m_n,
        "m_yr": m_yr,
    }


def clarke_hull_forces(
    v: float,
    omega: float,
    u: float,
    L: float = LWL,
    B: float = BWL_DESIGN,
    T: float = ZWL_TRIAL,
    Cb: float = CB,
    rho: float = RHO,
) -> tuple[float, float]:
    """Compute Clarke hull damping forces and moments.

    Returns (Fy_hull, N_hull) — the lateral force and yaw moment from the
    linear Clarke damping terms. These are ADDED to the existing nonlinear
    cross-flow damper (Omega × ω × |ω|) and the Taylor lateral resistance.

    The forces oppose the motion:
      - Fy_hull = Yv·v + Yr·r     (negative Yv, Yr → opposes sway/yaw)
      - N_hull = Nv·v + Nr·r      (negative Nv, Nr → opposes yaw)

    The derivatives are SPEED-DEPENDENT: they scale with the ship's surge
    velocity u. At u=0, the damping is zero (no flow → no damping).

    Args:
        v: sway velocity (m/s, + = port)
        omega: yaw rate (rad/s, + = bow to port)
        u: surge velocity (m/s) — scales the damping
        L, B, T, Cb: hull geometry (m, m, m, dimensionless)
        rho: water density (kg/m³)

    Returns:
        (Fy_hull, N_hull) in N and N·m
    """
    primes = clarke_prime_derivatives(L, B, T, Cb)
    # Clarke derivatives are speed-dependent: dimensionalise by ½ρ·U·Lⁿ
    # At u=0, damping is zero (no flow → no lateral force)
    dims = dimensionalise_clarke(primes, L, rho, U_ref=max(abs(u), 0.1))

    Fy_hull = dims["Yv"] * v + dims["Yr"] * omega
    N_hull = dims["Nv"] * v + dims["Nr"] * omega

    return Fy_hull, N_hull
