"""The decision gym: documented past situations, four actors, one score each against the realized outcome.

What: situations built as of their date with no hindsight — the queue
requests of a region and cohort at entry and at the two-year gate (from
``decision_pack.csv``), the lease candidates at the start of three oil-price
regimes (2014, 2020, 2022) and a 2018 budget cut — each with a budget, a
table of what was knowable, and the realized value revealed afterwards.
Four actors pick a book under the same budget: *instinct* (top-N expected
NPV), the *optimizer* (the registered gate rule for requests, the
risk-aware MILP for leases), the *advisor* (the LLM, from the same table)
and the *human* (the dashboard's ledger). Each book is scored by the
realized value and its regret against the hindsight-best book.
Why: "the AI defies the human instinct" is a claim the gym measures;
PLAN.md §14.10 mode 3 and the "learn from history" addendum.
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

def queue_situation(pack, region, cohort, gate="entry", n_show=15, budget_share=0.4, budget_cut=0.0):
    """One situation: the ``n_show`` largest requests of a region and cohort, as of entry or the two-year gate.

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
    rows = rows.sort_values("mw", ascending=False).head(n_show)
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


def lease_situation(name, start, leases, baselines, wti_nominal, hh_nominal, cpi, changes, months=240, budget_share=0.4, n_scen=300, seed=2020, lam=1.0):
    """One regime: the lease candidates valued flat at the regime's start price, scored on the realized path.

    Parameters
    ----------
    leases : pandas.DataFrame
        ``project_id``, ``n_wells``, ``capex`` and ``breakeven_wti_base`` of the lease candidates.
    baselines : dict
        ``lease_number`` -> (base_oil, base_gas) Arps baselines of ``months`` months.
    wti_nominal, hh_nominal : pandas.DataFrame
        ``month`` and the nominal price (EIA xls files).
    cpi : pandas.DataFrame
        ``month``, ``cpi_u``.
    changes : numpy.ndarray
        Historical joint monthly log changes for the optimizer's scenarios (WTI, Henry Hub, …).

    Notes
    -----
    As-of valuation: the real price at the start month held flat (what a
    desk would have used). Realized: the observed real path from the start
    month, then the last observed value held. The optimizer draws
    ``n_scen`` mean-reverting scenarios from the start level toward the
    path's own mean, with the 2018–2024 shock history (a mild hindsight for
    2014, stated in the notebook), and solves the risk-aware MILP.
    """
    wti_path = real_price_path(wti_nominal, cpi, start, months)
    hh_path = real_price_path(hh_nominal, cpi, start, months)
    flat_w, flat_h = np.full(months, wti_path[0]), np.full(months, hh_path[0])
    rows, realized, npv_scen = [], [], None
    shocks = sc.block_bootstrap_paths(changes[:, :2], n_scen, months, block=12, seed=seed)
    long_run = np.array([wti_path.mean(), hh_path.mean()])
    prices = sc.mean_reverting_prices(shocks, [wti_path[0], hh_path[0]], long_run)
    npv_scen = np.empty((n_scen, len(leases)))
    for j, r in leases.reset_index(drop=True).iterrows():
        bo, bg = baselines[r["project_id"].split("|")[1]]
        wells = int(r["n_wells"])
        asof = ec.incremental_npv(bo, bg, flat_w, flat_h, wells, "base") / 1e6
        rows.append({"project_id": r["project_id"], "n_wells": wells, "capex_$M": r["capex"] / 1e6, "breakeven_wti_$bbl": r["breakeven_wti_base"], "expected_npv_$M": asof})
        realized.append(ec.incremental_npv(bo, bg, wti_path, hh_path, wells, "base") / 1e6)
        for s in range(n_scen):
            npv_scen[s, j] = ec.incremental_npv(bo, bg, prices[s, :, 0], prices[s, :, 1], wells, "base") / 1e6
    table = pd.DataFrame(rows)
    ids = table["project_id"].to_numpy()
    capex = table["capex_$M"].to_numpy(float)
    budget = float(capex.sum() * budget_share)
    out = opt.solve_milp(npv_scen, capex, budget, lam=lam)
    return {"name": name, "kind": "lease", "as_of": f"{pd.Timestamp(start):%B %Y}, WTI at ${wti_path[0]:.0f} a barrel (2024 dollars)", "start": start, "table": table,
            "budget": budget, "cost": pd.Series(capex, index=ids), "realized": pd.Series(realized, index=ids), "optimizer_book": pd.Series(out["x"], index=ids),
            "wti_path": wti_path, "hh_path": hh_path, "key": "project_id", "value_col": "expected_npv_$M", "cost_col": "capex_$M"}


# --- actors and scores --------------------------------------------------------------------------

def instinct_book(situation):
    """Top-N by the as-of expected NPV within the budget (positive NPV only)."""
    t = situation["table"]
    x = opt.top_n_by_npv(t[situation["value_col"]].to_numpy(float), t[situation["cost_col"]].to_numpy(float), situation["budget"])
    return list(t[situation["key"]][x == 1])


def optimizer_book(situation):
    """The registered rule: the gate verdict 'invest' filled by NPV per dollar (requests); the risk-aware MILP (leases)."""
    t = situation["table"]
    if situation["kind"] == "lease":
        return list(situation["optimizer_book"].index[situation["optimizer_book"].to_numpy() == 1])
    keys = t[situation["key"]].to_numpy()
    value, cost = t[situation["value_col"]].to_numpy(float), t[situation["cost_col"]].to_numpy(float)
    invest = situation["optimizer_rule"].reindex(keys).to_numpy() == "invest"
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
