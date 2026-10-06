"""The monotone constraint of candidate K3 lands on log_mw, and the size rule matches notebook 08's."""

import pandas as pd

from src import variants


def test_monotone_constraint_is_on_log_mw_only():
    columns = variants.design_columns()
    constraint = variants.MONOTONE_MW["monotone_constraints"]
    assert len(constraint) == len(columns)
    assert {c for c, k in zip(columns, constraint) if k != 0} == {"log_mw"}


def test_at_least_20_follows_the_size_regime():
    frame = pd.DataFrame({"size_regime": ["<5", "5–<20", "20–<100", "≥500"]})
    assert variants.at_least_20(frame).tolist() == [False, False, True, True]
