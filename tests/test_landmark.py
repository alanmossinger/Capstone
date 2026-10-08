"""The landmark features use only information dated before the landmark (criterion C12)."""

import numpy as np
import pandas as pd

from src import landmark


def _frame():
    return pd.DataFrame({"q_date": pd.to_datetime(["2017-01-01", "2017-01-01", "2017-01-01"]),
                         "duration_years": [4.0, 1.5, 6.0], "event": [1, 2, 0], "entry_years": [0.0, 0.0, 2.0]})


def test_agreement_flag_is_known_only_from_the_year_after_the_agreement():
    frame = _frame()
    ia = pd.Series(pd.to_datetime(["2018-06-01", pd.NaT, "2017-01-01"]), index=frame.index)
    rows = pd.DataFrame({"project": [0, 0, 0, 1, 2, 2], "year_in_queue": [1, 2, 3, 2, 1, 2]})
    flag = landmark.ia_before_year(rows, frame, ia)
    # project 0: agreement 2018-06-01 is before the start of year 3 (2019-01-01) only
    assert flag.tolist()[:3] == [0.0, 0.0, 1.0]
    assert flag.tolist()[3] == 0.0  # no dated agreement → never flagged
    # project 2: agreement on the request day is not before the start of year 1, but is before year 2
    assert flag.tolist()[4:] == [0.0, 1.0]


def test_risk_set_requires_being_in_the_queue_and_past_delayed_entry():
    frame = _frame()
    assert landmark.risk_set(frame, 1).tolist() == [True, True, False]  # project 2 enters the risk set only at year 2
    assert landmark.risk_set(frame, 2).tolist() == [True, False, True]


def test_conditional_cif_restarts_at_the_landmark():
    h_op = np.array([[0.1, 0.2, 0.0]])
    h_wd = np.array([[0.3, 0.0, 0.0]])
    out = landmark.conditional_cif(h_op, h_wd, 1, [1, 2, 3])
    assert np.isclose(out.loc[0, 1], 0.1)
    assert np.isclose(out.loc[0, 2], 0.1 + 0.6 * 0.2)
    assert np.isclose(out.loc[0, 3], out.loc[0, 2])


def test_agreement_lookup_splits_cells_by_what_is_known_at_the_landmark():
    rng = np.random.default_rng(0)
    n = 400
    q = pd.Timestamp("2010-01-01")
    agreed = np.arange(n) < 200
    train = pd.DataFrame({"q_date": q, "region": "R", "tech": "solar", "size_regime": "large", "entry_years": 0.0,
                          "duration_years": 2.5 + rng.uniform(0, 2, n), "event": np.where(agreed, 1, 2)})
    ia = pd.Series(np.where(agreed, q + pd.Timedelta(days=200), pd.NaT), index=train.index, dtype="datetime64[ns]")
    target = train.iloc[[0, 300]].copy()  # one with an agreement known at +2, one without
    out = landmark.agreement_lookup_at_landmark(train, target, 2, [3], ia)
    assert out["agreement_known"].tolist() == [True, False]
    assert out.loc[0, 3] > 0.9 and out.loc[300, 3] < 0.1  # every agreed request operated, every other withdrew
