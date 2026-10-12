"""Tests for the blending and recalibration helpers of notebook 06 (part B)."""

import numpy as np

from src import posthoc


def test_simplex_grid_sums_to_one():
    grid = posthoc.simplex_grid(3, 0.1)
    assert len(grid) == 66 and np.allclose(grid.sum(axis=1), 1) and (grid >= 0).all()


def test_blend_puts_all_weight_on_the_true_probabilities():
    rng = np.random.default_rng(0)
    truth = rng.uniform(0.02, 0.5, 5000)
    y = rng.binomial(1, truth)
    P = np.column_stack([np.full(5000, truth.mean()), truth, rng.uniform(0, 1, 5000)])
    assert np.allclose(posthoc.fit_blend(P, y), [0, 1, 0])


def test_recalibration_recovers_known_intercept_and_slope():
    rng = np.random.default_rng(1)
    p = rng.uniform(0.02, 0.6, 40000)
    logit = np.log(p / (1 - p))
    y = rng.binomial(1, 1 / (1 + np.exp(-(-0.4 + 1.3 * logit))))
    a, b = posthoc.fit_recalibration(p, y)
    assert abs(a + 0.4) < 0.08 and abs(b - 1.3) < 0.05
    assert np.allclose(posthoc.apply_recalibration(p, [0.0, 1.0]), p, atol=1e-9)


def test_cross_fit_never_uses_a_request_to_predict_itself():
    def fit(train_idx):
        return set(train_idx)

    def apply(train, idx):
        return np.array([float(i in train) for i in idx])  # 1 if the request was among the fitting rows

    assert (posthoc.cross_fit(fit, apply, n=20) == 0).all()
