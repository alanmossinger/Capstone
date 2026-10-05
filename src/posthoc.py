"""Blending and recalibration for the post-hoc analysis of notebook 08b.

What: a grid of blend weights on the simplex, the weights that minimise the
Brier score of a weighted average of several models' P(operation by t), a
logistic recalibration (intercept and slope on the logit scale), and a
cross-fitting helper that scores either step on data it was not fitted on.
Why: notebooks 08 and 09 found that the discrete-time logit is the best
calibrated model at 3 and 5 years, Cox ranks best at 7 years and LightGBM's
probabilities run high; a blend or a recalibration may combine their
strengths. Both are fitted on the 2016 cohort, so their 2016 score must be
cross-fitted to be compared fairly with models that never saw 2016.
Reads / writes: nothing.
Used by: notebook 08b; ``tests/test_posthoc.py``.
"""

from itertools import product

import numpy as np
from sklearn.model_selection import KFold

from src import evaluation


def simplex_grid(n_models, step=0.1):
    """All non-negative weight vectors on a grid of ``step`` that sum to 1."""
    k = int(round(1 / step))
    return np.array([w for w in product(range(k + 1), repeat=n_models) if sum(w) == k], dtype=float) / k


def fit_blend(P, y, w=None, step=0.1):
    """Blend weights (one per column of ``P``) with the lowest Brier score.

    Parameters
    ----------
    P : numpy.ndarray
        Shape (requests, models): each model's P(operation by t).
    y, w : array-like
        Outcomes and weights (``evaluation.horizon_outcome``).
    step : float
        Grid step of the weights.

    Notes
    -----
    A grid search rather than an optimiser: with three models and a step of
    0.1 there are 66 candidates, every one is checked, and ties go to the
    first (which puts more weight on the earlier columns).
    """
    w = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
    grid = simplex_grid(P.shape[1], step)
    scores = [evaluation.brier(P @ g, y, w) for g in grid]
    return grid[int(np.argmin(scores))]


def fit_recalibration(p, y, w=None):
    """Intercept and slope of a logistic recalibration: logit(p') = a + b · logit(p)."""
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    w = np.ones(len(p)) if w is None else np.asarray(w, dtype=float)
    keep = w > 0
    x = np.log(p / (1 - p))[keep]
    X = np.column_stack([np.ones(len(x)), x])
    return evaluation._logistic(X, np.asarray(y, dtype=float)[keep], w[keep], np.zeros(len(x)))


def apply_recalibration(p, coef):
    """Apply ``fit_recalibration``'s coefficients to new predictions."""
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return 1 / (1 + np.exp(-(coef[0] + coef[1] * np.log(p / (1 - p)))))


def cross_fit(fit, apply, n, n_folds=2, seed=0):
    """Out-of-fold predictions: ``fit(train_index)`` returns parameters, ``apply(params, test_index)`` predictions.

    Notes
    -----
    Each request's prediction comes from parameters fitted without it, so
    the score of a blend or a recalibration on the cohort it is fitted on
    is not flattered (the same idea as ``track_b.cross_fit_isotonic``).
    """
    out = np.empty(n)
    for fit_idx, apply_idx in KFold(n_folds, shuffle=True, random_state=seed).split(np.arange(n)):
        out[apply_idx] = apply(fit(fit_idx), apply_idx)
    return out
