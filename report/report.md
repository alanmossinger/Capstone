---
title: "From Queue to Capital: AI-Driven Portfolio Management for an Integrated U.S. Energy Book"
author: "Alan Mössinger"
date: "SIADS 699 Capstone, University of Michigan — Group 13 — October 2026"
---

## Abstract

An energy company that holds interconnection-queue requests must decide, request by request, whether to invest, hold or exit, and where to add. This report answers those questions with the public record of 13,366 requests in CAISO, ERCOT and PJM, tested on the 2,268 that entered in 2017–2019. Which requests get built is predictable: a gradient-boosted hazard model ranks the test cohort at an AUC of 0.858 at three years against 0.733 for cohort averages, and two years in the executed interconnection agreement lifts Uno's C from 0.687 to 0.797. Why they fail is legible: size, technology and the agreement set the odds (PJM falls from 24% five-year completion under 5 MW to 4% at 500 MW and up; an agreement signed within two years lifts ERCOT from 0.8% to 63%), and the regions run on different clocks (CAISO and PJM cull in year one, ERCOT after year four). What a plant is worth, once capital is counted at its cost of capital, is two short lists: at merchant prices only wind everywhere and gas or solar in PJM earn their capital back; under a 15-year contract at index prices, wind and solar do so everywhere; the credit deadline of 2027 decides the sign for the rest. The portfolio rules built on those three layers were scored on what happened: the requests the gates mark to fund reached operation 21–26% of the time at entry and 18–20% two years in, against 5% and 8% for those they mark to drop, and returned +$4 to +$9 billion with capital counted where the drops would have lost $5 billion; a book of 25 chosen two years in by the model held 19 requests that reached operation against 11 for an agreement-aware lookup. The conclusion is a set of decisions, each with its probability, value, cost and downside: enter by the cells and rules, review at two years in CAISO and PJM and at the agreement in ERCOT, fund wind anywhere and solar under contract, and size every book to the newest cohort's level, which runs at a quarter of the historical rate. Part II extends the decision to an integrated portfolio — twenty offshore Gulf lease redevelopments and twenty ERCOT requests under one budget and 2,000 joint scenarios — with the queue models as the timing engine: the lease book carries $14.6B of incremental NPV at base under an assumed cost grid, the contracted wind is the only power request that earns its capital at 2024 prices, the registered allocation criteria C21–C24 fail because no book loses money under that grid, a grounded and recorded LLM advisor is scored in a decision gym where the registered rule beat instinct by $100M a situation over 16 past situations, and the forward view says the book at one year is not the book at twenty.

## Capital Allocation Memo

*To the investment committee. One page. Every number below is read from `results/` by code; the figures and tables that carry it are in Part II.*

**The ask.** A budget of $6.15B (40% of the forty candidates' capital), no technology above 40% of it, over 2025–2044, across 20 federal offshore Gulf of Mexico lease redevelopments and 20 ERCOT power requests (5 gas combined cycle, 5 solar, 5 wind, 5 storage) drawn from a pool of 513 producing leases and 2,268 queue requests.

**The recommendation.** Fund the twenty lease redevelopments and the contracted wind requests; hold the gas requests to their next gate; do not fund solar or storage at 2024 prices. This is the risk-aware book D of notebook 09: 24 candidates, $4.2B of capital, an expected NPV of $20.65B on the held-out scenarios, a probability of losing money of 1.8%, and a worst-5% outcome that is still a profit. Top-N NPV (book A) earns $21.07B with the same budget and the same tail sign; the difference, −$420M [−$659M, −$210M], is the price of a risk aversion that has nothing to buy here, which is the finding, not a failure of the method.

**Why.** Under the confirmed upstream cost grid a lease redevelopment is an uplift on a producing asset for a modest spend: the twenty leases carry $14.6B of incremental NPV at base, every one positive, with a median break-even of $33 a barrel against a 2024 real WTI of $77. The twenty requests are worth −$0.76B merchant and −$0.28B contracted once the queue models' chance of operating within seven years (6%–23%) and the cost to carry are priced in; only wind under a $62 PPA is positive. No book of these forty loses money in any of 2,000 joint scenarios, so the 5% tail is a smaller profit, not a loss.

**What would change the answer.** The uplift share (10%–30% moves the book from $5.9B to $21.8B) and the operating cost ($12–$28 a barrel of oil equivalent: $16.6B to $9.2B) — both ASSUMED, both in the dashboard's grid page; a WTI collapse of the 2020 shape leaves the book at $13.85B on the flat path, the simultaneous downside at $12.07B from $13.83B. The requests' sign turns on the hub price and the PPA, not on the grid.

**When.** The lease book is negative within one and two years (−$1.4B, the workovers), positive from year three ($0.2B), $14.6B at twenty; a request is a carry cost until it operates, −$0.84B of expected loss at twenty years. A one-year owner funds nothing; a three-year owner funds twelve leases; the twenty-year owner buys the contracted wind.

**The record.** C21–C24, registered before any book was solved, all fail as registered (decision #71). In the decision gym the registered rule beat instinct by $100M a situation over 16 past situations, with a mean regret against hindsight of $197M against $297M. The advisor's own answers are not yet recorded (no key on this machine); the replay record fills in on the first live run.

## Decision Board

| Decision | Rule | Evidence | Where |
|---|---|---|---|
| D0 Enter the queue | by the cells and rules of Part I; the model's edge is at the milestones | C6–C12: the lookup ties at entry, the landmark model wins two years in | §4, §7 |
| D1 Review a request | at two years in CAISO and PJM, at the agreement in ERCOT | the stage-specific hazards; C8: the landmark model wins two years in | §5, §7 |
| D2 Value a plant | wind anywhere; solar under contract; gas in PJM; storage only above its break-even | the value tables at the cost of capital, merchant and contracted | §6 |
| D3 Size the book | to the newest cohort's level, a quarter of the historical rate | C15 passes on operations, C16–C17 fail on MW and level | §8 |
| D4 Allocate across sectors | the twenty leases plus contracted wind (book D); solar and storage wait for the price | C21–C24 fail; no book loses money in 2,000 scenarios | §19 |
| D5 Stress the book | the uplift share and the operating cost decide the lease side; the hub price and the PPA decide the power side | tornado; named stresses | §17, §18 |
| D6 Choose the horizon | nothing at one year; twelve leases at three; the full book from ten | within-horizon value by candidate | §21 |
| D7 Use the advisor | recommend per scenario, challenge the human, override only through the gate, score in the gym | grounding rate, agreement with D, gym score vs instinct | §20, Appendix A |

*Table 0.* The Decision Board: one line per decision, with the rule, the registered evidence and the section that carries it. Sources: `results/decision_ledger.csv`, `results/success_criteria_v7_scored.csv`, `results/decision_gym_scores.csv`.

## 1 The decision

At the end of 2024 the U.S. interconnection queues held more generation and storage capacity than the installed fleet, and of the capacity that asked to connect in 2000–2019, 12.6% was operating and 76.9% had withdrawn (Rand et al., 2025). A request enters a queue with a size, a technology and a place; it leaves, usually years later, as an operating plant or a withdrawal. An energy company that develops plants holds a book of such requests, and every request costs money to keep: a deposit, a study, then a larger deposit and a longer study.

The company asks five questions, and this report is organised around them. Where is the opportunity: which regions, states and technologies? Which requests get built, and when? Why do requests fail, and at which stage? What is a plant worth once it is built, at its cost of capital and under the contract it can sign, and what does it cost to find out? And, given all that, which requests should it fund, hold or exit, and how much should it add, where? Each section ends in a rule the company can apply, with the number, the interval and the evidence behind it. The data science is the evidence layer: survival models under competing risks, a pre-registered evaluation on a held-out cohort, interpretable rules, an unsupervised map of the market, a project cash-flow model and a scenario simulation of the book. The rules are thin arithmetic on top of those outputs, and they are scored on what actually happened to the 2017–2019 requests.

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

Once capital is counted, the value index of the earlier work becomes two short lists (Figure 11). The plant is valued the way a developer values it: a 20-year life from the operation date, overnight capital and operating cost per kW from the NREL Annual Technology Baseline 2024, a new plant's capacity factor, the investment credit for solar, storage and offshore wind and the production credit for wind, and the cash flows discounted at the technology's own real cost of capital from the ATB's Market financing case: 4.2% for solar and hybrids, 4.9% for wind, 5.1% for offshore wind, 5.4% for gas. The chance of never reaching operation is not loaded into the rate; the gates of section 7 carry it as a probability, which is how a staged development portfolio is run. Two revenue cases are kept side by side. **Merchant** sells energy at the on-peak hub price. **Contracted** sells it under a 15-year power purchase agreement at index-level prices (solar $57/MWh, wind $62, hybrids $70, offshore wind $110, each ±$10 as a range) and merchant after; gas, storage and the mixed group have no public contract index and stay merchant in both.

![Figure 11](../figures/F26_npv_per_mw.png)

*Figure 11.* NPV per MW at operation by technology and region: merchant revenue with today's credits (2024), a 15-year contract at index prices (2024), and merchant revenue after the credit deadline (2028); 20-year life, ATB real cost of capital per technology, low and high value cases as lines.

For a plant entering operation in 2024 with today's credits, five of the 21 technology-region pairs have a positive merchant NPV per MW: wind in PJM ($1.92 million per MW), ERCOT ($0.83M) and CAISO ($0.49M), gas in PJM ($0.64M) and solar in PJM ($0.45M). Solar in ERCOT and CAISO, hybrids, storage and offshore wind are negative at merchant prices. Under contract ten pairs are positive: wind and solar in every region, gas and hybrids in PJM, offshore wind in PJM and CAISO; storage stays negative because the public files give it capacity revenue only. After the 2027 credit deadline the merchant list shrinks to four. The break-even flat price says the same in the unit a company negotiates in: at its cost of capital a new solar plant needs $44/MWh over twenty years, wind $41, a combined cycle $72 at $3.50 gas, a hybrid $78; the on-peak price the market captures is $30–40/MWh for solar and $57–68 for wind. Wind clears its break-even on merchant prices and solar does not anywhere; a contract at the index level clears both. The gap, not the technology, decides the sign of solar, which is why section 7 runs the gates in both cases.

Probability-weighted and discounted to the day of the request, the median test request has an expected NPV of +$0.3 million at merchant prices and +$2.3 million under contract. If built three years after entry, 80% of PJM's requests, 22% of ERCOT's and 7% of CAISO's would have a positive merchant NPV per MW; under contract 87%, 79% and 22%. The difference is ERCOT's solar, which pays only with a contract, and CAISO's storage and hybrids, which pay in neither case on the revenue the files record. The cost of finding out is small next to these numbers: the deposit and study to the next gate are $8,169 per MW at 20–100 MW and $841 per MW at 500 MW and more, plus $150,000 of studies.

**The rule.** Develop wind anywhere; develop solar under a contract at or above the index, and in PJM even without one; develop gas in PJM, where the capacity market carries it; develop storage and hybrids only against a contract above their break-even price; and be operating by 2027 where the credit decides the sign. The NPV is the simplest form of a project DCF (no financing structure, tax depreciation, degradation or terminal value, and no energy revenue for storage), enough to rank and to put a sign on a request, not to price one.

## 7 The portfolio review: fund, hold or exit

The three layers above combine into one rule applied at two gates. At entry (G1) the company pays the first deposit and study; two years in (G2) it funds the next study or stops. At each gate the inputs are the probability of operating from there, the expected NPV if it does, discounted at the technology's cost of capital, the cost of the next gate and a hurdle *h* on the margin: **commit** when the probability is at least the pool's own outcome rate and the base-case margin is at least *h* times the cost; **exit** when the probability is well below the pool or the margin is negative even in the high value case at the low cost; **hold** otherwise, which at entry means entering with the two-year review scheduled and at two years means a request worth more to a buyer with a different hurdle than to this book. The hurdle falls as risk resolves, 3 at entry and 2 two years in, as staged development capital is judged in practice. At entry the probability is the lookup cell and the segment rate, because C19 was not met; two years in it is the landmark model with the agreement flag. Every number is computed under merchant and under contracted revenue, because a developer underwrites on the contract and the merchant case is the floor. The rule was scored on what happened (Figure 12).

**At entry.** The rule sorts the 2,268 test requests into 237 to invest in, 964 to enter with the review scheduled and 1,067 to leave alone at merchant prices; under contract 326, 903 and 1,039. 26% of the merchant invest class reached operation within five years [21%, 32%] and 21% of the contracted one [17%, 26%], against 11% for the hold classes and 5% for the exits; the cohort rate is 10%. Valued with capital counted, the invest class returned +$4,130 million (merchant) and +$9,347 million (contracted); the exit classes would have lost $5,277 and $4,900 million had every request been carried to the end. The invest class is wind in ERCOT (105 requests) and gas and solar in PJM (61 and 65); under contract ERCOT solar joins it with 82 requests, which is where the two cases differ. The price of the screen is coverage: the exits still hold 25% of the cohort's operations, and in ERCOT 100 exits reached operation 24% of the time, because that class is the mixed technology group, priced at a median cost it does not deserve, and the batteries whose ERCOT revenue the public files do not carry.

**Two years in.** On the 1,298 requests still in the queue, with a hurdle of 2, the rule accelerates 316 requests at merchant prices and 410 under contract, holds 577 and 493 for sale or a later review, and exits 405 and 395. The accelerate classes reached operation within three years 18% [14%, 23%] and 20% [17%, 25%] of the time against 8% for the exits; the pool rate is 12%. In ERCOT the merchant rule accelerates 35 requests, all wind, of which 51% operated; the contracted rule accelerates 120, wind and solar, of which 36% operated, 43 requests and more than half of ERCOT's operations in the pool. In PJM the rules accelerate 281 and 290 gas and solar requests with a 14% hit rate against the region's 6%. With capital counted the accelerate classes returned +$3,642 million (merchant) and +$8,989 million (contracted); the exits would have lost $5,094 and $4,572 million; hold-or-sell is near zero at merchant prices and +$1,536 million under contract, the mark of a class worth more to a buyer than to this book. Against the registered count book of section 8, which held 19 operations in 25 requests, the contracted accelerate class holds 55% of the pool's 152 operations in 32% of its requests: the gate trades hit rate for coverage and value, which is what a hurdle of 2 is for. Of the 237 requests the merchant rule invested in at entry, 77 are accelerated again two years in and 33 exited; of the 1,067 left alone, 304 are confirmed exits and 132 would be accelerated with what is known two years in.

![Figure 12](../figures/F23_portfolio_review.png)

*Figure 12.* Share of requests that reached operation by gate decision and region, merchant and contracted revenue, with Wilson intervals; hurdle 3 at entry and 2 two years in.

Three cards from the decision pack show the rule at work. A 525 MW ERCOT wind request that entered in 2019: lookup probability 24%, landmark probability 20%, expected NPV two years in $84 million merchant and $183 million under contract against a next-gate cost of $0.6 million, accelerate in both cases; it operated within five years. A 279 MW ERCOT wind request of 2021 vintage, landmark probability 36%, expected NPV $80 million merchant and $170 million contracted, accelerate; still waiting at the end of 2024. And the modal request of the cohort, a utility-scale PJM solar request in a county with earlier requests: segment rate 7%, lookup cell 13%, a plant worth $0.45 million per MW at merchant prices and $0.55 million under contract, which the rule holds at entry and accelerates two years in if the landmark model agrees; most of PJM's 290 contracted accelerations are of this kind, and 14% of them were built.

## 8 The book: when to buy, where, and how much

**When.** The registered test of a milestone-managed book settles the timing: a book of 25 utility-scale requests chosen two years in by the landmark model held 19 that reached operation within three years against 11 for a lookup that knew the same agreement status (+8 [+1, +11]); the book of 50 held 33 against 24 (C15 passes). The same model's book held fewer megawatts (1,078 against 1,681 MW; C16 fails), and its level could not be repaired at the landmark (C17 fails): more projects built, not more megawatts. At entry the lookup ties or wins (an exploratory count book of 25 held 13 operations for the fair baseline against 7 for the model). Buy at the milestone, not at entry (Figure 13).

![Figure 13](../figures/F18_managed_book.png)

*Figure 13.* The milestone-managed book: operations and MW realised within three years of the two-year landmark for books of 25 and 50 chosen by the landmark model, the agreement-aware lookup, the entry lookup and at random, with 95% resampling intervals.

**Where and how much (Figure 14).** Adding in the model's order while its probability stays at or above the pool's own rate (10.5%) admits 410 of the 1,132 utility-scale requests still in the queue two years in; 95 of them operated within three years, 23% against the pool's 10.5%, and the model's own expectation for that book was 104. The curve says where the edge is: the model's first 25 picks held 22 operations against 11 for the lookup, its first 50 held 34 against 25, and at 100 both held 51; beyond that the lookup catches up. ERCOT is where the two-year review pays: 167 adds out of 347 captured 70 of the region's 75 operations, a 42% hit rate against a pool rate of 22%. In PJM the model adds 241 of 665 for 24 of the region's 37 operations (10% against 6%): without dated agreements it separates little, and the company should add fewer there and review again later. In CAISO the floor admits two requests. Counted in expected NPV at the technology's cost of capital, the ERCOT adds are worth −$1,975 million at merchant prices and +$2,186 million under a 15-year contract, because most are solar, which pays only with a contract; the PJM adds are worth +$725 and +$948 million. The count book says which requests will exist; the gates say which are worth owning, and the contract decides it in ERCOT.

![Figure 14](../figures/F24_book_per_region.png)

*Figure 14.* How many to add two years in and where: operations realised within three years of the landmark against the number added in the landmark model's and the agreement-aware lookup's order, and the model's floor book by region with resampling intervals.

**Four ways to spend the same budget, with the level as the risk.** Four policies spent the same $20.11 million deposit budget on the 2017–2019 pool, scored in 5,000 scenarios from the copula of the book simulation with one more factor, a cohort level multiplier drawn from the observed-to-predicted ratios of the 2017, 2018 and 2019 cohorts, so the whole book runs hot or cold together. Every policy that counts capital buys wind, and every one made money in both revenue cases, where the value-index book of the earlier backtest lost it at merchant prices (Table 3): the NPV-per-dollar book (21 requests), the model's expected-NPV book without caps (27) and the risk-adjusted book that greedily raises E[NPV] − λ·ES₉₅ under the caps (21) have expected NPVs of $1.5–1.8 billion with a 2–3% chance of a loss and returned +$391 to +$396 million at merchant NPV; the equal regional split returned +$581 million on 26 requests. Under contract the same books returned +$1,235 to +$1,611 million. The value-index book, which bought offshore wind and giant requests by megawatts, has an expected shortfall of −$3.8 billion and a 79% chance of a loss at merchant prices and returned −$46 million; under contract it returned +$440 million, because the offshore wind it bought pays with a contract. The objective decides the book: counting capital removes the giant-request bias of the earlier backtest and turns the choice between choosers into a choice between signs. The risk-adjusted book barely differs from the plain NPV book, because once the level is a common factor the shortfall is driven by the level, not by which wind requests are in the book. The shared risk beyond the level is small (latent correlation 0.041 between requests of the same region and cohort); the level is the risk, and it is the one a company can read before it buys, from the newest cohort's early outcomes.

| Policy under the same budget | Requests | Expected NPV, $M (merchant) | ES₉₅, $M | P(loss) | Realised NPV, $M (merchant) | Realised NPV, $M (contracted) |
|---|---|---|---|---|---|---|
| Equal regional split | 26 | +1,404 | +29 | 2% | +581 | +1,271 |
| NPV per dollar, with caps | 21 | +1,536 | +55 | 3% | +396 | +1,235 |
| Model expected NPV, no caps | 27 | +1,803 | +99 | 2% | +391 | +1,611 |
| Risk-adjusted (E[NPV] − λ·ES₉₅), with caps | 21 | +1,531 | +66 | 2% | +396 | +1,235 |
| Fair baseline, value index | 22 | −747 | −3,804 | 79% | −46 | +440 |
| Random | 22 | −220 | −1,369 | 88% | −85 | +15 |

*Table 3.* Six ways to spend the deposit budget on the 2017–2019 pool: expected NPV and downside in the merchant scenarios, and what happened under each revenue case. Source: `results/policy_comparison.csv`.

**The committee memo per region.**

*ERCOT.* Invest: the base rate is the highest of the three (18.4% at five years), the agreement is dated for 30% of requests and it is the one signal that moves the odds from 0.8% to 63%; at merchant prices only wind earns its capital back (+$0.83 million per MW with the credit) and solar needs a contract at or above $44/MWh, so enter wind, enter solar with a contract, hold storage, and review every request at the agreement rather than at a calendar date. Two years in, add by the model's order: 167 picks captured 70 of the region's 75 operations, worth +$2,186 million under contract. What would reverse it: the level, which has fallen for every cohort since 2017, and the credit deadline of 2027.

*PJM.* Invest: gas (+$0.64 million per MW, a bet on the capacity market), wind (+$1.92 million) and solar (+$0.45 million) pay at merchant prices and more under contract; the queue is the most crowded of the three and completion falls from 22% in the quietest fifth of entry dates to 10% in the most crowded; the agreement is not dated in the public file, so the model separates little two years in (241 adds for 24 of 37 operations) and the review should wait for the system impact study, where 42% of PJM's withdrawals happen. Prefer the light, settled queues of the PJM core (the 19.7% archetype) and requests under 66 MW.

*CAISO.* Hold capital: five-year completion is 4.8%, a twentieth of ERCOT's in the test cohort for utility-scale requests, 82% of withdrawals happen in the system impact study in the first year, and at merchant prices only wind has a positive NPV ($0.49 million per MW); solar pays under contract ($0.38 million). Enter only with a signed agreement in hand (58% five-year completion where it was signed within two years, on 19 requests) and a contract; two years in, the floor admits two requests.

## 9 Evaluation record

| Criteria | Registered before | Lines | Passed | What they say |
|---|---|---|---|---|
| C1–C5 | notebook 06, part A | 12 | 8 | the model beats cohort averages at 3 and 5 years; calibration slope fails |
| C6–C12 | notebook 04, part D | 12 | 3 | at utility scale the fair lookup ties; the landmark model wins at +2 years (C8); the simulated band covers the realised book (C11); no leakage (C12) |
| C13–C14 | notebook 04, part K | 12 | 3 | MISO: +0.067 [+0.008, +0.127] at 5 years; SPP too thin |
| C15–C17 | notebook 09, part C | 10 | 4 | the milestone book wins on operations, not MW; the level is not repaired at the landmark |
| C18–C19 | notebook 06, part B | 8 | 5 | other learners tie LightGBM (C18 fails on one line) and do not beat the lookup (C19 fails) |

*Table 2.* Every registered criterion, as registered, pass or fail. Sources: `results/success_criteria*_scored.csv`, `results/tournament_criteria.csv`.

## 10 Broader impacts

A score like this can fulfil itself: if lenders refuse the requests it ranks low, those requests fail, and the next model learns that they fail. It encodes the rules of a regime that is ending (every test request entered before FERC Order No. 2023 moved interconnection to cluster studies), and size is a top driver, so a gatekeeper using it to screen applicants would penalise small developers for a pattern partly made by rules. The version of this report a company should act on makes that risk smaller: at entry it recommends public averages and rules, which treat every applicant of a kind alike; the model's value is at the milestones, on requests already in the queue. The line I draw is the same as before: the score may inform portfolio choices and should not screen access to the queue.

## 11 Limitations

The agreement is dated for 30% of ERCOT's requests, 15% of CAISO's and 2.6% of PJM's, so the milestone results rest on ERCOT and CAISO; PJM's own export dates no study or agreement. The timing models cover three ISOs and a pre-reform regime; the seven-year horizon rests on 2017 entrants alone. No entry-time model is calibrated to the post-2020 level. The NPV is a capstone-scale DCF: national average costs for a representative class in 2022 dollars, merchant on-peak prices with an assumed capture, no contracts, no financing, no energy revenue for storage; the sign of gas in PJM is a bet on the capacity market. Nodal prices, weather, land, transmission network data and financing curves, which a siting or pricing decision would need, are outside the public files used here and are stated as the next layer, not attempted.

## 12 Conclusion of Part I

Where is the opportunity: ERCOT for base rates and dated agreements, PJM for gas and the capacity market, CAISO only with a signed agreement. Which requests get built, and when: predictable at an AUC of 0.858 at three years and far better two years in with the agreement; the clock is good to about a year in PJM; the level must be read from the newest cohort. Why they fail: size, technology and the agreement, in the system impact study in year one in CAISO and PJM and in the facilities study after year four in ERCOT. What a plant is worth: wind anywhere, solar under contract and in PJM even merchant, gas in PJM; storage and hybrids only with a contract above their break-even price, and the credit deadline of 2027 decides the rest. What to do with the book: fund the requests the gates mark, 10–14% of the cohort at entry and 24–32% of the two-year pool, which returned +$4.1 and +$3.6 billion at merchant NPV and +$9.3 and +$9.0 billion under contract, and stop carrying the 47% they mark for exit at entry, which would have lost $5 billion; buy at the milestone, where a model-managed book of 25 held 19 operations against 11; two years in, add in ERCOT, where 167 picks captured 70 of 75 operations, add sparingly in PJM, and nothing yet in CAISO. Each of these is a decision with a probability, a value, a cost and a downside behind it, and each was scored on what happened to the requests that entered in 2017–2019.

## Part II — The integrated portfolio

## 13 The portfolio problem

Part I answered the queue's questions for a developer. An energy company does not hold only queue requests: it holds producing assets, and its capital decision is across sectors. Part II extends the decision to a real integrated U.S. portfolio — 20 federal offshore Gulf of Mexico lease redevelopments drawn from a pool of 513 producing leases, and 20 ERCOT power requests (5 gas combined cycle, 5 solar, 5 wind, 5 storage) drawn from the 2,268 test-cohort requests of Part I — under one budget, one scenario set and one risk measure. Everything built in Part I is kept: the queue-survival and landmark models are the completion and timing engine of the power candidates. Four research questions: can machine learning improve the physical forecasts (RQ1); how do forecast error, price uncertainty and cross-asset correlation change portfolio risk (RQ2); does a risk-aware multi-energy book beat NPV ranking and sector-only books under the same budget out of sample (RQ3); and which features and constraints in fact change the selection (RQ4). The criteria were registered before scoring (C20 for the forecasts, C21–C24 for the allocation) and are reported as registered.

Every exported figure carries a provenance label — OBSERVED (a public record), DERIVED (arithmetic on records), FORECAST (a model's output) or ASSUMED (a stated assumption) — and a figure built from several carries the weakest. The upstream cost grid is ASSUMED throughout, because public records do not disclose a redevelopment's cost; its impact is shown before its results are used.

## 14 Data for the portfolio

| Source | Grain | What it feeds | Gate |
|---|---|---|---|
| BSEE OGOR-A production, 2010–2024 (15 files, SHA-256 hashed) | lease-month: oil, gas, water, days on production | the lease pool (1,041 leases with 60 or more producing months), the Arps baselines, the forecasts | PASS |
| EIA-923 via the EIA API v2 (186,744 rows, Texas, 2018–2024) | plant × prime mover × month | capacity factors and heat rates of 69 gas combined-cycle, 108 solar, 201 wind and 18 storage plants | PASS |
| EIA WTI and Henry Hub monthly spot prices; BLS CPI-U | month, real 2024 dollars | the price panel, the scenario engine | PASS |
| ERCOT DAM and RTM settlement-point prices, 2024 hourly (my Forecast-to-Dispatch pull, hashes pinned) | hour, North hub | capture factors, the battery dispatch, the 2024 anchor | PASS |
| ERCOT 2020–2023 months (bridged from PJM West at the 2017–2019 ratio, labelled ASSUMED; 48 months) | month | the price panel | FAIL (non-blocking) |
| EPA eGRID2023 | plant | emissions of the generation panel (98.8% of 2023 plants join) | PASS |

*Table 3.* The v5 sources and the readiness gate of `docs/data_readiness.md` (outcome GO). Every raw file is hashed in `data/raw/manifest_v5.json`; the EIA key is read from `.env` and never printed (38 pages checked).

Features are built at rolling origins with each source's release lag (BSEE three months, EIA-923 two, prices none), and a truncation test proves that no feature at an origin uses a month after it. The split is registered: development January 2018 to December 2022, validation the first half of 2023, holdout July 2023 to December 2024.

## 15 What the energy data say

A quarter of lease-months are zero by nature; the median lease keeps half its peak oil for twelve months and the pooled Arps exponent is the physics floor. Texas wind runs at 33% of nameplate, solar at 22%, gas combined cycle at 23%, each with the seasonal shape a revenue model needs. Henry Hub is twice as volatile as WTI; prices and physical output barely co-move month to month, which is why the scenario engine draws prices jointly and output separately. The decline clusters are weak and decide nothing.

## 16 Forecasting the physical output (C20)

C20 registered twelve lines — lease oil and gas at 3, 6 and 12 months, plant capacity factors at 1 and 3 months, the prices at 1 and 3 months — each a challenger (ElasticNet or LightGBM, chosen on validation, refit quarterly) against the best of five baselines at rolling origins, scored by a paired moving-block bootstrap. Three of twelve pass, all plant lines: the challengers cut the seasonal-naive error of the gas, solar and wind capacity factors by 8%, 12% and 15%. The lease lines fail with the registered challenger's error 1.35 times the last-value baseline at three months, a large negative bias from the log transform; a post-hoc level model (labelled, not registered, decision #67) brings the ratio to 0.96 and is the one the scenario engine draws its residuals from. The price lines fail, as random walks should.

## 17 What each candidate is worth, and what it depends on

Lease redevelopment: an Arps baseline from the last 36 months, an uplift of 20% of the baseline rate after a two-year lead time, the workover paid at month zero, the incremental cash flow against doing nothing, discounted at the ATB offshore rate, under the confirmed cost grid (decision #68). Power request: the NPV if built, at the 2024 hourly basis — solar earns 92% of the flat hub price because it produces when the price is low, wind 83%, gas combined cycle 135% because it runs when the price is high (63% of hours), the battery $74.6k per MW-year from one cycle a day — weighted by the queue models' probability of operating in each of seven years, minus the cost to carry.

At the flat 2024 real prices the twenty leases carry $14.6B of incremental NPV, every one positive, median break-even $33 a barrel; the twenty requests −$0.76B merchant and −$0.28B contracted (P(operation within seven years) 6%–23%); wind is positive under the $62 PPA, nothing else is. The tornado (Figure 16) says what the lease side rests on: the uplift share, 10%–30%, moves the book from $5.9B to $21.8B; the operating cost, $12–$28 a barrel of oil equivalent, from $16.6B to $9.2B; the power price basis moves the book by under $0.5B.

![Figure 15](../figures/F28_candidates.png)

*Figure 15.* The forty candidates: capital, expected NPV and the probability of operating, with the provenance of each column.

![Figure 16](../figures/F29_cost_tornado.png)

*Figure 16.* The cost grid's impact on the default book: each ASSUMED item swung across its stated range, one at a time.

## 18 Scenarios and risk

2,000 joint paths of 240 months: block-bootstrapped monthly shocks of WTI, Henry Hub and the ERCOT price over 2018–2024 (blocks of 12 months, the same months for all three, so the correlations and the 2020 and 2022 episodes travel together) on log prices that revert toward their 2018–2024 real means with a four-year half-life (ASSUMED; a pure random walk put WTI anywhere from $13 to $800 and was replaced before any criterion was scored). Output multipliers come from the scored holdout residuals, one per lease or plant, widened by the inverse of the data-completeness score; cost multipliers are triangular 0.75–1.5; operation years come from the entry curves through the copula of the book simulation, under which 87% of the twenty requests never operate within seven years. A Gaussian copula on the same marginals makes a second, held-out set that the optimizer never selects on.

Ten years out WTI sits between $27 and $224 a barrel (5–95%). The default book of forty has a mean NPV of $20.6B merchant, a 3.5% chance of a loss, and a worst-5% outcome that is still a $1.5B profit; every named stress leaves it positive, the worst (the simultaneous downside) at $12.07B from $13.83B on the flat path. Removing the correlations changes the book's CVaR by $1.8B, which is what joint modelling is worth here.

![Figure 17](../figures/F30_price_scenarios.png)

*Figure 17.* The joint price scenarios against the real-dollar history.

![Figure 18](../figures/F32_stresses.png)

*Figure 18.* The default book under the named stresses.

## 19 The four books under one budget (C21–C24)

Registered before any book was solved (decision #70): budget 40% of the default book's capital ($6.15B), no technology above 40% of it, the contracted case for solar and wind, selection on the primary scenarios, scoring on the held-out copula set. Book A takes candidates by expected NPV; B splits the budget equally by sector; C is the deterministic MILP; D maximises expected NPV minus the CVaR95 of the loss (Rockafellar–Uryasev, HiGHS).

All four criteria fail as registered (decision #71). Out of sample D earns $20.65B against $21.07B for A (C21: −$420M [−$659M, −$210M]) and no more than B (C22: −$150M [−$350M, +$24M]); its selection moves more than C's under the six stresses (C23: mean Jaccard 0.95 against 0.99); its CVaR is not below the registered single-sector comparator's (C24: −$323M [−$937M, +$250M], the comparator being the near-empty power-only book, which the rule registered before the scenarios existed picked and which is kept with that reading). The finding behind the four failures: no book of these forty loses money in any scenario under the confirmed grid, so risk aversion has nothing to buy; the books converge on the twenty leases plus contracted wind and some gas (D: 24 candidates, $4.2B; P(NPV < 0) 1.8%). Sensitivity (budget −20%, λ doubled, a $50 carbon price, a 25% cap) moves D by a Jaccard of 0.84–0.96. H2 and H3 are not supported on this candidate set, for a reason the report states: the grid, not the optimizer.

![Figure 19](../figures/F33_four_books.png)

*Figure 19.* The four books and the two single-sector books out of sample, the frontier over λ, and capital by technology.

## 20 The advisor and the decision gym

An LLM advisor (Anthropic Messages API, model `claude-sonnet-5-5`, temperature 0) sees only the result tables of §17–§19 rendered as text and nothing else; every number it writes is checked against those tables, every call is recorded to `results/advisor_runs.jsonl` and replayed from there, so the pipeline runs offline and each answer can be audited against the prompt that produced it. Three modes: a recommendation per named scenario and per horizon (the book, the numbers cited, the binding constraint, what would change the answer); a challenge round in which the human states a preferred book and the advisor runs the motivated-reasoning check (at most five questions, then the patterns named with the sentence that shows each) and the ideological Turing test (the opposing book argued by its strongest advocate, ending in a convergence line); and the decision gym. The human may override the advisor's book only after answering the five questions and reading the opposing case; every decision goes to the ledger. Appendix A carries the prompts and the evaluation.

The gym scores decisions, not prose. Sixteen situations built as of their date with no hindsight — the fifteen largest requests of ERCOT, PJM and CAISO in each 2017–2019 cohort at entry, the 2017 cohort at its two-year gate, ERCOT 2018 with the budget cut a fifth, and the twenty lease candidates at the start of the 2014, 2020 and 2022 oil-price regimes — each under 40% of its total cost; instinct (top-N expected NPV), the registered rule, the advisor and the human pick, the realized value is revealed (for a request, the modeled value per MW when it in fact operated, minus the cost to the gate: a proxy, labelled DERIVED), and the exact knapsack with hindsight is the ceiling. Over the 16 situations the registered rule beat instinct by $100M a situation on average, with a mean regret of $197M against $297M. The rooms differ: in 9 of the 13 queue situations (all of PJM and CAISO, ERCOT 2019) none of the fifteen largest requests operated within the window, so the best book is empty, instinct lost the gate costs and the rule, which held or exited, lost nothing; at the ERCOT two-year gate the rule held every request and missed the five that operated ($2.17B to instinct, $0 to the rule); in the lease regimes the MILP matched hindsight in 2 of 3 because every lease pays and the budget binds. The advisor's picks are not recorded on this machine (no key); the human's appear as the dashboard's ledger fills.

![Figure 20](../figures/F34_decision_gym.png)

*Figure 20.* The decision gym: realized value of each actor's book in sixteen past situations, against hindsight.

## 21 The forward view: the book at one to twenty years

A twenty-year NPV says nothing about what the owner holds at year three. For each candidate the value counted within a horizon — leases: the incremental cash flows against the baseline, truncated; requests: the carry cost, the capital at the operation year and the operating margin to the horizon, weighted by the probability of operating by each year — gives the book at each horizon under the same budget and cap. The lease book is −$1.4B within one and two years (the workovers), $0.2B at three, $2.9B at five, $8.1B at ten and $14.6B at twenty; the requests are a cost at every horizon, −$0.84B at twenty. The deterministic book holds nothing at one and two years, 12 leases at three, 19 at five and all 20 from ten. The dashboard shows the horizon beside the book so the committee's own horizon, not the model's, picks the row.

![Figure 21](../figures/F35_horizon_view.png)

*Figure 21.* The forward view: expected NPV within 1, 2, 3, 5, 10 and 20 years by sector, and the book at each horizon.

## 22 Evaluation record of Part II

| Criteria | Registered before | Lines | Passed | What they say |
|---|---|---|---|---|
| C20 | notebook 03, part B | 12 | 3 | the plant capacity-factor lines beat the seasonal naive; the lease lines fail on the log transform's bias; the prices are random walks |
| C21–C24 | notebook 09, part D | 4 | 0 | no book loses money under the confirmed grid, so the risk-aware book cannot beat the rules; the comparator reading is kept as registered |

*Table 4.* Sources: `results/success_criteria_v6_scored.csv`, `results/success_criteria_v7_scored.csv`.

## 23 Broader impacts and limitations of Part II

Modeled costs are not company data: the lease NPVs rest on an ASSUMED grid whose two largest items move the book by a factor of four, and the report never presents a modeled NPV as an observed one; the grid and its impact are the first page of the dashboard. No headline of the form "AI increases returns by X%" is made: the advisor's value is a gym score against realized outcomes, and on this machine that score is not yet recorded. The ERCOT price for 2020–2023 is bridged and labelled; the lease pool is federal offshore only; EIA-923 is plant-level, so no generator-level claim is made; the gym's realized value for a request is the modeled value per MW at the observed outcome, a proxy; the optimizer's scenarios for the 2014 regime use the 2018–2024 shock history; the forecasts' lease lines are carried by a post-hoc model that is labelled as such. Where a region's data are thinner the candidate carries a data-completeness score, its uncertainty is widened and its constraints tightened, and the dashboard says so; nothing is silenced.

## 24 Conclusion of Part II

Across sectors the capital goes where the asset already produces: the lease redevelopments, cheap uplifts on producing leases under the confirmed grid, carry the book, and the contracted wind is the only power request that earns its capital at 2024 prices. The risk-aware optimizer does not beat NPV ranking here because nothing in this candidate set loses money; that is a statement about the grid and the prices, made with its envelope, not a claim about the method. The forecasts earn their keep on the plant side and not on the leases; the scenarios keep the history's joint jumps and bound them; the advisor is a grounded, recorded, scored participant with a human gate; and the gym is where "the AI defies instinct" stops being a slogan and becomes a number next to the rule's.

## Statement of work

All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried out by Alan Mössinger.

## Appendix A — The AI advisor: prompts, grounding, record and evaluation

The advisor is a system component, documented in `docs/ai_use.md`; this appendix carries what the course asks for: the actual prompts, the grounding rule and the evaluation.

**Grounding.** The model receives the system prompt below and a user message with a task template and a DATA block of result tables rendered by one formatter. `advisor.verify_numbers` accepts a number in the answer only if the same token appears in the DATA block (years and counts up to 50 exempt); the grounding rate and the ungrounded tokens are stored with the answer.

**Record and replay.** Every call is appended to `results/advisor_runs.jsonl` (model, temperature, prompts, response, usage, verification), keyed by the hash of model, system and user prompts; a recorded call is served from the record, so notebook 10 runs offline. With no key and no record the advisor's rows read "not recorded".

**Override gate.** `advisor.override_allowed` requires an answer of at least 20 characters to each of the 5 questions and the opposing case read; a refused override names the missing items. Every decision goes to `results/decision_ledger.csv`.

**Evaluation** (`results/advisor_evaluation.csv`, `results/advisor_rubric.csv`): grounding rate over recorded answers; agreement with book D (Jaccard and by name) over the 7 named scenarios and the 6 horizons; gym score against instinct and regret against hindsight; the rubric on up to ten answers. On this machine: 0 recorded answers, 33 calls missing; the first live run records them.

**System prompt** (`prompts/advisor_system.md`), **recommend** (`prompts/recommend.md`), **gym** (`prompts/gym_pick.md`), **the motivated-reasoning check** (`prompts/motivated_reasoning_check.md`) and **the ideological Turing test** (`prompts/ideological_turing_test.md`) are committed in `prompts/` and printed in full in notebook 10, section 1. The two reasoning prompts are my instruments for a decision meeting, written as templates with a `{human_statement}` and an `{opposing_book}` slot.

## Changes after mentor feedback

Feedback items and the changes they led to are logged in `docs/mentor_feedback.md`.
