"""One executive through the decision page: the pick, the reasons, the challenge, the five answers, the decision, the result.

What: the worked example the dashboard shows a new executive and notebook 13
records. The executive wants the leases and nothing else — the biggest first
until the budget is spent — and says so in the words of the challenge round
recorded in notebook 10 (``results/advisor_transcripts/challenge_all_leases.md``),
brought to the $3.82B decision. ``run`` puts that proposal through the
registered challenger (``challenge.challenge``: the model reads the reasons
into rules, tools score the book and compute the repair and the optimizer's
book, the model writes its memo, code checks it), records the author's own
five answers to the motivated-reasoning check, applies the override gate,
takes the decision the answers point to — the repair, the smallest change
that keeps the rules — and scores the first pick, the decision and the
advisor's solution on the executive's own rules, with the paired interval
between the decision and the solution.
Why: a new executive reads one complete round before making their own
(Alan, 28 Oct 2026, decision #120). The statement and the answers are the
author's; every number is the tools'. With no model available the round is
recorded with the tools alone (decision #121): the registered default rules
stand in for the model's reading and the checklist for its memo, which is
the registered "tools only" arm of the ladder, so the example needs no key.
Reads: the challenger's setting (``challenge.Setting``); ``prompts/``; ``results/advisor_runs.jsonl`` (replay).
Writes: ``results/v2/worked_example.json`` through ``write``; ``results/advisor_runs.jsonl`` on the first (live) run only.
Used by: notebook 13 section 7; ``app/example.py``; ``tests/test_worked_example.py``.
"""

import json
from dataclasses import asdict

import numpy as np

from src import advisor as adv, challenge as ch, paths

PATH = paths.RESULTS / "v2" / "worked_example.json"
TAG = "worked-example"
STATEMENT = ("I want the leases and nothing else: the biggest ones first, until the budget is spent. The leases produce today and every one of them "
             "is positive at base; the power requests lose money at 2024 prices and most of them never reach operation. Oil has always paid for this "
             "company and I do not see why we should learn a new business now.")
ANSWERS = {  # the author's answers from the recorded round, keyed as the override gate keys them
    "context_and_stakes": "If the leases are wrong the loss is the redevelopment capital spent now under an assumed cost grid; the worst case I have in mind is five years of $42 oil.",
    "parties": "The committee wants the budget on what already produces; the lender wants a thin tail; the operator wants workovers it knows how to run; the grid operator decides nothing on the lease side, which is part of why I like it.",
    "emotional_investment": "The company has run offshore oil for thirty years and I have defended the Gulf position in every budget round; the queue deposits already paid are small and I do not count them.",
    "evidence": "I leaned on the flat-path lease NPVs and on every lease being positive at base; I passed over the scenario median, the high-cost case and the contracted wind requests that are positive.",
    "framing": "I did not put a mixed book on the table, nor a smaller lease book that leaves room for the contracted wind requests.",
}
SOLUTION = {"proposal": "the executive's book as it is", "repair": "the repair: the fewest changes to the book that keep the rules", "optimizer": "the optimizer's book under the executive's rules"}


def pick(s):
    """The executive's first pick: leases only, the highest expected value first, while the next one still fits the budget."""
    lease = np.where(s.tech == "Lease redevelopment")[0]
    out, spent = [], 0.0
    for i in lease[np.argsort(-s.A[:, lease].mean(axis=0))]:
        if spent + s.charge[i] <= s.budget:
            spent += s.charge[i]
            out.append(s.ids[i])
    return [m for m in s.ids if m in set(out)]  # the setting's order, as the challenger is called


def _ids(s, x):
    return [s.ids[i] for i in np.where(np.asarray(x) == 1)[0]]


def _scores(s, x, prefs):
    return ch.scores_of(ch.totals(s, x, prefs), prefs.lam)


def tools_only(s, proposal_ids):
    """The round with the tools alone: the registered default rules, the diagnosis, the alternatives, the fact sheet and the checklist, in the shape ``challenge.challenge`` returns."""
    prefs = ch.Preferences()
    x0 = s.vector(proposal_ids)
    diag = ch.diagnose(s, x0, prefs)
    alts = ch.alternatives(s, x0, prefs)
    check = ch.checklist(diag, alts)
    return {"status": "tools only (no language model)", "preferences": asdict(prefs),
            "reading": "no model read the words: the registered default rules were used (tail weight 1, the budget and the 40% technology cap)",
            "not_representable": None, "diagnosis": diag, "alternatives": alts, "sheet": ch.fact_sheet(diag, alts, prefs), "memo": None, "verification": None,
            "level_requested": check["level"], "level": check["level"], "checklist": check}


def run(advisor, s):
    """The whole round as a dict: the pick, the challenge, the answers, the gate, the decision and the scores.

    Notes
    -----
    The decision is the repair when the advisor computed one and the
    optimizer's book otherwise: the answers say the executive left a smaller
    lease book off the table, and the repair is that book. A decision that
    departs from the advisor's solution passes the override gate on the five
    answers; the gate's verdict is recorded either way. The optimizer's book
    under the executive's rules is scored too, as the best book the rules
    allow, whether or not the advisor recommended it.
    """
    first = pick(s)
    res = ch.challenge(advisor, s, STATEMENT, first, adv.load_prompt("advisor_system"), tag=TAG)
    if res["status"] == "no record":
        res = tools_only(s, first)
    prefs = ch.Preferences(**res["preferences"])
    alts = res["alternatives"]
    rec = (res["memo"] or {}).get("recommended_book", "proposal") if res["status"] == "challenged" else res["checklist"]["recommended_book"]
    rec = rec if rec in alts else "proposal"
    x_first = s.vector(first)
    x_adv = alts[rec]["x"] if rec in alts else x_first
    chosen = "repair" if "repair" in alts else ("optimizer" if "optimizer" in alts else "proposal")
    x_dec = alts[chosen]["x"] if chosen in alts else x_first
    allowed, missing = adv.override_allowed(ANSWERS, opposing_case_read=True)
    accepted = bool(np.array_equal(x_dec, x_adv))
    cmp = None if accepted else ch.compare(s, x_adv, x_dec, prefs)
    memo = res["memo"] or {}
    return {
        "statement": STATEMENT, "first_pick": first, "first_pick_charge": float(s.charge @ x_first), "budget": float(s.budget),
        "status": res["status"], "reading": res["reading"], "not_representable": res["not_representable"], "preferences": res["preferences"],
        "level": res["level"], "level_requested": res["level_requested"],
        "vulnerabilities": memo.get("vulnerabilities", []), "why": memo.get("why", ""), "loss_avoided": memo.get("loss_avoided", ""),
        "what_would_change_it": memo.get("what_would_change_it", ""), "question_for_the_committee": memo.get("question_for_the_committee", ""),
        "verification": {k: res["verification"][k] for k in ("n_numbers", "n_grounded", "ungrounded")} if res["verification"] else None,
        "checklist_flags": res["checklist"]["flags"], "sheet": res["sheet"],
        "solution": rec, "solution_text": SOLUTION[rec], "solution_members": _ids(s, x_adv),
        "solution_changes": {k: alts[rec][k] for k in ("changes", "added", "dropped")} if rec in alts else {"changes": 0, "added": [], "dropped": []},
        "answers": ANSWERS, "gate_allowed": allowed, "gate_missing": missing,
        "decision": chosen, "decision_text": SOLUTION[chosen], "decision_members": _ids(s, x_dec), "accepted_in_full": accepted,
        "scores": {"first_pick": _scores(s, x_first, prefs), "decision": _scores(s, x_dec, prefs), "solution": _scores(s, x_adv, prefs),
                   **({"optimizer": _scores(s, alts["optimizer"]["x"], prefs)} if "optimizer" in alts else {})},
        "optimizer_members": _ids(s, alts["optimizer"]["x"]) if "optimizer" in alts else None,
        "optimizer_vs_decision": ch.compare(s, alts["optimizer"]["x"], x_dec, prefs) if "optimizer" in alts and not np.array_equal(alts["optimizer"]["x"], x_dec) else None,
        "solution_vs_decision": cmp, "rules_broken": {"first_pick": [r["rule"] for r in ch.rule_checks(s, x_first, prefs) if r["broken"]],
                                                      "decision": [r["rule"] for r in ch.rule_checks(s, x_dec, prefs) if r["broken"]]},
        "calls": dict(advisor.calls),
    }


def write(example, path=PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(example, indent=1, ensure_ascii=False), encoding="utf-8")
    return path


def load(path=PATH):
    return json.loads(path.read_text(encoding="utf-8"))


def labels():
    """A short label per candidate for the pages: the id without its prefix, the technology, the size of a request."""
    import pandas as pd
    m = pd.read_csv(paths.RESULTS / "v2" / "book_D_members.csv")
    return {r.project_id: f"{r.project_id.split('|')[-1]} · {r.technology}" + (f" {r.mw:.0f} MW" if pd.notna(r.mw) and r.technology != "Lease redevelopment" else "")
            for r in m.itertuples()}


def rules_text(prefs):
    """The executive's rules as the advisor read them, in plain words."""
    out = [f"tail weight λ = {prefs.lam:g} (a dollar of average loss in the worst 5% of scenarios counts as {prefs.lam:g} dollars of expected value)"]
    if prefs.max_p_loss is not None:
        out.append(f"chance of a loss at most {prefs.max_p_loss:.0%}")
    if prefs.max_cvar_musd is not None:
        out.append(f"worst-5% average loss at most ${prefs.max_cvar_musd:,.0f}M")
    if prefs.excluded_technologies or prefs.excluded_ids:
        out.append("will not fund " + ", ".join(prefs.excluded_technologies + prefs.excluded_ids))
    if prefs.liquidity_line_musd is not None:
        out.append(f"a construction line of ${prefs.liquidity_line_musd:,.0f}M beyond the reserve")
    if prefs.min_utilization is not None:
        out.append(f"at least {prefs.min_utilization:.0%} of the budget committed")
    return "; ".join(out)
