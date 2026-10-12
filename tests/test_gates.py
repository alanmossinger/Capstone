"""The gate rule, the outcome simulator, the expected shortfall and the greedy book behave as documented."""

import numpy as np

from src import portfolio


def test_gate_decision_orders_the_three_classes():
    out = portfolio.gate_decision(p_low=[0.3, 0.05, 0.2, 0.2], p_high=[0.3, 0.06, 0.2, 0.2], p_floor=0.1,
                                  ev_low=[5, 5, 5, -5], ev_base=[10, 10, 2, -2], ev_high=[20, 20, 4, -1],
                                  c_low=[1, 1, 1, 1], c_base=[2, 2, 2, 2], c_high=[3, 3, 3, 3], h=3.0)
    assert list(out) == ["invest", "exit", "hold", "exit"]


def test_simulated_years_keep_the_marginals_and_apply_the_level_factor():
    P = np.tile(np.array([[0.1, 0.2, 0.3]]), (200, 1))
    years = portfolio.simulate_operation_years(P, np.zeros(200), rho=0.0, n_draws=4000, seed=1)
    by3 = (years > 0).mean()
    assert abs(by3 - 0.3) < 0.02
    assert abs(((years == 1).mean()) - 0.1) < 0.02
    half = portfolio.simulate_operation_years(P, np.zeros(200), rho=0.0, n_draws=4000, seed=1, level_factors=np.full(4000, 0.5))
    assert abs((half > 0).mean() - 0.15) < 0.02


def test_expected_shortfall_is_the_mean_of_the_worst_tail():
    x = np.arange(100, dtype=float)
    assert portfolio.expected_shortfall(x, 0.95) == np.mean([0, 1, 2, 3, 4])


def test_greedy_book_respects_the_budget_and_prefers_the_sure_thing():
    rng = np.random.default_rng(0)
    sure = np.full((1000, 1), 10.0)
    risky = np.where(rng.uniform(size=(1000, 1)) < 0.5, 40.0, -30.0)  # same mean, heavy loss tail
    draws = np.hstack([sure, risky, np.full((1000, 1), -1.0)])
    chosen = portfolio.greedy_risk_adjusted(draws, cost=[5.0, 5.0, 5.0], budget=5.0, lam=1.0)
    assert chosen.tolist() == [True, False, False]
