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
