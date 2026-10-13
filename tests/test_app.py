"""The dashboard runs headless in both modes without an exception and reads only results/ (no key needed)."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

APP = Path(__file__).resolve().parents[1] / "app" / "app.py"


@pytest.fixture(scope="module")
def app():
    return st_testing.AppTest.from_file(str(APP), default_timeout=600).run()


def test_decide_forward_renders_the_resolved_book_and_the_four_books(app):
    assert not app.exception, [str(e) for e in app.exception]
    assert any("Decide forward" in t.value for t in app.title)
    assert len(app.metric) >= 5  # members, capital, expected NPV, CVaR, P(NPV < 0)
    assert len(app.slider) == 3  # budget, λ, cap


def test_the_gym_builds_its_situations_and_shows_the_as_of_table(app):
    app.radio[0].set_value("Learn from history (the gym)").run()
    assert not app.exception, [str(e) for e in app.exception]
    assert any("Learn from history" in t.value for t in app.title)
    assert len(app.selectbox) >= 1 and len(app.dataframe) >= 1
