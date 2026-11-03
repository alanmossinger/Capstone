"""External benchmarks: LBNL's published summaries next to the same numbers from my clean table.

What: reads five summary tables from LBNL's own workbook (completion rate by
type and by region, status after an interconnection agreement, request-to-
operation time by size, request-to-agreement time by service type) and
computes each one from the clean public file with the same definition.
Why: if the clean file reproduces LBNL's published figures, the data and the
cleaning are doing what I think they do; where it does not, the gap is
explained instead of hidden (docs/plan.md §6, notebook 02 (part A)).
Reads: sheets 22, 23, 25, 31 and 38 of the frozen LBNL workbook.
Writes: nothing (notebook 02 (part A) saves ``results/benchmarks.csv``).
Used by: notebook 02 (part A).

LBNL's summaries draw on 7 ISOs and 32 non-ISO areas with complete status
information, and partly on non-public data, so small differences from the
public file are expected.
"""

import numpy as np
import pandas as pd

from src import config

_STATUSES = ["active", "operational", "suspended", "withdrawn"]
_DAYS_PER_MONTH = config.DAYS_PER_YEAR / 12
_LBNL_SIZE_BINS = [0, 5, 20, 50, 100, 200, np.inf]  # MW edges of LBNL sheet 38
_LBNL_SIZE_LABELS = ["<5 MW", "5 - <20 MW", "20 - <50 MW", "50 - <100 MW", "100 - <200 MW", "200+ MW"]


def _block(sheet, label, first_col, n_cols):
    """The table whose header row has ``label`` in column ``first_col``, down to its first empty row.

    Notes
    -----
    LBNL's summary sheets stack several small tables in one sheet, so the
    block stops at the first row that is empty across its columns.
    """
    rows, cols = np.where(sheet.to_numpy() == label)
    top = [r for r, c in zip(rows, cols) if c == first_col][0]
    block = sheet.iloc[top + 1:, first_col:first_col + n_cols]
    empty = block.isna().all(axis=1).to_numpy()
    if empty.any():
        block = block.iloc[:int(np.argmax(empty))]
    block.columns = sheet.iloc[top, first_col:first_col + n_cols].tolist()
    return block.dropna(subset=[block.columns[0]])


def lbnl_completion(path, sheet_name, group_label):
    """LBNL completion rates (count and capacity) from sheet 22 or 23.

    Parameters
    ----------
    path : pathlib.Path
        The LBNL workbook.
    sheet_name : str
        ``"22. Comp. Rate Gen Type"`` or ``"23. Comp. Rate Region"``.
    group_label : str
        Header of the group column (``"Type"`` or ``"Region"``).

    Returns
    -------
    pandas.DataFrame
        ``group``, ``by_count``, ``by_capacity``: operational share of
        2000–2019 requests, as LBNL defines it.
    """
    sheet = pd.read_excel(path, sheet_name=sheet_name, header=None)
    capacity = _block(sheet, group_label, 0, 5).set_index(group_label).astype(float).fillna(0)
    count = _block(sheet, group_label, 6, 5).set_index(group_label).astype(float).fillna(0)
    return pd.DataFrame({
        "by_count": count["Operational"] / count.sum(axis=1),
        "by_capacity": capacity["Operational"] / capacity.sum(axis=1),
    }).rename_axis("group").reset_index()


def my_completion(clean, by, groups):
    """Operational share of 2000–2019 requests by ``by``, LBNL's definition, from the clean table."""
    cohort = clean[clean["q_year"].between(*config.HEADLINE_YEARS)
                   & clean["q_status"].isin(_STATUSES) & clean[by].isin(groups)]
    operational = cohort["q_status"] == "operational"
    grouped = cohort.assign(op=operational, op_mw=cohort["mw"].where(operational, 0)).groupby(by)
    return pd.DataFrame({"by_count": grouped["op"].mean(),
                         "by_capacity": grouped["op_mw"].sum() / grouped["mw"].sum()}
                        ).rename_axis("group").reset_index()


def lbnl_post_ia(path):
    """Status at end-2024 of requests whose IA was signed 2000–2021 (LBNL sheet 25)."""
    sheet = pd.read_excel(path, sheet_name="25. Post-IA Completion", header=None)
    block = _block(sheet, "Status (As of End of 2024)", 0, 3)
    return pd.Series(block["Percentage"].astype(float).to_numpy(),
                     index=block["Status (As of End of 2024)"].str.strip(), name="lbnl")


def my_post_ia(clean):
    """The same status shares from the clean table (IA signed 2000–2021)."""
    signed = clean[clean["ia_date"].dt.year.between(2000, 2021) & clean["q_status"].isin(_STATUSES)]
    return signed["q_status"].value_counts(normalize=True).rename("mine"), len(signed)


def lbnl_ir_to_cod_by_size(path, years=(2018, 2024)):
    """Median months from request to operation by LBNL size bin, from sheet 38's project rows."""
    sheet = pd.read_excel(path, sheet_name="38. IR to COD - size", header=None)
    rows = _block(sheet, "In-Service Year", 0, 3)
    rows = rows[pd.to_numeric(rows["In-Service Year"], errors="coerce").between(*years)]
    return rows.groupby("Project Capacity (MW)")["Duration (months)"].median().astype(float)


def my_ir_to_cod_by_size(clean, years=(2018, 2024)):
    """The same medians from the clean table (operational projects reaching COD in ``years``)."""
    done = clean[(clean["q_status"] == "operational") & clean["on_date"].dt.year.between(*years)
                 & clean["q_date"].notna()]
    months = (done["on_date"] - done["q_date"]).dt.days / _DAYS_PER_MONTH
    bins = pd.cut(done["mw"], bins=_LBNL_SIZE_BINS, labels=_LBNL_SIZE_LABELS, right=False)
    return months.groupby(bins, observed=True).median()


def lbnl_ir_to_ia_by_service(path, years=(2010, 2024)):
    """Median months from request to IA by service type, from sheet 31's box-plot rows."""
    sheet = pd.read_excel(path, sheet_name="31. IR to IA - service", header=None)
    rows = _block(sheet, "Year of IA", 8, 3)
    rows = rows[pd.to_numeric(rows["Year of IA"], errors="coerce").between(*years)]
    return rows.groupby("Service")["Duration (months)"].median().astype(float)


def my_ir_to_ia_by_service(clean, years=(2010, 2024)):
    """The same medians from the clean table; ERCOT is its own service label, as in LBNL's sheet."""
    signed = clean[clean["ia_date"].dt.year.between(*years) & clean["q_date"].notna()
                   & (clean["ia_date"] >= clean["q_date"])]
    service = signed["service"].where(signed["region"] != "ERCOT", "ERCOT")
    months = (signed["ia_date"] - signed["q_date"]).dt.days / _DAYS_PER_MONTH
    return months.groupby(service).median()
