"""Scoring P(operation by t) under competing risks and censoring, and Track B's P(built).

What: censoring weights (inverse probability of censoring, IPCW), the
outcome "operated by year t" with its weight, the competing-risks
concordance index (Harrell's and Uno's), time-dependent AUC, the Brier
score, the calibration slope and intercept, a calibration table by
predicted decile, precision and lift in the top fraction of predictions,
and a bootstrap that resamples requests.
Why: a request that withdrew before year t is a known non-event, not a
censored one; only requests still waiting on 2024-12-31 are censored.
Off-the-shelf survival metrics treat withdrawal as censoring, which would
score a different question. Every function takes an optional
``sample_weight`` (how many times each request is drawn), so the bootstrap
reuses the same code instead of copying rows.
Reads / writes: nothing.
Used by: notebook 08; ``tests/test_evaluation.py``.
"""

import numpy as np
import pandas as pd

from src.events import OPERATION, WITHDRAWAL


def censoring_km(durations, censored):
    """Kaplan–Meier estimate G of the censoring distribution, returned as a step function.

    Parameters
    ----------
    durations : array-like
        Years from request to censoring or exit.
    censored : array-like of bool
        True where the duration ends in censoring (the "event" of this fit).

    Returns
    -------
    callable
        ``G(s, left=False)``: probability of not being censored by ``s``
        (``left=True`` gives the value just before ``s``, G(s−)).

    Notes
    -----
    The usual Kaplan–Meier product with the roles of event and censoring
    swapped: an exit by operation or withdrawal ends a request's chance of
    being censored without being censored. When every censoring time is
    known in advance (administrative censoring), passing those times with
    ``censored`` all True gives the plain share of requests whose window is
    longer than ``s``.
    """
    d = np.asarray(durations, dtype=float)
    c = np.asarray(censored, dtype=bool)
    unique = np.unique(d[c])
    at_risk = np.array([(d >= u).sum() for u in unique], dtype=float)
    counts = np.array([((d == u) & c).sum() for u in unique], dtype=float)
    survival = np.cumprod(1 - counts / at_risk)

    def G(s, left=False):
        s = np.asarray(s, dtype=float)
        index = np.searchsorted(unique, s, side="left" if left else "right") - 1
        return np.where(index >= 0, survival[np.clip(index, 0, None)], 1.0)

    return G


def horizon_outcome(durations, events, t, G):
    """Whether each request reached operation by year ``t``, and its IPCW weight.

    Parameters
    ----------
    durations, events : array-like
        Years to exit or censoring; 0 censored, 1 operation, 2 withdrawal.
    t : float
        Horizon in years.
    G : callable
        Censoring survival from ``censoring_km``.

    Returns
    -------
    tuple of numpy.ndarray
        ``y`` (1 = operated by ``t``) and ``w`` (weight; 0 = status at ``t``
        unknown).

    Notes
    -----
    Operation by ``t``: y = 1, weight 1/G(T−). Withdrawal by ``t``: a known
    non-event, y = 0, weight 1/G(T−). Still in the queue after ``t``
    (whatever happened later): y = 0, weight 1/G(t). Censored before ``t``:
    unknown, weight 0. The weights make the requests whose status is known
    stand in for those censored at the same time (Graf et al., 1999; with a
    competing event as in Schoop et al., 2011).
    """
    d = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=int)
    y = ((e == OPERATION) & (d <= t)).astype(float)
    w = np.zeros(len(d))
    exited = (e > 0) & (d <= t)
    later = d > t
    w[exited] = 1 / G(d[exited], left=True)
    w[later] = 1 / G(t)
    return y, w


def _weights(n, sample_weight):
    return np.ones(n) if sample_weight is None else np.asarray(sample_weight, dtype=float)


def brier(p, y, w, sample_weight=None):
    """IPCW Brier score: mean weighted squared gap between prediction and outcome.

    Notes
    -----
    Divided by the number of requests (censored ones included, with weight
    0), the Graf et al. estimator; lower is better.
    """
    sw = _weights(len(p), sample_weight)
    return float(np.sum(sw * w * (np.asarray(y) - np.asarray(p)) ** 2) / np.sum(sw))


def auc(p, y, w=None, sample_weight=None):
    """Weighted area under the ROC curve (time-dependent AUC when ``y``, ``w`` come from ``horizon_outcome``).

    Notes
    -----
    Cases are requests with y = 1, controls those with y = 0 and a positive
    weight; every case–control pair counts with the product of their
    weights, a tie in prediction counts one half. Computed from sorted
    unique predictions, so it is linear in the number of requests apart from
    the sort. Controls include withdrawn requests (Blanche et al., 2013,
    definition 2).
    """
    p = np.asarray(p, dtype=float)
    y = np.asarray(y)
    weight = (np.ones(len(p)) if w is None else np.asarray(w, dtype=float)) * _weights(len(p), sample_weight)
    values, position = np.unique(p, return_inverse=True)
    case = np.bincount(position, weights=weight * (y == 1), minlength=len(values))
    control = np.bincount(position, weights=weight * (y == 0), minlength=len(values))
    below = np.cumsum(control) - control
    return float(np.sum(case * (below + 0.5 * control)) / (case.sum() * control.sum()))


def concordance(p, durations, events, t, G=None, sample_weight=None):
    """Concordance of P(operation by ``t``) with the order of operations, withdrawal as a competing event.

    Parameters
    ----------
    p : array-like
        Predicted P(operation by ``t``).
    durations, events : array-like
        As in ``horizon_outcome``.
    t : float
        Truncation time: only operations by ``t`` define pairs.
    G : callable, optional
        Censoring survival. None gives Harrell's version (every comparable
        pair counts once); with ``G`` the pairs are weighted as in Uno et al.
        (2011), extended to competing risks by Wolbers et al. (2014).
    sample_weight : array-like, optional

    Returns
    -------
    float

    Notes
    -----
    A pair (i, j) is comparable when i operated at T_i ≤ t and either j was
    still in the queue at T_i (T_j > T_i, any later status) or j had already
    withdrawn (withdrawn at T_j ≤ T_i: it will never operate). It is
    concordant when i's prediction is higher; ties count one half. Weights:
    1/(G(T_i−)·G(T_i)) for the first kind, 1/(G(T_i−)·G(T_j−)) for the
    second.
    """
    p = np.asarray(p, dtype=float)
    d = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=int)
    sw = _weights(len(p), sample_weight)
    cases = np.flatnonzero((e == OPERATION) & (d <= t) & (sw > 0))
    di = d[cases][:, None]
    later = d[None, :] > di
    withdrawn_before = (e[None, :] == WITHDRAWAL) & (d[None, :] <= di)
    if G is None:
        pair = later.astype(float) + withdrawn_before
    else:
        gi = G(d[cases], left=True)[:, None]
        pair = later / (gi * G(d[cases])[:, None]) + withdrawn_before / (gi * G(d, left=True)[None, :])
    pair = pair * sw[cases][:, None] * sw[None, :]
    score = (p[cases][:, None] > p[None, :]) + 0.5 * (p[cases][:, None] == p[None, :])
    return float(np.sum(pair * score) / np.sum(pair))


def _logistic(X, y, weight, offset):
    """Weighted logistic regression by Newton's method (two or fewer parameters)."""
    beta = np.zeros(X.shape[1])
    for _ in range(100):
        mu = 1 / (1 + np.exp(-(X @ beta + offset)))
        gradient = X.T @ (weight * (y - mu))
        hessian = (X * (weight * mu * (1 - mu))[:, None]).T @ X
        step = np.linalg.solve(hessian, gradient)
        beta += step
        if np.max(np.abs(step)) < 1e-10:
            break
    return beta


def calibration_slope_intercept(p, y, w=None, sample_weight=None):
    """Calibration slope and intercept of predicted probabilities.

    Returns
    -------
    dict
        ``slope``: coefficient of logit(p) in a logistic regression of the
        outcome on logit(p) (1 = spread right; < 1 = predictions too
        extreme). ``intercept``: intercept with logit(p) as a fixed offset
        (0 = right average level; > 0 = predictions too low).

    Notes
    -----
    The usual recalibration framework (Cox, 1958; Van Calster et al., 2019),
    weighted by the IPCW weights so censored requests drop out and the
    others stand in for them. Predictions are clipped to [1e-6, 1 − 1e-6]
    before the logit.
    """
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, dtype=float)
    weight = (np.ones(len(p)) if w is None else np.asarray(w, dtype=float)) * _weights(len(p), sample_weight)
    keep = weight > 0
    x, y, weight = np.log(p / (1 - p))[keep], y[keep], weight[keep]
    slope = _logistic(np.column_stack([np.ones(len(x)), x]), y, weight, np.zeros(len(x)))[1]
    intercept = _logistic(np.ones((len(x), 1)), y, weight, x)[0]
    return {"slope": float(slope), "intercept": float(intercept)}


def top_fraction(p, y, w=None, fraction=0.1, sample_weight=None):
    """Precision and lift among the requests with the highest predictions.

    Parameters
    ----------
    p, y, w : array-like
        Predictions, outcomes and weights (``horizon_outcome``).
    fraction : float
        Share of requests selected (0.1 = top decile).

    Returns
    -------
    dict
        ``precision`` (weighted share operated among the selected),
        ``base_rate`` (the same share among all requests) and ``lift``
        (precision ÷ base rate).

    Notes
    -----
    Requests are taken in order of prediction until ``fraction`` of them is
    selected. Predictions tied at the cut-off (the baseline gives whole
    region × technology cells one value) are included in proportion, which
    equals the average over every random way of breaking the tie, so a
    coarse predictor is neither helped nor hurt by the order of rows.
    """
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    sw = _weights(len(p), sample_weight)
    weight = (np.ones(len(p)) if w is None else np.asarray(w, dtype=float)) * sw
    values, position = np.unique(-p, return_inverse=True)  # highest prediction first
    group_count = np.bincount(position, weights=sw, minlength=len(values))
    before = np.cumsum(group_count) - group_count
    target = fraction * sw.sum()
    share = np.clip((target - before) / np.where(group_count > 0, group_count, 1), 0, 1)
    included = share[position]
    precision = np.sum(included * weight * y) / np.sum(included * weight)
    base_rate = np.sum(weight * y) / np.sum(weight)
    return {"precision": float(precision), "base_rate": float(base_rate), "lift": float(precision / base_rate)}


def decile_groups(p, n_groups=10):
    """Group number 0 … n_groups − 1 by predicted value (ties broken by row order).

    Notes
    -----
    Ranking with ties broken by position puts the same number of requests in
    every group even for the baseline, whose predictions take a few values;
    the groups of a tied value then share one mean prediction.
    """
    ranks = pd.Series(np.asarray(p, dtype=float)).rank(method="first").to_numpy()
    return np.minimum(((ranks - 1) * n_groups / len(ranks)).astype(int), n_groups - 1)


HIGHER_IS_BETTER = {"uno_c": True, "harrell_c": True, "auc": True, "brier": False,
                    "precision_10": True, "lift_10": True}  # slope and intercept have a target, not a direction


def score(predictions, y, w=None, sample_weight=None):
    """AUC, Brier score, calibration slope and intercept, top-decile precision and lift for each model.

    Parameters
    ----------
    predictions : dict
        Model name → predicted probabilities (same order as ``y``).
    y, w : array-like
        Outcomes and weights (``horizon_outcome``; ``w`` None = all 1).

    Returns
    -------
    dict
        Keys ``"<model>|<metric>"``.
    """
    w = np.ones(len(y)) if w is None else w
    out = {}
    for name, p in predictions.items():
        out[f"{name}|auc"] = auc(p, y, w, sample_weight)
        out[f"{name}|brier"] = brier(p, y, w, sample_weight)
        calibration = calibration_slope_intercept(p, y, w, sample_weight)
        out[f"{name}|slope"], out[f"{name}|intercept"] = calibration["slope"], calibration["intercept"]
        top = top_fraction(p, y, w, 0.1, sample_weight)
        out[f"{name}|precision_10"], out[f"{name}|lift_10"] = top["precision"], top["lift"]
    return out


def score_horizon(predictions, durations, events, t, G, sample_weight=None):
    """``score`` for P(operation by ``t``), plus Uno's and Harrell's concordance."""
    y, w = horizon_outcome(durations, events, t, G)
    out = score(predictions, y, w, sample_weight)
    for name, p in predictions.items():
        out[f"{name}|uno_c"] = concordance(p, durations, events, t, G, sample_weight)
        out[f"{name}|harrell_c"] = concordance(p, durations, events, t, None, sample_weight)
    return out


def summarise(point, draws, reference="baseline", level=0.95):
    """Long table of estimates with bootstrap intervals and paired differences from ``reference``.

    Parameters
    ----------
    point : dict
        Full-sample values, keys ``"<model>|<metric>"``.
    draws : pandas.DataFrame
        ``bootstrap`` output of the same function.
    reference : str
        Model every other model is compared with.

    Returns
    -------
    pandas.DataFrame
        ``model``, ``metric``, ``estimate``, ``low``, ``high`` and, for
        metrics with a direction, ``diff`` (model − reference) with its
        interval and ``beats`` (the interval excludes zero on the better
        side).
    """
    rows = []
    for key, value in point.items():
        model, metric = key.split("|")
        row = {"model": model, "metric": metric, "estimate": value}
        row["low"], row["high"] = interval(draws[key], level)
        ref_key = f"{reference}|{metric}"
        if metric in HIGHER_IS_BETTER and model != reference and ref_key in point:
            row["diff"] = value - point[ref_key]
            row["diff_low"], row["diff_high"] = interval(draws[key] - draws[ref_key], level)
            row["beats"] = row["diff_low"] > 0 if HIGHER_IS_BETTER[metric] else row["diff_high"] < 0
        rows.append(row)
    return pd.DataFrame(rows)


def bootstrap(stat, n, n_boot=200, seed=0):
    """Apply ``stat`` to ``n_boot`` bootstrap resamples of ``n`` requests.

    Parameters
    ----------
    stat : callable
        ``stat(sample_weight) -> dict`` of named values; ``sample_weight``
        holds how often each request was drawn.
    n, n_boot, seed : int

    Returns
    -------
    pandas.DataFrame
        One row per resample, one column per key of ``stat``'s result.

    Notes
    -----
    Every value in a row comes from the same resample, so differences
    between columns (model − baseline) form a paired bootstrap. The
    censoring weights are held at their full-sample values (they describe
    the follow-up window, fixed by the request date).
    """
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_boot):
        counts = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        rows.append(stat(counts))
    return pd.DataFrame(rows)


def interval(values, level=0.95):
    """Percentile interval of bootstrap values: (low, high)."""
    tail = (1 - level) / 2 * 100
    return float(np.percentile(values, tail)), float(np.percentile(values, 100 - tail))
