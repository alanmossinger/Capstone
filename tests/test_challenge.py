"""The challenger: rules read into preferences are validated, the tools find rule breaches, the repair is the fewest changes, a guide the evidence does not support is downgraded."""

import json
from types import SimpleNamespace

import numpy as np
import pytest

from src import challenge as ch


def _setting():
    """Four candidates: two leases (safe), a risky gas request, a wind request; budget 3 units, cap 40%."""
    rng = np.random.default_rng(0)
    S = 400
    lease = rng.normal(5.0, 1.0, size=(S, 2))
    gas = np.where(rng.random(S) < 0.1, 60.0, -4.0)[:, None]  # loses in 90% of scenarios, large rare gain
    wind = rng.normal(2.0, 0.5, size=(S, 1))
    A = np.hstack([lease, gas, wind]) * 1e6
    held = SimpleNamespace(op_year=np.zeros((S, 2), int))
    return SimpleNamespace(A=A, A_h=A.copy(), charge=np.array([1.0, 1.0, 1.0, 1.0]) * 1e6, budget=3.0e6, ids=["L1", "L2", "G", "W"],
                           tech=np.array(["Lease", "Lease", "Gas", "Wind"]), power_idx=np.array([2, 3]), capex_p=np.array([10.0, 10.0]) * 1e6,
                           carry_p=np.array([0.1, 0.1]) * 1e6, p7=np.array([0.1, 0.1]), priority=np.array([1.0, 2.0]), held=held, grid="committee", calls=np.zeros((S, 4)),
                           vector=lambda members: np.array([1 if m in members else 0 for m in ["L1", "L2", "G", "W"]]))


def test_preferences_refuse_unknown_fields_and_values_out_of_range():
    with pytest.raises(ch.PreferenceError):
        ch.Preferences.from_dict({"max_p_loss": 1.5}, ["a"], ["Wind"])
    with pytest.raises(ch.PreferenceError):
        ch.Preferences.from_dict({"interest_rate": 0.05}, ["a"], ["Wind"])
    with pytest.raises(ch.PreferenceError):
        ch.Preferences.from_dict({"excluded_technologies": ["Coal"]}, ["a"], ["Wind"])
    assert ch.Preferences.from_dict({"max_p_loss": 0.1, "excluded_ids": ["a"]}, ["a"], ["Wind"]).max_p_loss == 0.1


def test_rule_checks_flag_the_cap_and_the_committee_s_own_limits():
    s = _setting()
    s.budget = 3.0e6
    rules = ch.rule_checks(s, np.array([1, 1, 1, 0]), ch.Preferences(max_p_loss=0.0, excluded_technologies=["Gas"]))
    broken = {r["rule"] for r in rules if r["broken"]}
    assert "technology cap, Lease (share of budget)" in broken  # two leases = 2/3 of the budget > 40%
    assert "excluded candidates held (count)" in broken


def test_the_repair_is_the_fewest_changes_that_keep_the_rules():
    s = _setting()
    s.budget = 5.0e6  # the cap is 2 units per technology
    x0 = np.array([1, 1, 1, 0])  # holds the gas request the committee says it will not fund
    rep = ch.repair(s, x0, ch.Preferences(excluded_technologies=["Gas"]))
    assert rep is not None and rep["dropped"] == ["G"] and rep["changes"] in (1, 2)
    assert not any(r["broken"] for r in ch.rule_checks(s, rep["x"], ch.Preferences(excluded_technologies=["Gas"]), A=s.A))


def test_guide_is_allowed_only_toward_an_alternative_the_evidence_supports():
    diag = {"rules": [{"rule": "x", "broken": False}]}
    weak = {"optimizer": {"rules_broken": [], "vs_proposal": {"clear_of_zero": False}}}
    strong = {"optimizer": {"rules_broken": [], "vs_proposal": {"clear_of_zero": True}}}
    assert ch.qualifying(diag, weak) == [] and ch.qualifying(diag, strong) == ["optimizer"]
    broken = {"rules": [{"rule": "x", "broken": True}]}
    assert ch.qualifying(broken, weak) == ["optimizer"]  # a book that keeps the rule the proposal breaks qualifies


class _FakeAdvisor:
    """Returns canned answers by mode, as the recorded advisor would."""

    def __init__(self, read, memo):
        self.answers = {"challenge-read": read, "challenge-memo": memo}

    def ask(self, system, user, mode, tag=""):
        return {"response": json.dumps(self.answers[mode]), "replayed": True}


def test_an_unsupported_guide_is_downgraded_and_fact_references_are_checked(monkeypatch):
    s = _setting()
    s.budget = 5.0e6
    monkeypatch.setattr(ch.adv, "render", lambda name, **kw: name)
    memo = {"vulnerabilities": [{"claim": "The gas request loses in most scenarios.", "kind": "computed fact", "facts": ["F4"]}],
            "level": "guide", "recommended_book": "optimizer", "why": "", "loss_avoided": "none", "what_would_change_it": "", "evidence_insufficient": False,
            "question_for_the_committee": ""}
    out = ch.challenge(_FakeAdvisor({"preferences": {}, "whatifs": [], "reading": "maximise value", "not_representable": ""}, memo), s,
                       "We like gas.", ["L1", "G", "W"], "system")
    assert out["status"] == "challenged" and out["fact_refs_ok"]
    assert out["level"] in ("guide", "challenge")
    if "optimizer" not in ch.qualifying(out["diagnosis"], out["alternatives"]):
        assert out["level"] == "challenge"


def test_the_checklist_flags_a_fragile_member():
    s = _setting()
    s.budget = 5.0e6
    diag = ch.diagnose(s, np.array([1, 0, 1, 1]), ch.Preferences())
    flags = ch.checklist(diag, {})["flags"]
    assert any("fragile member: G" in f for f in flags)
