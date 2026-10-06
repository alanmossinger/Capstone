"""Tests for the level-repair helpers: the intercept shift and the rolling rule."""

import numpy as np
import pandas as pd
import pytest

from src import drift


def test_intercept_shift_matches_the_observed_level():
    rng = np.random.default_rng(0)
    p = rng.uniform(0.05, 0.3, 4000)
    y = (rng.uniform(size=4000) < drift.apply_intercept(p, -0.7)).astype(float)  # outcomes at a lower level
    a = drift.fit_intercept(p, y)
    assert abs(a - (-0.7)) < 0.15
    assert abs(drift.apply_intercept(p, a).mean() - y.mean()) < 0.01


def test_rolling_recalibration_uses_only_earlier_cohorts():
    rng = np.random.default_rng(1)
    n = 3000
    years = rng.choice([2016, 2017, 2018], n)
    regions = rng.choice(["PJM", "ERCOT"], n)
    p = rng.uniform(0.05, 0.3, n)
    y = (rng.uniform(size=n) < p * 0.5).astype(float)
    w = np.ones(n)
    out, table = drift.rolling_recalibration(p, y, w, years, regions, {2017: 2016, 2018: 2017})
    assert np.isnan(out[years == 2016]).all()  # 2016 has no source, so it is not scored
    assert np.isfinite(out[years != 2016]).all()
    assert set(table["scored_year"]) == {2017, 2018}
    assert (table["source_year"] < table["scored_year"]).all()
    with pytest.raises(AssertionError):
        drift.rolling_recalibration(p, y, w, years, regions, {2017: 2018})


def test_early_incidence_counts_events_within_the_horizon():
    frame = pd.DataFrame({"q_year": [2020] * 6, "duration_years": [0.5, 1.5, 2.5, 0.8, 3.0, 1.2],
                          "event": [1, 1, 1, 2, 0, 0]})
    out = drift.early_incidence(frame, [2020], horizons=(1, 2), n_boot=20)
    assert out.loc[out["horizon"] == 1, "operations"].iloc[0] == 1
    assert out.loc[out["horizon"] == 2, "operations"].iloc[0] == 2
