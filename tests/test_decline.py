"""The Arps fit recovers known parameters from a clean decline and falls back honestly on thin histories."""

import numpy as np

from src import decline


def test_fit_recovers_a_hyperbolic_decline():
    t = np.arange(48)
    q = decline.arps(t, 5000.0, 0.08, 0.7)
    fit = decline.fit_arps(q)
    assert fit["form"] == "hyperbolic"
    assert abs(fit["q_i"] - 5000) / 5000 < 0.02 and abs(fit["d_i"] - 0.08) < 0.01 and abs(fit["b"] - 0.7) < 0.1
    assert np.isclose(decline.forecast_arps(fit, 12, 48), decline.arps(59, 5000.0, 0.08, 0.7), rtol=0.03)


def test_exponential_case_and_zero_months_are_dropped_not_imputed():
    t = np.arange(36)
    q = decline.arps(t, 2000.0, 0.05, 0.0)
    q[5] = 0.0  # a shut-in month
    fit = decline.fit_arps(q)
    assert fit["n"] == 35 and fit["b"] < 0.05 and abs(fit["d_i"] - 0.05) < 0.005


def test_thin_history_returns_a_flat_curve():
    fit = decline.fit_arps([0.0, 120.0, 0.0])
    assert fit["form"] == "flat" and fit["q_i"] == 120.0 and decline.forecast_arps(fit, 6, 3) == 120.0
