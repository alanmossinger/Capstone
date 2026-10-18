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


def test_floored_baseline_never_declines_slower_than_the_floor():
    flat = np.full(36, 1000.0)  # a flat window: the unbounded fit returns no decline at all (audit E2)
    rates, rec = decline.floored_baseline(flat, 240, 0.08)
    yearly = rates.reshape(20, 12).sum(axis=1)
    assert rec["form"] == "fitted"
    assert np.all(yearly[1:] / yearly[:-1] <= 0.92 + 1e-9)
    assert abs(yearly[-1] / yearly[0] - 0.92 ** 19) < 1e-6


def test_steep_hyperbola_keeps_its_own_decline_until_it_reaches_the_floor():
    t = np.arange(36)
    q = decline.arps(t, 5000.0, 0.10, 1.0)  # starts at about 70% a year, slows below 8% later
    rates, rec = decline.floored_baseline(q, 240, 0.08)
    d_min = decline.monthly_decline(0.08)
    monthly = -np.diff(np.log(rates))
    assert monthly[0] > d_min  # early: the fitted, steeper decline
    assert np.allclose(monthly[-12:], d_min)  # late: exactly the floor


def test_a_lease_still_ramping_declines_from_its_recent_level():
    q = np.concatenate([np.full(30, 100.0), np.linspace(200.0, 600.0, 6)])  # the peak is in the last months
    rates, rec = decline.floored_baseline(q, 24, 0.08)
    assert rec["form"] == "ramp-up"
    assert abs(rec["level"] - q[-3:].mean()) < 1e-9 and rates[0] < rec["level"]
