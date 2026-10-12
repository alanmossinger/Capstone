"""Every file-system location the project uses, relative to the repository root.

What: one place that defines the data, figure, result and document folders.
Why: notebooks and modules never hard-code a path, so the repository runs
from any clone location.
Reads / writes: nothing on import; ``ensure_dirs()`` creates missing folders.
Used by: every notebook's setup cell and every ``src`` module that touches disk.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

DATA = REPO / "data"
DATA_RAW = DATA / "raw"
RAW_LBNL = DATA_RAW / "lbnl"
RAW_EIA860M = DATA_RAW / "eia860m"
RAW_ERCOT = DATA_RAW / "ercot"
RAW_BSEE = DATA_RAW / "bsee"
RAW_EIA923 = DATA_RAW / "eia923"
RAW_PRICES = DATA_RAW / "prices"
RAW_EGRID = DATA_RAW / "egrid"
MANIFEST_V5 = DATA_RAW / "manifest_v5.json"
DATA_INTERIM = DATA / "interim"
DATA_PROCESSED = DATA / "processed"

NOTEBOOKS = REPO / "notebooks"
FIGURES = REPO / "figures"
RESULTS = REPO / "results"
DOCS = REPO / "docs"
REPORT = REPO / "report"

ENV_FILE = REPO / ".env"
FIGURE_NOTES = REPORT / "figure_notes.md"


def ensure_dirs():
    """Create every output folder that does not exist yet.

    Notes
    -----
    Called once in each notebook's setup cell. Creating folders up front means
    a fresh clone can run the pipeline without any manual ``mkdir``.
    """
    for folder in (RAW_LBNL, RAW_EIA860M, RAW_ERCOT, RAW_BSEE, RAW_EIA923, RAW_PRICES, RAW_EGRID, DATA_INTERIM, DATA_PROCESSED,
                   FIGURES, RESULTS, DOCS, REPORT):
        folder.mkdir(parents=True, exist_ok=True)
