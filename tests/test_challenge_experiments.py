"""The registered experiments: the case list is as registered (48 cases, 12 clean, four per flaw; 40 statements, 8 out of scope) and the scoring follows the keys."""

import pandas as pd

from src import challenge_experiments as cx


def test_the_case_list_has_the_registered_shape():
    flaws = pd.Series([c["flaw"] for c in cx.CASES]).value_counts()
    assert len(cx.CASES) == 48 and flaws["none"] == 12
    assert all(flaws[f] == 4 for f in list(cx.COMPUTABLE) + list(cx.REASONING))
    assert len({c["id"] for c in cx.CASES}) == 48 and all(c["persona"] in cx.PERSONAS for c in cx.CASES)
    assert len(cx.STATEMENTS) == 40 and sum(k is None for _, _, k in cx.STATEMENTS) == 8


def test_detection_is_by_the_type_of_a_named_vulnerability():
    case = {"flaw": "sunk"}
    assert cx.detected(case, {"types": ["sunk cost", "fragile position"]})
    assert not cx.detected(case, {"types": ["fragile position"]})
    assert cx.detected({"flaw": "liquidity"}, {"types": ["unfunded construction calls"]})


def test_the_checklist_cannot_detect_a_flaw_in_the_words():
    r = {"checklist": {"flags": ["rule broken: chance of a loss", "fragile member: X"], "level": "guide"}}
    assert cx.checklist_detected({"flaw": "ploss"}, r)
    assert cx.checklist_detected({"flaw": "fragile", "relies_on": ["X"]}, r)
    assert not cx.checklist_detected({"flaw": "sunk"}, r)


def test_a_clean_case_is_falsely_challenged_by_a_guide_or_an_invented_flaw():
    assert cx.false_challenge({"level": "guide", "types": []})
    assert cx.false_challenge({"level": "challenge", "types": ["sunk cost"]})
    assert not cx.false_challenge({"level": "challenge", "types": ["fragile position", "unfunded construction calls"]})


def test_the_case_bootstrap_interval_contains_the_mean():
    b = cx.case_bootstrap([1.0, 2.0, 3.0, 4.0])
    assert b["low"] <= b["mean"] <= b["high"] and b["n"] == 4


def test_numbers_match_within_one_percent_and_lists_as_sets():
    assert cx._same(0.1, 0.1) and cx._same(1001, 1000) and not cx._same(1100, 1000)
    assert cx._same(["Solar", "Storage"], ["Storage", "Solar"]) and cx._same(None, None) and not cx._same(0.1, None)
