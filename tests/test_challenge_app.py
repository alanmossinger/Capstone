"""The challenge page runs headless, shows the alternatives and the advisor's pick first, asks only after a reasoned choice, and judges with the answers."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

from src import advisor as adv  # noqa: E402

APP = Path(__file__).resolve().parents[1] / "app" / "challenge.py"


class FakeAdvisor:
    live = True

    def __init__(self):
        self.calls = []

    def ask(self, system, user, mode_name="", tag=""):
        self.calls.append(mode_name)
        text = {"challenge/questions": "1. What if the leases fail?\n2. Who wants what?\n3. Where is the sunk cost?\n4. Which table?\n5. What is off the table?",
                "challenge/opposing": "The case.\nCONVERGE: book D | DISAGREE: the grid"}.get(mode_name, "The verdict.")
        return {"response": text, "replayed": False, "verification": {"rate": 1.0, "n_numbers": 0, "n_grounded": 0, "ungrounded": []}}


def test_the_alternatives_and_the_pick_come_first_and_the_button_waits_for_reasons(monkeypatch):
    monkeypatch.setattr(adv, "Advisor", lambda mode="auto": FakeAdvisor())
    app = st_testing.AppTest.from_file(str(APP), default_timeout=120).run()
    assert not app.exception, [str(e) for e in app.exception]
    assert any("Reason my thinking" in t.value for t in app.title)
    assert len(app.dataframe) == 1 and any("advisor's pick" in m.value for m in app.markdown)
    assert len(app.radio) == 1 and app.button[0].disabled  # the book, and the button waits for reasons and a flip condition
    app.text_area[0].set_value("The leases already produce and every one of them is positive.")
    app.text_input[0].set_value("If the worst-5% loss of my book exceeded $1B I would switch.").run()
    app.radio[0].set_value("leases only (D rule)").run()
    app.button[0].click().run()
    assert not app.exception, [str(e) for e in app.exception]
    assert any("What if the leases fail?" in m.value for m in app.markdown)
    assert len(app.text_area) == 6  # the reasons and five answers


def test_short_answers_are_refused_and_full_answers_reach_the_verdict_and_the_gate(monkeypatch):
    monkeypatch.setattr(adv, "Advisor", lambda mode="auto": FakeAdvisor())
    app = st_testing.AppTest.from_file(str(APP), default_timeout=120).run()
    app.text_area[0].set_value("The leases already produce and every one of them is positive.")
    app.text_input[0].set_value("If the worst-5% loss of my book exceeded $1B I would switch.").run()
    app.button[0].click().run()
    for box in app.text_area[1:]:
        box.set_value("too short")
    app.button[1].click().run()
    assert any("characters" in e.value for e in app.error)
    for box in app.text_area[1:]:
        box.set_value("an answer long enough to count as a considered one")
    app.button[1].click().run()
    assert not app.exception, [str(e) for e in app.exception]
    assert any("Converge" in m.value for m in app.markdown)  # the advisor's final say
    assert any("gate is open" in m.value for m in app.markdown)
    assert len(app.metric) >= 1  # your book beside the advisor's
