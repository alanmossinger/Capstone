"""Outcome coding for the time-to-event models: events, durations, samples.

What: turns the clean queue table into one outcome per request — operation
(event 1), withdrawal (event 2) or still in the queue at the censor date
(event 0) — with the time from request to that outcome, and selects the
Track A sample.
Why: every survival curve and model in notebooks 02–06 must use the same
clock and the same censoring rules, so they are written once here.
Reads: the clean table (``data/interim/queue_clean.parquet``).
Writes: nothing (notebook 03 saves the event table).
Used by: notebooks 02 and 03; ``tests/test_features.py``.

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
        Output of notebook 01 (part B) (dates already checked by rules R1–R4).
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


def flag_bulk_withdrawals(events):
    """Mark ERCOT withdrawals carrying the bulk-recorded date of 2018-08-29.

    Parameters
    ----------
    events : pandas.DataFrame
        Output of ``code_events``.

    Returns
    -------
    pandas.Series of bool
        True for the stamped rows (decision #21). They stay in every sample;
        the flag drives the as-recorded sensitivity run of notebook 06 (part A).
    """
    return ((events["region"] == "ERCOT") & (events["q_status"] == "withdrawn")
            & (events["wd_date"] == pd.Timestamp(config.ERCOT_BULK_WD_DATE)))


def delayed_entry_years(events, region="ERCOT", date=config.ERCOT_BULK_WD_DATE):
    """Years after the request at which a project enters the risk set under delayed entry.

    Parameters
    ----------
    events : pandas.DataFrame
        Output of ``code_events``.
    region : str
        Region whose observation window starts late.
    date : str
        Start of the trustworthy window.

    Returns
    -------
    pandas.Series
        0 for every project outside ``region`` or requested after ``date``;
        otherwise the years between the request and ``date``. A project whose
        exit is at or before its entry time left before the window opened and
        must be dropped from a delayed-entry fit.

    Notes
    -----
    Main timing models use this delayed entry for ERCOT (decision #21): a
    project-year or a Cox risk-set interval counts only after ``date``,
    because ERCOT's withdrawal dates before it are a bulk stamp.
    """
    start = pd.Timestamp(date)
    gap = (start - events["q_date"]).dt.days / config.DAYS_PER_YEAR
    return gap.where((events["region"] == region) & (events["q_date"] < start), 0.0).clip(lower=0)


def split_label(q_year):
    """Temporal split of docs/plan.md §6 (notebook 06 (part A)): train, validation, test, later.

    Notes
    -----
    Hyperparameters are tuned on entrants up to 2015 and checked on 2016;
    the final models are refitted on entrants up to 2016 and tested on
    2017–2019 entrants. Entrants from 2020 on are not used for testing
    because their outcomes are mostly still open.
    """
    year = q_year.astype(float)
    return pd.Series(np.select(
        [year <= config.TUNE_MAX_YEAR, year == config.VALIDATION_YEAR,
         year.between(*config.TEST_YEARS), year > config.TEST_YEARS[1]],
        ["train", "validation", "test", "later"], default="unknown"), index=q_year.index)


def track_b_sample(events):
    """All-region sample for the "ever built?" classifier (Track B).

    Parameters
    ----------
    events : pandas.DataFrame
        Output of ``code_events``.

    Returns
    -------
    pandas.DataFrame
        Requests from every region entering up to 2017 whose outcome is
        known (operational or withdrawn), with ``built`` = 1 if operational.

    Notes
    -----
    No dates beyond the status are needed, so the six regions without exit
    dates can join. Keeping only resolved requests drops the slow ones that
    are still waiting; the later the cohort, the larger that selection, which
    is why Track B stops at the 2017 entrants (docs/plan.md §6, notebook 04 (part C)).
    """
    keep = (events["q_year"].astype(float) <= config.TRACK_B_MAX_YEAR) \
        & events["q_status"].isin(["operational", "withdrawn"])
    out = events[keep].copy()
    out["built"] = (out["q_status"] == "operational").astype(int)
    return out


def entry_cohort(q_year):
    """Label request years with the cohorts used in the exploratory curves.

    Notes
    -----
    2000–09, 2010–14 and 2015–19 (docs/plan.md §6, notebook 02 (part A)); later entrants
    have too little follow-up for a 5-year view and are labelled 2020–24.
    """
    bins = [1999, 2009, 2014, 2019, 2024]
    labels = ["2000–09", "2010–14", "2015–19", "2020–24"]
    return pd.cut(q_year.astype(float), bins=bins, labels=labels)
