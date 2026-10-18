"""The advisor with tools: a question becomes parameters, the engine computes, the explanation may cite only what was computed, in its unit."""

import json

import pandas as pd

from src import advisor_tools as at, whatif as wi

RESULT = "| figure | base book | new book | change | unit |\n| expected NPV | 5,839 | 5,410 | -429 | $M |\n| chance of a loss | 0.03 | 0.05 | 0.02 | share |\n"


def test_numbers_must_come_from_the_result_and_keep_its_unit():
    ok = at.verify_attributed("Expected NPV falls from $5,839M to $5,410M, a change of -429 million.", RESULT)
    assert ok["rate"] == 1.0 and not ok["unit_errors"]
    wrong_unit = at.verify_attributed("Expected NPV falls to 5,410 billion.", RESULT)
    assert wrong_unit["unit_errors"] == ["5,410 billion"] and wrong_unit["rate"] == 0.0
    invented = at.verify_attributed("It would be about $6.2B.", RESULT)
    assert invented["ungrounded"] == ["6.2B"]


class FakeAdvisor:
    def __init__(self, answers):
        self.answers = list(answers)

    def ask(self, system, user, mode_name="", tag=""):
        return {"response": self.answers.pop(0)}


class FakeEngine:
    ids = ["LEASE|G1", "REQ|ERCOT|X"]

    def run(self, w):
        candidates = pd.DataFrame({"project_id": self.ids, "technology": ["Lease redevelopment", "Wind"], "in_book": [True, False], "charge_$M": [100.0, 5.0],
                                   "expected_npv_$M": [50.0, -1.0], "median_npv_$M": [45.0, -1.0], "p_negative": [0.1, 0.9], "status": ["invest now", "reject"]})
        same = {"n": 1, "charge": 1e8, "expected_npv": 5e7, "median_npv": 4.5e7, "p_loss": 0.1, "cvar_loss": 1e7, "hhi": 1.0}
        return {"whatif": w.changes(), "grid": w.grid, "revenue_case": w.revenue_case, "budget": 2e8, "feasible": True, "reason": None, "n_scenarios": 10,
                "provenance": "test", "diff": {"entered": [], "left": [], "old": same, "new": same, "change": {k: 0 for k in same}}, "candidates": candidates}


def test_the_pipeline_answers_refuses_and_reports():
    question = "What if WTI stays at $45 for five years?"
    answered = at.ask_whatif(FakeAdvisor([json.dumps({"whatif": {"wti_level": 45.0, "wti_years": 5}, "reading": "oil at 45"}), "Expected NPV stays at 50 $M."]),
                             FakeEngine(), question, "system")
    assert answered["status"] == "answered" and answered["whatif"].wti_level == 45.0 and answered["verification"]["rate"] == 1.0
    cannot = at.ask_whatif(FakeAdvisor([json.dumps({"cannot_answer": "no interest-rate parameter"})]), FakeEngine(), "What if rates rise?", "system")
    assert cannot["status"] == "cannot answer" and cannot["result"] is None
    refused = at.ask_whatif(FakeAdvisor([json.dumps({"whatif": {"wti_level": 900}})]), FakeEngine(), "Oil at $900?", "system")
    assert refused["status"] == "refused by the engine" and "outside the range" in refused["reading"]


def test_schema_lists_every_parameter_and_candidate():
    text = at.schema_text(["LEASE|G1"])
    assert all(f in text for f in ("wti_level", "cvar_limit_musd", "technology_cap", "forced_out")) and "LEASE|G1" in text


def test_the_questions_own_figures_may_be_repeated():
    v = at.verify_attributed("A budget cut of 20% leaves expected NPV at 5,410 $M.", RESULT, question="What if the budget is cut by 20%?")
    assert v["rate"] == 1.0


def test_a_change_may_be_cited_by_its_magnitude():
    v = at.verify_attributed("Expected NPV falls by 429 $M.", RESULT)
    assert v["rate"] == 1.0  # the fact sheet shows the change as -429
