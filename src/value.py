"""The value and cost layer: what a MW online is worth, by region, technology and year, and what a request costs to carry.

What: parsers for the public sources on disk (EIA's ICE wholesale price
files, the PJM market monitor's capacity-revenue table, EIA generation for
capacity factors, LBNL's PJM interconnection-cost data), one explicit
value formula per MW-year with low / base / high settings, and the
expected value of a request from its P(operation by year) curve.
Why: a portfolio needs more than a probability — expected MW online and a
value behind each request — and every number in that value must trace to
a file on disk or to an assumption stated in `results/value_assumptions.csv`
with its range (PLAN.md, notebook 15).
Reads: ``data/raw/value/ice_electric-<year>final.xlsx`` (EIA, public
domain), ``data/raw/value/2024-som-pjm-sec5.pdf`` (Monitoring Analytics,
2024 State of the Market, Section 5), ``data/raw/lbnl_costs/pjm_costs_2022_clean_data.xlsx``
(LBNL), EIA API responses cached by notebook 15.
Writes: nothing.
Used by: notebooks 15 and 16; ``tests/test_value.py``.
"""

import glob
import re
import subprocess

import numpy as np
import pandas as pd

from src import paths

RAW_VALUE = paths.DATA_RAW / "value"
RAW_COSTS = paths.DATA_RAW / "lbnl_costs"
HOURS_PER_YEAR = 8760
# EIA ICE price hubs standing in for each region's energy price (on-peak, $/MWh)
HUB_BY_REGION = {"PJM": "PJM WH Real Time Peak", "CAISO": "SP15 EZ Gen DA LMP Peak", "ERCOT": "ERCOT North 345KV Peak"}


def ice_hub_prices(folder=RAW_VALUE):
    """Volume-weighted annual average on-peak price per ICE hub, $/MWh, from EIA's files.

    Returns
    -------
    pandas.DataFrame
        Index hub, columns year; NaN where the hub has no trades that year
        (ERCOT North stops after 2019 in these files).

    Notes
    -----
    EIA republishes ICE's daily traded prices (weighted average, volume);
    the annual value here weights each day's price by its traded volume.
    On-peak hubs overstate the round-the-clock price a plant earns, which
    the technology capture factors of ``value_per_mw_year`` correct for.
    """
    frames = []
    for file in sorted(glob.glob(str(folder / "ice_electric-*final.xlsx"))):
        d = pd.read_excel(file, sheet_name=0)
        d.columns = [str(c).replace("\n", " ").strip() for c in d.columns]
        d["year"] = int(re.search(r"(\d{4})final", file).group(1))
        frames.append(d[["Price hub", "year", "Wtd avg price $/MWh", "Daily volume MWh"]])
    d = pd.concat(frames, ignore_index=True)
    for column in ["Wtd avg price $/MWh", "Daily volume MWh"]:
        d[column] = pd.to_numeric(d[column], errors="coerce")
    d = d.dropna()
    d["weighted"] = d["Wtd avg price $/MWh"] * d["Daily volume MWh"]
    grouped = d.groupby(["Price hub", "year"])
    return (grouped["weighted"].sum() / grouped["Daily volume MWh"].sum()).unstack("year")


def pjm_capacity_revenue(pdf=RAW_VALUE / "2024-som-pjm-sec5.pdf"):
    """PJM's cleared-UCAP-weighted average RPM price by calendar year, $/MW-day (Table 5-23 of the 2024 SOM).

    Returns
    -------
    pandas.Series
        Index calendar year 2007 … 2026 (2026 partial: 151 effective days),
        values $ per MW-day.

    Notes
    -----
    The table is read from the PDF's text (``pdftotext``), not typed: the
    years run as one list and the prices as another, in the same order.
    """
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout
    start = text.rfind("Table 5-23 RPM revenue by calendar year")
    block = text[start:start + 3000]
    year_list = block.split("Year", 1)[1].split("Weighted Average")[0]  # the list after the "Year" header, before the price header
    years = [int(y) for y in re.findall(r"\b(20[0-2]\d)\b", year_list)]
    prices = [float(p.replace(",", "")) for p in re.findall(r"\$(\d{2,3}\.\d{2})\b", block.split("Effective Days")[0])]
    assert len(years) == len(prices) == 20, f"unexpected table shape: {len(years)} years, {len(prices)} prices"
    return pd.Series(prices, index=pd.Index(years, name="year"), name="usd_per_mw_day")


ELCC_CLASSES = ["Onshore Wind", "Offshore Wind", "Solar Fixed", "Solar Tracking", "Landfill", "Intermittent Hydro",
                "4-hr Storage", "6-hr Storage", "8-hr Storage", "10-hr Storage", "Demand Response", "Nuclear", "Coal",
                "Gas Combined Cycle", "Gas Combustion Turbine", "Gas Combustion Turbine Dual Fuel", "Diesel", "Utility Steam"]


def pjm_elcc_ratings(pdf=RAW_VALUE / "2024-som-pjm-sec5.pdf"):
    """PJM's final marginal ELCC class ratings for the 2025/2026 delivery year (Table 5-13 of the 2024 SOM, Jan 23, 2025 column).

    Returns
    -------
    pandas.Series
        Index ELCC class, values fraction of nameplate accredited as capacity.

    Notes
    -----
    The table lists three ratings per class for 2025/2026 (the BRA, the
    December 31, 2024 posting and the final January 23, 2025 posting); the
    final one is kept. Read from the PDF's text, not typed.
    """
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout
    start = text.find("Table 5-13 Marginal ELCC ratings for the 2025/2026 Delivery Year")
    block = text[start:start + 4000]
    after = block[block.find("Jan 23, 2025"):]
    values = [int(v) / 100 for v in re.findall(r"(\d{1,3})%", after)[:3 * len(ELCC_CLASSES)]]
    assert len(values) == 3 * len(ELCC_CLASSES), f"expected {3 * len(ELCC_CLASSES)} ratings, found {len(values)}"
    return pd.Series(values[2::3], index=pd.Index(ELCC_CLASSES, name="elcc_class"), name="accreditation")


def capacity_factors(generation, capacity):
    """Capacity factor by (state, technology) = annual generation / (nameplate × 8760).

    Parameters
    ----------
    generation : pandas.DataFrame
        ``state``, ``tech``, ``mwh`` (one year, from the EIA API).
    capacity : pandas.DataFrame
        ``state``, ``tech``, ``mw`` (nameplate of operating generators,
        EIA-860M).

    Returns
    -------
    pandas.DataFrame
        ``state``, ``tech``, ``capacity_factor`` clipped to [0, 1].
    """
    out = generation.merge(capacity, on=["state", "tech"], how="inner")
    out["capacity_factor"] = (out["mwh"] / (out["mw"] * HOURS_PER_YEAR)).clip(0, 1)
    return out[["state", "tech", "mwh", "mw", "capacity_factor"]]


def pjm_cost_table(file=RAW_COSTS / "pjm_costs_2022_clean_data.xlsx"):
    """LBNL's project-level PJM interconnection cost estimates, $2022 per kW, with the request's size band."""
    from src import features  # local import: the size regime rule of notebook 04
    d = pd.read_excel(file, sheet_name="data")
    d = d.rename(columns={"Project #": "q_id", "Nameplate MW": "mw", "$2022 Total Cost/kW": "total_cost_per_kw",
                          "$2022 Network Cost/kW": "network_cost_per_kw", "$2022 POI Cost/kW": "poi_cost_per_kw",
                          "Study Type": "study_type", "Study Date": "study_date", "Fuel": "fuel", "Request Status": "status"})
    d["q_id"] = d["q_id"].astype(str).str.strip()
    d["size_regime"] = features.size_regime(d["mw"])
    return d


def value_per_mw_year(region, tech, year, inputs, case="base"):
    """Value of one MW online for one year, $/MW-year: energy + capacity + credit.

    Parameters
    ----------
    region, tech, year : str, str, int
    inputs : dict
        ``energy_price`` (region → year → $/MWh), ``capacity_factor``
        (tech → fraction), ``capture`` (tech → fraction of the on-peak price
        the technology earns), ``capacity_price`` (region → year →
        $/kW-year), ``accreditation`` (tech → fraction of nameplate that
        counts as capacity), ``credit`` (tech → $/MWh, 0 when the
        technology or the year is not eligible), ``multiplier`` (case →
        {"energy", "capacity", "credit"} scaling for low / base / high).
    case : {"low", "base", "high"}

    Returns
    -------
    float

    Notes
    -----
    energy = CF × 8760 × price × capture; capacity = accreditation × 1000 kW
    × capacity price; credit = CF × 8760 × credit rate. Each term is scaled
    by the case multiplier so a sensitivity run moves the three sources of
    value separately.
    """
    m = inputs["multiplier"][case]
    cf = inputs["capacity_factor"].get(tech, 0.0)
    price = inputs["energy_price"].get(region, {}).get(year, np.nan)
    energy = cf * HOURS_PER_YEAR * price * inputs["capture"].get(tech, 1.0) * m["energy"]
    cap_price = inputs["capacity_price"].get(region, {}).get(year, 0.0)
    capacity = inputs["accreditation"].get(tech, 0.0) * 1000 * cap_price * m["capacity"]
    credit = cf * HOURS_PER_YEAR * inputs["credit"].get(tech, 0.0) * m["credit"]
    return float(energy + capacity + credit)


def expected_value(p_by_year, mw, values_by_year, sunk_cost):
    """Expected value of a request: Σ_year P(operates in that year) × MW × Σ later annual values − sunk cost.

    Parameters
    ----------
    p_by_year : array-like
        P(operation by year 1, 2, …, H) (cumulative incidence from the decision point).
    mw : float
    values_by_year : array-like
        $/MW-year for the years 1 … H + L the plant would run (from the
        value table; the plant earns from its operation year to the end of
        the valuation window).
    sunk_cost : float
        Cost committed between the decision point and the next gate.

    Notes
    -----
    The incidence curve's yearly increments are the probabilities of
    operating in each year; a plant that starts in year j earns the values
    of years j … end of window. No discounting: the window is short and the
    report compares books, not absolute worth (stated in notebook 15).
    """
    p = np.asarray(p_by_year, dtype=float)
    increments = np.diff(np.concatenate([[0.0], p]))
    values = np.asarray(values_by_year, dtype=float)
    earned = np.array([values[j:].sum() for j in range(len(increments))])
    return float((increments * earned).sum() * mw - sunk_cost)
