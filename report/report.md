---
title: "From Queue to Capital: AI-Driven Portfolio Management for the U.S. Power-Plant Pipeline"
author: "Alan Mössinger"
date: "SIADS 699 Capstone, University of Michigan — Group 13 — October 2026"
---

## Abstract

An energy company that holds interconnection-queue requests must decide, request by request, whether to invest, hold or exit, and where to add. This report answers those questions with the public record of 13,366 requests in CAISO, ERCOT and PJM, tested on the 2,268 that entered in 2017–2019. Which requests get built is predictable: a gradient-boosted hazard model ranks the test cohort at an AUC of 0.858 at three years against 0.733 for cohort averages, and two years in the executed interconnection agreement lifts Uno's C from 0.687 to 0.797. Why they fail is legible: size, technology and the agreement set the odds (PJM falls from 24% five-year completion under 5 MW to 4% at 500 MW and up; an agreement signed within two years lifts ERCOT from 0.8% to 63%), and the regions run on different clocks (CAISO and PJM cull in year one, ERCOT after year four). What a plant is worth, once capital is counted, is a short list: at merchant prices only wind everywhere and gas or solar in PJM earn their capital back, and only before the 2027 credit deadline. The portfolio rules built on those three layers were scored on what happened: 51% of the requests the two-year gate says to fund reached operation within three years against 10% of those it says to drop, and a book of 25 chosen two years in by the model held 19 requests that reached operation against 11 for an agreement-aware lookup. The conclusion is a set of decisions, each with its probability, value, cost and downside: enter by the cells and rules, review at two years in CAISO and PJM and at the agreement in ERCOT, fund wind anywhere and PJM gas and solar before 2027, and size every book to the newest cohort's level, which runs at a quarter of the historical rate.

## 1 The decision

At the end of 2024 the U.S. interconnection queues held more generation and storage capacity than the installed fleet, and of the capacity that asked to connect in 2000–2019, 12.6% was operating and 76.9% had withdrawn (Rand et al., 2025). A request enters a queue with a size, a technology and a place; it leaves, usually years later, as an operating plant or a withdrawal. An energy company that develops plants holds a book of such requests, and every request costs money to keep: a deposit, a study, then a larger deposit and a longer study.

The company asks five questions, and this report is organised around them. Where is the opportunity: which regions, states and technologies? Which requests get built, and when? Why do requests fail, and at which stage? What is a plant worth once it is built, and what does it cost to find out? And, given all that, which requests should it fund, hold or exit, and how much should it add, where? Each section ends in a rule the company can apply, with the number, the interval and the evidence behind it. The data science is the evidence layer: survival models under competing risks, a pre-registered evaluation on a held-out cohort, interpretable rules, an unsupervised map of the market, a project cash-flow model and a scenario simulation of the book. The rules are thin arithmetic on top of those outputs, and they are scored on what actually happened to the 2017–2019 requests.

## 2 Data

The population is the project-level file of Lawrence Berkeley National Laboratory's *Queued Up* series, 2025 edition (Rand et al., 2025; 36,441 requests through the end of 2024), with the 2026 edition (Rand et al., 2026) used alongside it for the 2025 outcomes of requests active at end-2024, the earliest outcomes of the 2020–2022 entrants, and the MISO and SPP event dates. Operation and withdrawal dates are near-complete only in CAISO, ERCOT and PJM, so the timing models cover those three: 13,366 requests, of which 1,730 operated, 7,064 withdrew and 4,572 were still waiting at the censor date, 31 December 2024. Models are fitted on entrants to 2016 and tested on the 2,268 entrants of 2017–2019, every one followed for at least five years. The two editions together date an executed interconnection agreement for 1,818 of these requests (30% of ERCOT's, 15% of CAISO's and 2.6% of PJM's inside the queue time). Value and cost come from public files: EIA's hub prices, the PJM market monitor's capacity revenues and accreditation ratings, EIA generation and nameplate for capacity factors, LBNL's PJM interconnection cost estimates, and the NREL Annual Technology Baseline 2024 for capital and operating cost per kW. Every value input that is not parsed from a file is an assumption listed with its range in `results/value_assumptions.csv`. Nine numbered cleaning rules, the data dictionary and the access statement are in the repository. Figure 1 places the queue and the operating fleet on the map.

![Figure 1](../figures/F9_project_map.png)

*Figure 1.* Requests waiting in U.S. queues at end-2024 by county (left; area ∝ MW; the three timing ISOs in colour) and the operating fleet from EIA-860M (right). 91% of requests have a county code.

## 3 Where is the opportunity

Before the company looks at a request it looks at a market. Seven features that exist in the public files describe each state's queue: the waiting MW relative to the operating fleet, the shares of that MW that are solar, storage and gas, the median size of a waiting request, the share that entered since 2022, and the share of 2010–2018 entrants that reached operation. Standardised and clustered with k-means, the 47 states with 30 or more resolved entrants sort into four archetypes (Figure 2); the structure is soft (a silhouette near 0.20 at every k), but the clusters separate an outcome they were never given, the share of 2017–2019 entrants operating by the end of 2024, from 5.5% to 19.7%. The best market is a light, settled queue with a mixed technology list, the PJM core and Florida (19.7% of 2017–2019 entrants operating; the queue is 0.8 times the fleet). The crowded, hot, storage-heavy queues of twenty states from New England to Texas and the mountain west run at 11.5%; the storage-dominated Southwest, where the queue is 3.5 times the fleet and 80% of it is storage or hybrids, at 7.0%; and the light, hot, gas-leaning queues of the Southeast and plains at 5.5%, most of them outside the three ISOs whose outcomes the file dates.

![Figure 2](../figures/F25_state_archetypes.png)

*Figure 2.* State archetypes from k-means on seven market features, mapped, and the share of 2017–2019 entrants operating by end-2024 in each archetype with Wilson intervals; hatched states have fewer than 30 resolved entrants.

The base rates are the first screen. Five years after the request, 18.4% of ERCOT's entrants are operating, 13.2% of PJM's and 4.8% of CAISO's; withdrawals take 27.4%, 61.2% and 66.5%. Within regions, gas builds most often (31.9% in PJM, 26.9% in ERCOT) and storage least (no region above 3.4% for batteries or solar-plus-storage). The constraint behind the rates is the queue itself: Figure 3 shows the GW waiting at entry rising many-fold in PJM since 2010, and since 2018 the entrants neither leave nor get built at the historical pace, which is the level problem of section 4.

![Figure 3](../figures/F16_constraint_map.png)

*Figure 3.* The constraint map: requests, GW waiting at entry, three-year withdrawal and operation shares by region and entry year, with the median years to an executed agreement where it is dated.

**The rule.** Look first where the base rate is highest and the agreement is dated, which is ERCOT; look at PJM for gas and for the capacity market; treat CAISO as a market where entry odds are a twentieth of ERCOT's and only a signed agreement changes them.

## 4 Which requests get built, and when

**How the models were built and judged.** Three families were fitted to the 2000–2016 entrants and never retuned: cause-specific Cox models, multinomial discrete-time hazard models (a ridge logit and a LightGBM) that treat operation and withdrawal as competing exits, and the Aalen–Johansen cohort averages a planner would use without a model. Criteria were written before scoring (C1–C5 for the first round, C6–C12 for the portfolio layer, C13–C14 for the MISO and SPP extension, C15–C17 for the milestone-managed book, C18–C19 for the tournament of other learners) and are reported as registered in section 9. Censoring is handled with inverse-probability weights; every interval is a paired bootstrap of 200 resamples.

**Ranking and lift (Table 1).** On the test cohort the discrete-time LightGBM ranks requests at a time-dependent AUC of 0.858 at three years and 0.766 at five, against 0.733 and 0.725 for the region × technology averages; its top decile reached operation within five years 39.7% of the time, a lift of 3.96 (C1, C2 and C4 pass at three and five years). At seven years the gain is inside the noise. For requests of 20 MW and more, a careful analyst's lookup by region × technology × size ranks as well as the model (Uno's C 0.783 against 0.779 at three years; the model wins 0 of 6 comparisons), so at entry the model earns nothing over a lookup at utility scale. Three further learners, a random survival forest pair, a neural discrete-time hazard and a blend of five, were selected on the 2016 cohort and scored once under criteria C18–C19 registered first (Figure 4): the forest and the network alone rank worse than LightGBM (Uno's C 0.66 and 0.68 against 0.76 at five years), the blend ties it (C18 fails on the five-year line, +0.015 [+0.002, +0.028] at three years but −0.007 [−0.020, +0.005] at five) and does not beat the lookup at utility scale (C19 fails). The cheaper models stay: the ceiling at entry is set by what the file records about a request, not by the learner.

| Test cohort 2017–2019 | Cohort averages | Fair lookup (≥ 20 MW) | LightGBM | LightGBM (≥ 20 MW) |
|---|---|---|---|---|
| AUC, 3 years | 0.733 | — | 0.858 | — |
| AUC, 5 years | 0.725 | — | 0.766 | — |
| Uno's C, 3 years, ≥ 20 MW | — | 0.783 | — | 0.779 |
| Uno's C, 5 years, ≥ 20 MW | — | 0.752 | — | 0.734 |
| Top-decile lift, 5 years | 3.35 | — | 3.96 | — |

*Table 1.* Ranking at entry: the model against cohort averages (all sizes) and against the fair lookup (20 MW and more). Sources: `results/metrics.csv`, `results/metrics_v2.csv`.

![Figure 4](../figures/F22_tournament.png)

*Figure 4.* The chosen alternative learner (a blend of the main logit, Cox, LightGBM, a random survival forest pair and a neural discrete-time hazard) against the registered LightGBM and the fair lookup: paired differences in Uno's C and Brier score by horizon, with 95% bootstrap intervals; criteria C18–C19 registered before scoring.

**The level, and when.** Every model is calibrated to a level that fell: for requests of 20 MW and more, five-year completion was 11.0% for the 2017 entrants and 5.9% for 2018, while the model predicted 12.3% and 11.8% (Figure 5); a rolling intercept fitted on the newest completed cohort removes about 40% of the error and none of the post-2020 gap, where the 2020–2022 entrants operate within two years at 1.1%, 0.3% and 0.7% (2026 edition), about a quarter of the predicted rate. On *when*: among the 297 test requests that operated within seven years, the model's expected year of operation is within a year of the truth 52% of the time (mean error 1.19 years) against 33% for a historical median by region; the gain is PJM's (1.07 against 1.88 years), and in ERCOT the historical median of 3.3 years does as well.

![Figure 5](../figures/F11_level_by_entry_year.png)

*Figure 5.* Five-year completion observed and predicted by entry year, 20 MW and more: the level fell by nearly half between the 2017 and 2018 cohorts while the model held near 12%.

**Two years in.** For a request still in the queue two years after entry, the dated agreement changes everything the model can do (Figure 6): the landmark model with the agreement flag ranks the next three years at Uno's C 0.797 against 0.687 for the entry model (+0.111 [+0.076, +0.146]) while the lookup conditional on the landmark falls to 0.591; in ERCOT, requests with an agreement known at the landmark operated at 55.7% within three years against 4.9% without (115 and 246 requests).

![Figure 6](../figures/F12_landmark_models.png)

*Figure 6.* Uno's C and Brier score three years after each landmark (entry, +1, +2 years, the agreement date) for the entry model, the updated models and the fair baseline.

**The rule.** At entry, rank by the lookup cell and the segment rules of section 5; the model adds nothing at utility scale. Two years in, re-score every held request with the landmark model and the agreement. Plan the clock with the model in PJM and with the historical median in ERCOT. And size every book to the newest cohort's level, not the model's: the 2017–2019 cohort was expected to bring 29.2 GW online within five years (25.2 GW after the level repair) and brought 18.8 GW.

## 5 Why requests fail

**Six drivers on one cohort (Figure 7).** On the 5,497 entrants of 2010–2019, every one of which has five years of follow-up, five-year completion runs 12.8% overall and is decided by four things. Size: PJM falls from 24% under 5 MW to 4% at 200 MW and more, CAISO from 14% to about 1%; ERCOT is flat at 19–23% up to 500 MW and 11% beyond. Technology: gas 32% in PJM and 25% in ERCOT, solar 9% and 13%, batteries 4–7% everywhere, solar-plus-storage below stand-alone solar (0.5% against 4% in CAISO), and none of PJM's 37 offshore wind requests within five years. The regional queue at entry and crowding in the same county matter in PJM only (22% in its quietest fifth of entry dates against 10% in the most crowded; 19% with no earlier request in the county against 10% with eleven or more) and are partly the slowdown of later cohorts. Service type barely moves the raw rate (PJM 14% NRIS against 13% ERIS). And the agreement: where the 2025 file dates an executed agreement within two years of the request, 63% of ERCOT's 218 such requests were operating within five years; where none is dated, 0.8% of 484.

![Figure 7](../figures/F19_drivers.png)

*Figure 7.* Five-year completion by six drivers within each region, 2010–2019 entrants, 95% Wilson intervals.

**Where and when they die (Figure 8).** CAISO and PJM cull early: 48% of CAISO's requests still waiting at the start of year one leave during it and 31% of the survivors in year two; in PJM 31% and 21%. ERCOT culls late: 7% leave in year one and the withdrawal hazard climbs to 16–20% in years five to seven. 82% of CAISO's withdrawals and 42% of PJM's come out of the system impact study (a further 27% of PJM's out of the feasibility study) at a median 0.6–1.9 years; ERCOT's come out of the facilities study (87%) at a median 3.4 years, 13% of them after an executed agreement. Surviving two years roughly triples the odds of operating within the next three: 7% to 21% in ERCOT, 9% to 16% in PJM, 1% to 10% in CAISO.

![Figure 8](../figures/F20_when_requests_die.png)

*Figure 8.* Annual withdrawal and operation hazards by year in the queue, the study stage reached at withdrawal, and the share operating within the next three years after surviving s years, by region.

**The same drivers with time and both exits modelled (Figure 9).** The cause-specific Cox model puts ERCOT's operation hazard at 1.66 times PJM's and CAISO's at 0.52; gas at 2.56 times solar; requests of 500 MW and more at 0.31 times those of 20–100 MW; energy-only service at 0.70 after size and technology are held fixed.

![Figure 9](../figures/F6_hazard_ratios.png)

*Figure 9.* Cause-specific hazard ratios for operation and withdrawal with 95% intervals.

**Ten rules a company applies by hand (Figure 10).** A depth-four tree on the entry attributes, fitted on the 2010–2016 entrants and re-measured on 2017–2019, gives ten rules whose rates span 1% to 47% and whose order holds out of time (Spearman 0.77). Gas of 66 MW or less outside CAISO: 47% in the fitting cohort, 48% later. ERCOT's larger non-solar requests: 28% then 23%. CAISO above 25 MW in a county with six or more earlier requests: 0.4% then 1.4%. Utility-scale solar outside CAISO in a county with earlier requests, the largest segment with 871 test requests: 7% then 6%. The one rule that broke, solar outside CAISO with no earlier request in its county (19% then 6%), says that county crowding measured at entry is a weaker guide than size and technology.

![Figure 10](../figures/F21_segments.png)

*Figure 10.* Five-year completion by the ten leaves of the tree, fitting cohort (2010–2016) and later cohort (2017–2019) with Wilson intervals.

**The rule.** Screen at entry by the segments: enter the top two, enter the middle ones only with the two-year review scheduled, and do not enter the bottom three on entry information alone. Review in year two in CAISO and PJM, when the cull is over; review at the agreement in ERCOT, where survival alone says little.

## 6 What a project is worth

Once capital is counted the value index of the earlier work becomes a short list (Figure 11). For a plant entering operation in 2024, with today's credits, a 20-year life and an 8% real discount rate, only five of the 21 technology-region pairs have a positive base-case NPV per MW: wind in PJM ($1.18 million per MW), ERCOT ($0.34M) and CAISO ($0.09M), gas in PJM ($0.22M) and solar in PJM ($0.03M). Storage, hybrids and offshore wind are negative in every region, and so is everything in ERCOT and CAISO except wind. After the 2027 credit deadline only PJM wind ($0.55M) and PJM gas ($0.36M) stay positive. The ranges are wide: PJM gas runs from −$0.9M to +$2.1M with the capacity and gas-price cases.

![Figure 11](../figures/F26_npv_per_mw.png)

*Figure 11.* NPV per MW at operation by technology and region for a plant entering operation in 2024 (credits apply) and 2028 (after the deadline); revenue from the value table with new-build capacity factors, capital and O&M from NREL ATB 2024, low and high value cases as lines.

The break-even flat price says the same in the unit a company negotiates in: a new solar plant needs $57/MWh over twenty years to earn 8% on its capital, wind $51, a combined cycle $80 at $3.50 gas, a hybrid $97; the on-peak price the table captures is $30–40/MWh for solar and $57–68 for wind. The gap is what a power purchase agreement, renewable energy certificates or a capacity contract must close, and none of those is in the public files. Probability-weighted and discounted to the day of the request, the median test request has an expected NPV of −$0.3 million; only 42% of PJM's, 22% of ERCOT's and 7% of CAISO's requests would have a positive NPV per MW if built in their third year; wind is the exception, with a median expected NPV of about $14 million in ERCOT and PJM. The cost of finding out is small next to these numbers: the deposit and study to the next gate are $8,169 per MW at 20–100 MW and $841 per MW at 500 MW and more, plus $150,000 of studies.

**The rule.** At merchant prices, develop wind anywhere and gas or solar in PJM, and only if the plant can be operating by 2027. Develop the rest only with a contract above the break-even price. The NPV is the simplest form of a project DCF (no financing, tax depreciation, degradation or terminal value, and no energy revenue for storage), enough to rank and to put a sign on a request, not to price one.

## 7 The portfolio review: fund, hold or exit

The three layers above combine into one rule applied at two gates. At entry (G1) the company pays the first deposit and study; two years in (G2) it funds the next study or stops. At each gate the inputs are the probability of operating from there, the expected NPV if it does, the cost of the next gate and a hurdle *h* on the margin: **commit** when the probability is at least the pool's own outcome rate and the base-case margin is at least *h* times the cost; **exit** when the probability is well below the pool or the margin is negative even in the high value case at the low cost; **hold** otherwise, which at entry means entering with the two-year review scheduled and at two years means a request worth more to a buyer with a different hurdle than to this book. At entry the probability is the lookup cell and the segment rate, because C19 was not met; two years in it is the landmark model with the agreement flag. The rule was scored on what happened (Figure 12).

**At entry.** With a hurdle of 3 the rule sorts the 2,268 test requests into 101 to invest in, 699 to enter with the review scheduled and 1,468 to leave alone. 25% of the invest class reached operation within five years [17%, 34%], 14% of the hold class and 7% of the exit class, against 10% for the cohort. Valued at merchant NPV with capital counted, the invest class returned +$1,448 million on 23,621 MW of requests; the exit class would have lost $8,889 million had every request been carried to the end. The price of the screen is coverage: the exit class still holds 45% of the cohort's operations, most of them small PJM solar and storage requests whose plants do not earn their capital back at merchant prices. The hurdle barely matters (97 to 107 invest requests from h = 5 to h = 2) because the binding condition is the sign of the NPV. The invest class is ERCOT wind: 97 of the 101 requests.

**Two years in.** On the 1,298 requests still in the queue, the rule accelerates 39, holds 629 for sale or a later review and exits 630. The accelerate class reached operation within three years 51% of the time [36%, 66%], the exit class 10% [8%, 13%] and the hold class 11%; in ERCOT 18 of the 30 accelerated requests operated, in PJM 2 of 9. The accelerate class returned +$1,228 million on 9,385 MW at merchant NPV; the exit class would have lost $8,316 million; hold-or-sell is near zero (+$82 million on 629 requests), which is what a class worth more to a buyer than to this book should look like. The gate and the registered count book answer different questions: the count book of 25 held 19 operations, the accelerate class holds 20 of the pool's 152 in 39 requests, because the gate refuses the solar and storage the count book keeps. Of the 101 requests invested in at entry, 29 are accelerated again and 29 exited two years in; of the 1,468 left alone, 575 are confirmed exits and 4 would be accelerated.

![Figure 12](../figures/F23_portfolio_review.png)

*Figure 12.* Share of requests that reached operation by gate decision and region, with Wilson intervals, hurdle 3.

Three cards from the decision pack show the rule at work. A 525 MW ERCOT wind request that entered in 2019: lookup probability 24%, landmark probability 20%, expected NPV two years in $27 million against a next-gate cost of $0.6 million, accelerate; it operated within five years. A 279 MW ERCOT wind request of 2021 vintage in the same class, landmark probability 36%, expected NPV $27 million, accelerate; still waiting at the end of 2024. And the modal request of the cohort, a utility-scale PJM solar request in a county with earlier requests: segment rate 7%, lookup cell 13%, a plant with a negative NPV at merchant prices, exit at both gates unless a contract above $57/MWh is in hand.

## 8 The book: when to buy, where, and how much

**When.** The registered test of a milestone-managed book settles the timing: a book of 25 utility-scale requests chosen two years in by the landmark model held 19 that reached operation within three years against 11 for a lookup that knew the same agreement status (+8 [+1, +11]); the book of 50 held 33 against 24 (C15 passes). The same model's book held fewer megawatts (1,078 against 1,681 MW; C16 fails), and its level could not be repaired at the landmark (C17 fails): more projects built, not more megawatts. At entry the lookup ties or wins (an exploratory count book of 25 held 13 operations for the fair baseline against 7 for the model). Buy at the milestone, not at entry (Figure 13).

![Figure 13](../figures/F18_managed_book.png)

*Figure 13.* The milestone-managed book: operations and MW realised within three years of the two-year landmark for books of 25 and 50 chosen by the landmark model, the agreement-aware lookup, the entry lookup and at random, with 95% resampling intervals.

**Where and how much (Figure 14).** Adding in the model's order while its probability stays at or above the pool's own rate (10.5%) admits 410 of the 1,132 utility-scale requests still in the queue two years in; 95 of them operated within three years, 23% against the pool's 10.5%, and the model's own expectation for that book was 104. The curve says where the edge is: the model's first 25 picks held 22 operations against 11 for the lookup, its first 50 held 34 against 25, and at 100 both held 51; beyond that the lookup catches up. ERCOT is where the two-year review pays: 167 adds out of 347 captured 70 of the region's 75 operations, a 42% hit rate against a pool rate of 22%. In PJM the model adds 241 of 665 for 24 of the region's 37 operations (10% against 6%): without dated agreements it separates little, and the company should add fewer there and review again later. In CAISO the floor admits two requests. The count comes with a warning from section 6: at merchant prices the ERCOT adds have a negative expected NPV in total, because most are solar and storage. The count book says which requests will exist; the gates say which are worth owning.

![Figure 14](../figures/F24_book_per_region.png)

*Figure 14.* How many to add two years in and where: operations realised within three years of the landmark against the number added in the landmark model's and the agreement-aware lookup's order, and the model's floor book by region with resampling intervals.

**Four ways to spend the same budget, with the level as the risk.** Four policies spent the same $20.11 million deposit budget on the 2017–2019 pool, scored in 5,000 scenarios from the copula of the book simulation with one more factor, a cohort level multiplier drawn from the observed-to-predicted ratios of the 2017, 2018 and 2019 cohorts, so the whole book runs hot or cold together. Every policy that counts capital buys wind, and every one made money where the value-index book lost it (Table 3): the NPV-per-dollar book (20 requests), the model's expected-NPV book without caps (27) and the risk-adjusted book that greedily raises E[NPV] − λ·ES₉₅ under the caps (19) have expected NPVs of $476–593 million, an expected shortfall near −$25 million and a 4–7% chance of a loss, and returned +$146 to +$214 million at merchant NPV; the equal regional split returned +$221 million on 25 requests. The fair baseline's value-index book, which bought offshore wind and giant requests by megawatts, has an expected shortfall of −$4.8 billion and an 86% chance of a loss, and returned −$362 million. The objective decides the book: counting capital removes the giant-request bias of the earlier backtest and turns the choice between choosers into a choice between signs. The risk-adjusted book barely differs from the plain NPV book, because once the level is a common factor the shortfall is driven by the level, not by which wind requests are in the book.

| Policy under the same budget | Requests | Expected NPV, $M | ES₉₅, $M | P(loss) | Realised operations | Realised NPV, $M |
|---|---|---|---|---|---|---|
| Equal regional split | 25 | +429 | −31 | 5% | 4 | +221 |
| NPV per dollar, with caps | 20 | +476 | −28 | 7% | 1 | +146 |
| Model expected NPV, no caps | 27 | +593 | −23 | 4% | 2 | +182 |
| Risk-adjusted (E[NPV] − λ·ES₉₅), with caps | 19 | +475 | −27 | 7% | 3 | +214 |
| Fair baseline, value index | 22 | −1,369 | −4,772 | 86% | 2 | −362 |
| Random | 22 | −191 | −879 | 100% | 2 | −147 |

*Table 3.* Six ways to spend the deposit budget on the 2017–2019 pool: expected NPV and downside in the scenarios, and what happened. Source: `results/policy_comparison.csv`. The shared risk beyond the level is small (latent correlation 0.041 between requests of the same region and cohort); the level is the risk, and it is the one a company can read before it buys, from the newest cohort's early outcomes.

**The committee memo per region.** *ERCOT.* Invest: the base rate is the highest of the three (18.4% at five years), the agreement is dated for 30% of requests and it is the one signal that moves the odds from 0.8% to 63%; at merchant prices only wind earns its capital back (+$0.34 million per MW with the credit), so enter wind, hold solar and storage only against a contract above $57/MWh, and review every request at the agreement rather than at a calendar date. Two years in, add by the model's order: 167 picks captured 70 of the region's 75 operations. What would reverse it: the level, which has fallen for every cohort since 2017, and the credit deadline of 2027.

*PJM.* Invest selectively: gas (+$0.22 million per MW, a bet on the capacity market) and wind (+$1.18 million) pay at merchant prices, solar only just; the queue is the most crowded of the three and completion falls from 22% in the quietest fifth of entry dates to 10% in the most crowded; the agreement is not dated in the public file, so the model separates little two years in (241 adds for 24 of 37 operations) and the review should wait for the system impact study, where 42% of PJM's withdrawals happen. Prefer the light, settled queues of the PJM core (the 19.7% archetype) and requests under 66 MW.

*CAISO.* Hold capital: five-year completion is 4.8%, a twentieth of ERCOT's in the test cohort for utility-scale requests, 82% of withdrawals happen in the system impact study in the first year, and at merchant prices only wind has a positive NPV ($0.09 million per MW). Enter only with a signed agreement in hand (58% five-year completion where it was signed within two years, on 19 requests) or a contract above the break-even price; two years in, the floor admits two requests.

## 9 Evaluation record

| Criteria | Registered before | Lines | Passed | What they say |
|---|---|---|---|---|
| C1–C5 | notebook 08 | 12 | 8 | the model beats cohort averages at 3 and 5 years; calibration slope fails |
| C6–C12 | notebook 11 | 12 | 3 | at utility scale the fair lookup ties; the landmark model wins at +2 years (C8); the simulated band covers the realised book (C11); no leakage (C12) |
| C13–C14 | notebook 19 | 12 | 3 | MISO: +0.067 [+0.008, +0.127] at 5 years; SPP too thin |
| C15–C17 | notebook 20 | 10 | 4 | the milestone book wins on operations, not MW; the level is not repaired at the landmark |
| C18–C19 | notebook 08b | 8 | 5 | other learners tie LightGBM (C18 fails on one line) and do not beat the lookup (C19 fails) |

*Table 2.* Every registered criterion, as registered, pass or fail. Sources: `results/success_criteria*_scored.csv`, `results/tournament_criteria.csv`.

## 10 Broader impacts

A score like this can fulfil itself: if lenders refuse the requests it ranks low, those requests fail, and the next model learns that they fail. It encodes the rules of a regime that is ending (every test request entered before FERC Order No. 2023 moved interconnection to cluster studies), and size is a top driver, so a gatekeeper using it to screen applicants would penalise small developers for a pattern partly made by rules. The version of this report a company should act on makes that risk smaller: at entry it recommends public averages and rules, which treat every applicant of a kind alike; the model's value is at the milestones, on requests already in the queue. The line I draw is the same as before: the score may inform portfolio choices and should not screen access to the queue.

## 11 Limitations

The agreement is dated for 30% of ERCOT's requests, 15% of CAISO's and 2.6% of PJM's, so the milestone results rest on ERCOT and CAISO; PJM's own export dates no study or agreement. The timing models cover three ISOs and a pre-reform regime; the seven-year horizon rests on 2017 entrants alone. No entry-time model is calibrated to the post-2020 level. The NPV is a capstone-scale DCF: national average costs for a representative class in 2022 dollars, merchant on-peak prices with an assumed capture, no contracts, no financing, no energy revenue for storage; the sign of gas in PJM is a bet on the capacity market. Nodal prices, weather, land, transmission network data and financing curves, which a siting or pricing decision would need, are outside the public files used here and are stated as the next layer, not attempted.

## 12 Conclusion

Where is the opportunity: ERCOT for base rates and dated agreements, PJM for gas and the capacity market, CAISO only with a signed agreement. Which requests get built, and when: predictable at an AUC of 0.858 at three years and far better two years in with the agreement; the clock is good to about a year in PJM; the level must be read from the newest cohort. Why they fail: size, technology and the agreement, in the system impact study in year one in CAISO and PJM and in the facilities study after year four in ERCOT. What a plant is worth: at merchant prices, wind anywhere and gas or solar in PJM before 2027; everything else needs a contract above its break-even price. What to do with the book: fund the 4% of requests the gates mark, which returned +$1.4 billion at entry and +$1.2 billion two years in at merchant NPV, and stop carrying the 65% they mark for exit, which would have lost $8.9 billion; buy at the milestone, where a model-managed book of 25 held 19 operations against 11; two years in, add in ERCOT, where 167 picks captured 70 of 75 operations, add sparingly in PJM, and nothing yet in CAISO. Each of these is a decision with a probability, a value, a cost and a downside behind it, and each was scored on what happened to the requests that entered in 2017–2019.

## Statement of work

All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried out by Alan Mössinger.

## Changes after mentor feedback

Feedback items and the changes they led to are logged in `docs/mentor_feedback.md`.
