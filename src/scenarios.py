"""Joint scenarios for the portfolio: prices, output, costs and timing drawn together, with named stresses.

What: reproducible scenario sets for the forty candidates (PLAN.md §14.8)
— a moving-block bootstrap of the joint monthly log changes of WTI, Henry
Hub and the ERCOT price that keeps their cross-correlation; a Gaussian
copula on the same marginals as a second, held-out generator; empirical
residual draws for lease output and plant capacity factors from the scored
holdout forecasts of notebook 05; cost multipliers from the grid; operation
years for the power candidates from the queue models' curves through the
copula of notebook 09's book simulation; named stresses; and the risk
measures (P(NPV < 0), VaR, CVaR).
Why: the capital decision has to see the candidates' NPVs moving together
— an oil collapse, a gas spike and a weak wind year are joint events — and
the optimizer of notebook 09 must be scored on scenarios it did not select
on, which is why two generators exist.
Reads: nothing on import; the notebook passes the tables in.
Writes: nothing; notebook 08 writes the scenario tables.
Used by: notebooks 08 and 09; `tests/test_scenarios.py`.
"""

import numpy as np
import pandas as pd
from scipy import stats

from src import economics as ec

SERIES = ["wti_usd_bbl", "hh_usd_mmbtu", "ercot_usd_mwh"]
STRESSES = {  # name -> what moves; every multiplier is ASSUMED and stated in the report
    "base": {},
    "oil collapse (2020 path)": {"wti_path": "2020"},
    "high gas, low spark spread": {"hh": 1.5, "ercot": 1.0},
    "weak wind year": {"wind_cf": 0.85},
    "solar curtailment": {"solar_revenue": 0.90},
    "two-year delay": {"delay_years": 2},
    "simultaneous downside": {"wti_path": "2020", "hh": 1.5, "wind_cf": 0.85, "solar_revenue": 0.90, "delay_years": 2, "cost": 1.2},
}


# --- price paths ----------------------------------------------------------------------------

MAX_MONTHLY_LOG_CHANGE = 1.5  # ASSUMED: a monthly log change is capped at ±1.5 (a ×4.5 move), the largest the history shows outside February 2021 (decision #81)


def joint_log_changes(market, series=SERIES, start="2018-01-01", end="2024-12-01", cap=MAX_MONTHLY_LOG_CHANGE):
    """Monthly log changes of the price series over the window, as a (months × series) array, capped at ±``cap``.

    Notes
    -----
    Winter Storm Uri took the ERCOT North hub from $26 to $1,772 a MWh and
    back within two months (log changes of +4.2 and −4.3). A generator that
    draws months one at a time, or a block that ends between the two
    months, carries the spike without its reversal, and a four-year
    half-life then holds a ×67 price for years: the first rerun on the
    observed prices put the books' expected NPV in the trillions while
    their medians stayed near $16B. The cap keeps the month as an extreme
    one (×4.5, as large as the August 2019 and August 2023 spikes) and
    applies to every series alike; ``cap=None`` disables it.
    """
    m = market.set_index("month").sort_index().loc[start:end, series]
    changes = np.log(m).diff().dropna().to_numpy()
    return np.clip(changes, -cap, cap) if cap is not None else changes


def block_bootstrap_paths(changes, n_scenarios, horizon_months, block=12, seed=2020, aligned=True):
    """Joint monthly log-change paths by block bootstrap of the historical rows.

    Parameters
    ----------
    aligned : bool
        True draws blocks that start at multiples of ``block`` months from
        the first row (calendar years when the history starts in February
        and ``block`` is 12), so a spike and its reversal in the next month
        stay in one block; False is the moving-block bootstrap, which can
        start a block anywhere.

    Returns
    -------
    numpy.ndarray
        Shape (n_scenarios, horizon_months, n_series). A block takes the
        same consecutive months for every series, so cross-correlation and
        the 2020, 2021 and 2022 episodes travel together.
    """
    rng = np.random.default_rng(seed)
    n, k = changes.shape
    out = np.empty((n_scenarios, horizon_months, k))
    allowed = np.arange(0, n, block) if aligned else np.arange(0, n - block + 1)  # aligned: every calendar year, the last one as far as the history runs
    for s in range(n_scenarios):
        pieces, length = [], 0
        while length < horizon_months:  # blocks until the horizon is covered; an aligned last-year block may be short
            st = rng.choice(allowed)
            pieces.append(changes[st: st + block])
            length += len(pieces[-1])
        out[s] = np.concatenate(pieces)[:horizon_months]
    return out


def gaussian_copula_paths(changes, n_scenarios, horizon_months, seed=2021):
    """Joint paths from a Gaussian copula on the empirical marginals of the monthly changes.

    Notes
    -----
    Correlated normals with the rank correlation of the historical changes
    are mapped through each series' empirical quantile function; months are
    independent, which is the copula's known weakness and the reason it is
    the held-out generator, not the primary one.
    """
    rng = np.random.default_rng(seed)
    n, k = changes.shape
    corr = stats.spearmanr(changes).statistic if k > 1 else np.array([[1.0]])
    corr = np.atleast_2d(corr)
    normal_corr = 2 * np.sin(np.pi * corr / 6)  # Spearman -> Pearson of the underlying normals
    z = rng.multivariate_normal(np.zeros(k), normal_corr, size=(n_scenarios, horizon_months))
    u = stats.norm.cdf(z)
    out = np.empty_like(u)
    for j in range(k):
        out[..., j] = np.quantile(changes[:, j], u[..., j])
    return out


def paths_to_prices(log_change_paths, base_levels):
    """Price levels from log-change paths and the starting levels (shape (n, H, k)): a pure random walk, no reversion."""
    return np.asarray(base_levels)[None, None, :] * np.exp(np.cumsum(log_change_paths, axis=1))


HALF_LIFE_MONTHS = 48  # ASSUMED: real commodity prices revert to their long-run level with a four-year half-life (decision #69)


def mean_reverting_prices(shock_paths, base_levels, long_run_levels, half_life_months=HALF_LIFE_MONTHS):
    """Price levels from demeaned shock paths with mean reversion of the log price toward a long-run level.

    Parameters
    ----------
    shock_paths : numpy.ndarray
        Shape (n, H, k): joint monthly log shocks (demeaned inside).
    base_levels : array-like
        Starting levels (the 2024 real means).
    long_run_levels : array-like
        Levels the log prices revert to (the 2018–2024 real means, OBSERVED).
    half_life_months : float
        Months for half of a deviation to close (ASSUMED).

    Returns
    -------
    numpy.ndarray
        Shape (n, H, k).

    Notes
    -----
    log p_t = log p_{t−1} + κ (log p̄ − log p_{t−1}) + ε_t with κ = ln 2 / half-life.
    The shocks keep the history's joint jumps (they are the bootstrapped
    changes minus their mean), while the drift and the unbounded variance of
    a twenty-year random walk are replaced by reversion: the long-run
    dispersion of the log price is σ / √(2κ), about ×/÷ 2 for WTI.
    """
    eps = shock_paths - shock_paths.mean(axis=(0, 1), keepdims=True)
    kappa = np.log(2) / half_life_months
    n, H, k = eps.shape
    log_p = np.empty((n, H, k))
    level = np.log(np.asarray(base_levels, float))[None, :].repeat(n, axis=0)
    target = np.log(np.asarray(long_run_levels, float))[None, :]
    for t in range(H):
        level = level + kappa * (target - level) + eps[:, t, :]
        log_p[:, t, :] = level
    return np.exp(log_p)


# --- residual and cost draws ------------------------------------------------------------------

def ratio_distribution(forecasts, line_prefix, pred_column="pred", floor=0.2, cap=3.0):
    """Empirical distribution of actual / forecast per row on the scored holdout rows of lines starting with ``line_prefix``."""
    rows = forecasts[forecasts["line"].str.startswith(line_prefix) & forecasts[pred_column].notna() & forecasts["y"].notna()]
    rows = rows[rows[pred_column] > 0]
    ratio = (rows["y"] / rows[pred_column]).clip(floor, cap)
    return ratio.to_numpy()


def key_level_ratios(forecasts, line_prefix, pred_column="pred", floor=0.2, cap=3.0, min_rows=6, return_weights=False):
    """Actual over forecast summed per key (lease or plant) across its scored holdout months: one ratio per key.

    Notes
    -----
    A month-level ratio mixes shut-in months with producing ones and says
    nothing about a year; summing a key's actuals and forecasts over its
    holdout months gives the error of the volume a cash flow is built on.
    Keys with fewer than ``min_rows`` scored months are left out. With
    ``return_weights`` the forecast volume of each key comes back too, so a
    draw can weight a key's error by the volume behind it (a multiplier for
    a large candidate should come from large producers' errors, not from the
    hundreds of small leases in their tail).
    """
    rows = forecasts[forecasts["line"].str.startswith(line_prefix) & forecasts[pred_column].notna() & forecasts["y"].notna()]
    sums = rows.groupby("key").agg(y=("y", "sum"), pred=(pred_column, "sum"), n=("y", "size"))
    sums = sums[(sums["n"] >= min_rows) & (sums["pred"] > 0)]
    ratios = (sums["y"] / sums["pred"]).clip(floor, cap).to_numpy()
    if return_weights:
        return ratios, sums["pred"].to_numpy(float)
    return ratios


def draw_multipliers(ratios, n_scenarios, n_items, seed, weights=None):
    """Independent draws from an empirical ratio distribution, shape (n_scenarios, n_items); ``weights`` make the draw volume-weighted."""
    rng = np.random.default_rng(seed)
    p = None if weights is None else np.asarray(weights, float) / np.sum(weights)
    return rng.choice(np.asarray(ratios, float), size=(n_scenarios, n_items), replace=True, p=p)


def cost_multipliers(n_scenarios, seed, low=0.75, mode=1.0, high=1.5):
    """Triangular cost multipliers per scenario (ASSUMED: the grid's span around base)."""
    rng = np.random.default_rng(seed)
    return rng.triangular(low, mode, high, size=n_scenarios)


# --- risk measures ----------------------------------------------------------------------------

def risk_measures(npv_draws, level=0.95):
    """P(NPV < 0), mean, VaR and CVaR of an NPV distribution (losses in the lower tail)."""
    x = np.asarray(npv_draws, float)
    q = np.quantile(x, 1 - level)
    return {"mean": float(x.mean()), "sd": float(x.std()), "p_negative": float((x < 0).mean()), "var": float(q),
            "cvar": float(x[x <= q].mean()) if (x <= q).any() else float(q)}


def stress_prices(base_prices, stress, wti_2020_path=None):
    """Apply a named stress to a (H, 3) real price path; returns a new array."""
    p = np.array(base_prices, float)
    if stress.get("wti_path") == "2020" and wti_2020_path is not None:
        h = min(len(wti_2020_path), len(p))
        p[:h, 0] = wti_2020_path[:h]
    if "hh" in stress:
        p[:, 1] = p[:, 1] * stress["hh"]
    if "ercot" in stress:
        p[:, 2] = p[:, 2] * stress["ercot"]
    return p
