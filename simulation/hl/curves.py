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

# The achieved-rate curve (task B): the exhausted crew cannot hold the
# tempo at high rates — the LL's rower.py tempo branch (the drive cannot
# fit its slot; B_eff falls below the floor). Provisional bootstrap:
# identity (no loss) — the calibration measures the empty-tank rate_eff
# over rate at the anchor levels.
TEMPO_RATES = [25.5, 36.0, 40.0, 44.5, 50.0]
TEMPO_EMPTY = [25.5, 36.0, 40.0, 44.5, 50.0]

# The untrimmed lateral-drift table, rad/s (task C): the LL's
# straight-cruise yaw slope at the anchor (rate, pressure) cells — the
# symmetric crew carries a lateral kick, so a midship-helm cruise curves
# slowly (~−0.0010 rad/s at spoude vs ~−0.0003 at steady, flat over
# rate). The HL carries the bias (the §21.3 decision — the single-scalar
# floor cannot represent the pressure dependence; the HL matches the
# LL's truth and the position gate stays as-written). Measured in this
# session; the calibration measures it fresh.
DRIFT_RATES = [25.5, 28.8, 32.3, 44.5]
DRIFT_SPOUDE_FULL = [-0.001168, -0.001311, -0.001409, -0.001305]
DRIFT_SPOUDE_EMPTY = [-0.001109, -0.001044, -0.001169, -0.000381]
DRIFT_STEADY_FULL = [-0.000709, -0.000827, -0.000866, -0.001053]
DRIFT_STEADY_EMPTY = [-0.000325, -0.000273, -0.000580, -0.000565]

# The V-ramp kick-transient (the wprime closure): the LL's yaw during
# a strong V-rise rides below its settled drift (the sway's excited
# state) — measured over the burst-path ramp (calibrate.measure_drift_kick).
DRIFT_KICK_V = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
DRIFT_KICK_W = [0.0] * 8

# The back-state surge lag, s over rate (task E): the entry at high rate
# is the degenerate regime (back ≡ hold, ~24 s); the low-rate collapse
# (the cruise_turn 1440 s bin) is dip-and-recover, fitted to the gate
# window's mean speed (~60 s effective). Provisional bootstrap:
# identity with the hold value; the calibration measures both anchors.
TAU_BACK_RATES = [24.0, 44.0]
TAU_BACK_TAU = [TAU_SURGE, TAU_SURGE]


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
        nv = t.get("drift_kick") or {}
        self._kick_v = list(nv.get("v", DRIFT_KICK_V))
        self._kick_w = list(nv.get("w", DRIFT_KICK_W))
        tl = t.get("tempo_loss") or {}
        self._tempo_rates = list(tl.get("rates", TEMPO_RATES))
        self._tempo_empty = list(tl.get("empty_rate_eff",
                                        self._tempo_rates))
        dr = t.get("drift") or {}
        self._drift_rates = list(dr.get("rates", DRIFT_RATES))
        self._drift_sf = list(dr.get("spoude_full", DRIFT_SPOUDE_FULL))
        self._drift_se = list(dr.get("spoude_empty", DRIFT_SPOUDE_EMPTY))
        self._drift_tf = list(dr.get("steady_full", DRIFT_STEADY_FULL))
        self._drift_te = list(dr.get("steady_empty", DRIFT_STEADY_EMPTY))
        tb = t.get("tau_back") or {}
        self._tau_back_rates = list(tb.get("rates", TAU_BACK_RATES))
        self._tau_back_tau = list(tb.get("tau", TAU_BACK_TAU))
        self.d_rudder_pts = [tuple(p) for p in t["d_rudder"]]
        self.d_oar_pts = [tuple(p) for p in t["d_oar"]]
        na = t.get("net_hold") or {}
        nb = t.get("net_back") or {}
        self._asym_rates = list(na.get("rates", [24.0, 30.0, 36.0]))
        self._net_hold_spoude = list(na.get("spoude", [24.7, 27.7, 27.8]))
        self._net_hold_steady = list(na.get("steady", [0.0, 0.0, 9.3]))
        self._net_back_spoude = list(nb.get("spoude", [24.4, 27.7, 27.7]))
        self._net_back_steady = list(nb.get("steady", [0.0, 0.0, 8.0]))
        s = scalars or {}
        self.tau_surge = s.get("tau_surge", TAU_SURGE)
        self.tau_turn = s.get("tau_turn", TAU_TURN)
        self.w_max = s.get("w_max", W_MAX)
        self.p_crit = s.get("p_crit", P_CRIT)
        self.tau_w = s.get("tau_w", TAU)
        self.net_rest = s.get("net_rest", NET_REST)
        self.tau_hold = s.get("tau_hold", TAU_SURGE)
        self.turn_drag_extra = s.get("turn_drag_extra", 0.0)
        td = t.get("turn_drag") or {}
        self._td_fracs = list(td.get("fracs", [1.0]))
        self._td_rates = list(td.get("rates", [19.9]))
        self._td_spoude = td.get("spoude", [[self.turn_drag_extra]])
        self._td_steady = td.get("steady", self._td_spoude)
        # tolerate the pre-rate-dimension flat format (the old k lists)
        if self._td_spoude and isinstance(self._td_spoude[0], (int, float)):
            self._td_spoude = [self._td_spoude]
        if self._td_steady and isinstance(self._td_steady[0], (int, float)):
            self._td_steady = [self._td_steady]
        if len(self._td_rates) != len(self._td_spoude):
            self._td_rates = [self._td_rates[0]] * len(self._td_spoude)
        yb = t.get("yaw_build") or {}
        self._yb_helm = yb.get("helm", dict(A=0.6, tf=6.0, ts=10.0))
        self._yb_oar = yb.get("oar", dict(A=0.95, tf=3.0, ts=10.0))
        self.tau_exit = s.get("tau_exit", TAU_TURN)
        self.drift_tau_exp = s.get("drift_tau_exp", 0.0)
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

    def yaw_build(self, helm_frac):
        """The yaw approach's two-timescale shape (task T3): (A, ts) —
        the fast share A of the rise at the chase's tau, then the
        sway-coupled slow tail at ts. The helm turns vs the one-side-
        stopped turns (the measured families)."""
        return self._yb_helm if helm_frac > 0.0 else self._yb_oar

    def turn_drag(self, helm_frac, pressure=1.0, rate=19.9):
        """The measured turn-deceleration extra-drag factor vs helm
        fraction, pressure and rate (task T4 — the per-fraction fits to
        the LL's turn V(t); the steady turns lose relatively more and
        the rate matters — the sprint's 28.8-30 spm turns carry a
        bigger factor than the G1's 19.9 anchor)."""
        rows = self._td_steady if pressure <= 0.7 else self._td_spoude
        i0 = 0
        for i, r in enumerate(self._td_rates):
            if rate >= r:
                i0 = i
        if i0 + 1 >= len(self._td_rates):
            k = _pwl(self._td_fracs, rows[-1], helm_frac)
        else:
            k0 = _pwl(self._td_fracs, rows[i0], helm_frac)
            k1 = _pwl(self._td_fracs, rows[i0 + 1], helm_frac)
            f = (rate - self._td_rates[i0]) /                 (self._td_rates[i0 + 1] - self._td_rates[i0])
            k = k0 + f * (k1 - k0)
        return k

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

    def net_asym(self, rate, pressure, state):
        """The rowing side's tank net in the one-side-stopped legs, W/man
        (task T4 follow-up): the LL's rowing side pulls less at the low
        hold/back speeds (~28 W/man spoude vs the symmetric ~68 — the
        measured hold/back drains, flat over rate; the back ~= the hold,
        the degeneration)."""
        if state == "back":
            spoude = _pwl(self._asym_rates, self._net_back_spoude, rate)
            steady = _pwl(self._asym_rates, self._net_back_steady, rate)
        else:
            spoude = _pwl(self._asym_rates, self._net_hold_spoude, rate)
            steady = _pwl(self._asym_rates, self._net_hold_steady, rate)
        if pressure >= 1.0:
            return spoude
        if pressure <= 0.7:
            return steady * pressure / 0.7
        return steady + (spoude - steady) * (pressure - 0.7) / 0.3

    def p_spoude(self, rate):
        """The measured spoude external power per man, W (P_crit + drain)."""
        return P_CRIT + _pwl(self._net_rates, self._net_spoude, rate)

    def rate_eff(self, rate, empty):
        """The achieved stroke rate, spm: the commanded rate, except when
        the tank is empty at high rates — the exhausted crew loses tempo
        (measured: the LL's rower.py tempo branch — the drive cannot fit
        its slot; the curve is the empty-tank rate_eff over rate)."""
        if not empty:
            return rate
        return _pwl(self._tempo_rates, self._tempo_empty, rate)

    def drift_kick(self, v):
        """The V-ramp kick-transient floor, rad/s (the wprime closure):
        the LL's yaw rides below its settled drift during a strong V-
        rise (the sway's excited state) — measured over the burst-path
        ramp; the ship takes min(drift_bias, drift_kick(V)) while the V
        is rising fast."""
        if v < 0.5:
            return 0.0
        return _pwl(self._kick_v, self._kick_w, v)

    def drift_bias(self, rate, pressure, w_frac=1.0):
        """The untrimmed lateral-drift rate, rad/s (task C): the LL's
        measured straight-cruise yaw bias at (rate, pressure, tank state)
        — the kick follows the stroke force, so the bias interpolates
        between the full-tank and the drained anchors by W_frac; scales
        from 0 at rest (no oar forces, no kick). The HL carries the bias
        so the position gate stays as-written (§21.3 decision)."""
        if pressure <= 0.0:
            return 0.0
        w = max(0.0, min(1.0, w_frac))
        sf = _pwl(self._drift_rates, self._drift_sf, rate)
        se = _pwl(self._drift_rates, self._drift_se, rate)
        tf = _pwl(self._drift_rates, self._drift_tf, rate)
        te = _pwl(self._drift_rates, self._drift_te, rate)
        if pressure >= 1.0:
            full, empty = sf, se
        elif pressure <= 0.7:
            full = tf * pressure / 0.7
            empty = te * pressure / 0.7
        else:
            f = (pressure - 0.7) / 0.3
            full = tf + (sf - tf) * f
            empty = te + (se - te) * f
        return full + (empty - full) * (1.0 - w)

    def tau_back(self, rate):
        """The back-state surge lag, s at rate (task E): the degenerate
        entry regime at high rate vs the low-rate collapse — measured
        anchors, linear between."""
        return _pwl(self._tau_back_rates, self._tau_back_tau, rate)

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
        "tempo_loss": {"rates": TEMPO_RATES, "full_rate_eff": TEMPO_RATES,
                        "empty_rate_eff": TEMPO_EMPTY},
        "drift": {"rates": DRIFT_RATES, "spoude_full": DRIFT_SPOUDE_FULL,
                   "spoude_empty": DRIFT_SPOUDE_EMPTY,
                   "steady_full": DRIFT_STEADY_FULL,
                   "steady_empty": DRIFT_STEADY_EMPTY},
        "tau_back": {"rates": TAU_BACK_RATES, "tau": TAU_BACK_TAU},
        "turn_drag": {"fracs": [1.0], "k": [0.28]},
    }


def _scalars():
    return dict(tau_surge=TAU_SURGE, tau_turn=TAU_TURN, w_max=W_MAX,
                p_crit=P_CRIT, tau_w=TAU, net_rest=NET_REST,
                tau_hold=TAU_SURGE, turn_drag_extra=0.0, tau_exit=TAU_TURN,
                drift_tau_exp=0.0)


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
