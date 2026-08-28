"""Command-language parser tests (pytest)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from commands.parser import Command, ScriptError, load_schema, parse_file, parse_script

SCHEMA = load_schema()
SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "cruise_turn.txt"


def test_sample_script_parses():
    cmds = parse_file(SAMPLE, SCHEMA)
    assert [c.verb for c in cmds] == [
        "rate",
        "pressure",
        "rate",
        "helm",
        "oars",
        "oars",
        "rate",
        "pressure",
        "oars",
    ]
    assert cmds[0] == Command(time=0.0, verb="rate", args=(30.0,), lineno=4)
    assert cmds[4].args == ("hold", "starboard")
    assert cmds[7].args == ("steady", "port")


def test_optional_args_take_defaults():
    cmds = parse_script("10, oars, back\n20, helm, port\n30, pressure, spoude", SCHEMA)
    assert cmds[0].args == ("back", "both")  # side defaults to both
    assert cmds[1].args == ("port", 1.0)  # helm fraction defaults to 1
    assert cmds[2].args == ("spoude", "both")  # pressure side defaults to both


def test_rate_aliases():
    cmds = parse_script("0, rate, slow\n1, rate, racing", SCHEMA)
    assert cmds[0].args == (24.0,)
    assert cmds[1].args == (44.0,)


def test_numeric_pressure_and_side():
    cmds = parse_script("0, pressure, 0.5\n1, pressure, 1, port", SCHEMA)
    assert cmds[0].args == (0.5, "both")
    assert cmds[1].args == (1.0, "port")


def test_comments_and_blank_lines():
    cmds = parse_script("# lead\n\n  0, rate, 30   # trailing comment", SCHEMA)
    assert len(cmds) == 1 and cmds[0].verb == "rate"


def test_same_timestamp_keeps_file_order():
    cmds = parse_script("0, oars, hold port\n0, rate, 40", SCHEMA)
    assert [c.verb for c in cmds] == ["oars", "rate"]


def test_whitespace_separated():
    cmds = parse_script("0 rate 30", SCHEMA)
    assert cmds[0].args == (30.0,)


def test_unknown_verb_rejected():
    with pytest.raises(ScriptError):
        parse_script("0, speed, 8", SCHEMA)


def test_rate_out_of_range_rejected():
    with pytest.raises(ScriptError):
        parse_script("0, rate, 60", SCHEMA)
    with pytest.raises(ScriptError):
        parse_script("0, rate, -5", SCHEMA)


def test_bad_oar_state_rejected():
    with pytest.raises(ScriptError):
        parse_script("0, oars, trailing", SCHEMA)


def test_missing_required_arg_rejected():
    with pytest.raises(ScriptError):
        parse_script("0, oars", SCHEMA)


def test_too_many_args_rejected():
    with pytest.raises(ScriptError):
        parse_script("0, helm, port, 0.5, extra", SCHEMA)


def test_bad_time_rejected():
    with pytest.raises(ScriptError):
        parse_script("now, rate, 30", SCHEMA)
    with pytest.raises(ScriptError):
        parse_script("-1, rate, 30", SCHEMA)


def test_missing_verb_rejected():
    with pytest.raises(ScriptError):
        parse_script("0,", SCHEMA)


def test_bad_helm_rejected():
    with pytest.raises(ScriptError):
        parse_script("0, helm, up", SCHEMA)
    with pytest.raises(ScriptError):
        parse_script("0, helm, port, 1.5", SCHEMA)


def test_errors_name_the_line():
    with pytest.raises(ScriptError) as e:
        parse_script("0, rate, 30\n7, oars, flying", SCHEMA)
    assert "line 2" in str(e.value)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
