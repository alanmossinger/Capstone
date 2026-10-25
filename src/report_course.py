"""The course-length report: report V2's executive summary, decision brief and conclusions, under 3,000 words.

What: writes ``report/report_course.md`` from ``report/report.md`` — the
YAML header, the executive summary, the decision brief, the executive
conclusions, four figures and the statement of work — so the course's
suggested length (about 3,000 words excluding references and appendices)
is met by the same text, with the same numbers, as the executive edition.
Why: the executive edition runs to about 11,500 words at Alan's request;
a grader following the course guidance gets the short version, and every
number in it is the long version's (``tests/test_report.py`` checks both).
Reads: ``report/report.md``.
Writes: ``report/report_course.md`` (``make report-course`` then builds
``report/report_course.pdf`` and ``.docx`` from it with pandoc and typst).
Used by: ``python -m src.report_course``; ``make report-course``.
"""

import re

from src import paths

SOURCE = paths.REPORT / "report.md"
TARGET = paths.REPORT / "report_course.md"
# the figures the short version keeps, placed after the section whose finding they carry
FIGURES = {
    "## Executive decision brief": [("F43_architecture", "The decision workflow in six stages — prediction, uncertainty, prescription, AI challenge, decision, outcome — and what is measured at each on the same held-out scenarios."),
                                   ("F54_allocation", "The recommended capital allocation: each member's budget charge and expected NPV, with its chance of a loss and the cost of removing it."),
                                   ("F51_true_economics", "The true economics of capital allocation: what each decision process is worth on three funding bases, and what each commits, reserves and may call."),
                                   ("F53_ladder_five_arms", "Where the economic value of AI comes from: the committee's own objective under five arms, and the paired rungs — three registered as scored, two added for the optimizer-first rule.")],
}


def section(text, heading):
    """The text of one level-two section, heading included, up to the next level-two heading."""
    start = text.index(heading)
    nxt = re.search(r"^## ", text[start + len(heading):], flags=re.MULTILINE)
    return text[start: start + len(heading) + nxt.start()] if nxt else text[start:]


def build():
    """Write the course-length report and return its path."""
    text = SOURCE.read_text(encoding="utf-8")
    header = text[: text.index("---", 3) + 3]
    header = header.replace('title: "Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation"',
                            'title: "Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation"\nsubtitle-note: "Course-length edition; the executive edition is report.pdf"')
    parts = [header, "\n\n*This is the course-length edition of the report: the executive summary, the decision brief and the conclusions of the executive edition (`report/report.pdf`, 14 sections and nine appendices), with the same numbers. The method, the evidence, the registered record and every correction are in the executive edition.*\n"]
    for heading in ("## Executive summary", "## Executive decision brief", "## 14 Executive conclusions and recommendations", "## Statement of work"):
        body = section(text, heading)
        body = re.sub(r"```\{=typst\}\n#pagebreak\(\)\n```\n*", "", body)
        if heading == "## 14 Executive conclusions and recommendations":
            body = body.replace(heading, "## Executive conclusions and recommendations", 1)
        body = re.sub(r"\((?:Sections?|Section) [0-9–,\s and]+\)", "", body)  # the short edition has no numbered sections
        body = re.sub(r"\(Figure \d+\)", "", body)
        body = re.sub(r" +\.", ".", body)
        parts.append(body.rstrip() + "\n")
        for name, caption in FIGURES.get(heading, []):
            k = len([p for p in parts if p.startswith("![")]) + 1
            parts.append(f"\n![Figure {k}](../figures/{name}.png)\n\n*Figure {k}.* {caption}\n")
    TARGET.write_text("\n".join(parts), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    out = build()
    words = len([w for w in re.split(r"\s+", out.read_text(encoding="utf-8")) if re.search(r"\w", w)])
    print(f"{out} written: about {words} words")
