"""Drive one command stream on both simulators (the harness — simulation/AGENTS.md).

The same parsed commands, the same starting state (V0), the same event
semantics as the simulators' own run_script — but stepped manually so both
ships are sampled at a common 1 Hz cadence. Deterministic: no RNG in either
simulator; the command log is returned for the record.

    rows = run_both(commands, V0=..., until=...)
    rows["ll"]  # list of snap dicts, one per second
    rows["hl"]  # same
"""

from __future__ import annotations

from hl.ship import Ship as HLShip
from ll.ship import Ship as LLShip

LL_DT = 0.05  # the LL's comparison dt (the suite's de-facto)
HL_DT = 0.5  # the HL design (simulation/AGENTS.md): the HL's 0.5-1 s step
SAMPLE_S = 1.0  # common telemetry cadence


def _drive(ship, commands, dt, until, V0, sample):
    """Step the ship through the command stream, sampling snaps at the
    common cadence. Same event semantics as the simulators' run_script."""
    ship.V = V0
    events = list(commands)
    idx = 0
    t_end = until if until is not None else (events[-1].time if events else 0.0) + 1e-6
    next_s = 0.0
    rows = []
    while ship.t <= t_end:
        while idx < len(events) and events[idx].time <= ship.t + 1e-6:
            ship.apply(events[idx])
            idx += 1
        ship.step(dt)
        if ship.t >= next_s - 1e-9:
            rows.append(ship.snap())
            next_s += sample
    return rows


def run_both(
    commands, until=None, V0=0.0, ll_dt=LL_DT, hl_dt=HL_DT, sample=SAMPLE_S
) -> dict:
    """Run the same command stream on the LL and the HL from the same
    starting state; return the 1 Hz telemetry of each + the run meta."""
    rows_ll = _drive(LLShip(), commands, ll_dt, until, V0, sample)
    rows_hl = _drive(HLShip(), commands, hl_dt, until, V0, sample)
    t_end = until if until is not None else (commands[-1].time if commands else 0.0)
    return {
        "ll": rows_ll,
        "hl": rows_hl,
        "meta": {
            "ll_dt": ll_dt,
            "hl_dt": hl_dt,
            "sample": sample,
            "V0": V0,
            "t_end": t_end,
            "calibration": rows_hl[-1]["calibration"],
            "n_commands": len(commands),
        },
    }


def turn_stream(rate: float, helm: tuple, oar_state=("row", "row")) -> list:
    """A command stream for a fixed-rate turn scenario (rate is the LL's
    speed-holding rate, ll.ship.rate_for_speed — a build-time number). The
    one-side-stopped scenarios emit the oars command too."""
    from commands.parser import Command

    cmds = [
        Command(time=0.0, verb="rate", args=[rate], lineno=1),
        Command(time=0.0, verb="helm", args=[helm[0], float(helm[1])], lineno=2),
    ]
    if oar_state[0] != "row" or oar_state[1] != "row":
        side = "starboard" if oar_state[1] != "row" else "port"
        state = oar_state[1] if oar_state[1] != "row" else oar_state[0]
        cmds.append(Command(time=0.0, verb="oars", args=[state, side], lineno=3))
    return cmds
