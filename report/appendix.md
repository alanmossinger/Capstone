```{=typst}
#pagebreak()
```

## Appendix A — Pre-registered criteria (`results/success_criteria.csv`)

Slope = calibration slope; lift = top-decile lift; (B) = Track B.

| Line | Metric | Horizon | Model | Benchmark | Difference [95% interval] | Verdict | Point est. |
|----|---------|-----|-------------|-------|------------------------|------|-------|
| C1 | Uno's C | 3 yr | 0.853 | 0.731 | +0.121 [+0.072, +0.170] | PASS | better |
| C1 | Uno's C | 5 yr | 0.760 | 0.719 | +0.041 [+0.013, +0.069] | PASS | better |
| C1 | Uno's C | 7 yr | 0.672 | 0.657 | +0.015 [−0.014, +0.050] | FAIL | better |
| C2 | Brier | 3 yr | 0.0411 | 0.0471 | −0.006 [−0.008, −0.004] | PASS | better |
| C2 | Brier | 5 yr | 0.0808 | 0.0858 | −0.005 [−0.007, −0.003] | PASS | better |
| C2 | Brier | 7 yr | 0.1211 | 0.1219 | −0.001 [−0.004, +0.002] | FAIL | better |
| C3 | Slope | 3 yr | 1.345 [1.15, 1.58] | 0.9–1.1 | — | FAIL | — |
| C3 | Slope | 5 yr | 1.273 [1.11, 1.49] | 0.9–1.1 | — | FAIL | — |
| C3 | Slope | 7 yr | 0.939 [0.72, 1.14] | 0.9–1.1 | — | PASS | — |
| C4 | Lift | 5 yr | 3.96 [3.44, 4.51] | ≥ 1.5 | — | PASS | — |
| C5 | AUC (B) | — | 0.608 | 0.525 | +0.084 [+0.050, +0.118] | PASS | better |
| C5 | Brier (B) | — | 0.1475 | 0.1532 | −0.006 [−0.009, −0.002] | PASS | better |

Track A lines use the discrete-time LightGBM against the region × technology Aalen–Johansen baseline; Track B lines use the calibrated LightGBM against region × technology base rates. On the 2017 entrants alone, where 7 years are fully observed, LightGBM's concordance is 0.671 against 0.619 for the baseline, and the interval of the difference is [−0.006, +0.117].

### Appendix A2 — Pre-registered v2 criteria (`results/success_criteria_v2_scored.csv`)

Registered by notebook 11's first cell (decision #52) and scored in notebook 18. Primary cohort: test requests of 20 MW and more.

| Line | What | Model | Benchmark | Difference [95% interval] | Verdict |
|---|---|---|---|---|---|
| C6 | ≥ 20 MW: v2 vs fair baseline, uno_c at 3 years | 0.779 | 0.783 | −0.004 [−0.044, +0.046] | FAIL |
| C6 | ≥ 20 MW: v2 vs fair baseline, uno_c at 5 years | 0.734 | 0.752 | −0.018 [−0.051, +0.015] | FAIL |
| C6 | ≥ 20 MW: v2 vs fair baseline, brier at 3 years | 0.022 | 0.023 | −0.001 [−0.003, +0.001] | FAIL |
| C6 | ≥ 20 MW: v2 vs fair baseline, brier at 5 years | 0.064 | 0.064 | +0.000 [−0.002, +0.003] | FAIL |
| C7 | 2018–2019 ≥ 20 MW, level repaired: slope and intercept at 3 years | slope 1.09 | 0.8–1.2; 0 | intercept −0.74 [−1.17, −0.41] | FAIL |
| C7 | 2018–2019 ≥ 20 MW, level repaired: slope and intercept at 5 years | slope 1.18 | 0.8–1.2; 0 | intercept −0.47 [−0.70, −0.27] | FAIL |
| C8 | landmark +24 months: both updated vs entry model, Uno's C 3 years after | 0.788 | 0.687 | +0.101 [+0.062, +0.136] | PASS |
| C8 | landmark agreement executed: both updated vs entry model, Uno's C 3 years after | 0.598 | 0.593 | +0.004 [−0.016, +0.028] | FAIL |
| C9 | backtest: model book vs fair-baseline book, realised MW online within 5 years | 1,035 | 1,035 | +0 [−18, +450] | FAIL |
| C10 | backtest: model book vs fair-baseline book, realised value, base case | 1,463 | 1,463 | −0 [−54, +577] | FAIL |
| C11 | simulated 5–95% band covers the realised MW of the model's book | 1,035 MW realised | 1,473 expected | band 58–3,371 MW | PASS |
| C12 | leakage guard: dated features (test) and landmark AUC below the ablation's | — | — | — | PASS |

### Appendix A3 — Pre-registered v3 criteria, MISO and SPP (`results/success_criteria_v3_scored.csv`)

Registered by notebook 19's first cell (decision #54); the 2026 LBNL file, censored 2025-12-31; one model per region, notebook 06's settings.

| Line | Region | Metric | Horizon | LightGBM | Fair baseline | Difference / interval | Verdict |
|---|---|---|---|---|---|---|---|
| C13 | MISO | uno_c | 3 yr | 0.813 | 0.802 | +0.011 [−0.076, +0.091] | FAIL |
| C13 | MISO | uno_c | 5 yr | 0.557 | 0.490 | +0.067 [+0.008, +0.127] | PASS |
| C13 | MISO | brier | 3 yr | 0.023 | 0.018 | +0.005 [+0.003, +0.006] | FAIL |
| C13 | MISO | brier | 5 yr | 0.092 | 0.077 | +0.015 [+0.010, +0.020] | FAIL |
| C13 | SPP | uno_c | 3 yr | 0.510 | 0.810 | −0.301 [−0.622, +0.004] | FAIL |
| C13 | SPP | uno_c | 5 yr | 0.750 | 0.742 | +0.009 [−0.237, +0.200] | FAIL |
| C13 | SPP | brier | 3 yr | 0.005 | 0.013 | −0.009 [−0.012, −0.005] | PASS |
| C13 | SPP | brier | 5 yr | 0.025 | 0.042 | −0.017 [−0.022, −0.012] | PASS |
| C14 | MISO | slope | 3 yr | 1.87 | 0.8–1.2 | [0.83, 3.10] | FAIL |
| C14 | MISO | slope | 5 yr | 0.30 | 0.8–1.2 | [−0.14, 0.74] | FAIL |
| C14 | SPP | slope | 3 yr | 0.75 | 0.8–1.2 | [−4.85, 4.28] | FAIL |
| C14 | SPP | slope | 5 yr | 1.00 | 0.8–1.2 | [−0.97, 3.62] | FAIL |

### Appendix A4 — Pre-registered criteria for the milestone-managed book (`results/success_criteria_v4_scored.csv`)

Registered by notebook 20's first cell and committed before any later cell existed (decision #58). Pool: test requests of 20 MW and more in the queue two years after the request (1,132); books of 25 and 50, no region above half; M = landmark model, LA = lookup with agreement status, E = entry ranking not re-scored; 200 resamples.

| Line | What | Model | Benchmark | Difference [95% interval] | Verdict |
|---|---|---|---|---|---|
| C15 | book of 25: operations within 3 years, M vs LA | 19 | 11 | +8 [+1, +11] | PASS |
| C15 | book of 50: operations within 3 years, M vs LA | 33 | 24 | +9 [+0.98, +13] | PASS |
| C15 | book of 25: operations within 3 years, M vs E | 19 | 8 | +11 [+4, +13] | PASS |
| C15 | book of 50: operations within 3 years, M vs E | 33 | 19 | +14 [+7, +19] | PASS |
| C16 | book of 25: MW within 3 years, M vs LA | 1,078 | 1,681 | −604 [−2,196, +155] | FAIL |
| C16 | book of 50: MW within 3 years, M vs LA | 2,357 | 3,271 | −914 [−3,090, +180] | FAIL |
| C16 | book of 25: MW within 3 years, M vs E | 1,078 | 712 | +365 [−337, +846] | FAIL |
| C16 | book of 50: MW within 3 years, M vs E | 2,357 | 1,858 | +498 [−871, +1,238] | FAIL |
| C17 | all sizes: M after the level repair, intercept at 3 years (must cover 0) | raw −0.29 | 0 | −0.44 [−0.59, −0.28] | FAIL |
| C17 | ≥ 20 MW: M after the level repair, intercept at 3 years (must cover 0) | — | 0 | −0.50 [−0.68, −0.32] | FAIL |

## Appendix E — Value and cost assumptions (`results/value_assumptions.csv`)

Every input of the value index that is not parsed from a file on disk, with its range; parsed inputs are listed with their source.

| Input | Value | Low | High | Source | Status |
|---|---|---|---|---|---|
| ERCOT energy price 2020 onward | PJM West × 0.77 | × 0.7 | × 1.3 | ERCOT North traded in EIA's ICE files only 2017–2019; ratio of the 2017–2019 means | assumption |
| prices after 2025 | held at 2025 |  |  | no forward curve used | assumption |
| CAISO capacity price | $8.0/kW-month | $4.0 | $12.0 | CPUC Resource Adequacy reports (not fetched from this machine) | assumption — verify |
| ERCOT capacity price | 0 | 0 | 0 | energy-only market | by design |
| PJM capacity price after 2026 | held at 2026 (partial year) |  |  | Monitoring Analytics 2024 SOM Table 5-23 | parsed |
| accreditation by technology group | PJM 2025/26 ELCC class averages | × 0.7 | × 1.3 | Monitoring Analytics 2024 SOM Table 5-13 (Jan 23, 2025 column); applied to CAISO as a proxy | parsed; mapping is an assumption |
| capacity factors | 2024 generation / July-2026 nameplate, by state × technology | × 0.85 | × 1.15 | EIA API electric-power-operational-data; EIA-860M (notebook 01) | computed; vintage mismatch stated |
| offshore wind capacity factor | 0.4 | 0.35 | 0.45 | no operating U.S. fleet in 2024 data | assumption |
| 'Other' technology capacity factor | 0.3 | 0.2 | 0.5 | mixed group | assumption |
| capture of the on-peak price | {'Solar': 0.8, 'Solar+Battery': 0.85, 'Wind': 0.8, 'Offshore Wind': 0.85, 'Battery': 0.0, 'Gas': 1.0, 'Other': 0.9} | energy × 0.7 | energy × 1.3 | assumption | assumption |
| production credit, wind and solar | $27.5/MWh if operating by 2027 | 0 | $27.5 | IRC §45 base rate inflation-adjusted (verify the year's rate); deadline from IRS Notice 2025-42 (data/raw/value/irs_notice_2025-42.pdf) | deadline from the notice; rate to verify |
| case multipliers | {'low': {'energy': 0.7, 'capacity': 0.5, 'credit': 0.0}, 'base': {'energy': 1.0, 'capacity': 1.0, 'credit': 1.0}, 'high': {'energy': 1.3, 'capacity': 1.5, 'credit': 1.0}} |  |  | assumption | assumption |
| interconnection cost per kW outside PJM | PJM median by size band | × 0.5 | × 2 | LBNL PJM cost data (no CAISO/ERCOT file) | proxy |
| deposit share of interconnection cost to the next gate | 0.1 | 0.05 | 0.2 | assumption | assumption |
| study cost to the next gate, $ per request | 150000 | 50000 | 500000 | assumption | assumption |

## Appendix F — Landmark risk sets (`results/landmark_coverage.csv`)

| Landmark | Requests | ≥ 20 MW | Operations within 1 / 2 / 3 years | Withdrawals within 3 years |
|---|---|---|---|---|
| entry | 2,064 | 1,644 | 40 / 72 / 108 | 944 |
| +1 year | 1,508 | 1,263 | 34 / 73 / 116 | 453 |
| +2 years | 1,298 | 1,132 | 43 / 90 / 152 | 351 |
| agreement executed | 313 | 306 | 21 / 65 / 98 | 19 |

## Appendix B — Features, models and hyperparameters

| Feature | Type | How it is built |
|---|---|---|
| Region | categorical | CAISO, ERCOT or PJM |
| State | numeric (encoded) | operation and withdrawal rates of the state, computed out of fold, grouped by request, shrunk toward the overall rate with a prior of 50 requests |
| Technology | categorical | LBNL technology group; groups with fewer than 100 requests pooled into Other |
| Hybrid | binary | a second technology is listed |
| Capacity | numeric | MW; log scale in the logit and Cox models |
| Size regime | categorical | FERC bands with the step at 20 MW |
| Service type | categorical | NRIS, ERIS or missing |
| Request year | numeric | year of the request |
| Congestion | numeric | GW and rank of earlier same-region requests still waiting on the request date |

| Model | Library | Setting chosen | How it was chosen |
|---|---|---|---|
| Baseline | numpy (Aalen–Johansen) | region × technology cells | none to tune |
| Cox, operation / withdrawal | lifelines (Davidson-Pilon, 2019) | ridge 0.01 / 1.0 | 2016 log-likelihood |
| Discrete-time logit | scikit-learn (Pedregosa et al., 2011) | C = 0.1, early-year interactions | 5-fold grouped CV, C from 0.003 to 3.0 (CV log loss 0.720) |
| Discrete-time LightGBM | lightgbm | 8 leaves, 10 rows per leaf, 331 rounds, learning rate 0.05, feature and bagging fraction 0.8, L2 penalty 1.0 | 2016 log loss among 15 settings (decision #27) |
| Track B logit | scikit-learn | C = 0.1 | 5-fold CV |
| Track B LightGBM | lightgbm | 4 leaves, 20 rows per leaf, 243 rounds; isotonic map on bins of 50 | 2016 log loss (CV ranked the settings the other way, Spearman −0.85) |

## Appendix C — Reproducing the numbers

`make all` executes notebooks 01–09, then notebook 01b and notebooks 11–19, in order from the raw files (`make v3` runs only the portfolio layer). `make numbers` then writes `results/report_numbers.csv`, the source of every number in this report, and `pytest` checks each number in the report and these appendices against it.

## Appendix D — Terms

- **Censoring:** the request was still waiting at the end of 2024, so its outcome is unknown.
- **Competing risk:** withdrawal ends the wait for operation; it is an outcome of its own, not missing data.
- **Risk set; delayed entry:** the requests still waiting, and so able to have an event, at a given time. Under delayed entry a request joins the risk set only once it is observed.
- **Cumulative incidence:** the probability of having reached operation by time t, with withdrawal possible along the way.
- **Discrete-time hazard:** the probability of operating (or withdrawing) during a given year in the queue, given that the request is still waiting at its start.
- **Inverse-probability-of-censoring weights (IPCW):** weights that let requests observed long enough stand in for similar requests censored earlier.
- **Concordance and time-dependent AUC:** both measure ranking. Concordance compares pairs of requests at different event times; the AUC compares requests that operated by t with those that did not.
- **Brier score:** mean squared error of the predicted probability; lower is better.
- **Calibration slope:** slope of a logistic regression of outcomes on the model's log-odds; above 1, the predictions are spread too narrowly.
- **Top-decile lift:** completion rate in the 10% of requests with the highest predictions, divided by the overall rate.
- **Out-of-fold target encoding:** replacing a state by its outcome rate, computed without the request's own rows.
- **Grouped cross-validation:** folds that keep all rows of one request together.
- **Bagging and feature fraction:** the share of rows and columns each LightGBM tree sees.
- **Isotonic calibration:** a monotone map from raw scores to observed rates.
- **Spearman correlation:** correlation of ranks.
- **SHAP value:** a feature's contribution to one prediction, relative to the average prediction.
- **Partial dependence:** the mean prediction when one feature is set to a value for every request.
- **Fair baseline:** the Aalen–Johansen average by region × technology × FERC size band, cells under 50 requests shrunk to their parent.
- **Landmark:** a later decision point (one or two years in, or the executed agreement) from which the model is read for the requests still in the queue, with only information dated before it.
- **Level (intercept) and drift:** the average probability a model assigns against the share that occurred; drift is its change across entry cohorts.
- **Gaussian copula with a shared factor:** a simulation in which each request keeps its own probability but requests in the same region and cohort draw on one common shock.
- **Budget-constrained choice (binary program):** the book that maximises expected value subject to a deposit budget and concentration caps, solved exactly.
