"""Tests that pin the raw-file audit and, from notebook 02 on, the cleaning rules.

``test_audit_counts`` compares ``results/audit_counts.json`` (written by
notebook 01) with the counts of the 2026-10-03 audit, typed in here by hand
so the test does not share a constant with the code it checks.
"""

import json

import pytest

from src import paths

AUDIT_FILE = paths.RESULTS / "audit_counts.json"


@pytest.fixture(scope="module")
def audit():
    if not AUDIT_FILE.exists():
        pytest.skip("results/audit_counts.json missing — run notebook 01 first")
    return json.loads(AUDIT_FILE.read_text(encoding="utf-8"))


def test_audit_counts(audit):
    assert (audit["n_rows"], audit["n_cols"]) == (36441, 31)
    assert audit["q_status"] == {"withdrawn": 20921, "active": 10538, "operational": 4432,
                                 "suspended": 546, "unknown": 4}
    assert audit["region"] == {"PJM": 8152, "West": 7675, "MISO": 4978, "Southeast": 3950,
                               "ERCOT": 3282, "CAISO": 2837, "SPP": 2469, "NYISO": 1817,
                               "ISO-NE": 1281}
    assert audit["placeholder_q_date"] == 204
    assert audit["negative_mw_rows"] == 17
