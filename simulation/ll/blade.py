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

TWO turning-point interpretations (the oQ-18 diagnosis, plan §15.2; the
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

Cant (plan §16.1): a canted rig (the Mark IIb's 18.4-deg sweep-plane
tilt) reduces the horizontal components of the blade-face normal by
cos(phi): the ship's flow on the blade shrinks (vn = V·cosC·cos(phi) -
l_cp·omega) — the blade outruns the water more easily — and the thrust
carries the same factor. Identity at phi = 0 (Olympias).
"""

from __future__ import annotations

import math

from common.chain import CN, RHO

# The (q/p)^2 turning-point law's interpretation switch (plan §15.2, task I):
#   "actual"   — the kinematic turning point (p = V·nx/omega): IDENTICAL to
#                the flat-plate law (the locked identity) — the default, the
#                physics the validated chain prescribes.
#   "geometric" — Shaw's appendix d-formula slip limit: OFF by default — it
#                contradicts the measured Table 9.6 kinematics (less
#                thrust, negative at our points; lower bound, locked).
TURNING_POINT = "actual"


def _d_turning_point(C: float, B: float) -> float:
    """Shaw's appendix d-formula: tip -> turning-point distance in plan (m).

    d = 0.953·sin[120(C_shaw - A)/B + 30 deg], C_shaw the angle of attack
    from the keel (A at the catch). With C here from athwartships and the
    stroke symmetric about athwartships (C_shaw - A = B/2 - C):
    d = 0.953·cos(120·C/B) — 0.476 m at catch/finish, 0.953 m at mid.
    C, B in radians (the 120·C/B ratio is angle-unit-free)."""
    return 0.953 * math.cos(120.0 * C / B)


def blade_force(C: float, omega: float, V: float, rig: dict,
                immersed: bool = True) -> dict:
    """Blade force at oar angle C (rad) and angular rate omega (rad/s, + = bowward),
    hull speed V (m/s). Returns vn, Fn, Fx, Fy, Fh (N) and the law's
    turning-point geometry p, q (m; None when undefined).

    Evaluates the (q/p)^2 turning-point law at the interpretation selected
    by TURNING_POINT (module constant, see the module docstring)."""
    if not immersed:
        return dict(vn=0.0, Fn=0.0, Fx=0.0, Fy=0.0, Fh=0.0, p=None, q=None)
    lin = rig["lin"]
    l_cp = rig["lout"] - (rig["blade"] - 0.260)   # blade CP from thole
    cf = math.cos(math.radians(rig.get("cant", 0.0)))
    nx, ny = math.cos(C) * cf, -math.sin(C) * cf
    slip = rig.get("slip", 1.0)
    if TURNING_POINT == "geometric":
        # the appendix d-formula turning point + the deadpoint-stationary
        # omega: v_n = -slip·V·nx·(q/p) — the (q/p)^2 law directly
        # (diagnostic only; OFF by default)
        B = math.radians(rig["sweep"])
        p = rig["lout"] / math.cos(math.radians(30.0)) - _d_turning_point(C, B)
        q = l_cp - p
        vn = -(V * nx * slip) * (q / p)
    else:
        # the ACTUAL turning point: p = -V·nx/omega (omega < 0 during the
        # drive — the point where the blade's speed equals the water's
        # flow; slip is a force-side correction, so it does not move the
        # turning point), q = l_cp - p, vn = slip·omega·q =
        # slip·(V·nx - l_cp·|omega|) — the flat-plate form (the locked
        # identity)
        vn = (V * nx + l_cp * omega) * slip
        p = -V * nx / omega if abs(omega) > 1e-12 else None
        q = l_cp - p if p is not None else None
    Fn = 0.5 * RHO * rig["area"] * CN * abs(vn) * vn
    Fx = -Fn * nx                                 # force on hull, along keel
    Fy = -Fn * ny
    Fh = abs(Fn) * l_cp / lin
    return dict(vn=vn, Fn=Fn, Fx=Fx, Fy=Fy, Fh=Fh, p=p, q=q)
