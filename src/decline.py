"""Arps decline curves: the physics baseline for lease production.

What: the Arps hyperbolic rate equation and a bounded least-squares fit of
its three parameters to a lease's monthly history, with an exponential
fallback when the hyperbolic fit does not converge.
Why: a decline curve is what a reservoir engineer forecasts with; the ML
challengers of notebook 05 must beat it, not only a naive last value
(PLAN.md §14.6), and the redevelopment uplift of notebook 07 is measured
against it.
Reads / writes: nothing.
Used by: notebook 02 (cohort curves), notebook 05 (baseline), notebook 07
(the decline baseline of each candidate); ``tests/test_decline.py``.

Adapted from: Arps, J. J. (1945), "Analysis of decline curves", Trans. AIME
160, 228–247 — the hyperbolic form q(t) = q_i (1 + b D_i t)^(-1/b).
"""

import numpy as np
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
