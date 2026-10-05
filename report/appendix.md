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

`make all` executes notebooks 01–09 in order from the raw files. `make numbers` then writes `results/report_numbers.csv`, the source of every number in this report, and `pytest` checks each number in the report and these appendices against it.

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
