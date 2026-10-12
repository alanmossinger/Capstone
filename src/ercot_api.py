"""Pull ERCOT public-report prices through the ERCOT Public API (api.ercot.com).

What: signs in to ERCOT's B2C identity service for a one-hour bearer token,
then reads a public report page by page (5,000 rows) with the subscription
key. Reports used: NP4-190-CD (day-ahead settlement point prices, hourly),
NP6-905-CD (real-time settlement point prices, 15-minute) and NP4-188-CD
(day-ahead ancillary-service clearing prices).
Why: hourly ERCOT prices for 2018–2023 are the market basis of the power
candidates (PLAN.md §14.1, source S7). ercot.com's report servlet refuses
this machine (decision #53); api.ercot.com is a different host, so the first
call is a test of whether the pull can run here at all.
Reads: ``ERCOT_SUBSCRIPTION_KEY``, ``ERCOT_USERNAME``, ``ERCOT_PASSWORD``
from ``.env``.
Writes: ``data/raw/ercot/ercot_dam_spp_<year>.parquet`` and ``SHA256.txt``
(``pull_dam_years``; ``python -m src.ercot_api 2018 2023`` from a network
ERCOT's edge accepts).
Used by: notebook 01 (the v5 sources, part D).

Adapted from my own ``MADS_Milestone2/src/price_loader.py`` (self-reuse,
credited in the statement of work): the sign-in flow and the paging loop are
the same; the report table, the settlement-point filter, the block detection
and the secret scrubbing are new.

The three credentials are passed only in the sign-in form body and in request
headers. They are never printed, logged, written to a file or put in an error
message: every exception raised here is built from the status code and a
scrubbed excerpt of the response.
"""

import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

from src import config, paths

_TOKEN = {"value": None, "expires": 0.0}  # one bearer token per process; ERCOT issues no refresh token


def load_credentials():
    """Return (subscription key, username, password) from ``.env`` without revealing them.

    Raises
    ------
    RuntimeError
        If any of the three variables is missing or empty.

    Notes
    -----
    ``load_dotenv`` does not override variables already set in the shell, so
    values exported in the environment also work. The message names the
    variables, never their values.
    """
    load_dotenv(paths.ENV_FILE)
    values = [os.environ.get(name, "").strip()
              for name in ("ERCOT_SUBSCRIPTION_KEY", "ERCOT_USERNAME", "ERCOT_PASSWORD")]
    if not all(values):
        raise RuntimeError(
            "ERCOT credentials are not set. Register at https://apiexplorer.ercot.com/ "
            "(Products -> ERCOT Public API -> Subscribe; Profile -> Show for the key) and put "
            "ERCOT_SUBSCRIPTION_KEY, ERCOT_USERNAME and ERCOT_PASSWORD in .env.")
    return tuple(values)


def _scrub(text, secrets):
    """Replace every secret that might appear in ``text`` by ``<secret>``."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<secret>")
    return text


def _blocked(response):
    """True when the body is the Incapsula interstitial that ERCOT's edge serves to this machine."""
    return "_Incapsula_Resource" in response.text[:2000]


def _id_token(credentials):
    """Mint (or reuse) the bearer token; valid one hour, no refresh.

    Notes
    -----
    The flow is ERCOT's published resource-owner-password flow on Azure B2C.
    The password travels only in this form body. A failed sign-in is reported
    with the status code and B2C's error code, scrubbed of the credentials.
    """
    now = time.time()
    if _TOKEN["value"] and now < _TOKEN["expires"] - 120:
        return _TOKEN["value"]
    key, user, password = credentials
    try:
        response = requests.post(config.ERCOT_TOKEN_URL, timeout=config.ERCOT_TIMEOUT_S, data={
            "grant_type": "password", "username": user, "password": password,
            "client_id": config.ERCOT_CLIENT_ID, "response_type": "id_token",
            "scope": f"openid {config.ERCOT_CLIENT_ID} offline_access"})
    except requests.RequestException as err:
        raise RuntimeError(f"ERCOT sign-in request failed ({type(err).__name__}).") from None
    if response.status_code != 200:
        excerpt = _scrub(response.text[:200], (key, user, password))
        raise RuntimeError(f"ERCOT sign-in refused (HTTP {response.status_code}): {excerpt}") from None
    token = response.json().get("id_token")
    if not token:
        raise RuntimeError("ERCOT sign-in returned no id_token.")
    _TOKEN.update(value=token, expires=now + 3600.0)
    return token


def fetch_page(report, params, page=1, size=config.ERCOT_PAGE_SIZE, credentials=None):
    """GET one page of a report and return the parsed JSON body.

    Parameters
    ----------
    report : str
        EMIL report id, a key of ``config.ERCOT_REPORTS`` (e.g. ``"NP4-190-CD"``).
    params : dict
        Report filters such as ``deliveryDateFrom``, ``deliveryDateTo``,
        ``settlementPoint``.
    page, size : int
        Page number (1-based) and rows per page (API maximum 5,000).
    credentials : tuple, optional
        From ``load_credentials``; read from ``.env`` when omitted.

    Returns
    -------
    dict
        The API body: ``_meta`` (``totalRecords``, ``totalPages``, …),
        ``fields`` (column descriptors) and ``data`` (rows as lists).

    Raises
    ------
    RuntimeError
        With a scrubbed message on a network-edge block (Incapsula), an
        authorisation failure or any non-200 status.
    """
    credentials = credentials or load_credentials()
    key = credentials[0]
    url = f"{config.ERCOT_API_BASE}/{config.ERCOT_REPORTS[report]}"
    headers = {"Ocp-Apim-Subscription-Key": key,
               "Authorization": f"Bearer {_id_token(credentials)}",
               "Accept": "application/json"}
    try:
        response = requests.get(url, params={**params, "page": page, "size": size},
                                headers=headers, timeout=config.ERCOT_TIMEOUT_S)
    except requests.RequestException as err:
        raise RuntimeError(f"ERCOT API request failed ({type(err).__name__}).") from None
    if _blocked(response):
        raise RuntimeError(
            f"ERCOT API blocked at the network edge (Incapsula interstitial, HTTP "
            f"{response.status_code}); the pull has to run from another network.") from None
    if response.status_code != 200:
        excerpt = _scrub(response.text[:200], credentials + (_TOKEN["value"],))
        raise RuntimeError(f"ERCOT API returned HTTP {response.status_code}: {excerpt}") from None
    if any(secret in response.text for secret in credentials):  # defensive; the API does not echo them
        raise RuntimeError("ERCOT response contains a credential; page discarded.")
    return response.json()


def page_to_frame(body):
    """Turn one API body into a DataFrame with the API's own column names."""
    columns = [field["name"] for field in body.get("fields", [])]
    return pd.DataFrame(body.get("data", []), columns=columns)


def pull_report(report, params, max_pages=None, pause_s=0.5, credentials=None):
    """Read every page of a report for the given filters.

    Parameters
    ----------
    report : str
        EMIL report id, a key of ``config.ERCOT_REPORTS``.
    params : dict
        Report filters (see ``fetch_page``).
    max_pages : int, optional
        Stop after this many pages (the probe reads one); all pages when omitted.
    pause_s : float
        Seconds between pages, to stay polite.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)
        The rows and a log with ``total_records``, ``total_pages`` and
        ``pages_read``.

    Notes
    -----
    Rows arrive as lists in the order of ``fields``; nothing is renamed here,
    so the raw layer keeps the API's names. Day-ahead prices are hourly with
    ``hourEnding`` 01:00–24:00 in local prevailing time (``config.ERCOT_TZ``).
    """
    credentials = credentials or load_credentials()
    frames, page, total_pages, total_records = [], 1, None, 0
    while total_pages is None or page <= total_pages:
        body = fetch_page(report, params, page=page, credentials=credentials)
        meta = body.get("_meta", {})
        total_pages = int(meta.get("totalPages", 1))
        total_records = int(meta.get("totalRecords", 0))
        frames.append(page_to_frame(body))
        if max_pages and page >= max_pages:
            break
        page += 1
        time.sleep(pause_s)
    table = pd.concat(frames, ignore_index=True)
    return table, {"report": report, "total_records": total_records,
                   "total_pages": total_pages, "pages_read": len(frames)}


def dam_spp(start, end, settlement_point, max_pages=None, credentials=None):
    """Day-ahead settlement point prices (NP4-190-CD) for one point over [start, end].

    Parameters
    ----------
    start, end : str
        Delivery dates ``YYYY-MM-DD``, inclusive.
    settlement_point : str
        E.g. ``"HB_HOUSTON"``.

    Returns
    -------
    tuple of (pandas.DataFrame, dict)
        As ``pull_report``.
    """
    params = {"deliveryDateFrom": start, "deliveryDateTo": end,
              "settlementPoint": settlement_point}
    return pull_report("NP4-190-CD", params, max_pages=max_pages, credentials=credentials)


def pull_dam_years(years, settlement_points=config.ERCOT_HUBS, out_dir=paths.RAW_ERCOT, force=False):
    """Pull hourly day-ahead prices for whole years and cache one parquet per year, with SHA-256.

    Parameters
    ----------
    years : iterable of int
    settlement_points : list of str
        Hubs to keep (``config.ERCOT_HUBS``); one API query per hub and year.
    out_dir : pathlib.Path
    force : bool
        Pull again even if the year's parquet exists.

    Returns
    -------
    pandas.DataFrame
        One row per (year, settlement point) with the rows received and the file written.

    Notes
    -----
    Each year is written as ``ercot_dam_spp_<year>.parquet`` with the API's
    own column names, the same layout `Forecast to Dispatch` uses for 2024,
    and its SHA-256 is appended to ``SHA256.txt`` beside it. Run from a
    network ERCOT's edge accepts: ``python -m src.ercot_api 2018 2023``.
    """
    import hashlib

    out_dir.mkdir(parents=True, exist_ok=True)
    credentials = load_credentials()
    log = []
    for year in years:
        target = out_dir / f"ercot_dam_spp_{year}.parquet"
        if target.exists() and not force:
            log.append({"year": year, "settlement_point": "all", "rows": len(pd.read_parquet(target)), "file": target.name, "from_cache": True})
            continue
        frames = []
        for point in settlement_points:
            table, meta = dam_spp(f"{year}-01-01", f"{year}-12-31", point, credentials=credentials)
            frames.append(table)
            log.append({"year": year, "settlement_point": point, "rows": len(table), "file": target.name, "from_cache": False})
            print(f"{year} {point}: {len(table):,} rows in {meta['total_pages']} pages", flush=True)
        pd.concat(frames, ignore_index=True).to_parquet(target, index=False)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        with (out_dir / "SHA256.txt").open("a", encoding="utf-8") as handle:
            handle.write(f"{digest}  {target.name}\n")
    return pd.DataFrame(log)


if __name__ == "__main__":  # python -m src.ercot_api 2018 2023  (first and last year)
    import sys

    first, last = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) == 3 else (2018, 2023)
    print(pull_dam_years(range(first, last + 1)).to_string())
