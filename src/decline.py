"""Arps decline curves: the physics baseline for lease production.

What: the Arps hyperbolic rate equation and a bounded least-squares fit of
its three parameters to a lease's monthly history, with an exponential
fallback when the hyperbolic fit does not converge.
Why: a decline curve is what a reservoir engineer forecasts with; the ML
challengers of notebook 05 must beat it, not only a naive last value
(docs/plan.md §14.6), and the redevelopment uplift of notebook 07 is measured
against it.
Reads / writes: nothing.
Used by: notebook 02 (cohort curves), notebook 05 (baseline), notebook 07
(the decline baseline of each candidate, through ``floored_baseline``);
``tests/test_decline.py``.

``fit_arps`` and ``forecast_arps`` are the registered forecasting baseline
of criterion C20 and stay as they were scored. ``floored_baseline`` is the
valuation baseline of the lease candidates since the 17 October audit
(audit E2, decision #90): an unbounded Arps fit on a flat or rising window
returns no decline at all, and ten of the twenty leases then produced at
their 2024 rate for twenty years.

Adapted from: Arps, J. J. (1945), "Analysis of decline curves", Trans. AIME
160, 228–247 — the hyperbolic form q(t) = q_i (1 + b D_i t)^(-1/b).
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def arps(t, q_i, d_i, b):
    """Arps rate at time ``t`` (months): hyperbolic for ``b > 0``, exponential at ``b = 0``.

    Parameters
    ----------
    t : array-like
        Months since the start of the decline (0 at the first point).
    q_i : float
        Initial rate (volume per month).
    d_i : float
        Initial nominal decline per month.
    b : float
        Decline exponent; 0 exponential, 1 harmonic, between them hyperbolic.
    """
    t = np.asarray(t, dtype=float)
    if b < 1e-6:
        return q_i * np.exp(-d_i * t)
    return q_i * np.power(1.0 + b * d_i * t, -1.0 / b)


def fit_arps(q, max_b=2.0):
    """Fit Arps parameters to a monthly rate history by bounded least squares on log rates.

    Parameters
    ----------
    q : array-like
        Monthly volumes from the start of the decline (zeros allowed; they
        are dropped from the fit, not imputed).
    max_b : float
        Upper bound of the decline exponent.

    Returns
    -------
    dict
        ``q_i``, ``d_i``, ``b``, ``n`` (points used), ``form`` ("hyperbolic",
        "exponential" or "flat" when fewer than three positive points exist).

    Notes
    -----
    The fit minimises squared errors of log rates, so a lease's large early
    months do not dominate its tail; the exponential fallback is the same
    fit with ``b`` fixed at zero. A history with fewer than three positive
    months returns a flat curve at its mean, which is the honest prediction.
    """
    q = np.asarray(q, dtype=float)
    t = np.arange(len(q), dtype=float)
    keep = np.isfinite(q) & (q > 0)
    if keep.sum() < 3:
        level = float(q[keep].mean()) if keep.any() else 0.0
        return {"q_i": level, "d_i": 0.0, "b": 0.0, "n": int(keep.sum()), "form": "flat"}
    t_k, log_q = t[keep], np.log(q[keep])
    q0 = float(np.exp(log_q[:3].mean()))

    def log_arps(tt, q_i, d_i, b):
        return np.log(np.maximum(arps(tt, q_i, d_i, b), 1e-9))

    try:
        params, _ = curve_fit(log_arps, t_k, log_q, p0=[q0, 0.05, 0.5],
                              bounds=([1e-6, 0.0, 0.0], [np.inf, 5.0, max_b]), maxfev=2000)
        q_i, d_i, b = (float(v) for v in params)
        form = "hyperbolic"
    except (RuntimeError, ValueError):
        slope, intercept = np.polyfit(t_k, log_q, 1)
        q_i, d_i, b, form = float(np.exp(intercept)), float(max(-slope, 0.0)), 0.0, "exponential"
    return {"q_i": q_i, "d_i": d_i, "b": b, "n": int(keep.sum()), "form": form}


def forecast_arps(fit, horizon_months, history_length):
    """Rate ``horizon_months`` after the last fitted month, from a ``fit_arps`` result."""
    if fit["form"] == "flat":
        return fit["q_i"]
    return float(arps(history_length - 1 + horizon_months, fit["q_i"], fit["d_i"], fit["b"]))


def monthly_decline(annual):
    """Nominal monthly decline whose effective annual decline is ``annual`` (0.08 → 0.00695 a month)."""
    return float(-np.log(1.0 - annual) / 12.0)


def modified_hyperbolic(t, fit, d_min, t_anchor):
    """Arps rate that turns exponential at ``d_min`` once its own decline falls below it, never before ``t_anchor``.

    Parameters
    ----------
    t : array-like
        Months since the start of the fitted tail.
    fit : dict
        ``fit_arps`` result.
    d_min : float
        Terminal nominal decline per month.
    t_anchor : float
        The last fitted month: the curve follows the fit up to here, so the
        forecast starts from the rate the data support.

    Notes
    -----
    The instantaneous decline of the hyperbola is D(t) = d_i / (1 + b d_i t);
    it reaches d_min at t* = (d_i / d_min − 1) / (b d_i). The switch happens
    at max(t*, t_anchor), so a fit with no decline (d_i ≤ d_min) declines at
    d_min from the last observed month. This is the modified hyperbolic of
    reserves practice (Robertson, 1988).
    """
    t = np.asarray(t, dtype=float)
    if fit["form"] == "flat":
        return fit["q_i"] * np.exp(-d_min * np.maximum(t - t_anchor, 0.0))
    d_i, b = fit["d_i"], fit["b"]
    if d_i <= d_min:
        t_star = 0.0
    elif b < 1e-6:
        t_star = np.inf  # exponential above the floor never reaches it
    else:
        t_star = (d_i / d_min - 1.0) / (b * d_i)
    t_switch = max(t_star, t_anchor)
    q_switch = arps(t_switch, fit["q_i"], d_i, b) if np.isfinite(t_switch) else 0.0
    before = arps(np.minimum(t, t_switch) if np.isfinite(t_switch) else t, fit["q_i"], d_i, b)
    after = q_switch * np.exp(-d_min * np.maximum(t - t_switch, 0.0)) if np.isfinite(t_switch) else before
    return np.where(t <= t_switch, before, after)


def floored_baseline(q, months, annual_floor, min_post_peak=12, smooth=3):
    """Monthly baseline of a lease for the next ``months``: fitted after its peak, never declining slower than the floor.

    Parameters
    ----------
    q : array-like
        Monthly volumes, oldest first (the window the valuation uses).
    months : int
        Forecast length.
    annual_floor : float
        Terminal effective annual decline (``config.LEASE_TERMINAL_DECLINE``).
    min_post_peak : int
        Positive months needed after the peak to fit a decline.
    smooth : int
        Months in the rolling mean that locates the peak.

    Returns
    -------
    tuple of (numpy.ndarray, dict)
        The rates and a record: ``form`` ("fitted", "ramp-up" or "empty"),
        ``peak_index``, the Arps fit, ``d_min`` and ``level`` (ramp-up only).

    Notes
    -----
    A lease whose rate peaked inside the window is fitted from the peak, so
    the ramp-up months do not pull the fitted level down (lease G09982's
    first baseline year was a third of its 2024 output). A lease that peaked
    in the last ``min_post_peak`` months is still ramping: no decline can be
    fitted, so it declines at the floor from the mean of its last three
    positive months, which is the conservative reading.
    """
    q = np.asarray(q, dtype=float)
    d_min = monthly_decline(annual_floor)
    if not np.any(q > 0):
        return np.zeros(months), {"form": "empty", "peak_index": None, "fit": None, "d_min": d_min}
    rolled = pd.Series(q).rolling(smooth, min_periods=1).mean().to_numpy()
    peak = int(np.nanargmax(rolled))
    tail = q[peak:]
    h = np.arange(1, months + 1)
    if (tail > 0).sum() < min_post_peak:
        level = float(q[q > 0][-3:].mean())
        return level * np.exp(-d_min * h), {"form": "ramp-up", "peak_index": peak, "fit": None, "d_min": d_min, "level": level}
    fit = fit_arps(tail)
    t_last = len(tail) - 1
    rates = modified_hyperbolic(t_last + h, fit, d_min, t_last)
    return np.maximum(rates, 0.0), {"form": "fitted", "peak_index": peak, "fit": fit, "d_min": d_min}
