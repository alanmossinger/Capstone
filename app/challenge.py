"""The challenge round, as one page: state the book, answer the advisor's five questions, read its verdict and the opposing case.

What: a Streamlit page (``make challenge``) with three steps and nothing
else. Step 1 — the decision-maker states the book they prefer and why,
in their own words, and picks the alternative the advisor must argue for.
Step 2 — the advisor asks five questions tied to the statement, one per
item of the override gate, and the decision-maker answers them. Step 3 —
the advisor's verdict on the reasoning and its case for the other book,
with the convergence line; the override gate opens because the answers
are on record, and the decision goes to the ledger.
Why: the "reason my thinking" round is the human-in-the-loop instrument
of the report (decision #79); the portfolio dashboard carries it among
many other panels, and Alan asked for a simpler one (14 Oct 2026).
Reads: ``results/*.csv`` through ``src.advisor.portfolio_context``;
``prompts/``; ``results/advisor_runs.jsonl`` (replay).
Writes: ``results/advisor_transcripts/challenge_<tag>.md``,
``results/decision_ledger.csv`` (append), ``results/advisor_runs.jsonl``
(live calls only).
Used by: ``streamlit run app/challenge.py``; ``tests/test_challenge_app.py``.
"""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv, paths  # noqa: E402

st.set_page_config(page_title="Reason my thinking", layout="centered")

BOOKS = {  # the alternatives the advisor can be asked to argue for
    "Book D, the risk-aware book": adv.OPPOSING_BOOK_D,
    "Book A, the twenty leases and the requests with the highest expected NPV": "Book A (top-N expected NPV): the candidates with the highest expected NPV until the budget is spent, within the 40% technology cap.",
    "The twenty leases only": "The twenty lease redevelopments and no power request.",
    "The contracted wind requests only": "The wind requests under 15-year contracts and no lease.",
    "Fund nothing this year": "Fund nothing this year: hold the budget and review in twelve months.",
}


@st.cache_resource
def advisor():
    return adv.Advisor(mode="auto")


@st.cache_data
def context():
    return adv.portfolio_context("base")


def step(n, title):
    st.markdown(f"### {n}. {title}")


st.title("Reason my thinking")
st.caption("The advisor reads only the result tables. It asks before it judges, argues the other book, and can be overruled only after your answers are on record.")
a = advisor()
if not a.live:
    st.warning("No live backend (no API key and the claude command is not signed in): recorded exchanges replay, a new statement gets no answer.")

# --- step 1: the statement ----------------------------------------------------------------------
step(1, "State the book you prefer, and why")
statement = st.text_area("Your decision and your reasons, in your own words", height=160, key="statement",
                         placeholder="I want the twenty leases and nothing else. The leases earn ... ; the power requests ...")
opposing_name = st.selectbox("The alternative the advisor must argue for", list(BOOKS))
if st.button("Ask me the five questions", type="primary", disabled=not statement.strip()):
    system = adv.load_prompt("advisor_system") + "\nDATA\n\n" + context()
    tag = datetime.now().strftime("app_%Y%m%d_%H%M")
    out = a.ask(system, adv.render("motivated_reasoning_questions", human_statement=statement), "challenge/questions", tag)
    st.session_state["round"] = {"tag": tag, "statement": statement, "opposing": BOOKS[opposing_name], "questions": out["response"] if out else None}
    st.session_state.pop("result", None)

# --- step 2: the five questions ----------------------------------------------------------------
if "round" in st.session_state:
    rnd = st.session_state["round"]
    step(2, "Answer the advisor's five questions")
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
                    with st.spinner("The advisor is reading your answers"):
                        result = adv.challenge(a, rnd["statement"], rnd["opposing"], context(), answers=answers, tag=rnd["tag"])
                    st.session_state["result"] = result
                    st.session_state["given"] = answers

# --- step 3: the verdict, the opposing case, the gate ------------------------------------------
if "result" in st.session_state:
    res, rnd, answers = st.session_state["result"], st.session_state["round"], st.session_state["given"]
    step(3, "The verdict, and the case for the other book")
    tab_check, tab_opposing = st.tabs(["Motivated-reasoning check", "The opposing case"])
    with tab_check:
        st.markdown(res["check"]["response"] if res["check"] else "_not recorded_")
    with tab_opposing:
        st.markdown(res["opposing"]["response"] if res["opposing"] else "_not recorded_")
    if res["converge"]:
        st.info(f"**Converge:** {res['converge']}  \n**Still open:** {res['disagree']}")
    grounded = [r["verification"]["rate"] for r in (res["check"], res["opposing"]) if r]
    if grounded:
        st.caption(f"Numbers the advisor wrote that its tables hold: {100 * sum(grounded) / len(grounded):.0f}% (the rest is its own arithmetic).")
    allowed, _ = adv.override_allowed(answers, opposing_case_read=res["opposing"] is not None)
    st.markdown("### Your decision")
    st.caption("The override gate is open: your five answers and the opposing case are on record." if allowed else "The gate is closed.")
    decision = st.radio("After the round, I", ["keep my book (an override of the advisor)", "take the advisor's book", "want to think again"], index=2)
    if st.button("Record the decision in the ledger", disabled=not allowed):
        folder = paths.RESULTS / "advisor_transcripts"
        folder.mkdir(exist_ok=True)
        (folder / f"challenge_{rnd['tag']}.md").write_text(f"# Challenge round — {rnd['tag']} (the challenge page)\n\n" + res["transcript"], encoding="utf-8")
        adv.ledger_append({"entry_id": f"APP-{rnd['tag']}", "actor": "human", "mode": "challenge/app", "override": decision.startswith("keep"),
                           "reasoning_answered": " | ".join(f"{k}: {v}" for k, v in answers.items() if v.strip()),
                           "note": f"{decision}; converge: {res['converge']}; disagree: {res['disagree']}"})
        st.success(f"Recorded: results/decision_ledger.csv (APP-{rnd['tag']}) and the transcript in results/advisor_transcripts/.")
