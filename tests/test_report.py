"""Every number in the report traces to results/report_numbers.csv; the word-limit test records that the limit is off (decision #44)."""

import re

import pandas as pd
import pytest

from src import paths, report_numbers

REPORT = paths.REPORT / "report.md"
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
    r"\b(?:RQ|[CRKDSH])\d+\b",             # criteria C1–C5, rules R1–R9, post-hoc K, decisions D0–D7, sources S13, hypotheses H2, questions RQ1
    r"§\s?\d+(?:[–-]§?\d+)?",             # section marks in the Decision Board
    r"\bTables?\s+\d+",                    # table numbers
    r"\bPart I{1,2}\b",
    r"\bOrder No\. \d+",
    r"\bEIA-860M\b",
    r"\bEIA-923\b",
    r"\beGRID20\d\d\b",
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
    text = REPORT.read_text(encoding="utf-8")
    missing = sorted(numbers_in(text) - cited)
    assert not missing, f"numbers in report.md not in results/report_numbers.csv: {missing}"


def test_report_numbers_keys_are_unique():
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv")
    assert table["key"].is_unique


@pytest.mark.skip(reason="word, figure and page limits are off for the v3 report (decision #44); the test stays so the limit can be restored by removing this line")
def test_report_is_under_the_word_limit():
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body(REPORT.read_text(encoding="utf-8")))
    text = re.sub(r"^\|[-| ]+\|$", " ", text, flags=re.MULTILINE)  # table rule lines
    words = [w for w in re.split(r"\s+", text) if re.search(r"\w", w)]
    assert len(words) <= WORD_LIMIT, f"{len(words)} words"


def test_every_number_on_the_poster_is_in_report_numbers():
    """The poster cites the report's numbers only; layout sizes (mm, pt, %) and colours are not quantities."""
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv")
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    poster = (paths.REPORT / "poster.typ").read_text(encoding="utf-8")
    poster = "\n".join(line for line in poster.splitlines() if not line.lstrip().startswith(("//", "#set", "#let")))
    poster = re.sub(r'#(?:text|image|v|line|grid|align|block)\([^)]*\)', " ", poster)  # typst calls carry sizes, not findings
    poster = re.sub(r"\b\d+(?:\.\d+)?(?:mm|pt|em)\b|\d+%(?=\))", " ", poster)
    missing = sorted(numbers_in(poster) - cited)
    assert not missing, f"numbers on the poster not in results/report_numbers.csv: {missing}"
