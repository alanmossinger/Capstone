"""The value arithmetic of src/value.py, on small hand-checked cases."""

import numpy as np

from src import value


def test_expected_value_sums_the_years_a_plant_would_run():
    # operates in year 1 with probability 0.5 and never otherwise; worth 10 per MW-year for 3 years; 2 MW; 1 sunk
    out = value.expected_value([0.5, 0.5, 0.5], mw=2.0, values_by_year=[10, 10, 10], sunk_cost=1.0)
    assert np.isclose(out, 0.5 * 30 * 2 - 1)
    # operates in year 3 only: earns the third year's value only
    out = value.expected_value([0.0, 0.0, 1.0], mw=1.0, values_by_year=[10, 20, 30], sunk_cost=0.0)
    assert np.isclose(out, 30)


def test_value_per_mw_year_adds_three_terms_and_scales_by_case():
    inputs = {"energy_price": {"PJM": {2020: 40.0}}, "capacity_factor": {"Solar": 0.25}, "capture": {"Solar": 0.8},
              "capacity_price": {"PJM": {2020: 50.0}}, "accreditation": {"Solar": 0.1}, "credit": {"Solar": 20.0},
              "multiplier": {"base": {"energy": 1, "capacity": 1, "credit": 1}, "low": {"energy": 0.5, "capacity": 0, "credit": 0}}}
    base = value.value_per_mw_year("PJM", "Solar", 2020, inputs, "base")
    energy = 0.25 * 8760 * 40 * 0.8
    capacity = 0.1 * 1000 * 50
    credit = 0.25 * 8760 * 20
    assert np.isclose(base, energy + capacity + credit)
    assert np.isclose(value.value_per_mw_year("PJM", "Solar", 2020, inputs, "low"), 0.5 * energy)
