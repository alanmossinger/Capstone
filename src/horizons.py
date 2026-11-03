"""The forward view: what each candidate is worth within 1, 2, 3, 5, 10 and 20 years, and the book at each horizon.

What: for every candidate the expected NPV of the cash flows that fall
within a horizon (leases: the incremental cash flows against the Arps
baseline, truncated; requests: the cost to carry, the capital at the
operation year and the operating margin up to the horizon, weighted by
the queue models' probability of operating by each year), and the
deterministic book that maximises it under the budget and the cap.
Why: docs/plan.md §14's addendum asks the advisor to propose the most likely
book at 1, 2, 3, 5, 10 and 20 years; a twenty-year NPV says nothing about
what the owner holds at year 3.
Reads / writes: nothing; notebook 10 passes the tables in and writes
``results/horizon_view.csv`` and ``results/horizon_books.csv``.
Used by: notebook 10, the dashboard's forward page; ``tests/test_horizons.py``.
"""

import numpy as np
import pandas as pd

from src import economics as ec, optimizer as opt

HORIZONS = (1, 2, 3, 5, 10, 20)
LIFE_YEARS = 20  # a power plant's operating life in the value table


def lease_within(base_oil, base_gas, wti, hh, n_wells, horizon_years, case="base"):
    """Discounted incremental cash flow of a lease redevelopment within the horizon ($)."""
    g = ec.grid_case(case)
    with_ = ec.lease_cash_flows(base_oil, base_gas, wti, hh, n_wells, case, redevelop=True)["cash_flow"].to_numpy()
    without = ec.lease_cash_flows(base_oil, base_gas, wti, hh, n_wells, case, redevelop=False)["cash_flow"].to_numpy()
    cut = min(len(with_), 12 * horizon_years)
    return ec.npv_monthly((with_ - without)[:cut], g["wacc_real"])


def power_within(expected_npv, carry_cost, capex, mw, curve, rate, horizon_years, life=LIFE_YEARS):
    """Expected discounted cash of a request within the horizon ($), from its full-life expected NPV and its operation curve.

    Notes
    -----
    The full-life expected NPV of notebook 07 is Σ_y inc_y · V · mw /
    (1 + r)^y − carry, with V the NPV per MW at the operation date; V is
    recovered from that identity, the annual operating margin m from
    V = m · A(r, life) − capex per MW, and the cash within H years when
    operation starts in year y ≤ H is −capex/(1+r)^y + m · Σ_{t=y+1}^{H}
    1/(1+r)^t, weighted by inc_y. The carry cost is paid either way. A
    request that has not operated by H is worth −carry within H.
    """
    curve = np.asarray(curve, float)
    inc = np.diff(np.concatenate([[0.0], curve]))
    years = np.arange(1, len(curve) + 1)
    disc = (1 + rate) ** years
    weight = float((inc / disc).sum())
    if weight <= 0 or mw <= 0:
        return -carry_cost
    v_per_mw = (expected_npv + carry_cost) / (mw * weight)
    capex_per_mw = capex / mw
    annuity = float((1 / (1 + rate) ** np.arange(1, life + 1)).sum())
    margin = (v_per_mw + capex_per_mw) / annuity
    total = -carry_cost
    for y, p in zip(years, inc):
        if y > horizon_years or p <= 0:
            continue
        t = np.arange(y + 1, min(horizon_years, y + life) + 1)  # the margin stops at the end of the plant's life
        total += p * mw * (-capex_per_mw / (1 + rate) ** y + margin * float((1 / (1 + rate) ** t).sum()))
    return float(total)


def horizon_view(candidates, baselines, wti, hh, curves, horizons=HORIZONS):
    """Expected NPV within each horizon for every candidate (long table), plus P(operation by horizon) for requests.

    Parameters
    ----------
    candidates : pandas.DataFrame
        ``candidate_npv.csv`` rows (``project_id``, ``sector``, ``technology``, ``n_wells``, ``expected_npv_base``, ``carry_cost``, ``capex``, ``mw``, ``wacc_real``).
    baselines : dict
        lease number -> (base_oil, base_gas).
    wti, hh : numpy.ndarray
        Flat real price paths of the baseline's length.
    curves : dict
        project_id -> cumulative P(operation by year 1 … 7) for the requests.
    """
    rows = []
    for _, r in candidates.iterrows():
        for h in horizons:
            if r["sector"] == "offshore oil and gas":
                bo, bg = baselines[r["project_id"].split("|")[1]]
                value, p_op = lease_within(bo, bg, wti, hh, int(r["n_wells"]), h), 1.0
            else:
                curve = curves.get(r["project_id"])
                if curve is None:
                    value, p_op = -r["carry_cost"], np.nan
                else:
                    value = power_within(r["expected_npv_base"], r["carry_cost"], r["capex"], r["mw"], curve, r["wacc_real"], h)
                    p_op = float(curve[min(h, len(curve)) - 1])
            rows.append({"project_id": r["project_id"], "sector": r["sector"], "technology": r["technology"], "horizon_years": h,
                         "expected_npv_within_horizon": value, "p_operation_by_horizon": p_op})
    return pd.DataFrame(rows)


def horizon_books(view, capex, groups, budget, group_cap, horizons=HORIZONS):
    """The deterministic book that maximises expected NPV within each horizon under the budget and the cap."""
    ids = list(capex.index)
    out = {}
    for h in horizons:
        v = view[view["horizon_years"] == h].set_index("project_id")["expected_npv_within_horizon"].reindex(ids).to_numpy(float)
        res = opt.solve_milp(v[None, :], capex.to_numpy(float), budget, lam=0.0, groups=groups, group_cap=group_cap)
        out[h] = pd.Series(res["x"], index=ids)
    return out
