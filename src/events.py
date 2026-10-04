"""Outcome coding for the time-to-event models: events, durations, samples.

What: turns the clean queue table into one outcome per request — operation
(event 1), withdrawal (event 2) or still in the queue at the censor date
(event 0) — with the time from request to that outcome, and selects the
Track A sample.
Why: every survival curve and model in notebooks 03–09 must use the same
clock and the same censoring rules, so they are written once here.
Reads: the clean table (``data/interim/queue_clean.parquet``).
Writes: nothing (notebook 04 saves the event table).
Used by: notebooks 03 and 04; ``tests/test_features.py``.

Censoring rules: active, suspended (decision #4) and unknown requests are
censored at 2024-12-31; so are withdrawals dated after that day, because on
the censor date those projects were still in the queue. An operational row
without an operation date, or a withdrawn row without a withdrawal date, has
an outcome but no time for it, so it is excluded and counted.
"""

import numpy as np
import pandas as pd

from src import config

CENSORED, OPERATION, WITHDRAWAL = 0, 1, 2
EVENT_NAMES = {CENSORED: "censored", OPERATION: "operation", WITHDRAWAL: "withdrawal"}


def code_events(clean, censor_date=config.CENSOR_DATE):
    """Add ``event``, ``exit_date``, ``duration_years`` and ``exclusion`` to the clean table.

    Parameters
    ----------
    clean : pandas.DataFrame
        Output of notebook 02 (dates already checked by rules R1–R4).
    censor_date : str
        End of follow-up.

    Returns
    -------
    pandas.DataFrame
        Copy of ``clean`` with the four new columns. ``exclusion`` is an
        empty string for rows that can enter a time-to-event sample.

    Notes
    -----
    Durations are measured from the request date. An event on the request
    day itself is counted as one day, because survival estimators need a
    positive time.
    """
    censor = pd.Timestamp(censor_date)
    out = clean.copy()
    operation = (out["q_status"] == "operational") & out["on_date"].notna() & (out["on_date"] <= censor)
    withdrawal = (out["q_status"] == "withdrawn") & out["wd_date"].notna() & (out["wd_date"] <= censor)
    out["event"] = np.select([operation, withdrawal], [OPERATION, WITHDRAWAL], default=CENSORED)
    out["exit_date"] = out["on_date"].where(operation, out["wd_date"].where(withdrawal, censor))
    days = (out["exit_date"] - out["q_date"]).dt.days.clip(lower=1)
    out["duration_years"] = days / config.DAYS_PER_YEAR

    reasons = [
        out["q_date"].isna(),
        (out["q_status"] == "operational") & out["on_date"].isna(),
        (out["q_status"] == "withdrawn") & out["wd_date"].isna(),
    ]
    labels = ["no valid request date", "operational without operation date",
              "withdrawn without withdrawal date"]
    out["exclusion"] = np.select(reasons, labels, default="")
    return out


def track_a_sample(events):
    """Rows of the three Track A regions that can enter the timing model.

    Parameters
    ----------
    events : pandas.DataFrame
        Output of ``code_events``.

    Returns
    -------
    pandas.DataFrame
        CAISO, ERCOT and PJM rows with no exclusion.
    """
    keep = events["region"].isin(config.TRACK_A_REGIONS) & (events["exclusion"] == "")
    return events[keep].copy()


def entry_cohort(q_year):
    """Label request years with the cohorts used in the exploratory curves.

    Notes
    -----
    2000–09, 2010–14 and 2015–19 (PLAN.md §6, notebook 03); later entrants
    have too little follow-up for a 5-year view and are labelled 2020–24.
    """
    bins = [1999, 2009, 2014, 2019, 2024]
    labels = ["2000–09", "2010–14", "2015–19", "2020–24"]
    return pd.cut(q_year.astype(float), bins=bins, labels=labels)
