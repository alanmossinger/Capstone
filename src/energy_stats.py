"""Statistics for autocorrelated monthly series: block bootstrap, lagged correlation, stationarity, breaks.

What: a moving-block bootstrap interval for any statistic of a monthly
series, Pearson and Spearman correlations at lags, ADF and KPSS tests, and
a Chow test for a structural break at a named month.
Why: the proposal asks for intervals that respect autocorrelation, for
lagged cross-correlations among prices and output, and for stationarity
and break tests before a price model is fitted (docs/plan.md §14.4).
Reads / writes: nothing.
Used by: notebooks 02 (part C) and 03 (part B); ``tests/test_energy_stats.py``.

The ADF and KPSS tests come from ``statsmodels`` (decision #65).
"""

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss
import statsmodels.api as sm


def block_bootstrap(values, statistic, block=12, n_boot=1000, seed=0, level=0.95):
    """Moving-block bootstrap interval of ``statistic(values)``.

    Parameters
    ----------
    values : array-like
        A monthly series (NaN dropped).
    statistic : callable
        Maps an array to a float.
    block : int
        Block length in months; twelve keeps a year's seasonality inside a block.

    Returns
    -------
    dict
        ``estimate``, ``low``, ``high``, ``n``, ``block``.

    Notes
    -----
    Blocks of consecutive months are drawn with replacement and concatenated
    to the series length, so the resampled series keep the autocorrelation
    an i.i.d. bootstrap would destroy (Künsch, 1989).
    """
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    rng = np.random.default_rng(seed)
    block = min(block, n)
    n_blocks = int(np.ceil(n / block))
    draws = np.empty(n_boot)
    for k in range(n_boot):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        sample = np.concatenate([x[s: s + block] for s in starts])[:n]
        draws[k] = statistic(sample)
    alpha = (1 - level) / 2
    return {"estimate": float(statistic(x)), "low": float(np.quantile(draws, alpha)),
            "high": float(np.quantile(draws, 1 - alpha)), "n": n, "block": block}


def lagged_correlation(a, b, max_lag=12):
    """Pearson and Spearman correlation of ``a(t)`` with ``b(t − lag)`` for lags −max_lag … max_lag.

    Returns
    -------
    pandas.DataFrame
        ``lag``, ``pearson``, ``spearman``, ``n``. A positive lag means
        ``b`` leads ``a``.
    """
    a, b = pd.Series(np.asarray(a, float)), pd.Series(np.asarray(b, float))
    rows = []
    for lag in range(-max_lag, max_lag + 1):
        shifted = b.shift(lag)
        pair = pd.concat([a, shifted], axis=1).dropna()
        if len(pair) < 8:
            continue
        rows.append({"lag": lag, "pearson": stats.pearsonr(pair.iloc[:, 0], pair.iloc[:, 1])[0],
                     "spearman": stats.spearmanr(pair.iloc[:, 0], pair.iloc[:, 1])[0], "n": len(pair)})
    return pd.DataFrame(rows)


def stationarity(values, name=""):
    """ADF and KPSS tests of one series.

    Returns
    -------
    dict
        ``series``, ``adf_stat``, ``adf_p``, ``kpss_stat``, ``kpss_p``,
        ``verdict``: "stationary" when ADF rejects a unit root and KPSS does
        not reject stationarity, "unit root" when the reverse, "unclear"
        otherwise.

    Notes
    -----
    The two tests have opposite null hypotheses, which is why both are
    reported; the KPSS p-value is truncated by ``statsmodels`` at 0.01 and
    0.1, and that is noted in the verdict rule, not hidden.
    """
    x = np.asarray(values, float)
    x = x[np.isfinite(x)]
    adf_stat, adf_p, *_ = adfuller(x, autolag="AIC")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # statsmodels warns when the KPSS p-value is truncated; the verdict rule says so
        kpss_stat, kpss_p, *_ = kpss(x, regression="c", nlags="auto")
    if adf_p < 0.05 and kpss_p >= 0.05:
        verdict = "stationary"
    elif adf_p >= 0.05 and kpss_p < 0.05:
        verdict = "unit root"
    else:
        verdict = "unclear"
    return {"series": name, "adf_stat": float(adf_stat), "adf_p": float(adf_p), "kpss_stat": float(kpss_stat),
            "kpss_p": float(kpss_p), "verdict": verdict, "n": int(len(x))}


def chow_test(y, break_at):
    """Chow test for a break in the mean and trend of ``y`` at index ``break_at``.

    Returns
    -------
    dict
        ``f_stat``, ``p_value``, ``n_before``, ``n_after``.

    Notes
    -----
    Fits ``y = a + b·t`` on the whole series and on each side of the break;
    the F statistic compares the pooled residual sum of squares with the sum
    of the two sides' (two parameters per segment).
    """
    y = np.asarray(y, float)
    t = np.arange(len(y), dtype=float)
    x = sm.add_constant(t)
    pooled = sm.OLS(y, x).fit().ssr
    before = sm.OLS(y[:break_at], x[:break_at]).fit().ssr
    after = sm.OLS(y[break_at:], x[break_at:]).fit().ssr
    k, n = 2, len(y)
    f_stat = ((pooled - (before + after)) / k) / ((before + after) / (n - 2 * k))
    p_value = 1 - stats.f.cdf(f_stat, k, n - 2 * k)
    return {"f_stat": float(f_stat), "p_value": float(p_value), "n_before": int(break_at), "n_after": int(n - break_at)}
