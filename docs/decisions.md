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
8. **Data readiness GO/NO-GO** — 2026-10-03: **NO-GO**, 13 of 15 checks
   pass (`docs/data_readiness.md`). Both failures are thresholds, not data
   defects: CAISO withdrawal-date coverage 82.6% vs ≥ 83%, and 2,292
   test-cohort projects vs ≥ 2,500 (304 completions vs ≥ 150). *(open — Alan
   decides whether to amend the two bars or change the test design; no
   modeling notebook until this reads GO)*
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
