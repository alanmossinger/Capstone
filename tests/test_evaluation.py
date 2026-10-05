"""Tests for the evaluation metrics of notebook 08.

Each metric is checked on a toy dataset small enough to work out by hand,
and the bootstrap's ``sample_weight`` is checked against literally repeating
rows. One simulation checks that the censoring weights recover the true
P(operation by t) when part of the sample is censored.
"""

import numpy as np
from sklearn.metrics import roc_auc_score

from src import evaluation


def test_censoring_km_matches_hand_calculation():
    G = evaluation.censoring_km([1, 2, 2, 3, 4], [True, False, True, False, True])
    # censoring at 1 (5 at risk), 2 (4 at risk), 4 (1 at risk): 0.8, 0.6, 0
    assert np.isclose(G(0.5), 1.0)
    assert np.isclose(G(1.5), 0.8)
    assert np.isclose(G(2), 0.6) and np.isclose(G(2, left=True), 0.8)
    assert np.isclose(G(5), 0.0)


def test_horizon_outcome_treats_withdrawal_as_known_non_event():
    def G(s, left=False):
        return np.where(np.asarray(s, dtype=float) < 4.5, 1.0, 0.5)

    y, w = evaluation.horizon_outcome([1, 2, 6, 4, 3], [1, 2, 0, 0, 1], 5, G)
    assert y.tolist() == [1, 0, 0, 0, 1]
    assert w.tolist() == [1, 1, 2, 0, 1]  # withdrawn: known 0; waiting past 5: 1/G(5); censored at 4: unknown


def test_brier_by_hand():
    assert np.isclose(evaluation.brier([0.8, 0.3], [1, 0], [1, 2]), (0.04 + 2 * 0.09) / 2)


def test_auc_by_hand_and_against_sklearn():
    assert np.isclose(evaluation.auc([0.9, 0.4, 0.6, 0.2], [1, 1, 0, 0]), 0.75)
    assert np.isclose(evaluation.auc([0.5, 0.5], [1, 0]), 0.5)
    rng = np.random.default_rng(0)
    p, y, w = rng.uniform(size=300).round(2), rng.integers(0, 2, 300), rng.uniform(0.5, 2, 300)
    assert np.isclose(evaluation.auc(p, y, w), roc_auc_score(y, p, sample_weight=w))


def test_concordance_by_hand():
    durations, events, p = [1, 2, 3, 4], [1, 2, 1, 0], [0.9, 0.1, 0.2, 0.5]
    # operation at 1: beats all three later requests; operation at 3: below the request still waiting (0.5),
    # above the one that had withdrawn at 2 (0.1) → 4 concordant of 5 comparable pairs
    assert np.isclose(evaluation.concordance(p, durations, events, 5), 0.8)
    assert np.isclose(evaluation.concordance(p, durations, events, 2), 1.0)
    def G(s, left=False):
        return np.ones_like(np.asarray(s, dtype=float))
    assert np.isclose(evaluation.concordance(p, durations, events, 5, G), 0.8)  # Uno = Harrell without censoring


def test_sample_weight_equals_repeated_rows():
    rng = np.random.default_rng(1)
    n = 60
    durations = rng.uniform(0.1, 8, n).round(1)
    events = rng.choice([0, 1, 2], n)
    p = rng.uniform(size=n)
    counts = rng.integers(0, 3, n).astype(float)
    repeat = np.repeat(np.arange(n), counts.astype(int))
    assert np.isclose(evaluation.concordance(p, durations, events, 5, sample_weight=counts),
                      evaluation.concordance(p[repeat], durations[repeat], events[repeat], 5))
    y, w = (events == 1).astype(float), np.ones(n)
    assert np.isclose(evaluation.brier(p, y, w, counts), evaluation.brier(p[repeat], y[repeat], w[repeat]))
    assert np.isclose(evaluation.auc(p, y, w, counts), evaluation.auc(p[repeat], y[repeat], w[repeat]))


def test_top_fraction_shares_a_tied_cutoff():
    p = np.array([0.9] + [0.5] * 4 + [0.1] * 5)
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    out = evaluation.top_fraction(p, y, fraction=0.3)
    # top 3 = the 0.9 request plus half of the four tied at 0.5: (1 + 0.5) / 3
    assert np.isclose(out["precision"], 0.5) and np.isclose(out["base_rate"], 0.2) and np.isclose(out["lift"], 2.5)


def test_calibration_slope_recovers_known_values():
    rng = np.random.default_rng(2)
    p = rng.uniform(0.05, 0.6, 40000)
    y = rng.binomial(1, p)
    fit = evaluation.calibration_slope_intercept(p, y)
    assert abs(fit["slope"] - 1) < 0.05 and abs(fit["intercept"]) < 0.03
    logit = np.log(p / (1 - p))
    y_flat = rng.binomial(1, 1 / (1 + np.exp(-0.5 * logit)))  # predictions twice as extreme as the truth
    assert abs(evaluation.calibration_slope_intercept(p, y_flat)["slope"] - 0.5) < 0.05
    constant = evaluation.calibration_slope_intercept(np.full(100, 0.2), rng.binomial(1, 0.2, 100))
    assert np.isnan(constant["slope"]) and np.isfinite(constant["intercept"])


def test_ipcw_recovers_incidence_under_censoring():
    rng = np.random.default_rng(3)
    n = 40000
    exit_time = rng.exponential(4, n)
    cause = rng.choice([1, 2], n, p=[0.3, 0.7])
    window = rng.uniform(5, 8, n)  # administrative censoring, known for everyone
    truth = np.mean((cause == 1) & (exit_time <= 7))
    durations = np.minimum(exit_time, window)
    events = np.where(exit_time <= window, cause, 0)
    G = evaluation.censoring_km(window, np.ones(n, dtype=bool))
    y, w = evaluation.horizon_outcome(durations, events, 7, G)
    assert abs(np.mean(w * y) - truth) < 0.01
    assert abs(np.mean(y[w > 0]) - truth) > 0.02  # dropping the censored requests instead is biased


def test_bootstrap_rows_are_paired():
    draws = evaluation.bootstrap(lambda sw: {"a": sw.sum(), "b": sw[0]}, n=5, n_boot=10, seed=0)
    assert len(draws) == 10 and (draws["a"] == 5).all()
    low, high = evaluation.interval(np.arange(101))
    assert np.isclose(low, 2.5) and np.isclose(high, 97.5)
