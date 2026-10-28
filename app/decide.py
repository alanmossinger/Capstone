"""The decision page: the options, your book and your reasons, the advisor's challenge, then your result against the advisor's.

What: one page in four steps, each opening after the one before. (1) The
options: the budget, the four books of the report and the forty candidates.
(2) Your book: a starting book, the members you keep or add, and your
reasons in your own words. (3) The advisor's challenge: the registered
challenger of notebook 12 (``src.challenge``) reads your reasons into rules,
tools score the book on the 2,000 held-out scenarios and compute the repair
and the optimizer's book under those rules, and the language model writes
its memo — the weaknesses it finds, its level, the book it recommends and
its question for you. You answer its five reasoning questions and decide:
keep your book, take the advisor's solution in full, or change some members
(a departure from its solution needs the five answers: the registered
override gate). (4) The result: your decision and the advisor's solution
scored side by side on your own rules, with the paired difference and its
interval — what you would have had, had you accepted the advisor's solution
in full.
Why: Alan asked for a simple dashboard that shows the options, lets the
investor pick a book, has the advisor challenge the investor's thinking so
it may or may not change their mind, and then shows the investor's result
against the advisor's (28 Oct 2026, decision #119).
Reads: ``results/v2/book_D_members.csv``, ``results/v8/frontier.csv``,
``results/v10/cases_v10.json`` (the registered example X25); the challenger's
setting, built once from the engines of ``src.whatif`` and kept in
``data/interim/challenge_setting.pkl``; ``prompts/``;
``results/advisor_runs.jsonl`` (the record, replayed).
Writes: ``results/advisor_runs.jsonl`` on a live call only, as every call of
the advisor is written down. Nothing else.
Used by: ``app/app.py`` (``make app``); ``tests/test_app.py``.
"""

import json
import pickle
import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv, challenge as ch, config, paths, whatif as wi, worked_example as we  # noqa: E402

V2, V8, V10 = paths.RESULTS / "v2", paths.RESULTS / "v8", paths.RESULTS / "v10"
SETTING = paths.DATA_INTERIM / "challenge_setting.pkl"
BOOK_NAME = {"A NPV ranking": "A — ranking by NPV", "B equal capital by sector": "B — equal capital by sector",
             "C deterministic MILP": "C — the deterministic optimizer", "D risk-aware MILP": "D — the risk-aware book, the report's recommendation"}
LEVEL_TEXT = {"explain": "explain — nothing material is wrong with your book",
              "challenge": "challenge — a material weakness, but no computed alternative is clearly better on your own terms",
              "guide": "guide — an alternative keeps every rule and is clearly better on your own terms, so the advisor recommends it"}
SOLUTION = {"proposal": "your book as it is", "repair": "the repair — the fewest changes to your book that keep your rules", "optimizer": "the optimizer's book under your rules"}
CHOICES = ("Keep my book", "Take the advisor's solution in full", "Change some members")


@st.cache_data
def load():
    cand = pd.read_csv(V2 / "book_D_members.csv")
    fr = pd.read_csv(V8 / "frontier.csv")
    books = fr[fr["kind"] == "comparator"].set_index("policy")
    example = {c["id"]: c for c in json.loads((V10 / "cases_v10.json").read_text(encoding="utf-8"))["cases"]}["X25"]
    return cand, books, example


@st.cache_resource(show_spinner=False)
def setting():
    """The challenger's setting — the two scenario engines and the base matrices — built once (about two minutes) and kept on disk until notebook 11 runs again."""
    if SETTING.exists() and SETTING.stat().st_mtime >= (V8 / "frontier.csv").stat().st_mtime:
        s = pickle.loads(SETTING.read_bytes())
    else:
        s = ch.Setting(wi.Engine(2000, "primary"), wi.Engine(2000, "held-out"), "committee")
        SETTING.parent.mkdir(parents=True, exist_ok=True)
        SETTING.write_bytes(pickle.dumps(s))
    s.fee, s.rate = config.LINE_FEE, config.LINE_RATE  # a construction line you state is priced as in the registered run
    return s


def money(x, unit="B", digits=2):
    v = x / (1e9 if unit == "B" else 1e6)
    return ("−" if v < 0 else "") + f"${abs(v):,.{digits}f}{unit}"


def signed(x):
    return ("+" if x >= 0 else "−") + f"${abs(x) / 1e6:,.0f}M"


def md(text):
    """Escape dollar signs: Streamlit reads a pair of them in one string as a formula."""
    return text.replace("$", r"\$")


def scored(s, x, prefs):
    return ch.scores_of(ch.totals(s, x, prefs), prefs.lam)


def show_scores(col, title, sc):
    col.markdown(f"**{title}**")
    col.metric("Expected NPV", money(sc["mean"]))
    col.metric("Worst-5% average loss", money(sc["cvar"]))
    col.metric("Chance of a loss", f"{sc['p_loss']:.0%}")
    col.metric("Score on your rules", money(sc["metric"]))


# --- the page --------------------------------------------------------------------------------------

st.title("Decide: your book, the advisor's challenge, your result")
st.markdown("""<div class="howto"><b>What this page does.</b> You see the options, pick a book and say why. The advisor reads your reasons
into rules, scores your book on 2,000 held-out scenarios, computes the closest book that keeps your rules and the optimizer's book,
and challenges your thinking. You then decide — it may change your mind or not — and see what your decision gives against what the
advisor's solution would have given. Every number is computed by the report's own tools; the model only reads and argues. New here? Read <b>A worked example</b> in the sidebar first: one executive's round from pick to result.</div>""",
            unsafe_allow_html=True)

cand, books, example = load()
with st.spinner("building the challenger's setting — about two minutes the first time, then kept in data/interim/"):
    s = setting()
ids = s.ids
charge = pd.Series(s.charge, index=ids)
LABEL = we.labels()
D_MEMBERS = [ids[i] for i in np.where(np.asarray(s.x_model) == 1)[0]]
STARTS = {BOOK_NAME["D risk-aware MILP"]: D_MEMBERS, **{BOOK_NAME[p]: books.loc[p, "members"].split(";") for p in ("A NPV ranking", "B equal capital by sector", "C deterministic MILP")},
          "an empty book": []}

# --- 1 the options ---------------------------------------------------------------------------------
st.header("1 · The options")
c1, c2, c3 = st.columns(3)
c1.metric("One budget", money(s.budget), "1 January 2025, built from what was public that day", delta_color="off")
c2.metric("Forty candidates", "20 + 20", "Gulf of Mexico leases to redevelop; ERCOT interconnection requests", delta_color="off")
c3.metric("Scored on", "2,000 scenarios", "held out: the same the report scores on", delta_color="off")
st.markdown("**The four books of the report** — each a way of choosing under the same budget, scored before financing at the registered tail weight λ = 1.")
tbl = books.loc[list(BOOK_NAME)].reset_index()
tbl["book"] = tbl["policy"].map(BOOK_NAME)
st.dataframe(tbl[["book", "leases", "requests", "charge", "mean", "cvar_loss", "p_loss"]]
             .rename(columns={"charge": "capital charged now", "mean": "expected NPV", "cvar_loss": "worst-5% average loss", "p_loss": "chance of a loss"})
             .style.format({"capital charged now": lambda v: money(v), "expected NPV": lambda v: money(v), "worst-5% average loss": lambda v: money(v), "chance of a loss": "{:.0%}"}),
             hide_index=True, width="stretch")
st.markdown("**The forty candidates** — what each costs now, what it is expected to earn, how often it loses, and the report's verdict on it.")
show = cand[["project_id", "technology", "status", "charge_$M", "expected_npv_$M", "p_negative", "in_book"]].rename(columns={
    "project_id": "candidate", "status": "the report's verdict", "charge_$M": "capital charged now ($M)", "expected_npv_$M": "expected NPV ($M)",
    "p_negative": "chance of a loss", "in_book": "in the recommended book"})
show["candidate"] = show["candidate"].map(LABEL)
st.dataframe(show.style.format({"capital charged now ($M)": "{:,.0f}", "expected NPV ($M)": "{:,.0f}", "chance of a loss": "{:.0%}"}), hide_index=True, width="stretch", height=300)

# --- 2 your book -----------------------------------------------------------------------------------
st.header("2 · Your book and your reasons")
st.session_state.setdefault("start", BOOK_NAME["D risk-aware MILP"])
st.session_state.setdefault("members", D_MEMBERS)
st.session_state.setdefault("statement", "")
advisor_available = adv.api_key() is not None or adv.cli_path() is not None
st.session_state.setdefault("replay_only", not advisor_available)


def set_members():
    st.session_state["members"] = STARTS[st.session_state["start"]]


def use_example():
    st.session_state["start"] = BOOK_NAME["D risk-aware MILP"]
    st.session_state["members"] = D_MEMBERS
    st.session_state["statement"] = example["statement"]


left, right = st.columns([1, 1.2])
with left:
    st.selectbox("Start from", list(STARTS), key="start", on_change=set_members)
    chosen = st.multiselect("The members of your book", ids, key="members", format_func=LABEL.get)
    cost = float(charge.reindex(chosen).sum()) if chosen else 0.0
    over = cost > s.budget + 1
    st.markdown(md(f"Capital charged now: **{money(cost)}** of {money(s.budget)}" + (" — **over the budget**" if over else "")))
with right:
    st.text_area("Why this book? Say it as you would to the committee: your objective, any rule you hold (a limit on the chance of a loss, a sector you will not fund, "
                 "a construction line you can call), and what you believe about the market.", key="statement", height=150, placeholder="We should fund … because …")
    b1, b2 = st.columns([1, 1])
    b1.button("Challenge my thinking", key="challenge", type="primary", disabled=over or not chosen or not st.session_state["statement"].strip())
    b2.button("Use the registered example (case X25)", key="example", on_click=use_example, help="A sunk-cost argument for the recommended book, as recorded in the report; replays with no call.")
    st.checkbox("Recorded answers only — no call to the model", key="replay_only", disabled=not advisor_available)

advisor = adv.Advisor(mode="replay" if st.session_state["replay_only"] else "auto")
st.caption(f"Advisor: {advisor.model} — {'live' if advisor.live else 'recorded answers only'}; every call is written to results/advisor_runs.jsonl and checked against the fact sheet.")

if st.session_state.get("challenge"):
    members0 = [m for m in ids if m in set(chosen)]  # the setting's order, as the registered run passed it
    with st.spinner("the advisor reads your reasons, tools score your book and compute the alternatives, the advisor writes its memo — about a minute"):
        res = ch.challenge(advisor, s, st.session_state["statement"], members0, adv.load_prompt("advisor_system"), tag="dashboard")
    st.session_state["round"] = {"result": res, "members": members0, "statement": st.session_state["statement"]}
    st.session_state.pop("decision", None)

# --- 3 the advisor's challenge ---------------------------------------------------------------------
if "round" in st.session_state:
    rnd = st.session_state["round"]
    res, members0 = rnd["result"], rnd["members"]
    st.header("3 · The advisor's challenge")
    if set(members0) != set(chosen) or rnd["statement"] != st.session_state["statement"]:
        st.warning("Your book or your reasons changed since this challenge; run it again to challenge the new ones.")
    if res["status"] == "no record":
        st.error("No recorded answer for these words, and no live backend. Put a language-model key in .env (any provider: see the note at the top) and untick 'recorded answers only', or use the registered example.")
        st.stop()
    prefs = ch.Preferences(**res["preferences"])
    st.markdown(f"**How the advisor read your reasons:** {res['reading']}")
    st.markdown(md(f"**Your rules, as it read them:** {we.rules_text(prefs)}."))
    if res["not_representable"]:
        st.markdown(f"**What it cannot represent:** {res['not_representable']}")
    alts = res["alternatives"]
    if res["status"] == "challenged":
        memo = res["memo"]
        st.markdown(f"**Level: {LEVEL_TEXT[res['level']]}.**" + ("" if res["level"] == res["level_requested"] else
                    f" *(The model asked to guide; the evidence does not support that book, so the level was set to challenge.)*"))
        st.markdown("**Where your thinking is weak, in the advisor's words:**")
        for v in memo.get("vulnerabilities", []):
            st.markdown(md(f"- **{v.get('type', 'other')}** · *{v.get('kind', '')}* — {v.get('claim', '')}  (facts {', '.join(v.get('facts', [])) or 'none named'})"))
        st.markdown(md(f"**Why:** {memo.get('why', '')}"))
        st.markdown(md(f"**Loss avoided:** {memo.get('loss_avoided', 'none')}  ·  **What would change it:** {memo.get('what_would_change_it', '')}"))
        st.markdown(f"**Its question for you:** {memo.get('question_for_the_committee', '')}")
        ver = res["verification"]
        st.caption(f"Checked by code: {ver['n_grounded']} of {ver['n_numbers']} numbers in the memo are on the fact sheet" + (f"; flagged: {', '.join(u.rstrip(',') for u in ver['ungrounded'])}" if ver["ungrounded"] else "") + ".")
        rec = memo.get("recommended_book", "proposal")
    else:
        st.info("Your book was scored and the alternatives computed, but the model's memo could not be obtained (no record for these words and no live backend). The checklist below is the tools' own reading.")
        for flag in res["checklist"]["flags"]:
            st.markdown(f"- {flag}")
        rec = res["checklist"]["recommended_book"]
    rec = rec if rec in alts else "proposal"
    x_adv = alts[rec]["x"] if rec in alts else s.vector(members0)
    adv_ids = [ids[i] for i in np.where(np.asarray(x_adv) == 1)[0]]
    if rec == "proposal":
        st.markdown("**The advisor's solution: your book as it is.**")
    else:
        a = alts[rec]
        st.markdown(md(f"**The advisor's solution: {SOLUTION[rec]}** — {a['changes']} change(s): adds {', '.join(LABEL.get(m, m) for m in a['added']) or 'nothing'}; "
                       f"drops {', '.join(LABEL.get(m, m) for m in a['dropped']) or 'nothing'}."))
    with st.expander("The fact sheet the advisor worked from (every number it may cite)"):
        st.text(res["sheet"])

    st.subheader("Reason my thinking, then decide")
    st.markdown("The five questions of the motivated-reasoning check. Answer them in a sentence or two each; they are required only if you depart from the advisor's solution.")
    answers = {k: st.text_area(q, key=f"q_{k}", height=70) for k, q in adv.REASONING_QUESTIONS.items()}
    choice = st.radio("Your decision", CHOICES, key="choice", horizontal=True)
    if choice == CHOICES[2]:
        st.session_state.setdefault("final_members", members0)
        final = st.multiselect("The book you decide on", ids, key="final_members", format_func=LABEL.get)
    else:
        final = members0 if choice == CHOICES[0] else adv_ids
    final = [m for m in ids if m in set(final)]
    if st.button("Decide", key="decide", type="primary", disabled=not final):
        if set(final) != set(adv_ids):
            allowed, missing = adv.override_allowed(answers, opposing_case_read=True)
            if not allowed:
                st.error("You are departing from the advisor's solution: answer the five questions first (" + ", ".join(adv.REASONING_QUESTIONS[k] for k in missing) + ").")
            else:
                st.session_state["decision"] = {"final": final, "prefs": prefs, "x_adv": x_adv, "rec": rec}
        else:
            st.session_state["decision"] = {"final": final, "prefs": prefs, "x_adv": x_adv, "rec": rec}

# --- 4 your result against the advisor's ----------------------------------------------------------
if "decision" in st.session_state and "round" in st.session_state:
    d, members0 = st.session_state["decision"], st.session_state["round"]["members"]
    prefs, final, x_adv = d["prefs"], d["final"], d["x_adv"]
    st.header("4 · Your result against the advisor's")
    x_final = s.vector(final)
    sc_final, sc_adv = scored(s, x_final, prefs), scored(s, x_adv, prefs)
    accepted = set(final) == set(np.array(ids)[np.asarray(x_adv) == 1])
    changed = set(final) != set(members0)
    cols = st.columns(3 if changed else 2)
    show_scores(cols[0], "Your decision", sc_final)
    show_scores(cols[1], "The advisor's solution", sc_adv)
    if changed:
        show_scores(cols[2], "Your first pick", scored(s, s.vector(members0), prefs))
        added, dropped = [m for m in final if m not in members0], [m for m in members0 if m not in final]
        st.markdown(md(f"The challenge changed your mind on {len(added) + len(dropped)} member(s): added {', '.join(LABEL.get(m, m) for m in added) or 'none'}; "
                       f"dropped {', '.join(LABEL.get(m, m) for m in dropped) or 'none'}."))
    else:
        st.markdown("You kept your first pick.")
    if accepted:
        st.success("You accepted the advisor's solution in full: its result on your rules is yours.")
    else:
        cmp = ch.compare(s, x_adv, x_final, prefs)
        more = cmp["metric_diff"] >= 0
        st.warning(md(f"Had you accepted the advisor's solution in full, the book would score {money(sc_adv['metric'])} on your rules: "
                      f"{signed(cmp['metric_diff'])} [{signed(cmp['metric_low'])}, {signed(cmp['metric_high'])}] {'more' if more else 'less'} than your decision, "
                      f"an interval {'clear of zero' if cmp['clear_of_zero'] or cmp['metric_high'] < 0 else 'not clear of zero'}; expected NPV {signed(cmp['mean_diff'])}."))
    rows = [("Your decision", sc_final), ("The advisor's solution", sc_adv)] + ([("Your first pick", scored(s, s.vector(members0), prefs))] if changed else [])
    long = pd.DataFrame([{"book": n, "measure": m, "value": sc[k] / 1e9} for n, sc in rows for m, k in (("expected NPV", "mean"), ("worst-5% average loss", "cvar"))])
    st.altair_chart(alt.Chart(long).mark_bar().encode(
        x=alt.X("value:Q", title="$ billion", axis=alt.Axis(format="$.2f")), y=alt.Y("measure:N", title=None), yOffset=alt.YOffset("book:N", sort=[r[0] for r in rows]),
        color=alt.Color("book:N", sort=[r[0] for r in rows], scale=alt.Scale(range=["#0072B2", "#009E73", "#999999"]), legend=alt.Legend(title=None, orient="bottom")),
        tooltip=["book", "measure", alt.Tooltip("value:Q", format="$,.3f", title="$B")]).properties(height=160), width="stretch")
    st.caption(md(f"Scored on 2,000 held-out scenarios under your rules as the advisor read them ({we.rules_text(prefs)}); "
                  + ("every construction call funded. " if prefs.liquidity_line_musd is None else "financed within the line you stated, net of its fee and interest. ")
                  + "Model-based results on public data and assumed lease costs, not realized returns."))
