"""The fixed list of size-aware model variants of notebook 04 (part D), shared with the notebooks that reuse the chosen one.

What: the candidates K0–K3 (LightGBM) and the K1/K2 logits as named
specifications, and one function that fits a specification with notebook
06's settings on a given training frame.
Why: notebook 04 (part D) chooses a candidate on 2016 entrants; notebook 04's parts G, J and
16 must refit exactly that candidate on other frames (other cohorts, other
horizons) without copying its definition.
Reads / writes: nothing.
Used by: notebook 04 (parts D, G, J) and notebook 09; ``tests/test_variants.py``.
"""

import pandas as pd

from src import discrete_time

SMALL_REGIMES = ["<5", "5–<20"]  # the two size regimes under the 20 MW FERC step


def design_columns():
    """Column order of LightGBM's design, so a monotone constraint lands on the right column."""
    dummy = pd.DataFrame({c: [0.0] for c in ["year_in_queue", "hybrid", "log_mw", "q_year", "log_congestion_gw",
                                              "congestion_rank", "state_operation", "state_withdrawal"]})
    dummy["region"], dummy["tech"], dummy["size_regime"], dummy["service"] = "PJM", "Solar", "<5", "NRIS"
    return list(discrete_time.lgbm_design(dummy).columns)


MONOTONE_MW = {"monotone_constraints": [-1 if c == "log_mw" else 0 for c in design_columns()]}

CANDIDATES = {
    "K0 LightGBM, yearly congestion": dict(congestion="yearly", large_only=False, params=None, model="dt_lgbm"),
    "K1 LightGBM, entry congestion": dict(congestion="entry", large_only=False, params=None, model="dt_lgbm"),
    "K2 LightGBM, entry congestion, ≥ 20 MW only": dict(congestion="entry", large_only=True, params=None, model="dt_lgbm"),
    "K3 LightGBM, entry congestion, monotone in MW": dict(congestion="entry", large_only=False, params=MONOTONE_MW,
                                                         model="dt_lgbm"),
    "K1 logit, entry congestion": dict(congestion="entry", large_only=False, params=None, model="dt_logit"),
    "K2 logit, entry congestion, ≥ 20 MW only": dict(congestion="entry", large_only=True, params=None, model="dt_logit"),
}


def at_least_20(frame):
    """Requests in a size regime of 20 MW or more (the same rule as notebook 06 (part A)'s robustness run)."""
    return ~frame["size_regime"].astype(str).isin(SMALL_REGIMES)


def fit_key(spec):
    """Candidates that share a fit (the K1 LightGBM and logit come from one ``fit_both`` call)."""
    return (spec["congestion"], spec["large_only"], str(spec["params"]))


def fit_candidate(spec, frame, clean, tuning):
    """Fit a candidate's specification on ``frame`` with notebook 04 (part B)'s settings.

    Parameters
    ----------
    spec : dict
        One value of ``CANDIDATES``.
    frame, clean, tuning :
        As in ``discrete_time.fit_both``.

    Returns
    -------
    dict
        ``discrete_time.fit_both``'s output; use ``predict_both(...)[spec["model"]]``.
    """
    train = frame[at_least_20(frame)] if spec["large_only"] else frame
    return discrete_time.fit_both(train, clean, tuning, congestion=spec["congestion"], params=spec["params"])
