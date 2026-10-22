"""The forward test reads outcomes from the later edition's dates, scores only resolved requests, and places prices in their band."""

import numpy as np
import pandas as pd

from src import forward as fw


def test_queue_year_one_codes_operated_withdrawn_active_and_missing():
    predictions = pd.DataFrame({"project_key": ["ERCOT|A", "ERCOT|B", "ERCOT|C", "ERCOT|D"], "mw": [100.0] * 4, "agreement_known": [True, False, False, False],
                                "p1": [0.5, 0.2, 0.1, 0.3], "p1_level": [0.4, 0.1, 0.1, 0.2], "p1_lookup": [0.3, 0.3, 0.3, 0.3]})
    track_a = pd.DataFrame({"project_key": ["ERCOT|A", "ERCOT|B", "ERCOT|C", "ERCOT|D"], "q_id": ["A", "B", "C", "D"], "entity": ["E"] * 4, "region": ["ERCOT"] * 4})
    clean_2026 = pd.DataFrame({"q_id": ["A", "B", "C"], "entity": ["E"] * 3, "region": ["ERCOT"] * 3, "q_date": pd.to_datetime(["2022-01-01"] * 3),
                               "on_date": [pd.Timestamp("2025-06-01"), pd.NaT, pd.NaT], "wd_date": [pd.NaT, pd.Timestamp("2025-03-01"), pd.NaT],
                               "q_status": ["operational", "withdrawn", "active"]})
    out = fw.queue_year_one(predictions, track_a, clean_2026)
    assert out.set_index("project_key")["outcome"].to_dict() == {"ERCOT|A": "operated", "ERCOT|B": "withdrawn", "ERCOT|C": "active", "ERCOT|D": "not in the 2026 file"}
    scores = fw.queue_scores(out)
    assert (scores["n"] == 3).all() and (scores["operated"] == 1).all()
    assert np.isclose(scores.set_index("method").loc["p1", "brier"], ((1 - 0.5) ** 2 + 0.2 ** 2 + 0.1 ** 2) / 3)


def test_prices_year_places_the_realized_mean_in_its_band():
    bands = pd.DataFrame({"series": ["WTI", "WTI"], "year": [2025, 2026], "q05": [50, 48], "q25": [60, 58], "q50": [70, 70], "q75": [80, 82], "q95": [100, 110]})
    out = fw.prices_year({"WTI": 65.0}, bands, 2025)
    assert out.loc[0, "band"] == "q25–q50"
    assert fw.prices_year({"WTI": 120.0}, bands, 2025).loc[0, "band"] == "above q95"
