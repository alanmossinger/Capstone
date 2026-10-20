"""The robustness checks: held-out against selection scores, re-selection, capital calls, funding-or-forfeit and tail dependence."""

import numpy as np

from src import robustness as rb


def test_in_vs_out_reports_the_change_between_the_two_sets():
    A = np.array([[1.0, 2.0], [3.0, 4.0]])
    t = rb.in_vs_out({"both": np.array([1, 1])}, A, A - 1.0, lam=0.0)
    assert np.isclose(t.loc[0, "mean_in"], 5.0) and np.isclose(t.loc[0, "mean_change"], -2.0)


def test_reselection_returns_one_row_per_resample_and_frequencies_in_zero_one():
    rng = np.random.default_rng(0)
    A = rng.normal(1.0, 1.0, size=(200, 4))
    charge = np.ones(4)
    rows, freq = rb.reselect(A, A, charge, 2.0, np.array(["a", "a", "b", "b"]), 1.0, np.array([1, 1, 0, 0]), n=3)
    assert len(rows) == 3 and ((freq >= 0) & (freq <= 1)).all()


def test_capital_calls_compare_the_drawn_capital_with_the_expected_draw():
    op_year = np.array([[1, 0], [0, 0], [2, 3], [0, 1]])
    out = rb.capital_calls(op_year, np.array([100.0, 50.0]), np.array([1, 1]), np.array([0.5, 0.5]))
    assert out["reserve"] == 75.0
    assert np.allclose(out["drawn"], [100.0, 0.0, 150.0, 50.0]) and out["p_over"] == 0.5


def test_an_unlimited_line_gives_the_static_book_and_no_line_forfeits():
    A = np.array([[10.0, 5.0], [-1.0, -2.0]])  # scenario 0: both built; scenario 1: neither (−carry)
    op_year = np.array([[1, 1], [0, 0]])
    capex, carry = np.array([100.0, 100.0]), np.array([1.0, 2.0])
    static = rb.funding_or_forfeit(A, op_year, capex, carry, np.array([1, 1]), reserve=0.0, line=1e12, priority=np.array([2.0, 1.0]))
    assert np.allclose(static, A.sum(axis=1))
    one = rb.funding_or_forfeit(A, op_year, capex, carry, np.array([1, 1]), reserve=100.0, line=0.0, priority=np.array([2.0, 1.0]))
    assert np.isclose(one[0], 10.0 - 2.0)  # the first in priority funded, the other forfeits its carry
    other = rb.funding_or_forfeit(A, op_year, capex, carry, np.array([1, 1]), reserve=100.0, line=0.0, priority=np.array([1.0, 2.0]))
    assert np.isclose(other[0], 5.0 - 1.0)  # the order is the priority given in advance, not the scenario's outcome


def test_tail_dependence_finds_value_concentrated_in_few_scenarios():
    v = np.r_[np.full(95, -1.0), np.full(5, 100.0)]
    d = rb.tail_dependence(v)
    assert d["p_loss"] == 0.95 and d["share_from_top"] > 1.0  # the best 5% earn more than the total: the rest lose
