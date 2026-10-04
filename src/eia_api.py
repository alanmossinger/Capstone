"""Pull the EIA-860M inventory of operable generators through the EIA API v2.

What: reads the route metadata (latest month available) and downloads one
month of the route ``electricity/operating-generator-capacity`` page by page.
Why: EIA-860M carries generator operating dates, county and coordinates for
every region, which the public LBNL file lacks outside CAISO/ERCOT/PJM
(PLAN.md §5.1, source S2).
Reads: the API key from ``.env`` (``EIA_API_KEY``); the EIA API.
Writes: ``data/raw/eia860m/api_<period>_page<N>.json`` (one file per page,
as returned) and ``data/raw/eia860m/eia860m_<period>.parquet`` (all pages).
Used by: notebook 01 (and notebook 10 for the linkage stretch).

The key is personal. It is passed only as a request parameter and is never
printed, logged, stored in a page file or put in an error message.
"""

import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from src import config, paths

_NUMERIC_FIELDS = ["nameplate-capacity-mw", "latitude", "longitude"]

# One line per column of the pulled table, for the data dictionary (data/README.md).
FIELD_DESCRIPTIONS = {
    "period": "inventory month (YYYY-MM)",
    "stateid": "state postal code",
    "stateName": "state name",
    "sector": "EIA sector code (electric utility, IPP, commercial, industrial …)",
    "sectorName": "EIA sector name",
    "entityid": "EIA id of the operating entity",
    "entityName": "name of the operating entity",
    "plantid": "EIA plant code",
    "plantName": "plant name",
    "generatorid": "generator id within the plant",
    "technology": "EIA technology description (crosswalked to LBNL type_clean)",
    "energy_source_code": "primary energy source code",
    "energy-source-desc": "primary energy source description",
    "prime_mover_code": "prime mover code (PV, WT, CT, CA, ST, BA …)",
    "balancing_authority_code": "balancing authority code (e.g. ERCO, PJM, CISO)",
    "balancing-authority-name": "balancing authority name",
    "status": "operating status: OP operating, SB standby, OS/OA out of service",
    "statusDescription": "operating status description",
    "nameplate-capacity-mw": "nameplate capacity (MW)",
    "operating-year-month": "month the generator entered commercial operation (YYYY-MM)",
    "planned-retirement-year-month": "planned retirement month, if reported",
    "county": "county of the plant",
    "latitude": "plant latitude (decimal degrees)",
    "longitude": "plant longitude (decimal degrees)",
    "unit": "unit code grouping generators of one combined-cycle unit",
    "nameplate-capacity-mw-units": "units of nameplate capacity (MW)",
}


def load_api_key():
    """Return the EIA API key from ``.env`` without revealing it.

    Returns
    -------
    str
        The key.

    Raises
    ------
    RuntimeError
        If ``EIA_API_KEY`` is missing or empty.

    Notes
    -----
    ``load_dotenv`` does not override a variable already set in the shell,
    so a key exported in the environment also works.
    """
    load_dotenv(paths.ENV_FILE)
    key = os.environ.get("EIA_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "EIA_API_KEY is not set. Create .env in the repository root with the "
            "line EIA_API_KEY=<your key from https://www.eia.gov/opendata/register.php>."
        )
    return key


def _get(url, params, key):
    """GET an API url and return the JSON body, with any key scrubbed from errors.

    Notes
    -----
    ``requests`` puts the full URL (key included) in its exception text, so
    exceptions are re-raised as a short ``RuntimeError`` built only from the
    status code and the API's own message, with the original chain dropped.
    """
    try:
        response = requests.get(url, params={**params, "api_key": key},
                                timeout=config.EIA_TIMEOUT_S)
    except requests.RequestException as err:
        raise RuntimeError(f"EIA API request failed ({type(err).__name__}).") from None
    if response.status_code != 200:
        message = response.text[:300].replace(key, "<key>")
        raise RuntimeError(f"EIA API returned HTTP {response.status_code}: {message}") from None
    return response.json()


def fetch_route_metadata(key=None):
    """Describe the route: first and last month, facets and data fields.

    Parameters
    ----------
    key : str, optional
        API key; read from ``.env`` when omitted.

    Returns
    -------
    dict
        ``start_period``, ``end_period`` (``"YYYY-MM"``), ``facets`` and
        ``data_fields`` (lists of ids).
    """
    key = key or load_api_key()
    body = _get(f"{config.EIA_API_BASE}/{config.EIA_ROUTE}/", {}, key)["response"]
    return {
        "start_period": body["startPeriod"],
        "end_period": body["endPeriod"],
        "facets": [facet["id"] for facet in body["facets"]],
        "data_fields": list(body["data"].keys()),
    }


def pull_generators(period, out_dir=paths.RAW_EIA860M, key=None, force=False):
    """Download every generator row for one month, page by page, with a cache.

    Parameters
    ----------
    period : str
        Month to pull, ``"YYYY-MM"`` (normally the route's latest period).
    out_dir : pathlib.Path
        Folder for page files and the combined parquet.
    key : str, optional
        API key; read from ``.env`` when omitted.
    force : bool
        Pull again even if the parquet for ``period`` already exists.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)
        The generator table and a pull log with ``total`` (rows the API says
        exist), ``rows`` (rows received), ``pages`` and ``from_cache``.

    Notes
    -----
    The API serves at most 5,000 rows per call, so ``offset`` advances until
    the reported ``total`` is reached. Each page is saved exactly as
    returned so the raw layer can be audited; the page JSON is checked not to
    contain the key before it is written. Numeric fields arrive as strings
    and are converted here; nothing else is changed.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet = out_dir / f"eia860m_{period}.parquet"
    log_file = out_dir / f"eia860m_{period}_pull_log.json"
    if parquet.exists() and log_file.exists() and not force:
        log = json.loads(log_file.read_text(encoding="utf-8"))
        return pd.read_parquet(parquet), {**log, "from_cache": True}

    key = key or load_api_key()
    url = f"{config.EIA_API_BASE}/{config.EIA_ROUTE}/data/"
    params = {"frequency": "monthly", "data[]": config.EIA_DATA_FIELDS,
              "start": period, "end": period, "length": config.EIA_PAGE_LENGTH,
              "sort[0][column]": "plantid", "sort[0][direction]": "asc",
              "sort[1][column]": "generatorid", "sort[1][direction]": "asc"}

    rows, offset, page, total = [], 0, 0, None
    while total is None or offset < total:
        body = _get(url, {**params, "offset": offset}, key)
        text = json.dumps(body)
        if key in text:  # defensive: the API does not echo the key today
            raise RuntimeError("API response contains the key; page not saved.")
        (out_dir / f"api_{period}_page{page}.json").write_text(text, encoding="utf-8")
        data = body["response"]["data"]
        total = int(body["response"]["total"])
        if not data:
            break
        rows.extend(data)
        offset += len(data)
        page += 1

    table = pd.DataFrame(rows)
    for column in _NUMERIC_FIELDS:
        table[column] = pd.to_numeric(table[column], errors="coerce")
    table.to_parquet(parquet, index=False)
    log = {"period": period, "total": total, "rows": len(table), "pages": page}
    log_file.write_text(json.dumps(log, indent=2), encoding="utf-8")
    return table, {**log, "from_cache": False}


def technology_crosswalk(generators):
    """Map every EIA technology in a pull to an LBNL ``type_clean`` group.

    Parameters
    ----------
    generators : pandas.DataFrame
        Output of ``pull_generators``.

    Returns
    -------
    pandas.DataFrame
        ``eia_technology``, ``type_clean``, ``note``, ``n_generators`` and
        ``nameplate_gw``, largest capacity first. Technologies missing from
        ``config.EIA_TECHNOLOGY_MAP`` are put in "Other" with a note saying
        so, which makes a new EIA category visible instead of silent.
    """
    summary = (generators.groupby("technology")
               .agg(n_generators=("generatorid", "size"),
                    nameplate_gw=("nameplate-capacity-mw", lambda mw: mw.sum() / 1000))
               .reset_index().rename(columns={"technology": "eia_technology"}))
    unmapped = ("Other", "NOT IN MAP: new EIA technology, defaulted to Other")
    mapped = summary["eia_technology"].map(lambda t: config.EIA_TECHNOLOGY_MAP.get(t, unmapped))
    summary["type_clean"] = mapped.str[0]
    summary["note"] = mapped.str[1]
    columns = ["eia_technology", "type_clean", "note", "n_generators", "nameplate_gw"]
    return summary[columns].sort_values("nameplate_gw", ascending=False, ignore_index=True)
