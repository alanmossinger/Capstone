"""Driver rates, crowding and the segment rules behave as documented."""

import numpy as np
import pandas as pd

from src import drivers


def test_wilson_is_inside_the_unit_interval_and_covers_the_point():
    low, high = drivers.wilson([0, 5, 50], [10, 10, 50])
    assert (low >= 0).all() and (high <= 1).all()
    assert low[0] == 0 and high[2] == 1
    assert low[1] < 0.5 < high[1]


def test_poi_crowding_counts_only_earlier_requests_inside_the_window():
    frame = pd.DataFrame({"region": ["PJM"] * 4 + ["ERCOT"],
                          "poi_name": ["Sub A", "sub  a", "Sub A", "Sub B", "Sub A"],
                          "q_date": pd.to_datetime(["2015-01-01", "2016-01-01", "2018-06-01", "2016-01-01", "2016-01-01"])})
    count = drivers.poi_crowding(frame, window_years=2)
    # the second request sees the first (same POI after normalising the name); the third is outside the window
    assert count.tolist()[:4] == [0, 1, 0, 0]
    assert count.iloc[4] == 0  # same name, other region


def test_stage_at_exit_is_ordered_and_unknown_is_last():
    stage = drivers.stage_at_exit(pd.Series(["IA Executed", "Feasibility Study", None, "Withdrawn"]))
    assert list(stage) == ["Agreement executed", "Feasibility study", "Unknown", "Unknown"]
    assert stage.categories[-1] == "Unknown"


def test_annual_hazards_count_exits_in_their_year():
    frame = pd.DataFrame({"region": ["PJM"] * 3, "duration_years": [0.5, 1.5, 3.0], "event": [2, 1, 0]})
    table = drivers.annual_hazards(frame, max_years=3).set_index("year_in_queue")
    assert table.loc[1, "at_risk"] == 3 and table.loc[1, "withdrawals"] == 1
    assert table.loc[2, "at_risk"] == 2 and table.loc[2, "operations"] == 1
    assert table.loc[3, "at_risk"] == 1 and table.loc[3, "operations"] == 0


def test_leaf_rules_translate_log_mw_back_to_megawatts():
    rng = np.random.default_rng(0)
    X = pd.DataFrame({"log_mw": np.log(rng.uniform(1, 1000, 400)), "region_PJM": rng.integers(0, 2, 400).astype(float)})
    y = (X["log_mw"] < np.log(20)).astype(int)
    tree = drivers.fit_segment_tree(X, y, max_depth=1, min_samples_leaf=20)
    rules = drivers.leaf_rules(tree, list(X.columns))
    assert len(rules) == 2
    assert any("MW" in cond for path in rules.values() for cond in path)
