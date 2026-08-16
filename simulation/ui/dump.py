#!/usr/bin/env python3
"""Dump deterministic replay logs for the browser UI (ui/viewer.html).

Runs the harness's script set + the turn scenarios on both simulators
(harness.run_both — the same telemetry the validation uses) and writes
the 1 Hz snaps to ui/logs/<id>.<ll|hl>.json, plus logs/index.json for
the viewer's run dropdown. The sims are deterministic, so the logs are
stable and can be committed; re-run this after any LL/HL change to
refresh them.

Usage (from simulation/):
    python3 ui/dump.py             # everything (~2-5 min of LL runs)
    python3 ui/dump.py --only g1   # one run (script stem or turn name)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.chain import KT
from commands.parser import parse_file
from harness.run_validation import SCRIPTS, TURNS
from harness.script import run_both, turn_stream
from ll.ship import rate_for_speed

LOGS = Path(__file__).resolve().parent / "logs"
SIM_LABEL = {"ll": "LL (per-oar)", "hl": "HL (fast)"}

TURN_LABELS = {
    "g1": "turn g1 — full rudder @ 6 kt",
    "f1": "turn f1 — 22.5\u00b0 rudder @ 6 kt",
    "tightest": "turn tightest — helm + hold one side @ 6.5 kt",
    "oar-hold": "turn oar-hold — one side holds, midship helm",
    "oar-back": "turn oar-back — one side backs, midship helm",
}


def write_log(id_: str, sim: str, label: str, meta: dict,
              commands: list, rows: list) -> None:
    LOGS.mkdir(exist_ok=True)
    payload = dict(
        meta=dict(label=label, sim=sim, sim_label=SIM_LABEL[sim], **meta),
        commands=[dict(time=c.time, verb=c.verb, args=list(c.args),
                       lineno=c.lineno) for c in commands],
        rows=rows,
    )
    path = LOGS / f"{id_}.{sim}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    return path


def dump_script(entry: tuple, index: list, only: str | None) -> None:
    label, path, v0, _ = entry
    id_ = Path(path).stem
    if only and only != id_:
        return
    cmds = parse_file(Path(__file__).resolve().parents[1] / path)
    t0 = time.time()
    out = run_both(cmds, V0=v0)
    sims = []
    for sim in ("ll", "hl"):
        write_log(id_, sim, label,
                  meta=dict(script=path, v0_kt=round(v0 / KT, 3),
                            sample=out["meta"]["sample"], dt=out["meta"][f"{sim}_dt"],
                            t_end=out["meta"]["t_end"],
                            calibration=out["meta"]["calibration"],
                            n_commands=out["meta"]["n_commands"]),
                  commands=cmds, rows=out[sim])
        sims.append(sim)
    index.append(dict(id=id_, label=label, sims=sims))
    print(f"  {id_:16s} {time.time()-t0:5.0f} s wall ({label})")


def dump_turn(name: str, v0_kt: float, n_oars: int, helm: tuple,
              oar_state: tuple, index: list, only: str | None) -> None:
    if only and only != name:
        return
    rate = rate_for_speed("Olympias", v0_kt, n_oars=n_oars)
    cmds = turn_stream(rate, helm, oar_state)
    t0 = time.time()
    out = run_both(cmds, V0=v0_kt * KT, until=600.0)
    sims = []
    for sim in ("ll", "hl"):
        write_log(name, sim, TURN_LABELS[name],
                  meta=dict(script=f"turn scenario {name}",
                            v0_kt=v0_kt, rate_kt=round(rate, 2),
                            n_oars=n_oars, helm=helm,
                            sample=out["meta"]["sample"], dt=out["meta"][f"{sim}_dt"],
                            t_end=out["meta"]["t_end"],
                            calibration=out["meta"]["calibration"],
                            n_commands=out["meta"]["n_commands"]),
                  commands=cmds, rows=out[sim])
        sims.append(sim)
    index.append(dict(id=name, label=TURN_LABELS[name], sims=sims))
    print(f"  {name:16s} {time.time()-t0:5.0f} s wall (turn @ {rate:.1f} spm)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="dump a single run (script stem or turn name)")
    args = ap.parse_args()

    index: list = []
    print("scripts:")
    for entry in SCRIPTS:
        dump_script(entry, index, args.only)
    print("turns:")
    for turn in TURNS:
        dump_turn(*turn, index, args.only)

    if not args.only:
        with open(LOGS / "index.json", "w", encoding="utf-8") as fh:
            json.dump(index, fh, indent=1)
        print(f"\n{len(index)} runs, {len(index) * 2} logs -> ui/logs/")
        print("start the viewer: python3 ui/serve.py")


if __name__ == "__main__":
    main()
