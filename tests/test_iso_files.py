"""Tests for src/iso_files.py: the PJM XML and ERCOT GIS readers on small hand-made files."""

import pandas as pd

from src import iso_files

PJM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Projects>
  <Project><ProjectNumber>AE1-001</ProjectNumber><Status>Withdrawn</Status><ProjectType>Generation Interconnection</ProjectType>
    <SubmittedDate>4/1/2018</SubmittedDate><WithdrawalDate>6/30/2020</WithdrawalDate><ActualInServiceDate></ActualInServiceDate>
    <SystemImpactStudyStatus>Document Posted</SystemImpactStudyStatus>
    <Interim-InterconnectionService-GenerationInterconnectionAgreement-Status>N/A</Interim-InterconnectionService-GenerationInterconnectionAgreement-Status>
  </Project>
  <Project><ProjectNumber>AE1-002</ProjectNumber><Status>In Service</Status><ProjectType>Generation Interconnection</ProjectType>
    <SubmittedDate>5/2/2018</SubmittedDate><WithdrawalDate>N/A</WithdrawalDate><ActualInServiceDate>12/1/2021</ActualInServiceDate>
    <BackfeedDate>9/1/2021</BackfeedDate>
    <Interim-InterconnectionService-GenerationInterconnectionAgreement-Status>Document Posted</Interim-InterconnectionService-GenerationInterconnectionAgreement-Status>
  </Project>
</Projects>"""


def test_pjm_reader_parses_dates_and_blanks(tmp_path):
    path = tmp_path / "pjm.xml"
    path.write_text(PJM_XML, encoding="utf-8")
    out = iso_files.read_pjm_queue(path).set_index("q_id")
    assert out.loc["AE1-001", "submitted_date"] == pd.Timestamp("2018-04-01")
    assert out.loc["AE1-001", "withdrawal_date"] == pd.Timestamp("2020-06-30")
    assert pd.isna(out.loc["AE1-002", "withdrawal_date"])  # "N/A" is missing, not a date
    assert pd.isna(out.loc["AE1-001", "isa_status"])
    assert out.loc["AE1-002", "isa_status"] == "Document Posted"
    assert pd.isna(out.loc["AE1-001", "backfeed_date"])  # a field absent from a project is missing


def _sheet(header, rows, pad=3):
    """A GIS-style sheet: a title block of ``pad`` rows, then the header, then the rows."""
    blank = [[None] * len(header) for _ in range(pad)]
    return pd.DataFrame(blank + [header] + rows)


def test_ercot_reader_finds_header_and_tags_sheet(tmp_path):
    path = tmp_path / "gis.xlsx"
    large = _sheet(["INR", "GIM Study Phase", "Capacity (MW)", "FIS Approved", "IA Signed"],
                   [["19INR0001", "SS Completed, FIS Completed, IA", 150.0, "2020-01-15", "2020-06-01"],
                    ["19INR0002", "SS Completed, FIS Started, No IA", 80.0, None, None]])
    small = _sheet(["INR", "GIM Study Phase", "Capacity (MW)"], [["19INR0003", "SS Completed", 9.0]])
    inactive = _sheet(["INR", "Inactive Date", "MW **"], [["17INR0009", "2019-09-09"]], pad=5)
    cancelled = _sheet(["INR", "Cancel Date", "MW **"], [["19INR0001", "2026-09-01", 150.0]], pad=5)
    with pd.ExcelWriter(path) as writer:
        for name, frame in [("Project Details - Large Gen", large), ("Project Details - Small Gen", small),
                            ("Inactive Projects", inactive), ("Cancellation Update", cancelled)]:
            frame.to_excel(writer, sheet_name=name, header=False, index=False)
    out = iso_files.read_ercot_gis(path).set_index("q_id")
    assert out.loc["19INR0001", "listed_as"] == "active (large)"  # first listing kept when a request appears twice
    assert out.loc["19INR0001", "ia_signed"] == pd.Timestamp("2020-06-01")
    assert pd.isna(out.loc["19INR0002", "fis_approved"])
    assert out.loc["19INR0003", "listed_as"] == "active (small)"
    assert out.loc["17INR0009", "inactive_date"] == pd.Timestamp("2019-09-09")
    assert len(out) == 4
