"""Audit of the raw LBNL queue file: counts, date coverage and headline checks.

What: functions that describe the project sheet exactly as LBNL published it
— row counts by status and region, placeholder dates, negative capacities,
event-date coverage by region, the "13 % built / 77 % withdrawn" headline,
the median request-to-operation time, a naive 5-year completion mock-up,
and the size of the Track A sample.
Why: the readiness gate (PLAN.md §5.3) asks whether the public file can
carry a time-to-event model, and these numbers answer it. They are computed
before any cleaning so the gate judges the file, not my edits to it.
Reads: the raw DataFrame from ``get_lbnl.load_queue``.
Writes: nothing (notebook 01 (part A) saves the outputs to ``results/``).
Used by: notebook 01 (part A); ``tests/test_cleaning.py`` pins the counts.

Run as a script (``python -m src.audit_queue``) it prints the audit.
"""

import numpy as np
import pandas as pd

from src import config


def excel_serial_to_datetime(values):
    """Convert Excel serial day numbers to timestamps.

    Parameters
    ----------
    values : pandas.Series
        Serial numbers (e.g. 43511), possibly with blanks or text.

    Returns
    -------
    pandas.Series
        ``datetime64[ns]``; anything non-numeric becomes ``NaT``.

    Notes
    -----
    Excel's day zero is 1899-12-30 (it counts a non-existent 1900-02-29), so
    43511 maps to 2019-02-15. ``errors="coerce"`` turns stray text into a
    missing date instead of failing the whole column. Every serial in the
    LBNL file is a whole day, so the numbers are converted as integer days:
    ``pd.to_datetime(floats, unit="D")`` multiplies floats under numpy's
    raise-on-overflow setting, which on Windows intermittently raised a
    spurious ``FloatingPointError`` in one run of notebook 01 (part A).
    """
    numbers = pd.to_numeric(values, errors="coerce")
    days = numbers.round().astype("Int64")
    return pd.Timestamp(config.EXCEL_ORIGIN) + pd.to_timedelta(days, unit="D")


def with_dates(raw):
    """Return a copy of the raw sheet with the five date columns converted.

    Parameters
    ----------
    raw : pandas.DataFrame
        Sheet 03 as loaded.

    Returns
    -------
    pandas.DataFrame
        Same rows and columns, plus ``mw`` (total capacity), and an
        ``q_date_valid`` flag that is False for missing dates and for the
        1970-01-01 placeholder.

    Notes
    -----
    Only a view for auditing: placeholders are flagged, not removed. Removing
    them is cleaning rule R2 in notebook 01 (part B).
    """
    dated = raw.copy()
    for column in config.LBNL_DATE_COLS:
        dated[column] = excel_serial_to_datetime(dated[column])
    dated["mw"] = dated[["mw1", "mw2", "mw3"]].sum(axis=1, min_count=1)
    dated["q_date_valid"] = (dated["q_date"].notna()
                             & (dated["q_date"] != pd.Timestamp(config.PLACEHOLDER_Q_DATE)))
    return dated


def audit_counts(raw):
    """Count the facts the readiness gate compares with the 2026-10-03 audit.

    Parameters
    ----------
    raw : pandas.DataFrame
        Sheet 03 as loaded.

    Returns
    -------
    dict
        Shape, status and region counts, placeholder request dates,
        non-positive and very large capacities, duplicate keys and missing
        ``q_year`` values. Plain Python types, so it can be saved as JSON.
    """
    dated = with_dates(raw)
    duplicated_key = raw.duplicated(["q_id", "entity"], keep=False)
    return {
        "n_rows": int(raw.shape[0]),
        "n_cols": int(raw.shape[1]),
        "q_status": {k: int(v) for k, v in raw["q_status"].value_counts(dropna=False).items()},
        "region": {k: int(v) for k, v in raw["region"].value_counts(dropna=False).items()},
        "placeholder_q_date": int((dated["q_date"] == pd.Timestamp(config.PLACEHOLDER_Q_DATE)).sum()),
        "missing_q_date": int(dated["q_date"].isna().sum()),
        "negative_mw_rows": int((dated["mw"] < 0).sum()),
        "zero_mw_rows": int((dated["mw"] == 0).sum()),
        "mw_over_5000_rows": int((dated["mw"] > 5000).sum()),
        "max_mw": float(dated["mw"].max()),
        "duplicate_key_rows": int(duplicated_key.sum()),
        "missing_q_year": int(raw["q_year"].isna().sum()),
    }


def event_date_coverage(dated):
    """Share of rows whose status implies a date that actually carry it, by region.

    Parameters
    ----------
    dated : pandas.DataFrame
        Output of ``with_dates``.

    Returns
    -------
    pandas.DataFrame
        One row per region (``config.ALL_REGIONS`` order) with counts and the
        shares ``on_date_share`` (operational rows with ``on_date``),
        ``wd_date_share`` (withdrawn rows with ``wd_date``) and
        ``q_date_share`` (rows with a valid request date).

    Notes
    -----
    A time-to-event model needs both ends of the clock: the request date and
    the exit date. Where the public file lacks exit dates the region cannot
    enter the timing model (decision #6).
    """
    rows = []
    for region in config.ALL_REGIONS:
        part = dated[dated["region"] == region]
        operational = part[part["q_status"] == "operational"]
        withdrawn = part[part["q_status"] == "withdrawn"]
        rows.append({
            "region": region,
            "n_projects": len(part),
            "n_operational": len(operational),
            "operational_with_on_date": int(operational["on_date"].notna().sum()),
            "n_withdrawn": len(withdrawn),
            "withdrawn_with_wd_date": int(withdrawn["wd_date"].notna().sum()),
            "with_valid_q_date": int(part["q_date_valid"].sum()),
        })
    table = pd.DataFrame(rows)
    table["on_date_share"] = table["operational_with_on_date"] / table["n_operational"]
    table["wd_date_share"] = table["withdrawn_with_wd_date"] / table["n_withdrawn"]
    table["q_date_share"] = table["with_valid_q_date"] / table["n_projects"]
    return table


def capacity_shares_by_status(dated, years=config.HEADLINE_YEARS):
    """Share of requested capacity in each status for a range of request years.

    Parameters
    ----------
    dated : pandas.DataFrame
        Output of ``with_dates``.
    years : tuple of int
        Inclusive range of ``q_year``.

    Returns
    -------
    pandas.DataFrame
        ``q_status``, ``gw`` and ``share`` (of total MW in the range).

    Notes
    -----
    Uses LBNL's own ``q_year`` so the result is comparable with the
    published headline (Rand et al., 2025), which is stated by capacity.
    """
    cohort = dated[dated["q_year"].between(*years)]
    mw = cohort.groupby("q_status")["mw"].sum()
    return pd.DataFrame({"q_status": mw.index, "gw": mw.values / 1000,
                         "share": mw.values / mw.sum()})


def ir_to_cod_years(dated):
    """Years from interconnection request to commercial operation, per project.

    Parameters
    ----------
    dated : pandas.DataFrame
        Output of ``with_dates``.

    Returns
    -------
    pandas.DataFrame
        Operational projects with a valid request date and an operation date
        not before it: ``region``, ``type_clean``, ``mw``, ``cod_year`` and
        ``years``.
    """
    done = dated[(dated["q_status"] == "operational") & dated["q_date_valid"]
                 & dated["on_date"].notna() & (dated["on_date"] >= dated["q_date"])]
    years = (done["on_date"] - done["q_date"]).dt.days / config.DAYS_PER_YEAR
    return pd.DataFrame({"region": done["region"], "type_clean": done["type_clean"],
                         "mw": done["mw"], "cod_year": done["on_date"].dt.year,
                         "years": years})


def five_year_completion(dated, regions=config.TRACK_A_REGIONS, years=config.MOCKUP_YEARS):
    """Naive share of generation entrants that reached operation within 5 years.

    Parameters
    ----------
    dated : pandas.DataFrame
        Output of ``with_dates``.
    regions : list of str
        Regions to report.
    years : tuple of int
        Inclusive range of request years (from the valid ``q_date``).

    Returns
    -------
    pandas.DataFrame
        ``region``, ``n``, ``completed``, ``share`` and a 95 % Wilson interval.

    Notes
    -----
    "Naive" because it ignores censoring and competing risks; that is
    harmless here only because every 2010–2018 entrant has at least six
    years of follow-up before the censor date. Generation entrants are rows
    whose ``project_type`` is Generation or missing (the same filter as
    cleaning rule R5).
    """
    entry_year = dated["q_date"].dt.year
    is_generation = dated["project_type"].isna() | (dated["project_type"] == "Generation")
    cohort = dated[dated["region"].isin(regions) & dated["q_date_valid"]
                   & entry_year.between(*years) & is_generation]
    within = ((cohort["q_status"] == "operational") & cohort["on_date"].notna()
              & ((cohort["on_date"] - cohort["q_date"]).dt.days <= 5 * config.DAYS_PER_YEAR))
    rows = []
    for region in regions:
        mask = cohort["region"] == region
        n, k = int(mask.sum()), int(within[mask].sum())
        low, high = wilson_interval(k, n)
        rows.append({"region": region, "n": n, "completed": k, "share": k / n,
                     "ci_low": low, "ci_high": high})
    return pd.DataFrame(rows)


def track_a_candidates(dated):
    """Flag rows that can enter the three-ISO timing model.

    Parameters
    ----------
    dated : pandas.DataFrame
        Output of ``with_dates``.

    Returns
    -------
    pandas.Series of bool
        True for CAISO, ERCOT and PJM rows whose status-implied event date
        is present (operational rows need ``on_date``, withdrawn rows need
        ``wd_date``; active, suspended and unknown rows need nothing).

    Notes
    -----
    This is the candidate definition used by the readiness gate. Notebook 04
    additionally requires a valid request date and applies the cleaning
    rules, so its final sample is a little smaller.
    """
    in_region = dated["region"].isin(config.TRACK_A_REGIONS)
    missing_on = (dated["q_status"] == "operational") & dated["on_date"].isna()
    missing_wd = (dated["q_status"] == "withdrawn") & dated["wd_date"].isna()
    return in_region & ~missing_on & ~missing_wd


def held_out_cohort_events(dated, candidates, years=config.TEST_YEARS):
    """Count the projects and completions available for a held-out test.

    Parameters
    ----------
    dated : pandas.DataFrame
        Output of ``with_dates``.
    candidates : pandas.Series of bool
        Track A candidate flag.
    years : tuple of int
        Inclusive range of entry years for the test cohort.

    Returns
    -------
    dict
        ``projects``, ``completions`` (operational by the censor date) and
        ``withdrawals`` among test-cohort candidates.
    """
    entry_year = dated["q_date"].dt.year
    cohort = dated[candidates & dated["q_date_valid"] & entry_year.between(*years)]
    censor = pd.Timestamp(config.CENSOR_DATE)
    completions = (cohort["q_status"] == "operational") & (cohort["on_date"] <= censor)
    withdrawals = (cohort["q_status"] == "withdrawn") & (cohort["wd_date"] <= censor)
    return {"projects": len(cohort), "completions": int(completions.sum()),
            "withdrawals": int(withdrawals.sum())}


def wilson_interval(successes, trials, z=1.96):
    """Wilson score interval for a binomial proportion.

    Parameters
    ----------
    successes, trials : int
        Counts.
    z : float
        Normal quantile (1.96 for 95 %).

    Returns
    -------
    tuple of float
        Lower and upper bound; ``(nan, nan)`` when ``trials`` is 0.

    Notes
    -----
    Preferred over the normal approximation because it stays inside [0, 1]
    and behaves well for small shares such as CAISO's 4 %.
    """
    if trials == 0:
        return np.nan, np.nan
    p = successes / trials
    centre = (p + z**2 / (2 * trials)) / (1 + z**2 / trials)
    half = z * np.sqrt(p * (1 - p) / trials + z**2 / (4 * trials**2)) / (1 + z**2 / trials)
    return centre - half, centre + half


if __name__ == "__main__":
    from src import get_lbnl

    raw_sheet = get_lbnl.load_queue(get_lbnl.download())
    for name, value in audit_counts(raw_sheet).items():
        print(f"{name}: {value}")
    print(event_date_coverage(with_dates(raw_sheet)).round(3).to_string(index=False))
