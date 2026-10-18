"""The advisor with tools: a question becomes a validated what-if, the model computes it, the advisor explains only what was computed.

What: ``ask_whatif`` runs one committee question through three steps. (1)
The language model reads the question and the parameter schema and answers
with a ``WhatIf`` as JSON, or says the question cannot be represented.
(2) ``src/whatif.py`` validates it and computes the new book, its
difference from the base book and every candidate's status — no language
model involved. (3) The language model explains the computed result, and
``verify_attributed`` checks every number in the explanation against the
result it was given, in its unit. Every call is recorded and replays
through ``advisor.Advisor``.
Why: the v6 advisor could only read pre-rendered tables, so a what-if was
answered in prose (audit S1); its grounding check accepted any number that
appeared anywhere in sixty kilobytes of tables, in any unit (audit S4).
Here the advisor's investment value and its explanation value are measured
separately: the book comes from the optimizer, the words from the model.
Reads: `prompts/whatif_translate.md`, `prompts/whatif_explain.md`.
Writes: through ``advisor.Advisor`` only (`results/advisor_runs.jsonl`).
Used by: notebook 11, the decision page; `tests/test_advisor_tools.py`.
"""

import re
from dataclasses import fields

import pandas as pd

from src import advisor as adv, whatif as wi

UNIT_WORDS = {"b": "$B", "bn": "$B", "billion": "$B", "m": "$M", "mn": "$M", "million": "$M", "%": "%", "percent": "%"}
TOKEN = re.compile(r"(?<![\w.])(-?\d[\d,]*(?:\.\d+)?)\s*(%|billion|million|bn|mn|[BbMm](?![a-z]))?")


def schema_text(ids):
    """The parameter list the translation prompt shows: names, defaults, ranges and the candidate ids."""
    lines = ["Parameters (name: default; allowed range or values):"]
    for f in fields(wi.WhatIf):
        default = f.default if not callable(f.default_factory) else []
        rng = wi.LIMITS.get(f.name)
        allowed = {"grid": "'registered' or 'committee'", "revenue_case": "'merchant' or 'contracted'", "credits": "true or false",
                   "wti_level": "real 2024 $/bbl, " + str(wi.LIMITS["wti_level"]), "cvar_limit_musd": "a $ million limit on the worst-5% average loss",
                   "forced_in": "candidate ids", "forced_out": "candidate ids"}.get(f.name, str(rng) if rng else "")
        lines.append(f"- {f.name}: {default}; {allowed}")
    lines.append("Candidate ids: " + ", ".join(ids))
    lines.append("Notes: wti_level holds WTI at that price for wti_years years; hh_multiplier and ercot_multiplier scale the whole path; "
                 "ercot_volatility scales the spread of ERCOT prices around their median (0.5 halves it); lease_cost_multiplier scales "
                 "lease redevelopment capital, power_capex_multiplier plant capital; delay_years pushes every request's operation back; "
                 "lam is the penalty on the worst-5% average loss, cvar_limit_musd a hard limit on it; technology_cap is the largest share "
                 "of the budget one technology may take.")
    return "\n".join(lines)


def result_text(result, top=12):
    """The computed answer as the fact sheet the explanation may cite: every figure with its unit."""
    if not result["feasible"]:
        return (f"No book meets the question's limits. Reason from the optimizer: {result['reason']}\n"
                f"Changes asked: {result['whatif']}. Grid: {result['grid']}. Revenue case: {result['revenue_case']}.\n")
    d = result["diff"]
    rows = []
    for label, key, unit, scale in (("candidates in the book", "n", "count", 1), ("budget charge", "charge", "$M", 1e6), ("expected NPV", "expected_npv", "$M", 1e6),
                                    ("median NPV", "median_npv", "$M", 1e6), ("chance of a loss", "p_loss", "share", 1), ("worst-5% average loss (CVaR95)", "cvar_loss", "$M", 1e6),
                                    ("concentration across technologies (HHI)", "hhi", "index 0-1", 1)):
        rows.append({"figure": label, "base book": d["old"][key] / scale, "new book": d["new"][key] / scale, "change": d["change"][key] / scale, "unit": unit})
    sheet = adv.format_table(pd.DataFrame(rows), "The base book and the book under the question", result["provenance"])
    moved = result["candidates"].set_index("project_id").loc[d["entered"] + d["left"]].reset_index() if d["entered"] + d["left"] else None
    parts = [f"Changes asked: {result['whatif']}. Grid: {result['grid']}. Revenue case: {result['revenue_case']}. Budget: {result['budget'] / 1e6:,.0f} $M. "
             f"Scenarios: {result['n_scenarios']:,}.\n", sheet,
             "Entered the book: " + (", ".join(d["entered"]) or "none") + ". Left the book: " + (", ".join(d["left"]) or "none") + ".\n"]
    if moved is not None:
        parts.append(adv.format_table(moved[["project_id", "technology", "in_book", "charge_$M", "expected_npv_$M", "median_npv_$M", "p_negative", "status"]],
                                      "The candidates that moved", "FORECAST on ASSUMED costs"))
    book = result["candidates"][result["candidates"]["in_book"]].sort_values("expected_npv_$M", ascending=False).head(top)
    parts.append(adv.format_table(book[["project_id", "technology", "charge_$M", "expected_npv_$M", "p_negative", "status"]], "The new book, largest expected NPV first",
                                  "FORECAST on ASSUMED costs"))
    return "\n".join(parts)


def tokens(text):
    """(value, unit) pairs in a text; the unit is '$B', '$M', '%' or '' when none is written next to the number."""
    out = []
    for m in TOKEN.finditer(text):
        raw = m.group(1).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        unit = UNIT_WORDS.get((m.group(2) or "").lower(), "")
        out.append((m.group(0).strip(), value, unit))
    return out


def verify_attributed(answer, result, allow_small_integers=10, question=""):
    """Every number in ``answer`` must be one the ``result`` shows, and its unit, if written, must not contradict the result's.

    Returns
    -------
    dict
        ``n_numbers``, ``n_grounded``, ``rate``, ``ungrounded`` and
        ``unit_errors`` (a number found in the result but cited in another
        unit, e.g. "5,839 billion" for a $ million figure).

    Notes
    -----
    Stricter than ``advisor.verify_numbers`` in three ways: the reference is
    the computed result (and the committee's own question, whose figures may
    be repeated), not every table of ``results/``; a "$B"
    written beside a "$M" figure is an error, not a match; small integers
    are exempt only up to ten. The result states every money figure in $
    million, so a correct citation of one carries "$M", "M", "million" or no
    unit at all.
    """
    allowed = {adv._norm(abs(v)) for _, v, _ in tokens(result + " " + question)}  # magnitudes: "falls by 870.2" cites a change shown as −870.2
    money = {adv._norm(abs(v)) for _, v, u in tokens(result)} if "$M" in result else set()
    checked, ungrounded, unit_errors = 0, [], []
    for raw, value, unit in tokens(answer):
        if value.is_integer() and (adv.YEAR_RANGE[0] <= value <= adv.YEAR_RANGE[1] or abs(value) <= allow_small_integers):
            continue
        checked += 1
        key = adv._norm(abs(value))
        if key not in allowed:
            ungrounded.append(raw)
        elif unit == "$B" and key in money:
            unit_errors.append(raw)
    bad = len(ungrounded) + len(unit_errors)
    return {"n_numbers": checked, "n_grounded": checked - bad, "rate": (checked - bad) / checked if checked else 1.0,
            "ungrounded": ungrounded, "unit_errors": unit_errors}


def ask_whatif(advisor, engine, question, system, tag=""):
    """One committee question, end to end: translate, validate, compute, explain, check.

    Parameters
    ----------
    advisor : advisor.Advisor
    engine : whatif.Engine
    question : str
    system : str
        The advisor's system prompt.
    tag : str
        Record tag.

    Returns
    -------
    dict
        ``question``, ``status`` ("answered", "cannot answer", "refused by
        the engine", "no record"), ``whatif``, ``reading``, ``result`` (the
        engine's output), ``result_text``, ``explanation``, ``verification``
        and the two call records' statuses.
    """
    out = {"question": question, "status": "no record", "whatif": None, "reading": None, "result": None, "result_text": None, "explanation": None, "verification": None}
    t = advisor.ask(system, adv.render("whatif_translate", question=question, schema=schema_text(engine.ids)), "whatif-translate", tag)
    if t is None:
        return out
    j = adv.parse_json(t["response"]) or {}
    if "cannot_answer" in j or "whatif" not in j:
        out.update(status="cannot answer", reading=j.get("cannot_answer", "the answer was not a what-if"))
        return out
    try:
        w = wi.WhatIf.from_dict(j["whatif"], engine.ids)
    except (wi.WhatIfError, TypeError) as err:
        out.update(status="refused by the engine", reading=str(err))
        return out
    out.update(whatif=w, reading=j.get("reading"))
    result = engine.run(w)
    text = result_text(result)
    out.update(result=result, result_text=text)
    e = advisor.ask(system, adv.render("whatif_explain", question=question, result=text), "whatif-explain", tag)
    if e is None:
        out["status"] = "computed, not explained"
        return out
    out.update(status="answered", explanation=e["response"], verification=verify_attributed(e["response"], text, question=question))
    return out
