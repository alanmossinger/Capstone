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

import numpy as np
import pandas as pd

from src import config


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
    at once instead of comparing every pair of requests. Only information
    dated before t is used.
    """
    exit_date = frame["on_date"].where(frame["q_status"] == "operational",
                                       frame["wd_date"].where(frame["q_status"] == "withdrawn"))
    out = pd.DataFrame(index=frame.index, columns=["congestion_n", "congestion_gw"], dtype=float)
    for _, part in frame[frame["q_date"].notna()].groupby("region"):
        entries = part["q_date"].to_numpy()
        entry_order = np.argsort(entries, kind="stable")
        entry_sorted = entries[entry_order]
        entry_gw = np.concatenate([[0.0], np.cumsum(part["mw"].to_numpy()[entry_order]) / 1000])

        exits = exit_date.loc[part.index]
        has_exit = exits.notna().to_numpy()
        exit_values = exits.to_numpy()[has_exit]
        exit_order = np.argsort(exit_values, kind="stable")
        exit_sorted = exit_values[exit_order]
        exit_gw = np.concatenate([[0.0], np.cumsum(part["mw"].to_numpy()[has_exit][exit_order]) / 1000])

        entered = np.searchsorted(entry_sorted, entries, side="left")
        left = np.searchsorted(exit_sorted, entries, side="left")
        out.loc[part.index, "congestion_n"] = entered - left
        out.loc[part.index, "congestion_gw"] = entry_gw[entered] - exit_gw[left]
    return out
