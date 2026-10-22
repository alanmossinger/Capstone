"""Readers for the two ISO queue files Alan fetched on 2026-10-07: PJM's queue export and ERCOT's GIS report.

What: ``read_pjm_queue`` parses PJM's ``PlanningQueues.xml`` export into one
row per queue position with its dated fields (submitted, withdrawn, in
service, backfeed, test energy) and its study and agreement *statuses*;
``read_ercot_gis`` reads the project sheets of ERCOT's monthly Generator
Interconnection Status (GIS) report into one row per INR with the dated
study phases and the sheet the request was listed on.
Why: notebook 04 (part I) needs to know what each file can date after entry for the
2017–2019 test cohort before anything from it is used in a landmark
(decision #53, #57). The readers only parse; joining and judging the
coverage happen in the notebook, where they are printed.
Reads: ``data/raw/iso/pjm_queue_<date>.xml``, ``data/raw/iso/ercot_gis_<date>.xlsx``.
Writes: nothing.
Used by: notebook 04 (part I); ``tests/test_iso_files.py``.
"""

import xml.etree.ElementTree as ET

from pathlib import Path

import numpy as np
import pandas as pd

PJM_DATES = {"SubmittedDate": "submitted_date", "WithdrawalDate": "withdrawal_date", "ActualInServiceDate": "in_service_date",
             "BackfeedDate": "backfeed_date", "TestEnergyDate": "test_energy_date"}
PJM_STATUSES = {"Status": "pjm_status", "ProjectType": "project_type", "FeasibilityStudyStatus": "feasibility_status",
                "SystemImpactStudyStatus": "impact_status", "FacilitiesStudyStatus": "facilities_status",
                "Interim-InterconnectionService-GenerationInterconnectionAgreement-Status": "isa_status"}
ERCOT_SHEETS = {"Project Details - Large Gen": "active (large)", "Project Details - Small Gen": "active (small)",
                "Inactive Projects": "inactive", "Cancellation Update": "cancelled"}
ERCOT_DATES = {"Screening Study Started": "ss_started", "Screening Study Complete": "ss_complete", "FIS Requested": "fis_requested",
               "FIS Approved": "fis_approved", "IA Signed": "ia_signed", "Approved for Energization": "energization_approved",
               "Approved for Synchronization": "synchronization_approved", "Inactive Date": "inactive_date", "Cancel Date": "cancel_date"}


def read_pjm_queue(path):
    """One row per PJM queue position from the XML export, dates parsed, statuses kept as text.

    Parameters
    ----------
    path : str or pathlib.Path
        PJM's ``PlanningQueues.xml`` export.

    Returns
    -------
    pandas.DataFrame
        ``q_id`` (``ProjectNumber``), the dated fields of ``PJM_DATES`` and
        the status fields of ``PJM_STATUSES``.

    Notes
    -----
    The export carries a status for each study ("Document Posted") and a
    link to its PDF, but no date for any study or for the agreement; the
    only dates are the request, the exit and two late construction steps
    (backfeed and test energy). "N/A" and empty fields become missing.
    """
    root = ET.parse(path).getroot()
    rows = [{child.tag: (child.text or "").strip() for child in project} for project in root]
    raw = pd.DataFrame(rows)
    raw = raw.where(~raw.isin(["N/A", ""]))
    out = pd.DataFrame({"q_id": raw["ProjectNumber"].astype(str).str.strip()})
    for source, name in PJM_DATES.items():
        out[name] = pd.to_datetime(raw.get(source), format="%m/%d/%Y", errors="coerce")
    for source, name in PJM_STATUSES.items():
        out[name] = raw.get(source)
    return out


def _ercot_sheet(path, sheet):
    """One ERCOT sheet with its header row found by the ``INR`` column (the report pads each sheet with a title block)."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header = next(i for i in range(len(raw)) if (raw.iloc[i].astype(str).str.strip() == "INR").any())
    frame = raw.iloc[header + 1:].copy()
    frame.columns = [str(c).replace("\n", " ").strip() for c in raw.iloc[header]]
    return frame[frame["INR"].notna()]


def read_ercot_gis(path, report_month=None):
    """One row per INR across the GIS report's project sheets, with the dated phases and the sheet it is listed on.

    Parameters
    ----------
    path : str or pathlib.Path
        ERCOT's monthly GIS report (``.xlsx``).
    report_month : str or pandas.Timestamp, optional
        The month the report describes; read from the file name (``..._2024-11.xlsx``
        or ``..._November_2024.xlsx``) when not given. Needed to stack monthly reports.

    Returns
    -------
    pandas.DataFrame
        ``q_id`` (INR), ``listed_as`` (active large / active small /
        inactive / cancelled), the dated fields of ``ERCOT_DATES`` that the
        sheet carries, ``phase`` (GIM study phase) and ``mw``.

    Notes
    -----
    The report lists requests that are still active, plus the month's
    inactive and cancelled ones; a request that reached commercial operation
    or withdrew earlier is no longer in it. Being listed is therefore
    information about the outcome, which notebook 04 (part I) measures before any
    date from the report is used.
    """
    parts = []
    for sheet, listed_as in ERCOT_SHEETS.items():
        frame = _ercot_sheet(path, sheet)
        part = pd.DataFrame({"q_id": frame["INR"].astype(str).str.strip(), "listed_as": listed_as})
        for source, name in ERCOT_DATES.items():
            if source in frame:
                part[name] = pd.to_datetime(frame[source], errors="coerce").to_numpy()
        part["phase"] = frame["GIM Study Phase"].to_numpy() if "GIM Study Phase" in frame else np.nan
        for source, name in (("Fuel", "fuel"), ("Technology", "technology")):  # what kind of plant: the 2024 entrants of the as-of view have no other source
            part[name] = frame[source].astype(str).str.strip().to_numpy() if source in frame else np.nan
        mw = next((c for c in frame.columns if c.startswith("Capacity") or c.startswith("MW")), None)
        part["mw"] = pd.to_numeric(frame[mw], errors="coerce").to_numpy() if mw else np.nan
        parts.append(part)
    out = pd.concat(parts, ignore_index=True).drop_duplicates("q_id")
    out["report_month"] = pd.Timestamp(report_month) if report_month is not None else month_from_name(Path(path).name)
    return out


def month_from_name(name):
    """The report month in a GIS file name: ``2024-11``, ``2024_11`` or ``November_2024``; NaT when none."""
    import re

    m = re.search(r"(20\d\d)[-_](\d\d)", name)
    if m:
        return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)[-_ ]?(20\d\d)", name, re.IGNORECASE)
    if m:
        return pd.Timestamp(f"{m.group(2)}-{pd.Timestamp(m.group(1) + ' 1 2000').month:02d}-01")
    return pd.NaT
