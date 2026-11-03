"""The decision gym: documented past situations, four actors, one score each against the realized outcome.

What: situations built as of their date with no hindsight — the queue
requests of a region and cohort at entry and at the two-year gate (from
``decision_pack.csv``), the lease candidates at the start of three oil-price
regimes (2014, 2020, 2022) and a 2018 budget cut — each with a budget, a
table of what was knowable, and the realized value revealed afterwards.
Since the 17 October audit (G1) the lease rooms are rebuilt as of their
date: the leases producing then, baselines fitted on the public months,
scenarios from the history before the date, outcomes from the observed
production. Actors pick a book under the same budget: *instinct* (top-N
expected NPV), *instinct per dollar* (NPV per dollar of cost), *nothing*
(spend nothing), the *optimizer* (the registered gate rule for requests, the
risk-aware MILP for leases), the *advisor* (the LLM, from the same table)
and the *human* (the dashboard's ledger). Each book is scored by the
realized value and its regret against the hindsight-best book.
Why: "the AI defies the human instinct" is a claim the gym measures;
docs/plan.md §14.10 mode 3 and the "learn from history" addendum.
Reads: nothing on import; the notebook passes the tables in.
Writes: nothing; notebook 10 writes ``decision_gym_scores.csv``.
Used by: notebook 10, the dashboard's gym page; ``tests/test_gym.py``.
"""

import numpy as np
import pandas as pd

from src import economics as ec, optimizer as opt, scenarios as sc

ENTRY_COLUMNS = ["project_key", "tech", "mw", "p5_lookup", "p5_model_repaired", "cost_to_next_gate_base_$M", "breakeven_price_$MWh", "expected_npv_entry_base_contracted_$M"]
GATE_COLUMNS = ["project_key", "tech", "mw", "p3_landmark", "cost_to_next_gate_base_$M", "breakeven_price_$MWh", "expected_npv_2y_base_contracted_$M"]
HIDDEN = ["status_end_2024", "operated_within_3y_of_gate", "npv_per_mw_if_built_year3_contracted_$M", "decision_entry_contracted", "decision_2y_contracted"]
REGIMES = {  # name -> start month of the realized price path the lease candidates are scored on
    "oil collapse from June 2014": "2014-06-01",
    "the 2020 collapse from January 2020": "2020-01-01",
    "the 2022 spike from March 2022": "2022-03-01",
}


# --- queue situations ---------------------------------------------------------------------------

FUND_VERDICT = {"entry": "invest", "2y": "accelerate"}  # the gate rule's funding verdict at each gate (notebook 09 part B)


def queue_situation(pack, region, cohort, gate="entry", n_show=15, budget_share=0.4, budget_cut=0.0, seed=2020):
    """One situation: ``n_show`` requests of a region and cohort drawn at random, as of entry or the two-year gate.

    Returns
    -------
    dict or None
        ``name``, ``as_of``, ``table`` (as-of columns only), ``budget``
        ($M), ``realized`` (Series by project_key, $M), ``optimizer_rule``
        (the registered gate verdicts, hidden from the advisor), or None
        when fewer than five requests qualify.

    Notes
    -----
    Realized value of a request = the modeled value per MW if built in
    year 3 times its MW when it reached operation (within five years of
    entry, or within three years of the gate), minus the cost to the next
    gate either way: the outcome is OBSERVED, the value per MW DERIVED
    from the value table, so the score is a proxy and is labelled so.
    """
    rows = pack[(pack["region"] == region) & (pack["q_year"] == cohort)]
    if gate == "2y":
        rows = rows[rows["in_pool_2y"]]
    rows = rows.sample(n=min(n_show, len(rows)), random_state=seed).sort_values("mw", ascending=False)  # a random draw: the largest requests fail most, which would stack the rooms toward abstention
    if len(rows) < 5:
        return None
    cost = rows["cost_to_next_gate_base_$M"].to_numpy(float)
    if gate == "entry":
        built = (rows["status_end_2024"] == "operated within 5 years").to_numpy()
        table = rows[ENTRY_COLUMNS].rename(columns={"expected_npv_entry_base_contracted_$M": "expected_npv_$M"})
        rule = rows["decision_entry_contracted"].to_numpy()
        as_of = f"the end of {cohort}, at queue entry"
    else:
        built = rows["operated_within_3y_of_gate"].to_numpy().astype(bool)
        table = rows[GATE_COLUMNS].rename(columns={"expected_npv_2y_base_contracted_$M": "expected_npv_$M"})
        rule = rows["decision_2y_contracted"].to_numpy()
        as_of = f"the end of {cohort + 2}, two years after queue entry"
    realized = np.where(built, rows["npv_per_mw_if_built_year3_contracted_$M"].to_numpy(float) * rows["mw"].to_numpy(float), 0.0) - cost
    budget = float(cost.sum() * budget_share * (1 - budget_cut))
    name = f"{region} {cohort} {'entry' if gate == 'entry' else '2-year gate'}" + (f", budget −{budget_cut:.0%}" if budget_cut else "")
    return {"name": name, "kind": "queue", "as_of": as_of, "region": region, "cohort": cohort, "gate": gate, "table": table.reset_index(drop=True),
            "budget": budget, "cost": pd.Series(cost, index=rows["project_key"].to_numpy()), "realized": pd.Series(realized, index=rows["project_key"].to_numpy()),
            "optimizer_rule": pd.Series(rule, index=rows["project_key"].to_numpy()), "key": "project_key", "value_col": "expected_npv_$M", "cost_col": "cost_to_next_gate_base_$M"}


# --- lease regimes ------------------------------------------------------------------------------

def real_price_path(nominal, cpi, start, months, base_year=2024):
    """A real-dollar monthly path from ``start``: the observed months, then the last observed value held flat.

    Notes
    -----
    The CPI table starts in 2016; months before it are deflated with the
    January 2016 index (the 2014–2015 error is under 2% and stated).
    """
    idx = cpi.set_index("month")["cpi_u"]
    base = idx[idx.index.year == base_year].mean()
    series = nominal.set_index("month").iloc[:, 0]
    observed = series.loc[start:]
    deflator = idx.reindex(observed.index).ffill().bfill()
    real = (observed * base / deflator).to_numpy(float)
    if len(real) >= months:
        return real[:months]
    return np.concatenate([real, np.full(months - len(real), real[-1])])


def real_series(nominal, cpi, base_year=2024):
    """The whole nominal monthly series in ``base_year`` dollars (months before the CPI table use its first index)."""
    idx = cpi.set_index("month")["cpi_u"]
    base = idx[idx.index.year == base_year].mean()
    series = nominal.set_index("month").iloc[:, 0]
    deflator = idx.reindex(series.index).ffill().bfill()
    return series * base / deflator


def lease_pool_as_of(monthly, start, n=20, lag_months=3, min_producing_months=24, trailing_months=12):
    """The ``n`` leases with the most output in the public months before ``start``, and their producing wells then.

    Parameters
    ----------
    monthly : pandas.DataFrame
        BSEE lease-months: ``lease_number``, ``month``, ``oil_bbl``, ``gas_mcf``, ``n_producing``, ``producing``.
    start : str or pandas.Timestamp
        The room's date.
    n : int
        Leases in the room.
    lag_months : int
        BSEE's publication lag (``config.RELEASE_LAGS``): months on or after
        ``start`` − lag were not public yet.
    min_producing_months : int
        Producing months a lease needs before the cutoff (the file starts in
        2010, so a 2014 room cannot ask for the sixty of notebook 07).
    trailing_months : int
        Months of output the ranking sums.

    Returns
    -------
    pandas.DataFrame
        ``lease_number``, ``boe_trailing``, ``n_wells``, sorted by output.

    Notes
    -----
    Report v6 put the twenty leases chosen on 2024 output into the 2014, 2020
    and 2022 rooms, eight of which were not producing in mid-2014 (audit G1).
    """
    cutoff = pd.Timestamp(start) - pd.DateOffset(months=lag_months)
    known = monthly[monthly["month"] < cutoff]
    producing_months = known[known["producing"]].groupby("lease_number").size()
    eligible = producing_months[producing_months >= min_producing_months].index
    recent = known[(known["month"] >= cutoff - pd.DateOffset(months=trailing_months)) & known["lease_number"].isin(eligible)]
    boe = (recent["oil_bbl"] + recent["gas_mcf"] * ec.BOE_PER_MCF).groupby(recent["lease_number"]).sum()
    top = boe[boe > 0].sort_values(ascending=False).head(n)
    wells = recent[recent["lease_number"].isin(top.index)].groupby("lease_number")["n_producing"].max().clip(lower=1).astype(int)
    return pd.DataFrame({"lease_number": top.index, "boe_trailing": top.to_numpy(), "n_wells": wells.reindex(top.index).to_numpy()})


def lease_situation(name, start, monthly, wti_nominal, hh_nominal, cpi, months=240, n=20, lag_months=3, history_months=84,
                    budget_share=0.4, n_scen=300, seed=2020, lam=1.0, max_change=sc.MAX_MONTHLY_LOG_CHANGE):
    """One regime, rebuilt as of its date: the leases, their baselines and the optimizer's scenarios use only what was public then.

    Parameters
    ----------
    name, start : str
        Room name and date.
    monthly : pandas.DataFrame
        BSEE lease-months (all leases, all months).
    wti_nominal, hh_nominal : pandas.DataFrame
        ``month`` and the nominal price (EIA xls files).
    cpi : pandas.DataFrame
        ``month``, ``cpi_u``.
    months : int
        Valuation horizon.
    n, lag_months : int
        As in ``lease_pool_as_of``.
    history_months : int
        Months of price history before ``start`` the scenarios resample.

    Returns
    -------
    dict
        The situation, as ``queue_situation`` returns it.

    Notes
    -----
    As of the date: the pool and wells (``lease_pool_as_of``); each baseline
    fitted on the public months only (``economics.lease_baseline``, with the
    decline floor); the real price at the start month held flat for the
    expected NPV; the optimizer's scenarios resample the ``history_months``
    real monthly changes before the date and revert to their geometric mean
    — v6 reverted to the mean of the realized future path (audit G1).
    Realized: the uplift on the lease's *observed* production after the date
    (a baseline fitted on the whole file extends it past the end of the
    file), at the observed real prices. Months before 2016 are deflated with
    the first CPI index of the table, so their real changes are nominal
    changes (stated).
    """
    start = pd.Timestamp(start)
    cutoff = start - pd.DateOffset(months=lag_months)
    pool = lease_pool_as_of(monthly, start, n, lag_months)
    sub = monthly[monthly["lease_number"].isin(pool["lease_number"])]
    oil = sub.pivot(index="lease_number", columns="month", values="oil_bbl").fillna(0)
    gas = sub.pivot(index="lease_number", columns="month", values="gas_mcf").fillna(0)
    before = oil.columns < cutoff
    after = oil.columns >= start
    wti_path = real_price_path(wti_nominal, cpi, start, months)
    hh_path = real_price_path(hh_nominal, cpi, start, months)
    flat_w, flat_h = np.full(months, wti_path[0]), np.full(months, hh_path[0])
    real_w, real_h = real_series(wti_nominal, cpi), real_series(hh_nominal, cpi)
    hist = pd.concat([real_w, real_h], axis=1).loc[start - pd.DateOffset(months=history_months):start - pd.DateOffset(months=1)].dropna()
    changes = np.clip(np.diff(np.log(hist.to_numpy(float)), axis=0), -max_change, max_change)
    long_run = np.exp(np.log(hist.to_numpy(float)).mean(axis=0))
    shocks = sc.block_bootstrap_paths(changes, n_scen, months, block=12, seed=seed)
    prices = sc.mean_reverting_prices(shocks, [wti_path[0], hh_path[0]], long_run)
    g = ec.grid_case("base")
    rows, realized = [], []
    npv_scen = np.empty((n_scen, len(pool)))
    for j, r in pool.reset_index(drop=True).iterrows():
        lid, wells = r["lease_number"], int(r["n_wells"])
        bo, bg, _, _ = ec.lease_baseline(oil.loc[lid].to_numpy()[before], gas.loc[lid].to_numpy()[before], months=months)
        asof = ec.incremental_npv(bo, bg, flat_w, flat_h, wells, "base") / 1e6
        rows.append({"project_id": f"LEASE|{lid}", "n_wells": wells, "boe_trailing_12m": float(r["boe_trailing"]),
                     "capex_$M": g["workover_cost_per_well_usd"] * wells / 1e6, "breakeven_wti_$bbl": ec.breakeven_wti(bo, bg, flat_h, wells, "base"),
                     "expected_npv_$M": asof})
        obs_o, obs_g = oil.loc[lid].to_numpy()[after], gas.loc[lid].to_numpy()[after]
        tail_o, tail_g, _, _ = ec.lease_baseline(oil.loc[lid].to_numpy(), gas.loc[lid].to_numpy(), months=max(months - len(obs_o), 1))
        real_o = np.concatenate([obs_o, tail_o])[:months]
        real_g = np.concatenate([obs_g, tail_g])[:months]
        realized.append(ec.incremental_npv(real_o, real_g, wti_path, hh_path, wells, "base") / 1e6)
        for s in range(n_scen):
            npv_scen[s, j] = ec.incremental_npv(bo, bg, prices[s, :, 0], prices[s, :, 1], wells, "base") / 1e6
    table = pd.DataFrame(rows)
    ids = table["project_id"].to_numpy()
    capex = table["capex_$M"].to_numpy(float)
    budget = float(capex.sum() * budget_share)
    out = opt.solve_milp(npv_scen, capex, budget, lam=lam)
    return {"name": name, "kind": "lease", "as_of": f"{start:%B %Y}, WTI at ${wti_path[0]:.0f} a barrel (2024 dollars)", "start": start, "cutoff": cutoff,
            "table": table, "budget": budget, "cost": pd.Series(capex, index=ids), "realized": pd.Series(realized, index=ids),
            "optimizer_book": pd.Series(out["x"], index=ids), "wti_path": wti_path, "hh_path": hh_path, "key": "project_id",
            "value_col": "expected_npv_$M", "cost_col": "capex_$M"}


# --- actors and scores --------------------------------------------------------------------------

def instinct_book(situation):
    """Top-N by the as-of expected NPV within the budget (positive NPV only)."""
    t = situation["table"]
    x = opt.top_n_by_npv(t[situation["value_col"]].to_numpy(float), t[situation["cost_col"]].to_numpy(float), situation["budget"])
    return list(t[situation["key"]][x == 1])


def ratio_instinct_book(situation):
    """Instinct that ranks by expected NPV per dollar of cost within the budget (positive NPV only): the analyst who knows the budget binds."""
    t = situation["table"]
    value, cost = t[situation["value_col"]].to_numpy(float), t[situation["cost_col"]].to_numpy(float)
    order = np.argsort(-(value / np.where(cost > 0, cost, np.nan)))
    chosen, spent = [], 0.0
    for i in order:
        if value[i] > 0 and spent + cost[i] <= situation["budget"]:
            chosen.append(t[situation["key"]].iloc[i])
            spent += cost[i]
    return chosen


def optimizer_book(situation):
    """The registered rule: the gate's funding verdict ('invest' at entry, 'accelerate' two years in) filled by NPV per dollar (requests); the risk-aware MILP (leases)."""
    t = situation["table"]
    if situation["kind"] == "lease":
        return list(situation["optimizer_book"].index[situation["optimizer_book"].to_numpy() == 1])
    keys = t[situation["key"]].to_numpy()
    value, cost = t[situation["value_col"]].to_numpy(float), t[situation["cost_col"]].to_numpy(float)
    invest = situation["optimizer_rule"].reindex(keys).to_numpy() == FUND_VERDICT[situation["gate"]]
    order = np.argsort(-(value / np.where(cost > 0, cost, np.nan)))
    chosen, spent = [], 0.0
    for i in order:
        if invest[i] and value[i] > 0 and spent + cost[i] <= situation["budget"]:
            chosen.append(keys[i])
            spent += cost[i]
    return chosen


def hindsight_book(situation):
    """The best book with the outcomes known: the exact knapsack on realized value within the budget (an upper bound, not an actor)."""
    keys = situation["realized"].index.to_numpy()
    realized = situation["realized"].to_numpy(float)
    x = opt.solve_milp(realized[None, :], situation["cost"].reindex(keys).to_numpy(float), situation["budget"], lam=0.0)["x"]
    return list(keys[x == 1])


def validate_pick(situation, members):
    """Keep the advisor's members that exist and fit the budget in the order given; report what was dropped."""
    keys = set(situation["table"][situation["key"]])
    kept, spent, dropped = [], 0.0, []
    for m in members or []:
        if m in keys and m not in kept and spent + float(situation["cost"][m]) <= situation["budget"] + 1e-9:
            kept.append(m)
            spent += float(situation["cost"][m])
        else:
            dropped.append(m)
    return kept, dropped


def score(situation, members):
    """Realized value, cost and size of a book in a situation ($M)."""
    members = list(members)
    realized = float(situation["realized"].reindex(members).sum()) if members else 0.0
    cost = float(situation["cost"].reindex(members).sum()) if members else 0.0
    return {"realized_$M": realized, "cost_$M": cost, "n": len(members)}


def score_table(situation, books):
    """One row per actor: realized value, regret against hindsight, difference to instinct."""
    best = score(situation, hindsight_book(situation))["realized_$M"]
    instinct = score(situation, books["instinct"])["realized_$M"] if "instinct" in books else np.nan
    rows = []
    for actor, members in books.items():
        s = score(situation, members)
        rows.append({"situation": situation["name"], "kind": situation["kind"], "as_of": situation["as_of"], "actor": actor, "n": s["n"], "cost_$M": s["cost_$M"],
                     "budget_$M": situation["budget"], "realized_$M": s["realized_$M"], "hindsight_best_$M": best, "regret_$M": best - s["realized_$M"],
                     "vs_instinct_$M": s["realized_$M"] - instinct, "members": ";".join(members)})
    return pd.DataFrame(rows)
