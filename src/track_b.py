"""Track B: the "ever built?" classifier for all nine regions.

What: designs for a logistic regression and a LightGBM classifier of
P(built) from entry-time features, a state encoding computed inside the
training rows only, the region × technology base rate it must beat, isotonic
calibration with an honest (cross-fitted) estimate of its effect, and the
Wilson interval used to judge per-region calibration.
Why: six of the nine regions publish no usable exit dates (decision #6), so
they cannot enter the timing models; resolved requests still say whether a
project was built. One row per request makes this a plain classification
problem, but with the same leakage rules as Track A.
Reads / writes: nothing.
Used by: notebook 04 (part C); ``tests/test_track_b.py``.
"""

from statistics import NormalDist

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import KFold

from src import config, discrete_time

STATE_PRIOR = 50  # smoothing of the state encoding: a state with 50 training requests gets half its own rate
SERVICE_LEVELS = ["NRIS", "ERIS", "NRIS/ERIS", "Other", "missing"]  # NRIS is the reference; NRIS/ERIS only in SPP
CALIBRATION_MIN_BIN = 50  # requests behind every step of the isotonic map (decision #30)
LGBM_BINARY = {"objective": "binary", "metric": "binary_logloss", "num_class": 1}  # overrides the multiclass base


def encode_state(train, others=(), n_folds=5, seed=0, prior=STATE_PRIOR):
    """Add ``state_rate`` (smoothed share built) without letting a request see its own outcome.

    Parameters
    ----------
    train : pandas.DataFrame
        Requests the model is fitted on (``state``, ``built``).
    others : sequence of pandas.DataFrame
        Requests to score; they get rates from all of ``train``.
    n_folds, seed : int
        Inner folds for the training requests' own encoding.
    prior : int
        m-estimate weight: rate = (built + prior × overall) / (n + prior).

    Returns
    -------
    tuple
        ``train`` with the column, then each of ``others``.

    Notes
    -----
    Training requests are encoded out of fold, so the model cannot learn a
    state's rate from the outcome it is predicting; unseen states get the
    overall rate. Same idea as ``discrete_time.encode_state``, one row per
    request instead of per project-year.
    """
    def rates(rows):
        overall = rows["built"].mean()
        grouped = rows.groupby("state")["built"].agg(["sum", "size"])
        return (grouped["sum"] + prior * overall) / (grouped["size"] + prior), overall

    out = train.copy()
    out["state_rate"] = np.nan
    for fit_idx, apply_idx in KFold(n_folds, shuffle=True, random_state=seed).split(out):
        table, overall = rates(out.iloc[fit_idx])
        out.iloc[apply_idx, out.columns.get_loc("state_rate")] = \
            out["state"].iloc[apply_idx].map(table).fillna(overall).to_numpy()
    table, overall = rates(train)
    scored = [rows.assign(state_rate=rows["state"].map(table).fillna(overall).to_numpy()) for rows in others]
    return (out, *scored)


def logit_design(frame):
    """Numeric design of the logistic regression (one row per request).

    Notes
    -----
    Indicators against PJM, solar, 20–<100 MW and NRIS; numeric request
    year, log size, log GW waiting at entry, congestion rank and the state
    rate. The hybrid flag is left out because Solar+Battery carries it (as
    in notebook 04, parts A and B). Fixed level lists give every design the same
    columns.
    """
    X = pd.DataFrame(index=frame.index)
    for region in config.ALL_REGIONS:
        if region != "PJM":
            X[f"region_{region}"] = (frame["region"] == region).astype(float)
    for tech in discrete_time.TECH_LEVELS[1:]:
        X[f"tech_{tech}"] = (frame["tech"] == tech).astype(float)
    for size in config.SIZE_LABELS:
        if size != "20–<100":
            X[f"size_{size}"] = (frame["size_regime"].astype(str) == size).astype(float)
    for service in SERVICE_LEVELS[1:]:
        X[f"service_{service}"] = (frame["service"] == service).astype(float)
    X["log_mw"] = frame["log_mw"].astype(float)
    X["q_year"] = frame["q_year"].astype(float)
    X["log_congestion_gw"] = np.log1p(frame["congestion_gw"].astype(float))
    X["congestion_rank"] = frame["congestion_rank"].astype(float).fillna(0.5)
    X["state_rate"] = frame["state_rate"].astype(float)
    return X


def lgbm_design(frame):
    """Design of the LightGBM classifier: categoricals with fixed levels plus the numeric features."""
    X = pd.DataFrame(index=frame.index)
    X["region"] = pd.Categorical(frame["region"].astype(str), categories=config.ALL_REGIONS)
    X["tech"] = pd.Categorical(frame["tech"].astype(str), categories=discrete_time.TECH_LEVELS)
    X["size_regime"] = pd.Categorical(frame["size_regime"].astype(str), categories=config.SIZE_LABELS)
    X["service"] = pd.Categorical(frame["service"].astype(str), categories=SERVICE_LEVELS)
    X["hybrid"] = frame["hybrid"].astype(float)
    X["log_mw"] = frame["log_mw"].astype(float)
    X["q_year"] = frame["q_year"].astype(float)
    X["log_congestion_gw"] = np.log1p(frame["congestion_gw"].astype(float))
    X["congestion_rank"] = frame["congestion_rank"].astype(float)
    X["state_rate"] = frame["state_rate"].astype(float)
    return X


def fit_lgbm(X, y, params, n_rounds, valid=None, record=None):
    """Binary LightGBM with the project's fixed seeds (``discrete_time.fit_lgbm`` with a binary objective)."""
    return discrete_time.fit_lgbm(X, y, {**LGBM_BINARY, **params}, n_rounds, valid=valid, record=record)


def base_rates(train, target, min_n=50):
    """Region × technology share built among training requests: the benchmark.

    Returns
    -------
    pandas.DataFrame
        Index of ``target``: ``rate`` and ``cell`` ("region × technology",
        or "region" when the cell has fewer than ``min_n`` requests).

    Notes
    -----
    Track B's version of notebook 04 (part A)'s baseline: what an analyst would
    quote for a new request from the historical record of similar ones.
    """
    cells = train.groupby(["region", "tech"])["built"].agg(["mean", "size"])
    regions = train.groupby("region")["built"].mean()
    keys = list(zip(target["region"], target["tech"]))
    own = [cells.loc[k, "mean"] if k in cells.index and cells.loc[k, "size"] >= min_n else np.nan for k in keys]
    out = pd.DataFrame({"rate": own}, index=target.index)
    out["cell"] = np.where(out["rate"].notna(), "region × technology", "region")
    out["rate"] = out["rate"].fillna(target["region"].map(regions))
    return out


def technology_rates(train, target):
    """Share built by technology among ``train`` (the benchmark for a region the model has never seen)."""
    return target["tech"].map(train.groupby("tech")["built"].mean()).fillna(train["built"].mean())


def isotonic(p, y, min_bin=CALIBRATION_MIN_BIN):
    """Isotonic map from raw scores to calibrated probabilities, every step backed by ``min_bin`` requests.

    Parameters
    ----------
    p, y : array-like
        Raw scores and outcomes (0/1) of the calibration requests.
    min_bin : int
        Requests per bin: the scores are cut into consecutive bins of at
        least this many requests before the isotonic fit.

    Returns
    -------
    sklearn.isotonic.IsotonicRegression
        Fitted on the bins' mean score and share built (weighted by bin
        size); ``predict`` interpolates linearly between bins and is flat
        beyond the first and last bin.

    Notes
    -----
    Plain isotonic regression on individual requests lets a handful of
    extreme scores set the top of the map: on the 2016 cohort nine requests
    with LightGBM scores above 0.53 sent the map to 100%, which 29 requests
    of the 2017 cohort would have inherited (decision #30). Fitting on bins
    keeps the monotone, assumption-free shape of isotonic calibration while
    no step rests on fewer than ``min_bin`` requests.
    """
    p, y = np.asarray(p, float), np.asarray(y, float)
    order = np.argsort(p, kind="stable")
    bins = np.array_split(order, max(1, len(p) // min_bin))
    x = np.array([p[b].mean() for b in bins])
    rate = np.array([y[b].mean() for b in bins])
    size = np.array([len(b) for b in bins])
    return IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(x, rate, sample_weight=size)


def cross_fit_isotonic(p, y, n_folds=2, seed=0):
    """Calibrated probabilities where each request's map was fitted without it.

    Notes
    -----
    The final map is fitted on the whole validation cohort, so scoring it on
    that cohort would flatter it. Fitting on one half and applying to the
    other gives an honest estimate of what calibration adds.
    """
    p, y = np.asarray(p, float), np.asarray(y, float)
    out = np.empty_like(p)
    for fit_idx, apply_idx in KFold(n_folds, shuffle=True, random_state=seed).split(p):
        out[apply_idx] = isotonic(p[fit_idx], y[fit_idx]).predict(p[apply_idx])
    return out


def wilson(successes, n, level=0.95):
    """Wilson score interval for a proportion.

    Notes
    -----
    Stays inside [0, 1] and behaves for small regions (ISO-NE and NYISO have
    a few dozen validation requests), unlike the normal approximation.
    """
    z = NormalDist().inv_cdf(1 - (1 - level) / 2)
    p = successes / n
    centre = (p + z ** 2 / (2 * n)) / (1 + z ** 2 / n)
    half = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / (1 + z ** 2 / n)
    return centre - half, centre + half
