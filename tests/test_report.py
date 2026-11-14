"""Every number in the official report and on the poster traces to results/report_numbers.csv; the report's body stays within the course's length."""

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


# The poster (report/poster_V2.typ) is drawn from the report's numbers only; typst layout sizes (mm, pt, em, fr, %),
# colours and file names are not quantities.
POSTER = paths.REPORT / "poster_V2.typ"

# The report folder (the Word report, the poster and their notes) is kept by the author and is not in the repository
# (decision #132): on a clone without it the tests that read those files are skipped, not failed.
def needs(path):
    return pytest.mark.skipif(not path.exists(), reason=f"{path.name} is kept outside the repository (decision #132)")


@needs(POSTER)
def test_every_number_on_the_poster_is_in_report_numbers():
    table = report_numbers.build()
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    poster = POSTER.read_text(encoding="utf-8")
    poster = "\n".join(line for line in poster.splitlines() if not line.lstrip().startswith(("//", "#set", "#let")))
    poster = re.sub(r'#(?:text|image|v|line|grid|align|block|circle)\([^)]*\)', " ", poster)  # typst calls carry sizes, not findings
    poster = re.sub(r"\b\d+(?:\.\d+)?(?:mm|pt|em|fr)\b|\d+(?:\.\d+)?%(?=[,)\s])", " ", poster)
    poster = re.sub(r'"[^"]*\.(?:svg|png)"', " ", poster)
    missing = sorted(numbers_in(poster) - cited)
    assert not missing, f"numbers on the poster not in results/report_numbers.csv: {missing}"


# The official capstone report is the Word edition (decision #117). It is edited in Word, not built from Markdown,
# so its text is read straight from the document XML: the abstract through the appendices, without the references.
OFFICIAL = paths.REPORT / "Beyond_Prediction_Edited_Full_Report_V3_no_criterion_codes.docx"  # the final report (decision #132)


def official_text():
    """The paragraphs of the official report from Abstract up to References, with cross-references removed."""
    import zipfile
    xml = zipfile.ZipFile(OFFICIAL).read("word/document.xml").decode("utf-8")
    paras = ["".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", p)) for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)]
    start = max(i for i, p in enumerate(paras) if p.strip() == "Abstract")  # the last one; the first is the contents list
    end = max(i for i, p in enumerate(paras) if p.strip() == "References")
    text = "\n".join(paras[start:end])
    text = re.sub(r"^\d+(?:\.\d+)* [A-Z].*$", " ", text, flags=re.MULTILINE)  # numbered headings
    text = re.sub(r"\bSections?\s+\d+(?:\.\d+)?", " ", text)
    text = re.sub(r"maps onto this report as follows:.*?\.\s", " ", text, flags=re.S)  # the appendices' section map
    return re.sub(r"[\w/.-]+\.(?:md|csv|py|json|jsonl|ipynb|png|svg|typ|pdf)\b", " ", text)  # file names


OFFICIAL_WORD_LIMIT = 3000  # the course's length, excluding references and appendices (decision #124)


def official_body_words():
    """Words of the official report from the Abstract heading to the Appendices heading: headings, captions and tables included."""
    import zipfile
    xml = zipfile.ZipFile(OFFICIAL).read("word/document.xml").decode("utf-8")
    blocks = re.findall(r"<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>", xml, flags=re.S)
    texts = ["".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", b)) for b in blocks]
    start = max(i for i, t in enumerate(texts) if t.strip() == "Abstract")
    end = max(i for i, t in enumerate(texts) if t.strip() == "Appendices")
    return sum(len(t.split()) for t in texts[start:end])


@needs(OFFICIAL)
def test_the_official_report_body_is_within_the_course_length():
    assert official_body_words() <= OFFICIAL_WORD_LIMIT


@needs(OFFICIAL)
def test_every_number_in_the_official_report_is_in_report_numbers():
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv", dtype=str)
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    missing = sorted(numbers_in(official_text()) - cited)
    assert not missing, f"numbers in the official report not in results/report_numbers.csv: {missing}"
