"""Values of information are never negative, never exceed perfect information, and match a hand-worked case."""

import numpy as np

from src import voi


def test_hand_worked_two_scenario_case():
    # one budget slot, two candidates: A pays 10 in s0 and 0 in s1; B pays 0 and 10; equal chances
    A = np.array([[10.0, 0.0], [0.0, 10.0]])
    A, unit = A * 1e6, 1e6  # dollars, the scale the optimizer is built for
    out = voi.evpi_total(A, np.ones(2) * unit, unit)
    assert abs(out["prior_value"] - 5e6) < 1e-3 and abs(out["evpi"] - 5e6) < 1e-3
    part = voi.evpi_partition(A, np.ones(2) * unit, unit, labels=[0, 1])
    assert abs(part["evpi"] - 5e6) < 1e-3


def test_sample_information_lies_between_zero_and_perfect_information():
    rng = np.random.default_rng(1)
    built = rng.random(400) < 0.3
    A = np.column_stack([np.where(built, 50.0, -10.0), rng.normal(5.0, 1.0, 400), rng.normal(3.0, 1.0, 400)]) * 1e6
    charge, budget = np.ones(3) * 1e6, 1e6
    perfect = voi.evpi_partition(A, charge, budget, labels=built)["evpi"]
    noisy = voi.evsi_signal(A, charge, budget, built, {True: 0.8, False: 0.1})
    useless = voi.evsi_signal(A, charge, budget, built, {True: 0.5, False: 0.5})
    assert -1e-3 <= noisy["evsi"] <= perfect + 1e-3 and noisy["evsi"] > 0
    assert abs(useless["evsi"]) < 1e-3  # a signal that says nothing is worth nothing
