"""The partial forward test: what 2025 showed against what the models said on 1 January 2025.

What: the realized first year after the decision date, from records that did
not exist when the decision was made — the queue outcomes of the 2026 LBNL
edition (through end-2025), the 2025 oil, gas and ERCOT prices, the 2025 lease
production — set beside the predictions and the scenario bands of that day.
Why: the critique review of 21 October called this the cheapest new evidence
the project had not used. It is a post-hoc check, labelled so: one year is
not a test of a seven-year completion curve or a twenty-year tail, and no
registered line is scored on it.
Reads: ``data/processed/predictions_2025.parquet``, ``data/interim/trackA.parquet``,
``data/interim/queue_clean_2026.parquet``, ``results/scenario_price_bands.csv``,
the EIA spot-price workbooks on disk, ``results/candidate_npv.csv``.
Writes: nothing; notebook 12 writes ``results/v10/forward_*.csv``.
Used by: notebook 12; ``tests/test_forward.py``.
"""

import numpy as np
import pandas as pd

from src import config, evaluation, events

KEY = ["q_id", "entity", "region"]  # the join of the 2025 and 2026 editions (notebook 04)
YEAR_END = "2025-12-31"


def queue_year_one(predictions, track_a, clean_2026, as_of=config.DECISION_DATE, end=YEAR_END):
    """Each live request's realized status one year on, beside its one-year completion probabilities.

    Parameters
    ----------
    predictions : pandas.DataFrame
        ``predictions_2025.parquet``: ``project_key``, ``p1``, ``p1_level``, ``p1_lookup``, ``mw``.
    track_a : pandas.DataFrame
        The 2025-edition requests with ``project_key`` and the join key.
    clean_2026 : pandas.DataFrame
        The 2026 edition, cleaned (``q_id, entity, region, on_date, wd_date, q_status``).
    as_of, end : str
        The decision date and the end of the first year.

    Returns
    -------
    pandas.DataFrame
        One row per live request: ``outcome`` (operated / withdrawn / active /
        not in the 2026 file), ``y`` (1 if operated by ``end``), the three
        probabilities, ``mw``.

    Notes
    -----
    Outcomes come from the 2026 edition's dates coded by ``events.code_events``
    with the censor date at ``end``, so a request still waiting is "active",
    not failed. A request the 2026 file does not list is reported as such and
    left out of the scores (it may have changed id or been merged).
    """
    keys = track_a[["project_key"] + KEY].drop_duplicates("project_key")
    for c in KEY:
        keys[c] = keys[c].astype(str)
    later = clean_2026.copy()
    for c in KEY:
        later[c] = later[c].astype(str)
    later = events.code_events(later, censor_date=end)[KEY + ["event", "exit_date", "q_status"]].drop_duplicates(KEY)
    out = predictions.drop(columns=[c for c in KEY if c in predictions]).merge(keys, on="project_key", how="left").merge(later, on=KEY, how="left")
    end_ts, start = pd.Timestamp(end), pd.Timestamp(as_of)
    in_year = out["exit_date"].between(start, end_ts)
    out["outcome"] = np.select([out["event"].isna(), (out["event"] == events.OPERATION) & in_year, (out["event"] == events.WITHDRAWAL) & in_year],
                               ["not in the 2026 file", "operated", "withdrawn"], default="active")
    out["y"] = (out["outcome"] == "operated").astype(int)
    cols = ["project_key", "q_id", "mw", "agreement_known", "outcome", "y", "p1", "p1_level", "p1_lookup"]
    return out[[c for c in cols if c in out]]


def queue_scores(year_one):
    """Brier score and calibration of the three one-year probabilities on the requests the 2026 file resolves.

    Notes
    -----
    Every request is observed to the end of the year, so the Brier score needs
    no censoring weight (weights of one); the calibration slope is
    ``evaluation.calibration_slope_intercept``. Realized and predicted
    operation counts are given beside them: the level is the question the
    backtests could not settle.
    """
    scored = year_one[year_one["outcome"] != "not in the 2026 file"]
    rows = []
    for name in ("p1", "p1_level", "p1_lookup"):
        p = scored[name].clip(1e-6, 1 - 1e-6).to_numpy(float)
        y = scored["y"].to_numpy(int)
        cal = evaluation.calibration_slope_intercept(p, y)
        rows.append({"method": name, "n": len(scored), "operated": int(y.sum()), "predicted_operations": float(p.sum()),
                     "brier": float(np.mean((y - p) ** 2)), "slope": cal["slope"], "intercept": cal["intercept"]})
    return pd.DataFrame(rows)


def prices_year(realized, bands, year=2025):
    """Where each realized annual mean price fell in that year's scenario band.

    Parameters
    ----------
    realized : dict
        Series name → realized annual mean (e.g. ``{"WTI": 65.1}``), in the bands' units.
    bands : pandas.DataFrame
        ``results/scenario_price_bands.csv`` (series, year, q05 … q95).

    Returns
    -------
    pandas.DataFrame
        One row per series: the realized value, the band's quantiles and the
        band it fell in ("below q05", "q05–q25", …, "above q95").
    """
    b = bands[bands["year"] == year].set_index("series")
    rows = []
    for s, v in realized.items():
        q = b.loc[s]
        edges = [("below q05", -np.inf, q["q05"]), ("q05–q25", q["q05"], q["q25"]), ("q25–q50", q["q25"], q["q50"]),
                 ("q50–q75", q["q50"], q["q75"]), ("q75–q95", q["q75"], q["q95"]), ("above q95", q["q95"], np.inf)]
        where = next(name for name, lo, hi in edges if lo <= v < hi)
        rows.append({"series": s, "year": year, "realized": v, "q05": q["q05"], "q50": q["q50"], "q95": q["q95"], "band": where})
    return pd.DataFrame(rows)
