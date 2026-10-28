"""The report's decision on one screen: the second page of the dashboard, for presenting the recommendation.

What: a page of the dashboard (``app/app.py``, ``make app``) that opens with
what is being decided and how to read it, then seven tabs — the
recommendation, risk against return, financing, what can go wrong, the AI
challenger, the controls, and the committee's own call (how much the bad
years weigh, whether a construction facility can be arranged) — each a chart
or a table with one sentence under it. Every number is read from
``results/`` (the tables notebooks 11–13 wrote); nothing is recomputed, no
model is called, nothing is written, and the numbers are the report's.
Why: a committee meeting needs the decision, its price, its risk and its
controls in a form that can be shown in ten minutes (decision #118); the
page where the investor decides and is challenged is ``app/decide.py``
(decision #119).
Reads: ``results/v2/*.csv``, ``results/v8/frontier.csv``,
``results/v8/process_comparison.csv``, ``results/v10/*`` (the ladder, the
registered lines, case X25 and its recorded memo), ``figures/executive/``.
Writes: nothing.
Used by: ``app/app.py``; ``tests/test_app.py``.
"""

import json
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import paths  # noqa: E402

R, V2, V8, V10, FIG = paths.RESULTS, paths.RESULTS / "v2", paths.RESULTS / "v8", paths.RESULTS / "v10", paths.FIGURES / "executive"

INK, MUTED = "#222222", "#5F6368"
BOOK_COLOR = {"A": "#999999", "B": "#CC79A7", "C": "#56B4E9", "D": "#0072B2", "F": "#009E73"}
BOOK_NAME = {"A": "A  NPV ranking", "B": "B  equal capital by sector", "C": "C  deterministic optimizer", "D": "D  risk-aware optimizer (recommended)", "F": "F  risk-aware, lookup forecasts"}
TECH_COLOR = {"Lease redevelopment": "#D55E00", "Gas CC": "#555555", "Solar": "#E69F00", "Wind": "#56B4E9", "Storage": "#CC79A7"}
ARM_LABEL = {"proposal": "committee's own proposal", "tools": "tools only (checklist)", "optimizer_first": "optimizer-first rule (no LLM)", "tools_llm": "tools + language model", "optimizer": "optimizer under the true rules"}
ARM_COLOR = {"proposal": "#BBBBBB", "tools": "#555555", "optimizer_first": "#E69F00", "tools_llm": "#0072B2", "optimizer": "#009E73"}


# --- cached loads --------------------------------------------------------------------------------

@st.cache_data
def load():
    t = {name: pd.read_csv(V2 / f"{name}.csv") for name in ("books_financed", "books_financed_pairs", "books_worlds", "dependence_dial", "ladder_five_arms", "ladder_five_rungs", "book_D_members", "readiness_matrix")}
    t["frontier"] = pd.read_csv(V8 / "frontier.csv")
    t["numbers"] = pd.read_csv(R / "report_numbers.csv", dtype=str).set_index("key")["text"]
    t["lines"] = pd.read_csv(V10 / "success_criteria_v10_scored.csv")
    records = {json.loads(line)["id"]: json.loads(line) for line in (V10 / "x1_outputs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    cases = {c["id"]: c for c in json.loads((V10 / "cases_v10.json").read_text(encoding="utf-8"))["cases"]}
    t["example"] = {"case": cases["X25"], "record": records["X25"]}
    return t


T = load()
N = T["numbers"]


def money(x, unit="B", digits=2):
    v = x / (1e9 if unit == "B" else 1e6)
    return ("−" if v < 0 else "") + f"${abs(v):,.{digits}f}{unit}"


def md(text):
    """Escape dollar signs: Streamlit reads a pair of them in one string as a LaTeX formula."""
    return text.replace("$", r"\$")


def reading(text):
    st.markdown(f'<div class="reading">{text}</div>', unsafe_allow_html=True)


def figure(name, caption):
    st.image(str(FIG / f"{name}.png"), width="stretch")
    reading(caption)


# --- header and the four numbers -------------------------------------------------------------------

st.title("Beyond Prediction: the committee's decision")
st.markdown(f"<span style='color:{MUTED}'>One budget of {N['v8_budget']} on 1 January 2025 · twenty Gulf of Mexico lease redevelopments and twenty ERCOT interconnection requests · built only from what was public that day · every number is the report's (`results/report_numbers.csv`).</span>", unsafe_allow_html=True)

fin = T["books_financed"]
own = fin[fin["basis"] == "own line, net of fee and interest"].set_index("book")
static = fin[fin["basis"] == "static (unlimited capital)"].set_index("book")
pairs = T["books_financed_pairs"].set_index(["basis", "book", "against"])
rungs = T["ladder_five_rungs"].set_index("rung")

st.markdown(f"""<div class="howto"><b>What is being decided.</b> Which of forty candidates — twenty Gulf of Mexico leases to redevelop
and twenty ERCOT interconnection requests — to fund from one budget of {N['v8_budget']}, and how to pay for the construction
calls that come later. <b>How to read this page.</b> The four numbers below are the answer. The tabs explain it in the order a
committee asks: 1 what to fund, 2 why not simply the highest return, 3 how it is paid for, 4 what can go wrong, 5 what the
language model adds, 6 which controls are in place. <b>Tab 7 is yours:</b> set the two things only the committee can decide
and see which book follows.</div>""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Capital committed now", N["v2_D_committed"], md(f"{N['v2_D_members']} candidates: 5 leases, 8 requests"), delta_color="off")
k2.metric("Gain over ranking by NPV, risk-adjusted", N["v2_pair_own_D_A"], md(f"before financing, pre-registered: {N['v10_c33']} {N['v10_c33_ci']}"), delta_color="off")
k3.metric("Construction facility to arrange", N["v2_D_facility"], md(f"drawn beyond the reserve in {N['v2_D_p_over']} of scenarios"), delta_color="off")
k4.metric("Language-model challenger, per case", N["v10_c34"], md(f"{N['v2_rung_tools_llm_minus_optimizer_first']} against a fixed rule that reads no words"), delta_color="off")
reading("Risk-adjusted = expected NPV minus the average loss in the worst 5% of scenarios, the report's registered metric. All figures are modelled on public data and assumed lease costs, not realized returns.")

tabs = st.tabs(["1 · What to fund", "2 · Risk against return", "3 · Financing", "4 · What can go wrong", "5 · The AI challenger", "6 · Controls", "7 · Your call"])

# --- 1 the recommendation ---------------------------------------------------------------------------
with tabs[0]:
    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Fund five leases and eight requests, with a construction facility")
        st.markdown(f"""<div class="rec">
<b>1. Choose the tail weight first</b> — and say it; an unstated one is read as zero.<br><br>
<b>2. Fund the risk-aware book</b> — {N['v2_D_committed']} committed: {N['v2_D_lease_capital']} of lease capital, {N['v2_D_deposits']} of deposits and a {N['v2_D_reserve']} construction reserve — <b>together with a {N['v2_D_facility']} contingent facility</b>. If no facility can be arranged, fund equal capital by sector instead.<br><br>
<b>3. Defer the {N['v2_status_defer']} waiting requests</b> until their agreements are signed; monitor {N['v2_status_monitor']} leases; reject {N['v2_status_reject']}. Reject nothing on the strength of money already spent.<br><br>
<b>4. Run the challenger before signing</b>, confirm its reading of your rules, and record any departure from its guidance with the evidence acknowledged.
</div>""", unsafe_allow_html=True)
        st.markdown("")
        c1, c2, c3 = st.columns(3)
        c1.metric("Expected NPV, held-out", N["v2_D_static_mean"], f"financed {N['v2_D_own_mean']}", delta_color="off")
        c2.metric("Worst-5% average loss", N["v2_D_static_cvar"], f"financed {N['v2_D_own_cvar']}", delta_color="off")
        c3.metric("Chance of losing money", N["v2_D_static_ploss"], f"financed {N['v2_D_own_ploss']}", delta_color="off")
        reading("Scored on 2,000 held-out scenarios. \"Financed\" means funded within the facility, net of a 0.5% commitment fee and 8% interest on draws. Model-based results on public data and assumed lease costs — not realized returns.")
    with right:
        m = T["book_D_members"]
        inb = m[m["in_book"]].copy()
        inb["label"] = [f"{p.split('|')[-1]} {t}" + (f" {mw:.0f} MW" if pd.notna(mw) and t != "Lease redevelopment" else "") for p, t, mw in zip(inb["project_id"], inb["technology"], inb["mw"])]
        long = inb.melt(id_vars=["label", "technology", "p_negative", "status"], value_vars=["charge_$M", "expected_npv_$M"], var_name="measure", value_name="value")
        long["measure"] = long["measure"].map({"charge_$M": "capital charged now", "expected_npv_$M": "expected NPV"})
        order = inb.sort_values("charge_$M", ascending=False)["label"].tolist()
        chart = (alt.Chart(long).mark_bar().encode(
            y=alt.Y("label:N", sort=order, title=None, axis=alt.Axis(labelLimit=260)),
            x=alt.X("value:Q", title="$ million (2024)"),
            yOffset=alt.YOffset("measure:N"),
            color=alt.Color("technology:N", scale=alt.Scale(domain=list(TECH_COLOR), range=list(TECH_COLOR.values())), legend=alt.Legend(title=None, orient="bottom")),
            opacity=alt.condition(alt.datum.measure == "expected NPV", alt.value(0.45), alt.value(1.0)),
            tooltip=["label", "status", "measure", alt.Tooltip("value:Q", format=",.0f", title="$M"), alt.Tooltip("p_negative:Q", format=".0%", title="chance of a loss")],
        ).properties(height=430, title="Capital charged now (solid) and expected NPV (light), $M"))
        st.altair_chart(chart, width="stretch")
        reading("Three requests with signed agreements carry most of the construction reserve and lose in 62–64% of scenarios; the five waiting wind and solar requests cost only their deposits and pay in exactly the scenarios in which the leases do not. Hover for each member's chance of a loss.")
    with st.expander("Every candidate and its status"):
        show = m[["project_id", "technology", "status", "charge_$M", "expected_npv_$M", "p_negative", "objective_cost_$M"]].rename(columns={"charge_$M": "charge ($M)", "expected_npv_$M": "expected NPV ($M)", "p_negative": "chance of a loss", "objective_cost_$M": "removal costs the objective ($M)"})
        st.dataframe(show.style.format({"charge ($M)": "{:,.0f}", "expected NPV ($M)": "{:,.0f}", "chance of a loss": "{:.0%}", "removal costs the objective ($M)": "{:,.0f}"}), width="stretch", height=420, hide_index=True)

# --- 2 risk against return --------------------------------------------------------------------------
with tabs[1]:
    st.subheader("The highest expected return is not the best investment")
    fr = T["frontier"]
    pen = fr[fr["kind"] == "penalty"].dropna(subset=["mean"]).copy()
    pen["tail weight"] = pen["setting"]
    comp = fr[fr["kind"] == "comparator"].copy()
    comp["book"] = comp["policy"].str[0]
    comp["name"] = comp["book"].map(BOOK_NAME)
    left, right = st.columns([1.3, 1])
    with left:
        lam = st.select_slider("How much the bad years weigh, λ: a dollar of average loss in the worst 5% of scenarios counts as λ dollars of expected value", options=sorted(pen["tail weight"].unique()), value=1.0)
        chosen = pen[pen["tail weight"] == lam].iloc[0]
        base = alt.Chart(pen).encode(x=alt.X("cvar_loss:Q", title="Worst-5% average loss, held-out ($ billion)", axis=alt.Axis(format="$.1s")), y=alt.Y("mean:Q", title="Expected NPV, held-out ($ billion)", axis=alt.Axis(format="$.2s"), scale=alt.Scale(zero=False)))
        line = base.mark_line(color=INK, strokeWidth=2).encode(order="tail weight:Q")
        pts = base.mark_circle(size=70, color=INK).encode(tooltip=[alt.Tooltip("tail weight:Q"), alt.Tooltip("mean:Q", format="$,.0f"), alt.Tooltip("cvar_loss:Q", format="$,.0f"), alt.Tooltip("n:Q", title="members")])
        sel = alt.Chart(pen[pen["tail weight"] == lam]).mark_circle(size=420, color="#0072B2", stroke=INK, strokeWidth=1.5).encode(x="cvar_loss:Q", y="mean:Q")
        comps = alt.Chart(comp).mark_point(size=260, filled=True, stroke=INK, strokeWidth=1).encode(
            x="cvar_loss:Q", y="mean:Q", shape=alt.Shape("name:N", legend=alt.Legend(title=None, orient="bottom", columns=2)),
            color=alt.Color("book:N", scale=alt.Scale(domain=list(BOOK_COLOR), range=list(BOOK_COLOR.values())), legend=None),
            tooltip=["name", alt.Tooltip("mean:Q", format="$,.0f"), alt.Tooltip("cvar_loss:Q", format="$,.0f")])
        st.altair_chart((line + pts + sel + comps).properties(height=420, title="The frontier over tail weights, and where the conventional books sit"), width="stretch")
        reading("Each point on the line is the best book for one tail weight; the blue circle is the weight you chose. The conventional books (symbols) sit below the frontier: they take more tail for the same expected value. λ = 1 is the registered setting.")
    with right:
        st.markdown(f"**At λ = {lam:g}: {int(chosen['n'])} members**")
        st.metric("Expected NPV", money(chosen["mean"]))
        st.metric("Worst-5% average loss", money(chosen["cvar_loss"]))
        st.metric("Chance of a loss", f"{chosen['p_loss']:.0%}")
        st.markdown("**Budget by technology**")
        techs = [c for c in pen.columns if c.startswith("charge_") and c != "charge"]
        tdf = pd.DataFrame({"technology": [c.replace("charge_", "") for c in techs], "capital": [chosen[c] for c in techs]})
        tdf = tdf[tdf["capital"] > 0]
        st.altair_chart(alt.Chart(tdf).mark_bar().encode(x=alt.X("capital:Q", title="$ billion", axis=alt.Axis(format="$.2s")), y=alt.Y("technology:N", title=None, sort="-x"),
                        color=alt.Color("technology:N", scale=alt.Scale(domain=list(TECH_COLOR), range=list(TECH_COLOR.values())), legend=None), tooltip=["technology", alt.Tooltip("capital:Q", format="$,.0f")]).properties(height=200), width="stretch")
        reading("Move the slider: a heavier weight on the tail drops the large gas and solar requests first and, at λ = 4, keeps only the wind requests.")

# --- 3 financing ------------------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Funded the same way, the risk-aware book still scores best — and needs its facility")
    left, right = st.columns([1.3, 1])
    bases = ["static (unlimited capital)", "no line (calls beyond the reserve forfeit)", "own line, net of fee and interest", "common $2.53B line, net of fee and interest"]
    with left:
        f = fin[fin["basis"].isin(bases) & fin["book"].isin(list(BOOK_COLOR))].copy()
        f["name"] = f["book"].map(BOOK_NAME)
        f["basis_short"] = f["basis"].map({bases[0]: "static, as compared before", bases[1]: "no construction line", bases[2]: "own line, net of fee and interest", bases[3]: "common $2.53B line, net"})
        chart = alt.Chart(f).mark_bar().encode(
            x=alt.X("basis_short:N", title=None, sort=[f["basis_short"].unique()[i] for i in range(4)], axis=alt.Axis(labelAngle=0, labelLimit=200)),
            y=alt.Y("metric:Q", title="Registered metric: expected NPV − worst-5% loss ($ billion)", axis=alt.Axis(format="$.2s")),
            xOffset=alt.XOffset("book:N", sort=list(BOOK_COLOR)),
            color=alt.Color("book:N", scale=alt.Scale(domain=list(BOOK_COLOR), range=list(BOOK_COLOR.values())), legend=alt.Legend(title=None, orient="bottom", labelLimit=320), sort=list(BOOK_COLOR)),
            tooltip=["name", "basis", alt.Tooltip("metric:Q", format="$,.0f"), alt.Tooltip("mean:Q", format="$,.0f", title="expected NPV"), alt.Tooltip("cvar_loss:Q", format="$,.0f", title="worst-5% loss")],
        ).properties(height=400, title="Five decision processes on four funding bases")
        st.altair_chart(chart, width="stretch")
        reading(f"On the financed basis the risk-aware book (D) scores {N['v2_D_own_metric']} against {N['v2_C_own_metric']} for the deterministic optimizer and {N['v2_A_own_metric']} for NPV ranking: {N['v2_pair_own_D_A']} {N['v2_pair_own_D_A_ci']} over NPV ranking, {N['v2_pair_own_D_C']} {N['v2_pair_own_D_C_ci']} over the deterministic book. With no line at all, equal capital by sector (B) would lead — the recommendation is the book and its facility together.")
    with right:
        cap = own.loc[list(BOOK_COLOR), ["lease_capital", "deposits", "reserve", "facility_own_q95", "financing_cost_mean_own_line", "capital_committed"]].reset_index()
        stack = cap.melt(id_vars="book", value_vars=["lease_capital", "deposits", "reserve", "facility_own_q95"], var_name="part", value_name="capital")
        stack["part"] = stack["part"].map({"lease_capital": "lease capital, spent now", "deposits": "request deposits, spent now", "reserve": "construction reserve (expected draw)", "facility_own_q95": "contingent facility (95th-percentile excess)"})
        order = ["lease capital, spent now", "request deposits, spent now", "construction reserve (expected draw)", "contingent facility (95th-percentile excess)"]
        st.altair_chart(alt.Chart(stack).mark_bar().encode(
            x=alt.X("book:N", title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y("capital:Q", title="$ billion", axis=alt.Axis(format="$.2s"), stack="zero"),
            color=alt.Color("part:N", sort=order, scale=alt.Scale(domain=order, range=["#D55E00", "#E69F00", "#56B4E9", "#DDDDDD"]), legend=alt.Legend(title=None, orient="bottom", columns=1, labelLimit=320)),
            order=alt.Order("part_order:Q"), tooltip=["book", "part", alt.Tooltip("capital:Q", format="$,.0f")],
        ).transform_calculate(part_order="indexof(" + json.dumps(order) + ", datum.part)").properties(height=330, title="What each process commits, reserves and may call"), width="stretch")
        tbl = cap.assign(**{"committed now": cap["capital_committed"].map(money), "facility": cap["facility_own_q95"].map(money), "expected financing cost": cap["financing_cost_mean_own_line"].map(lambda x: money(x, "M", 0))})[["book", "committed now", "facility", "expected financing cost"]]
        st.dataframe(tbl, hide_index=True, width="stretch")
        reading("Every process needs a facility of $2.5–3.2B and pays $126–147M for it in expected present value; the risk-aware book's is neither the largest nor the dearest.")

# --- 4 what can go wrong ----------------------------------------------------------------------------
with tabs[3]:
    st.subheader("The tail is the candidates' co-movement, and the risk-aware book holds up in every world")
    left, right = st.columns([1, 1.2])
    with left:
        d = T["dependence_dial"]
        dd = d[d["omega"].notna() & d["book"].isin(list(BOOK_COLOR))].copy()
        dd["name"] = dd["book"].map(BOOK_NAME)
        st.altair_chart(alt.Chart(dd).mark_line(point=True, strokeWidth=2.5).encode(
            x=alt.X("omega:Q", title="Share of scenarios keeping the co-movement (0 = independent, 1 = as scored)"),
            y=alt.Y("cvar_loss:Q", title="Worst-5% average loss ($ billion)", axis=alt.Axis(format="$.1s")),
            color=alt.Color("book:N", scale=alt.Scale(domain=list(BOOK_COLOR), range=list(BOOK_COLOR.values())), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=["name", "omega", alt.Tooltip("cvar_loss:Q", format="$,.0f")]).properties(height=380, title="The tail grows with the co-movement"), width="stretch")
        como = d[d["dependence"] == "comonotonic bound"].set_index("book")["cvar_loss"]
        reading(f"Five leases on one oil price, eight requests on one power price. If every candidate had its worst day on the same day (the comonotonic bound) the risk-aware book's loss would be {money(como['D'])}, NPV ranking's {money(como['A'])}. The risk-aware book keeps the smallest tail at every setting.")
    with right:
        w = T["books_worlds"]
        w["name"] = w["book"].map(BOOK_NAME)
        worlds = list(dict.fromkeys(w["world"]))
        st.altair_chart(alt.Chart(w[w["book"].isin(list(BOOK_COLOR))]).mark_bar().encode(
            y=alt.Y("world:N", sort=worlds, title=None, axis=alt.Axis(labelLimit=260)), x=alt.X("metric:Q", title="Registered metric ($ billion)", axis=alt.Axis(format="$.2s")),
            yOffset=alt.YOffset("book:N", sort=list(BOOK_COLOR)),
            color=alt.Color("book:N", scale=alt.Scale(domain=list(BOOK_COLOR), range=list(BOOK_COLOR.values())), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=["name", "world", alt.Tooltip("metric:Q", format="$,.0f"), alt.Tooltip("mean:Q", format="$,.0f", title="expected NPV"), alt.Tooltip("cvar_loss:Q", format="$,.0f", title="worst-5% loss")]).properties(height=380, title="The books in seven worlds"), width="stretch")
        reading(f"The risk-aware book scores best in {N['v2_worlds_D_best']} of 7 worlds and is the only one whose metric stays positive when ERCOT prices are 25% lower ({N['v2_world_ercot_low_D']} against {N['v2_world_ercot_low_A']} for NPV ranking) or oil sits at $45 for five years ({N['v2_world_oil45_D']}).")

# --- 5 the AI challenger ----------------------------------------------------------------------------
with tabs[4]:
    st.subheader("The optimizer does the work; the language model guards the reasoning")
    left, right = st.columns([1, 1.15])
    with left:
        arms = T["ladder_five_arms"].groupby("arm")["metric"].mean().reindex(list(ARM_LABEL)).reset_index()
        arms["label"] = arms["arm"].map(ARM_LABEL)
        st.altair_chart(alt.Chart(arms).mark_bar().encode(
            x=alt.X("label:N", sort=list(ARM_LABEL.values()), title=None, axis=alt.Axis(labelAngle=0, labelLimit=140)),
            y=alt.Y("metric:Q", title="Committee's own objective, mean per case ($ million)", axis=alt.Axis(format="$.3s")),
            color=alt.Color("arm:N", scale=alt.Scale(domain=list(ARM_COLOR), range=list(ARM_COLOR.values())), legend=None),
            tooltip=["label", alt.Tooltip("metric:Q", format="$,.0f")]).properties(height=330, title="Where each process leaves the committee (48 registered cases × 5 worlds)"), width="stretch")
        rr = rungs.reset_index()
        rr["label"] = rr["rung"].map({"tools_minus_proposal": "tools only vs the proposal (registered)", "tools_llm_minus_tools": "tools + LLM vs tools only (registered, C34)", "optimizer_first_minus_tools": "optimizer-first rule vs tools only (post-registration)",
                                      "tools_llm_minus_optimizer_first": "tools + LLM vs optimizer-first rule (post-registration)", "optimizer_minus_tools_llm": "optimizer vs tools + LLM (registered, C36)", "optimizer_minus_optimizer_first": "optimizer vs optimizer-first rule (post-registration)"})
        order = ["tools only vs the proposal (registered)", "tools + LLM vs tools only (registered, C34)", "optimizer-first rule vs tools only (post-registration)", "tools + LLM vs optimizer-first rule (post-registration)", "optimizer vs tools + LLM (registered, C36)"]
        rr = rr[rr["label"].isin(order)]
        base = alt.Chart(rr).encode(y=alt.Y("label:N", sort=order, title=None, axis=alt.Axis(labelLimit=330)))
        bars = base.mark_rule(strokeWidth=2, color=INK).encode(x=alt.X("low:Q", title="Paired difference per case, $ million (95% interval)", axis=alt.Axis(format="$.2s")), x2="high:Q")
        dots = base.mark_circle(size=140, color="#0072B2").encode(x="mean:Q", tooltip=["label", alt.Tooltip("mean:Q", format="$,.0f"), alt.Tooltip("low:Q", format="$,.0f"), alt.Tooltip("high:Q", format="$,.0f")])
        zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=INK).encode(x="x:Q")
        st.altair_chart((bars + dots + zero).properties(height=260, title="The rungs: what each part adds"), width="stretch")
        reading(f"Tools {N['v2_rung_tools_minus_proposal']}, the language model {N['v2_rung_tools_llm_minus_tools']} more, the optimizer {N['v2_rung_optimizer_minus_tools_llm']} beyond — registered and scored once. Against a fixed optimizer-first rule the model's edge is {N['v2_rung_tools_llm_minus_optimizer_first']} {N['v2_rung_tools_llm_minus_optimizer_first_ci']}: a rule that reads no words chooses the book as well. The model's value is the argument it makes, not the book it picks.")
    with right:
        st.markdown("**One registered case, as recorded (X25: a sunk-cost argument on the recommended book)**")
        ex = T["example"]
        st.markdown(f'<div class="quote"><b>The committee says:</b> “{ex["case"]["statement"]}”</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="quote" style="border-color:#E69F00"><b>The model reads it as:</b> {ex["record"]["reading"]}<br><br><b>What it cannot represent:</b> {ex["record"]["not_representable"]}</div>', unsafe_allow_html=True)
        st.markdown("<b>The memo (every number checked against the fact sheet):</b>", unsafe_allow_html=True)
        for v in ex["record"]["memo"]["vulnerabilities"]:
            st.markdown(f'<div class="quote" style="border-color:#009E73"><b>{v["type"]}</b> — {v["claim"]}</div>', unsafe_allow_html=True)
        ver = ex["record"]["verification"]
        st.markdown(f'<div class="quote" style="border-color:#D55E00"><b>Level:</b> {ex["record"]["level"]} (the proposal is kept; no computed book beats it clear of zero). <b>Question for the committee:</b> {ex["record"]["memo"]["question_for_the_committee"]}<br><b>Verification:</b> {ver["n_grounded"]} of {ver["n_numbers"]} numbers on the fact sheet; flagged: {", ".join(ver["ungrounded"]) or "none"}.</div>', unsafe_allow_html=True)
        reading("The model named the sunk cost — which no tool can — and the unfunded construction calls, which the checklist had already flagged. It also wrote one number that was not on its sheet, and the verifier flagged it. A named person signs; the ledger records what was read, shown and decided.")
    st.markdown("**The nine registered lines, scored once**")
    lines = T["lines"]
    cols = [c for c in ("id", "question", "line", "rule", "estimate", "result") if c in lines.columns]
    st.dataframe(lines[cols], hide_index=True, width="stretch", height=360)

# --- 6 controls ---------------------------------------------------------------------------------------
with tabs[5]:
    st.subheader(f"{N['v2_controls']} controls: {N['v2_controls_yes']} in place, {N['v2_controls_partly']} partly — and what a real commitment still needs")
    m = T["readiness_matrix"].rename(columns={"control": "Control", "implemented": "In place", "how it was tested": "How it was tested", "known limitation": "Known limitation", "validation before a real commitment": "Validation before a real commitment"})

    def shade(v):
        return {"yes": "background-color: #D5F0E3", "partly": "background-color: #F5D9C8"}.get(v, "")

    st.dataframe(m.style.map(shade, subset=["In place"]), hide_index=True, width="stretch", height=520)
    reading("Every number is computed by tools; the committee confirms the model's reading before anything is computed; a guide is allowed only toward a book that keeps every rule; every number in the memo is verified; a named person signs; the ledger is hash-chained. The two controls partly in place — injection resistance and scenario realism — have named remedies. Nothing here is a demonstrated improvement in a company's returns: simulated committees, assumed costs, public data.")
    figure("F55_committee_workflow", "How a committee uses it: nine stages in three hands — the committee decides, tools compute, the model argues — and the five levels at which the challenger may act or must stand back.")

# --- 7 your call ------------------------------------------------------------------------------------
# The two inputs the recommendation leaves to the committee (tab 1, steps 1 and 2): the tail weight, and whether a
# construction facility can be arranged. Each answer is a row the notebooks already scored; nothing is re-solved.
with tabs[6]:
    st.subheader("Two choices only the committee can make — and the book that follows from them")
    left, right = st.columns([1, 1.3])
    weights = {0.0: "0 — ignore the bad years", 0.25: "0.25", 0.5: "0.5", 1.0: "1 — the registered setting", 2.0: "2", 4.0: "4 — avoid losses above all"}
    with left:
        st.markdown("**1. How much do the bad years weigh?**")
        lam7 = st.radio("A dollar of average loss in the worst 5% of scenarios counts as this many dollars of expected value", list(weights), index=3, format_func=weights.get)
        st.markdown("**2. Can the company arrange a contingent construction facility?**")
        line = st.radio(md(f"A standby credit line of about {N['v2_D_facility']} for construction calls beyond the reserve, at a 0.5% commitment fee and 8% interest on draws"),
                        ["yes", "no"], format_func={"yes": "Yes, a facility can be arranged", "no": "No, every call must be met from the budget"}.get)
    with right:
        if line == "yes":
            row = pen[pen["tail weight"] == lam7].iloc[0]
            st.markdown(f"**Fund the risk-aware book for λ = {lam7:g}: {int(row['leases'])} leases and {int(row['requests'])} requests**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Expected NPV", money(row["mean"]))
            c2.metric("Worst-5% average loss", money(row["cvar_loss"]))
            c3.metric("Chance of a loss", f"{row['p_loss']:.0%}")
            if lam7 == 1.0:
                reading(f"This is the report's recommendation (book D). Financed through the facility it scores {N['v2_D_own_metric']} on the registered metric, {N['v2_pair_own_D_A']} {N['v2_pair_own_D_A_ci']} above ranking by NPV.")
            else:
                reading("Scored before financing, as in tab 2. Only the registered setting, λ = 1, was also scored through the facility; a different weight is a different decision, so the committee should state it before the book is chosen.")
            members = [p.split("|")[-1] for p in str(row["members"]).split(";")]
            st.markdown("**Members:** " + ", ".join(members))
        else:
            noline = fin[fin["basis"] == "no line (calls beyond the reserve forfeit)"].set_index("book").loc[list(BOOK_COLOR)].reset_index()
            best = noline.loc[noline["metric"].idxmax()]
            st.markdown(f"**Without a facility, fund {BOOK_NAME[best['book']].split('  ')[1]}: {int(best['leases'])} leases and {int(best['requests'])} requests**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Expected NPV", money(best["mean"]))
            c2.metric("Worst-5% average loss", money(best["cvar_loss"]))
            c3.metric("Chance of a loss", f"{best['p_loss']:.0%}")
            noline["name"] = noline["book"].map(BOOK_NAME)
            st.altair_chart(alt.Chart(noline).mark_bar().encode(
                y=alt.Y("name:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)), x=alt.X("metric:Q", title="Registered metric with no facility ($ billion)", axis=alt.Axis(format="$.2s")),
                color=alt.Color("book:N", scale=alt.Scale(domain=list(BOOK_COLOR), range=list(BOOK_COLOR.values())), legend=None),
                tooltip=["name", alt.Tooltip("metric:Q", format="$,.0f"), alt.Tooltip("mean:Q", format="$,.0f", title="expected NPV"), alt.Tooltip("cvar_loss:Q", format="$,.0f", title="worst-5% loss")]).properties(height=220), width="stretch")
            reading("With no facility a construction call beyond the reserve is forfeited, and the request with it. Scored at the registered setting, λ = 1, whatever the weight chosen on the left: equal capital by sector then leads, so the recommendation is the risk-aware book and its facility together.")
