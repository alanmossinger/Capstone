"""Tests for entry-time features and outcome coding.

The congestion test compares the sorted sweep with a count done by hand on a
toy region; the outcome tests check the censoring rules of ``src/events.py``.
"""

import pandas as pd

from src import events, features


def _toy_region():
    """Five requests in one region and one in another, with known exits."""
    return pd.DataFrame({
        "region": ["R", "R", "R", "R", "R", "S"],
        "q_date": pd.to_datetime(["2010-01-01", "2011-01-01", "2012-01-01", "2013-01-01",
                                  "2013-01-01", "2012-06-01"]),
        "mw": [100.0, 200.0, 300.0, 400.0, 500.0, 50.0],
        "q_status": ["operational", "withdrawn", "active", "withdrawn", "active", "active"],
        "on_date": pd.to_datetime(["2012-01-01", None, None, None, None, None]),
        "wd_date": pd.to_datetime([None, "2011-06-01", None, "2020-01-01", None, None]),
    })


def test_congestion_matches_hand_count():
    out = features.congestion_at_entry(_toy_region())
    # 2010: nobody before. 2011: #0 waiting. 2012: #0 leaves that very day (still counted),
    # #1 left 2011-06 -> {#0}. 2013 (both rows): #0 gone 2012-01, #1 gone, #2 waiting -> {#2}.
    assert out["congestion_n"].tolist() == [0, 1, 1, 1, 1, 0]
    assert out["congestion_gw"].round(3).tolist() == [0.0, 0.1, 0.1, 0.3, 0.3, 0.0]


def test_congestion_uses_only_earlier_information():
    toy = _toy_region()
    later = toy.copy()
    later.loc[3, "wd_date"] = pd.Timestamp("2030-01-01")  # a change after every entry date
    assert features.congestion_at_entry(toy).equals(features.congestion_at_entry(later))


def test_size_regime_puts_20_mw_on_the_large_side():
    assert features.size_regime(pd.Series([19.9, 20.0])).astype(str).tolist() == ["5–<20", "20–<100"]


def test_event_coding_and_censoring():
    toy = _toy_region()
    toy.loc[1, "wd_date"] = pd.Timestamp("2025-02-01")  # withdrawn after the censor date
    toy.loc[2, "q_status"] = "suspended"
    coded = events.code_events(toy)
    assert coded["event"].tolist() == [1, 0, 0, 2, 0, 0]
    assert coded.loc[1, "exit_date"] == pd.Timestamp("2024-12-31")
    assert coded.loc[0, "duration_years"] == (pd.Timestamp("2012-01-01") - pd.Timestamp("2010-01-01")).days / 365.25
    assert (coded["exclusion"] == "").all()
