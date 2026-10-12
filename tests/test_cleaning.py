"""Tests for the raw-file audit and the cleaning rules R1–R9.

Three kinds of test:

* ``test_audit_counts`` compares ``results/audit_counts.json`` (notebook 01 (part A))
  with the counts of the 2026-10-03 audit, typed in here by hand so the test
  does not share a constant with the code it checks;
* one small hand-made table per rule, so each rule is checked without the
  LBNL file;
* checks on the real clean table and its log (``data/interim/
  queue_clean.parquet``, ``results/clean_log.csv``), skipped until notebook
  02 has run.
"""

import json

import pandas as pd
import pytest

from src import cleaning, paths

AUDIT_FILE = paths.RESULTS / "audit_counts.json"
CLEAN_FILE = paths.DATA_INTERIM / "queue_clean.parquet"
LOG_FILE = paths.RESULTS / "clean_log.csv"


def _load_or_skip(path, reader, notebook):
    if not path.exists():
        pytest.skip(f"{path.name} missing — run notebook {notebook} first")
    return reader(path)


# --- audit -----------------------------------------------------------------

def test_audit_counts():
    audit = _load_or_skip(AUDIT_FILE, lambda p: json.loads(p.read_text(encoding="utf-8")), "01")
    assert (audit["n_rows"], audit["n_cols"]) == (36441, 31)
    assert audit["q_status"] == {"withdrawn": 20921, "active": 10538, "operational": 4432,
                                 "suspended": 546, "unknown": 4}
    assert audit["region"] == {"PJM": 8152, "West": 7675, "MISO": 4978, "Southeast": 3950,
                               "ERCOT": 3282, "CAISO": 2837, "SPP": 2469, "NYISO": 1817,
                               "ISO-NE": 1281}
    assert audit["placeholder_q_date"] == 204
    assert audit["negative_mw_rows"] == 17


# --- one toy table per rule --------------------------------------------------

def _toy():
    """Four requests with one problem each, dates already converted (as after R1)."""
    return pd.DataFrame({
        "q_id": [1, 2, "A3", 4],
        "entity": ["X", "X", "Y", "Y"],
        "q_status": ["operational", "withdrawn", "operational", "active"],
        "q_date": pd.to_datetime(["2015-01-01", "1970-01-01", "2016-06-01", "2018-01-01"]),
        "on_date": pd.to_datetime(["2018-01-01", "2019-01-01", "2016-01-01", pd.NaT]),
        "wd_date": pd.to_datetime([pd.NaT, "2017-01-01", pd.NaT, "2019-01-01"]),
        "ia_date": pd.to_datetime([pd.NaT, "1970-01-01", pd.NaT, pd.NaT]),
        "q_year": [2015.0, 1970.0, 2016.0, 2018.0],
    })


def test_r1_converts_excel_serials():
    raw = pd.DataFrame({column: [43511, None] for column in
                        ["q_date", "prop_date", "on_date", "wd_date", "ia_date"]})
    out, touched = cleaning.r1_convert_dates(raw)
    assert out["q_date"].iloc[0] == pd.Timestamp("2019-02-15")
    assert pd.isna(out["q_date"].iloc[1])
    assert touched["q_date converted"] == 1


def test_r2_placeholders_become_missing_and_year_follows_date():
    out, touched = cleaning.r2_placeholder_dates(_toy())
    assert pd.isna(out.loc[1, "q_date"]) and pd.isna(out.loc[1, "ia_date"])
    assert pd.isna(out.loc[1, "q_year"]) and out.loc[0, "q_year"] == 2015
    assert touched["q_date placeholder set to missing"] == 1


def test_r3_clears_impossible_operation_dates():
    out, touched = cleaning.r3_operation_dates(_toy())
    assert out.loc[0, "on_date"] == pd.Timestamp("2018-01-01")  # valid, kept
    assert pd.isna(out.loc[1, "on_date"])  # withdrawn row
    assert pd.isna(out.loc[2, "on_date"])  # before its request date
    assert touched["on_date cleared: status is not operational"] == 1
    assert touched["on_date cleared: before the request date"] == 1


def test_r4_clears_impossible_withdrawal_dates():
    toy = _toy()
    toy.loc[1, "q_date"] = pd.Timestamp("2018-01-01")  # withdrawal now precedes the request
    out, touched = cleaning.r4_withdrawal_dates(toy)
    assert pd.isna(out.loc[1, "wd_date"])  # before its request date
    assert pd.isna(out.loc[3, "wd_date"])  # active row
    assert touched == {"wd_date cleared: status is not withdrawn": 1,
                       "wd_date cleared: before the request date": 1}


def test_r5_keeps_generation_and_missing_type():
    toy = pd.DataFrame({"project_type": ["Generation", None, "Upgrade", "Surplus"]})
    out, touched = cleaning.r5_generation_only(toy)
    assert len(out) == 2
    assert touched == {"dropped: project_type = Upgrade": 1, "dropped: project_type = Surplus": 1}


def test_r6_sums_components_drops_non_positive_and_flags_large():
    toy = pd.DataFrame({"mw1": [100, -5, 3000, 0], "mw2": [50, None, 2500, None],
                        "mw3": [None, None, None, None]})
    out, touched = cleaning.r6_capacity(toy)
    assert out["mw"].tolist() == [150, 5500]
    assert out["mw_large"].tolist() == [False, True]
    assert touched["dropped: mw ≤ 0 or missing"] == 2


def test_r7_drops_the_duplicate_without_request_date():
    toy = _toy()
    toy.loc[1, ["q_id", "entity"]] = [1, "X"]  # same key as row 0
    toy.loc[1, "q_date"] = pd.NaT
    out, touched = cleaning.r7_project_key(toy)
    assert out["project_key"].is_unique and len(out) == 3
    assert touched["dropped: duplicate without a request date"] == 1


def test_r8_drops_sparse_fields_and_fills_missing_levels():
    toy = pd.DataFrame({"developer": ["D", None], "cluster": [None, None],
                        "service": ["NRIS", None], "county": [None, "Kern"]})
    out, _ = cleaning.r8_sparse_fields(toy)
    assert "developer" not in out and "cluster" not in out
    assert out["service"].tolist() == ["NRIS", "missing"]
    assert out["county"].tolist() == ["missing", "Kern"]


def test_r9_flags_hybrids():
    toy = pd.DataFrame({"type2": ["Battery", None], "mw2": [None, None]})
    out, touched = cleaning.r9_hybrid(toy)
    assert out["hybrid"].tolist() == [True, False]
    assert touched["hybrid without mw2 (second capacity unknown)"] == 1


# --- the real clean table (after notebook 01 (part B)) -------------------------------

@pytest.fixture(scope="module")
def clean():
    return _load_or_skip(CLEAN_FILE, pd.read_parquet, "02")


def test_no_serial_number_dates(clean):
    for column in ["q_date", "prop_date", "on_date", "wd_date", "ia_date"]:
        assert pd.api.types.is_datetime64_any_dtype(clean[column]), column


def test_event_dates_agree_with_status(clean):
    assert clean.loc[clean["q_status"] != "operational", "on_date"].isna().all()
    assert clean.loc[clean["q_status"] != "withdrawn", "wd_date"].isna().all()
    assert not (clean["on_date"] < clean["q_date"]).any()
    assert not (clean["wd_date"] < clean["q_date"]).any()


def test_capacity_positive_and_key_unique(clean):
    assert (clean["mw"] > 0).all()
    assert clean["project_key"].is_unique


def test_clean_log_counts():
    """Pin the rows each rule touched (the rule table of PLAN.md §7, as observed)."""
    log = _load_or_skip(LOG_FILE, pd.read_csv, "02")
    rows = dict(zip(log["item"], log["rows"]))
    assert rows["q_date placeholder set to missing"] == 204
    assert rows["on_date cleared: status is not operational"] == 596
    assert rows["on_date cleared: before the request date"] == 69
    assert rows["wd_date cleared: status is not withdrawn"] == 23
    assert rows["wd_date cleared: before the request date"] == 4
    assert sum(v for k, v in rows.items() if k.startswith("dropped: project_type")) == 208
    assert rows["dropped: mw ≤ 0 or missing"] == 16  # 17 in the raw file; one is an Upgrade row R5 removes
    assert rows["flagged: mw > 5,000"] == 2
    assert rows["dropped: duplicate without a request date"] == 1
    assert log["rows_out"].iloc[-1] == 36216
