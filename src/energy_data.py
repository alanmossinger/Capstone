"""Fetch, verify and parse the v5 energy sources: BSEE production, EIA-923, prices, ERCOT files, eGRID.

What: scripted downloads with SHA-256 (BSEE OGOR-A zips, the EIA monthly
spot-price workbooks, eGRID), the EIA-923 pull through the EIA API, the
hash check of the ERCOT 2024 files, the parsers that turn each raw file into
a tidy monthly table, and the manifest every source is recorded in.
Why: the integrated portfolio (PLAN.md §14) needs observed production,
generation and prices beside the queue file, each traceable to a public
file with its checksum, vintage and units (decision #64).
Reads: the URLs in ``src/config.py``; ``data/raw/<source>/``; the EIA key
from ``.env`` for EIA-923.
Writes: ``data/raw/bsee/ogora<year>delimit.zip``, ``data/raw/prices/*.xls``,
``data/raw/egrid/<file>``, ``data/raw/eia923/api_*.json`` and the combined
parquet, ``data/raw/<source>/SHA256.txt``, ``data/raw/manifest_v5.json``.
Used by: notebook 01 (parts D and E); ``tests/test_energy_data.py``.

Units are kept as the sources report them — barrels, thousand cubic feet,
megawatt-hours, nominal dollars — and named in the column names; the panel
of notebook 01 part E converts to real dollars.
"""

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone

import pandas as pd
import requests

from src import config, eia_api, paths

# OGOR-A delimited layout (BSEE field definitions page, accessed 2026-10-12): 19 quoted fields, no header
OGORA_COLUMNS = ["lease_number", "completion_name", "production_date", "days_on_prod", "product_code",
                 "oil_bbl", "gas_mcf", "water_bbl", "api_well_number", "well_status", "area_block",
                 "operator_num", "operator_name", "field_name_code", "injection_bbl", "prod_interval_cd",
                 "first_prod_date", "unit_agt_number", "unit_aloc_suffix"]
OGORA_NUMERIC = ["days_on_prod", "oil_bbl", "gas_mcf", "water_bbl", "injection_bbl"]
EGRID_PLANT_COLUMNS = {  # eGRID plant sheet -> tidy names
    "ORISPL": "plant_code", "PNAME": "plant_name", "PSTATABB": "state", "BACODE": "balancing_authority",
    "LAT": "latitude", "LON": "longitude", "PLPRMFL": "primary_fuel", "PLFUELCT": "fuel_category",
    "NAMEPCAP": "nameplate_mw", "CAPFAC": "capacity_factor", "PLNGENAN": "net_generation_mwh",
    "PLCO2RTA": "co2_lb_per_mwh", "PLHTRT": "heat_rate_btu_per_kwh",
}


def sha256(path):
    """SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url, path, force=False, timeout=600):
    """Download ``url`` to ``path`` unless it already exists; return the path.

    Notes
    -----
    Files are fetched once and kept as downloaded (``data/raw`` is never
    edited); a short browser-like user agent is sent because data.bsee.gov
    refuses the default one.
    """
    if path.exists() and path.stat().st_size > 0 and not force:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path


def record_hashes(folder):
    """Write ``SHA256.txt`` beside the data files of ``folder`` and return the digests."""
    digests = {p.name: sha256(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name != "SHA256.txt"}
    (folder / "SHA256.txt").write_text("".join(f"{d}  {n}\n" for n, d in digests.items()), encoding="utf-8")
    return digests


# --- BSEE OGOR-A ----------------------------------------------------------------

def fetch_ogora(years=config.BSEE_YEARS, out_dir=paths.RAW_BSEE, force=False):
    """Download one OGOR-A zip per production year and record their hashes.

    Returns
    -------
    pandas.DataFrame
        ``year``, ``file``, ``bytes``, ``sha256``.
    """
    rows = []
    for year in range(years[0], years[1] + 1):
        path = download(config.BSEE_URL.format(year=year), out_dir / f"ogora{year}delimit.zip", force=force)
        rows.append({"year": year, "file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    record_hashes(out_dir)
    return pd.DataFrame(rows)


def read_ogora(source):
    """Parse one OGOR-A delimited file (zip path, text path or text) into completion-months.

    Returns
    -------
    pandas.DataFrame
        One row per (lease, completion, month) with the 19 OGOR-A columns,
        numeric volumes, ``month`` as a Timestamp and stripped identifiers.

    Notes
    -----
    The file has no header; the column order follows BSEE's field
    definitions. Volumes are in barrels and thousand cubic feet, as reported;
    ``production_date`` is ``YYYYMM``. Leading blanks in the lease number
    (``" 00016"``) are stripped so the key joins across years.
    """
    if isinstance(source, str) and "\n" in source:
        handle = io.StringIO(source)
    elif str(source).endswith(".zip"):
        archive = zipfile.ZipFile(source)
        handle = io.TextIOWrapper(archive.open(archive.namelist()[0]), encoding="latin-1")
    else:
        handle = open(source, encoding="latin-1")
    frame = pd.read_csv(handle, header=None, names=OGORA_COLUMNS, dtype=str, keep_default_na=False)
    for column in OGORA_NUMERIC:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in ["lease_number", "completion_name", "product_code", "well_status", "area_block",
                   "operator_name", "field_name_code", "first_prod_date"]:
        frame[column] = frame[column].str.strip()
    frame["month"] = pd.to_datetime(frame["production_date"].str.strip(), format="%Y%m", errors="coerce")
    return frame


def lease_monthly(completions):
    """Aggregate completion-months to lease-months.

    Parameters
    ----------
    completions : pandas.DataFrame
        Output of ``read_ogora`` (one or several years concatenated).

    Returns
    -------
    pandas.DataFrame
        One row per (``lease_number``, ``month``): ``oil_bbl``, ``gas_mcf``,
        ``water_bbl`` summed over completions, ``days_on_prod`` (the most
        any completion produced), ``n_completions``, ``n_producing`` (with
        oil or gas above zero), ``operator_name`` and ``area_block`` (the
        most frequent in the month), ``producing`` (any oil or gas).

    Notes
    -----
    The lease is the unit the candidates are anchored to (a redevelopment is
    decided per lease), so volumes are summed across its completions; the
    water and injection volumes are kept because the water ratio is a
    decline feature.
    """
    grouped = completions.groupby(["lease_number", "month"], sort=True)
    out = grouped.agg(oil_bbl=("oil_bbl", "sum"), gas_mcf=("gas_mcf", "sum"), water_bbl=("water_bbl", "sum"),
                      injection_bbl=("injection_bbl", "sum"), days_on_prod=("days_on_prod", "max"),
                      n_completions=("completion_name", "size"),
                      operator_name=("operator_name", lambda s: s.mode().iloc[0] if len(s.mode()) else ""),
                      area_block=("area_block", lambda s: s.mode().iloc[0] if len(s.mode()) else "")).reset_index()
    producing = completions.assign(p=(completions["oil_bbl"].fillna(0) > 0) | (completions["gas_mcf"].fillna(0) > 0))
    out["n_producing"] = producing.groupby(["lease_number", "month"])["p"].sum().to_numpy()
    out["producing"] = (out["oil_bbl"] > 0) | (out["gas_mcf"] > 0)
    return out


# --- EIA monthly spot prices and eGRID -----------------------------------------

def fetch_eia_prices(out_dir=paths.RAW_PRICES, force=False):
    """Download the WTI and Henry Hub monthly workbooks and record their hashes."""
    rows = []
    for name, (url, filename) in config.EIA_PRICE_FILES.items():
        path = download(url, out_dir / filename, force=force)
        rows.append({"series": name, "file": filename, "bytes": path.stat().st_size, "sha256": sha256(path)})
    record_hashes(out_dir)
    return pd.DataFrame(rows)


def read_eia_monthly_price(path, name):
    """Read an EIA ``hist_xls`` monthly workbook into ``month``, ``<name>``.

    Notes
    -----
    Sheet ``Data 1`` has two title rows; the date column holds the 15th of
    each month, which is normalised to the first so it joins the other
    monthly tables.
    """
    frame = pd.read_excel(path, sheet_name="Data 1", header=2)
    frame.columns = ["month", name]
    frame["month"] = pd.to_datetime(frame["month"]).dt.to_period("M").dt.to_timestamp()
    return frame.dropna().reset_index(drop=True)


def fetch_egrid(out_dir=paths.RAW_EGRID, force=False):
    """Download the eGRID workbook and record its hash."""
    path = download(config.EGRID_URL, out_dir / config.EGRID_FILENAME, force=force)
    record_hashes(out_dir)
    return path


def read_egrid_plants(path, state=config.EIA923_STATE):
    """Plant-level eGRID rows of one state with tidy column names."""
    frame = pd.read_excel(path, sheet_name=config.EGRID_PLANT_SHEET, header=1, usecols=list(EGRID_PLANT_COLUMNS))
    frame = frame.rename(columns=EGRID_PLANT_COLUMNS)
    return frame[frame["state"] == state].reset_index(drop=True)


# --- EIA-923 through the API ---------------------------------------------------

def pull_eia923(state=config.EIA923_STATE, start=config.EIA923_START, end=config.EIA923_END,
                out_dir=paths.RAW_EIA923, key=None, force=False):
    """Download EIA-923 plant × fuel × prime-mover monthly rows for one state, page by page, with a cache.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)
        The rows (numeric fields converted) and a pull log with ``total``,
        ``rows``, ``pages`` and ``from_cache``.

    Notes
    -----
    Same discipline as ``eia_api.pull_generators``: every page is saved as
    returned, checked not to contain the key, and the parquet is rebuilt from
    the pages. Rows with ``fuelType == "ALL"`` or ``primeMover == "ALL"`` are
    EIA's own subtotals and are kept, flagged by those values, so the panel
    can choose the grain it needs without double counting.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"eia923_{state}_{start[:4]}-{end[:4]}"
    parquet, log_file = out_dir / f"{stem}.parquet", out_dir / f"{stem}_pull_log.json"
    if parquet.exists() and log_file.exists() and not force:
        return pd.read_parquet(parquet), {**json.loads(log_file.read_text(encoding="utf-8")), "from_cache": True}
    key = key or eia_api.load_api_key()
    url = f"{config.EIA_API_BASE}/{config.EIA923_ROUTE}/data/"
    params = {"frequency": "monthly", "data[]": config.EIA923_DATA_FIELDS, "facets[state][]": state,
              "start": start, "end": end, "length": config.EIA_PAGE_LENGTH,
              "sort[0][column]": "period", "sort[0][direction]": "asc",
              "sort[1][column]": "plantCode", "sort[1][direction]": "asc"}
    rows, offset, page, total = [], 0, 0, None
    while total is None or offset < total:
        body = eia_api._get(url, {**params, "offset": offset}, key)
        text = json.dumps(body)
        if key in text:
            raise RuntimeError("API response contains the key; page not saved.")
        (out_dir / f"api_{state}_{start[:4]}-{end[:4]}_page{page}.json").write_text(text, encoding="utf-8")
        data = body["response"]["data"]
        total = int(body["response"]["total"])
        if not data:
            break
        rows.extend(data)
        offset += len(data)
        page += 1
    table = pd.DataFrame(rows)
    for column in config.EIA923_DATA_FIELDS:
        table[column] = pd.to_numeric(table[column], errors="coerce")
    table.to_parquet(parquet, index=False)
    log = {"state": state, "start": start, "end": end, "total": total, "rows": len(table), "pages": page}
    log_file.write_text(json.dumps(log, indent=2), encoding="utf-8")
    return table, {**log, "from_cache": False}


def generation_monthly(eia923):
    """Plant × prime-mover monthly generation at EIA's reported grain, with the candidate technology.

    Notes
    -----
    EIA reports fuel-specific rows per prime mover and "ALL" subtotals (all
    fuels of a prime mover, all prime movers of a plant). The fuel-specific
    rows are summed per (plant, prime mover, month), so every megawatt-hour
    is counted once and the grain stays plant × prime mover, never a
    generator (PLAN.md §14.2). ``technology`` comes from
    ``config.PRIME_MOVER_TECH``; other prime movers are labelled "Other".
    """
    rows = eia923[(eia923["fuelType"] != "ALL") & (eia923["primeMover"] != "ALL")].copy()
    rows["month"] = pd.to_datetime(rows["period"], format="%Y-%m")
    rows["plant_code"] = pd.to_numeric(rows["plantCode"], errors="coerce").astype("Int64")
    out = (rows.groupby(["plant_code", "plantName", "primeMover", "month"], sort=True)
           .agg(generation_mwh=("generation", "sum"), gross_generation_mwh=("gross-generation", "sum"),
                consumption_mmbtu=("total-consumption-btu", "sum"),
                consumption_for_eg_mmbtu=("consumption-for-eg-btu", "sum"), n_fuels=("fuelType", "nunique"))
           .reset_index().rename(columns={"plantName": "plant_name", "primeMover": "prime_mover"}))
    out.insert(3, "technology", out["prime_mover"].map(config.PRIME_MOVER_TECH).fillna("Other"))
    return out


# --- ERCOT 2024 files ---------------------------------------------------------

def verify_ercot_files(folder=paths.RAW_ERCOT):
    """Check the five ERCOT 2024 files against the hashes pinned in ``config``.

    Returns
    -------
    pandas.DataFrame
        ``file``, ``present``, ``sha256_ok``.
    """
    rows = []
    for name, expected in config.ERCOT_2024_FILES.items():
        path = folder / name
        rows.append({"file": name, "present": path.exists(), "sha256_ok": path.exists() and sha256(path) == expected})
    return pd.DataFrame(rows)


def ercot_dam_monthly(path, hubs=config.ERCOT_HUBS):
    """Monthly mean day-ahead price per trading hub from the hourly 2024 file.

    Notes
    -----
    The gridstatus layout: ``Interval Start`` (tz-aware, US/Central),
    ``Location``, ``SPP`` ($/MWh). The monthly mean of hourly prices is the
    flat-price basis of the market table; capture factors by technology are
    derived in notebook 07 from the same hourly file.
    """
    frame = pd.read_parquet(path)
    frame = frame[frame["Location"].isin(hubs)].copy()
    frame["month"] = frame["Interval Start"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    out = frame.groupby(["month", "Location"])["SPP"].mean().unstack("Location").reset_index()
    out.columns.name = None
    return out


# --- the manifest -------------------------------------------------------------

def manifest_entry(source_id, name, url, files, vintage, units, grain, provenance="OBSERVED", note=""):
    """One manifest record (PLAN.md §14.1): URL, retrieval time, vintage, checksums, units, grain."""
    if provenance not in config.PROVENANCE:
        raise ValueError(f"provenance must be one of {config.PROVENANCE}")
    return {"source_id": source_id, "name": name, "url": url,
            "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "files": {p.name: sha256(p) for p in files}, "vintage": vintage, "units": units, "grain": grain,
            "provenance": provenance, "note": note}


def write_manifest(entries, path=paths.MANIFEST_V5):
    """Write the manifest as JSON; return the path."""
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# --- BLS CPI-U (real dollars) --------------------------------------------------

def fetch_cpi(years=config.CPI_YEARS, out_dir=paths.RAW_PRICES, force=False):
    """Pull the CPI-U monthly index from the BLS public API and save the response as returned.

    Returns
    -------
    pathlib.Path
        ``bls_<series>_<first>-<last>.json``.

    Notes
    -----
    The unregistered API allows ten years per call, enough for the 2016–2024
    window; the JSON is kept so the deflator is reproducible offline.
    """
    path = out_dir / f"bls_{config.CPI_SERIES}_{years[0]}-{years[1]}.json"
    if path.exists() and not force:
        return path
    out_dir.mkdir(parents=True, exist_ok=True)
    response = requests.post(config.BLS_API_URL, json={"seriesid": [config.CPI_SERIES], "startyear": str(years[0]),
                                                       "endyear": str(years[1])}, timeout=60)
    response.raise_for_status()
    body = response.json()
    if body.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API: {body.get('status')} {body.get('message')}")
    path.write_text(json.dumps(body, indent=1), encoding="utf-8")
    record_hashes(out_dir)
    return path


def read_cpi(path):
    """Monthly CPI-U from a saved BLS response: ``month``, ``cpi_u``."""
    rows = json.loads(path.read_text(encoding="utf-8"))["Results"]["series"][0]["data"]
    frame = pd.DataFrame([{"month": pd.Timestamp(int(r["year"]), int(r["period"][1:]), 1), "cpi_u": float(r["value"])}
                          for r in rows if r["period"].startswith("M")])
    return frame.sort_values("month").reset_index(drop=True)


def to_real(nominal, months, cpi, base_year=config.REAL_DOLLAR_YEAR):
    """Convert a nominal monthly series to ``base_year`` dollars with the CPI-U.

    Notes
    -----
    Each value is scaled by the base year's mean index over its own month's
    index, so a 2018 price reads in 2024 purchasing power.
    """
    index = cpi.set_index("month")["cpi_u"]
    base = index[index.index.year == base_year].mean()
    return nominal.to_numpy(float) * base / index.reindex(pd.DatetimeIndex(months)).to_numpy(float)


# --- audits of the panel (rules R10–R13, numbered after the queue file's R1–R9) ---

def panel_audits(lease, generation, market, window=config.V5_COVERAGE):
    """Count what each audit rule touches; the panel is never changed by them.

    Returns
    -------
    pandas.DataFrame
        ``rule``, ``item``, ``rows``, ``note``.

    Notes
    -----
    R10: duplicate keys in the lease-month and plant × prime-mover-month tables
    (must be zero, the joins are one-to-many by construction). R11: negative
    volumes (not expected) and zero-production lease-months (kept, flagged
    ``producing``). R12: plant-months with negative net generation (batteries
    and pumped storage draw more than they send; kept, it is their physics).
    R13: months missing from each market series inside the coverage window.
    """
    start, end = pd.Timestamp(window[0]), pd.Timestamp(window[1])
    months = pd.date_range(start, end, freq="MS")
    rows = [
        ("R10", "duplicate (lease, month) keys", int(lease.duplicated(["lease_number", "month"]).sum()), "must be 0"),
        ("R10", "duplicate (plant, prime mover, month) keys",
         int(generation.duplicated(["plant_code", "prime_mover", "month"]).sum()), "must be 0"),
        ("R11", "lease-months with a negative volume",
         int((lease[["oil_bbl", "gas_mcf", "water_bbl"]] < 0).any(axis=1).sum()), "not expected"),
        ("R11", "lease-months with zero oil and gas", int((~lease["producing"]).sum()), "kept; flagged producing = False"),
        ("R12", "plant-months with negative net generation", int((generation["generation_mwh"] < 0).sum()),
         "kept; storage and pumped hydro draw power"),
    ]
    for column in [c for c in market.columns if c not in ("month",) and market[c].dtype.kind == "f"]:
        have = market.loc[market["month"].between(start, end) & market[column].notna(), "month"]
        rows.append(("R13", f"{column}: months missing in {window[0]}→{window[1]}", int(len(months) - have.nunique()),
                     "must be 0 for every priced month"))
    return pd.DataFrame(rows, columns=["rule", "item", "rows", "note"])
