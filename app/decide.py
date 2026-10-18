"""The decision page of v8: the alternatives, your book, the models' answers to your questions, then a decision a person authorizes.

What: a Streamlit page (``make decide-page``) in four steps. Step 1 — the
alternatives: the frontier of books over risk policies and the decision
processes compared on held-out scenarios (notebook 11), and a slider for
how much the committee weighs the tail, which shows the book that weight
picks. Step 2 — the decision-maker picks a book and states, in their own
words, why and what would change their mind; nothing below opens before
that. Step 3 — the models answer: a scenario lab whose controls are the
validated ``WhatIf`` parameters, re-solved by the engine on the spot, and
a box for a question in words that the advisor turns into parameters (or
declines) and explains from the computed result only. Step 4 — the
decision: a verb, the members and the name of the person authorizing;
a book that departs from the model's for the chosen weight is an override
and needs the five answers of the gate and the opposing case read; the
ledger refuses anything else.
Why: the brief asks for an executive interface that shows actual model
outputs and says when it cannot answer; Alan asked for one page that
explains the alternatives first and makes the human think before the
advisor speaks (14 Oct 2026). Every number shown is read from
``results/v8/`` or computed by ``src/whatif.py`` while the page runs.
Reads: ``results/v8/*.csv``, the engine's inputs (``src/whatif.py``),
``prompts/``, ``results/advisor_runs.jsonl``.
Writes: ``results/decision_ledger_v8.jsonl`` (append, through ``src/ledger.py``);
``results/advisor_runs.jsonl`` (live calls only).
Used by: ``streamlit run app/decide.py``; ``tests/test_decide_app.py``.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv, advisor_tools as at, ledger, paths, whatif as wi  # noqa: E402

st.set_page_config(page_title="Decide the book", layout="centered")
V8 = paths.RESULTS / "v8"
INTERACTIVE_SCENARIOS = 500  # the lab re-solves on the first 500 primary scenarios; the report's figures use 2,000


@st.cache_data
def tables():
    """The notebook-11 tables the page shows."""
    return {name: pd.read_csv(V8 / f"{name}.csv") for name in ("frontier", "policy_choice", "process_comparison", "statuses", "explanations")}


@st.cache_resource
def engine():
    """The what-if engine on the interactive scenario count."""
    return wi.Engine(INTERACTIVE_SCENARIOS, "primary")


def money(x):
    return "—" if pd.isna(x) else f"${x / 1e9:,.2f}B"


T = tables()
st.title("Decide the book")
st.caption("Committee grid, contracted case, decisions on 1 January 2025. Every figure is a model output from notebook 11 or computed here by the engine; "
           "lease costs are ASSUMED, request timing and prices are FORECAST.")

# --- step 1: the alternatives ---------------------------------------------------------------------
st.header("1. The alternatives")
proc = T["process_comparison"]
st.dataframe(pd.DataFrame({"process": proc["process"], "expected NPV": proc["mean"].map(money), "median": proc["median"].map(money),
                           "worst-5% loss": proc["cvar_loss"].map(money), "chance of a loss": proc["p_loss"].map(lambda v: f"{v:.0%}"),
                           "regret vs hindsight": proc["regret_vs_hindsight"].map(money)}), hide_index=True)
choice = T["policy_choice"]
w = st.slider("How much does the committee weigh the worst-5% loss against expected NPV? (w in E[NPV] − w × loss)", 0.0, 10.0, 1.0, 0.25)
picked = choice.iloc[(choice["tail_weight_w"] - w).abs().argmin()]
st.markdown(f"At w = {w:g} the frontier picks **{picked['policy']}**: expected NPV {money(picked['mean'])}, worst-5% loss {money(picked['cvar_loss'])}.")
model_members = [m for m in str(picked["members"]).split(";") if m]

# --- step 2: your book, before anyone else speaks ----------------------------------------------------
st.header("2. Your book and why")
front = T["frontier"].dropna(subset=["mean"]).drop_duplicates(subset=["members"])
options = list(front["policy"])
mine = st.radio("The book you would fund", options, index=options.index(picked["policy"]) if picked["policy"] in options else 0)
reasons = st.text_area("Why this book, in your own words")
flip = st.text_input("What figure, at what level, would change your mind?")
ready = len(reasons.strip()) >= 20 and len(flip.strip()) >= 10
if not ready:
    st.info("The models answer after you have stated your book, your reasons and what would change your mind.")
    st.stop()
my_members = [m for m in str(front.set_index("policy").loc[mine, "members"]).split(";") if m]

# --- step 3: the models answer ----------------------------------------------------------------------
st.header("3. Ask the models")
with st.form("lab"):
    st.markdown("**Scenario lab** — every control is a parameter the engine validates; the book is re-solved when you press the button.")
    c1, c2 = st.columns(2)
    wti = c1.number_input("WTI held at ($/bbl, 0 = no change)", 0.0, wi.LIMITS["wti_level"][1], 0.0, 5.0)
    years = c1.number_input("for years", 1, 20, 5)
    hh = c1.slider("Henry Hub ×", *wi.LIMITS["hh_multiplier"], 1.0, 0.05)
    vol = c1.slider("ERCOT volatility ×", *wi.LIMITS["ercot_volatility"], 1.0, 0.05)
    budget = c2.slider("Budget ×", *wi.LIMITS["budget_multiplier"], 1.0, 0.05)
    lease_cost = c2.slider("Lease capital ×", *wi.LIMITS["lease_cost_multiplier"], 1.0, 0.05)
    lam = c2.slider("λ (penalty on the worst-5% loss)", 0.0, 8.0, 1.0, 0.25)
    limit = c2.number_input("Hard limit on the worst-5% loss ($ million, 0 = none)", 0.0, 1e5, 0.0, 50.0)
    run = st.form_submit_button("Re-solve")
if run:
    try:
        what = wi.WhatIf(wti_level=wti or None, wti_years=int(years), hh_multiplier=hh, ercot_volatility=vol, budget_multiplier=budget,
                         lease_cost_multiplier=lease_cost, lam=lam, cvar_limit_musd=limit or None).validate()
        res = engine().run(what)
        if not res["feasible"]:
            st.error(f"No book meets these limits: {res['reason']}")
        else:
            d = res["diff"]
            c = st.columns(3)
            c[0].metric("Expected NPV", money(d["new"]["expected_npv"]), money(d["change"]["expected_npv"]))
            c[1].metric("Worst-5% loss", money(d["new"]["cvar_loss"]), money(d["change"]["cvar_loss"]), delta_color="inverse")
            c[2].metric("Chance of a loss", f"{d['new']['p_loss']:.0%}")
            st.markdown("Entered: " + (", ".join(d["entered"]) or "none") + ". Left: " + (", ".join(d["left"]) or "none") + ".")
            st.dataframe(res["candidates"][["project_id", "technology", "in_book", "expected_npv_$M", "p_negative", "status"]].round(2), hide_index=True)
            st.caption(f"{res['n_scenarios']:,} scenarios; {res['provenance']}.")
    except wi.WhatIfError as err:
        st.error(f"The engine cannot answer that: {err}")
question = st.text_input("Or ask in words (the advisor turns it into parameters, or says it cannot)")
if question:
    advisor = adv.Advisor(mode="auto")
    out = at.ask_whatif(advisor, engine(), question, adv.load_prompt("advisor_system"), tag="decide-page")
    if out["status"] == "answered":
        st.markdown(out["explanation"])
        v = out["verification"]
        st.caption(f"Read as {json.dumps(out['whatif'].changes())}. Numbers checked against the computed result: {v['n_grounded']} of {v['n_numbers']}"
                   + (f"; not found: {', '.join(v['ungrounded'] + v['unit_errors'])}" if v["ungrounded"] or v["unit_errors"] else "") + ".")
    elif out["status"] in ("cannot answer", "refused by the engine"):
        st.warning(f"No answer: {out['reading']}")
    else:
        st.warning("No advisor is reachable and this question has no recorded answer.")
with st.expander("Why each candidate is in or out of book D"):
    e = T["explanations"]
    st.dataframe(e[["project_id", "in_book", "status", "objective_cost_$M", "expected_npv_$M", "p_negative"]].round(1), hide_index=True)
    st.caption("Opportunity cost: how much the best book's E[NPV] − λ·CVaR falls when the candidate is forced the other way. A model-supported reason, not a causal one.")

# --- step 4: the decision ----------------------------------------------------------------------------
st.header("4. Decide")
verb = st.selectbox("Decision", ledger.VERBS)
who = st.text_input("Authorized by (your name)")
override = set(my_members) != set(model_members)
answers, read = {}, False
if override:
    st.markdown(f"Your book departs from the frontier's pick at w = {w:g}. That is an override: answer the five questions and read the opposing case.")
    other = front.set_index("policy").loc[picked["policy"]]
    st.markdown(f"**The opposing case.** {picked['policy']} expects {money(other['mean'])} with a worst-5% loss of {money(other['cvar_loss'])}; "
                f"yours expects {money(front.set_index('policy').loc[mine, 'mean'])} with {money(front.set_index('policy').loc[mine, 'cvar_loss'])}.")
    for key, q in adv.REASONING_QUESTIONS.items():
        answers[key] = st.text_area(q, key=f"gate_{key}")
    read = st.checkbox("I have read the opposing case")
if st.button("Record the decision"):
    try:
        row = ledger.record(ledger.Decision(verb=verb, members=my_members, authorized_by=who, model_members=model_members, whatif={"tail_weight_w": w},
                                            gate_answers=answers, opposing_case_read=read, note=f"{reasons} | flips if: {flip}"), ledger.LEDGER_V8)
        st.success(f"Recorded at {row['time']} ({'override' if row['override'] else 'follows the model'}).")
    except (ledger.NotAuthorized, ValueError) as err:
        st.error(str(err))
if ledger.LEDGER_V8.exists():
    rows = [json.loads(line) for line in ledger.LEDGER_V8.read_text(encoding="utf-8").splitlines() if line.strip()]
    st.dataframe(pd.DataFrame(rows)[["time", "verb", "authorized_by", "override", "note"]], hide_index=True)
    st.caption("Ledger chain intact." if ledger.verify_chain(ledger.LEDGER_V8) else "The ledger chain is broken: a row was edited.")
