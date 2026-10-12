"""The MILP respects the budget and the caps, D is never worse than C on its own objective, the comparators and the bootstrap behave."""

import numpy as np

from src import optimizer as opt


def _scenarios(seed=0, S=300, n=8):
    rng = np.random.default_rng(seed)
    mu = np.array([5, 4, 3, 2, 1, 0.5, -1, -2], float)[:n]
    sd = np.array([1, 8, 1, 6, 1, 1, 1, 1], float)[:n]  # candidates 2 and 4 are the risky ones
    return mu[None, :] + sd[None, :] * rng.normal(size=(S, n)), mu


def test_milp_respects_budget_and_group_cap_and_exclusivity():
    A, mu = _scenarios()
    capex = np.ones(8) * 10.0
    groups = np.array(["a", "a", "b", "b", "c", "c", "d", "d"])
    out = opt.solve_milp(A, capex, budget=40.0, lam=1.0, groups=groups, group_cap=0.5, exclusive=[(0, 2)])
    x = out["x"]
    assert out["capex_used"] <= 40.0 + 1e-6
    for g in np.unique(groups):
        assert capex[(groups == g)] @ x[groups == g] <= 0.5 * 40.0 + 1e-6
    assert x[0] + x[2] <= 1 and out["status"]


def test_risk_aware_prefers_the_steady_candidate_and_is_not_worse_than_deterministic_on_its_objective():
    A, mu = _scenarios()
    capex = np.ones(8) * 10.0
    c = opt.solve_milp(A, capex, budget=30.0, lam=0.0)
    d = opt.solve_milp(A, capex, budget=30.0, lam=2.0)
    assert c["expected_npv"] >= d["expected_npv"] - 1e-6  # C maximises expected NPV
    assert opt.book_metric(A, d["x"], lam=2.0) >= opt.book_metric(A, c["x"], lam=2.0) - 1e-6  # D maximises the risk-adjusted metric
    assert d["x"][2] == 1 and d["x"][1] == 0  # the steady candidate 3 over the risky 4


def test_comparators_and_jaccard():
    A, mu = _scenarios()
    capex = np.ones(8) * 10.0
    a = opt.top_n_by_npv(mu, capex, budget=30.0)
    assert a.sum() == 3 and a[[0, 1, 2]].all()
    b = opt.equal_capital_by_sector(mu, capex, np.array(["x"] * 4 + ["y"] * 4), budget=40.0)
    assert b[:4].sum() == 2 and b[4:].sum() == 2  # two per sector, positive NPV only
    assert opt.jaccard(a, a) == 1.0 and opt.jaccard(a, np.zeros(8)) == 0.0


def test_paired_bootstrap_passes_for_a_clearly_better_book():
    A, mu = _scenarios()
    better = np.array([1, 0, 1, 0, 1, 0, 0, 0])
    worse = np.array([0, 1, 0, 1, 0, 0, 1, 1])
    out = opt.paired_scenario_bootstrap(A, better, worse, lam=1.0, n_boot=300)
    assert out["pass"] and out["low"] > 0
    out2 = opt.score_books({"better": better, "worse": worse}, A)
    assert out2.loc[0, "metric"] > out2.loc[1, "metric"]
