#!/usr/bin/env python3
"""Fast-ship demo runner (Phase 2 HL, the calibration protocol (simulation/AGENTS.md)).

Usage (from simulation/):
    python3 hl/run_hl.py                    # examples/cruise_turn.txt
    python3 hl/run_hl.py --table             # V* over the rates
    python3 hl/run_hl.py --turn g1          # turn scenario (D = |y| at 180 deg)
    python3 hl/run_hl.py --turn table       # all scenarios vs the LL anchors

Turn scenarios mirror ll/run_turn.py (entry speeds, helm, one-side stops);
the rates are the LL's speed-holding rates (ll.ship.rate_for_speed), the
diameters the HL produces from its calibrated D families. The LL anchors
are the current ll/run_turn.py outputs.
"""

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from commands.parser import parse_file
from common.chain import KT

from hl.ship import Ship

SCENARIOS = {
    "g1": {
        "V0": 6.0,
        "oar_state": ("row", "row"),
        "helm": ("port", 1.0),
        "n_oars": 170,
        "anchor": 89.7,
        "note": "vs LL 89.7 m",
    },
    "f1": {
        "V0": 6.0,
        "oar_state": ("row", "row"),
        "helm": ("port", 22.5 / 67.5),
        "n_oars": 170,
        "anchor": 117.4,
        "note": "vs LL 117.4 m",
    },
    "tightest": {
        "V0": 6.5,
        "oar_state": ("row", "hold"),
        "helm": ("starboard", 1.0),
        "n_oars": 85,
        "anchor": 67.7,
        "note": "vs LL 67.7 m",
    },
    "oar-hold": {
        "V0": 6.5,
        "oar_state": ("row", "hold"),
        "helm": ("midship", 0.0),
        "n_oars": 85,
        "anchor": 126.6,
        "note": "vs LL 126.6 m",
    },
    "oar-back": {
        "V0": 6.5,
        "oar_state": ("row", "back"),
        "helm": ("midship", 0.0),
        "n_oars": 85,
        "anchor": 126.6,
        "note": "vs LL 126.6 m (degenerate)",
    },
}


def run_turn(ship: Ship, target_psi: float = math.pi) -> dict:
    """Same protocol as ll.ship.run_turn: |y| at the target heading."""
    tgt = abs(target_psi)
    while abs(ship.psi) < tgt and ship.t < 3600.0:
        ship.step(ship.dt)
    return {"D": abs(ship.y), "t_turn": ship.t, "psi": ship.psi, "V_end": ship.V / KT}


def run_one(name: str) -> None:
    cfg = SCENARIOS[name]
    from ll.ship import rate_for_speed  # build-time: the LL's rate

    v0_raw = cfg["V0"]
    assert isinstance(v0_raw, (int, float))
    v0 = float(v0_raw)
    n_oars_raw = cfg["n_oars"]
    assert isinstance(n_oars_raw, int)
    n_oars = n_oars_raw
    rate = rate_for_speed("Olympias", v0, n_oars=n_oars)
    ship = Ship(
        rate=rate,
        oar_state=cfg["oar_state"],
        helm=cfg["helm"],
    )
    ship.V = v0 * KT
    r = run_turn(ship)
    d_pct = (r["D"] / cfg["anchor"] - 1.0) * 100.0
    print(
        f"{name:10s} D={r['D']:7.1f} m  t_180={r['t_turn']:6.1f} s  "
        f"V0={cfg['V0']:.1f} -> V_end={r['V_end']:4.2f} kt  "
        f"({d_pct:+.1f}% vs LL)  {cfg['note']}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--table", action="store_true", help="V* over the rates")
    ap.add_argument(
        "--turn",
        nargs="?",
        const="table",
        default=None,
        help="turn scenario (g1|f1|tightest|oar-hold|oar-back|table)",
    )
    ap.add_argument("--dt", type=float, default=0.5)
    ap.add_argument("--t-end", type=float, default=None, help="script run length")
    args = ap.parse_args()

    ship = Ship(dt=args.dt)
    m = ship.curves.meta
    print(f"calibration: {m['id']} (ll {m.get('ll_commit', '?')})")

    if args.turn:
        names = list(SCENARIOS) if args.turn == "table" else [args.turn]
        for n in names:
            run_one(n)
        return

    if args.table:
        print(f"{'rate':>6} {'V* kt':>8} {'V* asym kt':>11} {'spoude W/man':>12}")
        for r in (8, 12, 16, 20, 24, 25.5, 28.8, 32.3, 36, 40, 44.5, 50):
            print(
                f"{r:6.1f} {ship.curves.vstar_kt(r):8.2f} "
                f"{ship.curves.vasym(r, 1.0, 'hold') / KT:11.2f} "
                f"{ship.curves.p_spoude(r):12.1f}"
            )
        return

    cmds = parse_file(
        Path(__file__).resolve().parents[1] / "examples" / "cruise_turn.txt"
    )
    ship.run_script(cmds, dt=args.dt, until=args.t_end, V0=5.0 * KT)
    s = ship.snap()
    print(
        f"script cruise_turn.txt: t={s['t']:.0f} s  "
        f"pos=({s['x']:.0f}, {s['y']:.0f}) m  V={s['V'] / KT:.2f} kt  "
        f"heading={math.degrees(s['psi']) % 360:.0f} deg  "
        f"W_frac={s['crew']['port']['W_frac']:.2f}  "
        f"crew={ {k: v['state'] for k, v in s['crew'].items()} }"
    )


if __name__ == "__main__":
    main()
