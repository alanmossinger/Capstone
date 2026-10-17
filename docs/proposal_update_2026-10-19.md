# SIADS 699 — Project Proposal Form, update of 2026-10-19

Group 13 · Alan Mössinger (solo project) · University of Michigan, Master of Applied Data Science.
This update replaces the answers of the first form (submitted October 2026) where the scope changed on
12 October 2026 (decision #62) and where the framing changed on 17 October 2026 (decision #83). Answers
that did not change are kept and marked *(unchanged)*.

## 1. Short name for the project and team

Team Queued Up (Group 13) — project title: **"Beyond Prediction: Prescriptive AI for Energy Portfolio
Optimization — From Machine Learning to Risk-Aware Capital Allocation Across Oil, Gas, Power,
Renewables, and Storage."**

## 2. Subject and questions

An energy company with a fixed annual capital budget must choose, among about forty documented U.S.
opportunities, which to fund, when and how much: twenty federal offshore Gulf of Mexico lease
redevelopments and twenty ERCOT power candidates (five gas combined-cycle, five utility solar, five
onshore wind, five battery storage), each anchored to a real asset or a real interconnection-queue request.
The decision is hard for four reasons the data can speak to: physical output must be forecast; oil, gas and
power prices move together; a new power plant may never reach commercial operation, or may reach it
years late; and costs are only partly observable.

The first form asked whether a project-level survival model beats the cohort averages the industry uses to
judge which interconnection requests get built, and when. That work is done and its verdicts are
registered: at entry the model ties a careful region × technology × size lookup; at the milestones, two
years in, it wins where the interconnection agreement is dated (Uno's C 0.80 against 0.59), and a book
managed by it holds more operations than the analyst's lookup. This update keeps everything built and
turns it into the **completion-and-timing engine** of the power candidates: each power candidate's
probability of reaching operation, and the distribution of its operation year, come from those models.
Around that engine the project adds what the capital decision needs.

**The contribution is the step from predictive to prescriptive AI.** Predictive models estimate what is
likely to happen to each asset — completion, timing, output, price. Prescriptive AI determines which
actions are preferable given an objective, a budget, constraints, uncertainty and a stated risk
tolerance, and is then judged against the conventional methods it claims to improve on. The report
moves through four stages — descriptive (what happened), predictive (what is likely), uncertainty
(what could go wrong) and prescriptive (what to do) — and the last stage is the one evaluated. The
overarching question is:

> *Can prescriptive AI turn uncertain predictions about oil, gas and electricity investments into better
> capital-allocation decisions than conventional financial and portfolio-selection methods?*

Four research questions sit under it:

- **RQ1 — Predict.** How accurately can machine learning estimate project completion and timing (the
  queue engine), lease oil and gas output, plant generation and the three prices (WTI, Henry Hub, ERCOT),
  compared with transparent baselines — the region × technology × size lookup, seasonal naive, Arps
  decline, random walk?
- **RQ2 — Quantify uncertainty.** How do commodity-price volatility, cross-asset correlation, forecast
  error and the never-built / late-build risk of the power candidates change investment value and
  portfolio-level risk (P(NPV < 0), the worst-5% average loss)?
- **RQ3 — Prescribe.** Under one budget and diversification and downside-risk constraints, which
  combination of oil, gas, renewable generation and storage investments should be selected, and how does
  the recommended book change with the organisation's risk preference?
- **RQ4 — Evaluate.** Under which assumptions and risk preferences does the prescriptive recommendation
  outperform, match or underperform conventional approaches — top-N NPV ranking, equal capital by sector,
  deterministic optimization — out of sample, in a replayed decision gym against realized outcomes, and
  when an AI advisor restricted to the project's own result tables makes the recommendation?

Prescriptive does not mean automatically superior; it means recommending actions from a stated
objective and reporting what the recommendation costs.

Hypotheses, with thresholds registered before any test is scored (as C1–C19 were): **H1** the ML
challengers reduce held-out error against the best baseline per target (C20); **H2** the risk-aware
portfolio improves the registered risk/return metric against the sector-concentrated and top-N books
(C21–C22); **H3** uncertainty-aware selection is more stable under the named stresses than deterministic
selection (C23–C24).

## 3. Datasets

Every source is public U.S. data; each is on disk with a SHA-256 beside it and a line in the machine-readable
manifest, and `docs/data_readiness.md` ends in GO / NO-GO before any modelling notebook is written.

| Source | What it gives | Access | Status on 2026-10-17 |
|---|---|---|---|
| S1 Berkeley Lab "Queued Up: 2025 Edition" project-level file (Rand et al., 2025) | 36,441 interconnection requests 2000–2024: dates, status, phase, region, technology, MW | manual download, hash pinned *(unchanged)* | in hand, frozen; every registered verdict rests on it |
| S6 LBNL 2026 edition | one more year of outcomes, MISO/SPP dates | manual download | in hand (reconciliation and MISO/SPP only) |
| S2 EIA-860M generator inventory | operating dates, technology, MW, county, coordinates | EIA API v2, personal key in `.env` | in hand (July 2026 vintage) |
| S7 ISO queue files (CAISO report, PJM export, ERCOT GIS report) | milestone dates after entry | public files, fetched | in hand |
| S13 BSEE OGOR-A production, 2010–2024 | lease-month oil (bbl), gas (Mcf), water, days on production, completions, operator | 15 delimited zip files, scripted download, 1.4–3.7 MB each | downloaded 2026-10-12; 2010 file holds 163,361 completion-months |
| S14 EIA-923 plant / prime-mover monthly generation and fuel | Texas plant-month generation and consumption, 2001-01 → 2026-07 | EIA API v2 route `electricity/facility-fuel` (facets plant, fuel, state, prime mover) | in hand (notebook 01) |
| S15 WTI Cushing and Henry Hub monthly spot prices | 1986-01 → 2026-09 and 1997-01 → 2026-09 | EIA monthly files (and the API routes `petroleum/pri/spt`, `natural-gas/pri/fut`) | downloaded 2026-10-12 |
| S16 ERCOT prices | hourly day-ahead settlement-point prices at the trading hubs, ancillary clearing prices | 2024: my Forecast-to-Dispatch pull (gridstatus), copied with hashes; 2017–2019: ICE ERCOT North monthly (on disk); 2018–2023: ERCOT's public yearly files, parsed into the same layout (decision #78) | all in hand and observed; the earlier bridge from PJM prices for 2020–2023 is kept only as the first scoring of C20–C24 |
| S12 NREL Annual Technology Baseline 2024 | capital cost, O&M, heat rate, capacity factor, cost of capital per technology | OEDI parquet, hash pinned | in hand |
| S17 EPA eGRID 2023 | plant emission rates | xlsx, 21 MB, scripted download | downloaded 2026-10-12 |
| Census gazetteer and boundaries | positions and outlines for the maps | scripted download | in hand |

Features to explore: for the leases, lagged output at 1, 3, 6 and 12 months, decline slope, water ratio,
oil/gas mix, producing months, lease vintage; for the plants, lagged MWh, normalized generation,
heat-rate proxy, fuel cost, season; for storage, price-spread statistics on the hourly 2024 prices; for all
assets, the three prices, trailing volatility and the macro period; for the power candidates, the entry-time
and landmark features of the queue models as they stand. Every feature is lagged relative to the forecast
origin using a table of release lags, and a truncation test proves that no feature changes when post-origin
data are removed.

## 4. Usage restrictions

*(LBNL, EIA-860M, Census unchanged.)* BSEE, EIA and EPA files are U.S. federal public data; NREL's
ATB is published for open use with attribution; the ERCOT Public API serves public market information
to registered accounts under ERCOT's terms, which I cite and which do not restrict analysis of the
prices. EIA's hub-price files that originate from ICE are republished under permission and are not
redistributed. The repository ships download code, a data access statement, the manifest with hashes,
and only small derived tables; no raw file is committed. The EIA key, the ERCOT credentials and the
Anthropic API key live in `.env`, which is git-ignored and never printed. No personal data are involved;
leases and plants belong to companies. No IRB review is needed.

## 5. Minimum viable product

A reproducible analysis delivered as a public GitHub repository (one command, `make all`, rebuilds every
table and figure from the raw files), a written report, a poster, and a small dashboard — containing,
whatever the results turn out to be:

- **What is already built and registered**, kept as the timing engine: the cleaned queue file, the survival
  curves, the entry-time models, the fair lookup baseline, the level repair, the landmark models two years
  in, the value and cost layer with a project NPV at the technology's cost of capital, the stage gates, four
  allocation policies and the milestone-managed book, with criteria C1–C19 scored as registered (passed
  lines: 8 of 12, 3 of 12, 3 of 12, 4 of 10, 5 of 8).
- **A documented energy panel**: lease-months, plant-months, market-months, technology costs, with
  numbered audit rules, release lags and unit standardisation (bbl, Mcf, MWh, real 2024 dollars).
- **EDA with decision insights**: data quality, lease decline profiles, capacity-factor distributions by
  technology and season, price regimes, the asset map (offshore leases and Texas plants), the
  cross-sector correlation heatmap — each descriptive figure with block-bootstrap intervals.
- **Supervised forecasts** at rolling origins for lease output, plant generation and the three prices,
  against naive and physics baselines, with quantile intervals and SHAP; criterion C20 registered first.
- **Forty candidates with transparent economics**: the twenty leases with a modeled redevelopment
  (uplift against an Arps baseline, costs from a documented low / base / high grid) and the twenty ERCOT
  requests with ATB costs and the queue models' completion and timing distributions; every exported
  figure carries a provenance label (OBSERVED / DERIVED / FORECAST / ASSUMED), asserted by a test.
- **Joint scenarios and stresses**: 2,000 seeded scenarios from a moving-block bootstrap of the joint
  price changes, residual draws from the forecast models, cost multipliers and timing draws from the
  landmark models; named stresses (oil collapse, high gas, weak wind, curtailment, two-year delay,
  simultaneous downside); P(NPV < 0), VaR95 and CVaR95 per candidate and per book.
- **The prescriptive core**: a stated objective — maximize expected NPV minus λ times the worst-5%
  average loss — under one budget (40% of the forty candidates' capital) and a 40% cap per technology;
  books A (top-N NPV), B (equal-capital sectors), C (deterministic MILP) and D (risk-aware MILP, with the
  Rockafellar–Uryasev linearization, HiGHS through SciPy) under the same budget and scenarios; the
  recommended book at three risk preferences (yield, balanced, defensive); out-of-sample scoring on a
  second, held-out draw of the scenario bootstrap; an efficient frontier; ablations (no correlations;
  naive forecasts; no oil and gas; no renewables and storage); criteria C21–C24 registered first; and the
  trade-off between expected value and downside reported under two cost grids — the registered grid
  fixed before any result, and the harder grid an investment committee would use.
- **The AI advisor and the decision gym**: an advisor (a Claude model called through its command-line
  client, every call recorded and replayable offline) that sees only the result tables,
  recommends a book per scenario with every number verified against those tables by code, challenges
  the human's reasoning (a motivated-reasoning check and an ideological-Turing-test opponent) until
  the two converge or disagree on record, and is scored in a replayed decision gym against the human,
  the optimizer and instinct on realized NPV; every call logged, with a replay mode so the pipeline runs
  offline without a key.
- **A Streamlit dashboard** reading the result tables only (budget, risk aversion and price-shock
  sliders; books side by side; scenarios; the candidates map; the advisor in replay mode; the gym).
- **An executive, data-science and portfolio report** that opens with a one-page capital allocation
  memo and a decision board.

Stretch, not part of the MVP: a second investment stage with defer / expand options; Texas onshore
production from the Railroad Commission; ancillary-service revenue for the batteries beyond the
simplified daily-spread dispatch; a Bayesian cohort level for the queue models.

## 6. Ethical challenges and mitigations

*(The five items of the first form stand: self-fulfilling predictions, encoding past rules into future
decisions, misuse by gatekeepers, fairness to small developers, data limitations stated as limits.)* Added:

- **Modeled costs are not company data.** No public file holds an individual lease's redevelopment cost
  or a developer's contract. Every cost is parsed from a public file or listed as an assumption with a
  range and a source; break-even analyses show where the decision flips; no figure or table presents a
  modeled NPV as an observed corporate NPV, and the provenance label makes the difference visible on
  every export.
- **No unsupported "AI improves returns" claim.** A value difference between books, or between the
  advisor and the human, is reported only when it is computed under a registered criterion with its
  interval and its assumption envelope; the gym measures the advisor rather than asserting its value.
- **A language model that could invent numbers.** The advisor is grounded only in result tables; a check
  rejects any answer whose numbers do not appear in them, and the check result is stored with the
  answer. The prompts are committed and reproduced in the appendix; the model id, parameters and
  every response are logged.
- **Fossil assets in the book.** Oil and gas redevelopments and gas plants carry emissions; the
  optimizer takes an optional emissions cap built from eGRID factors and the report shows what the
  book looks like with and without it, so the trade-off is explicit rather than hidden in a discount rate.
- **The human in the loop.** The challenge mode is designed to argue against the user; the report states
  that its purpose is to surface reasoning, not to replace the decision, and the gym records where the
  human overruled the advisor and what it cost or saved.

## 7. Technical challenges

*(Censoring and competing risks, uneven event dates, the queue file's cleaning and the leakage control
are solved and documented; unchanged.)* Added:

- **Unit and grain harmonisation.** Barrels, Mcf and MWh become monthly cash flows under common
  real-dollar conventions and one valuation date; EIA-923 is kept at its reported plant / prime-mover
  grain and never split to generators; BSEE is joined by lease and month with one-to-many audits.
- **Leakage across time.** Every feature is lagged relative to the forecast origin by the source's release
  lag (EIA-923 about two months, BSEE about three, prices same month); imputers and scalers are fitted
  inside each training fold; the truncation test is the one test that may not be skipped.
- **Network access.** ERCOT's web edge refuses this machine; the 2018–2023 prices were pulled from
  ERCOT's public yearly files on a U.S. GitHub runner and parsed into the same layout as the 2024 pull,
  so no price month is an assumption. One Winter Storm Uri in seven years of history broke the first
  scenario engine (means in the trillions); monthly log changes are now capped at ±1.5 and the blocks
  aligned to calendar years, so a spike stays with its reversal.
- **Reproducible AI.** Model answers are not deterministic; every call is recorded and replayed, so the
  committed results never depend on a live key.
- **Optimization and run time.** A binary program over 40 candidates and 2,000 scenarios with the
  CVaR linearization solves in seconds with HiGHS; the dashboard re-solves on cached scenarios. The
  full pipeline rebuilds in about two hours on a laptop; no cloud is needed.

## 8. Evaluation and success criteria

Every claim has a metric and a baseline that a careful analyst could build without my models. Every
criterion is written and committed before the data it scores are seen; failures are reported as
registered and never re-scored (decision #34 is the precedent). Of 70 registered lines, 28 pass.

**What is measured, and against what.**

- **Completion and timing (RQ1; C1–C19, kept as registered).** Uno's C, time-dependent AUC and Brier
  score at 3, 5 and 7 years, calibration by entry cohort, expected against realized MW. Baselines: the
  cohort average and the *lookup* (the share built among earlier requests in the same region × technology
  × size cell). The lookup is the comparison that matters: at 20 MW and above the model ties it at entry
  (Uno's C 0.78 for both), and the claim moves to two years in, where the landmark model with the
  agreement flag reaches 0.80 against 0.59 for the lookup.
- **Output and price forecasts (RQ1, H1; C20).** The ratio of the machine-learning challenger's error to
  the best of five transparent baselines (last value, seasonal naive, Arps decline, technology-month
  median, random walk) at rolling origins, with paired moving-block bootstrap intervals; the challenger is
  named on validation before scoring. An ablation swaps naive forecasts into the optimizer and asks
  whether the book changes.
- **The prescription (RQ2–RQ4, H2–H3; C21–C24).** Books A–D under one budget, chosen on 2,000 primary
  scenario paths and scored on a second held-out draw of 2,000 with its own seed: expected NPV minus
  the worst-5% average loss (D against A and B, paired interval on the better side); stability of the
  selection under six named stresses (Jaccard, D against C); the tail against a single-sector book.
  Forecasting and allocation are evaluated separately: a lower error does not count as a better book.
  The trade-off is reported under two cost grids, and a recommendation that fails its registered metric
  but changes the downside is reported as that, not as a win.
- **The decision gym and the advisor (RQ4).** Sixteen past situations rebuilt as of their date with no
  outcome shown; instinct (top-N NPV), the registered rule, the AI advisor and the human each pick a book
  under the same budget and are scored on realized value against hindsight. The advisor is also scored on
  grounding — the share of the numbers it writes that appear in its tables — with every call recorded.

**How I could fool myself, and the guard against each.** A weak baseline (so the lookup leads, not the
cohort average); post-entry leakage (agreement dates and study phase enter only the landmark model, and
a registered criterion checks the entry model); level drift (every cohort since 2017 completes below the
model's level — the 2017–2019 cohort brought 18.8 GW online of the 29.2 GW expected — so calibration by
cohort is reported and books are sized to the newest cohort); rescoring until it passes (when observed
ERCOT prices replaced the bridge from PJM prices the verdicts moved; the first scoring is kept beside the
second, and post-scoring work is labelled); assumptions doing the work (lease costs are assumptions, so
every book is shown under the registered and the committee grid); machine learning that does not matter
(with naive forecasts the risk-aware book is unchanged, overlap 1.00, so the allocation is not credited to
it); grading a language model on its prose (numbers checked against tables and outcomes in the gym, not
style); thin evidence (in 6 of the 13 queue rooms nothing operated; the gym's edge comes mostly from the
three lease regimes, and the text says so); and regime change (every queue outcome predates FERC Order
No. 2023's cluster studies and the price history holds one Winter Storm Uri).

Visuals that make the case: cumulative incidence by region and technology; the level by entry cohort
before and after repair; the four books on the held-out scenarios with the frontier; the committee grid;
the decision gym; the AI workflow.

## 9. Contributions *(solo, unchanged)*

All roles are held by one person. Where the project reuses my own earlier work — the ERCOT 2024 price
pull and the battery dispatch program from my Forecast-to-Dispatch repository, the ERCOT Public API
client from my Milestone II project — the reuse is mine and is disclosed in the statement of work.

## 10. Cloud computing *(unchanged)*

No. The largest raw file is 21 MB and every model runs on a laptop.

## 11. What the teaching team should know

- A mentor with experience in energy economics or portfolio optimization under uncertainty would be
  valuable now that the project allocates capital across five sectors; the survival-analysis questions of
  the first form are settled.
- On 17 October the title and framing changed to make the prescriptive step the contribution: the
  record, the criteria and the verdicts are unchanged; the report is reorganised around the four
  questions above with the method and the full evidence in appendices.
- Feedback requested on two design choices: (a) scoring an AI advisor in a replayed decision gym against
  realized NPV — whether the course sees that as an acceptable evaluation of AI output; (b) whether a
  prescriptive recommendation that fails its registered risk/return criterion but cuts the worst-5% loss
  under the committee's cost grid is an acceptable primary finding, reported as a trade-off the committee
  decides rather than as a win.
- The first form's open question on EIA-860M linkage is closed (the generator inventory is on disk and
  used for the map and the capacity factors).
