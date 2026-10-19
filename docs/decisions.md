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
35. **"Beat" stays the registered interval rule** (Alan, 2026-10-05,
    question 10). Confirms #32: the verdict in `results/success_criteria.csv`
    is the 95% paired-bootstrap interval rule of decision #5, and the
    `point_estimate_reading` column stays beside it. The report gives the
    registered count and names the two lines (C1 and C2 at 7 years) that are
    better on the point estimate but fail by the interval. *Reason:* the rule
    was committed before scoring; changing it afterwards would turn two FAILs
    into PASSes after seeing them. *Rejected:* the point estimate as verdict.
36. **PJM (2018) commercial-probability benchmark dropped** (Alan,
    2026-10-05, question 12). PLAN.md §6 lists it for notebook 08, but its
    coefficients and method document are not available to the project, so it
    was never run. The report says that it was planned and not run, and lists
    it under limitations. *Reason:* a re-estimated stand-in would not be
    PJM's model and could not be called that benchmark. *Rejected:*
    approximating the benchmark from its general description.
37. **Poster, not video** (Alan, 2026-10-05; PLAN.md §8b). The final
    presentation is `poster/poster.pptx`, built after the report draft and
    mentor feedback, from the report's figures and `results/`. *Rejected:*
    the 4-minute video.
38. **`report/report.md` only for now** (Alan, 2026-10-05). pandoc is not
    installed, so `make report` (report.md → report.pdf) is not run; the
    Markdown file is the draft of record and the PDF build is a later step.
    *Rejected:* installing system software from a working session.
39. **How the report is built and checked** (2026-10-05, report draft v1).
    (a) Every number the report cites comes from `results/report_numbers.csv`,
    written by `src/report_numbers.py` (`make numbers`) from the result
    tables, with the source file of each value; design constants (horizons,
    the 20 MW step, bootstrap settings, model settings) are traced the same
    way. `tests/test_report.py` fails if a number in `report/report.md` is
    not in that table, ignoring calendar years and labels (figure, decision,
    criterion and rule numbers). The 90% range of operations in the 25-request
    book is computed exactly (Poisson-binomial), not by simulation, so it does
    not depend on a seed; it equals notebook 09's simulated range (1–6).
    (b) Word count: everything from the title to the end of the mentor-
    feedback section, including captions and lists, excluding references and
    appendices; the test fails above 3,000.
    (c) Figures: F1, F3, F8 (data), 08_12, F5, F4, 08_17 (evaluation), F7
    (explanation). F2 and F6 are left out to stay at eight; their findings
    appear as numbers in the text.
    (d) Alan asked for the data-science steps to be explicit (gathering,
    EDA, features, supervised models with hyperparameters and how they were
    tuned, metrics); the report says plainly that no unsupervised method was
    used. *Rejected:* typing numbers into the report by hand; counting
    captions out of the limit.
40. **Word and figure limits relaxed for draft v1** (Alan, 2026-10-05).
    The 3,000-word limit and the 6–8 figure plan are set aside for now, so the
    draft can carry the data-science detail Alan asked for and all of F1–F8
    plus 08_12, 08_14, 08_17 and 09_09 (12 figures). The word-count test in
    `tests/test_report.py` is skipped, not deleted, with this decision as
    its reason; it must pass again before the final report, which means
    cutting the draft (moving detail to the appendices) later. This
    supersedes 39(b)–(c) for the draft. *Rejected:* cutting now, before
    mentor feedback shows which parts matter.
41. **PDF build: pandoc 3.12 with the Typst 0.15.1 engine** (Alan,
    2026-10-05; supersedes #38). Both installed with winget (system tools,
    not Python packages, so `requirements.txt` is unchanged). `make report`
    runs `make numbers`, then joins `report/report.md`,
    `report/references.md` and `report/appendix.md` into `report/report.pdf`.
    The appendices moved out of `report.md` into `appendix.md` so the PDF
    has references before appendices; `tests/test_report.py` checks the
    numbers in both files. Implicit figures are turned off so pandoc does not
    add a second caption under each figure. The PDF is git-ignored because
    it rebuilds from the sources. *Rejected:* a LaTeX engine (a large
    install for the same result).
42. **v3 scope: a portfolio-management report backed by data science**
    (Alan, 2026-10-06). The report must let its reader decide which
    requests to back, where, and how to build a book. It answers six
    questions (prediction quality; each request's probability and why;
    what a request should have different and the constraints; how to
    reduce them; the right book per region; what an energy company should
    do), each tied to a notebook: 11 fair baseline and utility-scale
    cohort, 12 level repair, 13 ISO queue files, 14 landmark models, 15
    value and cost, 16 portfolio (scorecards, what-ifs, simulated book,
    budget-constrained choice, backtest), 17 constraints and levers, 18 v2
    evaluation. New criteria C6–C12 are written before scoring
    (`results/success_criteria_v2.csv`, notebook 11's first cell). The v1
    pipeline and its registered verdict (8 of 12) are untouched. Source:
    the review doc "Queue Survival — Report Review and Portfolio Upgrade
    Plan" (2026-10-06), checked against `results/`: requests ≥ 20 MW are
    81% of the test cohort by count (the doc said two-thirds) and 98.9% by
    MW; unused entrants from 2020 on number 6,122 in the three ISOs and
    15,715 overall (the doc said 5,800). *Rejected:* filling the doc's
    empty sections instead of changing the repository; starting the
    must-fix items without a plan.
43. **LBNL 2026 file added alongside the frozen 2025 file** (Alan,
    2026-10-06; refines #2). Alan downloads it by hand (the site returns
    403 to scripts). Notebook 01b reconciles the two editions and computes
    the 2020–2022 entrants' 1- and 2-year incidence for the level check in
    notebook 12. No registered model is fitted or scored on the 2026 file;
    the 2025 hash stays the basis of every result. *Rejected:* keeping the
    2025 file alone (loses the newest hazards); switching to the 2026 file
    (changes every number and breaks the registered verdict).
44. **Word, figure and page limits off for report v2** (Alan, 2026-10-06;
    supersedes #40 for v2). The report is as long as the six questions
    need; `tests/test_report.py`'s word-count test stays skipped with this
    decision as the reason. *Rejected:* a 3,000-word report that drops
    the portfolio layer.
45. **`geopandas` added** (2026-10-06) with `shapely`, `pyproj` and
    `pyogrio`, for the F9 project map (notebook 03b) and the region
    playbook maps (notebook 17). Positions come from Census county
    centroids (91% of requests carry a FIPS code) and EIA-860M coordinates
    for the operating fleet. *Rejected:* a state choropleth only (hides
    where in a state the queue sits); plotly (not in the stack, no SVG
    export matching `src/plots.py`).
46. **Portfolio defaults and the Bayesian stretch** (Alan, 2026-10-06).
    For notebook 16 the book budget is a deposit budget equal to the median
    2019 book of 25 requests, with caps of 50% per region and 60% per
    technology; both are swept in a sensitivity table. The PyMC discrete-
    time hazard with a random walk on the cohort intercept (notebook 12,
    option c) is wanted as a stretch item once option (b) passes its check.
    The ERCOT and CAISO capacity-value proxies are proposed in notebook 15
    with their sources and confirmed by Alan before the value table is
    fixed. *Rejected:* fixing the value proxies now, before the sources are
    read.
47. **Report title: "From Queue to Grid: AI-Driven Portfolio Management for the U.S. Power-Plant Pipeline"** (Alan, 2026-10-06). The title
    names the subject (portfolio management) and the method (AI, meaning
    the machine-learning models of notebooks 06, 11–16); "Queue Survival"
    stays as the repository's short name. Chosen from four options for
    being conventional enough for a course report while leading with the
    decision. *Rejected:* "Betting on the Grid" (the recommendation; more
    hook, less formal), "2,100 GW Are Waiting" (a number as the hook),
    "Which Power Plants Will Actually Get Built?" (close to the old title).
48. **The LBNL 2026 data file is on disk, and what it changes** (2026-10-06;
    refines #43). Downloaded with Alan's permission from the links on
    https://emp.lbl.gov/queues together with the June 2026 slide report;
    both checksummed. The data file is licensed CC BY 4.0 (LBNL and
    GridTracker), which the 2025 page did not state; it stays out of git
    like all of `data/raw/`. Layout differences are mapped in
    `config.LBNL_2026_RENAMES`. Two findings for the plan: (a) MISO and SPP
    now carry event dates for most operations and withdrawals, so a timing
    model for them is possible on the 2026 file — not under the registered
    v1 verdict, which stays on the 2025 file, but as a separately
    registered v3 extension (**ASK ALAN**: extend Track A to MISO and SPP
    on the 2026 file, with its own criteria, or keep them as Track B); (b)
    ERCOT's withdrawal dates are far less complete in the 2026 file (49%
    against 100%), so the 2026 file cannot simply replace the 2025 file for
    ERCOT, which supports #43's "alongside" choice. *Rejected:* switching
    the registered pipeline to the 2026 file.
49. **MISO and SPP timing models as a registered v3 extension** (Alan,
    2026-10-06; follows #48). Notebook 19 fits the fair baseline, the
    discrete-time logit and LightGBM for MISO and SPP on the 2026 file
    (censor 2025-12-31), with criteria C13–C14 written to
    `results/success_criteria_v3.csv` before scoring, and reports them
    beside, never pooled with, the three-ISO results on the 2025 file.
    ERCOT is not refitted on the 2026 file because its withdrawal dates
    are 49% complete there. *Rejected:* a sensitivity run without criteria
    (weaker claim for the same fitting work); keeping MISO and SPP in
    Track B (ignores dates that now exist).
50. **Figure footnotes name the author** (Alan, 2026-10-06). Every figure's
    source line now reads "Figure: Alan Mössinger. Data: LBNL Queued Up:
    2025 Edition (Rand et al., 2025). [EIA-860M …] Cohort: …" instead of
    "Source: …; author's analysis", so authorship is explicit on the figure
    itself; the data credit stays, as the course requires. One constant in
    `src/config.py`; all figures re-rendered. *Rejected:* keeping the
    anonymous "author's analysis" (Alan found it read as if the figures
    came from elsewhere).
51. **Build order: the full v3 pipeline first, then the calendar** (Alan,
    2026-10-06). Notebooks 11–19 and 01b are built in sequence in
    continuous sessions, each executed and checked before the next, with
    stops only at the ASK ALAN items; the week-by-week calendar in
    `PLAN.md §2` becomes the order of work, not the pace.
52. **Pre-registered v2 success criteria C6–C12** (Alan, 2026-10-06; written
    by the first cell of notebook 11 before any test metric of v2 existed).
    Primary cohort: test requests of 20 MW and more; the v2 model is the
    candidate with the lowest 2016 log loss on ≥ 20 MW project-years,
    chosen before the test cohort is scored (rule in
    `results/success_criteria_v2_registered.json`). Lines: C6 Uno's C and
    Brier vs the fair baseline at 3 and 5 years; C7 calibration slope
    0.8–1.2 and intercept covering 0 on 2018–2019 entrants after the level
    repair; C8 landmark models beat the entry model on the same risk set;
    C9 and C10 the model-chosen book delivers more realised MW and value
    than the fair-baseline book in the backtest; C11 the simulated band
    covers the realised MW; C12 the leakage guard holds. Scored in notebook
    18; failures are reported, not removed; the v1 verdict (decision #5) is
    untouched. *Rejected:* scoring the ≥ 20 MW cohort against the v1
    baseline only (that is the comparison a size lookup would pass).
53. **ISO-native queue files: what could be obtained** (2026-10-06).
    `gridstatus` 0.36.0 added (pinned) for the ISO queue snapshots. CAISO's
    public queue report came through (2,278 rows, 2026-10-06 snapshot,
    `data/raw/iso/`): every 2017–2019 LBNL CAISO request is found by queue
    ID; it carries the cluster, study-phase *statuses*, agreement status,
    withdrawal and completion dates, but no phase dates. PJM's export
    endpoint and ERCOT's report servlet are unreachable from this machine
    (connections refused from both the shell and the browser pane; not a
    bot check), and PJM's API route needs a personal Data Miner key.
    Notebook 13 therefore builds the milestone table from the CAISO
    snapshot and the two LBNL editions' interconnection-agreement dates
    (2,508 more in the 2026 file) and phase reached; notebook 14's
    landmarks are entry, +12 and +24 months with the dated agreement, and
    the agreement date itself. Phase reached is undated in every source and
    is kept out of the landmark features (it would be post-outcome
    information). If Alan can fetch PJM's queue export and ERCOT's GIS
    report from his side, notebook 13 gains dated study phases for PJM and
    ERCOT and is rerun. *Rejected:* registering for a PJM API key on Alan's
    behalf (an account is his to create).
54. **Pre-registered criteria C13–C14 for the MISO and SPP timing models**
    (2026-10-06; written by the first cell of notebook 19 before any MISO or
    SPP model was fitted; follows #49). Data: the 2026 LBNL file censored at
    2025-12-31; one model per region (region pooled, state target-encoded),
    notebook 06's settings unchanged, fitted on entrants to 2016, scored on
    2017–2019 entrants. C13: LightGBM beats the fair baseline (region ×
    technology × size) on Uno's C and Brier at 3 and 5 years, per region,
    with the 95% paired interval on the better side. C14: LightGBM's
    calibration slope interval within 0.8–1.2 at 3 and 5 years, per region.
    Twelve lines; failures reported, not removed; never pooled with the
    three-ISO verdict. MISO's operation-date coverage (92%) is below the
    95% notebook 01 asked of the 2025 file and is stated as a caveat.
55. **The registered backtest is a tie, and an exploratory book is added
    beside it, labelled** (2026-10-06). Under criteria C9–C10 as registered
    (expected-value objective, a deposit budget equal to the median
    25-request 2019 book, 50% region and 60% technology caps), every
    optimising chooser — the model, raw or level-repaired, the fair
    baseline and the v1 baseline — fills the budget with the same few very
    large gas and offshore-wind requests, because value per MW and MW per
    dollar of deposit dominate the probability; all four realised the same
    1,035 MW within five years, so the paired differences are zero with
    one-sided intervals and both lines fail as registered. Notebook 16
    reports that verdict unchanged and adds, after it and marked
    "exploratory, not registered", a count-limited book: the 25 requests
    of 20 MW and more with the highest P(operation by 5 years) under each
    chooser, scored on operations and MW realised, with the same paired
    bootstrap. It answers whether the ranking matters in a decision frame;
    it decides nothing about C9–C10. *Rejected:* changing the registered
    objective after seeing the result.
56. **Reform and equipment scenarios are stated multipliers, not
    estimates** (2026-10-06). Notebook 17 applies named scenarios (cluster
    reform speeds studies 0.9/1.1/1.3; reform raises withdrawals 0.8; gas
    backlog, a two-year delay on gas MW; the post-2020 level, 0.3 from
    notebook 12) to the sample book's incidence curve. The multipliers are
    assumptions with ranges, because every test request predates Order No.
    2023 and the post-reform regime is not observable; the one scenario
    with a measured basis (the post-2020 level) is the largest.
    *Rejected:* fitting a reform effect on data that cannot carry it.
57. **PJM's queue export and ERCOT's GIS report: joined, and neither adds a
    landmark** (2026-10-08). Alan fetched both files from another network
    on 2026-10-07 (`data/raw/iso/`, SHA-256 recorded; `src/iso_files.py`).
    Notebook 13 joins them and measures what they date after entry for the
    2017–2019 cohort. PJM's export finds 94.5% of the cohort and agrees
    with the LBNL PJM request, withdrawal and in-service dates on the same
    day for every shared request, but dates no study and no agreement: each
    phase is a status with a PDF link, and the status is October 2026's,
    so it carries the outcome. Its backfeed dates come a median 0.27 years
    before operation and are often planned dates. ERCOT's report dates every
    phase but lists only requests still active (or inactive / cancelled in
    the month); none of the cohort's 92 operations or 223 withdrawals is in
    it, so its dates are observed only for survivors. The milestone table
    is therefore unchanged and PJM's dated phases remain the open gap.
    *Rejected:* using PJM's agreement status or ERCOT's phase dates as
    landmark features (both would carry the outcome; C12); parsing the 158
    executed-agreement PDFs the public web archive holds (63 for the
    1,465 PJM test requests, a selected sample, coverage from about 3% to
    about 7%).
58. **Pre-registered criteria C15–C17: the milestone-managed book and the
    level at the landmark** (2026-10-08; written to
    `results/success_criteria_v4.csv` and committed before notebook 20 ran
    any test). *Pool:* Track A test entrants 2017–2019 of 20 MW and more
    still in the queue two years after the request (notebook 14's +2 risk
    set). *Decision:* keep N requests, N = 25 and 50, no region above 50%
    of N, ties broken by a fixed random order shared by every chooser.
    *Choosers* (each ranks by P(operation within 3 years of the landmark)):
    M, the landmark model (notebook 14's "agreement updated" view, chosen
    there as the best view before this test); LA, the agreement-aware
    lookup (region × technology × size cells, fitted separately on training
    requests with and without an agreement known at the landmark); E, no
    re-scoring (the fair baseline's entry P(operation by 5 years)). The
    plain lookup at the landmark is reported, not registered, because C8
    already showed M beats it. *Outcome:* operation within 3 years of the
    landmark (all observed by end-2024) and its MW. *Test:* 200 resamples
    of the pool, books re-chosen in each, paired 95% percentile interval.
    C15: operations, M vs LA and M vs E, N = 25 and 50 (four lines). C16:
    MW, the same four. C17: M's level repaired with an intercept fitted on
    early outcomes dated before the landmark (cohort c's 1-year and cohort
    c − 1's 2-year operations against the landmark model's entry view), the
    calibration intercept at 3 years from the landmark covers 0, on the full
    +2 risk set and on ≥ 20 MW (two lines). Pass: the interval entirely on
    the better side (C15, C16) or covering 0 (C17). *Thesis rule, fixed
    now:* the stronger thesis — a model-managed book beats a careful
    analyst's lookup at the milestone — is supported only if both C15 lines
    against LA pass; otherwise the report keeps the current thesis.
    *Rejected:* comparing only with the plain lookup (it does not know the
    agreement, so the model would win on information the analyst also has);
    choosing the view, N or the cap after seeing a book.

59. **v4 scope: From Queue to Capital, at capstone scale** (2026-10-12;
    Alan's direction of 2026-10-11/12, PLAN.md §13). The report becomes one
    narrative for an energy company that owns a book of queue requests,
    organised as six engines feeding one capital-allocation decision: market
    intelligence, development forecasting, asset economics, risk, spatial
    (state level only), portfolio optimisation. Everything already built is
    kept; additions go into the notebooks that own the topic (03, 03b, 08,
    08b, 09, 15, 16, 20), each as an explained section; no new notebooks; no
    appendix. Added: a project NPV from the value table and NREL ATB costs
    (one new public file); stage-gate rules G1 and G2 with
    `V = −cost_to_next_gate + P × NPV`; expected shortfall of book NPV; four
    allocation policies compared on 2017–2019; state archetypes; a tournament
    of other learners under criteria C18–C19 registered first. *Reason:* the
    v2 report was organised as a contest between the model and a lookup,
    which turned usable findings into "the answer is nothing"; the company's
    questions are decisions, and each needs a probability, a value, a cost
    and a downside behind it. *Rejected:* new notebooks 21–23 (the work has
    owners already); request-level k-means archetypes (they recover
    region × technology cells and decide nothing); nodal prices, weather,
    land, transmission and financing data (not obtainable by December 14;
    stated as out of scope); multistate models (PJM has no dated stages);
    cutting the v2 report to 3,000 words without changing its organisation.

60. **NREL ATB 2024 added as the cost source for a project NPV** (2026-10-12;
    notebook 15 §8, PLAN.md §13). One public file (5 MB parquet, source S12
    in `data/README.md`) gives overnight capital cost, fixed and variable
    O&M and heat rate per technology. The NPV per MW is the simplest project
    DCF: 20-year life from the operation date, revenue from the existing
    value table, 8% real discount rate (6% and 10% as cases), gas fuel from
    heat rate × a gas-price assumption, no financing, tax or degradation.
    *Reason:* the value index of notebook 15 had no capital cost, so a large
    request always looked worth more and a battery worth nothing; the gates
    of notebook 16 need a sign and an order that include what a plant costs.
    *Rejected:* a full financing model (data the public files do not hold;
    out of scope for a capstone); the ATB's R&D case (the Market case is the
    one investors see); typing CAPEX by hand (the rule is that every cost
    is parsed from a file or listed as an assumption with a range).

61. **Practice-grade valuation: the ATB cost of capital, a contracted case,
    and a hurdle that falls with risk** (2026-10-12; Alan's "go" after the
    market-practice note in the journal). (a) The NPV discounts operating
    cash flows at the technology's real WACC from the ATB 2024 Market
    financing case (4.2% solar and hybrids, 4.9% wind, 5.2% offshore, 5.4%
    gas; storage takes the solar rate, "Other" the median), with 8% kept as a
    stress case; the chance of never reaching operation is carried as a
    probability by the gates, not as a higher rate. (b) A **contracted**
    revenue case runs beside the merchant one: a 15-year PPA at index-level
    prices (solar $57, wind $62, hybrids $70, offshore $110 per MWh, ±$10;
    assumptions at the level of public North American PPA indices for 2024,
    to verify) replaces the merchant energy term for solar, wind, hybrids
    and offshore wind; gas, storage and "Other" stay merchant. (c) The
    hurdle on the margin is 3 at entry and 2 two years in (both reported at
    2, 3 and 5). Every gate, policy and book number is computed for both
    revenue cases; the report shows both and treats the merchant case as the
    floor. *Reason:* no developer underwrites on merchant on-peak prices,
    and an 8% flat rate was three points above the market's cost of capital,
    which pushed solar below zero everywhere. *Rejected:* a single blended
    rate (hides the technology difference the ATB documents); a merchant-only
    report (the contract is where the sign of solar is decided).
62. **v5 scope: an integrated U.S. energy portfolio, with the queue models as
    its timing engine** (2026-10-12; Alan's direction, PLAN.md §14). The
    capstone extends from a book of interconnection-queue requests to a real
    integrated U.S. energy portfolio: 20 federal offshore Gulf of Mexico
    oil-and-gas lease redevelopments (BSEE OGOR-A production, a modeled
    redevelopment against an Arps baseline) and 20 ERCOT power candidates
    anchored to real queue requests of the 2017–2019 cohort (5 gas
    combined-cycle, 5 solar, 5 wind, 5 storage), under joint price, output,
    cost and timing uncertainty. Everything built stays: the entry, landmark
    and managed-book models become the completion and timing engine of the
    power candidates, and every registered verdict C1–C19 is untouched.
    Added: an LLM advisor (Anthropic API, key in `.env`, never printed)
    grounded only in result tables, with a recommend mode, a challenge mode
    built from Alan's two prompts (motivated-reasoning check, ideological
    Turing test) and a decision gym scored against realized NPV, with a
    replay mode that re-serves recorded answers so the pipeline runs offline;
    a Streamlit dashboard that reads `results/` only; the 22 notebooks
    consolidated into 10 story notebooks (merge map in PLAN.md §14) with
    every result table byte-identical after the merge (tournament tables
    within 1e-16) before any v5 line is written; figures drawn by named,
    documented functions with a provenance footnote (OBSERVED / DERIVED /
    FORECAST / ASSUMED); the report reorganised as an executive, data-science
    and portfolio report that opens with a one-page Capital Allocation Memo
    and the Decision Board. Self-reuse from Alan's other repositories
    (Forecast to Dispatch: ERCOT 2024 hourly prices and the battery dispatch
    LP; MADS_Milestone2: the ERCOT Public API client; the net-load
    repository) is credited in the statement of work. New criteria C20–C24
    are registered before scoring. *Reason:* the proposal of 12 Oct widens
    the decision to the capital allocation an energy company actually makes
    across sectors, and the queue work is the piece no public portfolio study
    has — a modeled chance that a power asset never arrives, or arrives
    late. *Rejected:* a new repository (the timing engine and its registered
    record would have to be rebuilt or cited at arm's length); a synthetic
    portfolio (every candidate is anchored to a real lease or request, and
    modeled costs are labelled as such); an advisor free to use its own
    knowledge (every number must come from a result table and is checked by
    code); large candidate counts (forty show the method and keep the gym
    scorable).
63. **The 22 notebooks consolidated into the story layout, with the result
    tables as the gate** (2026-10-12; PLAN.md §14, Alan's merge map). Seven
    notebooks exist after the merge — `01_problem_and_data` (01, 02, 01b),
    `02_eda` (03, 03b), `03_statistics_and_features` (04),
    `04_forecast_queue` (05, 06, 07, 11, 12, 13, 14, 19),
    `06_evaluation_record` (08, 08b, 09, 18), `07_economics` (15),
    `09_portfolio` (16, 17, 20) — and 05, 08 and 10 are the v5 additions.
    Each old notebook became a lettered part with its own setup, sections,
    Reading-this cells and takeaways; the part header names the notebook it
    was; `NOTEBOOK` constants and figure folders carry the new names. Three
    sections changed notebook because a merged notebook must not read a
    file a later one writes: the early incidence of the 2020–2022 entrants
    (01b §5, which needs the Track A sample of 03) sits in 04 next to the
    level repair that uses it; the labelled leakage ablation (08 §9, the
    ceiling of the C12 guard) sits in 04 ahead of the landmark models; the
    ten entry rules (09 §4b, read by the entry gate) sit in 04 ahead of the
    portfolio. Notebook 17 went whole into 09 because its scenarios are
    multipliers on the simulated book of 16. The notebooks are numbered by
    the story and `make all` runs them in dependency order — 06, the
    record, runs last because it reads every scored table. *Gate:* `make
    all` before and after the merge from the raw files, every file in
    `results/` byte-identical except the tournament tables, which are
    identical within 1e-16 (`report_numbers.csv` is rebuilt by `make
    numbers` and changes only its `source` column); the test suite green;
    old notebooks and their figure folders deleted in the same commit.
    *Rejected:* moving the record into 09 to keep a numeric run order (the
    record would no longer hold every criterion); renumbering so that the
    run order is numeric (the numbers are the plan's); leaving the old
    notebooks beside the new ones (dead files).
64. **The v5 energy sources, their gate, and the provenance rule** (2026-10-12;
    notebook 01 parts D and E, PLAN.md §14.1–14.2). Six public sources join
    the queue file: BSEE OGOR-A production 2010–2024 (S13, fifteen delimited
    files), EIA-923 plant × fuel × prime-mover generation for Texas 2018–2024
    through the EIA API (S14; the bulk workbooks returned HTTP 503), the EIA
    WTI and Henry Hub monthly spot workbooks (S15), the five ERCOT 2024 files
    of my Forecast-to-Dispatch pull copied with pinned hashes (S16), eGRID2023
    (S17) and the BLS CPI-U series for real 2024 dollars (S18; FRED refused
    the connection, the BLS public API did not). Every file is hashed in
    `data/raw/manifest_v5.json` with URL, retrieval date, vintage, units and
    grain. Tables keep the publisher's grain: lease-month, plant × prime
    mover × month (fuel-specific rows summed, EIA's subtotals dropped, never
    split to generators), month. Audits R10–R13 count and never change rows.
    *The ERCOT price* is one series with three labels: 2024 observed (DAM
    North hub monthly mean), 2017–2019 derived (ICE North peak annual means
    repeated by month), 2020–2023 assumed (PJM West × 0.77, the value layer's
    assumption) until the hourly 2018–2023 pull runs from a network ERCOT's
    edge accepts (`python -m src.ercot_api 2018 2023`); the gate reports that
    line as FAIL and non-blocking, as the plan allowed. *Provenance rule:*
    every v5 figure prints one of OBSERVED, DERIVED, FORECAST, ASSUMED in its
    source note (`plots.finish(provenance=…)`, asserted by a test); a figure
    that mixes labels carries the weakest of them and the subtitle says which
    part is which. *The gate:* twelve blocking lines pass (coverage
    2018-01→2024-12 for every monthly series; 1,041 leases with sixty or more
    producing months against a minimum of 20; Texas plants with 36 months of
    generation: gas CC 69, solar 108, wind 201, storage 18 against a minimum
    of 5 each; eGRID joins 98.8% of the plants generating in 2023; manifest,
    audits and secrets) — GO. The first evaluation read NO-GO on the eGRID
    line because I had specified it against every plant in the 2018–2024
    panel, which includes the 122 Texas batteries that first reported in
    2024 and cannot be in a 2023 file; the line was re-specified to the
    plants generating in 2023 and the correction is recorded here, as
    decision #15 did for the v1 gate. *Rejected:* a typed CPI deflator (an
    observed series was reachable); monthly ERCOT prices for 2020–2023 from
    any other proxy (the existing assumption is already cited and the hourly
    pull is one command away); splitting EIA-923 to generators with EIA-860M
    shares (the proposal's own warning); pulling EIA-923 for every state now
    (one call per state when the all-region candidates of §14's addendum are
    built in notebook 07).
65. **`statsmodels` and `xlrd` added** (2026-10-12; notebooks 02 part C and
    03 part B). `statsmodels` 0.14.6 for the ADF and KPSS stationarity tests
    and the OLS behind the Chow break test (`src/energy_stats.py`); `xlrd`
    2.0.2 because EIA's monthly spot-price workbooks are `.xls` files that
    pandas cannot read without it (it was already present as a transitive
    dependency and is now pinned because it is relied on). *Rejected:* hand
    implementations of the unit-root tests (critical values are tabulated
    and easy to get wrong); converting the `.xls` files by hand (the raw
    layer is never edited).
66. **Pre-registered criterion C20 and the split protocol of the energy
    forecasts** (2026-10-12; written by notebook 03 part B's first cell to
    `results/success_criteria_v6.csv` and committed before notebook 05 ran
    any model). *Targets:* lease oil and gas output 3, 6 and 12 months ahead
    (eligible leases); plant capacity factor one month ahead for Texas gas
    CC, solar and wind; WTI, Henry Hub and ERCOT log price one month ahead.
    *Baselines:* last value, seasonal naive and the Arps decline for leases;
    last value, seasonal naive and the technology-month median for plants;
    the random walk and seasonal naive for prices. *Challengers:* ElasticNet
    and LightGBM; the one with the lower validation MAE is "the challenger"
    of each line, named before the holdout is scored. *Split:* origins
    2018-01 to 2022-12 development, 2023-01 to 2023-06 validation, 2023-07
    to 2024-12 holdout, restricted to origins whose target exists by 2024-12
    (and, for ERCOT, is observed); expanding window refitted quarterly on
    rows whose target is on or before the refit origin. *Test:* MAE per origin, paired difference
    challenger − best baseline, 1,000 moving-block bootstrap resamples of the
    holdout origins (blocks of three months), seed 2020. Pass: the 95%
    interval entirely below zero. Twelve lines. *Rejected:* a random
    temporal split (the proposal forbids it); a single pooled MAE without
    pairing (origins differ in difficulty); registering interval coverage as
    a criterion (reported instead: the quantile model is a tool, not the
    claim).
67. **C20 scored as registered: 3 of 12 lines pass; the lease failure
    diagnosed post-hoc and labelled** (2026-10-12; notebook 05). The three
    plant capacity-factor lines pass (gas CC, solar and wind one month
    ahead beat the seasonal naive with the whole interval below zero); the
    six lease lines fail, with the registered challenger 19–42% worse than
    the last observed value; the three price lines fail with intervals that
    straddle zero against the random walk. The verdict stands. *Post-hoc,
    labelled (the precedent is decision #34):* the lease challengers were
    fitted on log(1 + volume) and transformed back, a choice made before any
    score existed; the back-transformed forecast is biased low by about
    10,000–20,000 barrels or Mcf a month (`forecast_posthoc_leases.csv`),
    the retransformation effect. LightGBM refitted on the level has a bias
    near zero and a holdout MAE within 4% of the last-value baseline on
    every lease line (one of six would pass); the honest reading is that at
    three to twelve months a lease's own last month is nearly as good a
    forecast as the model, and the model's value is the interval, not the
    point. *Consequences:* the scenario engine of notebook 08 draws lease
    residuals from the level model's scored holdout, labelled post-hoc; the
    registered verdict is reported in the record and the report; H1 is
    supported for the plant targets only. *Rejected:* re-registering the
    lease lines on the level (a rule changed after the result is no rule);
    dropping the price lines (a fail against the random walk is the
    expected and reportable answer for a unit-root series).
68. **The upstream cost grid, confirmed; results and impact shown to everyone
    in the dashboard** (Alan, 2026-10-12, "confirm 6"). The twenty Gulf
    candidates are valued with the grid of journal question 37, labelled
    ASSUMED on every export: workover or recompletion $4M / $8M / $15M per
    well; incremental uplift +10% / +20% / +30% of the lease's current rate
    on the Arps baseline, decaying with the lease's own decline; operating
    cost $12 / $18 / $28 per boe; federal royalty 18.75% (12.5% as the low
    case); abandonment $1M / $3M / $8M per well at the lease's end; a
    24-month lead time; oil at WTI minus $3 / $5 / $8, gas at Henry Hub minus
    $0.3 / $0.5 / $0.8 per MMBtu; the ATB real cost of capital for offshore
    (5.1%) with 8% as the stress. The three redevelopment cases of notebook
    02 part C (young oil, mature oil watering out, gas tail) carry the same
    grid until Alan says otherwise. *Alan's condition:* the dashboard shows
    these numbers and their impact to every viewer — the grid itself, the
    change in each candidate's NPV and in the book when any assumption moves
    (the tornado), and each project's impact on the portfolio (its share of
    expected NPV, of CVaR and of emissions) — so no modeled cost is hidden
    behind a result. *Rejected:* per-lease cost estimates (no public file
    holds them); a single base case without ranges.
69. **The scenario engine: two generators, residual draws from scored
    forecasts, and the settings** (2026-10-12; notebook 08). Prices: 2,000
    joint paths of 240 months by moving-block bootstrap (blocks of twelve
    months, the same months for WTI, Henry Hub and ERCOT) of the 2018–2024
    monthly log changes from the 2024 real base, seed 2020 — the primary
    set the optimizer selects on; a Gaussian copula on the same marginals
    (seed 2021) — the held-out set it is scored on. Output: one multiplier
    per candidate per scenario drawn from the scored holdout ratios of
    actual to forecast (leases: the labelled post-hoc level model of
    decision #67; plants: the registered challengers), bounded to [0.2, 3]
    and widened by 1/completeness where a candidate's data are thin.
    Costs: a triangular multiplier 0.75–1.5 (mode 1) on the workover and
    operating cost, common to all leases in a scenario (ASSUMED). *Prices
    revert:* the bootstrapped changes are demeaned and applied as shocks to
    a log price that reverts toward the 2018–2024 real mean of each series
    with a four-year half-life (ASSUMED); the first run as a pure random
    walk put WTI between $13 and $800 a barrel ten years out, a drift and a
    variance no planner would use, so the walk was replaced before any
    criterion was scored on the scenarios. Output multipliers are one ratio
    per lease or plant (actuals over forecasts summed across its scored
    months), not per month, so shut-in months do not become twenty-year
    multipliers. Timing:
    operation years of the requests from the entry curves through the book
    simulation's copula with ρ = 0.041 (notebook 09 part A). Risk at the
    95% level (VaR, CVaR as expected shortfall). Six named stresses as
    deterministic multipliers on the flat base; the correlation ablation
    resamples each price on its own. *Rejected:* a fitted multivariate
    normal or GARCH for prices (the history's jumps are the risk; a block
    keeps them); independent draws per month for the primary set (that is
    the copula's weakness, kept out of sample on purpose); scenario-specific
    Arps refits (the uplift is already an assumption; a multiplier on the
    baseline is enough and faster).
70. **Pre-registered criteria C21–C24: the four books under one budget**
    (2026-10-12; written by notebook 09 part D's first cell to
    `results/success_criteria_v7.csv` and committed before any book was
    solved). *Budget:* 40% of the default book's total capital; *caps:* no
    technology above 40% of the budget; *revenue case:* contracted for
    solar and wind (the index PPA of decision #61), merchant for the rest,
    the merchant case reported beside it. *Books:* A top-N by expected
    NPV; B equal capital by sector filled by NPV per dollar; C the
    deterministic MILP (λ = 0); D the risk-aware MILP maximising E[NPV] −
    λ·CVaR95 with λ = 1 (Rockafellar–Uryasev, HiGHS). Books are selected
    on the primary block-bootstrap scenarios and scored on the held-out
    copula scenarios that no selection touched. C21: D beats A on the
    out-of-sample metric, paired scenario bootstrap (1,000 resamples, seed
    2020), interval entirely above zero. C22: D beats B, the same. C23:
    D's selection moves less than C's across the six named stresses (mean
    Jaccard to the base book, D ≥ C). C24: on the joint scenarios D's
    CVaR95 loss is below the best single-sector book's of the same budget,
    interval entirely on the better side. H2 rests on C21–C22, H3 on
    C23–C24. *Rejected:* scoring on the selection set (in-sample flattery);
    a merchant-only registered case (no developer underwrites solar on
    merchant prices, and every power request is then negative, which makes
    the comparison trivial); an emissions cap in the registered run (kept
    as a what-if, so the trade-off is visible rather than imposed).
71. **C21–C24 scored as registered: all four fail, and what the failure
    says** (2026-10-12; notebook 09 part D). On the held-out copula
    scenarios the risk-aware book earns less than top-N NPV (metric
    difference −$420M, interval entirely below zero) and no more than equal
    capital by sector (−$150M [−$350M, +$24M]); its selection moves more
    than the deterministic book's under the six stresses (mean Jaccard 0.95
    against 0.99); and its CVaR is not below the registered single-sector
    comparator's. The verdict stands. *What the tables say:* no book — not
    one of the six — loses money in any of the 2,000 joint scenarios; under
    the confirmed grid a lease redevelopment is an uplift on a producing
    asset for a modest spend, so its incremental NPV is positive almost
    everywhere and every book's 5% tail is a smaller profit, not a loss.
    Risk aversion then has nothing to buy, and the registered question —
    does a risk-aware allocation beat the rules — is answered "not here"
    for a reason the report must state: the grid, not the optimizer. The
    C24 comparator rule (the single-sector book with the lowest CVaR) picks
    the near-empty power-only book, whose tail is small because it is
    small; the rule was registered before the scenarios existed and is kept
    with that reading, as decision #34 requires. *Consequences:* the report
    carries the four failures, the zero-loss finding and the two
    assumptions behind it (the uplift share and the operating cost, the top
    of the tornado); the dashboard shows the frontier and the books so a
    reader can move the grid and watch the tail appear; H2 and H3 are not
    supported on this candidate set. *Rejected:* re-registering with a
    tighter budget or a merchant case to manufacture a trade-off; adding a
    loss to the leases by hand; dropping the C24 line.
72. **The advisor, the gym and the forward view: grounded, recorded,
    replayable, scored** (2026-10-12; notebook 10, `src/advisor.py`,
    `src/gym.py`, `src/horizons.py`; `anthropic==1.13.0` and
    `streamlit==1.65.0` added to `requirements.txt`). *Grounding:* the
    model sees only result tables rendered by one formatter, and
    `verify_numbers` accepts a number in an answer only if the same token
    appears in that text (years and counts up to 50 exempt); a differently
    rounded figure counts as ungrounded on purpose. *Record and replay:*
    every call is appended to `results/advisor_runs.jsonl` keyed by the
    hash of (model, system, user); a matching call is served from the
    record, so `make all` runs offline; with no key and no record the
    advisor's rows read "not recorded" and nothing else changes. Model id
    `claude-sonnet-5-5`, temperature 0, recorded with every call. *The
    prompts:* `prompts/` holds the system prompt, the recommend and gym
    templates and the two reasoning prompts; the two reasoning files are
    drafted from the description in PLAN.md §14.10 and are replaced by the
    author's own wording verbatim when it arrives (journal #34). *Override
    gate:* `override_allowed` needs an answer of at least twenty characters
    to each of the five questions and the opposing case read. *Gym:* sixteen
    situations — the fifteen largest requests of each region × cohort
    (2017–2019) at entry, the 2017 cohort at its two-year gate, ERCOT 2018
    with the budget cut a fifth, the twenty lease candidates at June 2014,
    January 2020 and March 2022 — each under 40% of its total cost; actors
    instinct (top-N NPV), the registered rule (the gate verdict filled by
    NPV per dollar; the risk-aware MILP for leases), the advisor, the human
    (ledger); hindsight is the exact knapsack on realized value, an upper
    bound. Realized value of a request = modeled value per MW if built ×
    MW when it in fact operated − the cost to the gate (OBSERVED outcome,
    DERIVED value: a proxy, labelled). Lease regimes: as-of = the real
    price of the start month held flat; realized = the observed real path
    then held; the CPI before 2016 is January 2016's (error under 2%); the
    optimizer's scenarios use the 2018–2024 shock history (a mild hindsight
    for 2014, stated). *Forward view:* within-horizon value — leases
    truncated incremental cash flows; requests the carry, the capital at
    the operation year and the margin to the horizon weighted by the
    operation curve, nothing beyond the plant's life — and the
    deterministic book per horizon under the registered budget and cap.
    *Rejected:* a deterministic fallback that writes advisor rows without a
    model (would fake AI output); scoring the gym on expected rather than
    realized values; a greedy hindsight (an actor could beat it); the
    `claude-api` skill named in the prompt, which this environment does not
    list — the SDK's documented Messages call is used and the model id is
    a constant in one place.
73. **The two reasoning prompts are final as they stand** (Alan, 2026-10-13:
    "finish it"). The templates in `prompts/motivated_reasoning_check.md`
    and `prompts/ideological_turing_test.md` — drafted from PLAN.md §14.10
    and extended on 13 Oct with the "strongest arguments against it"
    question and the top-three-risks step — are the prompts the project
    uses; the draft status line is removed and open question 34 is closed.
    *Rejected:* waiting for a separate text that does not exist.
74. **After the outside review of 14 Oct: four corrections and a labelled
    post-hoc part** (2026-10-14). *Corrections (bugs, not choices):* (a)
    the gym's two-year rooms checked the gate rule for an 'invest' verdict
    the two-year rule never issues ('accelerate' is its funding verdict),
    so the rule funded nothing in every gate room — fixed in `src/gym.py`;
    (b) the gym's rooms were the fifteen largest requests, which stacks
    them toward requests that fail (size is Part I's strongest predictor of
    failure) and rewards abstention — now fifteen drawn at random, seed
    2020; (c) the EDA's gas combined-cycle capacity factor divided each
    prime-mover part by the whole plant's nameplate, roughly halving it —
    now plant-level (C20's registered lines are unchanged: target and
    forecast share the same definition, and the scored ratios are
    unaffected); (d) report figure titles cut to the finding in twelve
    words or fewer (`plots.SHORT_TITLES`). *Post-hoc, labelled (notebook
    09 part E):* the committee grid — lease capital at $25k / $40k / $60k
    per incremental flowing boe/d and a real rate of 5.1% / 8% / 10% — on
    the same scenario paths and draws; the scenario median beside the
    mean; a sustained oil stress (WTI $42 real for five years); a second
    draw of power candidates from the entry rule's invest class. C21–C24
    stand as registered; the committee-grid books are reported, not
    scored. *Not done, and why:* ERCOT 2020–2023 prices stay bridged
    because EIA's ICE files stop quoting ERCOT North after 2019 and
    ercot.com refuses this machine (decision #53); the advisor stays
    unscored until `ANTHROPIC_API_KEY` is in `.env` (cloud-session credits
    do not pay for the project's own API calls). *Rejected:* replacing the
    registered grid and re-scoring C21–C24 (moves a registered verdict
    after seeing it).
75. **Report v5: structure, title and figure standard** (Alan, 2026-10-14).
    Title *Beyond Prediction: AI-Driven Energy Portfolio Decisions Under
    Uncertainty*, subtitle *From Machine Learning to Risk-Aware Capital
    Allocation*. Two parts kept with a bridge (the reviewer's advice) and
    Part II ordered as the proposal's paper outline (the proposal map is in
    Appendix C); the memo leads with the committee grid and states the
    registered verdicts beside it; codes, decision numbers and file paths
    move to the appendices. Figures: titles ≤ 12 words, 11-inch width,
    PNG at 450 dpi, SVG in the PDF. *Rejected:* merging Parts I and II into
    one portfolio chapter (loses the scored gate results); leading the memo
    with the registered grid (the review showed it is the generous case).
76. **The advisor runs on the Claude subscription when there is no API key**
    (Alan, 2026-10-14: "use my Max plan to run"). `src/advisor.py` gains a
    second backend, `ask_cli`, which calls `claude -p` signed in to the
    author's Claude subscription. The system prompt is replaced
    (`--system-prompt-file`), the user message goes on standard input, and
    the child runs with `--tools ""`, `--strict-mcp-config`,
    `--no-session-persistence`, no CLAUDE.md or memory, in an empty folder
    and an environment stripped of every `CLAUDE*`, `ANTHROPIC_*` and `MCP_*`
    variable. The model therefore receives the same two texts the Messages
    API would, and the grounding check means the same. The record key stays
    the hash of (model, system, user), so a call recorded through either
    backend replays identically; each record names its backend. In auto
    mode a failed call (an expired sign-in) falls back to "not recorded" and
    the notebook prints the reason, so `make all` still runs offline; live
    mode raises. *Also fixed:* `claude-sonnet-5-5` rejects any non-default
    temperature, so the API path no longer sends `temperature=0`
    (`TEMPERATURE = None`), and the record says "model default". *Rejected:*
    piggybacking on the desktop app's session token (not the author's own
    sign-in, and it routes through another process); a scripted fallback that
    writes advisor rows without a model (decision #72).
77. **Open question 38 closed; figure and text corrections before v1.0**
    (Alan, 2026-10-14: "ok, use the recommended"). The memo recommends book
    D under the committee grid and states book A as the alternative for a
    committee with more appetite for risk. A figure review against the
    report found two titles that contradicted their own figure (F16: queues
    swell while recent entrants withdraw less, not more; F23: at entry
    ERCOT's exits operated at least as often as its funded requests) and
    legends on data (F27, F28, F33), raw column names and a decision number
    (F29), stale notebook pointers (F23, F26), the old names "fair baseline"
    and "v2 model" (F11, F12, F22), non-integer counts (F35) and a missing
    dollar sign (F37); all fixed in the notebooks. In the text: §11's claim
    that the tornado's top items are the committee grid's two items was
    wrong (the tornado ranks uplift, operating cost, then the rate) and is
    rewritten; Appendix A's tail sentence now names the held-out scenarios;
    §6 states the ERCOT exception; §13 adds the carbon-price and
    risk-aversion sensitivities the proposal's §10 asked for (overlaps 0.96
    and 0.84, already in `results/portfolio_sensitivity.csv`). The poster
    now carries v5 numbers only, checked by `test_report.py`; its design is
    to be redone (Alan). *Rejected:* leaving the titles and fixing the
    captions instead (the title is what a reader takes away).
78. **ERCOT 2018–2023 hourly prices from ERCOT's public yearly files,
    pulled on a U.S. GitHub runner** (Alan, 2026-10-14: "set up the GitHub
    Actions ERCOT pull"). ERCOT's edge refuses connections from outside the
    United States (a phone hotspot in Brazil was refused the same way), so
    the pull cannot run from Alan's machine on any local network.
    `src/ercot_history.py` lists report 13060 ("Historical DAM Load Zone and
    Hub Prices"), downloads one zip per year, parses the monthly sheets and
    writes `ercot_dam_spp_<year>.parquet` in the gridstatus layout of the
    2024 file, with the fall-back hour resolved by the repeated-hour flag.
    `.github/workflows/ercot_history.yml` runs it on `ubuntu-latest` and
    returns the files as a private artifact (never committed); the six
    hashes are pinned in `config.ERCOT_HISTORY_FILES` and checked by
    `energy_data.verify_ercot_history` in notebook 01. Notebook 01 now takes
    the observed DAM North hub monthly mean for every year on disk, so
    2018–2023 become OBSERVED and the PJM West bridge is used only for a
    year with no file. Annual means of the observed hub: 2018 $33, 2019 $38,
    2020 $22, 2021 $156 (February 2021 alone $1,486), 2022 $64, 2023 $55.
    *Not yet done:* the rerun of 01→10 on the observed prices, because it
    re-scores C20–C24 on new data — a registered-verdict question for Alan
    (handoff). *Rejected:* the ERCOT Public API with credentials in GitHub
    secrets (the public files need none); a VPN (not reproducible).
79. **The "reason my thinking" round is a human-in-the-loop exchange,
    written for this portfolio decision** (Alan, 2026-10-14: "I want the
    reasoning my thinking prompt to HITL. We must adjust them for this
    purpose of deciding in the portfolio"; supersedes #73). The round is now
    three calls: `prompts/motivated_reasoning_questions.md` asks exactly
    five questions tied to the human's statement, one per item of the
    override gate (stakes, parties, emotional investment, evidence,
    framing), and nothing else; the human answers; then
    `motivated_reasoning_check.md` judges the statement and the answers,
    naming the patterns this decision invites (judging the leases on the
    flat path and the requests on the scenarios, treating an ASSUMED cost
    or a FORECAST chance as observed, counting paid deposits), and
    `ideological_turing_test.md` argues the opposing book against what the
    human actually said. The answers are keyed as the override gate keys
    them, so the challenge and the override are one exchange. At the
    keyboard: `python -m src.advisor` (the terminal session), which writes
    the transcript and a ledger row. Notebook 10 runs the two scripted
    statements with the author's own answers so the pipeline reproduces
    offline. The DATA block moved to `advisor.portfolio_context` so the
    notebook, the terminal and the dashboard show the model the same
    tables. A one-shot caller with no answers (the dashboard, untouched)
    still gets a verdict, judged on the statement alone. *Also:* the
    grounding check now reads a unit suffix ("$6.15B", "40%", "150k"), and
    a replayed record is re-verified with the current checker, so a checker
    fix rescores the record without a call; the rubric covers the JSON
    answers only. *Rejected:* a form with the five standing questions
    (the questions must come from what the human wrote).
80. **The pipeline reruns on the observed ERCOT prices; the bridged-price
    verdicts are kept as registered** (Alan, 2026-10-14: "do your
    recommendation"). With the 2018–2023 hourly files on disk (decision
    #78) the ERCOT price history that the scenario engine resamples and
    reverts to changes (2021 alone moves from about $45 to $156 a MWh), so
    every table that rests on the scenarios moves: the books, C21–C24, the
    committee-grid tables, the memo. The main results are now the rerun on
    the observed prices. The criteria stay as registered; their first
    scoring, on the bridged prices, is kept unchanged in
    `results/registered_bridged/` and reported beside the rescoring in
    Appendix A, so a reader sees the verdict as registered and the verdict
    on the corrected data. *Rejected:* keeping the bridged run as the main
    line with the observed prices as a sensitivity (the bridge was a stand-in
    for missing data, not an assumption with a claim of its own).
81. **The scenario engine on the observed ERCOT prices: capped monthly
    shocks, year-aligned blocks, a geometric long-run level** (2026-10-14,
    after the first rerun of decision #80). Winter Storm Uri took the
    ERCOT North hub from $26 to $1,772 a MWh and back within two months
    (log changes +4.2, −4.3). The registered engine (decision #69) draws
    twelve-month blocks that can start anywhere and a copula that draws
    months independently; both can carry the spike without its reversal,
    and the four-year half-life then holds a ×69 price for years. The
    first rerun put book D's expected NPV out of sample at $2,098B against
    a median of $15.8B, and the ERCOT 5–95% band at $1,900 a MWh for two
    decades — a generator artefact, not a risk. Three changes, each
    applied to all three series: (a) monthly log changes are capped at
    ±1.5 (a ×4.5 move, the largest the history shows outside February
    2021), so the Uri month stays an extreme month and no longer a new
    level; (b) the primary blocks are aligned to calendar years, so a spike
    and its reversal travel together and the 2020, 2021 and 2022 episodes
    stay whole; (c) the long-run level the log price reverts to is the
    geometric mean of the 2018–2024 real prices, consistent with a model in
    logs (the arithmetic mean let one month lift the ERCOT target by about
    40%). The bridged-price verdicts of `results/registered_bridged/` were
    scored with the registered engine and are kept as they are. *Rejected:*
    dropping February 2021 from the history (it happened); winsorising at a
    quantile (with 83 months the 99th percentile is set by the Uri pair
    itself); keeping the moving blocks and the trillions (the median would
    carry the report, but every mean, tail and criterion would be noise).
82. **The held-out scoring set is a second draw of the block bootstrap,
    not a Gaussian copula** (2026-10-14, after the rerun of decision #81).
    With the shocks capped and the blocks aligned, the primary set behaved
    (the default book's mean $16.0B against a median of $14.8B), but the
    copula set still put the books' held-out means at $90–107B against
    medians near $10–13B: a copula draws months independently, so a capped
    +1.5 month lands with no reversal and the four-year half-life keeps a
    ×4.5 price for years. That is the copula's design, not a parameter, so
    it cannot be the scoring set once the ERCOT months are observed. The
    held-out set is now the same generator with seed 2021, so every scored
    path is one the optimizer never saw while the generator's assumptions
    are the same on both sides, as in a train/test split of simulations.
    The file key `generator == "copula"` is kept so the parquet, notebooks
    09 and 10 and the dashboard read as before; the labels say "held-out".
    The registered criteria name the copula set and are not rewritten; the
    bridged-price scoring in `results/registered_bridged/` used it.
    `scenarios.gaussian_copula_paths` stays in the module for that record.
    *Rejected:* a copula over calendar-year blocks (seven blocks give a
    rank correlation on seven points); scoring on the primary set (the
    optimizer selected on it).
83. **Title and framing: prescriptive AI is the contribution** (Alan,
    2026-10-17, after an outside review received that day). The report is now
    *Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization —
    From Machine Learning to Risk-Aware Capital Allocation Across Oil, Gas,
    Power, Renewables, and Storage*. One overarching question (can
    prescriptive AI turn uncertain predictions into better capital-allocation
    decisions than conventional methods) and four under it: Predict,
    Quantify, Prescribe, Evaluate. H1–H3 and every criterion, verdict and
    number are unchanged; the abstract, the opening section, the method and
    the results are rewritten around the four stages (descriptive,
    predictive, uncertainty, prescriptive) and the trade-off under the two
    grids is the headline result, stated as a policy choice and not a win.
    Three references added (Bertsimas & Kallus 2020; Elmachtoub & Grigas
    2022; Lepenioti et al. 2020), each verified against its journal record.
    The proposal update of 2026-10-19 carries the same title and questions.
    *Rejected:* "From Predictive to Prescriptive AI: Optimizing Energy
    Portfolios Under Uncertainty" (the review's alternative; weaker
    identity).
84. **Core + appendices; the word limit is back on at 3,500** (Alan,
    2026-10-17; supersedes #44). The body is a core of about 3,400 words
    (abstract, memo, sections 1–7, statement of work, changes after review)
    with five figures; Parts I and II move in full to Appendices E and F,
    renumbered E.1–E.8 and F.1–F.8 with their figures (E1–E9, F1–F4) and
    tables (E1–E3, F1–F3); the full results table and the five decision
    questions are Appendix G (G1, G2). Nothing was deleted. The course
    suggests 3,000 words excluding references and appendices; Alan accepted
    about 3,400 rather than move the Capital Allocation Memo out of the body
    or thin the evaluation chapter, so `tests/test_report.py` counts the
    text before Appendix A against a limit of 3,500 and is no longer skipped.
    *Rejected:* the memo as Appendix G.1 (it is the prescriptive output and
    belongs up front); a 3,000-word body that drops the evaluation chapter.
85. **The evaluation chapter is the source of the Nov 2 mini-deliverable**
    (2026-10-17). Section 3 of the core ("How the work is evaluated": what
    is measured and against what, what the models never see, how I could
    fool myself) is written from the registered record; the Slack one-pager
    `docs/evaluation_plan.md` and its PDF are copied from it, so the two
    cannot diverge, and every number in both is in `report_numbers.csv`.
86. **`value.pjm_capacity_revenue` reads the RPM table from `pdftotext -layout`**
    (2026-10-17, found by a clean-environment reproduction). The plain text
    order of `pdftotext` differs between poppler versions, and poppler 24.02
    on Linux drops the body of Table 5-23 from the default output entirely,
    so the parser that split the text after the caption failed with an
    IndexError in notebook 07. Layout mode keeps each row on one line (year,
    weighted average RPM price, cleared UCAP); the rows are matched by that
    shape, the "2007/2008" delivery-year rows of the next table are excluded,
    and the twenty calendar years 2007–2026 are asserted. The parsed prices
    equal the committed `results/capacity_prices.csv` to the cent, so no
    result changes. README names `pdftotext` as a requirement. *Rejected:*
    typing the twenty prices into `config.py` (the rule is that no cited
    number is typed by hand); a Python PDF library (a new dependency for one
    table).
87. **Reproduction record for v1.1** (2026-10-17). (a) On the author's
    machine, a full `make all` (01 → 10, 66 minutes) changed only the
    decision ledger's dates and float rounding in the tournament tables
    (commit 61a8177; no cited number moved); every other notebook, result,
    processed table and figure came back byte-identical. (b) In a clean Linux environment built from
    `requirements.txt` on Python 3.11, notebooks 02 → 10 ran end to end from
    notebook 01's outputs (01 needs the EIA key and network); of 310 result
    files 249 were identical or equal within 1e-6 and 61 differed by
    floating-point drift (typically 1e-5 to 1e-3 relative); every registered
    verdict (C1–C24, the tournament) was identical; of the 2,241 numbers the
    report cites, 2,234 were identical as printed, two moved in the last digit
    ($5.9B → $5.8B at the low uplift; $13.83B → $13.82B on the flat path) and
    five are advisor statistics that changed only because that environment
    had a live backend and the replay missed 17 of 114 calls on the drifted
    tables; 182 tests passed. The committed results stay as the author's
    machine produced them.
88. **The 17 October audit and the v8 plan; the v7 record frozen**
    (2026-10-17). An independent audit of report v6 and its code
    (`docs/audit_2026-10-17.md`) found that the prediction layer holds and
    that valuation, allocation and the gym do not: the comparator books A and
    B were not held to the registered 40% technology cap (A1), ten of the
    twenty ERCOT candidates were already withdrawn or operating by the end of
    2024 (E1), ten of the twenty lease baselines were fitted with zero decline
    (E2), and the gym's edge came from lease rooms built with 2024 data (G1).
    The scored record as it stood at commit 61a8177 is copied to
    `results/registered_v7/` with a hash manifest and a test, and is never
    edited; corrections are scored beside it. `docs/implementation_plan_v8.md`
    orders the work: freeze, implementation corrections, framing corrections,
    the decision layers, the evaluation of decision processes, figures,
    report. *Rejected:* rescoring the registered criteria in place (it would
    erase what was registered); fixing only the report text (the numbers
    themselves move).
89. **Implementation corrections, labelled as such** (2026-10-17). Where the
    code did not do what the registration or the docstring said, the code is
    fixed and the main tables rerun, and the change is called an
    *implementation correction*, not a new result: (A1) `top_n_by_npv` and
    `equal_capital_by_sector` take the technology cap, and notebook 09 passes
    it to all four books, with `optimizer.violations` checking every book;
    (A13) one CVaR, `optimizer.cvar`, averaging exactly the worst
    `tail_count` scenarios (100 of 2,000, not 101), used by
    `scenarios.risk_measures` too; (E10) gas revenue multiplies Mcf by 1.037
    MMBtu/Mcf (it divided); (G2) the gate rule's floor is the pool's expected
    rate from the probabilities the gate reads, not the cohort's realized
    rate. The registered verdicts in `results/registered_v7/` stand as
    scored. *Rejected:* a training-cohort realized rate as the floor (the
    five-year rate of entrants through 2016 closes in 2021, after the 2017–2019
    gates; the latest cohort closed before a gate is 2012–2014, a level the
    queue has since left).
90. **The v8 framing, as Alan chose it** (Alan, 2026-10-17). (1) One
    decision date for both sectors, 1 January 2025: the power pool is
    redrawn from ERCOT requests still active on 31 December 2024 (the five
    largest per technology), with the chance of operating conditional on
    having survived to that date; the leases are already valued then.
    (2) Lease baselines are modified hyperbolic with a terminal decline of
    8% a year (ASSUMED; 5% and 12% as the range), fitted on post-peak
    months, ramp-up leases fitted from their peak. (3) A two-stage budget:
    stage 1 charges what is committed now — lease capital, and for a request
    its deposits and studies plus a construction reserve — and construction
    capital is decided at the agreement in the dynamic module. (4) The core
    of the report stays within 3,500 words in the eleven sections of the
    brief; the interface is one decision page that shows the alternatives
    first and asks for the human's book before the advisor speaks.
    *Rejected:* a backtest at 2019 (it duplicates the rebuilt gym and makes
    the memo historical); a 12% floor as the base (kept as the range's top);
    charging expected capital (not cash a committee can spend); a
    multi-page dashboard (the earlier critique).
91. **The decision layers of v8** (2026-10-17). Six modules, each with
    tests: `src/decision_date.py` (the queue on 1 January 2025 — requests
    still live, their chance of operating conditional on their age, read
    with the agreement model when an agreement is signed and the plain model
    otherwise, the request year capped at the last cohort with five closed
    years because the trees otherwise extrapolate a 2024 request into
    near-certain withdrawal, and the level corrected by a backtest as of
    1 January 2020; the lookup life table beside it as the transparent
    benchmark); `src/valuation.py` (the repricing that lived only in
    notebook 08, with ATB costs in 2024 dollars and the credits by operation
    year); `src/whatif.py` (a committee question as validated parameters,
    repriced, re-solved and diffed; a statement of each candidate's status;
    opportunity costs from forced re-solves); `src/advisor_tools.py` (the
    language model translates a question into parameters or declines, the
    engine computes, the model explains what was computed, every number
    checked against the computed result in its unit); `src/ledger.py`
    (append-only, a named authorizer on every row, overrides gated where
    they are written, a hash chain); `src/voi.py` (EVPI, partial EVPI and
    the EVSI of the agreement signal, reported as the most worth paying, not
    a return); `src/dynamic.py` (commit in 2025, revise in 2027 on two years
    of prices and the agreement signal, a least-squares continuation value
    fitted on the primary scenarios and scored on the held-out ones — a
    scenario-based extension that establishes no real-option value).
    Notebook 11 runs them; all of it is post-registration and labelled so.
    The advisor's investment increment is measured as zero when its book is
    the optimizer's; its other contributions are scored on translation,
    attributed grounding and refusals, with no money attached. *Rejected:*
    letting the language model propose books or numbers (it cannot be held
    to the constraints or the scenarios); a dynamic program over all forty
    candidates (intractable at capstone scale; two dates and a regression
    policy are enough to measure flexibility); a dollar value for
    explanations (no evidence supports one).
92. **The budget is 40% of the candidates, in the units it is spent in;
    the revision faces the same cap** (2026-10-17, found while rehearsing
    notebook 11 and rerunning notebook 09). The registered rule funds 40% of
    the opportunity set: 40% of the forty candidates' capital when every
    candidate's capital was spent at once. Under the two-stage budget of
    decision #90 a candidate costs the budget its stage-one charge, so the
    rule becomes 40% of the forty stage-one charges. A first attempt kept
    the budget at 40% of full capital: with the 2025 requests' plant capital
    of about $35B the budget rose to about $16B, nothing bound, and the
    comparators A, B and C all funded the same 34 positive candidates — a
    comparison with nothing to compare. That budget is reported in notebook
    11 as a sensitivity. The same rehearsal found the staged policy starting
    deferred leases past the 40% technology cap with capital released by
    dropped requests — the error of audit A1 in a new place; the revision now
    respects the cap the static book faces, with a test. *Rejected:* a
    budget in dollars carried over from v6 ($7.81B; tied to a candidate set
    that no longer exists); letting the revision exceed the cap.
93. **Four fixes after the v8 reading-cell rewrite** (Alan, 2026-10-19).
    (1) The `NB10-advisor-base` row of `results/decision_ledger.csv` is
    corrected and kept: notebook 10 replaced it only when it was absent, so
    the v7 row (26 members, $5.37B against a $1.79B budget) survived the v8
    rerun; the notebook now replaces its row on every run. (2) F0's bottom
    line names every technology the committee-grid book D holds; it listed
    leases, wind and gas and left out the book's solar. (3) Notebook 09 E.6
    scores the naive-forecast book on a held-out set that redraws the naive
    output errors with its own seed and uses the held-out cost draws, as
    notebook 08 does (audit A7); before, its held-out values reused the
    primary draws. The selection, made on the primary set, is unchanged.
    (4) Notebook 09 E.5's second power draw applies part A's entry gate
    (hurdle 3, floor at the pool's mean chance, contracted value before the
    carry, the carry as the gate's cost) to the 1,649 requests live on
    1 January 2025, with only that day's information; it took the 2017–2019
    test cohort's entry decisions, which could reach only the entrants of
    those years still waiting in 2025. Only the base value case exists for
    the 2025 pool, so the rule's low and high cases take it. No new
    notebook; notebooks 09 and 10 rerun. *Rejected:* deleting the ledger row
    (Alan chose to keep the advisor's entry); dropping the second draw.
