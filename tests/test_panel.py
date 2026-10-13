"""The v5 panel: one row per key and month, the audits count what they should, the release lags are one set of numbers everywhere."""

import numpy as np
import pandas as pd
import pytest

from src import config, energy_data, energy_features, paths


def _panel():
    months = pd.date_range("2018-01-01", "2018-06-01", freq="MS")
    lease = pd.DataFrame({"lease_number": ["L1"] * 6 + ["L2"] * 6, "month": list(months) * 2,
                          "oil_bbl": [100, 0, 90, 80, 70, 60] + [10] * 6, "gas_mcf": [50, 0, 40, 30, 20, 10] + [5] * 6, "water_bbl": 0.0})
    lease["producing"] = (lease["oil_bbl"] + lease["gas_mcf"]) > 0
    generation = pd.DataFrame({"plant_code": [1] * 6 + [2] * 6, "prime_mover": ["WT"] * 6 + ["BA"] * 6, "month": list(months) * 2,
                               "generation_mwh": [500] * 6 + [-20] * 6})
    market = pd.DataFrame({"month": months, "wti_usd_bbl": np.linspace(60, 70, 6), "hh_usd_mmbtu": [np.nan] + [3.0] * 5})
    return lease, generation, market


def test_audits_count_duplicates_zero_months_negative_generation_and_missing_price_months():
    lease, generation, market = _panel()
    audits = energy_data.panel_audits(lease, generation, market, window=("2018-01", "2018-06")).set_index("item")
    assert audits.loc["duplicate (lease, month) keys", "rows"] == 0
    assert audits.loc["lease-months with zero oil and gas", "rows"] == 1
    assert audits.loc["plant-months with negative net generation", "rows"] == 6
    missing = audits[audits.index.str.startswith("hh_usd_mmbtu")]["rows"].iloc[0]
    assert missing == 1  # the one priced month that is missing inside the window
    dup = energy_data.panel_audits(pd.concat([lease, lease.iloc[:1]]), generation, market, window=("2018-01", "2018-06")).set_index("item")
    assert dup.loc["duplicate (lease, month) keys", "rows"] == 1


def test_release_lags_are_one_set_of_numbers():
    assert energy_features.LAG_LEASE == config.RELEASE_LAGS["BSEE OGOR-A"] >= 0
    assert energy_features.LAG_PLANT == config.RELEASE_LAGS["EIA-923 monthly"] >= 0
    assert energy_features.LAG_MARKET == config.RELEASE_LAGS["WTI, Henry Hub"] == 0
    table = paths.DATA_PROCESSED / "release_lags.csv"
    if table.exists():
        lags = pd.read_csv(table)
        col = next(c for c in lags.columns if "lag" in c.lower())
        src = next(c for c in lags.columns if c != col)
        for source, lag in config.RELEASE_LAGS.items():
            row = lags[lags[src] == source]
            if len(row):
                assert int(row[col].iloc[0]) == lag


@pytest.mark.skipif(not (paths.DATA_INTERIM / "upstream_monthly.parquet").exists(), reason="interim panel not on this machine")
def test_the_built_panel_has_one_row_per_key_and_month():
    lease = pd.read_parquet(paths.DATA_INTERIM / "upstream_monthly.parquet", columns=["lease_number", "month"])
    assert not lease.duplicated(["lease_number", "month"]).any()
    generation = pd.read_parquet(paths.DATA_INTERIM / "generation_monthly.parquet", columns=["plant_code", "prime_mover", "month"])
    assert not generation.duplicated(["plant_code", "prime_mover", "month"]).any()
    market = pd.read_parquet(paths.DATA_INTERIM / "market_monthly.parquet", columns=["month"])
    assert market["month"].is_unique
