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
Used by: notebook 02 and notebook 04 part A (baseline predictor), notebook 06 part B (Cox refits);
``tests/test_survival_tools.py``.
"""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

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
        Number of resamples (500 in notebook 02 (part A)).
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


def expand_project_years(frame, max_years=None):
    """One row per project per year in the queue, for discrete-time hazard models.

    Parameters
    ----------
    frame : pandas.DataFrame
        Needs ``duration_years`` and ``event`` (0/1/2).
    max_years : int, optional
        Drop project-years beyond this year in the queue.

    Returns
    -------
    pandas.DataFrame
        ``project`` (index label in ``frame``), ``year_in_queue`` (1, 2, …)
        and ``outcome`` (0 stay, 1 operation, 2 withdrawal) — non-zero only in
        the year the project exits.

    Notes
    -----
    Year k covers (k − 1, k] years since the request. A project that exits
    contributes every year up to and including the year of its exit. A
    censored project contributes only the years it was watched in full: a
    partly observed last year would count as "survived" although the project
    might still have left before the year ended, which biases hazards down.
    """
    d = frame["duration_years"].to_numpy(dtype=float)
    e = frame["event"].to_numpy(dtype=int)
    n_rows = np.where(e > 0, np.ceil(d), np.floor(d)).astype(int)
    project = np.repeat(frame.index.to_numpy(), n_rows)
    year = np.concatenate([np.arange(1, n + 1) for n in n_rows]) if len(n_rows) else np.array([], int)
    last = np.cumsum(n_rows) - 1
    outcome = np.zeros(len(project), dtype=int)
    exits = (e > 0) & (n_rows > 0)
    outcome[last[exits]] = e[exits]
    rows = pd.DataFrame({"project": project, "year_in_queue": year, "outcome": outcome})
    if max_years is not None:
        rows = rows[rows["year_in_queue"] <= max_years]
    return rows.reset_index(drop=True)


def cif_from_hazards(h_operation, h_withdrawal):
    """Turn yearly cause-specific hazards into cumulative incidence by year.

    Parameters
    ----------
    h_operation, h_withdrawal : numpy.ndarray
        Shape (projects, years): probability of operating / withdrawing in
        year k given still in the queue at the start of year k.

    Returns
    -------
    tuple of numpy.ndarray
        CIF of operation and of withdrawal, same shape; column k − 1 is the
        probability of having exited that way by the end of year k.

    Notes
    -----
    CIF(t) = Σ_{k ≤ t} h_op(k) · Π_{j < k} (1 − h_op(j) − h_wd(j)) (PLAN.md §6).
    The product is the probability of still waiting at the start of year k.
    """
    staying = np.cumprod(1 - h_operation - h_withdrawal, axis=1)
    before = np.concatenate([np.ones((h_operation.shape[0], 1)), staying[:, :-1]], axis=1)
    return np.cumsum(before * h_operation, axis=1), np.cumsum(before * h_withdrawal, axis=1)


def baseline_cif(train, target, horizons, min_n=50):
    """The "industry average" predictor: Aalen–Johansen CIF of operation in the project's region × technology cell.

    Parameters
    ----------
    train : pandas.DataFrame
        Training requests with ``region``, ``tech``, ``duration_years``, ``event``.
    target : pandas.DataFrame
        Requests to predict for (needs ``region`` and ``tech``).
    horizons : list of int
        Years at which to report P(operation by t).
    min_n : int
        Cells with fewer training requests fall back to the region's curve.

    Returns
    -------
    pandas.DataFrame
        Index of ``target``, one column per horizon, plus ``cell`` saying
        which estimate was used ("region × technology" or "region").

    Notes
    -----
    This is what a developer or lender uses today: the historical completion
    rate of similar projects. Withdrawal dates do not enter the operation
    curve's risk sets in a way that changes it (notebook 03 shows stamped
    withdrawals leave it unchanged), so the cells use the dates as recorded.
    """
    cells, regions = {}, {}
    for (region, tech), part in train.groupby(["region", "tech"]):
        if len(part) >= min_n:
            cells[(region, tech)] = aalen_johansen(part["duration_years"], part["event"], horizons)["cif_operation"].to_numpy()
    for region, part in train.groupby("region"):
        regions[region] = aalen_johansen(part["duration_years"], part["event"], horizons)["cif_operation"].to_numpy()
    rows, used = [], []
    for region, tech in zip(target["region"], target["tech"]):
        if (region, tech) in cells:
            rows.append(cells[(region, tech)])
            used.append("region × technology")
        else:
            rows.append(regions[region])
            used.append("region")
    out = pd.DataFrame(rows, index=target.index, columns=horizons)
    out["cell"] = used
    return out


COX_TECH_LEVELS = ["Solar+Battery", "Wind", "Offshore Wind", "Battery", "Gas", "Other"]  # reference: Solar
COX_SIZE_LEVELS = ["<5", "5–<20", "100–<200", "200–<500", "≥500"]  # reference: 20–<100 MW
COX_SERVICE_LEVELS = ["ERIS", "missing"]  # reference: NRIS; NRIS/ERIS occurs only in SPP, outside Track A


def cox_design(frame):
    """Numeric design matrix for the Cox models (one row per request).

    Parameters
    ----------
    frame : pandas.DataFrame
        Track A rows with ``region``, ``tech``, ``size_regime``, ``service``,
        ``q_year``, ``congestion_gw`` and ``congestion_rank``.

    Returns
    -------
    pandas.DataFrame
        Indicator columns against the reference levels PJM, Solar, 20–<100 MW
        and NRIS; ``q_year_5`` (request year in 5-year units, 0 = 2010);
        ``log_congestion_gw`` (log of 1 + GW waiting at entry);
        ``congestion_rank`` (missing for a region's first request → 0.5).

    Notes
    -----
    Region enters as indicators, not strata: with ERCOT's delayed entry
    (decision #21) an ERCOT-only baseline would have almost nobody at risk in
    the first years, while a shared baseline lets ERCOT borrow its early-year
    shape from PJM and CAISO (decision #24). Size enters as regimes, so the
    20 MW step can show. The separate hybrid flag is left out because
    Solar+Battery already carries it.
    """
    X = pd.DataFrame(index=frame.index)
    for region in ["ERCOT", "CAISO"]:
        X[f"region_{region}"] = (frame["region"] == region).astype(float)
    for tech in COX_TECH_LEVELS:
        X[f"tech_{tech}"] = (frame["tech"] == tech).astype(float)
    for size in COX_SIZE_LEVELS:
        X[f"size_{size}"] = (frame["size_regime"].astype(str) == size).astype(float)
    for service in COX_SERVICE_LEVELS:
        X[f"service_{service}"] = (frame["service"] == service).astype(float)
    X["q_year_5"] = (frame["q_year"].astype(float) - 2010) / 5
    X["log_congestion_gw"] = np.log1p(frame["congestion_gw"].astype(float))
    X["congestion_rank"] = frame["congestion_rank"].astype(float).fillna(0.5)
    return X


def cause_specific_cif(model_operation, model_withdrawal, X, horizons, step=1 / 12):
    """CIF of operation from two cause-specific Cox models.

    Parameters
    ----------
    model_operation, model_withdrawal : lifelines.CoxPHFitter
        Fitted for operation (withdrawal censored) and for withdrawal.
    X : pandas.DataFrame
        Design rows to predict for.
    horizons : list of int
        Years at which to report.
    step : float
        Grid step in years for the integral.

    Returns
    -------
    pandas.DataFrame
        Index of ``X``, one column per horizon: P(operation by t).

    Notes
    -----
    CIF_op(t) = Σ S(t_{k−1}) · ΔΛ_op(t_k), with S = exp(−Λ_op − Λ_wd): a project
    can only start operating while it is still in the queue, so the
    operation hazard is weighted by the chance of not having left either way.
    """
    grid = np.arange(0, max(horizons) + step / 2, step)
    cum_op = model_operation.predict_cumulative_hazard(X, times=grid).to_numpy().T
    cum_wd = model_withdrawal.predict_cumulative_hazard(X, times=grid).to_numpy().T
    survival = np.exp(-(cum_op + cum_wd))
    before = np.concatenate([np.ones((len(X), 1)), survival[:, :-1]], axis=1)
    increment = np.diff(np.concatenate([np.zeros((len(X), 1)), cum_op], axis=1), axis=1)
    cif = np.cumsum(before * increment, axis=1)
    columns = [int(round(h / step)) for h in horizons]
    return pd.DataFrame(cif[:, columns], index=X.index, columns=horizons)


def fit_cause_specific_cox(frame, cause, penalizer, delayed=True):
    """One cause-specific Cox model (the other exit treated as censoring), as fitted in notebook 04 (part A).

    Parameters
    ----------
    frame : pandas.DataFrame
        Track A requests with the ``cox_design`` columns, ``duration_years``,
        ``event`` and ``entry_years``.
    cause : {"operation", "withdrawal"}
    penalizer : float
        Ridge penalty (notebook 04 (part A) tuned it on the 2016 cohort).
    delayed : bool
        ERCOT delayed entry (decision #21): requests that left before their
        entry time are dropped and the others enter the risk set late.

    Notes
    -----
    The same steps as the fit inside notebook 04 (part A), moved here so notebook 06 (part B)
    can refit Cox on entrants to 2015; notebook 06 (part B) checks that the refit
    reproduces notebook 04 (part A)'s predictions.
    """
    code = OPERATION if cause == "operation" else WITHDRAWAL
    data = cox_design(frame).assign(T=frame["duration_years"], E=(frame["event"] == code).astype(int),
                                    entry=frame["entry_years"] if delayed else 0.0)
    if delayed:
        data = data[data["T"] > data["entry"]]
        return CoxPHFitter(penalizer=penalizer).fit(data, "T", "E", entry_col="entry")
    return CoxPHFitter(penalizer=penalizer).fit(data.drop(columns="entry"), "T", "E")


def cif_from_cumulative_hazards(cum_op, cum_wd, grid, horizons):
    """CIF of operation from two cumulative-hazard matrices on a common time grid.

    Parameters
    ----------
    cum_op, cum_wd : numpy.ndarray
        Shape (requests, len(grid)): cumulative hazards of operation and of
        withdrawal at each grid time, starting at 0.
    grid : numpy.ndarray
        Increasing times in years, ``grid[0] == 0``.
    horizons : list of int
        Years at which to report.

    Notes
    -----
    The same arithmetic as ``cause_specific_cif``: CIF_op(t) = Σ S(t_{k−1}) ·
    ΔΛ_op(t_k) with S = exp(−Λ_op − Λ_wd). Kept separate so the Cox function
    that notebook 04 (parts A–C) and notebook 06 (part A) scored stays byte-for-byte as it was.
    """
    survival = np.exp(-(cum_op + cum_wd))
    before = np.concatenate([np.ones((cum_op.shape[0], 1)), survival[:, :-1]], axis=1)
    increment = np.diff(np.concatenate([np.zeros((cum_op.shape[0], 1)), cum_op], axis=1), axis=1)
    cif = np.cumsum(before * increment, axis=1)
    columns = [int(np.searchsorted(grid, h)) for h in horizons]
    return cif[:, columns]


def _step_on_grid(model, X, grid):
    """A forest's cumulative hazard functions evaluated on ``grid`` (right-continuous steps)."""
    curves = model.predict_cumulative_hazard_function(X, return_array=True)
    times = model.unique_times_
    idx = np.searchsorted(times, grid, side="right") - 1
    out = np.where(idx[None, :] >= 0, curves[:, np.clip(idx, 0, len(times) - 1)], 0.0)
    return out


def fit_rsf_pair(frame, min_samples_leaf, n_estimators=300, seed=0):
    """Two cause-specific random survival forests (operation; withdrawal) on the Cox design.

    Parameters
    ----------
    frame : pandas.DataFrame
        Track A requests with the ``cox_design`` columns, ``duration_years``,
        ``event`` and ``entry_years``.
    min_samples_leaf : int
        The one tuned setting (chosen on the 2016 cohort in notebook 06 (part B)).
    n_estimators, seed : int
        Fixed in the protocol.

    Returns
    -------
    dict
        ``operation`` and ``withdrawal`` forests and the ``design`` columns.

    Notes
    -----
    A random survival forest cannot take left-truncated rows, so the ERCOT
    requests that enter the Cox fit with a delayed entry (``entry_years`` > 0,
    732 of the 5,298 entrants to 2016) are left out of the forest's fit.
    Each forest treats the other exit as censoring, as the Cox pair does.
    """
    from sksurv.ensemble import RandomSurvivalForest
    from sksurv.util import Surv

    rows = frame[frame["entry_years"] <= 0]
    X = cox_design(rows)
    out = {"design": list(X.columns)}
    for cause, code in [("operation", 1), ("withdrawal", 2)]:
        y = Surv.from_arrays(event=(rows["event"] == code).to_numpy(), time=rows["duration_years"].to_numpy())
        out[cause] = RandomSurvivalForest(n_estimators=n_estimators, min_samples_leaf=min_samples_leaf,
                                          max_features="sqrt", n_jobs=4, random_state=seed).fit(X, y)
    return out


def rsf_cif(fitted, target, horizons, step=1 / 12):
    """P(operation by each horizon) for ``target`` from a fitted forest pair."""
    X = cox_design(target)[fitted["design"]]
    grid = np.arange(0, max(horizons) + step / 2, step)
    cum_op = _step_on_grid(fitted["operation"], X, grid)
    cum_wd = _step_on_grid(fitted["withdrawal"], X, grid)
    cif = cif_from_cumulative_hazards(cum_op, cum_wd, grid, horizons)
    return pd.DataFrame(cif, index=target.index, columns=horizons)

