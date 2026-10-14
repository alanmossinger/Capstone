"""The challenge round, as one page: see the alternatives and the advisor's pick, choose, answer its five questions, read its verdict, decide.

What: a Streamlit page (``make challenge``) in four steps and nothing
else. Step 1 — the alternatives: the six books of notebook 09 with their
capital, expected NPV, worst-5% tail and chance of a loss, and the
advisor's own pick for the base case with its reasons and the figure at
which its answer would flip. Step 2 — the decision-maker picks a book,
states why in their own words, and writes down what would change their
mind before the advisor speaks. Step 3 — the advisor asks five questions
tied to the statement, one per item of the override gate, and the
decision-maker answers them. Step 4 — the advisor's verdict on the
reasoning, its case for the other book, the convergence line, its final
pick beside the human's flip condition, and the decision to the ledger.
Why: the "reason my thinking" round is the human-in-the-loop instrument
of the report (decision #79). Alan asked for a simpler page than the
portfolio dashboard, one that explains the alternatives first, lets the
AI decide and help to decide, and makes the human think (14 Oct 2026).
Reads: ``results/portfolio_scores.csv``, ``portfolio_allocation.csv``,
``advisor_recommendations.csv``; the result tables through
``src.advisor.portfolio_context``; ``prompts/``; ``results/advisor_runs.jsonl`` (replay).
Writes: ``results/advisor_transcripts/challenge_<tag>.md``,
``results/decision_ledger.csv`` (append), ``results/advisor_runs.jsonl``
(live calls only).
Used by: ``streamlit run app/challenge.py``; ``tests/test_challenge_app.py``.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv, paths  # noqa: E402

st.set_page_config(page_title="Reason my thinking", layout="centered")

LABELS = {  # the six books of notebook 09, in plain words
    "A top-N NPV": "A — rank by expected NPV until the budget is spent",
    "B equal capital": "B — split the budget equally by sector",
    "C deterministic MILP": "C — maximise expected NPV under the budget and the cap",
    "D risk-aware MILP": "D — maximise expected NPV minus the worst-5% loss (risk-aware)",
    "leases only (D rule)": "Leases only — the twenty redevelopments, no power request",
    "power only (D rule)": "Power only — the requests that pay, no lease",
}
DESCRIPTIONS = {  # what the advisor is told the book is, when asked to argue for it
    "A top-N NPV": "Book A (top-N expected NPV): the candidates with the highest expected NPV until the budget is spent, within the 40% technology cap.",
    "B equal capital": "Book B (equal capital): the budget split equally between the lease and the power sectors, each sector ranked by expected NPV.",
    "C deterministic MILP": "Book C (deterministic MILP): the set that maximises expected NPV within the budget and the 40% technology cap.",
    "D risk-aware MILP": adv.OPPOSING_BOOK_D,
    "leases only (D rule)": "The twenty lease redevelopments and no power request.",
    "power only (D rule)": "The power requests the risk-aware rule keeps when no lease may be held, and no lease.",
}


@st.cache_resource
def advisor():
    return adv.Advisor(mode="auto")


@st.cache_data
def context():
    return adv.portfolio_context("base")


@st.cache_data
def alternatives():
    """The six books on the held-out scenarios, with capital by technology, and the advisor's recorded base-case pick."""
    scores = pd.read_csv(paths.RESULTS / "portfolio_scores.csv")
    scores = scores[scores["scenarios"].str.startswith("held-out") & (scores["revenue_case"] == "contracted")].set_index("book")
    alloc = pd.read_csv(paths.RESULTS / "portfolio_allocation.csv").set_index("book")
    table = pd.DataFrame({
        "Book": [LABELS[b] for b in scores.index],
        "Members": scores["n_selected"].astype(int).to_numpy(),
        "Capital, $B": (alloc.loc[scores.index, "capex_total"] / 1e9).round(2).to_numpy(),
        "Expected NPV, $B": (scores["expected_npv"] / 1e9).round(1).to_numpy(),
        "Worst-5% average, $B": (-scores["cvar_loss"] / 1e9).round(1).to_numpy(),  # positive = still a profit
        "Chance of a loss": (100 * scores["p_negative"]).round(0).astype(int).astype(str).to_numpy() + "%",
        "Gas, $B": (alloc.loc[scores.index, "Gas CC"] / 1e9).round(2).to_numpy(),
        "Wind, $B": (alloc.loc[scores.index, "Wind"] / 1e9).round(2).to_numpy(),
    }, index=scores.index)
    rec = pd.read_csv(paths.RESULTS / "advisor_recommendations.csv")
    base = rec[rec["scenario"] == "base"].iloc[0].to_dict() if (rec["scenario"] == "base").any() else {}
    return table, base


def step(n, title):
    st.markdown(f"### {n}. {title}")


st.title("Reason my thinking")
st.caption("The advisor reads only the result tables. It states its pick and why, asks before it judges, argues the book you did not choose, and can be overruled only after your answers are on record.")
a = advisor()
if not a.live:
    st.warning("No live backend (no API key and the claude command is not signed in): recorded exchanges replay, a new statement gets no answer.")
table, pick = alternatives()

# --- step 1: the alternatives and the advisor's pick --------------------------------------------
step(1, "The alternatives, and the advisor's pick")
st.markdown("Six books compete for one budget — 40% of the forty candidates' capital, no technology above 40% of it — scored on 2,000 held-out scenarios. The worst-5% column is the average of the worst 5% of outcomes: a positive number is still a profit.")
st.dataframe(table.set_index("Book"), use_container_width=True)
if pick:
    st.markdown(f"**The advisor's pick for the base case: {LABELS.get(pick.get('book'), pick.get('book'))}.**")
    st.markdown(f"_Why:_ {pick.get('why', '')}")
    st.markdown(f"_What would change its answer:_ {pick.get('what_would_change_the_answer', '')}")
    st.caption(f"Numbers it cited that its tables hold: {100 * float(pick.get('grounding_rate', 1)):.0f}%. Weakest provenance behind the pick: {pick.get('weakest_provenance', '')}.")
else:
    st.info("The advisor's base-case recommendation is not recorded yet (notebook 10 writes it).")

# --- step 2: the human's decision, and the flip condition ---------------------------------------
step(2, "Your decision — before the advisor speaks")
chosen = st.radio("The book you would fund", list(LABELS), format_func=LABELS.get, index=list(LABELS).index("D risk-aware MILP"), key="chosen")
reasons = st.text_area("Why — your reasons, in your own words", height=140, key="reasons",
                       placeholder="The leases already produce and every one is positive; the power requests ...")
flip = st.text_input("What would change your mind? Name the figure and the level at which you would switch books", key="flip",
                     placeholder="If the worst-5% loss of my book exceeded $1B under the committee grid, I would take book D.")
others = [b for b in LABELS if b != chosen]
default_opposing = pick.get("book") if pick and pick.get("book") in others else "A top-N NPV" if chosen != "A top-N NPV" else "D risk-aware MILP"
opposing = st.selectbox("The book the advisor will argue for against you", others, index=others.index(default_opposing), format_func=LABELS.get)
ready = bool(reasons.strip()) and bool(flip.strip())
if st.button("Ask me the five questions", type="primary", disabled=not ready):
    statement = f"I would fund {LABELS[chosen]}. {reasons.strip()} What would change my mind: {flip.strip()}"
    system = adv.load_prompt("advisor_system") + "\nDATA\n\n" + context()
    tag = datetime.now().strftime("app_%Y%m%d_%H%M")
    out = a.ask(system, adv.render("motivated_reasoning_questions", human_statement=statement), "challenge/questions", tag)
    st.session_state["round"] = {"tag": tag, "statement": statement, "chosen": chosen, "opposing": opposing, "flip": flip.strip(),
                                 "questions": out["response"] if out else None}
    st.session_state.pop("result", None)
if not ready:
    st.caption("Both boxes are needed: the reasons, and the figure that would change your mind.")

# --- step 3: the five questions ----------------------------------------------------------------
if "round" in st.session_state:
    rnd = st.session_state["round"]
    step(3, "Answer the advisor's five questions")
    if rnd["questions"] is None:
        st.error("The advisor could not answer (no backend and no record for this statement).")
    else:
        st.markdown(rnd["questions"])
        with st.form("answers"):
            answers = {key: st.text_area(f"Answer {n}", key=f"a{n}", height=90) for n, key in enumerate(adv.REASONING_QUESTIONS, start=1)}
            if st.form_submit_button("Judge my reasoning and argue the other book", type="primary"):
                allowed, missing = adv.override_allowed(answers)
                short = [k for k in missing if k != "opposing_case_read"]
                if short:
                    st.error(f"Every answer needs at least {adv.override_allowed.__defaults__[1]} characters; {len(short)} of five are shorter.")
                else:
                    with st.spinner("The advisor is reading your answers (about a minute for each of its two answers)"):
                        result = adv.challenge(a, rnd["statement"], DESCRIPTIONS[rnd["opposing"]], context(), answers=answers, tag=rnd["tag"])
                    st.session_state["result"] = result
                    st.session_state["given"] = answers

# --- step 4: the verdict, the opposing case, the advisor's final say, the decision -------------
if "result" in st.session_state:
    res, rnd, answers = st.session_state["result"], st.session_state["round"], st.session_state["given"]
    step(4, "The verdict, the other book, and the decision")
    tab_check, tab_opposing = st.tabs(["Motivated-reasoning check", "The case for " + LABELS[rnd["opposing"]].split(" — ")[0]])
    with tab_check:
        st.markdown(res["check"]["response"] if res["check"] else "_not recorded_")
    with tab_opposing:
        st.markdown(res["opposing"]["response"] if res["opposing"] else "_not recorded_")
    left, right = st.columns(2)
    with left:
        st.markdown("**You said would change your mind**")
        st.write(rnd["flip"])
    with right:
        st.markdown("**The advisor's final say**")
        st.write(f"Converge: {res['converge']}" if res["converge"] else "no convergence line")
        st.write(f"Still open: {res['disagree']}" if res["disagree"] else "")
    your, advisors = table.loc[rnd["chosen"]], (table.loc[pick["book"]] if pick and pick.get("book") in table.index else None)
    c1, c2 = st.columns(2)
    c1.metric(f"Your book — {LABELS[rnd['chosen']].split(' — ')[0]}", f"${your['Expected NPV, $B']}B expected", f"worst 5%: ${your['Worst-5% average, $B']}B, loss in {your['Chance of a loss']} of scenarios", delta_color="off")
    if advisors is not None:
        c2.metric(f"The advisor's — {LABELS[pick['book']].split(' — ')[0]}", f"${advisors['Expected NPV, $B']}B expected", f"worst 5%: ${advisors['Worst-5% average, $B']}B, loss in {advisors['Chance of a loss']} of scenarios", delta_color="off")
    grounded = [r["verification"]["rate"] for r in (res["check"], res["opposing"]) if r]
    if grounded:
        st.caption(f"Numbers the advisor wrote that its tables hold: {100 * sum(grounded) / len(grounded):.0f}% (the rest is its own arithmetic).")
    allowed, _ = adv.override_allowed(answers, opposing_case_read=res["opposing"] is not None)
    st.markdown("**Your decision.** " + ("The override gate is open: your five answers and the opposing case are on record." if allowed else "The gate is closed."))
    decision = st.radio("After the round, I", [f"keep my book (an override of the advisor)", "take the advisor's book", "want to think again"], index=2)
    if st.button("Record the decision in the ledger", disabled=not allowed):
        folder = paths.RESULTS / "advisor_transcripts"
        folder.mkdir(exist_ok=True)
        (folder / f"challenge_{rnd['tag']}.md").write_text(f"# Challenge round — {rnd['tag']} (the challenge page)\n\n" + res["transcript"], encoding="utf-8")
        adv.ledger_append({"entry_id": f"APP-{rnd['tag']}", "actor": "human", "mode": "challenge/app", "override": decision.startswith("keep"),
                           "members": rnd["chosen"], "reasoning_answered": " | ".join(f"{k}: {v}" for k, v in answers.items() if v.strip()),
                           "note": f"{decision}; flip condition: {rnd['flip']}; converge: {res['converge']}; disagree: {res['disagree']}"})
        st.success(f"Recorded: results/decision_ledger.csv (APP-{rnd['tag']}) and the transcript in results/advisor_transcripts/.")
