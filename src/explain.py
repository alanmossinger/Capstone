"""Explaining a request's P(operation by t), not one year's hazard.

What: a numeric encoding of the entry-time features (and its inverse), and
a function that maps encoded features to P(operation by t) through the whole
chain of the discrete-time LightGBM: ten yearly rows, state rates from the
fitting rows, hazards, cumulative incidence. SHAP's permutation explainer and
partial-dependence curves call that function.
Why: the LightGBM model predicts yearly hazards of two causes; SHAP values of
one hazard on one project-year would not say how a feature moves the number
a developer or lender reads, P(operation within 5 years). Explaining the
composed function answers that directly, in probability points.
Reads / writes: nothing.
Used by: notebook 06 (part C); ``tests/test_explain.py``.
"""

import numpy as np
import pandas as pd

from src import config, discrete_time, features

FEATURES = ["region", "state", "tech", "hybrid", "size_mw", "service", "q_year", "congestion_gw", "congestion_rank"]
CATEGORIES = {"region": config.TRACK_A_REGIONS, "tech": discrete_time.TECH_LEVELS,
              "service": discrete_time.SERVICE_LEVELS}  # state's levels come from the data


def encode(frame, states):
    """Entry-time features as a float matrix (categories as integer codes).

    Parameters
    ----------
    frame : pandas.DataFrame
        Track A requests with ``region``, ``state``, ``tech``, ``hybrid``,
        ``log_mw``, ``service``, ``q_year``, ``congestion_gw``,
        ``congestion_rank``.
    states : list of str
        Levels of ``state``.

    Returns
    -------
    pandas.DataFrame
        Columns ``FEATURES``, all float.

    Notes
    -----
    Size enters once, in MW (the size regime is derived from it when
    decoding), so SHAP cannot split one attribute between two correlated
    columns; MW are rounded to 6 decimals so that a 20 MW request, stored as
    log MW, lands back on the large-generator side of the 20 MW step. A
    missing congestion rank (a region's first request) becomes
    0.5, as in the models.
    """
    X = pd.DataFrame(index=frame.index)
    levels = {**CATEGORIES, "state": states}
    for column in ["region", "state", "tech", "service"]:
        codes = pd.Categorical(frame[column].astype(str), categories=levels[column]).codes
        assert (codes >= 0).all(), f"unknown level in {column}"
        X[column] = codes
    X["hybrid"] = frame["hybrid"].astype(float)
    X["size_mw"] = np.round(np.exp(frame["log_mw"].astype(float)), 6)  # exp(log(20)) is 19.999…: round back onto the 20 MW step
    X["service"] = X.pop("service")
    X["q_year"] = frame["q_year"].astype(float)
    X["congestion_gw"] = frame["congestion_gw"].astype(float)
    X["congestion_rank"] = frame["congestion_rank"].astype(float).fillna(0.5)
    return X[FEATURES].astype(float)


def decode(X, states):
    """Inverse of ``encode``: a frame ``discrete_time.prediction_rows`` accepts (index 0 … n − 1)."""
    X = pd.DataFrame(np.asarray(X, dtype=float), columns=FEATURES)
    levels = {**CATEGORIES, "state": states}
    frame = pd.DataFrame(index=X.index)
    for column in ["region", "state", "tech", "service"]:
        frame[column] = np.asarray(levels[column], dtype=object)[X[column].round().astype(int)]
    frame["hybrid"] = X["hybrid"] > 0.5
    frame["log_mw"] = np.log(X["size_mw"])
    frame["size_regime"] = features.size_regime(X["size_mw"]).astype(str)
    frame["q_year"] = X["q_year"]
    frame["congestion_gw"] = X["congestion_gw"]
    frame["congestion_rank"] = X["congestion_rank"]
    return frame


def incidence_function(fitted, states, horizon):
    """Function from encoded features to the fitted LightGBM's P(operation by ``horizon``).

    Parameters
    ----------
    fitted : dict
        ``discrete_time.fit_both`` output (main version, no extra columns).
    states : list of str
        Levels used by ``encode``.
    horizon : int
        Years.

    Returns
    -------
    callable
        ``f(X) -> numpy.ndarray`` of probabilities, one per row of ``X``.

    Notes
    -----
    The state rates are computed once from the fitting rows (what
    ``discrete_time.encode_state`` gives rows being scored), so each call
    only builds the yearly rows and runs the trees. Congestion is held at
    its entry value in every year, as in every prediction made at entry.
    """
    rates, overall = discrete_time.state_rates(fitted["rows"])

    def f(X):
        frame = decode(X, states)
        rows = discrete_time.prediction_rows(frame)
        for cause in ["operation", "withdrawal"]:
            rows[f"state_{cause}"] = rows["state"].map(rates[cause]).fillna(overall[cause]).to_numpy()
        h_op, h_wd = discrete_time.predict_hazards(fitted["lgbm"], discrete_time.lgbm_design(rows))
        return discrete_time.cif_table(h_op, h_wd, frame.index, [horizon])[horizon].to_numpy()

    return f
