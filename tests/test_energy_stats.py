"""The statistics helpers behave on known series: a random walk is a unit root, white noise is stationary, a break is found."""

import numpy as np

from src import energy_stats as es


def test_stationarity_verdicts_on_known_series():
    rng = np.random.default_rng(0)
    noise = rng.normal(size=300)
    walk = np.cumsum(rng.normal(size=300))
    assert es.stationarity(noise, "noise")["verdict"] == "stationary"
    assert es.stationarity(walk, "walk")["verdict"] == "unit root"


def test_block_bootstrap_interval_covers_the_mean_and_keeps_length():
    rng = np.random.default_rng(1)
    x = 10 + rng.normal(size=120)
    out = es.block_bootstrap(x, np.mean, block=12, n_boot=300, seed=2)
    assert out["low"] <= out["estimate"] <= out["high"] and out["n"] == 120 and out["high"] - out["low"] < 1.0


def test_lagged_correlation_finds_the_lead():
    rng = np.random.default_rng(4)
    b = rng.normal(size=200)
    a = np.roll(b, 3) + 0.1 * rng.normal(size=200)  # a(t) follows b(t - 3)
    table = es.lagged_correlation(a, b, max_lag=6)
    assert table.loc[table["pearson"].idxmax(), "lag"] == 3


def test_chow_test_detects_a_level_shift():
    rng = np.random.default_rng(5)
    y = np.concatenate([rng.normal(0, 1, 60), rng.normal(5, 1, 60)])
    assert es.chow_test(y, 60)["p_value"] < 0.001
    flat = rng.normal(0, 1, 120)
    assert es.chow_test(flat, 60)["p_value"] > 0.01
