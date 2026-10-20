"""The active challenger: the advisor turns the committee's words into rules, tools test the proposal, the advisor challenges it.

What: one committee proposal — a statement in words and a book of
candidates — goes through four steps. (1) The language model reads the
statement into ``Preferences`` (a tail weight, a chance-of-loss limit, a tail
limit, exclusions, a liquidity line for construction calls), or says what it
cannot represent; it may also ask for up to two what-ifs to test an
assumption. (2) Deterministic tools diagnose the proposal on the held-out
scenarios — the committee's own rules, capital calls, each member's tail
dependence and risk contribution — and compute two alternatives: the
optimizer's book under the stated preferences, and the *repair*, the
fewest changes to the committee's book that meet its rules. (3) The language
model writes a challenge memo from that fact sheet only: at most three
vulnerabilities, each tied to a fact, a recommendation level and what would
change it. (4) Code checks every number against the sheet, every
vulnerability's fact references, and whether "guide" is allowed; a guide the
evidence does not support is downgraded and the downgrade recorded.
Why: the v8 advisor explained what the optimizer computed and added no
investment value by construction. Decision #94 asks whether an advisor that
challenges can improve a committee's decision; it can do so only through
mechanisms the optimizer lacks — the committee's own rules read from words,
a missing constraint (capital calls), a fragile member, a tested assumption —
never by beating the optimizer on its own objective. ``checklist`` runs the
same tools with fixed rules and no language model: the control that says
how much of any gain is the tools' and how much the model's.
Reads: `prompts/challenge_read.md`, `prompts/challenge_memo.md`; the engines of `src/whatif.py`.
Writes: through ``advisor.Advisor`` only (`results/advisor_runs.jsonl`).
Used by: notebook 11 (the challenger section), the decision page; `tests/test_challenge.py`.
"""

import json
from dataclasses import asdict, dataclass, field, fields

import numpy as np
import pandas as pd

from src import advisor as adv, advisor_tools as at, optimizer as opt, robustness as rb, whatif as wi

LEVEL, CAP, N_BOOT, SEED = 0.95, 0.40, 1000, 2020
LIMITS = {"lam": (0.0, 32.0), "max_p_loss": (0.0, 1.0), "max_cvar_musd": (0.0, 1e5), "liquidity_line_musd": (0.0, 1e5), "min_utilization": (0.0, 1.0)}
LEVELS = ("explain", "challenge", "guide")
KINDS = ("computed fact", "assumption", "inference", "hypothesis to test")
TYPES = ("broken rule", "unfunded construction calls", "fragile position", "sunk cost", "double standard", "unsupported claim", "concentration", "other")  # what a vulnerability is about (decision #96: scored mechanically)
MAX_WHATIFS = 2


class PreferenceError(ValueError):
    """A preference outside its range, or a candidate or technology the model does not know."""


@dataclass
class Preferences:
    """The committee's rules, read from its words.

    Notes
    -----
    Every field is optional except the tail weight, which defaults to the
    registered λ = 1. A rule left out is not enforced; the challenger may
    still point out that the statement implies it.
    """

    lam: float = 1.0
    max_p_loss: float | None = None
    max_cvar_musd: float | None = None
    excluded_technologies: list = field(default_factory=list)
    excluded_ids: list = field(default_factory=list)
    liquidity_line_musd: float | None = None
    min_utilization: float | None = None

    def validate(self, ids, technologies):
        for name, (lo, hi) in LIMITS.items():
            v = getattr(self, name)
            if v is not None and not (lo <= float(v) <= hi):
                raise PreferenceError(f"{name} = {v} is outside [{lo}, {hi}]")
        unknown = [t for t in self.excluded_technologies if t not in set(technologies)]
        if unknown:
            raise PreferenceError(f"unknown technologies {unknown}; one of {sorted(set(technologies))}")
        unknown = [i for i in self.excluded_ids if i not in ids]
        if unknown:
            raise PreferenceError(f"unknown candidates {unknown}")
        return self

    @classmethod
    def from_dict(cls, d, ids, technologies):
        """Build from the advisor's JSON, refusing unknown fields."""
        names = {f.name for f in fields(cls)}
        extra = set(d) - names
        if extra:
            raise PreferenceError(f"unknown preference fields {sorted(extra)}")
        return cls(**d).validate(ids, technologies)


def schema_text(technologies):
    """The preference fields the reading prompt shows, with their ranges."""
    lines = ["Preference fields (leave out what the statement does not say):",
             "- lam: tail weight, how much a dollar of worst-5% average loss counts against a dollar of expected NPV; default 1; range 0 to 32",
             "- max_p_loss: the largest chance of losing money the committee accepts for the book, a share between 0 and 1",
             "- max_cvar_musd: the largest worst-5% average loss the committee accepts, $ million",
             "- excluded_technologies: technologies the committee will not fund; one or more of " + ", ".join(sorted(set(technologies))),
             "- excluded_ids: candidate ids the committee will not fund",
             "- liquidity_line_musd: construction capital the company can call beyond the stage-one reserve, $ million (leave out if the statement says nothing about it)",
             "- min_utilization: the smallest share of the budget the committee wants committed, between 0 and 1"]
    return "\n".join(lines)


# --- the deterministic tools ------------------------------------------------------------------

class Setting:
    """The two engines, the base matrices and the budget of one grid, computed once."""

    def __init__(self, sel, held, grid="committee"):
        self.sel, self.held, self.grid = sel, held, grid
        base = sel.base_case(grid, "contracted")
        self.w = wi.WhatIf(grid=grid)
        self.A, self.charge, self.budget, self.x_model = base["A"], base["charge"], base["budget"], base["x"]
        self.A_h, _ = held.matrix(self.w)
        self.ids = sel.ids
        self.tech = sel.candidates["technology"].to_numpy()
        self.power_idx = np.where(sel.candidates["sector"].to_numpy() == "ERCOT power")[0]
        self.capex_p = sel.power["capex"].to_numpy(float)
        self.carry_p = sel.power["carry_cost"].to_numpy(float)
        self.p7 = sel.power["p_operation_7y"].to_numpy(float)
        self.priority = self.A[:, self.power_idx].mean(axis=0) / self.capex_p  # funding order set in advance
        built = sel.op_year > 0  # primary scenarios: the choice may use them, the scoring may not
        self.calls = np.zeros_like(self.A)
        self.calls[:, self.power_idx] = built * self.capex_p - self.capex_p * self.p7  # construction capital called beyond each request's reserve

    def vector(self, members):
        x = np.zeros(len(self.ids), int)
        unknown = [m for m in members if m not in self.ids]
        if unknown:
            raise PreferenceError(f"unknown candidates in the proposal: {unknown}")
        x[[self.ids.index(m) for m in members]] = 1
        return x


def scores(A, x, lam=1.0):
    """A book's expected NPV, median, chance of a loss, CVaR95 loss and the metric E − λ·CVaR ($)."""
    return scores_of(A @ np.asarray(x, int), lam)


def scores_of(total, lam=1.0):
    """The same scores from a book's value in each scenario."""
    cvar = opt.cvar(-total, LEVEL)
    return {"mean": float(total.mean()), "median": float(np.median(total)), "p_loss": float((total < 0).mean()), "cvar": cvar, "metric": float(total.mean() - lam * cvar)}


def totals(s, x, prefs):
    """A book's value in each held-out scenario as it would be funded.

    Notes
    -----
    Without a stated liquidity line every request that reaches its agreement
    is built (the static valuation of notebook 11). With one, construction
    calls beyond the reserve plus the line cannot be funded and those
    requests forfeit their deposits (``robustness.funding_or_forfeit``, the
    order set in advance), so a proposal and its alternatives are compared
    under the committee's own funding constraint.
    """
    x = np.asarray(x, int)
    if prefs.liquidity_line_musd is None:
        return s.A_h @ x
    lease = np.ones(len(s.ids), bool)
    lease[s.power_idx] = False
    reserve = float((s.capex_p * s.p7)[x[s.power_idx] == 1].sum())
    return s.A_h[:, lease] @ x[lease] + rb.funding_or_forfeit(s.A_h[:, s.power_idx], s.held.op_year, s.capex_p, s.carry_p, x[s.power_idx], reserve,
                                                               prefs.liquidity_line_musd * 1e6, s.priority)


def rule_checks(s, x, prefs, A=None):
    """Which of the committee's rules (and the registered budget and cap) the book breaks.

    Returns a list of dicts: ``rule``, ``limit``, ``value``, ``broken``. Scored
    on ``A`` (the held-out set by default)."""
    A = s.A_h if A is None else A
    x = np.asarray(x, int)
    sc = scores(A, x, prefs.lam)
    out = [{"rule": "budget ($M)", "limit": s.budget / 1e6, "value": float(s.charge @ x) / 1e6, "broken": bool(s.charge @ x > s.budget + 1)}]
    for t in np.unique(s.tech):
        share = float(s.charge[s.tech == t] @ x[s.tech == t]) / s.budget
        out.append({"rule": f"technology cap, {t} (share of budget)", "limit": CAP, "value": share, "broken": share > CAP + 1e-9})
    if prefs.max_p_loss is not None:
        out.append({"rule": "chance of a loss", "limit": prefs.max_p_loss, "value": sc["p_loss"], "broken": sc["p_loss"] > prefs.max_p_loss})
    if prefs.max_cvar_musd is not None:
        out.append({"rule": "worst-5% average loss ($M)", "limit": prefs.max_cvar_musd, "value": sc["cvar"] / 1e6, "broken": sc["cvar"] / 1e6 > prefs.max_cvar_musd})
    banned = [i for i, m in enumerate(s.ids) if x[i] and (m in prefs.excluded_ids or s.tech[i] in prefs.excluded_technologies)]
    if prefs.excluded_ids or prefs.excluded_technologies:
        out.append({"rule": "excluded candidates held (count)", "limit": 0, "value": len(banned), "broken": bool(banned)})
    if prefs.min_utilization is not None:
        u = float(s.charge @ x) / s.budget
        out.append({"rule": "budget committed (share)", "limit": prefs.min_utilization, "value": u, "broken": u < prefs.min_utilization})
    if prefs.liquidity_line_musd is not None:
        calls = rb.capital_calls(s.held.op_year, s.capex_p, x[s.power_idx], s.p7)
        out.append({"rule": "construction calls beyond the reserve, 95th percentile ($M)", "limit": prefs.liquidity_line_musd,
                    "value": calls["excess_q95"] / 1e6, "broken": calls["excess_q95"] / 1e6 > prefs.liquidity_line_musd})
    return out


def diagnose(s, x, prefs):
    """The facts about one proposal on the held-out scenarios: its scores, its rule checks, its capital calls, each member's profile.

    Notes
    -----
    Each member's *risk contribution* is its mean NPV in the book's worst 5%
    of scenarios; its *tail dependence* the share of its total value earned in
    its own best 5%; its *drop test* what the book scores without it (no
    re-solve). A member with a high chance of loss and most of its value in a
    few scenarios is flagged as fragile.
    """
    x = np.asarray(x, int)
    sc = scores(s.A_h, x, prefs.lam)
    total = s.A_h @ x
    worst = total <= np.quantile(total, 1 - LEVEL)
    calls = rb.capital_calls(s.held.op_year, s.capex_p, x[s.power_idx], s.p7)
    line = None if prefs.liquidity_line_musd is None else prefs.liquidity_line_musd * 1e6
    funded = totals(s, x, prefs) if line is not None else totals(s, x, Preferences(lam=prefs.lam, liquidity_line_musd=0.0))
    members = []
    for i in np.where(x == 1)[0]:
        td = rb.tail_dependence(s.A_h[:, i])
        without = x.copy()
        without[i] = 0
        drop = scores(s.A_h, without, prefs.lam)
        members.append({"candidate": s.ids[i], "technology": s.tech[i], "charge_$M": s.charge[i] / 1e6, "expected_npv_$M": td["mean"] / 1e6,
                        "chance_of_loss": td["p_loss"], "share_of_value_in_best_5%": td["share_from_top"], "npv_in_book_worst_5%_$M": float(s.A_h[worst, i].mean()) / 1e6,
                        "drop_change_expected_npv_$M": (drop["mean"] - sc["mean"]) / 1e6, "drop_change_tail_loss_$M": (drop["cvar"] - sc["cvar"]) / 1e6,
                        "drop_change_metric_$M": (drop["metric"] - sc["metric"]) / 1e6})
    m = pd.DataFrame(members)
    m["fragile"] = (m["chance_of_loss"] >= 0.7) & (m["share_of_value_in_best_5%"].fillna(0) >= 0.5) if len(m) else []
    return {"scores": sc, "rules": rule_checks(s, x, prefs), "calls": calls, "value_with_line": scores_of(funded, prefs.lam), "line_used": line, "members": m}


def liquidity(s, prefs):
    """The liquidity line as solver arguments: the CVaR95 of construction calls beyond the reserve within the line (none when no line is stated)."""
    if prefs.liquidity_line_musd is None:
        return {}
    return {"calls": s.calls, "calls_cap": prefs.liquidity_line_musd * 1e6}


def repair(s, x0, prefs, max_steps=None):
    """The fewest changes to ``x0`` that meet the budget, the cap and the committee's rules, and the best such book.

    Returns
    -------
    dict or None
        ``x``, ``changes``, ``added``, ``dropped``; None when no book within
        ``max_steps`` changes meets the rules.

    Notes
    -----
    The MILP takes the budget, the cap, the exclusions, the tail limit and the
    liquidity line (the CVaR of construction calls beyond the reserve, a
    conservative form of the stated percentile) as constraints and the
    committee's tail weight as its objective, with at most k changes from the
    proposal; k rises from 0 until a book exists. The chance of a loss is not
    linear in the book, so a candidate book is checked against every rule on
    the primary scenarios and k rises again if it breaks one. The repair is a mathematical answer to the
    committee's own question — the closest book that keeps its rules — not
    a better book than the optimizer's under the same rules.
    """
    x0 = np.asarray(x0, int)
    out_ids = [i for i, m in enumerate(s.ids) if m in prefs.excluded_ids or s.tech[i] in prefs.excluded_technologies]
    cap = None if prefs.max_cvar_musd is None else prefs.max_cvar_musd * 1e6
    for k in range(0, (max_steps or len(s.ids)) + 1):
        try:
            x = opt.solve_milp(s.A, s.charge, s.budget, lam=prefs.lam, level=LEVEL, groups=s.tech, group_cap=CAP, cvar_cap=cap,
                               forced_out=out_ids, reference=x0, max_changes=k, **liquidity(s, prefs))["x"]
        except opt.InfeasibleBook:
            continue
        broken = [r for r in rule_checks(s, x, prefs, A=s.A) if r["broken"]]
        if not broken:
            return {"x": x, "changes": int(np.abs(x - x0).sum()), "added": [s.ids[i] for i in np.where((x == 1) & (x0 == 0))[0]],
                    "dropped": [s.ids[i] for i in np.where((x == 0) & (x0 == 1))[0]]}
    return None


def model_book(s, prefs):
    """The optimizer's book under the committee's stated preferences (None when no book meets them)."""
    out_ids = [i for i, m in enumerate(s.ids) if m in prefs.excluded_ids or s.tech[i] in prefs.excluded_technologies]
    try:
        return opt.solve_milp(s.A, s.charge, s.budget, lam=prefs.lam, level=LEVEL, groups=s.tech, group_cap=CAP,
                              cvar_cap=None if prefs.max_cvar_musd is None else prefs.max_cvar_musd * 1e6, forced_out=out_ids, **liquidity(s, prefs))["x"]
    except opt.InfeasibleBook:
        return None


def compare(s, x_alt, x0, prefs):
    """The alternative against the proposal on the held-out scenarios, each as it would be funded: metric and mean differences with paired intervals."""
    t_alt, t0 = totals(s, x_alt, prefs), totals(s, x0, prefs)
    rng = np.random.default_rng(SEED)
    S = len(t0)
    draws_m, draws_mean = [], []
    for _ in range(N_BOOT):
        idx = rng.integers(0, S, S)
        a, b = scores_of(t_alt[idx], prefs.lam), scores_of(t0[idx], prefs.lam)
        draws_m.append(a["metric"] - b["metric"])
        draws_mean.append(a["mean"] - b["mean"])
    point = scores_of(t_alt, prefs.lam)["metric"] - scores_of(t0, prefs.lam)["metric"]
    low, high = np.percentile(draws_m, [2.5, 97.5])
    return {"metric_diff": float(point), "metric_low": float(low), "metric_high": float(high), "clear_of_zero": bool(low > 0),
            "mean_diff": float((t_alt - t0).mean()), "mean_low": float(np.percentile(draws_mean, 2.5)), "mean_high": float(np.percentile(draws_mean, 97.5))}


def alternatives(s, x0, prefs):
    """The repair and the optimizer's book, each scored and compared with the proposal."""
    out = {}
    rep = repair(s, x0, prefs)
    if rep is not None and rep["changes"] > 0:
        out["repair"] = {**rep, "scores": scores_of(totals(s, rep["x"], prefs), prefs.lam), "rules_broken": [r["rule"] for r in rule_checks(s, rep["x"], prefs) if r["broken"]],
                         "vs_proposal": compare(s, rep["x"], x0, prefs)}
    xm = model_book(s, prefs)
    if xm is not None and int(np.abs(xm - x0).sum()) > 0:
        out["optimizer"] = {"x": xm, "changes": int(np.abs(xm - x0).sum()), "added": [s.ids[i] for i in np.where((xm == 1) & (x0 == 0))[0]],
                            "dropped": [s.ids[i] for i in np.where((xm == 0) & (x0 == 1))[0]], "scores": scores_of(totals(s, xm, prefs), prefs.lam),
                            "rules_broken": [r["rule"] for r in rule_checks(s, xm, prefs) if r["broken"]], "vs_proposal": compare(s, xm, x0, prefs)}
    return out


def held_matrix(s, w):
    """The held-out matrix under a what-if, computed once per setting (a what-if costs a full repricing)."""
    cache = s.__dict__.setdefault("_held_cache", {})
    key = json.dumps(w.changes(), sort_keys=True)
    if key not in cache:
        cache[key] = s.held.matrix(w)[0]
    return cache[key]


def stress(s, x0, alts, w):
    """The proposal and the alternatives scored on the held-out scenarios under one what-if (a tested assumption)."""
    A_w = held_matrix(s, w)
    books = {"proposal": x0, **{k: v["x"] for k, v in alts.items()}}
    return {name: scores(A_w, x, 1.0) for name, x in books.items()}


# --- the fact sheet, the checklist control and the guide rule -----------------------------------

def fact_sheet(diag, alts, prefs, stresses=None):
    """Everything the memo may cite, as numbered facts in $ million, shares and counts."""
    sc = diag["scores"]
    funded = diag["value_with_line"]
    lines = [f"[F1] The proposal on 2,000 held-out scenarios, every construction call funded: expected NPV {sc['mean'] / 1e6:,.0f} $M; median {sc['median'] / 1e6:,.0f} $M; "
             f"chance of a loss {sc['p_loss']:.3f}; worst-5% average loss {sc['cvar'] / 1e6:,.0f} $M (negative = still a profit); "
             f"metric at tail weight {prefs.lam:g}: {sc['metric'] / 1e6:,.0f} $M."
             + ("" if diag["line_used"] is None else f" Funded within the committee's liquidity line instead: expected NPV {funded['mean'] / 1e6:,.0f} $M; "
                f"chance of a loss {funded['p_loss']:.3f}; worst-5% average loss {funded['cvar'] / 1e6:,.0f} $M; metric {funded['metric'] / 1e6:,.0f} $M. "
                "The alternatives below are scored and compared the same way, within the line.")]
    rules = "; ".join(f"{r['rule']}: {r['value']:,.3f} against {r['limit']:,.3f}{' — BROKEN' if r['broken'] else ''}" for r in diag["rules"])
    lines.append(f"[F2] Rules (the registered budget and 40% technology cap, and the committee's own): {rules}.")
    c = diag["calls"]
    line = "no liquidity line (no capital beyond the reserve)" if diag["line_used"] is None else f"the stated liquidity line of {diag['line_used'] / 1e6:,.0f} $M"
    lines.append(f"[F3] Construction calls: reserve {c['reserve'] / 1e6:,.0f} $M; exceeded in a share {c['p_over']:.3f} of scenarios; "
                 f"excess at the 95th percentile {c['excess_q95'] / 1e6:,.0f} $M. With {line}, requests beyond it forfeit their deposits and the "
                 f"proposal's expected NPV is {funded['mean'] / 1e6:,.0f} $M (chance of a loss {funded['p_loss']:.3f}).")
    m = diag["members"]
    if len(m):
        table = adv.format_table(m.round(3), "[F4] Each member of the proposal", "FORECAST on ASSUMED costs; computed by src/challenge.py",
                                 note="drop_change_*: the proposal without this member minus the proposal; fragile: chance of loss ≥ 0.7 and at least half its value in its best 5% of scenarios.")
        lines.append(table)
    for k, (name, a) in enumerate(alts.items(), start=5):
        v, s2 = a["vs_proposal"], a["scores"]
        label = {"repair": "The repair (fewest changes to the proposal that keep the committee's rules)", "optimizer": "The optimizer's book under the committee's stated preferences"}[name]
        lines.append(f"[F{k}] {label}: {a['changes']} changes; adds {', '.join(a['added']) or 'nothing'}; drops {', '.join(a['dropped']) or 'nothing'}. "
                     f"Expected NPV {s2['mean'] / 1e6:,.0f} $M; chance of a loss {s2['p_loss']:.3f}; worst-5% average loss {s2['cvar'] / 1e6:,.0f} $M. "
                     f"Against the proposal: metric {v['metric_diff'] / 1e6:+,.0f} $M [{v['metric_low'] / 1e6:+,.0f}, {v['metric_high'] / 1e6:+,.0f}], "
                     f"interval clear of zero: {'yes' if v['clear_of_zero'] else 'no'}; expected NPV {v['mean_diff'] / 1e6:+,.0f} $M; "
                     f"rules it breaks: {', '.join(a['rules_broken']) or 'none'}.")
    for j, (label, res) in enumerate((stresses or {}).items(), start=5 + len(alts)):
        parts = "; ".join(f"{b}: expected NPV {r['mean'] / 1e6:,.0f} $M, chance of a loss {r['p_loss']:.3f}, worst-5% average loss {r['cvar'] / 1e6:,.0f} $M" for b, r in res.items())
        lines.append(f"[F{j}] Tested assumption — {label} (every construction call funded): {parts}.")
    return "\n".join(lines)


def qualifying(diag, alts):
    """The alternatives the evidence lets the advisor recommend: each keeps every rule and either repairs a rule the proposal breaks or beats it clearly on the committee's objective."""
    broken = any(r["broken"] for r in diag["rules"])
    return [name for name in ("repair", "optimizer") if name in alts and not alts[name]["rules_broken"]
            and (broken or alts[name]["vs_proposal"]["clear_of_zero"])]


def guide_allowed(diag, alts):
    """The first qualifying alternative (the repair before the optimizer's book: the smaller change), or None."""
    q = qualifying(diag, alts)
    return q[0] if q else None


def checklist(diag, alts):
    """The control: the same tools, fixed rules, no language model.

    Returns ``flags`` (rule breaches, fragile members, capital calls beyond
    the reserve in more than a fifth of scenarios), ``level`` and
    ``recommended_book``.
    """
    flags = [f"rule broken: {r['rule']}" for r in diag["rules"] if r["broken"]]
    m = diag["members"]
    if len(m):
        flags += [f"fragile member: {c}" for c in m.loc[m["fragile"], "candidate"]]
    if diag["calls"]["p_over"] > 0.2:
        flags.append("construction calls exceed the reserve in more than a fifth of scenarios")
    pick = guide_allowed(diag, alts)
    level = "guide" if pick else ("challenge" if flags else "explain")
    return {"flags": flags, "level": level, "recommended_book": pick or "proposal"}


# --- the two-round challenge with the language model ----------------------------------------

def challenge(advisor, s, statement, proposal_ids, system, tag=""):
    """One proposal, end to end: read the rules, compute the facts and alternatives, write the memo, check it.

    Returns
    -------
    dict
        ``status``, ``preferences``, ``reading``, ``not_representable``,
        ``diagnosis``, ``alternatives``, ``sheet``, ``memo`` (parsed),
        ``verification`` (numbers), ``fact_refs_ok``, ``level_requested``,
        ``level`` (after the guide rule), ``checklist`` and the call statuses.
    """
    x0 = s.vector(proposal_ids)
    out = {"status": "no record", "preferences": None, "reading": None, "not_representable": None, "diagnosis": None, "alternatives": None,
           "sheet": None, "memo": None, "verification": None, "fact_refs_ok": None, "level_requested": None, "level": None, "checklist": None}
    proposal = ", ".join(proposal_ids)
    r1 = advisor.ask(system, adv.render("challenge_read", statement=statement, proposal=proposal, schema=schema_text(s.tech),
                                        whatif_schema=at.schema_text(s.ids)), "challenge-read", tag)
    if r1 is None:
        return out
    j = adv.parse_json(r1["response"]) or {}
    try:
        prefs = Preferences.from_dict(j.get("preferences", {}) or {}, s.ids, s.tech)
        out["reading"] = j.get("reading")
    except (PreferenceError, TypeError) as err:
        prefs = Preferences()
        out["reading"] = f"preferences refused by the engine ({err}); the registered defaults were used"
    out.update(preferences=asdict(prefs), not_representable=j.get("not_representable"))
    diag = diagnose(s, x0, prefs)
    alts = alternatives(s, x0, prefs)
    stresses = {}
    for wd in (j.get("whatifs") or [])[:MAX_WHATIFS]:
        try:
            w = wi.WhatIf.from_dict({**wd, "grid": s.grid}, s.ids)
            stresses[json.dumps(w.changes())] = stress(s, x0, alts, w)
        except (wi.WhatIfError, TypeError):
            continue
    sheet = fact_sheet(diag, alts, prefs, stresses)
    out.update(diagnosis=diag, alternatives=alts, sheet=sheet, checklist=checklist(diag, alts))
    r2 = advisor.ask(system, adv.render("challenge_memo", statement=statement, proposal=proposal, reading=out["reading"] or "", sheet=sheet), "challenge-memo", tag)
    if r2 is None:
        out["status"] = "computed, not challenged"
        return out
    memo = adv.parse_json(r2["response"]) or {}
    text = json.dumps(memo, ensure_ascii=False)
    refs = [f for v in memo.get("vulnerabilities", []) for f in v.get("facts", [])]
    known = {f"F{k}" for k in range(1, 5 + len(alts) + len(stresses))}
    requested = memo.get("level") if memo.get("level") in LEVELS else "explain"
    level = requested
    if requested == "guide" and memo.get("recommended_book") not in qualifying(diag, alts):
        level = "challenge"  # the evidence does not let the advisor guide toward that book; the downgrade is recorded
    out.update(status="challenged", memo=memo, verification=at.verify_attributed(text, sheet, question=statement),
               fact_refs_ok=bool(refs) and all(f in known for f in refs) and len(memo.get("vulnerabilities", [])) <= 3,
               types=[v.get("type") for v in memo.get("vulnerabilities", [])],
               types_ok=all(v.get("type") in TYPES for v in memo.get("vulnerabilities", [])),
               level_requested=requested, level=level)
    return out
