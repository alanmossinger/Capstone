"""Tests for the discrete-time models of notebook 06.

The unit tests check the project-year rows (delayed entry, congestion without
the project itself), the state encoding (no row sees its own outcome) and the
hazard → incidence arithmetic on toy data. ``test_model_cif_inside_aj_bands``
is notebook 06's acceptance check: averaged by region, each model's
P(operation by 3/5/7 years) for the entrants it was fitted on must lie inside
the Aalen–Johansen 95% bootstrap band of the same entrants
(``results/dt_band_check.csv``, written by the notebook).
"""

import numpy as np
import pandas as pd
import pytest

from src import config, discrete_time, features, paths

BAND_FILE = paths.RESULTS / "dt_band_check.csv"


def _toy_requests():
    """Three requests in one region: plain, delayed entry with a later exit, delayed entry stamped."""
    clean = pd.DataFrame({
        "region": ["R", "R", "R"],
        "q_date": pd.to_datetime(["2010-01-01", "2010-07-01", "2011-01-01"]),
        "mw": [100.0, 200.0, 300.0],
        "q_status": ["operational", "operational", "withdrawn"],
        "on_date": pd.to_datetime(["2012-07-01", "2014-03-01", None]),
        "wd_date": pd.to_datetime([None, None, "2012-07-01"]),
    })
    frame = clean.assign(
        duration_years=[2.5, 3.67, 1.5], event=[1, 1, 2], entry_years=[0.0, 1.5, 1.5],
        tech="Solar", size_regime="20–<100", service="NRIS", hybrid=False, log_mw=np.log(clean["mw"]),
        q_year=clean["q_date"].dt.year, congestion_rank=0.5, state="XX")
    frame["congestion_gw"] = features.congestion_at_entry(clean)["congestion_gw"]
    return clean, frame


def test_delayed_entry_keeps_only_full_years_after_entry():
    _, frame = _toy_requests()
    rows = discrete_time.observed_years(frame)
    by_project = rows.groupby("project")["year_in_queue"].apply(list).to_dict()
    assert by_project[0] == [1, 2, 3]  # no delayed entry: every year up to the exit
    assert by_project[1] == [3, 4]  # entry at 1.5 years: first full year is year 3; exit in year 4
    assert 2 not in by_project  # exit recorded on the entry date (a stamped withdrawal): no rows
    assert rows.loc[rows["project"] == 1, "outcome"].tolist() == [0, 1]


def test_as_recorded_version_keeps_every_year():
    _, frame = _toy_requests()
    rows = discrete_time.observed_years(frame, delayed=False)
    assert rows.groupby("project").size().to_dict() == {0: 3, 1: 4, 2: 2}


def test_yearly_congestion_leaves_out_the_project_itself():
    clean, frame = _toy_requests()
    rows = discrete_time.project_years(frame, clean, delayed=False)
    year_1 = rows[rows["year_in_queue"] == 1].set_index("project")["congestion_gw"]
    assert np.allclose(year_1.to_numpy(), frame["congestion_gw"].to_numpy())  # year 1 = congestion at entry
    # start of project 0's year 2 (2011-01-01): #1 waiting (0.2 GW); #2 enters that very day, not before
    second = rows[(rows["project"] == 0) & (rows["year_in_queue"] == 2)]["congestion_gw"].iloc[0]
    assert np.isclose(second, 0.2)


def test_state_encoding_never_sees_a_rows_own_outcome():
    rng = np.random.default_rng(0)
    rows = pd.DataFrame({"project": np.repeat(np.arange(200), 3), "state": np.repeat(rng.choice(list("ABCD"), 200), 3),
                         "outcome": rng.choice([0, 1, 2], 600, p=[0.8, 0.1, 0.1])})
    changed = rows.copy()
    changed.loc[changed["project"] == 7, "outcome"] = 1  # change one project's outcomes only
    first = discrete_time.encode_state(rows)[0]
    second = discrete_time.encode_state(changed)[0]
    own = rows["project"] == 7
    assert np.allclose(first.loc[own, "state_operation"], second.loc[own, "state_operation"])


def test_held_out_rows_get_training_rates():
    train = pd.DataFrame({"project": [0, 0, 1, 1], "state": ["A", "A", "B", "B"], "outcome": [0, 1, 0, 0]})
    held_out = pd.DataFrame({"project": [9], "state": ["Z"], "outcome": [1]})
    _, scored = discrete_time.encode_state(train, [held_out], n_folds=2, prior_rows=0)
    assert np.isclose(scored["state_operation"].iloc[0], 0.25)  # unseen state → overall training rate


def test_cif_table_matches_hand_calculation():
    # constant hazards 0.1 (operation) and 0.2 (withdrawal) for 10 years
    table = discrete_time.cif_table(np.full(10, 0.1), np.full(10, 0.2), pd.Index(["p"]))
    stay = 0.7 ** np.arange(10)
    assert np.isclose(table.loc["p", 3], 0.1 * stay[:3].sum())
    assert np.isclose(table.loc["p", "withdrawal_5"], 0.2 * stay[:5].sum())
    expected = (0.1 * stay * (np.arange(1, 11) - 0.5)).sum() / (0.1 * stay).sum()
    assert np.isclose(table.loc["p", "expected_years"], expected)


def test_logit_design_has_fixed_columns():
    _, frame = _toy_requests()
    rows = discrete_time.prediction_rows(frame).assign(state_operation=0.1, state_withdrawal=0.2)
    one = discrete_time.logit_design(rows.iloc[:10])
    other = discrete_time.logit_design(rows.iloc[10:])
    assert list(one.columns) == list(other.columns)
    assert not any(column.startswith("early × region_ERCOT") for column in one.columns)


def _band_rows():
    if not BAND_FILE.exists():
        pytest.skip(f"{BAND_FILE.name} missing — run notebook 06 first")
    return pd.read_csv(BAND_FILE)


@pytest.mark.parametrize("model", ["dt_logit", "dt_lgbm"])
@pytest.mark.parametrize("region", config.TRACK_A_REGIONS)
def test_model_cif_inside_aj_bands(region, model):
    rows = _band_rows()
    part = rows[(rows["region"] == region) & (rows["model"] == model)]
    assert set(part["horizon"]) == set(config.HORIZONS)
    outside = part[(part["predicted"] < part["band_low"]) | (part["predicted"] > part["band_high"])]
    assert outside.empty, outside[["horizon", "predicted", "band_low", "band_high"]].round(3).to_string(index=False)
