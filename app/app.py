"""The dashboard: the AI inside the portfolio decision, in two modes, reading results/ only.

What: a Streamlit app (``make app``) with the two modes of PLAN.md §14's
addenda. *Decide forward* — the budget, the risk aversion, the technology
cap and the named stress re-solve the risk-aware MILP on the cached
scenarios of notebook 08 in a second or two; the four books of notebook
09, the frontier, the cost grid and its impact, each project's impact,
the forward view at 1–20 years, the advisor's recorded recommendation,
the challenge round and the override gate with the ledger. *Learn from
history* — the decision gym: a past situation as of its date, the human
picks under the budget, the outcome is revealed with instinct, the rule,
the advisor and hindsight beside it, and the pick goes to the ledger.
Also the scenarios and risk page, the candidates page with the
data-completeness warning, and the ledger.
Why: the capital decision has to be seen, moved and challenged by a
person; replay by default, live only with the key in ``.env``.
Reads: ``results/*.csv``, ``data/processed/candidate_npv_scenarios.parquet``,
``figures/*.png``, ``prompts/``; the modules ``src.optimizer``,
``src.advisor``, ``src.gym``, ``src.horizons``.
Writes: ``results/decision_ledger.csv`` (append), ``results/advisor_runs.jsonl`` (live calls only).
Used by: ``streamlit run app/app.py``.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv, economics as ec, energy_data, gym, horizons as hz, optimizer as opt, paths, scenarios as sc  # noqa: E402

R, FIG = paths.RESULTS, paths.FIGURES
st.set_page_config(page_title="Queue to Capital — the portfolio desk", layout="wide")


# --- cached loads ------------------------------------------------------------------------------

@st.cache_data
def load_tables():
    t = {name: pd.read_csv(R / f"{name}.csv") for name in (
        "candidate_npv", "portfolio_scores", "portfolio_allocation", "stress_tests", "stress_candidates", "project_impact", "upstream_cost_grid",
        "cost_sensitivity", "scenario_summary", "horizon_view", "horizon_books", "advisor_recommendations", "decision_gym_situations", "decision_gym_scores",
        "advisor_evaluation", "investment_candidates")}
    t["books"] = pd.read_csv(R / "portfolio_books.csv", index_col=0)
    t["registered"] = pd.read_json(R / "success_criteria_v7_registered.json", typ="series")
    scen = pd.read_parquet(paths.DATA_PROCESSED / "candidate_npv_scenarios.parquet")
    ids = list(t["candidate_npv"]["project_id"])
    t["ids"] = ids
    t["A"] = {(g, c): scen[(scen["generator"] == g) & (scen["revenue_case"] == c)].sort_values("scenario")[ids].to_numpy(float)
              for g in ("primary", "copula") for c in ("merchant", "contracted")}
    return t


@st.cache_data
def load_situations():
    """The gym's sixteen situations, rebuilt as in notebook 10 (the lease regimes take a few seconds)."""
    pack = pd.read_csv(R / "decision_pack.csv")
    out = []
    for region in ("ERCOT", "PJM", "CAISO"):
        for cohort in (2017, 2018, 2019):
            s = gym.queue_situation(pack, region, cohort, "entry")
            if s:
                out.append(s)
        s = gym.queue_situation(pack, region, 2017, "2y")
        if s:
            out.append(s)
    out.append(gym.queue_situation(pack, "ERCOT", 2018, "entry", budget_cut=0.2))
    cand = pd.read_csv(R / "candidate_npv.csv")
    leases = cand[cand["sector"] == "offshore oil and gas"].reset_index(drop=True)
    upstream = pd.read_parquet(paths.DATA_INTERIM / "upstream_monthly.parquet")
    market = pd.read_parquet(paths.DATA_INTERIM / "market_monthly.parquet")
    cpi = pd.read_parquet(paths.DATA_INTERIM / "cpi_monthly.parquet")
    wti = energy_data.read_eia_monthly_price(paths.RAW_PRICES / "RWTCm.xls", "wti_usd_bbl")
    hh = energy_data.read_eia_monthly_price(paths.RAW_PRICES / "RNGWHHDm.xls", "hh_usd_mmbtu")
    lease_ids = [p.split("|")[1] for p in leases["project_id"]]
    hist = upstream[upstream["lease_number"].isin(lease_ids)]
    oil_w = hist.pivot(index="lease_number", columns="month", values="oil_bbl").fillna(0)
    gas_w = hist.pivot(index="lease_number", columns="month", values="gas_mcf").fillna(0)
    baselines = {lid: ec.lease_baseline(oil_w.loc[lid].to_numpy(), gas_w.loc[lid].to_numpy(), months=240)[:2] for lid in lease_ids}
    changes = sc.joint_log_changes(market.rename(columns={"wti_usd_bbl_real2024": "w", "hh_usd_mmbtu_real2024": "h", "ercot_usd_mwh_real2024": "e"}), series=["w", "h", "e"])
    lam = float(pd.read_json(R / "success_criteria_v7_registered.json", typ="series")["lam"])
    for name, start in gym.REGIMES.items():
        out.append(gym.lease_situation(name, start, leases, baselines, wti, hh, cpi, changes, n_scen=300, seed=2020, lam=lam))
    return out


T = load_tables()
cand, ids = T["candidate_npv"], T["ids"]
capex = cand.set_index("project_id")["capex"].reindex(ids)
tech = cand.set_index("project_id")["technology"].reindex(ids).to_numpy()
completeness = cand.set_index("project_id")["data_completeness"].reindex(ids)
ledger0 = pd.read_csv(R / "decision_ledger.csv")
BUDGET0, CAP0, LAM0, LEVEL = float(ledger0.loc[0, "budget"]), float(T["registered"]["technology_cap"]) if "technology_cap" in T["registered"] else 0.4, float(T["registered"]["lam"]), float(T["registered"]["level"])
advisor = adv.Advisor(mode="auto")


def money(x, unit="B"):
    return f"${x / (1e9 if unit == 'B' else 1e6):,.2f}{unit}"


def ledger():
    return pd.read_csv(R / "decision_ledger.csv")


def figure(name, caption):
    path = FIG / f"{name}.png"
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")


# --- sidebar -----------------------------------------------------------------------------------

st.sidebar.title("Queue to Capital")
st.sidebar.caption(f"Advisor: {advisor.model} — {'live (key in .env)' if advisor.live else 'replay only (no key)'}; {len(advisor.records)} recorded answers")
page = st.sidebar.radio("Mode", ["Decide forward", "Learn from history (the gym)", "Scenarios and risk", "Candidates and the cost grid", "The ledger"])
st.sidebar.markdown("Every number on these pages is read from `results/`; nothing is recomputed except the book, re-solved on the cached scenarios.")


# --- decide forward ----------------------------------------------------------------------------

if page == "Decide forward":
    st.title("Decide forward: the book under your budget, your risk aversion and the scenario distribution")
    c1, c2, c3, c4 = st.columns(4)
    budget = c1.slider("Budget ($ billion)", 0.5, 15.0, round(BUDGET0 / 1e9, 2), 0.25) * 1e9
    lam = c2.slider("Risk aversion λ (0 = deterministic)", 0.0, 4.0, LAM0, 0.25)
    cap = c3.slider("Technology cap (share of budget)", 0.2, 1.0, CAP0, 0.05)
    case = c4.selectbox("Revenue case", ["contracted", "merchant"])
    thin_rule = st.checkbox("Apply the thin-data rule: a technology whose candidates have completeness below 1 gets its cap scaled by that completeness and its NPV spread widened", value=True)
    stress = st.selectbox("Named stress to read the book under", list(T["stress_tests"]["stress"]))
    A = T["A"][("primary", case)]
    A_oos = T["A"][("copula", case)]
    if thin_rule:
        comp = completeness.to_numpy()
        A = A.mean(axis=0)[None, :] + (A - A.mean(axis=0)[None, :]) / comp[None, :]  # wider spread where data are thin
        caps = {t: cap * float(completeness[tech == t].mean()) for t in np.unique(tech)}
    with st.spinner("re-solving the risk-aware MILP on 2,000 cached scenarios"):
        try:
            if thin_rule:
                # the tightest of the per-technology caps is applied to every technology (one MILP call); the caps are shown beside the book
                res = opt.solve_milp(A, capex.to_numpy(), budget, lam=lam, level=LEVEL, groups=tech, group_cap=min(caps.values()))
            else:
                res = opt.solve_milp(A, capex.to_numpy(), budget, lam=lam, level=LEVEL, groups=tech, group_cap=cap)
            x = res["x"]
        except RuntimeError as err:
            st.error(str(err))
            x = np.zeros(len(ids), int)
    total_oos = A_oos @ x
    members = list(np.array(ids)[x == 1])
    thin = [m for m in members if completeness[m] < 1]
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Members", int(x.sum()))
    m2.metric("Capital", money(float(capex.to_numpy() @ x)))
    m3.metric("Expected NPV (held-out scenarios)", money(float(total_oos.mean())))
    cv = opt.cvar(-total_oos, LEVEL)
    m4.metric("CVaR95", (f"loss {money(cv)}" if cv > 0 else f"worst 5% still a profit of {money(-cv)}"))
    m5.metric("P(NPV < 0)", f"{(total_oos < 0).mean():.1%}")
    used = float(capex.to_numpy() @ x)
    binding = "budget" if used > 0.98 * budget else "technology cap" if any(float(capex[tech == t].to_numpy() @ x[tech == t]) > 0.98 * cap * budget for t in np.unique(tech)) else "nothing binds (no more positive-NPV candidates)"
    st.write(f"**Binding constraint:** {binding}." + (f" **Thin data:** {len(thin)} member(s) with completeness below 1 ({', '.join(thin)}); their uncertainty is widened and the cap scaled to {min(caps.values()):.0%}." if thin_rule and thin else ""))
    if thin_rule:
        st.caption("Per-technology caps under the rule: " + ", ".join(f"{t} {v:.0%}" for t, v in caps.items()))
    npv_stress = T["stress_candidates"][T["stress_candidates"]["stress"] == stress].set_index("project_id")["npv"].reindex(ids).fillna(0).to_numpy()
    st.write(f"Under the stress **{stress}** this book's flat-path NPV is {money(float(npv_stress @ x))} (base: {money(float(T['stress_candidates'][T['stress_candidates']['stress'] == 'base'].set_index('project_id')['npv'].reindex(ids).fillna(0).to_numpy() @ x))}).")
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Your book beside the four registered books")
        ps = T["portfolio_scores"]
        oos = ps[ps["scenarios"].str.startswith("held-out") & (ps["revenue_case"] == case)].set_index("book")
        if oos.empty:
            oos = ps[ps["scenarios"].str.startswith("held-out")].drop_duplicates("book").set_index("book")
        rows = [{"book": b, "members": int(T["books"][b].reindex(ids).sum()), "expected NPV $B": oos.loc[b, "expected_npv"] / 1e9, "CVaR95 loss $B": oos.loc[b, "cvar_loss"] / 1e9, "P(NPV<0)": oos.loc[b, "p_negative"]}
                for b in ("A top-N NPV", "B equal capital", "C deterministic MILP", "D risk-aware MILP")]
        rows.append({"book": "your book", "members": int(x.sum()), "expected NPV $B": total_oos.mean() / 1e9, "CVaR95 loss $B": cv / 1e9, "P(NPV<0)": float((total_oos < 0).mean())})
        st.dataframe(pd.DataFrame(rows).round(3), hide_index=True)
        alloc = pd.Series({t: float(capex[tech == t].to_numpy() @ x[tech == t]) / 1e9 for t in np.unique(tech)}, name="capital $B")
        st.bar_chart(alloc)
    with right:
        st.subheader("Members")
        tbl = cand.set_index("project_id").loc[members, ["technology", "capex", "expected_npv_base", "expected_npv_contracted", "p_operation_7y", "data_completeness", "provenance"]] if members else cand.iloc[0:0]
        st.dataframe(tbl.assign(capex=tbl["capex"] / 1e6, expected_npv_base=tbl["expected_npv_base"] / 1e6, expected_npv_contracted=tbl["expected_npv_contracted"] / 1e6)
                     .rename(columns={"capex": "capex $M", "expected_npv_base": "NPV merchant $M", "expected_npv_contracted": "NPV contracted $M"}).round(1))
    figure("F33_four_books", "F33: the four books and the frontier out of sample (notebook 09).")

    st.subheader("The forward view: the book at 1, 2, 3, 5, 10 and 20 years")
    h = st.select_slider("Horizon (years)", options=list(hz.HORIZONS), value=5)
    hb = T["horizon_books"].set_index("horizon_years").loc[h]
    hv = T["horizon_view"][T["horizon_view"]["horizon_years"] == h].set_index("project_id").reindex(ids)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Members at this horizon", int(hb["n_members"]))
    k2.metric("Expected NPV within horizon", f"${hb['expected_npv_within_horizon_$B']:.2f}B")
    k3.metric("Full-life expected NPV (held-out)", f"${hb['full_life_expected_npv_oos_$B']:.2f}B")
    k4.metric("Full-life P(NPV < 0)", f"{hb['full_life_p_negative_oos']:.1%}")
    st.dataframe(hv[["technology", "expected_npv_within_horizon", "p_operation_by_horizon"]].assign(expected_npv_within_horizon=hv["expected_npv_within_horizon"] / 1e6)
                 .rename(columns={"expected_npv_within_horizon": f"NPV within {h} y, $M", "p_operation_by_horizon": f"P(operation by {h} y)"}).round(2))
    figure("F35_horizon_view", "F35: the forward view (notebook 10).")

    st.subheader("The advisor")
    rec = T["advisor_recommendations"]
    row = rec[rec["scenario"] == stress]
    if len(row) and row.iloc[0]["status"] != "not recorded":
        r = row.iloc[0]
        st.markdown(f"**Recorded recommendation for '{stress}'** ({r['status']}, grounding rate {r['grounding_rate']:.2f}): book **{r['book']}**, {int(r['n_members'])} members, Jaccard to D {r['jaccard_to_D']:.2f}.")
        st.write(r["why"])
        st.write(f"*What would change the answer:* {r['what_would_change_the_answer']}")
    else:
        st.info("No recorded recommendation for this scenario yet: run notebook 10 once with `ANTHROPIC_API_KEY` in `.env` and the answers replay here.")
    st.markdown("**Challenge my decision.** State the book you prefer and why; the advisor runs the motivated-reasoning check and argues the opposing case. The override gate below opens only after the five answers and the opposing case.")
    statement = st.text_area("Your decision and your reasons", height=120, placeholder="I want … because …")
    opposing = st.text_input("The opposing book (default: the book re-solved above)", value=f"The re-solved book: {', '.join(members) if members else 'empty'}")
    if st.button("Run the challenge round") and statement.strip():
        context = adv.format_table(cand[["project_id", "technology", "capex", "expected_npv_base", "expected_npv_contracted", "p_operation_7y", "data_completeness", "provenance"]]
                                   .assign(capex=cand["capex"] / 1e6, expected_npv_base=cand["expected_npv_base"] / 1e6, expected_npv_contracted=cand["expected_npv_contracted"] / 1e6)
                                   .rename(columns={"capex": "capex_$M", "expected_npv_base": "expected_npv_merchant_$M", "expected_npv_contracted": "expected_npv_contracted_$M"}),
                                   "The forty candidates", "FORECAST; lease costs ASSUMED") + "\n" + \
            adv.format_table(pd.DataFrame(rows).round(3), "The books out of sample and your book", "FORECAST")
        result = adv.challenge(advisor, statement, opposing, context, tag="dashboard")
        st.session_state["challenge"] = result
    if "challenge" in st.session_state:
        res = st.session_state["challenge"]
        st.markdown(res["transcript"])
        if res["converge"]:
            st.success(f"CONVERGE: {res['converge']} — DISAGREE: {res['disagree']}")
    st.subheader("Override gate and the ledger")
    with st.form("override"):
        answers = {k: st.text_area(q, key=k, height=70) for k, q in adv.REASONING_QUESTIONS.items()}
        read = st.checkbox("I have read the opposing case")
        chosen = st.multiselect("The book you decide on (members)", ids, default=members)
        note = st.text_input("Note for the ledger")
        submitted = st.form_submit_button("Record my decision")
    if submitted:
        allowed, missing = adv.override_allowed(answers, opposing_case_read=read)
        xh = np.array([1 if p in chosen else 0 for p in ids])
        is_override = set(chosen) != set(members)
        if is_override and not allowed:
            st.error(f"Override refused: answer the reasoning questions first ({', '.join(missing)}).")
        else:
            tot = A_oos @ xh
            adv.ledger_append({"entry_id": f"APP-{len(ledger()) + 1:03d}", "actor": "human", "mode": "forward book", "horizon": "2025–2044", "revenue_case": case, "budget": budget, "lam": lam,
                               "technology_cap": cap, "members": ";".join(chosen), "n_members": len(chosen), "capex": float(capex.to_numpy() @ xh), "expected_npv_oos": float(tot.mean()),
                               "cvar_loss_oos": opt.cvar(-tot, LEVEL), "override": bool(is_override), "reasoning_answered": " | ".join(f"{k}: {v}" for k, v in answers.items() if v.strip()), "note": note})
            st.success(("Override recorded" if is_override else "Decision recorded (agrees with the re-solved book)") + " in results/decision_ledger.csv.")


# --- the gym -----------------------------------------------------------------------------------

elif page == "Learn from history (the gym)":
    st.title("Learn from history: pick a book as of the date, then see what happened")
    with st.spinner("building the situations as of their dates"):
        situations = load_situations()
    names = [s["name"] for s in situations]
    pick = st.selectbox("Situation", names)
    s = situations[names.index(pick)]
    st.markdown(f"**As of {s['as_of']}.** Budget **${s['budget']:,.1f}M**; {len(s['table'])} candidates. The table holds only what was knowable on that date.")
    st.dataframe(s["table"].round(2), hide_index=True)
    chosen = st.multiselect("Your book (within the budget)", list(s["table"][s["key"]]))
    cost = float(s["cost"].reindex(chosen).sum()) if chosen else 0.0
    st.write(f"Cost of your book: ${cost:,.1f}M of ${s['budget']:,.1f}M" + (" — over budget" if cost > s["budget"] else ""))
    gs = T["decision_gym_scores"][T["decision_gym_scores"]["situation"] == pick].set_index("actor")
    adv_pick = list(gs.loc["advisor", "members"].split(";")) if "advisor" in gs.index and isinstance(gs.loc["advisor", "members"], str) else None
    if st.button("Reveal the outcome and score my book", disabled=cost > s["budget"] or not chosen):
        books = {"human": chosen, "instinct": gym.instinct_book(s), "optimizer": gym.optimizer_book(s)}
        if adv_pick:
            books["advisor"] = adv_pick
        books["hindsight"] = gym.hindsight_book(s)
        table = gym.score_table(s, books)
        st.dataframe(table[["actor", "n", "cost_$M", "realized_$M", "regret_$M", "vs_instinct_$M", "members"]].round(1), hide_index=True)
        realized = s["realized"].rename("realized value $M").round(1)
        st.bar_chart(realized)
        adv.ledger_append({"entry_id": f"GYM-{len(ledger()) + 1:03d}", "actor": "human", "mode": "gym", "horizon": s["as_of"], "budget": s["budget"], "members": ";".join(chosen),
                           "n_members": len(chosen), "capex": cost, "realized_npv": float(s["realized"].reindex(chosen).sum()), "scored_on": "realized value proxy (gym)", "note": pick})
        st.success("Your pick is in the ledger; notebook 10 scores it as the human actor on its next run.")
    figure("F34_decision_gym", "F34: the gym as scored in notebook 10.")
    st.dataframe(T["decision_gym_situations"].round(1), hide_index=True)


# --- scenarios ---------------------------------------------------------------------------------

elif page == "Scenarios and risk":
    st.title("Scenarios and risk")
    figure("F30_price_scenarios", "F30: the joint price scenarios (notebook 08).")
    figure("F31_candidate_risk", "F31: each candidate's risk (notebook 08).")
    figure("F32_stresses", "F32: the named stresses (notebook 08).")
    st.subheader("Named stresses on the default book")
    st.dataframe(T["stress_tests"].assign(**{c: T["stress_tests"][c] / 1e9 for c in ("book_npv_leases", "book_npv_power", "book_npv", "change_vs_base")}).round(3), hide_index=True)
    st.subheader("Risk per candidate (primary scenarios)")
    ss = T["scenario_summary"]
    gsel = st.selectbox("Generator", sorted(ss["generator"].unique()))
    csel = st.selectbox("Revenue case ", sorted(ss["revenue_case"].unique()))
    part = ss[(ss["generator"] == gsel) & (ss["revenue_case"] == csel)].copy()
    for c in ("mean", "sd", "var", "cvar"):
        part[c] = part[c] / 1e6
    st.dataframe(part.rename(columns={"mean": "mean $M", "sd": "sd $M", "var": "VaR95 $M", "cvar": "CVaR95 $M"}).round(1), hide_index=True)


# --- candidates --------------------------------------------------------------------------------

elif page == "Candidates and the cost grid":
    st.title("Candidates, the cost grid and its impact")
    st.markdown("Every lease figure rests on the **upstream cost grid** (ASSUMED, decision #68). The grid, the tornado it drives and each project's share of the book's value, emissions and tail are shown here so a reader sees what the numbers depend on before using them.")
    st.dataframe(T["upstream_cost_grid"], hide_index=True)
    figure("F29_cost_tornado", "F29: the cost grid's impact on the default book (notebook 07).")
    st.dataframe(T["cost_sensitivity"].round(3), hide_index=True)
    st.subheader("Each project's impact")
    st.dataframe(T["project_impact"].assign(expected_npv_base=T["project_impact"]["expected_npv_base"] / 1e6, capex=T["project_impact"]["capex"] / 1e6)
                 .rename(columns={"expected_npv_base": "NPV $M", "capex": "capex $M"}).round(3), hide_index=True)
    st.subheader("The whole pool, every region")
    inv = T["investment_candidates"]
    region = st.multiselect("Region", sorted(inv["region"].dropna().unique()), default=sorted(inv["region"].dropna().unique()))
    part = inv[inv["region"].isin(region)]
    low = part[part["data_completeness"] < 1]
    if len(low):
        st.warning(f"{len(low):,} of {len(part):,} candidates in this view have a data-completeness score below 1 (thinner prices, milestones or panels). The method is the same for them; their uncertainty is wider and their constraints tighter, never silent.")
    st.dataframe(part.round(3), hide_index=True)
    figure("F28_candidates", "F28: the candidates (notebook 07).")


# --- ledger ------------------------------------------------------------------------------------

else:
    st.title("The decision ledger")
    st.markdown("Every book, proposal, override and realized outcome, in order. The gym scores the human's entries against outcomes on notebook 10's next run.")
    st.dataframe(ledger(), hide_index=True)
    st.subheader("Evaluation of the AI outputs (notebook 10)")
    st.dataframe(T["advisor_evaluation"], hide_index=True)
