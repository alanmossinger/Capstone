"""Candidate economics: lease redevelopment cash flows, power-plant revenue capture, battery dispatch, NPV.

What: the monthly cash-flow engine of the forty candidates (PLAN.md §14.7)
— an Arps baseline and a modeled redevelopment uplift for a Gulf of Mexico
lease under the confirmed cost grid (decision #68); hourly price-capture
factors for solar, wind and gas from the 2024 ERCOT hourly prices and
system shapes; a one-cycle-a-day battery dispatch on the same prices; and
the present value of any cash-flow vector at a technology's real cost of
capital.
Why: every candidate must be comparable in 2024 dollars at one valuation
date, with every cost either parsed from a public file or listed as an
assumption with a range and a label (OBSERVED / DERIVED / FORECAST /
ASSUMED), so the optimizer of notebook 09 and the advisor of notebook 10
never see a number without its provenance.
Reads: nothing on import; the notebook passes the tables in.
Writes: nothing; notebook 07 writes `investment_candidates.csv`,
`candidate_npv.csv`, `candidate_breakeven.csv`, `cost_sensitivity.csv`.
Used by: notebooks 07, 08 and 09; `tests/test_economics.py`.

The battery dispatch reuses the idea of my Forecast-to-Dispatch LP
(self-reuse, statement of work) in its simplest form: energy arbitrage
only, one cycle a day, no ancillary services, stated on every export.
"""

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from src import decline

# --- the upstream cost grid (decision #68; every value ASSUMED, in 2024 dollars) ---------------
UPSTREAM_GRID = pd.DataFrame([
    {"item": "workover_cost_per_well_usd", "low": 4e6, "base": 8e6, "high": 15e6, "unit": "$ per well", "note": "shelf to deepwater recompletion or workover"},
    {"item": "uplift_share", "low": 0.10, "base": 0.20, "high": 0.30, "unit": "share of the current rate", "note": "incremental rate on the Arps baseline, decaying with the lease's own decline"},
    {"item": "opex_usd_per_boe", "low": 12.0, "base": 18.0, "high": 28.0, "unit": "$ per boe", "note": "lease operating cost"},
    {"item": "royalty_share", "low": 0.125, "base": 0.1875, "high": 0.1875, "unit": "share of revenue", "note": "federal OCS royalty; 12.5% for pre-2007 leases is the low case"},
    {"item": "abandonment_usd_per_well", "low": 1e6, "base": 3e6, "high": 8e6, "unit": "$ per well", "note": "plugging and abandonment accrual at the lease's end"},
    {"item": "lead_time_months", "low": 24, "base": 24, "high": 24, "unit": "months", "note": "from decision to first incremental production"},
    {"item": "oil_differential_usd_per_bbl", "low": 3.0, "base": 5.0, "high": 8.0, "unit": "$ per bbl below WTI", "note": "realised price = WTI − differential"},
    {"item": "gas_differential_usd_per_mmbtu", "low": 0.3, "base": 0.5, "high": 0.8, "unit": "$ per MMBtu below Henry Hub", "note": "realised price = Henry Hub − differential"},
    {"item": "wacc_real", "low": 0.051, "base": 0.051, "high": 0.08, "unit": "real rate", "note": "ATB offshore cost of capital; 8% as the stress"},
])
CASES = ("low", "base", "high")
MCF_PER_MMBTU = 1.0 / 1.037  # 1 Mcf of pipeline gas ≈ 1.037 MMBtu
BOE_PER_MCF = 1.0 / 6.0  # 6 Mcf per barrel of oil equivalent
ECONOMIC_LIMIT_BOE_PER_MONTH = 300.0  # a lease below this rate is shut in and abandoned (ASSUMED)
VALUATION_MONTH = pd.Timestamp("2025-01-01")  # common valuation date of every candidate


def grid_case(case):
    """The upstream grid as a dict for one case (``low``, ``base`` or ``high``)."""
    return dict(zip(UPSTREAM_GRID["item"], UPSTREAM_GRID[case]))


# --- lease cash flows ------------------------------------------------------------------------

def lease_baseline(history_oil, history_gas, months=240, window=36):
    """Arps baseline forecast of oil (bbl) and gas (Mcf) per month from the last ``window`` observed months.

    Returns
    -------
    tuple of (numpy.ndarray, numpy.ndarray, dict, dict)
        Oil and gas rates for the next ``months``, and the two Arps fits.
    """
    oil = np.asarray(history_oil, float)[-window:]
    gas = np.asarray(history_gas, float)[-window:]
    fit_o, fit_g = decline.fit_arps(oil), decline.fit_arps(gas)
    t = np.arange(1, months + 1)
    base_o = np.array([decline.forecast_arps(fit_o, h, len(oil)) for h in t])
    base_g = np.array([decline.forecast_arps(fit_g, h, len(gas)) for h in t])
    return np.maximum(base_o, 0.0), np.maximum(base_g, 0.0), fit_o, fit_g


def lease_cash_flows(base_oil, base_gas, wti, hh, n_wells, case="base", grid=None, redevelop=True):
    """Monthly incremental cash flow of a lease redevelopment against its Arps baseline, in 2024 dollars.

    Parameters
    ----------
    base_oil, base_gas : array-like
        Baseline rates per month (bbl, Mcf) from ``lease_baseline``.
    wti, hh : array-like
        Monthly price paths over the same months ($/bbl, $/MMBtu, real 2024).
    n_wells : int
        Wells worked over (the lease's producing completions).
    case : str
        Grid case.
    grid : dict, optional
        Overrides of ``grid_case(case)`` (the tornado changes one item at a time).
    redevelop : bool
        False gives the do-nothing baseline cash flow (for the uplift's value).

    Returns
    -------
    pandas.DataFrame
        One row per month: ``oil_bbl``, ``gas_mcf``, ``revenue``, ``royalty``,
        ``opex``, ``capex``, ``abandonment``, ``cash_flow`` (incremental when
        ``redevelop``, baseline otherwise), ``shut_in`` flag.

    Notes
    -----
    The uplift adds ``uplift_share`` of the baseline rate after the lead
    time and decays with the baseline, so it is a share of what the lease
    would do anyway, never a new field. The workover cost is paid at month
    zero; abandonment is paid in the month the lease reaches its economic
    limit (both cases) and is incremental only through its timing.
    """
    g = {**grid_case(case), **(grid or {})}
    base_oil, base_gas = np.asarray(base_oil, float), np.asarray(base_gas, float)
    months = len(base_oil)
    lead = int(g["lead_time_months"])
    uplift = np.zeros(months)
    if redevelop:
        uplift[lead:] = g["uplift_share"]
    oil = base_oil * (1 + uplift)
    gas = base_gas * (1 + uplift)
    boe = oil + gas * BOE_PER_MCF
    alive = np.cumprod(boe >= ECONOMIC_LIMIT_BOE_PER_MONTH).astype(bool)  # once below the limit, shut in for good
    oil, gas, boe = oil * alive, gas * alive, boe * alive
    price_oil = np.maximum(np.asarray(wti, float)[:months] - g["oil_differential_usd_per_bbl"], 0.0)
    price_gas = np.maximum(np.asarray(hh, float)[:months] - g["gas_differential_usd_per_mmbtu"], 0.0)
    revenue = oil * price_oil + gas * MCF_PER_MMBTU * price_gas
    royalty = revenue * g["royalty_share"]
    opex = boe * g["opex_usd_per_boe"]
    capex = np.zeros(months)
    if redevelop:
        capex[0] = g["workover_cost_per_well_usd"] * n_wells
    abandonment = np.zeros(months)
    end = int(alive.sum())
    if end < months:
        abandonment[end] = g["abandonment_usd_per_well"] * n_wells
    cash = revenue - royalty - opex - capex - abandonment
    return pd.DataFrame({"oil_bbl": oil, "gas_mcf": gas, "revenue": revenue, "royalty": royalty, "opex": opex, "capex": capex,
                         "abandonment": abandonment, "cash_flow": cash, "shut_in": ~alive})


def incremental_npv(base_oil, base_gas, wti, hh, n_wells, case="base", grid=None):
    """NPV of the redevelopment minus the do-nothing baseline, at the grid's real rate, from the valuation date."""
    g = {**grid_case(case), **(grid or {})}
    with_ = lease_cash_flows(base_oil, base_gas, wti, hh, n_wells, case, grid, redevelop=True)["cash_flow"].to_numpy()
    without = lease_cash_flows(base_oil, base_gas, wti, hh, n_wells, case, grid, redevelop=False)["cash_flow"].to_numpy()
    return npv_monthly(with_ - without, g["wacc_real"])


def npv_monthly(cash_flows, rate_real):
    """Present value of monthly cash flows at an annual real rate, month 0 undiscounted."""
    cash = np.asarray(cash_flows, float)
    discount = (1 + rate_real) ** (np.arange(len(cash)) / 12.0)
    return float((cash / discount).sum())


def breakeven_wti(base_oil, base_gas, hh, n_wells, case="base", lo=10.0, hi=200.0, tol=0.5):
    """Flat WTI at which the incremental NPV is zero (bisection), with Henry Hub held at its path."""
    months = len(base_oil)

    def f(price):
        return incremental_npv(base_oil, base_gas, np.full(months, price), hh, n_wells, case)

    if f(hi) < 0:
        return np.nan
    if f(lo) > 0:
        return lo
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


# --- power candidates: capture factors and battery dispatch on the hourly 2024 prices ---------

def capture_factors(hourly_price, solar_shape, wind_shape, gas_marginal_cost):
    """Price-capture factors from one year of hourly prices and system output shapes.

    Parameters
    ----------
    hourly_price : pandas.Series
        $/MWh, hourly, indexed by interval start.
    solar_shape, wind_shape : pandas.Series
        System output (MW) on the same index; only the shape matters.
    gas_marginal_cost : float
        $/MWh (heat rate × gas price + variable O&M); the plant runs when
        the price exceeds it.

    Returns
    -------
    dict
        ``solar``, ``wind``: generation-weighted mean price over the flat
        mean price; ``gas``: mean price in the hours the plant runs over the
        flat mean, and ``gas_hours_share``; all DERIVED.
    """
    price = hourly_price.astype(float)
    flat = price.mean()
    out = {}
    for name, shape in (("solar", solar_shape), ("wind", wind_shape)):
        w = shape.reindex(price.index).fillna(0.0).astype(float)
        out[name] = float((price * w).sum() / w.sum() / flat) if w.sum() > 0 else np.nan
    running = price > gas_marginal_cost
    out["gas"] = float(price[running].mean() / flat) if running.any() else np.nan
    out["gas_hours_share"] = float(running.mean())
    out["flat_price"] = float(flat)
    return out


def battery_day(prices, hours=4, efficiency=0.85, cycles=1.0):
    """Optimal one-day energy arbitrage of a 1 MW / ``hours`` MWh battery by linear programming.

    Parameters
    ----------
    prices : array-like
        24 hourly prices ($/MWh).
    hours : int
        Duration at full power (MWh per MW).
    efficiency : float
        Round-trip efficiency applied on charging.
    cycles : float
        Maximum full cycles in the day.

    Returns
    -------
    float
        Net revenue per MW for the day ($).

    Notes
    -----
    Variables: charge c_t and discharge d_t in [0, 1] MW each hour; state of
    charge s_t = s_{t-1} + η c_t − d_t within [0, hours], starting and
    ending empty; total discharge ≤ cycles × hours. Objective: maximise
    Σ p_t (d_t − c_t). Adapted from my Forecast-to-Dispatch dispatch LP,
    reduced to energy only.
    """
    p = np.asarray(prices, float)
    n = len(p)
    c_obj = np.concatenate([p, -p])  # minimise −(p·d − p·c) → coefficients for [c, d]
    A_ub, b_ub = [], []
    for t in range(n):
        row = np.zeros(2 * n)
        row[: t + 1] = efficiency  # charge adds
        row[n: n + t + 1] = -1.0  # discharge removes
        A_ub.append(row); b_ub.append(hours)  # s_t ≤ hours
        A_ub.append(-row); b_ub.append(0.0)  # s_t ≥ 0
    row = np.zeros(2 * n)
    row[n:] = 1.0
    A_ub.append(row); b_ub.append(cycles * hours)  # total discharge
    res = linprog(c_obj, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, 1)] * (2 * n), method="highs")
    return float(-res.fun) if res.success else np.nan


def battery_annual_revenue(hourly_price, hours=4, efficiency=0.85, cycles=1.0):
    """Sum of ``battery_day`` over the days of a year: $ per MW-year, energy arbitrage only."""
    price = hourly_price.astype(float)
    days = price.groupby(price.index.date)
    revenue = sum(battery_day(group.to_numpy(), hours, efficiency, cycles) for _, group in days if len(group) >= 23)
    return float(revenue)


# --- power candidate NPV with the timing engine ---------------------------------------------

def power_npv(p_operation_by_year, npv_if_built_by_year, cost_to_carry, rate_real, years=7):
    """Expected NPV at the valuation date of a request that may never operate, or operate late.

    Parameters
    ----------
    p_operation_by_year : array-like
        Cumulative P(operation by year j), j = 1 … ``years`` (the landmark
        and entry models).
    npv_if_built_by_year : array-like
        NPV per MW if operation starts in year j (the value table and ATB
        costs, discounted from year j to the valuation date by the caller).
    cost_to_carry : float
        Deposits and studies spent whether or not the request operates ($/MW).
    rate_real : float
        Unused here (the caller discounts ``npv_if_built_by_year``); kept
        so the signature reads like the lease engine.

    Returns
    -------
    dict
        ``expected_npv``, ``p_operation`` (by the last year), ``p_by_year``
        (increments) and ``expected_operation_year`` among those that operate.
    """
    P = np.asarray(p_operation_by_year, float)
    inc = np.diff(np.concatenate([[0.0], P]))
    v = np.asarray(npv_if_built_by_year, float)
    expected = float((inc * v).sum() - cost_to_carry)
    p_op = float(P[-1])
    exp_year = float((inc * np.arange(1, len(inc) + 1)).sum() / p_op) if p_op > 0 else np.nan
    return {"expected_npv": expected, "p_operation": p_op, "p_by_year": inc, "expected_operation_year": exp_year}


def operation_curve(key, landmark_entry, entry_predictions, years=7):
    """Cumulative P(operation by year 1 … ``years``) of a request at entry, from the queue models.

    Parameters
    ----------
    key : str
        ``project_key``.
    landmark_entry : pandas.DataFrame
        Landmark-0 predictions pivoted to ``project_key`` × ``horizon_after``
        (1, 2, 3), the entry model.
    entry_predictions : pandas.DataFrame
        Entry predictions pivoted to ``project_key`` × ``horizon`` (5, 7), the chosen model.

    Returns
    -------
    numpy.ndarray or None
        Non-decreasing probabilities for years 1–7 (years 4 and 6
        interpolated), or None when the request has no prediction.

    Notes
    -----
    Shared by notebooks 07 (expected NPV) and 08 (timing draws), so both
    use the same curve.
    """
    if key not in landmark_entry.index or key not in entry_predictions.index:
        return None
    p1, p2, p3 = (float(landmark_entry.loc[key, h]) for h in (1, 2, 3))
    p5 = float(entry_predictions.loc[key, 5])
    p7 = float(entry_predictions.loc[key, 7]) if 7 in entry_predictions.columns and not np.isnan(entry_predictions.loc[key, 7]) else p5
    if any(np.isnan(v) for v in (p1, p2, p3, p5)):
        return None
    curve = np.array([p1, p2, p3, (p3 + p5) / 2, p5, (p5 + p7) / 2, p7])[:years]
    return np.maximum.accumulate(np.clip(curve, 0, 1))
