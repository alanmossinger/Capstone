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
    extension, or keep them in Track B?
17. Value proxies for ERCOT and CAISO capacity value (PLAN.md §11 b):
    proposed with sources in notebook 15, confirmed by Alan before the
    table is fixed. Budget and caps: defaults accepted (decision #46).
18. PyMC Bayesian level model: wanted as a stretch (decision #46).
- Report title changed to "From Queue to Grid: AI-Driven Portfolio Management for the U.S. Power-Plant Pipeline" (decision #47); README, report and CLAUDE.md updated.
19. Figure footnotes read "Source: LBNL … ; author's analysis." Should they
    say "Figure: Alan Mössinger, from LBNL …" so authorship is explicit?
    One line in `src/config.py` changes every figure on the next run.
