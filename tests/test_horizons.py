"""The horizon view grows with the horizon, reaches the full-life value at twenty years, and the books fit the budget."""

import numpy as np
import pandas as pd

from src import horizons as hz


def test_power_within_reaches_the_full_life_expected_npv_at_twenty_years_and_is_minus_carry_before_operation():
    curve = np.array([0.0, 0.1, 0.3, 0.4, 0.5, 0.5, 0.5])
    rate, mw, capex, carry = 0.06, 100.0, 100e6, 5e6
    expected = 20e6
    assert hz.power_within(expected, carry, capex, mw, curve, rate, 1) == -carry
    values = [hz.power_within(expected, carry, capex, mw, curve, rate, h) for h in (2, 3, 5, 10, 27)]
    assert values[-1] > values[0]
    # at year 7 + life the whole margin stream is in, so the value is the full-life expected NPV
    assert abs(values[-1] - expected) / abs(expected) < 1e-6


def test_lease_within_is_monotone_in_the_horizon_once_the_workover_is_paid():
    bo, bg = np.full(240, 20000.0), np.full(240, 30000.0)
    wti, hh = np.full(240, 70.0), np.full(240, 3.0)
    v = [hz.lease_within(bo, bg, wti, hh, 4, h) for h in (1, 2, 3, 5, 10, 20)]
    assert v[0] < v[2] < v[-1]


def test_horizon_books_respect_the_budget():
    ids = [f"c{i}" for i in range(6)]
    view = pd.DataFrame([{"project_id": i, "horizon_years": h, "expected_npv_within_horizon": (k + 1) * h * 1.0} for k, i in enumerate(ids) for h in (1, 5)])
    capex = pd.Series(10.0, index=ids)
    books = hz.horizon_books(view, capex, np.array(["a", "a", "a", "b", "b", "b"]), budget=30.0, group_cap=0.7, horizons=(1, 5))
    for x in books.values():
        assert capex @ x <= 30.0 + 1e-9 and x.sum() == 3
