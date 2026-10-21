"""Obtain the frozen LBNL queue file, verify it, and load its project sheet.

What: places ``lbnl_ix_queue_data_file_thru2024_v2.xlsx`` in ``data/raw/lbnl/``,
checks its SHA-256 against the hash recorded in ``config``, writes
``SHA256.txt`` next to it, and reads sheet ``03. Complete Queue Data``.
Why: every result depends on one exact release of the file (decision #2), so
the file is never silently replaced and its identity is provable.
Reads: https://emp.lbl.gov/queues (only when the file is not on disk yet).
Writes: ``data/raw/lbnl/<file>.xlsx`` and ``data/raw/lbnl/SHA256.txt``.
Used by: notebook 01 (part A).

The LBNL site sits behind a bot filter that usually refuses scripted
requests. When that happens ``download()`` stops with instructions for the
manual fallback: download the file in a browser and save it in
``data/raw/lbnl/``. The checksum then proves it is the same file.
"""

import hashlib
import re
from urllib.parse import urljoin

import pandas as pd
import requests

from src import config, paths

_BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0 (research download; queue-survival)"}


def sha256(path):
    """Return the SHA-256 hex digest of a file.

    Parameters
    ----------
    path : pathlib.Path
        File to hash.

    Returns
    -------
    str
        64-character lowercase hex digest.

    Notes
    -----
    Reads in 1 MB blocks so memory use does not depend on file size.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def find_file_links(page_html, base_url=config.LBNL_PAGE_URL):
    """List the queue-data workbook links on the LBNL landing page.

    Parameters
    ----------
    page_html : str
        HTML of https://emp.lbl.gov/queues.
    base_url : str
        Used to turn relative links into absolute ones.

    Returns
    -------
    list of str
        Absolute URLs of ``.xlsx`` files whose name contains ``queue_data``.

    Notes
    -----
    A regular expression is enough here: the page links the workbook with a
    plain ``href``. Returning every match lets the caller notice a newer
    release (a different file name) without switching to it.
    """
    links = re.findall(r'href="([^"]+\.xlsx)"', page_html, flags=re.IGNORECASE)
    return sorted({urljoin(base_url, link) for link in links if "queue_data" in link.lower()})


def check_for_newer_release():
    """Look at the LBNL page and report whether a different queue file is offered.

    Returns
    -------
    dict
        ``status`` is ``"same"``, ``"newer"`` or ``"unreachable"``; ``links``
        lists the workbook URLs found; ``detail`` explains an unreachable page.

    Notes
    -----
    Never downloads or switches anything. A ``"newer"`` result is written to
    ``docs/decisions.md`` as an open item for Alan (decision #2).
    """
    try:
        response = requests.get(config.LBNL_PAGE_URL, headers=_BROWSER_HEADERS, timeout=60)
    except requests.RequestException as err:
        return {"status": "unreachable", "links": [], "detail": type(err).__name__}
    if response.status_code != 200 or "queue" not in response.text.lower():
        return {"status": "unreachable", "links": [],
                "detail": f"HTTP {response.status_code} (bot filter or page change)"}
    links = find_file_links(response.text)
    names = [link.rsplit("/", 1)[-1] for link in links]
    newer = [name for name in names if name != config.LBNL_FILENAME]
    return {"status": "newer" if newer else "same", "links": links, "detail": ""}


def download(dest_dir=paths.RAW_LBNL):
    """Make sure the frozen LBNL workbook is on disk and verified.

    Parameters
    ----------
    dest_dir : pathlib.Path
        Folder for the raw file (``data/raw/lbnl/`` by default).

    Returns
    -------
    pathlib.Path
        Path of the verified workbook.

    Raises
    ------
    RuntimeError
        If the file on disk does not match the recorded hash, or if it is
        missing and cannot be downloaded (manual instructions included).

    Notes
    -----
    A file already on disk is never overwritten: the release is frozen, so a
    hash mismatch is an error to investigate, not something to repair by
    downloading again. ``SHA256.txt`` is (re)written so the hash travels with
    the file.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / config.LBNL_FILENAME

    if not target.exists():
        _try_scripted_download(target)

    digest = sha256(target)
    if digest != config.LBNL_SHA256:
        raise RuntimeError(
            f"{target.name} has SHA-256 {digest}, expected {config.LBNL_SHA256}. "
            "The frozen release was replaced; restore the original file (decision #2)."
        )
    record_hash(dest_dir / "SHA256.txt", target.name, digest)
    return target


def record_hash(path, name, digest):
    """Write ``digest  name`` into a hash file, replacing the line for ``name`` and keeping every other file's line.

    Notes
    -----
    The file used to be rewritten with one line, so adding the 2026 edition
    (decision #43) and the 2024 edition (decision #101) alongside the frozen
    2025 file dropped the others' hashes each time one was downloaded.
    """
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []
    kept = [l for l in lines if l.split()[-1] != name]
    path.write_text("".join(l + "\n" for l in kept + [f"{digest}  {name}"]), encoding="utf-8")


def _try_scripted_download(target):
    """Fetch the workbook from the LBNL page, or explain the manual fallback."""
    manual = (
        f"Download {config.LBNL_FILENAME} by hand from {config.LBNL_PAGE_URL} "
        f"and save it as {target}. Then run this cell again."
    )
    release = check_for_newer_release()
    wanted = [link for link in release["links"] if link.endswith(config.LBNL_FILENAME)]
    if not wanted:
        raise RuntimeError(f"Scripted download not possible ({release['status']} "
                           f"{release['detail']}). {manual}")
    response = requests.get(wanted[0], headers=_BROWSER_HEADERS, timeout=300)
    if response.status_code != 200:
        raise RuntimeError(f"Download returned HTTP {response.status_code}. {manual}")
    target.write_bytes(response.content)


def load_queue(path):
    """Read the project-level sheet exactly as published.

    Parameters
    ----------
    path : pathlib.Path
        The verified workbook.

    Returns
    -------
    pandas.DataFrame
        36,441 rows × 31 columns for the frozen release; dates are still
        Excel serial numbers (converted by rule R1 in notebook 01 (part B)).

    Notes
    -----
    ``header=1`` skips the title banner in row 0. No cleaning happens here so
    that the audit in notebook 01 (part A) describes the file as LBNL published it.
    """
    return pd.read_excel(path, sheet_name=config.LBNL_SHEET, header=config.LBNL_HEADER_ROW)
