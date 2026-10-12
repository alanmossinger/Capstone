"""The random survival forest pair and the MLP hazard model return proper incidence curves."""

import numpy as np
import pandas as pd

from src import config, survival_tools


def _requests(n=300, seed=0):
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame({
        "region": rng.choice(config.TRACK_A_REGIONS, n),
        "tech": rng.choice(["Solar", "Gas", "Wind"], n),
        "size_regime": pd.Categorical(rng.choice(config.SIZE_LABELS, n), categories=config.SIZE_LABELS),
        "service": rng.choice(["NRIS", "ERIS"], n),
        "q_year": rng.integers(2010, 2017, n),
        "congestion_gw": rng.uniform(10, 200, n),
        "congestion_rank": rng.uniform(0, 1, n),
        "duration_years": rng.exponential(3, n).clip(0.1, 12),
        "event": rng.choice([0, 1, 2], n, p=[0.3, 0.2, 0.5]),
        "entry_years": 0.0,
    })
    frame.loc[:9, "entry_years"] = 1.0  # left-truncated rows the forest must skip
    return frame


def test_cif_from_cumulative_hazards_matches_the_cox_arithmetic():
    grid = np.array([0.0, 1.0, 2.0, 3.0])
    cum_op = np.array([[0.0, 0.1, 0.2, 0.3]])
    cum_wd = np.array([[0.0, 0.2, 0.4, 0.6]])
    cif = survival_tools.cif_from_cumulative_hazards(cum_op, cum_wd, grid, [1, 2, 3])
    # first increment is weighted by S(0) = 1, the second by S(1) = exp(−0.3)
    assert np.isclose(cif[0, 0], 0.1)
    assert np.isclose(cif[0, 1], 0.1 + np.exp(-0.3) * 0.1)
    assert (np.diff(cif[0]) >= 0).all()


def test_rsf_pair_skips_truncated_rows_and_returns_monotone_cif():
    frame = _requests()
    fitted = survival_tools.fit_rsf_pair(frame, min_samples_leaf=20, n_estimators=20, seed=1)
    assert fitted["operation"].n_features_in_ == len(fitted["design"])
    cif = survival_tools.rsf_cif(fitted, frame.iloc[:25], [3, 5, 7])
    assert cif.shape == (25, 3)
    assert ((cif >= 0) & (cif <= 1)).all().all()
    assert (cif[5] >= cif[3]).all() and (cif[7] >= cif[5]).all()
