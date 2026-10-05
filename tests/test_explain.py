"""Tests for the feature encoding behind notebook 09's explanations.

The encoding must round-trip, and size must land on the right side of the
FERC 20 MW step when the size regime is rebuilt from MW.
"""

import numpy as np
import pandas as pd

from src import explain


def toy():
    return pd.DataFrame({"region": ["PJM", "ERCOT", "CAISO"], "state": ["VA", "TX", "CA"],
                         "tech": ["Solar", "Gas", "Battery"], "hybrid": [False, False, True],
                         "log_mw": np.log([19.99, 20.0, 150.0]), "service": ["NRIS", "missing", "ERIS"],
                         "q_year": [2017.0, 2018.0, 2019.0], "congestion_gw": [80.0, 30.0, 120.0],
                         "congestion_rank": [0.4, np.nan, 0.9]})


def test_encode_decode_round_trip():
    states = ["CA", "TX", "VA"]
    frame = explain.decode(explain.encode(toy(), states), states)
    original = toy()
    for column in ["region", "state", "tech", "service"]:
        assert frame[column].tolist() == original[column].tolist()
    assert frame["hybrid"].tolist() == [False, False, True]
    assert np.allclose(frame["log_mw"], original["log_mw"])
    assert np.isclose(frame["congestion_rank"].iloc[1], 0.5)  # missing rank → 0.5, as in the models


def test_size_regime_rebuilt_on_the_right_side_of_20_mw():
    states = ["CA", "TX", "VA"]
    frame = explain.decode(explain.encode(toy(), states), states)
    assert frame["size_regime"].tolist() == ["5–<20", "20–<100", "100–<200"]
