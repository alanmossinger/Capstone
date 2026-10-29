"""Every number in the report traces to results/report_numbers.csv; the core of the report stays under the word limit (decision #84)."""

import re

import pandas as pd

from src import paths, report_numbers

REPORT = paths.REPORT / "report.md"
WORD_LIMIT = 12500  # the course suggests 3,000 excluding references and appendices; the executive report V2 with its executive summary runs to about 11,500 (decision #113, superseding #94)
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
    table = report_numbers.build() if REPORT_V10_WRITTEN else pd.read_csv(V9_NUMBERS)
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


# Report v9, the poster and the Petrobras edition were written before the decision moved to the as-of candidates (decision
# #105): until report v10 replaces the report and the poster, all three are checked against the numbers table they were
# written from, frozen in results/report_v9/. The Petrobras edition is out of scope for v10 and stays on it.
V9_NUMBERS = paths.RESULTS / "report_v9" / "report_numbers.csv"
REPORT_V10_WRITTEN = True  # report.md and poster.typ were rewritten from the v10 results on 22 October 2026


def test_every_number_on_the_poster_is_in_report_numbers():
    """The poster cites the report's numbers only; layout sizes (mm, pt, %) and colours are not quantities."""
    table = report_numbers.build() if REPORT_V10_WRITTEN else pd.read_csv(V9_NUMBERS)
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
    """The executive edition cites report v9's numbers; typst sizes, colours and file names are not quantities."""
    table = pd.read_csv(V9_NUMBERS)
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


# The course-length edition (src/report_course.py) is the executive summary, the brief and the conclusions of report.md:
# the same numbers, under the course's suggested length.
COURSE = paths.REPORT / "report_course.md"
COURSE_WORD_LIMIT = 3000


def test_course_edition_numbers_are_in_report_numbers():
    from src import report_course
    report_course.build()
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv", dtype=str)
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    missing = sorted(numbers_in(COURSE.read_text(encoding="utf-8")) - cited)
    assert not missing, f"numbers in report_course.md not in results/report_numbers.csv: {missing}"


def test_course_edition_is_under_the_course_word_limit():
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", COURSE.read_text(encoding="utf-8"))
    text = re.sub(r"^\|[-| ]+\|$", " ", text, flags=re.MULTILINE)
    words = [w for w in re.split(r"\s+", text) if re.search(r"\w", w)]
    assert len(words) <= COURSE_WORD_LIMIT, f"{len(words)} words"


# The official capstone report is Alan's Word edition (decision #117). It is edited in Word, not built from report.md,
# so its text is read straight from the document XML: the abstract through the appendices, without the references.
OFFICIAL = paths.REPORT / "Beyond_Prediction_Capstone_Report_Final.docx"


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


def test_the_official_report_body_is_within_the_course_length():
    assert official_body_words() <= OFFICIAL_WORD_LIMIT


def test_every_number_in_the_official_report_is_in_report_numbers():
    table = pd.read_csv(paths.RESULTS / "report_numbers.csv", dtype=str)
    cited = set()
    for text in table["text"].astype(str):
        cited |= numbers_in(text)
    missing = sorted(numbers_in(official_text()) - cited)
    assert not missing, f"numbers in the official report not in results/report_numbers.csv: {missing}"
