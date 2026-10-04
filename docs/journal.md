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
