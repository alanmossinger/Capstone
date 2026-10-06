# Queue Survival: Which Proposed Power Plants Get Built, and When?

Alan Mössinger · SIADS 699 Capstone, University of Michigan · Draft v1

## Abstract

Most power plants that ask to connect to the U.S. grid are never built, and developers, lenders and grid operators plan with cohort averages. I built project-level models that estimate, on the day a request enters the queue, the probability that it reaches commercial operation within 3, 5 and 7 years, using only information known at entry. On 2,268 held-out requests that entered CAISO, ERCOT and PJM queues in 2017–2019, my models passed 8 of 12 pre-registered criterion lines; the timing model, a discrete-time gradient-boosted hazard model, passed 6 of 10. It ranks requests better than region × technology averages at 3 and 5 years. Its probabilities run too high in the middle of the range, and its advantage disappears when requests under 20 MW are excluded.

## 1 Problem and who decides

At the end of 2024 the queues held more generation and storage capacity than the installed U.S. fleet (Rand et al., 2025). If history holds, most of it will be withdrawn: of the capacity that requested interconnection in 2000–2019, I count 12.6% operating and 76.9% withdrawn by the end of 2024. Three groups act on this pipeline. A developer decides where to spend deposits and engineering effort, a lender prices timing risk, and an independent system operator (ISO) plans transmission around projects that may never arrive. All three mostly reason with averages by region and technology. My question is whether a model of each request, fitted on earlier requests and tested on later ones, can rank and price requests better than those averages, and where it cannot.

## 2 Data gathering and preparation

**Sources.** The study population is the project-level file of Lawrence Berkeley National Laboratory's *Queued Up: 2025 Edition* (Rand et al., 2025): 36,441 requests × 31 columns, with request, operation and withdrawal dates, status, region, state, technology, capacity and service type. The LBNL site refuses scripted downloads, so I downloaded the file by hand and pinned it by its SHA-256 hash; the raw file is not redistributed. I also pulled the July 2026 inventory of operable generators (EIA-860M; U.S. Energy Information Administration [EIA], 2026) through the EIA API: 28,324 generators in 6 pages, 1,408.6 GW of nameplate capacity.

**Readiness gate.** Before any modeling I ran a written go/no-go check (`docs/data_readiness.md`). All 15 of 15 checks pass after I amended two thresholds, after seeing the numbers: one had been set from a rounded figure, the other from a cohort size the file could not reach (decision #15). The gate found the project's main constraint. Event dates are near-complete only in CAISO, ERCOT and PJM, where at least 95.2% of operating requests have an operation date and at least 82.6% of withdrawn ones a withdrawal date. Elsewhere they are sparse: MISO dates 1.4% of operations and 41.8% of withdrawals, the West 21.5% and 7.5%, SPP no withdrawals at all (0.0%). Timing models are therefore limited to the three ISOs ("Track A"). Linking LBNL projects to EIA generators to recover missing dates matched 31.1% of 1,650 projects, with 74.9% of matches agreeing on the operating date, against bars of 40% and 80% set in advance, so I dropped that extension (decision #14).

**Cleaning.** Nine numbered rules (R1–R9, `src/cleaning.py`) convert Excel serial dates, clear 204 placeholder request dates and 692 event dates that contradict the status or precede the request, drop 208 non-generation requests and requests without a positive capacity, and resolve one duplicate key, leaving 36,216 requests. Track A holds 13,366 requests: 1,730 reached operation, 7,064 withdrew and 4,572 were still waiting at the end of 2024 (censored). A second sample, Track B, keeps 14,624 resolved requests from all nine regions to predict whether a request is ever built, without timing.

## 3 Exploratory analysis

I estimated cumulative incidence curves with the Aalen–Johansen estimator (Aalen & Johansen, 1978), which treats withdrawal as a competing event rather than as censoring, with 95% bootstrap bands.

![Figure 1](../figures/F1_cif_by_region.png)

*Figure 1.* Cumulative incidence of reaching operation (left) and of withdrawing (right) by years since the request, Track A, n = 13,366, 95% bootstrap bands.

![Figure 2](../figures/F2_operation_by_technology.png)

*Figure 2.* Cumulative incidence of reaching operation by technology group within CAISO, ERCOT and PJM, Track A, groups with at least 50 requests, 95% bootstrap bands.

Region dominates the raw outcomes (Figure 1): within 5 years 18.4% of ERCOT requests operate against 13.2% in PJM and 4.8% in CAISO, while 66.5% of CAISO's and 61.2% of PJM's requests withdraw, against 27.4% in ERCOT. Technology orders outcomes within each region (Figure 2): gas reaches operation within 5 years for 26.9% of ERCOT, 31.9% of PJM and 10.5% of CAISO requests, against 11.1%, 7.4% and 4.2% for solar, and no battery or solar-plus-battery group exceeds 3.4%. Smaller requests are built more often (Figure 3): in PJM 29.3% of requests under 5 MW operate within 5 years against 3.7% at 500 MW and above, and CAISO falls from 15.8% in the band just under 20 MW to 6.1% in the band above it. ERCOT shows no gradient until its largest band (8.7% at 500 MW and above, against 25.8% at its peak). Crowding at entry, the mechanism Johnston et al. (2023) describe, is visible only in PJM (Figure 4: 32.1% in the least crowded fifth, 8.7% in the most crowded), and there it moves together with the request year.

![Figure 3](../figures/F3_five_year_by_size.png)

*Figure 3.* Probability of operation within 5 years by requested capacity, Track A entrants 2000–2019, 95% bootstrap intervals; the 20 MW FERC small/large generator step is marked.

![Figure 4](../figures/F8_congestion_vs_completion.png)

*Figure 4.* Probability of operation within 5 years by fifths of capacity already waiting in the region's queue at entry, Track A entrants 2000–2019, 95% bootstrap intervals.

The analysis also tested the data. My recomputed completion rates match LBNL's published ones within 1.2 points. In ERCOT, 441 withdrawals share one recorded date in August 2018 and none is dated earlier, so ERCOT's withdrawal timing before then is unknown. The proposed online date appears to be revised after entry, so it would leak the outcome and stays out of the main models (decision #22).

## 4 Methods

**Framing.** This is supervised learning with time-to-event labels: each request ends in operation, withdrawal or censoring at the end of 2024. A classifier of "built or not" would discard the timing and would have to drop requests still waiting or count them as failures, so the timing models handle censoring and competing risks explicitly (Putter et al., 2007). Every request carries an outcome or a censoring time and the question is predictive, so I used no unsupervised method.

**Features.** Only information known on the request date enters the models: region, state, technology, hybrid flag, capacity in MW, FERC size regime, service type, request year, and two measures of queue congestion (Appendix B). Congestion measures the capacity of earlier same-region requests still waiting on the request date. State is target-encoded out of fold (Micci-Barreca, 2001). Study phase, interconnection-agreement dates and the proposed online date are kept out and used only in a labeled leakage ablation. One mismatch remains: the discrete-time models are fitted on the congestion of each year a request waited, but predict with its value at entry (decision #26), which produces an artifact discussed in section 7.

**Models.** Four Track A models predict P(operation by t):

1. *Baseline:* the Aalen–Johansen curve of the request's region × technology cell in the training data, the kind of average the industry uses today.
2. *Cause-specific Cox models* for operation and for withdrawal (Cox, 1972), ridge-penalized (0.01 and 1.0, chosen by 2016 log-likelihood). I used cause-specific hazards rather than Fine–Gray subdistribution hazards (Fine & Gray, 1999) because they are what the discrete-time models estimate and combine into both incidence curves consistently.
3. *Discrete-time multinomial logit* (Allison, 1982): each request becomes one row per year in the queue (14,653 project-years) with an effect for each year, the last years pooled. C = 0.1 (inverse penalty strength) and early-year interactions were chosen by 5-fold cross-validation grouped by request.
4. *Discrete-time LightGBM* (Ke et al., 2017), a multiclass booster on the same rows. Of 15 settings, grouped cross-validation preferred the largest trees (64 leaves), but on 2016 entrants, later than every fitting row, the settings ranked nearly in reverse (Spearman −0.65). I chose 8 leaves and 331 rounds by 2016 log loss: 0.649, against 0.666 for the cross-validation choice and 0.690 for the logit (decision #27).

The yearly hazards convert to P(operation by t) through the cumulative incidence formula. ERCOT's undated early withdrawals are handled by delayed entry (decision #21): ERCOT requests that entered before August 2018 join the risk set only from that month, which leaves 98 of 732 ERCOT training requests. For Track B, a logistic regression and LightGBM predict P(built), with isotonic calibration on bins of at least 50 requests (Zadrozny & Elkan, 2002). Appendix B lists every setting; Appendix D defines the terms.

## 5 Evaluation design

The split follows time. Tuning uses fits to 4,725 entrants up to 2015 scored on 573 entrants from 2016; the Track A models are then refitted on entrants up to 2016 and scored once on the 2,268 requests that entered in 2017–2019 (549, 672 and 1,047 by year), of which 227 (10.0%) operated within 5 years. The 5,800 requests from 2020 onwards are too recent to score. Track B is fitted on entrants up to 2015, calibrated on 2016 and tested on 2017 (decision #29). The 7-year horizon is fully observed only for 2017 entrants; 532 test requests were censored before 7 years. A withdrawn request is a known non-event, and censored requests are reweighted by the inverse probability of censoring. One change from my draft, made before any test data were read: these weights come from the test requests' own follow-up windows, because training-set weights would all be 1.

I score each model on concordance (Uno et al., 2011, adapted to competing risks by Wolbers et al., 2014), time-dependent AUC (Blanche et al., 2013), Brier score (Graf et al., 1999), calibration slope (Cox, 1958) and top-decile lift. I wrote the scoring code myself because the library functions I found (Pölsterl, 2020) treat withdrawal as censoring, which answers a different question (decision #31).

Before scoring, I fixed and committed five criteria (decision #5):

- C1: concordance above the baseline's at 3, 5 and 7 years.
- C2: Brier score below the baseline's at 3, 5 and 7 years.
- C3: calibration slope between 0.9 and 1.1.
- C4: top-decile lift of at least 1.5 at 5 years.
- C5: Track B AUC above and Brier score below the region × technology base rates'.

For C1, C2 and C5, "beat" means the 95% interval of the paired difference, from 200 bootstrap resamples, lies entirely on the better side of zero; C3 and C4 are judged on the point estimate.

## 6 Results

![Figure 5](../figures/08_evaluate/08_12_success_criteria.png)

*Figure 5.* The pre-registered criteria with 95% bootstrap intervals; C1, C2 and C5 as paired gains over the benchmark. Track A test entrants 2017–2019 (n = 2,268); Track B resolved 2017 entrants (n = 1,534).

**The pre-registered verdict: 8 of 12 lines pass** (Figure 5; Appendix A). LightGBM beats the baseline on concordance at 3 years (+0.121 [+0.072, +0.170]) and 5 years (+0.041 [+0.013, +0.069]), and on the Brier score at both horizons. At 7 years the differences (+0.015 and −0.001) are better on the point estimate but their intervals include zero, so both lines fail; these are the 2 lines a point-estimate reading would pass (decision #35). Calibration fails at 3 and 5 years (slopes 1.345 and 1.273) and passes at 7 years (0.939), although that interval [0.72, 1.14] crosses both bounds. Top-decile lift is 3.96, so C4 passes, but the baseline's 3.35 would pass it too. The Track B model beats the base rates on 1,534 requests from 2017 (AUC 0.608 against 0.525; Brier 0.1475 against 0.1532).

![Figure 6](../figures/F5_auc_brier_by_horizon.png)

*Figure 6.* Time-dependent AUC and Brier score of the four Track A models at 3, 5 and 7 years, test cohort (n = 2,268), 95% bootstrap intervals.

**Discrimination fades with the horizon** (Figure 6). LightGBM's AUC falls from 0.858 to 0.766 and 0.672 at 3, 5 and 7 years, while the baseline's goes from 0.733 to 0.725 and 0.654. At 7 years Cox scores highest (0.696). Among the top 10% of LightGBM's list, 39.7% of requests operated within 5 years, and that 10% holds 39.6% of all 5-year operations, against 33.5% for the baseline's top 10%.

![Figure 7](../figures/F4_calibration_by_horizon.png)

*Figure 7.* Calibration by predicted decile: mean predicted against observed P(operation by 3, 5 and 7 years), baseline, logit and LightGBM, test cohort (n = 2,268), 95% bootstrap bands.

**The probabilities run high** (Figure 7). In LightGBM's ninth decile at 5 years it predicts 21.2% and 9.7% operate. A change after the training years explains part of it: 5-year completion fell from 12.8% for 2017 entrants to 8.3% and 9.6% for 2018 and 2019 entrants, while LightGBM's mean prediction stayed at 14.2%, 13.1% and 13.6%. Trees cannot extrapolate the request year beyond the training range (Figure 8). In PJM, LightGBM predicts 14.5% at 5 years and 9.4% operate. The simpler logit is the best calibrated model (slope 1.03 at 3 and 5 years).

![Figure 8](../figures/08_evaluate/08_14_by_entry_year.png)

*Figure 8.* Mean predicted against observed P(operation by 3 and 5 years) for each test entry year (n = 549, 672 and 1,047), four models, observed values with 95% bootstrap bands.

![Figure 9](../figures/08_evaluate/08_17_robustness.png)

*Figure 9.* LightGBM against the refitted baseline under five data versions: paired differences in concordance and Brier score and the calibration slope, Track A test entrants 2017–2019, 95% bootstrap intervals.

**Where the advantage comes from** (Figure 9). LightGBM wins 4 of 6 concordance and Brier comparisons in the main version and at least half of them under other ERCOT date treatments and with suspended requests counted as withdrawn, but 0 of 6 once requests under 20 MW are excluded. By region, the gain is largest in PJM (5-year concordance 0.784 against 0.691). In ERCOT the model's 3-year Brier score is worse than the baseline's (+0.004 [+0.001, +0.009]); in CAISO it wins 3 of 6 comparisons, on only 10 operations within 5 years. Without its own region in training the model misses the level badly: 2.5% predicted against 16.7% observed for ERCOT, 23.9% against 3.1% for CAISO. Adding the excluded post-entry columns would raise the 5-year AUC in CAISO and ERCOT from 0.715 to 0.990, which shows how much an evaluation that allowed them would overstate.

**Post-hoc analysis (after the registered scoring; decision #34).** I then compared five fixed candidates, the registered model and four repairs, and chose among them on 2016 entrants only. They were indistinguishable there (mean Brier 0.0994–0.0997; 12 of 12 paired intervals include zero). The chosen candidate, a blend of a logit and LightGBM fitted on congestion at entry with Cox, passes 5 of 10 Track A lines on the test cohort, against 6 for the registered model. Under decision #34 the registered result stands whatever the post-hoc result; here the repair did not do better either.

## 7 Explanation and what a developer or lender should do

![Figure 10](../figures/F6_hazard_ratios.png)

*Figure 10.* Hazard ratios with 95% intervals from the cause-specific Cox models for operation and withdrawal; reference request PJM, solar, 20–100 MW, NRIS; Track A entrants up to 2016.

The Cox models give the simplest summary (Figure 10). Relative to PJM, ERCOT requests reach operation at 1.66 times the rate [1.04, 2.64] and CAISO's at 0.52 times [0.43, 0.64]. Gas reaches operation at 2.56 times the rate of solar [2.19, 3.01] and withdraws at about the same rate (0.95 [0.90, 1.00]). Requests under 5 MW reach operation at 1.85 times the rate of requests of 20–100 MW, and those of 500 MW and above at 0.31 times. These ratios average effects that change over the wait.

![Figure 11](../figures/F7_shap_summary.png)

*Figure 11.* SHAP values of LightGBM's P(operation within 5 years) for 300 test requests against 100 background test requests; labels give each feature's mean absolute contribution in percentage points.

For the boosted model, I explained the whole hazard-to-probability chain with SHAP (Lundberg & Lee, 2017). State, size and technology move a request's 5-year probability most: 5.12, 3.68 and 2.95 points on average (Figure 11). The request year contributes 0.00, consistent with trees that cannot extrapolate it. In partial dependence (point estimates, no intervals), size is a smooth gradient, with ERCOT requests near 3 MW at 41.8% and near 1,000 MW at 7.4%, and no step at 20 MW (+1.8, +1.4 and +0.7 points by region); gas reaches operation more often than solar (24.3% against 10.7%).

I wrote down 6 facts from outside sources before looking, and the model recovered 2. It misses the region order (every test request moved to ERCOT, PJM and CAISO: 13.4%, 13.9%, 12.6%), most likely because state, which nests within region, carries the regional signal (mean absolute SHAP 5.12 against 0.44 for region). It also misses the 20 MW step and the lag of solar-plus-battery hybrids behind solar, and it gives crowding a positive effect in ERCOT and PJM. That last one is the congestion artifact: in PJM's training rows, crowded queues occur mostly late in a request's wait, when operation is more likely (Figure 12).

![Figure 12](../figures/09_explain_and_rank/09_09_congestion_confounding.png)

*Figure 12.* PJM fitting rows: median capacity waiting on the first day of each year in the queue, against the range at entry of PJM test requests (left), and the yearly hazard of operation (right); Track A entrants up to 2016.

For a book of 25 random 2019 requests, the model expected 3.0 operations within 5 years (90% range 1 to 6), the baseline 2.6, and 2 operated, ranked 2 and 3 by the model. Three worked examples show how to read a prediction:

- *Ranked first:* a 4 MW ERCOT solar request. Its chance was 32% / 38% / 40% at 3 / 5 / 7 years, against a 14% baseline, driven by its size (+15.9 points). It withdrew.
- *Moved up most:* a 0.8 MW PJM solar request, from baseline rank 12 to 3 (32% against 13%). It operated.
- *Ranked last:* a 1,568 MW CAISO request at 1% against a 9% baseline. It withdrew.

**What to do with this.** Use the model to order a portfolio and to decide which requests deserve early deposits and diligence, not as a probability to put in a financial model unadjusted. Calibrate the level to the most recent cohorts before pricing timing risk. For an ISO, the explanations matter more than the scores: they show which attributes go with attrition.

## 8 Broader impacts and ethics

A score like this can fulfill itself. If lenders refuse requests the model ranks low, those requests fail, and the next model learns that they fail. It also encodes the rules of the past: every test request entered the queue before FERC Order No. 2023 (Federal Energy Regulatory Commission [FERC], 2023) moved interconnection to cluster studies, so the model describes a regime that is ending. Small developers deserve particular care, because size is a top driver and the advantage over averages rests on small requests. A gatekeeper using the score to screen applicants would penalize small developers for a pattern partly made by rules. The ethical question I would put to a user is whether a statistical record of who got built should decide who gets to try. My answer is that it can inform portfolio choices but should not screen access to the queue.

## 9 Limitations and next steps

- The timing model covers three ISOs only, and it does not carry over to an ISO it has not seen.
- The 7-year horizon rests on 2017 entrants alone.
- Completion fell after 2017, and the trees cannot extrapolate the request year.
- The advantage over the baseline is largely confined to requests under 20 MW.
- Fitting on yearly congestion produces the congestion artifact.
- ERCOT's delayed entry leaves 98 of 732 training requests.
- LightGBM was tuned on 2016, so its 2016 checks are partly in-sample.
- Track B scores resolved requests only, which favors requests that finished quickly, and it misses the level in 4 of 9 regions.
- All test requests predate Order No. 2023.
- The public file has date gaps: ERCOT's withdrawals on one date, a block of PJM withdrawals on one day in December 2024 kept as recorded (decision #23), and withdrawn requests without a date left out of Track A.
- PJM's own commercial-probability model (PJM Interconnection, 2018) was planned as an external benchmark and not run, because its coefficients were not available to me (decision #36).

Next steps: recalibrate on recent cohorts, test a trend term once later cohorts mature, and try boosted survival models (Ishwaran et al., 2008; Pölsterl, 2020).

## 10 Conclusion

I asked whether a model can tell, on the day a request enters the queue, which proposed power plants will be built, and when. I framed it as supervised time-to-event learning with competing risks (operation, withdrawal, censoring), fitted on entrants up to 2016 and tested on 2,268 requests that entered the CAISO, ERCOT and PJM queues in 2017–2019. A discrete-time hazard model fitted with LightGBM ranked those requests better than region × technology averages at 3 and 5 years; its top 10% held 39.6% of the requests that operated within 5 years, against 33.5% for the averages. Three limits come with it: its probabilities run high because completion fell after the training years, its advantage rests on requests under 20 MW, and it does not carry over to an ISO it has not seen.

The evaluation design matters as much as the scores. I wrote the success criteria before scoring the test cohort and report the verdict as registered, 8 of 12 lines, with 95% bootstrap intervals on every metric. I kept post-entry information out of the features and measured what it would have done: the 5-year AUC in CAISO and ERCOT would rise from 0.715 to 0.990. Grouped cross-validation and a check on later entrants ranked the tuning settings nearly in reverse (Spearman −0.65), so I tuned on time, not on shuffled folds. The model is fit to order a portfolio, not to price one; its levels need recalibrating on the newest cohorts first.

## Statement of work

All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried out by Alan Mössinger.

## Changes after mentor feedback

Feedback items and the changes they led to are logged in `docs/mentor_feedback.md`.
