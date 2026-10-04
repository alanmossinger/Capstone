"""Entry-time features: what is known about a request on the day it enters the queue.

What: the size regime (with the FERC 20 MW step) and queue congestion at
entry — how many same-region requests, and how many GW, were already waiting
on that day.
Why: every feature must be computable on the request date, so the models
never learn from what happened later (decision #7). Congestion is the
mechanism Johnston, Liu & Yang (2023) point to: a crowded queue slows studies
and raises the chance of dropping out.
Reads / writes: nothing.
Used by: notebooks 03 (figure F8) and 04 (full feature table);
``tests/test_features.py``.
"""

import bisect

import numpy as np
import pandas as pd

from src import config

# Features the main models may use: all known on the request date.
MAIN_FEATURES = ["region", "state", "type_group", "hybrid", "log_mw", "size_regime", "service",
                 "q_year", "congestion_n", "congestion_gw", "congestion_rank"]
# Built but kept for the labelled leakage ablation only (decisions #7 and #22).
ABLATION_FEATURES = ["ambition_gap_years", "ambition_gap_missing"]
# Columns that describe what happened after entry; no main feature may be built from them.
POST_ENTRY_COLUMNS = ["q_status", "on_date", "wd_date", "ia_date", "IA_status_raw",
                      "IA_status_clean", "prop_date", "prop_year"]


def size_regime(mw):
    """Bin capacity into the regimes of PLAN.md §7 (right-open MW bins).

    Parameters
    ----------
    mw : pandas.Series
        Requested capacity in MW.

    Returns
    -------
    pandas.Series
        Ordered categorical: <5, 5–<20, 20–<100, 100–<200, 200–<500, ≥500.

    Notes
    -----
    Right-open bins put a 20 MW request on the large-generator side, as the
    FERC small/large generator rules do.
    """
    return pd.cut(mw, bins=config.SIZE_BINS, labels=config.SIZE_LABELS, right=False)


def congestion_at_entry(frame):
    """Requests and GW already waiting in the same region on each request's entry date.

    Parameters
    ----------
    frame : pandas.DataFrame
        Clean table with ``region``, ``q_date``, ``mw``, ``q_status``,
        ``on_date`` and ``wd_date``.

    Returns
    -------
    pandas.DataFrame
        Same index as ``frame``: ``congestion_n`` and ``congestion_gw``
        (missing where the request date is missing).

    Notes
    -----
    A request counts as waiting on day t if it entered strictly before t and
    had not left before t. It leaves on its operation date if operational
    and on its withdrawal date if withdrawn; with no exit date it is treated
    as still waiting (PLAN.md §7), which overstates congestion where exit
    dates are missing. Because every exit follows its entry (rules R3–R4),
    "entered before t" minus "left before t" counts exactly the waiting
    requests, so a sorted sweep with ``searchsorted`` does the whole region
    at once instead of comparing every pair of requests (see
    ``congestion_on_dates``). Only information dated before t is used, and a
    request never counts itself because it enters on t, not before.
    """
    known = frame["q_date"].notna()
    out = pd.DataFrame(index=frame.index, columns=["congestion_n", "congestion_gw"], dtype=float)
    swept = congestion_on_dates(frame, frame.loc[known, "region"], frame.loc[known, "q_date"])
    out.loc[known, ["congestion_n", "congestion_gw"]] = swept.to_numpy()
    return out


def congestion_on_dates(frame, regions, dates):
    """Requests and GW waiting in a region on arbitrary dates (for time-varying congestion).

    Parameters
    ----------
    frame : pandas.DataFrame
        Clean table (as for ``congestion_at_entry``).
    regions : array-like of str
        Region of each query.
    dates : array-like of datetime64
        Date of each query.

    Returns
    -------
    pandas.DataFrame
        ``congestion_n`` and ``congestion_gw`` for each query, in input order.

    Notes
    -----
    Same rule as ``congestion_at_entry``: a request is waiting on day t if it
    entered before t and had not left before t. Notebook 06 asks this for the
    first day of every project-year; a project counts itself there, so the
    caller subtracts it. Only information dated before t is used.
    """
    exit_date = frame["on_date"].where(frame["q_status"] == "operational",
                                       frame["wd_date"].where(frame["q_status"] == "withdrawn"))
    regions = np.asarray(regions)
    dates = np.asarray(dates, dtype="datetime64[ns]")
    n_out = np.full(len(dates), np.nan)
    gw_out = np.full(len(dates), np.nan)
    for region in np.unique(regions):
        part = frame[(frame["region"] == region) & frame["q_date"].notna()]
        entry_order = np.argsort(part["q_date"].to_numpy(), kind="stable")
        entry_sorted = part["q_date"].to_numpy()[entry_order]
        entry_gw = np.concatenate([[0.0], np.cumsum(part["mw"].to_numpy()[entry_order]) / 1000])
        exits = exit_date.loc[part.index]
        has_exit = exits.notna().to_numpy()
        exit_values = exits.to_numpy()[has_exit]
        exit_order = np.argsort(exit_values, kind="stable")
        exit_sorted = exit_values[exit_order]
        exit_gw = np.concatenate([[0.0], np.cumsum(part["mw"].to_numpy()[has_exit][exit_order]) / 1000])
        query = regions == region
        entered = np.searchsorted(entry_sorted, dates[query], side="left")
        left = np.searchsorted(exit_sorted, dates[query], side="left")
        n_out[query] = entered - left
        gw_out[query] = entry_gw[entered] - exit_gw[left]
    return pd.DataFrame({"congestion_n": n_out, "congestion_gw": gw_out})


def congestion_rank(frame, congestion_gw):
    """Where a request's congestion sits among all earlier same-region requests (0–1).

    Parameters
    ----------
    frame : pandas.DataFrame
        Needs ``region`` and ``q_date``.
    congestion_gw : pandas.Series
        Output column of ``congestion_at_entry``.

    Returns
    -------
    pandas.Series
        Share of earlier same-region requests that entered a less congested
        queue; missing for the first request of a region.

    Notes
    -----
    A relative measure: 0.9 means the queue was more crowded than for 90% of
    the region's earlier requests. Only earlier requests are compared, so the
    rank never uses the future.
    """
    rank = pd.Series(np.nan, index=frame.index)
    known = frame["q_date"].notna() & congestion_gw.notna()
    for _, part in frame[known].groupby("region"):
        seen = []  # congestion of strictly earlier requests, kept sorted: each rank is one binary search
        for _, same_day in part.groupby("q_date", sort=True):
            values = congestion_gw.loc[same_day.index].to_numpy()
            if seen:
                rank.loc[same_day.index] = [bisect.bisect_left(seen, v) / len(seen) for v in values]
            for value in values:  # same-day requests are not compared with each other
                bisect.insort(seen, value)
    return rank


def group_rare_types(type_clean, min_count=config.RARE_TYPE_MIN):
    """Pool technology levels with fewer than ``min_count`` requests into "Other"."""
    counts = type_clean.value_counts()
    return type_clean.where(type_clean.map(counts) >= min_count, "Other")


def ambition_gap(frame):
    """Years between the proposed online date and the request date (ablation only).

    Notes
    -----
    Values below −1 or above 20 years are treated as missing: they are typing
    errors (notebook 01 found proposed dates in 1905 and gaps of 49 years).
    The field appears to be updated after entry (decision #22), so this
    feature never enters the main models.
    """
    gap = (frame["prop_date"] - frame["q_date"]).dt.days / config.DAYS_PER_YEAR
    return gap.where(gap.between(-1, 20))


def build_features(clean):
    """Every entry-time feature for every clean request.

    Parameters
    ----------
    clean : pandas.DataFrame
        Output of notebook 02.

    Returns
    -------
    pandas.DataFrame
        Same index as ``clean``: ``MAIN_FEATURES`` plus ``ABLATION_FEATURES``.

    Notes
    -----
    Size uses the first component's capacity (``mw1``) rather than the total,
    because the second component's capacity is missing for most hybrids
    outside CAISO (notebook 02); composition is carried by ``hybrid``.
    ``state`` is left as text: it is target-encoded inside the
    cross-validation folds of notebooks 06–07, never on the whole table.
    """
    size = clean["mw1"].where(clean["mw1"] > 0, clean["mw"])
    congestion = congestion_at_entry(clean)
    gap = ambition_gap(clean)
    features = pd.DataFrame({
        "region": clean["region"],
        "state": clean["state"].fillna("missing"),
        "type_group": group_rare_types(clean["type_clean"]),
        "hybrid": clean["hybrid"].astype(bool),
        "log_mw": np.log(size),
        "size_regime": size_regime(size),
        "service": clean["service"],
        "q_year": clean["q_year"].astype(float),
        "congestion_n": congestion["congestion_n"],
        "congestion_gw": congestion["congestion_gw"],
        "congestion_rank": congestion_rank(clean, congestion["congestion_gw"]),
        "ambition_gap_years": gap,
        "ambition_gap_missing": gap.isna(),
    }, index=clean.index)
    return features[MAIN_FEATURES + ABLATION_FEATURES]
