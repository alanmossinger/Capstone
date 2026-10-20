"""The valuation engine agrees with the part A DCF, applies the credits of the law in force on the decision date (and the 2025-law stress) by operation year, and values a scenario like the flat path when prices are flat."""

import numpy as np
import pandas as pd

from src import valuation as va, value

ATB = pd.DataFrame({"capex_per_kw": [1200.0, 1500.0, 1000.0, 1300.0], "fom_per_kw_year": [20.0, 30.0, 25.0, 35.0], "vom_per_mwh": [2.0, 0.0, 0.0, 0.0],
                    "heat_rate_mmbtu_per_mwh": [6.5, 0.0, 0.0, 0.0], "wacc_real": [0.054, 0.045, 0.042, 0.05], "new_build_cf": [0.5, 0.35, 0.25, 0.0]},
                   index=["Gas", "Wind", "Solar", "Battery"])
BASIS = {"capture": {"gas": 1.3, "solar": 0.9, "wind": 0.8, "gas_hours_share": 0.6}, "battery_revenue": 70_000.0, "gas_mc": 20.0}


def test_merchant_npv_matches_the_part_a_dcf_without_credits():
    comp = va.pv_components("Gas", ATB, BASIS, ercot_base=30.0, hh_base=2.5)
    mwh = 0.6 * 8760
    revenue = np.full(20, 30.0 * 1.3 * mwh)
    expected = value.npv_per_mw(revenue, 1200.0, 20.0, 2.0 + 6.5 * 2.5, mwh, rate=0.054, life=20)
    assert abs(va.npv_if_built(comp, "merchant") - expected) < 1e-6


def test_the_law_in_force_on_the_decision_date_keeps_every_credit_in_the_window():
    assert all(va.credit_eligible(t, y) for t in ("Wind", "Solar", "Battery") for y in range(2025, 2032))
    assert not va.credit_eligible("Gas", 2025)
    comp = va.pv_components("Solar", ATB, BASIS, 30.0, 2.5)
    assert abs(va.npv_if_built(comp, "merchant", operation_year=1) - va.npv_if_built(comp, "merchant", operation_year=5)) < 1e-6


def test_the_2025_law_stress_ends_wind_and_solar_credits_after_2027_and_storage_keeps_it():
    assert va.credit_eligible("Wind", 2027, "2025 law") and not va.credit_eligible("Wind", 2028, "2025 law")
    assert va.credit_eligible("Solar", 2025, "2025 law") and not va.credit_eligible("Solar", 2030, "2025 law")
    assert va.credit_eligible("Battery", 2031, "2025 law")
    comp = va.pv_components("Solar", ATB, BASIS, 30.0, 2.5)
    early = va.npv_if_built(comp, "merchant", operation_year=1, credits="2025 law")
    late = va.npv_if_built(comp, "merchant", operation_year=5, credits="2025 law")
    assert abs((early - late) - 0.30 * 1000.0 * 1000) < 1e-6  # the 30% investment credit on $1,000/kW
    assert va.npv_if_built(comp, "merchant", operation_year=5, credits=False) == late


def test_an_unknown_credit_policy_is_refused():
    import pytest
    with pytest.raises(ValueError):
        va.credit_policy_of("repealed")


def test_expected_npv_when_operation_is_certain_in_year_one():
    comp = va.pv_components("Wind", ATB, BASIS, 30.0, 2.5)
    out = va.expected_power_npv([1.0] * 7, comp, mw=100.0, carry=1e6, case="contracted")
    assert abs(out["expected_npv"] - (va.npv_if_built(comp, "contracted", 1) * 100.0 / 1.045 - 1e6)) < 1e-3


def test_flat_scenario_equals_the_flat_path():
    comp = {"Wind": va.pv_components("Wind", ATB, BASIS, 30.0, 2.5)}
    power = pd.DataFrame({"technology": ["Wind"], "mw": [100.0], "carry_cost": [1e6]})
    base = np.array([70.0, 2.5, 30.0])
    prices = np.broadcast_to(base, (3, 240, 3)).copy()
    m = va.power_npv_matrix(power, comp, prices, np.ones((3, 1)), np.array([[1], [3], [0]]), base, 240, "merchant")
    assert abs(m[0, 0] - (va.npv_if_built(comp["Wind"], "merchant", 1) * 100.0 / 1.045 - 1e6)) < 1e-3
    assert abs(m[1, 0] - (va.npv_if_built(comp["Wind"], "merchant", 3) * 100.0 / 1.045 ** 3 - 1e6)) < 1e-3
    assert m[2, 0] == -1e6  # never operates: the carry only


def test_stage_one_charge_is_lease_capital_or_carry_plus_reserve():
    charge = va.stage_one_charge(["offshore oil and gas", "ERCOT power"], [5e8, 1e9], [0.0, 2e6], [1.0, 0.2])
    assert charge.tolist() == [5e8, 2e6 + 2e8]
