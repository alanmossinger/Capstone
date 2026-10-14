"""Download ERCOT's historical day-ahead hub and load-zone prices (2018–2023) from its public yearly files.

What: ERCOT publishes "Historical DAM Load Zone and Hub Prices" as one zip
per year (report type 13060, no sign-in), each holding a workbook with one
sheet per month of hourly settlement-point prices. This module lists the
report's documents, downloads the yearly zips, parses the sheets and writes
one parquet per year in the same layout as the 2024 gridstatus file
(``Time``, ``Interval Start``, ``Interval End``, ``Location``,
``Location Type``, ``Market``, ``SPP``), so ``energy_data.ercot_dam_monthly``
reads every year the same way.
Why: hourly ERCOT prices for 2018–2023 replace the ASSUMED 2020–2023 bridge
(PJM West × 0.77) in the market table and restore Winter Storm Uri to the
price history (decision #78). ERCOT's edge refuses connections from outside
the United States (decision #53), so this runs on a GitHub-hosted runner in
the U.S. (``.github/workflows/ercot_history.yml``) and the files come back
as a workflow artifact; nothing under ``data/raw/`` is committed.
Reads: the public report listing and the yearly zips on ercot.com.
Writes: ``<out_dir>/ercot_dam_spp_<year>.parquet`` and ``SHA256.txt``.
Used by: the workflow; ``python -m src.ercot_history 2018 2023 --out data/raw/ercot``;
``tests/test_ercot_history.py`` (the parser, on a small synthetic workbook).
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

LISTING_URL = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS"
DOWNLOAD_URL = "https://www.ercot.com/misdownload/servlets/mirDownload"
REPORT_TYPE_ID = 13060  # Historical DAM Load Zone and Hub Prices, one zip per year
HEADERS = {"User-Agent": "Mozilla/5.0 (research pull of public market data; alanmossinger/Capstone)"}
COLUMNS = ["Time", "Interval Start", "Interval End", "Location", "Location Type", "Market", "SPP"]


def list_documents(report_type_id=REPORT_TYPE_ID, session=None):
    """The report's document list as a DataFrame with ``doc_id``, ``name`` and ``year`` (None when the name has no year)."""
    session = session or requests.Session()
    response = session.get(LISTING_URL, params={"reportTypeId": report_type_id}, headers=HEADERS, timeout=60)
    response.raise_for_status()
    docs = response.json()["ListDocsByRptTypeRes"]["DocumentList"]
    rows = []
    for item in docs:
        doc = item["Document"]
        name = doc.get("ConstructedName") or doc.get("FriendlyName", "")
        year = re.search(r"_(\d{4})\.zip$", name)
        rows.append({"doc_id": doc["DocID"], "name": name, "year": int(year.group(1)) if year else None})
    return pd.DataFrame(rows)


def download_zip(doc_id, session=None):
    """The bytes of one document."""
    session = session or requests.Session()
    response = session.get(DOWNLOAD_URL, params={"doclookupId": doc_id}, headers=HEADERS, timeout=300)
    response.raise_for_status()
    return response.content


def parse_workbook(data):
    """One year's workbook (bytes of the xlsx, or of the zip that holds it) as hourly rows in the gridstatus layout.

    Parameters
    ----------
    data : bytes

    Returns
    -------
    pandas.DataFrame
        Columns ``COLUMNS``; one row per hour and settlement point.

    Notes
    -----
    Each sheet carries ``Delivery Date``, ``Hour Ending`` ("01:00" … "24:00"),
    ``Repeated Hour Flag`` ("Y" for the second 01:00–02:00 hour of the
    fall-back day), ``Settlement Point`` and ``Settlement Point Price``. The
    interval start is the delivery date plus hour-ending minus one, localised
    to US/Central; the repeated-hour flag resolves the one ambiguous hour, and
    the spring-forward day has no 02:00 row, so nothing is non-existent.
    Hubs (``HB_``) are typed "Trading Hub" and load zones (``LZ_``) "Load
    Zone", as gridstatus types them.
    """
    if data[:2] == b"PK" and zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            inner = [n for n in archive.namelist() if n.lower().endswith((".xlsx", ".xls"))]
            if inner:  # a zip of the workbook (the report's layout); an xlsx is itself a zip, so only unwrap when one is inside
                data = archive.read(inner[0])
    sheets = pd.read_excel(io.BytesIO(data), sheet_name=None)
    frames = []
    for name, sheet in sheets.items():
        sheet = sheet.rename(columns=lambda c: str(c).strip())
        if "Settlement Point Price" not in sheet.columns:
            continue
        hour = sheet["Hour Ending"].astype(str).str.slice(0, 2).astype(int)
        start = pd.to_datetime(sheet["Delivery Date"]) + pd.to_timedelta(hour - 1, unit="h")
        repeated = sheet["Repeated Hour Flag"].astype(str).str.strip().str.upper().eq("Y")
        start = start.dt.tz_localize("US/Central", ambiguous=~repeated.to_numpy(), nonexistent="shift_forward")
        location = sheet["Settlement Point"].astype("string")
        frames.append(pd.DataFrame({"Time": start, "Interval Start": start, "Interval End": start + pd.Timedelta(hours=1),
                                    "Location": location,
                                    "Location Type": pd.Categorical(location.str.startswith("HB_").map({True: "Trading Hub", False: "Load Zone"}),
                                                                    categories=["Load Zone", "Trading Hub"]),
                                    "Market": "DAY_AHEAD_HOURLY", "SPP": pd.to_numeric(sheet["Settlement Point Price"], errors="coerce")}))
    if not frames:
        raise ValueError("no sheet with a 'Settlement Point Price' column")
    out = pd.concat(frames, ignore_index=True).sort_values(["Interval Start", "Location"], kind="stable").reset_index(drop=True)
    return out[COLUMNS]


def pull_years(years, out_dir, force=False):
    """Download and parse each year, write the parquet and its SHA-256; return a log, one row per year."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    docs = list_documents(session=session)
    log = []
    for year in years:
        target = out_dir / f"ercot_dam_spp_{year}.parquet"
        if target.exists() and not force:
            log.append({"year": year, "rows": len(pd.read_parquet(target)), "file": target.name, "from_cache": True})
            continue
        match = docs[(docs["year"] == year) & docs["name"].str.contains("DAMLZHBSPP", case=False)]
        if match.empty:
            raise RuntimeError(f"no DAMLZHBSPP document for {year} in report {REPORT_TYPE_ID}; names seen: {docs['name'].head(5).tolist()}")
        table = parse_workbook(download_zip(int(match.iloc[0]["doc_id"]), session=session))
        table.to_parquet(target, index=False)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        with (out_dir / "SHA256.txt").open("a", encoding="utf-8") as handle:
            handle.write(f"{digest}  {target.name}\n")
        log.append({"year": year, "rows": len(table), "file": target.name, "from_cache": False})
        print(f"{year}: {len(table):,} rows, {table['Location'].nunique()} settlement points, "
              f"{table['Interval Start'].min():%Y-%m-%d} to {table['Interval Start'].max():%Y-%m-%d}", flush=True)
    return pd.DataFrame(log)


if __name__ == "__main__":  # python -m src.ercot_history 2018 2023 --out data/raw/ercot
    parser = argparse.ArgumentParser(description="Download ERCOT historical DAM hub and load-zone prices by year.")
    parser.add_argument("first", type=int)
    parser.add_argument("last", type=int)
    parser.add_argument("--out", default="data/raw/ercot")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = pull_years(range(args.first, args.last + 1), args.out, force=args.force)
    print(result.to_string(index=False))
    sys.exit(0 if (result["rows"] > 0).all() else 1)
