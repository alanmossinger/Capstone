"""The queue as seen on one decision date: which requests are still live, and their chance of operating from there.

What: censor the request table at a date (outcomes after it unknown), fit the
landmark hazard model on what was known then, and give every request still
waiting on that date its cumulative chance of operating within 1 … 7 years,
conditional on having survived to its current age in the queue.
Why: report v6 valued twenty ERCOT requests that entered in 2017–2019 as if
they were live in 2025, though ten had already been withdrawn or built
(audit E1). Decision #90 sets one decision date for both sectors, 1 January
2025; the same functions run as of 1 January 2020 give a backtest scored on
2020–2024 outcomes, and its observed-to-predicted ratio is a level correction
that was knowable on the decision date (audit E4).
The same date governs the leases and the agreements: lease history stops at
the last month BSEE had published (the release lag of ``config.RELEASE_LAGS``),
and an agreement counts only if the edition frozen at the date dates it — the
2026 edition's backfilled dates are later information (decision #94).
Reads / writes: nothing; notebook 04 passes the tables in and saves
`data/processed/predictions_2025.parquet` and `results/decision_date_backtest.csv`.
Used by: notebook 04 (part L), notebooks 07–11 and `src/whatif.py` (the lease history and baselines);
`tests/test_decision_date.py`.
"""

import numpy as np
import pandas as pd

from src import config, discrete_time, economics as ec, landmark

LEASE_LAG = config.RELEASE_LAGS["BSEE OGOR-A"]  # months between a production month and BSEE publishing it
AGREEMENT_EDITION = "2025 edition"  # the LBNL edition that was the latest public record of the queue on the decision date


def censor_at(frame, as_of):
    """The request table as it looked on ``as_of``: later entrants dropped, later exits not yet known.

    Parameters
    ----------
    frame : pandas.DataFrame
        Track A requests with ``q_date``, ``exit_date``, ``event`` and ``duration_years``.
    as_of : str or pandas.Timestamp
        The decision date.

    Returns
    -------
    pandas.DataFrame
        Requests that entered before ``as_of``; an exit after ``as_of`` becomes
        a censored stay (event 0) with the duration measured to ``as_of``.

    Notes
    -----
    Only the outcome columns change. Entry-time features are known at entry,
    and the yearly congestion and agreement flags of the hazard rows are read
    on the first day of each project-year, which for every kept row falls
    before ``as_of``, so nothing dated later enters a fit made on this table.
    """
    as_of = pd.Timestamp(as_of)
    out = frame[frame["q_date"] < as_of].copy()
    later = out["exit_date"].isna() | (out["exit_date"] > as_of)
    out.loc[later, "event"] = 0
    out.loc[later, "duration_years"] = (as_of - out.loc[later, "q_date"]).dt.days / config.DAYS_PER_YEAR
    return out


def live_on(frame, as_of):
    """Requests still waiting on ``as_of`` (entered before it, no exit on or before it).

    Notes
    -----
    A request still open at the end of the file carries ``event`` 0 and the
    censoring date as its ``exit_date``; it is waiting on any later date.
    """
    as_of = pd.Timestamp(as_of)
    waiting = (frame["q_date"] < as_of) & ((frame["event"] == 0) | frame["exit_date"].isna() | (frame["exit_date"] > as_of))
    return frame[waiting].copy()


def age_in_queue(frame, as_of):
    """Full years each request has waited by ``as_of``."""
    return np.floor((pd.Timestamp(as_of) - frame["q_date"]).dt.days / config.DAYS_PER_YEAR).astype(int)


def conditional_curves(fitted_agreement, fitted_plain, target, clean, as_of, ia_dates, years=7, max_years=discrete_time.MAX_YEARS, q_year_cap=None):
    """Cumulative P(operation within 1 … ``years`` of ``as_of``) for each live request, from its own age.

    Parameters
    ----------
    fitted_agreement : dict
        ``discrete_time.fit_both`` output with the agreement flag (``landmark.ia_extra``).
    fitted_plain : dict
        The same fit without the flag.
    target : pandas.DataFrame
        Requests live on ``as_of``.
    clean : pandas.DataFrame
        The full clean table (congestion is counted in it).
    as_of : str or pandas.Timestamp
        The decision date.
    ia_dates : pandas.Series
        Agreement dates by row label.
    years : int
        Horizon of the curve.
    max_years : int
        Last year in the queue the hazard model covers.
    q_year_cap : int, optional
        The request year a prediction reads is capped here; by default the
        last entry year whose five-year outcomes were complete on ``as_of``
        (``as_of`` year − 6).

    Returns
    -------
    pandas.DataFrame
        Index of ``target``; columns ``age``, ``agreement_known``, ``model``
        and ``p1`` … ``p<years>``.

    Notes
    -----
    A request ``k`` full years old is predicted from its landmark at ``k``:
    the hazards of queue years k + 1 … ``max_years``, congestion as of the
    first day of year k + 1. A request with an executed agreement by then is
    read with the agreement model, whose flag stays 1 in later years as a
    signed agreement does. A request without one is read with the plain
    model: the agreement model would hold its flag at 0 for every later year,
    as if no agreement could ever come, and a fifth queue year without one
    almost never ends in operation, so its seven-year curve went flat after
    year three (found while building this view; the 2018 and 2020 backtests
    in notebook 04 score the rule). The hazard models were never fitted beyond
    ``max_years`` in the queue, so the curve is held flat after it — no
    operation after ten years of waiting (ASSUMED; rare in the file).

    The request year is a feature of the hazard model, and no cohort newer
    than ``q_year_cap`` had been watched past its first years on the
    decision date. Read at its own year, a 2024 request got a withdrawal
    hazard of 0.73 in its first year and 0.97 by its third, against 0.02–0.06
    observed for recent ERCOT solar: the trees extrapolate the year into
    near-certain withdrawal. The prediction therefore reads the request
    year at most at the cap; the level that newer cohorts actually reach is
    handled by the backtest's level correction (notebook 04 part L).
    """
    as_of = pd.Timestamp(as_of)
    cap = as_of.year - 6 if q_year_cap is None else q_year_cap
    target = target.assign(q_year=target["q_year"].clip(upper=cap))
    ages = age_in_queue(target, as_of).clip(lower=0)
    known = ia_dates.reindex(target.index)
    # signed before the first day of year k + 1, the day the landmark rows read the flag, so the two agree
    landmark_day = discrete_time.year_start_dates(target["q_date"], ages.to_numpy() + 1)
    signed = (known.notna().to_numpy() & (known.to_numpy(dtype="datetime64[ns]") < landmark_day.to_numpy()))
    cols = [f"p{h}" for h in range(1, years + 1)]
    out = pd.DataFrame(0.0, index=target.index, columns=cols)
    for k in np.unique(ages):
        if k >= max_years:
            continue
        horizons = list(range(1, min(years, max_years - int(k)) + 1))
        for has_agreement in (True, False):
            mask = (ages.to_numpy() == k) & (signed == has_agreement)
            if not mask.any():
                continue
            part = target[mask]
            if has_agreement:
                pred = landmark.predict_at_landmark(fitted_agreement, part, clean, int(k), horizons, ia_dates, update_congestion=True, update_ia=True)
            else:
                pred = landmark.predict_at_landmark(fitted_plain, part, clean, int(k), horizons, None, update_congestion=True, update_ia=False)
            values = pred[horizons].to_numpy(dtype=float)
            if len(horizons) < years:
                values = np.hstack([values, np.repeat(values[:, -1:], years - len(horizons), axis=1)])
            out.loc[part.index, cols] = np.maximum.accumulate(np.clip(values, 0.0, 1.0), axis=1)
    out.insert(0, "age", ages.to_numpy())
    out.insert(1, "agreement_known", signed)
    out.insert(2, "model", np.where(signed, "agreement model", "plain model"))
    return out


def observed_within(frame, as_of, years):
    """1 when a request live on ``as_of`` operated within ``years`` of it, by the uncensored outcomes."""
    as_of = pd.Timestamp(as_of)
    limit = as_of + pd.to_timedelta(round(years * config.DAYS_PER_YEAR), unit="D")
    return ((frame["event"] == 1) & (frame["exit_date"] <= limit)).astype(int)


def lookup_curves(known, target, as_of, years=7, group=("region", "type_clean"), max_years=discrete_time.MAX_YEARS, min_at_risk=20):
    """The transparent benchmark: a life table of earlier requests, by region and technology, read from each request's age.

    Parameters
    ----------
    known : pandas.DataFrame
        Requests as known on ``as_of`` (``censor_at``): ``duration_years``, ``event``, ``entry_years`` and the group columns.
    target : pandas.DataFrame
        Requests live on ``as_of``.
    as_of : str or pandas.Timestamp
        The decision date.
    years : int
        Horizon of the curve.
    group : tuple of str
        Columns that define a cell; a cell with fewer than ``min_at_risk``
        requests at risk in a queue year falls back to the region's table.
    max_years : int
        Last queue year counted; the curve is flat after it, as the model's.

    Returns
    -------
    pandas.DataFrame
        Index of ``target``; ``p1`` … ``p<years>``.

    Notes
    -----
    Queue year y covers (y − 1, y] years since the request. Its operation
    and withdrawal hazards are the shares of requests at risk at its start
    (still waiting, past their delayed entry) that left that way during it.
    From age k the curve is the Aalen–Johansen sum
    Σ S(y − 1) h_op(y) over y = k + 1 … k + j, with S the share still waiting.
    This is what a careful analyst computes by hand, and what the machine-
    learning curve must beat to matter (the "lookup" of the report).
    """
    d = known["duration_years"].to_numpy(float)
    e = known["event"].to_numpy()
    entry = known["entry_years"].to_numpy(float)
    cells = known[list(group)].astype(str).agg("|".join, axis=1).to_numpy()
    regions = known[group[0]].astype(str).to_numpy()

    def hazards(mask):
        h_op, h_wd, n = np.zeros(max_years), np.zeros(max_years), np.zeros(max_years)
        for y in range(1, max_years + 1):
            at_risk = mask & (d > y - 1) & (entry <= y - 1)
            n[y - 1] = at_risk.sum()
            if n[y - 1] > 0:
                inside = at_risk & (d <= y)
                h_op[y - 1] = (inside & (e == 1)).sum() / n[y - 1]
                h_wd[y - 1] = (inside & (e == 2)).sum() / n[y - 1]
        return h_op, h_wd, n

    tables = {}
    ages = age_in_queue(target, as_of).clip(lower=0).to_numpy()
    t_cells = target[list(group)].astype(str).agg("|".join, axis=1).to_numpy()
    t_regions = target[group[0]].astype(str).to_numpy()
    out = np.zeros((len(target), years))
    for i, (cell, region, k) in enumerate(zip(t_cells, t_regions, ages)):
        if cell not in tables:
            tables[cell] = hazards(cells == cell)
        if region not in tables:
            tables[region] = hazards(regions == region)
        h_op, h_wd, n = tables[cell]
        r_op, r_wd, _ = tables[region]
        thin = n < min_at_risk
        h_op, h_wd = np.where(thin, r_op, h_op), np.where(thin, r_wd, h_wd)
        survive, cif = 1.0, 0.0
        for j in range(years):
            y = k + j + 1
            if y <= max_years:
                cif += survive * h_op[y - 1]
                survive *= 1.0 - h_op[y - 1] - h_wd[y - 1]
            out[i, j] = cif
    return pd.DataFrame(out, index=target.index, columns=[f"p{h}" for h in range(1, years + 1)])


def lease_history_on(upstream, as_of=config.DECISION_DATE, lag=LEASE_LAG):
    """The lease months BSEE had published by ``as_of``.

    Parameters
    ----------
    upstream : pandas.DataFrame
        Monthly lease rows with a ``month`` column (``data/interim/upstream_monthly.parquet``).
    as_of : str or pandas.Timestamp
        The decision date.
    lag : int
        Months between a production month and its publication.

    Returns
    -------
    pandas.DataFrame
        The rows whose production month is earlier than ``as_of`` minus ``lag`` months.

    Notes
    -----
    On 1 January 2025 the last published month was September 2024; the first
    v8 run read through December 2024, three months no committee could have
    seen (review of 19 October, §2.1). The files as served in 2026 also carry
    later revisions of the published months, which cannot be undone without
    archived copies; the report states it.
    """
    cutoff = pd.Timestamp(as_of) - pd.DateOffset(months=lag)
    return upstream[upstream["month"] < cutoff]


def lease_baseline_on(history_oil, history_gas, months, gap=LEASE_LAG, **kwargs):
    """A lease's baseline from its published history, started at the decision date.

    Parameters
    ----------
    history_oil, history_gas : array-like
        Monthly volumes up to the last published month, oldest first.
    months : int
        Forecast length from the decision date.
    gap : int
        Months between the last published month and the decision date.
    **kwargs
        Passed to ``economics.lease_baseline``.

    Returns
    -------
    tuple
        As ``economics.lease_baseline``, with the forecast starting at the decision date.

    Notes
    -----
    The decline fit sees only published months; its first ``gap`` forecast
    months fall before the decision date and are dropped, so month 0 of the
    baseline is month 0 of the price paths.
    """
    bo, bg, fo, fg = ec.lease_baseline(history_oil, history_gas, months=months + gap, **kwargs)
    return bo[gap:], bg[gap:], fo, fg


def agreement_dates_on(milestones, edition=AGREEMENT_EDITION):
    """Agreement dates a committee could read on the decision date, by project key.

    Parameters
    ----------
    milestones : pandas.DataFrame
        ``data/interim/milestones.parquet`` indexed by ``project_key``.
    edition : str
        The ``ia_source`` value of the edition public on the date.

    Returns
    -------
    pandas.Series
        ``ia_date_best`` where the agreement falls inside the request's time in the queue
        and the date comes from ``edition``; NaT otherwise.

    Notes
    -----
    The merged dates fill the 2025 edition's gaps from the 2026 edition
    (566 dates). That is right for the registered landmark tests, which score
    the past, and wrong for any view as of a date, which must use what was
    public then (review of 19 October, §2.1).
    """
    keep = milestones["ia_inside_queue"] & (milestones["ia_source"] == edition)
    return milestones["ia_date_best"].where(keep)



def candidates_as_of(frame, gis, as_of=config.DECISION_DATE, per_tech=5, min_mw=config.FERC_SIZE_STEP_MW,
                     technologies=("Gas CC", "Solar", "Wind", "Storage")):
    """The ERCOT candidates of a decision date from the records public that day: an LBNL edition's rows and ERCOT's monthly reports.

    Parameters
    ----------
    frame : pandas.DataFrame
        The requests of the edition public on ``as_of`` (``q_id``, ``region``,
        ``type_clean``, ``mw``, ``q_date``, ``exit_date``, ``event``; ``ia_date``
        when the edition has it).
    gis : pandas.DataFrame
        ERCOT's monthly GIS reports stacked (``iso_files.read_ercot_gis`` with a
        ``report_month``): ``q_id``, ``listed_as``, ``report_month`` and the dated
        fields it carries.
    as_of : str
        The decision date.
    per_tech : int
        How many of the largest live requests per technology become candidates.
    min_mw : float
        The size floor of the registered pool.

    Returns
    -------
    pandas.DataFrame
        The candidates: ``q_id``, ``type_clean``, ``mw``, ``q_date``,
        ``liveness_source`` ("GIS <month>" or "edition: no GIS record") and
        ``agreement_known`` (an agreement signed on or before ``as_of`` in a
        report before it, or in the edition).

    Notes
    -----
    The LBNL 2025 edition, which notebook 04 used for this view, was released
    in August 2025: a committee on 1 January 2025 had the 2024 edition (data
    through 2023) and ERCOT's monthly reports. A request is live if the latest
    report before ``as_of`` lists it as active; one listed as inactive or
    cancelled, or approved for energization, in any earlier report is not;
    one no report mentions falls back to the edition's own record, which is
    said in ``liveness_source``. The 2025 and 2026 editions supply outcome
    labels later, never this view (review of 21 October).
    """
    as_of = pd.Timestamp(as_of)
    pool = frame[(frame["region"] == "ERCOT") & (frame["q_date"] < as_of) & (frame["mw"] >= min_mw) & frame["type_clean"].isin(technologies)].copy()
    pool["q_id"] = pool["q_id"].astype(str).str.strip()
    before = gis[gis["report_month"] < as_of].copy()
    before["q_id"] = before["q_id"].astype(str).str.strip()
    latest_month = before["report_month"].max() if len(before) else pd.NaT
    latest = before[before["report_month"] == latest_month]
    active = set(latest.loc[latest["listed_as"].str.startswith("active"), "q_id"])
    dead = set(before.loc[before["listed_as"].isin(["inactive", "cancelled"]), "q_id"])
    if "energization_approved" in before:
        dead |= set(before.loc[before["energization_approved"] <= as_of, "q_id"])
    seen = set(before["q_id"])
    edition_live = (pool["event"] == 0) | pool["exit_date"].isna() | (pool["exit_date"] > as_of)
    in_gis = pool["q_id"].isin(seen)
    live = np.where(in_gis, pool["q_id"].isin(active) & ~pool["q_id"].isin(dead), edition_live)
    pool["liveness_source"] = np.where(in_gis, f"GIS {latest_month:%Y-%m}" if pd.notna(latest_month) else "GIS", "edition: no GIS record")
    signed = set()
    if "ia_signed" in before:
        signed |= set(before.loc[before["ia_signed"] <= as_of, "q_id"])
    if "ia_date" in pool:
        signed |= set(pool.loc[pool["ia_date"] <= as_of, "q_id"])
    pool["agreement_known"] = pool["q_id"].isin(signed)
    pool = pool[live]
    cols = ["q_id", "type_clean", "mw", "q_date", "liveness_source", "agreement_known"] + [c for c in ("project_key",) if c in pool]
    return (pool.sort_values("mw", ascending=False).groupby("type_clean", group_keys=False).head(per_tech)[cols].reset_index(drop=True))
