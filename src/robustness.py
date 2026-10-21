"""How far a chosen book can be trusted: tail noise, selection noise, capital calls and tail dependence.

What: four checks on a book chosen by the optimizer — its score on the
scenarios it was chosen on against the held-out ones; how often it, and its
margin over NPV ranking, survive re-selection on resampled scenario sets; the
construction capital its requests call beyond the reserve, and what the book
is worth when calls beyond a liquidity line cannot be funded; and how much of
each candidate's value sits in its best scenarios.
Why: the review of 19 October found that two draws of the same generator
disagree about every book's tail by about $0.2B, that book D's members change
when it is re-selected, and that the reserve is exceeded in 45% of scenarios
(V1, V3); a committee needs these beside the book, and the advisor's tools
(decision #94) call the same functions.
Reads / writes: nothing; notebook 11 passes the matrices in and saves `results/v8/robustness_*.csv`.
Used by: notebook 11; `tests/test_robustness.py`.
"""

import numpy as np
import pandas as pd

from src import config, optimizer as opt


def in_vs_out(books, A_selection, A_held, lam=1.0, level=0.95):
    """Each book scored on the scenarios it was chosen on and on the held-out set.

    Parameters
    ----------
    books : dict
        Name → 0/1 vector over candidates.
    A_selection, A_held : numpy.ndarray
        Scenarios × candidates NPV on the selection set and the held-out set.
    lam, level : float
        The registered metric's weight and tail level.

    Returns
    -------
    pandas.DataFrame
        One row per book: mean, CVaR95 loss and metric on each set, and the change.

    Notes
    -----
    A book whose metric falls much more than the others' was chosen on noise;
    a fall shared by every book is the held-out set's tail being heavier, which
    is Monte Carlo noise in a 100-scenario tail, not a property of any book.
    """
    rows = []
    for name, x in books.items():
        x = np.asarray(x, int)
        ins, out = A_selection @ x, A_held @ x
        rows.append({"book": name, "mean_in": ins.mean(), "cvar_in": opt.cvar(-ins, level), "metric_in": opt.book_metric(A_selection, x, lam, level),
                     "mean_out": out.mean(), "cvar_out": opt.cvar(-out, level), "metric_out": opt.book_metric(A_held, x, lam, level)})
    t = pd.DataFrame(rows)
    t["mean_change"] = t["mean_out"] - t["mean_in"]
    t["metric_change"] = t["metric_out"] - t["metric_in"]
    return t


def reselect(A, A_held, charge, budget, groups, cap, x_ref, n=20, lam=1.0, level=0.95, seed=2020):
    """Book D and book A re-chosen on ``n`` bootstrap resamples of the selection set, each scored on the held-out set.

    Parameters
    ----------
    A, A_held : numpy.ndarray
        Scenarios × candidates NPV, selection and held-out.
    charge : numpy.ndarray
        Each candidate's stage-one charge.
    budget, cap : float
        The budget and the technology cap (share of the budget).
    groups : numpy.ndarray
        Each candidate's technology.
    x_ref : numpy.ndarray
        The reported book D.
    n, lam, level, seed
        Resamples, the registered metric, the seed.

    Returns
    -------
    tuple of (pandas.DataFrame, numpy.ndarray)
        One row per resample (D minus A on the held-out metric and mean, D's size
        and overlap with the reported book) and each candidate's share of
        resamples in which D holds it.

    Notes
    -----
    The paired scenario bootstrap of the report resamples the scoring set only,
    so its interval leaves out the noise in the choice itself. Re-choosing on
    resampled selection sets puts it back: a ranking that holds in every
    resample is robust to it, a member held in few is a swing member.
    """
    rng = np.random.default_rng(seed)
    freq = np.zeros(A.shape[1])
    rows = []
    for b in range(n):
        idx = rng.integers(0, A.shape[0], A.shape[0])
        Ab = A[idx]
        xd = opt.solve_milp(Ab, charge, budget, lam=lam, level=level, groups=groups, group_cap=cap)["x"]
        xa = opt.top_n_by_npv(Ab.mean(axis=0), charge, budget, groups=groups, group_cap=cap)
        freq += xd
        rows.append({"resample": b, "d_minus_a_metric": opt.book_metric(A_held, xd, lam, level) - opt.book_metric(A_held, xa, lam, level),
                     "d_minus_a_mean": float((A_held @ xd).mean() - (A_held @ xa).mean()), "n_D": int(xd.sum()),
                     "jaccard_to_reported_D": opt.jaccard(xd, x_ref)})
    return pd.DataFrame(rows), freq / n


def capital_calls(op_year, capex, member, p_operation):
    """Construction capital the book's requests call in each scenario, against the reserve.

    Parameters
    ----------
    op_year : numpy.ndarray
        Scenarios × requests operation year (0 = never within the window).
    capex : numpy.ndarray
        Each request's full plant capital ($).
    member : numpy.ndarray
        0/1, whether the book holds each request.
    p_operation : numpy.ndarray
        Each request's chance of operating within the window.

    Returns
    -------
    dict
        ``reserve``, ``drawn`` (per scenario), ``excess`` (per scenario) and
        summary shares and quantiles.

    Notes
    -----
    The stage-one charge reserves each request's expected draw, P × capital
    (decision #90). With a few large requests the draw is lumpy: either a big
    plant reaches its agreement or it does not, so the reserve is exceeded
    often and by a lot. This is the quantity a committee needs as a liquidity
    line.
    """
    member = np.asarray(member, bool)
    built = (np.asarray(op_year) > 0)[:, member]
    cap = np.asarray(capex, float)[member]
    drawn = built @ cap
    reserve = float((cap * np.asarray(p_operation, float)[member]).sum())
    excess = drawn - reserve
    over = excess > 0
    return {"reserve": reserve, "drawn": drawn, "excess": excess, "p_over": float(over.mean()),
            "mean_excess_when_over": float(excess[over].mean()) if over.any() else 0.0,
            "excess_q90": float(np.quantile(excess, 0.90)), "excess_q95": float(np.quantile(excess, 0.95)), "excess_max": float(excess.max())}


def _funded(built_s, cap, pri, budget):
    """Which of a scenario's built requests are funded: in priority order until ``budget`` is spent (one rule for both the value and its financing)."""
    funded = np.zeros(len(cap), bool)
    spent = 0.0
    idx = np.where(built_s)[0]
    for j in idx[np.argsort(-pri[idx], kind="stable")]:
        if spent + cap[j] <= budget + 1e-6:
            spent += cap[j]
            funded[j] = True
    return funded


def funding_or_forfeit(A_power, op_year, capex, carry, member, reserve, line, priority, fee=0.0, rate=0.0,
                       discount=config.LINE_DISCOUNT, build_years=config.CONSTRUCTION_YEARS, years=config.LINE_YEARS):
    """The power side of a book when construction calls beyond the reserve plus a liquidity line cannot be funded.

    Parameters
    ----------
    A_power : numpy.ndarray
        Scenarios × requests NPV (built: value net of carry; not built: −carry).
    op_year : numpy.ndarray
        Scenarios × requests operation year.
    capex, carry : numpy.ndarray
        Each request's plant capital and its carry (deposits and studies).
    member : numpy.ndarray
        0/1, whether the book holds each request.
    reserve, line : float
        Capital set aside at stage one, and the extra capital the committee can call.
    priority : numpy.ndarray
        Each request's funding priority, known before the scenario unfolds
        (expected NPV per dollar of capital on the selection scenarios).
    fee, rate : float
        The line's commitment fee a year on its undrawn part and the interest
        a year on its drawn part; both zero by default, so the value is gross
        of financing as in report v9. See ``financing_cost``.
    discount, build_years, years : float, int, int
        Passed to ``financing_cost``.

    Returns
    -------
    numpy.ndarray
        The book's power NPV in each scenario under the rule, net of the
        line's financing cost when a fee or a rate is given.

    Notes
    -----
    In each scenario the requests that reach operation are funded in the
    order of ``priority`` until reserve + line is spent; the rest forfeit and
    are worth −carry, their deposits lost. With an unlimited line this equals
    the static book. The order must be known in advance: ranking by each
    scenario's realized value would let the rule see the future and flatter
    a limited line (the first version did; it made a $1B line look better
    than unlimited capital). It is a two-stage *evaluation* of a fixed book,
    not a re-optimization.
    """
    member = np.asarray(member, bool)
    A_p = np.asarray(A_power, float)[:, member]
    built = (np.asarray(op_year) > 0)[:, member]
    cap = np.asarray(capex, float)[member]
    car = np.asarray(carry, float)[member]
    pri = np.asarray(priority, float)[member]
    out = np.empty(A_p.shape[0])
    budget = reserve + line
    for s in range(A_p.shape[0]):
        funded = _funded(built[s], cap, pri, budget)
        forfeited = built[s] & ~funded
        out[s] = A_p[s, funded].sum() - car[forfeited].sum() + A_p[s, ~built[s]].sum()
    if fee > 0 or rate > 0:
        out = out - financing_cost(op_year, capex, member, reserve, line, priority, fee, rate, discount, build_years, years)
    return out


def financing_cost(op_year, capex, member, reserve, line, priority, fee=config.LINE_FEE, rate=config.LINE_RATE,
                   discount=config.LINE_DISCOUNT, build_years=config.CONSTRUCTION_YEARS, years=config.LINE_YEARS):
    """What the liquidity line costs in each scenario: a commitment fee on what is not drawn, interest on what is.

    Parameters
    ----------
    op_year, capex, member, reserve, line, priority
        As in ``funding_or_forfeit``; the same funding rule decides which
        requests draw.
    fee : float
        Commitment fee a year on the undrawn part of the line.
    rate : float
        Interest a year on the drawn part, from the construction draw until
        the plant operates.
    discount : float
        The rate the yearly costs are discounted at (the committee grid's
        hurdle).
    build_years : int
        Years between a plant's construction draw and its operation
        (ASSUMED); the draw is ``build_years`` before ``op_year``, not before
        year 1.
    years : int
        The commitment period, the years the fee is charged.

    Returns
    -------
    numpy.ndarray
        The present value of the line's cost in each scenario ($).

    Notes
    -----
    Report v9 valued the line as free: "a $3.28B line restores $2.02B". A
    line is a product a bank sells, so its value to the book is net of what
    it costs. The reserve is spent first in time order, the line after it:
    a funded plant whose cumulative draw passes the reserve draws the excess
    on the line in its construction year and repays it at operation (the
    plant is then financed on its own). The fee runs on the whole undrawn
    line through the commitment period. The costs are per scenario, so they
    enter the tail as they would be paid; an "unlimited" line has no fee
    (``line`` is a benchmark there, not a product).
    """
    member = np.asarray(member, bool)
    built = (np.asarray(op_year) > 0)[:, member]
    t_op = np.asarray(op_year)[:, member]
    cap = np.asarray(capex, float)[member]
    pri = np.asarray(priority, float)[member]
    disc = (1 + discount) ** -np.arange(1, years + 1)
    out = np.zeros(built.shape[0])
    if line <= 0 or not np.isfinite(line):
        return out
    for s in range(built.shape[0]):
        funded = _funded(built[s], cap, pri, reserve + line)
        idx = np.where(funded)[0]
        draw_year = np.maximum(1, t_op[s, idx] - build_years)
        order = np.lexsort((-pri[idx], draw_year))  # time order; the priority breaks ties within a year
        outstanding = np.zeros(years)
        cum = 0.0
        for k in order:
            on_line = max(0.0, cum + cap[idx[k]] - max(reserve, cum))  # the part of this draw beyond the reserve
            cum += cap[idx[k]]
            if on_line > 0:
                d = int(draw_year[k])
                outstanding[d - 1:min(years, d - 1 + build_years)] += on_line
        yearly = rate * outstanding + fee * np.maximum(0.0, line - outstanding)
        out[s] = float(yearly @ disc)
    return out


def breakeven_fee(value_at, target, hi=0.2, tol=1e-6):
    """The commitment fee at which a line is worth no more than no line.

    Parameters
    ----------
    value_at : callable
        ``fee -> value`` of the book with the line, decreasing in the fee.
    target : float
        The book's value without the line.
    hi : float
        The largest fee searched.

    Returns
    -------
    float
        The fee where ``value_at(fee) == target``, by bisection; NaN when the
        line is worth less than no line even at a zero fee, or still worth
        more at ``hi``.
    """
    lo_v, hi_v = value_at(0.0), value_at(hi)
    if lo_v <= target or hi_v > target:
        return float("nan")
    lo, high = 0.0, hi
    while high - lo > tol:
        mid = (lo + high) / 2
        if value_at(mid) > target:
            lo = mid
        else:
            high = mid
    return (lo + high) / 2


def tail_dependence(values, top=0.05):
    """How a candidate's value is spread over the scenarios.

    Parameters
    ----------
    values : numpy.ndarray
        The candidate's NPV in each scenario.
    top : float
        The share of best scenarios examined.

    Returns
    -------
    dict
        ``mean``, ``p_loss``, and ``share_from_top``: the share of the total
        value earned in the best ``top`` of scenarios (NaN when the total is
        not positive).

    Notes
    -----
    A candidate with a positive mean, a high chance of loss and most of its
    value in a few scenarios is an option on rare outcomes, not an asset: its
    place in the book rests on those outcomes recurring as the scenario model
    assumes.
    """
    v = np.asarray(values, float)
    best = v >= np.quantile(v, 1 - top)
    total = v.sum()
    return {"mean": float(v.mean()), "p_loss": float((v < 0).mean()), "share_from_top": float(v[best].sum() / total) if total > 0 else np.nan}
