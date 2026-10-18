"""The decision page runs headless, opens the models only after a stated book, and records nothing without a named authorizer."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

from src import ledger, paths  # noqa: E402

APP = Path(__file__).resolve().parents[1] / "app" / "decide.py"
needs_results = pytest.mark.skipif(not (paths.RESULTS / "v8" / "frontier.csv").exists() or not (paths.DATA_INTERIM / "scenario_state.npz").exists(),
                                   reason="notebooks 08 and 11 have not run on this machine")


@needs_results
def test_the_models_wait_for_a_stated_book_and_the_ledger_needs_a_name(tmp_path, monkeypatch):
    monkeypatch.setattr(ledger, "LEDGER_V8", tmp_path / "ledger.jsonl")
    app = st_testing.AppTest.from_file(str(APP), default_timeout=600).run()
    assert not app.exception, [str(e) for e in app.exception]
    assert not any("Ask the models" in h.value for h in app.header)  # nothing below step 2 before the reasons
    app.text_area[0].set_value("The leases already produce and the tail is what the committee fears.")
    app.text_input[0].set_value("A worst-5% loss above $500M would change my mind.").run()
    assert any("Ask the models" in h.value for h in app.header)
    app.button[-1].click().run()  # record with no name
    assert any("authorized" in e.value for e in app.error)
    assert not (tmp_path / "ledger.jsonl").exists()
