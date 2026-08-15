"""The HL's response curves — the only numbers the fast ship knows.

The fast ship (hl/ship.py) reads everything through a Calibration: the
equilibrium-speed table, the steering diameters, the approach constants
and the crew-tank parameters. The ship hardcodes no number of its own.

bootstrap() — the provisional curve set, assembled from the validated chain
anchors and direct LL measurements (each constant below cites its
measurement). hl/calibrate.py regenerates the same structure from LL
protocols and writes a JSON that curves.load() reads; default() picks the
pinned latest calibration file, falling back to the bootstrap until the
first calibration run. The ship is agnostic to the source.

Units: kt inside the tables; m/s at the API boundary.
"""

from __future__ import annotations

import math
from pathlib import Path

from common.chain import CN, KT, RHO, RIGS, VESSELS
from ll.rower import HOLD_FRAC, P_CRIT, PRESSURE, TAU, W_MAX

# ---------------------------------------------------------------------------
# Bootstrap tables — measured from the current LL (the HL build session;
# ll/hull.equilibrium_speed and ll/ship runs, see the calibration plan §19).
# Calibration pending: these are provisional, labelled, never silent.
# ---------------------------------------------------------------------------

# V* over rate, kt: spoude, full W', 170 oars, hull = 1.0.
# At cruise no cap binds, so spoude + full W' == the bare commanded oar that
# ll.hull.equilibrium_speed simulates (its V* values, measured directly).
VSTAR_RATES = [8.0, 12.0, 16.0, 20.0, 24.0, 25.5, 28.8, 32.3, 36.0, 40.0,
               44.5, 50.0]
VSTAR_KT = [5.07, 5.55, 5.97, 6.356, 6.742, 6.888, 7.216, 7.578, 7.981,
            8.448, 8.540, 9.80]

# The pressure rows, kt — LL ship runs (settled, 1 Hz tail-mean over the
# final 60 s — a single sample would be biased by the surge ripple ±0.1 kt):
# steady 0.7, fast 0.85. Measured, not a power-law guess: the thrust-vs-
# handle-force relation is strongly nonlinear (steady lands ~0.74-0.78 of
# the spoude V*). Recorded as printed, including the high-rate quirks.
PRESSURE_RATES = [25.5, 28.8, 32.3, 36.0, 44.5]
VSTEADY_KT = [5.10, 5.60, 6.03, 6.23, 6.28]
VFAST_KT = [5.46, 5.87, 6.13, 6.23, 6.41]

# The empty row, kt: spoude with W' preset at zero (the P_crit-limited
# plan) — the level a spoude burst fades to (~6.1-6.4 kt, not the 7.0 kt
# the 80 W handle-power anchor suggests: the cap binds below that level).
VEMPTY_RATES = [25.5, 28.8, 36.0, 44.5]
VEMPTY_KT = [6.11, 6.30, 6.32, 6.36]

# One side stopped, straight-line equilibria, kt — LL ship runs, tail-mean.
# The held-blade brake bites hard: ~3.6-3.8 kt at spoude, NOT the 0.92 x V*
# the no-brake 85-oar equilibrium would suggest. The back rows: the reversed
# oar degenerates to the hold-brake at speed (>= 30 spm) but collapses at
# low rates (the astern-thrust/brake interplay — 1.9 kt at 24 spm spoude,
# 0.9 at steady). The steady rows measured at 0.7 (the ratio scaling would
# be wrong — the brake dominates at low speeds).
VASYM_RATES = [24.0, 30.0, 36.0]
VASYM_KT = [3.58, 3.73, 3.76]
VASYM_STEADY_KT = [2.88, 3.33, 3.71]
VBACK_RATES = [24.0, 30.0, 36.0, 44.5]
VBACK_KT = [1.87, 3.73, 3.76, 3.69]
VBACK_STEADY_KT = [0.91, 1.29, 3.71, 3.71]

# Steering diameters, m (ll/run_turn.py, current LL):
#   rudder family (both sides rowing): 1/D linear in helm_frac through
#     (0.0 -> straight), (22.5/67.5 = 0.3333 -> 117.4 m, the F1 scenario) and
#     (1.0 -> 89.7 m, G1).
#   oar family (one side hold or back — the LL measures the same diameter for
#     both, backing degenerates to the hold-brake at speed): no helm -> 126.6 m,
#     full helm on the held side -> 67.7 m (the tightest turn).
D_RUDDER = [(0.0, math.inf), (0.3333, 117.4), (1.0, 89.7)]
D_OAR = [(0.0, 126.6), (1.0, 67.7)]

# Approach time constants, s. tau_surge: fitted to the LL crewed rest-start
# (6.0 kt @ 30 s, 6.75 @ 60 s at 28.8 spm spoude). tau_turn: fitted so the
# HL's first-order yaw lag reproduces the LL's path-measured turn diameters
# (the lag inflates |y| at 180 deg; tau 8.5 s — the LL's true omega build-up
# — overshoots the D gate by ~7 %, tau 4.0 s lands inside it; the LL's
# sway-coupled build-up is not a pure lag — documented HL-loose).
TAU_SURGE = 20.0
TAU_TURN = 4.0

# The tank nets, W/man (+ = drain, - = refill), measured from LL runs at
# the anchor levels (the settled speed, tank preset low, short window): the
# spoude drains {25.5: +37.0, 28.8: +53.1, 36: +90.1, 44.5: +130.4} measured
# earlier; steady/fast measured now. The nets replace the chain-law + flip
# estimate (the harness fatigue gate: the commanded-omega flip overestimates
# the LL's actual flip — the achieved omega is lower — and the LL's refill
# runs ~25 % faster than the estimate). The fast 32.3/36 drains and the
# balanced 44.5 points recorded as measured.
NET_RATES = [25.5, 28.8, 32.3, 36.0, 44.5]
NET_SPOUDE = [37.0, 53.1, 68.4, 90.1, 130.4]   # 32.3 interpolated
NET_STEADY = [-30.7, -16.8, -0.3, +17.9, 0.0]
NET_FAST = [-20.3, -3.7, +16.0, +1.4, 0.0]

# the rest refill: the tank's cap (W_max / tau = 41.7 W/man)
NET_REST = -41.7


def _pwl(xs, ys, x):
    """Piecewise-linear interpolation with flat clamps."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if x <= xs[i + 1]:
            f = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + f * (ys[i + 1] - ys[i])
    raise AssertionError


def _d_inv_lin(points, frac):
    """Turn diameter from 1/D linear in helm_frac through (frac, D) points;
    clamped at the end points (a (0.0, inf) point means midship = straight)."""
    if frac <= points[0][0]:
        return points[0][1]
    if frac >= points[-1][0]:
        return points[-1][1]
    for i in range(len(points) - 1):
        f0, d0 = points[i]
        f1, d1 = points[i + 1]
        if frac <= f1:
            inv = (1.0 / d1 - 1.0 / d0) * (frac - f0) / (f1 - f0) + 1.0 / d0
            return 1.0 / inv
    raise AssertionError


class Calibration:
    """One curve set for the fast ship. All lookups are deterministic,
    piecewise-linear with flat clamps; meta carries the provenance label.

    The constructor takes the table dict in the calibration-file schema
    (hl/calibrate.py writes it; bootstrap() and load() build the same
    structure) — the ship is agnostic to the source."""

    def __init__(self, meta, tables, scalars=None):
        t = tables
        self.meta = dict(meta)
        self.vstar_rates = list(t["vstar"]["rates"])
        self._vstar_kt = list(t["vstar"]["kt"])
        self._pressure_rates = list(t["steady"]["rates"])
        self._vsteady_kt = list(t["steady"]["kt"])
        self._vfast_kt = list(t["fast"]["kt"])
        self._vempty_rates = list(t["empty"]["rates"])
        self._vempty_kt = list(t["empty"]["kt"])
        self.vasym_rates = list(t["hold"]["rates"])
        self.vasym_kt = list(t["hold"]["kt"])
        self._vasym_steady = list(t["hold"]["steady_kt"])
        self._vback_rates = list(t["back"]["rates"])
        self._vback_kt = list(t["back"]["kt"])
        self._vback_steady = list(t["back"]["steady_kt"])
        self._net_rates = list(t["net"]["rates"])
        self._net_spoude = list(t["net"]["spoude"])
        self._net_steady = list(t["net"]["steady"])
        self._net_fast = list(t["net"]["fast"])
        self.d_rudder_pts = [tuple(p) for p in t["d_rudder"]]
        self.d_oar_pts = [tuple(p) for p in t["d_oar"]]
        s = scalars or {}
        self.tau_surge = s.get("tau_surge", TAU_SURGE)
        self.tau_turn = s.get("tau_turn", TAU_TURN)
        self.w_max = s.get("w_max", W_MAX)
        self.p_crit = s.get("p_crit", P_CRIT)
        self.tau_w = s.get("tau_w", TAU)
        self.net_rest = s.get("net_rest", NET_REST)
        rig = RIGS["Olympias"]
        self.hold_k = HOLD_FRAC * 0.5 * RHO * rig["area"] * CN  # N/(m/s)^2/oar

    # -- speeds --------------------------------------------------------
    def vstar_kt(self, rate):
        """Equilibrium speed at rate (full crew, spoude, full W'), kt."""
        return _pwl(self.vstar_rates, self._vstar_kt, rate)

    def _row_kt(self, rate, pressure):
        """The pressure row at rate, kt: measured rows at the anchor levels
        (steady 0.7 / fast 0.85 / spoude 1.0), linear between; below steady
        scales from 0 (rest), above spoude clamps."""
        spoude = self.vstar_kt(rate)
        if pressure >= 1.0:
            return spoude
        steady = _pwl(self._pressure_rates, self._vsteady_kt, rate)
        fast = _pwl(self._pressure_rates, self._vfast_kt, rate)
        if pressure <= 0.7:
            return steady * pressure / 0.7
        if pressure <= 0.85:
            return steady + (fast - steady) * (pressure - 0.7) / 0.15
        return fast + (spoude - fast) * (pressure - 0.85) / 0.15

    def vstar(self, rate, pressure, empty=False):
        """Chase target, m/s. empty: W' tank at zero — the target drops to
        the measured P_crit-limited row where it binds below the command."""
        v = self._row_kt(rate, pressure)
        if empty:
            v = min(v, _pwl(self._vempty_rates, self._vempty_kt, rate))
        return v * KT

    def _asym_row(self, rates, kt_row, steady_row, rate, pressure):
        """One-side-stopped row at (rate, pressure), kt: measured at the
        anchor levels (steady 0.7 / spoude 1.0), linear between, scaling
        from 0 below steady."""
        spoude_v = _pwl(rates, kt_row, rate)
        if pressure >= 1.0:
            return spoude_v
        steady_v = _pwl(rates, steady_row, rate)
        if pressure <= 0.7:
            return steady_v * pressure / 0.7
        return steady_v + (spoude_v - steady_v) * (pressure - 0.7) / 0.3

    def vasym(self, rate, pressure, state="hold", empty=False):
        """Chase target with one side stopped, m/s. state: the stopped
        side's oar state (hold or back — measured separately: the reversed
        oar collapses at low rates, the harness caught it)."""
        if state == "back":
            v = self._asym_row(self._vback_rates, self._vback_kt,
                               self._vback_steady, rate, pressure)
        else:
            v = self._asym_row(self.vasym_rates, self.vasym_kt,
                               self._vasym_steady, rate, pressure)
        if empty:
            v = min(v, _pwl(self._vempty_rates, self._vempty_kt, rate))
        return v * KT

    # -- steering ------------------------------------------------------
    def d_rudder(self, helm_frac):
        return _d_inv_lin(self.d_rudder_pts, helm_frac)

    def d_oar(self, helm_frac):
        return _d_inv_lin(self.d_oar_pts, helm_frac)

    # -- crew tank -----------------------------------------------------
    def net(self, rate, pressure):
        """The LL's measured tank net, W/man (+ = drain, - = refill): the
        anchor levels (rest 0 / steady 0.7 / fast 0.85 / spoude 1.0), linear
        in rate and pressure."""
        if pressure <= 0.0:
            return self.net_rest
        spoude = _pwl(self._net_rates, self._net_spoude, rate)
        if pressure >= 1.0:
            return spoude
        steady = _pwl(self._net_rates, self._net_steady, rate)
        fast = _pwl(self._net_rates, self._net_fast, rate)
        if pressure <= 0.7:
            return self.net_rest + (steady - self.net_rest) * pressure / 0.7
        if pressure <= 0.85:
            return steady + (fast - steady) * (pressure - 0.7) / 0.15
        return fast + (spoude - fast) * (pressure - 0.85) / 0.15

    def p_spoude(self, rate):
        """The measured spoude external power per man, W (P_crit + drain)."""
        return P_CRIT + _pwl(self._net_rates, self._net_spoude, rate)

    def resolve_pressure(self, value):
        """Schema pressure value (enum name or number) -> numeric level."""
        if isinstance(value, str):
            return PRESSURE[value]
        return float(value)


def _tables():
    """The bootstrap table set — every number a direct LL measurement
    from the build session (provenance in the table comments above)."""
    return {
        "vstar": {"rates": VSTAR_RATES, "kt": VSTAR_KT},
        "steady": {"rates": PRESSURE_RATES, "kt": VSTEADY_KT},
        "fast": {"rates": PRESSURE_RATES, "kt": VFAST_KT},
        "empty": {"rates": VEMPTY_RATES, "kt": VEMPTY_KT},
        "hold": {"rates": VASYM_RATES, "kt": VASYM_KT,
                 "steady_kt": VASYM_STEADY_KT},
        "back": {"rates": VBACK_RATES, "kt": VBACK_KT,
                  "steady_kt": VBACK_STEADY_KT},
        "d_rudder": D_RUDDER,
        "d_oar": D_OAR,
        "net": {"rates": NET_RATES, "spoude": NET_SPOUDE,
                 "steady": NET_STEADY, "fast": NET_FAST},
    }


def _scalars():
    return dict(tau_surge=TAU_SURGE, tau_turn=TAU_TURN, w_max=W_MAX,
                p_crit=P_CRIT, tau_w=TAU, net_rest=NET_REST)


def bootstrap():
    """The provisional curve set (chain anchors + LL measurements)."""
    return Calibration(
        meta=dict(
            id="bootstrap-0",
            source="validated chain anchors + direct LL measurements "
                   "(HL build session); calibration pending, plan §19",
            note="provisional: pressure rows measured at the anchor levels, "
                 "numeric pressures interpolated; the oar-family helm blend "
                 "and the tau fits land inside the Level-2 gates — refined "
                 "in the calibration run",
        ),
        tables=_tables(), scalars=_scalars(),
    )


def load(path=None):
    """Load a calibration file (hl/calibration/calib_*.json or a path).
    The file schema is the tables/scalars structure above."""
    import json
    if path is None:
        path = Path(__file__).resolve().parent / "calibration" / "latest.json"
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    tables = d["tables"]
    # the D tables store the midship point as null (json has no inf)
    for key in ("d_rudder", "d_oar"):
        tables[key] = [[f, math.inf if d is None else d] for f, d in tables[key]]
    return Calibration(d["meta"], tables, d.get("scalars"))


def default():
    """The ship's default curve set: the pinned latest calibration file,
    falling back to the bootstrap until the first calibration run."""
    try:
        return load()
    except (FileNotFoundError, KeyError):
        return bootstrap()
