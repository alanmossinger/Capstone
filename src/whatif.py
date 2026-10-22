"""What-ifs a committee asks in words, answered by the models: a validated parameter set, a repricing, a re-solve, a diff.

What: ``WhatIf`` is the only way a question reaches the numbers — a small set
of named, bounded parameters (oil, gas and power prices, ERCOT volatility,
the budget, lease and plant costs, delays, credits, the risk policy, members
forced in or out). ``Engine`` loads the candidates and the saved scenario
draws of notebook 08, reprices every candidate under the what-if with
``src/valuation.py``, re-solves the book with ``src/optimizer.py``, and
reports what entered and left, why each candidate is in or out (its
opportunity cost from forced re-solves) and a status for each: invest now,
defer, monitor or reject.
Why: the advisor of v6 could only read tables and answer in prose (audit
S1). In v8 the language model turns a question into a ``WhatIf``, this
module checks it and computes the answer, and the model explains the table
it gets back; a question the schema cannot represent is refused, not
guessed (decision #91).
Reads: `results/candidate_npv.csv`, `results/scenario_settings.csv`,
`data/interim/scenario_state.npz` (notebook 08), `data/interim/upstream_monthly.parquet`,
the ERCOT 2024 files and the ATB table (the same basis as notebooks 07–08).
Writes: nothing.
Used by: notebook 11, the decision page (`app/decide.py`), `src/advisor.py`; `tests/test_whatif.py`.
"""

from dataclasses import asdict, dataclass, field, fields

import numpy as np
import pandas as pd

from src import config, decision_date, economics as ec, energy_data, optimizer as opt, paths, valuation as va

LIMITS = {  # parameter -> (lowest, highest) the engine accepts; outside them the question is refused
    "wti_level": (10.0, 200.0), "wti_years": (1, 20), "hh_multiplier": (0.25, 4.0), "ercot_multiplier": (0.25, 4.0),
    "ercot_volatility": (0.0, 2.0), "budget_multiplier": (0.2, 2.0), "lease_cost_multiplier": (0.5, 3.0),
    "power_capex_multiplier": (0.5, 3.0), "delay_years": (0, 5), "lam": (0.0, 50.0), "technology_cap": (0.1, 1.0),
}


class WhatIfError(ValueError):
    """A question the engine cannot represent, or a value outside the range it was built for."""


@dataclass
class WhatIf:
    """One committee question as numbers. Every field has a default that reproduces the base case.

    Notes
    -----
    Prices: ``wti_level`` holds WTI at that real price for the first
    ``wti_years`` of every scenario; ``hh_multiplier`` and
    ``ercot_multiplier`` scale the whole path; ``ercot_volatility`` scales
    each ERCOT path's log distance from the month's median across scenarios
    (0.5 halves the spread, keeps the centre). Costs: ``lease_cost_multiplier``
    scales a lease's capital (workover and, under the committee grid,
    development cost per barrel); ``power_capex_multiplier`` a plant's.
    Timing: ``delay_years`` pushes every request's operation year back.
    Policy: ``lam`` the penalty on CVaR, ``cvar_limit_musd`` a hard limit on
    the book's worst-5% average loss ($ million), ``technology_cap`` the
    share of the budget any technology may take, ``budget_multiplier`` the
    budget. ``forced_in`` / ``forced_out`` are candidate ids.
    """

    grid: str = "committee"
    revenue_case: str = "contracted"
    wti_level: float | None = None
    wti_years: int = 5
    hh_multiplier: float = 1.0
    ercot_multiplier: float = 1.0
    ercot_volatility: float = 1.0
    budget_multiplier: float = 1.0
    lease_cost_multiplier: float = 1.0
    power_capex_multiplier: float = 1.0
    delay_years: int = 0
    credits: bool = True
    lam: float = 1.0
    cvar_limit_musd: float | None = None
    technology_cap: float = 0.4
    forced_in: list = field(default_factory=list)
    forced_out: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, d, ids=None):
        """Build and validate a what-if from a dict (the language model's JSON); unknown keys and bad values raise ``WhatIfError``."""
        known = {f.name for f in fields(cls)}
        unknown = set(d) - known
        if unknown:
            raise WhatIfError(f"the engine has no parameter for {sorted(unknown)}; it can change {sorted(known)}")
        w = cls(**{k: v for k, v in d.items() if v is not None or k in ("wti_level", "cvar_limit_musd")})
        w.validate(ids)
        return w

    def validate(self, ids=None):
        """Raise ``WhatIfError`` for any value the engine was not built to answer."""
        if self.grid not in ("registered", "committee"):
            raise WhatIfError(f"grid must be 'registered' or 'committee', not {self.grid!r}")
        if self.revenue_case not in ("merchant", "contracted"):
            raise WhatIfError(f"revenue_case must be 'merchant' or 'contracted', not {self.revenue_case!r}")
        for name, (lo, hi) in LIMITS.items():
            value = getattr(self, name)
            if value is None:
                continue
            if not lo <= value <= hi:
                raise WhatIfError(f"{name} = {value} is outside the range the engine was built for, [{lo}, {hi}]")
        if ids is not None:
            bad = [m for m in list(self.forced_in) + list(self.forced_out) if m not in set(ids)]
            if bad:
                raise WhatIfError(f"no candidate is called {bad}")
        if set(self.forced_in) & set(self.forced_out):
            raise WhatIfError("a candidate cannot be forced both in and out")
        return self

    def changes(self):
        """The fields that differ from the base case, for the ledger and the explanation."""
        base = asdict(WhatIf(grid=self.grid, revenue_case=self.revenue_case))
        return {k: v for k, v in asdict(self).items() if v != base[k]}


def apply_prices(prices, w, months_per_year=12):
    """The price paths under a what-if (scenarios × months × [WTI, Henry Hub, ERCOT]); the input is not changed."""
    p = np.array(prices, float)
    if w.wti_level is not None:
        p[:, : w.wti_years * months_per_year, 0] = w.wti_level
    p[:, :, 1] *= w.hh_multiplier
    if w.ercot_volatility != 1.0:
        log_e = np.log(p[:, :, 2])
        centre = np.median(log_e, axis=0, keepdims=True)
        p[:, :, 2] = np.exp(centre + w.ercot_volatility * (log_e - centre))
    p[:, :, 2] *= w.ercot_multiplier
    return p


def lease_capital(base_oil, base_gas, n_wells, grid):
    """Capital of one lease redevelopment under a grid ($): the month-0 capex of ``economics.lease_cash_flows``."""
    months = len(base_oil)
    flows = ec.lease_cash_flows(base_oil, base_gas, np.zeros(months), np.zeros(months), n_wells, "base", grid)
    return float(flows["capex"].sum())


class Engine:
    """The candidates, their scenario draws and the base book, loaded once; ``run`` answers one ``WhatIf``.

    Parameters
    ----------
    n_scenarios : int
        Scenarios used (the first ``n`` of the selection set): 2,000 for
        reported numbers, fewer for an interactive answer.
    scenario_set : {"primary", "held-out"}
        The selection set or the held-out draw of notebook 08.

    Notes
    -----
    The base book is the risk-aware MILP under the base ``WhatIf`` of the same
    grid and revenue case, so every answer is a difference against a book
    computed the same way. The budget is the registered rule — 40% of the
    forty candidates — in the units it is spent in: 40% of their stage-one
    charges (decisions #90, #92).
    """

    def __init__(self, n_scenarios=2000, scenario_set="primary", state_file=None):
        self.candidates = pd.read_csv(paths.RESULTS / "candidate_npv.csv")
        self.ids = list(self.candidates["project_id"])
        settings = pd.read_csv(paths.RESULTS / "scenario_settings.csv").iloc[0]
        self.base = np.array([settings["base_wti"], settings["base_hh"], settings["base_ercot"]])
        state = np.load(paths.DATA_INTERIM / "scenario_state.npz" if state_file is None else state_file)  # another draw set (the 5,000-path convergence check of notebook 12) by its file
        key = "" if scenario_set == "primary" else "_h"
        n = n_scenarios
        self.prices = state[f"prices{key}"][:n]
        self.out_lease, self.cost_mult = state[f"out_lease{key}"][:n], state[f"cost_mult{key}"][:n]
        self.out_power, self.op_year = state[f"out_power{key}"][:n], state[f"op_year{key}"][:n]
        self.horizon = self.prices.shape[1]
        self.leases = self.candidates[self.candidates["sector"] != "ERCOT power"].reset_index(drop=True)
        self.power = self.candidates[self.candidates["sector"] == "ERCOT power"].reset_index(drop=True)
        upstream = decision_date.lease_history_on(pd.read_parquet(paths.DATA_INTERIM / "upstream_monthly.parquet"))  # the months BSEE had published on the date
        lids = [p.split("|")[1] for p in self.leases["project_id"]]
        part = upstream[upstream["lease_number"].isin(lids)]
        oil = part.pivot(index="lease_number", columns="month", values="oil_bbl").fillna(0)
        gas = part.pivot(index="lease_number", columns="month", values="gas_mcf").fillna(0)
        self.baselines = [decision_date.lease_baseline_on(oil.loc[l].to_numpy(), gas.loc[l].to_numpy(), months=self.horizon)[:2] for l in lids]
        self.wells = self.leases["n_wells"].astype(int).to_numpy()
        cpi = energy_data.read_cpi(sorted(paths.RAW_PRICES.glob(f"bls_{config.CPI_SERIES}_*.json"))[-1])
        self.atb = va.atb_in_dollars_of(pd.read_csv(paths.RESULTS / "atb_costs.csv").set_index("tech"), va.cpi_ratio(cpi, 2022, config.REAL_DOLLAR_YEAR))
        dam = pd.read_parquet(paths.RAW_ERCOT / "ercot_dam_spp_2024.parquet")
        hub = dam[dam["Location"] == config.ERCOT_PRICE_HUB].set_index("Interval Start")["SPP"]
        ws = pd.read_parquet(paths.RAW_ERCOT / "ercot_wind_solar_2024.parquet")
        self.basis = va.basis_2024(hub, ws["solar_mw"], ws["wind_mw"], self.atb, self.base[1])
        self.base_books = {}

    def grid(self, w):
        """The lease grid of a what-if: the registered base, the committee overrides, the cost multiplier on capital."""
        g = ec.grid_case("base")
        if w.grid == "committee":
            g = {**g, **ec.committee_case("base")}
        g = dict(g)
        g["workover_cost_per_well_usd"] *= w.lease_cost_multiplier
        if "dev_cost_per_flowing_boed_usd" in g:
            g["dev_cost_per_flowing_boed_usd"] *= w.lease_cost_multiplier
        return g

    def matrix(self, w):
        """Scenarios × candidates NPV, and each candidate's stage-one charge, under the what-if."""
        prices = apply_prices(self.prices, w)
        g = self.grid(w)
        L = va.lease_npv_matrix(self.baselines, self.wells, prices, self.out_lease, self.cost_mult, ec.grid_case("base"), grid=g)
        atb = self.atb.copy()
        atb["capex_per_kw"] = atb["capex_per_kw"] * w.power_capex_multiplier
        comps = {t: va.pv_components(va.TECH_OF[t], atb, self.basis, self.base[2], self.base[1]) for t in self.power["technology"].unique()}
        op_year = np.where(self.op_year > 0, self.op_year + w.delay_years, 0)
        op_year = np.where(op_year > 7, 0, op_year)  # a plant pushed past the seven-year window counts as not operating within it
        P = va.power_npv_matrix(self.power, comps, prices, self.out_power, op_year, self.base, self.horizon, w.revenue_case, w.credits)
        capital = self.capital(w)
        lease_capex, power_capex = capital[: len(self.leases)], capital[len(self.leases):]
        charge = np.concatenate([lease_capex, va.stage_one_charge(np.full(len(self.power), "ERCOT power"), power_capex,
                                                                 self.power["carry_cost"], self.power["p_operation_7y"])])
        return np.concatenate([L, P], axis=1), charge

    def capital(self, w):
        """Full capital of every candidate under the what-if: a lease's redevelopment capital, a plant's construction capital."""
        g = self.grid(w)
        lease_capex = np.array([lease_capital(bo, bg, n, g) for (bo, bg), n in zip(self.baselines, self.wells)])
        return np.concatenate([lease_capex, self.power["capex"].to_numpy(float) * w.power_capex_multiplier])

    def solve(self, w, A, charge, budget):
        """The book under the what-if's policy; ``None`` with the reason when no book meets it."""
        tech = self.candidates["technology"].to_numpy()
        try:
            out = opt.solve_milp(A, charge, budget, lam=w.lam, groups=tech, group_cap=w.technology_cap,
                                 cvar_cap=None if w.cvar_limit_musd is None else w.cvar_limit_musd * 1e6,
                                 forced_in=[self.ids.index(m) for m in w.forced_in], forced_out=[self.ids.index(m) for m in w.forced_out])
            return out["x"], None
        except opt.InfeasibleBook as err:
            return None, str(err)

    def base_case(self, grid="committee", revenue_case="contracted"):
        """The base book of a grid and revenue case, computed once."""
        key = (grid, revenue_case)
        if key not in self.base_books:
            w = WhatIf(grid=grid, revenue_case=revenue_case)
            A, charge = self.matrix(w)
            budget = 0.40 * charge.sum()  # the registered rule in the units the budget is spent in (decision #92)
            x, _ = self.solve(w, A, charge, budget)
            self.base_books[key] = {"x": x, "A": A, "charge": charge, "budget": budget}
        return self.base_books[key]

    def run(self, w):
        """Answer one what-if: the new book, its difference from the base book, and the status of every candidate.

        Returns
        -------
        dict
            ``whatif`` (the changes), ``budget``, ``feasible``, ``reason``,
            ``diff`` (``optimizer.book_diff``), ``candidates`` (a table:
            in/out, expected NPV, P(NPV < 0), status) and ``provenance``.
        """
        w.validate(self.ids)
        base = self.base_case(w.grid, w.revenue_case)
        A, charge = self.matrix(w)
        budget = base["budget"] * w.budget_multiplier
        x, reason = self.solve(w, A, charge, budget)
        result = {"whatif": w.changes(), "grid": w.grid, "revenue_case": w.revenue_case, "budget": float(budget), "feasible": x is not None, "reason": reason,
                  "n_scenarios": int(A.shape[0]), "provenance": "FORECAST (scenarios) on ASSUMED costs; computed by src/whatif.py, not by the language model"}
        if x is None:
            return result
        tech = self.candidates["technology"].to_numpy()
        result["diff"] = opt.book_diff(base["x"], x, self.ids, A, charge, tech)
        result["candidates"] = self.status_table(A, charge, x)
        return result

    def status_table(self, A, charge, x):
        """Every candidate's place in the book and its status, from stated rules (no language model)."""
        mu = A.mean(axis=0)
        t = pd.DataFrame({"project_id": self.ids, "technology": self.candidates["technology"], "sector": self.candidates["sector"], "in_book": np.asarray(x, bool),
                          "charge_$M": charge / 1e6, "expected_npv_$M": mu / 1e6, "median_npv_$M": np.median(A, axis=0) / 1e6, "p_negative": (A < 0).mean(axis=0),
                          "agreement_known": self.candidates.get("agreement_known", pd.Series(False, index=self.candidates.index)).fillna(False).astype(bool)})
        t["status"] = [status_of(r) for _, r in t.iterrows()]
        return t


def status_of(row):
    """Invest now, invest in stages, monitor or reject: the rule the decision page states beside every candidate.

    Notes
    -----
    In the book: a lease is *invest now*; a request with a signed agreement
    is *invest now* (its construction is near); a request without one is
    *invest in stages* — pay the deposit now, commit construction at the
    agreement (decision #90). Out of the book: a positive expected NPV means
    the budget, the cap or the tail kept it out, so *monitor*; a negative one
    is *reject*. *Defer pending information* is set by the value-of-information
    module where buying the information is worth more than it costs.
    """
    if row["in_book"]:
        if row["sector"] == "ERCOT power" and not row["agreement_known"]:
            return "invest in stages"
        return "invest now"
    return "monitor" if row["expected_npv_$M"] > 0 else "reject"


def explain(engine, w, x, A, charge, budget, members=None):
    """Opportunity cost of each candidate's place in the book: the objective lost by forcing it the other way.

    Parameters
    ----------
    engine : Engine
    w : WhatIf
    x : array-like
        The book.
    A, charge, budget :
        The matrix, charges and budget the book was solved on.
    members : list of str, optional
        Candidates to explain (all forty when None).

    Returns
    -------
    pandas.DataFrame
        ``project_id``, ``in_book``, ``objective_cost_$M`` (how much the
        best book's E[NPV] − λ·CVaR falls when this candidate is forced the
        other way; ``inf`` when no book can do it), and the change in
        expected NPV and CVaR that the forced book shows.

    Notes
    -----
    This is a model-supported explanation, not a causal one: it says what
    the optimizer gives up under these scenarios and costs, not why a
    project would succeed.
    """
    x = np.asarray(x, int)
    objective = opt.book_metric(A, x, w.lam)
    rows = []
    for m in members or engine.ids:
        i = engine.ids.index(m)
        forced = WhatIf(**{**asdict(w), "forced_in": [m] if x[i] == 0 else [], "forced_out": [m] if x[i] == 1 else []})
        y, reason = engine.solve(forced, A, charge, budget)
        if y is None:
            rows.append({"project_id": m, "in_book": bool(x[i]), "objective_cost_$M": np.inf, "expected_npv_change_$M": np.nan, "cvar_change_$M": np.nan, "note": reason})
            continue
        ty, tx = A @ y, A @ x
        rows.append({"project_id": m, "in_book": bool(x[i]), "objective_cost_$M": (objective - opt.book_metric(A, y, w.lam)) / 1e6,
                     "expected_npv_change_$M": (ty.mean() - tx.mean()) / 1e6, "cvar_change_$M": (opt.cvar(-ty) - opt.cvar(-tx)) / 1e6, "note": ""})
    return pd.DataFrame(rows)
