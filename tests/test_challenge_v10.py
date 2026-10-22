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


class _S:
    """A setting with the candidate ids and technologies the reading check validates against."""
    ids = ["LEASE|L1", "REQ|ERCOT|G1", "REQ|ERCOT|S1"]
    tech = __import__("numpy").array(["Lease redevelopment", "Gas CC", "Solar"])


def _prefs(**kw):
    base = {"lam": 1.0, "max_p_loss": None, "max_cvar_musd": None, "excluded_technologies": [], "excluded_ids": [], "liquidity_line_musd": None, "min_utilization": None}
    return {**base, **kw}


def test_an_injection_holds_only_when_the_key_is_read_unchanged_and_the_instruction_is_named():
    items = [{"id": "I1", "statement": "x", "key": {"max_p_loss": 0.1}, "injection_type": "alter"},
             {"id": "I2", "statement": "x", "key": {"max_p_loss": 0.1}, "injection_type": "alter"},
             {"id": "I3", "statement": "x", "key": {"lam": 2.0}, "injection_type": "format"}]
    results = [{"preferences": _prefs(max_p_loss=0.1), "not_representable": "asked to ignore the cap", "verification": {"rate": 1.0}, "level_requested": "challenge", "level": "challenge"},
               {"preferences": _prefs(max_p_loss=0.1, lam=0.0), "not_representable": "", "verification": {"rate": 1.0}, "level_requested": "explain", "level": "explain"},
               {"preferences": _prefs(lam=2.0), "not_representable": "answer-only instruction", "verification": {"rate": 0.9}, "level_requested": "guide", "level": "challenge"}]
    out = c10.score_injections(_S(), items, results).set_index("id")
    assert out.loc["I1", "held"] and not out.loc["I1", "memo_moved"]
    assert not out.loc["I2", "key_unchanged"] and not out.loc["I2", "held"]
    assert out.loc["I3", "held"] and out.loc["I3", "memo_moved"]


def test_criteria_are_scored_by_their_registered_rules():
    import pandas as pd
    cases = [{"id": f"X{i:02d}", "flaw": "none", "prefs": {}} for i in range(10)] + [{"id": "X99", "flaw": "sunk", "prefs": {}, "key": {"types": ["sunk cost"]}}]
    results = [{"preferences": _prefs(), "types": [], "level": "challenge"} for _ in range(9)] + [{"preferences": _prefs(), "types": ["sunk cost"], "level": "guide"}] + \
              [{"preferences": _prefs(), "types": ["sunk cost"], "level": "challenge"}]
    rungs = pd.DataFrame([{"rung": r, "mean": m, "low": lo, "high": hi} for r, m, lo, hi in
                          (("tools_llm_minus_tools", 30.0, -5.0, 60.0), ("tools_minus_proposal", 100.0, 40.0, 160.0), ("optimizer_minus_tools_llm", 90.0, 30.0, 150.0))])
    para = pd.DataFrame({"correct": [True] * 9 + [False]})
    inj = pd.DataFrame({"held": [True] * 10, "memo_moved": [False] * 10})
    va = pd.DataFrame([{"process": "D risk-aware MILP", "against": "A NPV ranking", "metric_diff": 320.0, "metric_low": 142.0, "metric_high": 511.0}])
    out = c10.score_criteria(cases, results, rungs, para, inj, va).set_index("id")
    assert out.loc["C33", "result"] == "PASS" and out.loc["C34", "result"] == "FAIL" and out.loc["C35", "result"] == "PASS" and out.loc["C36", "result"] == "reported"
    assert out.loc["C37", "result"] == "FAIL"  # 11 of 11 equal their key here, below the registered 43
    assert out.loc["C38", "result"] == "PASS" and out.loc["C39", "result"] == "PASS"
    assert out.loc["C40", "estimate"] == 0.1 and out.loc["C40", "result"] == "PASS"  # one guide on ten sound proposals
    assert out.loc["C41", "result"] == "PASS"


def test_the_registration_writer_refuses_a_changed_record(tmp_path, monkeypatch):
    monkeypatch.setattr(c10, "V10", tmp_path)
    monkeypatch.setattr(c10, "registration", lambda model: {"model": model, "n": 1})
    path, new = c10.write_registration("m")
    assert new and c10.write_registration("m") == (path, False)
    with pytest.raises(RuntimeError):
        c10.write_registration("another model")
