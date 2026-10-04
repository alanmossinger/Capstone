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
5. **Pre-registered success criteria** — written by notebook 08's first cell
   before any test metric exists. *(open)*
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
