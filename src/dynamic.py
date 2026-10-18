"""Staged decisions: commit in 2025, learn until 2027, then continue, drop or start — a scenario-based extension.

What: a two-date policy on the same scenarios as the static book. On
1 January 2025 the company funds the static book's leases and pays the
deposits of its requests. On 1 January 2027 each scenario has revealed two
years of prices and, for each request, whether it signed its
interconnection agreement (a signal drawn with likelihoods from the queue
history). The company then (a) continues a request — committing its
construction — only if its expected value given that information beats
walking away from the deposit, and (b) starts a lease it deferred in 2025
if its expected value given the oil and gas prices so far is positive and
the capital released by dropped requests covers it. The expected values
given the information are least-squares regressions fitted on the primary
scenarios (Longstaff and Schwartz, 2001); the policy is scored on the
held-out scenarios it never saw.
Why: the static book commits everything on one date. The brief asks when
to invest, defer or reconsider, and what flexibility is worth. This
module measures that on the model's own scenarios; it does not establish
real future costs or real-option values, which no public file holds, and
the report labels it a scenario-based methodological extension (decision #91).
Reads / writes: nothing; notebook 11 passes the matrices in.
Used by: notebook 11; `tests/test_dynamic.py`.

Adapted from: Longstaff, F. A. and Schwartz, E. S. (2001), "Valuing
American options by simulation: a simple least-squares approach", Review of
Financial Studies 14(1), 113–147 — the regression of a continuation value
on what is known at the decision date.
"""

import numpy as np

from src import economics as ec, optimizer as opt

DECISION_MONTHS = 24  # the second decision date, 1 January 2027, in months after the first


def deferred_lease_matrix(baselines, wells, prices, out_mult, cost_mult, grid_base, grid=None, delay_months=DECISION_MONTHS):
    """NPV on 1 January 2025 of each lease redevelopment started ``delay_months`` later, in every scenario.

    Notes
    -----
    The do-nothing baseline keeps declining while the company waits, so the
    uplift applies to a lower rate; prices are the scenario's from the start
    month; the value is discounted back over the delay at the grid's rate.
    The months after the scenario's horizon hold its last price.
    """
    g = {**grid_base, **(grid or {})}
    months = prices.shape[1]
    shifted = np.concatenate([prices[:, delay_months:], np.repeat(prices[:, -1:], delay_months, axis=1)], axis=1)
    out = np.empty((prices.shape[0], len(baselines)))
    for j, (bo, bg) in enumerate(baselines):
        bo_d = np.concatenate([bo[delay_months:], np.zeros(delay_months)])[:months]
        bg_d = np.concatenate([bg[delay_months:], np.zeros(delay_months)])[:months]
        for s in range(prices.shape[0]):
            override = {**(grid or {}), "workover_cost_per_well_usd": g["workover_cost_per_well_usd"] * cost_mult[s], "opex_usd_per_boe": g["opex_usd_per_boe"] * cost_mult[s]}
            if "dev_cost_per_flowing_boed_usd" in g:
                override["dev_cost_per_flowing_boed_usd"] = g["dev_cost_per_flowing_boed_usd"] * cost_mult[s]
            value = ec.incremental_npv(bo_d * out_mult[s, j], bg_d * out_mult[s, j], shifted[s, :, 0], shifted[s, :, 1], int(wells[j]), "base", override)
            out[s, j] = value / (1 + g["wacc_real"]) ** (delay_months / 12)
    return out


def agreement_signal(op_year, p_signal_if_built, p_signal_if_not, decided_year=3, seed=2020):
    """Whether each request has signed its agreement by the second decision date, in every scenario.

    Parameters
    ----------
    op_year : numpy.ndarray
        Scenarios × requests operation year (0 = not within the window).
    p_signal_if_built, p_signal_if_not : float
        P(agreement by then | operates later in the window) and P(… | never), from the queue history.
    decided_year : int
        Requests already operating before this operation year have no
        decision left; their signal is set to 1.

    Notes
    -----
    The signal is conditionally independent across requests given their
    outcomes; the dependence between requests lives in the operation years.
    """
    rng = np.random.default_rng(seed)
    built = op_year > 0
    p = np.where(built, p_signal_if_built, p_signal_if_not)
    signal = rng.random(op_year.shape) < p
    return np.where((op_year > 0) & (op_year < decided_year), True, signal)


def features(prices, signal_j=None, months=DECISION_MONTHS):
    """What is known on the second date: the mean log prices of the first two years (and a request's signal)."""
    first = np.log(prices[:, :months].mean(axis=1))
    cols = [np.ones(len(prices)), first[:, 0], first[:, 1], first[:, 2]]
    if signal_j is not None:
        s = signal_j.astype(float)
        cols += [s, s * first[:, 2], s * first[:, 1]]
    return np.column_stack(cols)


def fit_continuation(X, y):
    """Least-squares coefficients of a continuation value on the features known at the decision date."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def staged_policy(book, A, A_deferred, carry, charge, budget, lease_mask, op_year, signal, prices, models=None, fit=False, lease_cap=None):
    """Payoff of the staged policy in every scenario, with what it did.

    Parameters
    ----------
    book : array-like
        The 2025 book (0/1 over all candidates): leases funded now, requests whose deposits are paid.
    A : numpy.ndarray
        Scenarios × candidates NPV of the static commitments (a request's value nets its carry).
    A_deferred : numpy.ndarray
        Scenarios × leases NPV if started at the second date.
    carry : numpy.ndarray
        Each request's deposits and studies (lost if it is dropped).
    charge : numpy.ndarray
        Stage-one charge of every candidate (a request's includes its construction reserve).
    budget : float
        The stage-one budget.
    lease_mask : numpy.ndarray of bool
        Which candidates are leases.
    op_year, signal : numpy.ndarray
        Scenarios × requests operation year and agreement signal.
    prices : numpy.ndarray
        Scenarios × months × 3.
    models : dict, optional
        Fitted regression coefficients (``fit=True`` returns them).
    fit : bool
        True on the primary scenarios: fit the continuation values, then apply them.
    lease_cap : float, optional
        Largest share of the budget the leases may take (the technology cap);
        deferred leases are started only within it, as the static book is.

    Returns
    -------
    dict
        ``payoff`` (scenarios), ``dropped`` and ``started`` (counts per
        scenario), ``redeployed`` (capital moved into deferred leases per
        scenario), ``models``.

    Notes
    -----
    A request still before operation on the second date is dropped when its
    predicted value given the information is below what walking away earns:
    −carry, plus its released construction reserve times the best predicted
    value per dollar among the deferred leases in that scenario. A request
    that never operates costs only its carry either way, so dropping it is
    worth something only through what its reserve can do elsewhere. The
    released reserves, with whatever the 2025 book left unspent, fund the
    deferred leases with a positive predicted value, best value per dollar
    first. Requests already operating, and leases funded in 2025, are not
    revisited.
    """
    book = np.asarray(book, int)
    S = A.shape[0]
    power_idx = np.where(~lease_mask)[0]
    lease_idx = list(np.where(lease_mask)[0])
    payoff = A[:, lease_idx] @ book[lease_idx]
    models = {} if models is None else dict(models)
    # the deferred leases first: their predicted value per dollar is what a released reserve could earn
    X0 = features(prices)
    candidates = [j for j in lease_idx if not book[j]]
    preds = {}
    for j in candidates:
        if fit:
            models[("lease", j)] = fit_continuation(X0, A_deferred[:, lease_idx.index(j)])
        preds[j] = X0 @ models[("lease", j)]
    cap_room = np.inf if lease_cap is None else lease_cap * budget - charge[lease_idx] @ book[lease_idx]
    startable = [j for j in candidates if charge[j] <= cap_room]  # a deferred lease the cap would never let in earns a released reserve nothing
    best_ratio = np.max([np.maximum(preds[j] / charge[j], 0.0) for j in startable], axis=0) if startable else np.zeros(S)
    reserve_released = np.zeros(S)
    dropped = np.zeros(S, int)
    for k, j in enumerate(power_idx):
        if not book[j]:
            continue
        value = A[:, j]
        open_ = ~((op_year[:, k] > 0) & (op_year[:, k] < 3))  # still before operation on the second date
        X = features(prices, signal[:, k])
        if fit:
            models[("request", j)] = fit_continuation(X[open_], value[open_])
        predicted = X @ models[("request", j)]
        release = charge[j] - carry[k]
        drop = open_ & (predicted < -carry[k] + best_ratio * release)
        payoff += np.where(drop, -carry[k], value)
        dropped += drop
        reserve_released += np.where(drop, release, 0.0)
    spare = budget - charge @ book + reserve_released
    if lease_cap is not None:  # the same cap as the static book: the revision may not buy past it (audit A1's lesson)
        spare = np.minimum(spare, lease_cap * budget - charge[lease_idx] @ book[lease_idx])
    started = np.zeros(S, int)
    redeployed = np.zeros(S)
    for s in range(S):
        order = sorted((j for j in candidates if preds[j][s] > 0), key=lambda j: -preds[j][s] / charge[j])
        room = spare[s]
        for j in order:
            if charge[j] <= room:
                room -= charge[j]
                payoff[s] += A_deferred[s, lease_idx.index(j)]
                started[s] += 1
                redeployed[s] += charge[j]
    return {"payoff": payoff, "dropped": dropped, "started": started, "redeployed": redeployed, "models": models}


def summarize(payoff, level=0.95):
    """Mean, median, P(loss) and CVaR95 of a payoff across scenarios."""
    payoff = np.asarray(payoff, float)
    return {"mean": float(payoff.mean()), "median": float(np.median(payoff)), "p_loss": float((payoff < 0).mean()), "cvar_loss": opt.cvar(-payoff, level)}
