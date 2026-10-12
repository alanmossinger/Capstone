"""The ATB reader and the project NPV behave as documented."""

import numpy as np

from src import value


def test_npv_is_minus_capex_when_nothing_is_earned():
    assert np.isclose(value.npv_per_mw([0.0] * 20, 1000.0, 0.0, 0.0, 0.0), -1_000_000.0)


def test_npv_discounts_a_constant_margin_as_an_annuity():
    # 100,000 $/MW-year net for 20 years at 8%: annuity factor 9.818
    npv = value.npv_per_mw([100_000.0] * 20, 0.0, 0.0, 0.0, 0.0, rate=0.08)
    assert np.isclose(npv, 100_000 * (1 - 1.08 ** -20) / 0.08)


def test_npv_subtracts_fixed_and_variable_costs():
    base = value.npv_per_mw([100_000.0] * 20, 0.0, 0.0, 0.0, 0.0)
    with_costs = value.npv_per_mw([100_000.0] * 20, 0.0, 10.0, 2.0, 4000.0)  # 10 $/kW-yr = 10,000 $/MW-yr; 2 $/MWh × 4,000 MWh
    annuity = (1 - 1.08 ** -20) / 0.08
    assert np.isclose(base - with_costs, (10_000 + 8_000) * annuity)


def test_atb_costs_cover_every_technology_group():
    if not value.RAW_ATB.exists():
        return  # the raw file is not committed; notebook 07 checks it on disk
    costs = value.atb_costs()
    assert set(costs.index) == set(value.ATB_MAP) | {"Other"}
    assert (costs["capex_per_kw"] > 500).all() and (costs["capex_per_kw"] < 10_000).all()
    assert costs.loc["Gas", "heat_rate_mmbtu_per_mwh"] > 5 and costs.loc["Solar", "heat_rate_mmbtu_per_mwh"] == 0


def test_atb_capacity_factors_are_design_values_for_the_variable_technologies():
    if not value.RAW_ATB.exists():
        return
    cf = value.atb_capacity_factors()
    assert set(cf) == {"Solar", "Solar+Battery", "Wind", "Offshore Wind"}
    assert 0.2 < cf["Solar"] < 0.35 and 0.35 < cf["Wind"] < 0.55


def test_atb_wacc_is_a_small_real_rate_for_every_group():
    if not value.RAW_ATB.exists():
        return
    w = value.atb_wacc()
    assert set(w) == set(value.ATB_MAP) | {"Other"}
    assert all(0.03 < v < 0.08 for v in w.values())

