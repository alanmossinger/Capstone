"""Value of information: what knowing more before committing is worth, on the scenarios the book is chosen on.

What: the expected value of perfect information (EVPI) for the whole
uncertainty and for blocks of it (prices, a request's completion, the
lease cost draw), and the expected value of sample information (EVSI) for
a signal a developer can actually wait for — whether a request signs its
interconnection agreement — whose likelihoods come from the queue history.
Every value is the gain in the best book's expected NPV from deciding after
the information rather than before, under the same budget and caps.
Why: the brief asks when to invest now and when to wait; a value of
information is the most a committee should pay — in money or in delay — to
learn something first. No public file gives what the information would
cost, so the report states the value as that ceiling, not as a return
(decision #91).
Reads / writes: nothing; notebook 11 passes the matrices in.
Used by: notebook 11; `tests/test_voi.py`.

Adapted from: Raiffa, H. and Schlaifer, R. (1961), *Applied Statistical
Decision Theory* — the preposterior analysis that values a signal by the
decisions it would change.
"""

import numpy as np
import pandas as pd

from src import optimizer as opt


def best_mean_value(A, charge, budget, groups=None, group_cap=None, weights=None):
    """The best book's expected NPV for scenario weights ``weights`` (equal when None), risk-neutral, under the budget and caps.

    Notes
    -----
    With λ = 0 only the weighted mean of each candidate enters the MILP, so
    the problem is solved on that one row: a 40-item knapsack with
    technology caps, solved exactly by HiGHS.
    """
    A = np.asarray(A, float)
    w = np.full(A.shape[0], 1.0 / A.shape[0]) if weights is None else np.asarray(weights, float) / np.sum(weights)
    mu = w @ A
    out = opt.solve_milp(mu[None, :], charge, budget, lam=0.0, groups=groups, group_cap=group_cap)
    return float(mu @ out["x"]), out["x"]


def evpi_total(A, charge, budget, groups=None, group_cap=None):
    """EVPI of everything: the mean over scenarios of the best book for that scenario, less the best book for all of them."""
    prior, _ = best_mean_value(A, charge, budget, groups, group_cap)
    per_scenario = [best_mean_value(A[s:s + 1], charge, budget, groups, group_cap)[0] for s in range(A.shape[0])]
    return {"prior_value": prior, "with_information": float(np.mean(per_scenario)), "evpi": float(np.mean(per_scenario) - prior)}


def evpi_partition(A, charge, budget, labels, groups=None, group_cap=None):
    """EVPI of learning which cell of a partition of the scenarios is true (a partial EVPI).

    Parameters
    ----------
    labels : array-like
        One cell label per scenario: the information revealed. For a
        request's completion, built or not; for prices or costs, a decile of
        the quantity learned.

    Returns
    -------
    dict
        ``prior_value``, ``with_information``, ``evpi`` and ``cells`` (the
        book each cell would choose, by cell).

    Notes
    -----
    Σ_c P(c) · max_x E[NPV(x) | c] − max_x E[NPV(x)]: the decision is made
    after the cell is known and before anything else is. It is never
    negative: knowing more cannot lower the best expected value.
    """
    labels = np.asarray(labels)
    prior, _ = best_mean_value(A, charge, budget, groups, group_cap)
    value, books = 0.0, {}
    for c in np.unique(labels):
        mask = labels == c
        v, x = best_mean_value(A[mask], charge, budget, groups, group_cap)
        value += mask.mean() * v
        books[c] = x
    return {"prior_value": prior, "with_information": float(value), "evpi": float(value - prior), "cells": books}


def evsi_signal(A, charge, budget, state, p_signal_given_state, groups=None, group_cap=None):
    """EVSI of an imperfect binary signal about a binary state (a request signs its agreement; it is in fact built).

    Parameters
    ----------
    A : numpy.ndarray
        Scenarios × candidates NPV.
    state : array-like of bool
        The true state in each scenario (the request operates within the window).
    p_signal_given_state : dict
        ``{True: P(signal | state), False: P(signal | not state)}`` from history.

    Returns
    -------
    dict
        ``prior_value``, ``with_information``, ``evsi``, ``p_signal`` and the
        books chosen after each signal.

    Notes
    -----
    Preposterior analysis on the scenarios: after a signal, every scenario
    is reweighted by the likelihood of that signal in its state, and the best
    book is chosen on the reweighted means. The EVSI is the probability-
    weighted value of the two posterior books less the prior book's value.
    It lies between zero and the EVPI of the state.
    """
    state = np.asarray(state, bool)
    prior, _ = best_mean_value(A, charge, budget, groups, group_cap)
    like = {True: np.where(state, p_signal_given_state[True], p_signal_given_state[False])}
    like[False] = 1.0 - like[True]
    value, books, p_sig = 0.0, {}, {}
    for signal in (True, False):
        weight = like[signal]
        p = float(weight.mean())
        p_sig[signal] = p
        if p <= 0:
            continue
        v, x = best_mean_value(A, charge, budget, groups, group_cap, weights=weight)
        value += p * v
        books[signal] = x
    return {"prior_value": prior, "with_information": float(value), "evsi": float(value - prior), "p_signal": p_sig[True], "books": books}


def deciles(values, n=10):
    """Decile labels of a quantity across scenarios (the cells of a partial EVPI)."""
    return pd.qcut(np.asarray(values, float), n, labels=False, duplicates="drop")
