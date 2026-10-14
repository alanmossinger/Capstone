"""The ERCOT historical-price parser: the report's sheet layout becomes the gridstatus layout, with the fall-back hour resolved."""

import io
import zipfile

import pandas as pd

from src import ercot_history


def workbook_bytes():
    """A two-sheet workbook in the report's layout: the 2020 fall-back day (1 November) and one ordinary day."""
    rows = []
    for point, price in (("HB_NORTH", 20.0), ("LZ_HOUSTON", 22.5)):
        for hour in range(1, 26):  # 25 hour-ending rows on the fall-back day: 02:00 appears twice, the second flagged
            he = min(hour, 24) if hour < 3 else hour - 1
            rows.append({"Delivery Date": "11/01/2020", "Hour Ending": f"{he:02d}:00", "Repeated Hour Flag": "Y" if hour == 3 else "N",
                         "Settlement Point": point, "Settlement Point Price": price + hour})
    nov = pd.DataFrame(rows)
    dec = pd.DataFrame({"Delivery Date": ["12/01/2020"] * 2, "Hour Ending": ["01:00", "24:00"], "Repeated Hour Flag": ["N", "N"],
                        "Settlement Point": ["HB_NORTH", "HB_NORTH"], "Settlement Point Price": [30.0, 31.0]})
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        nov.to_excel(writer, sheet_name="Nov", index=False)
        dec.to_excel(writer, sheet_name="Dec", index=False)
    return buffer.getvalue()


def test_parse_workbook_gives_the_gridstatus_layout_and_resolves_the_repeated_hour():
    table = ercot_history.parse_workbook(workbook_bytes())
    assert list(table.columns) == ercot_history.COLUMNS
    assert str(table["Interval Start"].dt.tz) == "US/Central"
    north = table[table["Location"] == "HB_NORTH"]
    assert len(north) == 25 + 2 and north["Interval Start"].is_unique  # the repeated 01:00 hour is two distinct instants
    offsets = north["Interval Start"].dt.strftime("%z")
    assert set(offsets) == {"-0500", "-0600"}  # daylight time before the fall-back, standard after
    assert (table["Interval End"] - table["Interval Start"] == pd.Timedelta(hours=1)).all()
    assert table.loc[table["Location"] == "LZ_HOUSTON", "Location Type"].iloc[0] == "Load Zone"
    assert table.loc[table["Location"] == "HB_NORTH", "Location Type"].iloc[0] == "Trading Hub"
    assert (table["Market"] == "DAY_AHEAD_HOURLY").all()


def test_parse_workbook_unwraps_the_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("rpt.00013060.0000000000000000.DAMLZHBSPP_2020.xlsx", workbook_bytes())
    table = ercot_history.parse_workbook(buffer.getvalue())
    assert len(table) == 25 * 2 + 2
