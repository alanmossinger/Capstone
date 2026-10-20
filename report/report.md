---
title: "Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization"
subtitle: "An AI-Assisted Decision Intelligence Framework for Risk-Aware Capital Allocation Across Oil, Gas, Power, Renewables, and Storage"
author: "Alan Mössinger"
date: "SIADS 699 Capstone, University of Michigan — Group 13 (a solo project) — October 2026"
---

## Abstract

Can an AI-assisted prescriptive system improve how an energy company allocates capital, and can its contribution be measured apart from the forecasts and the optimizer beneath it? I build such a system for one decision — twenty Gulf of Mexico lease redevelopments and twenty ERCOT interconnection requests under one budget on 1 January 2025 — and evaluate it against conventional rules on the same held-out scenarios. An independent audit corrected errors that had decided the previous version's recommendation, and a later review removed three inputs that were not public on the decision date. Under equal constraints a risk-aware optimizer beats NPV ranking on the registered risk–return metric by $320M [+$142M, +$511M], buying a thinner tail with $274M of expected value; the ranking holds when the book is re-chosen on resampled scenarios, but its capital plan holds only with a contingent construction line. Machine-learning queue forecasts rank requests better than a transparent lookup in two backtests, yet the book chosen with them does not beat the book chosen with the lookup. Revising the book in 2027 adds nothing in this model. The AI advisor read six committee questions correctly — five into model parameters, the sixth refused as outside the model — and cited computed numbers only; its investment increment is zero, because the book is the optimizer's. The contribution is a decision system that shows a committee its trade-off and states where prediction, optimization and a language model add value, and where they do not.

## Capital Allocation Memo

*To the investment committee, 1 January 2025. Every figure is a model output scored on held-out scenarios; lease costs are assumed.*

**The ask.** Commit up to $3.42B now — 40% of what the forty candidates would cost the budget today — across twenty Gulf lease redevelopments and twenty ERCOT requests still in the queue, with no technology above 40% of the budget. A lease costs its redevelopment capital; a request costs its deposits plus a reserve for the construction it may need.

**The choice.** There is no single right book, only a trade-off to price (Figure 2). The return-seeking book expects $2.36B with a worst-5% average loss of $1.60B. The registered risk-aware book expects $2.05B with a loss of $1.02B and a 10% chance of losing money. A defensive book expects $1.55B with a loss of $0.52B. I recommend the committee choose its tail weight first; at the registered weight that is the risk-aware book.

**What to do with each candidate under that book.** Invest now in six leases and two requests with signed agreements. Invest in stages in five requests: pay the deposit now, commit construction at the agreement. Wait for information on thirteen requests whose agreement signal is worth more than their deposit. Monitor thirteen; reject one.

**What the commitment really is.** The construction reserve is an average: the capital the book's requests call exceeds it in 44.5% of scenarios. Without a contingent line the book is worth $1.40B, not $2.05B, because requests that reach their agreement cannot be built; a line of $3.28B restores $2.02B.

**What would change it.** Oil at $45 a barrel for five years, or redevelopment capital 30% higher, removes every lease from the book. The two largest power positions rest on ERCOT prices spiking as they did in 2021 and on prices reverting upward from 2024's low level.

**What information is worth.** Knowing everything before committing would be worth at most $571M; knowing the 2025–2029 ERCOT price level, $52M; one request's agreement signal, at most $11.5M.

## 1 Introduction: why better predictions do not guarantee better investment decisions

An energy company with one budget holds requests to connect new plants to the grid, most of which are never built, and oil and gas leases that already produce. Data science usually stops at the forecast. A forecast is not a decision: the decision also depends on costs, constraints, timing and how much loss the owner can bear, and on whether the machinery that joins them does what it says.

The previous version of this report shows the second point. An independent audit (Appendix H) found five errors that no test of forecast accuracy would have caught. The comparison books faced different constraints, so the "price of cutting the tail" was really the price of a cap one book ignored. Ten of the twenty power candidates had already been withdrawn or built. Half the leases were projected never to decline. The backtest of past decisions used information from after their dates. And the AI advisor added nothing over the rule it was meant to improve. Each was corrected; a later review found three inputs that were not public on 1 January 2025 — a tax-credit deadline set by a July 2025 law, agreement dates from a 2026 data release, and lease months not yet published — and those were removed too. The registered record is kept as it was scored (Appendix A).

| Stage | Question | In this report |
|------------------|----------------------------|----------------------------------------------------------------|
| Descriptive | What happened? | Queue outcomes 2000–2024, lease production, prices |
| Predictive | What is likely? | Each request's chance of operating from today; lease and plant output |
| Uncertainty | What could go wrong? | 2,000 joint scenarios of prices, output, costs and timing |
| Prescriptive | What should we do, and is it better? | The book under a budget, caps and a risk policy; its value against conventional choices |

*Table 1.* The four analytical stages. The last is the contribution.

## 2 Research questions, hypotheses and contributions

The overarching question is whether an AI-assisted prescriptive system can improve energy capital allocation by joining machine-learning predictions, uncertainty, valuation, portfolio optimization and explainable human decision support — and demonstrate when it beats conventional alternatives.

- **RQ1 Predict.** How well does machine learning estimate completion, timing and output against transparent baselines?
- **RQ2 Quantify.** How do price, output, cost and timing risk change value and downside?
- **RQ3 Prescribe.** Which investments should be selected under capital, diversification and downside constraints, and how does the choice move with risk preference and market conditions?
- **RQ4 Evaluate.** Under equal constraints and scenarios, which decision process does better, and how much of any gain comes from the forecasts, the optimizer and the AI advisor separately?

Three hypotheses were registered before any result: **H1** machine-learning forecasts reduce held-out error against naive and physics baselines; **H2** a risk-aware book beats NPV ranking and sector-concentrated books on a stated risk–return metric; **H3** uncertainty-aware selection is more stable under stresses than deterministic selection. Everything RQ4 adds — the ML increment in the decision, the value of revising the book, the advisor's increment — is a post-registration extension and is labelled so.

The contributions are three: a corrected prescriptive pipeline with the audit that produced it; a six-layer decision system in which a language model translates and explains but never computes (Figure 1); and an evaluation that separates forecasting, optimization and decision-support value on the same scenarios.

![Figure 1](../figures/F43_architecture.png)

*Figure 1.* The decision system in six layers, and the evaluation that scores it.

## 3 Energy portfolio, datasets and economic assumptions

Every source is public: LBNL's *Queued Up* interconnection files (2025 edition, 2026 edition for later outcomes), BSEE monthly lease production, EIA prices and plant generation, ERCOT's hourly settlement prices for 2018–2024 and the NREL Annual Technology Baseline. A readiness gate checked each source before any model was fitted.

**One decision date.** Both sectors are decided on 1 January 2025, with only what was public that day: lease output to September 2024, agreements as the 2025 edition dates them, and the tax credits of the law then in force. The leases are the twenty with the most output in the twelve months published by that date. The requests are the five largest of each technology — gas combined cycle, solar, wind, storage — among the 1,649 ERCOT requests of 20 MW and more still waiting on that date, about 359 GW. Each request's chance of operating within seven years is conditional on how long it has already waited and on whether it has signed its interconnection agreement.

**Valuation.** A lease redevelopment adds 20% to output after two years; its value is the cash flow it adds over a baseline fitted after the lease's peak that declines at least 8% a year (ASSUMED; 5–12% as the range). Redevelopment costs are not public, so every result is shown under two grids: the registered grid fixed before any result, and the harder committee grid an investment committee would use, which prices capital per incremental barrel and discounts at 8%. Under the registered grid the twenty leases are worth $8.19B; under the committee grid $2.73B, for $5.12B of capital. A power request is valued on the 2024 hourly prices, with ATB costs in 2024 dollars and the tax credits each plant would earn under the law in force on the decision date; the 2027 deadline a July 2025 law set for wind and solar is a stress, not the base case.

**The budget.** A lease spends its capital now. A request needs only its deposits now, plus a reserve for the construction it will call if it reaches its agreement; that is what it charges the budget. The budget is the registered rule in those units, 40% of the forty charges. Every dollar figure carries a provenance label: OBSERVED, DERIVED, FORECAST or ASSUMED.

## 4 Predictive modeling and uncertainty quantification

**Queue completion.** Discrete-time LightGBM hazards on entry attributes, fitted on entrants to 2016 and tested once on 2017–2019 entrants, rank requests above cohort averages (AUC 0.86 against 0.73), but for requests of 20 MW and more a careful lookup — the share built among earlier requests of the same region, technology and size — ranks as well. Two years in, with the agreement known, the model wins (Appendix E). For the 2025 decision the models were refitted on what was known on each of two earlier dates and scored on what followed: as of 2020 the model ranked better than the lookup (AUC 0.731 against 0.686) but put ERCOT's five-year chance at 0.380 where 0.238 operated. That ratio, knowable on the decision date, corrects the 2025 curves.

**Energy forecasts.** Of twelve registered lines, machine learning beat the best of five transparent baselines for plant capacity factors and failed for lease output and prices (Appendix F).

**Scenarios.** 2,000 joint twenty-year paths resample calendar-year blocks of the 2018–2024 monthly changes of oil, gas and ERCOT prices together, revert toward their 2018–2024 means with a four-year half-life (ASSUMED), and carry output, cost and timing draws. A second set of 2,000 paths, redrawn in every component with its own seeds, is used only to score books. Seven historical years are thin material for a twenty-year tail; Section 10 states what that leaves out.

## 5 Prescriptive portfolio optimization

The risk-aware book maximises expected NPV minus λ times the worst-5% average loss (CVaR95), over binary choices of the forty candidates, under the budget and a 40% cap per technology, with the tail linearised after Rockafellar and Uryasev (2000) and solved exactly with HiGHS. λ = 1 is the registered setting; λ = 0 gives the deterministic book; a hard limit on CVaR replaces the penalty when a committee states its downside as a rule. The conventional books are **A**, ranking by expected NPV, and **B**, equal capital by sector, now held to the same budget and cap as the optimizers — in the previous version they were not, which made the risk-aware book look $1.9B worse than it was.

Three tools turn the optimizer into something a committee can question. The **frontier** solves the book at nine values of λ and four CVaR limits. A **what-if** reprices every candidate under validated parameters — an oil price for a number of years, ERCOT volatility, the budget, redevelopment capital, a downside limit — and re-solves. An **explanation** re-solves the book with each candidate forced the other way; the objective lost is that candidate's opportunity cost, a model-supported reason, not a causal one.

## 6 AI-assisted investment decision framework

The language model sits in one layer and never produces a number the decision uses (Figure 1; Appendix B). A committee question in words goes to the model, which answers with parameters from a fixed schema or says the question cannot be represented. The engine validates the parameters, refusing any outside the ranges it was built for, and computes the new book, its difference from the base book and every candidate's status. The model then explains the computed fact sheet, and a checker holds every number of the explanation to that sheet in its unit. A named person decides: a book that departs from the model's for the committee's chosen tail weight is an override, accepted only with answers to five questions about the reasoning and the opposing case read. Every decision is appended to a hash-chained ledger with the scenarios it saw. The decision page shows the alternatives first and asks for the committee's own book and reasons before the models answer.

## 7 Experiments, benchmarks and validation

**The registered record.** Of 70 registered lines, 28 passed, scored once and never re-scored; the version scored before the audit is frozen with a hash test (Appendix A). Applied to the corrected system, the same allocation criteria give different verdicts; those are post-registration results.

**Post-registration experiments.** Seven decision processes see the same candidates, budget, cap and scenarios; each book is chosen on the primary scenarios and scored on the held-out ones: **A** and **B** as above; **C** deterministic; **D** risk-aware; **D + revision**, which revises book D on 1 January 2027; **E**, AI-assisted, the process of the decision page; and **F**, book D chosen with the lookup's queue curves in place of the model's. Regret is measured against the best book with perfect information, scenario by scenario. Differences carry paired bootstrap intervals.

**How I could fool myself.** *Unequal constraints:* every book is now checked against the same budget and cap. *Hindsight:* the queue view, the lease rooms of the decision gym and the 2027 revision use only what was known on their dates. *A weak baseline:* the lookup sits beside every queue forecast. *Crediting the language model with the optimizer's work:* its investment increment is measured, and it is zero. *Assumptions doing the work:* both cost grids are shown, and Section 8 names the assumptions the book rests on.

## 8 Economic results and portfolio trade-offs

**The trade-off is real and the committee must price it.** Along the frontier, expected value and tail fall together (Figure 2). Under the committee grid the deterministic book expects $2.36B with a worst-5% loss of $1.60B; the risk-aware book $2.05B and $1.02B; at λ = 2, $1.55B and $0.52B.

![Figure 2](../figures/F38_frontier.png)

*Figure 2.* The frontier over risk policies on held-out scenarios, the four registered books on it, and capital by technology along it.

**Under equal constraints, the risk-aware book wins on the registered metric.** It beats NPV ranking by $320M [+$142M, +$511M] and equal capital by $213M [+$120M, +$315M] on expected NPV minus CVaR95, while giving up $274M of expected value against NPV ranking (Figure 3). Re-chosen on 20 resampled scenario sets it beats NPV ranking every time, by $116M to $352M; 11 of its members are chosen in at least 80% of them. Under the registered grid, applying the same criteria to the corrected system, the risk-aware book beats NPV ranking by $1,332M, ties equal capital (+$24M, an interval that includes zero), and fails the stability and single-sector tests.

![Figure 3](../figures/F42_value_added.png)

*Figure 3.* Each process against its comparator on the same held-out scenarios: expected NPV and the registered metric, with paired bootstrap intervals.

| Committee grid, held-out | A NPV ranking | B equal capital | C deterministic | D risk-aware | F lookup forecasts |
|-------------------------|--------------|----------------|----------------|-------------|------------------|
| Candidates funded | 16 | 16 | 17 | 13 | 18 |
| Expected NPV, $B | 2.33 | 2.08 | 2.36 | 2.05 | 1.84 |
| Worst-5% loss, $B | 1.61 | 1.26 | 1.60 | 1.02 | 0.83 |
| Chance of a loss | 13% | 12% | 13% | 10% | 9% |
| Regret against perfect information, $B | 0.60 | 0.84 | 0.57 | 0.87 | 1.08 |

*Table 2.* The decision processes on the same 2,000 held-out scenarios.

**Machine learning does not demonstrably improve this decision.** The book chosen with the lookup's queue curves (F) spends 91% of the budget; book D expects $209M more and on the registered metric scores +$22M [−$168M, +$207M] in the model's own scenarios and −$143M [−$375M, +$87M] in the lookup's — neither interval excludes zero. The model ranks requests better, but the decision turns on a few large requests whose chance of operating neither method knows well, and the two books differ in size. By the rule this project set itself, the simpler forecast should be used for this decision.

**What drives value and downside.** Book D holds six leases — not the three largest producers, whose capital per budget dollar is high under the committee grid while the 40% cap binds — and seven requests. The position whose removal costs the most is an 836 MW wind request with a signed agreement: forcing it out lowers the objective by $549M. The largest power position, a 1,350 MW gas request four years into the queue, expects $512M yet loses money in 77% of scenarios; it earns its place through rare large outcomes, and its place is worth only $7.7M at the registered tail weight — a committee slightly more averse to the tail would drop it.

**How the book moves.** Re-solved under five committee questions (Figure 4), the book drops every lease when oil stays at $45 for five years or redevelopment capital rises 30%, keeping only wind. Halving ERCOT's volatility drops the gas request and brings in four solar requests. A budget cut of a fifth drops one lease and the gas request and brings in a solar request. Capping the worst-5% loss at half of book D's drops one lease and the gas request and brings in four solar requests.

![Figure 4](../figures/F39_reallocation.png)

*Figure 4.* Book D's capital by technology, re-solved under each committee question.

## 9 Dynamic decisions and scenario analysis

**Revising the book in 2027 adds nothing here.** Committing in 2025 and revising on 1 January 2027 — after two years of prices and the agreement signal, with the continuation values fitted on the primary scenarios — is worth −$9M [−$16M, −$3M] on the held-out scenarios (Figure 5). The cap leaves no room to start a deferred lease with released capital, so the revision can only drop requests, and its estimates drop some that would have paid. A negative value says this rule's estimates are noisy, not that flexibility has negative value; it establishes no real-option value. The construction reserve is an average: the capital the book's requests actually call exceeds it in 44.5% of scenarios, and without a contingent line the book is worth $1.40B.

![Figure 5](../figures/F41_staged.png)

*Figure 5.* Book D held, or revised on 1 January 2027, on the held-out scenarios.

**What information is worth.** Perfect knowledge of everything before committing would raise the best book's expected value by $571M — the most any information could be worth, on a risk-neutral objective. Knowing the 2025–2029 ERCOT price level is worth $52M, the oil price level $32M, the lease cost draw $30M. Learning within two years whether one request signs its agreement is worth between $0.5M and $11.5M depending on the request; for thirteen requests outside the book that exceeds the deposit needed to wait, so their status is "defer pending information".

**The AI advisor helped the committee ask, not choose.** All six questions were translated correctly — five into parameters, the sixth, about interest rates, refused as outside the model. Its five explanations cited 119 numbers, all in the computed fact sheet in their units. Its investment increment is zero: the book is the optimizer's.

## 10 Limitations, governance and practical implications

**What the results are, and are not.** They are model-based comparisons on public data and assumed costs, not demonstrated improvements in a company's capital allocation. Redevelopment costs are an assumption bracketed by two grids; at the committee grid's high case no lease is positive. The scenarios resample seven years of history, so a worse tail than 2018–2024 cannot appear, and the mean reversion lifts gas and ERCOT prices well above 2024's, which is what makes the gas requests valuable. The 2025 queue curves rest on two backtests that disagree about the level. The advisor's contribution was measured on six questions, not on committees making decisions; a study with people is proposed, not run. The decision page is a prototype, not production software. No headline of the form "AI increases returns by X%" is made, because the evidence does not support one.

**Who could be harmed.** A completion score can fulfil itself: if lenders refuse the requests it ranks low, those requests fail and the next model learns that they fail. Size is a top driver, so a gatekeeper screening applicants by the score would penalise small developers for a pattern partly made by the rules. The score should inform a portfolio, not screen access to the grid.

**Governance.** A named person decides; the ledger records what each decision saw and refuses an override without its reasons.

## 11 Conclusions and future research

Better predictions did not, by themselves, produce better decisions here. The machine-learning queue model ranks requests better than a lookup, yet the book built on it scores no better. The optimizer earns its place only when held to the same constraints as the rules it is compared with; then the risk-aware book wins on the registered metric by trading expected value for a thinner tail, a trade the committee must price itself. The AI advisor makes that trade-off easier to question — it reads questions into parameters, refuses what it cannot represent and explains only what was computed — but adds no investment value of its own, because the book is the optimizer's. A decision system is useful when it states which of these is doing the work. Future work: committees deciding with and without the page, tails beyond the historical years, real redevelopment costs, and a recourse model with room to redeploy capital.

## Statement of work

This is a solo project registered in a group slot (Group 13). All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried out by Alan Mössinger. The ERCOT price client and the battery dispatch model are reused, with credit, from my own earlier projects (Forecast to Dispatch; MADS Milestone II).

## Changes after review

Two outside reviews in October 2026 led to the changes logged in `docs/mentor_feedback.md`. The second asked for a decision intelligence system, evaluated. Its first request was an independent audit; the audit's corrections and the new decision layers are this version. A review on 19 October found three inputs that were not public on the decision date and the book's capital calls unpriced; both are corrected here (decisions #93–#94). A course mentor is assigned after the proposal review; their feedback will be logged in the same file.

## Appendix A — The evaluation record

Every claim in the body that says "registered" refers to a line below. Each criterion was written and committed before the data it scores were looked at; failures are reported as registered and never re-scored. The scoring of C20–C24 as it stood before the audit of 17 October 2026 is frozen in `results/registered_v7/` with a hash test.

| Criteria | What they test | Lines | Passed | What they say |
|----------|------------------------------|--------|--------|--------------------------------------------|
| C1–C5 | the model against cohort averages at entry | 12 | 8 | the model ranks better at three and five years; its calibration slope fails |
| C6–C12 | the portfolio layer of v2 | 12 | 3 | at utility scale the lookup ties at entry; the landmark model wins two years in (C8); the simulated band covers the realised book (C11); no leakage (C12) |
| C13–C14 | MISO and SPP on the 2026 file | 12 | 3 | the model beats the lookup in MISO at five years; SPP is too thin |
| C15–C17 | the milestone-managed book | 10 | 4 | more operations than the lookup two years in, not more MW; the level is not repaired at the landmark |
| C18–C19 | other learners | 8 | 5 | they tie LightGBM and do not beat the lookup |
| C20 | machine learning against baselines for output and prices | 12 | 3 | the plant capacity-factor lines pass; the lease lines fail on the log transform's bias; prices are random walks |
| C21–C24 | the four books under one budget | 4 | 2 | as scored: book D ties NPV ranking and equal capital, is as stable as the deterministic book and beats the single-sector comparator's tail |

*Table A1.* The registered record. Twenty-eight of seventy lines pass. Sources: the `success_criteria*_scored.csv` files and `tournament_criteria.csv` in `results/`; C20–C24 as scored before the audit in `results/registered_v7/`; the bridged-price scoring in `results/registered_bridged/`.

**C21–C24 as scored.** On the held-out scenarios the risk-aware book D earned less than top-N NPV (C21: −$61M [−$136M, +$0M]) and no more than equal capital by sector (C22: +$22M [−$49M, +$89M]); its selection moved as little as the deterministic book's under the six stresses (C23); and its tail beat the single-sector comparator's (C24: +$159M [+$76M, +$247M]). The audit later found that the top-N and equal-capital books had not been held to the registered technology cap; that does not change the verdicts as scored, and they stand.

**Scored first on the bridged prices.** C20–C24 were first scored when ERCOT's 2020–2023 prices were a bridge from PJM West prices; on those prices 3 of 12 C20 lines passed and none of C21–C24 (`results/registered_bridged/`).

**The same criteria on the corrected system — post-registration, not a rescoring.** Applied to the system of this version — the 2025 candidates as they could be seen that day, the decline floor, the two-stage budget, every book under the same cap — the allocation criteria read as in Table A2. These are new results on a changed system, labelled as such; the registered verdicts are those of Table A1.

| Criterion, registered grid | As scored (v7) | On the corrected system (v8) |
|------------------------------------------|-----------------|------------------------------|
| C21: D minus NPV ranking, registered metric | −$61M, FAIL | +$1,332M [+$1,131M, +$1,528M], PASS |
| C22: D minus equal capital | +$22M, FAIL | +$24M [−$73M, +$122M], FAIL |
| C23: stability under the stresses | PASS | FAIL |
| C24: tail against the single-sector book | +$159M, PASS | +$51M [−$90M, +$194M], FAIL |

*Table A2.* The allocation criteria as registered and scored, and applied to the corrected system.

**The hypotheses.** *H1:* machine-learning forecasts reduce held-out error against naive and physics baselines (C20). *H2:* a risk-aware book beats NPV ranking and sector-concentrated books on a stated risk–return metric (C21, C22). *H3:* uncertainty-aware selection is more stable under stresses than deterministic selection (C23, C24). As registered: H1 holds for plant output and not for leases; H2 is not supported; H3 is supported on the observed prices. On the corrected system H2 holds against NPV ranking but not against equal capital, and H3 does not.

## Appendix B — The AI advisor

**What it sees and what it may do.** In v8 the advisor works through the engine (`src/advisor_tools.py`). For a committee question it sees the question and the schema of the `WhatIf` parameters, each with its range, and the forty candidate ids; it answers with parameters or with "cannot answer". The engine validates the parameters and computes. For the explanation it sees only the computed fact sheet. It sees no web, no memory across calls and no company data.

**How its numbers are checked.** `advisor_tools.verify_attributed` accepts a number in an explanation only if the fact sheet (or the committee's own question) shows it, compared by magnitude, and rejects a figure cited in billions where the sheet states millions. Integers up to ten and years are exempt. The v6 check, `advisor.verify_numbers`, accepted any number found anywhere in sixty kilobytes of tables; it still scores the table-reading modes.

**Record and replay.** Every call is appended to `results/advisor_runs.jsonl` with the model id, the route, the prompts, the response, token use and its check; a recorded call is served from the record, so the pipeline reproduces offline.

**The override gate and the ledger.** A decision is written by `src/ledger.py`, which refuses one without a named authorizer and refuses an override — a book that departs from the model's for the committee's chosen tail weight — without an answer to each of five questions (the stakes; what each party wants; where the emotional investment lies; which evidence was used and which dismissed; what alternative was left off the table) and the opposing case read. Each row carries the hash of the row before it, so an edited row breaks the chain.

**The prompts.** Eight templates sit in `prompts/`: the system prompt, the recommendation, the gym pick, the three of the challenge round (the five questions, the motivated-reasoning check and the ideological Turing test, unchanged since decision #73), and the two of v8, which translate a question into parameters and explain a computed result.

**Scored.** On the six committee questions of notebook 11 it read all six correctly — five into parameters, the sixth refused — and its five explanations cited 119 numbers, all in the computed fact sheet. Across all modes, 171 calls are recorded; their numbers were in the tables shown 94% of the time. In the decision gym the advisor trailed the registered rule by $5.1M a situation [−$11.0M, −$1.5M], worse in 12 of 14.

![Figure B1](../figures/F44_advisor_tools.png)

*Figure B1.* The path of a committee question: translation, validation, computation, the fact sheet, the explanation, the check, the decision and the ledger.

## Appendix C — Where things are

| Need | Where |
|------------------------------|----------------------------------------------------------------------|
| Run everything | `make all` (eleven notebooks in order), `make test`, `make report`; `make decide-page` for the decision page |
| Data access and dictionary | `data/README.md`; raw files hashed in `data/raw/manifest_v5.json` |
| Every cited number | `results/report_numbers.csv`, written by `src/report_numbers.py` and checked by `tests/test_report.py` |
| Every decision and its reason | `docs/decisions.md` (numbered); the registered criteria in `results/success_criteria*.csv`; the frozen record in `results/registered_v7/` |
| The audit and the plan | `docs/audit_2026-10-17.md`, `docs/implementation_plan_v8.md`, `docs/v8_status.md` |
| The decision layers | `src/decision_date.py`, `src/valuation.py`, `src/whatif.py`, `src/advisor_tools.py`, `src/ledger.py`, `src/voi.py`, `src/dynamic.py`; notebook 11 |
| Figure captions and their notebooks | `report/figure_notes.md` |
| Changes after review and mentor feedback | `docs/mentor_feedback.md` |

**Reproducibility.** Every notebook runs top to bottom with `make all`; the scenario sets, bootstraps and draws are seeded; the solver must reach optimality or the run stops; advisor calls replay from their record. The parser of one PJM table needs poppler's `pdftotext`; a clean Linux environment reproduced the previous version's registered verdicts and nearly all its cited numbers (decision #87).

## Appendix D — Supporting figures
![Figure A1](../figures/F25_state_archetypes.png)

*Figure A1.* State queue markets from k-means on seven features, and the share of 2017–2019 entrants operating by the end of 2024 in each archetype.

![Figure A2](../figures/F6_hazard_ratios.png)

*Figure A2.* Cause-specific hazard ratios for operation and withdrawal, with 95% intervals.

![Figure A3](../figures/F20_when_requests_die.png)

*Figure A3.* Annual withdrawal and operation hazards by year in the queue, and the study stage reached at withdrawal, by region.

![Figure A4](../figures/F24_book_per_region.png)

*Figure A4.* Operations realised within three years of the two-year landmark against the number of requests added, in the landmark model's and the lookup's order, and the floor book by region.

![Figure A5](../figures/F30_price_scenarios.png)

*Figure A5.* The joint price scenarios against the real-dollar history.

![Figure A6](../figures/F32_stresses.png)

*Figure A6.* The default book under the registered named stresses, on the flat path.

![Figure A7](../figures/F22_tournament.png)

*Figure A7.* Other learners against LightGBM and the lookup: paired differences in Uno's C and Brier score by horizon.

![Figure A8](../figures/02_eda/02_C6_correlation_and_clusters.png)

*Figure A8.* Correlation of monthly log changes across the three prices, Gulf output and Texas capacity factors, and the two shapes of lease oil decline after the peak.

![Figure A9](../figures/02_eda/02_C5_asset_map.png)

*Figure A9.* Gulf of Mexico oil by protraction area in 2024, and Texas plants by fuel and size.

## Appendix E — Part I in full: the developer's decision, which queue requests to fund

*The method and evidence behind sections 4 and 5 for the queue side, kept in full. Words used one way throughout:*

| Term | Meaning |
|----------------------------|------------------------------------------------------------------------|
| Request | An application to connect a new plant to the grid; it ends as an operating plant or a withdrawal. |
| Entry, two years in, the agreement | The three moments a request is reviewed: the request date, two years later, and the date an interconnection agreement is executed. |
| The model | A gradient-boosted hazard model (LightGBM) that sees only what is known on the request date. |
| The landmark model | The same model refitted two years in, with the agreement flag. |
| The lookup | The share of earlier requests in the same region, technology and size band that were built — what a careful analyst would compute by hand. |
| The cohort average | The share built in the request's region and technology. |
| The level | The share of a cohort that is ever built; it has fallen for every cohort since 2017. |
| Merchant, contracted | Two revenue cases: selling at market prices, or under a 15-year power purchase agreement at index prices. |
| Book | A set of projects funded together under one budget. |
| The grid | The assumed costs of redeveloping an oil and gas lease (Part II); the *registered grid* was fixed before any result was seen, the *committee grid* is the harder one an investment committee would use. |
| OBSERVED, DERIVED, FORECAST, ASSUMED | The provenance of every dollar figure: a public record, arithmetic on records, a model's output, or a stated assumption. |

**Numbers.** Prose carries one number per claim, rounded; intervals, second cases and counts are in the tables. Every number in the report is written by code to the results tables and checked against the text by a test. Dollar figures in Part I are in 2022 dollars, in Part II in 2024 dollars.

### E.1 The decision and the data

A developer who wants to build a power plant in the United States must first ask the grid operator for a connection. The request enters a queue with a size, a technology and a place, and it leaves years later as an operating plant or a withdrawal. Most leave as withdrawals: of the capacity that asked to connect in 2000–2019, 12.6% was operating by the end of 2024 and 76.9% had withdrawn (Rand et al., 2025). Every request costs money to keep alive: a deposit, a study, then a larger deposit and a longer study. A developer holds many requests at once and must decide, request by request, which to fund, which to hold and which to drop.

The data are the project-level file of Lawrence Berkeley National Laboratory's *Queued Up* series, 2025 edition, with the 2026 edition alongside it for later outcomes. Only CAISO, ERCOT and PJM date both operation and withdrawal, so the timing models cover those three regions: 13,366 requests. The models are fitted on requests that entered up to 2016 and tested once on the 2,268 that entered in 2017–2019, every one followed for at least five years. Value and cost come from public files: EIA hub prices, the PJM market monitor's capacity revenues, the NREL Annual Technology Baseline 2024 and LBNL's PJM interconnection-cost estimates. Every value input that is an assumption carries its range in the repository.

![Figure E1](../figures/F9_project_map.png)

*Figure E1.* Requests waiting in U.S. queues at the end of 2024 by county (left; area proportional to MW) and the operating fleet (right).

### E.2 Where the opportunity is

**ERCOT is where requests get built.** Five years after the request, 18.4% of ERCOT's entrants are operating, against 13.2% in PJM and 4.8% in CAISO (Figure E2). Gas is built most often and storage least: no region builds more than 3.4% of its battery or hybrid requests within five years. Across the country, the states sort into four kinds of queue market, and the best is the light, settled queue of the PJM core and Florida, where about one entrant in five operates (Appendix Figure A1).

![Figure E2](../figures/F1_cif_by_region.png)

*Figure E2.* Share of requests operating (and withdrawn) by years since the request, by region, Aalen–Johansen estimates with 95% intervals.

**The queue itself is the constraint.** The capacity waiting at entry has grown many-fold in PJM since 2010, and since 2018 entrants neither leave nor get built at the old pace (Figure E3). This is the *level* problem of Appendix E.3: every cohort since 2017 completes below the one before.

![Figure E3](../figures/F16_constraint_map.png)

*Figure E3.* Requests, capacity waiting at entry, and three-year withdrawal and operation shares by region and entry year.

**The rule.** Look first in ERCOT, where the base rate is highest and the agreement is dated. Look at PJM for gas and its capacity market. Treat CAISO as a market where entry odds are a fraction of ERCOT's and only a signed agreement changes them.

### E.3 Which requests get built, and when

Three predictors are compared throughout, always in this order. **The model** is a gradient-boosted discrete-time hazard model (LightGBM) that sees what is known on the request date. **The lookup** is the share built among earlier requests in the same region × technology × size cell — the number a careful analyst would compute by hand. **The cohort average** is the share built in the request's region and technology. Appendix E.7 adds **the landmark model**, refitted two years after entry with the executed-agreement flag.

**At entry, the model beats cohort averages but not the lookup.** The model ranks the test cohort at an AUC of 0.86 at three years against 0.73 for cohort averages, and its top tenth of requests reached operation four times as often as the cohort. But for requests of 20 MW and more, the lookup ranks as well as the model: Uno's C is 0.78 for both at three years, and the model wins none of six comparisons (Table E1). Three other learners — a random survival forest, a neural hazard model and a blend — were registered and scored once; none beat the lookup either. At entry, the ceiling is what the file records about a request, not the learner.

| Test cohort 2017–2019 | Cohort average | Lookup (≥ 20 MW) | Model | Model (≥ 20 MW) |
|----------------------------|------------------|------------------|------------------|------------------|
| AUC, 3 years | 0.733 | — | 0.858 | — |
| AUC, 5 years | 0.725 | — | 0.766 | — |
| Uno's C, 3 years | — | 0.783 | — | 0.779 |
| Uno's C, 5 years | — | 0.752 | — | 0.734 |
| Top-decile lift, 5 years | 3.35 | — | 3.96 | — |

*Table E1.* Ranking at entry. The model against cohort averages (all sizes) and against the lookup (20 MW and more).

**Every cohort completes below the model's level.** For requests of 20 MW and more, 11.0% of 2017 entrants and 5.9% of 2018 entrants operated within five years, while the model predicted about 12% for both (Figure 2). The 2020–2022 entrants operate within two years at about a quarter of the predicted rate. Refitting the intercept on the newest completed cohort removes about 40% of the error and none of the post-2020 gap. In megawatts, the 2017–2019 cohort was expected to bring 29.2 GW online within five years and brought 18.8 GW. A book must be sized to the newest cohort's level, not to the model's.

**When: the model's clock helps in PJM only.** Among test requests that operated within seven years, the model's expected year of operation is within a year of the truth 52% of the time, against 33% for the regional median. The gain is all in PJM; in ERCOT the historical median does as well.

**Two years in, the model earns its keep.** For a request still waiting two years after entry, the executed agreement changes what can be known. The landmark model with the agreement flag ranks the next three years at Uno's C 0.80 against 0.69 for the entry model, a gain of 0.11, while the lookup conditioned on surviving two years falls to 0.59 (Figure E4). In ERCOT, requests with an agreement in hand two years in operated within three years 56% of the time, against 5% without.

![Figure E4](../figures/F12_landmark_models.png)

*Figure E4.* Gain in Uno's C and Brier score over the entry model at each landmark, three years ahead, for the landmark model with both inputs updated, with the agreement flag only, and for the lookup; 95% intervals. The text cites the agreement-flag variant.

**The rule.** At entry, rank by the lookup and the segment rules of Appendix E.4; the model adds nothing at utility scale. Two years in, re-score every request still held with the landmark model and the agreement. Plan the clock with the model in PJM and with the historical median in ERCOT. Size every book to the newest cohort's level.

### E.4 Why requests fail

**Size, technology and the agreement decide the odds (Figure E5).** On the 5,497 entrants of 2010–2019, five-year completion runs 12.8% overall. In PJM it falls from 24% for requests under 5 MW to 4% at 500 MW and up; ERCOT is flat up to 500 MW. Gas builds most often (32% in PJM), solar-plus-storage less than stand-alone solar, and none of PJM's 37 offshore wind requests operated within five years. The executed agreement dominates everything: where the file dates one within two years of the request, 63% of ERCOT's requests were operating within five years; where none is dated, 0.8%. A survival model with both exits confirms the ranking: requests of 500 MW and more reach operation at 0.31 times the rate of those of 20–100 MW, and gas at 2.56 times solar (Appendix Figure A2).

![Figure E5](../figures/F19_drivers.png)

*Figure E5.* Five-year completion by six drivers within each region, 2010–2019 entrants, 95% Wilson intervals.

**The regions run on different clocks.** CAISO and PJM cull early: 48% of CAISO's waiting requests leave in their first year, mostly out of the system impact study. ERCOT culls late, after year four, out of the facilities study. Surviving two years roughly triples the odds of operating in the next three (Appendix Figure A3).

**Ten rules a company can apply by hand (Figure E6).** A depth-four tree on the entry attributes, fitted on 2010–2016 entrants and re-measured on 2017–2019, gives ten rules whose order held out of time (Spearman 0.77). Small gas outside CAISO is the best segment: 47% then 48%. Large CAISO requests in crowded counties are the worst: below 2% in both periods. The one rule that broke — solar in a county with no earlier request — shows that crowding measured at entry is a weaker guide than size and technology.

![Figure E6](../figures/F21_segments.png)

*Figure E6.* Five-year completion by the ten rules, fitting cohort (2010–2016) and later cohort (2017–2019), with Wilson intervals.

**The rule.** Enter the top two segments; enter the middle ones only with the two-year review scheduled; do not enter the bottom three on entry information alone. Review in year two in CAISO and PJM, after the cull; review at the agreement in ERCOT.

### E.5 What a plant is worth

**At merchant prices only wind pays everywhere (Figure E7).** Each plant is valued as a developer would: a 20-year life, capital and operating cost from the NREL Annual Technology Baseline 2024, today's tax credits, and cash flows discounted at the technology's own real cost of capital (4.2–5.4%). Two revenue cases run side by side throughout the report. *Merchant* sells at the on-peak hub price. *Contracted* sells under a 15-year power purchase agreement at index prices (solar $57/MWh, wind $62), then merchant. At merchant prices five of 21 technology-region pairs have a positive value: wind in all three regions and gas and solar in PJM. Under contract ten pairs are positive, including solar everywhere. Storage stays negative in both cases, because the public files give it capacity revenue only.

![Figure E7](../figures/F26_npv_per_mw.png)

*Figure E7.* NPV per MW at operation by technology and region: merchant with today's credits, a 15-year contract at index prices, and merchant after the 2027 credit deadline.

**The break-even says the same in dollars a company negotiates.** A new solar plant needs a flat $44/MWh over twenty years and wind $41; the on-peak price the market pays them on Part I's national basis is below that for solar and above it for wind. Part II measures capture directly on ERCOT's 2024 hourly prices and finds the opposite order inside Texas (Appendix F.4), because Texas wind blows at night; Part I's assumed capture rates are national averages and are kept only for the three-region screen.

**The rule.** Develop wind anywhere; develop solar under a contract at or above the index, and in PJM even without one; develop gas in PJM, where the capacity market carries it; develop storage and hybrids only against a contract above their break-even; be operating by 2027 where the credit decides the sign. These values are in 2022 dollars; Part II works in 2024 dollars (the CPI-U ratio is 1.08).

### E.6 Fund, hold or exit: two gates

**The rule.** At entry (the first gate) and two years in (the second), the company compares three things: the chance the request operates, its value if it does, and the cost of the next gate. It **funds** when the chance is at least the pool's expected rate — the mean of the probabilities the gate reads, so no outcome enters the rule; the first version used the cohort's realized rate (audit G2) — and the value is at least *h* times the cost, where the hurdle *h* is 3 at entry and 2 two years in; it **exits** when the chance is well below the pool or the value is negative even in the best case; it **holds** otherwise. At entry the chance comes from the lookup, because the model did not beat it; two years in, from the landmark model.

**At entry, the funded requests were built three times as often as the cohort.** At merchant prices the rule funds 166 requests and exits 1,542. The funded requests reached operation 33% of the time, the exits 6%, the cohort 10% (Figure E8). In ERCOT the rule separates less — its funded requests operated 23% of the time and its exits 18% — because there the entry attributes do not separate the requests and the agreement does (Appendix E.4). Carried to the end, the funded class returned +$4.1B at merchant prices and +$9.1B under contract. The funded class is mostly ERCOT wind and PJM gas and solar.

**Two years in, the accelerated requests were built four times as often as the exits.** The rule accelerates 178 requests at merchant prices and 251 under contract. They reached operation within three years 29–30% of the time against 7% for the exits, and returned +$3.6B at merchant prices and +$9.0B under contract. Table E2 gives the counts, rates and intervals for both revenue cases.

![Figure E8](../figures/F23_portfolio_review.png)

*Figure E8.* Share of requests that reached operation by gate decision and region, merchant and contracted revenue, with Wilson intervals.

| Gate, revenue | Funded | Held | Exited | Funded: operated | Exited: operated | Funded: value, $M |
|----------------------|----------|----------|----------|----------------|----------------|----------------|
| Entry, merchant | 166 | 560 | 1,542 | 33% [26%, 41%] | 6% | +4,079 |
| Entry, contracted | 203 | 550 | 1,515 | 29% [23%, 36%] | 6% | +9,137 |
| Two years in, merchant | 178 | 620 | 500 | 29% [23%, 36%] | 7% | +3,642 |
| Two years in, contracted | 251 | 554 | 493 | 30% [25%, 36%] | 7% | +8,975 |

*Table E2.* The two gates scored on what happened to the 2017–2019 requests. Operated: within five years of entry at the first gate, within three years of the second.

### E.7 The book: when to buy and how much

**Buy at the milestone, not at entry.** A registered test settles the timing. Two years in, a book of 25 requests chosen by the landmark model held 19 that reached operation within three years, against 11 for the lookup that knew the same agreement status (Figure E9). A book of 50 held 33 against 24. The same books held fewer megawatts, so the landmark model picks more plants that get built, not more capacity. At entry the lookup ties or wins.

![Figure E9](../figures/F18_managed_book.png)

*Figure E9.* Operations and MW realised within three years of the two-year landmark, for books of 25 and 50 chosen by the landmark model, the agreement-aware lookup, the entry lookup and at random, with 95% intervals.

**How many to add, and where.** Adding requests in the landmark model's order while its probability stays at or above the pool's rate admits 410 of the 1,132 utility-scale requests still waiting; 23% of them operated, against 10.5% for the pool. This floor book is built without the regional cap of the registered book, which is why its first 25 picks hold 22 operations rather than 19. ERCOT is where the two-year review pays: 167 adds captured 70 of the region's 75 operations. In PJM, without dated agreements, the model separates little; in CAISO the floor admits two requests (Appendix Figure A4).

**Four ways to spend one deposit budget.** Four policies spent the same $20.11 million deposit budget on the 2017–2019 pool. Every policy that counts capital buys wind, and every one made money in both revenue cases, where a book chosen by megawatts lost it at merchant prices (Table E3). The risk-adjusted book barely differs from the plain value book, because the shared risk between requests is small; the cohort level is the risk, and the newest cohort's early outcomes reveal it before a company buys.

| Policy, same budget | Requests | Expected NPV, $M | P(loss) | Realised NPV, $M (merchant) | Realised NPV, $M (contracted) |
|----------------------------|------------|---------------|------------|----------------|-----------------|
| Equal regional split | 26 | +1,404 | 2% | +581 | +1,271 |
| NPV per dollar, with caps | 21 | +1,536 | 3% | +396 | +1,235 |
| Model expected NPV, no caps | 27 | +1,803 | 2% | +391 | +1,611 |
| Risk-adjusted, with caps | 21 | +1,531 | 2% | +396 | +1,235 |
| Lookup, value index by MW | 22 | −747 | 79% | −46 | +440 |
| Random | 22 | −220 | 88% | −85 | +15 |

*Table E3.* Six ways to spend the deposit budget on the 2017–2019 pool. Expected NPV and P(loss) are from the merchant scenarios.

**The rule, region by region.** *ERCOT:* invest; enter wind, enter solar with a contract, hold storage, and review every request at the agreement. *PJM:* invest in gas, wind and solar, prefer the light queues of the PJM core and requests under 66 MW, and review after the system impact study. *CAISO:* hold capital; enter only with a signed agreement and a contract.

### E.8 Bridge to Part II

Part I answers the developer: which requests to fund and when. Part II answers the company: how to split one budget between those requests and assets that already produce. One thing carries forward — the hazard models of operation and withdrawal, refitted on what was known on the decision date, which become the timing engine of every power candidate in Part II. Two things do not: Part I's national value basis, replaced by ERCOT's 2024 hourly prices, and Part I's view from the request date, replaced by each request's chance of operating from 1 January 2025, conditional on how long it has waited (section 3).

## Appendix F — Part II in full: the company's decision, how to split one budget

*The method and evidence behind sections 3–9 for the energy portfolio.*

### F.1 The candidates on 1 January 2025

The leases are the twenty with the most output in the twelve months published by the decision date (to September 2024), among the 506 producing in 2024, out of 1,041 with at least sixty producing months. The requests are the five largest of each technology among the 1,649 ERCOT requests of 20 MW and more waiting on 1 January 2025. In v6 they were drawn from the 2017–2019 entrants and valued at entry, though ten of those twenty had been withdrawn or built by the end of 2024; drawing them from the requests still waiting on the decision date removes that inconsistency. Most of the twenty are 2023–2024 entrants of 500 MW and more, the size and age at which requests are least likely to operate, so their chances sit far below the queue's averages unless an agreement is signed.

| Twenty leases, flat 2024 prices | Registered grid | Committee grid |
|----------------------------------------|------------------------------|------------------------------|
| Capital | $1.35B | $5.12B |
| Incremental NPV, base | $8.19B | $2.73B |
| Incremental NPV, low and high grid cases | $5.69B and $5.10B | $4.77B and −$4.77B |
| Leases positive at the high case | 19 of 20 | 0 of 20 |

*Table F1.* The lease book under the two grids. The registered low case pairs low costs with a low uplift, which is why it sits below base.

### F.2 What the energy data say, and how the features were built

A quarter of lease-months produce nothing, and that is normal: leases are shut in for maintenance, storms and workovers, so 25.3% of the 203,963 lease-months report no oil or gas. WTI and Henry Hub correlate at 0.06 month to month; Henry Hub and the ERCOT price at 0.63, because gas sets the Texas price in most hours; Gulf output with any price at almost zero (Appendix Figure A8). Every feature at a forecast origin uses only months that were public by then, and a truncation test shows that features rebuilt after deleting all later data are identical; the test covers the feature builders, not the choice of the lease universe.

### F.3 Forecasting output: machine learning helps for plants, not for leases

Twelve forecast lines were registered before scoring: lease oil and gas at 3, 6 and 12 months, plant capacity factors at 1 and 3 months, and prices. Each pits a machine-learning challenger against the best of five transparent baselines at rolling origins (Figure F1). Three of twelve pass, all for plants. The lease lines fail: the registered challenger's error at three months is 1.35 times the last-value baseline's, a bias from forecasting in logs; a level model added after scoring, and labelled so, brings the ratio to 0.96, and the scenarios draw their output uncertainty from it. Prices behave as random walks. The decision-level test of machine learning is section 8's: the book chosen with the lookup's queue curves against the book chosen with the model's.

![Figure F1](../figures/F27_forecast_gains.png)

*Figure F1.* Forecast error of the challenger relative to the best baseline, by registered line, with paired moving-block bootstrap intervals.

### F.4 What each candidate is worth, and what that rests on

**A lease redevelopment is an uplift on a producing asset.** Each lease's baseline is an Arps decline fitted after the lease's peak in its last 36 months, switching to an 8% annual decline once its own decline falls below that; four leases still ramping decline at the floor from their recent level. The v6 fit had no floor, and ten of the twenty leases were projected never to decline. The redevelopment adds 20% of the baseline after a two-year lead time; its value is the cash flow it adds over doing nothing. The committee grid prices capital at $40,000 per incremental flowing barrel of oil equivalent a day and discounts at 8%; it was added after the registered results, at an outside reviewer's request, and is labelled ASSUMED.

**A power request is a plant that may never be built.** Its value if built uses the 2024 hourly prices — solar earns 92% of the flat hub price, wind 83%, gas combined cycle 136% because it runs only when prices clear its fuel cost — with ATB costs converted to 2024 dollars and the tax credits of the law in force on 1 January 2025: wind the production credit, solar and storage the investment credit, in every operation year of the window. The 2027 deadline for wind and solar was set by a July 2025 law and IRS Notice 2025-42, after the decision date; it is a stress. That value is weighted by the chance of operating in each of seven years and net of the deposits. On the flat 2024 path, under contract, all ten wind and solar requests are positive (+$70M together) — but only with the credits: −$615M without them, −$284M under the 2027 deadline. Every gas and storage request is negative.

### F.5 Scenarios and risk

Prices, output, costs and timing are drawn together: 2,000 twenty-year paths resample calendar-year blocks of the 2018–2024 monthly log changes of WTI, Henry Hub and ERCOT, the same months for all three, capped at ±1.5 a month and reverting toward their 2018–2024 real geometric means with a four-year half-life (ASSUMED). Output varies by the scored forecast errors, costs by a triangular multiplier, and each request's operation year by its curve from the decision date. The held-out set of 2,000 paths redraws every component with its own seeds; in v6 only its prices were redrawn. Two weaknesses remain. Seven historical years make every path, so there is effectively no joint oil–power tail beyond 2018–2024. And the reversion targets sit well above 2024's gas and ERCOT prices, which is what lifts the gas requests' scenario values above their flat-path values (Appendix Figure A5).

### F.6 Allocating the budget

Section 8 reports the books under the committee grid. Under the registered grid the leases are cheap against the barrels they buy, so the risk-aware book holds fourteen leases and seven requests, expects $7.67B and almost never loses money; risk aversion has little to buy there. The registered comparison on that grid is Table A2.

### F.7 When: the book at one to twenty years

A twenty-year NPV says nothing about what the owner holds at year three. Counting only the cash that falls within each horizon, under the registered grid, the best book holds nothing at one or two years, eleven leases at three and fourteen from five; its value within twenty years is $6.56B. A queue request is a carrying cost until it operates (Figure F4).

![Figure F4](../figures/F35_horizon_view.png)

*Figure F4.* Expected NPV counted within 1, 2, 3, 5, 10 and 20 years, by sector, and the composition of the best book at each horizon.

### F.8 The decision gym and the AI advisor

**The gym scores decisions on outcomes, not prose.** Sixteen past situations are rebuilt as of their date: fifteen requests drawn at random from each region's 2017, 2018 and 2019 entrants, the 2017 entrants two years in, ERCOT 2018 with a budget cut of a fifth, and three oil-price regimes — June 2014, January 2020 and March 2022. Since the audit the lease regimes hold the leases producing on their date, baselines fitted on what BSEE had published by then, scenarios drawn from the seven years before the date, and outcomes from the leases' observed production; v6 used the 2024 leases, 2024 fits and the realized future's mean. The three regimes are nearly one decision and count as one situation. Actors: instinct (top-N expected NPV), instinct per dollar, nothing, the registered rule (the gate rule for requests, the risk-aware optimizer for leases), the advisor and, when one is recorded, the human.

**The rule beats instinct only by packing the budget better.** Over the fourteen effective situations the rule beats instinct by $56M a situation, an interval of [−$12M, +$176M] that includes zero, and ties instinct per dollar (−$2.7M [−$12.7M, +$3.0M]): its edge in the lease regimes is choosing by value per dollar under a binding budget. In the queue rooms the gate rule's fund threshold is now the pool's expected rate, not the test cohort's realized one (audit G2), and the rule is behind instinct by $0.6M a room. The advisor trails the rule by $5.1M a situation [−$11.0M, −$1.5M].

![Figure F5](../figures/F34_decision_gym.png)

*Figure F5.* Realized value of the book each actor chose in each past situation, against the best book with hindsight.

## Appendix G — Every finding, its evidence and its verdict

| Question | Finding | Evidence | Verdict |
|-----------------|-----------------------------------------------------|---------------|---------------|
| Where to look | ERCOT builds most often: 18.4% of requests operate within five years, against 4.8% in CAISO. | Appendix E.2 | Observed |
| RQ1, at entry | The model beats cohort averages (AUC 0.86 against 0.73) but ties the lookup at utility scale. | Appendix E.3; C1–C12 | Partly |
| RQ1, two years in | A book of 25 chosen by the landmark model held 19 operations, against 11 for the lookup. | Appendix E.7; C15 | Supported |
| RQ1, on the decision date | Backtested as of 2020 the model ranks better than the lookup (AUC 0.731 against 0.686) but over-predicts ERCOT's level. | Section 4 | Supported for ranking |
| RQ1, output | Machine learning beats baselines for plant output, not for leases or prices. | Appendix F.3; C20 | Partly |
| RQ1, in the decision | The book chosen with the lookup's curves is not beaten by the model's on the registered metric. | Section 8 | Not supported |
| RQ2 | Under the committee grid the risk-aware book loses money in 10% of scenarios with a worst-5% loss of $1.02B; its construction calls exceed the reserve in 44.5% of scenarios. | Sections 8–9 | Derived |
| RQ3 | Under equal constraints the risk-aware book beats NPV ranking by $320M on the registered metric, for $274M of expected value. | Section 8 | Post-registration |
| RQ3, sensitivity | Cheaper oil or dearer redevelopment removes every lease from the book. | Section 8 | Derived |
| RQ4, flexibility | Revising the book in 2027 with this rule is worth −$9M; without a construction line the book is worth $1.40B instead of $2.05B. | Section 9 | Post-registration |
| RQ4, information | Perfect information is worth at most $571M; the ERCOT price level $52M; an agreement signal at most $11.5M. | Section 9 | Post-registration |
| RQ4, the advisor | Its investment increment is zero; it read six questions correctly; it trails the rule in the gym. | Sections 8–9; Appendix B | Post-registration |

*Table G1.* Every finding, its evidence and its verdict. Registered criteria are in Appendix A.

## Appendix H — The audit of 17 October 2026

An independent audit of report v6 and its code (`docs/audit_2026-10-17.md`) found that the prediction layer held and that valuation, allocation and the gym did not. The five findings that changed the recommendation:

| Finding | What was wrong | What changed |
|---------|----------------|--------------|
| A1 | The top-N and equal-capital books ignored the registered 40% technology cap; the risk-aware book's "$1.9B for a smaller tail" was the price of the cap, not of risk aversion. | Every book is held to the same budget and cap and checked. |
| E1 | Ten of the twenty power candidates had been withdrawn or built by the end of 2024, while the leases were valued at 2025. | One decision date; the requests are those still waiting, with chances conditional on their age. |
| E2 | Ten of the twenty lease baselines were fitted with no decline. | A post-peak fit with an 8% terminal decline; the registered lease book fell from $14.6B to $8.19B in this version. |
| G1 | The gym's lease rooms used 2024 leases, 2024 fits and the realized future's mean. | Rooms rebuilt as of their date and counted as one situation. |
| G5 | The advisor's value over the rule was never reported; it was negative. | Reported, and the advisor rebuilt to work through the engine. |

*Table H1.* The audit's headline findings. Smaller corrections — the CVaR tail count, the gas heat content, the gate floor, ATB dollars, the credits, the provenance labels, the held-out draw — are in the audit's register and decisions #88–#92.
