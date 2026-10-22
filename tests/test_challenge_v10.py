"""The v10 case material: templates carry every keyed rule and nothing else; the author's cases are checked, not written, by code."""

import json

import pytest

from src import challenge_experiments as cx, challenge_v10 as c10


def test_templates_are_deterministic_and_name_every_keyed_rule():
    for case in cx.CASES:
        if case["flaw"] not in cx.COMPUTABLE:
            continue
        s = c10.statement_of(case)
        assert s == c10.statement_of(case)
        for k, v in case["prefs"].items():
            for item in (v if isinstance(v, list) else [v]):
                assert str(item) in s, (case["id"], k)
        if case["flaw"] == "fragile":
            assert all(m in s for m in case["relies_on"])
    assert len(c10.templated_cases()) == 24 and len(c10.AUTHOR_IDS) == 24


def test_a_reasoning_case_cannot_be_templated():
    with pytest.raises(ValueError):
        c10.statement_of({"id": "X25", "flaw": "sunk", "book": {"base": "D"}, "prefs": {}})


def test_the_form_has_the_author_ids_with_empty_statements(tmp_path):
    form = json.loads(c10.write_form(tmp_path / "form.json").read_text(encoding="utf-8"))
    assert [c["id"] for c in form["cases"]] == c10.AUTHOR_IDS
    assert all(c["statement"] == "" for c in form["cases"]) and "_instructions" in form


def test_author_cases_are_checked_for_empty_statements_and_missing_keys(tmp_path):
    form = json.loads(c10.write_form(tmp_path / "form.json").read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="empty"):
        (tmp_path / "a.json").write_text(json.dumps(form), encoding="utf-8")
        c10.author_cases(tmp_path / "a.json")
    for c in form["cases"]:
        c["statement"] = "A statement."
        if c["flaw"] in cx.REASONING:
            c["key"] = {"types": ["sunk cost"]}
    (tmp_path / "b.json").write_text(json.dumps(form), encoding="utf-8")
    cases = c10.cases_v10(tmp_path / "b.json")
    assert len(cases) == 48 and [c["id"] for c in cases] == [c["id"] for c in cx.CASES]
    with pytest.raises(FileNotFoundError):
        c10.author_cases(tmp_path / "missing.json")


def test_ladder_rungs_are_paired_differences_of_the_per_case_means():
    import pandas as pd
    rows = []
    for cid, base in (("X01", 100.0), ("X02", 200.0)):
        for w in ("w1", "w2"):
            for arm, add in (("proposal", 0.0), ("tools", 10.0), ("tools_llm", 15.0), ("optimizer", 30.0)):
                rows.append({"id": cid, "world": w, "arm": arm, "metric": base + add})
    diffs, rungs = c10.ladder_rungs(pd.DataFrame(rows))
    assert (diffs["tools_minus_proposal"] == 10.0).all() and (diffs["tools_llm_minus_tools"] == 5.0).all() and (diffs["optimizer_minus_tools_llm"] == 15.0).all()
    assert set(rungs["rung"]) == set(diffs.columns) and (rungs["n"] == 2).all()


def test_reading_equals_key_fails_on_an_invented_or_altered_rule():
    case = {"prefs": {"liquidity_line_musd": 1000}}
    assert c10.reading_equals_key(case, {"preferences": {"lam": 1.0, "max_p_loss": None, "max_cvar_musd": None, "excluded_technologies": [], "excluded_ids": [], "liquidity_line_musd": 1000, "min_utilization": None}})
    assert not c10.reading_equals_key(case, {"preferences": {"lam": 1.0, "max_p_loss": 0.1, "max_cvar_musd": None, "excluded_technologies": [], "excluded_ids": [], "liquidity_line_musd": 1000, "min_utilization": None}})
    assert not c10.reading_equals_key(case, {"preferences": {"lam": 1.0, "max_p_loss": None, "max_cvar_musd": None, "excluded_technologies": [], "excluded_ids": [], "liquidity_line_musd": 1500, "min_utilization": None}})
    assert not c10.reading_equals_key(case, {"preferences": None})
