"""Rolling-origin forecasts for leases, plants and prices: baselines, challengers, paired scoring.

What: the baselines of criterion C20 (last value, seasonal naive, Arps
decline, technology-month median, random walk), the two challengers
(ElasticNet, LightGBM) with a quantile LightGBM for intervals, the
expanding-window refit schedule, and the paired moving-block bootstrap that
scores a challenger against the best baseline at matched origins.
Why: H1 of the proposal — does machine learning reduce held-out error
against transparent baselines — scored exactly as registered in
`results/success_criteria_v6_registered.json` (decision #66).
Reads: the feature tables of notebook 03 (`data/interim/features_*.parquet`).
Writes: nothing; notebook 05 writes the tables.
Used by: notebook 05; `tests/test_energy_models.py`.

Every fit uses rows whose target month is on or before the refit origin, so
a prediction never sees its own future; imputers and scalers are fitted
inside the same rows.
"""

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb

from src import decline

REFIT_EVERY = 3  # origins between refits (quarterly), as registered
LGBM_PARAMS = {"n_estimators": 300, "learning_rate": 0.05, "num_leaves": 31, "min_child_samples": 50,
               "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "random_state": 2020, "verbose": -1}
ENET_GRID = [(alpha, l1) for alpha in (0.001, 0.01, 0.1) for l1 in (0.2, 0.5, 0.8)]
LEASE_FEATURES = ["oil_lag1", "oil_lag3", "oil_lag6", "oil_lag12", "gas_lag1", "gas_lag3", "gas_lag6", "gas_lag12", "oil_mean3", "gas_mean3",
                  "oil_slope12", "gas_slope12", "water_ratio3", "producing_months", "months_since_first", "oil_share12", "n_completions",
                  "days_on_prod", "seasonal_oil", "seasonal_gas"]
PLANT_FEATURES = ["cf_lag1", "cf_lag3", "cf_lag12", "cf_mean12", "cf_seasonal", "zero_months12", "heat_rate3", "fuel_cost3",
                  "target_month_of_year", "nameplate_mw"]
MARKET_FEATURES = ["log_p0", "log_p1", "log_p2", "log_p3", "log_p6", "log_p12", "ret1", "ret3", "ret12", "vol3", "vol12"]


# --- baselines ------------------------------------------------------------------

def arps_baseline(lease, rows, window=36):
    """Arps forecast for each (lease, origin, horizon) row from the lease's observable history.

    Parameters
    ----------
    lease : pandas.DataFrame
        ``upstream_monthly``.
    rows : pandas.DataFrame
        Feature rows (``lease_number``, ``last_month_used``, ``horizon``).
    window : int
        Months of history fitted (the most recent observable ones).

    Returns
    -------
    pandas.DataFrame
        ``rows`` keys with ``arps_oil`` and ``arps_gas``.

    Notes
    -----
    One fit per (lease, last month used, product) on the last ``window``
    observable months; a horizon reuses the fit. Fits are cached by key so
    the three horizons of an origin share one fit.
    """
    oil = lease.pivot(index="lease_number", columns="month", values="oil_bbl")
    gas = lease.pivot(index="lease_number", columns="month", values="gas_mcf")
    months = oil.columns
    cache = {}
    out = []
    for key, part in rows.groupby(["lease_number", "last_month_used"]):
        lease_id, last = key
        if (lease_id, last) not in cache:
            i = months.get_loc(last)
            hist_o = oil.loc[lease_id].iloc[max(0, i - window + 1): i + 1].fillna(0).to_numpy()
            hist_g = gas.loc[lease_id].iloc[max(0, i - window + 1): i + 1].fillna(0).to_numpy()
            cache[(lease_id, last)] = (decline.fit_arps(hist_o), len(hist_o), decline.fit_arps(hist_g), len(hist_g))
        fit_o, n_o, fit_g, n_g = cache[(lease_id, last)]
        for h in part["horizon"]:
            out.append({"lease_number": lease_id, "last_month_used": last, "horizon": h,
                        "arps_oil": decline.forecast_arps(fit_o, h + rows_lag_months(last, part), n_o),
                        "arps_gas": decline.forecast_arps(fit_g, h + rows_lag_months(last, part), n_g)})
    return pd.DataFrame(out)


def rows_lag_months(last, part):
    """Months from the last observable month to the origin (the release lag of the rows)."""
    origin = part["origin"].iloc[0]
    return (origin.year - last.year) * 12 + (origin.month - last.month)


def technology_month_median(train, rows):
    """Median capacity factor of the training rows for each (technology, target month of year)."""
    med = train.groupby(["technology", "target_month_of_year"])["y_cf"].median().rename("tech_month_median")
    return rows.join(med, on=["technology", "target_month_of_year"])["tech_month_median"].to_numpy()


# --- challengers ----------------------------------------------------------------

def make_elasticnet(alpha, l1_ratio):
    """Median imputation, standardisation and an ElasticNet, fitted together inside each training fold."""
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=5000))


def make_lgbm(quantile=None):
    """LightGBM regressor with the registered parameters; a quantile objective when ``quantile`` is given."""
    params = dict(LGBM_PARAMS)
    if quantile is not None:
        params.update(objective="quantile", alpha=quantile)
    return lgb.LGBMRegressor(**params)


def rolling_predict(table, features, target, origins, factory, refit_every=REFIT_EVERY, transform=None):
    """Predict ``target`` at each origin with an expanding window refitted every ``refit_every`` origins.

    Parameters
    ----------
    table : pandas.DataFrame
        Feature rows of one horizon with ``origin``, ``target_month`` and ``target``.
    features : list of str
    target : str
    origins : sequence of Timestamp
        Scored origins, in order.
    factory : callable
        Returns a fresh unfitted estimator.
    refit_every : int
    transform : tuple of (callable, callable), optional
        Forward and inverse transforms of the target (e.g. ``np.log1p``, ``np.expm1``).

    Returns
    -------
    pandas.Series
        Predictions indexed like the rows at the scored origins, on the
        original scale.

    Notes
    -----
    The training rows of a refit at origin ``o`` are every row whose target
    month is on or before ``o`` with a known target — rows from earlier
    scored origins included, which is what an expanding window means.
    """
    fwd, inv = transform if transform else (lambda x: x, lambda x: x)
    preds = pd.Series(np.nan, index=table.index, dtype=float)
    model = None
    for k, origin in enumerate(origins):
        if k % refit_every == 0 or model is None:
            train = table[(table["target_month"] <= origin) & table[target].notna()]
            model = factory()
            model.fit(train[features], fwd(train[target].to_numpy()))
        rows = table[table["origin"] == origin]
        if len(rows):
            preds.loc[rows.index] = inv(model.predict(rows[features]))
    return preds


def choose_elasticnet(table, features, target, validation_origins, transform=None):
    """Pick (alpha, l1_ratio) by validation MAE from the registered grid, fitting once at the first validation origin."""
    first = validation_origins[0]
    fwd, inv = transform if transform else (lambda x: x, lambda x: x)
    train = table[(table["target_month"] <= first) & table[target].notna()]
    valid = table[table["origin"].isin(validation_origins) & table[target].notna()]
    best = None
    for alpha, l1 in ENET_GRID:
        model = make_elasticnet(alpha, l1).fit(train[features], fwd(train[target].to_numpy()))
        mae = np.mean(np.abs(inv(model.predict(valid[features])) - valid[target].to_numpy()))
        if best is None or mae < best[2]:
            best = (alpha, l1, mae)
    return {"alpha": best[0], "l1_ratio": best[1], "validation_mae": best[2]}


# --- scoring --------------------------------------------------------------------

def mae_by_origin(frame, columns, target):
    """MAE of each prediction column per origin (rows with a known target)."""
    known = frame[frame[target].notna()]
    return known.groupby("origin").apply(lambda g: pd.Series({c: np.mean(np.abs(g[c] - g[target])) for c in columns}), include_groups=False)


def paired_block_bootstrap(diff, n_boot=1000, block=3, seed=2020, level=0.95):
    """Interval of the mean of ``diff`` (one value per origin, in order) by moving-block bootstrap.

    Returns
    -------
    dict
        ``mean``, ``low``, ``high``, ``n_origins``, ``pass`` (interval entirely below 0).
    """
    x = np.asarray(diff, float)
    x = x[np.isfinite(x)]
    n = len(x)
    rng = np.random.default_rng(seed)
    block = min(block, n)
    n_blocks = int(np.ceil(n / block))
    draws = np.empty(n_boot)
    for k in range(n_boot):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        draws[k] = np.concatenate([x[s: s + block] for s in starts])[:n].mean()
    alpha = (1 - level) / 2
    low, high = float(np.quantile(draws, alpha)), float(np.quantile(draws, 1 - alpha))
    return {"mean": float(x.mean()), "low": low, "high": high, "n_origins": n, "pass": bool(high < 0)}


def score_line(frame, target, challenger, baselines, n_boot=1000, block=3, seed=2020):
    """Score one registered line: challenger against the best baseline (lowest holdout MAE) at matched origins.

    Returns
    -------
    dict
        ``best_baseline``, MAE of each model, the paired interval and the verdict.
    """
    per_origin = mae_by_origin(frame, [challenger] + list(baselines), target)
    best = per_origin[list(baselines)].mean().idxmin()
    paired = paired_block_bootstrap((per_origin[challenger] - per_origin[best]).to_numpy(), n_boot, block, seed)
    return {"best_baseline": best, **{f"mae_{m}": float(per_origin[m].mean()) for m in [challenger] + list(baselines)},
            "diff_mean": paired["mean"], "diff_low": paired["low"], "diff_high": paired["high"], "n_origins": paired["n_origins"],
            "result": "PASS" if paired["pass"] else "FAIL"}
