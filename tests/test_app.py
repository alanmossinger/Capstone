"""The dashboard runs headless without an exception: the decision page through the registered example with no call, and the report's decision page."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

APP = Path(__file__).resolve().parents[1] / "app"


@pytest.fixture(scope="module")
def decide():
    """The decision page with recorded answers only: the registered case X25 replays from results/advisor_runs.jsonl."""
    at = st_testing.AppTest.from_file(str(APP / "decide.py"), default_timeout=900)
    at.session_state["replay_only"] = True
    return at.run()


def test_the_decision_page_opens_with_the_options_and_the_recommended_book(decide):
    assert not decide.exception, [str(e) for e in decide.exception]
    assert len(decide.dataframe) >= 2  # the four books, the forty candidates
    assert len(decide.multiselect(key="members").value) == 13  # book D: five leases and eight requests


def test_the_registered_example_is_challenged_from_the_record_and_the_result_is_scored(decide):
    decide.button(key="example").click().run()
    decide.button(key="challenge").click().run()
    assert not decide.exception, [str(e) for e in decide.exception]
    text = "\n".join(m.value for m in decide.markdown)
    assert "sunk cost" in text.lower()  # X25's flaw, named by the recorded memo
    assert "The advisor's solution" in text
    decide.radio(key="choice").set_value("Take the advisor's solution in full").run()
    decide.button(key="decide").click().run()
    assert not decide.exception, [str(e) for e in decide.exception]
    assert any("accepted the advisor's solution in full" in s.value for s in decide.success)
    assert len(decide.metric) >= 8  # your decision and the advisor's solution, four scores each


def test_a_departure_from_the_advisors_solution_needs_the_five_answers(decide):
    decide.radio(key="choice").set_value("Change some members").run()
    members = decide.multiselect(key="final_members").value
    decide.multiselect(key="final_members").set_value(members[:-1]).run()
    decide.button(key="decide").click().run()
    assert any("answer the five questions first" in e.value for e in decide.error)


@pytest.fixture(scope="module")
def report():
    return st_testing.AppTest.from_file(str(APP / "executive.py"), default_timeout=120).run()


def test_the_report_page_opens_with_what_is_decided_and_the_four_numbers(report):
    assert not report.exception, [str(e) for e in report.exception]
    assert any("What is being decided" in m.value for m in report.markdown)
    assert len(report.metric) >= 4
    assert len(report.tabs) == 7


def test_no_metric_carries_an_unescaped_pair_of_dollar_signs(report):
    """Streamlit reads two dollar signs in one metric delta as a formula; the page escapes them."""
    for m in report.metric:
        delta = str(m.proto.delta)
        assert delta.count("$") - delta.count(r"\$") < 2, delta


def test_your_call_without_a_facility_turns_to_equal_capital(report):
    assert any("5 leases and 8 requests" in m.value for m in report.markdown)
    no_line = [r for r in report.radio if "standby credit line" in r.label][0]
    no_line.set_value("no").run()
    assert not report.exception, [str(e) for e in report.exception]
    assert any("Without a facility, fund equal capital by sector" in m.value for m in report.markdown)
