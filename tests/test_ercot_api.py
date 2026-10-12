"""The ERCOT client fails clearly without credentials, scrubs secrets from errors and recognises the network-edge block."""

import pytest

from src import ercot_api


def test_missing_credentials_name_the_variables(monkeypatch):
    for name in ("ERCOT_SUBSCRIPTION_KEY", "ERCOT_USERNAME", "ERCOT_PASSWORD"):
        monkeypatch.setenv(name, "")
    monkeypatch.setattr(ercot_api, "load_dotenv", lambda *_: None)
    with pytest.raises(RuntimeError, match="ERCOT_SUBSCRIPTION_KEY, ERCOT_USERNAME and ERCOT_PASSWORD"):
        ercot_api.load_credentials()


def test_scrub_replaces_every_secret():
    text = ercot_api._scrub("key=abc user=u@x.org pw=hunter2", ("abc", "u@x.org", "hunter2"))
    assert text == "key=<secret> user=<secret> pw=<secret>"


class _Response:
    def __init__(self, text, status_code=403):
        self.text, self.status_code = text, status_code


def test_incapsula_interstitial_is_recognised():
    assert ercot_api._blocked(_Response('<html><iframe src="/_Incapsula_Resource?CWUDNSAI=23"></iframe></html>'))
    assert not ercot_api._blocked(_Response('{"_meta": {"totalRecords": 24}, "data": []}', 200))


def test_page_to_frame_uses_the_api_column_names():
    body = {"fields": [{"name": "deliveryDate"}, {"name": "hourEnding"}, {"name": "settlementPointPrice"}],
            "data": [["2023-01-03", "01:00", 21.5], ["2023-01-03", "02:00", 20.1]]}
    frame = ercot_api.page_to_frame(body)
    assert list(frame.columns) == ["deliveryDate", "hourEnding", "settlementPointPrice"] and len(frame) == 2
