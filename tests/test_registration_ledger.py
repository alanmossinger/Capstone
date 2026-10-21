"""The registration ledger holds every registered line once, and a correction never changes a registered verdict."""

import pandas as pd

from src import registration_ledger as rl


def test_every_criterion_appears_and_the_lines_are_counted_as_registered():
    ledger = rl.build()
    assert {f"C{i}" for i in range(1, 33)} <= set(ledger["criterion"])
    lines = ledger.groupby(["criterion", "line"]).ngroups
    assert lines == 78  # 70 lines of C1–C24 (report v9, Appendix A) and the 8 of C25–C32


def test_registered_verdicts_match_the_files_they_cite():
    ledger = rl.build().set_index(["criterion", "line"])
    c21 = ledger.loc[("C21", "D vs A, out-of-sample metric")]
    assert (c21["registered_verdict"] == "FAIL").all()  # the bridged-price scoring, as first registered
    after = c21.set_index("correction_date")["verdict_after"]
    assert after["2026-10-14"] == "FAIL" and after["2026-10-20"] == "PASS"  # observed prices; the corrected system
    c25 = ledger.loc["C25"]
    assert (c25["registered_verdict"] == "PASS").all() and (c25["status"] == rl.AS_REGISTERED).all()
    c1 = ledger.loc["C1"]
    assert len(c1) == 3 and set(c1["registered_verdict"]) <= {"PASS", "FAIL"}


def test_a_correction_always_carries_a_date_and_a_decision():
    ledger = rl.build()
    corrected = ledger[ledger["correction"] != ""]
    assert (corrected["correction_date"] != "").all() and (corrected["decision"] != "").all()
    assert ledger.loc[ledger["correction"] == "", "status"].eq(rl.AS_REGISTERED).all()
