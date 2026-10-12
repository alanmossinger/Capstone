"""Leakage-safe forecasting features for leases, plants and prices, at rolling origins.

What: for every forecast origin (the last day of a month) builds one row per
lease, plant or market series using only the months a forecaster could
have seen at that origin — the observation months minus each source's
release lag (``config.RELEASE_LAGS``, ``data/processed/release_lags.csv``)
— and attaches the target ``h`` months after the origin. Also the split
protocol (development, validation, holdout origins) and the truncation
check that proves no feature changes when post-origin rows are removed.
Why: the proposal's non-negotiable rule — lag every feature relative to
the origin, fit scalers inside each training fold — and criterion C20,
which is scored at matched origins (PLAN.md §14.5–14.6).
Reads: the interim panel tables of notebook 01 (parts D–E).
Writes: nothing; notebook 03 writes the feature tables.
Used by: notebooks 03 and 05; ``tests/test_energy_features.py``.

Every builder takes the panel and a list of origins and returns a long
table with ``origin``, ``horizon``, ``split``, the features and the target.
The latest month a builder may use is ``origin − lag`` months; the builders
assert it.
"""

import warnings

import numpy as np
import pandas as pd

from src import config

HORIZONS_LEASE = (3, 6, 12)  # months ahead for lease oil and gas output
HORIZONS_PLANT = (1, 3)  # months ahead for plant capacity factor
HORIZONS_MARKET = (1, 3)  # months ahead for log prices
ORIGINS = pd.date_range("2018-01-01", "2024-12-01", freq="MS")  # origin = the end of that month
SPLIT = {  # registered with C20 (decision #66): targets of every horizon must exist by 2024-12
    "development": ("2018-01", "2022-12"),
    "validation": ("2023-01", "2023-06"),
    "holdout": ("2023-07", "2024-12"),
}
LAST_OBSERVED = pd.Timestamp("2024-12-01")  # the panel ends here; a target after it is missing, never imputed
LAG_LEASE = config.RELEASE_LAGS["BSEE OGOR-A"]
LAG_PLANT = config.RELEASE_LAGS["EIA-923 monthly"]
LAG_MARKET = config.RELEASE_LAGS["WTI, Henry Hub"]


def split_of(origin):
    """Name of the split an origin belongs to (``development``, ``validation``, ``holdout``)."""
    period = pd.Timestamp(origin).strftime("%Y-%m")
    for name, (start, end) in SPLIT.items():
        if start <= period <= end:
            return name
    return "outside"


MIN_HISTORY = 12  # observable months a lease or plant needs before it gets a feature row


def _wide(frame, key, value, zero_after_first=False):
    """Pivot a long monthly table to keys × months.

    Notes
    -----
    Missing months are NaN, except with ``zero_after_first``: a month after
    the key's first appearance in the file with no row is zero production
    (a lease that stops reporting has stopped producing; BSEE files carry no
    row for it), while months before the first appearance stay NaN.
    """
    wide = frame.pivot(index=key, columns="month", values=value)
    months = pd.date_range(frame["month"].min(), frame["month"].max(), freq="MS")
    wide = wide.reindex(columns=months)
    if zero_after_first:
        first = frame.groupby(key)["month"].min().reindex(wide.index)
        after_first = np.array(months)[None, :] >= first.to_numpy()[:, None]
        wide = wide.where(~(after_first & wide.isna()), 0.0)
    return wide


def _slope(window):
    """OLS slope of log(1 + value) over the columns of a keys × months window, NaN-aware."""
    y = np.log1p(window.to_numpy(float))
    t = np.arange(y.shape[1], dtype=float)
    ok = np.isfinite(y)
    n = ok.sum(axis=1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # a key with no observable month gives NaN, which the caller drops
        t_mean = np.nanmean(np.where(ok, t, np.nan), axis=1, keepdims=True)
        y_mean = np.nanmean(y, axis=1, keepdims=True)
    cov = np.nansum(np.where(ok, (t - t_mean) * (y - y_mean), 0.0), axis=1)
    var = np.nansum(np.where(ok, (t - t_mean) ** 2, 0.0), axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        slope = np.where((n >= 3) & (var > 0), cov / var, np.nan)
    return slope


def lease_features(lease, origins=ORIGINS, horizons=HORIZONS_LEASE, lag=LAG_LEASE, eligible=None):
    """One row per (lease, origin, horizon) with lagged production features and the oil and gas targets.

    Parameters
    ----------
    lease : pandas.DataFrame
        ``upstream_monthly`` (notebook 01 part D).
    origins : DatetimeIndex
        Origin months (the forecast is made at the end of each).
    horizons : tuple of int
    lag : int
        Release lag in months: the latest usable month is ``origin − lag``.
    eligible : iterable, optional
        Lease numbers to keep (the candidate pool).

    Returns
    -------
    pandas.DataFrame
        ``lease_number``, ``origin``, ``last_month_used``, ``horizon``,
        ``split``, features ``oil_lag1`` … ``gas_lag12``, ``oil_mean3``,
        ``gas_mean3``, ``oil_slope12``, ``gas_slope12``, ``water_ratio3``,
        ``producing_months``, ``months_since_first``, ``oil_share12``,
        ``n_completions``, ``days_on_prod``, ``seasonal_oil``, ``seasonal_gas``
        (the value twelve months before the target when observable), and
        targets ``y_oil``, ``y_gas`` (NaN after the panel's end).

    Notes
    -----
    ``oil_lag1`` is the latest *observable* month (``origin − lag``), not the
    origin month; ``oil_lag3`` is two months before it, and so on, so a
    forecaster at the origin would have had every column. The slope is the
    OLS slope of log(1 + volume) over the twelve observable months ending at
    the latest one: the lease's own decline rate.
    """
    frame = lease if eligible is None else lease[lease["lease_number"].isin(eligible)]
    oil, gas, water = (_wide(frame, "lease_number", c, zero_after_first=True) for c in ["oil_bbl", "gas_mcf", "water_bbl"])
    comp, days = _wide(frame, "lease_number", "n_completions"), _wide(frame, "lease_number", "days_on_prod")
    first = frame.groupby("lease_number")["month"].min()
    months = oil.columns
    rows = []
    for origin in origins:
        last = origin - pd.DateOffset(months=lag)
        if last not in months:
            continue
        i = months.get_loc(last)
        assert months[i] <= origin - pd.DateOffset(months=lag), "feature month after origin − lag"
        hist_o, hist_g = oil.iloc[:, : i + 1], gas.iloc[:, : i + 1]
        win_o, win_g, win_w = hist_o.iloc[:, -12:], hist_g.iloc[:, -12:], water.iloc[:, : i + 1].iloc[:, -3:]
        producing = ((hist_o.fillna(0) > 0) | (hist_g.fillna(0) > 0)).sum(axis=1)
        base = pd.DataFrame({
            "lease_number": oil.index, "origin": origin, "last_month_used": last,
            "oil_lag1": hist_o.iloc[:, -1].to_numpy(), "oil_lag3": hist_o.iloc[:, -3].to_numpy() if i >= 2 else np.nan,
            "oil_lag6": hist_o.iloc[:, -6].to_numpy() if i >= 5 else np.nan, "oil_lag12": hist_o.iloc[:, -12].to_numpy() if i >= 11 else np.nan,
            "gas_lag1": hist_g.iloc[:, -1].to_numpy(), "gas_lag3": hist_g.iloc[:, -3].to_numpy() if i >= 2 else np.nan,
            "gas_lag6": hist_g.iloc[:, -6].to_numpy() if i >= 5 else np.nan, "gas_lag12": hist_g.iloc[:, -12].to_numpy() if i >= 11 else np.nan,
            "oil_mean3": hist_o.iloc[:, -3:].mean(axis=1).to_numpy(), "gas_mean3": hist_g.iloc[:, -3:].mean(axis=1).to_numpy(),
            "oil_slope12": _slope(win_o), "gas_slope12": _slope(win_g),
            "water_ratio3": (win_w.sum(axis=1) / (win_w.sum(axis=1) + hist_o.iloc[:, -3:].sum(axis=1)).replace(0, np.nan)).to_numpy(),
            "producing_months": producing.to_numpy(), "months_since_first": ((last - first.reindex(oil.index)).dt.days / 30.44).to_numpy(),
            "oil_share12": (win_o.sum(axis=1) / (win_o.sum(axis=1) + win_g.sum(axis=1) / 6.0).replace(0, np.nan)).to_numpy(),  # 6 Mcf ≈ 1 boe
            "n_completions": comp.iloc[:, i].to_numpy(), "days_on_prod": days.iloc[:, i].to_numpy(),
        })
        keep = (hist_o.notna().sum(axis=1).to_numpy() >= MIN_HISTORY) & (base["months_since_first"].to_numpy() >= 0)  # no history, no row
        for h in horizons:
            target = origin + pd.DateOffset(months=h)
            seasonal = target - pd.DateOffset(months=12)
            part = base.copy()
            part["horizon"] = h
            part["target_month"] = target
            part["y_oil"] = oil[target].to_numpy() if target in months else np.nan
            part["y_gas"] = gas[target].to_numpy() if target in months else np.nan
            observable = seasonal in months and seasonal <= last
            part["seasonal_oil"] = oil[seasonal].to_numpy() if observable else part["oil_lag1"]
            part["seasonal_gas"] = gas[seasonal].to_numpy() if observable else part["gas_lag1"]
            rows.append(part[keep])
    out = pd.concat(rows, ignore_index=True)
    out["split"] = out["origin"].map(split_of)
    out.loc[out["target_month"] > LAST_OBSERVED, ["y_oil", "y_gas"]] = np.nan
    return out


def plant_features(generation, nameplate, hh, origins=ORIGINS, horizons=HORIZONS_PLANT, lag=LAG_PLANT,
                   technologies=("Gas CC", "Solar", "Wind")):
    """One row per (plant, prime mover, origin, horizon) with lagged capacity-factor features and the target.

    Parameters
    ----------
    generation : pandas.DataFrame
        ``generation_monthly`` (notebook 01 part D).
    nameplate : pandas.DataFrame
        ``plant_code``, ``technology``, ``nameplate_mw`` (from the EIA-860M generators).
    hh : pandas.DataFrame
        ``month``, ``hh_usd_mmbtu`` (for the fuel-cost feature of gas plants).

    Returns
    -------
    pandas.DataFrame
        ``plant_code``, ``prime_mover``, ``technology``, ``origin``,
        ``last_month_used``, ``horizon``, ``split``, ``cf_lag1``, ``cf_lag3``,
        ``cf_lag12``, ``cf_mean12``, ``cf_seasonal`` (same month as the
        target a year earlier when observable), ``zero_months12``,
        ``heat_rate3`` (MMBtu per MWh, gas only), ``fuel_cost3`` (heat rate ×
        Henry Hub at the origin), ``target_month_of_year``, ``nameplate_mw``,
        ``y_cf``.

    Notes
    -----
    Capacity factor is net generation over nameplate × hours in the month;
    plants without a nameplate are dropped. Values above 1.2 (a nameplate
    that is out of date) are set to missing rather than clipped. A heat rate
    is computed only in months the plant ran at 5% or more and kept only
    within 4–20 MMBtu/MWh. A plant gets a row once it has ``MIN_HISTORY``
    observable months, so a plant that first reports after the origin has
    no row — which is also what the truncation check requires.
    """
    frame = generation[generation["technology"].isin(technologies)].merge(nameplate, on=["plant_code", "technology"], how="inner")
    frame = frame[frame["nameplate_mw"] > 0].copy()
    frame["key"] = frame["plant_code"].astype(str) + "|" + frame["prime_mover"]
    hours = frame["month"].dt.days_in_month * 24
    frame["cf"] = frame["generation_mwh"] / (frame["nameplate_mw"] * hours)
    frame.loc[frame["cf"] > 1.2, "cf"] = np.nan
    ran = (frame["technology"] == "Gas CC") & (frame["cf"] >= 0.05)  # a heat rate means nothing when the plant barely ran
    frame["heat_rate"] = np.where(ran, frame["consumption_for_eg_mmbtu"] / frame["generation_mwh"].replace(0, np.nan), np.nan)
    frame.loc[(frame["heat_rate"] < 4) | (frame["heat_rate"] > 20), "heat_rate"] = np.nan  # outside any combined cycle's range
    cf, hr = _wide(frame, "key", "cf"), _wide(frame, "key", "heat_rate")
    meta = frame.groupby("key").agg(plant_code=("plant_code", "first"), prime_mover=("prime_mover", "first"),
                                    technology=("technology", "first"), nameplate_mw=("nameplate_mw", "first"))
    hh_index = hh.set_index("month")["hh_usd_mmbtu"]
    months = cf.columns
    rows = []
    for origin in origins:
        last = origin - pd.DateOffset(months=lag)
        if last not in months:
            continue
        i = months.get_loc(last)
        hist = cf.iloc[:, : i + 1]
        win = hist.iloc[:, -12:]
        hr3 = hr.iloc[:, : i + 1].iloc[:, -3:].mean(axis=1)
        base = pd.DataFrame({
            "key": cf.index, "origin": origin, "last_month_used": last,
            "cf_lag1": hist.iloc[:, -1].to_numpy(), "cf_lag3": hist.iloc[:, -3].to_numpy() if i >= 2 else np.nan,
            "cf_lag12": hist.iloc[:, -12].to_numpy() if i >= 11 else np.nan, "cf_mean12": win.mean(axis=1).to_numpy(),
            "zero_months12": (win.fillna(0) <= 0).sum(axis=1).to_numpy(), "heat_rate3": hr3.to_numpy(),
            "fuel_cost3": (hr3 * hh_index.get(origin, np.nan)).to_numpy(),
        }).join(meta, on="key")
        keep = hist.notna().sum(axis=1).to_numpy() >= MIN_HISTORY  # no history, no row
        for h in horizons:
            target = origin + pd.DateOffset(months=h)
            seasonal = target - pd.DateOffset(months=12)
            part = base.copy()
            part["horizon"] = h
            part["target_month"] = target
            part["target_month_of_year"] = target.month
            part["y_cf"] = cf[target].to_numpy() if target in months else np.nan
            part["cf_seasonal"] = cf[seasonal].to_numpy() if (seasonal in months and seasonal <= last) else part["cf_lag1"]
            rows.append(part[keep])
    out = pd.concat(rows, ignore_index=True).drop(columns="key")
    out["split"] = out["origin"].map(split_of)
    out.loc[out["target_month"] > LAST_OBSERVED, "y_cf"] = np.nan
    return out


def market_features(prices, origins=ORIGINS, horizons=HORIZONS_MARKET, lag=LAG_MARKET, series=("wti_usd_bbl", "hh_usd_mmbtu", "ercot_usd_mwh")):
    """One row per (series, origin, horizon) with lagged log-price features and the log-price target.

    Parameters
    ----------
    prices : pandas.DataFrame
        ``month`` and the price columns in ``series`` (the long monthly
        histories; ERCOT may carry an ``ercot_provenance`` column).

    Returns
    -------
    pandas.DataFrame
        ``series``, ``origin``, ``horizon``, ``split``, ``log_p0``,
        ``log_p1`` … ``log_p12`` (lags in months), ``ret1``, ``ret3``,
        ``ret12``, ``vol3``, ``vol12`` (standard deviation of monthly log
        changes), ``y_log`` (log price at the target), ``y_provenance``
        (OBSERVED unless the ERCOT month is derived or assumed).

    Notes
    -----
    Prices are known in their own month (lag 0), so the latest value is the
    origin's. The target is a log level, the baseline of notebook 05 is the
    random walk (``log_p0``), so a model's error is a log return error.
    """
    table = prices.set_index("month").sort_index()
    rows = []
    for name in series:
        p = table[name].astype(float)
        logp = np.log(p)
        change = logp.diff()
        prov = table["ercot_provenance"] if (name.startswith("ercot") and "ercot_provenance" in table) else pd.Series("OBSERVED", index=table.index)
        for origin in origins:
            last = origin - pd.DateOffset(months=lag)
            if last not in logp.index or pd.isna(logp.get(last)):
                continue
            i = logp.index.get_loc(last)
            lagged = {f"log_p{k}": (logp.iloc[i - k] if i - k >= 0 else np.nan) for k in (0, 1, 2, 3, 6, 12)}
            feats = {"series": name, "origin": origin, "last_month_used": last, **lagged,
                     "ret1": lagged["log_p0"] - lagged["log_p1"], "ret3": lagged["log_p0"] - lagged["log_p3"],
                     "ret12": lagged["log_p0"] - lagged["log_p12"],
                     "vol3": change.iloc[max(0, i - 2): i + 1].std(), "vol12": change.iloc[max(0, i - 11): i + 1].std()}
            for h in horizons:
                target = origin + pd.DateOffset(months=h)
                y = logp.get(target, np.nan) if target <= LAST_OBSERVED else np.nan
                rows.append({**feats, "horizon": h, "target_month": target, "y_log": y,
                             "y_provenance": prov.get(target, "OBSERVED") if target in prov.index else "OBSERVED"})
    out = pd.DataFrame(rows)
    out["split"] = out["origin"].map(split_of)
    return out


def truncation_check(builder, panel, origin, lag, **kwargs):
    """True when features at ``origin`` are identical whether or not rows after ``origin − lag`` exist.

    Notes
    -----
    The leakage proof: the builder is run on the full panel and on the panel
    with every row after the latest usable month deleted; the feature
    columns (everything but the targets) must match exactly. Used by
    notebook 03 and ``tests/test_energy_features.py``.
    """
    cutoff = pd.Timestamp(origin) - pd.DateOffset(months=lag)
    full = builder(panel, origins=pd.DatetimeIndex([origin]), **kwargs)
    truncated = builder(panel[panel["month"] <= cutoff], origins=pd.DatetimeIndex([origin]), **kwargs)
    targets = [c for c in full.columns if c.startswith("y_") or c in ("target_month", "cf_seasonal", "seasonal_oil", "seasonal_gas")]
    a, b = full.drop(columns=targets), truncated.drop(columns=targets)
    return a.shape == b.shape and a.fillna(-1).reset_index(drop=True).equals(b.fillna(-1).reset_index(drop=True))
