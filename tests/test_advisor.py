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


def test_live_mode_without_backend_raises(monkeypatch):
    monkeypatch.setattr(adv, "api_key", lambda: None)
    monkeypatch.setattr(adv, "cli_path", lambda: None)
    try:
        adv.Advisor(mode="live")
        assert False, "live mode must refuse to start without a key or the claude command"
    except RuntimeError as err:
        assert "ANTHROPIC_API_KEY" in str(err)


def test_auto_mode_falls_back_when_the_command_line_fails(monkeypatch, tmp_path):
    """An expired subscription sign-in must not stop an offline run: the call is counted missing and the reason kept."""
    monkeypatch.setattr(adv, "api_key", lambda: None)
    monkeypatch.setattr(adv, "cli_path", lambda: "claude")

    def failing(*args, **kwargs):
        raise RuntimeError("claude -p reported an error: sign-in expired")

    monkeypatch.setattr(adv, "ask_cli", failing)
    a = adv.Advisor(mode="auto", runs_path=tmp_path / "runs.jsonl")
    assert a.backend == "cli" and a.live
    assert a.ask("sys", "user", "test") is None
    assert a.calls["missing"] == 1 and not a.live and "sign-in" in a.last_error


def test_cli_environment_drops_session_variables(monkeypatch):
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "placeholder")
    env = adv.cli_environment()
    assert "CLAUDECODE" not in env and "ANTHROPIC_API_KEY" not in env
    assert env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] == "1"


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


def test_numbers_in_reads_unit_suffixes():
    found = adv.numbers_in("Budget $6.15B, cap 40%, 150k rows, 20.7, 1,234.5 and -0.30; v2; 3.4.5")
    assert {"6.15", "40", "150", "20.7", "1234.5", "-0.3"} <= found
    assert "2" not in found  # "v2" is a name, not a quantity


def test_format_answers_pairs_the_questions_with_the_answers():
    questions = "1. What if the leases fail?\n2. What does the lender want?\n3. Where is the sunk cost?\n4. Which table?\n5. What is off the table?"
    text = adv.format_answers(questions, {"context_and_stakes": "We lose the capital.", "framing": "A mixed book."})
    assert "Q1. What if the leases fail?\nA1. We lose the capital." in text
    assert "A2. (no answer)" in text and "Q5. What is off the table?\nA5. A mixed book." in text
    standing = adv.format_answers(None, {"parties": "The lender wants a thin tail."})
    assert "Q2. What does each party to the decision want?\nA2. The lender wants a thin tail." in standing


class FakeAdvisor:
    """Answers every call with its mode name, so the round's wiring can be checked without a model."""

    def __init__(self):
        self.asked = []

    def ask(self, system, user, mode_name="", tag=""):
        self.asked.append((mode_name, user))
        text = {"challenge/questions": "1. Q one?\n2. Q two?\n3. Q three?\n4. Q four?\n5. Q five?",
                "challenge/opposing": "The case.\nCONVERGE: book D | DISAGREE: the grid"}.get(mode_name, "The verdict.")
        return {"response": text, "replayed": False, "verification": {"rate": 1.0, "n_numbers": 0, "n_grounded": 0, "ungrounded": []}}


def test_challenge_asks_then_judges_with_the_answers():
    fake = FakeAdvisor()
    answers = {k: f"my answer to {k}, long enough to count" for k in adv.REASONING_QUESTIONS}
    out = adv.challenge(fake, "I want the leases only.", "Book D", "DATA tables", answers=answers, tag="t")
    modes = [m for m, _ in fake.asked]
    assert modes == ["challenge/questions", "challenge/check", "challenge/opposing"]
    assert "Q1. Q one?" in fake.asked[1][1] and "my answer to framing" in fake.asked[2][1]  # the verdict and the opposing case see the answers
    assert out["converge"] == "book D" and out["disagree"] == "the grid"
    assert "## The human's answers" in out["transcript"]
    assert adv.override_allowed(answers, opposing_case_read=True)[0]  # the same answers open the gate


def test_challenge_without_answers_still_returns_a_verdict():
    fake = FakeAdvisor()
    out = adv.challenge(fake, "I want the leases only.", "Book D", "DATA tables")
    assert out["check"] is not None and "no answers were given" in fake.asked[1][1]
