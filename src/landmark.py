"""Landmark predictions: P(operation within h years of a later decision point), from the discrete-time models.

What: the risk set of requests still in the queue at a landmark L (one, two
years after the request, or the executed interconnection agreement), the
prediction rows from L onward with the covariates updated to what is known
at L (queue congestion on that day, whether an agreement has been
executed), the conditional cumulative incidence from L, and the shifted
outcomes to score it with.
Why: a portfolio is managed at milestones, not at entry. The discrete-time
hazard models of notebook 04 (part B) already describe every year in the queue, so a
landmark prediction is the same model read from year k + 1 on, with the
time-varying covariates set to their value at L rather than frozen at entry
— and only information dated before L is used (criterion C12).
Reads / writes: nothing.
Used by: notebook 04 (part J); ``tests/test_landmark.py``.
"""

import numpy as np
import pandas as pd

from src import discrete_time, survival_tools


def ia_before_year(rows, frame, ia_dates):
    """1.0 when the request's agreement was executed before the start of the project-year, else 0.0.

    Parameters
    ----------
    rows : pandas.DataFrame
        ``project`` (row label in ``frame``) and ``year_in_queue``.
    frame : pandas.DataFrame
        Requests with ``q_date``.
    ia_dates : pandas.Series
        Executed-agreement date per request (index = row label in
        ``frame``), NaT where none is dated.

    Notes
    -----
    Year k starts (k − 1) years after the request; an agreement dated on or
    after that day is not yet known in year k. A request without a dated
    agreement is 0 in every year, which also covers the regions whose
    agreement dates the public file lacks — the flag means "known to be
    executed", not "not executed".
    """
    project = rows["project"].to_numpy()
    start = discrete_time.year_start_dates(frame.loc[project, "q_date"], rows["year_in_queue"]).to_numpy()
    ia = ia_dates.reindex(project).to_numpy(dtype="datetime64[ns]")
    return pd.Series(((~pd.isna(ia)) & (ia < start)).astype(float), index=rows.index)


def ia_extra(frame, ia_dates):
    """The ``extra`` callable for ``discrete_time.fit_both``: adds ``ia_before`` to LightGBM's design."""
    def extra(rows):
        return pd.DataFrame({"ia_before": ia_before_year(rows, frame, ia_dates)}, index=rows.index)
    return extra


def risk_set(frame, k):
    """Requests still in the queue k full years after the request (and past ERCOT's delayed entry)."""
    return (frame["duration_years"].to_numpy() > k) & (frame["entry_years"].to_numpy() <= k)


def landmark_rows(target, clean, k, ia_dates=None, update_congestion=True, update_ia=True, max_years=discrete_time.MAX_YEARS):
    """Prediction rows for years k + 1 … ``max_years`` of each request, as known at the landmark.

    Parameters
    ----------
    target : pandas.DataFrame
        Requests in the risk set at k (entry-time features, ``q_date``).
    clean : pandas.DataFrame
        Full clean table (congestion is counted in it).
    k : int
        Landmark, in full years after the request.
    ia_dates : pandas.Series, optional
        Agreement dates; needed when the fitted model carries ``ia_before``.
    update_congestion : bool
        True: congestion on the first day of year k + 1, held for the later
        years; False: frozen at entry, as the entry predictions have it.
    update_ia : bool
        True: the agreement flag as of the first day of year k + 1; False:
        no agreement known (the entry model's view).

    Returns
    -------
    pandas.DataFrame
        Rows in ``discrete_time.prediction_rows`` layout, years k + 1 … max.

    Notes
    -----
    Holding the landmark values for the later years is the same persistence
    forecast the entry predictions use; the landmark only moves the day the
    forecast is made. Nothing dated after the first day of year k + 1 enters.
    """
    years = np.tile(np.arange(k + 1, max_years + 1), len(target))
    rows = pd.DataFrame({"project": np.repeat(target.index.to_numpy(), max_years - k), "year_in_queue": years})
    out = discrete_time.attach_features(rows, target)
    at_landmark = rows.copy()
    at_landmark["year_in_queue"] = k + 1
    if update_congestion:
        out["congestion_gw"] = discrete_time.yearly_congestion(at_landmark, target, clean)
    else:
        out["congestion_gw"] = target.loc[rows["project"], "congestion_gw"].to_numpy(dtype=float)
    if ia_dates is not None:
        out["ia_before"] = ia_before_year(at_landmark, target, ia_dates).to_numpy() if update_ia else 0.0
    out["log_congestion_gw"] = np.log1p(out["congestion_gw"])
    return out


def conditional_cif(h_operation, h_withdrawal, n_requests, horizons):
    """P(operation within h years of the landmark) from the hazards of the years after it.

    Notes
    -----
    The request is in the queue at the landmark with probability 1, so the
    incidence restarts there: ``survival_tools.cif_from_hazards`` on the
    years after L, read at the h-th of them.
    """
    h_op = np.asarray(h_operation).reshape(n_requests, -1)
    h_wd = np.asarray(h_withdrawal).reshape(n_requests, -1)
    cif_op, _ = survival_tools.cif_from_hazards(h_op, h_wd)
    return pd.DataFrame({h: cif_op[:, h - 1] for h in horizons})


def predict_at_landmark(fitted, target, clean, k, horizons, ia_dates=None, update_congestion=True, update_ia=True):
    """LightGBM's P(operation within h of landmark k) for every request of ``target``.

    Parameters
    ----------
    fitted : dict
        ``discrete_time.fit_both`` output (with or without the ``ia_before`` extra).
    target : pandas.DataFrame
        Requests in the risk set at k.
    clean, k, horizons, ia_dates, update_congestion, update_ia :
        As in ``landmark_rows``; ``ia_dates`` is required when the fit
        carries the agreement flag.

    Returns
    -------
    pandas.DataFrame
        Index of ``target``, one column per horizon.
    """
    rows = landmark_rows(target, clean, k, ia_dates, update_congestion, update_ia)
    _, rows = discrete_time.encode_state(fitted["rows"], [rows])
    X = discrete_time.lgbm_design(rows)
    if fitted["extra"] is not None:
        X = X.join(pd.DataFrame({"ia_before": rows["ia_before"].to_numpy()}, index=rows.index))
    h_op, h_wd = discrete_time.predict_hazards(fitted["lgbm"], X)
    out = conditional_cif(h_op, h_wd, len(target), horizons)
    out.index = target.index
    return out


def shifted_outcomes(frame, k, censor_date, days_per_year):
    """Time-to-event data measured from the landmark: durations − k, the same events, follow-up − k."""
    durations = frame["duration_years"].to_numpy() - k
    follow_up = ((pd.Timestamp(censor_date) - frame["q_date"]).dt.days / days_per_year).to_numpy() - k
    return durations, frame["event"].to_numpy(), follow_up


def fair_baseline_at_landmark(train, target, k, horizons):
    """The fair baseline conditional on being in the queue at k: its cells refitted on the shifted training data."""
    at_risk = train[risk_set(train, k)].copy()
    at_risk["duration_years"] = at_risk["duration_years"] - k
    from src import baselines  # local import: baselines does not depend on this module
    return baselines.fair_baseline_cif(at_risk, target, horizons)


def agreement_known_at(frame, k, ia_dates):
    """True when the request's agreement is dated before the first day of year k + 1 (known at landmark k)."""
    rows = pd.DataFrame({"project": frame.index.to_numpy(), "year_in_queue": k + 1}, index=frame.index)
    return ia_before_year(rows, frame, ia_dates).astype(bool)


def agreement_lookup_at_landmark(train, target, k, horizons, ia_dates):
    """The lookup an analyst builds at a landmark when the agreement status is known: fair-baseline cells split by it.

    Parameters
    ----------
    train, target : pandas.DataFrame
        Training requests and requests to predict for, with the fair
        baseline's columns and ``q_date``.
    k : int
        Landmark, in full years after the request.
    horizons : list of int
        Years after the landmark.
    ia_dates : pandas.Series
        Agreement dates by row label (NaT where none is dated).

    Returns
    -------
    pandas.DataFrame
        Index of ``target``, one column per horizon, ``cell`` and
        ``agreement_known``.

    Notes
    -----
    The comparator a careful analyst could build with the same dated
    information the landmark model has: region × technology × size-band
    incidence from the landmark on, fitted separately on the training
    requests with and without an agreement known at the landmark, with the
    usual fallback to coarser cells (decision #58). Without it, a model that
    beats the plain lookup at a landmark may only be using the agreement
    flag, which a table can use as well.
    """
    at_risk = train[risk_set(train, k)]
    known_train = agreement_known_at(at_risk, k, ia_dates)
    known_target = agreement_known_at(target, k, ia_dates)
    out = []
    for flag in (True, False):
        part = target[known_target == flag]
        if len(part):
            pred = fair_baseline_at_landmark(at_risk[known_train == flag], part, k, horizons)
            pred["agreement_known"] = flag
            out.append(pred)
    return pd.concat(out).reindex(target.index)
