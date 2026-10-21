---
title: "Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization"
subtitle: "An AI-Assisted Decision Intelligence Framework for Risk-Aware Capital Allocation Across Oil, Gas, Power, Renewables, and Storage"
author: "Alan Mössinger"
date: "SIADS 699 Capstone, University of Michigan — Group 13 (a solo project) — October 2026"
---

## Abstract

Can an AI-assisted prescriptive system improve how an energy company allocates capital, and can each part's contribution be measured? I build such a system for one decision — twenty Gulf of Mexico lease redevelopments and twenty ERCOT interconnection requests under one budget on 1 January 2025 — and test it against conventional rules on the same held-out scenarios. Under equal constraints a risk-aware optimizer beats NPV ranking on the registered risk–return metric by $320M [+$142M, +$511M], buying a thinner tail with $274M of expected value; its capital plan holds only with a contingent construction line. Machine-learning queue forecasts rank requests better than a transparent lookup, yet the book chosen with them is not demonstrably better. A language-model challenger then questions the committee's own proposal with computed tools. In a registered test on 36 flawed proposals from simulated committees, following it improved the committee's own objective by $192M per case [+$108M, +$281M] and avoided $240M of worst-5% loss per case. The same tools without the language model achieved most of that. The language model's own contribution is reading the committee: it named 11 of 12 flaws of argument that the tools cannot see and read 40 of 40 rules correctly from words. The contribution is a decision system that shows a committee its trade-off, challenges its proposal, and states where prediction, optimization and a language model add value, and where they do not.

## Executive summary

**The decision.** One budget, forty candidates, 1 January 2025, only what was public that day. The committee must choose how much expected value to give up for a thinner tail, and how to fund construction its requests may call.

**What the models say.** There is no single right book, only a trade-off (Figure 2). At the registered tail weight the risk-aware book expects $2.05B with a worst-5% loss of $1.02B; the return-seeking book expects $2.36B with $1.60B. The risk-aware book wins under equal constraints and keeps winning when re-chosen on resampled scenarios. Its weak point is capital: construction calls exceed the reserve in 44.5% of scenarios, and without a contingent line the book is worth $1.40B.

**What machine learning adds.** It ranks requests better than the lookup, but the decision turns on a few large requests whose chance of operating neither method knows well. The simpler forecast is enough for this decision.

**What the AI adds.** Two roles, both with a person deciding. The *advisor* answers a committee's questions by setting the engine's parameters and explaining only computed numbers; it chooses nothing. The *challenger* reads the committee's rules from its words, tests its proposal against them with the engine's tools, and recommends a computed alternative when the proposal breaks a rule. Challenging improves the committee's own decision and avoids loss. Most of the gain comes from the computed tools, which a checklist without a language model also uses. What only the language model adds is understanding: it reads rules stated in words and names flaws of argument — a sunk cost, a double standard, a belief no fact supports.

**What I recommend.** Choose the tail weight first; at the registered weight, fund the risk-aware book with a contingent construction line of $3.28B. Use the challenger before signing, and record any departure from its guidance with the evidence acknowledged.

## Capital Allocation Memo

*To the investment committee, 1 January 2025. Every figure is a model output scored on held-out scenarios; lease costs are assumed.*

**The ask.** Commit up to $3.42B now — 40% of what the forty candidates would cost the budget today — across twenty Gulf lease redevelopments and twenty ERCOT requests still in the queue, with no technology above 40% of the budget. A lease costs its redevelopment capital; a request costs its deposits plus a reserve for the construction it may need.

**The choice.** The return-seeking book expects $2.36B with a worst-5% average loss of $1.60B. The registered risk-aware book expects $2.05B with a loss of $1.02B and a 10% chance of losing money. A defensive book expects $1.55B with a loss of $0.52B. I recommend the committee choose its tail weight first; at the registered weight that is the risk-aware book.

**What to do with each candidate under that book.** Invest now in six leases and two requests with signed agreements. Invest in stages in five requests: pay the deposit now, commit construction at the agreement. Wait for information on thirteen requests whose agreement signal is worth more than their deposit. Monitor thirteen; reject one.

**What the commitment really is.** The construction reserve is an average: the capital the book's requests call exceeds it in 44.5% of scenarios. Without a contingent line the book is worth $1.40B, not $2.05B, because requests that reach their agreement cannot be built; a line of $3.28B restores $2.02B.

**What would change it.** Oil at $45 a barrel for five years, or redevelopment capital 30% higher, removes every lease from the book. The two largest power positions rest on ERCOT prices spiking as they did in 2021 and on prices reverting upward from 2024's low level.

**What information is worth.** Knowing everything before committing would be worth at most $571M; knowing the 2025–2029 ERCOT price level, $52M; one request's agreement signal, at most $11.5M.

**Before you sign.** State your rules in words — your tolerance for loss, your liquidity, what you will not hold. The challenger reads them back as numbers for you to confirm, tests your proposal against them and names the computed book that keeps them. If you depart from a book it guides you to, the ledger asks you to acknowledge the evidence.

## 1 Introduction: why better predictions do not guarantee better investment decisions

An energy company with one budget holds requests to connect new plants to the grid, most of which are never built, and oil and gas leases that already produce. Data science usually stops at the forecast. A forecast is not a decision: the decision also depends on costs, constraints, timing and how much loss the owner can bear, and on whether the machinery that joins them does what it says.

The previous version of this report shows the second point. An independent audit (Appendix H) found five errors that no test of forecast accuracy would have caught: comparison books held to different constraints, power candidates already withdrawn or built, leases projected never to decline, a backtest that used information from after its dates, and an AI advisor that added nothing over the rule it was meant to improve. A later review found three inputs that were not public on 1 January 2025. All were corrected; the registered record is kept as it was scored (Appendix A).

| Stage | Question | In this report |
|------------------|----------------------------|----------------------------------------------------------------|
| Predictive | What is likely? | Each request's chance of operating from today; lease and plant output |
| Uncertainty | What could go wrong? | 2,000 joint scenarios of prices, output, costs and timing |
| Prescriptive | What should we do, and is it better? | The book under a budget, caps and a risk policy, against conventional choices |
| Challenge | Is the committee's own choice sound? | A language model that tests the proposal with computed tools, against a checklist |

*Table 1.* The analytical stages. The last two are the contribution.

## 2 Research questions, hypotheses and contributions

The overarching question is whether an AI-assisted prescriptive system can improve energy capital allocation by joining machine-learning predictions, uncertainty, portfolio optimization and human decision support — and show when it beats conventional alternatives.

- **RQ1 Predict.** How well does machine learning estimate completion, timing and output against transparent baselines?
- **RQ2 Quantify.** How do price, output, cost and timing risk change value and downside?
- **RQ3 Prescribe.** Which investments should be selected under capital, diversification and downside constraints?
- **RQ4 Evaluate.** Under equal constraints and scenarios, how much of any gain comes from the forecasts, the optimizer and the language model separately — and does challenging a committee's proposal improve its decision?

Three hypotheses were registered before any result: **H1** machine-learning forecasts reduce held-out error against simpler baselines; **H2** a risk-aware book beats NPV ranking and sector-concentrated books on a stated risk–return metric; **H3** uncertainty-aware selection is more stable under stresses than deterministic selection. Four more were registered before the challenger was run, on a corrected system and so labelled post-registration: **H4** it finds flaws the tools alone cannot, without over-challenging; **H5** following it improves the committee's decision; **H6** the language model adds decision value beyond its tools; **H7** it reads rules reliably from words.

The contributions are three: a corrected prescriptive pipeline with the audit that produced it; a decision workflow in which a language model reads and argues but never computes (Figure 1); and an evaluation that separates forecasting, optimization and language-model value on the same scenarios.

![Figure 1](../figures/F43_architecture.png)

*Figure 1.* The decision workflow in six stages, and what is measured.

## 3 Energy portfolio, datasets and economic assumptions

Every source is public: LBNL's *Queued Up* interconnection files, BSEE monthly lease production, EIA prices and plant generation, ERCOT's hourly settlement prices for 2018–2024 and the NREL Annual Technology Baseline. A readiness gate checked each source before any model was fitted.

**One decision date.** Both sectors are decided on 1 January 2025 with only what was public that day: lease output to September 2024, agreements as the 2025 edition dates them, and the tax credits of the law then in force. The leases are the twenty with the most output in the twelve months published by that date. The requests are the five largest of each technology — gas combined cycle, solar, wind, storage — among the 1,649 ERCOT requests of 20 MW and more still waiting, about 359 GW. Each request's chance of operating within seven years is conditional on how long it has waited and on whether it has signed its interconnection agreement.

**Valuation.** A lease redevelopment adds 20% to output after two years; its value is the cash flow it adds over a baseline that declines at least 8% a year (ASSUMED; 5–12% as the range). Redevelopment costs are not public, so every result is shown under two grids: the registered grid fixed before any result, and the harder committee grid, which prices capital per incremental barrel and discounts at 8%. Under the registered grid the twenty leases are worth $8.19B; under the committee grid $2.73B, for $5.12B of capital. A power request is valued on the 2024 hourly prices with ATB costs and the tax credits of the law in force; the 2027 deadline a July 2025 law set for wind and solar is a stress, not the base case.

**The budget.** A lease spends its capital now. A request needs only its deposits now, plus a reserve for the construction it will call if it reaches its agreement. The budget is the registered rule in those units, 40% of the forty charges. Every dollar figure carries a provenance label: OBSERVED, DERIVED, FORECAST or ASSUMED.

## 4 Prediction and uncertainty

**Queue completion.** Discrete-time LightGBM hazards on entry attributes, tested once on 2017–2019 entrants, rank requests above cohort averages (AUC 0.86 against 0.73), but for requests of 20 MW and more a careful lookup — the share built among earlier requests of the same region, technology and size — ranks as well. Refitted on what was known in 2020 and scored on what followed, the model ranked better than the lookup (AUC 0.731 against 0.686) but put ERCOT's five-year chance at 0.380 where 0.238 operated; that ratio, knowable on the decision date, corrects the 2025 curves.

**Energy forecasts.** Of twelve registered lines, machine learning beat the best of five transparent baselines for plant capacity factors and failed for lease output and prices (Appendix F).

**Scenarios.** 2,000 joint twenty-year paths resample calendar-year blocks of the 2018–2024 monthly changes of oil, gas and ERCOT prices together, revert toward their means with a four-year half-life (ASSUMED), and carry output, cost and timing draws. A second set of 2,000 paths, redrawn in every component, is used only to score books.

## 5 Prescriptive portfolio optimization

The risk-aware book maximises expected NPV minus λ times the worst-5% average loss (CVaR95), over binary choices of the forty candidates, under the budget and a 40% cap per technology, with the tail linearised after Rockafellar and Uryasev (2000) and solved exactly with HiGHS. λ = 1 is the registered setting; λ = 0 gives the deterministic book; a hard limit on the tail, or on construction calls beyond a liquidity line, replaces the penalty when a committee states its downside as a rule. The conventional books are **A**, ranking by expected NPV, and **B**, equal capital by sector, held to the same budget and cap.

Three tools make the optimizer something a committee can question. The **frontier** solves the book across tail weights and limits. A **what-if** reprices every candidate under validated parameters — an oil price for some years, ERCOT volatility, the budget, redevelopment capital — and re-solves. A **repair** finds the fewest changes to a committee's own book that make it keep its rules.

## 6 The AI layer: an advisor, a challenger and a person who decides

The language model never produces a number the decision uses (Figure 1; Appendix B). It does two jobs.

**The advisor answers questions.** A committee question in words becomes parameters from a fixed schema, or a refusal if the model cannot represent it. The engine validates the parameters, computes the new book and every candidate's status, and the language model explains the computed fact sheet; a checker holds every number to that sheet in its unit.

**The challenger questions the committee.** It works in two rounds. First, the language model reads the committee's statement into rules — tail weight, chance-of-loss and tail limits, exclusions, a liquidity line — and may ask the engine to test up to two of the committee's beliefs as what-ifs. Then tools, not the language model, diagnose the proposal on held-out scenarios: which rules it breaks, the construction calls it cannot fund, the members that lose in most scenarios. They compute two alternatives under the committee's own rules: the repair and the optimizer's book. Finally the language model writes a memo: at most three vulnerabilities, each tied to numbered facts and typed; a level — explain, challenge or guide; the loss the change avoids; and what would change its mind. Code checks every number and the guide rule: it may guide only toward an alternative that keeps every rule and either fixes a broken one or beats the proposal with an interval clear of zero.

**A person decides.** The committee sees its rules read back as numbers before anything is computed. A named person signs. Leaving a book the challenger guided toward is allowed, but the ledger records the decision only with the contrary evidence acknowledged, and each row is hash-chained to the one before.

## 7 Experiments, benchmarks and validation

**The registered record.** Of 70 registered lines, 28 passed, scored once and never re-scored (Appendix A). Applied to the corrected system, the same allocation criteria give different verdicts; those are post-registration results.

**Decision processes.** Seven processes see the same candidates, budget, cap and scenarios; each book is chosen on the primary scenarios and scored on the held-out ones: **A** and **B** as above; **C** deterministic; **D** risk-aware; **D + revision** in 2027; **E**, AI-assisted; and **F**, book D chosen with the lookup's queue curves. Differences carry paired bootstrap intervals.

**The challenger, registered before it ran.** I wrote 48 committee proposals from ten personas: 36 carry one flaw — a broken rule, unfunded construction calls, a fragile position, a sunk cost, a double standard or an unsupported claim — and 12 are sound. Each flawed proposal ends as the committee's book under three policies: keep it; follow a checklist that uses the same tools and fixed rules with no language model; or follow the challenger. Each is scored on the committee's own objective in five worlds: the base model, ERCOT prices 25% lower, ERCOT half as volatile, lease capital 30% higher, and completion as the lookup says. Forty rules in words test the reading. The cases, statements, prompts and model were hashed and committed before the first call.

**How I could fool myself.** *Unequal constraints:* every book faces the same budget and cap. *Hindsight:* every view uses only what was known on its date. *A weak baseline:* the lookup sits beside every forecast, and the checklist beside the challenger. *Crediting the language model with the tools' work:* the checklist isolates it. *Grading my own memos:* detection is scored by the type the memo assigns, not by a judge.

## 8 Findings: the trade-off and what drives it

**The trade-off is real and the committee must price it.** Along the frontier, expected value and tail fall together (Figure 2). Under the committee grid the deterministic book expects $2.36B with a worst-5% loss of $1.60B; the risk-aware book $2.05B and $1.02B; at λ = 2, $1.55B and $0.52B.

![Figure 2](../figures/F38_frontier.png)

*Figure 2.* The frontier over risk policies on held-out scenarios, the registered books on it, and capital by technology along it.

**Under equal constraints, the risk-aware book wins on the registered metric.** It beats NPV ranking by $320M [+$142M, +$511M] and equal capital by $213M [+$120M, +$315M] on expected NPV minus CVaR95, while giving up $274M of expected value against NPV ranking (Figure 3). Re-chosen on 20 resampled scenario sets it beats NPV ranking every time, by $116M to $352M; 11 of its members are chosen in at least 80% of them. Under the registered grid the risk-aware book beats NPV ranking by $1,332M, ties equal capital (+$24M, an interval that includes zero), and fails the stability and single-sector tests.

![Figure 3](../figures/F42_value_added.png)

*Figure 3.* Each process against its comparator on the same held-out scenarios, with paired bootstrap intervals.

| Committee grid, held-out | A NPV ranking | B equal capital | C deterministic | D risk-aware | F lookup forecasts |
|-------------------------|--------------|----------------|----------------|-------------|------------------|
| Candidates funded | 16 | 16 | 17 | 13 | 18 |
| Expected NPV, $B | 2.33 | 2.08 | 2.36 | 2.05 | 1.84 |
| Worst-5% loss, $B | 1.61 | 1.26 | 1.60 | 1.02 | 0.83 |
| Chance of a loss | 13% | 12% | 13% | 10% | 9% |
| Regret against perfect information, $B | 0.60 | 0.84 | 0.57 | 0.87 | 1.08 |

*Table 2.* The decision processes on the same 2,000 held-out scenarios.

**Machine learning does not demonstrably improve this decision.** Book D expects $209M more than the book chosen with the lookup's curves, and scores +$22M [−$168M, +$207M] on the registered metric in the model's scenarios and −$143M [−$375M, +$87M] in the lookup's; neither interval excludes zero. The model ranks requests better, but the decision turns on a few large requests whose chance of operating neither method knows well.

**What drives value and downside.** Book D holds six leases and seven requests. The position whose removal costs the most is an 836 MW wind request with a signed agreement: forcing it out lowers the objective by $549M. The largest power position, a 1,350 MW gas request, expects $512M yet loses money in 77% of scenarios; its place is worth only $7.7M at the registered tail weight. Re-solved under the committee's questions (Appendix D), the book drops every lease when oil stays at $45 for five years or redevelopment capital rises 30%, and drops the gas request when ERCOT is half as volatile.

## 9 Findings: capital, timing and information

**The capital plan is the weak point.** The book's requests call construction capital beyond the reserve in 44.5% of held-out scenarios; in one scenario in twenty the excess is $3.28B or more (Figure 4). Without a contingent line the requests that reach their agreement cannot be built and the book is worth $1.40B; a line at that 95th percentile restores $2.02B.

![Figure 4](../figures/F45_robustness.png)

*Figure 4.* Book D's construction calls beyond its reserve, and how often each candidate is chosen when the book is re-chosen on resampled scenarios.

**Revising the book in 2027 adds nothing here.** Revising on 1 January 2027, after two years of prices and agreement signals, is worth −$9M [−$16M, −$3M] on held-out scenarios. The cap leaves no room to start a deferred lease, so the revision can only drop requests, and its estimates drop some that would have paid. This says the rule's estimates are noisy, not that flexibility has no value.

**What information is worth.** Perfect knowledge before committing would be worth at most $571M on a risk-neutral objective; knowing the 2025–2029 ERCOT price level $52M, the oil level $32M. Learning within two years whether one request signs its agreement is worth up to $11.5M; for thirteen requests outside the book that exceeds the deposit needed to wait, so their status is "defer pending information".

## 10 Findings: does challenging the committee improve its decision?

**Yes — and it mostly avoids loss.** Following the challenger improved the committee's own objective by $192M per flawed case [+$108M, +$281M], averaged over five worlds, and cut the worst-5% loss by $240M per case [+$133M, +$345M] in the base world (Figure 5, Table 3). The gain is largest where the model is wrong in the proposal's disfavour: with ERCOT prices 25% lower or lease capital 30% higher, the challenged books stayed near break-even on the committee's objective while the proposals lost.

**Most of the gain is the tools'.** The checklist, with the same tools and no language model, improved the objective by $145M and cut the tail by $257M. The challenger's further $46M [+$4M, +$116M] came from four cases in which it chose the optimizer's book where the checklist takes the smaller repair; a fixed rule that prefers the optimizer's book does as well (+$1M [−$50M, +$64M]).

**What only the language model adds is understanding.** It named the flaw in all 24 computable cases, as the checklist did, and in 11 of the 12 flaws of argument, which the checklist cannot see because they live in the committee's words. It read all 32 representable rules exactly and refused all 8 it could not represent, from a carbon price to a partner's appetite. In this test that understanding did not change what was bought: every flaw of argument that warranted a different book also broke a computed rule. A test in which only the argument is wrong is the next experiment.

**It has costs.** It challenged 2 of the 12 sound proposals with a claim they did not earn, above the registered limit of 15%, and 10 of 48 memos carried a number that was not on their fact sheet — listed beside the memo by the checker, never used by the engine.

![Figure 5](../figures/F46_challenger.png)

*Figure 5.* Left: flaws named, by type, by the challenger and by the checklist. Right: the committee's objective and the loss avoided, per flawed case, with case-bootstrap intervals.

| 48 committee cases | Challenger | Checklist (no language model) |
|------------------------------|-----------------|-----------------|
| Computable flaws named | 24 of 24 | 24 of 24 |
| Flaws of argument named | 11 of 12 | 0 of 12 |
| Sound proposals over-challenged | 2 of 12 | 0 of 12 |
| Committee objective vs proposal, per case | +$192M [+$108M, +$281M] | +$145M |
| Worst-5% loss avoided, per case | $240M [+$133M, +$345M] | $257M |
| Rules read from words | 40 of 40 | — |

*Table 3.* The registered challenger experiments on simulated committees; 6 of 8 registered lines pass.

## 11 Limitations, governance and practical implications

**What the results are, and are not.** They are model-based comparisons on public data and assumed costs, not demonstrated improvements in a company's capital allocation. Redevelopment costs are bracketed by two grids. The scenarios resample seven years of history, so a worse tail than 2018–2024 cannot appear, and mean reversion lifts gas and ERCOT prices well above 2024's. The 2025 queue curves rest on two backtests that disagree about the level. The committees of the challenger test are personas I wrote, the advisor is one model, and there are 36 flawed cases; a study with real committees is proposed, not run. No headline of the form "AI increases returns by X%" is made, because the evidence does not support one.

**Who could be harmed.** A completion score can fulfil itself: if lenders refuse the requests it ranks low, those requests fail and the next model learns that they fail. Size is a top driver, so screening applicants by the score would penalise small developers. The score should inform a portfolio, not screen access to the grid.

**Governance.** A named person decides. The language model computes nothing; its numbers are checked against computed facts; it may guide only when the evidence allows; and the ledger refuses a departure from guided advice without the evidence acknowledged.

## 12 Conclusions and future research

Better predictions did not, by themselves, produce better decisions here. The machine-learning queue model ranks requests better than a lookup, yet the book built on it scores no better. The optimizer earns its place only when held to the same constraints as the rules it is compared with; then the risk-aware book wins by trading expected value for a thinner tail, and its capital plan needs a contingent line. A language model that challenges the committee with computed tools improves the committee's decision and avoids loss, but the tools do most of that work; the language model's part is to understand the committee — its rules, its arguments, its blind spots. A decision system is useful when it states which part is doing the work. Future work: committees deciding with and without the challenger, cases where only the argument is wrong, tails beyond the historical years, and real redevelopment costs.

## Statement of work

This is a solo project registered in a group slot (Group 13). All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried out by Alan Mössinger. The ERCOT price client and the battery dispatch model are reused, with credit, from my own earlier projects (Forecast to Dispatch; MADS Milestone II).

## Changes after review

Two outside reviews in October 2026 led to the changes logged in `docs/mentor_feedback.md`. The second asked for an evaluated decision intelligence system; its first request was an independent audit, whose corrections are this version. A review on 19 October found three inputs that were not public on the decision date and the capital calls unpriced, both corrected, and asked that the language model help the committee decide; the challenger and its registered test are the answer. A course mentor is assigned after the proposal review; their feedback will be logged in the same file.

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

**The challenger's registered record — post-registration, scored once.** Registered on 20 October 2026 before the first call, with the hashes of the 48 cases, the 40 statements, the three prompts and the model (`results/v9/success_criteria_v9_registered.json`); the committees are simulated.

| Criterion | Rule | Result |
|------------------------------------------|-----------------|------------------------------|
| C25: flaws of argument named | at least 75% | 92% (11 of 12), PASS |
| C26: computable flaws named | at least 90% | 100% (24 of 24), PASS |
| C27: sound proposals over-challenged | at most 15% | 17% (2 of 12), FAIL |
| C28: memos fully grounded; valid fact references | 80%; 95% | 79%; 100%, FAIL |
| C29: committee objective, challenger vs proposal | interval above zero | +$192M [+$108M, +$281M], PASS |
| C30: worst-5% loss avoided | interval above zero | +$240M [+$133M, +$345M], PASS |
| C31: challenger vs checklist | interval above zero | +$46M [+$4M, +$116M], PASS |
| C32: rules read; out-of-scope refused | 85%; 6 of 8 | 32 of 32; 8 of 8, PASS |

*Table A3.* The challenger's registered lines; 6 of 8 pass. Source: `results/v9/success_criteria_v9_scored.csv`.

*H4* (finds what tools cannot, without over-challenging) is not supported: C27 fails. *H5* (challenging improves the decision) is supported. *H6* (the language model adds value beyond its tools) passes its registered rule, but two checks reported and not registered show what it rests on: without its largest case the edge is +$19M [+$0M, +$46M], and against a fixed rule that takes the optimizer's book first it is +$1M [−$50M, +$64M] (decision #97). *H7* (reads rules reliably) is supported.

## Appendix B — The AI advisor

**What it sees and what it may do.** In v8 the advisor works through the engine (`src/advisor_tools.py`). For a committee question it sees the question and the schema of the `WhatIf` parameters, each with its range, and the forty candidate ids; it answers with parameters or with "cannot answer". The engine validates the parameters and computes. For the explanation it sees only the computed fact sheet. It sees no web, no memory across calls and no company data.

**How its numbers are checked.** `advisor_tools.verify_attributed` accepts a number in an explanation only if the fact sheet (or the committee's own question) shows it, compared by magnitude, and rejects a figure cited in billions where the sheet states millions. Integers up to ten and years are exempt. The v6 check, `advisor.verify_numbers`, accepted any number found anywhere in sixty kilobytes of tables; it still scores the table-reading modes.

**Record and replay.** Every call is appended to `results/advisor_runs.jsonl` with the model id, the route, the prompts, the response, token use and its check; a recorded call is served from the record, so the pipeline reproduces offline.

**The override gate and the ledger.** A decision is written by `src/ledger.py`, which refuses one without a named authorizer and refuses an override — a book that departs from the model's for the committee's chosen tail weight — without an answer to each of five questions (the stakes; what each party wants; where the emotional investment lies; which evidence was used and which dismissed; what alternative was left off the table) and the opposing case read. Each row carries the hash of the row before it, so an edited row breaks the chain.

**The prompts.** Eight templates sit in `prompts/`: the system prompt, the recommendation, the gym pick, the three of the challenge round (the five questions, the motivated-reasoning check and the ideological Turing test, unchanged since decision #73), and the two of v8, which translate a question into parameters and explain a computed result.

**The challenger.** Two more templates, `challenge_read.md` and `challenge_memo.md`, drive `src/challenge.py`. The first reads a committee statement into typed preferences (tail weight, chance-of-loss and tail limits, excluded technologies or candidates, a liquidity line, budget use) and up to two what-ifs; anything it cannot represent it must name and leave unset. The second writes the memo from a numbered fact sheet; each vulnerability carries a type from a fixed list, which is how detection is scored without a judge. Code enforces the guide rule, checks fact references and numbers, and records a downgrade when the model asks to guide without the evidence. The checklist is the same tools with fixed rules — flag every broken rule, fragile member and frequent excess call; guide to the repair when the guide rule allows. The registered run made 136 live calls, none failed; every one replays from the record.

**Scored.** On the six committee questions of notebook 11 it read all six correctly — five into parameters, the sixth refused — and its five explanations cited 119 numbers, all in the computed fact sheet. Across the table-reading and what-if modes, 195 calls are recorded; their numbers were in the tables shown 94% of the time. The challenger's 136 calls are scored apart, under their registered checks (Section 10, Table A3). In the decision gym the advisor trailed the registered rule by $5.1M a situation [−$11.0M, −$1.5M], worse in 12 of 14.

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
| The decision layers | `src/decision_date.py`, `src/valuation.py`, `src/whatif.py`, `src/advisor_tools.py`, `src/ledger.py`, `src/voi.py`, `src/dynamic.py`, `src/robustness.py`; notebook 11 |
| The challenger and its experiments | `src/challenge.py`, `src/challenge_experiments.py`, `prompts/challenge_*.md`; the registration and every output in `results/v9/`; notebook 11, section 11 |
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

![Figure A10](../figures/F39_reallocation.png)

*Figure A10.* Book D's capital by technology, re-solved under each committee question.

![Figure A11](../figures/F41_staged.png)

*Figure A11.* Book D held, or revised on 1 January 2027, on the held-out scenarios.

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

**Every cohort completes below the model's level.** For requests of 20 MW and more, 11.0% of 2017 entrants and 5.9% of 2018 entrants operated within five years, while the model predicted about 12% for both. The 2020–2022 entrants operate within two years at about a quarter of the predicted rate. Refitting the intercept on the newest completed cohort removes about 40% of the error and none of the post-2020 gap. In megawatts, the 2017–2019 cohort was expected to bring 29.2 GW online within five years and brought 18.8 GW. A book must be sized to the newest cohort's level, not to the model's.

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
| RQ4, the advisor | Its investment increment is zero; it read six questions correctly; it trails the rule in the gym. | Section 6; Appendix B | Post-registration |
| RQ4, the challenger | Following it improves the committee's own objective by $192M per flawed case and avoids $240M of worst-5% loss; a checklist without a language model achieves $145M and $257M. | Section 10; Table A3 | Post-registration |
| RQ4, the language model | It names 11 of 12 flaws of argument and reads 40 of 40 rules; against a fixed rule its decision value is +$1M [−$50M, +$64M]. | Section 10; Appendix A | Post-registration |

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
