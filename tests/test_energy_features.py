"""The leakage proof: features at an origin never change when rows after origin − lag are removed, and never use a later month."""

import numpy as np
import pandas as pd

from src import energy_features as ef


def _lease_panel(n_leases=4, months=60, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for k in range(n_leases):
        q0 = 1000 * (k + 1)
        for i, month in enumerate(pd.date_range("2019-01-01", periods=months, freq="MS")):
            oil = q0 * np.exp(-0.02 * i) * rng.uniform(0.8, 1.2)
            rows.append({"lease_number": f"L{k}", "month": month, "oil_bbl": oil, "gas_mcf": oil * 2, "water_bbl": oil * 0.5,
                         "injection_bbl": 0.0, "days_on_prod": 30, "n_completions": 2, "n_producing": 2, "producing": True})
    return pd.DataFrame(rows)


def test_lease_features_never_use_months_after_origin_minus_lag():
    panel = _lease_panel()
    origin = pd.Timestamp("2022-06-01")
    table = ef.lease_features(panel, origins=pd.DatetimeIndex([origin]), horizons=(3,))
    assert (table["last_month_used"] == origin - pd.DateOffset(months=ef.LAG_LEASE)).all()
    # the latest observable month's volume is the lag-1 feature, not the origin month's
    expected = panel[(panel["lease_number"] == "L0") & (panel["month"] == table["last_month_used"].iloc[0])]["oil_bbl"].iloc[0]
    assert np.isclose(table.loc[table["lease_number"] == "L0", "oil_lag1"].iloc[0], expected)
    # the target is the month h after the origin
    y = panel[(panel["lease_number"] == "L0") & (panel["month"] == origin + pd.DateOffset(months=3))]["oil_bbl"].iloc[0]
    assert np.isclose(table.loc[table["lease_number"] == "L0", "y_oil"].iloc[0], y)


def test_truncation_leaves_lease_features_unchanged():
    panel = _lease_panel()
    assert ef.truncation_check(ef.lease_features, panel, "2022-06-01", ef.LAG_LEASE, horizons=(3, 12))


def test_truncation_leaves_market_features_unchanged():
    months = pd.date_range("2015-01-01", periods=120, freq="MS")
    rng = np.random.default_rng(3)
    prices = pd.DataFrame({"month": months, "wti_usd_bbl": 50 * np.exp(np.cumsum(rng.normal(0, 0.05, 120))),
                           "hh_usd_mmbtu": 3 * np.exp(np.cumsum(rng.normal(0, 0.08, 120)))})
    assert ef.truncation_check(ef.market_features, prices, "2022-06-01", ef.LAG_MARKET, series=("wti_usd_bbl", "hh_usd_mmbtu"))
    table = ef.market_features(prices, origins=pd.DatetimeIndex([pd.Timestamp("2022-06-01")]), series=("wti_usd_bbl",))
    assert np.isclose(table["log_p0"].iloc[0], np.log(prices.set_index("month").loc["2022-06-01", "wti_usd_bbl"]))


def test_split_protocol_boundaries():
    assert ef.split_of("2018-01-01") == "development" and ef.split_of("2022-12-01") == "development"
    assert ef.split_of("2023-01-01") == "validation" and ef.split_of("2023-06-01") == "validation"
    assert ef.split_of("2023-07-01") == "holdout" and ef.split_of("2024-12-01") == "holdout"
    assert ef.split_of("2017-12-01") == "outside"


def test_targets_after_the_panel_end_are_missing_not_imputed():
    panel = _lease_panel(months=72)  # ends 2024-12
    table = ef.lease_features(panel, origins=pd.DatetimeIndex([pd.Timestamp("2024-10-01")]), horizons=(3, 6))
    assert table.loc[table["horizon"] == 3, "y_oil"].isna().all()  # target 2025-01 is after the panel
    assert table.loc[table["horizon"] == 6, "y_oil"].isna().all()
