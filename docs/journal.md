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
