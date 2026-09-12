"""Braithwaite workbook physics model — faithful Python port (D1 stage 1).

Source: research/sources/galley-sizing-xlsm/vba_extracted.txt (Modules 7/8),
decoded in research/sources/galley-sizing-xlsm/DECODE.md. This module ports
three routines WITHOUT re-interpretation so the independent model can be
compared against the LL turn-by-turn (D1):

  man_coefficients(...)  <- ManAcceleration: Clarke-Gedling-Hine (1983)
      prime-I derivatives, dimensionalised, + surge added mass
      Xu = 0.04 + 0.06*CB + nonlinear cross-flow yaw damper
      Nr2 = -rho*CN*T*L^4/64 (code value CN = 0.8; the code comment and the
      paper say CN = 0.40 `[?]` — both variants computable here)
  oar_forces(...)        <- OarForces: per-side thrust =
      pressure*(n/2)*maxThrust*(1 - V_local/9.252), V_local = u +/- lever*r;
      yaw moment = +/-thrust*lever; NO sway force
  rudder_forces(...)     <- RudderForces: flat-plate foil CL = sin(2a),
      CD = 2*sin^2(a) (Hoerner) on the relative blade velocity (with the
      yaw-rate terms), + trials parasitic drag2 = 0.5*(137*u^2+0.65*u)
      scaled by SurfaceArea/1.5. PER-RUDDER call (the sheet calls it per
      rudder; ship totals need x2 — documented at the call site).

Transcription notes (fidelity flags):
  - VBA Y+/Z+ = starboard/clockwise; the LL uses port-positive. This module
    keeps VBA signs; callers map them (documented in the test).
  - The sheet's rudder-angle units are not visible in the extraction; the
    VBA calls Cos(angle) directly, so this port takes RADIANS explicitly.
  - RV (skin-friction) and FroudeNumber are computed in the VBA but never
    used downstream; ported as informational returns (rv_unused, froude).
  - ReynoldsNumber uses ShipVelocityX (not the magnitude) verbatim; the
    port guards u <= 0 (returns Cfo = None) where the VBA would error.
  - KinematicViscosity = 1.188e-6 (workbook) differs from our NU = 1.14e-6;
    the workbook value is used here for fidelity.
  - OarForces treats all blades at x = 0 (one longitudinal station).

Stage 2 (not here): time-domain integration (transfer/updata scheme) and
G1/F1/tightest runs against the LL.
"""

from __future__ import annotations

import math

RHO = 1025.0
NU_WORKBOOK = 1.188e-6
KT = 0.51444


# =====================================================================
# ManAcceleration — dimensionalised CGH derivatives + cross-flow damper
# =====================================================================
def man_coefficients(
    lwl: float,
    bwl: float,
    draft: float,
    disp: float,
    iz: float,
    cb: float,
    u: float,
    v: float = 0.0,
    cn: float = 0.8,
) -> dict:
    """Port of ManAcceleration's derivative block. Returns dimensional
    derivatives (SI), the surge mass, the determinant, and Nr2."""
    if lwl <= 0 or bwl <= 0 or draft <= 0 or disp <= 0 or iz <= 0:
        raise ValueError("positive hull particulars required")
    t_l = draft / lwl
    b_l = bwl / lwl
    b_t = bwl / draft
    p_tl = math.pi * t_l**2
    speed = math.hypot(u, v)

    yvdot_nd = -p_tl * (1 + 0.16 * cb * b_t - 5.1 * b_l**2)
    yrdot_nd = -p_tl * (0.67 * b_l - 0.0033 * b_t**2)
    nvdot_nd = -p_tl * (1.1 * b_l - 0.041 * b_t)
    nrdot_nd = -p_tl * (1.0 / 12.0 + 0.017 * cb * b_t - 0.33 * b_l)
    yv_nd = -p_tl * (1 + 0.4 * cb * b_t)
    yr_nd = -p_tl * (-0.5 + 2.2 * b_l - 0.08 * b_t)
    nv_nd = -p_tl * (0.5 + 2.4 * t_l)
    nr_nd = -p_tl * (0.25 + 0.039 * b_t - 0.56 * b_l)

    half_rho = 0.5 * RHO
    yvdot = yvdot_nd * half_rho * lwl**3
    yrdot = yrdot_nd * half_rho * lwl**4
    nvdot = nvdot_nd * half_rho * lwl**4
    nrdot = nrdot_nd * half_rho * lwl**5
    yv = yv_nd * half_rho * speed * lwl**2
    yr = yr_nd * half_rho * speed * lwl**3
    nv = nv_nd * half_rho * speed * lwl**3
    nr = nr_nd * half_rho * speed * lwl**4

    surge_frac = 0.04 + 0.06 * cb
    m_surge = disp * (1 + surge_frac)

    det = (disp - yvdot) * (iz - nrdot) - yrdot * nvdot
    nr2 = -RHO * cn * draft * lwl**4 / 64.0

    return {
        "Yvdot": yvdot,
        "Yrdot": yrdot,
        "Nvdot": nvdot,
        "Nrdot": nrdot,
        "Yv": yv,
        "Yr": yr,
        "Nv": nv,
        "Nr": nr,
        "surge_frac": surge_frac,
        "m_surge": m_surge,
        "det": det,
        "Nr2": nr2,
        "cn": cn,
        "U": speed,
    }


def man_acceleration(
    lwl: float,
    bwl: float,
    draft: float,
    disp: float,
    iz: float,
    cb: float,
    drag: float,
    u: float,
    v: float,
    r: float,
    oar: tuple[float, float, float],
    rud: tuple[float, float, float],
    cn: float = 0.8,
) -> tuple[float, float, float]:
    """Port of ManAcceleration's solve. oar/rud = (X, Y, Z) external
    force/moment triples (VBA signs: Y starboard+, Z clockwise+).
    Returns (u_dot, v_dot, r_dot)."""
    c = man_coefficients(lwl, bwl, draft, disp, iz, cb, u, v, cn)
    if abs(c["det"]) < 1e-5:
        return (0.0, 0.0, 0.0)
    fx = drag + disp * v * r + oar[0] + rud[0]
    fy = c["Yv"] * v + c["Yr"] * r - disp * u * r + oar[1] + rud[1]
    fz = (
        c["Nv"] * v
        + c["Nr"] * r
        + c["Nr2"] * r * abs(r)
        + oar[2]
        + rud[2]
    )
    ax = fx / c["m_surge"]
    ay = ((iz - c["Nrdot"]) * fy + c["Yrdot"] * fz) / c["det"]
    az = (c["Nvdot"] * fy + (disp - c["Yvdot"]) * fz) / c["det"]
    return (ax, ay, az)


# =====================================================================
# OarForces — faithful port (all blades at x = 0)
# =====================================================================
def oar_forces(
    n_oars: float,
    lever: float,
    p_port: float,
    p_star: float,
    max_thrust: float,
    u: float,
    r: float = 0.0,
) -> dict:
    """Returns dict with port/starboard thrust (N), total surge (N) and
    yaw moment (N m, VBA sign: clockwise+). Sway is identically zero."""
    v_port = u - lever * r
    v_star = u + lever * r
    t_port = p_port * 0.5 * n_oars * max_thrust * (1 - v_port / 9.252)
    t_star = p_star * 0.5 * n_oars * max_thrust * (1 - v_star / 9.252)
    return {
        "port": t_port,
        "starboard": t_star,
        "surge": t_port + t_star,
        "yaw": -t_port * lever + t_star * lever,
        "sway": 0.0,
    }


# =====================================================================
# RudderForces — faithful per-rudder port
# =====================================================================
def rudder_forces(
    pos_x: float,
    pos_y: float,
    chord: float,
    area: float,
    angle_rad: float,
    u: float,
    v: float = 0.0,
    r: float = 0.0,
) -> dict:
    """Returns dict with RX (surge, +forward), RY (+starboard), RZ moment
    about CG (clockwise+), plus angle of attack, CL/CD, lift/drag, and the
    unused RV skin-friction value (rv_unused) for fidelity."""
    pos_mag = math.hypot(pos_x, pos_y)
    rvx = u + pos_mag * math.cos(angle_rad) * r
    rvy = v + pos_mag * math.sin(angle_rad) * r
    vmag = math.hypot(rvx, rvy)

    surface = 2.0 * area
    rv_unused = None
    if u > 0:
        rn = u * chord / NU_WORKBOOK
        cfo = 0.075 / (math.log10(rn) - 2.0) ** 2
        rv_unused = 0.5 * RHO * u**2 * surface * cfo

    dx, dy = math.cos(angle_rad), math.sin(angle_rad)
    if vmag == 0:
        aoa = 0.0
    else:
        aoa = math.acos(
            max(-1.0, min(1.0, (rvx * dx + rvy * dy) / vmag))
        )
    if aoa > math.pi / 2:
        aoa = math.pi - aoa
        dx, dy = -dx, -dy

    cd = 2.0 * math.sin(aoa) ** 2
    cl = math.sin(2.0 * aoa)
    lift = 0.5 * RHO * area * vmag**2 * cl
    drag = 0.5 * RHO * area * vmag**2 * cd
    drag2 = 0.5 * (137.0 * u**2 + 0.65 * u) * surface / 1.5
    drag += drag2

    if vmag == 0:
        lx, ly = 0.0, 0.0
        dx_, dy_ = 0.0, 0.0
    else:
        lx = lift * rvy / vmag
        ly = -lift * rvx / vmag
        dx_ = -drag * rvx / vmag
        dy_ = -drag * rvy / vmag
        lmag = math.hypot(lx, ly)
        if lmag > 0:
            th2 = math.acos(
                max(-1.0, min(1.0, (lx * dx + ly * dy) / lmag))
            )
            if th2 > math.pi / 2:
                lx, ly = -lx, -ly
    rx = lx + dx_
    ry = ly + dy_
    rz = ry * pos_x - rx * pos_y
    return {
        "RX": rx,
        "RY": ry,
        "RZ": rz,
        "aoa": aoa,
        "CL": cl,
        "CD": cd,
        "lift": lift,
        "drag": drag,
        "drag2": drag2,
        "rv_unused": rv_unused,
    }


# =====================================================================
# Self-checks (transcription fidelity — no LL involved)
# =====================================================================
def _self_check() -> dict:
    out: dict[str, float] = {}
    # oar law: zero at the 9.252 m/s intercept, 81 N/oar at rest (full crew)
    z = oar_forces(170, 4.8, 1.0, 1.0, 81.0, 9.252)
    out["oar_zero_at_intercept"] = z["surge"]
    r = oar_forces(170, 4.8, 1.0, 1.0, 81.0, 0.0)
    out["oar_rest_total"] = r["surge"]  # 170*81 = 13770
    # rudder: zero angle -> zero lift, pure drag2
    f0 = rudder_forces(-15.0, 0.0, 0.5, 0.75, 0.0, 3.0)
    out["rudder_zero_helm_lift"] = f0["RY"]
    out["rudder_zero_helm_drag"] = -f0["RX"]  # + = resistance
    # symmetric helm sweep sanity: lift grows then falls past 45 deg
    l22 = rudder_forces(-15.0, 0.0, 0.5, 0.75, math.radians(22.5), 3.0)["RY"]
    l67 = rudder_forces(-15.0, 0.0, 0.5, 0.75, math.radians(67.5), 3.0)["RY"]
    out["rudder_lift_22"] = l22
    out["rudder_lift_67"] = l67
    return out


if __name__ == "__main__":
    for k, val in _self_check().items():
        print(f"{k}: {val:.3f}")


# =====================================================================
# Stage 2 — time-domain simulation (sheet integration scheme)
# =====================================================================
# The Manoevering sheet integrates semi-implicit Euler at dt = 1 s
# (verified: E139 = E138 + R138*1, positions advance with end-of-step
# velocity). Drag = piecewise trials fit (DECODE Powering; sheet K column
# matches it to 0.2-0.7% — table-lerp vs formula ambiguity, immaterial).

def _trials_table_kt() -> list[float]:
    """Integer-kt trials table (0..20 kt) from the documented piecewise fit
    (DECODE Powering: 40.2V^2 (1-6), 75.2V^2-1560 (7-8), 88.6V^2-2640
    (9-10), V in kt) — the sheet's G column matches these knot values
    exactly, and its Drag column matches linear interpolation between
    them to ~0.2% (table-lerp vs direct-formula ambiguity, immaterial)."""
    table = []
    for v in range(21):
        if v <= 6:
            table.append(40.2 * v * v)
        elif v <= 8:
            table.append(75.2 * v * v - 1560.0)
        else:
            table.append(88.6 * v * v - 2640.0)
    return table


_TRIALS_TABLE = _trials_table_kt()


def trials_drag(u_ms: float) -> float:
    """Bare-hull resistance (N, positive): linear interpolation of the
    integer-kt trials table (the sheet's method)."""
    vkt = abs(u_ms) / KT
    if vkt >= 20.0:
        return _TRIALS_TABLE[20]
    lo = int(vkt)
    frac = vkt - lo
    return _TRIALS_TABLE[lo] * (1 - frac) + _TRIALS_TABLE[lo + 1] * frac


# Sheet inputs (Manoevering B1-B37, Olympias block)
SHEET_INPUTS = {
    "lwl": 32.35,
    "bwl": 3.7042357797642769,
    "draft": 1.15,
    "disp": 45376.946465736604,
    "iz": 5276443.9397432031,
    "cb": 0.32118549392675172,
    "n_oars": 170,
    "lever": 5.2,
    "n_rudders": 2,
    "rudder_area": 0.75,
    "rudder_chord": 0.5,
    "rudder_pos_x": -15.0,
    "rudder_pos_y": 0.0,
    "max_thrust": 80.645161290322577,
}


def simulate(
    u0: float,
    v0: float = 0.0,
    r0: float = 0.0,
    p_port: float = 0.0,
    p_star: float = 1.0,
    rudder_rad: float = -1.1693705988362009,
    t_end: float = 120.0,
    dt: float = 1.0,
    cn: float = 0.8,
    inputs: dict | None = None,
) -> dict:
    """Integrate the VBA model (semi-implicit Euler). Rudder called
    per-rudder and doubled (matches the sheet to 0.6% at t=0).
    Angles: VBA signs (Y starboard+, Z clockwise+). Returns timelines."""
    inp = dict(SHEET_INPUTS, **(inputs or {}))
    u, v, r = u0, v0, r0
    x, y, psi = 0.0, 0.0, 0.0
    ts, us, vs, rs, xs, ys, psis = [], [], [], [], [], [], []
    t = 0.0
    while t <= t_end + 1e-9:
        ts.append(t)
        us.append(u)
        vs.append(v)
        rs.append(r)
        xs.append(x)
        ys.append(y)
        psis.append(psi)
        of = oar_forces(
            inp["n_oars"], inp["lever"], p_port, p_star,
            inp["max_thrust"], u, r,
        )
        rf = rudder_forces(
            inp["rudder_pos_x"], inp["rudder_pos_y"], inp["rudder_chord"],
            inp["rudder_area"], rudder_rad, u, v, r,
        )
        oar = (of["surge"], of["sway"], of["yaw"])
        rud = (
            inp["n_rudders"] * rf["RX"],
            inp["n_rudders"] * rf["RY"],
            inp["n_rudders"] * rf["RZ"],
        )
        ax, ay, az = man_acceleration(
            inp["lwl"], inp["bwl"], inp["draft"], inp["disp"], inp["iz"],
            # the sheet passes Drag NEGATIVE (aft force, K column) despite
            # the VBA header calling it "(positive)" — sheet rules here
            inp["cb"], -trials_drag(u), u, v, r, oar, rud, cn,
        )
        u += ax * dt
        v += ay * dt
        r += az * dt
        vx0 = u * math.cos(psi) - v * math.sin(psi)
        vy0 = u * math.sin(psi) + v * math.cos(psi)
        x += vx0 * dt
        y += vy0 * dt
        psi += r * dt
        t += dt
    return {
        "t": ts, "u": us, "v": vs, "r": rs, "x": xs, "y": ys, "psi": psis,
    }


if __name__ == "__main__":
    for k, val in _self_check().items():
        print(f"{k}: {val:.3f}")
