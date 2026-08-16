"""Parser for trireme command scripts (3).

Format: plain text, one command per line; ``#`` starts a comment; fields are
comma- or whitespace-separated::

    <time_s> <verb> [args...]

Every line is validated against ``commands/schema.json`` before the run
(fail-fast, deterministic): unknown verbs, bad argument counts, out-of-range
numbers and bad enums raise :class:`ScriptError` naming the offending line.

Output is a chronological list of :class:`Command`; commands sharing a
timestamp keep their file order (stable sort).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"


class ScriptError(ValueError):
    """A script line that fails schema validation."""


@dataclass(frozen=True)
class Command:
    time: float          # seconds from script start
    verb: str            # one of the schema verbs
    args: tuple[Any, ...]
    lineno: int          # 1-based, for error messages and replay logs

    def __str__(self) -> str:
        args = ", ".join(str(a) for a in self.args)
        return f"t={self.time:9.2f}  {self.verb} {args}"


def load_schema(path: Path | str = SCHEMA_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _tokens(line: str) -> list[str]:
    line = line.split("#", 1)[0]     # strip comment to end of line
    line = line.replace(",", " ")    # comma- or space-separated
    return line.split()


def _parse_number(raw: str, spec: dict, verb: str, lineno: int) -> float:
    try:
        value = float(raw)
    except ValueError:
        raise ScriptError(f"line {lineno}: {verb}: expected a number, got {raw!r}")
    lo, hi = spec.get("min"), spec.get("max")
    if (lo is not None and value < lo) or (hi is not None and value > hi):
        raise ScriptError(
            f"line {lineno}: {verb}: {value:g} out of range [{lo}, {hi}]"
        )
    return value


def _parse_arg(raw: str, spec: dict, verb: str, lineno: int) -> Any:
    kind = spec["type"]
    if kind == "number":
        return _parse_number(raw, spec, verb, lineno)
    if kind == "enum":
        if raw not in spec["values"]:
            raise ScriptError(
                f"line {lineno}: {verb}: bad value {raw!r}, "
                f"expected one of {spec['values']}"
            )
        return raw
    if kind == "enum-or-number":
        if raw in spec["values"]:
            return raw
        return _parse_number(raw, spec, verb, lineno)
    raise ScriptError(f"line {lineno}: schema error: unknown arg type {kind!r}")


def parse_line(line: str, lineno: int, schema: dict) -> Command | None:
    """Parse one script line; returns None for blank/comment-only lines."""
    toks = _tokens(line)
    if not toks:
        return None
    try:
        t = float(toks[0])
    except ValueError:
        raise ScriptError(
            f"line {lineno}: first field must be a time in seconds, got {toks[0]!r}"
        )
    if t < 0:
        raise ScriptError(f"line {lineno}: time must be >= 0, got {t:g}")
    if len(toks) < 2:
        raise ScriptError(f"line {lineno}: missing verb after time {t:g}")

    verb, rest = toks[1], toks[2:]
    vdef = schema["verbs"].get(verb)
    if vdef is None:
        known = ", ".join(sorted(schema["verbs"]))
        raise ScriptError(f"line {lineno}: unknown verb {verb!r} (known: {known})")

    aliases = vdef.get("aliases", {})
    if aliases and rest and rest[0] in aliases:
        rest = [str(aliases[rest[0]])] + rest[1:]

    specs = vdef["args"]
    if len(rest) > len(specs):
        raise ScriptError(f"line {lineno}: {verb}: too many arguments ({rest!r})")

    args = []
    for i, raw in enumerate(rest):
        args.append(_parse_arg(raw, specs[i], verb, lineno))
    for i in range(len(args), len(specs)):
        spec = specs[i]
        if not spec.get("optional"):
            raise ScriptError(
                f"line {lineno}: {verb}: missing required argument {spec['name']!r}"
            )
        args.append(spec["default"])

    return Command(time=t, verb=verb, args=tuple(args), lineno=lineno)


def parse_script(text: str, schema: dict | None = None) -> list[Command]:
    """Parse a whole script; chronological order, file order within a timestamp."""
    schema = schema or load_schema()
    commands = []
    for lineno, line in enumerate(text.splitlines(), 1):
        cmd = parse_line(line, lineno, schema)
        if cmd is not None:
            commands.append(cmd)
    return sorted(commands, key=lambda c: c.time)


def parse_file(path: Path | str, schema: dict | None = None) -> list[Command]:
    with open(path, encoding="utf-8") as fh:
        return parse_script(fh.read(), schema)
