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


def tail_count(n, level=0.95):
    """Number of scenarios in the worst (1 − level) share of ``n``.

    Notes
    -----
    Rounded before the ceiling: (1 − 0.95) × 2000 is 100.00000000000009 in
    floating point, which an unrounded ceiling turns into 101 (audit A13).
    """
    return max(1, int(np.ceil(round((1 - level) * n, 9))))


def cvar(losses, level=0.95):
    """CVaR of a loss sample: the mean of the worst (1 − level) share, the same count the R–U objective divides by."""
    x = np.sort(np.asarray(losses, float))[::-1]
    return float(x[:tail_count(len(x), level)].mean())


def book_metric(npv_scenarios, x, lam=1.0, level=0.95):
    """E[NPV] − λ·CVaR_level(loss) of the book ``x`` over the scenarios (scenarios × candidates)."""
    total = np.asarray(npv_scenarios, float) @ np.asarray(x, float)
    return float(total.mean() - lam * cvar(-total, level))


class InfeasibleBook(RuntimeError):
    """No book satisfies the constraints (a CVaR limit tighter than any book can meet, members forced in over the budget)."""


def solve_milp(npv_scenarios, capex, budget, lam=1.0, level=0.95, groups=None, group_cap=None, co2=None, co2_cap=None,
               exclusive=(), time_limit=300, cvar_cap=None, forced_in=(), forced_out=(), reference=None, max_changes=None,
               calls=None, calls_cap=None):
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
    cvar_cap : float, optional
        Hard limit on the book's CVaR of loss ($): the committee's downside
        rule written as a constraint rather than a penalty.
    forced_in, forced_out : iterable of int
        Candidate indices that must be in, or out of, the book (an existing
        commitment; a project the committee has ruled out; the explanation's
        forced re-solves).
    reference : array-like of 0/1, optional
        A book to stay close to (the committee's own proposal).
    max_changes : int, optional
        With ``reference``: at most this many candidates may differ from it
        (added plus dropped). The repair tool of the challenger raises it one
        step at a time to find the smallest change that meets the committee's
        rules (decision #94).
    calls, calls_cap : numpy.ndarray, float, optional
        Scenarios × candidates construction capital called beyond each
        candidate's reserve ($), and a limit on the CVaR at ``level`` of the
        book's total: the committee's liquidity line as a constraint. CVaR is
        at least the quantile, so the book's 95th-percentile excess is then
        within the line too (a conservative linear form of the chance
        constraint).

    Returns
    -------
    dict
        ``x`` (0/1 array), ``expected_npv``, ``cvar_loss``, ``objective``,
        ``status``, ``capex_used``.

    Raises
    ------
    InfeasibleBook
        When no book meets the constraints.

    Notes
    -----
    The problem is solved in millions of dollars (HiGHS stalls on
    dollar-scale coefficients) and raises when the solver does not reach an
    optimum, so a time-limited incumbent is never mistaken for an answer.
    Variables: x (binary, n), α (free) and u_s ≥ 0 (one per scenario).
    CVaR of the loss L_s = −NPV_s·x equals min_α α + Σ u_s / ((1 − level) S)
    with u_s ≥ L_s − α, so the objective −μ·x + λ(α + Σ u_s/((1−level)S))
    is linear. With λ = 0 the α and u variables are left in but do nothing.
    A CVaR limit uses the same variables: α + Σ u_s/((1−level)S) ≤ cap holds
    for some α exactly when the book's CVaR is at most the cap, because CVaR
    is the minimum of that expression over α (Rockafellar and Uryasev, 2000).
    """
    scale = 1e6  # solve in $ millions: dollar-scale coefficients stall HiGHS's branch and bound
    A = np.asarray(npv_scenarios, float) / scale
    S, n = A.shape
    capex = np.asarray(capex, float) / scale
    budget = budget / scale
    mu = A.mean(axis=0)
    liquidity = calls is not None and calls_cap is not None
    extra = 1 + S if liquidity else 0  # beta and v_s for the CVaR of the construction calls
    n_var = n + 1 + S + extra  # x, alpha, u (, beta, v)

    def pad(head, tail=None):
        """A row over every variable: ``head`` from the start (x, then alpha and u if given), ``tail`` over beta and v."""
        row = np.zeros(n_var)
        row[: len(head)] = head
        if tail is not None:
            row[n + 1 + S:] = tail
        return row

    c = np.concatenate([-mu, [lam], np.full(S, lam / ((1 - level) * S)), np.zeros(extra)])
    constraints = []
    # u_s + alpha + NPV_s · x >= 0
    rows = np.hstack([A, np.ones((S, 1)), np.eye(S), np.zeros((S, extra))])
    constraints.append(LinearConstraint(rows, lb=np.zeros(S), ub=np.full(S, np.inf)))
    # budget
    constraints.append(LinearConstraint(pad(capex)[None, :], lb=-np.inf, ub=budget))
    if groups is not None and group_cap is not None:
        groups = np.asarray(groups)
        for g in np.unique(groups):
            constraints.append(LinearConstraint(pad(np.where(groups == g, capex, 0.0))[None, :], lb=-np.inf, ub=group_cap * budget))
    if co2 is not None and co2_cap is not None:
        constraints.append(LinearConstraint(pad(np.asarray(co2, float))[None, :], lb=-np.inf, ub=co2_cap))
    for members in exclusive:
        row = np.zeros(n_var)
        row[list(members)] = 1.0
        constraints.append(LinearConstraint(row[None, :], lb=-np.inf, ub=1.0))
    if cvar_cap is not None:
        row = pad(np.concatenate([np.zeros(n), [1.0], np.full(S, 1.0 / ((1 - level) * S))]))
        constraints.append(LinearConstraint(row[None, :], lb=-np.inf, ub=cvar_cap / scale))
    if reference is not None and max_changes is not None:
        ref = np.asarray(reference, float)
        # changes = sum over ref=1 of (1 - x_j) + sum over ref=0 of x_j = sum (1 - 2 ref_j) x_j + sum ref_j
        constraints.append(LinearConstraint(pad(1.0 - 2.0 * ref)[None, :], lb=-np.inf, ub=max_changes - ref.sum()))
    if liquidity:
        C = np.asarray(calls, float) / scale
        # v_s + beta - C_s · x >= 0, and beta + sum v_s / ((1 - level) S) <= cap: the CVaR of the calls within the line
        rows = np.hstack([-C, np.zeros((S, 1 + S)), np.ones((S, 1)), np.eye(S)])
        constraints.append(LinearConstraint(rows, lb=np.zeros(S), ub=np.full(S, np.inf)))
        tail = np.concatenate([[1.0], np.full(S, 1.0 / ((1 - level) * S))])
        constraints.append(LinearConstraint(pad(np.zeros(n), tail)[None, :], lb=-np.inf, ub=calls_cap / scale))
    integrality = np.concatenate([np.ones(n), np.zeros(1 + S + extra)])
    lower, upper = np.zeros(n), np.ones(n)
    lower[list(forced_in)] = 1.0
    upper[list(forced_out)] = 0.0
    lb_extra = np.concatenate([[-np.inf], np.zeros(S)]) if liquidity else np.zeros(0)
    bounds = Bounds(lb=np.concatenate([lower, [-np.inf], np.zeros(S), lb_extra]), ub=np.concatenate([upper, [np.inf], np.full(S, np.inf), np.full(extra, np.inf)]))
    res = milp(c, constraints=constraints, integrality=integrality, bounds=bounds, options={"time_limit": time_limit, "mip_rel_gap": 1e-4})
    if res.status == 2:
        raise InfeasibleBook(f"no book meets the constraints: {res.message}")
    if res.x is None or res.status != 0:
        raise RuntimeError(f"MILP did not reach an optimum: {res.message} (status {res.status})")
    x = np.round(res.x[:n]).astype(int)
    total = A @ x * scale
    return {"x": x, "expected_npv": float(total.mean()), "cvar_loss": cvar(-total, level), "objective": float(total.mean() - lam * cvar(-total, level)),
            "status": res.message, "capex_used": float(capex @ x * scale)}


def _fits(i, capex, spent_group, groups, group_cap, budget):
    """True when candidate ``i`` keeps its group within ``group_cap`` × ``budget`` (always true without a cap)."""
    if groups is None or group_cap is None:
        return True
    return spent_group.get(groups[i], 0.0) + capex[i] <= group_cap * budget + 1e-9


def top_n_by_npv(expected_npv, capex, budget, groups=None, group_cap=None):
    """Comparator A: take candidates in order of expected NPV while the budget and the group cap allow (positive NPV only).

    Notes
    -----
    The registration of C21–C24 applies the 40% technology cap to every book;
    the comparator as first run ignored it, so it could put two thirds of the
    budget into leases while C and D could not (audit A1). With ``groups`` and
    ``group_cap`` a candidate that would breach its group's cap is skipped and
    the ranking continues, as an analyst filling a capped book by hand would.
    """
    groups = None if groups is None else np.asarray(groups)
    x = np.zeros(len(expected_npv), int)
    spent, spent_group = 0.0, {}
    for i in np.argsort(-np.asarray(expected_npv, float)):
        if expected_npv[i] <= 0:
            break
        if spent + capex[i] <= budget and _fits(i, capex, spent_group, groups, group_cap, budget):
            x[i] = 1
            spent += capex[i]
            if groups is not None:
                spent_group[groups[i]] = spent_group.get(groups[i], 0.0) + capex[i]
    return x


def equal_capital_by_sector(expected_npv, capex, sectors, budget, groups=None, group_cap=None):
    """Comparator B: the budget split equally across sectors, each filled by NPV per dollar of capital (positive NPV only).

    Notes
    -----
    ``groups`` and ``group_cap`` hold B to the same technology cap as the
    other books (audit A1); the cap is a share of the whole budget, not of the
    sector's half.
    """
    sectors = np.asarray(sectors)
    groups = None if groups is None else np.asarray(groups)
    x = np.zeros(len(expected_npv), int)
    per_sector = budget / len(np.unique(sectors))
    ratio = np.asarray(expected_npv, float) / np.asarray(capex, float)
    spent_group = {}
    for s in np.unique(sectors):
        spent = 0.0
        for i in np.argsort(-ratio):
            if sectors[i] != s or expected_npv[i] <= 0:
                continue
            if spent + capex[i] <= per_sector and _fits(i, capex, spent_group, groups, group_cap, budget):
                x[i] = 1
                spent += capex[i]
                if groups is not None:
                    spent_group[groups[i]] = spent_group.get(groups[i], 0.0) + capex[i]
    return x


def violations(x, capex, budget, groups=None, group_cap=None):
    """Constraint violations of a book: budget overrun and each group above its cap ($; empty when feasible)."""
    x, capex = np.asarray(x, float), np.asarray(capex, float)
    out = {}
    if capex @ x > budget + 1e-6:
        out["budget"] = float(capex @ x - budget)
    if groups is not None and group_cap is not None:
        groups = np.asarray(groups)
        for g in np.unique(groups):
            over = capex[groups == g] @ x[groups == g] - group_cap * budget
            if over > 1e-6:
                out[str(g)] = float(over)
    return out


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


def book_diff(x_old, x_new, ids, npv_scenarios, charge, groups, level=0.95):
    """What changes between two books: who enters and leaves, and the change in capital, value, tail and concentration.

    Parameters
    ----------
    x_old, x_new : array-like
        0/1 selections.
    ids : list of str
        Candidate ids in column order.
    npv_scenarios : numpy.ndarray
        Scenarios × candidates, the set both books are scored on.
    charge : array-like
        What each candidate costs the budget.
    groups : array-like
        Technology of each candidate.
    level : float
        CVaR level.

    Returns
    -------
    dict
        ``entered`` and ``left`` (ids), and for each book and their difference:
        ``charge``, ``expected_npv``, ``median_npv``, ``p_loss``, ``cvar_loss``
        and ``hhi`` (the Herfindahl index of the charge across technologies,
        1 for a one-technology book).
    """
    ids = np.asarray(ids)
    A = np.asarray(npv_scenarios, float)
    charge, groups = np.asarray(charge, float), np.asarray(groups)

    def describe(x):
        x = np.asarray(x, int)
        total = A @ x
        spent = charge @ x
        shares = np.array([charge[groups == g] @ x[groups == g] for g in np.unique(groups)]) / spent if spent > 0 else np.zeros(1)
        return {"charge": float(spent), "expected_npv": float(total.mean()), "median_npv": float(np.median(total)), "p_loss": float((total < 0).mean()),
                "cvar_loss": cvar(-total, level), "hhi": float((shares ** 2).sum()), "n": int(x.sum())}

    old, new = describe(x_old), describe(x_new)
    x_old, x_new = np.asarray(x_old, int), np.asarray(x_new, int)
    return {"entered": list(ids[(x_new == 1) & (x_old == 0)]), "left": list(ids[(x_old == 1) & (x_new == 0)]),
            "old": old, "new": new, "change": {k: new[k] - old[k] for k in old}}
