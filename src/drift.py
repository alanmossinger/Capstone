"""Cohort drift: how the level of completion moves between entry years, and how to repair a model's level.

What: observed against predicted P(operation by t) by entry cohort with
bootstrap bands; a rolling, intercept-only logistic recalibration that sets
a model's level from the newest cohort whose outcomes are observed and
earlier than the cohort being scored; the early (1- and 2-year) incidence of
recent entrants.
Why: completion within 5 years fell from 12.8% for 2017 entrants to 8.3%
and 9.6% for 2018 and 2019 entrants while the tree model, which cannot
extrapolate the request year, stayed at 13–14% (notebook 08). A portfolio's
expected MW online scales with the level, so the level has to be repaired
before any book is priced (PLAN.md, notebook 12).
Reads / writes: nothing.
Used by: notebook 12; ``tests/test_drift.py``.
"""

import numpy as np
import pandas as pd

from src import evaluation, survival_tools


def level_by_group(predictions, durations, events, groups, horizon, n_boot=200, seed=0):
    """Observed P(operation by ``horizon``) with a bootstrap band and each model's mean prediction, per group.

    Parameters
    ----------
    predictions : dict
        Model name → predicted P(operation by ``horizon``), one value per request.
    durations, events : array-like
        Time-to-event data of the same requests.
    groups : array-like
        Group label of each request (entry year, region, size band …).
    horizon : int
    n_boot, seed : int
        Bootstrap settings for the observed band.

    Returns
    -------
    pandas.DataFrame
        One row per group: ``n``, ``observed``, ``low``, ``high`` and one
        column per model.

    Notes
    -----
    The observed value is the Aalen–Johansen incidence, so withdrawals are
    competing events and censored requests are handled properly; the
    predicted value is the plain mean of the model's probabilities.
    """
    durations, events, groups = (np.asarray(durations), np.asarray(events), np.asarray(groups))
    rows = []
    for g_i, g in enumerate(pd.unique(groups)):
        idx = groups == g
        observed = survival_tools.aalen_johansen(durations[idx], events[idx], [horizon])["cif_operation"].iloc[0]
        band = survival_tools.bootstrap_bands(durations[idx], events[idx], [horizon], n_boot=n_boot, seed=seed + g_i)
        rows.append({"group": g, "n": int(idx.sum()), "observed": observed,
                     "low": band["cif_operation_low"].iloc[0], "high": band["cif_operation_high"].iloc[0],
                     **{m: float(np.mean(np.asarray(p)[idx])) for m, p in predictions.items()}})
    return pd.DataFrame(rows)


def fit_intercept(p, y, w=None):
    """Intercept of a logistic recalibration with the slope fixed at 1: logit(p') = a + logit(p).

    Notes
    -----
    A level shift only. With a slope as well the repair would also reshape
    the ranking, and the ranking is what the model is kept for; the slope is
    reported, not fitted (PLAN.md, notebook 12). Weighted by the IPCW weights
    so censored requests drop out.
    """
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    w = np.ones(len(p)) if w is None else np.asarray(w, dtype=float)
    keep = w > 0
    x = np.log(p / (1 - p))[keep]
    return float(evaluation._logistic(np.ones((len(x), 1)), np.asarray(y, dtype=float)[keep], w[keep], x)[0])


def apply_intercept(p, a):
    """Shift predictions on the logit scale by ``a``."""
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return 1 / (1 + np.exp(-(a + np.log(p / (1 - p)))))


def rolling_recalibration(p, y, w, years, regions, source_year):
    """Recalibrate each scored cohort on an earlier cohort, region by region.

    Parameters
    ----------
    p, y, w : array-like
        Predictions, horizon outcomes and IPCW weights of every request
        (scored and source cohorts together).
    years, regions : array-like
        Entry year and region of each request.
    source_year : dict
        Scored entry year → the entry year whose outcomes set its level
        (for example {2017: 2016, 2018: 2017, 2019: 2018}).

    Returns
    -------
    tuple of (numpy.ndarray, pandas.DataFrame)
        Recalibrated predictions for the requests whose year is in
        ``source_year`` (NaN elsewhere) and the fitted intercepts per
        (scored year, region) with the source cohort's size.

    Notes
    -----
    The scored cohort's own outcomes never enter its intercept: year Y is
    shifted by the level of the year named in ``source_year[Y]``, which must
    be earlier. The source cohort's outcomes have to be observed by the
    analysis date, so this is the level an analyst sets *today* from the
    newest cohort that has had time to resolve, not a level that was
    knowable on the request date (the report says so). A region with no
    source requests keeps the pooled intercept of that year.
    """
    p, y, w, years, regions = (np.asarray(p, dtype=float), np.asarray(y, dtype=float), np.asarray(w, dtype=float),
                               np.asarray(years), np.asarray(regions))
    out = np.full(len(p), np.nan)
    rows = []
    for year, source in source_year.items():
        assert source < year, "the source cohort must be earlier than the scored cohort"
        src = years == source
        pooled = fit_intercept(p[src], y[src], w[src])
        for region in pd.unique(regions[years == year]):
            src_r = src & (regions == region)
            a = fit_intercept(p[src_r], y[src_r], w[src_r]) if (w[src_r] > 0).sum() >= 30 else pooled
            if not np.isfinite(a):
                a = pooled
            idx = (years == year) & (regions == region)
            out[idx] = apply_intercept(p[idx], a)
            rows.append({"scored_year": year, "source_year": source, "region": region, "intercept": a,
                         "source_requests": int(src_r.sum())})
    return out, pd.DataFrame(rows)


def early_incidence(frame, entry_years, horizons=(1, 2), n_boot=200, seed=0):
    """Aalen–Johansen P(operation by h) of recent entrants, by entry year, with bands.

    Parameters
    ----------
    frame : pandas.DataFrame
        Requests with ``q_year``, ``duration_years`` and ``event`` (coded
        against the file's own censoring date).
    entry_years : iterable of int
    horizons : tuple of int
        Short horizons every listed cohort can reach before censoring.

    Returns
    -------
    pandas.DataFrame
        One row per (entry year, horizon): ``n``, ``observed``, ``low``,
        ``high``, ``operations`` (events within the horizon).

    Notes
    -----
    Used for the 2020–2022 entrants, whose 1- and 2-year outcomes are the
    newest evidence on the level; the model's predicted P(operation by 1
    and 2 years) for the same requests is compared with these in notebook 12.
    """
    rows = []
    for y_i, year in enumerate(entry_years):
        part = frame[frame["q_year"] == year]
        aj = survival_tools.aalen_johansen(part["duration_years"], part["event"], list(horizons))
        band = survival_tools.bootstrap_bands(part["duration_years"], part["event"], list(horizons), n_boot=n_boot, seed=seed + y_i)
        for j, h in enumerate(horizons):
            rows.append({"entry_year": year, "horizon": h, "n": len(part), "observed": aj["cif_operation"].iloc[j],
                         "low": band["cif_operation_low"].iloc[j], "high": band["cif_operation_high"].iloc[j],
                         "operations": int(((part["event"] == 1) & (part["duration_years"] <= h)).sum())})
    return pd.DataFrame(rows)
