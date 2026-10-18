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


def test_capped_comparators_stay_within_budget_and_cap_on_random_instances():
    rng = np.random.default_rng(7)
    groups = np.array(["lease"] * 10 + ["gas"] * 4 + ["wind"] * 4)
    for _ in range(50):
        mu = rng.normal(2.0, 2.0, size=18)
        capex = rng.uniform(1.0, 10.0, size=18)
        budget = 0.4 * capex.sum()
        for x in (opt.top_n_by_npv(mu, capex, budget, groups=groups, group_cap=0.4),
                  opt.equal_capital_by_sector(mu, capex, np.where(groups == "lease", "oil", "power"), budget, groups=groups, group_cap=0.4)):
            assert opt.violations(x, capex, budget, groups, 0.4) == {}


def test_without_the_cap_top_n_can_breach_it_and_violations_reports_it():
    mu = np.array([9.0, 8.0, 7.0, 1.0])
    capex = np.array([10.0, 10.0, 10.0, 10.0])
    groups = np.array(["lease", "lease", "lease", "wind"])
    x = opt.top_n_by_npv(mu, capex, budget=30.0)  # the comparator as first run: three leases, 100% in one group
    assert set(opt.violations(x, capex, 30.0, groups, 0.4)) == {"lease"}
    capped = opt.top_n_by_npv(mu, capex, budget=30.0, groups=groups, group_cap=0.4)
    assert capped.tolist() == [1, 0, 0, 1]  # one lease (10 ≤ 12), the next lease would breach, wind fills


def test_cvar_averages_exactly_the_worst_five_percent_of_2000():
    losses = np.arange(2000, dtype=float)  # the worst 100 are 1900 … 1999
    assert opt.tail_count(2000, 0.95) == 100
    assert opt.cvar(losses, 0.95) == np.mean(np.arange(1900, 2000))


def test_cvar_equals_the_ru_objective_at_the_optimum():
    A, mu = _scenarios(S=400)
    capex = np.ones(8) * 10.0
    out = opt.solve_milp(A, capex, budget=30.0, lam=1.0)
    assert abs(out["cvar_loss"] - opt.cvar(-(A @ out["x"]), 0.95)) < 1e-9


def test_one_cvar_definition_across_modules():
    from src import portfolio, scenarios
    npv = np.random.default_rng(3).normal(10.0, 5.0, size=2000)
    assert abs(scenarios.risk_measures(npv)["cvar"] - (-opt.cvar(-npv, 0.95))) < 1e-9
    assert abs(portfolio.expected_shortfall(npv, 0.95) - (-opt.cvar(-npv, 0.95))) < 1e-9


def test_cvar_limit_binds_and_an_impossible_limit_is_reported():
    A, mu = _scenarios(S=400)
    capex = np.ones(8) * 10.0
    free = opt.solve_milp(A, capex, budget=30.0, lam=0.0)
    limit = free["cvar_loss"] - 1.0  # stricter than the free book's tail
    capped = opt.solve_milp(A, capex, budget=30.0, lam=0.0, cvar_cap=limit * 1e6 / 1e6)
    assert capped["cvar_loss"] <= limit + 1e-6
    assert capped["expected_npv"] <= free["expected_npv"] + 1e-9  # a tighter tail costs expected value
    try:
        opt.solve_milp(A + 1000.0, capex, budget=30.0, lam=0.0, cvar_cap=-1e12, forced_in=[0])
        assert False, "an impossible limit must raise"
    except opt.InfeasibleBook:
        pass


def test_forced_members_are_respected():
    A, mu = _scenarios()
    capex = np.ones(8) * 10.0
    out = opt.solve_milp(A, capex, budget=30.0, lam=0.0, forced_in=[6], forced_out=[0])
    assert out["x"][6] == 1 and out["x"][0] == 0


def test_book_diff_names_entries_exits_and_the_changes():
    A, mu = _scenarios()
    ids = [f"c{i}" for i in range(8)]
    groups = np.array(["a"] * 4 + ["b"] * 4)
    d = opt.book_diff([1, 1, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0, 0], ids, A, np.ones(8), groups)
    assert d["entered"] == ["c2", "c4"] and d["left"] == ["c1"]
    assert abs(d["change"]["charge"] - 1.0) < 1e-12
    assert d["old"]["hhi"] == 1.0 and abs(d["new"]["hhi"] - (2 / 3) ** 2 - (1 / 3) ** 2) < 1e-12
