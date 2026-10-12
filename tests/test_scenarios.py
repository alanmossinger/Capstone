"""The scenario generators keep correlation, are reproducible by seed, and the risk measures and stresses behave."""

import numpy as np
import pandas as pd

from src import scenarios as sc


def _changes(n=200, rho=0.6, seed=0):
    rng = np.random.default_rng(seed)
    z = rng.multivariate_normal([0, 0, 0], [[1, rho, 0.2], [rho, 1, 0.3], [0.2, 0.3, 1]], size=n) * 0.05
    return z


def test_block_bootstrap_preserves_cross_correlation_and_is_seeded():
    changes = _changes()
    paths = sc.block_bootstrap_paths(changes, n_scenarios=300, horizon_months=120, block=12, seed=1)
    assert paths.shape == (300, 120, 3)
    sim = paths.reshape(-1, 3)
    assert abs(np.corrcoef(sim[:, 0], sim[:, 1])[0, 1] - np.corrcoef(changes[:, 0], changes[:, 1])[0, 1]) < 0.08
    again = sc.block_bootstrap_paths(changes, n_scenarios=300, horizon_months=120, block=12, seed=1)
    assert np.array_equal(paths, again)


def test_copula_matches_marginals_and_rank_correlation():
    changes = _changes(n=400)
    paths = sc.gaussian_copula_paths(changes, n_scenarios=200, horizon_months=60, seed=3)
    sim = paths.reshape(-1, 3)
    assert abs(np.std(sim[:, 0]) - np.std(changes[:, 0])) < 0.01
    from scipy.stats import spearmanr
    assert abs(spearmanr(sim[:, 0], sim[:, 1]).statistic - spearmanr(changes[:, 0], changes[:, 1]).statistic) < 0.1


def test_paths_to_prices_starts_from_the_base_level():
    paths = np.zeros((2, 5, 3))
    prices = sc.paths_to_prices(paths, [70.0, 3.0, 30.0])
    assert np.allclose(prices[:, :, 0], 70.0) and np.allclose(prices[:, :, 2], 30.0)


def test_risk_measures_and_stress():
    x = np.concatenate([np.full(90, 10.0), np.full(10, -100.0)])
    out = sc.risk_measures(x, level=0.95)
    assert abs(out["p_negative"] - 0.10) < 1e-9 and out["cvar"] <= out["var"] < out["mean"] and out["cvar"] == -100.0
    base = np.ones((12, 3)) * [[70.0, 3.0, 30.0]]
    stressed = sc.stress_prices(base, {"hh": 1.5, "wti_path": "2020"}, wti_2020_path=np.full(6, 20.0))
    assert np.allclose(stressed[:6, 0], 20.0) and np.allclose(stressed[6:, 0], 70.0) and np.allclose(stressed[:, 1], 4.5)


def test_ratio_distribution_is_bounded_and_draws_have_the_right_shape():
    forecasts = pd.DataFrame({"line": ["lease_oil_h3"] * 5 + ["cf_Wind_h1"] * 2, "pred": [10, 10, 10, 10, 0, 0.3, 0.3], "y": [8, 50, 10, 12, 3, 0.33, 0.2]})
    ratios = sc.ratio_distribution(forecasts, "lease_oil")
    assert len(ratios) == 4 and ratios.max() <= 3.0 and ratios.min() >= 0.2
    draws = sc.draw_multipliers(ratios, n_scenarios=7, n_items=3, seed=0)
    assert draws.shape == (7, 3) and set(np.unique(draws)) <= set(np.unique(ratios))


def test_mean_reversion_bounds_the_long_run_dispersion_and_is_centred():
    changes = _changes(n=300)
    shocks = sc.block_bootstrap_paths(changes, n_scenarios=400, horizon_months=240, block=12, seed=5)
    prices = sc.mean_reverting_prices(shocks, [70.0, 3.0, 30.0], [60.0, 3.5, 35.0], half_life_months=48)
    last = np.log(prices[:, -1, :])
    assert abs(np.exp(last[:, 0].mean()) - 60.0) / 60.0 < 0.15  # reverts toward the long-run level
    walk = sc.paths_to_prices(shocks, [70.0, 3.0, 30.0])
    assert np.log(prices[:, -1, 0]).std() < np.log(walk[:, -1, 0]).std()  # far less dispersion than the random walk


def test_key_level_ratios_sum_within_each_key():
    forecasts = pd.DataFrame({"line": ["lease_oil_h3"] * 12, "key": ["L1"] * 6 + ["L2"] * 6,
                              "pred": [10] * 6 + [10] * 6, "y": [0, 20, 10, 10, 10, 10] + [5] * 6})
    ratios = sc.key_level_ratios(forecasts, "lease_oil", min_rows=6)
    assert sorted(np.round(ratios, 3).tolist()) == [0.5, 1.0]
