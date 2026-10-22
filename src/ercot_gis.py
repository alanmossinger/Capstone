"""ERCOT's monthly GIS reports of a past year, fetched from ERCOT's public report archive.

What: lists ERCOT's "GIS Report" (Generator Interconnection Status, report type
15933) documents, keeps those whose report month falls in the requested range,
and saves each workbook as published, with its SHA-256.
Why: the 1 January 2025 candidate set must be read from what was public that
day (decision #101). The LBNL 2024 edition ends at 2023; which ERCOT requests
were still waiting at the end of 2024, and which had signed an agreement, was
public only in ERCOT's monthly GIS reports of 2024.
Reads: ERCOT's public report service (the listing and download servlets of
``src/ercot_history.py``). ERCOT refuses connections from outside the United
States, so this runs on a U.S. GitHub runner (``.github/workflows/ercot_gis.yml``).
Writes: ``<out>/<published file name>.xlsx`` and ``<out>/SHA256.txt``.
Used by: the workflow; ``decision_date.candidates_as_of`` reads the files through
``iso_files.read_ercot_gis``.
"""

import argparse
import hashlib
import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

from src import ercot_history as eh

REPORT_TYPE_ID = 15933  # GIS Report: the monthly Generator Interconnection Status workbook
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}


def report_month(name):
    """The month a GIS report describes, from its published name (``...GIS_Report_November2024.xlsx``); NaT when none."""
    m = re.search(r"GIS_Report_([A-Za-z]+)[_ -]?(20\d\d)", name)
    if m and m.group(1).capitalize() in MONTHS:
        return pd.Timestamp(int(m.group(2)), MONTHS[m.group(1).capitalize()], 1)
    return pd.NaT


def list_reports(session=None):
    """Every GIS report the archive lists: ``doc_id``, ``name``, ``month``."""
    session = session or requests.Session()
    response = session.get(eh.LISTING_URL, params={"reportTypeId": REPORT_TYPE_ID}, headers=eh.HEADERS, timeout=60)
    response.raise_for_status()
    docs = response.json()["ListDocsByRptTypeRes"]["DocumentList"]
    rows = []
    for item in docs:
        doc = item["Document"]
        name = doc.get("ConstructedName") or doc.get("FriendlyName", "")
        rows.append({"doc_id": doc["DocID"], "name": name, "month": report_month(name)})
    return pd.DataFrame(rows)


def workbook_bytes(data):
    """The xlsx inside a download (the service returns the workbook itself or a zip holding it)."""
    if data[:2] == b"PK" and not data[:4] == b"PK\x03\x04":
        return data
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            inner = [n for n in z.namelist() if n.lower().endswith(".xlsx")]
            if inner and not any(n.startswith("xl/") for n in z.namelist()):
                return z.read(inner[0])
    except zipfile.BadZipFile:
        pass
    return data


def pull(first, last, out_dir):
    """Save every GIS report whose month is in [first, last]; return a log, one row per report."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    docs = list_reports(session)
    print(f"{len(docs)} GIS reports listed; months {docs['month'].min():%Y-%m} to {docs['month'].max():%Y-%m}", flush=True)
    keep = docs[(docs["month"] >= pd.Timestamp(first)) & (docs["month"] <= pd.Timestamp(last))].sort_values("month")
    log = []
    for r in keep.itertuples():
        name = r.name if r.name.lower().endswith(".xlsx") else f"GIS_Report_{r.month:%Y-%m}.xlsx"
        target = out_dir / name
        target.write_bytes(workbook_bytes(eh.download_zip(int(r.doc_id), session=session)))
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        with (out_dir / "SHA256.txt").open("a", encoding="utf-8") as handle:
            handle.write(f"{digest}  {target.name}\n")
        log.append({"month": f"{r.month:%Y-%m}", "file": target.name, "bytes": target.stat().st_size})
        print(f"{r.month:%Y-%m}: {target.name} ({target.stat().st_size:,} bytes)", flush=True)
    return pd.DataFrame(log)


if __name__ == "__main__":  # python -m src.ercot_gis 2024-04 2024-11 --out gis_out
    parser = argparse.ArgumentParser(description="Download ERCOT's monthly GIS reports for a range of months.")
    parser.add_argument("first", help="first report month, YYYY-MM")
    parser.add_argument("last", help="last report month, YYYY-MM")
    parser.add_argument("--out", default="data/raw/iso/gis_2024")
    args = parser.parse_args()
    result = pull(args.first, args.last, args.out)
    print(result.to_string(index=False))
    sys.exit(0 if len(result) else 1)
