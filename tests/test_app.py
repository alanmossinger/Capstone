"""The dashboard runs headless without an exception, opens with what is decided, and answers the committee's two calls from results/."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

APP = Path(__file__).resolve().parents[1] / "app" / "executive.py"


@pytest.fixture(scope="module")
def app():
    return st_testing.AppTest.from_file(str(APP), default_timeout=120).run()


def test_the_page_opens_with_what_is_decided_and_the_four_numbers(app):
    assert not app.exception, [str(e) for e in app.exception]
    assert any("What is being decided" in m.value for m in app.markdown)
    assert len(app.metric) >= 4
    assert len(app.tabs) == 7


def test_no_metric_carries_an_unescaped_pair_of_dollar_signs(app):
    """Streamlit reads two dollar signs in one metric delta as a formula; the dashboard escapes them."""
    for m in app.metric:
        delta = str(m.proto.delta)
        assert delta.count("$") - delta.count(r"\$") < 2, delta


def test_your_call_with_a_facility_at_the_registered_weight_is_the_recommended_book(app):
    assert any("5 leases and 8 requests" in m.value for m in app.markdown)


def test_your_call_without_a_facility_turns_to_equal_capital(app):
    no_line = [r for r in app.radio if "standby credit line" in r.label][0]
    no_line.set_value("no").run()
    assert not app.exception, [str(e) for e in app.exception]
    assert any("Without a facility, fund equal capital by sector" in m.value for m in app.markdown)
