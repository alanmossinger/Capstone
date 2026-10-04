"""Non-parametric survival estimates with competing risks, and their bootstrap bands.

What: the Aalen–Johansen estimator of the cumulative incidence of operation
and of withdrawal (and, from the same pass, the Kaplan–Meier probability of
still being in the queue), evaluated on a fixed time grid; a bootstrap that
resamples projects to put bands around those curves; and a helper that runs
both for every group of a table.
Why: a project leaves the queue in one of two ways, so "1 − Kaplan–Meier for
operation" would overstate completion by treating withdrawals as censored.
Aalen–Johansen splits the exits correctly. The estimator is written out in
numpy (a few lines, checked against lifelines in the tests) because the
bootstrap refits it tens of thousands of times.
Reads / writes: nothing.
Used by: notebooks 03 and 05 (baseline predictor); ``tests/test_survival_tools.py``.
"""

import numpy as np
import pandas as pd

from src.events import OPERATION, WITHDRAWAL


def aalen_johansen(durations, events, times):
    """Cumulative incidence of operation and withdrawal, and survival, at given times.

    Parameters
    ----------
    durations : array-like
        Years from request to exit or censoring (positive).
    events : array-like of int
        0 censored, 1 operation, 2 withdrawal.
    times : array-like
        Times (years) at which to evaluate the step functions.

    Returns
    -------
    pandas.DataFrame
        ``time``, ``cif_operation``, ``cif_withdrawal`` and ``survival``
        (share still in the queue); the three add up to 1.

    Notes
    -----
    At each distinct time t_j with n_j projects at risk and d_1j, d_2j
    exits: S(t_j) = S(t_j−1)·(1 − (d_1j + d_2j)/n_j) and
    CIF_k(t_j) = CIF_k(t_j−1) + S(t_j−1)·d_kj/n_j. Projects censored at t_j
    are counted at risk at t_j, the usual convention. With one cause this is
    1 − Kaplan–Meier.
    """
    d = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=int)
    order = np.argsort(d, kind="stable")
    d, e = d[order], e[order]
    unique, first = np.unique(d, return_index=True)
    at_risk = len(d) - first
    position = np.searchsorted(unique, d)
    d1 = np.bincount(position[e == OPERATION], minlength=len(unique))
    d2 = np.bincount(position[e == WITHDRAWAL], minlength=len(unique))
    survival = np.cumprod(1 - (d1 + d2) / at_risk)
    before = np.concatenate([[1.0], survival[:-1]])
    cif1 = np.cumsum(before * d1 / at_risk)
    cif2 = np.cumsum(before * d2 / at_risk)

    times = np.asarray(times, dtype=float)
    index = np.searchsorted(unique, times, side="right") - 1

    def step(values, start):
        # value of the step function at each requested time; `start` before the first exit
        return np.where(index >= 0, values[np.clip(index, 0, None)], start)

    return pd.DataFrame({"time": times, "cif_operation": step(cif1, 0.0),
                         "cif_withdrawal": step(cif2, 0.0), "survival": step(survival, 1.0)})


def bootstrap_bands(durations, events, times, n_boot=500, seed=0, level=0.95):
    """Percentile bootstrap bands for the three curves of ``aalen_johansen``.

    Parameters
    ----------
    durations, events, times
        As in ``aalen_johansen``.
    n_boot : int
        Number of resamples (500 in notebook 03).
    seed : int
        Seed for the random generator, so bands reproduce exactly.
    level : float
        Coverage of the band.

    Returns
    -------
    pandas.DataFrame
        ``time`` and ``<curve>_low`` / ``<curve>_high`` for each curve.

    Notes
    -----
    Projects are resampled with replacement, which keeps each project's
    duration and outcome together. Percentile bands need no variance
    formula and stay inside [0, 1].
    """
    d = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=int)
    rng = np.random.default_rng(seed)
    curves = ["cif_operation", "cif_withdrawal", "survival"]
    draws = {c: np.empty((n_boot, len(times))) for c in curves}
    for b in range(n_boot):
        idx = rng.integers(0, len(d), len(d))
        fit = aalen_johansen(d[idx], e[idx], times)
        for c in curves:
            draws[c][b] = fit[c].to_numpy()
    tail = (1 - level) / 2
    out = {"time": np.asarray(times, dtype=float)}
    for c in curves:
        out[f"{c}_low"] = np.quantile(draws[c], tail, axis=0)
        out[f"{c}_high"] = np.quantile(draws[c], 1 - tail, axis=0)
    return pd.DataFrame(out)


def curves_by_group(frame, by, times, n_boot=500, seed=0, min_n=1):
    """Aalen–Johansen curves with bootstrap bands for every group of ``frame``.

    Parameters
    ----------
    frame : pandas.DataFrame
        Needs ``duration_years`` and ``event``.
    by : str or list of str
        Grouping columns.
    times : array-like
        Evaluation grid (years).
    n_boot : int
        Bootstrap resamples per group.
    seed : int
        Base seed; each group gets its own seed derived from it.
    min_n : int
        Groups smaller than this are skipped.

    Returns
    -------
    pandas.DataFrame
        Long table: group columns, ``n``, ``time``, the three curves and
        their bands.
    """
    keys = [by] if isinstance(by, str) else list(by)
    pieces = []
    for i, (group, part) in enumerate(frame.groupby(keys, observed=True)):
        if len(part) < min_n:
            continue
        fit = aalen_johansen(part["duration_years"], part["event"], times)
        bands = bootstrap_bands(part["duration_years"], part["event"], times,
                                n_boot=n_boot, seed=seed + i)
        piece = fit.merge(bands, on="time")
        for key, value in zip(keys, group if isinstance(group, tuple) else (group,)):
            piece[key] = value
        piece["n"] = len(part)
        pieces.append(piece)
    result = pd.concat(pieces, ignore_index=True)
    return result[keys + ["n"] + [c for c in result.columns if c not in keys + ["n"]]]
