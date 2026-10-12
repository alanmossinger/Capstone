"""The rolling refit never sees its own future, the paired bootstrap passes only when the interval is below zero, and the Arps baseline runs."""

import numpy as np
import pandas as pd

from src import energy_models as em


def _table(n_origins=24, n_keys=5, seed=0):
    rng = np.random.default_rng(seed)
    origins = pd.date_range("2022-01-01", periods=n_origins, freq="MS")
    rows = []
    for k in range(n_keys):
        level = 10 * (k + 1)
        for o in origins:
            x = level + rng.normal()
            rows.append({"key": k, "origin": o, "target_month": o + pd.DateOffset(months=1), "x": x, "y": x + rng.normal(0, 0.1)})
    return pd.DataFrame(rows)


class _Recorder:
    """A fake estimator that remembers the latest target month it was trained on."""

    def __init__(self):
        self.max_target = None

    def fit(self, X, y):
        self.n = len(y)
        return self

    def predict(self, X):
        return np.full(len(X), 0.0)


def test_rolling_predict_trains_only_on_targets_at_or_before_the_origin():
    table = _table()
    origins = list(table["origin"].unique()[12:18])
    seen = []

    def factory():
        model = _Recorder()
        seen.append(model)
        return model

    preds = em.rolling_predict(table, ["x"], "y", origins, factory, refit_every=3)
    assert len(seen) == 2  # six origins, quarterly refits
    # the first refit at origins[0] may use rows whose target month <= origins[0]
    allowed = int((table["target_month"] <= origins[0]).sum())
    assert seen[0].n == allowed
    assert preds.loc[table["origin"].isin(origins)].notna().all() and preds.loc[~table["origin"].isin(origins)].isna().all()


def test_paired_block_bootstrap_passes_only_below_zero():
    better = np.full(12, -1.0) + np.random.default_rng(1).normal(0, 0.1, 12)
    worse = np.full(12, 1.0) + np.random.default_rng(2).normal(0, 0.1, 12)
    noise = np.random.default_rng(3).normal(0, 1.0, 12)
    assert em.paired_block_bootstrap(better, n_boot=200)["pass"]
    assert not em.paired_block_bootstrap(worse, n_boot=200)["pass"]
    assert not em.paired_block_bootstrap(noise, n_boot=200)["pass"]


def test_score_line_picks_the_best_baseline_and_reports_every_mae():
    table = _table()
    table["last"] = table["x"]  # a baseline that is nearly right
    table["naive"] = 0.0  # a baseline that is far off
    table["ml"] = table["y"] + 0.01  # a challenger that is better than both
    out = em.score_line(table, "y", "ml", ["last", "naive"], n_boot=200)
    assert out["best_baseline"] == "last" and out["mae_ml"] < out["mae_last"] < out["mae_naive"]
    assert out["result"] == "PASS" and out["n_origins"] == 24


def test_elasticnet_choice_returns_a_grid_point():
    table = _table()
    origins = list(table["origin"].unique())
    choice = em.choose_elasticnet(table, ["x"], "y", origins[12:18])
    assert (choice["alpha"], choice["l1_ratio"]) in em.ENET_GRID and choice["validation_mae"] < 1.0
