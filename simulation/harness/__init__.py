"""The pair harness (plan §20, Phase 3).

One command stream, two simulators. script.py drives both ships with the
same commands, the same starting state and the same event semantics;
comparator.py computes the Level-2 equivalence metrics (plan §6) and prints
the equivalence table; run_validation.py is the validation runner over the
script set.
"""
