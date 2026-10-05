# Decisions

Numbered, never renumbered. Each entry: the choice, the reason, the
alternative rejected.

1. **No AI-use appendix; sole author** (2026-10-03). Alan Mössinger is the
   only author of every file. *Rejected:* a disclosure appendix.
2. **LBNL file frozen** at the through-end-2024 v2 release
   (`lbnl_ix_queue_data_file_thru2024_v2.xlsx`, SHA-256 in `src/config.py`).
   Switching to a newer release is Alan's call. *Reason:* every number must
   trace to one file. *Rejected:* auto-updating to the newest release.
3. **Git identity** Alan Mössinger; no trailers or attribution lines in
   commits.
4. **Suspended projects are censored** at 2024-12-31 in the main model; a
   sensitivity run treats them as withdrawn. *Reason:* suspension is
   reversible. *Rejected:* dropping them.
5. **Pre-registered success criteria** (Alan, 2026-10-04; written by the
   first cell of notebook 08 before any test data were read, and committed
   on its own before the first scoring run). Test sets: Track A requests
   entering 2017–2019 with outcomes through 2024-12-31; Track B resolved
   requests entering in 2017.
   *Primary models, named before scoring:* Track A — discrete-time LightGBM
   (`dt_lgbm`, lowest 2016 log loss in notebook 06); Track B — calibrated
   LightGBM (`lgbm_cal`). The discrete-time logit, Cox and the uncalibrated
   Track B models are reported beside them and decide nothing.
   *Benchmarks:* region × technology Aalen–Johansen cells (Track A, notebook
   05); region × technology base rates (Track B, notebook 07).
   - **C1** Uno's concordance index of P(operation by t), withdrawal as a
     competing event, above the baseline's at t = 3, 5 and 7 years.
   - **C2** IPCW Brier score below the baseline's at 3, 5 and 7 years.
   - **C3** Calibration slope between 0.9 and 1.1 at 3, 5 and 7 years.
   - **C4** Top-decile lift at 5 years ≥ 1.5: the share reaching operation
     within 5 years among the 10% of test requests with the highest
     predictions, divided by the share in the whole test cohort.
   - **C5** Track B, 2017 cohort: AUC above and Brier score below the base
     rate's.
   *"Beat"* (C1, C2, C5) means that the 95% percentile interval of the
   paired difference model − benchmark, from 200 bootstrap resamples of test
   requests (seeds 800 for Track A and 801 for Track B, recorded in
   `results/success_criteria_registered.json`), lies entirely on the better
   side of zero.
   *Thresholds* (C3, C4) are judged on the point estimate; the interval is
   reported. Each criterion × horizon is one PASS/FAIL line of
   `results/success_criteria.csv` (12 lines); point estimates are reported
   either way, failures are reported, not removed, and no criterion is
   changed after scoring.
   *Outcome and censoring:* for "operation by t" a request that withdrew
   before t is a known non-event; only requests still waiting on 2024-12-31
   before reaching t are censored, with inverse-probability-of-censoring
   weights from a Kaplan–Meier estimate of the censoring distribution. All
   censoring is administrative (2024-12-31), so that distribution is the
   distribution of the test requests' follow-up windows (2024-12-31 minus the
   request date), which is known at entry; every test request has at least
   five years, so the weights differ from 1 only at 7 years. The 7-year
   horizon is fully observed only for 2017 entrants; this is stated with
   every 7-year number, and the 7-year metrics are also reported for 2017
   entrants alone. *Change from the draft (journal, question 9):* the draft
   took the censoring distribution from the training set, whose requests
   have at least eight years of follow-up, so every weight would be 1 and the
   7-year metrics would silently drop the 2018–2019 requests still waiting.
   Changed before any test data were read.
   *Reported, not criteria:* Harrell's concordance, time-dependent AUC,
   calibration intercept and deciles, precision in the top 10%, metrics by
   region, the 7-year check on 2017 entrants, leave-one-ISO-out, the leakage
   ablation and the robustness reruns.
   *Rejected:* "beat" on point estimates (a difference inside the noise
   would count as a win); lift ≥ 1.5 × the baseline's lift (Alan, question
   9b).
6. **Timing model restricted to CAISO/ERCOT/PJM**, the regions whose public
   file carries event dates; Track B covers the other regions at the cost of
   timing. Stated as a limitation, as LBNL itself does. *Rejected:* imputing
   missing exit dates.
7. **No post-entry milestones** (study phase, IA date) in the main models;
   they appear only in the labelled leakage ablation.
8. **Data readiness GO/NO-GO** — first evaluation 2026-10-03: NO-GO, 13 of
   15 checks passed; both failures were thresholds, not data defects (CAISO
   withdrawal-date coverage 82.6% vs ≥ 83%; 2,292 test-cohort projects vs
   ≥ 2,500, with 304 completions vs ≥ 150). After Alan amended the two
   thresholds (#15) the gate reads **GO** (`docs/data_readiness.md`).
9. **EIA-860M through the EIA API** with a personal key kept in `.env`; the
   monthly XLSX is the documented fallback; EIA data are public domain.
10. **LBNL file obtained by hand and pinned by hash** (2026-10-03). The LBNL
    site refuses scripted requests, so the plan's manual fallback is the
    normal path: `get_lbnl.download()` uses the file in `data/raw/lbnl/`,
    verifies its SHA-256 and refuses to overwrite it. *Rejected:* working
    around the site's bot filter.
11. **Linkage quick test matches without dates** (2026-10-03). An LBNL
    project matches an EIA plant vintage on state, technology group, nameplate
    within ±15 % and at least one shared distinctive word of the project name;
    the operating month is compared only afterwards, so the agreement rate is
    a real test of the match. *Rejected:* matching inside the ±6-month window
    (agreement would be 100 % by construction); using the point-of-
    interconnection name (substation names produce false matches).
12. **Exploratory figures per notebook** (2026-10-03). Each notebook saves
    every figure it draws to `figures/<notebook>/`, with a caption stub in
    `report/figure_notes.md`, so the report's 6–8 figures can be chosen from a
    larger set. Report figures F1–F9 keep their names at the top of
    `figures/`.
13. **Environment** (2026-10-03). Python 3.11 in `.venv`, packages pinned in
    `requirements.txt`; notebooks run on a named kernel `queue-survival`
    registered from `.venv` (`make setup`), so a global Jupyter install
    cannot pick a different interpreter. `ipykernel` is pinned for that
    reason.
14. **Notebook 10 dropped** (2026-10-03). The pre-set linkage test failed
    (31.1% matched vs ≥ 40%; 74.9% agree vs ≥ 80%; `results/linkage_test.csv`),
    so, as PLAN.md §5.3 says, the EIA-860M linkage stretch is not attempted.
    *Rejected:* re-tuning the matcher until it passes — any new linkage test
    restricted to new solar/wind/battery projects would need its own bar set
    in advance.
15. **Two readiness thresholds amended** (Alan, 2026-10-03, after the first
    evaluation). Withdrawal-date coverage in each Track A region: ≥ 83% →
    **≥ 82%** (the 83% was the audit's rounded figure; CAISO has 82.6%).
    Held-out test cohort: ≥ 2,500 projects → **≥ 2,000** projects, still with
    ≥ 150 completions (the three ISOs hold only 2,313 rows that entered in
    2017–2019, so 2,500 was unreachable; the cohort has 2,292 projects and
    304 completions). The change is made after seeing the numbers and is
    stated as such in `docs/data_readiness.md`. *Rejected:* changing the test
    cohort to 2016–2019 entrants, which would take 2016 away from validation.
16. **Cleaning details beyond the rule table** (2026-10-03). R2 also clears the
    1970-01-01 placeholder in `ia_date` (56 rows); R7 keeps the copy of a
    duplicated key that has a request date and drops the other (1 row); text
    columns are stored as text in the parquet. The plan's ">5,000 MW: one
    row" is two rows; both are flagged, not dropped. *Rejected:* merging the
    two copies of the duplicate (it would invent a record).
17. **Outcome coding** (2026-10-03, `src/events.py`). Withdrawals dated after
    the censor date (175 rows, mostly early 2025) are censored at 2024-12-31,
    because the projects were still in the queue on that day; same-day exits
    count as one day. *Rejected:* counting them as withdrawals, which would
    use information from after the censor date.
18. **Survival estimates in numpy, bootstrap bands** (2026-10-03,
    `src/survival_tools.py`). Aalen–Johansen and Kaplan–Meier are written out
    in a few lines and tested against lifelines; bands are 500-resample
    percentile bootstraps with fixed seeds. *Reason:* the bootstrap refits the
    estimator tens of thousands of times. *Rejected:* lifelines'
    AalenJohansenFitter in the loop (it jitters tied times and is slower).
19. **Five-year views use 2000–2019 entrants** (2026-10-03, F3, F8, 03_05):
    every project then has at least five years of follow-up. Curves over time
    (F1, F2) use all entrants with censoring.
20. **`src/benchmarks.py` added** (2026-10-03): reads LBNL's summary sheets
    and recomputes them from the clean table (`results/benchmarks.csv`). Not
    in PLAN.md's module list; kept separate so notebook 03 stays short.
21. **ERCOT bulk withdrawal date → delayed entry** (found 2026-10-03,
    notebook 03; settled in notebook 04). 441 of ERCOT's 954 dated
    withdrawals share 2018-08-29 and none is dated earlier. **Main timing
    models: delayed entry** — ERCOT requests entering before 2018-08-29 join
    the risk set on that date (`entry_years`); those that had left by then drop
    out of fitting. **Sensitivity run: dates as recorded.** Track B and the
    evaluation are unaffected (a stamped withdrawal of a test project is a
    non-event at every horizon either way). ERCOT congestion before 2018
    stays overstated and is reported as a limitation.
    *How it was settled:* Alan approved delayed entry; I first argued for
    keeping the dates, because P(operation by t) from Aalen–Johansen is
    unchanged by misdated withdrawals and because no ERCOT training project
    would be seen in its first years. Notebook 04 tested both claims. Stamping
    PJM's withdrawals the ERCOT way left Aalen–Johansen unchanged but moved a
    discrete-time logit's P(operation by t) by up to 6.6 points; and fitting on
    entrants to 2015 and predicting 2016 entrants, delayed entry had the
    lowest error (2.4 points for ERCOT, vs 3.1 as recorded and 3.1 imputed),
    borrowing ERCOT's early years from PJM and CAISO through the shared
    year-in-queue effect (`results/ercot_treatment_validation.csv`).
    *Rejected:* as recorded (biased hazards); imputing stamped times from
    other regions (no better, adds noise); dropping the stamped rows (removes
    real failures, inflates ERCOT completion from 20% to 32%).
22. **Proposed online date out of the main models** (Alan, 2026-10-03). The
    stored `prop_date` looks updated after entry (notebook 01, figure 01_15),
    so `ambition_gap_years` is built in notebook 04 but used only in the
    labelled leakage ablation of notebook 08, alongside the IA date and study
    phase (decision #7).
23. **PJM's 2024-12-18 withdrawals kept as recorded** (Alan, 2026-10-03):
    456 PJM withdrawals share that date, which may be a real deadline of
    PJM's queue reform; nothing in the file says otherwise.
24. **Cox models: region as covariate, not strata** (2026-10-03, notebook
    05). PLAN.md §6 stratifies the cause-specific Cox models by region. With
    ERCOT's delayed entry (#21) every ERCOT training project enters the risk
    set at least 1.66 years after its request, so an ERCOT-only baseline
    hazard would have almost no one at risk in the first years and could not
    predict 3-year outcomes. Region therefore enters as indicators with a
    shared baseline, which also gives the region hazard ratios the plan's
    sign check asks for. Whether region's effect is proportional is tested
    with the Schoenfeld diagnostics; non-proportional effects are left to the
    discrete-time models of notebook 06, which give each region its own
    year-in-queue profile. *Rejected:* stratified Cox (ERCOT's early baseline
    not identified under delayed entry). The separate `hybrid` flag is left
    out of the Cox design because the Solar+Battery group already carries it.
25. **PH diagnostics on the as-recorded fit** (2026-10-03). lifelines cannot
    compute Schoenfeld residuals with delayed entry, so the proportional-
    hazards tests and plots use the same covariates fitted on the dates as
    recorded (the sensitivity version of #21).
26. **Discrete-time models: how delayed entry, years and features enter**
    (2026-10-04, notebook 06, `src/discrete_time.py`). (a) Under ERCOT's
    delayed entry (#21) a project-year is kept only if it *starts* on or after
    the entry time (`year − 1 ≥ entry_years`). Keeping the year that contains
    2018-08-29 would add 122 partly watched ERCOT years whose operation hazard
    is half that of full years (0.057 vs 0.125), and would let the stamped
    withdrawals back in, since their recorded exit *is* the entry time.
    ERCOT is left with 98 of 732 training requests (288 project-years).
    (b) The logit's "early" (years 1–3) interactions cover CAISO, technology and
    size but not ERCOT: no ERCOT training request is watched in its first two
    years, so that term would rest on a few rows (it pushed ERCOT's 3-year
    prediction to 0.5% in a first draft). (c) The logit pools years 8–10 into
    one effect (6% of project-years) and leaves out the hybrid flag, which the
    Solar+Battery group already carries (as in the Cox design, #24);
    LightGBM keeps both. (d) Predictions made at entry hold congestion at its
    entry value in every later year; the realised yearly value is used only in
    fitting and in a diagnostic. (e) The acceptance band check compares the
    models with Aalen–Johansen bands of the entrants they were fitted on (to
    2016), not with notebook 03's all-years bands, which contain the
    2017–2019 test outcomes. A new module rather than more functions in
    `survival_tools.py`, so notebook 08 can refit the models for its
    sensitivity runs. *Rejected:* the "year contains entry" rule (biased
    hazards); an ERCOT early term (not identified).
27. **LightGBM tuned on the 2016 cohort, not by grouped cross-validation**
    (2026-10-04, notebook 06). PLAN.md §6 chooses hyperparameters by 5-fold
    cross-validation grouped by project and uses 2016 only for early stopping.
    The grouped CV kept preferring ever larger trees and ended at the edge of
    two successive grids (64 leaves), while on the 2016 entrants — later in
    time than every fitting row — the 15 settings ranked nearly the other way
    (Spearman −0.65 between the two log losses; the CV's choice scores 0.6658
    on 2016, the best setting, 8 leaves and 331 rounds, 0.6493). Folds keep a
    project's years together but share calendar years, so the CV rewards
    learning events of particular years that do not carry forward. The tree
    setting and the round count are therefore chosen on the 2016 cohort,
    as the Cox penalty was in notebook 05; the CV curves stay in the notebook
    as the evidence, and the logit's penalty is still chosen by CV (its curve
    is flat around the choice). Cost: the 2016 calibration check is partly in-sample for
    LightGBM. *Rejected:* the CV's choice (worse forward in time);
    extending the grid further.
28. **ERCOT's band check uses its 2016 entrants** (Alan, 2026-10-04, after the
    first run of notebook 06). Notebook 06's acceptance check asks that the
    models' mean P(operation by 3/5/7 years) lie inside the Aalen–Johansen
    95% band of the entrants they were fitted on. PJM and CAISO pass that
    check; ERCOT failed it in 5 of 6 cases (logit 6.3% vs 12.2% observed by
    year 3), because under delayed entry (#21) the models never see ERCOT
    before 2018-08-29 and its 2005–14 entrants mostly completed before then;
    its 2015–16 entrants are matched (4.3% vs 4.3%). ERCOT is now checked on
    its 2016 entrants, predicted by the fits to 2015, where both models are
    inside the band at every horizon. The change is made after seeing the
    result and is stated as such in the notebook; the all-entrants ERCOT
    result stays in `results/dt_band_check.csv` (rows with `counts` = False)
    and in figure 06_13. The 2016 ERCOT cohort has 66 requests, so its band
    is wide (0–10.6% at 3 years) and the check is weak. *Rejected:* keeping
    the strict check as a documented FAIL (my recommendation); changing the
    ERCOT treatment (#21 stands, question 6).
29. **Track B: final models fitted on entrants to 2015, calibrated on 2016;
    the 2017 check moves to notebook 08** (2026-10-04, notebook 07). The
    isotonic map must be fitted on requests the models have not seen, so the
    final Track B models are the fits on entrants to 2015 and the map is
    fitted on the 2016 cohort; refitting on entrants to 2016 would leave no
    unseen cohort to calibrate on. PLAN.md §6 also asks notebook 07 to check
    AUC and Brier against the base rate on the 2017 cohort; that is the test
    set, so the check is made on 2016 in notebook 07 (both models pass) and on
    2017 in notebook 08, after its criteria are fixed. LightGBM is tuned on
    the 2016 cohort as in #27 (4 leaves, 243 rounds; grouped CV ranked the
    settings the other way, Spearman −0.85). *Rejected:* refitting on
    entrants to 2016 and calibrating in-sample; scoring 2017 in notebook 07.
30. **Isotonic calibration on bins of at least 50 requests**
    (2026-10-04, `src/track_b.isotonic`). Plain isotonic regression on the
    2016 cohort sent LightGBM's map to 100% above a raw score of 0.53 on the
    strength of nine requests, a value 29 test requests would have inherited.
    The map is now fitted on consecutive bins of at least 50 requests (mean
    score, share built, weighted by size) and interpolated between bins; the
    highest calibrated 2017 value is 44.1% (logit) and 40.2% (LightGBM).
    Calibration, scored cross-fitted on halves of the 2016 cohort, fixes the
    mean level (18.3% vs 18.4% built) but does not lower the Brier score;
    both raw and calibrated predictions go to notebook 08. *Rejected:* plain
    isotonic (unstable tail); Platt scaling (assumes a logistic shape the
    reliability diagram does not show).
31. **How notebook 08 scores** (2026-10-04, `src/evaluation.py`). Concordance
    for competing risks (Wolbers et al., 2014) with Uno's weights; time-
    dependent AUC with withdrawn requests among the controls (Blanche et al.,
    2013, definition 2); Brier score after Graf et al. (1999) with withdrawal
    as a known non-event; calibration slope and intercept from a weighted
    logistic recalibration; requests tied at the top-decile cut-off counted
    in proportion; the bootstrap holds the censoring weights at their full-
    sample values (they describe follow-up windows fixed by the request
    date). Two changes made after the first scoring run started, neither
    touching a registered number: that run stopped in the within-region
    section because a bootstrap resample made the recalibration fit singular
    (a region's baseline can take one value, or a resample separates the
    outcomes perfectly), so the fit now returns NaN when the maximum-
    likelihood estimate does not exist and intervals skip those resamples;
    and the "under 20 MW excluded" robustness run uses the size regime
    (first component's MW, as the features do) rather than total MW — changed
    before any robustness result existed. *Rejected:* scikit-survival's
    `concordance_index_ipcw` and `brier_score` (they treat withdrawal as
    censoring, which scores a different question).
32. **Point-estimate reading reported beside the registered verdict** (Alan,
    2026-10-04, after scoring). Alan's message "beat mean", read as asking
    that "beat" mean a better point estimate, arrived after the criteria were
    committed (0d5a47b) and scored. The verdict in
    `results/success_criteria.csv` stays the registered interval rule
    (decision #5); a column `point_estimate_reading` shows the point-estimate
    comparison for every "beat" line. They differ on 2 lines (C1 and C2 at 7
    years: better on the point estimate, FAIL by the interval). *Rejected:*
    switching the rule after seeing the results, which would turn two FAILs
    into PASSes.
33. **Explaining P(operation by t), not a yearly hazard** (2026-10-04,
    notebook 09, `src/explain.py`). SHAP values come from shap's permutation
    explainer applied to the whole chain of the discrete-time LightGBM (ten
    yearly rows → hazards → cumulative incidence), at 5 years, for 300 random
    test requests against 100 background test requests (two permutations,
    seed 9); size enters once, in MW, rounded so that 20 MW stays on the
    large-generator side (a floating-point slip caught by
    `tests/test_explain.py`); partial dependence sets one feature for every
    test request of a region. The sanity-check rules were written before the
    numbers were printed and are kept as computed (2 of 6 recovered); the
    diagnostics that explain the other four come after them. The 25-request
    book is drawn at random from 2019 entrants (seed 2019) and the three
    worked examples are chosen by rule. *Rejected:* TreeExplainer on one
    yearly hazard (it does not explain the probability a user reads); exact
    Shapley values (2⁹ coalitions × background, too slow).
34. **Post-hoc improvement analysis, notebook 08b** (Alan, 2026-10-05, after
    notebook 08 had been scored; written by the first cell of notebook 08b
    and committed on its own before any candidate was fitted). The
    registered verdicts of decision #5 stand; everything in notebook 08b is
    labelled post-hoc.
    *Aim:* the failures found in notebooks 08–09 — calibration slope 1.34
    and 1.27 at 3 and 5 years, PJM over-prediction with the congestion
    artefact of figure 09_09, and the 7-year horizon, where Cox ranks best.
    *Candidates (fixed list):* K0 the main discrete-time LightGBM
    (reference); K1 LightGBM fitted with congestion held at its entry value
    in every project-year, as at prediction; K2 a blend of the main
    discrete-time logit, Cox and LightGBM, weights ≥ 0 summing to 1 on a 0.1
    grid, chosen per horizon; K3 the main LightGBM after a logistic
    recalibration (intercept and slope on the logit scale) per horizon; K4 a
    blend as in K2 of the entry-congestion logit and LightGBM with Cox.
    Model settings are notebook 06's and notebook 05's; nothing else is
    tuned.
    *Choice, on the 2016 cohort only:* every component is fitted on entrants
    to 2015 and predicts the 2016 entrants (all followed for at least eight
    years, so no censoring weights are needed); blend weights and
    recalibrations are fitted on those 2016 predictions and their 2016 score
    is cross-fitted on two halves (seed 34). The candidate with the lowest
    mean Brier score over 3, 5 and 7 years is chosen; K0 stays unless another
    candidate is lower.
    *Final model:* the chosen candidate's components refitted on entrants
    to 2016, with weights or recalibration fitted on all 2016 predictions of
    the fits to 2015; scored once on the 2017–2019 test cohort with notebook
    08's metrics, seed and criteria rules (`results/posthoc_criteria.csv`).
    All five candidates are also scored on the test cohort, in a table
    marked "not used for the choice".
    *Not attempted:* a trend term for the slowdown of 2018–2019 entrants —
    it happened after the 2016 validation year, so no choice about it can be
    made without the test years.
    *Rejected:* choosing among candidates on the test cohort; any change
    after the post-hoc test scores are seen.
