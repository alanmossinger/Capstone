"""Discrete-time competing-risks models: project-year data, designs, fits and predictions.

What: turns Track A requests into one row per project per year in the queue
(with ERCOT's delayed entry and a queue-congestion value updated every
year), builds the design matrices of the multinomial logit and of LightGBM,
target-encodes the state inside the training rows only, fits both models
and turns their yearly hazards into P(operation by t) and an expected time
to operation.
Why: the Cox models of notebook 05 assume each effect is constant over the
wait, and 17 of 36 effects fail that test. A discrete-time model gives every
year in the queue its own baseline hazard and lets effects differ early and
late, and the two causes (operation, withdrawal) are modelled together as
the three outcomes of a year: stay, operate, withdraw.
Reads / writes: nothing.
Used by: notebook 06 (fits and predictions) and notebook 08 (sensitivity
refits); ``tests/test_discrete_time.py``.
"""

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src import config, features, survival_tools

MAX_YEARS = 10  # project-years beyond the tenth year in the queue are dropped; horizons stop at 7
POOLED_FROM = 8  # the logit gives years 8–10 one shared effect: only 6% of the fitted project-years are that late
EARLY_YEARS = 3  # "early" years for the logit's interactions: notebook 05 found fast profiles fast in years 0–3
STATE_PRIOR_ROWS = 200  # smoothing of the state encoding: a state with 200 project-years gets half its own rate
TECH_LEVELS = list(config.TECH_COLORS)  # Solar (reference) first; same seven groups as the baseline and Cox
SERVICE_LEVELS = ["NRIS", "ERIS", "missing"]  # NRIS/ERIS occurs only in SPP, outside Track A


def _exit_dates(clean):
    """Exit date used by the congestion sweep: operation or withdrawal date, else none (still waiting)."""
    return clean["on_date"].where(clean["q_status"] == "operational",
                                  clean["wd_date"].where(clean["q_status"] == "withdrawn"))


def year_start_dates(q_date, year_in_queue):
    """First day of each project-year: the request date plus (k − 1) years of 365.25 days."""
    days = np.round((np.asarray(year_in_queue, dtype=float) - 1) * config.DAYS_PER_YEAR).astype("int64")
    return pd.to_datetime(np.asarray(q_date, dtype="datetime64[ns]")) + pd.to_timedelta(days, unit="D")


def observed_years(frame, delayed=True, max_years=MAX_YEARS):
    """Project-years that are watched in full: ``project``, ``year_in_queue``, ``outcome``.

    Notes
    -----
    ``survival_tools.expand_project_years`` plus, under delayed entry, the
    rule k − 1 ≥ ``entry_years`` (see ``project_years``).
    """
    rows = survival_tools.expand_project_years(frame, max_years=max_years)
    if delayed:
        rows = rows[rows["year_in_queue"].to_numpy() - 1 >= frame.loc[rows["project"], "entry_years"].to_numpy()]
    return rows.reset_index(drop=True)


def project_years(frame, clean, delayed=True, max_years=MAX_YEARS, tech_column="tech"):
    """Project-year rows for fitting, with delayed entry and time-varying congestion.

    Parameters
    ----------
    frame : pandas.DataFrame
        Track A requests (index = row label in ``clean``) with the entry-time
        features, ``duration_years``, ``event`` and ``entry_years``.
    clean : pandas.DataFrame
        The full clean table (all regions); congestion is counted in it.
    delayed : bool
        Keep only project-years that start at or after the project's entry
        time (decisions #21 and #26). False gives the as-recorded version.
    max_years : int
        Last year in the queue that gets a row.
    tech_column : str
        Column of ``frame`` with the technology group.

    Returns
    -------
    pandas.DataFrame
        One row per project-year: ``project``, ``year_in_queue``, ``outcome``
        (0 stay, 1 operation, 2 withdrawal), the entry-time features and
        ``congestion_gw`` / ``log_congestion_gw`` measured on the first day
        of that year.

    Notes
    -----
    Year k covers (k − 1, k] years since the request
    (``survival_tools.expand_project_years``). Under delayed entry a year is
    kept only when it starts at or after the entry time (k − 1 ≥ entry), so
    every kept year is watched in full. Keeping the year that contains the
    entry date would understate its hazard (the project is watched for only
    part of it), and would let back in the projects whose recorded exit *is*
    the entry date — ERCOT's stamped withdrawals. A project that had left
    before its first full year contributes nothing (decision #26).
    Congestion on the first day of year k uses the same rule as at entry
    (requests that entered before that day and had not left before it), minus
    the project itself, which is still waiting on that day for k ≥ 2.
    """
    rows = observed_years(frame, delayed, max_years)
    out = attach_features(rows, frame, tech_column)
    out["congestion_gw"] = yearly_congestion(rows, frame, clean)
    out["log_congestion_gw"] = np.log1p(out["congestion_gw"])
    return out


def yearly_congestion(rows, frame, clean):
    """GW waiting in the project's region on the first day of each project-year, without the project.

    Parameters
    ----------
    rows : pandas.DataFrame
        ``project`` and ``year_in_queue``.
    frame, clean : pandas.DataFrame
        As in ``project_years``.

    Returns
    -------
    numpy.ndarray
        One value per row.

    Notes
    -----
    ``features.congestion_on_dates`` counts every request that entered
    before the day and had not left before it; the project itself meets that
    rule from year 2 on while it is still waiting, so its own MW are taken
    off.
    """
    project = rows["project"].to_numpy()
    start = year_start_dates(frame.loc[project, "q_date"], rows["year_in_queue"])
    congestion = features.congestion_on_dates(clean, frame.loc[project, "region"], start)
    exit_date = _exit_dates(clean).loc[project].to_numpy()
    entered = clean.loc[project, "q_date"].to_numpy() < start.to_numpy()
    waiting = pd.isna(exit_date) | (exit_date >= start.to_numpy())
    own_gw = np.where(entered & waiting, clean.loc[project, "mw"].to_numpy() / 1000, 0.0)
    return np.clip(congestion["congestion_gw"].to_numpy() - own_gw, 0, None)  # clip: float noise of cumulative sums


def prediction_rows(frame, max_years=MAX_YEARS, tech_column="tech"):
    """Rows for years 1 … ``max_years`` of each request, as known on its request date.

    Notes
    -----
    A prediction made at entry cannot know how crowded the queue will be in
    later years, so congestion stays at its entry value in every year (a
    persistence forecast). The models are fitted on the realised yearly
    values; notebook 06 measures on the 2016 cohort how much this costs.
    """
    years = np.tile(np.arange(1, max_years + 1), len(frame))
    rows = pd.DataFrame({"project": np.repeat(frame.index.to_numpy(), max_years), "year_in_queue": years})
    out = attach_features(rows, frame, tech_column)
    out["congestion_gw"] = frame.loc[rows["project"], "congestion_gw"].to_numpy(dtype=float)
    out["log_congestion_gw"] = np.log1p(out["congestion_gw"])
    return out


def attach_features(rows, frame, tech_column="tech"):
    """Copy each project's entry-time features onto its project-year rows."""
    project = rows["project"].to_numpy()
    out = rows.copy()
    out["region"] = frame.loc[project, "region"].astype(str).to_numpy()
    out["tech"] = frame.loc[project, tech_column].astype(str).to_numpy()
    out["size_regime"] = frame.loc[project, "size_regime"].astype(str).to_numpy()
    out["service"] = frame.loc[project, "service"].astype(str).to_numpy()
    out["hybrid"] = frame.loc[project, "hybrid"].astype(float).to_numpy()
    out["log_mw"] = frame.loc[project, "log_mw"].to_numpy(dtype=float)
    out["q_year"] = frame.loc[project, "q_year"].to_numpy(dtype=float)
    out["congestion_rank"] = frame.loc[project, "congestion_rank"].astype(float).fillna(0.5).to_numpy()
    out["state"] = frame.loc[project, "state"].astype(str).to_numpy()
    return out


def state_rates(train_rows, prior_rows=STATE_PRIOR_ROWS):
    """Smoothed yearly operation and withdrawal rates of each state in ``train_rows``.

    Notes
    -----
    Rate = (events + prior_rows × overall rate) / (project-years + prior_rows),
    an m-estimate: a state with few project-years is pulled towards the
    overall rate. Rates are on the hazard scale (per project-year), the scale
    the models work on.
    """
    overall = {cause: (train_rows["outcome"] == code).mean() for cause, code in [("operation", 1), ("withdrawal", 2)]}
    grouped = train_rows.groupby("state")["outcome"]
    table = pd.DataFrame({"n": grouped.size(), "operation": grouped.apply(lambda s: (s == 1).sum()),
                          "withdrawal": grouped.apply(lambda s: (s == 2).sum())})
    rates = pd.DataFrame(index=table.index)
    for cause in ["operation", "withdrawal"]:
        rates[cause] = (table[cause] + prior_rows * overall[cause]) / (table["n"] + prior_rows)
    return rates, overall


def encode_state(train_rows, other_rows=(), n_folds=5, seed=0, prior_rows=STATE_PRIOR_ROWS):
    """Add ``state_operation`` / ``state_withdrawal`` without letting a row see its own outcome.

    Parameters
    ----------
    train_rows : pandas.DataFrame
        Project-year rows the model is fitted on.
    other_rows : sequence of pandas.DataFrame
        Rows to score (held-out fold, validation, test); they get rates
        computed on all of ``train_rows``.
    n_folds, seed : int
        Inner folds for the training rows' own encoding.

    Returns
    -------
    tuple
        ``train_rows`` with the two columns, then each of ``other_rows``.

    Notes
    -----
    Training rows are encoded out of fold, grouped by project: a project's
    rows get state rates computed without any of its own years, so the model
    cannot learn "this state's rate" from the outcome it is predicting.
    States never seen in training get the overall rate. This runs inside each
    cross-validation fold (PLAN.md §7: state is target-encoded inside folds).
    """
    train = train_rows.copy()
    for column in ["state_operation", "state_withdrawal"]:
        train[column] = np.nan
    folds = GroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    for fit_idx, apply_idx in folds.split(train, groups=train["project"]):
        rates, overall = state_rates(train.iloc[fit_idx], prior_rows)
        states = train["state"].iloc[apply_idx]
        for cause in ["operation", "withdrawal"]:
            train.iloc[apply_idx, train.columns.get_loc(f"state_{cause}")] = \
                states.map(rates[cause]).fillna(overall[cause]).to_numpy()
    rates, overall = state_rates(train_rows, prior_rows)
    encoded = []
    for rows in other_rows:
        rows = rows.copy()
        for cause in ["operation", "withdrawal"]:
            rows[f"state_{cause}"] = rows["state"].map(rates[cause]).fillna(overall[cause]).to_numpy()
        encoded.append(rows)
    return (train, *encoded)


def logit_design(rows, interactions=True):
    """Numeric design of the multinomial logit (one row per project-year).

    Notes
    -----
    A free effect for each year in the queue 2–7 and one for years 8–10
    together (year 1 is the reference; after year 7 too few requests are
    still waiting for a separate effect per year), indicators against PJM,
    solar, 20–<100 MW and NRIS, and the numeric features. The hybrid flag is
    left out because the Solar+Battery group already carries it (as in the
    Cox design of notebook 05); LightGBM keeps it. With ``interactions`` the CAISO, technology and size
    indicators also get an "early" copy (years 1–3), so an attribute can
    matter more early than late — the drift notebook 05's Schoenfeld
    diagnostics showed. ERCOT gets no early copy: under delayed entry its
    training requests are almost never watched in their first three years
    (no rows in the fit on entrants to 2015, 24 in the fit to 2016), so the
    term would be set by a handful of rows; ERCOT's early years borrow their
    shape from PJM and CAISO instead (decision #26). Level lists are fixed,
    so every design has the same columns.
    """
    X = pd.DataFrame(index=rows.index)
    for k in range(2, POOLED_FROM):
        X[f"year_{k}"] = (rows["year_in_queue"] == k).astype(float)
    X[f"year_{POOLED_FROM}+"] = (rows["year_in_queue"] >= POOLED_FROM).astype(float)
    groups = {"region": ["ERCOT", "CAISO"], "tech": TECH_LEVELS[1:],
              "size": [s for s in config.SIZE_LABELS if s != "20–<100"]}
    columns = {"region": "region", "tech": "tech", "size": "size_regime"}
    for name, levels in groups.items():
        for level in levels:
            X[f"{name}_{level}"] = (rows[columns[name]] == level).astype(float)
    for level in SERVICE_LEVELS[1:]:
        X[f"service_{level}"] = (rows["service"] == level).astype(float)
    X["log_mw"] = rows["log_mw"]
    X["q_year"] = rows["q_year"]
    X["log_congestion_gw"] = rows["log_congestion_gw"]
    X["congestion_rank"] = rows["congestion_rank"]
    X["state_operation"] = rows["state_operation"]
    X["state_withdrawal"] = rows["state_withdrawal"]
    if interactions:
        early = (rows["year_in_queue"] <= EARLY_YEARS).astype(float)
        for name, levels in {**groups, "region": ["CAISO"]}.items():
            for level in levels:
                X[f"early × {name}_{level}"] = X[f"{name}_{level}"] * early
    return X


def lgbm_design(rows):
    """Design of the LightGBM model: categories as pandas categoricals with fixed levels.

    Notes
    -----
    Trees need no reference levels or interactions: year in the queue enters
    as a number and the trees can split it differently for each region or
    technology. Fixed category lists keep the integer codes the same in
    training and prediction.
    """
    X = pd.DataFrame(index=rows.index)
    X["year_in_queue"] = rows["year_in_queue"].astype(float)
    X["region"] = pd.Categorical(rows["region"], categories=config.TRACK_A_REGIONS)
    X["tech"] = pd.Categorical(rows["tech"], categories=TECH_LEVELS)
    X["size_regime"] = pd.Categorical(rows["size_regime"], categories=config.SIZE_LABELS)
    X["service"] = pd.Categorical(rows["service"], categories=SERVICE_LEVELS)
    for column in ["hybrid", "log_mw", "q_year", "log_congestion_gw", "congestion_rank",
                   "state_operation", "state_withdrawal"]:
        X[column] = rows[column].astype(float)
    return X


def fit_logit(X, y, C):
    """Multinomial logistic regression with a ridge penalty on standardised columns.

    Notes
    -----
    Standardising first makes one penalty strength mean the same for every
    column. The three classes share one softmax, so the predicted
    probabilities of stay, operate and withdraw always add up to 1.
    """
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=5000)).fit(X, y)


LGBM_BASE = {"objective": "multiclass", "num_class": 3, "metric": "multi_logloss", "learning_rate": 0.05,
             "feature_fraction": 0.8, "bagging_fraction": 0.8, "bagging_freq": 1, "lambda_l2": 1.0,
             "seed": 0, "deterministic": True, "force_row_wise": True, "num_threads": 4, "verbosity": -1}


def fit_lgbm(X, y, params, n_rounds, valid=None, record=None):
    """LightGBM multiclass hazard model.

    Parameters
    ----------
    X, y : training design and outcomes (0/1/2).
    params : dict
        Tuned parameters, merged over ``LGBM_BASE``.
    n_rounds : int
        Boosting rounds (the maximum when ``valid`` is given).
    valid : tuple (X, y), optional
        Evaluation rows; with ``record`` their log loss is stored per round.
    record : dict, optional
        Filled by LightGBM's ``record_evaluation`` callback.

    Notes
    -----
    Fixed seeds, ``deterministic`` and a fixed thread count make reruns give
    the same trees.
    """
    train_set = lgb.Dataset(X, y, free_raw_data=False)
    valid_sets, callbacks = [], []
    if valid is not None:
        valid_sets = [lgb.Dataset(valid[0], valid[1], reference=train_set)]
        if record is not None:
            callbacks.append(lgb.record_evaluation(record))
    return lgb.train({**LGBM_BASE, **params}, train_set, num_boost_round=n_rounds,
                     valid_sets=valid_sets, valid_names=["valid"][:len(valid_sets)], callbacks=callbacks)


def predict_hazards(model, X):
    """Yearly hazards of operation and withdrawal (columns 1 and 2 of the class probabilities)."""
    probs = model.predict_proba(X) if hasattr(model, "predict_proba") else model.predict(X)
    return probs[:, 1], probs[:, 2]


def cif_table(h_operation, h_withdrawal, index, horizons=config.HORIZONS, max_years=MAX_YEARS):
    """P(operation by each horizon) and expected years to operation, from row-wise hazards.

    Parameters
    ----------
    h_operation, h_withdrawal : numpy.ndarray
        Hazards from ``prediction_rows`` order: ``max_years`` consecutive
        rows per project.
    index : pandas.Index
        Project labels, in the same order.

    Returns
    -------
    pandas.DataFrame
        One column per horizon, ``withdrawal_<h>`` for the competing
        incidence, ``p_operation_10`` and ``expected_years`` — the mean time
        to operation among projects that operate within ``max_years``.

    Notes
    -----
    CIF via ``survival_tools.cif_from_hazards``. Year k covers (k − 1, k],
    so an operation in year k is placed at its midpoint k − 0.5; the
    expected time is Σ (k − 0.5) · P(operate in year k) / P(operate by year
    ``max_years``).
    """
    h_op = np.asarray(h_operation).reshape(len(index), max_years)
    h_wd = np.asarray(h_withdrawal).reshape(len(index), max_years)
    cif_op, cif_wd = survival_tools.cif_from_hazards(h_op, h_wd)
    out = pd.DataFrame({h: cif_op[:, h - 1] for h in horizons}, index=index)
    for h in horizons:
        out[f"withdrawal_{h}"] = cif_wd[:, h - 1]
    in_year = np.diff(np.concatenate([np.zeros((len(index), 1)), cif_op], axis=1), axis=1)
    out[f"p_operation_{max_years}"] = cif_op[:, -1]
    out["expected_years"] = (in_year * (np.arange(1, max_years + 1) - 0.5)).sum(axis=1) / cif_op[:, -1]
    return out


def multiclass_log_loss(y, probs):
    """Mean negative log probability of the observed outcome of each project-year."""
    probs = np.clip(np.asarray(probs), 1e-15, 1)
    return float(-np.mean(np.log(probs[np.arange(len(y)), np.asarray(y, dtype=int)])))
