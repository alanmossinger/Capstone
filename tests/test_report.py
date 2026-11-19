"""Every number in the official report and on the poster traces to results/report_numbers.csv."""

import functools
import re

import pandas as pd
import pytest

from src import paths, report_numbers

NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?%?")

# Labels and names that contain digits but are not cited quantities.
NOT_QUANTITIES = [
    r"!\[[^\]]*\]\([^)]*\)",               # image links (paths such as F1_cif_by_region.png)
    r"`[^`]*`",                            # file names and code
    r"^#+ .*$",                            # headings carry section numbers
    r"\b(?:Figure|Appendix|decisions?|notebooks?)\s+[\d–, and#]+",
    r"#\d+",                               # decision numbers
    r"\bsections?\s+\d+(?:\.\d+)?",       # section references
    r"\b\d{2}INR\d{4}\b",                  # ERCOT request ids (24INR0075)
    r"\bG\d{5}\b",                         # BSEE lease ids (G26253)
    r"\b(?:RQ|[CRKDSH])\d+\b",             # criteria C1–C5, rules R1–R9, post-hoc K, decisions D0–D7, sources S13, hypotheses H2, questions RQ1
    r"§\s?\d+(?:[–-]§?\d+)?",             # section marks in the Decision Board
    r"\bTables?\s+\d+",                    # table numbers
    r"\b(?:Figure|Table)\s+[A-K]\d+",      # appendix figures and tables (Figure E4, Table G1, Figure K3)
    r"\b[A-K]\.\d+(?:\.\d+)?\b",           # appendix section references (E.3, F.6, K.4.2)
    r"\bPart I{1,2}\b",
    r"\bOrder No\. \d+",
    r"\bEIA-860M\b",
    r"\bEIA-923\b",
    r"\beGRID20\d\d\b",
    r"\bSHA-256\b",
    r"\b[\w-]+(?:\.[\w-]+)*\.(?:gov|com|org)(?:/[\w./-]*)?",  # web addresses in the datasets appendix (eia.gov/electricity/data/eia923)
    r"\bCUUR\w+\b",                        # the BLS series id of the CPI-U (CUUR0000SA0)
    r"\b1:\d[\d,]*\b",                     # map scales (1:20,000,000)
    r"\bSIADS \d+",
    r"\bv\d+\b",
    r"\b(?:19|20)\d\d[a-z]?\b",            # calendar years, and citation years such as 2026c
]


def numbers_in(text):
    """Numeric tokens left after removing labels, with signs dropped."""
    for pattern in NOT_QUANTITIES:
        text = re.sub(pattern, " ", text, flags=re.MULTILINE)
    return {token.rstrip(",") for token in NUMBER.findall(text)}


def test_report_numbers_keys_are_unique():
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv")
    assert table["key"].is_unique


# The poster (report/poster_V3.typ, decision #133) is drawn from the report's numbers only; typst layout sizes
# (mm, pt, em, fr, %), colours, file names and its reference list are not quantities.
POSTER = paths.REPORT / "poster_V3.typ"

# Most of the report folder (the Word files, the poster source and their notes) is kept by the author and is not in the
# repository (decision #132): on a clone without a file the tests that read it are skipped, not failed.
def needs(path):
    return pytest.mark.skipif(not path.exists(), reason=f"{path.name} is kept outside the repository (decision #132)")


@needs(POSTER)
def test_every_number_on_the_poster_is_in_report_numbers():
    table = report_numbers.build()
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    poster = POSTER.read_text(encoding="utf-8")
    poster = poster.split("// ---- references")[0]  # volumes and pages of the cited works
    poster = "\n".join(line for line in poster.splitlines() if not line.lstrip().startswith(("//", "#set", "#let")))
    poster = re.sub(r'#(?:text|image|v|line|grid|align|block|circle)\([^)]*\)', " ", poster)  # typst calls carry sizes, not findings
    poster = re.sub(r"\b\d+(?:\.\d+)?(?:mm|pt|em|fr)\b|\d+(?:\.\d+)?%(?=[,)\s])", " ", poster)
    poster = re.sub(r'"[^"]*\.(?:svg|png)"', " ", poster)
    missing = sorted(numbers_in(poster) - cited)
    assert not missing, f"numbers on the poster not in results/report_numbers.csv: {missing}"


# The official capstone report is submitted as two PDFs, the only report files in the repository besides the poster:
# the full narrative edition and the 3,000-word edition. Their text is read from the PDF pages with pdfplumber:
# the abstract through the appendices, without the references.
REPORT_FULL = paths.REPORT / "Beyond_Prediction_MADS CAPSTONE_Alan Mossinger.pdf"              # the full narrative edition
REPORT_SHORT = paths.REPORT / "Beyond_Prediction_MADS CAPSTONE_Alan Mossinger_3000_words.pdf"  # the 3,000-word edition


@functools.lru_cache(maxsize=None)
def report_lines(path):
    """The text lines of a report PDF, page after page."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return tuple(line for page in pdf.pages for line in (page.extract_text() or "").splitlines())


def last_line(lines, heading):
    """Index of the last line that is exactly this heading."""
    return max(i for i, line in enumerate(lines) if line.strip() == heading)


def official_text(path):
    """The lines of a report from Abstract up to References, with cross-references removed."""
    lines = report_lines(path)
    text = "\n".join(lines[last_line(lines, "Abstract"):last_line(lines, "References")])
    text = re.sub(r"\(cid:\d+\)", " ", text)  # equation glyphs the PDF does not map to characters
    text = re.sub(r"^\d+(?:\.\d+)*\.? [A-Z].*$", " ", text, flags=re.MULTILINE)  # numbered headings
    text = re.sub(r"\bSections?\s+\d+(?:\.\d+)?", " ", text)
    text = re.sub(r"maps onto this report as follows:.*?\.\s", " ", text, flags=re.S)  # the appendices' section map
    return re.sub(r"[\w/.-]+\.(?:md|csv|py|json|jsonl|ipynb|png|svg|typ|pdf)\b", " ", text)  # file names


@pytest.mark.parametrize("path", [pytest.param(REPORT_FULL, marks=needs(REPORT_FULL), id="full"),
                                  pytest.param(REPORT_SHORT, marks=needs(REPORT_SHORT), id="3000_words")])
def test_every_number_in_the_official_report_is_in_report_numbers(path):
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv", dtype=str)
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    missing = sorted(numbers_in(official_text(path)) - cited)
    assert not missing, f"numbers in {path.name} not in results/report_numbers.csv: {missing}"
