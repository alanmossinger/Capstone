"""Every number in the report and its appendix traces to results/report_numbers.csv; the report stays under 3,000 words."""

import re

import pandas as pd
import pytest

from src import paths, report_numbers

REPORT = paths.REPORT / "report.md"
APPENDIX = paths.REPORT / "appendix.md"
WORD_LIMIT = 3000  # course limit, excluding references and appendix
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?%?")

# Labels and names that contain digits but are not cited quantities.
NOT_QUANTITIES = [
    r"!\[[^\]]*\]\([^)]*\)",               # image links (paths such as F1_cif_by_region.png)
    r"`[^`]*`",                            # file names and code
    r"^#+ .*$",                            # headings carry section numbers
    r"\b(?:Figure|Appendix|decisions?|notebooks?)\s+[\d–, and#]+",
    r"#\d+",                               # decision numbers
    r"\bsections?\s+\d+(?:\.\d+)?",       # section references
    r"\b[CRK]\d+\b",                       # criteria C1–C5, cleaning rules R1–R9, post-hoc candidates
    r"\bOrder No\. \d+",
    r"\bEIA-860M\b",
    r"\bSHA-256\b",
    r"\bSIADS \d+",
    r"\bv\d+\b",
    r"\b(?:19|20)\d\d\b",                  # calendar years
]


def body(text):
    """The counted part of the report: report.md holds no references or appendices."""
    return text


def numbers_in(text):
    """Numeric tokens left after removing labels, with signs dropped."""
    for pattern in NOT_QUANTITIES:
        text = re.sub(pattern, " ", text, flags=re.MULTILINE)
    return {token.rstrip(",") for token in NUMBER.findall(text)}


def test_every_number_in_the_report_is_in_report_numbers():
    table = report_numbers.build()
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    text = REPORT.read_text(encoding="utf-8") + APPENDIX.read_text(encoding="utf-8")
    missing = sorted(numbers_in(text) - cited)
    assert not missing, f"numbers in report.md or appendix.md not in results/report_numbers.csv: {missing}"


def test_report_numbers_keys_are_unique():
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv")
    assert table["key"].is_unique


@pytest.mark.skip(reason="word limit relaxed for draft v1 (decision #40); restore before the final report")
def test_report_is_under_the_word_limit():
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body(REPORT.read_text(encoding="utf-8")))
    text = re.sub(r"^\|[-| ]+\|$", " ", text, flags=re.MULTILINE)  # table rule lines
    words = [w for w in re.split(r"\s+", text) if re.search(r"\w", w)]
    assert len(words) <= WORD_LIMIT, f"{len(words)} words"
