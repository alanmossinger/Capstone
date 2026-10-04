"""Checks that the hand-written estimators agree with lifelines and with arithmetic."""

import numpy as np
import pandas as pd
from lifelines import AalenJohansenFitter, KaplanMeierFitter

from src import survival_tools


def _toy(n=400, seed=1):
    """Continuous durations (no ties) with two competing causes and censoring."""
    rng = np.random.default_rng(seed)
    t_op, t_wd, t_cens = rng.exponential(6, n), rng.exponential(3, n), rng.uniform(0, 10, n)
    durations = np.minimum.reduce([t_op, t_wd, t_cens])
    events = np.select([durations == t_op, durations == t_wd], [1, 2], default=0)
    return durations, events


def test_survival_matches_lifelines_kaplan_meier():
    durations, events = _toy()
    times = np.linspace(0, 8, 33)
    mine = survival_tools.aalen_johansen(durations, events, times)
    km = KaplanMeierFitter().fit(durations, events > 0).survival_function_at_times(times)
    assert np.allclose(mine["survival"], km.to_numpy(), atol=1e-10)


def test_cumulative_incidence_matches_lifelines_aalen_johansen():
    durations, events = _toy()
    times = np.linspace(0.5, 8, 16)
    mine = survival_tools.aalen_johansen(durations, events, times)
    for cause, column in [(1, "cif_operation"), (2, "cif_withdrawal")]:
        aj = AalenJohansenFitter(calculate_variance=False).fit(durations, events, event_of_interest=cause)
        theirs = aj.cumulative_density_.iloc[:, 0]
        expected = [theirs[theirs.index <= t].iloc[-1] for t in times]
        assert np.allclose(mine[column], expected, atol=1e-10), column


def test_hand_calculation_with_ties():
    # four projects: operation at 1, withdrawal at 1, censored at 2, operation at 3
    fit = survival_tools.aalen_johansen([1, 1, 2, 3], [1, 2, 0, 1], [0.5, 1, 2.5, 3])
    assert np.allclose(fit["cif_operation"], [0, 0.25, 0.25, 0.75])
    assert np.allclose(fit["cif_withdrawal"], [0, 0.25, 0.25, 0.25])
    assert np.allclose(fit["survival"], [1, 0.5, 0.5, 0.0])


def test_bands_contain_the_estimate():
    durations, events = _toy(n=300)
    times = np.array([1.0, 3.0, 5.0])
    fit = survival_tools.aalen_johansen(durations, events, times)
    bands = survival_tools.bootstrap_bands(durations, events, times, n_boot=200, seed=0)
    assert (bands["cif_operation_low"] <= fit["cif_operation"]).all()
    assert (fit["cif_operation"] <= bands["cif_operation_high"]).all()


def test_curves_by_group_reports_each_group():
    durations, events = _toy(n=200)
    frame = pd.DataFrame({"duration_years": durations, "event": events,
                          "region": np.where(np.arange(200) < 120, "A", "B")})
    out = survival_tools.curves_by_group(frame, "region", [1.0, 2.0], n_boot=20)
    assert set(out["region"]) == {"A", "B"}
    assert out.groupby("region")["n"].first().to_dict() == {"A": 120, "B": 80}
