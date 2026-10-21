"""Every number in the report traces to results/report_numbers.csv; the core of the report stays under the word limit (decision #84)."""

import re

import pandas as pd

from src import paths, report_numbers

REPORT = paths.REPORT / "report.md"
WORD_LIMIT = 4500  # the course suggests 3,000 excluding references and appendices; the executive report may run to about 4,500 (decision #94, superseding #84)
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
    r"\b(?:Figure|Table)\s+[A-G]\d+",      # appendix figures and tables (Figure E4, Table G1)
    r"\b[A-G]\.\d+\b",                     # appendix section references (E.3, F.6)
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
    """The counted part of the report: everything before Appendix A (references live in references.md)."""
    return text.split("## Appendix A", 1)[0]


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


def test_report_is_under_the_word_limit():
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body(REPORT.read_text(encoding="utf-8")))
    text = re.sub(r"^\|[-| ]+\|$", " ", text, flags=re.MULTILINE)  # table rule lines
    words = [w for w in re.split(r"\s+", text) if re.search(r"\w", w)]
    assert len(words) <= WORD_LIMIT, f"{len(words)} words"


# The poster and the Petrobras edition describe report v9, so they are checked against the live numbers table, as
# the report is (decision #99; until then they were checked against the frozen v7 table).


def test_every_number_on_the_poster_is_in_report_numbers():
    """The poster cites the report's numbers only; layout sizes (mm, pt, %) and colours are not quantities."""
    table = report_numbers.build()
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    poster = (paths.REPORT / "poster.typ").read_text(encoding="utf-8")
    poster = "\n".join(line for line in poster.splitlines() if not line.lstrip().startswith(("//", "#set", "#let")))
    poster = re.sub(r'#(?:text|image|v|line|grid|align|block)\([^)]*\)', " ", poster)  # typst calls carry sizes, not findings
    poster = re.sub(r"\b\d+(?:\.\d+)?(?:mm|pt|em)\b|\d+%(?=\))", " ", poster)
    missing = sorted(numbers_in(poster) - cited)
    assert not missing, f"numbers on the poster not in results/report_numbers.csv: {missing}"


def test_every_number_in_the_petrobras_report_is_in_report_numbers():
    """The executive edition cites the report's numbers only; typst sizes, colours and file names are not quantities."""
    table = report_numbers.build()
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    typ = (paths.REPORT / "petrobras_report.typ").read_text(encoding="utf-8")
    typ = "\n".join(line for line in typ.splitlines() if not line.lstrip().startswith(("//", "#set", "#let", "#show")))
    typ = re.sub(r'#(?:text|image|v|line|h|counter|page|outline|block)\([^)]*\)', " ", typ)
    typ = re.sub(r"\b\d+(?:\.\d+)?(?:pt|em|in|fr)\b|\d+%(?=[,)])", " ", typ)  # typst sizes, column fractions and widths
    typ = re.sub(r'"[^"]*\.svg"', " ", typ)  # figure file names
    missing = sorted(numbers_in(typ) - cited)
    assert not missing, f"numbers in the Petrobras report not in results/report_numbers.csv: {missing}"
