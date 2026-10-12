"""The gym's situations show no outcome, respect the budget, and score each actor against hindsight."""

import numpy as np
import pandas as pd

from src import gym


def _pack():
    n = 8
    return pd.DataFrame({
        "project_key": [f"ERCOT|{i}" for i in range(n)], "region": "ERCOT", "q_year": 2018, "tech": ["Solar", "Wind"] * 4, "mw": np.arange(100, 100 + 10 * n, 10)[::-1],
        "p5_lookup": 0.2, "p5_model_repaired": np.linspace(0.1, 0.5, n), "cost_to_next_gate_base_$M": 2.0, "breakeven_price_$MWh": 40.0,
        "expected_npv_entry_base_contracted_$M": np.linspace(-1, 5, n), "in_pool_2y": True, "p3_landmark": 0.3,
        "expected_npv_2y_base_contracted_$M": np.linspace(-1, 5, n), "decision_entry_contracted": ["invest"] * 4 + ["exit"] * 4,
        "decision_2y_contracted": "invest", "status_end_2024": ["operated within 5 years"] * 2 + ["withdrew within 5 years"] * 6,
        "operated_within_3y_of_gate": [True, False] * 4, "npv_per_mw_if_built_year3_contracted_$M": 0.5,
    })


def test_queue_situation_hides_outcomes_and_scores_actors_within_budget():
    s = gym.queue_situation(_pack(), "ERCOT", 2018, n_show=8, budget_share=0.5)
    assert not set(gym.HIDDEN) & set(s["table"].columns)  # no outcome column reaches the advisor
    assert s["budget"] == 8 * 2.0 * 0.5
    books = {"instinct": gym.instinct_book(s), "optimizer": gym.optimizer_book(s), "hindsight": gym.hindsight_book(s)}
    for members in books.values():
        assert gym.score(s, members)["cost_$M"] <= s["budget"] + 1e-9
    table = gym.score_table(s, books)
    assert (table["regret_$M"] >= -1e-9).all()  # nobody beats hindsight
    assert table.loc[table["actor"] == "hindsight", "regret_$M"].iloc[0] == 0.0


def test_validate_pick_drops_unknown_and_over_budget_members():
    s = gym.queue_situation(_pack(), "ERCOT", 2018, n_show=8, budget_share=0.25)  # budget 4 = two requests
    kept, dropped = gym.validate_pick(s, ["ERCOT|0", "nope", "ERCOT|1", "ERCOT|2"])
    assert kept == ["ERCOT|0", "ERCOT|1"] and dropped == ["nope", "ERCOT|2"]


def test_real_price_path_holds_the_last_value_flat():
    months = pd.date_range("2016-01-01", "2016-12-01", freq="MS")
    nominal = pd.DataFrame({"month": months, "wti": np.linspace(30, 52, 12)})
    cpi = pd.DataFrame({"month": months, "cpi_u": 100.0})
    path = gym.real_price_path(nominal, cpi, "2016-06-01", 12, base_year=2016)
    assert len(path) == 12 and path[-1] == path[6] == 52.0 and path[0] == 40.0
