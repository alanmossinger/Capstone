"""The economics engine: NPV identities, the incremental cash flow, the battery LP and the capture factors behave on known inputs."""

import numpy as np
import pandas as pd

from src import economics as ec


def test_npv_monthly_discounts_from_month_zero():
    assert ec.npv_monthly([100.0], 0.1) == 100.0
    twelve = ec.npv_monthly([0.0] * 12 + [110.0], 0.1)
    assert abs(twelve - 100.0) < 1e-9


def test_incremental_cash_flow_is_uplift_minus_cost_and_decays_with_the_baseline():
    months = 120
    base_oil = 10000 * np.exp(-0.02 * np.arange(1, months + 1))
    base_gas = np.zeros(months)
    wti, hh = np.full(months, 70.0), np.full(months, 3.0)
    with_ = ec.lease_cash_flows(base_oil, base_gas, wti, hh, n_wells=2, case="base")
    without = ec.lease_cash_flows(base_oil, base_gas, wti, hh, n_wells=2, case="base", redevelop=False)
    g = ec.grid_case("base")
    assert with_["capex"].iloc[0] == 2 * g["workover_cost_per_well_usd"] and without["capex"].sum() == 0
    lead = int(g["lead_time_months"])
    assert np.allclose(with_["oil_bbl"].iloc[:lead], without["oil_bbl"].iloc[:lead])
    assert np.allclose(with_["oil_bbl"].iloc[lead:], without["oil_bbl"].iloc[lead:] * (1 + g["uplift_share"]), rtol=1e-9)
    # revenue net of royalty, opex and the workover is what the NPV discounts
    expected_month = with_["oil_bbl"].iloc[lead] * (70 - g["oil_differential_usd_per_bbl"]) * (1 - g["royalty_share"]) - with_["oil_bbl"].iloc[lead] * g["opex_usd_per_boe"]
    assert abs(with_["cash_flow"].iloc[lead] - expected_month) < 1e-6


def test_economic_limit_shuts_in_and_abandons_once():
    months = 60
    base_oil = 2000 * np.exp(-0.1 * np.arange(1, months + 1))  # falls under 300 boe within the window
    flows = ec.lease_cash_flows(base_oil, np.zeros(months), np.full(months, 70.0), np.full(months, 3.0), n_wells=1, redevelop=False)
    assert flows["shut_in"].any() and (flows["abandonment"] > 0).sum() == 1
    assert flows.loc[flows["shut_in"], "oil_bbl"].sum() == 0


def test_breakeven_price_zeroes_the_incremental_npv():
    months = 240
    base_oil = 20000 * np.exp(-0.01 * np.arange(1, months + 1))
    hh = np.full(months, 3.0)
    be = ec.breakeven_wti(base_oil, np.zeros(months), hh, n_wells=3, case="base")
    assert 10 < be < 200
    assert abs(ec.incremental_npv(base_oil, np.zeros(months), np.full(months, be), hh, n_wells=3)) < 0.01 * ec.grid_case("base")["workover_cost_per_well_usd"]


def test_battery_lp_buys_low_and_sells_high_within_its_duration():
    prices = np.array([10.0] * 12 + [100.0] * 12)  # cheap morning, dear evening
    revenue = ec.battery_day(prices, hours=4, efficiency=1.0, cycles=1.0)
    assert abs(revenue - 4 * (100 - 10)) < 1e-6  # four MWh bought at 10, sold at 100
    lossy = ec.battery_day(prices, hours=4, efficiency=0.85, cycles=1.0)
    assert lossy < revenue


def test_capture_factors_weight_price_by_shape():
    index = pd.date_range("2024-01-01", periods=48, freq="h")
    price = pd.Series(np.tile(np.r_[np.full(12, 20.0), np.full(12, 60.0)], 2), index=index)
    solar = pd.Series(np.tile(np.r_[np.zeros(12), np.ones(12)], 2), index=index)  # produces only in the dear hours
    wind = pd.Series(np.ones(48), index=index)  # flat
    out = ec.capture_factors(price, solar, wind, gas_marginal_cost=30.0)
    assert abs(out["solar"] - 60.0 / 40.0) < 1e-9 and abs(out["wind"] - 1.0) < 1e-9
    assert abs(out["gas"] - 1.5) < 1e-9 and abs(out["gas_hours_share"] - 0.5) < 1e-9
