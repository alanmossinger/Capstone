"""The v8 ledger accepts only authorized decisions, gates overrides where they are written, and detects an edited row."""

import json

import numpy as np
import pytest

from src import advisor as adv, ledger


def _answers():
    return {k: "a full answer of more than twenty characters" for k in adv.REASONING_QUESTIONS}


def test_a_decision_needs_a_name_and_a_known_verb(tmp_path):
    path = tmp_path / "l.jsonl"
    with pytest.raises(ledger.NotAuthorized):
        ledger.record(ledger.Decision("invest now", ["A"], "", ["A"]), path)
    with pytest.raises(ValueError):
        ledger.record(ledger.Decision("buy everything", ["A"], "Alan", ["A"]), path)
    row = ledger.record(ledger.Decision("invest now", ["A"], "Alan", ["A"]), path)
    assert row["override"] is False and not path.read_text().count("\n") == 0


def test_an_override_is_written_only_through_the_gate(tmp_path):
    path = tmp_path / "l.jsonl"
    with pytest.raises(ledger.NotAuthorized):
        ledger.record(ledger.Decision("invest now", ["A", "B"], "Alan", ["A"]), path)
    with pytest.raises(ledger.NotAuthorized):
        ledger.record(ledger.Decision("invest now", ["A", "B"], "Alan", ["A"], gate_answers=_answers()), path)  # opposing case not read
    row = ledger.record(ledger.Decision("invest now", ["A", "B"], "Alan", ["A"], gate_answers=_answers(), opposing_case_read=True), path)
    assert row["override"] is True


def test_the_ledger_is_append_only_and_an_edit_breaks_the_chain(tmp_path):
    path = tmp_path / "l.jsonl"
    for verb in ("invest now", "monitor", "reject"):
        ledger.record(ledger.Decision(verb, ["A"], "Alan", ["A"], scenario_fingerprint=ledger.fingerprint(np.ones((3, 2)))), path)
    assert ledger.verify_chain(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["members"] = ["Z"]
    path.write_text("\n".join([json.dumps(first)] + lines[1:]) + "\n", encoding="utf-8")
    assert not ledger.verify_chain(path)
