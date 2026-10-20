"""Scenario valuation of the forty candidates: one engine for the flat path, the scenarios and every what-if.

What: the present-value components of a new ERCOT plant per MW (revenue on
the 2024 hourly basis, the fixed PPA years, fuel, capital and fixed costs,
the tax credits), the NPV of every power request and every lease
redevelopment in every price scenario, and the expected NPV of a request on
the flat path from its chance of operating by year.
Why: the repricing lived only inside notebook 08 (audit S2), so no price,
cost or credit question could be answered without rerunning a notebook; the
decision layers of v8 (what-ifs, re-optimization, value of information) call
these functions directly. Since decision #90 every request is valued from
1 January 2025, its operation year j = 1 … 7 counted from that date, and since
decision #94 its credits are those of the law in force on that date.
Reads / writes: nothing; notebooks 07 and 08 and `src/whatif.py` pass the tables in.
Used by: notebooks 07 and 08, `src/whatif.py`; `tests/test_valuation.py`.
"""

import numpy as np
import pandas as pd

from src import config, economics as ec

TECH_OF = {"Gas CC": "Gas", "Solar": "Solar", "Wind": "Wind", "Storage": "Battery"}  # candidate technology -> ATB technology
PPA = {"Solar": 57.0, "Wind": 62.0}  # $/MWh, the index-level contract of part A (decision #61)
PPA_YEARS = 15  # years under contract in the contracted case
LIFE = 20  # operating years valued
PTC_PER_MWH = 27.5  # IRC §45Y base rate, $/MWh, first ten operating years (results/value_assumptions.csv)
PTC_YEARS = 10
ITC_SHARE = 0.30  # IRC §48E base rate on capital
CREDIT_POLICIES = {  # the last calendar year in which a wind or solar plant entering operation earns its credit, by policy
    "in force": None,  # the law on 1 January 2025: the §45Y/§48E credits phase down no earlier than after 2032, beyond the seven-year window
    "2025 law": 2027,  # the July 2025 law and IRS Notice 2025-42 (August 2025), after the decision date: in service by the end of 2027; a policy stress
}
CREDIT_POLICY = "in force"  # the base case: only the law in force on the decision date (decision #94; review of 19 October, §2.1)
CREDIT_OF = {"Wind": "ptc", "Solar": "itc", "Battery": "itc"}  # wind takes the production credit, solar and storage the investment credit (part A's election)
DECISION_YEAR = int(config.DECISION_DATE[:4])  # operation year 1 is this calendar year


def cpi_ratio(cpi, from_year, to_year):
    """Ratio of annual-mean CPI-U, ``to_year`` over ``from_year`` (2024 / 2022 converts the ATB's 2022 dollars)."""
    annual = cpi.groupby(cpi["month"].dt.year)["cpi_u"].mean()
    return float(annual.loc[to_year] / annual.loc[from_year])


def atb_in_dollars_of(atb, ratio):
    """The ATB table with capital, fixed and variable O&M multiplied by ``ratio`` (heat rates and rates untouched).

    Notes
    -----
    Part II states every cash flow in 2024 dollars; the ATB 2024 file is in
    2022 dollars and was used unconverted until the 17 October audit (E7).
    """
    out = atb.copy()
    for column in ("capex_per_kw", "fom_per_kw_year", "vom_per_mwh"):
        out[column] = out[column] * ratio
    return out


def credit_eligible(tech, calendar_year, policy=CREDIT_POLICY):
    """True when a plant of ATB technology ``tech`` entering operation in ``calendar_year`` earns its credit under ``policy``.

    Notes
    -----
    The base case is the law in force on the decision date, under which no
    wind or solar plant entering operation in the seven-year window loses its
    credit. The 2027 deadline of the July 2025 law (IRS Notice 2025-42) was
    not law on 1 January 2025; the first v8 run applied it as certain, a
    look-ahead (review of 19 October, §2.1). It is kept as the "2025 law"
    stress, the policy risk a committee could see after the November 2024
    election. Storage keeps its investment credit in both (ASSUMED: the 2025
    law ended the credits for wind and solar, not storage); gas earns none.
    """
    if tech not in CREDIT_OF:
        return False
    last = CREDIT_POLICIES[policy]
    return tech == "Battery" or last is None or calendar_year <= last


def credit_policy_of(credits):
    """The credit policy a ``credits`` argument names: True is the base case, False no credits, a string a policy of ``CREDIT_POLICIES``."""
    if credits is True:
        return CREDIT_POLICY
    if credits is False:
        return None
    if credits not in CREDIT_POLICIES:
        raise ValueError(f"unknown credit policy {credits!r}; one of {list(CREDIT_POLICIES)}")
    return credits


def basis_2024(hub, solar_shape, wind_shape, atb, hh_base):
    """The 2024 ERCOT revenue basis: capture factors, the gas plant's running hours and the battery's arbitrage."""
    gas_mc = atb.loc["Gas", "heat_rate_mmbtu_per_mwh"] * hh_base + atb.loc["Gas", "vom_per_mwh"]
    capture = ec.capture_factors(hub, solar_shape, wind_shape, gas_marginal_cost=gas_mc)
    return {"capture": capture, "battery_revenue": ec.battery_annual_revenue(hub, hours=4, efficiency=0.85, cycles=1.0), "gas_mc": gas_mc}


def pv_components(tech, atb, basis, ercot_base, hh_base):
    """Present values per MW at the operation date of a new plant of ATB technology ``tech``.

    Returns
    -------
    dict
        ``pv_rev`` (merchant revenue, all years), ``pv_ppa_fixed`` and
        ``pv_tail`` (the contract years at the PPA price and the merchant years
        after them), ``pv_fuel``, ``pv_fixed`` (capital plus fixed and variable
        O&M), ``pv_credit`` (the credit if earned), ``rate``, ``mwh`` and
        ``cf_scales`` (output varies with the scenario's capacity factor).

    Notes
    -----
    The same DCF as ``value.npv_per_mw``: capital at the operation date, then
    operating years 1 … 20 discounted at the ATB real rate. The production
    credit is $27.5/MWh on the first ten years' output; the investment credit
    is 30% of capital, received at the operation date. No income tax or
    depreciation is modelled, so the credits enter as cash (a simplification
    stated in the report).
    """
    a = atb.loc[tech]
    r = float(a["wacc_real"])
    years = np.arange(1, LIFE + 1)
    disc = (1 + r) ** years
    cap = basis["capture"]
    if tech == "Battery":
        rev, mwh = basis["battery_revenue"], 0.0
    else:
        cf = cap["gas_hours_share"] if tech == "Gas" else a["new_build_cf"]
        mwh = cf * 8760
        rev = ercot_base * {"Gas": cap["gas"], "Solar": cap["solar"], "Wind": cap["wind"]}[tech] * mwh
    contract = years <= PPA_YEARS
    pv_rev = float((rev / disc).sum())
    pv_ppa_fixed = float((np.where(contract, PPA[tech] * mwh, 0.0) / disc).sum()) if tech in PPA else 0.0
    pv_tail = float((np.where(contract, 0.0, rev) / disc).sum()) if tech in PPA else pv_rev
    fuel = a["heat_rate_mmbtu_per_mwh"] * hh_base * mwh if tech == "Gas" else 0.0
    pv_fuel = float((fuel / disc).sum())
    pv_fixed = float(a["capex_per_kw"] * 1000 + ((a["fom_per_kw_year"] * 1000 + a["vom_per_mwh"] * mwh) / disc).sum())
    credit = CREDIT_OF.get(tech)
    if credit == "ptc":
        pv_credit = float((np.where(years <= PTC_YEARS, PTC_PER_MWH * mwh, 0.0) / disc).sum())
    elif credit == "itc":
        pv_credit = float(ITC_SHARE * a["capex_per_kw"] * 1000)
    else:
        pv_credit = 0.0
    return {"tech": tech, "pv_rev": pv_rev, "pv_ppa_fixed": pv_ppa_fixed, "pv_tail": pv_tail, "pv_fuel": pv_fuel, "pv_fixed": pv_fixed,
            "pv_credit": pv_credit, "rate": r, "mwh": float(mwh), "cf_scales": tech in ("Solar", "Wind")}


def npv_if_built(comp, case, operation_year=1, ercot_ratio=1.0, hh_ratio=1.0, cf=1.0, credits=True):
    """NPV per MW at the operation date, for operation year ``operation_year`` (1 = the decision year).

    Notes
    -----
    Prices enter as ratios to the 2024 base over the plant's operating
    window; under contract the PPA years are fixed in price and only the tail
    is merchant. Output scales the revenue but not the fixed costs.
    """
    if case == "contracted" and comp["tech"] in PPA:
        pv_rev = (comp["pv_ppa_fixed"] + comp["pv_tail"] * ercot_ratio) * cf
    else:
        pv_rev = comp["pv_rev"] * ercot_ratio * cf
    credit = comp["pv_credit"] * (cf if CREDIT_OF.get(comp["tech"]) == "ptc" else 1.0)
    policy = credit_policy_of(credits)
    earned = policy is not None and credit_eligible(comp["tech"], DECISION_YEAR + operation_year - 1, policy)
    return pv_rev - comp["pv_fuel"] * hh_ratio - comp["pv_fixed"] + (credit if earned else 0.0)


def expected_power_npv(p_by_year, comp, mw, carry, case, credits=True, ercot_ratio=1.0):
    """Expected NPV on 1 January 2025 of a request on the flat 2024 path, from its cumulative chance of operating.

    Parameters
    ----------
    p_by_year : array-like
        Cumulative P(operation by year j), j = 1 … 7, from the decision date.
    comp : dict
        ``pv_components`` of its technology.
    mw : float
        Nameplate.
    carry : float
        Deposits and studies spent whether or not it operates ($).
    case : {"merchant", "contracted"}
    credits : bool or str
        True for the credits of the law in force on the decision date, False
        for the credits-off sensitivity, or a policy of ``CREDIT_POLICIES``
        (``"2025 law"``: the 2027 deadline, a stress).
    ercot_ratio : float
        The flat hub price as a multiple of 2024's (the tornado's price lines).

    Returns
    -------
    dict
        ``expected_npv``, ``p_operation``, ``expected_operation_year``,
        ``npv_if_built_year1``.

    Notes
    -----
    Σ_j ΔP_j × NPV per MW if built in year j × MW / (1 + r)^j − carry: the
    same identity as ``economics.power_npv``, with the credit decided by the
    operation year.
    """
    p = np.asarray(p_by_year, float)
    by_year = np.array([npv_if_built(comp, case, j, ercot_ratio=ercot_ratio, credits=credits) * mw / (1 + comp["rate"]) ** j for j in range(1, len(p) + 1)])
    out = ec.power_npv(p, by_year, carry, comp["rate"], years=len(p))
    out["npv_if_built_year1"] = float(by_year[0] * (1 + comp["rate"]))
    return out


def power_npv_matrix(power, components, prices, out_mult, op_year, base, horizon, case="merchant", credits=True):
    """NPV of every request in every scenario from its drawn operation year and the scenario's price ratios.

    Parameters
    ----------
    power : pandas.DataFrame
        The requests: ``technology``, ``mw``, ``carry_cost``.
    components : dict
        ``pv_components`` by candidate technology.
    prices : numpy.ndarray
        Scenarios × months × 3 (WTI, Henry Hub, ERCOT), real 2024 dollars.
    out_mult : numpy.ndarray
        Scenarios × requests capacity-factor multipliers.
    op_year : numpy.ndarray
        Scenarios × requests operation year (0 = never within the window).
    base : array-like
        The 2024 base prices (WTI, Henry Hub, ERCOT).
    horizon : int
        Months in a path.
    case : {"merchant", "contracted"}
    credits : bool or str
        As in ``expected_power_npv``.

    Returns
    -------
    numpy.ndarray
        Scenarios × requests NPV on 1 January 2025 ($).
    """
    out = np.empty((prices.shape[0], len(power)))
    for j, r in power.reset_index(drop=True).iterrows():
        comp = components[r["technology"]]
        for s in range(prices.shape[0]):
            y = int(op_year[s, j])
            if y == 0:
                out[s, j] = -r["carry_cost"]
                continue
            window = slice((y - 1) * 12, min(horizon, (y - 1 + LIFE) * 12))
            ercot_ratio = prices[s, window, 2].mean() / base[2]
            hh_ratio = prices[s, window, 1].mean() / base[1]
            cf = out_mult[s, j] if comp["cf_scales"] else 1.0
            built = npv_if_built(comp, case, y, ercot_ratio, hh_ratio, cf, credits)
            out[s, j] = built * r["mw"] / (1 + comp["rate"]) ** y - r["carry_cost"]
    return out


def lease_npv_matrix(baselines, wells, prices, out_mult, cost_mult, grid_base, grid=None):
    """Incremental NPV of every lease in every scenario.

    Parameters
    ----------
    baselines : list of (numpy.ndarray, numpy.ndarray)
        Oil and gas baselines of each lease (``economics.lease_baseline``).
    wells : array-like
        Producing completions of each lease.
    prices : numpy.ndarray
        Scenarios × months × 3, real 2024 dollars.
    out_mult : numpy.ndarray
        Scenarios × leases output multipliers.
    cost_mult : numpy.ndarray
        One cost multiplier per scenario.
    grid_base : dict
        ``economics.grid_case("base")``: the workover and opex the multiplier scales.
    grid : dict, optional
        Further overrides of the grid (the committee grid, a what-if).

    Returns
    -------
    numpy.ndarray
        Scenarios × leases incremental NPV ($).
    """
    g = {**grid_base, **(grid or {})}
    out = np.empty((prices.shape[0], len(baselines)))
    for j, (bo, bg) in enumerate(baselines):
        for s in range(prices.shape[0]):
            override = {**(grid or {}), "workover_cost_per_well_usd": g["workover_cost_per_well_usd"] * cost_mult[s],
                        "opex_usd_per_boe": g["opex_usd_per_boe"] * cost_mult[s]}
            if "dev_cost_per_flowing_boed_usd" in g:  # the committee grid's capital moves with the cost draw too, as in notebook 09
                override["dev_cost_per_flowing_boed_usd"] = g["dev_cost_per_flowing_boed_usd"] * cost_mult[s]
            out[s, j] = ec.incremental_npv(bo * out_mult[s, j], bg * out_mult[s, j], prices[s, :, 0], prices[s, :, 1], int(wells[j]), "base", override)
    return out


def stage_one_charge(sector, capex, carry, p_operation):
    """What one budget dollar buys now (decision #90): a lease's capital; a request's deposits plus its construction reserve.

    Notes
    -----
    The reserve is the expected construction draw, P(operation within seven
    years) × capital: the money the company must hold back for the requests
    that reach their agreement. Construction itself is decided at the
    agreement (the dynamic module), and that module reports how often the
    drawn construction capital exceeds the reserve.
    """
    sector = np.asarray(sector)
    return np.where(sector == "ERCOT power", np.asarray(carry, float) + np.asarray(p_operation, float) * np.asarray(capex, float), np.asarray(capex, float))
