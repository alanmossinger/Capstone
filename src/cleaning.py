"""Cleaning rules R1–R9 for the LBNL queue file.

What: one function per rule of PLAN.md §7. Each takes the table, returns a
cleaned copy and a dict ``{what was done: rows touched}``; ``apply_rule``
records that dict in a log and ``clean_queue`` runs all nine in order.
Why: every change to the published file is named, counted and testable, so
the clean table can be traced back to the raw one rule by rule.
Reads: the raw sheet from ``get_lbnl.load_queue``.
Writes: nothing (notebook 01 (part B) saves ``data/interim/queue_clean.parquet`` and
``results/clean_log.csv``).
Used by: notebook 01 (part B); ``tests/test_cleaning.py``.

The order matters. Dates are converted (R1) and placeholders removed (R2)
before date checks (R3, R4); non-generation rows go (R5) before capacities
are checked (R6), so a row is counted under the first rule that removes it.
"""

import pandas as pd

from src import audit_queue, config

_PLACEHOLDER = pd.Timestamp(config.PLACEHOLDER_Q_DATE)
_EARLIEST = pd.Timestamp(config.EARLIEST_VALID_DATE)


def r1_convert_dates(frame):
    """R1 — convert the five date columns from Excel serial numbers.

    Parameters
    ----------
    frame : pandas.DataFrame
        Raw sheet.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)
        Table with ``datetime64`` date columns; rows converted per column.

    Notes
    -----
    LBNL stores dates as serial numbers (43511 = 2019-02-15). Nothing else
    changes here, so later rules can be read as checks on real dates.
    """
    out = frame.copy()
    touched = {}
    for column in config.LBNL_DATE_COLS:
        out[column] = audit_queue.excel_serial_to_datetime(out[column])
        touched[f"{column} converted"] = int(out[column].notna().sum())
    return out, touched


def r2_placeholder_dates(frame):
    """R2 — treat 1970-01-01 as missing and recompute ``q_year`` from ``q_date``.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R1.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Notes
    -----
    1970-01-01 is the Unix epoch, a fill value for "unknown". It appears in
    ``q_date`` (where LBNL's ``q_year`` then reads 1970) and in ``ia_date``.
    ``q_year`` is recomputed so that it can never disagree with ``q_date``;
    it is stored as a nullable integer.
    """
    out = frame.copy()
    q_mask = out["q_date"] == _PLACEHOLDER
    ia_mask = out["ia_date"] == _PLACEHOLDER
    out.loc[q_mask, "q_date"] = pd.NaT
    out.loc[ia_mask, "ia_date"] = pd.NaT
    new_year = out["q_date"].dt.year.astype("Int64")
    old_year = out["q_year"].astype("Int64")
    changed = (new_year != old_year).fillna(new_year.isna() != old_year.isna())
    out["q_year"] = new_year
    return out, {"q_date placeholder set to missing": int(q_mask.sum()),
                 "ia_date placeholder set to missing": int(ia_mask.sum()),
                 "q_year changed by recomputing it from q_date": int(changed.sum())}


def r3_operation_dates(frame):
    """R3 — keep ``on_date`` only where it can be a real operation date.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R2.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Notes
    -----
    Three artefacts, cleared in this order: an operation date on a row whose
    status is not operational (the status is the more recent field), an
    operation date before the request date, and a date before 1950. Clearing
    the date keeps the row: its status still says what happened.
    """
    out = frame.copy()
    wrong_status = out["on_date"].notna() & (out["q_status"] != "operational")
    out.loc[wrong_status, "on_date"] = pd.NaT
    before_request = out["on_date"].notna() & (out["on_date"] < out["q_date"])
    out.loc[before_request, "on_date"] = pd.NaT
    too_early = out["on_date"].notna() & (out["on_date"] < _EARLIEST)
    out.loc[too_early, "on_date"] = pd.NaT
    return out, {"on_date cleared: status is not operational": int(wrong_status.sum()),
                 "on_date cleared: before the request date": int(before_request.sum()),
                 "on_date cleared: before 1950": int(too_early.sum())}


def r4_withdrawal_dates(frame):
    """R4 — keep ``wd_date`` only where it can be a real withdrawal date.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R3.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Notes
    -----
    Same logic as R3: the status wins over a stray date, and a withdrawal
    cannot precede the request. Withdrawal dates after the censor date are
    left alone here; notebook 03 censors them.
    """
    out = frame.copy()
    wrong_status = out["wd_date"].notna() & (out["q_status"] != "withdrawn")
    out.loc[wrong_status, "wd_date"] = pd.NaT
    before_request = out["wd_date"].notna() & (out["wd_date"] < out["q_date"])
    out.loc[before_request, "wd_date"] = pd.NaT
    return out, {"wd_date cleared: status is not withdrawn": int(wrong_status.sum()),
                 "wd_date cleared: before the request date": int(before_request.sum())}


def r5_generation_only(frame):
    """R5 — keep generation requests (``project_type`` Generation or missing).

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R4.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)
        Rows dropped per ``project_type``.

    Notes
    -----
    Surplus, upgrade and replacement requests change an existing plant's
    interconnection rather than propose a new one, so they are a different
    process. Missing ``project_type`` is kept: in some queues the field is
    simply not reported and those rows are generation requests.
    """
    keep = frame["project_type"].isna() | (frame["project_type"] == "Generation")
    dropped = frame.loc[~keep, "project_type"].value_counts()
    return (frame[keep].copy(),
            {f"dropped: project_type = {kind}": int(n) for kind, n in dropped.items()})


def r6_capacity(frame):
    """R6 — total capacity ``mw``; drop non-positive values; flag very large ones.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R5.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Notes
    -----
    ``mw`` sums the components of a hybrid (``min_count=1`` keeps a row with
    no capacity at all missing instead of 0). A request cannot have zero or
    negative capacity, so those rows are dropped. Requests above
    ``MW_FLAG_THRESHOLD`` are flagged in ``mw_large`` but kept: some are real
    multi-gigawatt complexes.
    """
    out = frame.copy()
    out["mw"] = out[["mw1", "mw2", "mw3"]].sum(axis=1, min_count=1)
    bad = ~(out["mw"] > 0)
    out = out[~bad].copy()
    out["mw_large"] = out["mw"] > config.MW_FLAG_THRESHOLD
    return out, {"dropped: mw ≤ 0 or missing": int(bad.sum()),
                 f"flagged: mw > {config.MW_FLAG_THRESHOLD:,}": int(out["mw_large"].sum())}


def r7_project_key(frame):
    """R7 — build the project key (``entity`` | ``q_id``) and resolve duplicates.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R6.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Raises
    ------
    ValueError
        If the key is still not unique after resolving duplicates.

    Notes
    -----
    ``q_id`` alone repeats across transmission providers, so the key pairs it
    with ``entity``. Where a key still repeats, the copy without a request
    date is dropped: without a request date it cannot enter either model,
    and keeping it would count the project twice. ``q_id`` is stored as text
    because it mixes numbers and codes.
    """
    out = frame.copy()
    out["q_id"] = out["q_id"].astype(str)
    out["project_key"] = out["entity"].astype(str) + "|" + out["q_id"]
    shared = out["project_key"].duplicated(keep=False)
    drop = shared & out["q_date"].isna()
    out = out[~drop].copy()
    if out["project_key"].duplicated().any():
        raise ValueError("project_key is not unique after R7; inspect the duplicates.")
    return out, {"rows sharing a key": int(shared.sum()),
                 "dropped: duplicate without a request date": int(drop.sum())}


def r8_sparse_fields(frame):
    """R8 — drop sparse fields and give missing categories their own level.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R7.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Notes
    -----
    ``developer`` (about 18% filled) and ``cluster`` (about 26%) are blank for
    most rows, so they cannot be features and are removed. ``service`` and ``county`` are
    useful but often blank; a "missing" level keeps those rows in the models
    and lets the model learn whether missingness itself carries information.
    """
    out = frame.drop(columns=["developer", "cluster"])
    touched = {"developer values removed": int(frame["developer"].notna().sum()),
               "cluster values removed": int(frame["cluster"].notna().sum())}
    for column in ["service", "county"]:
        touched[f"{column} missing → 'missing'"] = int(out[column].isna().sum())
        out[column] = out[column].fillna("missing")
    return out, touched


def r9_hybrid(frame):
    """R9 — flag hybrids (a second resource type is present).

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of R8.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)

    Notes
    -----
    ``type_clean`` is kept as LBNL standardised it. LBNL notes that hybrid
    storage capacity is estimated for some projects (sheet 13, note 2), and
    many hybrids have no ``mw2`` at all, so ``mw`` understates their total
    capacity; the count of such rows is logged.
    """
    out = frame.copy()
    out["hybrid"] = out["type2"].notna()
    no_mw2 = out["hybrid"] & out["mw2"].isna()
    return out, {"hybrid = True": int(out["hybrid"].sum()),
                 "hybrid without mw2 (second capacity unknown)": int(no_mw2.sum())}


RULES = [r1_convert_dates, r2_placeholder_dates, r3_operation_dates, r4_withdrawal_dates,
         r5_generation_only, r6_capacity, r7_project_key, r8_sparse_fields, r9_hybrid]


def apply_rule(rule, frame, log):
    """Apply one rule and append its counts to ``log``.

    Parameters
    ----------
    rule : callable
        One of ``RULES``.
    frame : pandas.DataFrame
        Table before the rule.
    log : list of dict
        Running log; one entry per item the rule reports.

    Returns
    -------
    pandas.DataFrame
        Table after the rule.
    """
    out, touched = rule(frame)
    code = rule.__name__.split("_")[0].upper()
    for item, rows in touched.items():
        log.append({"rule": code, "function": rule.__name__, "item": item, "rows": rows,
                    "rows_in": len(frame), "rows_out": len(out)})
    return out


def clean_queue(raw):
    """Run R1–R9 in order.

    Parameters
    ----------
    raw : pandas.DataFrame
        Raw sheet from ``get_lbnl.load_queue``.

    Returns
    -------
    tuple of (pandas.DataFrame, pandas.DataFrame)
        Clean table and the rule log (``rule, function, item, rows, rows_in,
        rows_out``).
    """
    log, frame = [], raw
    for rule in RULES:
        frame = apply_rule(rule, frame, log)
    return frame, pd.DataFrame(log)
