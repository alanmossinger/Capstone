"""Portfolio selection over scenarios: the risk-aware MILP and its three comparators.

What: choose candidates x_i ∈ {0, 1} to maximise E[NPV] − λ·CVaR_β of the
book over a scenario set, with the Rockafellar–Uryasev linearisation of
CVaR, under a capital budget, concentration caps by sector or technology,
an optional emissions cap and mutually exclusive sets; solved with
``scipy.optimize.milp`` (HiGHS, no new dependency). Beside it the three
comparators of the proposal: A top-N by expected NPV, B equal capital by
sector, C the deterministic MILP (λ = 0). The out-of-sample score of any
book on a held-out scenario set, and the Jaccard similarity between books.
Why: criteria C21–C24 (PLAN.md §14.9, decision #70) compare the four books
under the same budget and the same scenarios; the book the dashboard
re-solves on cached scenarios is this one.
Reads / writes: nothing.
Used by: notebook 09 (part D), the dashboard; `tests/test_optimizer.py`.

Adapted from: Rockafellar, R. T. and Uryasev, S. (2000), "Optimization of
conditional value-at-risk", Journal of Risk 2(3), 21–41 — the auxiliary
variable α and the per-scenario excess u_s that make CVaR linear.
"""

import numpy as np
import pandas as pd
from scipy.optimize import LinearConstraint, milp, Bounds


def cvar(losses, level=0.95):
    """CVaR of a loss sample: the mean of the worst (1 − level) share."""
    x = np.sort(np.asarray(losses, float))[::-1]
    k = max(1, int(np.ceil((1 - level) * len(x))))
    return float(x[:k].mean())


def book_metric(npv_scenarios, x, lam=1.0, level=0.95):
    """E[NPV] − λ·CVaR_level(loss) of the book ``x`` over the scenarios (scenarios × candidates)."""
    total = np.asarray(npv_scenarios, float) @ np.asarray(x, float)
    return float(total.mean() - lam * cvar(-total, level))


def solve_milp(npv_scenarios, capex, budget, lam=1.0, level=0.95, groups=None, group_cap=None, co2=None, co2_cap=None,
               exclusive=(), time_limit=300):
    """Maximise E[NPV] − λ·CVaR of the book subject to the budget and the caps.

    Parameters
    ----------
    npv_scenarios : numpy.ndarray
        Shape (scenarios, candidates): NPV of each candidate in each scenario.
    capex : array-like
        Capital of each candidate ($).
    budget : float
        Capital budget ($).
    lam : float
        Risk aversion; 0 gives the deterministic MILP (comparator C).
    level : float
        CVaR level (0.95).
    groups : array-like, optional
        Group label of each candidate (sector or technology) for the concentration cap.
    group_cap : float, optional
        Maximum share of the budget in any one group.
    co2, co2_cap : array-like, float, optional
        Emissions per candidate and the cap on their sum.
    exclusive : iterable of iterables
        Sets of candidate indices of which at most one may be chosen.
    time_limit : float
        Seconds for HiGHS.

    Returns
    -------
    dict
        ``x`` (0/1 array), ``expected_npv``, ``cvar_loss``, ``objective``,
        ``status``, ``capex_used``.

    Notes
    -----
    The problem is solved in millions of dollars (HiGHS stalls on
    dollar-scale coefficients) and raises when the solver does not reach an
    optimum, so a time-limited incumbent is never mistaken for an answer.
    Variables: x (binary, n), α (free) and u_s ≥ 0 (one per scenario).
    CVaR of the loss L_s = −NPV_s·x equals min_α α + Σ u_s / ((1 − level) S)
    with u_s ≥ L_s − α, so the objective −μ·x + λ(α + Σ u_s/((1−level)S))
    is linear. With λ = 0 the α and u variables are left in but do nothing.
    """
    scale = 1e6  # solve in $ millions: dollar-scale coefficients stall HiGHS's branch and bound
    A = np.asarray(npv_scenarios, float) / scale
    S, n = A.shape
    capex = np.asarray(capex, float) / scale
    budget = budget / scale
    mu = A.mean(axis=0)
    n_var = n + 1 + S  # x, alpha, u
    c = np.concatenate([-mu, [lam], np.full(S, lam / ((1 - level) * S))])
    constraints = []
    # u_s + alpha + NPV_s · x >= 0
    rows = np.hstack([A, np.ones((S, 1)), np.eye(S)])
    constraints.append(LinearConstraint(rows, lb=np.zeros(S), ub=np.full(S, np.inf)))
    # budget
    constraints.append(LinearConstraint(np.concatenate([capex, np.zeros(1 + S)])[None, :], lb=-np.inf, ub=budget))
    if groups is not None and group_cap is not None:
        groups = np.asarray(groups)
        for g in np.unique(groups):
            row = np.concatenate([np.where(groups == g, capex, 0.0), np.zeros(1 + S)])
            constraints.append(LinearConstraint(row[None, :], lb=-np.inf, ub=group_cap * budget))
    if co2 is not None and co2_cap is not None:
        constraints.append(LinearConstraint(np.concatenate([np.asarray(co2, float), np.zeros(1 + S)])[None, :], lb=-np.inf, ub=co2_cap))
    for members in exclusive:
        row = np.zeros(n_var)
        row[list(members)] = 1.0
        constraints.append(LinearConstraint(row[None, :], lb=-np.inf, ub=1.0))
    integrality = np.concatenate([np.ones(n), np.zeros(1 + S)])
    bounds = Bounds(lb=np.concatenate([np.zeros(n), [-np.inf], np.zeros(S)]), ub=np.concatenate([np.ones(n), [np.inf], np.full(S, np.inf)]))
    res = milp(c, constraints=constraints, integrality=integrality, bounds=bounds, options={"time_limit": time_limit, "mip_rel_gap": 1e-4})
    if res.x is None or res.status != 0:
        raise RuntimeError(f"MILP did not reach an optimum: {res.message} (status {res.status})")
    x = np.round(res.x[:n]).astype(int)
    total = A @ x * scale
    return {"x": x, "expected_npv": float(total.mean()), "cvar_loss": cvar(-total, level), "objective": float(total.mean() - lam * cvar(-total, level)),
            "status": res.message, "capex_used": float(capex @ x * scale)}


def top_n_by_npv(expected_npv, capex, budget):
    """Comparator A: take candidates in order of expected NPV while the budget allows (positive NPV only)."""
    x = np.zeros(len(expected_npv), int)
    spent = 0.0
    for i in np.argsort(-np.asarray(expected_npv, float)):
        if expected_npv[i] <= 0:
            break
        if spent + capex[i] <= budget:
            x[i] = 1
            spent += capex[i]
    return x


def equal_capital_by_sector(expected_npv, capex, sectors, budget):
    """Comparator B: the budget split equally across sectors, each filled by NPV per dollar of capital (positive NPV only)."""
    sectors = np.asarray(sectors)
    x = np.zeros(len(expected_npv), int)
    per_sector = budget / len(np.unique(sectors))
    ratio = np.asarray(expected_npv, float) / np.asarray(capex, float)
    for s in np.unique(sectors):
        spent = 0.0
        for i in np.argsort(-ratio):
            if sectors[i] != s or expected_npv[i] <= 0:
                continue
            if spent + capex[i] <= per_sector:
                x[i] = 1
                spent += capex[i]
    return x


def jaccard(x, y):
    """Jaccard similarity of two 0/1 selections."""
    a, b = np.asarray(x, bool), np.asarray(y, bool)
    union = (a | b).sum()
    return float((a & b).sum() / union) if union else 1.0


def score_books(books, npv_scenarios, lam=1.0, level=0.95):
    """E[NPV], CVaR of the loss and the metric of each named book on one scenario set."""
    rows = []
    for name, x in books.items():
        total = np.asarray(npv_scenarios, float) @ np.asarray(x, float)
        rows.append({"book": name, "n_selected": int(np.sum(x)), "expected_npv": float(total.mean()), "cvar_loss": cvar(-total, level),
                     "p_negative": float((total < 0).mean()), "metric": float(total.mean() - lam * cvar(-total, level))})
    return pd.DataFrame(rows)


def paired_scenario_bootstrap(npv_scenarios, x_a, x_b, lam=1.0, level=0.95, n_boot=1000, seed=2020):
    """Interval of metric(A) − metric(B) by resampling scenarios with replacement; pass when entirely above 0."""
    A = np.asarray(npv_scenarios, float)
    ta, tb = A @ np.asarray(x_a, float), A @ np.asarray(x_b, float)
    rng = np.random.default_rng(seed)
    S = len(ta)
    diffs = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, S, size=S)
        a, b = ta[idx], tb[idx]
        diffs[k] = (a.mean() - lam * cvar(-a, level)) - (b.mean() - lam * cvar(-b, level))
    point = (ta.mean() - lam * cvar(-ta, level)) - (tb.mean() - lam * cvar(-tb, level))
    low, high = float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))
    return {"diff": float(point), "low": low, "high": high, "pass": bool(low > 0)}
