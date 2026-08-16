#!/usr/bin/env python3
"""The HL calibration run (the calibration protocol — simulation/AGENTS.md) — measure the response curves from
the LL and write hl/calibration/calib_<id>.json (+ latest.json).

Every table is produced by an LL protocol — nothing is hand-entered. The
residuals (fit quality per table) feed the tolerance labels. The loop:
run this, then harness/run_validation.py; if a gate fails, the trigger
table in the calibration protocol (simulation/AGENTS.md) names the adjustment; repeat until the HL matches
the LL. The calibration file records its LL commit — when the LL gains
fidelity, re-run and re-validate.

Usage (from simulation/):
    python3 hl/calibrate.py            # the full run (~10 min, LL at dt 0.05)
"""

import datetime
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT
from hl.curves import Calibration, _scalars, _tables
from ll.hull import equilibrium_speed
from ll.ship import Ship as LLShip, rate_for_speed

DT = 0.05                 # the LL's comparison dt
OUT_DIR = Path(__file__).resolve().parent / "calibration"

# protocol grids (the schema's anchor levels; numeric pressures interpolate)
VSTAR_GRID = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 25.5,
              28.8, 30.0, 32.3, 34.0, 36.0, 38.0, 40.0, 42.0, 44.5, 46.0,
              48.0, 50.0]
PRESSURE_RATES = [24.0, 25.5, 27.0, 28.8, 30.0, 32.3, 34.0, 36.0, 40.0, 44.5]
EMPTY_RATES = [25.5, 27.0, 28.8, 30.0, 32.3, 34.0, 36.0, 44.5]
ASYM_RATES = {"hold": [24.0, 30.0, 36.0], "back": [24.0, 30.0, 36.0, 44.5]}
NET_RATES = [25.5, 28.8, 32.3, 36.0, 44.5]
TEMPO_RATES = [25.5, 36.0, 40.0, 44.5, 50.0]
DRIFT_RATES = [25.5, 28.8, 32.3, 44.5]


def log(msg):
    print(msg, flush=True)


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, cwd=str(OUT_DIR
                             .parents[1]))
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# protocols
# ---------------------------------------------------------------------------
def measure_vstar(rates):
    """V* over rate (spoude, full W', 170 oars) — the bare commanded oar's
    mean-force equilibrium (ll.hull.equilibrium_speed)."""
    kt, t0 = [], time.time()
    for r in rates:
        kt.append(equilibrium_speed("Olympias", r)["V"] / KT)
    log(f"  vstar: {len(rates)} rates, {time.time()-t0:.0f} s")
    return dict(rates=rates, kt=kt)


def _settle_tail(ship, t_end=420.0, tail=60):
    """Run from 0.9·V*, return (tail mean kt, tail std kt). The tail mean
    is the row value — a single sample would be biased by the surge ripple
    (±0.1 kt); the std is the measurement's uncertainty. t_end: 120 s for
    the pressure rows (the full-W' command speed — a long settle would
    drain the tank at the draining points); 420 s for the drained-state
    rows (empty, asym)."""
    ship.V = 0.9 * equilibrium_speed("Olympias", ship.rate)["V"]
    t, next_s, Vs = 0.0, 0.0, []
    while t < t_end:
        ship.step(DT)
        t += DT
        if t >= next_s:
            Vs.append(ship.V / KT)
            next_s += 1.0
    tail_vs = Vs[-tail:]
    mean = sum(tail_vs) / len(tail_vs)
    std = (sum((v - mean) ** 2 for v in tail_vs) / len(tail_vs)) ** 0.5
    return mean, std


def measure_pressure_rows(rates, pressure):
    """The pressure row: the full-W' command speed (short runs — the
    draining points would empty the tank in a long settle; the empty row
    is the drained state's speed)."""
    kt, stds, t0 = [], [], time.time()
    for r in rates:
        v, s = _settle_tail(LLShip(rate=r, pressure=(pressure, pressure)),
                            t_end=120.0)
        kt.append(round(v, 3))
        stds.append(round(s, 3))
    log(f"  {pressure} row: {len(rates)} rates, {time.time()-t0:.0f} s")
    return dict(rates=rates, kt=kt, std_kt=stds)


def measure_empty(rates):
    """The P_crit-limited row: spoude with the tiers' W preset at zero."""
    kt, t0 = [], time.time()
    for r in rates:
        ship = LLShip(rate=r)
        for crew in ship.crew.values():
            for tier in crew.tiers.values():
                tier.W = 0.0
        v, _ = _settle_tail(ship)
        kt.append(round(v, 3))
    log(f"  empty row: {len(rates)} rates, {time.time()-t0:.0f} s")
    return dict(rates=rates, kt=kt)


def measure_asym(state, rates):
    """One-side-stopped rows (row + hold/back) at spoude and steady."""
    kt, steady_kt, t0 = [], [], time.time()
    for r in rates:
        v, _ = _settle_tail(LLShip(rate=r, oar_state=("row", state)))
        kt.append(round(v, 3))
        v, _ = _settle_tail(LLShip(rate=r, oar_state=("row", state),
                                   pressure=("steady", "steady")))
        steady_kt.append(round(v, 3))
    log(f"  {state} rows: {len(rates)} rates, {time.time()-t0:.0f} s")
    return dict(rates=rates, kt=kt, steady_kt=steady_kt)


def _tank_net(rate, pressure, settle=60.0, window=60.0, preset=None,
              from_rest=False):
    """The LL's tank net (W/man; + drain, - refill): the least-squares
    slope of W_frac(t) over the unsaturated part of a 1 Hz trace. A
    fixed-window slope is biased when the tank hits its 0/1 caps
    mid-window (the first calibration run measured the spoude drains as
    ~0 because the settle had already emptied the tank).
    settle/window: the spoude drains use a short settle (the tank must
    survive it); the refills use a long one (the speed must settle) with
    a low preset. from_rest: the spoude drains in the scripts' context
    (spoude phases mostly start from rest, where the drain runs ~6 %
    higher — the blade sees still water) — measure from V0 = 0, not from
    0.9·V*."""
    ship = LLShip(rate=rate, pressure=(pressure, pressure))
    ship.V = 0.0 if from_rest else 0.9 * equilibrium_speed("Olympias",
                                                          rate)["V"]
    if preset is not None:
        for crew in ship.crew.values():
            for tier in crew.tiers.values():
                tier.W = preset * tier.W_max
    t, next_s, Vs = 0.0, 0.0, []
    while t < settle + window:
        ship.step(DT)
        t += DT
        if t >= next_s:
            Vs.append(ship.crew["port"].W_frac)
            next_s += 1.0
    ws = Vs[int(settle):]
    ts, us = [], []
    for i, w in enumerate(ws):
        if 0.02 < w < 0.98:            # the unsaturated part only
            ts.append(float(i))
            us.append(w)
    if len(ts) < 10:
        return 0.0
    n = len(ts)
    mt = sum(ts) / n
    mu = sum(us) / n
    slope = sum((t_ - mt) * (u - mu) for t_, u in zip(ts, us)) \
        / sum((t_ - mt) ** 2 for t_ in ts)
    return -slope * 5000.0


def _tank_net_directed(rate, pressure):
    """Probe the direction first: 30 s from full — a drain shows a slope,
    a refill is stuck at the W' cap. Then measure with the right preset
    (the draining points would empty a low-preset tank during the settle;
    the refilling points would cap a full one)."""
    probe = _tank_net(rate, pressure, settle=10.0, window=30.0)
    if probe > 2.0:                          # a drain
        return _tank_net(rate, pressure, settle=15.0, window=90.0)
    return _tank_net(rate, pressure, preset=0.10, settle=90.0, window=90.0)


def measure_nets(rates):
    """The tank nets at the anchor levels: spoude drains (from full, short
    settle, measured from the rest start — the scripts' spoude phases
    mostly start from rest), steady/fast probed then measured with the
    right preset."""
    spoude, steady, fast, t0 = [], [], [], time.time()
    for r in rates:
        spoude.append(round(_tank_net(r, "spoude", settle=15.0, window=90.0,
                                      from_rest=True), 1))
        steady.append(round(_tank_net_directed(r, "steady"), 1))
        fast.append(round(_tank_net_directed(r, "fast"), 1))
    log(f"  nets: {len(rates)} rates x 3 levels, {time.time()-t0:.0f} s")
    return dict(rates=rates, spoude=spoude, steady=steady, fast=fast)


def measure_drift_kick():
    """The V-ramp kick-transient (the wprime closure): during a strong
    V-rise the LL's yaw rides well below its settled drift — the sway's
    excited state (the burst-path: the tank drains through the ramp, so
    the W-sweep is built in). The curve: the mean omega at the V bins
    over the burst's ramp window. The HL applies it as the drift-target
    floor while the V is rising fast."""
    ship = LLShip(rate=44.5, pressure=("spoude", "spoude"))
    t, rows = 0.0, []
    while t < 180.0:
        ship.step(DT)
        t += DT
        rows.append((ship.V, ship.omega))
    v_bins = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    ws = []
    for b in v_bins:
        s = [w for v, w in rows if b - 0.25 <= v < b + 0.25]
        ws.append(round(sum(s) / len(s), 7) if s else 0.0)
    log(f"  drift kick: {ws}")
    return dict(v=v_bins, w=ws)


def measure_drift_tau(tau_exit=None):
    """The sway's slow-mode decay exponent (the wprime closure): the
    LL's yaw decays to its drift equilibrium with an |omega|-dependent
    tau — the turn-scale fishtail (19 s at ~0.1 rad/s) and the drift-
    scale decay (fitted here: the burst-path run — from rest, drained,
    a 44.5-spoude ramp — the omega peaks ~-0.001 and decays; the fit
    over the decay window gives (|omega_peak|, tau)). The power law
    tau(|w|) = tau_exit * (0.1/|w|)^p bridges the two anchors.
    Returns the exponent p (the drift-anchor / the turn-anchor)."""
    import math
    tau_exit = tau_exit if tau_exit is not None \
        else measure_tau_exit()
    # the wprime path: the FULL tank (the burst's kick decays through the
    # tank's drain — the drained-preset run under-measures the tau)
    ship = LLShip(rate=44.5, pressure=("spoude", "spoude"))
    t, ws = 0.0, []
    while t < 600.0:
        ship.step(DT)
        t += DT
        ws.append((t, ship.omega))
    # the peak and the settled value
    peak = min(w for _, w in ws)
    w_settled = sum(w for t, w in ws[-100:]) / 100.0
    t_peak = next(t for t, w in ws if w == peak)
    # the log-linear fit over the decay (peak -> settled): the window
    # capped at 10% of the peak excess — the tail's noise (w -> w_settled)
    # must not dominate the slope (the 15% cut under-measures the tau:
    # the decay slows as the omega approaches the settle)
    cut = w_settled + 0.1 * (peak - w_settled)
    pts = [(t, w) for t, w in ws if t_peak < t and w < cut]
    ys = [math.log(w_settled - w) for t, w in pts]
    ts = [t for t, w in pts]
    n = len(ys)
    slope = (n * sum(t * y for t, y in zip(ts, ys)) - sum(ts) * sum(ys)) \
        / (n * sum(t * t for t in ts) - sum(ts) ** 2)
    tau = -1.0 / slope
    p = math.log(tau / tau_exit) / math.log(0.1 / abs(peak))
    log(f"  drift-decay: peak {peak:.6f} settled {w_settled:.6f} "
        f"tau {tau:.1f} s -> exponent {p:.3f}")
    return round(p, 3)


def measure_drift_table():
    """The untrimmed lateral-drift table (rad/s, task C): the LL's
    straight-cruise yaw slope at the (rate, pressure, tank-state) cells —
    the symmetric crew carries a lateral kick, so a midship-helm cruise
    curves slowly. The drift is W'-independent at the settle (the tank's
    drain barely moves it — the kick's W'-dependence is small) and
    rate-dependent — the cells are the SETTLED values: the full-tank run
    (300-600 s from 0.9·V*) and the drained state (W' preset 0, LSQ over
    600-900 s from rest). The 20-60 s window is the sway transient
    (2-3x the settle — the wprime closure measured it); the settle is
    the honest anchor. The ship interpolates by W_frac. All cells
    measured at the validation's LL dt (0.05) — the drift is dt-
    validation's LL dt (0.05) — the drift is dt-sensitive (the sway's
    rectified equilibrium); the cells are only valid at that dt."""
    rates, sf, se, tf, te = DRIFT_RATES, [], [], [], []
    for r in rates:
        for pressure in ("spoude", "steady"):
            ship = LLShip(rate=r, pressure=(pressure, pressure))
            ship.V = 0.9 * equilibrium_speed("Olympias", r)["V"]
            t, next_s, psis = 0.0, 0.0, []
            while t < 600.0:
                ship.step(DT)
                t += DT
                if t >= next_s:
                    psis.append(ship.psi)
                    next_s += 1.0
            full = _psi_slope(psis[300:600])
            ship = LLShip(rate=r, pressure=(pressure, pressure))
            for crew in ship.crew.values():
                for tier in crew.tiers.values():
                    tier.W = 0.0
            t, next_s, psis = 0.0, 0.0, []
            while t < 900.0:
                ship.step(DT)
                t += DT
                if t >= next_s:
                    psis.append(ship.psi)
                    next_s += 1.0
            empty = _psi_slope(psis[600:900])
            if pressure == "spoude":
                sf.append(round(full, 8))
                se.append(round(empty, 8))
            else:
                tf.append(round(full, 8))
                te.append(round(empty, 8))
    log(f"  drift: spoude full {sf} / empty {se}; steady full {tf} / "
        f"empty {te}")
    return dict(rates=rates, spoude_full=sf, spoude_empty=se,
                steady_full=tf, steady_empty=te)


def _psi_slope(ps):
    """The LSQ slope of a 1 Hz psi trace, rad/s."""
    ts = list(range(len(ps)))
    n = len(ps)
    mt = sum(ts) / n
    mu = sum(ps) / n
    return sum((t_ - mt) * (p - mu) for t_, p in zip(ts, ps)) \
        / sum((t_ - mt) ** 2 for t_ in ts)


def measure_tau_exit():
    """The turn-exit yaw decay (s, the sprint_turn position follow-up):
    the LL keeps turning after the helm returns to midship — the
    sway-coupled fishtail (a hard turn at ~6 kt exits with ~70 deg of
    extra heading over ~2 min; the HL's tau_turn decay is far too fast).
    Fitted as the exponential with the same heading integral over the
    120-s window (the quadratic-damped omega decays hyperbolically)."""
    rate = rate_for_speed("Olympias", 6.0)
    ship = LLShip(rate=rate, helm=("port", 1.0))
    ship.V = 6.0 * KT
    t = 0.0
    while t < 150.0:                  # well into the turn (omega ~ 0.1)
        ship.step(DT)
        t += DT
    ship.helm_dir, ship.helm_frac = "midship", 0.0
    t, next_s, om = 0.0, 0.0, []
    while t < 240.0:
        ship.step(DT)
        t += DT
        if t >= next_s:
            om.append(ship.omega)
            next_s += 1.0
    w0 = om[0]
    best, best_rms = None, float("inf")
    for tau in [x for x in range(4, 121)]:       # 4 .. 120 s
        rms = math.sqrt(sum((w - w0 * math.exp(-i / tau)) ** 2
                            for i, w in enumerate(om)) / len(om))
        if rms < best_rms:
            best, best_rms = tau, rms
    log(f"  tau_exit: {best:.0f} s (RMS {best_rms:.5f} rad/s over 240 s)")
    return float(best)


def _exponential_fit(v0, tail):
    """Best τ (s) fitting v0 + (v0 - v_asym)*exp(-i/tau) to the 1 Hz
    samples (v_asym = the tail mean). Returns (tau, rms m/s)."""
    v_asym = sum(tail[-60:]) / 60.0
    best, best_rms = None, float("inf")
    for tau in [x / 2 for x in range(4, 161)]:      # 2.0 .. 80.0 s
        rms = math.sqrt(sum((v - (v_asym + (v0 - v_asym)
                                  * math.exp(-i / tau))) ** 2
                            for i, v in enumerate(tail)) / len(tail))
        if rms < best_rms:
            best, best_rms = tau, rms
    return best, best_rms, v_asym


def _entry_decay(state, rate, pressure="fast", v0_kt=6.0, t_end=330.0):
    """The one-side-stopped entry decay (task E): the LL at (row, state)
    from v0 (the scenario's cruise speed), the state's equilibrium —
    fitted as the chase model's exponential (the fit_tau_surge
    methodology)."""
    ship = LLShip(rate=rate, oar_state=("row", state),
                  pressure=(pressure, pressure))
    ship.V = v0_kt * KT
    t, next_s, Vs = 0.0, 0.0, []
    while t < t_end:
        ship.step(DT)
        t += DT
        if t >= next_s:
            Vs.append(ship.V)
            next_s += 1.0
    tau, rms, v_asym = _exponential_fit(v0_kt * KT, Vs)
    log(f"  {state}@{rate} entry: tau {tau:.1f} s (RMS {rms*KT:.3f} kt, "
        f"settles {v_asym/KT:.2f} kt)")
    return tau, rms, v_asym / KT


def _collapse_window(state, rate_before, rate_after, entry_tau,
                     pressure="fast", settle=90.0, window=180.0):
    """The low-rate collapse transition (task E): the cruise_turn 1440 s
    bin — the LL at (row, back) at the pre-transition rate, the rate
    drops to the collapse regime. The LL's transient is dip-and-recover
    (not exponential), so the effective τ is fitted to the gate quantity:
    the HL's mean V over the window must match the LL's (the fit_tau_turn
    philosophy). entry_tau: the measured back-entry τ at the high rate
    (the tau_back table's second point)."""
    from hl.ship import Ship as HLShip
    ship = LLShip(rate=rate_before, oar_state=("row", state),
                  pressure=(pressure, pressure))
    ship.V = 0.9 * equilibrium_speed("Olympias", rate_before)["V"]
    t, next_s, Vs = 0.0, 0.0, []
    while t < settle + window:
        if abs(t - settle) < DT / 2:
            ship._set_rate(rate_after)
        ship.step(DT)
        t += DT
        if t >= next_s:
            Vs.append(ship.V)
            next_s += 1.0
    i0 = int(settle) - 1
    v0 = sum(Vs[i0 - 5:i0]) / 5.0
    ll_mean = sum(Vs[i0:i0 + int(window)]) / window
    tables = _tables()
    best, best_diff = None, float("inf")
    for tau in [x for x in range(10, 161)]:        # 10 .. 160 s
        tables["tau_back"] = {"rates": [rate_after, rate_before],
                               "tau": [tau, entry_tau]}
        cal = Calibration(dict(id="fit"), tables, _scalars())
        hl = HLShip(rate=rate_after, oar_state=("row", state),
                    pressure=(pressure, pressure), curves=cal)
        hl.V = v0
        vs = []
        while hl.t < window + 1e-6:
            hl.step(hl.dt)
            vs.append(hl.V)
        hl_mean = sum(vs) / len(vs)
        diff = abs(hl_mean - ll_mean)
        if diff < best_diff:
            best, best_diff = tau, diff
    log(f"  {state} {rate_before}->{rate_after} collapse: tau {best:.0f} s "
        f"(mean diff {best_diff*KT:.3f} kt; LL window mean {ll_mean/KT:.2f} kt)")
    return float(best), best_diff * KT, ll_mean / KT


def measure_state_tau(state):
    """The per-state surge lag (task E), measured at the cruise_turn's
    transitions: the entry decay at 44 spm fast from 6 kt (the degenerate
    back ≡ hold regime) and, for the back, the 44 → 24 collapse (the
    window-mean fit). Returns (tau_entry, tau_collapse)."""
    if state == "hold":
        tau, rms, v = _entry_decay("hold", 44.0)
        return dict(entry=tau, rms_mps=rms, settles_kt=v)
    tau_e, rms_e, v_e = _entry_decay("back", 44.0)
    tau_c, diff_c, mean_c = _collapse_window("back", 44.0, 24.0, tau_e)
    return dict(entry=tau_e, collapse=tau_c, entry_rms_mps=rms_e,
                collapse_mean_diff_mps=diff_c, settles_kt=v_e,
                window_mean_kt=mean_c)


def measure_tempo_loss(rates):
    """The achieved-rate curve (task B): the exhausted crew cannot hold
    the tempo at high rates (rower.py's tempo branch — the drive cannot
    fit its slot). W' preset at zero, spoude from 0.9·V* (the exhausted
    state's speed), settled rate_eff; the full-W' column is the record
    (expected: the commanded rate)."""
    full, empty, t0 = [], [], time.time()
    for r in rates:
        for preset, out in ((None, full), (0.0, empty)):
            ship = LLShip(rate=r)
            if preset is not None:
                for crew in ship.crew.values():
                    for tier in crew.tiers.values():
                        tier.W = 0.0
            ship.V = 0.9 * equilibrium_speed("Olympias", r)["V"]
            t, next_s, effs = 0.0, 0.0, []
            while t < 120.0:
                ship.step(DT)
                t += DT
                if t >= next_s:
                    effs.append(ship.crew["port"].rate_eff)
                    next_s += 1.0
            out.append(round(sum(effs[-30:]) / 30.0, 2))
    log(f"  tempo loss: rates {rates} -> full {full}, empty {empty}, "
        f"{time.time()-t0:.0f} s")
    return dict(rates=rates, full_rate_eff=full, empty_rate_eff=empty)


def measure_turn_drag(tables):
    """The turn-deceleration residual (task F -> T4): the sway-coupled
    loss the exact rudder drag law misses — the LL's V(t) through a turn
    vs the HL's, scanned over the extra-drag factor k per helm fraction
    AND pressure (a_rud_extra = k(frac)·rudder_straight·V²/m_app; k = 0
    is today's ship). The LL's loss is nonlinear in helm and the
    pressure's turn state differs (the zigzag found the steady turns
    lose relatively more — the fitted spoude curve under-applied there);
    the per-fraction x per-pressure table (T4) replaces the old linear
    k·frac scalar."""
    from hl.ship import Ship as HLShip
    rates = [rate_for_speed("Olympias", 6.0),   # 19.9 — the G1 anchor
             28.8, 30.0, 44.5]
    fracs = [1 / 3, 1 / 2, 2 / 3, 1.0]
    pressures = ["spoude", "steady"]
    out = dict(fracs=fracs, rates=rates)
    rmses = []
    for pressure in pressures:
        per_rate = []
        for rate in rates:
            ks = []
            for frac in fracs:
                ll = LLShip(rate=rate, pressure=(pressure, pressure),
                            helm=("port", frac))
                ll.V = 6.0 * KT
                t, next_s, ll_vs = 0.0, 0.0, []
                while abs(ll.psi) < math.pi and ll.t < 900.0:
                    ll.step(DT)
                    t += DT
                    if t >= next_s:
                        ll_vs.append(ll.V)
                        next_s += 1.0
                best, best_rms = None, float("inf")
                for k in [x / 100 for x in range(0, 201, 2)]:   # 0.00 .. 2.00
                    cal = Calibration(dict(id="fit"), tables,
                                      dict(_scalars(), turn_drag_extra=k))
                    hl = HLShip(rate=rate, pressure=(pressure, pressure),
                                helm=("port", frac), curves=cal)
                    hl.V = 6.0 * KT
                    hl_vs = [v for i, v in enumerate(hl_step(hl))
                             if i % 2 == 0]
                    n = min(len(ll_vs), len(hl_vs))
                    rms = math.sqrt(sum((ll_vs[i] - hl_vs[i]) ** 2
                                        for i in range(n)) / n)
                    if rms < best_rms:
                        best, best_rms = k, rms
                ks.append(best)
                rmses.append(best_rms)
            per_rate.append(ks)
            log(f"  turn drag {pressure} @ {rate:.1f}: " +
                " ".join(f"k={k:.2f}" for k in ks))
        out[pressure] = per_rate
    return out, max(rmses) * KT


def measure_yaw_build():
    """The yaw build-up (task T3): the LL's omega's approach to its
    turn rate. The fit: omega(t) = ss*(1 - A*exp(-t/tf) -
    (1-A)*exp(-t/ts)) per family, measured at the family's TRUE usage:
    the helm turns (g1 — full helm, both rowing) vs the oar-only turns
    (MIDSHIP helm, one side holds — the oar family was previously
    measured on the helm-assisted setup, which uses the helm family in
    the HL, making the midship oar turns build ~2x too fast — the K23
    finding). The LL's builds are near single exponentials (helm tau ~8
    s, oar tau ~11-12 s), so the grid includes A = 1.0 and tf up to 12."""
    import math
    builds = {}
    for name, v0_kt, n_oars, helm, oar in (
            ("helm", 6.0, 170, ("port", 1.0), ("row", "row")),
            ("oar", 6.5, 85, ("midship", 0.0), ("row", "hold"))):
        rate = rate_for_speed("Olympias", v0_kt, n_oars=n_oars)
        ship = LLShip(rate=rate, helm=helm, oar_state=oar)
        ship.V = v0_kt * KT
        rec = []
        while ship.t < 120.0:
            ship.step(DT)
            rec.append(abs(ship.omega))
        ss = rec[-1]
        best = None
        for A in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0):
            for tf in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0):
                for ts in (10.0, 12.0, 15.0, 18.0, 22.0, 26.0, 31.6, 40.0):
                    err = 0.0
                    for i, w in enumerate(rec):
                        t = (i + 1) * DT
                        pred = ss * (1 - A * math.exp(-t / tf)
                                     - (1 - A) * math.exp(-t / ts))
                        err += (w - pred) ** 2
                    if best is None or err < best[0]:
                        best = (err, A, tf, ts)
        builds[name] = dict(A=best[1], tf=best[2], ts=best[3])
        log(f"  yaw build {name}: A={best[1]:.2f} tf={best[2]:.1f} "
            f"ts={best[3]:.1f}")
    return builds


def hl_step(hl):
    """Step an HL ship through a full turn, returning its per-step V
    samples (dt = 0.5 s; the fit downsamples to the LL's 1 Hz)."""
    vs = []
    while abs(hl.psi) < math.pi and hl.t < 900.0:
        hl.step(hl.dt)
        vs.append(hl.V)
    return vs


def _ll_turn_D(rate, helm, oar_state=("row", "row"), v0_kt=6.0):
    """The LL's path-measured turn diameter (|y| at 180 deg)."""
    ship = LLShip(rate=rate, helm=helm, oar_state=oar_state)
    ship.V = v0_kt * KT
    while abs(ship.psi) < math.pi and ship.t < 900.0:
        ship.step(DT)
    return abs(ship.y)


def measure_d_tables():
    """The steering families: helm_frac midpoints included so the whole
    interpolation surface is measured (the midship point is straight)."""
    r6 = rate_for_speed("Olympias", 6.0, n_oars=170)
    r65 = rate_for_speed("Olympias", 6.5, n_oars=85)
    rudder, oar, t0 = [], [], time.time()
    for frac in (1.0 / 3, 0.5, 2.0 / 3, 1.0):
        d = _ll_turn_D(r6, ("port", frac))
        rudder.append([round(frac, 4), round(d, 1)])
        log(f"  d_rudder frac={frac:.3f}: {d:.1f} m")
    for frac in (0.0, 0.5, 1.0):
        # frac 0 = no rudder at all (helm midship — the LL treats an
        # applied 0.0 helm as a residual 0.14-coefficient rudder)
        helm = ("midship", 0.0) if frac == 0.0 else ("starboard", frac)
        d = _ll_turn_D(r65, helm, oar_state=("row", "hold"), v0_kt=6.5)
        oar.append([round(frac, 4), round(d, 1)])
        log(f"  d_oar frac={frac:.3f}: {d:.1f} m")
    log(f"  D tables: {time.time()-t0:.0f} s")
    return dict(rudder=rudder, oar=oar)


# ---------------------------------------------------------------------------
# fits
# ---------------------------------------------------------------------------
def fit_tau_surge(vstar_kt_28):
    """Least-squares fit of the HL's first-order chase to the LL's rest
    start at 28.8 spm spoude (1 Hz samples, 0-180 s)."""
    ship = LLShip(rate=28.8)
    t, next_s, Vs = 0.0, 0.0, []
    while t < 180.0:
        ship.step(DT)
        t += DT
        if t >= next_s:
            Vs.append(ship.V)
            next_s += 1.0
    target = vstar_kt_28 * KT
    best, best_rms = None, float("inf")
    for tau in [x / 2 for x in range(10, 80)]:        # 5.0 .. 39.5 s
        rms = math.sqrt(sum((v - target * (1 - math.exp(-i / tau))) ** 2
                            for i, v in enumerate(Vs)) / len(Vs))
        if rms < best_rms:
            best, best_rms = tau, rms
    return best, best_rms


def fit_tau_turn(tables, ll_d, scalars=None):
    """Scan tau_turn so the HL's path-measured D matches the LL's across
    the four families (g1/f1/tightest/oar-hold) — the first-order lag
    inflates |y| at 180 deg, so the fit is against the path, not the raw
    build-up (the calibration protocol — simulation/AGENTS.md). scalars: the measured extras (turn_drag_extra
    must be in — the ship's turn deceleration changes the path D)."""
    scalars = _scalars() if scalars is None else scalars
    from hl.ship import Ship as HLShip
    # a copy for the fits: the stored tables keep null for the midship D
    # (json has no inf); the fit needs the real infinity
    cal_tables = dict(tables)
    cal_tables["d_rudder"] = [[f, math.inf if d is None else d]
                               for f, d in tables["d_rudder"]]
    scenarios = [
        (ll_d["g1"], rate_for_speed("Olympias", 6.0), ("port", 1.0),
         ("row", "row"), 6.0),
        (ll_d["f1"], rate_for_speed("Olympias", 6.0), ("port", 1.0 / 3),
         ("row", "row"), 6.0),
        (ll_d["tightest"], rate_for_speed("Olympias", 6.5, n_oars=85),
         ("starboard", 1.0), ("row", "hold"), 6.5),
        (ll_d["oar_hold"], rate_for_speed("Olympias", 6.5, n_oars=85),
         ("midship", 0.0), ("row", "hold"), 6.5),
    ]
    best, best_max = None, float("inf")
    for tau in (3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0):
        cal = Calibration(dict(id="fit"), cal_tables,
                          dict(scalars, tau_turn=tau))
        worst = 0.0
        for d_ref, rate, helm, oar_state, v0 in scenarios:
            ship = HLShip(rate=rate, helm=helm, oar_state=oar_state,
                          curves=cal)
            ship.V = v0 * KT
            while abs(ship.psi) < math.pi and ship.t < 900.0:
                ship.step(ship.dt)
            worst = max(worst, abs(abs(ship.y) / d_ref - 1.0))
        if worst < best_max:
            best, best_max = tau, worst
    return best, best_max


# ---------------------------------------------------------------------------
def main() -> None:
    t_all = time.time()
    commit = git_commit()
    date = datetime.date.today().isoformat()
    cal_id = f"calib-{date}-{commit}"
    log(f"calibration run: {cal_id} (LL commit {commit})")

    tables = {
        "vstar": measure_vstar(VSTAR_GRID),
        "steady": measure_pressure_rows(PRESSURE_RATES, "steady"),
        "fast": measure_pressure_rows(PRESSURE_RATES, "fast"),
        "empty": measure_empty(EMPTY_RATES),
        "hold": measure_asym("hold", ASYM_RATES["hold"]),
        "back": measure_asym("back", ASYM_RATES["back"]),
        "net": measure_nets(NET_RATES),
        "tempo_loss": measure_tempo_loss(TEMPO_RATES),
        "drift": measure_drift_table(),
        "drift_kick": measure_drift_kick(),
    }
    asym_nets = measure_asym_nets()
    tables["net_hold"] = asym_nets["hold"]
    tables["net_back"] = asym_nets["back"]
    fresh_nets = measure_fresh_nets(NET_RATES)
    tables["net_fresh"] = fresh_nets["hold"]  # back == hold (the degeneration)
    tables["d_oar_v"] = measure_d_oar_v()
    d_tables = measure_d_tables()
    tables["d_rudder"] = [[f, None] if f == 0.0 else [f, d]
                          for f, d in d_tables["rudder"]]
    tables["d_oar"] = d_tables["oar"]

    tau_hold = measure_state_tau("hold")
    tau_back = measure_state_tau("back")
    tables["tau_back"] = {"rates": [24.0, 44.0],
                           "tau": [tau_back["collapse"],
                                    tau_back["entry"]]}
    tau_exit = measure_tau_exit()
    tau_surge, rms_surge = fit_tau_surge(tables["vstar"]["kt"][
        VSTAR_GRID.index(28.8)])
    log(f"  tau_surge fit: {tau_surge:.1f} s (RMS {rms_surge*KT:.2f} kt)")
    turn_drag, rms_k = measure_turn_drag(tables)
    turn_k = turn_drag["spoude"][0][-1]        # the G1-anchor full-helm cell
    tables["turn_drag"] = turn_drag
    tables["yaw_build"] = measure_yaw_build()
    tau_turn, max_d = fit_tau_turn(tables, dict(
        g1=[d for f, d in d_tables["rudder"] if f == 1.0][0],
        f1=[d for f, d in d_tables["rudder"] if abs(f - 1 / 3) < 1e-3][0],
        tightest=[d for f, d in d_tables["oar"] if f == 1.0][0],
        oar_hold=[d for f, d in d_tables["oar"] if f == 0.0][0],
    ), dict(_scalars(), turn_drag_extra=turn_k))
    log(f"  tau_turn fit: {tau_turn:.1f} s "
        f"(max |D diff| {max_d*100:.1f} % across the families)")

    scalars = dict(_scalars(), tau_surge=tau_surge, tau_turn=tau_turn,
                   tau_hold=tau_hold["entry"], turn_drag_extra=turn_k,
                   tau_exit=tau_exit,
                   drift_tau_exp=measure_drift_tau(tau_exit),
                   v_flow=measure_v_flow())
    residuals = dict(
        vstar="exact at the grid points (mean-force bisection)",
        pressure_rows_std_kt=dict(
            steady=tables["steady"].pop("std_kt"),
            fast=tables["fast"].pop("std_kt"),
        ),
        tau_surge_rms_mps=rms_surge,
        tau_turn_max_d_pct=max_d * 100.0,
        tau_hold_rms_mps=tau_hold["rms_mps"],
        tau_hold_settles_kt=tau_hold["settles_kt"],
        tau_back_entry_rms_mps=tau_back["entry_rms_mps"],
        tau_back_collapse_mean_diff_mps=tau_back["collapse_mean_diff_mps"],
        tau_back_window_mean_kt=tau_back["window_mean_kt"],
        tempo_loss_full_is_commanded=(
            tables["tempo_loss"]["full_rate_eff"] ==
            tables["tempo_loss"]["rates"]),
        turn_drag_rms_mps=rms_k,
        tau_exit="the LL's omega decay after helm->midship, exponential "
                 "fit over 240 s",
        drift="LSQ yaw slope at the (rate, pressure, tank) cells: the "
              "full-tank window 20-60 s + the drained 600-900 s",
    )
    meta = dict(
        id=cal_id, ll_commit=commit, date=date,
        config=dict(rig="Olympias", fleet="spruce", hull=1.0, n_oars=170),
        protocols=dict(
            vstar="ll.hull.equilibrium_speed",
            pressure_rows="LL ship 420-s settle, 60-s tail mean",
            empty="LL ship, tiers' W preset 0, settle",
            asym="LL ship (row, hold / row, back), spoude + steady, settle",
            nets="LL tank slope at the settled speed (refills: low preset, "
                 "short window)",
            net_fresh="LL full-drain mean (tier W / time to empty) from "
                      "the 6.5-kt entry (the turns' full-tank context)",
            d_oar_v="LL oar-back 600-s run: the instantaneous 2V/|omega| "
                    "binned by V (the drained means; the fresh plateau "
                    "anchored to the d_oar(0) gate cell)",
            v_flow="the LL oar-back run's star-side W' slope vs V (the "
                   "back blades' flow-limit unlock ~3.0 kt)",
            d_tables="ll.ship.run_turn protocol (|y| at 180 deg)",
            tau_surge="LSQ of the chase to the 28.8 spm rest start",
            tau_turn="scan so the HL's |y| at 180 deg matches the LL's",
            drift="LL straight-cruise yaw slope at the anchors (task C)",
            tau_exit="LL omega decay after the helm returns midship "
                     "(sprint_turn position follow-up)",
            tempo_loss="LL exhausted rate_eff at the anchor rates (task B)",
            tau_hold="LL (row, hold) entry decay fit at 44 spm (task E)",
            tau_back="LL (row, back) entry fit at 44 + the 44->24 collapse "
                     "window-mean fit (task E)",
            turn_drag="LL G1-turn V(t) vs the HL's, extra-drag scan (task F)",
        ),
    )

    OUT_DIR.mkdir(exist_ok=True)
    out = dict(id=cal_id, meta=meta, tables=tables, scalars=scalars,
               residuals=residuals)
    path = OUT_DIR / f"{cal_id}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    shutil.copy(path, OUT_DIR / "latest.json")
    log(f"\nwrote {path.name} (+ latest.json) in {time.time()-t_all:.0f} s")
    log("next: python3 harness/run_validation.py  (the loop: adjust -> "
        "re-run -> re-validate)")

def measure_asym_nets():
    """The rowing side's tank net in the one-side-stopped legs (task
    T4 follow-up): (row,hold) and (row,back) at the asym anchor rates,
    spoude and steady, from the STATE'S SETTLED ORBIT (the scripts'
    context — the legs start from the hold's speed, not the 6-kt crash;
    the back's low-speed state is multi-stable, the orbit selects the
    mean; the settled demand sits at P_crit, so the nets are ~0 — the
    HL must not drain the tank at the symmetric rate in those legs)."""
    out = {}
    for state in ("hold", "back"):
        spoude, steady = [], []
        for rate in [24.0, 30.0, 36.0]:
            for preset, outk in (("spoude", spoude), ("steady", steady)):
                ship = LLShip(rate=rate, pressure=(preset, preset),
                              oar_state=("row", state))
                ship.V = 3.3                     # the hold-speed entry
                for _ in range(int(300.0 / DT)):  # settle into the orbit
                    ship.step(DT)
                w0 = [t.W for t in ship.crew["port"].tiers.values()]
                for _ in range(int(120.0 / DT)):
                    ship.step(DT)
                w1 = [t.W for t in ship.crew["port"].tiers.values()]
                outk.append(round(sum(a - b for a, b in zip(w0, w1))
                                  / 3.0 / 120.0, 1))
        out[state] = dict(rates=[24.0, 30.0, 36.0],
                          spoude=spoude, steady=steady)
        log(f"  asym nets {state}: spoude {spoude} steady {steady}")
    return out


def measure_fresh_nets(rates):
    """The rowing side's FRESH-phase tank net in the one-side-stopped
    state, W/man (the turns' context — the legs start from the 6.5-kt
    entry with a full tank and drain at the commanded pull; the
    settled-orbit nets (measure_asym_nets) are the drained-state
    values). Cell = the FULL-DRAIN mean (the tier's W / the time to
    empty, K22): the LL's drain rate decays as V falls, so the HL's
    linear drain must empty the tank in the LL's time (the sequence —
    the rowing side's empty before the 180° crossing — depends on it).
    The empty is detected on the side's W_frac (the min across the
    tiers — the snap's tank, the depletion metric's basis; the tier
    MEAN would dilute the drain with the slowest tier, ~2.9x at 44.5).
    The hold and back states share the fresh phase — the measured V/W
    traces are identical (the back degenerates to the hold at speed,
    VALIDATION §3), so one table serves both."""
    out = {}
    for state in ("hold", "back"):
        spoude, steady = [], []
        for rate in rates:
            for preset, outk in (("spoude", spoude), ("steady", steady)):
                ship = LLShip(rate=rate, pressure=(preset, preset),
                              oar_state=("row", state))
                ship.V = 6.5 * KT
                for _ in range(int(1.0 / DT)):
                    ship.step(DT)
                w0 = sum(t.W for t in ship.crew["port"].tiers.values()) / 3.0
                t0 = ship.t
                t_empty = None
                while ship.t - t0 < 400.0:
                    ship.step(DT)
                    if t_empty is None and ship.crew["port"].W_frac <= 0.0:
                        t_empty = ship.t - t0
                if t_empty:
                    outk.append(round(w0 / t_empty, 1))
                else:
                    outk.append(0.0)
        out[state] = dict(rates=list(rates),
                          spoude=spoude, steady=steady)
        log(f"  fresh nets {state}: spoude {spoude} steady {steady}")
    return out


def measure_d_oar_v():
    """The oar-family orbit diameter vs the ship's speed, m (K22): the
    LL's one-side-back turn's settled orbits. Drained cells: the
    oar-back 600-s run's instantaneous 2V/|omega| binned by V (the
    multi-stable band's means); the fresh plateau = the d_oar(0) gate
    cell (103.5 m) above 3.0 kt (the half-circle anchor — the gate
    measures the fresh orbit); the transition interpolated (the LL's
    collapse transient — no settled states exist there)."""
    from harness.script import turn_stream
    from ll.ship import rate_for_speed
    rate = rate_for_speed("Olympias", 6.5, n_oars=85)
    ship = LLShip(rate=rate, oar_state=("row", "back"))
    ship.V = 6.5 * KT
    cmds = turn_stream(rate, ("midship", 0.0), ("row", "back"))
    events, idx = list(cmds), 0
    samples = []
    while ship.t <= 600.0:
        while idx < len(events) and events[idx].time <= ship.t + 1e-6:
            ship.apply(events[idx]); idx += 1
        ship.step(DT)
        if ship.t >= 110.0:                  # the drained phase only
            samples.append((ship.V / KT, 2.0 * ship.V
                            / max(abs(ship.omega), 1e-9)))
    cells = []
    for v in (1.0, 1.5, 2.0, 2.5):
        b = [d for vk, d in samples if abs(vk - v) < 0.25]
        cells.append(round(sum(b) / len(b), 1) if b else None)
    out = dict(v_kt=[1.0, 1.5, 2.0, 2.5, 3.0], d=cells + [103.5])
    log(f"  d_oar_v: {out['d']}")
    return out


def measure_v_flow():
    """The backing side's flow-limit threshold, kt (K22): the V below
    which the back stroke unlocks (the peak-force cap stops degenerating
    it to the hold-brake) and its W' starts draining. From the oar-back
    run: the star's W' slope vs V — locked (slope ~ 0) at 3.37 kt,
    draining at the full rate by 2.6 kt; the threshold is the slope's
    half-power point (~3.0)."""
    from harness.script import turn_stream
    from ll.ship import rate_for_speed
    rate = rate_for_speed("Olympias", 6.5, n_oars=85)
    ship = LLShip(rate=rate, oar_state=("row", "back"))
    ship.V = 6.5 * KT
    cmds = turn_stream(rate, ("midship", 0.0), ("row", "back"))
    events, idx = list(cmds), 0
    slopes = []
    prev = None
    while ship.t <= 600.0:
        while idx < len(events) and events[idx].time <= ship.t + 1e-6:
            ship.apply(events[idx]); idx += 1
        ship.step(DT)
        if ship.t >= 40.0 and int(ship.t * 2) != int((ship.t - DT) * 2):
            s = ship.crew["star"].W_frac
            if prev:
                slopes.append((ship.V / KT, (prev[1] - s) / (ship.t - prev[0])))
            prev = (ship.t, s)
    full = max(s for _, s in slopes)
    # the half-power threshold: the V where the star's drain rate crosses
    # half the full rate (the peak-cap ramp — the unlock is gradual)
    active = [(v, s) for v, s in slopes if s > 0.02 * full]
    half = full / 2.0
    v_flow = None
    for (v0, s0), (v1, s1) in zip(active, active[1:]):
        if s0 <= half <= s1 or s1 <= half <= s0:
            f = (half - s0) / (s1 - s0)
            v_flow = v0 + f * (v1 - v0)
            break
    out = round(v_flow, 2) if v_flow else 3.0
    log(f"  v_flow: {out} kt (slopes {len(slopes)}, full rate {full*1000:.1f}/ks)")
    return out


if __name__ == "__main__":
    main()
