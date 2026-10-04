"""Tests for the Track B helpers of notebook 07.

They check the state encoding (no request sees its own outcome), the base
rate's fallback to the region, the binned isotonic map (monotone, no step
backed by fewer requests than asked) and the Wilson interval against a hand
calculation.
"""

import numpy as np
import pandas as pd

from src import track_b


def test_state_encoding_never_sees_a_requests_own_outcome():
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"state": rng.choice(list("ABC"), 300), "built": rng.integers(0, 2, 300)})
    changed = frame.copy()
    changed.loc[17, "built"] = 1 - changed.loc[17, "built"]
    first = track_b.encode_state(frame)[0]
    second = track_b.encode_state(changed)[0]
    assert np.isclose(first.loc[17, "state_rate"], second.loc[17, "state_rate"])


def test_unseen_state_gets_overall_rate():
    train = pd.DataFrame({"state": ["A", "A", "B", "B"], "built": [1, 0, 0, 0]})
    _, scored = track_b.encode_state(train, [pd.DataFrame({"state": ["Z"]})], n_folds=2, prior=0)
    assert np.isclose(scored["state_rate"].iloc[0], 0.25)


def test_base_rate_falls_back_to_region_for_small_cells():
    train = pd.DataFrame({"region": ["R"] * 60 + ["R"] * 5, "tech": ["Solar"] * 60 + ["Wind"] * 5,
                          "built": [1] * 30 + [0] * 30 + [1] * 5})
    target = pd.DataFrame({"region": ["R", "R"], "tech": ["Solar", "Wind"]})
    rates = track_b.base_rates(train, target, min_n=50)
    assert np.isclose(rates["rate"].iloc[0], 0.5) and rates["cell"].iloc[0] == "region × technology"
    assert np.isclose(rates["rate"].iloc[1], 35 / 65) and rates["cell"].iloc[1] == "region"


def test_binned_isotonic_is_monotone_and_ignores_a_few_extreme_scores():
    rng = np.random.default_rng(1)
    p = np.concatenate([rng.uniform(0, 0.4, 500), [0.9, 0.91, 0.92]])
    y = np.concatenate([rng.binomial(1, p[:500]), [1, 1, 1]])  # three extreme scores, all built
    fitted = track_b.isotonic(p, y, min_bin=50)
    grid = np.linspace(0, 1, 101)
    values = fitted.predict(grid)
    assert np.all(np.diff(values) >= -1e-12)
    assert values[-1] < 0.6  # plain isotonic regression would send the top of the map to 1


def test_wilson_matches_hand_calculation():
    low, high = track_b.wilson(0, 10)
    assert np.isclose(low, 0.0) and np.isclose(high, 0.2775, atol=1e-4)
    low, high = track_b.wilson(5, 10)
    assert np.isclose(low, 0.2366, atol=1e-4) and np.isclose(high, 0.7634, atol=1e-4)
