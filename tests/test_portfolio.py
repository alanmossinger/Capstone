"""The portfolio helpers: marginals preserved by the simulation, caps respected by the choice."""

import numpy as np

from src import portfolio


def test_simulation_keeps_each_requests_probability():
    P = np.array([[0.1, 0.3], [0.5, 0.6], [0.05, 0.05]])
    mw = np.array([1.0, 10.0, 100.0])
    out = portfolio.simulate_book(P, mw, ["a", "a", "b"], rho=0.3, n_draws=20000, seed=1)
    expected = (P * mw[:, None]).sum(axis=0)  # expected MW online by year
    assert np.allclose(out.mean(axis=0), expected, rtol=0.05)
    assert (np.diff(out, axis=1) >= 0).all()  # cumulative: never fewer MW later


def test_shared_factor_widens_the_band():
    P = np.full((200, 1), 0.2)
    mw = np.ones(200)
    independent = portfolio.simulate_book(P, mw, ["g"] * 200, rho=0.0, n_draws=4000, seed=2)
    shared = portfolio.simulate_book(P, mw, ["g"] * 200, rho=0.4, n_draws=4000, seed=2)
    assert shared.std() > 1.5 * independent.std()


def test_choice_respects_budget_and_caps():
    score = np.array([10.0, 9.0, 8.0, 7.0, 1.0])
    cost = np.array([5.0, 5.0, 5.0, 5.0, 1.0])
    region = np.array(["A", "A", "A", "B", "B"])
    chosen = portfolio.choose_book(score, cost, budget=10.0, caps=[(region, 0.5)])
    assert cost[chosen].sum() <= 10.0
    assert cost[chosen & (region == "A")].sum() <= 5.0
    assert chosen[0] and chosen[3]  # the best of each region


def test_rho_is_zero_without_overdispersion():
    rho, phi = portfolio.estimate_rho(observed=[0.10, 0.11, 0.09, 0.10], predicted=[0.10] * 4, n=[1000] * 4)
    assert rho < 0.05
