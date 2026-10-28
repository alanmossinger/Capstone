# Journal

Dated work log. Newest entry at the bottom. Read first, update last.

## 2026-10-03 — Phase 0: data gathering and the readiness gate

**Done**

- Repository laid out as in PLAN.md §3: `src/` (paths, config, get_lbnl,
  eia_api, audit_queue, linkage, plots), `run_pipeline.py`, `Makefile`,
  pinned `requirements.txt` (Python 3.11 in `.venv`, kernel `queue-survival`),
  `.gitignore`, `.env.example`, `pytest.ini`, `tests/test_cleaning.py`.
- `audit_lbnl_queue.py` was not on disk, so `src/audit_queue.py` was written
  from the counts in PLAN.md §5.3; all 18 counts reproduce exactly.
- LBNL file: the site refuses scripted requests (HTTP 403), so the copy
  downloaded by hand is used and pinned by SHA-256 (decision #10).
- EIA API: 2026-07 inventory pulled (28,324 generators, 6 pages, rows = API
  total), cached under `data/raw/eia860m/`.
- `notebooks/01_get_data.ipynb` built and executed three times (first run
  called the API, later runs used the cache); 22 exploratory figures in
  `figures/01_get_data/`, each opened and checked, each followed by a
  *Reading this* cell; caption stubs in `report/figure_notes.md`.
- `docs/data_readiness.md`, `data/README.md` (access statement + generated
  dictionary), first `README.md`.
- Gate: 13 of 15 checks pass → **NO-GO** (see open questions).
- Quick linkage: 31.1% matched, 74.9% agree → notebook 10 dropped.

**Next**

- After Alan's decision on the gate: notebook 02 (`src/cleaning.py`, R1–R9,
  `tests/test_cleaning.py`).

**Open questions for Alan**

1. **Gate thresholds (ASK ALAN).** Two checks fail on thresholds, not on the
   data: CAISO withdrawal-date coverage 82.6% vs ≥ 83% (bar set from the
   audit's rounded 83%), and 2,292 test-cohort projects vs ≥ 2,500 (only
   2,313 Track A rows entered in 2017–2019 at all; completions 304 vs ≥ 150).
   Amend the bars (e.g. ≥ 82%; ≥ 2,000 projects with ≥ 150 completions) and
   record it as a decision, or keep them and change the test design?
   → *Answered the same day: amended as proposed (decision #15).*
2. **Proposed online date looks updated after entry (ASK ALAN).** 44% of
   completed Track A projects have a proposed date within a month of their
   actual operation date, and ERCOT/CAISO operational rows mostly have the
   field blank. Keep `ambition_gap_years` out of the main models (leakage
   ablation only) unless an entry-time snapshot exists, e.g. from earlier
   LBNL releases?
3. Notes for notebook 02: 2 rows above 5,000 MW (not 1); the "607 year
   mismatches" are 607 missing `q_year` values; one duplicate (`q_id`,
   `entity`) pair; ERCOT records no hybrids. Date artefacts seen in the raw
   serials: `prop_date` as early as serial 2001 (1905), `on_date` as early as
   8825 (1924), `ia_date` placeholders at 25569 (1970-01-01), and `wd_date`
   up to 45707 (2025-02-19, after the censor date).

**Note.** One of the executions failed with a `FloatingPointError` inside
`pd.to_datetime(…, unit="D")` that did not recur in five reruns; the Excel
date conversion now uses integer days (identical results, checked), which
avoids that code path.

## 2026-10-03 (later) — gate GO, notebooks 02 and 03

**Done**

- Gate thresholds amended at Alan's decision (#15); notebook 01 re-run: 15 of
  15 checks pass, **GO**.
- Notebook 02 (`src/cleaning.py`, R1–R9): 36,441 → 36,216 requests; 692 event
  dates that contradicted the status or the request date cleared; all seven
  checks pass; the plan's rule-table counts reproduce (the ">5,000 MW: one
  row" is two). 9 figures.
- Notebook 03 (`src/events.py`, `src/survival_tools.py`, `src/features.py`,
  `src/benchmarks.py`): Track A sample 13,366; Aalen–Johansen curves with
  500-resample bootstrap bands; F1, F2, F3, F8 and 10 exploratory figures;
  mock-up check passes; LBNL's completion rates reproduce within 1.2 points
  for every technology and region. All four checks pass.
- Tests: 23 pass (`test_cleaning`, `test_features`, `test_survival_tools`);
  my Aalen–Johansen matches lifelines exactly.
- Found in notebook 03: ERCOT's bulk withdrawal date (441 withdrawals dated
  2018-08-29, none earlier); notebook 01's reading of figure 01_13 corrected.

**Next**

- Notebook 04 (events, Track A/B samples, entry-time features, congestion,
  `tests/test_features.py` extended) — waits on questions 2 and 4 below.

**Open questions for Alan**

2. *(still open)* Proposed online date: keep `ambition_gap_years` out of the
   main models (leakage ablation only)? My recommendation: yes.
4. **ERCOT bulk withdrawal date (ASK ALAN).** 441 ERCOT withdrawals (projects
   entering 2002–2017) are dated 2018-08-29, so their true withdrawal time is
   only known to be before that day. Options for the timing models:
   (a) keep as recorded and flag — simplest, but those projects stay in the
   risk sets for years after they left, which biases ERCOT's withdrawal and
   operation hazards before 2018;
   (b) **delayed entry for ERCOT at 2018-08-29** (left truncation): ERCOT
   projects contribute only the time after that date, and those that had
   already left are not in ERCOT's risk sets — statistically clean, costs the
   early ERCOT years; lifelines (`entry_col`) and the discrete-time expansion
   both support it;
   (c) drop ERCOT entrants before 2018 from the timing models.
   My recommendation: (b) for the main models, (a) as a sensitivity run.
   The 2017–2019 test cohort is barely affected (10 of the stamped rows
   entered in 2017).
5. PJM has 456 withdrawals dated 2024-12-18, inside the test window. They
   may be a real deadline of PJM's queue reform; I have not verified it.
   Keep them as recorded unless you know otherwise?

## 2026-10-03 (evening) — notebooks 04 and 05

**Done**

- Alan approved the recommendations (ambition gap → ablation only; ERCOT
  delayed entry; PJM 2024-12-18 kept). Decisions #21–#25.
- Notebook 04: Track A 13,366 (1,730 : 7,064), Track B 14,624, test cohort
  2,268 (301 built, 627 still waiting); entry-time features with leakage
  tests (9 tests); the stored ambition gap separates 5-year completion 27-fold
  (kept out of main models). I first argued against delayed entry; the PJM
  stamping simulation (logit moves up to 6.6 points) and the 2016 validation
  (delayed entry best, 2.4 vs 3.1 points for ERCOT) reversed that, so the
  approved choice stands.
- Notebook 05: baseline (region × technology AJ cells) and cause-specific Cox
  (region as covariate, decision #24; ridge tuned on 2016: 0.01 operation, 1.0
  withdrawal). Sign checks pass (ERCOT 1.66, CAISO 0.52; small requests
  faster). PH fails for 17 of 36 effects — fast profiles are fast early.
  On the 2016 cohort the baseline's average level beat Cox (2.6 vs 3.9 points).
  Predictions for validation and test written; no test outcome looked at.
- 32 tests pass.

**Next**

- Notebook 06: discrete-time hazards (multinomial logit, LightGBM) with
  year-in-queue effects, time-varying congestion, grouped CV.

**Open questions for Alan**

6. **Cost of delayed entry.** It drops 607 of ERCOT's 732 training requests,
   including 176 of 221 completions, from the timing fits; ERCOT's effect rests
   on 125 post-2018 requests. Keep it as the pre-chosen main treatment (my
   recommendation — the alternative invents withdrawal times), with
   as-recorded and imputed versions as sensitivity runs in notebook 08?

## 2026-10-04 — notebook 06 (discrete-time models)

**Done**

- State check at the start: tree clean, `main` == `origin/main` at e7d5e89,
  32 tests passed.
- Alan's answers: delayed entry stays the main ERCOT treatment, with
  as-recorded and imputed versions as sensitivity runs in notebook 08
  (question 6); PJM's 2024-12-18 withdrawals stay as recorded (question 5).
- `src/discrete_time.py` (project-year rows with delayed entry and yearly
  congestion, state target encoding inside the training rows, logit and
  LightGBM designs and fits, hazards → P(operation by t) and expected time);
  `tests/test_discrete_time.py` (7 unit tests + the band check).
- Notebook 06: 14,653 project-years in the final fit. Logit chosen by grouped
  CV (early-years interactions, C = 0.1; CV log loss 0.7195). LightGBM chosen
  on the 2016 cohort (8 leaves, 331 rounds; 2016 log loss 0.6493 vs 0.6902 for
  the logit), because grouped CV preferred ever larger trees that did worse on
  2016 (decision #27). On the 2016 cohort the mean predictions are 1.8 (logit)
  and 1.7 (LightGBM) points from the observed incidence, against 2.6 for the
  baseline and 3.9 for Cox. Freezing congestion at entry costs nothing
  measurable there. Predictions for 2,841 validation/test requests in
  `data/processed/predictions_trackA.parquet`, merged with notebook 05's.
  17 figures, all opened and checked. No test outcome was looked at.
- Bugs caught on the way: the first project-year rule let ERCOT's stamped
  withdrawals back in (their exit equals the entry time) — fixed by the
  full-year rule (decision #26); a logit ERCOT × early-years term set by a
  handful of rows had pushed ERCOT's 3-year prediction to 0.5% — removed.
- **Acceptance check fails in ERCOT.** Models averaged over the entrants they
  were fitted on lie inside the Aalen–Johansen band in PJM and CAISO at 3, 5
  and 7 years; in ERCOT 5 of 6 values are below it (logit 6.3% vs 12.2%
  observed at 3 years). The cohort breakdown shows why: ERCOT's 2005–14
  entrants completed fast in years delayed entry never shows the models, while
  its 2015–16 entrants are matched (4.3% vs 4.3% at 3 years). `pytest`: 43
  passed, 2 failed (the two ERCOT band tests).
- Notebook 06 needs 3–5 minutes when OneDrive is not syncing; with OneDrive
  re-uploading the figures it took up to 8.7 minutes.

**Next**

- Notebook 07 (Track B), once Alan decides question 7. Then notebook 08,
  whose first cell writes the success criteria to decisions #5 — to be shown
  to Alan before they are fixed.

**Open questions for Alan**

7. **ERCOT fails notebook 06's band check (ASK ALAN).** The failure is the
   known cost of delayed entry (decision #21), not an arithmetic fault (PJM and
   CAISO pass). Options: (a) accept it as a documented FAIL and continue —
   the test stays red for ERCOT, reported in 08 and the limitations;
   (b) restate the check for ERCOT on the cohorts the models can see (none in
   training starts before 2018-08-29, so in practice only the 2016 validation
   cohort, where both models are inside the band) — a change made after seeing
   the result, recorded like #15; (c) revisit the ERCOT treatment. My
   recommendation: (a), keeping the strict test and saying so in the report.
8. **Decision #27** (LightGBM tuned on 2016 rather than by grouped CV)
   departs from PLAN.md §6. Keep it?

**Answered the same day:** question 7 → ERCOT's band check restated on its
2016 entrants (decision #28); both models pass it, notebook 06 now reports 7
of 7 checks PASS and `pytest` 45 passed. Question 8 → decision #27 kept.

## 2026-10-04 (later) — notebook 07 (Track B), stop before notebook 08

**Done**

- Notebook 07 (`src/track_b.py`, `tests/test_track_b.py`, 5 tests): logistic
  regression (C = 0.1 by CV) and LightGBM (4 leaves, 243 rounds, chosen on the
  2016 cohort as in #27; CV ranked the settings the other way, Spearman −0.85)
  for P(built), all nine regions, fitted on entrants to 2015.
- 2016 cohort (18.4% built): AUC 0.665 (logit) and 0.662 (LightGBM) against
  0.613 for the region × technology base rate; Brier 0.1433 and 0.1438
  against 0.1471, intervals overlapping. Calibration (binned isotonic,
  decision #30) fixes the mean level but not the Brier score.
- Per region on 2016 the calibrated models miss in PJM, MISO and SPP; held
  out, a region's level is missed in 8 of 9 regions (ERCOT worst: 5.9–9.9%
  predicted vs 32.4% built, probably through its stamp-inflated congestion),
  while ranking still beats a technology-only benchmark in 8 of 9.
- Track B keeps resolved requests only: up to 32.6% of 2016 entrants were
  still waiting at the end of 2024, which tilts later cohorts towards fast
  outcomes (request-year odds ratio 1.034).
- Predictions for 2,980 requests in `data/processed/predictions_trackB.parquet`.
  13 figures, all checked. Six of six checks pass; the 2017 comparison with
  the base rate moves to notebook 08 (decision #29). No 2017 outcome looked at.
- 50 tests pass.

**Next**

- Notebook 08, once Alan has approved the success criteria (question 9).

**Open questions for Alan**

9. **Pre-registered success criteria (ASK ALAN — draft, not yet written to
   decision #5).** Draft, from PLAN.md §6 made operational:
   - Primary models, named before scoring: Track A = discrete-time LightGBM
     (best 2016 log loss), with the logit, Cox and baseline reported beside it;
     Track B = calibrated LightGBM.
   - C1. Track A, test cohort 2017–2019: Uno's C-index for P(operation by t)
     above the baseline's at 3, 5 and 7 years.
   - C2. IPCW Brier score below the baseline's at 3, 5 and 7 years
     (withdrawn = known non-event; censoring weights from a Kaplan–Meier fit
     of the training censoring distribution).
   - C3. Calibration slope between 0.9 and 1.1 at each horizon.
   - C4. Top-decile lift ≥ 1.5 at 5 years.
   - C5. Track B, 2017 cohort: AUC above and Brier below the base rate.
   - "Beat" = the 95% interval of the paired difference (200 bootstrap
     resamples) excludes zero; point estimates are reported either way.
     Failures are reported, not removed. The 7-year horizon is fully observed
     only for 2017 entrants, which is stated with every 7-year number.
   Points to decide: (a) "beat" by interval (proposed) or by point estimate;
   (b) C4 as written in PLAN ("lift ≥ 1.5 × baseline") is ambiguous — model
   lift ≥ 1.5, or model lift ≥ 1.5 × the baseline's lift? (c) the primary
   models above.

## 2026-10-04/05 — notebooks 08 (evaluation) and 09 (explain and rank)

**Done**

- Alan's answers to question 9: "beat" by interval, C4 = model lift ≥ 1.5,
  primary models as drafted. Decision #5 written by notebook 08's first cell
  and committed and pushed on its own (0d5a47b) together with
  `src/evaluation.py` and its hand-checked tests, before any test metric was
  computed. One change from the draft, made before scoring: censoring
  weights come from the test requests' follow-up windows, not from the
  training set (whose weights would all be 1).
- Notebook 08: **8 of 12 criterion lines pass.** LightGBM beats the
  region × technology baseline on Uno's C and Brier at 3 and 5 years (Uno
  +0.121 and +0.041, intervals above zero) but not at 7 years; calibration
  slope 1.34 and 1.27 at 3 and 5 years (C3 fails), 0.94 at 7; top-decile
  lift 3.96 (C4 passes); Track B calibrated LightGBM beats the base rate on
  2017 (AUC 0.608 vs 0.525, Brier 0.1475 vs 0.1532; C5 passes).
- What else notebook 08 found: Cox is the best model at 7 years; completion
  fell for 2018–2019 entrants (5-year 12.8% → 8.3% and 9.6%) and LightGBM
  over-predicts them (mainly PJM: 14.5% vs 9.4%); without its region the
  model misses the level badly (leave-one-ISO-out); post-entry columns
  would inflate the 5-year AUC to 0.990 (leakage ablation); the advantage
  over the baseline holds in the ERCOT and suspended-request reruns but
  disappears when requests under 20 MW are excluded (0 of 6 comparisons
  won).
- Notebook 09: F6 (Cox hazard ratios), F7 (SHAP of P(operation within 5
  years) through the whole hazard chain, `src/explain.py`); state, size and
  technology carry the predictions; size acts as a smooth gradient with no
  step at 20 MW; 2 of 6 outside facts recovered as written, the other four
  explained — among them a positive congestion effect traced to fitting on
  yearly congestion (PJM queues as crowded as at the test requests' entry
  occur in the training rows almost only late in the wait: year 4.4 vs 2.6,
  operation hazard 11.7% vs 8.3%). 25-request ranking table and three
  worked examples.
- Both notebooks run clean twice with identical numbers (08: 3.8 min, 09:
  1.7 min); 37 new figures, all opened and checked; titles that state a
  direction are computed from the data (one hard-coded "lowers" was wrong
  and was fixed). 62 tests pass.
- Alan's mid-session message ("beat mean", "plan for the best result and
  explain", "best results and explainability, must be honest"): the
  registered interval verdict is kept and a point-estimate column added
  (decision #32); plan below; notebook 09 is the explainability step.

**Next**

- Alan's decisions on questions 10–12. Then report draft v1 (PLAN.md §8a).

**Plan for the best honest result (proposal, not started)**

The test cohort has now been seen, so any new model is post-hoc and must be
labelled as such; the registered verdicts do not change. Procedure: every
choice is made on fits to entrants up to 2015 scored on 2016 entrants only;
the single chosen version is refitted on entrants up to 2016, scored once on
2017–2019, and reported as "post-hoc, after the pre-registered evaluation".
Candidates, each aimed at a failure found in notebooks 08–09:

1. Congestion at entry in fitting as well as prediction (or the yearly
   value expressed relative to the entry value), to remove the
   crowding-as-lateness artefact (09_09) behind part of PJM's
   over-prediction.
2. A level-and-ranking hybrid or a simple average of logit, Cox and
   LightGBM, weights chosen on 2016: the logit is the best calibrated model
   at 3 and 5 years (slope 1.03), Cox the best ranker at 7 years.
3. A linear trend term the trees cannot provide (LightGBM `linear_tree`, or
   request year in a logit layer), aimed at the 2018–2019 slowdown.

None of these can be validated against the slowdown itself without using
the test years, so the honest expectation is a better-calibrated model, not
a different verdict.

**Open questions for Alan**

10. **"Beat mean" (ASK ALAN).** Read as: "beat" should mean a better point
    estimate. Because the criteria were registered and scored first, I kept
    the interval rule as the verdict and added the point-estimate reading
    beside it (2 lines differ: C1 and C2 at 7 years). If you meant something
    else, say so; changing the registered verdict now would have to be
    reported as a post-hoc change.
11. **Post-hoc improvement notebook (ASK ALAN).** Run the plan above as a
    labelled notebook 08b before the report, or report the registered
    results only?
12. **PJM (2018) commercial-probability benchmark (ASK ALAN).** PLAN.md §6
    lists it for notebook 08; its coefficients or method document are not in
    the repository, so it was not run. Do you have the source?
- Still open: poster vs 4-minute video; PLAN.md and the local working-rules file are git-excluded
  but cited by committed docs; rotate the EIA key pasted on 2026-10-03.

## 2026-10-05 — notebook 08b (post-hoc improvements)

**Done**

- Alan approved rewriting the last journal commit (history now free of the
  word the pre-push check looks for; force-pushed with lease, 83c2769) and
  asked for the post-hoc notebook (question 11).
- Protocol first: decision #34 written by notebook 08b's first cell and
  committed and pushed on its own (307730b) before any candidate was fitted
  — five fixed candidates, chosen on the 2016 cohort by mean Brier score
  with cross-fitting, one scoring on the test cohort, labelled post-hoc.
  Helpers: `src/posthoc.py` (blend, recalibration, cross-fitting, 4 tests),
  `discrete_time.fit_both(..., congestion="entry")`,
  `survival_tools.fit_cause_specific_cox` (reproduces notebook 05 exactly).
- Result: on 2016 the candidates were indistinguishable (mean Brier
  0.0994–0.0997, 12 of 12 paired intervals include zero); the rule chose K4
  (blend of entry-congestion logit and LightGBM with Cox). On the test
  cohort K4 passes **5 of 10** Track A criterion lines against 6 for the
  registered LightGBM — the repair does not improve the pre-registered
  result, which stands. K4 does bring the average level closer (inside the
  observed band in 12 of 18 region and entry-year cells, against 7) and
  fitting on entry-time congestion removes ERCOT's spurious congestion
  effect and halves PJM's; the slowdown of 2018–2019 entrants stays
  unrepaired.
- Why 2016 could not have found the repair: the main LightGBM was
  calibrated on 2016 (slopes 0.88–0.96) and miscalibrated only on 2017–2019
  entrants; K3's recalibration, fitted on 2016, pushed in the wrong
  direction on the test cohort.
- All five candidates are also scored on the test cohort, marked "not used
  for the choice"; K2 happens to score best there and is not promoted.
- Reading cells of notebooks 08, 08b and 09 no longer cite run times that
  vary between runs. 66 tests pass; 08b runs in about 2–2.5 minutes, results
  identical across three runs.

**Next**

- Report draft v1 (PLAN.md §8a): the registered results of notebook 08 as
  the main result, notebook 08b as one labelled post-hoc paragraph.

**Open questions for Alan**

- 10 ("beat mean") and 12 (PJM commercial-probability source) still open.
- Poster vs 4-minute video; EIA key rotation; PLAN.md cited by committed
  docs although git-excluded.

## 2026-10-05 (session 5) — report draft v1

**Done**

- State check at the start: tree clean, `main` == `origin/main` at 8db47e9,
  66 tests passed.
- Alan's answers, recorded as decisions #35–#38: question 10 closed (the
  registered interval verdict stays, point-estimate column beside it);
  question 12 closed (the PJM 2018 commercial-probability benchmark is
  dropped and the report says so); poster, not video; `report.md` only for
  now, no pandoc.
- `src/report_numbers.py` (`make numbers`) writes
  `results/report_numbers.csv`: every number the report cites, read from
  `results/`, with its source file. `tests/test_report.py` fails if a
  number in `report/report.md` is not in that table (decision #39).
- `report/report.md` v1: abstract; problem; data gathering and the
  readiness gate; cleaning; exploratory analysis; methods (framing as
  supervised time-to-event learning, entry-time features, four Track A
  models and Track B, hyperparameters and how each was tuned); evaluation
  design (split, metrics, pre-registered criteria); results (8 of 12
  lines, what passes and fails, drift, where the advantage comes from,
  ablation, leave-one-ISO-out, the post-hoc paragraph citing #34);
  explanation (Cox hazard ratios, SHAP, sanity checks, congestion
  artifact) and the ranking book with three worked examples; ethics;
  limitations; statement of work; appendices with the criteria table,
  features and hyperparameters, reproduction steps and a glossary.
  `report/references.md` in APA (23 entries, every in-text citation
  matched).
- Alan's outline feedback: the data-science steps had to be explicit
  (gathering, EDA, modeling, hyperparameters, metrics). Then, mid-session,
  the 3,000-word and figure limits were relaxed for the draft (decision
  #40); the draft has 12 figures and about 3,400 counted words, and the
  word-count test is skipped until the final report.
- An independent review of the draft against `results/` found errors that
  are now fixed: the 8 of 12 lines are not all the timing model's (it
  passes 6 of 10; C5 is Track B); Track B is fitted on entrants to 2015,
  not 2016; ERCOT's 3-year Brier score is worse than the baseline's, which
  "close to the baseline" hid; the congestion train/predict mismatch is now
  described in Methods; "beat" is "entirely on the better side of zero";
  C3's 7-year pass has an interval crossing both bounds; the baseline's
  lift would pass C4 too.
- Notebook 08 rebuilt and rerun for two figure fixes found in that
  review: F5's title said "the project-level models" beat the averages at
  5 years, but the logit's interval includes zero (the title is now
  computed for LightGBM from the intervals); F4's legend covered data
  points (moved to the 7-year panel). Result tables unchanged.

**Next**

- Mentor feedback on the draft (`docs/mentor_feedback.md`), then cut the
  report back toward 3,000 words for the final version; poster
  (`poster/poster.pptx`).

**Open questions for Alan**

13. **PJM (2018) source.** I found a PJM presentation, "Commercial
    probability background information" (Market Efficiency Process
    Enhancement Task Force, 2018-06-15), and cite it as the planned
    benchmark. I could not open it (the site did not resolve from here),
    so the title is taken from its file name. If it publishes the
    coefficients, the benchmark could still be run; decision #36 stands
    until you say otherwise.
14. **References to check:** Johnston, Liu & Yang (2023) is cited as a
    working paper with the authors' URL; DOIs are given only where I am
    sure of them.
15. **Word limit:** the final report must come back under 3,000 words; which
    sections may move to appendices is your call after mentor feedback.
- Still open: PLAN.md is git-excluded but cited by committed docs; rotate
  the EIA key pasted in chat on 2026-10-03.

**Answers (same day)**

- 13 (PJM 2018 source): Alan accepts the citation as it stands; decision
  #36 (benchmark not run) stands.
- 14 (references): checked against the publishers' and indexes' records.
  Johnston, Liu & Yang (2023) is NBER Working Paper No. 31946 (DOI added);
  DOIs added for Blanche et al. (2013), Cox (1958), Fine & Gray (1999), Graf
  et al. (1999) and Wolbers et al. (2014); journal URLs for Pedregosa et al.
  (2011) and Pölsterl (2020); the two NeurIPS papers cite the proceedings
  pages by URL, because the page ranges given in different indexes disagree.
- 15 (word limit): not a concern for now; the focus is the content.
- Unsupervised learning: the report's plain statement that none was used
  is kept.
- PLAN.md citations and the EIA key: closed by Alan, no action.

**PDF (same day).** pandoc 3.12 and Typst 0.15.1 installed at Alan's
request; `make report` builds `report/report.pdf` (20 pages; decision #41).
Checked page by page: figures carry one caption each, references come
before the appendices, the criteria table fits one page.

## 2026-10-06 (session 6) — conclusion section, Word copy

**Done**

- Status check: tree clean, `main` == `origin/main` at 7313df0.
- Built `report/report.docx` with pandoc from the same sources as the PDF
  (all 12 figures embedded); added it to `.gitignore` beside `report.pdf`.
- Added section 10, Conclusion, to `report/report.md` (about 250 words)
  for a data-science reader: the framing (time-to-event, competing risks, temporal
  split), the ranking result and its three limits, and the evaluation
  design (pre-registered criteria, leakage ablation, tuning on time rather
  than shuffled folds). Every number is in `results/report_numbers.csv`;
  `pytest`: 68 passed, 1 skipped. PDF rebuilt (20 pages).

- Alan's review doc ("Queue Survival — Report Review and Portfolio Upgrade
  Plan") read in full. "Portfolio" means a portfolio of power-plant
  requests managed by an energy company, not a showcase. Alan's direction:
  a complete portfolio-management report backed by data science, the 2026
  LBNL file alongside the frozen one, no word/figure/page limits.
  `PLAN.md` rewritten as v3 (notebooks 01b, 03b, 11–18; sources S6–S13;
  criteria C6–C12; figures F9–F16; report v2 skeleton; calendar to Dec 14).
  Decisions #42–#45. Two of the doc's counts corrected from the tables
  (see #42).
- Alan asked for a map of the projects' positions by area of work: F9,
  notebook `03b_project_map`, with `src/geo.py` and `tests/test_geo.py`.
  Positions are Census county representative points (2020 boundary files,
  checksummed in `data/raw/geo/`; the 2023 files fail on Connecticut's
  2022 county change and the gazetteer URL returns an HTML page); 91.4% of
  the 36,216 requests are placed (MISO 35% unmatched, ERCOT 21%). F9: 2,111
  GW waiting at end-2024 in 10,811 placed requests, 40% of it in ERCOT, PJM
  and CAISO, beside the 1,376 GW operating fleet from EIA-860M. Companion
  map: share built by state among resolved 2010–2018 entrants, 3% (GA) to
  42% (MA). Both figures looked at; panel titles, legend sizes and the
  choropleth anchor fixed after the first look. 03b is in
  `run_pipeline.py`, `make explore` and `make figures`; `geopandas` pinned
  (decision #45); S11 in `data/README.md`. `pytest`: 70 passed, 1 skipped.
- Alan's note that the figures must come from his own work: every figure
  in the report and F9 is drawn by a notebook from the LBNL and EIA data;
  the footnote credits the *data* sources, as the course requires. Open
  question 19 asks whether the footnote wording should name the author.

**Next**

- Notebook 11 (fair baseline, utility-scale cohort, v2 criteria first).

**Open questions for Alan**

16. Closed the same day: Alan opened the page in the Browser pane; the
    2026 edition exists (data through 2025, updated May 2026, CC BY 4.0).
    Data file and slide report downloaded with Alan's permission and
    checksummed; first-look readiness lines in `docs/data_readiness.md`;
    decision #48. New question 21: extend Track A to MISO and SPP on the
    2026 file (they now have event dates), as a separately registered
    extension, or keep them in Track B? Answered: registered extension,
    notebook 19, criteria C13–C14 (decision #49); PLAN.md updated.
17. Value proxies for ERCOT and CAISO capacity value (PLAN.md §11 b):
    proposed with sources in notebook 15, confirmed by Alan before the
    table is fixed. Budget and caps: defaults accepted (decision #46).
18. PyMC Bayesian level model: wanted as a stretch (decision #46).
- Report title changed to "From Queue to Grid: AI-Driven Portfolio Management for the U.S. Power-Plant Pipeline" (decision #47); README, report and CLAUDE.md updated.
19. Figure footnotes read "Source: LBNL … ; author's analysis." Should they
    say "Figure: Alan Mössinger, from LBNL …" so authorship is explicit?
    One line in `src/config.py` changes every figure on the next run.

## 2026-10-06 (session 7) — the full v3 build, part 1: notebooks 01b, 11, 12, 13

Alan's direction at the start: name him on every figure (decision #50),
build the whole v3 pipeline now and treat the calendar as the order of
work (decision #51), no limits on figures, report length or notebooks.

**Done**

- Figure footnotes read "Figure: Alan Mössinger. Data: …"; all figures
  re-rendered (notebooks 01, 03, 03b, 08, 09).
- **Notebook 01b** (LBNL 2026 file beside the frozen 2025 file): 96.9% of
  2025 requests found; 2,759 new rows; 135 appended duplicates dropped
  (NYISO/Southeast operational projects listed twice); of 9,815 requests
  active at end-2024, 2,963 withdrew, 278 operated, 238 suspended in 2025;
  63 withdrawn → operational and 80 operational → active between editions;
  all 441 stamped ERCOT withdrawals lost their date (ERCOT withdrawal
  coverage 49%); MISO, SPP and NYISO operations dated for the first time;
  2020–2022 entrants: 1.1%, 0.3%, 0.7% operated within two years.
- **Notebook 11** (fair baseline, utility-scale cohort; criteria C6–C12
  written first, decision #52): the fair baseline has 30 cells with ≥ 50
  requests; by the registered rule the v2 model is the v1 LightGBM (lowest
  2016 log loss on ≥ 20 MW rows, 0.590; the entry-congestion, monotone and
  ≥ 20 MW-only variants 0.606–0.610). **On requests of 20 MW and more the
  model beats the fair baseline in 0 of 6 comparisons** (the v1 baseline in
  3 of 6); under 20 MW, 2 of 6. C6 will fail. The size lookup absorbs the
  v1 gain.
- **Notebook 12** (level repair): among ≥ 20 MW requests, 5-year completion
  fell from 11.0% (2017 entrants) to 5.9% and 6.1% (2018, 2019) while the
  model stayed at 12%; the early-year operation hazard fell from 9.1% (2013
  entrants) to 2.3% (2018–2019), the withdrawal hazard much less. Rolling
  recalibration (level from the cohort before, per region) takes the
  2018–2019 ≥ 20 MW 5-year intercept from −0.81 to −0.47; no option's
  interval covers zero: **C7 fails**. 2020–2022 entrants operate within two
  years at a quarter of the predicted rate (intercept needed −2.16).
- **Notebook 13** (milestones): CAISO's queue report joins 100% of the
  2017–2019 LBNL CAISO requests and agrees with LBNL's dates; the two LBNL
  editions date an agreement for 1,818 Track A requests, 1,483 inside the
  queue time (ERCOT 31%, CAISO 15%, PJM 2.6%); 45% of those operated. PJM's
  export and ERCOT's GIS report are unreachable from this machine
  (decision #53); gridstatus pinned.
- New modules with tests: `src/baselines.py`, `src/drift.py`,
  `src/variants.py`, `src/landmark.py`; `tests/test_baselines.py`,
  `test_drift.py`, `test_variants.py`, `test_landmark.py`.
- **Notebook 14** (landmark models): the discrete-time model read from a
  landmark with the covariates updated to that day; two years in, the
  dated agreement flag lifts Uno's C from 0.687 to 0.797 (+0.101 [+0.062,
  +0.136]) and wins 6 of 6 comparisons — **C8 passes at +24 months**, fails
  at the agreement itself (+0.004); updating congestion alone hurts (the
  artefact); the fair baseline conditional on the landmark falls to 0.591.
  Leakage guard: highest landmark AUC 0.972 against the ablation's 0.990.
- **Notebook 15** (value and cost): every input parsed from a public file
  (EIA ICE hub prices 2017–2025; the PJM market monitor's capacity revenue
  2007–2026 and ELCC ratings, parsed from the PDF; EIA generation over
  EIA-860M nameplate for capacity factors; LBNL's PJM cost data) or stated
  in `results/value_assumptions.csv` with a range. 2017–2019 cohort: 29.2
  GW expected online within five years (raw), 25.2 GW repaired, 18.8 GW
  realised. The value case barely moves the order of requests (Spearman ≥
  0.97). Downloads made with Alan's permission; pjm.com and ercot.com are
  unreachable from this machine (decision #53).
- **Notebook 16** (the book): scorecards and what-ifs for the 25-request
  2019 book (cut to 19.9 MW +3.0 points, add storage +3.5, quieter queue
  −0.7 — the artefact); shared risk ρ = 0.041 from 15 region × year
  groups; the book expected 203 MW online within five years (band 0–586),
  72 MW were. Budget $20.11M; the registered backtest is a tie: the model's,
  the fair baseline's and the v1 baseline's books all realised 1,035 MW
  (one request), because an expected-value objective under a deposit budget
  buys the same giant requests whatever the chooser — C9 and C10 fail, C11
  passes (band 58–3,371). An exploratory count-limited book was added after
  the registered result, labelled (decision #55).
- **Notebook 17** (constraints, levers, playbooks): constraint map F16,
  scenario table (decision #56), ten levers, `report/playbooks.md`.
- **Notebook 18** (v2 verdict): 3 of 12 lines pass (C8 at +24 months, C11,
  C12); v1's 8 of 12 untouched and shown beside it; Track B calibration
  plot added.
- **Notebook 19** (MISO and SPP on the 2026 file; C13–C14 registered first,
  decision #54): 3 of 12 lines pass; the test cohorts hold 54 and 8
  operations — the method transfers, the evidence does not yet.
- **Report v2** assembled: `report/report.md` (12 sections, 5,509 words,
  F9–F16 as Figures 1–8), the appendix with the v2 and v3 criteria tables,
  the value assumptions and the landmark risk sets, 30 references.
  `src/report_numbers.py` extended with the v3 collectors (969 traced
  numbers); `tests/test_report.py` passes; three hand-typed numbers it
  caught were corrected (−2.15, $100.2, the agreement years). PDF built (26
  pages); the DOCX is locked by Word and rebuilds with the pandoc command
  in `HANDOFF.md`. 86 tests pass.
- `HANDOFF.md` written (git-excluded) with the state, the unfinished items
  and the prompt for the next session.

**Next**

- See `HANDOFF.md` "Unfinished": notebook 16's final reading cells; report
  v2 assembled, numbered and built; `make all`; then the calendar items.

**Open questions for Alan**

21. (answered) MISO/SPP as a registered extension — done, notebook 19.
22. PJM queue export and ERCOT GIS report from another network
    (`data/raw/iso/`): the single largest improvement available to the
    landmark models.
23. Verify three value assumptions (`results/value_assumptions.csv`): the
    CAISO capacity price, the production-credit rate, ERCOT's energy price
    after 2019.
24. Rotate the EIA API key pasted into chat on 2026-10-06.
25. `git push` when you want the remote updated (nothing pushed since
    7313df0).
- Alan's direction at the close of the session: pursue the stronger thesis
  (an AI-managed book beats the lookup) — through registered tests only.
  `HANDOFF.md` now carries the program (notebook 20: the milestone-managed
  book with criteria C15–C16 written first; PJM's dated phases; level
  repair at the landmark; a registered diversification objective) and the
  review-first prompt for the next session. The evidence to date is
  unchanged: at entry the lookup ties or wins; at the milestones the model
  wins where the agreement is dated.

## 2026-10-08 (session 8) — the missing ISO files, and the registered milestone-managed book

Alan's direction: get the data that was missing and finish the job.

**Done**

- **The missing data was already on disk.** Alan had fetched PJM's queue
  export (`pjm_queue_2026-10-07.xml`) and ERCOT's GIS report
  (`ercot_gis_2026-10-07.xlsx`) from another network on 2026-10-07.
  pjm.com still refuses this machine. `src/iso_files.py` parses both and
  has tests. Notebook 13 now joins them and measures what they add
  (decision #57):
  - PJM finds 94.5% of the 2017–2019 PJM entrants and agrees with the LBNL
    dates on the same day for all 7,051 request, 4,443 withdrawal and 1,143
    in-service dates. It dates no study and no agreement; the agreement
    status is October 2026's, so it carries the outcome. Backfeed precedes
    operation by a median 0.27 years, and 258 of the 342 test-cohort
    backfeed dates fall after 2024.
  - ERCOT dates every phase but lists only requests still active. Of 479
    test requests it lists 108, all active at end-2024, and none of the 92
    that operated or the 223 that withdrew. Its agreement dates agree with
    LBNL's (98% of 440 within 30 days), and it adds one for the test cohort.
  - The web archive holds 158 executed PJM agreement PDFs, 63 of them for
    the 1,465 PJM test requests. That is a selected sample, so it was
    rejected. **The PJM gap remains.**
- **Notebook 20 (the milestone-managed book).** Criteria C15–C17 and the
  thesis rule were registered and committed before scoring (decision #58,
  commit 850acea). New helpers: `portfolio.top_n_book`,
  `landmark.agreement_lookup_at_landmark`, with tests. Results, 4 of 10
  lines pass:
  - Pool: 1,132 requests of 20 MW and more in the queue two years after
    the request; 119 operated within three more years.
  - C15 passes (operations): the model's book of 25 held 19 against 11 for
    the agreement-aware lookup (+8 [+1, +11]); the book of 50 held 33
    against 24 (+9 [+0.98, +13]). Against the unchanged entry ranking:
    +11 and +14.
  - C16 fails (MW): −604 and −914 against the lookup; against the entry
    ranking, intervals include zero.
  - C17 fails (level repair from early outcomes): the intercept moved from
    −0.29 to −0.44, driven by the 2019 cohort's early burst (30
    first-year operations against 14.3 predicted).
  - **Thesis rule met.** The stronger thesis holds as registered: more
    requests built, not more MW, and only where agreements are dated.
- `docs/review_v2.md` written: a sceptical review of the six questions. It
  was written after notebook 20 was scored, against the handoff's planned
  order; the registration had already been committed.
- **Report.** The abstract, section 2, section 6, section 7.3 (new
  Figure 9 = F18), sections 8, 9 and 11, the conclusion and appendix A4
  were updated. `src/report_numbers.py` gained `v4_managed_book` (1,014
  numbers). `tests/test_report.py` passes. PDF (29 pages) and DOCX rebuilt.
  README, Makefile and `run_pipeline.py` include notebook 20.
- 90 tests pass, 1 skipped (the word limit).
- **Full rebuild from the raw files:** all 22 notebooks (01 → 09, 01b, 11 → 20) ran without error in about 50 minutes. Every result table reproduced unchanged; only the readiness report's date and two seconds-valued timing checks differ.

**Next**

- The report is 6,175 words against the 3,000 limit. Cut before the final
  version and restore the word-limit test.
- The calendar items: the proposal update before Oct 19, mentor feedback,
  poster, gallery post, tag `v1.0`.
- Explain the landmark model inside the agreement-known group
  (`docs/review_v2.md`, Q2). That is where the C15 gain comes from.

**Open questions for Alan**

26. **Did the thesis hold?** Yes, in its registered form: C15 passes,
    while C16 (MW) and C17 (level repair) fail. Is the report's framing,
    "more projects built, not more megawatts, where agreements are dated",
    the one you want to defend?
27. PJM's dated study phases are not in any file reachable here. The
    remaining routes are yours to take: a PJM Data Miner API key (your
    account), or asking PJM for the executed-agreement dates.
28. (carried) Verify three value assumptions; rotate the EIA API key;
    `git push` when you want (nothing pushed this session).

## 2026-10-11/12 (session 9) — From Queue to Capital: the report reorganised around an energy company's decisions

Alan's direction: the v2 report read as "nothing" because it was a contest
between a model and a lookup. The reader is an energy company that owns a
book of queue requests and must decide — invest, hold, exit; where, when,
how much, which project. Use everything already built, simplify (a
capstone, not a PhD), no new notebooks, every addition explained in the
notebook that owns it, and "we are paid to find, not to explore".
Decisions #59 (scope) and #60 (NREL ATB as the cost source); PLAN.md §13.

**Done**

- **Plan.** PLAN.md §13 rewritten: six engines (market intelligence,
  development forecasting, asset economics, risk, spatial at state level,
  portfolio optimisation) feeding one decision; nodal prices, weather, land,
  transmission, financing and multistate models stated out of scope.
- **Notebook 08b §7, the tournament (F22).** Criteria C18–C19 registered
  and committed (154e39d) before any fit. Random survival forest pair, MLP
  discrete-time hazard, blend of five; chosen on 2016 (T* = the blend,
  mean Brier 0.0995 vs 0.0996 for K0). On the test cohort **C18 fails**
  (3 of 4 lines: Uno's C +0.015 [+0.002, +0.028] at 3 y on ≥ 20 MW, but
  −0.007 [−0.020, +0.005] at 5 y) and **C19 fails** (2 of 4). The forest
  and the network alone rank worse than LightGBM (Uno's C 0.66, 0.68 vs
  0.76 at 5 y). The registered LightGBM and the lookup stay.
- **Notebook 03 §12–13 (F19, F20).** Six drivers on the 5,497 entrants of
  2010–2019 with Wilson intervals: PJM 24% under 5 MW → 4% at 500 MW+; gas
  32% PJM, 25% ERCOT; batteries 4–7%; an agreement signed within two years
  (2025 file) lifts ERCOT from 0.8% (484 undated) to 63% (218). When and
  where requests die: CAISO 48% and PJM 31% leave in year one, 82% and 42%
  of their withdrawals out of the system impact study; ERCOT culls after
  year four in the facilities study, 13% after a signed agreement.
  Surviving two years triples the odds of operating within the next three
  (ERCOT 7% → 21%, PJM 9% → 16%, CAISO 1% → 10%).
- **Notebook 09 §4b (F21).** Ten entry-time rules (depth-4 tree on
  2010–2016, re-measured on 2017–2019): 1%–47%, Spearman 0.77 out of time;
  `segments_by_request.csv` feeds the entry gate.
- **Notebook 08 §11.** Timing error among the 297 built: LightGBM within a
  year 52% of the time (MAE 1.19 y) vs 33% for a regional median; the gain
  is PJM's; in ERCOT the median (3.3 y) does as well.
- **Notebook 15 §8 (F26).** NREL ATB 2024 v3 (5 MB parquet, source S12,
  fetched and hash-checked by `value.fetch_atb`). NPV per MW with new-build
  capacity factors, ITC/PTC election, 8% real, 20 years: with today's
  credits only 5 of 21 technology-region pairs are positive (wind
  everywhere, gas and solar in PJM), 2 after 2027; storage, hybrids and
  offshore negative throughout. Break-even flat prices: solar $57, wind
  $51, gas $80 /MWh vs captured $30–68. Median expected NPV of a test
  request at entry −$0.3M; wind +$14M in ERCOT and PJM. A first pass with
  fleet capacity factors (PJM solar 10%) made every pair negative; the
  choice of the ATB class CF for new plants is stated as an assumption.
- **Notebook 03b §5 (F25).** k-means on seven state market features: four
  archetypes (silhouette ≈ 0.20, soft) that separate the 2017–2019 outcome
  they never saw, 5.5% (hot gas-leaning Southeast/plains) to 19.7% (light,
  settled PJM core and Florida).
- **Notebook 16 §9 (F23).** Gates G1 (entry: lookup cell and segment rate)
  and G2 (+2 y: landmark model) with `V = −C + P × NPV` and h = 3. G1:
  invest 101 (25% operated, +$1,448M at merchant NPV), hold 699 (14%),
  exit 1,468 (7%; would have lost $8,889M; still 45% of the cohort's
  operations). G2 on 1,298: accelerate 39 (51% operated; ERCOT 18 of 30),
  hold-or-sell 629 (11%, +$82M), exit 630 (10%, −$8,316M). Four policies
  under the section-5 budget with the cohort level as a common risk factor:
  every policy that counts capital buys wind and made money (+$146M to
  +$221M realised at merchant NPV; expected shortfall near −$25M) where the
  value-index book of section 5 lost $362M (ES95 −$4.8B); the risk-adjusted
  book barely differs from NPV per dollar because the shared risk is the
  level. `decision_pack.csv`: one row
  per request. Helpers `gate_decision`, `simulate_operation_years`,
  `expected_shortfall`, `greedy_risk_adjusted` in `src/portfolio.py`, with
  tests.
- **Notebook 20 §10 (F24).** The model's order keeps its edge over the
  agreement-aware lookup for about the first hundred adds (22 vs 11 at 25,
  34 vs 25 at 50, 51 each at 100). A floor at the pool's rate admits 410;
  95 operated (23%); ERCOT: 167 adds capture 70 of 75 operations; PJM 241
  for 24 of 37; CAISO 2. At merchant prices the ERCOT adds have a negative
  expected NPV — the count book says which requests will exist, the gates
  which are worth owning.
- **Plumbing.** `report/appendix.md` retired; Makefile builds PDF and DOCX;
  `tests/test_report.py` without the appendix; README; `src/drivers.py`
  and the `v5_*` collectors in `src/report_numbers.py`; `data/README.md`
  S12; all tests pass (107, 1 skipped).
- **Report v3** written to the §13 skeleton: twelve sections, fourteen
  figures, three tables, 5,909 words; every number traced
  (`tests/test_report.py` passes; 1,592 numbers in `report_numbers.csv`).
  `report/report.pdf` (6.1 MB) and `report/report.docx` rebuilt with
  `make report` once Alan closed the viewer that had locked them.

**Next**

- Full `make all` from the raw files (≈ 1.5 h with the new sections) and a
  read of every figure; F23's small-n rows and F24's label are patched in
  the source for that run.
- The proposal update for 19 October from sections 1 and 3–8; mentor
  feedback; poster; tag v1.0.

**Open questions for Alan**

29. The gates use merchant NPV, so they refuse solar and storage that a
    contracted developer would keep. The break-even prices (solar $57,
    wind $51, gas $80 /MWh) are the lever. Do you want a contracted case
    (a PPA at the break-even price plus a margin) run through the gates as
    a second column, or is the merchant case with the break-even table the
    answer you want to defend?
30. The hurdle h = 3 and the discount rate 8% are the two company
    parameters; both are reported at alternatives. Any other value?
31. (carried) EIA key rotation; `git push` when you want.

### Addendum, 2026-10-12 — the decision board

Alan asked for images that explain the report's decisions on their own, for
a portfolio page or a poster. Notebook 18 §4 now draws seven of them from
the result tables alone (`results/decision_board.csv` holds the headline
numbers): D0 the board (six decisions, each with its numbers and its rule),
D1 where, D2 which and when, D3 why, D4 what a plant is worth, D5 the book
and where to add, D6 six ways to spend the same budget. Saved as
`figures/D0_decision_board` … `D6_policies` (PNG and SVG). Open question 29
(a contracted PPA case through the gates, the ATB cost of capital per
technology, a hurdle of 2 at the second gate) stands; the images show the
merchant case as the report does.

### Addendum, 2026-10-12 — the contracted case through the gates (decision #61)

Alan answered open questions 29 and 30 ("close"; "what is the market best
practice?"): the practice is a project DCF at the technology's own cost of
capital, the never-built risk carried as a probability at staged gates, and
a contracted revenue case beside the merchant one. Done, in the notebooks
that own each piece:

- **Notebook 15 §8.** `value.atb_wacc()` reads the ATB 2024 real WACC per
  technology (solar and hybrids 4.2%, wind 4.9%, offshore 5.1%, gas 5.4%;
  8% kept as a stress column). A **contracted** case: a 15-year PPA at
  index prices (solar $57, wind $62, hybrids $70, offshore $110 per MWh,
  ±$10) then merchant; gas, storage and "Other" stay merchant. F26 now has
  three panels (merchant 2024, contracted 2024, merchant 2028). At the ATB
  rate 5 of 21 technology-region pairs pay at merchant prices and 10 under
  contract; break-even flat prices solar $44, wind $41, gas $72 per MWh
  (`npv_table.csv`, `npv_by_request.csv`, `atb_costs.csv` with `wacc_real`).
- **Notebook 16 §9.** Both revenue cases through the gates with the staged
  hurdle (3 at entry, 2 two years in). Merchant: invest 237 at entry (26%
  built, +$4.1B realised), exit 1,067 (5%, −$5.3B); accelerate 316 two
  years in (18%, +$3.6B), exit 405 (8%). Contracted: invest 326 (21%,
  +$9.3B), exit 1,039 (5%, −$4.9B); accelerate 410 (20%, +$9.0B), exit
  395 (8%). F23 is a 2×2. The six policies under the $20.11M deposit
  budget: the four that count capital returned +$391 to +$581M merchant
  and +$1,235 to +$1,611M under contract; the value-index book −$46M
  merchant, +$440M contracted (`portfolio_review_summary.csv`,
  `policy_comparison.csv`, `decision_pack.csv`, all with `revenue_case`).
- **Notebook 20 §10.** The recommended books carry a contracted expected
  NPV column: the ERCOT adds are −$2.0B merchant and +$2.2B under contract.
- **Notebook 18 §4.** D0, D4, D5 and D6 redrawn with both cases (D6's
  legend moved to the empty space left of zero, x axis widened).
- **Report v3** sections 6–8, abstract, memo and conclusion rewritten for
  the ATB rate and the contracted case (6,543 words); `v5_*` collectors
  extended (1,921 numbers); `tests/test_report.py` passes; 107 tests pass,
  1 skipped; `report.pdf` and `report.docx` rebuilt 09:20.

Open questions 29 and 30 are closed by decision #61. The earlier full
rebuild check predates this change; a final `make all` before tagging v1.0
stays on the list. New open question:

32. The PPA index prices (solar $57, wind $62, hybrids $70, offshore $110
    per MWh) are stated as assumptions in `value_assumptions.csv`; please
    confirm or replace them with the index you want cited.

## 2026-10-12 (session 10) — v5 begins: the ERCOT API test, the 22 → 10 consolidation, the proposal update, the energy sources and their gate

Alan's direction (12 Oct, decision #62): the capstone becomes a real
integrated U.S. energy portfolio — twenty Gulf of Mexico lease
redevelopments and twenty ERCOT power candidates anchored to real queue
requests — with everything built kept as the completion-and-timing engine,
an LLM advisor grounded only in result tables that recommends, challenges
the human and is scored in a decision gym, a dashboard, the notebooks
consolidated to the story layout, and an executive + data-science +
portfolio report. Later the same day he added: the AI is part of every
decision and may be overridden only after the human answers the reasoning
prompts (override gate, decision ledger); two dashboard modes (learn from
history, decide forward, scenario plans with probabilities on request);
all regions in the candidate universe, with thinner data showing up as
wider uncertainty and tighter constraints, never as silence (PLAN.md §14
addenda).

**Done**

- **HANDOFF.md** rewritten with the session-10 handoff, **PLAN.md §14**
  added from the plan of 12 Oct, decisions #62–#64.
- **(0) ERCOT Public API.** `src/ercot_api.py` ported from my Milestone II
  loader (B2C sign-in, paged reports, secret scrubbing, a year-by-year pull
  with hashes, `python -m src.ercot_api 2018 2023`), four tests. From this
  machine the sign-in succeeds and every ercot.com host (api, apiexplorer,
  www) answers the Incapsula interstitial to the report call whatever the
  headers; the 2018–2023 pull has to run from another network. The
  2020–2023 ERCOT months stay a labelled assumption until it does.
- **(1) The consolidation, 22 → 10 (decision #63).** Seven notebooks now:
  `01_problem_and_data` (01, 02, 01b), `02_eda` (03, 03b),
  `03_statistics_and_features` (04), `04_forecast_queue` (05, 06, 07, 11,
  12, 13, 14, 19), `06_evaluation_record` (08, 08b, 09, 18), `07_economics`
  (15), `09_portfolio` (16, 17, 20). Three sections moved so that no
  notebook reads a later one's file (the 2020–2022 early incidence, the
  leakage ablation and the ten entry rules, all into 04); 17 went whole
  into 09; 06 runs last. Gate: `make all` before (1 h 25 min) and after
  (30 min): 196 of 201 result files byte-identical; the five others are the
  two timing checks (seconds of run time) and the three tournament tables
  (6.7e-16 and 1.6e-15 on the scored tables; one MLP cell of the 2016
  validation table moves by 7e-5 between any two runs, before the merge
  too); `predictions_tournament.parquet` within 5.6e-17; all 66 report
  figures and 262 exploratory figures byte-identical; 111 tests. Old
  notebooks and figure folders deleted in the same commit; Makefile,
  `run_pipeline.py`, README, `report_numbers.py` sources and every notebook
  mention in `src/` and `tests/` updated.
- **(3) Proposal update** for 19 October: `docs/proposal_update_2026-10-19.md`
  (the Group 13 form answered again for the integrated portfolio).
- **(2) Notebook 01 parts D and E (decision #64).** Six sources fetched,
  hashed and parsed (`src/energy_data.py`, nine tests): BSEE OGOR-A
  2010–2024 (1,672,579 completion-months → 203,963 lease-months, 2,229
  leases, 1,041 with ≥ 60 producing months), EIA-923 Texas 2018–2024 via
  the API (186,744 rows → 61,136 plant × prime-mover months, 947 plants;
  with ≥ 36 generating months: gas CC 69, solar 108, wind 201, storage 18),
  WTI and Henry Hub monthly, the five ERCOT 2024 files with pinned hashes,
  eGRID2023 (824 Texas plants, 98.8% of the plants generating in 2023
  joined), BLS CPI-U (a 2018 dollar is 1.25 2024 dollars). Market table
  2017–2024 with the ERCOT series labelled observed / derived / assumed;
  release lags written down; audits R10–R13 touch nothing. Figures
  01_D1–01_D3 with provenance labels (`plots.finish(provenance=…)`). The
  v5 gate reads **GO** (12 blocking lines pass; the ERCOT hourly 2018–2023
  line fails and does not block). First evaluation read NO-GO on an eGRID
  line I had specified against the wrong year; corrected and recorded.
- `save_fig` retries a write OneDrive has briefly locked (three runs failed
  on it before the retry).
- Commits: the ERCOT client; the consolidation; the proposal update;
  notebook 01 parts D–E. Nothing pushed.

**Next**

- (4) `02_eda` part C (energy EDA) and `03_statistics_and_features` part B
  (statistics, leakage-safe features, split protocol, truncation test), C20
  registered first; (5) `05_forecast_energy`; (6) `07` candidates and
  economics (ASK ALAN: the upstream cost grid); (7) `08`; (8) `09` MILP with
  C21–C24; (9) `10` advisor and gym; (10) dashboard, report v4.

**Open questions for Alan**

33. Run `python -m src.ercot_api 2018 2023` from a network ERCOT's edge
    accepts (the credentials are in `.env`) and drop the six files into
    `data/raw/ercot/`; the gate line turns PASS and the assumed months go.
34. Paste the verbatim text of your two prompts (the motivated-reasoning
    check and the ideological Turing test) for `prompts/` and the appendix.
35. `ANTHROPIC_API_KEY` into `.env` before notebook 10.
36. (carried) EIA key and ERCOT password rotation; `git push` when wanted;
    the PPA index prices (#32); the upstream cost grid before notebook 07.

### Addendum, 2026-10-12 — step (4): the energy EDA, the statistics, the features and C20

- **Notebook 02 part C** (six families, figures 02_C1–02_C6 with provenance
  labels): a quarter of lease-months are zero by nature; the median lease
  keeps half its peak oil for 12 months (pooled Arps b = 1.47, the physics
  floor); Texas wind 33%, solar 22%, gas CC 23% of nameplate with the
  seasonal shapes a revenue model needs; Henry Hub twice as volatile as WTI
  (67% vs 35% annualised since 2018); MC and GC hold 70% of the eligible
  leases' 2024 oil; prices and output barely co-move month to month
  (WTI–Henry Hub 0.06, ERCOT–Henry Hub 0.38); the decline clusters are weak
  (silhouette 0.34) and decide nothing.
- **Notebook 03 part B.** C20 and the split protocol registered first
  (`results/success_criteria_v6.csv`, decision #66; twelve lines; quarterly
  refits — amended before anything was scored or committed). Price levels
  are unit roots and their changes stationary; ERCOT follows Henry Hub
  within the month. Three feature tables at rolling origins
  (`features_lease` 262,110 rows, `features_plant` 55,988, `features_market`
  504), lagged by the release schedule; the truncation test passes at nine
  of nine builder × origin checks and `tests/test_energy_features.py`.
- Modules `src/decline.py`, `src/energy_features.py`, `src/energy_stats.py`
  with tests (128 pass); `statsmodels` and `xlrd` pinned (decision #65).
- Next: step (5), `05_forecast_energy`.

### Addendum, 2026-10-12 — step (5): notebook 05, the energy forecasts and C20

- `05_forecast_energy` built and executed (7.7 min): baselines (last value,
  seasonal naive, Arps per lease at 21 scored origins, technology-month
  median, random walk), ElasticNet and LightGBM refitted quarterly, the
  challenger of each line named on validation, the holdout scored once.
- **C20: 3 of 12 registered lines pass** — gas CC, solar and wind capacity
  factor one month ahead (MAE 8–15% below the seasonal naive, intervals
  below zero). The six lease lines fail (challenger 19–42% worse than the
  last value), the three price lines fail (intervals straddle zero against
  the random walk). Decision #67 records the labelled post-hoc diagnosis:
  the log retransformation biased the lease forecasts low by 10–20 thousand
  bbl or Mcf a month; on the level, LightGBM is within 4% of the last value
  (one line would pass). F27, `success_criteria_v6_scored.csv`,
  `forecast_metrics.csv`, `forecast_coverage.csv` (90% intervals cover
  92–94% of lease targets, 72–80% of plant targets, 82–100% of prices),
  `forecast_robustness.csv`, `forecast_posthoc_leases.csv`,
  `data/processed/forecasts_holdout.parquet` for notebook 08.
- `src/energy_models.py` with tests (132 pass).

**Open question for Alan, added at the end of session 10**

37. **The upstream cost grid (ASK ALAN before notebook 07 part B).** No
    public file holds a lease's redevelopment cost, so the twenty Gulf
    candidates need a documented low / base / high grid, labelled ASSUMED.
    Proposed defaults, to confirm or replace: workover or recompletion cost
    per well $4M / $8M / $15M (shelf to deepwater); incremental uplift on
    the Arps baseline +10% / +20% / +30% of the lease's current rate, decaying
    with the lease's own decline; lease operating cost $12 / $18 / $28 per
    boe; federal royalty 18.75% (12.5% for leases issued before 2007 is the
    low case); abandonment accrual $1M / $3M / $8M per well, discounted at
    the lease's end; a 24-month redevelopment lead time; oil sold at WTI
    minus a $3 / $5 / $8 differential and gas at Henry Hub minus $0.3 / $0.5
    / $0.8 per MMBtu; the ATB real cost of capital for offshore (5.1%) with
    8% as the stress case. Say which numbers you want changed and whether
    the three redevelopment cases of notebook 02 part C (young oil, mature
    oil watering out, gas tail) should carry different uplifts.

### Addendum, 2026-10-12 — step (6): notebook 07 part B, the candidates and their economics

Alan confirmed the cost grid (decision #68) with one condition: results and
their impact visible to every viewer in the dashboard.

- `src/economics.py` (six tests): the Arps baseline and the incremental
  redevelopment cash flow under the grid, break-even WTI by bisection,
  2024 price-capture factors from the hourly North hub and the ERCOT
  system shapes, a one-cycle-a-day battery LP (energy only, no ancillary
  services; the simplest form of my Forecast-to-Dispatch dispatch), and
  the timing-weighted expected NPV of a request.
- **Notebook 07 part B.** The pool: 513 leases producing in 2024 with 60+
  producing months and all 2,268 test-cohort requests, each with a
  data-completeness score (ERCOT requests with v5 economics 1.0, other
  Track A 0.6, elsewhere 0.3; leases 0.8). Default book: the 20 leases with
  the most 2024 output (all young deepwater oil, 55% of the pool's 2024
  boe) and the 5 largest ERCOT requests of each technology (20 MW and
  more). Results on the flat 2024 real basis: lease incremental NPV
  $14.6B base (low-cost $16.6B, high-cost $9.2B), every lease positive,
  median break-even WTI in the pool from `candidate_npv.csv`; the twenty
  ERCOT requests −$0.76B merchant (none positive once P(operation by 7 y)
  of 0.06–0.23 and the cost to carry are priced in), wind +$20–28M each
  under a $62 PPA; capture factors solar 0.92, wind 0.83, gas CC 1.35
  (runs 63% of hours); battery $74.6k per MW-year; merchant break-evens
  solar $64, wind $50, gas $33 per MWh. Tornado: the uplift share
  ($5.9B–$21.8B) and the operating cost ($16.6B–$9.2B) dominate; the
  power price basis moves the book by under $0.5B. Figures F28, F29;
  tables `investment_candidates.csv`, `candidate_npv.csv`,
  `candidate_breakeven.csv`, `cost_sensitivity.csv`, `project_impact.csv`,
  `provenance_candidates.csv`, `upstream_cost_grid.csv`,
  `candidate_capture_factors.csv`. 138 tests pass.
- Next: step (7), `08_scenarios_and_risk`.

### Addendum, 2026-10-12 — steps (7) and (8): scenarios and risk, the four books

- **`08_scenarios_and_risk`** (decision #69, amended): 2,000 joint paths of
  240 months — block-bootstrapped 2018–2024 monthly shocks, demeaned, on
  log prices reverting to the 2018–2024 real means with a four-year
  half-life (the first run as a pure random walk put WTI at $13–$800 ten
  years out and was replaced before any criterion was scored); a held-out
  Gaussian-copula set (seed 2021) and an independent set for the
  correlation ablation; output multipliers one per lease or plant from the
  scored holdout (lease draws volume-weighted; mean 1.0, sd 0.26), cost
  multipliers triangular 0.75–1.5, operation years from the entry curves
  through the ρ copula (87% of the twenty requests never operate within
  seven years). Ten years out WTI sits in $27–$224 (5–95%). The default
  book: mean $20.6B merchant, no negative scenario, CVaR95 a profit of
  $1.5B; every named stress leaves it positive (worst: simultaneous
  downside, $12.1B from $13.8B on the flat base); removing the
  correlations changes the book's CVaR by $0.5B. F30–F32;
  `src/scenarios.py` with tests.
- **`09_portfolio` part D** (decisions #70, #71): C21–C24 registered first
  (budget 40% of the book's capital, technology cap 40%, contracted case,
  selection on the primary set, scoring on the copula set); the MILP on
  HiGHS with the CVaR linearisation (`src/optimizer.py`, solved in
  millions after a dollar-scale run stalled and returned an empty book —
  fixed, with an optimality check, before scoring). **All four lines fail:**
  D − A −$420M [−$659M, −$210M]; D − B −$150M [−$350M, +$24M]; Jaccard D
  0.95 vs C 0.99; C24's comparator is the near-empty power-only book. The
  finding: no book loses money in any scenario under the confirmed grid,
  so risk aversion buys nothing; the books converge on the twenty leases
  plus contracted wind and some gas (D: 24 candidates, $4.2B). Frontier,
  sensitivity (budget −20%, λ doubled, carbon $50/t, cap 25%: Jaccard to D
  0.84–0.96), ablations, the decision ledger with the six books, project
  impact with each candidate's share of book D's tail. F33.
- Next: step (9), `10_advisor_and_gym` — ASK ALAN items first:
  `ANTHROPIC_API_KEY` in `.env`, the verbatim text of the two prompts.

### Addendum, 2026-10-12 — step (9): the advisor, the gym and the forward view

- **`10_advisor_and_gym`** (decision #72): `src/advisor.py` (the Messages
  client with the grounding check, the JSONL record and replay, the two
  reasoning prompts as templates in `prompts/`, the override gate, the
  ledger append), `src/gym.py` (sixteen situations, four actors, the
  exact-knapsack hindsight), `src/horizons.py` (within-horizon value and
  the book at 1, 2, 3, 5, 10 and 20 years); tests `test_advisor.py`,
  `test_gym.py`, `test_horizons.py` (161 pass, 1 skipped). The notebook
  runs offline in 15 s: no key in `.env` yet, so every advisor row reads
  "not recorded" (33 calls missing) and the record is empty; the first
  live run fills `results/advisor_runs.jsonl` and every later run replays.
- **Gym, as scored:** the registered rule beats instinct by $99.6M a
  situation on average (regret against hindsight $197M vs $297M). In nine
  of the thirteen queue rooms (all of PJM and CAISO, ERCOT 2019) none of
  the fifteen largest requests operated within the window, so the best
  book is empty, instinct loses the gate costs and the rule, which held
  or exited, loses nothing; at the ERCOT two-year gate the rule held every
  request and missed the five that operated ($2.17B to instinct, $0 to the
  rule); in the lease regimes the MILP matches hindsight in two of three.
  F34.
- **Forward view:** the lease book is negative within 1–2 years
  (−$1.4B, the workovers), positive from year 3 ($0.2B), $14.6B at 20; the
  requests are a cost at every horizon (−$0.84B at 20 years, timing-weighted);
  the deterministic book is empty at 1–2 years, 12 leases at 3, 19 at 5,
  all 20 from 10. F35; `horizon_view.csv`, `horizon_books.csv`.
- The `claude-api` skill named in the prompt is not in this environment's
  skill list; the SDK's Messages call is used with the model id in one
  constant (decision #72).
- Next: step (10) — `app/app.py`, report v4, `docs/ai_use.md`, full
  `make all`. **ASK ALAN (still open):** #34 the verbatim prompts, #35 the
  key; one live run of notebook 10 after the key is in `.env` records the
  advisor's answers (then commit `results/advisor_runs.jsonl`).

### Addendum, 2026-10-12 — step (10): the dashboard, report v4, the AI note

- **`app/app.py`** (Streamlit 1.65, `make app`): *Decide forward* — budget,
  λ, cap and revenue case re-solve the risk-aware MILP on the 2,000 cached
  scenarios (the thin-data rule widens the spread and scales the cap by
  completeness), the four books beside it, the named stress, the forward
  view at 1–20 years, the advisor's recorded recommendation, the challenge
  round (live with the key, replay otherwise) and the override gate that
  writes to the ledger; *Learn from history* — the sixteen gym situations
  as of their dates, the human's pick scored against instinct, the rule,
  the advisor and hindsight, appended to the ledger as the human actor;
  *Scenarios and risk*; *Candidates and the cost grid* (the grid, F29,
  each project's impact, the completeness warning for every region); *The
  ledger*. Opened in the app's browser pane; both modes render. Notebook 09
  now keeps the ledger's appended entries.
- **Report v4:** the Capital Allocation Memo and the Decision Board
  (D0–D7) after the abstract; Part II §13–§24 (the portfolio problem, the
  v5 data and gate, the energy EDA, C20, economics and the tornado,
  scenarios, C21–C24, the advisor and the gym, the forward view, the Part
  II record, broader impacts and limitations, conclusion); Appendix A on
  the advisor (grounding, record and replay, the gate, the evaluation, the
  prompts); figures 15–21. `src/report_numbers.py` gains the v6 collectors
  (`v6_data`, `v6_forecasts`, `v6_economics`, `v6_scenarios`, `v6_books`,
  `v6_advisor`); `tests/test_report.py` exempts the section marks, table
  numbers, decision ids and source labels. `docs/ai_use.md` describes the
  AI as a system component (what it sees, record and replay, the gate, how
  it is evaluated). README: status, questions for both parts, map, results.
- The `make all` run of the ten notebooks and the final test count are
  recorded in the line below this entry.
- `make all` (2026-10-12, evening): all ten notebooks ran in order — 01 134 s,
  02 50 s, 03 26 s, 04 521 s, 05 432 s, 07 35 s, 08 51 s, 09 365 s, 06 668 s,
  10 14 s. The registered tables came out unchanged except float noise at
  the sixteenth digit in the tournament tables and the run-time columns of
  the check tables; the report's PJM gas five-year rate reads 31.9% as the
  table has it. 161 tests pass, 1 skipped (the word limit, decision #44).
  Report v4 built to PDF and DOCX.

### Addendum, 2026-10-13 — after the push

- Pushed main (26 commits, `d3b744f..ee84d45`); Alan's "1 to 4 yes" of
  13 Oct authorised the push; the key, the verbatim prompts and the ERCOT
  pull are still his to do (HANDOFF lists the commands).
- `tests/test_app.py`: the dashboard runs headless in both modes through
  Streamlit's AppTest (34 s), no key needed; `width="stretch"` replaces the
  deprecated argument. 163 tests pass, 1 skipped.
- `data/README.md`: the scenario parquet and the decision tables of
  notebooks 09 and 10 added to the dictionary.
- Open question 34: on 13 Oct Alan pasted a list of generic business-plan
  prompts (idea generation, validation, canvas); it does not hold the two
  reasoning prompts. Two of its lines fit the challenge round and are now
  in the templates — "if you were trying to convince me this is a terrible
  idea, what would be your strongest arguments against it?" opens the
  opposing case, and "the top three risks and what would mitigate them" is
  step 4 of the motivated-reasoning check. The draft status stays until
  the two prompts' own text arrives.
- Open question 34 closed (decision #73): the two reasoning prompts are
  final as written; the draft lines are gone. Notebook 10 rerun so its
  printed prompts match. Still open: #35 the key (then `make advisor`),
  #33 the ERCOT pull, #36 rotation.
- 13 Oct, later: `tests/test_panel.py` (the audits on a synthetic panel,
  the release lags as one set of numbers, one row per key and month in the
  built panel) and F36, the AI workflow diagram drawn by notebook 10 for
  Appendix A (Figure 22). 166 tests pass, 1 skipped. Report rebuilt.
- Poster draft: `report/poster.typ` → `report/poster.pdf` (`make poster`,
  A1 landscape, six panels built from the memo's sentences and F29, F33,
  F34, F35, F36; every number is the report's). README gains the target.

## Session 11 — 2026-10-14: the outside review, report v5

**Done**

- Outside review of report v4 logged item by item (`docs/mentor_feedback.md`,
  decision #74). Bugs found and fixed: the gym's two-year rule never funded
  (it looked for 'invest', the gate issues 'accelerate'); the EDA's gas
  combined-cycle capacity factor divided each prime-mover part by the
  whole plant (23% → 45% at plant level). The gym's rooms are now fifteen
  requests drawn at random, not the fifteen largest.
- Notebook 09 part E (post-hoc, labelled): the committee grid ($40k per
  incremental flowing boe/d, 8% real; ranges $25–60k and 5.1–10%): the
  twenty leases fall from $14.6B to $7.0B on four times the capital; the
  default book's median is $17.2B (registered) and $8.9B (committee)
  against means of $20.7B and $11.4B; under the committee grid it loses
  money in 16% of scenarios. The four books under the committee grid: D
  halves A's tail ($2.7B vs $5.3B worst-5% loss) at $3.4B of expected value;
  A still wins on the registered metric by $755M. Sustained $42 oil for
  five years: $11.5B (registered) and $4.25B (committee). Second power
  draw (the entry rule's invest class): contracted wind is still the only
  technology that pays. Naive-forecast ablation (proposal §10): book D is
  identical with naive output errors (overlap 1.00) — the allocation comes
  from the grid and the optimizer.
- Corrected gym: the registered rules beat instinct by $236M a situation
  (regret $18M vs $253M), almost all in the three lease regimes; queue
  rooms +$3.7M a room; the ERCOT 2017 two-year room +$41M.
- Figures: every report title cut to ≤ 12 words (`plots.SHORT_TITLES`);
  PNGs at 450 dpi; the PDF embeds the SVGs; y-labels taller than their
  axes shrink to fit; F0 (the project in one picture, report Figure 1),
  F37 (the committee grid), F36 at 11 inches.
- Report v5 under Alan's title, *Beyond Prediction: AI-Driven Energy
  Portfolio Decisions Under Uncertainty — From Machine Learning to
  Risk-Aware Capital Allocation*: short abstract, one-page memo led by the
  committee grid, reading guide and glossary, the questions and hypotheses
  up front, related work (15 references added), Part I rewritten finding
  first, a bridge, Part II in the proposal's order with an energy EDA
  section, a results table mapped to RQ1–RQ4, the proposal's five decision
  questions, limitations, conclusion, solo statement of work, the review's
  changes inline, appendices (record, advisor, proposal map, figures).
- `src/report_numbers.py`: v7 collectors (rounded Part I values, the
  post-hoc tables, the EDA facts, the five questions, the gym); the
  capacity factors are now read from the EDA table instead of typed.

**Next**

- One live run of notebook 10 with `ANTHROPIC_API_KEY` in `.env` scores
  the advisor; then `make numbers` and `make report`.
- The ERCOT 2020–2023 pull from another network.

**Open questions for Alan**

38. The memo recommends book D under the committee grid and states book A
    as the alternative; whether the committee's risk appetite favours A
    or D is a choice the report leaves to the reader — confirm that framing.

## Session 12 — 2026-10-14: closing session 11, the figure review, the advisor on the subscription

**Done**

- Session 11 was still running when this session started. It handed over
  at 07:54 without committing, and only one session committed.
- The figure review of all 26 report figures against the report. Every
  figure was already 11 inches wide at 450 dpi, with a title of 12 words
  or fewer. Fixed:
  - two titles that contradicted their own figure (F16, F23);
  - legends on the data (F27, F28, F33);
  - raw column names and a decision number (F29);
  - stale notebook pointers (F23, F26);
  - the old names "fair baseline" and "v2 model" (F11, F12, F22);
  - non-integer member counts (F35) and a missing dollar sign (F37);
  - a label touching a line (F24).
- The report, reviewed against the proposal:
  - §11's tornado sentence was wrong and is rewritten;
  - §6 states the ERCOT exception at entry;
  - §13 adds the carbon-price and risk-aversion sensitivities that the
    proposal's §10 asked for (overlaps 0.96 and 0.84);
  - Appendix A's tail sentence now names the held-out scenarios;
  - the Figure 6 caption and Table 8's RQ4 row are corrected;
  - `results/` paths are out of the body prose;
  - the proposal's correlation heatmap and asset map are added as
    Appendix Figures A8 and A9.
- The advisor gained a second backend (decision #76): `claude -p` on
  Alan's Claude subscription, with no tools, no files and no memory.
  Live calls failed with "OAuth access token has been revoked", so the
  command line needs `claude auth login`.
- A latent bug fixed: `claude-sonnet-5-5` rejects `temperature=0`, which
  the API path used to send.
- The poster now carries v5 numbers only, and a test checks every number
  on it against `results/report_numbers.csv`. Alan does not like the
  design; a new poster is to be built.
- `docs/demo_video_script.md`: about 4 minutes, numbers from the report.
- The ERCOT 2018–2023 pull was tried. `api.ercot.com` and `www.ercot.com`
  both return HTTP 403 to this machine, so it still needs another network.
- Open question 38 is closed (decision #77): D is recommended, with A as
  the alternative.

**Done, afternoon (Alan's answers: use the Max plan; pull ERCOT; the
recommendation stands; a new poster later; the challenge round with the
human in the loop; "do your recommendation" on the registered verdicts)**

- The advisor runs on the Claude subscription (decision #76): Alan signed
  the `claude` command in; notebook 10 ran live three times today as the
  tables changed, 96 calls recorded. Scores: 94% of its numbers are in
  its tables (52% of answers fully grounded; the rest is arithmetic it did
  itself), its stress books overlap book D by 0.89 (D named in 3 of 7),
  and in the gym it beat instinct by $228M a situation (rule $236M),
  matching the rule in 11 of 16 situations, regret $26M against hindsight.
  The checker now reads unit suffixes ("$6.15B") and re-verifies records
  on load.
- The "reason my thinking" round is a human-in-the-loop exchange written
  for the portfolio decision (decision #79): five questions tied to the
  statement, the human's answers, then the check and the opposing case;
  `python -m src.advisor` at the keyboard; the answers open the override
  gate. The DATA block moved to `advisor.portfolio_context`.
- ERCOT 2018–2023 hourly prices (decision #78): `src/ercot_history.py`
  parses ERCOT's public yearly files; `.github/workflows/ercot_history.yml`
  runs it on a U.S. runner (ERCOT refuses Brazilian addresses, hotspot
  included); six files, hashes pinned. February 2021 (Uri) is $1,772 a
  MWh real; 2021 averages $156.
- The pipeline rerun on the observed prices (decision #80); the
  bridged-price scoring kept in `results/registered_bridged/`. The first
  rerun put the books' means in the trillions: the block bootstrap and the
  copula carried the Uri spike without its reversal. Fixed (decisions
  #81–#82): monthly log changes capped at ±1.5, calendar-year blocks, a
  geometric long-run level, and the held-out set as a second draw of the
  bootstrap (the copula cannot keep a spike with its reversal). Results:
  default book mean $15.8B, median $14.9B; C23 and C24 pass on the
  observed prices, C21 and C22 fail; committee grid: D $5.8B with a $0.3B
  worst-5% loss against A's $7.7B and $1.3B; A still wins the registered
  metric by $888M. Gas requests are worth $427M between them in the
  scenarios (ERCOT spikes), negative on the flat path.
- Report Part II rewritten on the new numbers; Appendix A shows both
  scorings; Appendix B carries the advisor's scores and the new prompts;
  the poster's numbers updated (design still to be replaced).

- A clean `make all` reproduced every result offline (the advisor
  replayed its 96 calls); 178 tests pass; report and poster rebuilt;
  tagged v1.0 and pushed.

**Next**

- The new poster (open question 39).
- Rotation of the EIA key and the ERCOT password (Alan).

**Open questions for Alan**

39. The poster design: what should the new one look like (layout, which
    figures, the message)?
40. The scenario engine's cap of ±1.5 on a monthly log change (decision
    #81) is the one new assumption of the day; it keeps Winter Storm Uri an
    event rather than a level. Confirm, or name the bound you would use.

**Evening — the Petrobras Report (Alan: "this report will become a Petrobras
report, professional and executive, adjusted step by step; images inside
the report; do not override, I need both")**

- `report/petrobras_report.typ` → `make petrobras` → `report/Petrobras_Report.pdf`
  (25 pages, letter), modelled on the Forecast-to-Dispatch Petrobras report:
  cover, cover letter, contents, executive summary, purpose, nine stages
  with the figure under the paragraph that discusses it and a business
  consequence in every caption, results at a glance, why it matters for
  Petrobras, the transfer map, the management model, recommendations,
  limitations, one appendix (the record and the data). The academic report
  `report/report.md` is untouched.
- Stage 9 is written around the human-in-the-loop advisor: the five
  questions, the answers, the verdict, the opposing case, the gate.
- `tests/test_report.py` checks every number in the typst source against
  `results/report_numbers.csv`. First pass is configuration and figures;
  content is next, step by step with Alan.

**Later — the method stages, the executive figures, the challenge page**

- Stages 2–9 of the Petrobras report deepened: the regional clocks, the
  drivers, the ten rules, the clock, book sizing, the two gates with
  their table and the region-by-region rule; the leakage discipline; the
  per-candidate risk distribution; a sensitivity table; the gym room by
  room; the advisor's recommendation per stress.
- Alan: "the images are not professional, look at my example." The
  example's figures are single-panel, full text width, the finding and
  one line inside, no footer. `plots.save_executive` now saves a copy of
  every figure in that style (9 inches wide, tight bounding box, subtitle
  of at most two lines, no source footer; figures of three or more panels
  keep their width) in `figures/executive/`, called from `save_fig`; the
  academic figure is unchanged. The Petrobras report reads the copies at
  full text width with the source and provenance in the caption. A full
  `make all` regenerates them.
- `app/challenge.py` (`make challenge`, port 8502): the challenge round as
  one page. Alan: "explain first the alternatives, a little more
  interactive, still simple; I want an AI to decide and help to decide;
  make the HITL think." Four steps: the six books with capital, expected
  NPV, worst-5% and chance of a loss, and the advisor's recorded pick with
  its reasons and the figure at which its answer flips; the human picks a
  book, states why, and writes down what would change their mind before
  the advisor speaks; the five questions and the answers; the verdict, the
  case for the other book, the human's flip condition beside the advisor's
  final say, the two books' numbers side by side, the gate and the ledger.
  `tests/test_challenge_app.py`. The portfolio dashboard is untouched.
- Every figure's executive copy reviewed: figures of two or more panels
  keep their drawn width (their panel titles collide when narrowed); the
  F21 and F32 legends moved off the data; the diagrams F0 and F36 keep
  their width. Floating figures were tried in the Petrobras report and
  rejected: they drift across stage boundaries and away from the
  paragraph that discusses them, which is the one thing the example gets
  right. The gym's room-by-room numbers are collected
  (`report_numbers.v7_questions`, `room_*` keys).

## Session 13 — 2026-10-17: the prescriptive framing, report v6, the proposal update, the evaluation plan

An outside review asked for the step from predictive to prescriptive AI to be
the contribution. Decisions taken: the new title; a core + appendices report (he accepted about 3,400 words
rather than move the memo out of the body); the Nov 2 evaluation plan as a
chapter; the Oct 19 proposal reframed. Decisions #83–#85.

**Done**

- `docs/proposal_update_2026-10-19.md`: new title, the overarching question,
  RQ1–RQ4 as Predict / Quantify / Prescribe / Evaluate, the prescriptive core in
  §5, §8 rewritten from what was done (second bootstrap draw, not a copula;
  rolling origins; the gym; 70 lines / 28 pass; both price scorings kept), §11.
  Stale lines fixed (ERCOT 2018–2023 prices are observed). PDF built.
- `report/report.md` v6: the core rewritten (abstract, memo kept, sections 1–7,
  statement of work, changes after review); Parts I–II moved in full to
  Appendices E and F with figures, tables and section references renumbered;
  Appendix G holds the full results table and the five decision questions;
  Appendix C's proposal map rewritten. Five figures stay in the core (F0, F11,
  F33, F37, F34). Every number in the new text was checked against
  `results/report_numbers.csv` before the test ran.
- `tests/test_report.py`: word limit on at 3,500 over the text before Appendix A
  (3,432 today); appendix labels excluded from the number scan.
- `report/references.md`: three prescriptive-analytics references, verified.
- `docs/evaluation_plan.md` + PDF: section 3 of the report in Slack form.
- Title in README (status v6), poster.typ, the video script (figure references
  renumbered); `docs/mentor_feedback.md` item 8 and the outside-review label.
- HANDOFF rewritten at the top.

**Next**

- `make numbers && pytest -q` (report tests green on 2026-10-17); `make report`
  (built: 45 pages); read the PDF; `make poster`; a clean `make all` in a
  fresh environment before the tag; commit; tag v1.1.
- Nov 2: post `docs/evaluation_plan.md` in the team+mentor channel; paste the
  message link into Canvas.

**Open questions for Alan**

- Redraw F0 with the four-stage labels? (optional; one notebook rerun)
- The Petrobras report's title: when.
- Carried: the live challenge round; the ±1.5 cap; the poster refresh; key rotation.

## Session 14 — 2026-10-17: the pipeline rerun end to end, the report rebuilt

**Done**

- Notebooks 01–05 rerun and committed (14e0023): dates, run times and float
  rounding only.
- Notebooks 07, 08, 09, 06, 10 rerun in pipeline order (40 s, 81 s, 467 s,
  715 s, 20 s), all without error. Result changes are the decision-ledger dates
  and last-digit float rounding in the tournament tables; no reported value moved.
- `make numbers`: 2,241 numbers, identical to the committed file; `pytest -q`:
  182 passed. `report/report.md` needed no edit.
- Report PDF and DOCX rebuilt: 44 pages (the 13:16 build was 45; same text,
  page breaks moved). Every page rendered and checked.

**Next**

- Copy the new PDF into `report/` once the open copy is closed (the file was
  locked by a viewer), or rerun `make report`.
- `make poster`; a clean `make all` in a fresh environment; tag v1.1.

**Open questions for Alan**

- `src/value.py` has an uncommitted edit (14:34) that reads the PJM capacity
  table with `pdftotext -layout`. On this machine it finds only the even years
  2008–2026 and fails its assertion; the committed parser works. Not committed:
  keep, fix or discard?
- Carried: F0 four-stage labels; the Petrobras report's title; the live
  challenge round; the ±1.5 cap; the poster refresh; key rotation.

**Later — the end-to-end runs before the tag**

- Data: all 39 pinned raw files (25 in `manifest_v5.json`, 14 in
  `config.py`) match their SHA-256 hashes.
- `make all` on this machine, 01 → 10: only the decision ledger's dates and
  float rounding in the tournament tables changed (commit 61a8177, no cited
  number moved); every other notebook, result, processed table and figure
  came back byte-identical.
- A clean Linux environment (Python 3.11, `requirements.txt`) ran 02 → 10
  end to end. Notebook 07 failed on the first pass: `pdftotext` without
  `-layout` drops Table 5-23 on poppler 24.02, so `value.pjm_capacity_revenue`
  now reads the layout rows (decision #86; same prices to the cent). Second
  pass clean; 182 tests pass there; the registered verdicts and 2,234 of
  2,241 cited numbers identical (decision #87 has the record).
- README: `pdftotext` named as a requirement; the advisor replay's exact-text
  key explained.

## Session 15 — 2026-10-17: the independent audit, the v8 plan, the implementation corrections

**Done**

- The open question on `src/value.py` is closed: the `-layout` parser was
  committed as decision #86. It needs poppler (scoop's 25.07 reads all twenty
  years); Git Bash's mingw Xpdf 4.00 finds only the even years, so the
  pipeline runs with poppler first on the PATH.
- An independent audit of report v6 and its code: `docs/audit_2026-10-17.md`
  (issue register with severity, evidence, correction, files). Five
  findings change the memo: A1 (books A and B ignored the registered 40%
  technology cap), E1 (10 of the 20 ERCOT candidates were withdrawn or
  operating by the end of 2024; all five gas requests are resolved), E2 (10
  of the 20 lease baselines fitted with zero decline), G1 (the gym's lease
  rooms use 2024 leases, 2024 fits and the realized future's mean), G5 (the
  advisor trails the rule by $8.0M a situation, CI [−17.5, −1.3]).
- `docs/implementation_plan_v8.md`: freeze → implementation corrections →
  framing corrections (need Alan) → six decision layers → the
  decision-process evaluation → figures → report. Decisions #88–#89.
- Phase A: `results/registered_v7/` holds the v7 scoring at 61a8177, with a
  hash manifest and `tests/test_registered_frozen.py`.
- Phase B (implementation corrections A1, A13, E10, G2): the cap on the
  comparators, one CVaR with the right tail count, the gas heat content, the
  gate floor from the pool's expected rate. Notebooks 07, 08, 09, 06, 10
  rerun. Against the frozen record: C21 −$19M [−71, +33] (was −$61M; still
  FAIL, the interval now spans zero), C22 +$46M (FAIL), C23 and C24 PASS as
  before. Committee grid: capped A expects $5.52B with a $0.44B worst-5% loss;
  D $5.86B and $0.29B; D − A = +$494M [+423, +554]. The queue rooms' rule edge
  over instinct is now −$0.65M a room (was +$3.69M). 197 tests pass; the
  three report-number tests fail because the report text is v6 and the
  numbers moved — the report is rewritten once Phase C lands.
- Work is on branch `v8-corrections`; `main` keeps the consistent v6 report.

**Next**

- Phase C after Alan's four decisions (decision date, decline floor, power
  budget charge, scope and word limit); then Phase D.

**Open questions for Alan**

- The four decisions of `docs/implementation_plan_v8.md`.
- Push `v8-corrections`?
- Carried: F0 labels; the Petrobras title; the live challenge round; the
  ±1.5 cap; key rotation.

## Session 15, continued — 2026-10-17: the framing corrections, the decision layers, report v8

Alan chose the recommended option on all four framing questions (decision #90).

**Done**

- **Decision date 1 January 2025** (`src/decision_date.py`, notebook 04 part L). The power pool is the 1,649 ERCOT requests of 20 MW and more still waiting (about 359 GW); each request's seven-year chance is conditional on its age. Two guards were needed: a request without an agreement is read with the plain model (the agreement model holds the flag at zero for every later year), and the request year is capped at the last cohort with five closed years (read at 2024, the trees put a new request's first-year withdrawal at 0.73). Backtests as of 2018 and 2020: the model ranks better than the lookup (AUC 0.738 against 0.686 as of 2020) but over-predicts ERCOT's level (0.388 against 0.238); the ratio, 0.614, corrects the 2025 curves. The lookup travels with the candidates as the naive benchmark.
- **Lease baselines** with an 8% terminal decline (`decline.floored_baseline`; C20's forecasting baseline untouched): registered lease book $8.23B (was $14.6B), committee $2.74B for $5.15B of capital.
- **Valuation engine** (`src/valuation.py`): the repricing moved out of notebook 08; ATB costs in 2024 dollars; credits by operation year; the stage-one charge.
- **Budget** (decision #92): 40% of the stage-one charges. A first attempt at 40% of full capital left nothing binding and books A, B and C identical; it stays as a sensitivity.
- **Held-out set** redrawn in every component; the gym's lease rooms rebuilt as of their date and counted as one situation; two new actors (instinct per dollar, nothing).
- **Decision layers** (decision #91): `src/whatif.py`, `src/advisor_tools.py` with `prompts/whatif_*.md`, `src/ledger.py`, `src/voi.py`, `src/dynamic.py`, `app/decide.py` (`make decide-page`); notebook 11 runs them (`make decide`).
- **Results (committee grid, held-out, post-registration).** D beats NPV ranking by $293M [+151, +441] on the registered metric, for $130M of expected value; the lookup's book is not beaten by the model's (−$146M [−325, +30]); revision in 2027 −$13M [−24, −4]; EVPI $482M, ERCOT price level $40M; the advisor read six questions correctly and its 102 cited numbers were all in the fact sheets; its investment increment is zero; in the gym it trails the rule by $5.1M [−11.0, −1.5]. On the registered grid C21 and C22 pass on the corrected system (Table A2), labelled as new results.
- **Report v8**: the eleven sections of the brief, core 3,499 words by the test's rule, every number keyed (`v8_report` in `src/report_numbers.py`); Appendix A keeps the registered record from `results/registered_v7/`; Appendices F, G rewritten; H added (the audit).
- Figures F38–F44 looked at and fixed (titles that stated the wrong finding, legends over data, overflowing diagram text); F34 and F33 retitled from their results.
- 224 tests pass. The poster and the Petrobras edition still describe v7; their number tests read the v7 numbers table frozen with the record.

**Next**

- Rewrite the Reading-this cells of notebooks 07–10 from their new outputs (they still describe v7).
- Poster and Petrobras edition for v8; a clean-environment run of v8; tag.

**Open questions for Alan**

- The memo now presents a trade-off rather than one book; is that the framing you want for the committee?
- Push `v8-corrections`, and merge it into `main` when you have read the report?
- Carried: F0 labels (superseded by F43?); the Petrobras title; the live challenge round; key rotation.

## Session 16 — 2026-10-18: the reading cells of notebooks 07–10 on v8

**Done**

- Rewrote the markdown that still described v7 so that every number is one the notebook now prints (code cells and outputs untouched; checked cell by cell against the committed notebooks).
  - `07_economics`: cells 36 (Part A takeaways: test cohort vs the 2025 candidates), 37 (Part B introduction: one decision date, the live ERCOT pool, the stage-one charge), 40 (the decline floor), 44, 47 (was a placeholder), 51, 54, 55.
  - `08_scenarios_and_risk`: cells 0 and 1 (introduction; inputs table, which named inputs the notebook does not read), 7, 15, 18, 21, 24.
  - `09_portfolio`: cells 32, 36, 42, 45 (the gate counts after decision #89's floor: 166/203 invest at entry, 178/251 accelerate two years in), 101–102 (Part D introduction: what is registered, what is post-registration), 108, 115, 119, 124 (C21–C22 pass, C23–C24 fail on v8, the reverse of the frozen v7 verdict), 127, 130, 132, 133, 135, 138, 139, 141, 144, 146, 147 (Part E bullet added).
  - `10_advisor_and_gym`: cells 7, 10, 14, 17, 21 (gym on fourteen effective situations: rule − instinct +$56M [−12, +176], advisor − rule −$5.1M [−11.0, −1.5]), 26, 35, 36.
- 224 tests pass.

**Next**

- The poster and the Petrobras edition for v8; a clean-environment run; tag.

**Open questions for Alan**

- `results/decision_ledger.csv` keeps a `NB10-advisor-base` row from v7 (26 members, $5.37B of capital against the $1.79B budget): notebook 10 appends it only when absent, so it was never replaced. Delete the row and rerun 10?
- F0's bottom line counts leases, wind and gas of the committee book D, which also holds $0.48B of solar; the label needs solar.
- Notebook 09 E.6 scores the naive-forecast book on held-out values that reuse the primary set's output and cost draws (stated in its reading cell); redraw them as in notebook 08?
- Notebook 09 E.5's second power draw can only hold 2017–2019 entrants still waiting in 2025 (the entry rule ran on that cohort); keep it as a post-hoc check or drop it?

## Session 17 — 2026-10-19: the four open items of session 16 (decision #93)

Alan's answers: correct and keep the ledger row; F0 shows every technology; redraw E.6's held-out draws; fix E.5. No new notebooks.

**Done**

- `10_advisor_and_gym`: the `NB10-advisor-base` ledger row is rewritten on every run; it is now the advisor's base pick (16 members, $1.79B of stage-one charges against the $1.79B budget, book C's held-out scores). F0's bottom line names every technology of the committee book D ("6 leases + 5 wind + 1 solar under contract + 2 gas"), set at 11 pt so it fits its box; the PART I band text no longer overlaps "queue engine". Reading cells 35 and 36 updated.
- `09_portfolio` E.5: the second power draw applies part A's entry gate (hurdle 3) to the 1,649 requests live on 1 January 2025. It invests in 212 solar and 58 wind requests and exits every gas and storage request; the five largest solar (0.30 chance) and wind (0.30) all pay under contract (+$99M and +$877M). E.6: the naive book is scored on held-out output and cost draws (metric $9.56B against $9.81B; selection unchanged, Jaccard 0.95). Cells 124, 139, 141, 144 and 147 updated.
- Notebooks 09 (781 s) and 10 (replay, 35 calls, none live) rerun; only `posthoc_power_draws.csv`, `posthoc_ablation_naive_forecasts.csv`, `decision_ledger.csv` and F0 changed.

**Next**

- The poster and the Petrobras edition for v8 (both embed F0); a clean-environment run; tag.

**Open questions for Alan**

- Push `v8-corrections`?

## Session 18 — 2026-10-19/20: expert review, decision #94, phase 1 (the decision date made honest)

**Done**

- `docs/review_2026-10-19.md`: an expert review of report v8 (strengths, twelve issues rated, the active-advisor specification, experiments, report structure, roadmap), with read-only diagnostics. Alan's decisions are recorded as decision #94: an executive report of up to about 4,500 words; fewer, larger, vector figures; an advisor that challenges and guides through validated tools (including a repair tool), measured against the committee's own proposal in risk-adjusted NPV and loss avoided, with a no-LLM checklist as control; scripted committee personas plus Alan's own decisions as the human side; the look-ahead fixed first.
- **Phase 1, the look-ahead.** An input-by-input audit found three leaks into the 1 January 2025 decision, now fixed: (1) the 2027 wind and solar credit deadline came from the July 2025 law and IRS Notice 2025-42 — the base case is now the law in force on the date, the deadline a "2025 law" stress (`valuation.CREDIT_POLICIES`); (2) agreement dates backfilled from the 2026 LBNL edition fed the 2025 view — every as-of view now uses the 2025 edition (`decision_date.agreement_dates_on`), the registered landmark tests keep the merged dates; (3) lease months October–December 2024 were not yet published — lease history now stops at September 2024 and baselines start at the decision date (`decision_date.lease_history_on`, `lease_baseline_on`), in notebooks 07–10 and the engine.
- **Robustness in notebook 11** (`src/robustness.py`, section 9, figure F45): in- vs out-of-sample scores, re-selection on 20 resampled primary sets, capital calls against the reserve with a funding-or-forfeit valuation (funding order fixed in advance — a first version ranked by each scenario's realized value and flattered a limited line), and tail dependence.
- Notebooks 04, 07, 08, 09, 06, 10, 11 rerun (07 onward under PowerShell: Git Bash's own `pdftotext` splits the PJM table differently, decision #86). Registered results unchanged (tournament files differ by float rounding only). Advisor: 19 live calls in notebook 10 and 11 in notebook 11, now recorded.
- Reading and takeaway cells of 07–11 rewritten from the new outputs; notebook 11 made to print every table its cells cite.
- Report v8 brought to the corrected numbers and verdicts (interim; the executive restructure is phase 4): the memo now names the contingent construction line; Table A2 and the hypotheses read C21 pass, C22–C24 fail on the corrected system; new number keys for the robustness results and the credit stress. Word limit 4,500 (decision #94).
- Tests: 234 pass (10 new: credit policy, the as-of helpers, the robustness checks).

**What moved (committee grid, held-out, post-registration)**

- Book D: 13 members (6 leases, 5 wind, 1 solar, 1 gas), $2.05B expected, 10.4% chance of loss, worst-5% loss $1.02B (was 14 members, $1.92B, 13%, $1.33B). D beats NPV ranking by $320M [+142, +511] on the registered metric, giving up $274M of expected value; the ranking holds in all 20 re-selections ($116M–$352M); 11 of 13 members are core.
- Capital: the construction reserve ($2.06B) is exceeded in 44.5% of scenarios; without a liquidity line book D is worth $1.40B, with a line at the 95th percentile of the excess ($3.28B) $2.02B.
- With the credits in force all ten wind and solar requests of the default book pay under contract (+$70M; −$284M under the 2025-law stress). ML increment +$22M [−168, +207]; revision in 2027 −$9M; EVPI $571M, ERCOT price level $52.5M.
- Registered grid, applied to the corrected system: C21 passes (+$1,332M), C22, C23 and C24 fail.

**Next**

- Phase 2: the challenger tools and prompts; fix `advisor.portfolio_context`, whose books table shows full capital where the budget counts stage-one charges (the advisor itself flagged it in the all-leases round).

**Open questions for Alan**

- None blocking. Push `v8-corrections` when you have read the review?

## Session 18, continued — 2026-10-20: phase 2, the active challenger (decision #95)

**Done**

- `src/challenge.py`: the language model reads the committee's statement into `Preferences` and may request up to two what-ifs; tools diagnose the proposal (rules, capital calls, tail dependence, risk contribution, drop tests) and compute the repair and the optimizer's book under the stated preferences; the model writes a challenge memo from the numbered fact sheet; code checks numbers, fact references and the guide rule. `checklist` is the no-model control. Prompts `challenge_read.md`, `challenge_memo.md`.
- `optimizer.solve_milp`: a change limit to a reference book (the repair) and a liquidity line as a CVaR limit on construction calls beyond the reserve.
- `ledger`: a decision that departs from a guided book needs the evidence acknowledged.
- `advisor.portfolio_context` shows stage-one charges against the budget (the defect the advisor flagged in session 18).
- A development trial on the gas example (records kept outside `results/`): the challenger read "one-in-eight chance of loss" and "one billion beyond the reserve" correctly, tested ERCOT prices 25% lower and half as volatile, found the proposal breaks its own liquidity line (95th-percentile calls $3,281M against $1,000M), and guided to the repair — drop the gas request and five fragile requests — which within the line gives up $373M of expected value and halves the worst-5% loss ($963M to $510M), its metric gain [−81, +243] not clear of zero, which the memo said. 44 of 45 numbers grounded.
- Tests: 243 pass.

**Next**

- Phase 3: register the experiments (C25 onward) before any run — X1 seeded flaws, X2 misspecified worlds, X3 preference translation — with 8–12 committee personas and Alan's own decisions; then run them in notebook 11.

## Session 19 — 2026-10-20: phase 3 registered (decision #96)

**Done**

- `src/challenge_experiments.py`: ten personas, 48 cases (36 flawed, 12 clean), 40 rule statements (8 out of scope), the runners and the scoring for X1–X3, criteria C25–C32 and thesis H4–H7. The case builder checked all 48 keyed flaws against the facts the challenger sees.
- The memo prompt asks for the type of each vulnerability, so detection is scored without a judge; `challenge.held_matrix` caches the held-out repricing per what-if.
- Registration written to `results/v9/` (criteria, cases, statements, and the hashes of cases, statements, prompts and model) and committed before any challenger run; notebook 11 section 11 checks it on every run.
- Tests: 6 new in `tests/test_challenge_experiments.py`.

**Next**

- Run notebook 11 (live advisor calls), score C25–C32, write the reading cells and figure F46.

## Session 19, continued — 2026-10-20: phase 3 run and scored

**Done**

- Live run: 136 advisor calls (48 cases × 2 rounds, 40 readings), none failed; records in `results/advisor_runs.jsonl`, `results/v9/x1_outputs.jsonl`, `results/v9/x3_outputs.jsonl`. Notebook 11 section 11 replays them, scores C25–C32 and draws F46.
- Six of eight registered lines pass. C25 11 of 12 reasoning flaws named (checklist 0); C26 24 of 24 (checklist 24); C27 fails (2 of 12 clean cases challenged with an unsupported claim); C28 fails by one memo (38 of 48 fully grounded; 14 of 1,771 numbers not on a sheet, no unit error); C29 +$192M per case [+108, +281] (checklist +$145M); C30 $240M of worst-5% loss avoided [+133, +345] (checklist $257M); C31 +$46M [+4, +116]; C32 32 of 32 read, 8 of 8 refused. H4 not supported; H5, H6, H7 supported.
- Decision #97: C31 rests on four cases where the challenger chose the optimizer's book over the repair; against a fixed rule that takes the optimizer's book first the edge is +$1M [−50, +64]. Reading cells say so.
- `report_numbers.v9_challenger` keys for the report.

**Next**

- Phase 4: the executive report (about 4,500 words) with the challenger as a findings section, F46 and a workflow figure; figure overhaul.

**Open questions for Alan**

- The case design let every reasoning-flaw case that warranted a new book also break a computed rule, so the language model's reasoning could not change a book on its own. A second round of cases where only the argument is wrong would test that — worth registering, or report the limit as it is?
- Your own decision cases (the reserved slot): when you want to write them.

## Session 19, continued — 2026-10-20: phase 4, the executive report (decision #98)

**Done**

- Report v9 core rewritten (4,223 words): abstract, executive summary, memo with "before you sign", twelve sections with three findings sections — the trade-off, capital and timing, and whether challenging improves the committee's decision — Table 3 for the challenger, limits and governance with the simulated committees named.
- Appendices: Table A3 (C25–C32 and H4–H7, with the decision #97 checks), the challenger in Appendix B, the new modules in Appendix C, F39 and F41 moved to Appendix D, two rows in Appendix G; a stale "(Figure 2)" in E.3, left from v6, removed.
- Figures: F43 redrawn as the six-stage workflow; F42 labels; F45 legend; F28 title and lease labels. Notebooks 07 and 11 rerun.
- Answered Alan's question "is the LLM improving the results": the challenged decision is better than the proposal (+$192M per case, $240M of tail avoided), mostly through its tools (checklist +$145M, $257M); the language model's own part is reading rules and arguments.

**Next**

- Phase 5: the poster and the Petrobras edition brought to v9; a clean-environment run; tag on Alan's word.

## Session 19, continued — 2026-10-20: phase 5, the derived documents and the push (decision #99)

**Done**

- Poster rewritten from report v9 (one A0 landscape page; F28, F42, F43, F38, F46, F45 as SVGs) and the Petrobras edition rewritten for v9 (19 pages); both number tests read the live table, and both pass.
- `README.md` status line and `docs/v8_status.md` (a v9 table at its head) brought up to date.
- Pipeline rerun from PowerShell: notebooks 01–10 end to end (06 resumed after a OneDrive lock on `report/figure_notes.md`); 11 was stopped at Alan's "just finish" — it last ran cleanly at about 20:50 the same day on the same inputs. No result moved beyond dates and run-time checks.
- The rerun showed notebook 10's advisor evaluation counting the challenger's 136 calls (171 became 331 calls, grounding 87%); it now excludes the two challenger modes, which notebook 11 scores under their own checks: 195 calls, 94% grounded. Two uncited figures moved on replay (overlap with book D 0.96 → 0.92; book D named in 3 of 7 stresses, was 4). Appendix B updated.
- `report.pdf`, `poster.pdf` and `Petrobras_Report.pdf` rebuilt; 250 tests pass.
- `main` fast-forwarded to `v8-corrections`; both pushed to origin at Alan's word ("merge").

**Next**

- A tag on Alan's word; a clean-environment (Linux) run of v9; Alan's own decision cases; the decision page could expose the challenger; `docs/demo_video_script.md` still describes v6.

## Session 20 — 2026-10-21: plan v10 approved; phase 1 (decisions #100–#102)

**Done**

- Alan's critique review read and checked against the repository: the as-of claim fails (the 2025 edition did not exist on 1 January 2025); no cost of the line existed; the challenger's statements and keys were model-written; C29–C31 used 36 cases; nothing compared a reading with its statement. Plan written, checked against the capstone criteria, approved.
- The liquidity line priced (`src/robustness.py`, config constants): notebook 12 sections 1–2 (the registration ledger, the line net of financing, F48). The line is worth having for expected value, not for the registered metric.
- `src/registration_ledger.py`: 78 lines, 17 with a correction, 3 correction rows with a changed verdict; `docs/registration_ledger.md`.
- `src/challenge_v10.py`: templated statements for the 24 computable cases, the loader and the blank form for Alan's 24 cases (`results/v10/cases_v10_form.json`), paraphrase and injection drafts, criteria C33–C41, H8–H10, `registration()`.
- `decision_date.candidates_as_of`, `iso_files.read_ercot_gis(report_month)`, `get_lbnl.record_hash`, with tests; notebook 12 added to the pipeline and the Makefile; `report_numbers.v10_report`.
- Tests: 261 pass.

**Next**

- Alan: fill `results/v10/cases_v10_form.json` (24 statements and keys), approve the paraphrase and injection drafts, download the 2024 LBNL data file and the 2024 monthly GIS reports (April–November) into `data/raw/lbnl/` and `data/raw/iso/gis_2024/`.
- Then: hash the files, run the as-of build, write and commit the v10 registration, run the four arms.

**Open questions for Alan**

- Are the line's rates (0.5% undrawn, 8% drawn, two construction years) the ones to register, given that the interest may double-count ATB's construction-finance factor?

## Session 20, continued — 2026-10-21: the work that needs none of Alan's files (decision #103)

**Done**

- Realized 2025 data pulled: ERCOT 2025 day-ahead prices (workflow run 39693715189 into `data/raw/forward/`), BSEE 2025 OGOR-A (`data/raw/bsee/forward/`); EIA prices were on disk.
- `src/forward.py` and notebook 12 section 3: 43 of 1,649 live ERCOT requests operated in 2025, where the level-corrected model expected 104 and the lookup 24; slopes 0.75 against 0.07; oil and ERCOT prices inside the scenario bands, Henry Hub above; the twenty leases at 1.03 times their baseline; F49.
- Section 4: on 5,000 paths the books keep their order, D's margin over NPV ranking $256M (against $320M); without the candidates' co-movement D's worst-5% loss falls from $1.02B to $0.30B; a tail weight of 2 or 4 beats 1 in three of four misspecified worlds.
- Section 5: the ladder on the v9 cases (preview, rerun on the registered line cost): tools +$110M, the language model +$35M over the tools, the optimizer +$103M over the challenger; 41 of 48 readings equal their key; F47.
- `src/whatif.Engine(state_file=)`; report keys for sections 3–5.

**Next**

- Alan's files (cases, approvals, the 2024 edition, the GIS reports); then the as-of build, the v10 registration, the live run.

## Session 20, continued — 2026-10-21: the line's cost decided (decision #104)

- Alan chose the fee and the interest as the registered line cost. Config comments updated; notebook 12's ladder preview rerun on that cost.

## Session 21 — 2026-10-22: the registered run built, waiting on its material

**Done**

- `src/challenge_v10.py`: `with_members` (the proposal books of the v10 cases), `run_readings` (paraphrases, reading only), `run_injections` (both rounds on book D, so the memo is tested too), `score_readings`, `score_injections`, `score_criteria` (C33–C41 by their registered rules), `write_registration` (writes once, then refuses a changed record), `run_live` and a command line: `python -m src.challenge_v10 register`, then commit, then `python -m src.challenge_v10 run`. The run refuses to call the model unless the registration is committed.
- Notebook 12 section 6: checks the registration, replays the recorded outputs (the advisor in replay mode, so the notebook never calls the model) and scores the nine lines; until the registration exists it prints what it is waiting on and stops.
- Tests on toy records: an injection holds only when the key is read unchanged and the instruction is named; the criteria follow their registered rules; the registration writer refuses a changed record. 268 tests pass.

**When Alan's files arrive (in this order)**

1. `results/v10/cases_v10.json`, `paraphrases.json`, `injections.json` (from the form and the drafts).
2. The 2024 LBNL edition and the 2024 GIS reports: hash them into `config`, run `python -m src.asof_candidates` (to be written on the pattern of `decision_date.candidates_as_of`), and if the candidate set changes, rerun notebooks 07–12 before registering.
3. `python -m src.challenge_v10 register`; commit; `python -m src.challenge_v10 run` in the background (about 48 × 2 + 40 + 20 × 2 = 176 calls); `python run_pipeline.py --only 12`; reading cells; keys; report.

## Session 22 — 2026-10-22: the as-of switch, the registered v10 run, and the data for a grader (decisions #105, #106)

**Done**

- Decision #105 applied: notebooks 04–12 rerun on the candidates public on 1 January 2025 (16 of the 20 stand; book D is now 5 leases and 8 requests, $2.17B expected, $0.82B worst-5% loss; D over the NPV ranking +$219M [+13, +401]); the v9 record frozen with a hash manifest; the registration written and committed before any call (62b2100).
- The live v10 run: 176 calls, none failed, every record present (`results/v10/*_outputs.jsonl`). Notebook 12 replayed and scored the nine lines (`results/v10/success_criteria_v10_scored.csv`): six of eight graded lines pass. C33 +$219M [+13, +401] PASS; C34 +$43M [+9, +86] PASS; C35 +$76M [+13, +140] PASS; C36 +$134M [+72, +211] reported; C37 38 of 48 FAIL (eight readings set the tail weight to 0 where the statement is silent and the key keeps 1; two invented an exclusion); C38 40 of 40 PASS; C39 15 of 20 held and 7 memos with an ungrounded number FAIL; C40 0 of 12 PASS; C41 12 of 12 PASS. H8 and H10 supported, H9 not. The model's arm sits behind the checklist in the ERCOT-25%-lower world (274 against 359 $M) and ahead in three of the other four. Nothing re-scored; the reading cell of section 6 says all of this.
- Report keys `v10_c33`…`v10_c41`, `v10_pass` (`results/report_numbers.csv`, 2,539 numbers).
- For the grader's end-to-end run (decision #106, b59de91): `data/raw_manifest.csv` lists the 111 raw files with source and SHA-256; `python -m src.get_data check | fetch | bundle` (`make check-data`, `get-data`, `bundle-data`); `data/README.md` S18 and S19; `make setup` builds `.venv` from Python 3.11 by name; every notebook names the `queue-survival` kernel (`tests/test_notebooks.py`). The bundle (137 MB) is in `dist/`, git-ignored, for a reader on request.
- An editor re-pointed `.venv/pyvenv.cfg` at Python 3.12 at 13:28 and every import broke; restored to 3.11.9. 273 tests pass.

**Next**

1. The reading and takeaway cells of notebooks 04–11 still quote the pre-switch numbers; rewrite them from the rerun outputs.
2. Report v10 (Q0–Q3; title kept) and the poster from the v10 keys; then `REPORT_V10_WRITTEN = True` in `tests/test_report.py` so the document tests read the live table.
3. The clean Linux run (needs Alan's sudo for python3.11 and poppler).

**Open questions for Alan**

- C37 and C39 failed on a specific reading habit (silence read as zero tail weight; numbers not on the sheet). The report states the failures as registered. A follow-up test with a prompt that states the default explicitly would be post-registration and labelled as such — only if Alan wants it.

## Session 22, continued — 2026-10-22: report v10 and the poster

**Done**

- `report/report.md` rewritten from the v10 keys (decision #107): abstract, executive summary and one section per question (Q1 prediction, Q2 optimization, Q3 governance, Q0 attribution), limits, conclusions; the memo as Appendix I; Appendices A–H carried over with the as-of numbers (Table A2 on the corrected system now +$468M / +$95M / 0.93 against 1.00 / +$77M; Table A4 is Table 3 of the body). Body under the 4,500-word ceiling; every number in the live table (`tests/test_report.py`, `REPORT_V10_WRITTEN = True`).
- `report/poster.typ` rewritten: the four questions with F49, F43, F38, F50 and F48.
- Notebook 12: F50 (the registered ladder) drawn in section 6; F49's legend names the candidate the 2026 file does not list; the forward-test reading cell and Takeaways corrected to the as-of run (1,441 live, 30 operated, 78 / 17 expected, slopes 0.66 / 0.01).
- Keys added: `v10_c33`…`v10_c41`, `v10_pass`, `v10_calls`, `v10_asof_*`, `v10_bt_ercot_auc_*`, `v10_prior_c33`.

**Next**

1. `make report` and `make poster` once the notebook-12 rerun has written F50; look at both; commit and push.
2. The reading and takeaway cells of notebooks 04–11 (pre-switch numbers).
3. The clean Linux run.

## Session 22, closed — 2026-10-22: the notebook cells on the as-of run

**Done**

- `make report` and `make poster` on F50; report.pdf, report.docx and poster.pdf rebuilt and looked at (2bbc8f2).
- Notebooks 04 and 07–11: 33 reading and takeaway cells rewritten from the as-of outputs (f23e60e); notebooks 05 and 06 changed only in run times. Found on the way and corrected in the report: book D's gas request is the 697 MW one with an agreement ($437M, loses in 63%, worth $144.6M to the objective) and the 1,350 MW request stays outside (forcing it in costs $108.7M); redevelopment capital 30% higher no longer empties the lease side (two members leave, three enter, $0.91B of leases stay, 15% chance of a loss) — only oil at $45 does. Keys `v8_bookgas_*`, `v8_wi_*`.
- 273 tests pass; every number in the report and the poster is in the live table; the body is under the ceiling.

**Next**

1. The clean Linux run (needs Alan's sudo for python3.11 and poppler); `make check-data` there with the bundle.
2. A read of report v10 by Alan; the demo video script (`docs/demo_video_script.md`) still describes v9.

## Session 23 — 2026-10-23: the demo video script on report v10

**Done**

- `docs/demo_video_script.md` rewritten for report v10: the opening asks the three questions and the fourth; Q1 on F49 (AUC 0.731 against 0.686; 30 of 1,441 operated, 78 and 17 expected); Q2 on F38 and F48 (C33 +$219M [+13, +401], $508M of expected value for a worst-5% loss of $0.82B instead of $1.55B, the $2.53B line worth $1.03B net of fee and interest); Q3 and Q0 on F50 and Table 3 (tools +$76M, the model +$43M [+9, +86], the optimizer +$134M; C37 and C39 stated as failed). Every number checked against the report body; 608 spoken words, section times reset to 140 words a minute.
- `docs/next_session_prompt.md` says the script describes v10. 273 tests pass.

**Next**

1. The clean Linux run (needs Alan's sudo for python3.11 and poppler); `make check-data` there with the bundle.
2. Alan's read of report v10; recording the video from `report/report.pdf` when he is ready.

## Session 24 — 2026-10-23/24: the clean Linux run (decisions #108–#112)

**Done**

- The clean-environment run, without Alan's sudo: Docker Desktop on this machine (it had crashed on a stale
  analytics socket; its `run` folder was moved aside), a `python:3.11-slim-bookworm` container with poppler 22.12,
  the committed repository (`git archive`) and the raw-data bundle, no `.env`. Five runs; each stop was a fault a
  grader would have met, fixed and committed before the next:
  1. Notebook 01 required `EIA_API_KEY` with every EIA file on disk, and asked the API for its latest EIA-860M month,
     now 2026-08, so a rerun with a key would have pulled a newer inventory: month pinned (`config.EIA860M_PERIOD`),
     key optional (#108, 5e376de, 60dc248). `libgomp1` named in the README for LightGBM on Linux.
  2. Notebook 02's asset map read 03's `trackA.parquet` before 03 had run: the pipeline runs 03 before 02 (#109,
     0269e42); a static check finds no other interim file read before its writer.
  3. The bundle left out the per-folder `SHA256.txt` records, and notebook 04 asserts the ISO snapshots against one:
     `bundle()` now carries all 13 (#110, 50a1934); `dist/raw_data_bundle.zip` rebuilt (125 entries).
  4. Notebook 12 stopped at the v10 registration guard: on Linux `results/v8/value_added.csv` drifts in the fifth
     significant figure (C33 $219,173,642 against $219,195,835), so its registered hash fails, and the memo replays
     could not be found anyway. Section 6 now checks `challenge_v10.replayable()` first and, elsewhere, says why and
     keeps the committed scored record; `report_numbers` writes "no record" for an unrecoverable advisor statistic
     (#111, cbe1bdc). Here the section replays and scores exactly as before (run times only).
- The reproduction record (#112): 01 → 11 end to end in 3 h 3 min (notebook 04 2 h 7 min), 12 in 228 s after #111;
  of 407 result files 86 identical, 199 within 1e-6, 122 different (run times, replay tables, 1e-5 to 1e-4 drift);
  every registered verdict identical; one checks line changed (a run-time limit); of 2,561 cited numbers 2,548
  identical as printed, two moved in the last digit ($6.71B → $6.72B; $108.7M → $108.6M) and eleven advisor
  statistics moved because 14 calls could not be found; 273 of 274 tests pass there (the report-number test).
- `HANDOFF.md` and `docs/next_session_prompt.md` brought from v9 to v10. 274 tests pass here.

**Next**

1. Alan's read of report v10; recording the demo video from `report/report.pdf`.
2. A push of `v8-corrections` (and `main`) on Alan's word: the commits since a7de233 are local only.

**Open questions for Alan**

- Push now, and tag a release once he has read the report?
- Docker Desktop's old `run` folder is at `%LOCALAPPDATA%\Docker\run_stale` (it holds the socket file Windows would
  not delete); it can go once Docker has been restarted cleanly.

## Session 25 — 2026-10-24: the clean Linux run on a second environment

**Done**

- Alan has no sudo password for WSL, so Python 3.11.9 and poppler 26.09 came from conda-forge through micromamba in
  his WSL home (`~/mamba/envs/qs`); a clone of the repository in the Linux file system (`~/qs_clean`), the rebuilt
  bundle, `make setup`, `make check-data` (111 of 111), `make all`.
- Notebooks 01 → 11 in 90 minutes; 12 stopped at the registration guard and ran in 172 s with decision #111's source.
  All 2,561 cited numbers identical to the container's, the same thirteen moved against this machine; 273 of 274 tests
  pass. Poppler 26.09 reads the PJM tables as 22.12 and 25.07 do. Recorded under decision #112.
- The first attempt overlapped the container's run on WSL's four cores and timed out in notebook 04's LightGBM
  cross-validation at the one-hour cell limit; rerun alone it passed. A grader on four cores should run nothing else
  alongside `make all`.

**Next**

1. Alan's read of report v10; recording the demo video from `report/report.pdf`.
2. The WSL environment (`~/mamba`, `~/.local/bin/micromamba`, `~/qs_clean`, `~/qs_out`) can be removed when no
   further run is wanted.

## Session 26 — 2026-10-24: report V2 from the executive review (decision #113)

**Done**

- `docs/v2_review.md`: the review and correction register — what stands, seven corrections ranked by materiality, the scenario assessment, the governance controls, what needed computation.
- Notebook 13 (`13_executive_corrections.ipynb`, `make corrections`, in the pipeline after 12): every process on the same funding bases (D $1.03B against C $0.82B and A $0.72B net of fee and interest; D over A +$312M [+$110M, +$506M]; with no line B leads at $0.87B), D re-solved with the line as a constraint (9 members, −$49M [−$127M, +$23M]), the dependence dial (D's tail −$0.03B → $0.82B as ω goes 0 → 1; comonotonic bound $2.19B), seven worlds (D best in 7 of 7), the optimizer-first arm on the registered v10 cases (the model's edge −$14M [−$36M, +$2M]; the rule +$56M over the checklist; registered rungs reproduced), book D's member table, the workflow and the control matrix (10 of 12 controls in place). Figures F51–F56; `results/v2/`; keys `v2_*` in `src/report_numbers.py`.
- `report/report.md` rewritten as V2: the decision brief, fourteen sections by the committee's questions, eleven figures and four tables in the body, the registered example X25 as the committee conversation; the v10 appendices kept with cross-references moved and F48, F50 as Figures A16–A17. Every number in the live table (the 5 report tests pass); the body about 10,000 words (`WORD_LIMIT = 11000`).
- The first notebook-13 run took 30 minutes (the ladder's funding loops); a second run with the figure layouts fixed (F51's labels, F53's arm labels, F55's long captions that squeezed the axes, F56's cell heights).

**Next**

1. `make report` on the rerun figures; look at every page; the poster is unchanged (it cites the v10 numbers, which stand); full `pytest`; commit and push on Alan's word.
2. Alan's read of V2; the demo video script's figure numbers may need moving to V2's.

## Session 26, continued — 2026-10-24: the executive summary

- Alan drafted an executive summary (problem, challenges, method, application, results, implications, readiness, conclusion) and asked for it to be reviewed and added. Reviewed against the numbers table: every figure in the draft matched; "Monte Carlo" became "joint scenario simulation from 2018–2024 market history with mean reversion" (what notebook 08 does), "predefined criteria" became "pre-registered", and the voice moved to the first person. Inserted as the report's first section, before the decision brief, on its own pages; `WORD_LIMIT = 12500` (body about 11,500 words); PDF 68 pages; 274 tests pass.

## Session 26, continued — 2026-10-24: the capstone's deliverables brought to V2 (decision #114)

**Done**

- Checked V2 against the proposal of 19 October and the grading checklist (`PLAN.md §10`): met on every item but three — the course's 3,000-word guidance, the promised emissions cap, and a poster still on v10's layout; the demo video is still to record.
- `src/report_course.py` and `make report-course`: the course-length edition (about 2,900 words: the executive summary, the brief, the conclusions, four figures, the statement of work), with two tests (under 3,000 words; every number in the table). 11 pages.
- Notebook 13 section 6: the emissions cap. Book D emits 1.27 Mt a year, all from its gas request; any cap swaps it for the 1,026 MW solar request with an agreement; the zero-emission book scores $1.15B static and $0.86B financed against $1.35B and $1.03B — $201M, $158 per tonne-year. Section 7 and Section 13 of the report; keys `v2_co2_*`.
- `report/poster.typ` redrawn: header band, one headline, four numbers, five executive figures, the recommendation; one A1 page; the poster number test passes.
- `app/executive.py` (`make executive`): the decision on one screen, six tabs, Altair charts from `results/` only, the registered case X25 as the committee conversation; every tab opened in the browser and looked at. `.claude/launch.json` entry `executive` (port 8503).
- README run instructions; Appendix C; 276 tests pass; report, course edition and poster rebuilt.

**Next**

1. Alan's read of V2, the course edition, the poster and the dashboard; push on his word.
2. The demo video: the script's figure numbers to V2's, then record from `report/report.pdf` and the executive dashboard.

## Session 27 — 2026-10-26: the poster's workflow figure made readable (decision #115)

**Done**

- Alan flagged the poster's "How a committee uses it" figure (F55) as unreadable: nine boxes in one row, 8-pt text overflowing the boxes, and the executive copy squeezed from 11 to 9 inches.
- Notebook 13 section 5 redraws F55 as a 3×3 grid of stages (name plus two short lines each) with the challenger's five levels in a column beside it; `F55_committee_workflow` added to `plots.EXECUTIVE_KEEP_WIDTH`. Notebook 13 executed top to bottom (12 min): only the four F55 files changed.
- Poster (`make poster`) and report (`make report`) rebuilt; the figure looked at in both, on the poster at 100 dpi and on report page 23 (Figure 9). The report's stage references still match. Notebook 12's kernel restored to `queue-survival` (an editor had switched it); 276 tests pass.

**Next**

1. Alan's read of the poster at print scale.
2. Unchanged from session 26: the demo video script's figure numbers to V2's, then record.

## Session 27, continued — 2026-10-26: F43 redrawn; both Word reports given the new figures (decision #116)

**Done**

- `Beyond_Prediction_Capstone_Report_Final.docx`: Figure 9 replaced by the new F55 (picture and its height only; everything else byte-identical); page 13 looked at in a Word export.
- F43 (the six-stage architecture) redrawn in notebook 11 the same way as F55: a 3×2 grid of stages, three short lines each, "What is measured" beside it. Notebook 11 executed top to bottom (18 min): only the four F43 files changed, F44 and every result identical.
- `CONFIDENTIAL_Petrobras_Executive_Briefing_Beyond_Prediction.docx`: Exhibit 1 replaced by the new F43 the same way; page 6 looked at in a Word export; the caption still matches.
- `make report report-course petrobras` rebuilt; F43 looked at in `Petrobras_Report.pdf` (page 4). The originals of both Word files are kept outside the repository.

**Next**

1. Alan's read of the two Word reports and the poster.
2. Unchanged: the demo video script's figure numbers to V2's, then record.

## Session 28 — 2026-10-27: the mentor's questions on the proposal answered

**Done**

- The course mentor's feedback on the proposal of 19 October (five questions: the C-criteria, scope and ranking, the data sources and cleaning, the predictive work since Milestone II, the boundary of what Claude does) drafted as a reply in `docs/mentor_reply_2026-10-27.md`, every number taken from the report and the results tables (28 of 70 registered lines, the C1–C24 groups, the lookup and level findings, the forward test, the ladder +$76M / +$43M / +$134M, the −$14M optimizer-first check, 35 memo numbers with one flagged). Two draft claims corrected against the record before it was left for Alan: what the thirteen non-matching numbers of the Linux run were (decision #112), and that the report does not mention the unbuilt stretch items. The paragraph on the writing is left for Alan to word. Item 12 in `docs/mentor_feedback.md`.

**Next**

1. Alan reads and sends the reply.
2. Appendix A of the report to gain a per-criterion table (what it measures, against what, the threshold, the verdict) for C1–C41, as promised in the reply.

## Session 29 — 2026-10-28: the Word edition made the official report (decision #117)

**Done**

- Seven tracked files found deleted in the working tree (`README.md`, `Makefile`, `.gitignore`, `.env.example`, `app/app.py`, both workflow files) restored from HEAD; a stale `.git/index.lock` from 26 October removed first. With `.gitignore` back, `.env`, `.venv/` and `data/raw/` are ignored again.
- Session 28 committed (`075d095`).
- `report/Beyond_Prediction_Capstone_Report_Final.docx` declared the official capstone report. Every number from its abstract to its references (451 distinct) is in `results/report_numbers.csv`; a test now checks it on every `pytest` run. README points to it.

**Next**

1. The Word report runs to about 10,300 words before the appendices against the course's suggested 3,000; the course-length edition (`report/report_course.pdf`) is the short version if the course asks for one — Alan to decide which is uploaded, or both.
2. A PDF export of the Word report for submission, from Word.
3. Unchanged: the demo video; the per-criterion table for Appendix A promised in the mentor reply now goes into the Word report.

## Session 29, continued — 2026-10-28: one dashboard (decision #118)

**Done**

- Reviewed the dashboard Alan opened (`app/app.py`): superseded numbers ($2.31B budget, twelve leases, a worst 5% "still a profit") against the official report, no starting point, the advisor's book differing from the one on screen, jargon labels, and clicks that write to `results/`. Four pages existed; only `app/executive.py` reads the report's numbers.
- `app/executive.py` made the only dashboard (`make app`, port 8501): a "What is being decided / How to read this page" opening, plain labels on the four headline numbers, the garbled pre-registered margin fixed (dollar signs escaped), and tab 7 "Your call" (tail weight × facility → the book already scored for that choice). Every tab looked at in the browser; tab 7 checked at λ = 1 with and without a facility and at λ = 4.
- `app/app.py`, `app/decide.py`, `app/challenge.py`, their three tests and three Makefile targets removed; `tests/test_app.py` rewritten for the dashboard (4 tests); README, `report/report.md` Appendix C run line, `src/advisor.py` and `src/whatif.py` docstrings updated. 275 tests pass; the one failure is notebook 12's kernel, switched again by an open editor.

**Next**

1. Close notebook 12 in the editor and set its kernel back to `queue-survival`.
2. `make report` to carry the Appendix C run line into `report.pdf` (the official Word report does not mention the dashboard).
3. The demo video can now be recorded from `make app`.

## Session 29, continued — 2026-10-28: the decision page (decision #119)

**Done**

- Alan: the dashboard must be simple — the options, the book, the advisor challenging the investor's thinking (which may or may not change their mind), then the investor's result against what the advisor's solution would have given. Built as `app/decide.py`, the first page of `app/app.py` (`make app`); `app/executive.py` is the second page and loses its own page config and CSS (the entry sets them).
- The four steps use the registered challenger (`src.challenge`) unchanged; the setting is pickled to `data/interim/` after a two-minute first build. The registered example X25 replays with no call: in the browser, the memo named the sunk cost, the unfunded construction calls and the five fragile members, 34 of 35 numbers checked, level *challenge*, the advisor's solution the book as it is; taking it in full scored $2.17B expected NPV, $0.82B worst-5% loss, 9% chance of a loss, $1.35B on the rules — the report's numbers. `results/advisor_runs.jsonl` unchanged at 537 lines.
- `tests/test_app.py`: three tests on the decision page (headless, recorded answers only) and three on the report page; README, Makefile, `.claude/launch.json`.

**Next**

1. Alan tries the page with his own book and reasons (a live call, with the key in `.env`), and says whether the four steps read right.
2. Close notebook 12 in the editor and set its kernel back to `queue-survival`; `make report` for the Appendix C run line.
3. The demo video, from `make app`.

## Session 29, continued — 2026-10-28: the worked example (decisions #120, #121)

**Done**

- `src/worked_example.py`: the lease-only executive of notebook 10's recorded round, brought to the $3.82B decision (thirteen leases, $3.79B, the technology cap broken), with the author's five answers; the decision is the repair; the first pick, the decision, the advisor's solution and the best book the rules allow are scored on the executive's rules. Notebook 13 section 7 runs it; `app/example.py` is the dashboard's third page; `we.labels` and `we.rules_text` serve both pages.
- No backend was available (`.env` holds no key; `claude -p` not signed in). Alan: keep it recorded with no key. The round is recorded with the tools alone (`worked_example.tools_only`, the registered *tools only* arm): the checklist guides to the repair (8 leases inside the cap), taken in full; $0.29B → $0.10B on the executive's rules, the best book the rules allow $1.35B, +$1.25B [+$1.11B, +$1.38B] over the decision. `results/v2/worked_example.json`.
- Alan: anyone using the dashboard needs an LLM key, said at the top, and any provider's. `advisor.ask_openai` (OpenAI-compatible; `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`); registered rounds replay under any model; `app/app.py` says it before any page; README and `.env.example`.
- Tests: `tests/test_worked_example.py`, the example page in `tests/test_app.py`, two backend tests in `tests/test_advisor.py`. Notebook 13 executed top to bottom (13 min): section 7's table matches its *Reading this*; only `checks.csv` (one new row, PASS) and `worked_example.json` changed; 282 tests pass, the one failure notebook 12's kernel.

**Next**

1. Unchanged: notebook 12's kernel; `make report`; the demo video.

## Session 29, continued — 2026-10-28: the repository as the capstone's submission (decision #122)

**Done**

- `README.md` rewritten as the front page: deliverables, the question, the decision and the answer in the report's numbers, the thirteen notebooks, `src/` grouped, the dashboard, tests, data, how to run, the map, the statement of work, references. `docs/README.md` indexes `docs/` (course submissions, the record, the reviews the report cites, plans kept as history). `docs/next_session_prompt.md` removed. 283 tests pass.
- `main` fast-forwarded to `v8-corrections`; both pushed to `origin` (github.com/alanmossinger/Capstone).

**Next**

1. `make report` to carry the Appendix C run line into `report.pdf`; the demo video from `make app`.
