"""Flat-plate blade-force law (the rigid-oar convention, time-stepped).

Frame: x = along keel, bow = +x; C = oar angle from athwartships, + = blade
swept toward bow; nx = cos C, ny = -sin C is the blade-face normal.

The force on the water is Fn = 0.5 rho A C_N |v_n| v_n along the normal,
opposing the normal flow v_n; the reaction on the hull is -Fn (component Fx
along the keel). Handle force from the 2nd-class-lever balance about the
thole: Fh = |Fn| * l_cp / lin (massless lever — the inertia layer lands
after Gate 1, per the plan §5).
"""

from __future__ import annotations

import math

from common.chain import CN, RHO


def blade_force(C: float, omega: float, V: float, rig: dict,
                immersed: bool = True) -> dict:
    """Blade force at oar angle C (rad) and angular rate omega (rad/s, + = bowward),
    hull speed V (m/s). Returns vn, Fn, Fx, Fy, Fh (N).

    Cant (plan §16.1): a canted rig (the Mark IIb's 18.4-deg sweep-plane
    tilt) reduces the horizontal components of the blade-face normal by
    cos(phi): the ship's flow on the blade shrinks (vn = V·cosC·cos(phi) -
    l_cp·omega) — the blade outruns the water more easily — and the thrust
    carries the same factor. Identity at phi = 0 (Olympias)."""
    if not immersed:
        return dict(vn=0.0, Fn=0.0, Fx=0.0, Fy=0.0, Fh=0.0)
    lin = rig["lin"]
    l_cp = rig["lout"] - (rig["blade"] - 0.260)   # blade CP from thole
    cf = math.cos(math.radians(rig.get("cant", 0.0)))
    nx, ny = math.cos(C) * cf, -math.sin(C) * cf
    vn = (V * nx + l_cp * omega) * rig.get("slip", 1.0)
    Fn = 0.5 * RHO * rig["area"] * CN * abs(vn) * vn
    Fx = -Fn * nx                                 # force on hull, along keel
    Fy = -Fn * ny
    Fh = abs(Fn) * l_cp / lin
    return dict(vn=vn, Fn=Fn, Fx=Fx, Fy=Fy, Fh=Fh)
