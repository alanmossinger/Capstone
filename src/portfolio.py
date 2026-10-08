"""The portfolio layer: a book of requests simulated with correlated risk, chosen under a budget, and backtested.

What: an estimate of how much requests in the same region and cohort move
together (over-dispersion of cohort completion rates), a one-factor
Gaussian-copula simulation of a book that keeps each request's own
probability, a budget-constrained choice of requests by mixed-integer
programming, and the realised outcome of a book.
Why: a portfolio manager does not hold one request; the question is what a
*book* delivers and how wrong that can go. Independent draws understate the
risk when a whole cohort slows down together, which notebook 12 showed it
does. The choice of book is the decision the report is for, and the backtest
is how the choice is judged (criteria C9–C11).
Reads / writes: nothing.
Used by: notebook 16; ``tests/test_portfolio.py``.
"""

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.stats import norm


def estimate_rho(observed, predicted, n):
    """Latent correlation of a one-factor copula from the over-dispersion of cohort completion rates.

    Parameters
    ----------
    observed, predicted : array-like
        Observed and mean-predicted completion rate of each cohort group
        (region × entry year).
    n : array-like
        Requests in each group.

    Returns
    -------
    tuple of (float, float)
        ``rho`` (clipped to [0, 0.5]) and ``phi``, the excess of the
        variance of (observed − predicted) over its binomial expectation,
        as a share of the binomial variance.

    Notes
    -----
    If requests were independent given their probabilities, the cohort rate
    would vary around the mean prediction by p(1 − p)/n. Any excess is
    shared movement. ``phi`` is the intra-cohort correlation of outcomes
    under a beta-binomial reading; it is used directly as the copula's
    latent correlation, which is a rough but transparent mapping (the latent
    correlation of a Gaussian copula produces a smaller outcome correlation,
    so ``rho = phi`` errs on the side of more shared risk).
    """
    observed, predicted, n = (np.asarray(observed, float), np.asarray(predicted, float), np.asarray(n, float))
    binomial = predicted * (1 - predicted) / n
    excess = np.var(observed - predicted, ddof=1) - binomial.mean()
    phi = float(max(excess, 0.0) / (predicted * (1 - predicted)).mean())
    return float(np.clip(phi, 0.0, 0.5)), phi


def simulate_book(P, mw, groups, rho, n_draws=5000, seed=0):
    """MW built by year in each simulated draw of a book, with a shared factor per group.

    Parameters
    ----------
    P : numpy.ndarray
        Shape (requests, years): cumulative P(operation by year j).
    mw : array-like
        Capacity of each request.
    groups : array-like
        Group label of each request (the shared factor: region × cohort).
    rho : float
        Latent correlation within a group.
    n_draws, seed : int

    Returns
    -------
    numpy.ndarray
        Shape (draws, years): cumulative MW online in each draw.

    Notes
    -----
    Each request gets a latent z = √ρ · F_g + √(1 − ρ) · ε with F_g shared by
    its group; it has operated by year j when z < Φ⁻¹(P_ij), so its marginal
    probability is exactly P_ij and the events are nested across years.
    """
    P = np.asarray(P, float)
    mw = np.asarray(mw, float)
    groups = pd.factorize(np.asarray(groups))[0]
    rng = np.random.default_rng(seed)
    factor = rng.standard_normal((n_draws, groups.max() + 1))
    z = np.sqrt(rho) * factor[:, groups] + np.sqrt(1 - rho) * rng.standard_normal((n_draws, len(mw)))
    thresholds = norm.ppf(np.clip(P, 1e-9, 1 - 1e-9))  # (requests, years)
    out = np.empty((n_draws, P.shape[1]))
    for j in range(P.shape[1]):
        out[:, j] = (z < thresholds[:, j][None, :]) @ mw
    return out


def choose_book(score, cost, budget, caps=(), min_score=None):
    """Requests that maximise the total score under a budget and group caps (binary program).

    Parameters
    ----------
    score : array-like
        Value of choosing each request (expected value, expected MW …).
    cost : array-like
        What choosing it commits (the sunk cost to the next gate).
    budget : float
    caps : sequence of (labels, share)
        For each, the chosen cost inside any one label must not exceed
        ``share × budget`` (region and technology concentration limits).
    min_score : float, optional
        Requests scoring below it are not eligible.

    Returns
    -------
    numpy.ndarray of bool
        The chosen requests.

    Notes
    -----
    ``scipy.optimize.milp`` (HiGHS). The program is a knapsack with side
    constraints; it is small (a few thousand binaries) and solves in well
    under a second. Ties and near-ties are broken by the solver, so the
    chosen book is one optimal book, not the unique one.
    """
    score, cost = np.asarray(score, float), np.asarray(cost, float)
    n = len(score)
    eligible = np.ones(n, bool) if min_score is None else score >= min_score
    rows, upper = [cost], [budget]
    for labels, share in caps:
        labels = np.asarray(labels)
        for label in pd.unique(labels):
            rows.append(np.where(labels == label, cost, 0.0))
            upper.append(share * budget)
    A = np.vstack(rows)
    result = milp(c=-score * eligible, constraints=LinearConstraint(A, -np.inf, upper),
                  integrality=np.ones(n), bounds=Bounds(0, eligible.astype(float)))
    assert result.success, result.message
    return result.x > 0.5


def realised_mw(chosen, events, durations, mw, horizon):
    """MW of the chosen requests that reached operation within ``horizon`` years of entry."""
    chosen, events, durations, mw = (np.asarray(chosen, bool), np.asarray(events), np.asarray(durations, float), np.asarray(mw, float))
    return float(mw[chosen & (events == 1) & (durations <= horizon)].sum())


def random_book(cost, budget, caps, rng):
    """A book filled at random until the budget binds, respecting the caps (the 'no model' chooser)."""
    cost = np.asarray(cost, float)
    order = rng.permutation(len(cost))
    chosen = np.zeros(len(cost), bool)
    spent = 0.0
    spent_by = [dict() for _ in caps]
    for i in order:
        if spent + cost[i] > budget:
            continue
        ok = True
        for k, (labels, share) in enumerate(caps):
            if spent_by[k].get(labels[i], 0.0) + cost[i] > share * budget:
                ok = False
                break
        if not ok:
            continue
        chosen[i] = True
        spent += cost[i]
        for k, (labels, _) in enumerate(caps):
            spent_by[k][labels[i]] = spent_by[k].get(labels[i], 0.0) + cost[i]
    return chosen


def top_n_book(score, groups, n, cap_share, tiebreak):
    """The ``n`` requests with the highest score, no group above ``cap_share`` of ``n``.

    Parameters
    ----------
    score : array-like
        Each request's score (higher is kept first); ``-inf`` is never kept.
    groups : array-like
        Group of each request (region), for the concentration cap.
    n : int
        Size of the book.
    cap_share : float
        Largest share of the ``n`` places one group may take.
    tiebreak : array-like
        A random number per request; among equal scores the lower one is
        taken first.

    Returns
    -------
    numpy.ndarray of bool
        The chosen requests.

    Notes
    -----
    A count-limited book: the question is which requests, not how many MW
    per dollar, so ranking is all that matters (decision #58). Lookup
    scores are equal inside a cell, so the tie-break decides which members
    of the last cell get in; passing the same ``tiebreak`` to every chooser
    keeps the comparison paired, and drawing it afresh in each bootstrap
    resample averages its effect into the interval. Greedy order with the
    cap is optimal here because every request takes one place.
    """
    score, groups, tiebreak = np.asarray(score, float), np.asarray(groups), np.asarray(tiebreak, float)
    limit = int(np.floor(cap_share * n))
    order = np.lexsort((tiebreak, -score))
    chosen = np.zeros(len(score), bool)
    taken = {}
    for i in order:
        if chosen.sum() == n or not np.isfinite(score[i]):
            break
        if taken.get(groups[i], 0) < limit:
            chosen[i] = True
            taken[groups[i]] = taken.get(groups[i], 0) + 1
    return chosen
