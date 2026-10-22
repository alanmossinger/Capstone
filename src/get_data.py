"""Get, check and bundle every raw file the pipeline reads.

What: one manifest of the raw inputs (``data/raw_manifest.csv``: source,
path under ``data/raw/``, size, SHA-256), a check of the files on disk
against it, a fetch of every file a script can download, and a zip of
``data/raw/`` for a reader who cannot fetch the rest.
Why: ``data/raw/`` is not committed (the LBNL 2025 file carries no
redistribution grant, data/README.md S1), so a fresh clone needs the inputs
before ``make all``. Some of them cannot be fetched again byte for byte: the
ISO queue snapshots and the EIA-860M pull are dated, EIA revises its monthly
price workbooks, ERCOT refuses connections from outside the United States
and the LBNL pages sit behind a bot check. A fetched file whose hash differs
from the manifest is reported, never used silently; the bundle carries the
exact files the results were computed on.
Reads: ``data/raw/``; ``.env`` (``EIA_API_KEY``, only for the two EIA pulls).
Writes: ``data/raw_manifest.csv`` (``record``); downloads into ``data/raw/``
(``fetch``); ``dist/raw_data_bundle.zip`` (``bundle``).
Used by: ``make get-data``, ``make check-data``; README "How to run".

Usage::

    python -m src.get_data check     # every manifest file present with its hash
    python -m src.get_data fetch     # download what a script can, then check
    python -m src.get_data bundle    # zip data/raw/ for a reader without the sources
    python -m src.get_data record    # rewrite the manifest from the files on disk (author only)
"""

import hashlib
import sys
import zipfile

import pandas as pd

from src import config, paths

MANIFEST = paths.REPO / "data" / "raw_manifest.csv"
BUNDLE = paths.REPO / "dist" / "raw_data_bundle.zip"

# Where each folder of data/raw/ comes from (data/README.md) and how a reader gets it: "script" (fetch downloads it),
# "workflow" (a GitHub workflow on a U.S. runner, because ERCOT refuses other connections) or "hand" (a browser download).
SOURCES = {
    "lbnl/lbnl_ix_queue_data_file_thru2024_v2.xlsx": ("S1", "hand", f"download from {config.LBNL_PAGE_URL} (bot check on the page)"),
    "lbnl/LBNL_Ix_Queue_Data_File_thru2025.xlsx": ("S6", "hand", f"download from {config.LBNL_PAGE_URL} (bot check on the page)"),
    "lbnl/Queued_Up_2026_Edition.pdf": ("S6", "hand", f"download from {config.LBNL_PAGE_URL} (bot check on the page)"),
    "lbnl/queues_2023_clean_data_r1.xlsx": ("S18", "script", config.LBNL_2024_URL),
    "iso/gis_2024/": ("S18", "workflow", "gh workflow run ercot_gis.yml; save the artifact's eight files in data/raw/iso/gis_2024/"),
    "forward/": ("S19", "workflow", "gh workflow run ercot_history.yml -f first_year=2025 -f last_year=2025; save in data/raw/forward/"),
    "bsee/forward/": ("S19", "script", config.BSEE_URL.format(year=2025)),
    "eia860m/": ("S2", "script", "EIA API v2 with EIA_API_KEY in .env"),
    "iso/": ("S7", "hand", "dated snapshots of the CAISO, PJM and ERCOT queues (data/README.md S7); a new download is a different snapshot"),
    "lbnl_costs/": ("S8", "hand", "data/README.md S8"),
    "value/": ("S9/S10", "hand", "data/README.md S9/S10"),
    "geo/": ("S11", "hand", "data/README.md S11"),
    "atb/": ("S12", "script", config.ATB_URL),
    "bsee/": ("S13", "script", config.BSEE_URL),
    "eia923/": ("S14", "script", "EIA API v2 with EIA_API_KEY in .env"),
    "prices/": ("S15", "script", "EIA spot-price workbooks and the BLS API"),
    "ercot/": ("S16", "workflow", "gh workflow run ercot_history.yml -f first_year=2018 -f last_year=2023; the 2024 files as data/README.md S16"),
    "egrid/": ("S17", "script", config.EGRID_URL),
}
SKIP = {"SHA256.txt", "manifest_v5.json"}  # hash records themselves, not inputs


def sha256(path):
    """SHA-256 of a file, read in blocks so the 99 MB EIA-923 folder does not sit in memory at once."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def source_of(relative):
    """The ``SOURCES`` entry of a path under data/raw/: the exact file first, else the longest folder prefix."""
    if relative in SOURCES:
        return SOURCES[relative]
    folders = [k for k in SOURCES if k.endswith("/") and relative.startswith(k)]
    return SOURCES[max(folders, key=len)] if folders else ("?", "hand", "not in data/README.md")


def record():
    """Write the manifest from the files on disk (run by the author once the inputs are final).

    Notes
    -----
    Every file under ``data/raw/`` is listed except the per-folder hash
    records, so the manifest is the complete list of what the results were
    computed on.
    """
    rows = []
    for f in sorted(p for p in paths.DATA_RAW.rglob("*") if p.is_file() and p.name not in SKIP):
        rel = f.relative_to(paths.DATA_RAW).as_posix()
        source, how, where = source_of(rel)
        rows.append({"source": source, "path": rel, "bytes": f.stat().st_size, "sha256": sha256(f), "how": how, "where": where})
    table = pd.DataFrame(rows)
    table.to_csv(MANIFEST, index=False, lineterminator="\n")
    return table


def check():
    """Compare data/raw/ with the manifest; one row per manifest file with ``status`` ok / missing / differs."""
    table = pd.read_csv(MANIFEST)
    status = []
    for rel, digest in zip(table["path"], table["sha256"]):
        f = paths.DATA_RAW / rel
        status.append("missing" if not f.exists() else ("ok" if sha256(f) == digest else "differs"))
    return table.assign(status=status)


def _eia_key_present():
    """Whether .env holds an EIA key; the key itself is never read here, only its presence."""
    from dotenv import dotenv_values

    return bool(dotenv_values(paths.REPO / ".env").get("EIA_API_KEY"))


def fetch():
    """Download every missing file that a script can get, in the pipeline's own fetchers, then check.

    Notes
    -----
    Only missing files are fetched; a file on disk is never overwritten. The
    fetchers are the ones the notebooks use (``energy_data``, ``value``,
    ``eia_api``), so a downloaded file lands where the notebooks read it. A
    failed download is reported with the source's manual route and the run
    goes on to the next source.
    """
    import requests

    from src import eia_api, energy_data as ed, value

    status = check()
    missing = set(status.loc[status["status"] == "missing", "path"])

    def wanted(prefix):
        return any(p.startswith(prefix) for p in missing)

    steps = [
        ("lbnl/queues_2023_clean_data_r1.xlsx", lambda: ed.download(config.LBNL_2024_URL, paths.RAW_LBNL / config.LBNL_2024_FILENAME)),
        ("bsee/forward/", lambda: ed.fetch_ogora((2025, 2025), out_dir=paths.RAW_BSEE / "forward")),
        ("bsee/ogora", lambda: ed.fetch_ogora()),
        ("atb/", lambda: value.fetch_atb()),
        ("egrid/", lambda: ed.fetch_egrid()),
        ("prices/R", lambda: ed.fetch_eia_prices()),
        ("prices/bls", lambda: ed.fetch_cpi()),
    ]
    if _eia_key_present():
        period = next((p.split("_")[1] for p in missing if p.startswith("eia860m/eia860m_") and p.endswith(".parquet")), None)
        if period:
            steps.append(("eia860m/", lambda: eia_api.pull_generators(period)))
        steps.append(("eia923/", lambda: ed.pull_eia923()))
    elif wanted("eia860m/") or wanted("eia923/"):
        print("[skip] EIA-860M and EIA-923 need EIA_API_KEY in .env (copy .env.example)")
    for prefix, step in steps:
        if not wanted(prefix):
            continue
        print(f"[get ] {prefix}", flush=True)
        try:
            step()
        except (requests.RequestException, RuntimeError, OSError) as error:
            print(f"[fail] {prefix}: {error}")
    return check()


def bundle():
    """Zip every manifest file, with the manifest, into ``dist/raw_data_bundle.zip`` (unzip into the repository root).

    Notes
    -----
    The bundle is for a reader who needs the exact inputs (a grader); it is
    not published, because the LBNL 2025 file carries no redistribution grant.
    """
    status = check()
    bad = status[status["status"] != "ok"]
    if len(bad):
        raise SystemExit(f"{len(bad)} manifest files missing or changed; run check first:\n{bad[['path', 'status']].to_string(index=False)}")
    BUNDLE.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(MANIFEST, "data/raw_manifest.csv")
        for rel in status["path"]:
            z.write(paths.DATA_RAW / rel, f"data/raw/{rel}")
    return BUNDLE


def report(status):
    """Print the check by source and list what is not ok with its route; return True when every file is ok."""
    summary = status.groupby(["source", "how"])["status"].agg(lambda s: ", ".join(f"{n} {k}" for k, n in s.value_counts().items()))
    print(summary.to_string())
    bad = status[status["status"] != "ok"]
    for _, r in bad.drop_duplicates("where").iterrows():
        print(f"[{r['status']}] {r['source']} {r['path']}: {r['how']} - {r['where']}")
    print(f"{int((status['status'] == 'ok').sum())} of {len(status)} raw files present with the recorded hash")
    return bad.empty


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "check"
    if step == "record":
        print(f"manifest: {len(record())} files")
    elif step == "check":
        sys.exit(0 if report(check()) else 1)
    elif step == "fetch":
        sys.exit(0 if report(fetch()) else 1)
    elif step == "bundle":
        print(f"written: {bundle()}")
    else:
        raise SystemExit("usage: python -m src.get_data check | fetch | bundle | record")
