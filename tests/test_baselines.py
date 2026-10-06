"""The fair baseline reduces to notebook 05's baseline when the size bands are collapsed."""

import numpy as np
import pandas as pd

from src import baselines, survival_tools


def _requests(seed=0, n=600):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "region": rng.choice(["ERCOT", "PJM"], n),
        "tech": rng.choice(["Solar", "Gas"], n),
        "size_regime": rng.choice(["<5", "20–<100"], n),
        "duration_years": rng.exponential(3, n).round(2) + 0.1,
        "event": rng.choice([0, 1, 2], n, p=[0.3, 0.2, 0.5]),
    })


def test_single_size_band_reproduces_the_v1_baseline():
    train = _requests()
    train["size_regime"] = "20–<100"
    target = _requests(seed=1, n=50)
    target["size_regime"] = "20–<100"
    fair = baselines.fair_baseline_cif(train, target, [3, 5])
    v1 = survival_tools.baseline_cif(train, target, [3, 5])
    assert np.allclose(fair[[3, 5]].to_numpy(), v1[[3, 5]].to_numpy())


def test_thin_cells_fall_back_to_the_parent():
    train = _requests()
    target = _requests(seed=2, n=40)
    out = baselines.fair_baseline_cif(train, target, [5], min_n=10_000)  # every cell too thin
    assert (out["cell"] == "region").all()
    fine = baselines.fair_baseline_cif(train, target, [5], min_n=1)
    assert (fine["cell"] == "region × technology × size").all()
