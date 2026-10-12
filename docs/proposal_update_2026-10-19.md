# SIADS 699 — Project Proposal Form, update of 2026-10-19

Group 13 · Alan Mössinger (solo project) · University of Michigan, Master of Applied Data Science.
This update replaces the answers of the first form (submitted October 2026) where the scope changed on
12 October 2026 (decision #62). Answers that did not change are kept and marked *(unchanged)*.

## 1. Short name for the project and team

Team Queued Up (Group 13) — project name: **"From Queue to Capital: an AI-driven integrated U.S.
energy portfolio — offshore oil and gas, ERCOT gas, solar, wind and storage, with the interconnection
queue as the timing engine."**

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
Around that engine the project adds what the capital decision needs. The research questions are:

- **RQ1 — Predict.** Can machine learning improve 3-, 6- and 12-month forecasts of lease oil and gas
  output, plant generation and the three prices (WTI, Henry Hub, ERCOT) against naive and
  physics-informed baselines (seasonal naive, Arps decline, random walk)?
- **RQ2 — Quantify risk.** How do forecast error, price uncertainty, cross-asset correlation and the
  never-built / late-build risk of the power candidates change portfolio-level risk (P(NPV < 0), VaR,
  CVaR)?
- **RQ3 — Allocate.** Under the same budget and the same scenarios, does a risk-aware joint-scenario
  optimizer (maximize E[NPV] − λ·CVaR) beat top-N NPV ranking, equal-capital sectors and a deterministic
  optimizer out of sample, and does the diversification benefit survive modelling the correlations?
- **RQ4 — Explain and advise.** Which features and constraints change selection, diversification and
  timing — and can an AI advisor that may only cite the project's own result tables recommend a book per
  scenario, argue against the human's reasoning, and score better than instinct in a replayed decision
  gym against realized NPV?

Hypotheses, with thresholds registered before any test is scored (as C1–C19 were): **H1** the ML
challengers reduce held-out error against the best baseline per target (C20); **H2** the risk-aware
portfolio improves the registered risk/return metric against the sector-concentrated and top-N books
(C21–C22); **H3** uncertainty-aware selection is more stable under the named stresses than deterministic
selection (C23–C24).

## 3. Datasets

Every source is public U.S. data; each is on disk with a SHA-256 beside it and a line in the machine-readable
manifest, and `docs/data_readiness.md` ends in GO / NO-GO before any modelling notebook is written.

| Source | What it gives | Access | Status on 2026-10-12 |
|---|---|---|---|
| S1 Berkeley Lab "Queued Up: 2025 Edition" project-level file (Rand et al., 2025) | 36,441 interconnection requests 2000–2024: dates, status, phase, region, technology, MW | manual download, hash pinned *(unchanged)* | in hand, frozen; every registered verdict rests on it |
| S6 LBNL 2026 edition | one more year of outcomes, MISO/SPP dates | manual download | in hand (reconciliation and MISO/SPP only) |
| S2 EIA-860M generator inventory | operating dates, technology, MW, county, coordinates | EIA API v2, personal key in `.env` | in hand (July 2026 vintage) |
| S7 ISO queue files (CAISO report, PJM export, ERCOT GIS report) | milestone dates after entry | public files, fetched | in hand |
| S13 BSEE OGOR-A production, 2010–2024 | lease-month oil (bbl), gas (Mcf), water, days on production, completions, operator | 15 delimited zip files, scripted download, 1.4–3.7 MB each | downloaded 2026-10-12; 2010 file holds 163,361 completion-months |
| S14 EIA-923 plant / prime-mover monthly generation and fuel | Texas plant-month generation and consumption, 2001-01 → 2026-07 | EIA API v2 route `electricity/facility-fuel` (facets plant, fuel, state, prime mover); verified | route verified; pull in notebook 01 |
| S15 WTI Cushing and Henry Hub monthly spot prices | 1986-01 → 2026-09 and 1997-01 → 2026-09 | EIA monthly files (and the API routes `petroleum/pri/spt`, `natural-gas/pri/fut`) | downloaded 2026-10-12 |
| S16 ERCOT prices | hourly day-ahead and real-time settlement-point prices at the trading hubs, ancillary clearing prices | 2024: my Forecast-to-Dispatch pull (gridstatus), copied with hashes; 2017–2019: ICE ERCOT North monthly (on disk); 2018–2023: ERCOT Public API (NP4-190-CD), subscribed, from a network ERCOT's edge accepts | 2024 and 2017–2019 in hand; the 2018–2023 pull is a one-command job; until it runs the 2020–2023 months are labelled ASSUMED |
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
- **Allocation**: books A (top-N NPV), B (equal-capital sectors), C (deterministic MILP) and D (risk-aware
  MILP, E[NPV] − λ·CVaR with the Rockafellar–Uryasev linearization, HiGHS through SciPy) under the same
  budget and scenarios; out-of-sample scoring on held-out copula scenarios and on the realized
  2018–2024 path; an efficient frontier; ablations (no correlations; naive forecasts; no oil and gas; no
  renewables and storage); criteria C21–C24 registered first.
- **The AI advisor and the decision gym**: an advisor (Anthropic API) that sees only the result tables,
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
- **Network access.** ERCOT's web edge refuses this machine; the 2018–2023 price pull runs from another
  network through a client I wrote for an earlier course project, and the months stay labelled ASSUMED
  until it does.
- **Reproducible AI.** Model answers are not deterministic; every call is recorded and replayed, so the
  committed results never depend on a live key.
- **Optimization and run time.** A binary program over 40 candidates and 2,000 scenarios with the
  CVaR linearization solves in seconds with HiGHS; the dashboard re-solves on cached scenarios. The
  full pipeline rebuilds in about two hours on a laptop; no cloud is needed.

## 8. Evaluation and success criteria

Three layers, each with criteria written and committed before scoring, failures reported rather than
removed, and the verdict kept as registered (decision #34 is the precedent):

- **Forecast quality (RQ1, H1; C20).** Rolling-origin backtests with an expanding window; MAE and RMSE
  against the best baseline per target, bias and 90% interval coverage; paired differences at matched
  origins with moving-block bootstrap intervals; leave-some-leases-out and technology cold-start
  checks. Development 2018–2023, validation 2024-H1, holdout 2024-H2 (fixed after the data gate).
- **Decision quality (RQ2–RQ3, H2–H3; C21–C24).** Books A–D scored out of sample on held-out
  scenarios from a second generator (a Gaussian copula on the same marginals) and on the realized
  2018–2024 path: D beats A and B on the registered risk/return metric with the paired interval on the
  better side; D's selection changes less than C's across the stresses (Jaccard); the diversification
  benefit survives the correlation ablation. Forecasting and allocation are evaluated separately: a lower
  error does not count as a better book.
- **The advisor (RQ4).** Number-grounding rate, agreement with the optimizer's book, gym score against
  instinct, and a labelled rubric on ten answers.
- **The timing engine** keeps its registered record (C1–C19) and is not re-scored.

Visuals that make the case: the asset map; price, output and capacity-factor panels; the cross-sector
correlation heatmap; forecast-error distributions; the risk–return scatter and the efficient frontier; capital
allocation by sector under each book; the sensitivity tornado; the decision board.

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
- Feedback requested on two design choices: (a) scoring an AI advisor in a replayed decision gym against
  realized NPV — whether the course sees that as an acceptable evaluation of AI output; (b) the scope
  gate at week 4 — if a sector lacks data, keep oil and gas plus at least two others and reduce counts
  rather than drop a sector.
- The first form's open question on EIA-860M linkage is closed (the generator inventory is on disk and
  used for the map and the capacity factors).
