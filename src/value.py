"""The value and cost layer: what a MW online is worth, by region, technology and year, and what a request costs to carry.

What: parsers for the public sources on disk (EIA's ICE wholesale price
files, the PJM market monitor's capacity-revenue table, EIA generation for
capacity factors, LBNL's PJM interconnection-cost data), one explicit
value formula per MW-year with low / base / high settings, and the
expected value of a request from its P(operation by year) curve.
Why: a portfolio needs more than a probability — expected MW online and a
value behind each request — and every number in that value must trace to
a file on disk or to an assumption stated in `results/value_assumptions.csv`
with its range (PLAN.md, notebook 07).
Reads: ``data/raw/value/ice_electric-<year>final.xlsx`` (EIA, public
domain), ``data/raw/atb/ATBe_2024_v3.parquet`` (NREL Annual Technology
Baseline 2024, v3; CAPEX and O&M per kW), ``data/raw/value/2024-som-pjm-sec5.pdf`` (Monitoring Analytics,
2024 State of the Market, Section 5), ``data/raw/lbnl_costs/pjm_costs_2022_clean_data.xlsx``
(LBNL), EIA API responses cached by notebook 07.
Writes: nothing.
Used by: notebooks 07 and 09; ``tests/test_value.py``.
"""

import glob
import pathlib
import re
import subprocess

import numpy as np
import pandas as pd

from src import config, paths

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
    from src import features  # local import: the size regime rule of notebook 03
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
    report compares books, not absolute worth (stated in notebook 07).
    """
    p = np.asarray(p_by_year, dtype=float)
    increments = np.diff(np.concatenate([[0.0], p]))
    values = np.asarray(values_by_year, dtype=float)
    earned = np.array([values[j:].sum() for j in range(len(increments))])
    return float((increments * earned).sum() * mw - sunk_cost)


RAW_ATB = paths.DATA_RAW / "atb" / config.ATB_FILENAME
# LBNL technology group → the ATB technology and the one representative detail row used for its costs.
# Defaults are ATB's own (``default == 1``) where one exists; gas has none, so the F-frame 2-on-1 combined
# cycle is taken as the common new-build; "Other" (hydro, nuclear, coal, geothermal, biomass) takes the median
# of the six mapped groups, stated as such.
ATB_MAP = {
    "Solar": ("UtilityPV", "Class5"),
    "Solar+Battery": ("Utility-Scale PV-Plus-Battery", "Class5"),
    "Wind": ("LandbasedWind", "Class4"),
    "Offshore Wind": ("OffShoreWind", "Class3"),
    "Battery": ("Utility-Scale Battery Storage", "4Hr Battery Storage"),
    "Gas": ("NaturalGas_FE", "NG 2-on-1 Combined Cycle (F-Frame)"),
}
ATB_PARAMETERS = {"CAPEX": "capex_per_kw", "Fixed O&M": "fom_per_kw_year", "Variable O&M": "vom_per_mwh", "Heat Rate": "heat_rate_mmbtu_per_mwh"}


def fetch_atb(dest=RAW_ATB):
    """Download the ATB parquet if it is not on disk, and verify its SHA-256 either way.

    Notes
    -----
    The raw file is not committed (data/README.md, S12); this makes a fresh
    clone rebuild notebook 07 without a manual step. A hash mismatch stops
    the run rather than valuing plants on a file that is not the one the
    report used.
    """
    import hashlib

    import requests

    dest = pathlib.Path(dest)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(config.ATB_URL, timeout=300)
        response.raise_for_status()
        dest.write_bytes(response.content)
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    if digest != config.ATB_SHA256:
        raise RuntimeError(f"{dest.name}: SHA-256 {digest[:16]}… differs from the recorded {config.ATB_SHA256[:16]}…")
    return dest


def atb_costs(file=RAW_ATB, year=2024, scenario="Moderate", case="Market", crp="20"):
    """Overnight capital and operating costs per technology group from the NREL ATB.

    Parameters
    ----------
    file : path
        The ATB electricity parquet (``data/raw/atb/``).
    year : int
        ATB projection year to read (the cost of a plant built in that year).
    scenario, case, crp : str
        ATB's Moderate scenario, Market financial case, 20-year cost-recovery period.

    Returns
    -------
    pandas.DataFrame
        Index = LBNL technology group; ``capex_per_kw`` ($2022/kW),
        ``fom_per_kw_year`` ($2022/kW-year), ``vom_per_mwh`` ($2022/MWh, 0
        where ATB gives none), ``heat_rate_mmbtu_per_mwh`` (gas only),
        ``atb_technology`` and ``atb_detail``.

    Notes
    -----
    One representative class per technology (``ATB_MAP``): a capstone-scale
    cost, not a site estimate. Costs are in 2022 dollars while the value
    table is in the dollars of each year; the mismatch is a few percent and
    is stated in notebook 07. Battery CAPEX is per kW of a four-hour system.
    """
    d = pd.read_parquet(file)
    d = d[(d["scenario"] == scenario) & (d["core_metric_case"] == case) & (d["crpyears"] == str(crp))
          & (d["core_metric_variable"] == year) & d["core_metric_parameter"].isin(ATB_PARAMETERS)]
    rows = {}
    for group, (tech, detail) in ATB_MAP.items():
        part = d[(d["technology"] == tech) & (d["techdetail"] == detail)]
        values = part.groupby("core_metric_parameter")["value"].first()
        rows[group] = {ATB_PARAMETERS[p]: float(values.get(p, np.nan)) for p in ATB_PARAMETERS}
        rows[group].update({"atb_technology": tech, "atb_detail": detail})
    out = pd.DataFrame(rows).T
    numeric = list(ATB_PARAMETERS.values())
    out[numeric] = out[numeric].astype(float)
    out.loc["Other", numeric] = out[numeric].median()
    out.loc["Other", ["atb_technology", "atb_detail"]] = ["median of the six mapped groups", ""]
    out["vom_per_mwh"] = out["vom_per_mwh"].fillna(0.0)
    out["heat_rate_mmbtu_per_mwh"] = out["heat_rate_mmbtu_per_mwh"].fillna(0.0)
    out.index.name = "tech"
    return out


def npv_per_mw(revenue_by_year, capex_per_kw, fom_per_kw_year, variable_per_mwh, mwh_per_mw_year, rate=0.08, life=20):
    """Net present value of one MW at its commercial operation date: −CAPEX + Σ (revenue − O&M − variable cost)/(1+r)^t.

    Parameters
    ----------
    revenue_by_year : array-like
        $/MW-year of value for operating years 1 … ``life`` (from the value
        table, held at its last year beyond the table).
    capex_per_kw, fom_per_kw_year : float
        $/kW and $/kW-year (ATB).
    variable_per_mwh : float
        $/MWh of generation: variable O&M plus fuel (heat rate × gas price)
        for gas; 0 for the rest.
    mwh_per_mw_year : float
        Generation per MW-year (capacity factor × 8,760); 0 for storage,
        whose value in the table is capacity revenue only.
    rate : float
        Real discount rate; 8% base, 6% and 10% as cases (notebook 07).
    life : int
        Operating years valued.

    Returns
    -------
    float
        $ per MW at the operation date; negative when the plant does not
        earn back its capital at this rate.

    Notes
    -----
    The simplest form of a project DCF: no financing structure, no tax
    depreciation, no degradation, no terminal value. Enough to rank
    technologies and regions and to put a sign on a request; not enough to
    price one, which the report says.
    """
    revenue = np.asarray(revenue_by_year, dtype=float)
    assert len(revenue) == life, "one revenue value per operating year"
    cash = revenue - fom_per_kw_year * 1000 - variable_per_mwh * mwh_per_mw_year
    discount = (1 + rate) ** np.arange(1, life + 1)
    return float(-capex_per_kw * 1000 + (cash / discount).sum())


def atb_capacity_factors(file=RAW_ATB, year=2024, scenario="Moderate", case="Market", crp="20"):
    """Design capacity factor of a new plant per technology group, from the same ATB rows as ``atb_costs``.

    Returns
    -------
    dict
        Technology group -> capacity factor, for the groups whose ATB class
        carries one (solar, hybrid, wind, offshore wind). Gas and storage have
        none in the ATB; notebook 07 states what it uses for them.

    Notes
    -----
    Used for the NPV only. The value table of notebook 07 keeps the fleet
    capacity factors of EIA data (2024 generation over 2026 nameplate), which
    describe the plants that exist; a plant built today is designed to the
    class figure, and the two differ by a factor of two for PJM solar.
    """
    d = pd.read_parquet(file)
    d = d[(d["scenario"] == scenario) & (d["core_metric_case"] == case) & (d["crpyears"] == str(crp))
          & (d["core_metric_variable"] == year) & (d["core_metric_parameter"] == "CF")]
    out = {}
    for group, (tech, detail) in ATB_MAP.items():
        part = d[(d["technology"] == tech) & (d["techdetail"] == detail)]
        if len(part):
            out[group] = float(part["value"].iloc[0])
    return out


def atb_wacc(file=RAW_ATB, year=2024, case="Market", crp="20"):
    """Real weighted average cost of capital per technology group from the ATB's Market financing case.

    Returns
    -------
    dict
        Technology group -> real WACC (a fraction). "Other" takes the median
        of the mapped groups; battery storage, which the ATB prices without a
        financing row in this filter, takes the solar rate (it is financed
        with the same tax-equity structures).

    Notes
    -----
    Practice discounts operating cash flows at the project's cost of capital
    and carries the chance of never reaching operation as a probability, not
    as a higher rate; the gate rule of notebook 09 (part A) has that shape. The ATB
    Market case gives 4.2% real for utility solar and hybrids, 4.9% for land
    wind, 5.2% for offshore wind and 5.4% for gas (2024 values).
    """
    d = pd.read_parquet(file)
    d = d[(d["core_metric_case"] == case) & (d["crpyears"] == str(crp)) & (d["core_metric_variable"] == year)
          & (d["core_metric_parameter"] == "WACC Real")]
    out = {}
    for group, (tech, _) in ATB_MAP.items():
        part = d[d["technology"] == tech]
        if len(part):
            out[group] = float(part["value"].iloc[0])
    out.setdefault("Battery", out["Solar"])
    out["Other"] = float(np.median(list(out.values())))
    return out

