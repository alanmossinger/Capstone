# Implementation plan v8 — from a static recommendation to an evaluated decision system (2026-10-17)

Built from `docs/audit_2026-10-17.md`. Order: freeze what was registered, fix what is broken, settle the
decision framing, then build the new layers on the corrected engine, then evaluate, then write. Each phase
ends with its acceptance checks; the next starts only when they pass (CLAUDE.md §1.5).

## Rules that hold throughout

- The registered record is frozen before any rerun: `results/registered_v7/` holds the v7 scoring as run
  (C21–C24, Table F3, the gym, the advisor scores) with a hash test. Corrections are scored beside it, labelled
  *implementation correction* (the code did not do what the registration said: A1, A13, E2, E10, G2) or
  *post-registration extension* (anything new). No registered verdict is edited.
- New outputs go to `results/v8/` and `figures/v8/`; the report cites them through `src/report_numbers.py`.
- The language model never produces a number the report uses. It translates questions into validated
  parameters, the code computes, and it explains what the code returned.

## Decisions needed before Phase C (ASK ALAN)

1. **One decision date for both sectors (E1).** Recommended: *decide on 2025-01-01*, the date the leases are
   already valued at. The power pool becomes the requests active on 2024-12-31, re-drawn as the five largest
   per technology among them, with P(operate) conditional on having survived to that date (landmark model,
   agreement status as of 2024). Alternative: a backtest at 2019 with lease data as of 2019 — that is what the
   rebuilt gym already does, so it would duplicate it.
2. **The lease decline floor (E2).** Recommended: modified hyperbolic, terminal decline 8%/yr base, range
   5–12% (ASSUMED), fitted on post-peak months; ramp-up leases fitted from their peak.
3. **What the budget charges a power request (E3).** Recommended: a two-stage budget — the committed cost
   now (deposits and study costs to the next gate) plus a construction reserve released at the agreement,
   with construction capital charged when the request is decided at the gate. This is also the staged decision
   that Phase D6 needs. Alternative: keep full capital at certainty and disclose the bias.
4. **Scope and the word limit.** The requested report has eleven sections; the test is at 3,500 words. Recommended:
   keep 3,500 for the eleven sections with all detail in appendices. The dashboard is rebuilt as the decision page
   (Phase D9) on the lines of the earlier critique — alternatives first, the human thinks before the advisor
   speaks — not the old five-page app.

## Phase A — Freeze (0.5 day)

- A.1 Copy the v7 scored files, `posthoc_*committee*`, `decision_gym_*`, `advisor_evaluation.csv` to
  `results/registered_v7/` with a README and SHA-256 manifest; `tests/test_registered_frozen.py` checks hashes.
- **Check:** the test passes; `git diff` shows no change under `results/` other than the new folder.

## Phase B — Implementation corrections (2 days)

| Step | Fix | Test |
|---|---|---|
| B1 | Cap in `top_n_by_npv` and `equal_capital_by_sector` (A1) | every comparator book within budget and cap on random instances |
| B2 | One `cvar()` with the rounding fix, used by optimizer, portfolio and scenarios (A13) | CVaR of a known sample; equals the R–U objective at the optimum |
| B3 | Gas boe conversion (E10) | unit test on 1,037 Mcf |
| B4 | Gate floor from training outcomes only (G2) | the floor is a function of entrants ≤ 2016 |
| B5 | Level-repaired probabilities into `operation_curve` (E4) | the 20 candidates' P5 equals the repaired curve |
| B6 | ATB capital to 2024 dollars; provenance per field (E7, E9) | every dollar column has a tag; no ATB value tagged OBSERVED |
| B7 | Report text that is simply wrong: A2, A4 carbon line, A5, A6, A14, E6, G8, G9, A10's 0.63 | `tests/test_report.py` |

- **Check:** 182 + new tests green; notebooks 07–10 rerun; C21–C24 rescored with B1–B2 written to
  `results/v8/criteria_corrected.csv` beside the frozen record.

## Phase C — Valuation and framing corrections (3–4 days; needs decisions 1–3)

- C1 Decision date 2025-01 (decision 1): new power pool, conditional probabilities, valuation date aligned.
- C2 Decline floor (decision 2) in `src/decline.py`; lease NPVs, break-evens and the tornado rerun.
- C3 Staged budget (decision 3) in the MILP: stage-1 commitments under the budget; stage-2 construction as a
  recourse decision in D6.
- C4 Tax credits by drawn operation year (E5); credits-off as a sensitivity.
- C5 Held-out set redrawn in every component (A7); stated against the registration.
- C6 Gym rebuilt (G1, G3): lease rooms as of their date, counted as one situation, observed BSEE output as the
  outcome, an NPV-per-dollar instinct and a fund-nothing actor; queue rooms with models refit on labels censored
  at the room date (if refits are too slow, relabelled "pseudo-prospective" and the label carried into the report).
- C7 Ablation widened (G4): committee grid, lookup curves in place of the queue model, the registered challenger's
  residuals, naive output; the abstract's sentence follows the result.
- **Check:** every number in the audit's "contradicts itself" list is either gone or recomputed; leakage tests
  for the gym (no data after the room date enters any room).

## Phase D — The decision intelligence layers (8–10 days)

Six layers, each a small module with a docstring and tests; notebooks 11–12 tell the story.

| Layer | Module | What it does |
|---|---|---|
| 1 Evidence | `src/provenance.py` | OBSERVED / DERIVED / FORECAST / ASSUMED per field; every output table carries it |
| 2 Prediction | existing | queue curves, output forecasts, level repair; the simpler model wherever ML did not win |
| 3 Valuation | **`src/valuation.py`** (D1) | `lease_npvs`, `power_npvs`, `pv_components` moved out of nb 08: scenario → NPV matrix, so any price or cost change is recomputed |
| 4 Prescription | `src/optimizer.py` + **`src/whatif.py`** (D2–D3) | budget, caps, λ, a CVaR or loss-probability *limit* (ε-constraint), forced in/out; `book_diff()`; frontier; per-project explanation by forced-in/forced-out re-solves (opportunity cost); invest / defer / monitor / reject / reconsider from stated rules |
| 5 Advisor | `src/advisor.py` (D4) | two-call protocol that works with both backends: (i) the model turns a question into a `WhatIf` JSON, the code validates it against ranges and refuses what it cannot represent; (ii) the code runs valuation → optimizer → diff; (iii) the model explains the returned table. Grounding by attribution: each number must match a field of the returned table, units checked; books it names are re-scored and refused if infeasible |
| 6 Governance | `src/ledger.py` (D5) | decision verb, authorizer, timestamp, run id, scenario hash, inputs, overrides; writing an override without the gate raises; append-only |

- **D6 Dynamic reoptimization (experimental, labelled a scenario-based extension).** Information dates 2025,
  2027, 2029. At each date, along each of 200 scenario paths: update prices to that date, update P(operate)
  with the landmark model, revalue what remains, keep sunk capital, re-solve only the open decisions (defer a
  lease, release or drop a request at its agreement), with an assumed switching cost. Compared against holding
  the 2025 book. Reported: value of flexibility with its interval, turnover, capital redeployed. No claim about
  real future costs.
- **D7 Value of information.** EVPI by uncertainty block (prices, completion, lease cost) = E[max] − max E over
  the scenario set; EVSI for (a) learning a request's agreement status (preposterior from the landmark model),
  (b) a revised lease cost estimate (revealing the cost multiplier), (c) one more year of prices. Reported as the
  most a committee should pay for that information, not an ROI.
- **D8 Decision-process evaluation (the main new experiment, post-registration).** Processes on identical
  inputs, budget, constraints and scenarios: A NPV ranking, B equal capital by sector (both capped), C
  deterministic, D risk-aware, E AI-assisted (D plus the advisor's proposed what-ifs, the human gate, logged),
  F = E with naive forecasts. Metrics: E[NPV], scenario-evaluated NPV on a fully independent draw, CVaR95,
  P(loss), regret against the hindsight book per scenario, capital utilization, turnover (from D6), constraint
  violations, stability across stresses, value added against each baseline with paired intervals, the ML
  increment (F vs E) and the advisor increment (E vs D). Where E equals D the advisor's investment increment is
  reported as zero, and it is scored instead on: attribution-checked grounding, detection of seeded errors in
  the tables it reads, and coverage of the what-if space. No money is attached to those.
- **D9 Decision page** (`app/decide.py`): book overview, side-by-side books, interactive frontier, scenario lab on
  the `WhatIf` schema, the advisor answering about the *current* state or saying it cannot, per-project
  explanations, the ledger. Reads only computed outputs; a headless test checks each panel against the engine.
- **Check per module:** the test list of the brief — budget and cap, cash-flow consistency, scenario
  reproducibility, no leakage, CVaR, feasibility, reoptimization behaviour, grounding, logging, authorization.
  Interactive re-solve under 5 s with 2,000 scenarios (measured, not assumed).

## Phase E — Figures (3 days)

The ten figures of the brief, each with a question, units, source, provenance and a Reading-this cell:
architecture (F0 redrawn as six layers), composition by sector and technology, NPV–CVaR frontier with the books,
capital by risk policy, reallocation after shocks (D6), project attractiveness with intervals, price sensitivity
of the decision, value added against baselines (D8), advisor workflow with tools and the gate (F36 redrawn),
gym regret with intervals (rebuilt).

## Phase F — Report, memo, statements (4 days)

The eleven-section structure of the brief, core within the word limit decided in decision 4, appendices for
Parts I–II, the registered record, the audit and the corrections. The memo presents the frontier and lets the
committee choose its risk policy. Reproducibility and limitations statement; a status table that marks each
deliverable implemented / tested / partial / proposed.

## Compute

One MILP: 40 binaries, ~2,040 variables, seconds (measured in D2). D6: ~200 paths × 3 dates × a re-solve on a
conditional scenario subset ≈ 600 small MILPs, minutes. D7: EVPI is one pass; EVSI ≈ 20 requests × 2 signals
re-solves. The gym refits per room (C6) are the slowest item: 13 LightGBM refits, about 3–6 minutes each.

## Calendar (deadline 14 December)

| Weeks of | Phase |
|---|---|
| 19 Oct | A, B; decisions 1–4 |
| 26 Oct | C (2 Nov: the evaluation plan to the channel, updated with D8) |
| 2–16 Nov | D1–D5, D8 |
| 16–23 Nov | D6, D7, D9 |
| 23–30 Nov | E |
| 30 Nov–10 Dec | F, poster, video, tag |
