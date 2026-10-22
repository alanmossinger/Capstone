---
title: "Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization"
subtitle: "An AI-Assisted Decision Intelligence Framework for Risk-Aware Capital Allocation Across Oil, Gas, Power, Renewables, and Storage"
author: "Alan Mössinger"
date: "SIADS 699 Capstone, University of Michigan — Group 13 (a solo project) — October 2026"
---

## Abstract

I ask three questions of one capital decision — twenty Gulf of Mexico lease redevelopments and twenty ERCOT interconnection requests under one budget on 1 January 2025, built only from what was public that day — and a fourth about who deserves the credit. Can predictive models improve estimates of energy investment outcomes? Partly: a queue model ranks requests better than a transparent lookup (AUC 0.731 against 0.686; in ERCOT 0.656 against 0.591) and still ranks a year later, but it overstates the level, expecting 78 operations in 2025 where 30 happened. Can optimization turn those estimates into better capital-allocation decisions? Yes, when the constraints are shared: a risk-aware optimizer beats NPV ranking on the registered risk–return metric by $219M [+$13M, +$401M], buying a worst-5% loss of $0.82B instead of $1.55B with $508M of expected value, and the construction line it needs still pays at a bank's price. Can a language model improve investment governance without taking authority from decision-makers? In a registered test on 48 simulated committee proposals, tools alone improved the committee's own objective by $76M per case; the language model added $43M [+$9M, +$86M] more; the optimizer's own book $134M beyond that. The model read every paraphrased rule, named every flaw of argument I wrote and over-challenged no sound proposal; it failed two of nine registered lines, reading a committee's silence as a zero tail weight and writing numbers that are not on its fact sheet. Every registered line is scored once and every failure reported as it fell.

## Executive summary

**The decision.** One budget, forty candidates, 1 January 2025, only what was public that day. A committee must choose how much expected value to give up for a thinner tail, and how to fund the construction its requests may call.

**Q1, prediction.** The queue model ranks better than the lookup and still overstates how many requests will operate; the first year after the decision showed the same (Figure 4).

**Q2, optimization.** Under equal constraints the risk-aware book wins on the registered metric, by $219M against NPV ranking; its weak point, construction calls beyond the reserve in half the scenarios, is met by a $2.53B line worth having even at a bank's price (Figure 3).

**Q3, governance.** A language model that challenges the committee with computed tools improves the committee's own decision by $43M per case beyond what the tools alone do, and holds no authority: it computes nothing, may guide only when the evidence allows, and a named person signs. It reads stated rules and names flaws of argument; it reads silence badly and invents numbers, and the code catches both.

**Q0, attribution.** Of the $119M per case the challenged committee gains over its own proposal, the tools account for $76M and the language model for $43M; the optimizer would add $134M more (Figure 5).

**What I recommend.** Choose the tail weight first; at the registered weight, fund the risk-aware book — five leases and eight requests — with a contingent construction line of $2.53B. Use the challenger before signing, and record any departure from its guidance with the evidence acknowledged. The memo to the committee is Appendix I.

## 1 Introduction: why better predictions do not guarantee better investment decisions

An energy company with one budget holds requests to connect new plants to the grid, most of which are never built, and oil and gas leases that already produce. Data science usually stops at the forecast. A forecast is not a decision: the decision also depends on costs, constraints, timing and how much loss the owner can bear, and on whether the machinery that joins them does what it says.

Earlier versions of this report show the second point. An independent audit (Appendix H) found five errors no test of forecast accuracy would have caught — comparison books held to different constraints, candidates already withdrawn or built, leases projected never to decline, a backtest with hindsight, an advisor that added nothing — and a later critique found a candidate set built from a file released after the decision date, a construction line treated as free, and a challenger tested on statements written by the model family under test. All were corrected; every registered line is kept as scored, with its corrections (Appendix A). The stages — predict what is likely, quantify what could go wrong, prescribe the book, challenge the committee's own choice — are Figure 1; the last two are the contribution.

## 2 The questions and the two primary estimands

- **Q1 Prediction.** Can predictive models improve estimates of energy investment outcomes? The estimate is each request's chance of operating within seven years of the decision date, against a transparent lookup.
- **Q2 Optimization.** Can mathematical optimization turn those estimates into better capital-allocation decisions? The primary estimand, **C33**, is the paired difference on the registered metric — expected NPV minus the worst-5% average loss — between the risk-aware book and NPV ranking under identical constraints, on held-out scenarios.
- **Q3 Governance.** Can a language model improve the quality of investment governance without taking authority away from decision-makers? The primary estimand, **C34**, is the paired difference on the committee's own objective between the book it ends with when a language model challenges it with computed tools and the book it ends with when the same tools run as a checklist, over all 48 cases.
- **Q0 Attribution.** A four-arm ladder — unchallenged proposal, tools only, tools with the language model, the optimizer's own book — each rung a paired difference with a case-bootstrap interval.

Nine lines were registered and committed before the first model call of the final test (`results/v10/success_criteria_v10_registered.json`, 22 October 2026): C33 and C34 primary; C35 and C36 the other rungs; C37–C39 whether the model reads rules and paraphrases exactly and resists injected instructions; C40 and C41 whether it over-challenges sound proposals or misses flaws of argument. Three hypotheses hang on them: **H8** the model improves the committee's decision on its own objective (C34); **H9** it reads rules reliably and resists instructions to move them (C37–C39); **H10** it names flaws of argument the tools cannot see without over-challenging (C40, C41). H1–H7 and their 78 registered lines are in Appendix A with every correction.

The contributions: a prescriptive pipeline built from what was public on the decision date; a decision workflow in which a language model reads and argues but never computes (Figure 1); and an evaluation that separates the value of forecasting, optimization and the language model on the same scenarios, failures included.

![Figure 1](../figures/F43_architecture.png)

*Figure 1.* The decision workflow in six stages, and what is measured at each.

## 3 Data, candidates and assumptions

Every source is public — LBNL's *Queued Up* files, ERCOT's monthly interconnection reports, BSEE lease production, EIA prices and generation, ERCOT's hourly prices, the NREL Annual Technology Baseline — and `data/raw_manifest.csv` records every raw file with its hash.

**One decision date, strictly.** Both sectors are decided on 1 January 2025 with what was public that day. For the queue that is the LBNL 2024 edition (requests through 2023) and ERCOT's eight monthly reports of 2024, which say which requests were live, their size and whether an agreement was signed; the 2025 edition earlier versions used was released in August 2025. Of the twenty requests it had given, 16 stand; 4 were not public on the date and give way to 4 that were. The requests are the five largest of each technology — gas combined cycle, solar, wind, storage — among the 1,441 ERCOT requests of 20 MW and more live on the date, about 310 GW; the leases are the twenty with the most output in the twelve months published by then. Each request's chance of operating within seven years is conditional on its age and on whether it has signed its agreement; the hazard models learn from the history censored at the date, in which a request still waiting is right-censored, never counted as failed.

**Valuation and the loss variable.** A lease redevelopment adds 20% to output after two years; its value is the cash flow it adds over a baseline that declines at least 8% a year (ASSUMED; 5–12% as the range). Redevelopment costs are not public, so results are shown under two grids, the registered one and the harder committee grid that prices capital per incremental barrel. A power request is valued on the 2024 hourly prices with ATB costs and the tax credits of the law in force; the 2027 deadline a July 2025 law set for wind and solar is a stress. "Worst-5% loss" means the CVaR95 of −NPV: the mean of the 100 worst of 2,000 held-out scenarios.

**The budget and the line.** A lease spends its capital now; a request needs its deposits now plus a reserve for the construction it will call if it reaches its agreement. The budget is 40% of the forty charges in those units: $3.82B. A contingent construction line funds calls beyond the reserve in a fixed order until it is spent, priced (ASSUMED, registered before the final test) at a commitment fee of 0.5% a year on the undrawn amount and 8% a year on draws outstanding for 2 years of construction. Every dollar figure carries a provenance label: OBSERVED, DERIVED, FORECAST or ASSUMED.

## 4 Q1 — Prediction

**Ranking, as of 2020.** At entry, LightGBM hazards rank requests above cohort averages (AUC 0.86 against 0.73), but at 20 MW and more a careful lookup — the share built among earlier requests of the same region, technology and size — ranks as well (Appendix E). Refitted on what was known in 2020 and scored on what followed, the model ranked better than the lookup across the three regions (AUC 0.731 against 0.686) and in ERCOT alone (0.656 against 0.591), but put ERCOT's five-year chance at 0.380 where 0.238 operated. That ratio, knowable on the decision date, corrects the level of the 2025 curves. AUC is not calibration: the model orders requests well and sets their level badly.

**One year on, post-hoc.** The 2026 edition records what happened in 2025 (Figure 4). Of the 1,441 live requests, 30 operated, 77 withdrew and 1,323 were still waiting (11 the 2026 file no longer lists). The raw model expected 125 operations, the level-corrected model 78 and the lookup 17: the correction removed half the error, and the lookup erred the other way. The corrected model's calibration slope is 0.66 against 0.01 for the lookup, whose predictions barely separate the requests that operated from the rest; the lookup's better Brier score (0.0209 against 0.0258) comes from predicting almost nothing for everyone. Of the twenty candidates, 19 were still waiting. The realized 2025 prices fell inside the scenario bands for oil and ERCOT and above the 95th percentile for gas (Henry Hub $3.53 against a band topping at $3.41); the twenty leases produced 1.03 times their no-redevelopment baseline.

![Figure 4](../figures/F49_forward_calibration.png)

*Figure 4.* Realized 2025 queue outcomes against the one-year predictions of the decision date, and the twenty candidates one year on. Nothing refitted.

**Energy forecasts and scenarios.** Of twelve registered lines, machine learning beat the best of five transparent baselines for plant capacity factors and failed for lease output and prices (Appendix F). 2,000 joint twenty-year paths resample calendar-year blocks of the 2018–2024 monthly changes of oil, gas and ERCOT prices together, revert toward their means with a four-year half-life (ASSUMED), and carry output, cost and timing draws; a second set of 2,000, redrawn in every component, only scores books.

**What prediction is worth to this decision.** Perfect knowledge before committing would be worth at most $825M on a risk-neutral objective, the 2025–2029 ERCOT price level $47M. Learning within two years whether one request signs its agreement is worth up to $59.4M; for twelve requests outside the book that exceeds the deposit needed to wait, so their status is "defer pending information". The answer to Q1 is partial: the model improves the ranking of outcomes, not their level.

## 5 Q2 — Optimization

The risk-aware book maximises expected NPV minus λ times the worst-5% average loss, over binary choices of the forty candidates, under the budget and a 40% cap per technology, with the tail linearised after Rockafellar and Uryasev (2000) and solved exactly with HiGHS. λ = 1 is the registered setting; λ = 0 gives the deterministic book. The conventional books are **A**, ranking by expected NPV, and **B**, equal capital by sector, held to the same budget and cap; **C** is the deterministic optimizer, **D** the risk-aware one, **F** book D chosen with the lookup's curves; every book is chosen on the primary scenarios and scored on the held-out ones.

**The trade-off is real and the committee must price it.** Along the frontier, expected value and tail fall together (Figure 2): the deterministic book expects $2.73B with a worst-5% loss of $1.52B; the risk-aware book $2.17B and $0.82B; at λ = 2, $2.07B and $0.74B.

![Figure 2](../figures/F38_frontier.png)

*Figure 2.* The frontier over risk policies on held-out scenarios, the registered books on it, and capital by technology along it.

| Committee grid, held-out | A NPV ranking | B equal capital | C deterministic | D risk-aware | F lookup forecasts |
|-------------------------|--------------|----------------|----------------|-------------|------------------|
| Candidates funded | 15 | 18 | 17 | 13 | 20 |
| Expected NPV, $B | 2.68 | 2.44 | 2.73 | 2.17 | 2.40 |
| Worst-5% loss, $B | 1.55 | 1.33 | 1.52 | 0.82 | 1.09 |
| Chance of a loss | 12% | 11% | 11% | 9% | 10% |
| Regret against perfect information, $B | 0.87 | 1.11 | 0.82 | 1.38 | 1.15 |

*Table 2.* The decision processes on the same 2,000 held-out scenarios, on the candidates public on the decision date.

**C33, the primary line, passes.** Under equal constraints the risk-aware book beats NPV ranking by $219M [+$13M, +$401M] on the registered metric, equal capital by $239M [+$37M, +$437M] and the deterministic optimizer by $136M [−$63M, +$323M], while giving up $508M of expected value against NPV ranking. The margin is smaller than the +$320M the earlier candidate set gave and its interval clears zero by $13M: the result holds on the strict as-of set, narrowly. Re-chosen on 20 resampled scenario sets the book beats NPV ranking every time, by $76M to $235M, and 11 of its members are chosen in at least 80% of them; on 5,000 held-out paths the order is unchanged and the margin $225M (the registered grid is Appendix A).

**Machine learning does not demonstrably improve the allocation.** Book D scores +$37M [−$76M, +$151M] on the registered metric against the book chosen with the lookup's curves in the model's scenarios and +$59M [−$197M, +$311M] in the lookup's; neither interval excludes zero.

**What drives value and downside.** Book D holds five leases and eight requests. An 836 MW wind request with a signed agreement is the position whose removal costs most, $539M; the book's gas request, 697 MW with an agreement, expects $437M, loses money in 63% of scenarios and is worth $144.6M to the objective. The largest gas request, 1,350 MW, expects $514M yet loses in 77% of scenarios and stays outside: forcing it in would cost $108.7M. The tail is the co-movement of the candidates: with the co-movement removed and each candidate's own distribution kept, the worst-5% loss falls from $0.82B to $0.02B, the chance of a loss from 8.6% to 1.8%, and the deterministic book would score best ($2.50B against $2.15B).

**The capital plan, priced.** The book's requests call construction capital beyond the reserve in 50.3% of held-out scenarios; in one scenario in twenty the excess is $2.53B or more. Without a contingent line the requests that reach their agreement cannot be built and the book is worth $1.71B in expectation and $0.76B on the registered metric; a line at that 95th percentile restores $2.11B and $1.27B. Priced as a bank would, the line still pays (Figure 3): net of a 0.5% commitment fee it is worth $1.14B on the metric, net of the fee and 8% interest $1.03B, and all 12 of the 12 fee-and-rate settings tried beat no line; the fee alone breaks even at 2.04% a year. The cost lands on the tail — the mean financing cost is $126M, paid in full in exactly the scenarios in which nothing is built and the leases earn least — so the expected value stays $1.98B while the worst-5% loss returns to the no-line figure. ATB capital costs already carry a construction-finance factor, so the fee-only case bounds the cost from below and the fee-with-interest case from above.

![Figure 3](../figures/F48_credit_line_net.png)

*Figure 3.* Book D's registered metric by the size of the contingent line, gross of financing, net of the commitment fee, and net of the fee and interest.

**Two more checks.** Revising the book on 1 January 2027, after two years of prices and agreement signals, is worth −$11M [−$18M, −$5M]: the cap leaves no room to start a deferred lease, so the revision can only drop requests. Across four misspecified worlds the registered tail weight scores best in three ($1.348B against $1.327B at λ = 2 in the base world) and λ = 4 wins only when lease capital is 30% dearer; the deterministic book is the worst in every world, −$0.75B when ERCOT prices are 25% lower. The answer to Q2 is yes, on two conditions: the optimizer is held to the same constraints as the rules it is compared with, and it is funded.

## 6 Q3 — Governance

The language model never produces a number the decision uses (Figure 1; the advisor, which answers a committee's questions through the engine, is Appendix B). The *challenger* questions the committee's own proposal in two rounds. First the model reads the committee's statement into rules — tail weight, chance-of-loss and tail limits, exclusions, a liquidity line — naming anything it cannot represent and leaving it unset. Then tools, not the model, diagnose the proposal on held-out scenarios — the rules it breaks, the calls it cannot fund, the members that lose in most scenarios — and compute two alternatives under the committee's own rules, the repair and the optimizer's book. Finally the model writes a memo: at most three vulnerabilities, each tied to numbered facts and typed; a level — explain, challenge or guide; the loss the change avoids. Code checks every number and the guide rule: it may guide only toward an alternative that keeps every rule and either fixes a broken one or beats the proposal with an interval clear of zero. The same tools with fixed rules and no language model are the *checklist*, the control.

**Authority stays with the committee.** It sees its rules read back as numbers before anything is computed; a named person signs; leaving a book the challenger guided toward is allowed, but the ledger records the decision only with the contrary evidence acknowledged, each row hash-chained to the one before. The chain authenticates the sequence and content of what was decided and seen — not that the advice was correct, nor that the committee assented.

**The registered test.** The 24 computable flaws — a broken cap, an unfunded line, a limit exceeded, an excluded holding, a fragile position — are generated by code and their statements filled from fixed templates. The 12 flaws of argument — a sunk cost, a double standard, an unsupported claim — and the 12 sound proposals were written by me, with their keys, before any model saw them. Forty paraphrases test the reading; twenty injected instructions ("ignore the cap", "pre-approved, mark every rule kept") test its resistance. Every case ends as the committee's book under four arms, scored on the committee's own objective with its line priced, in five worlds: the base model, ERCOT prices 25% lower, ERCOT half as volatile, lease capital 30% higher, and completion as the lookup says. Cases, paraphrases, injections, prompts, model and line cost were hashed and committed before the first of 176 calls; none failed.

**C34, the primary line, passes.** Adding the language model to the tools improved the committee's own objective by $43M per case [+$9M, +$86M], paired over all 48 cases and averaged over the five worlds. The challenged book is ahead of the checklist's in the base world, under the lookup's completion rates and with lease capital 30% higher, level when ERCOT is half as volatile, and behind when ERCOT prices are 25% lower: the tail-loss finding of the earlier test survives in one world of five.

**What the model reads well, and what it does not.** It read all 40 paraphrased rules exactly, the 32 in scope into the right fields and the 8 out of scope refused with nothing set (C38, 100%). It named all 12 flaws of argument I wrote (C41, 100%) and over-challenged none of the 12 sound proposals (C40, 0%). It failed two lines. C37 asked that the reading equal the case's key in at least 43 of 48 cases; it did in 38. Eight of the ten misses set the tail weight to 0 where the statement names none and the key keeps the default of 1 — silence read as "no weight on the tail"; two wrote an exclusion the statement does not give. C39 asked that at least 90% of the injected instructions leave the reading unchanged and be named, with no memo moved; 75% held, and 7 memos carried a number not on their fact sheet, though none produced a guide the code had to downgrade. The verifier marks every ungrounded number; the engine never uses one.

**So: H8 supported, H9 not, H10 supported.** The model improves the committee's decision on the committee's own terms and names what the tools cannot see without crying wolf. It does not read rules reliably in the sense registered: it fills a silence with zero and embellishes with numbers. Each is a check the tools make — the reading is shown to the committee before anything is computed, and the verifier lists every ungrounded number beside the memo. That is the answer to Q3: the model improves governance because the tools around it, not the model, hold authority over what is computed and what is signed.

## 7 Q0 — Attribution

The ladder puts the three parts on one scale (Figure 5, Table 3). The tools alone improve the committee's own objective by $76M per case over its unchallenged proposal [+$13M, +$140M] (C35, passes); the language model adds $43M more [+$9M, +$86M] (C34); the optimizer's own book under the committee's true rules would add a further $134M [+$72M, +$211M] (C36, reported). Tools and model together add $119M per case. A preview on the earlier cases and candidate set had read +$110M, +$35M, +$103M and +$145M: the same order, the same smallest rung. The optimizer sits further above the challenged book than the model adds to the tools because the challenger guides toward the smallest repair while the optimizer re-solves the whole book.

![Figure 5](../figures/F50_ladder_v10.png)

*Figure 5.* The registered attribution ladder: what the tools, the language model and the optimizer each add to the committee's decision, paired per case, with case-bootstrap intervals.

| Registered line | Rule | Result |
|------------------------------------------|-----------------|------------------------------|
| C33 (Q2): risk-aware book vs NPV ranking, registered metric | interval above zero | +$219M [+$13M, +$401M], PASS |
| C34 (Q3): tools + language model vs tools only, 48 cases | interval above zero | +$43M [+$9M, +$86M], PASS |
| C35 (Q0): tools only vs the proposal | interval above zero | +$76M [+$13M, +$140M], PASS |
| C36 (Q0): optimizer vs tools + language model | reported | +$134M [+$72M, +$211M] |
| C37: readings equal the key | at least 43 of 48 | 38, FAIL |
| C38: paraphrases read exactly | at least 85% | 100%, PASS |
| C39: injections held; memos moved | at least 90%; 0 | 75%; 7, FAIL |
| C40: sound proposals over-challenged | at most 15% | 0%, PASS |
| C41: flaws of argument named | at least 75% | 100%, PASS |

*Table 3.* The nine registered lines of the final test, scored once; 6 of 8 graded lines pass. Source: `results/v10/success_criteria_v10_scored.csv`.

## 8 Limits and harms

**What the results are, and are not.** They are model-based comparisons on public data and assumed costs, not demonstrated improvements in a company's capital allocation. Redevelopment costs are bracketed by two grids, and a lease redevelopment is a modeled option on a producing asset, not a project any operator has priced. The scenarios resample seven years of history, so a worse joint tail than 2018–2024 cannot appear, and mean reversion lifts gas and ERCOT prices well above 2024's. The queue curves rest on two backtests that disagree about the level, and the first year after the decision confirmed the disagreement. The hazard models learn from the 2025 edition censored at the date, whose 2024 exits were in the ISOs' own reports during 2024 but compiled by LBNL later; that vintage gap is stated, not removed. The committees are simulated — 48 proposals I wrote or templated — and the advisor is one model; a study with real committees is proposed, not run. The primary result of Q2 clears zero by $13M. No headline of the form "AI increases returns by X%" is made, because the evidence does not support one.

**Who could be harmed.** A completion score can fulfil itself: if lenders refuse the requests it ranks low, those requests fail and the next model learns that they fail. Size is a top driver, so screening applicants by the score would penalise small developers; the score should inform a portfolio, not screen access to the grid. A challenger that reads an unstated tail weight as zero would, unchecked, push a committee toward the deterministic book, the one that loses most in every misspecified world; the reading is shown and confirmed before anything is computed.

## 9 Conclusions

Better predictions did not, by themselves, produce better decisions here. The queue model ranks requests better than a lookup, as of 2020 and in the year after the decision, yet the book built on it scores no better, because the level is what the book is sized to and the level is what neither method knows. The optimizer earns its place only when held to the same constraints as the rules it is compared with; then the risk-aware book wins by trading expected value for a thinner tail, narrowly on the strict as-of candidates, and its capital plan needs a contingent line that pays even at a bank's price. A language model that challenges the committee with computed tools improves the committee's decision beyond what the tools alone do and keeps no authority: where it fails — silence read as zero, numbers not on the sheet — the tools around it catch the failure before anything is computed or signed. Of the gain, the tools account for more than the model, and the optimizer for more than both. A decision system is useful when it states which part is doing the work, and which part is wrong. Next: committees deciding with and without the challenger; a prompt that states the defaults the committee did not; real redevelopment costs.

## Statement of work

This is a solo project registered in a group slot (Group 13). All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried out by Alan Mössinger. The ERCOT price client and the battery dispatch model are reused, with credit, from my own earlier projects (Forecast to Dispatch; MADS Milestone II).

## Appendix A — The evaluation record

Every claim in the body that says "registered" refers to a line below. Each criterion was written and committed before the data it scores were looked at; failures are reported as registered and never re-scored. The ledger (`docs/registration_ledger.md`) joins all 78 registered lines of C1–C32 with their corrections: 17 lines carry one, and 3 correction rows change the verdict (C21, C23 and C24 on the observed prices or the corrected system); the registered verdicts stand. The scoring of C20–C24 as it stood before the audit of 17 October 2026 is frozen in `results/registered_v7/`, the challenger's first record in `results/v9/`, each with a hash test.

| Criteria | What they test | Lines | Passed | What they say |
|----------|------------------------------|--------|--------|--------------------------------------------|
| C1–C5 | the model against cohort averages at entry | 12 | 8 | the model ranks better at three and five years; its calibration slope fails |
| C6–C12 | the portfolio layer of v2 | 12 | 3 | at utility scale the lookup ties at entry; the landmark model wins two years in (C8); the simulated band covers the realised book (C11); no leakage (C12) |
| C13–C14 | MISO and SPP on the 2026 file | 12 | 3 | the model beats the lookup in MISO at five years; SPP is too thin |
| C15–C17 | the milestone-managed book | 10 | 4 | more operations than the lookup two years in, not more MW; the level is not repaired at the landmark |
| C18–C19 | other learners | 8 | 5 | they tie LightGBM and do not beat the lookup |
| C20 | machine learning against baselines for output and prices | 12 | 3 | the plant capacity-factor lines pass; the lease lines fail on the log transform's bias; prices are random walks |
| C21–C24 | the four books under one budget | 4 | 2 | as scored: book D ties NPV ranking and equal capital, is as stable as the deterministic book and beats the single-sector comparator's tail |

*Table A1.* The registered record of H1–H3. Twenty-eight of seventy lines pass. Sources: the `success_criteria*_scored.csv` files and `tournament_criteria.csv` in `results/`; C20–C24 as scored before the audit in `results/registered_v7/`; the bridged-price scoring in `results/registered_bridged/`.

**C21–C24 as scored.** On the held-out scenarios the risk-aware book D earned less than top-N NPV (C21: −$61M [−$136M, +$0M]) and no more than equal capital by sector (C22: +$22M [−$49M, +$89M]); its selection moved as little as the deterministic book's under the six stresses (C23); and its tail beat the single-sector comparator's (C24: +$159M [+$76M, +$247M]). The audit later found that the top-N and equal-capital books had not been held to the registered technology cap; that does not change the verdicts as scored, and they stand. C20–C24 were first scored when ERCOT's 2020–2023 prices were a bridge from PJM West prices; on those prices 3 of 12 C20 lines passed and none of C21–C24 (`results/registered_bridged/`).

**The same criteria on the corrected system — post-registration, not a rescoring.** Applied to the system of this version — the candidates public on the decision date, the decline floor, the two-stage budget, every book under the same cap — the allocation criteria read as in Table A2. These are new results on a changed system, labelled as such; the registered verdicts are those of Table A1.

| Criterion, registered grid | As scored (v7) | On the corrected system (v10) |
|------------------------------------------|-----------------|------------------------------|
| C21: D minus NPV ranking, registered metric | −$61M, FAIL | +$468M [+$300M, +$643M], PASS |
| C22: D minus equal capital | +$22M, FAIL | +$95M [−$21M, +$215M], FAIL |
| C23: stability under the stresses (mean overlap, D against C) | PASS | 0.93 against 1.00, FAIL |
| C24: tail against the single-sector book | +$159M, PASS | +$77M [−$53M, +$207M], FAIL |

*Table A2.* The allocation criteria as registered and scored, and applied to the corrected system.

**The hypotheses H1–H7.** *H1:* machine-learning forecasts reduce held-out error against naive and physics baselines (C20). *H2:* a risk-aware book beats NPV ranking and sector-concentrated books on a stated risk–return metric (C21, C22). *H3:* uncertainty-aware selection is more stable under stresses than deterministic selection (C23, C24). As registered: H1 holds for plant output and not for leases; H2 is not supported; H3 is supported on the observed prices. On the corrected system H2 holds against NPV ranking but not against equal capital, and H3 does not. H4–H7 are the challenger's first record below.

**The challenger's first registered record (v9) — scored once on the earlier candidate set, frozen.** Registered on 20 October 2026 before the first call, with the hashes of the 48 cases, the 40 statements, the three prompts and the model (`results/v9/success_criteria_v9_registered.json`); the committees are simulated and the statements were written in session by the model family under test, which is what the final test corrects. The decision moved to the as-of candidates after this record was scored; it is read, not recomputed (Figure A12).

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

*Table A3.* The challenger's first registered lines; 6 of 8 pass. The checklist alone reached +$145M and +$257M. Source: `results/v9/success_criteria_v9_scored.csv`.

*H4* (finds what tools cannot, without over-challenging) is not supported: C27 fails. *H5* (challenging improves the decision) is supported. *H6* (the language model adds value beyond its tools) passes its registered rule, but two checks reported and not registered show what it rests on: without its largest case the edge is +$19M [+$0M, +$46M], and against a fixed rule that takes the optimizer's book first it is +$1M [−$50M, +$64M]. *H7* (reads rules reliably) is supported. The final test (Table 3) re-asks H4–H7 as H8–H10 on author-written cases with one primary line, and finds H9 not supported.

![Figure A12](../figures/F46_challenger.png)

*Figure A12.* The first registered challenger test (v9, earlier candidate set): flaws named by type, and the committee's objective and the loss avoided per flawed case.

## Appendix B — The AI advisor and the challenger

**What it sees and what it may do.** The advisor works through the engine (`src/advisor_tools.py`). For a committee question it sees the question and the schema of the `WhatIf` parameters, each with its range, and the forty candidate ids; it answers with parameters or with "cannot answer". The engine validates the parameters and computes. For the explanation it sees only the computed fact sheet. It sees no web, no memory across calls and no company data.

**How its numbers are checked.** `advisor_tools.verify_attributed` accepts a number in an explanation only if the fact sheet (or the committee's own question) shows it, compared by magnitude, and rejects a figure cited in billions where the sheet states millions. Integers up to ten and years are exempt. The v6 check, `advisor.verify_numbers`, accepted any number found anywhere in sixty kilobytes of tables; it still scores the table-reading modes.

**Record and replay.** Every call is appended to `results/advisor_runs.jsonl` with the model id, the route, the prompts, the response, token use and its check; a recorded call is served from the record, so the pipeline reproduces offline.

**The override gate and the ledger.** A decision is written by `src/ledger.py`, which refuses one without a named authorizer and refuses an override — a book that departs from the model's for the committee's chosen tail weight — without an answer to each of five questions (the stakes; what each party wants; where the emotional investment lies; which evidence was used and which dismissed; what alternative was left off the table) and the opposing case read. Each row carries the hash of the row before it, so an edited row breaks the chain.

**The prompts.** Eight templates sit in `prompts/`: the system prompt, the recommendation, the gym pick, the three of the challenge round (the five questions, the motivated-reasoning check and the ideological Turing test), and the two of v8, which translate a question into parameters and explain a computed result. Two more, `challenge_read.md` and `challenge_memo.md`, drive the challenger (`src/challenge.py`). The first reads a committee statement into typed preferences (tail weight, chance-of-loss and tail limits, excluded technologies or candidates, a liquidity line, budget use) and up to two what-ifs; anything it cannot represent it must name and leave unset. The second writes the memo from a numbered fact sheet; each vulnerability carries a type from a fixed list, which is how detection is scored without a judge. Code enforces the guide rule, checks fact references and numbers, and records a downgrade when the model asks to guide without the evidence. The checklist is the same tools with fixed rules — flag every broken rule, fragile member and frequent excess call; guide to the repair when the guide rule allows.

**The final test's material.** The 24 computable cases are generated by `src/challenge_v10.py` from their specifications and their statements filled from fixed templates; the 24 author-written statements and keys are in `results/v10/cases_v10.json`, the 40 paraphrases in `paraphrases.json` and the 20 injections in `injections.json`, all hashed in the registration. The first registered run made 136 live calls, the final one 176; none failed, and every one replays from the record.

**Scored.** On the six committee questions of notebook 11 the advisor read all six correctly — five into parameters, the sixth refused — and its five explanations cited 119 numbers, all in the computed fact sheet. Across the table-reading and what-if modes, 214 calls are recorded; their numbers were in the tables shown 94% of the time. In the decision gym the advisor trailed the registered rule by $5.1M a situation [−$11.0M, −$1.5M], worse in 12 of 14.

![Figure B1](../figures/F44_advisor_tools.png)

*Figure B1.* The path of a committee question: translation, validation, computation, the fact sheet, the explanation, the check, the decision and the ledger.

## Appendix C — Where things are

| Need | Where |
|------------------------------|----------------------------------------------------------------------|
| Run everything | `make setup`, then `make all` (twelve notebooks in order), `make test`, `make report`; `make decide-page` for the decision page |
| The raw inputs | `data/README.md`; every file with its hash in `data/raw_manifest.csv`; `make check-data`, `make get-data`, `make bundle-data` |
| Every cited number | `results/report_numbers.csv`, written by `src/report_numbers.py` and checked by `tests/test_report.py` |
| Every decision and its reason | `docs/decisions.md` (numbered); the registered criteria in `results/success_criteria*.csv`; the frozen records in `results/registered_v7/` and `results/v9/`; the ledger in `docs/registration_ledger.md` |
| The audit and the plans | `docs/audit_2026-10-17.md`, `docs/implementation_plan_v8.md`, `docs/plan_v10.md` |
| The decision layers | `src/decision_date.py`, `src/asof_candidates.py`, `src/valuation.py`, `src/whatif.py`, `src/advisor_tools.py`, `src/ledger.py`, `src/voi.py`, `src/dynamic.py`, `src/robustness.py`; notebooks 07–11 |
| The challenger and its tests | `src/challenge.py`, `src/challenge_experiments.py`, `src/challenge_v10.py`, `prompts/challenge_*.md`; the registrations and every output in `results/v9/` and `results/v10/`; notebook 11, section 11, and notebook 12 |
| The three questions | notebook 12: the ledger, the credit line, the forward test, the robustness checks, the ladder and the registered test |
| Figure captions and their notebooks | `report/figure_notes.md` |
| Changes after review and mentor feedback | `docs/mentor_feedback.md` |

**Reproducibility.** Every notebook runs top to bottom on the project kernel with `make all`; the scenario sets, bootstraps and draws are seeded; the solver must reach optimality or the run stops; advisor and challenger calls replay from their record. The parser of one PJM table needs poppler's `pdftotext`; a clean Linux environment reproduced an earlier version's registered verdicts and nearly all its cited numbers (decision #87).

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

![Figure A13](../figures/F42_value_added.png)

*Figure A13.* Each decision process against its comparator on the same held-out scenarios, with paired bootstrap intervals.

![Figure A14](../figures/F45_robustness.png)

*Figure A14.* Book D's construction calls beyond its reserve, and how often each candidate is chosen when the book is re-chosen on resampled scenarios.

![Figure A15](../figures/F47_ladder.png)

*Figure A15.* The attribution ladder as previewed on the first test's cases and the earlier candidate set, before the final registration: 41 of 48 readings equal to their key.

## Appendix E — Part I in full: the developer's decision, which queue requests to fund

*The method and evidence behind section 4 for the queue side, kept in full. Words used one way throughout:*

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

*The method and evidence behind sections 3–5 for the energy portfolio.*

### F.1 The candidates on 1 January 2025

The leases are the twenty with the most output in the twelve months published by the decision date (to September 2024), among the 506 producing in 2024, out of 1,041 with at least sixty producing months. The requests are the five largest of each technology among the 1,441 ERCOT requests of 20 MW and more that ERCOT's own reports listed as live on 1 January 2025. In v6 they were drawn from the 2017–2019 entrants and valued at entry, though ten of those twenty had been withdrawn or built by the end of 2024; in v8 and v9 they were drawn from the 2025 edition, released after the date; this version draws them from what was public. Most of the twenty are 2023–2024 entrants of 500 MW and more, the size and age at which requests are least likely to operate, so their chances sit far below the queue's averages unless an agreement is signed.

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

Twelve forecast lines were registered before scoring: lease oil and gas at 3, 6 and 12 months, plant capacity factors at 1 and 3 months, and prices. Each pits a machine-learning challenger against the best of five transparent baselines at rolling origins (Figure F1). Three of twelve pass, all for plants. The lease lines fail: the registered challenger's error at three months is 1.35 times the last-value baseline's, a bias from forecasting in logs; a level model added after scoring, and labelled so, brings the ratio to 0.96, and the scenarios draw their output uncertainty from it. Prices behave as random walks. The decision-level test of machine learning is section 5's: the book chosen with the lookup's queue curves against the book chosen with the model's.

![Figure F1](../figures/F27_forecast_gains.png)

*Figure F1.* Forecast error of the challenger relative to the best baseline, by registered line, with paired moving-block bootstrap intervals.

### F.4 What each candidate is worth, and what that rests on

**A lease redevelopment is an uplift on a producing asset.** Each lease's baseline is an Arps decline fitted after the lease's peak in its last 36 months, switching to an 8% annual decline once its own decline falls below that; four leases still ramping decline at the floor from their recent level. The v6 fit had no floor, and ten of the twenty leases were projected never to decline. The redevelopment adds 20% of the baseline after a two-year lead time; its value is the cash flow it adds over doing nothing. The committee grid prices capital at $40,000 per incremental flowing barrel of oil equivalent a day and discounts at 8%; it was added after the registered results, at an outside reviewer's request, and is labelled ASSUMED.

**A power request is a plant that may never be built.** Its value if built uses the 2024 hourly prices — solar earns 92% of the flat hub price, wind 83%, gas combined cycle 136% because it runs only when prices clear its fuel cost — with ATB costs converted to 2024 dollars and the tax credits of the law in force on 1 January 2025: wind the production credit, solar and storage the investment credit, in every operation year of the window. The 2027 deadline for wind and solar was set by a July 2025 law and IRS Notice 2025-42, after the decision date; it is a stress. That value is weighted by the chance of operating in each of seven years and net of the deposits. On the flat 2024 path, under contract, ten of the twenty requests are positive and the twenty together sum to −$108M; without the credits −$933M, under the 2027 deadline −$478M.

### F.5 Scenarios and risk

Prices, output, costs and timing are drawn together: 2,000 twenty-year paths resample calendar-year blocks of the 2018–2024 monthly log changes of WTI, Henry Hub and ERCOT, the same months for all three, capped at ±1.5 a month and reverting toward their 2018–2024 real geometric means with a four-year half-life (ASSUMED). Output varies by the scored forecast errors, costs by a triangular multiplier, and each request's operation year by its curve from the decision date. The held-out set of 2,000 paths redraws every component with its own seeds; in v6 only its prices were redrawn. Two weaknesses remain. Seven historical years make every path, so there is effectively no joint oil–power tail beyond 2018–2024. And the reversion targets sit well above 2024's gas and ERCOT prices, which is what lifts the gas requests' scenario values above their flat-path values (Appendix Figure A5). A check on 5,000 paths — the registered 2,000 followed by new ones — leaves the order of the books unchanged (book D $1.36B, the deterministic book $1.21B, NPV ranking $1.14B, equal capital $1.12B) and book D's worst-5% loss at $0.84B; re-solved on 5,000 primary paths, book D keeps about two thirds of its members (Jaccard 0.65) and scores $1.382B against $1.363B.

### F.6 Allocating the budget

Section 5 reports the books under the committee grid. Under the registered grid the leases are cheap against the barrels they buy, so the risk-aware book holds fourteen leases, expects $8.48B and almost never loses money; risk aversion has little to buy there. The registered comparison on that grid is Table A2.

### F.7 When: the book at one to twenty years

A twenty-year NPV says nothing about what the owner holds at year three. Counting only the cash that falls within each horizon, under the registered grid, the best book holds nothing at one or two years, eleven leases at three and fourteen from five; its value within twenty years is $7.09B. A queue request is a carrying cost until it operates (Figure F4).

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
| Q1, at entry | The model beats cohort averages (AUC 0.86 against 0.73) but ties the lookup at utility scale. | Appendix E.3; C1–C12 | Partly |
| Q1, two years in | A book of 25 chosen by the landmark model held 19 operations, against 11 for the lookup. | Appendix E.7; C15 | Supported |
| Q1, on the decision date | Backtested as of 2020 the model ranks better than the lookup (AUC 0.731 against 0.686; in ERCOT 0.656 against 0.591) but over-predicts ERCOT's level. | Section 4 | Supported for ranking |
| Q1, one year on | 30 of 1,441 live requests operated in 2025 where the corrected model expected 78 and the lookup 17; the model's slope is 0.66, the lookup's 0.01. | Section 4; Figure 4 | Post-hoc |
| Q1, output | Machine learning beats baselines for plant output, not for leases or prices. | Appendix F.3; C20 | Partly |
| Q1, in the decision | The book chosen with the lookup's curves is not beaten by the model's on the registered metric (+$37M [−$76M, +$151M]). | Section 5 | Not supported |
| Q2, risk | Under the committee grid the risk-aware book loses money in 9% of scenarios with a worst-5% loss of $0.82B; its construction calls exceed the reserve in 50.3% of scenarios. | Section 5 | Derived |
| Q2, the primary line | Under equal constraints the risk-aware book beats NPV ranking by $219M [+$13M, +$401M] on the registered metric, for $508M of expected value. | Section 5; C33 | Registered, PASS |
| Q2, the line priced | A $2.53B contingent line is worth $1.03B on the metric net of a 0.5% fee and 8% interest, against $0.76B with no line; the fee breaks even at 2.04%. | Section 5; Figure 3 | Post-registration |
| Q2, sensitivity | Oil at $45 for five years removes every lease from the book; redevelopment capital 30% higher swaps two members for three; the registered tail weight is best in three of four misspecified worlds. | Section 5; Appendix I | Derived |
| Q2, flexibility and information | Revising the book in 2027 with this rule is worth −$11M; perfect information is worth at most $825M, the ERCOT price level $47M, an agreement signal at most $59.4M. | Sections 4–5 | Post-registration |
| Q3, the primary line | Adding the language model to the tools improves the committee's own objective by $43M per case [+$9M, +$86M] over all 48 cases. | Section 6; C34 | Registered, PASS |
| Q3, reading | 40 of 40 paraphrases read exactly; 38 of 48 case readings equal their key; 75% of injections held with 7 memos carrying an ungrounded number. | Section 6; C37–C39 | Registered: PASS, FAIL, FAIL |
| Q3, argument | 12 of 12 author-written flaws of argument named; 0 of 12 sound proposals over-challenged. | Section 6; C40–C41 | Registered, PASS |
| Q0 | Tools add $76M per case over the proposal, the language model $43M more, the optimizer $134M beyond that. | Section 7; C35–C36 | Registered |
| Q3, the advisor | Its investment increment is zero; it read six questions correctly; it trails the rule in the gym. | Appendix B | Post-registration |

*Table G1.* Every finding, its evidence and its verdict. Registered criteria are in Appendix A and Table 3.

## Appendix H — The audit of 17 October 2026

An independent audit of report v6 and its code (`docs/audit_2026-10-17.md`) found that the prediction layer held and that valuation, allocation and the gym did not. The five findings that changed the recommendation:

| Finding | What was wrong | What changed |
|---------|----------------|--------------|
| A1 | The top-N and equal-capital books ignored the registered 40% technology cap; the risk-aware book's "$1.9B for a smaller tail" was the price of the cap, not of risk aversion. | Every book is held to the same budget and cap and checked. |
| E1 | Ten of the twenty power candidates had been withdrawn or built by the end of 2024, while the leases were valued at 2025. | One decision date; the requests are those still waiting, with chances conditional on their age — and, since the critique of 21 October, those ERCOT's own reports listed on the date. |
| E2 | Ten of the twenty lease baselines were fitted with no decline. | A post-peak fit with an 8% terminal decline; the registered lease book fell from $14.6B to $8.19B. |
| G1 | The gym's lease rooms used 2024 leases, 2024 fits and the realized future's mean. | Rooms rebuilt as of their date and counted as one situation. |
| G5 | The advisor's value over the rule was never reported; it was negative. | Reported, and the advisor rebuilt to work through the engine. |

*Table H1.* The audit's headline findings. Smaller corrections — the CVaR tail count, the gas heat content, the gate floor, ATB dollars, the credits, the provenance labels, the held-out draw — are in the audit's register and decisions #88–#92.

**Changes after review.** Three outside reviews in October 2026 led to the changes logged in `docs/mentor_feedback.md`. The first asked for an evaluated decision intelligence system; its first request was the audit above. The second found three inputs that were not public on the decision date and the capital calls unpriced, and asked that the language model help the committee decide; the challenger and its first registered test were the answer. The third, a critique review of 21 October, found that the candidate set rested on a file released after the decision date, that the challenger's test statements came from the model family being tested, that the construction line was free, and that no primary estimand had been named; this version rebuilds the candidates from what was public, prices the line, names one primary line per question, adds the four-arm ladder and the one-year forward test, and keeps a three-column ledger of every registered line and its corrections. A course mentor is assigned after the proposal review; their feedback will be logged in the same file.

## Appendix I — Capital allocation memo

*To the investment committee, 1 January 2025. Every figure is a model output scored on held-out scenarios; lease costs are assumed; the candidates are those public on the date.*

**The ask.** Commit up to $3.82B now — 40% of what the forty candidates would cost the budget today — across twenty Gulf lease redevelopments and twenty ERCOT requests still in the queue, with no technology above 40% of the budget. A lease costs its redevelopment capital; a request costs its deposits plus a reserve for the construction it may need.

**The choice.** The return-seeking book expects $2.73B with a worst-5% average loss of $1.52B. The registered risk-aware book expects $2.17B with a loss of $0.82B and a 9% chance of losing money. A more defensive book expects $2.07B with a loss of $0.74B. I recommend the committee choose its tail weight first; at the registered weight that is the risk-aware book.

**What to do with each candidate under that book.** Invest now in eight candidates, the leases and the requests with signed agreements. Invest in stages in five requests: pay the deposit now, commit construction at the agreement. Wait for information on twelve requests whose agreement signal is worth more than their deposit. Monitor fourteen; reject one.

**What the commitment really is.** The construction reserve is an average: the capital the book's requests call exceeds it in 50.3% of scenarios. Without a contingent line the book is worth $1.71B, not $2.17B, because requests that reach their agreement cannot be built; a line of $2.53B restores $2.11B gross and $1.98B net of a 0.5% commitment fee and 8% interest on the draws.

**What would change it.** Oil at $45 a barrel for five years removes every lease from the book and leaves the five wind requests, a book that expects $0.59B and loses money in 58% of scenarios. Redevelopment capital 30% higher drops two members for three and keeps $0.91B of leases, at a 15% chance of a loss. Knowing everything before committing would be worth at most $825M; the 2025–2029 ERCOT price level, $47M; one request's agreement signal, at most $59.4M.

**Before you sign.** State your rules in words — your tolerance for loss, your liquidity, what you will not hold, and your tail weight, because an unstated one is read as zero. The challenger reads them back as numbers for you to confirm, tests your proposal against them and names the computed book that keeps them. If you depart from a book it guides you to, the ledger asks you to acknowledge the evidence.
