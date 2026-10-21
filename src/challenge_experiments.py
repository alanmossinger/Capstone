"""The registered experiments of the active challenger (decision #96): seeded flaws, misspecified worlds, rule reading.

What: the 48 committee cases (ten personas; 36 proposals each with one keyed
flaw, 12 clean proposals), the 40 rule statements, the builder that turns a
case into a book and checks that its keyed flaw is really there, the runners
that put each case through the challenger and cache the result, the five
worlds of experiment X2, and the scoring of criteria C25–C32.
Why: decision #94 asks whether a challenging advisor improves a committee's
decision. The cases are written and checked before any challenger run, and
every outcome is scored mechanically against the keys: detection by the type
of each vulnerability the memo names, decision value by the committee's own
stated objective, translation by the stated rules. The checklist control
(``challenge.checklist``) is scored the same way, so what the language model
adds beyond its tools is measured, not assumed.
Reads: the engines of `src/whatif.py`; `results/v8/frontier.csv` (the comparator books); `results/book_rho.csv`.
Writes: `results/v9/` through notebook 11 (cases, outputs, scores).
Used by: notebook 11 (section 11); `tests/test_challenge_experiments.py`.
"""

import json
from dataclasses import asdict, fields
from pathlib import Path

import numpy as np
import pandas as pd

from src import advisor as adv, advisor_tools as at, challenge as ch, paths, portfolio, robustness as rb, whatif as wi

SEED, N_BOOT = 2020, 1000
GAS, SOLAR_A, WIND_A = "REQ|ERCOT|25INR0008", "REQ|ERCOT|26INR0155", "REQ|ERCOT|26INR0113"
SMALL_WIND = ["REQ|ERCOT|27INR0061", "REQ|ERCOT|28INR0033", "REQ|ERCOT|28INR0113", "REQ|ERCOT|30INR0004"]

PERSONAS = {
    "P1": "the oil veteran", "P2": "the transition advocate", "P3": "the return seeker", "P4": "the cautious treasurer", "P5": "the gas bull",
    "P6": "the lender's eye", "P7": "the diversifier", "P8": "the anchored chair", "P9": "the policy worrier", "P10": "the budget hawk",
}

# What a memo must name for a keyed flaw to count as detected (by the type of one of its vulnerabilities).
ACCEPT = {"cap": {"broken rule", "concentration"}, "liquidity": {"broken rule", "unfunded construction calls"}, "ploss": {"broken rule"},
          "tail": {"broken rule"}, "excluded": {"broken rule"}, "fragile": {"fragile position"}, "sunk": {"sunk cost"},
          "double": {"double standard"}, "unsupported": {"unsupported claim"}}
REASONING = ("sunk", "double", "unsupported")
COMPUTABLE = ("cap", "liquidity", "ploss", "tail", "excluded", "fragile")
FALSE_TYPES = {"broken rule", "sunk cost", "double standard", "unsupported claim"}

# book specs: a base ("D", "C", "A", "B", "L6" = book D's six leases, "TOPL:k" = the k leases of highest expected NPV, "model" = the
# optimizer's book under the case's true preferences) with candidates added or dropped.
CASES = [
    # --- broken rules: the technology cap (the leases above 40% of the budget)
    {"id": "X01", "persona": "P1", "flaw": "cap", "book": {"base": "TOPL:8", "add": [WIND_A]}, "prefs": {},
     "statement": "Oil has carried this company for thirty years. Put the budget into our eight strongest Gulf leases and keep the agreement-backed wind request as a token of the transition."},
    {"id": "X02", "persona": "P3", "flaw": "cap", "book": {"base": "TOPL:6"}, "prefs": {},
     "statement": "The leases give the best value per dollar we can find. Fund the six best of them and nothing else."},
    {"id": "X03", "persona": "P10", "flaw": "cap", "book": {"base": "TOPL:5", "add": [WIND_A]}, "prefs": {},
     "statement": "Spend less and spend well: five leases and the one wind request that already has a signed agreement."},
    {"id": "X04", "persona": "P8", "flaw": "cap", "book": {"base": "TOPL:10"}, "prefs": {},
     "statement": "Last year's committee funded ten Gulf leases, and we see no reason to change course."},
    # --- broken rules: construction calls beyond the stated liquidity line
    {"id": "X05", "persona": "P4", "flaw": "liquidity", "book": {"base": "D"}, "prefs": {"liquidity_line_musd": 1000},
     "statement": "We back the risk-aware book. Treasury tells us we can raise at most one billion dollars beyond the reserve if construction calls come in."},
    {"id": "X06", "persona": "P6", "flaw": "liquidity", "book": {"base": "C"}, "prefs": {"liquidity_line_musd": 500},
     "statement": "Return matters, so take the deterministic book; but our lenders will not extend more than five hundred million dollars for construction beyond what we reserve now."},
    {"id": "X07", "persona": "P7", "flaw": "liquidity", "book": {"base": "B"}, "prefs": {"liquidity_line_musd": 750},
     "statement": "Equal capital across oil and power is the fair split. We can cover construction calls of up to 750 million dollars beyond the reserve."},
    {"id": "X08", "persona": "P3", "flaw": "liquidity", "book": {"base": "A"}, "prefs": {"liquidity_line_musd": 1500},
     "statement": "Rank the candidates by expected value and fund from the top. Our credit line beyond the reserve is one and a half billion dollars."},
    # --- broken rules: the stated chance-of-loss limit
    {"id": "X09", "persona": "P4", "flaw": "ploss", "book": {"base": "D"}, "prefs": {"max_p_loss": 0.05},
     "statement": "We take the risk-aware book, provided the chance of losing money on it is no more than one in twenty."},
    {"id": "X10", "persona": "P6", "flaw": "ploss", "book": {"base": "C"}, "prefs": {"max_p_loss": 0.08},
     "statement": "The deterministic book earns the most. Our board will not accept more than an eight percent chance of losing money."},
    {"id": "X11", "persona": "P8", "flaw": "ploss", "book": {"base": "A"}, "prefs": {"max_p_loss": 0.10},
     "statement": "Fund the ranking as it was presented to us; we accept at most a ten percent chance of losing money."},
    {"id": "X12", "persona": "P2", "flaw": "ploss", "book": {"base": "B"}, "prefs": {"max_p_loss": 0.09},
     "statement": "Half to oil, half to power: that is balance. We cannot have more than a nine percent chance of a loss."},
    # --- broken rules: the stated worst-5% loss limit
    {"id": "X13", "persona": "P6", "flaw": "tail", "book": {"base": "D"}, "prefs": {"max_cvar_musd": 600},
     "statement": "The risk-aware book, please. Our lenders cap the average loss in the worst five percent of outcomes at six hundred million dollars."},
    {"id": "X14", "persona": "P4", "flaw": "tail", "book": {"base": "C"}, "prefs": {"max_cvar_musd": 900},
     "statement": "Take the highest-return book. In a bad year — the worst five percent — we must not lose more than nine hundred million on average."},
    {"id": "X15", "persona": "P10", "flaw": "tail", "book": {"base": "B"}, "prefs": {"max_cvar_musd": 1000},
     "statement": "Split the capital evenly between the sectors. Our worst-five-percent average loss has to stay under one billion dollars."},
    {"id": "X16", "persona": "P8", "flaw": "tail", "book": {"base": "A"}, "prefs": {"max_cvar_musd": 1200},
     "statement": "We fund the top of the ranking as usual, with a limit of 1.2 billion dollars on the average loss in the worst five percent of outcomes."},
    # --- broken rules: a technology the committee excludes
    {"id": "X17", "persona": "P2", "flaw": "excluded", "book": {"base": "D"}, "prefs": {"excluded_technologies": ["Gas CC"]},
     "statement": "We will not put money into new gas plants. Within that, we back the risk-aware book."},
    {"id": "X18", "persona": "P9", "flaw": "excluded", "book": {"base": "C"}, "prefs": {"excluded_technologies": ["Gas CC"]},
     "statement": "Gas plants are a policy risk we will not carry. Take the highest-return book."},
    {"id": "X19", "persona": "P9", "flaw": "excluded", "book": {"base": "D"}, "prefs": {"excluded_technologies": ["Solar"]},
     "statement": "Solar's tax credits could vanish, so leave solar out entirely. Otherwise we accept the risk-aware book."},
    {"id": "X20", "persona": "P1", "flaw": "excluded", "book": {"base": "A"}, "prefs": {"excluded_technologies": ["Storage"]},
     "statement": "Batteries are still a science project; no storage. Fund the top of the ranking."},
    # --- reliance on a fragile position (no stated rule is broken)
    {"id": "X21", "persona": "P5", "flaw": "fragile", "relies_on": [GAS], "book": {"base": "D"}, "prefs": {},
     "statement": "We back the risk-aware book because of the 1,350 MW gas request: it is the biggest earner on the list, and Texas will always pay for power when the wind drops."},
    {"id": "X22", "persona": "P2", "flaw": "fragile", "relies_on": [SOLAR_A], "book": {"base": "D"}, "prefs": {},
     "statement": "The 1,026 MW solar request with a signed agreement is the reason to own this book; solar is where Texas is growing."},
    {"id": "X23", "persona": "P7", "flaw": "fragile", "relies_on": ["REQ|ERCOT|28INR0033"], "book": {"base": "L6", "add": ["REQ|ERCOT|28INR0033"]}, "prefs": {},
     "statement": "The six leases plus the 1,200 MW wind request: that wind request gives us real exposure to the transition at low cost."},
    {"id": "X24", "persona": "P3", "flaw": "fragile", "relies_on": SMALL_WIND, "book": {"base": "D"}, "prefs": {},
     "statement": "The four smaller wind requests are cheap options with big upside; they are why this book beats a pure lease book."},
    # --- sunk cost
    {"id": "X25", "persona": "P5", "flaw": "sunk", "book": {"base": "D"}, "prefs": {},
     "statement": "We have already paid study deposits on the 1,350 MW gas request. Walking away now would waste that money, so it stays in."},
    {"id": "X26", "persona": "P9", "flaw": "sunk", "book": {"base": "D"}, "prefs": {},
     "statement": "We spent two years and real money getting the 1,026 MW solar request to its agreement. We cannot drop it now."},
    {"id": "X27", "persona": "P8", "flaw": "sunk", "book": {"base": "C"}, "prefs": {},
     "statement": "The company has already sunk capital into the Gulf, so the leases must take the largest share again."},
    {"id": "X28", "persona": "P1", "flaw": "sunk", "book": {"base": "D"}, "prefs": {},
     "statement": "We have paid for the seismic and the engineering on these six leases; that money is lost unless we redevelop them."},
    # --- double standard
    {"id": "X29", "persona": "P1", "flaw": "double", "book": {"base": "L6", "add": [WIND_A]}, "prefs": {},
     "statement": "The leases earn far more on average than any power request, while the power requests lose money in most scenarios, so we keep power to the one wind request."},
    {"id": "X30", "persona": "P2", "flaw": "double", "book": {"base": "B"}, "prefs": {},
     "statement": "Renewables should be judged on their long-run value; the leases should be judged on their worst years, when oil collapses."},
    {"id": "X31", "persona": "P5", "flaw": "double", "book": {"base": "C"}, "prefs": {},
     "statement": "We look at the gas plants in their best years, because that is when they earn, and at the leases in their average years."},
    {"id": "X32", "persona": "P6", "flaw": "double", "book": {"base": "L6"}, "prefs": {},
     "statement": "We hold the leases to their expected value and the power requests to their chance of loss; by that test only the leases pass."},
    # --- unsupported claims
    {"id": "X33", "persona": "P3", "flaw": "unsupported", "book": {"base": "C"}, "prefs": {},
     "statement": "Interest rates will fall next year, which lifts every project's value, so we should take the highest-return book."},
    {"id": "X34", "persona": "P2", "flaw": "unsupported", "book": {"base": "B"}, "prefs": {},
     "statement": "A federal carbon tax is coming within two years and will make the leases worthless, so we split the budget equally to hedge."},
    {"id": "X35", "persona": "P5", "flaw": "unsupported", "book": {"base": "D"}, "prefs": {},
     "statement": "Data centres will double Texas power demand by 2028, so the gas request will run flat out; back the risk-aware book."},
    {"id": "X36", "persona": "P9", "flaw": "unsupported", "book": {"base": "L6", "add": [WIND_A]}, "prefs": {},
     "statement": "Congress will extend the wind credit indefinitely, so the wind request is risk-free; keep the leases and that request."},
    # --- clean: the proposal is the optimizer's book under the committee's stated rules, and the statement is consistent
    {"id": "X37", "persona": "P8", "flaw": "none", "book": {"base": "model"}, "prefs": {"lam": 1.0},
     "statement": "We want the book that best balances expected value against the worst years, counting a dollar of loss in the worst five percent like a dollar of expected value."},
    {"id": "X38", "persona": "P3", "flaw": "none", "book": {"base": "model"}, "prefs": {"lam": 0.0},
     "statement": "Expected value is what we answer for: the book with the highest expected NPV within the budget and the technology cap."},
    {"id": "X39", "persona": "P6", "flaw": "none", "book": {"base": "model"}, "prefs": {"lam": 2.0},
     "statement": "We count a dollar of loss in the worst five percent of outcomes twice as heavily as a dollar of expected value."},
    {"id": "X40", "persona": "P4", "flaw": "none", "book": {"base": "model"}, "prefs": {"max_cvar_musd": 1300},
     "statement": "Our lenders want the average loss in the worst five percent below 1.3 billion dollars; within that, the best risk-adjusted book."},
    {"id": "X41", "persona": "P10", "flaw": "none", "book": {"base": "model"}, "prefs": {"max_cvar_musd": 1100},
     "statement": "Keep the worst-five-percent average loss under 1.1 billion dollars, and otherwise give us the best risk-adjusted book."},
    {"id": "X42", "persona": "P2", "flaw": "none", "book": {"base": "model"}, "prefs": {"excluded_technologies": ["Gas CC"]},
     "statement": "We will not fund new gas plants; otherwise the best risk-adjusted book."},
    {"id": "X43", "persona": "P9", "flaw": "none", "book": {"base": "model"}, "prefs": {"excluded_technologies": ["Solar"]},
     "statement": "Leave solar out; otherwise the best risk-adjusted book."},
    {"id": "X44", "persona": "P7", "flaw": "none", "book": {"base": "model"}, "prefs": {"excluded_technologies": ["Storage"]},
     "statement": "Leave storage out; otherwise the best risk-adjusted book."},
    {"id": "X45", "persona": "P4", "flaw": "none", "book": {"base": "model"}, "prefs": {"liquidity_line_musd": 2000},
     "statement": "We can raise up to two billion dollars beyond the reserve for construction; within that, the best risk-adjusted book."},
    {"id": "X46", "persona": "P6", "flaw": "none", "book": {"base": "model"}, "prefs": {"liquidity_line_musd": 3000, "max_cvar_musd": 1300},
     "statement": "We can cover three billion dollars of construction beyond the reserve, and the worst-five-percent average loss must stay below 1.3 billion; within that, the best risk-adjusted book."},
    {"id": "X47", "persona": "P1", "flaw": "none", "book": {"base": "model"}, "prefs": {"lam": 0.5},
     "statement": "We count a dollar of loss in the worst five percent of outcomes at half a dollar of expected value."},
    {"id": "X48", "persona": "P5", "flaw": "none", "book": {"base": "model"}, "prefs": {"excluded_technologies": ["Storage"], "lam": 0.0},
     "statement": "Storage is out; otherwise maximise expected NPV."},
]

# X3: committee rules in words, and what a correct reading sets (fields not listed stay at their defaults).
STATEMENTS = [
    ("S01", "We will not accept more than a ten percent chance of losing money on the book.", {"max_p_loss": 0.10}),
    ("S02", "Our lenders cap the average loss in the worst five percent of outcomes at 750 million dollars.", {"max_cvar_musd": 750}),
    ("S03", "No gas, full stop.", {"excluded_technologies": ["Gas CC"]}),
    ("S04", "We can find 1.5 billion dollars beyond the reserve for construction.", {"liquidity_line_musd": 1500}),
    ("S05", "Commit at least ninety percent of the budget.", {"min_utilization": 0.90}),
    ("S06", "A one-in-twenty chance of a loss is our ceiling.", {"max_p_loss": 0.05}),
    ("S07", "Keep storage out of the book, and the worst-five-percent average loss under 600 million.", {"excluded_technologies": ["Storage"], "max_cvar_musd": 600}),
    ("S08", "A dollar lost in the worst five percent of outcomes counts twice as much to us as a dollar of expected value.", {"lam": 2.0}),
    ("S09", "Only expected value matters to this committee; we are risk-neutral.", {"lam": 0.0}),
    ("S10", "We will not fund the 1,350 MW gas request, REQ|ERCOT|25INR0008.", {"excluded_ids": [GAS]}),
    ("S11", "No solar and no storage.", {"excluded_technologies": ["Solar", "Storage"]}),
    ("S12", "Our credit line for construction beyond the reserve is one billion dollars.", {"liquidity_line_musd": 1000}),
    ("S13", "We want at most an eight percent chance of losing money, and at least eighty percent of the budget committed.", {"max_p_loss": 0.08, "min_utilization": 0.80}),
    ("S14", "Treat a dollar of tail loss as half a dollar of value.", {"lam": 0.5}),
    ("S15", "The worst five percent of outcomes may not cost us more than 1.2 billion dollars on average.", {"max_cvar_musd": 1200}),
    ("S16", "We do not do wind.", {"excluded_technologies": ["Wind"]}),
    ("S17", "Leave out the Gulf leases altogether.", {"excluded_technologies": ["Lease redevelopment"]}),
    ("S18", "We can raise 500 million dollars for construction calls beyond what we reserve now, no more.", {"liquidity_line_musd": 500}),
    ("S19", "Spend at least three quarters of the budget.", {"min_utilization": 0.75}),
    ("S20", "Our board accepts a chance of loss of up to fifteen percent.", {"max_p_loss": 0.15}),
    ("S21", "Exclude the 836 MW wind request REQ|ERCOT|26INR0113 and the 1,026 MW solar request REQ|ERCOT|26INR0155.", {"excluded_ids": [WIND_A, SOLAR_A]}),
    ("S22", "We weigh losses in the worst five percent four times as heavily as expected value.", {"lam": 4.0}),
    ("S23", "Batteries are out, and the average loss in the worst five percent must stay below 900 million.", {"excluded_technologies": ["Storage"], "max_cvar_musd": 900}),
    ("S24", "Two billion dollars is available for construction beyond the reserve.", {"liquidity_line_musd": 2000}),
    ("S25", "A chance of losing money above six percent is unacceptable.", {"max_p_loss": 0.06}),
    ("S26", "No new gas plants, and at most a twelve percent chance of a loss.", {"excluded_technologies": ["Gas CC"], "max_p_loss": 0.12}),
    ("S27", "Put at least sixty percent of the budget to work.", {"min_utilization": 0.60}),
    ("S28", "Our worst-five-percent average loss limit is 450 million dollars.", {"max_cvar_musd": 450}),
    ("S29", "We count expected value and tail loss one for one.", {"lam": 1.0}),
    ("S30", "No solar requests, and we can call 800 million dollars beyond the reserve for construction.", {"excluded_technologies": ["Solar"], "liquidity_line_musd": 800}),
    ("S31", "Exclude the lease G14658.", {"excluded_ids": ["LEASE|G14658"]}),
    ("S32", "Risk-neutral, and no storage.", {"lam": 0.0, "excluded_technologies": ["Storage"]}),
    # out of scope: the correct reading says so and sets nothing
    ("S33", "Interest rates will rise two points; choose the book that survives that.", None),
    ("S34", "Price carbon at 80 dollars a tonne in every project.", None),
    ("S35", "Every project must clear an internal rate of return of twelve percent.", None),
    ("S36", "Only fund projects with an ESG rating of A or better.", None),
    ("S37", "Hedge the oil exposure with futures before committing.", None),
    ("S38", "Assume inflation runs at five percent a year.", None),
    ("S39", "Prefer projects that a partner would co-invest in.", None),
    ("S40", "Include hydrogen projects in the book.", None),
]


def comparator_books(s):
    """Books A, B and C of notebook 11 (results/v8/frontier.csv) as 0/1 vectors."""
    f = pd.read_csv(paths.RESULTS / "v8" / "frontier.csv").set_index("policy")
    names = {"A": "A NPV ranking", "B": "B equal capital by sector", "C": "C deterministic MILP"}
    return {k: s.vector(f.loc[v, "members"].split(";")) for k, v in names.items()}


def book_of(s, spec, prefs, books):
    """The 0/1 book of a case spec."""
    base = spec["base"]
    if base == "D":
        x = np.asarray(s.x_model, int).copy()
    elif base in books:
        x = books[base].copy()
    elif base == "L6":
        x = np.asarray(s.x_model, int) * (s.sel.candidates["sector"].to_numpy() != "ERCOT power")
    elif base.startswith("TOPL:"):
        k = int(base.split(":")[1])
        lease = np.where(s.sel.candidates["sector"].to_numpy() != "ERCOT power")[0]
        top = lease[np.argsort(-s.A[:, lease].mean(axis=0))][:k]
        x = np.zeros(len(s.ids), int)
        x[top] = 1
    elif base == "model":
        x = ch.model_book(s, prefs)
        if x is None:
            raise ValueError(f"no book meets {prefs}")
        x = np.asarray(x, int)
    else:
        raise ValueError(f"unknown base {base}")
    x = x.copy()
    for m in spec.get("add", []):
        x[s.ids.index(m)] = 1
    for m in spec.get("drop", []):
        x[s.ids.index(m)] = 0
    return x


def build_cases(s):
    """Every case with its book, and a check that its keyed flaw is in the facts the challenger will see.

    Returns
    -------
    tuple of (list, pandas.DataFrame)
        The cases with ``members`` added, and one verification row per case.

    Raises
    ------
    AssertionError
        When a case does not hold its keyed flaw (a rule case whose rule is not
        broken, a fragile case whose member is not fragile) or a clean case
        breaks a rule or has an alternative: the case list is wrong and must be
        fixed before registration, not after the run.
    """
    books = comparator_books(s)
    out, rows = [], []
    for c in CASES:
        prefs = ch.Preferences(**c["prefs"])
        x = book_of(s, c["book"], prefs, books)
        diag = ch.diagnose(s, x, prefs)
        broken = [r["rule"] for r in diag["rules"] if r["broken"]]
        fragile = set(diag["members"].loc[diag["members"]["fragile"], "candidate"]) if len(diag["members"]) else set()
        ok = True
        if c["flaw"] == "cap":
            ok = any(r.startswith("technology cap") or r.startswith("budget") for r in broken)
        elif c["flaw"] == "liquidity":
            ok = any(r.startswith("construction calls") for r in broken)
        elif c["flaw"] == "ploss":
            ok = "chance of a loss" in broken
        elif c["flaw"] == "tail":
            ok = any(r.startswith("worst-5%") for r in broken)
        elif c["flaw"] == "excluded":
            ok = "excluded candidates held (count)" in broken
        elif c["flaw"] == "fragile":
            ok = all(m in fragile for m in c["relies_on"]) and not broken
        elif c["flaw"] in REASONING:
            ok = True  # a reasoning flaw is in the words; the book may or may not break a rule, and the case is keyed on the words
        elif c["flaw"] == "none":
            ok = not broken and not ch.alternatives(s, x, prefs)
        assert ok, f"{c['id']}: keyed flaw '{c['flaw']}' is not in the facts (broken: {broken}; fragile: {sorted(fragile)})"
        out.append({**c, "members": [s.ids[i] for i in np.where(x == 1)[0]]})
        rows.append({"id": c["id"], "persona": c["persona"], "flaw": c["flaw"], "n_members": int(x.sum()), "rules_broken": "; ".join(broken),
                     "fragile_members": len(fragile), "verified": ok})
    return out, pd.DataFrame(rows)


def compact(out, s):
    """A challenger result reduced to what the scoring and the record need (no arrays)."""
    alts = {k: {"members": [s.ids[i] for i in np.where(np.asarray(v["x"]) == 1)[0]], "changes": v["changes"], "rules_broken": v["rules_broken"],
                "vs_proposal": v["vs_proposal"]} for k, v in (out.get("alternatives") or {}).items()}
    memo = out.get("memo") or {}
    return {"status": out["status"], "preferences": out["preferences"], "reading": out["reading"], "not_representable": out["not_representable"],
            "memo": memo, "types": out.get("types"), "types_ok": out.get("types_ok"), "fact_refs_ok": out["fact_refs_ok"],
            "verification": out["verification"], "level_requested": out["level_requested"], "level": out["level"],
            "recommended_book": memo.get("recommended_book"), "evidence_insufficient": memo.get("evidence_insufficient"),
            "checklist": out["checklist"], "alternatives": alts}


def run_x1(advisor, s, cases, cache, system, log=print):
    """Each case through the challenger, cached one JSON line per case (a rerun reads the cache and replays the record)."""
    cache = Path(cache)
    done = {}
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["id"]] = r
    for c in cases:
        if c["id"] in done:
            continue
        out = ch.challenge(advisor, s, c["statement"], c["members"], system, tag=f"x1-{c['id']}")
        r = {"id": c["id"], **compact(out, s)}
        with open(cache, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False, default=float) + "\n")
        done[c["id"]] = r
        log(f"{c['id']} {c['flaw']}: {r['status']}, level {r['level']}, types {r['types']}")
    return [done[c["id"]] for c in cases]


def detected(case, r):
    """Whether the challenger's memo names the case's keyed flaw (by vulnerability type)."""
    return bool(r.get("types")) and bool(set(r["types"]) & ACCEPT[case["flaw"]])


def checklist_detected(case, r):
    """Whether the checklist control flags the keyed flaw: rule flaws by a broken rule, a fragile case by its member; it cannot read words."""
    flags = (r.get("checklist") or {}).get("flags", [])
    if case["flaw"] in ("cap", "liquidity", "ploss", "tail", "excluded"):
        return any(f.startswith("rule broken") for f in flags)
    if case["flaw"] == "fragile":
        return all(any(f == f"fragile member: {m}" for f in flags) for m in case["relies_on"])
    return False


def false_challenge(r):
    """A clean case challenged on grounds it does not have: a guide, or a broken rule, sunk cost, double standard or unsupported claim named."""
    return r.get("level") == "guide" or bool(set(r.get("types") or []) & FALSE_TYPES)


def score_x1(cases, results):
    """One row per case: detection by the challenger and the checklist, false challenges on clean cases, grounding."""
    rows = []
    for c, r in zip(cases, results):
        v = r.get("verification") or {}
        rows.append({"id": c["id"], "persona": c["persona"], "flaw": c["flaw"], "status": r["status"], "level": r["level"],
                     "challenger_detects": detected(c, r) if c["flaw"] != "none" else np.nan,
                     "checklist_detects": checklist_detected(c, r) if c["flaw"] != "none" else np.nan,
                     "false_challenge": false_challenge(r) if c["flaw"] == "none" else np.nan,
                     "checklist_false_challenge": (any(f.startswith("rule broken") for f in r["checklist"]["flags"]) or r["checklist"]["level"] == "guide") if c["flaw"] == "none" else np.nan,
                     "all_numbers_grounded": v.get("rate") == 1.0, "grounding_rate": v.get("rate"), "fact_refs_ok": r.get("fact_refs_ok"), "types_ok": r.get("types_ok"),
                     "guided": r["level"] == "guide", "checklist_guided": r["checklist"]["level"] == "guide"})
    return pd.DataFrame(rows)


# --- X2: the decision in worlds where the base model is wrong ------------------------------

def worlds(s):
    """The held-out matrix and operation years of five worlds: the base model and four ways it could be wrong."""
    base = {"base model": (s.A_h, s.held.op_year)}
    for name, w in (("ERCOT prices 25% lower", wi.WhatIf(grid=s.grid, ercot_multiplier=0.75)), ("ERCOT half as volatile", wi.WhatIf(grid=s.grid, ercot_volatility=0.5)),
                    ("lease capital 30% higher", wi.WhatIf(grid=s.grid, lease_cost_multiplier=1.3))):
        base[name] = (ch.held_matrix(s, w), s.held.op_year)
    rho = float(pd.read_csv(paths.RESULTS / "book_rho.csv")["rho"].iloc[0])
    P_look = s.sel.power[[f"p_lookup_{h}" for h in range(1, 8)]].to_numpy(float)
    look = portfolio.simulate_operation_years(P_look, s.sel.power["technology"].to_numpy(), rho, n_draws=len(s.held.prices), seed=SEED + 1040)
    keep = s.held.op_year
    s.held.op_year = look
    try:
        A_look = s.held.matrix(s.w)[0]
    finally:
        s.held.op_year = keep
    base["completion as the lookup says"] = (A_look, look)
    return base


def world_totals(s, x, prefs, A, op_year):
    """A book's value in each scenario of one world, funded within the committee's stated line (``challenge.totals`` for any world)."""
    x = np.asarray(x, int)
    if prefs.liquidity_line_musd is None:
        return A @ x
    lease = np.ones(len(s.ids), bool)
    lease[s.power_idx] = False
    reserve = float((s.capex_p * s.p7)[x[s.power_idx] == 1].sum())
    return A[:, lease] @ x[lease] + rb.funding_or_forfeit(A[:, s.power_idx], op_year, s.capex_p, s.carry_p, x[s.power_idx], reserve,
                                                           prefs.liquidity_line_musd * 1e6, s.priority, fee=getattr(s, "fee", 0.0), rate=getattr(s, "rate", 0.0))


def final_books(s, case, r):
    """The book the committee ends with under each policy: keep its proposal, follow the checklist, follow the challenger."""
    x0 = s.vector(case["members"])
    alts = r["alternatives"]
    chk = r["checklist"]
    x_chk = s.vector(alts[chk["recommended_book"]]["members"]) if chk["level"] == "guide" and chk["recommended_book"] in alts else x0
    x_llm = s.vector(alts[r["recommended_book"]]["members"]) if r["level"] == "guide" and r["recommended_book"] in alts else x0
    return {"proposal": x0, "checklist": x_chk, "challenger": x_llm}


def optimizer_first(s, case, r):
    """A second fixed rule, reported and not registered: when the checklist guides, take the optimizer's book if it qualifies, else the repair.

    Notes
    -----
    The registered checklist takes the repair first (the smaller change).
    The challenger may choose the optimizer's book instead; this rule asks
    whether that choice alone, made without reading the committee's words,
    explains the challenger's edge over the checklist (C31).
    """
    x0 = s.vector(case["members"])
    chk, alts = r["checklist"], r["alternatives"]
    if chk["level"] != "guide":
        return x0
    broken = any(f.startswith("rule broken") for f in chk["flags"])
    best = alts.get("optimizer")
    if best and not best["rules_broken"] and (broken or best["vs_proposal"]["clear_of_zero"]):
        return s.vector(best["members"])
    return s.vector(alts[chk["recommended_book"]]["members"])


def score_x2(s, cases, results, world_set):
    """One row per flawed case, world and policy: the committee's own metric, the worst-5% loss and the chance of a loss."""
    rows = []
    for c, r in zip(cases, results):
        if c["flaw"] == "none":
            continue
        prefs = ch.Preferences(**c["prefs"])  # the committee's true rules, not the challenger's reading of them
        fb = final_books(s, c, r)
        for wname, (A, oy) in world_set.items():
            for policy, x in fb.items():
                t = world_totals(s, x, prefs, A, oy)
                sc = ch.scores_of(t, prefs.lam)
                rows.append({"id": c["id"], "flaw": c["flaw"], "world": wname, "policy": policy, "changed": bool(np.any(x != fb["proposal"])), **sc})
    return pd.DataFrame(rows)


def case_bootstrap(per_case, n_boot=N_BOOT, seed=SEED):
    """Mean of a per-case difference and its 95% interval by resampling cases."""
    d = np.asarray(per_case, float)
    draws = np.random.default_rng(seed).choice(d, size=(n_boot, len(d))).mean(axis=1)
    return {"mean": float(d.mean()), "low": float(np.percentile(draws, 2.5)), "high": float(np.percentile(draws, 97.5)), "n": len(d)}


# --- X3: reading rules from words -----------------------------------------------------------

def run_x3(advisor, s, cache, system, log=print):
    """Each rule statement through the reading round only, cached one line per statement."""
    cache = Path(cache)
    done = {}
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["id"]] = r
    proposal = ", ".join(s.ids[i] for i in np.where(np.asarray(s.x_model) == 1)[0])
    for sid, text, _ in STATEMENTS:
        if sid in done:
            continue
        a = advisor.ask(system, adv.render("challenge_read", statement=text, proposal=proposal, schema=ch.schema_text(s.tech), whatif_schema=at.schema_text(s.ids)),
                        "challenge-read", f"x3-{sid}")
        j = adv.parse_json(a["response"]) if a else {}
        r = {"id": sid, "status": "no record" if a is None else "read", "preferences": (j or {}).get("preferences"), "not_representable": (j or {}).get("not_representable", "")}
        with open(cache, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        done[sid] = r
        log(f"{sid}: {r['preferences']} | {r['not_representable']!r}")
    return [done[sid] for sid, _, _ in STATEMENTS]


def _same(a, b):
    if isinstance(b, list):
        return sorted(a or []) == sorted(b)
    if b is None:
        return a is None
    return a is not None and abs(float(a) - float(b)) <= 0.01 * max(abs(float(b)), 1e-9)


def score_x3(s, results):
    """One row per statement: whether the reading sets exactly the keyed rules (or, out of scope, says so and sets nothing)."""
    defaults = asdict(ch.Preferences())
    rows = []
    for (sid, text, key), r in zip(STATEMENTS, results):
        try:
            got = asdict(ch.Preferences.from_dict(r.get("preferences") or {}, s.ids, s.tech))
            valid = True
        except (ch.PreferenceError, TypeError):
            got, valid = None, False
        if key is None:
            correct = valid and got == defaults and bool((r.get("not_representable") or "").strip())
        else:
            expected = {**defaults, **key}
            correct = valid and all(_same(got[f.name], expected[f.name]) for f in fields(ch.Preferences))
        rows.append({"id": sid, "in_scope": key is not None, "correct": bool(correct), "valid": valid, "statement": text,
                     "read": json.dumps(r.get("preferences"), ensure_ascii=False), "not_representable": r.get("not_representable", "")})
    return pd.DataFrame(rows)


# --- the registration (written and committed before any challenger run) ---------------------

CRITERIA = [
    {"id": "C25", "experiment": "X1 seeded flaws", "line": "the challenger names the keyed flaw in the 12 reasoning-flaw cases (sunk cost, double standard, unsupported claim)",
     "metric": "recall: share of the 12 cases whose memo names a vulnerability of the accepted type", "rule": "recall >= 0.75"},
    {"id": "C26", "experiment": "X1 seeded flaws", "line": "the challenger names the keyed flaw in the 24 computable-flaw cases (cap, liquidity, chance of loss, tail, exclusion, fragile position)",
     "metric": "recall over the 24 cases", "rule": "recall >= 0.90"},
    {"id": "C27", "experiment": "X1 seeded flaws", "line": "the challenger does not challenge the 12 clean cases on grounds they do not have",
     "metric": "false-challenge rate: share of clean cases with a guide, or a broken rule, sunk cost, double standard or unsupported claim named", "rule": "rate <= 0.15"},
    {"id": "C28", "experiment": "X1 seeded flaws", "line": "the memos cite only computed numbers and real facts",
     "metric": "share of the 48 memos with every number grounded; share with valid fact references", "rule": "first >= 0.80 and second >= 0.95"},
    {"id": "C29", "experiment": "X2 misspecified worlds", "line": "following the challenger improves the committee's own objective over its proposal",
     "metric": "per flawed case, the mean over the five worlds of metric(challenger's final book) - metric(proposal), the committee's stated tail weight, funded within its stated line; averaged over the 36 cases",
     "rule": "case-bootstrap 95% interval (1,000 resamples, seed 2020) entirely above 0"},
    {"id": "C30", "experiment": "X2 misspecified worlds", "line": "following the challenger avoids loss",
     "metric": "per flawed case, CVaR95 loss of the proposal minus that of the challenger's final book in the base world; averaged over the 36 cases",
     "rule": "case-bootstrap 95% interval entirely above 0"},
    {"id": "C31", "experiment": "X2 misspecified worlds", "line": "the language model adds decision value beyond its tools",
     "metric": "as C29, the challenger's final book minus the checklist's final book", "rule": "case-bootstrap 95% interval entirely above 0"},
    {"id": "C32", "experiment": "X3 rule reading", "line": "the challenger reads the committee's rules from words",
     "metric": "share of the 32 in-scope statements read exactly; out-of-scope statements refused (said so, set nothing)",
     "rule": "share >= 0.85 and at least 6 of 8 refused"},
]
THESIS = {"H4": "the challenger finds what tools alone cannot, without over-challenging: C25 and C27 pass",
          "H5": "challenging improves the committee's decision: C29 and C30 pass",
          "H6": "the language model adds decision value beyond its tools: C31 passes",
          "H7": "the challenger reads rules reliably: C32 passes"}


def registration(model):
    """The registered record: criteria, thesis rule, and the hashes of everything the outcome depends on (cases, statements, prompts, model)."""
    import hashlib

    def sha(obj):
        return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

    # hashed as text, so a checkout that changes line endings does not read as a changed prompt
    prompts = {n: hashlib.sha256((paths.REPO / "prompts" / f"{n}.md").read_text(encoding="utf-8").encode("utf-8")).hexdigest() for n in ("advisor_system", "challenge_read", "challenge_memo")}
    return {"decided": "2026-10-20", "decision": 96, "criteria": CRITERIA, "thesis_rule": THESIS, "model": model,
            "cases_sha256": sha(CASES), "statements_sha256": sha(STATEMENTS), "prompts_sha256": prompts,
            "n_cases": len(CASES), "n_clean": sum(c["flaw"] == "none" for c in CASES), "n_statements": len(STATEMENTS),
            "worlds": ["base model", "ERCOT prices 25% lower", "ERCOT half as volatile", "lease capital 30% higher", "completion as the lookup says"],
            "policies": {"proposal": "the committee keeps its book", "checklist": "adopt the checklist's book when it guides (no language model)",
                         "challenger": "adopt the book the challenger guides toward; otherwise keep the proposal"},
            "reported_not_registered": ["checklist recall per flaw", "results per world", "changes in the chance of a loss",
                                        "Alan's own cases, scored separately when he writes them"],
            "status": "post-registration extension of report v8; scored once"}
