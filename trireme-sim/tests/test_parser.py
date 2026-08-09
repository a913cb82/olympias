"""Parser tests — run: python3 tests/test_parser.py (no pytest needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from commands.parser import Command, ScriptError, parse_file, parse_script, load_schema

SCHEMA = load_schema()
SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "cruise_turn.txt"

passed = 0


def check(label, fn):
    global passed
    fn()
    passed += 1
    print(f"ok - {label}")


def raises(label, exc, fn):
    global passed
    try:
        fn()
    except exc:
        passed += 1
        print(f"ok - {label}")
        return
    raise AssertionError(f"expected {exc.__name__} for: {label}")


# --- happy path ---

def t_sample():
    cmds = parse_file(SAMPLE, SCHEMA)
    assert [c.verb for c in cmds] == [
        "rate", "pressure", "rate", "helm", "oars", "oars", "rate", "pressure", "oars"
    ]
    assert cmds[0] == Command(time=0.0, verb="rate", args=(30.0,), lineno=4)
    assert cmds[4].args == ("hold", "starboard")
    assert cmds[7].args == ("steady", "port")
check("sample script parses to expected commands", t_sample)


def t_defaults():
    cmds = parse_script("10, oars, back\n20, helm, port\n30, pressure, spoude", SCHEMA)
    assert cmds[0].args == ("back", "both")        # side defaults to both
    assert cmds[1].args == ("port", 1.0)           # helm fraction defaults to 1
    assert cmds[2].args == ("spoude", "both")      # pressure side defaults to both
check("optional args take schema defaults", t_defaults)


def t_aliases():
    cmds = parse_script("0, rate, slow\n1, rate, racing", SCHEMA)
    assert cmds[0].args == (24.0,)
    assert cmds[1].args == (44.0,)
check("rate aliases resolve to spm", t_aliases)


def t_numeric_pressure():
    cmds = parse_script("0, pressure, 0.5\n1, pressure, 1, port", SCHEMA)
    assert cmds[0].args == (0.5, "both")
    assert cmds[1].args == (1.0, "port")
check("pressure accepts numeric 0-1 and side", t_numeric_pressure)


def t_comment_and_blank():
    cmds = parse_script("# lead\n\n  0, rate, 30   # trailing comment", SCHEMA)
    assert len(cmds) == 1 and cmds[0].verb == "rate"
check("comments and blank lines ignored", t_comment_and_blank)


def t_same_timestamp_order():
    cmds = parse_script("0, oars, hold port\n0, rate, 40", SCHEMA)
    assert [c.verb for c in cmds] == ["oars", "rate"]
check("same-timestamp commands keep file order", t_same_timestamp_order)


def t_space_separated():
    cmds = parse_script("0 rate 30", SCHEMA)
    assert cmds[0].args == (30.0,)
check("whitespace-separated fields accepted", t_space_separated)


# --- fail-fast errors ---

raises("unknown verb rejected", ScriptError,
       lambda: parse_script("0, speed, 8", SCHEMA))
raises("rate above ceiling rejected", ScriptError,
       lambda: parse_script("0, rate, 60", SCHEMA))
raises("negative rate rejected", ScriptError,
       lambda: parse_script("0, rate, -5", SCHEMA))
raises("bad oar state rejected", ScriptError,
       lambda: parse_script("0, oars, trailing", SCHEMA))
raises("missing required arg rejected", ScriptError,
       lambda: parse_script("0, oars", SCHEMA))
raises("too many args rejected", ScriptError,
       lambda: parse_script("0, helm, port, 0.5, extra", SCHEMA))
raises("non-numeric time rejected", ScriptError,
       lambda: parse_script("now, rate, 30", SCHEMA))
raises("negative time rejected", ScriptError,
       lambda: parse_script("-1, rate, 30", SCHEMA))
raises("missing verb rejected", ScriptError,
       lambda: parse_script("0,", SCHEMA))
raises("bad helm direction rejected", ScriptError,
       lambda: parse_script("0, helm, up", SCHEMA))
raises("helm fraction out of range rejected", ScriptError,
       lambda: parse_script("0, helm, port, 1.5", SCHEMA))


def t_error_line_number():
    try:
        parse_script("0, rate, 30\n7, oars, flying", SCHEMA)
        raise AssertionError("expected ScriptError")
    except ScriptError as e:
        assert "line 2" in str(e), str(e)
check("errors name the offending line", t_error_line_number)

print(f"\n{passed} checks passed")
