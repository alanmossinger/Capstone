"""The queue as seen on a decision date: later outcomes are hidden, only waiting requests are live, ages are full years."""

import numpy as np
import pandas as pd

from src import decision_date as dd


def _frame():
    return pd.DataFrame({
        "q_date": pd.to_datetime(["2015-03-01", "2016-06-01", "2018-01-15", "2021-05-01"]),
        "exit_date": pd.to_datetime(["2017-01-01", "2022-07-01", "2024-12-31", "2024-12-31"]),
        "event": [2, 1, 0, 0],
        "duration_years": [1.84, 6.08, 6.96, 3.67],
    })


def test_censor_at_hides_exits_after_the_date_and_drops_later_entrants():
    out = dd.censor_at(_frame(), "2020-01-01")
    assert len(out) == 3  # the 2021 entrant did not exist yet
    assert out.loc[0, "event"] == 2  # withdrew in 2017: known
    assert out.loc[1, "event"] == 0  # operated in 2022: not known in 2020
    assert abs(out.loc[1, "duration_years"] - (pd.Timestamp("2020-01-01") - pd.Timestamp("2016-06-01")).days / 365.25) < 1e-9


def test_live_on_counts_requests_open_at_the_end_of_the_file():
    live = dd.live_on(_frame(), "2025-01-01")
    assert list(live.index) == [2, 3]  # event 0 at the censor date means still waiting
    assert list(dd.live_on(_frame(), "2020-01-01").index) == [1, 2]


def test_age_in_queue_is_full_years():
    ages = dd.age_in_queue(_frame(), "2025-01-01")
    assert ages.tolist() == [9, 8, 6, 3]


def test_observed_within_counts_operation_inside_the_window_only():
    f = _frame()
    assert dd.observed_within(f, "2020-01-01", 5).tolist() == [0, 1, 0, 0]
    assert dd.observed_within(f, "2020-01-01", 2).tolist() == [0, 0, 0, 0]


def test_lookup_curve_is_the_life_table_from_the_request_age():
    # ten earlier requests: in queue year 1 two operate and two withdraw; in year 2 one operates of the six left
    known = pd.DataFrame({"duration_years": [0.5, 0.5, 0.4, 0.6, 1.5, 3, 3, 3, 3, 3], "event": [1, 1, 2, 2, 1, 0, 0, 0, 0, 0],
                          "entry_years": 0.0, "region": "ERCOT", "type_clean": "Wind"})
    target = pd.DataFrame({"q_date": pd.to_datetime(["2024-06-01", "2023-06-01"]), "region": "ERCOT", "type_clean": "Wind"})
    out = dd.lookup_curves(known, target, "2025-01-01", years=2, min_at_risk=1)
    assert abs(out.loc[0, "p1"] - 0.2) < 1e-12  # age 0: year 1 hazard 2 / 10
    assert abs(out.loc[0, "p2"] - (0.2 + 0.6 * (1 / 6))) < 1e-12  # then 60% still waiting × 1/6
    assert abs(out.loc[1, "p1"] - 1 / 6) < 1e-12  # age 1: starts at year 2


def test_lease_history_stops_at_the_last_month_bsee_had_published():
    months = pd.date_range("2024-01-01", "2024-12-01", freq="MS")
    upstream = pd.DataFrame({"month": months, "oil_bbl": 1.0})
    seen = dd.lease_history_on(upstream, "2025-01-01", lag=3)
    assert seen["month"].max() == pd.Timestamp("2024-09-01")


def test_the_baseline_from_published_months_starts_at_the_decision_date():
    import numpy as np
    from src import economics as ec
    oil = np.linspace(1000, 600, 48)
    gas = np.linspace(500, 300, 48)
    full_o, _, _, _ = ec.lease_baseline(oil, gas, months=27)
    on_o, _, _, _ = dd.lease_baseline_on(oil, gas, months=24, gap=3)
    assert len(on_o) == 24 and np.allclose(on_o, full_o[3:])


def test_agreement_dates_on_the_date_ignore_the_later_edition():
    ms = pd.DataFrame({"ia_date_best": pd.to_datetime(["2023-05-01", "2024-01-18", "2022-02-01"]),
                       "ia_source": ["2025 edition", "2026 edition", "2025 edition"], "ia_inside_queue": [True, True, False]},
                      index=["a", "b", "c"])
    on = dd.agreement_dates_on(ms)
    assert on["a"] == pd.Timestamp("2023-05-01") and pd.isna(on["b"]) and pd.isna(on["c"])


def test_candidates_as_of_reads_liveness_from_the_latest_report_before_the_date_and_agreements_from_either_record():
    frame = pd.DataFrame({
        "q_id": ["A", "B", "C", "D", "E", "F"], "region": ["ERCOT"] * 5 + ["PJM"], "type_clean": ["Wind", "Wind", "Solar", "Solar", "Gas CC", "Wind"],
        "mw": [500.0, 400.0, 300.0, 10.0, 200.0, 900.0], "q_date": pd.to_datetime(["2022-01-01"] * 6),
        "exit_date": [pd.NaT, pd.NaT, pd.NaT, pd.NaT, pd.Timestamp("2024-06-01"), pd.NaT], "event": [0, 0, 0, 0, 2, 0],
        "ia_date": [pd.NaT, pd.Timestamp("2023-05-01"), pd.NaT, pd.NaT, pd.NaT, pd.NaT]})
    gis = pd.DataFrame({
        "q_id": ["A", "B", "A", "C"], "listed_as": ["active (large)", "cancelled", "active (large)", "active (large)"],
        "report_month": pd.to_datetime(["2024-10-01", "2024-10-01", "2024-11-01", "2025-02-01"]),
        "ia_signed": [pd.NaT, pd.NaT, pd.Timestamp("2024-11-15"), pd.NaT]})
    out = dd.candidates_as_of(frame, gis, as_of="2025-01-01", per_tech=5, min_mw=20)
    assert set(out["q_id"]) == {"A", "C"}  # B cancelled in a report; D below the floor; E exited in the edition, no GIS record; F not ERCOT
    assert out.set_index("q_id").loc["A", "agreement_known"] and not out.set_index("q_id").loc["C", "agreement_known"]
    assert out.set_index("q_id").loc["A", "liveness_source"] == "GIS 2024-11" and out.set_index("q_id").loc["C", "liveness_source"] == "edition: no GIS record"
    # the February 2025 report is after the date: it did not make C live by itself, the edition did
    later = dd.candidates_as_of(frame, gis, as_of="2025-03-01", per_tech=5, min_mw=20)
    assert later.set_index("q_id").loc["C", "liveness_source"] == "GIS 2025-02"


def test_record_hash_keeps_every_other_file_s_line(tmp_path):
    from src import get_lbnl
    p = tmp_path / "SHA256.txt"
    get_lbnl.record_hash(p, "a.xlsx", "aaa")
    get_lbnl.record_hash(p, "b.xlsx", "bbb")
    get_lbnl.record_hash(p, "a.xlsx", "aaa2")
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines == ["bbb  b.xlsx", "aaa2  a.xlsx"]
