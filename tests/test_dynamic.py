"""The staged policy drops a request the signal condemns, redeploys its reserve, and never does worse than static when the signal is perfect."""

import numpy as np

from src import dynamic as dy


def _case(S=2000, seed=0):
    rng = np.random.default_rng(seed)
    prices = np.exp(rng.normal(0, 0.1, size=(S, 240, 3))) * np.array([70.0, 2.5, 30.0])
    built = rng.random(S) < 0.3
    op_year = np.where(built, 4, 0)[:, None]  # one request, operating in year 4 when built
    A = np.column_stack([np.full(S, 5e7), np.where(built, 2e8, -3e6)])  # a lease worth 50, a request worth 200 if built, −3 (its carry) if not
    A_def = np.full((S, 1), 4e7)  # the lease, deferred, still worth 40
    return prices, built, op_year, A, A_def


def test_a_perfect_signal_drops_only_the_losers_and_keeps_the_winners():
    prices, built, op_year, A, A_def = _case()
    signal = built[:, None]
    lease_mask = np.array([True, False])
    out = dy.staged_policy([1, 1], A, A_def, carry=np.array([3e6]), charge=np.array([5e7, 6e7]), budget=1.2e8, lease_mask=lease_mask,
                           op_year=op_year, signal=signal, prices=prices, fit=True)
    static = A @ np.array([1, 1])
    assert np.all(out["payoff"] >= static - 1e-6)  # the request is kept where it is built; dropped where it is not costs the same carry
    assert np.all(out["dropped"][built] == 0)


def test_reserve_released_by_a_drop_funds_a_deferred_lease():
    prices, built, op_year, A, A_def = _case()
    signal = built[:, None]
    out = dy.staged_policy([0, 1], A, A_def, carry=np.array([3e6]), charge=np.array([5e7, 6e7]), budget=6.5e7, lease_mask=np.array([True, False]),
                           op_year=op_year, signal=signal, prices=prices, fit=True)
    dropped = out["dropped"] == 1
    assert dropped.any() and np.all(out["started"][dropped] == 1)  # the dropped request's reserve (57) plus 5 spare covers the lease's 50
    assert np.all(out["started"][~dropped] == 0)  # without the drop only 5 is spare
    assert np.allclose(out["payoff"][dropped], -3e6 + 4e7)


def test_the_revision_respects_the_lease_cap():
    prices, built, op_year, A, A_def = _case()
    signal = built[:, None]
    out = dy.staged_policy([0, 1], A, A_def, carry=np.array([3e6]), charge=np.array([5e7, 6e7]), budget=6.5e7, lease_mask=np.array([True, False]),
                           op_year=op_year, signal=signal, prices=prices, fit=True, lease_cap=0.4)
    assert np.all(out["started"] == 0)  # 40% of 65 is 26, less than the lease's 50: nothing may start, released reserve or not


def test_no_request_is_dropped_for_a_lease_the_cap_would_never_admit():
    prices, built, op_year, A, A_def = _case()
    signal = built[:, None]
    out = dy.staged_policy([0, 1], A, A_def, carry=np.array([3e6]), charge=np.array([5e7, 6e7]), budget=6.5e7, lease_mask=np.array([True, False]),
                           op_year=op_year, signal=signal, prices=prices, fit=True, lease_cap=0.4)
    assert np.all(out["dropped"] == 0)  # walking away earns the carry back either way; the reserve has nowhere to go
