"""The ch.9 (q/p)^2 turning-point blade-force law (Shaw 2012, ch.9) — time-stepped.

Frame: x = along keel, bow = +x; C = oar angle from athwartships, + = blade
swept toward bow; nx = cos C, ny = -sin C is the blade-face normal.

THE LAW (Rankov 2012, ch.9 p.79: "the resistance offered by the water to
the blade"; decoded in research/lane-1-read/shaw-ch7-ch9-2024.md):

    Fn = k·(q/p)^2·V^2·cos^2C           (Shaw prints sin^2C — his C is the
                                         angle of attack vs the keel; here C
                                         is from athwartships, so
                                         sin^2C_shaw = cos^2C_code)

with k = 0.5·rho·A·C_N (flat plate), p = thole -> instantaneous turning
point (plan), q = turning point -> blade CP. The mean ideal efficiency is
E = 1/(1 + q/p), and q/p ~ 1/sqrt(n) (170 -> 116 rowers raises q/p x1.21).

TWO turning-point interpretations (the oQ-18 diagnosis, the OQ18 note (common/chain.py); the
switch below selects between them):

  TURNING_POINT = "actual" (DEFAULT) — the kinematic turning point: the
  point instantaneously at rest with respect to the water, p = V·nx/omega.
  Then q = l_cp - p and the normal flow at the CP is v_n = omega·q =
  V·nx - l_cp·omega, so k·(q/p)^2·V^2·cos^2C = k·(omega·q)^2 = k·v_n^2 —
  the flat-plate law IS Shaw's force form (algebraic identity, locked by
  tests/test_research_chain.py::test_turning_point_equivalence). The Mark
  IIb shortfall is therefore NOT a blade-law error: it is the A5 blade-area
  gap + the slip assumptions (ch.9's x3.3 area note; register A5; oQ-18,
  common/chain.OQ18) — the identity is kept by construction here, so the
  validated numbers cannot drift under this law.

  TURNING_POINT = "geometric" (OFF — diagnostic only) — Shaw's appendix
  d-formula: the turning point rides the shaft as d = 0.953·sin[120(C-A)/B
  + 30 deg] (0.476 m from the tip at catch/finish, 0.953 m at mid — here
  d = 0.953·cos(120·C/B), C from mid-stroke), p = L_plan - d, and the
  blade sweeps at the deadpoint-stationary omega = V·nx/p. Then
  v_n = -V·nx·(q/p): Fn = k·(q/p)^2·V^2·cos^2C directly. This variant
  gives LESS thrust than the measured Table 9.6 kinematics — net negative
  at our points (the crews sweep ~30 % faster than the deadpoint-stationary
  speed; the prescribed (measured) kinematics are the truth, the slip limit
  is a lower bound; locked by tests/test_research_chain.py::
  test_slip_limit_is_a_lower_bound and ll/tests/test_blade_law.py). NOTE:
  the geometric branch ignores the passed omega (the law prescribes its own
  deadpoint omega); the physiology planning (ll/rower.py closed forms) and
  the rigid-oar reference model use the actual-turning-point forms only.

Cant (the LL gates — docs/VALIDATION.md): a canted rig (the Mark IIb's 18.4-deg sweep-plane
tilt) reduces the horizontal components of the blade-face normal by
cos(phi): the ship's flow on the blade shrinks (vn = V·cosC·cos(phi) -
l_cp·omega) — the blade outruns the water more easily — and the thrust
carries the same factor. Identity at phi = 0 (Olympias).
"""

from __future__ import annotations

import math

from common.chain import CN, RHO

# The (q/p)^2 turning-point law's interpretation switch (the OQ18 note (common/chain.py), task I):
#   "actual"   — the kinematic turning point (p = V·nx/omega): IDENTICAL to
#                the flat-plate law (the locked identity) — the default, the
#                physics the validated chain prescribes.
#   "geometric" — Shaw's appendix d-formula slip limit: OFF by default — it
#                contradicts the measured Table 9.6 kinematics (less
#                thrust, negative at our points; lower bound, locked).
TURNING_POINT: str = "actual"

# The macon-polars variant (the Rev F B2 item): the report's
# Caplan-Gardiner approximations C_L = sin(2a), C_D = 2 sin^2 a — the
# NORMAL-component form (the lift's normal share + the drag's normal
# share, the direction along the blade normal — the full vector's
# refinement noted). Measured at the trireme's working angles (54-58
# deg): the lift is ~55 % of the total force and the polar's normal
# coefficient 2 sin a is 1.37x the flat plate's 1.8 sin^2 a — NOT
# negligible; the chain's calibrated C_N·A product absorbs the
# shortfall (the A5 register). OFF by default.
BLADE_POLAR: bool = False


def _d_turning_point(C: float, B: float) -> float:
    """Shaw's appendix d-formula: tip -> turning-point distance in plan (m).

    d = 0.953·sin[120(C_shaw - A)/B + 30 deg], C_shaw the angle of attack
    from the keel (A at the catch). With C here from athwartships and the
    stroke symmetric about athwartships (C_shaw - A = B/2 - C):
    d = 0.953·cos(120·C/B) — 0.476 m at catch/finish, 0.953 m at mid.
    C, B in radians (the 120·C/B ratio is angle-unit-free)."""
    return 0.953 * math.cos(120.0 * C / B)


def blade_consts(rig: dict) -> tuple:
    """The precomputed blade-law constants for one rig (the hot path).
    tuple: (lin, l_cp, k = 0.5·rho·area·CN, cos(cant), slip, sweep rad).
    `rig` is a shared research dict — never mutate it; pass the tuple to
    blade_force(..., bc=...) to skip the per-call derivations."""
    lin = rig["lin"]
    return (
        lin,
        rig["lout"] - (rig["blade"] - 0.260),  # blade CP from thole
        0.5 * RHO * rig["area"] * CN,
        math.cos(math.radians(rig.get("cant", 0.0))),
        rig.get("slip", 1.0),
        math.radians(rig["sweep"]),
    )


def blade_force(
    C: float,
    omega: float,
    V: float,
    rig: dict,
    immersed: bool = True,
    flow: tuple | None = None,
    bc: tuple | None = None,
) -> dict:
    """Blade force at oar angle C (rad) and angular rate omega (rad/s, + = bowward),
    hull speed V (m/s). Returns vn, Fn, Fx, Fy, Fh (N) and the law's
    turning-point geometry p, q (m; None when undefined).

    flow: the per-station layer's ship state (u, v, r, x, y) — the
    blade's normal flow then includes the ship's rotation and sway at
    the station (ll/stations.py, the Rev F A1 item): vn = (u - r·y)·nx
    + (v + r·x)·ny + l_cp·omega. None keeps the base law (the hull
    speed only).

    bc: the precomputed constants (blade_consts) — the per-step hot
    path passes them to skip the per-call derivations; None computes
    them here (the tests' path).

    Evaluates the (q/p)^2 turning-point law at the interpretation selected
    by TURNING_POINT (module constant, see the module docstring)."""
    if not immersed:
        return {
            "vn": 0.0,
            "Fn": 0.0,
            "Fx": 0.0,
            "Fy": 0.0,
            "Fh": 0.0,
            "p": None,
            "q": None,
        }
    if bc is None:
        bc = blade_consts(rig)
    lin, l_cp, k, cf, slip, B = bc
    nx, ny = math.cos(C) * cf, -math.sin(C) * cf
    if TURNING_POINT == "geometric":
        # the appendix d-formula turning point + the deadpoint-stationary
        # omega: v_n = -slip·V·nx·(q/p) — the (q/p)^2 law directly
        # (diagnostic only; OFF by default)
        p = rig["lout"] / math.cos(math.radians(30.0)) - _d_turning_point(C, B)
        q = l_cp - p
        vn = -(V * nx * slip) * (q / p)
    else:
        # the ACTUAL turning point: p = -V·nx/omega (omega < 0 during the
        # drive — the point where the blade's speed equals the water's
        # flow; slip is a force-side correction, so it does not move the
        # turning point), q = l_cp - p, vn = slip·omega·q =
        # slip·(V·nx - l_cp·|omega|) — the flat-plate form (the locked
        # identity); the per-station flow replaces the bare hull speed
        if flow is not None:
            u, v, r, x, y = flow
            vn = ((u - r * y) * nx + (v + r * x) * ny + l_cp * omega) * slip
        else:
            vn = (V * nx + l_cp * omega) * slip
        p = -V * nx / omega if abs(omega) > 1e-12 else None
        q = l_cp - p if p is not None else None
    if BLADE_POLAR:
        # the macon polars' normal-component form: Fn = 0.5 rho A |v|^2
        # (C_L cos a + C_D sin a) = 0.5 rho A 2 |v| |vn| (the 2 sin a
        # identity), with |v| = sqrt(vn^2 + vt^2) and vt the flow's
        # along-the-face projection (the blade's own motion is normal)
        if flow is not None:
            u, v, r, x, y = flow
            vt = (u - r * y) * math.sin(C) + (v + r * x) * math.cos(C)
        else:
            vt = V * math.sin(C)
        vm = math.hypot(vn, vt)
        Fn = k * (2.0 / CN) * vm * vn * slip
    else:
        Fn = k * abs(vn) * vn
    Fx = -Fn * nx  # force on hull, along keel
    Fy = -Fn * ny
    Fh = abs(Fn) * l_cp / lin
    return {"vn": vn, "Fn": Fn, "Fx": Fx, "Fy": Fy, "Fh": Fh, "p": p, "q": q}
