"""A worked example: one executive's round through the decision page, read-only, for a new executive to read before their own.

What: the third page of the dashboard. It shows the round recorded by
notebook 13 section 7 (``src.worked_example``, ``results/v2/worked_example.json``)
in the four steps of the decision page: the executive's pick and reasons;
the advisor's reading, memo and solution; the executive's five answers,
the gate and the decision; the first pick, the decision and the advisor's
solution scored on the executive's own rules, with what accepting the
solution in full would have given. A button loads the same pick and
reasons into *Decide* so the reader can run the round themselves.
Why: a new executive understands the page from one complete round better
than from its instructions (Alan, 28 Oct 2026, decision #120).
Reads: ``results/v2/worked_example.json``, ``results/v2/book_D_members.csv`` (labels).
Writes: nothing.
Used by: ``app/app.py``; ``tests/test_app.py``.
"""

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv, challenge as ch, worked_example as we  # noqa: E402

LEVEL_TEXT = {"explain": "explain — nothing material is wrong with the book",
              "challenge": "challenge — a material weakness, but no computed alternative is clearly better on the executive's own terms",
              "guide": "guide — an alternative keeps every rule and is clearly better on the executive's own terms, so the advisor recommends it"}


def money(x, unit="B", digits=2):
    v = x / (1e9 if unit == "B" else 1e6)
    return ("−" if v < 0 else "") + f"${abs(v):,.{digits}f}{unit}"


def signed(x):
    return ("+" if x >= 0 else "−") + f"${abs(x) / 1e6:,.0f}M"


def md(text):
    """Escape dollar signs: Streamlit reads a pair of them in one string as a formula."""
    return text.replace("$", r"\$")


def show_scores(col, title, sc, n):
    col.markdown(f"**{title}** · {n} members")
    col.metric("Expected NPV", money(sc["mean"]))
    col.metric("Worst-5% average loss", money(sc["cvar"]))
    col.metric("Chance of a loss", f"{sc['p_loss']:.0%}")
    col.metric("Score on the executive's rules", money(sc["metric"]))


st.title("A worked example: one executive through the decision page")
st.markdown("""<div class="howto"><b>What this page shows.</b> One complete round, as recorded: an executive who wants the leases and nothing
else picks a book and says why; the advisor reads the reasons into rules, scores the book and computes the alternatives, and writes its
memo; the executive answers the five reasoning questions and decides; the result is scored beside what the advisor's solution would have
given. The words are the author's; every number is the tools'. Read it top to bottom, then run your own round on <b>Decide</b>.</div>""",
            unsafe_allow_html=True)

if not we.PATH.exists():
    st.info("The example has not been recorded yet: run notebook 13, section 7 (`make corrections`) with a backend for the advisor — "
            "`ANTHROPIC_API_KEY` in `.env` or the `claude` command signed in — and it appears here.")
    st.stop()
ex = we.load()
LABEL = we.labels()
prefs = ch.Preferences(**ex["preferences"])
names = lambda ms: ", ".join(LABEL.get(m, m) for m in ms) or "none"  # noqa: E731

# --- 1 the pick ---------------------------------------------------------------------------------------
st.header("1 · The executive's book and reasons")
left, right = st.columns([1, 1.2])
with left:
    st.markdown(md(f"**{len(ex['first_pick'])} members, {money(ex['first_pick_charge'])} of the {money(ex['budget'])} budget.**"))
    st.markdown(names(ex["first_pick"]))
    if ex["rules_broken"]["first_pick"]:
        st.markdown("**Rules this book breaks:** " + "; ".join(ex["rules_broken"]["first_pick"]) + ".")
with right:
    st.markdown(f'<div class="quote"><b>The executive says:</b> “{ex["statement"]}”</div>', unsafe_allow_html=True)

# --- 2 the challenge ----------------------------------------------------------------------------------
st.header("2 · The advisor's challenge")
st.markdown(f"**How the advisor read the reasons:** {ex['reading']}")
st.markdown(md(f"**The rules, as it read them:** {we.rules_text(prefs)}."))
if ex["not_representable"]:
    st.markdown(f"**What it cannot represent:** {ex['not_representable']}")
if ex["status"] == "challenged":
    st.markdown(f"**Level: {LEVEL_TEXT[ex['level']]}.**" + ("" if ex["level"] == ex["level_requested"] else
                " *(The model asked to guide; the evidence does not support that book, so the level was set to challenge.)*"))
    st.markdown("**Where the thinking is weak, in the advisor's words:**")
    for v in ex["vulnerabilities"]:
        st.markdown(md(f"- **{v.get('type', 'other')}** · *{v.get('kind', '')}* — {v.get('claim', '')}  (facts {', '.join(v.get('facts', [])) or 'none named'})"))
    st.markdown(md(f"**Why:** {ex['why']}"))
    st.markdown(md(f"**Loss avoided:** {ex['loss_avoided']}  ·  **What would change it:** {ex['what_would_change_it']}"))
    st.markdown(f"**Its question for the executive:** {ex['question_for_the_committee']}")
    ver = ex["verification"]
    st.caption(f"Checked by code: {ver['n_grounded']} of {ver['n_numbers']} numbers in the memo are on the fact sheet"
               + (f"; flagged: {', '.join(u.rstrip(',') for u in ver['ungrounded'])}" if ver["ungrounded"] else "") + ".")
else:
    st.markdown(f"**Level: {LEVEL_TEXT[ex['level']]}.**")
    st.markdown("**This round was recorded with the tools alone** — no language model read the words, so the registered default rules apply and the "
                "checklist (the tools' own reading, the registered *tools only* arm) stands in for the memo. **What it flags:**")
    for flag in ex["checklist_flags"]:
        st.markdown(f"- {flag}")
ch_ = ex["solution_changes"]
st.markdown(md(f"**The advisor's solution: {ex['solution_text']}** — {ch_['changes']} change(s): adds {names(ch_['added'])}; drops {names(ch_['dropped'])}."))
with st.expander("The fact sheet the advisor worked from (every number it may cite)"):
    st.text(ex["sheet"])

# --- 3 the answers and the decision -------------------------------------------------------------------
st.header("3 · The executive reasons, then decides")
for k, q in adv.REASONING_QUESTIONS.items():
    st.markdown(f'<div class="quote" style="border-color:#009E73"><b>{q}</b><br>{ex["answers"][k]}</div>', unsafe_allow_html=True)  # HTML: no escaping, a lone $ is safe
st.markdown(md(f"**The decision: {ex['decision_text']}** — {len(ex['decision_members'])} members: {names(ex['decision_members'])}."))
if ex["accepted_in_full"]:
    st.markdown("The decision is the advisor's solution in full; no override was needed.")
else:
    st.markdown("The decision departs from the advisor's solution, so the override gate applied: " + ("the five answers were given and the gate passed." if ex["gate_allowed"] else "the gate refused it (answers missing: " + ", ".join(ex["gate_missing"]) + ")."))

# --- 4 the result -------------------------------------------------------------------------------------
st.header("4 · The result against the advisor's")
sc = ex["scores"]
first, dec = sc["first_pick"], sc["decision"]
summary = (f"**In one paragraph.** The executive's first pick — {len(ex['first_pick'])} leases, {money(ex['first_pick_charge'])} of the budget — "
           + ("broke " + "; ".join(ex["rules_broken"]["first_pick"]) + " and " if ex["rules_broken"]["first_pick"] else "kept every rule and ")
           + f"scored {money(first['metric'])} on the executive's own rules: {money(first['mean'])} expected, {money(first['cvar'])} average loss in the worst 5% of scenarios, "
           f"a {first['p_loss']:.0%} chance of a loss. After the challenge the executive decided on {ex['decision_text'].split(':')[0]} — {len(ex['decision_members'])} members, "
           + ("every rule kept" if not ex["rules_broken"]["decision"] else "still breaking " + "; ".join(ex["rules_broken"]["decision"]))
           + f" — which scores {money(dec['metric'])}: {money(dec['mean'])} expected, {money(dec['cvar'])} in the worst 5%, a {dec['p_loss']:.0%} chance of a loss. "
           + (f"The tail fell by {money(first['cvar'] - dec['cvar'])} and the expected value by {money(first['mean'] - dec['mean'])}: that is the price of 'the leases and nothing else' inside the rules. "
              if dec["cvar"] < first["cvar"] and dec["mean"] < first["mean"] else "")
           + (f"The best book the rules allow would have scored {money(sc['optimizer']['metric'])}, {signed(ex['optimizer_vs_decision']['metric_diff'])} more." if ex.get("optimizer_vs_decision") else ""))
st.markdown(md(summary))
extra = "optimizer" in sc and ex["optimizer_members"] != ex["solution_members"]
cols = st.columns(4 if extra else 3)
show_scores(cols[0], "The first pick", sc["first_pick"], len(ex["first_pick"]))
show_scores(cols[1], "The decision", sc["decision"], len(ex["decision_members"]))
show_scores(cols[2], "The advisor's solution", sc["solution"], len(ex["solution_members"]))
if extra:
    show_scores(cols[3], "The best book the rules allow", sc["optimizer"], len(ex["optimizer_members"]))
if ex["accepted_in_full"]:
    st.success("The executive accepted the advisor's solution in full: its result on the executive's rules is the executive's.")
else:
    cmp = ex["solution_vs_decision"]
    more = cmp["metric_diff"] >= 0
    st.warning(md(f"Had the executive accepted the advisor's solution in full, the book would score {money(sc['solution']['metric'])} on the executive's rules: "
                  f"{signed(cmp['metric_diff'])} [{signed(cmp['metric_low'])}, {signed(cmp['metric_high'])}] {'more' if more else 'less'} than the decision, "
                  f"an interval {'clear of zero' if cmp['clear_of_zero'] or cmp['metric_high'] < 0 else 'not clear of zero'}; expected NPV {signed(cmp['mean_diff'])}."))
if extra and ex["optimizer_vs_decision"]:
    o = ex["optimizer_vs_decision"]
    st.markdown(md(f"**The best book the rules allow** — the optimizer's book under the executive's own rules ({len(ex['optimizer_members'])} members: {names(ex['optimizer_members'])}) — "
                   f"would score {money(sc['optimizer']['metric'])}: {signed(o['metric_diff'])} [{signed(o['metric_low'])}, {signed(o['metric_high'])}] against the decision. "
                   "The tools do not push the executive there: the guide rule allows only the smallest change that keeps every rule, and the rest is the executive's call."))
rows = [("The first pick", sc["first_pick"]), ("The decision", sc["decision"]), ("The advisor's solution", sc["solution"])] + ([("The best book the rules allow", sc["optimizer"])] if extra else [])
long = pd.DataFrame([{"book": n, "measure": m, "value": v[k] / 1e9} for n, v in rows for m, k in (("expected NPV", "mean"), ("worst-5% average loss", "cvar"))])
st.altair_chart(alt.Chart(long).mark_bar().encode(
    x=alt.X("value:Q", title="$ billion", axis=alt.Axis(format="$.2f")), y=alt.Y("measure:N", title=None), yOffset=alt.YOffset("book:N", sort=[r[0] for r in rows]),
    color=alt.Color("book:N", sort=[r[0] for r in rows], scale=alt.Scale(range=["#999999", "#0072B2", "#009E73", "#E69F00"]), legend=alt.Legend(title=None, orient="bottom")),
    tooltip=["book", "measure", alt.Tooltip("value:Q", format="$,.3f", title="$B")]).properties(height=160), width="stretch")
st.caption(md(f"Scored on 2,000 held-out scenarios under the executive's rules as the advisor read them ({we.rules_text(prefs)}); "
              + ("every construction call funded. " if prefs.liquidity_line_musd is None else "financed within the line stated, net of its fee and interest. ")
              + "Model-based results on public data and assumed lease costs, not realized returns."))


def load_into_decide():
    st.session_state["start"] = "an empty book"
    st.session_state["members"] = list(ex["first_pick"])
    st.session_state["statement"] = ex["statement"]
    for k in ("round", "decision", "final_members"):
        st.session_state.pop(k, None)


if st.button("Run this round yourself on Decide", key="try", type="primary", on_click=load_into_decide):
    st.switch_page("decide.py")
