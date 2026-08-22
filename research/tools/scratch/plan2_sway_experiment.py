#!/usr/bin/env python3
"""Plan 2 experiment: the cross-flow sway modes vs the turn anchors.

Runs the five turn scenarios (run_turn.py's set) under three configs:
  (a) fitted   — the validated default (Omega 3.2e6, clr 0.8, A_lat 35)
  (b) omegacf  — the fitted mode with Omega = Omega_cf(0.3) (the audit's
                 pure-rotation value, parametric hull + ram: 3.25e6)
  (c) crossflow— the consistent cross-flow model (sway="crossflow",
                 C_D = 0.3, the drag-crisis band input — no fitted trio)
plus a 5-min straight-line trim check (symmetric crew, heading drift).

The no-regression gate: the turn diameters must stay inside the W5 bands
(G1 89.4 ±7 %, F1 111.9 ±7 %, tightest 62 ±10 %).

Usage (from simulation/): ../../.venv/bin/python3 \
    ../research/tools/scratch/plan2_sway_experiment.py
"""

import sys
import math
from pathlib import Path

SIM = Path(__file__).resolve().parents[3] / "simulation"
sys.path.insert(0, str(SIM))

from common.chain import KT, RIGS, VESSELS  # noqa: E402
from ll.ship import Ship, rate_for_speed, run_turn  # noqa: E402

_L5 = Path(__file__).resolve().parents[2] / "lane-5-manoeuvre"
sys.path.insert(0, str(_L5))
from crossflow import omega_crossflow, X_CG  # noqa: E402

ANCHORS = {"g1": (89.4, 0.07), "f1": (111.9, 0.07), "tightest": (62.0, 0.10)}

SCEN = {
    "g1":       dict(V0=6.0, rate=lambda: rate_for_speed("Olympias", 6.0, n_oars=170),
                     helm=("port", 1.0)),
    "f1":       dict(V0=6.0, rate=lambda: rate_for_speed("Olympias", 6.0, n_oars=170),
                     helm=("port", 22.5 / 67.5)),
    "tightest": dict(V0=6.5, rate=lambda: rate_for_speed("Olympias", 6.5, n_oars=85),
                     oar_state=("row", "hold"), helm=("starboard", 1.0)),
    "oar-hold": dict(V0=6.5, rate=lambda: rate_for_speed("Olympias", 6.5, n_oars=85),
                     oar_state=("row", "hold"), helm=("midship", 0.0)),
    "oar-back": dict(V0=6.5, rate=lambda: rate_for_speed("Olympias", 6.5, n_oars=85),
                     oar_state=("row", "back"), helm=("midship", 0.0)),
}


def run_scenario(name, sway="fitted", cd=0.3, omega=None):
    cfg = SCEN[name]
    kw = {k: v for k, v in cfg.items() if k not in ("V0", "rate")}
    kw["rate"] = cfg["rate"]()
    ship = Ship(sway=sway, cd=cd, **kw)
    if omega is not None:
        ship.Omega = omega
    ship.V = cfg["V0"] * KT
    r = run_turn(ship)
    return r


def trim_check(sway="fitted", cd=0.3, t_end=300.0, dt=0.05):
    """Symmetric crew at cruise: the heading drift over t_end (deg)."""
    ship = Ship(rate=28.8, sway=sway, cd=cd)
    ship.V = 7.2 * KT
    for _ in range(int(t_end / dt)):
        ship.step(dt)
    return math.degrees(abs(ship.psi)), ship.V / KT


def main():
    om_cf = omega_crossflow(0.3)
    print(f"Omega_cf(0.3) = {om_cf:.2e} (vs fitted 3.2e6) — the audit's "
          f"pure-rotation value\n")
    hdr = (f"{'scenario':10s} {'mode':10s} {'D m':>7s} {'t_180 s':>8s} "
           f"{'V_end':>6s} {'vs anchor':>10s}")
    print(hdr)
    print("-" * len(hdr))
    for name, (anchor, band) in ANCHORS.items():
        for mode, kw in (("fitted", {}),
                         ("omegacf", dict(omega=om_cf)),
                         ("crossflow", dict(sway="crossflow"))):
            r = run_scenario(name, **kw)
            d = r["D"]
            ok = abs(d - anchor) / anchor <= band
            print(f"{name:10s} {mode:10s} {d:7.1f} {r['t_turn']:8.1f} "
                  f"{r['V_end']:6.2f} {100*(d-anchor)/anchor:+9.1f}%"
                  f"{'  OK' if ok else '  OUT'}")
        print("-" * len(hdr))
    for name in ("oar-hold", "oar-back"):
        for mode, kw in (("fitted", {}), ("crossflow", dict(sway="crossflow"))):
            r = run_scenario(name, **kw)
            print(f"{name:10s} {mode:10s} {r['D']:7.1f} {r['t_turn']:8.1f} "
                  f"{r['V_end']:6.2f}      (no anchor)")
    print("-" * len(hdr))
    for mode in ("fitted", "crossflow"):
        drift, v = trim_check(sway=mode)
        print(f"trim 5 min @ 7.2 kt: {mode:10s} heading drift {drift:6.2f} deg, "
              f"V_end {v:.2f} kt")


if __name__ == "__main__":
    main()
