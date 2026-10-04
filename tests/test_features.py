"""Tests for entry-time features and outcome coding.

The congestion test compares the sorted sweep with a count done by hand on a
toy region; the outcome tests check the censoring rules of ``src/events.py``.
"""

import numpy as np
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


def _toy_clean():
    """The toy region with the extra columns ``build_features`` reads."""
    toy = _toy_region()
    toy["mw1"] = toy["mw"]
    toy["state"] = ["TX", "TX", "TX", "TX", "TX", "CA"]
    toy["type_clean"] = ["Solar", "Wind", "Solar", "Gas", "Solar", "Battery"]
    toy["hybrid"] = False
    toy["service"] = "NRIS"
    toy["q_year"] = toy["q_date"].dt.year
    toy["prop_date"] = toy["q_date"] + pd.DateOffset(years=3)
    toy["ia_date"] = pd.NaT
    return toy


def test_main_features_contain_no_post_entry_field():
    assert not set(features.MAIN_FEATURES) & set(features.POST_ENTRY_COLUMNS)
    assert not set(features.MAIN_FEATURES) & set(features.ABLATION_FEATURES)


def test_outcome_of_the_latest_entrant_cannot_move_any_feature():
    toy = _toy_clean()
    changed = toy.copy()
    latest = changed["q_date"].idxmax()  # nobody enters after it, so its outcome is pure future
    changed.loc[latest, ["q_status", "on_date", "ia_date"]] = ["operational", pd.Timestamp("2014-01-01"),
                                                             pd.Timestamp("2013-06-01")]
    changed["prop_date"] = changed["prop_date"] + pd.DateOffset(years=2)
    before = features.build_features(toy)[features.MAIN_FEATURES]
    after = features.build_features(changed)[features.MAIN_FEATURES]
    pd.testing.assert_frame_equal(before, after)


def test_congestion_on_dates_matches_entry_sweep():
    toy = _toy_region()
    at_entry = features.congestion_at_entry(toy)
    on_dates = features.congestion_on_dates(toy, toy["region"], toy["q_date"])
    assert np.allclose(at_entry.to_numpy(dtype=float), on_dates.to_numpy(dtype=float))


def test_congestion_rank_compares_with_earlier_requests_only():
    toy = _toy_region()
    rank = features.congestion_rank(toy, pd.Series([0.0, 0.1, 0.1, 0.3, 0.3, 0.0]))
    # region R in date order: 0.0 (first, no rank), 0.1 (above 1 of 1 earlier), 0.1 (above 1 of 2),
    # then two rows on the same day with 0.3: each is above the 3 earlier values
    assert np.isnan(rank[0]) and rank[1] == 1.0 and rank[2] == 0.5 and rank[3] == 1.0 and rank[4] == 1.0
    assert np.isnan(rank[5])  # only request of region S


def test_split_labels_and_track_b():
    years = pd.Series([2010, 2015, 2016, 2017, 2019, 2021])
    assert events.split_label(years).tolist() == ["train", "train", "validation", "test", "test", "later"]
    coded = events.code_events(_toy_clean())
    track_b = events.track_b_sample(coded)
    assert set(track_b["q_status"]) <= {"operational", "withdrawn"}
    assert track_b["built"].tolist() == (track_b["q_status"] == "operational").astype(int).tolist()
