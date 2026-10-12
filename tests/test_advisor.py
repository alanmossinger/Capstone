"""The grounding check catches invented numbers, replay serves the record without a key, the override gate holds."""

import json

import pandas as pd

from src import advisor as adv


CONTEXT = adv.format_table(pd.DataFrame({"book": ["D risk-aware MILP", "A top-N NPV"], "expected_npv_$B": [20.65, 21.07], "cvar_loss_$B": [-0.30, -0.30], "p_negative": [0.0185, 0.0175]}),
                           "Books out of sample", "FORECAST")


def test_verify_numbers_accepts_table_numbers_and_flags_inventions():
    ok = adv.verify_numbers("Book D earns 20.6 with a tail of -0.30; A earns 21.1. In 2024 we had 24 candidates.", CONTEXT)
    assert ok["n_numbers"] == 3 and ok["rate"] == 1.0 and ok["ungrounded"] == []
    bad = adv.verify_numbers("Book D earns 20.65 and A about 21.07 billion, a tail of -0.30.", CONTEXT)  # the unrounded values were never shown
    assert bad["ungrounded"] == ["20.65", "21.07"] and abs(bad["rate"] - 1 / 3) < 1e-9


def test_replay_serves_the_record_and_returns_none_when_offline_without_record(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(adv, "api_key", lambda: None)
    runs = tmp_path / "runs.jsonl"
    a = adv.Advisor(mode="replay", runs_path=runs)
    assert a.ask("sys", "user", "test") is None and a.calls["missing"] == 1
    key = a._key("sys", "user")
    runs.write_text(json.dumps({"key": key, "response": "recorded", "model": adv.MODEL, "verification": {"rate": 1.0}}) + "\n", encoding="utf-8")
    b = adv.Advisor(mode="replay", runs_path=runs)
    out = b.ask("sys", "user", "test")
    assert out["response"] == "recorded" and out["replayed"] is True and b.calls["replayed"] == 1


def test_live_mode_without_key_raises(monkeypatch):
    monkeypatch.setattr(adv, "api_key", lambda: None)
    try:
        adv.Advisor(mode="live")
        assert False, "live mode must refuse to start without a key"
    except RuntimeError as err:
        assert "ANTHROPIC_API_KEY" in str(err)


def test_prompts_render_and_json_parses():
    text = adv.render("gym_pick", as_of="the end of 2018", budget="$100M", situation="ERCOT 2018 entry")
    assert "the end of 2018" in text and '"members"' in text
    assert adv.parse_json('```json\n{"members": ["a"], "cost_used": 1}\n```')["members"] == ["a"]
    assert adv.parse_json("no json here") is None
    for name in ("advisor_system", "motivated_reasoning_check", "ideological_turing_test", "recommend"):
        assert adv.load_prompt(name)


def test_override_gate_needs_every_answer_and_the_opposing_case():
    answers = {k: "an answer long enough to count as one" for k in adv.REASONING_QUESTIONS}
    assert adv.override_allowed(answers, opposing_case_read=True) == (True, [])
    allowed, missing = adv.override_allowed({**answers, "framing": "no"}, opposing_case_read=False)
    assert not allowed and missing == ["framing", "opposing_case_read"]


def test_ledger_append_keeps_the_fixed_columns(tmp_path):
    path = tmp_path / "ledger.csv"
    ledger = adv.ledger_append({"entry_id": "T1", "actor": "human", "members": "a;b", "n_members": 2}, path=path)
    assert list(ledger.columns) == adv.LEDGER_COLUMNS and len(ledger) == 1 and ledger.loc[0, "date"]
