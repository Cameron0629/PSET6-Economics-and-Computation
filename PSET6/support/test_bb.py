#!/usr/bin/env python3

"""Tests for a generated TEAMNAMEbb.py balanced-bidding agent.

Run either

    python3 test_bb.py TEAMNAME

or, if exactly one ``*bb.py`` team file is present,

    python3 test_bb.py

The file remains compatible with pytest. Under pytest, set ``TEAMNAME`` in the
shell if the directory contains multiple generated balanced-bidding agents.
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from functools import lru_cache
from pathlib import Path

from history import History


SCRIPT_DIR = Path(__file__).resolve().parent


def _module_name() -> str:
    teamname = os.environ.get("TEAMNAME")
    if teamname:
        return f"{teamname.lower()}bb"

    candidates = sorted(
        path.stem
        for path in SCRIPT_DIR.glob("*bb.py")
        if path.name != "test_bb.py"
    )
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise AssertionError(
            "No generated TEAMNAMEbb.py file was found. "
            "Run `python3 start.py TEAMNAME` first."
        )
    raise AssertionError(
        "Multiple TEAMNAMEbb.py files were found. Run "
        "`python3 test_bb.py TEAMNAME` or set the TEAMNAME environment variable."
    )


@lru_cache(maxsize=1)
def balanced_bidding_class():
    module_name = _module_name()
    module = importlib.import_module(module_name)

    matches = [
        obj
        for name, obj in vars(module).items()
        if inspect.isclass(obj)
        and obj.__module__ == module.__name__
        and name.lower() == module_name.lower()
    ]
    if len(matches) != 1:
        expected = module_name[0].upper() + module_name[1:]
        raise AssertionError(
            f"{module_name}.py must define class {expected}. "
            "Regenerate the file with start.py or rename the class accordingly."
        )
    return matches[0]


def assert_integer_bid(actual, expected):
    assert isinstance(actual, int) and not isinstance(actual, bool), (
        f"Expected an integer-cent bid, got {actual!r} ({type(actual).__name__})."
    )
    assert actual == expected, f"Expected bid {expected}, got {actual}."


def test_bb():
    BBAgent = balanced_bidding_class()
    budget = 1000
    t = 1
    reserve = 0

    bids = [[(3, 10), (2, 5), (1, 4)]]
    occupants = [[3, 2, 1]]
    slot_clicks = [[3, 2, 0]]
    per_click_payments = [[5, 4, 0]]
    slot_payments = [[15, 8, 0]]
    history = History(
        bids,
        occupants,
        slot_clicks,
        per_click_payments,
        slot_payments,
        n_agents=4,
    )

    a1 = BBAgent(1, 8, budget)
    a2 = BBAgent(2, 10, budget)
    a3 = BBAgent(3, 20, budget)

    assert a1.expected_utils(t, history, reserve) == [-6, 6, 0]
    assert a1.target_slot(t, history, reserve) == (1, 5, 10)
    assert_integer_bid(a1.bid(t, history, reserve), 6)

    assert a2.expected_utils(t, history, reserve) == [0, 12, 0]
    assert a2.target_slot(t, history, reserve) == (1, 4, 10)
    assert_integer_bid(a2.bid(t, history, reserve), 6)

    assert a3.expected_utils(t, history, reserve) == [45, 32, 0]
    assert a3.target_slot(t, history, reserve) == (0, 5, 10)
    assert_integer_bid(a3.bid(t, history, reserve), 20)


def test_bb_reserve():
    BBAgent = balanced_bidding_class()
    budget = 1000
    t = 1
    reserve = 5

    bids = [[(3, 10), (2, 7), (1, 6)]]
    occupants = [[3, 2, 1]]
    slot_clicks = [[3, 2, 1]]
    per_click_payments = [[7, 6, 5]]
    slot_payments = [[21, 12, 5]]
    history = History(
        bids,
        occupants,
        slot_clicks,
        per_click_payments,
        slot_payments,
        n_agents=4,
    )

    a1 = BBAgent(1, 8, budget)
    a2 = BBAgent(2, 10, budget)
    a3 = BBAgent(3, 20, budget)

    assert a1.expected_utils(t, history, reserve) == [-6, 2, 3]
    assert a1.target_slot(t, history, reserve) == (2, 5, 7)
    assert_integer_bid(a1.bid(t, history, reserve), 6)

    assert a2.expected_utils(t, history, reserve) == [0, 8, 5]
    assert a2.target_slot(t, history, reserve) == (1, 6, 10)
    assert_integer_bid(a2.bid(t, history, reserve), 7)

    assert a3.expected_utils(t, history, reserve) == [39, 28, 15]
    assert a3.target_slot(t, history, reserve) == (0, 7, 14)
    assert_integer_bid(a3.bid(t, history, reserve), 20)


def test_bb_overbid():
    BBAgent = balanced_bidding_class()
    budget = 1000
    t = 1
    reserve = 0

    bids = [[(3, 16), (2, 14), (1, 4)]]
    occupants = [[3, 2, 1]]
    slot_clicks = [[3, 2, 0]]
    per_click_payments = [[14, 4, 0]]
    slot_payments = [[42, 8, 0]]
    history = History(
        bids,
        occupants,
        slot_clicks,
        per_click_payments,
        slot_payments,
        n_agents=4,
    )

    a1 = BBAgent(1, 8, budget)
    assert a1.expected_utils(t, history, reserve) == [-24, -12, 0]
    assert a1.target_slot(t, history, reserve) == (2, 0, 14)
    assert_integer_bid(a1.bid(t, history, reserve), 8)


def main():
    if len(sys.argv) > 2:
        raise SystemExit("Usage: python3 test_bb.py [TEAMNAME]")
    if len(sys.argv) == 2:
        os.environ["TEAMNAME"] = sys.argv[1]

    test_bb()
    test_bb_reserve()
    test_bb_overbid()
    print("All balanced-bidding tests passed.")


if __name__ == "__main__":
    main()
