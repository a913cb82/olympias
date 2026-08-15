#!/usr/bin/env python3
"""The HL calibration run (plan §19.2) — measure the response curves from
the LL and write hl/calibration/calib_<id>.json (+ latest.json).

Every table is produced by an LL protocol — nothing is hand-entered. The
residuals (fit quality per table) feed the tolerance labels. The loop:
run this, then harness/run_validation.py; if a gate fails, the trigger
table in plan §19.2 names the adjustment; repeat until the HL matches
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
from hl.curves import Calibration, _scalars
from ll.hull import equilibrium_speed
from ll.ship import Ship as LLShip, rate_for_speed

DT = 0.05                 # the LL's comparison dt
OUT_DIR = Path(__file__).resolve().parent / "calibration"

# protocol grids (the schema's anchor levels; numeric pressures interpolate)
VSTAR_GRID = [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 25.5,
              28.8, 30.0, 32.3, 34.0, 36.0, 38.0, 40.0, 42.0, 44.5, 46.0,
              48.0, 50.0]
PRESSURE_RATES = [24.0, 25.5, 28.8, 32.3, 36.0, 40.0, 44.5]
EMPTY_RATES = [25.5, 28.8, 32.3, 36.0, 44.5]
ASYM_RATES = {"hold": [24.0, 30.0, 36.0], "back": [24.0, 30.0, 36.0, 44.5]}
NET_RATES = [25.5, 28.8, 32.3, 36.0, 44.5]


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


def fit_tau_turn(tables, ll_d):
    """Scan tau_turn so the HL's path-measured D matches the LL's across
    the four families (g1/f1/tightest/oar-hold) — the first-order lag
    inflates |y| at 180 deg, so the fit is against the path, not the raw
    build-up (plan §19.2)."""
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
        cal = Calibration(dict(id="fit"), cal_tables, dict(_scalars(),
                                                           tau_turn=tau))
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
    }
    d_tables = measure_d_tables()
    tables["d_rudder"] = [[f, None] if f == 0.0 else [f, d]
                          for f, d in d_tables["rudder"]]
    tables["d_oar"] = d_tables["oar"]

    tau_surge, rms_surge = fit_tau_surge(tables["vstar"]["kt"][
        VSTAR_GRID.index(28.8)])
    log(f"  tau_surge fit: {tau_surge:.1f} s (RMS {rms_surge*KT:.2f} kt)")
    tau_turn, max_d = fit_tau_turn(tables, dict(
        g1=[d for f, d in d_tables["rudder"] if f == 1.0][0],
        f1=[d for f, d in d_tables["rudder"] if abs(f - 1 / 3) < 1e-3][0],
        tightest=[d for f, d in d_tables["oar"] if f == 1.0][0],
        oar_hold=[d for f, d in d_tables["oar"] if f == 0.0][0],
    ))
    log(f"  tau_turn fit: {tau_turn:.1f} s "
        f"(max |D diff| {max_d*100:.1f} % across the families)")

    scalars = dict(_scalars(), tau_surge=tau_surge, tau_turn=tau_turn)
    residuals = dict(
        vstar="exact at the grid points (mean-force bisection)",
        pressure_rows_std_kt=dict(
            steady=tables["steady"].pop("std_kt"),
            fast=tables["fast"].pop("std_kt"),
        ),
        tau_surge_rms_mps=rms_surge,
        tau_turn_max_d_pct=max_d * 100.0,
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
            d_tables="ll.ship.run_turn protocol (|y| at 180 deg)",
            tau_surge="LSQ of the chase to the 28.8 spm rest start",
            tau_turn="scan so the HL's |y| at 180 deg matches the LL's",
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


if __name__ == "__main__":
    main()
