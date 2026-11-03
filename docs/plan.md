# Build plan (Oct 6 → Dec 14, 2026) · v3, portfolio management backed by data science

*Kept as history: the plan the notebooks were built from. Section numbers are the ones `src/` docstrings cite (§5–§14). The notebook numbers of §6 and §14 are the pre-consolidation ones; the map onto the final 01–13 is in §14's closing notes.*

Author: Alan Mössinger (sole). Course: SIADS 699, Group 13.

**v3 changes (2026-10-06).** Draft v1 of the report answered one question
well — how well entry-time attributes predict which requests get built, and
when — and left the portfolio questions open. The v3 goal is a **complete
portfolio-management report whose reader can decide which requests to back,
where, and how to build a book**, with every claim backed by the data
science behind it. The v1 pipeline (notebooks 01–09) and its registered
verdict stay as they are; v3 adds notebooks 11–18 and report v2. The word,
figure and page limits are off (decision #44). The LBNL 2025 file stays the
frozen basis of every registered result; the 2026 file is added alongside
for reconciliation and the 2020–2022 early-hazard check only (decision #43).

**v2 (2026-10-03)** made the project data-first: a readiness gate, numbered
notebooks, a small `src/` package, one command end-to-end. That is built.

Everything marked **must-have** is what report v2 needs; **stretch** starts
only after the must-haves of the same phase pass their checks.

---

## 1. The project in one paragraph (the report's opening)

The United States has more power-plant capacity waiting to connect to the
grid than it has in operation: at the end of 2024 about 10,300 projects were
in interconnection queues, almost twice the installed fleet, and most will
never be built. Of the capacity that requested interconnection in 2000–2019,
13% had reached commercial operation by end-2024 and 77% had been withdrawn;
the median wait from request to operation is above four years (Rand et al.,
2025). Developers, lenders and grid operators manage this pipeline with
cohort averages. I built project-level models that estimate, from what is
known on the day a request enters the queue and again at each later
milestone, the probability that it reaches operation within 3, 5 and 7
years, and I turned those estimates into the tools a portfolio manager
needs: a scorecard with reasons and what-ifs for each request, a simulated
book with correlated risk, a budget-constrained choice of requests per
region, a map of where the queue and the built fleet sit, and a backtest of
those choices on requests that entered in 2017–2019. Every number comes with
an interval, and every claim about the portfolio is tested against a
pre-registered criterion.

| Course question | Answer |
|---|---|
| Who decides, on what? | A developer or IPP portfolio manager choosing which requests get deposits, studies and engineering effort, and in which regions; a lender pricing timing risk at each milestone; an ISO or regulator asking which attributes go with attrition. |
| What changes because of the output? | Which requests are kept, dropped or accelerated; how a book is spread across regions and technologies; what COD assumptions go into a financial model; which levers (size, siting, timing, service type) are worth pulling. |
| How wrong can it be and still help? | Ranking and the level both matter now: a book's expected MW online scales with the level. ±1 year on a single request is tolerable; a 40% overstatement of the level is not, which is why v3 repairs it first. |
| Features known at decision time | At entry: region, state, technology, MW and hybrid composition, service type, request year, congestion at entry, FERC size regime. At a later landmark: the same plus phase reached, months in phase, interconnection-agreement status, dated before the landmark. **Never** anything dated after the decision point. |
| Baseline to beat | Two: the v1 region × technology Aalen–Johansen average, and a **fair** region × technology × size-band average (§8). Whatever survives the second is what machine learning adds beyond a lookup table. |

---

## 2. Calendar

| Week | Dates (2026) | Work | Course event |
|---|---|---|---|
| 1 | Oct 6–11 | This plan; **F9 map** (nb 03b); **nb 11** fair baseline + utility-scale cohort, v2 criteria registered | |
| 2 | Oct 12–18 | **nb 12** level repair and 2020–2022 early-hazard check; **nb 01b** LBNL 2026 reconciliation (file from Alan) | Prior-work resubmission Oct 12 |
| 3 | Oct 19–25 | **nb 13** ISO-native queue files (PJM, CAISO, ERCOT) → milestone dates; join to LBNL | **Proposal due Oct 19** — portfolio framing, F9 and nb 11 go in |
| 4 | Oct 26–Nov 1 | **nb 14** landmark (stage-updated) model | |
| 5 | Nov 2–8 | **nb 15** value and cost layer | |
| 6 | Nov 9–15 | **nb 16** portfolio layer: scorecards, what-ifs, Monte Carlo book, budget-constrained choice, backtest | **Midway check-in opens Nov 10** |
| 7 | Nov 16–22 | **nb 17** constraints, levers and region playbooks; **nb 18** v2 evaluation; report v2 complete | Mentor feedback |
| 8 | Nov 23–29 | **nb 19** MISO and SPP timing models on the 2026 file (registered extension, decision #49); revise on feedback; poster | Check-in closes Nov 30 |
| 9 | Nov 30–Dec 6 | README, tests, `make all` from a fresh clone, final figures, gallery post | |
| 10 | Dec 7–13 | Final report v2, poster, tag `v1.0` | **Project due Dec 14** |

Slack: weeks 8–9 absorb overruns from weeks 3–6. If nb 13 (ISO files) slips,
nb 14 runs on the LBNL `ia_date` landmark alone (§6, nb 14 fallback) and the
ISO files move to stretch.

---

## 3. Repository layout (additions to the built v2 layout)

```
queue-survival/
├── notebooks/
│   ├── 01_get_data … 09_explain_and_rank      v1 pipeline (built; unchanged)
│   ├── 08b_posthoc_improvements               built; post-hoc, labelled
│   ├── 01b_lbnl_2026_reconcile.ipynb          2025 vs 2026 file: same requests, changed status/dates; 2020–2022 early hazards
│   ├── 03b_project_map.ipynb                  F9: queue requests and the built fleet on a U.S. map, by region
│   ├── 11_fair_baseline_and_scale.ipynb       region × technology × size baseline; ≥ 20 MW primary cohort; v2 criteria written first
│   ├── 12_level_repair.ipynb                  cohort drift; recalibration by region and horizon; drift-aware models
│   ├── 13_iso_queue_files.ipynb               gridstatus / ISO files → milestone dates, withdrawal comments, POI; join to LBNL
│   ├── 14_landmark_models.ipynb               P(online within h of landmark L) for L ∈ {entry, +12 mo, +24 mo, IA executed}
│   ├── 15_value_and_cost.ipynb                value per MW-year by region/technology/COD year; interconnection cost per kW; expected value per request
│   ├── 16_portfolio.ipynb                     scorecards + reason codes; what-ifs; correlated Monte Carlo book; budget-constrained choice; backtest
│   ├── 17_constraints_and_levers.ipynb        constraint map (congestion, siting, equipment, regime); levers by actor; region playbooks
│   ├── 18_evaluate_v2.ipynb                   v2 criteria scored; decision-focused backtest; what passed, what failed
│   └── 19_miso_spp_timing.ipynb               MISO and SPP timing models on the 2026 file; criteria C13–C14 written first
├── src/
│   ├── baselines.py          fair baseline (region × technology × size band, shrinkage to parent cells)
│   ├── drift.py              cohort-level recalibration; trend terms; drift diagnostics
│   ├── iso_queues.py         pulls and snapshot-diffs of ISO queue files; join keys to LBNL
│   ├── landmark.py           landmark datasets and models
│   ├── value.py              value and cost proxies; expected value per request; sensitivity grid
│   ├── portfolio.py          scorecards, what-ifs, Gaussian-copula book simulation, budget-constrained choice, backtest
│   ├── geo.py                county centroids, state outlines, region polygons for F9 and the playbook maps
│   └── (existing modules unchanged)
├── data/raw/
│   ├── lbnl/                 2025 file (frozen) + lbnl_ix_queue_data_file_thru2025*.xlsx (2026 edition, alongside)
│   ├── iso/                  PJM / CAISO / ERCOT queue files as downloaded, dated snapshots
│   ├── lbnl_costs/           LBNL interconnection cost workbooks
│   ├── value/                PJM BRA results, EIA capacity factors, tax-credit rule table (hand-typed with source)
│   ├── siting/               NREL/NLR wind and solar ordinance databases (stretch)
│   └── geo/                  Census county gazetteer and cartographic state boundaries
├── results/                  v2 tables: success_criteria_v2.csv, fair_baseline_*.csv, drift_*.csv, landmark_*.csv, value_*.csv, portfolio_*.csv, backtest_*.csv
├── figures/                  F9–F16 (§9)
└── report/
    ├── report.md             report v2 (no word limit); v1 kept in git history
    ├── appendix.md           criteria v1 and v2, features, hyperparameters, value assumptions, reproduction
    └── references.md
```

---

## 4. Environment

- Python 3.11 venv; `requirements.txt` pinned, only what is imported.
- New dependencies, each with a line in `docs/decisions.md`:
  `geopandas` (+ `shapely`, `pyproj`, `pyogrio`) for F9 and the playbook
  maps; `gridstatus` for the ISO queue files (nb 13); `rapidfuzz` for the
  ISO ↔ LBNL join; `scipy` is already present (via scikit-learn) and its
  `milp` solves the budget-constrained choice; **stretch:** `pymc` for the
  Bayesian cohort intercept (nb 12 option c).
- `make all` runs 01 → 09, then 01b, 03b, 11 → 18, stopping at the first
  error. Target under 45 minutes from the raw files on a laptop; every
  download is cached and checksummed.

---

## 5. Phase 0b — the v3 data gate (must-have for nb 13, 15; stretch for 17)

Goal: every new source on disk under `data/raw/`, verified, documented in
`data/README.md`, with a PASS/FAIL line in `docs/data_readiness.md` (a new
dated section, "v3 sources") before the notebook that needs it is written.

### 5.1 Sources

| # | Source | What it gives | Access | License / terms | Needed by |
|---|---|---|---|---|---|
| S6 | **LBNL Queued Up 2026 data file** (data through 2025) | One more year of outcomes: 2020–2022 entrants' 1- and 2-year hazards; 2018 entrants reach 7 years; status/date changes between editions | Manual download by Alan (site returns 403 to scripts); SHA-256 pinned beside the 2025 hash. **If the edition is not yet published, nb 01b waits and the report says so** | Same DOE terms as the 2025 file; not committed | nb 01b, nb 12 |
| S7 | **ISO-native queue files**: PJM Cycle / serial queue status, CAISO interconnection queue report, ERCOT GIS monthly reports (2019 →) | Milestone dates (study phases, IA, suspension), withdrawal comments, POI, developer | `gridstatus` `get_interconnection_queue()` for the current snapshot; ERCOT monthly GIS archive for history; snapshot diffs give dated transitions | Public ISO data; each ISO's terms cited; raw files not committed | nb 13, nb 14 |
| S8 | **LBNL interconnection cost data** (MISO, PJM, SPP, NYISO, ISO-NE and others; project-level estimates by study phase) | Network-upgrade and POI cost per kW — the documented withdrawal driver — and the sunk-cost side of the value layer | Excel attached to each LBNL cost brief; manual download | LBNL publication terms; derived tables only | nb 15 |
| S9 | **Value proxies**: PJM Base Residual Auction clearing prices by delivery year; EIA capacity factors by technology and state (EIA-860M/923 via the API already in use); ERCOT and CAISO price proxies | Value per MW online by region, technology and COD year | PDF reports (hand-typed table with page citation) and the EIA API | Public | nb 15 |
| S10 | **Tax-credit timing rule table** (begin-construction and placed-in-service deadlines for wind and solar; ITC/PTC eligibility by COD year) | A value cliff by COD year | Static rule table typed from the IRS notice and cited | Public | nb 15 |
| S11 | **Census county gazetteer** (county centroids by FIPS) and **cartographic boundary files** (states, 20m) | Positions for the 91% of requests with a FIPS code; state outlines for F9 | Census Bureau bulk files, scripted download with checksum | Public domain | nb 03b, nb 17 |
| S12 | *(stretch)* **NREL/NLR siting ordinance databases** (wind, solar; county-level bans, moratoria, setbacks) | Siting-risk feature; constraint map | OpenEI xlsx + GeoPackage; match county + state | Public; machine-collected, validated on a sample | nb 17 |
| S13 | *(scenario only)* Gas-turbine vendor backlog and delivery years | COD-slippage scenario for gas requests; **not** a feature | Earnings releases, cited | Public | nb 17 |

### 5.2 Readiness checks (added to `docs/data_readiness.md`)

| Check | Pass condition |
|---|---|
| S6 loads and is the stated edition | sheet and columns match the 2025 layout, or every difference listed; rows ≥ 36,441; SHA-256 recorded |
| S6 reconciles with S1 | ≥ 95% of 2025 requests found in 2026 by (`q_id`, `entity`, region); status transitions tabulated; requests whose event *dates* changed listed with counts (the ERCOT 2018-08-29 block checked) |
| S7 coverage | for each ISO: snapshot rows, share with a queue ID that matches LBNL `q_id` (target ≥ 70% of 2017–2019 LBNL requests), share with at least one dated milestone |
| S8 coverage | projects with a cost estimate joined to LBNL by queue ID: counts by region; PJM ≥ 500 |
| S9/S10 complete | one value row per (region, technology, COD year) used by nb 15; every cell carries a source and a sensitivity range |
| S11 complete | every FIPS in the queue file resolves to a centroid; unmatched counts listed by region |
| Secrets safe | unchanged: `.env` only |

---

## 6. Notebooks 01b, 03b and 11–18 (tasks → outputs → acceptance checks)

The v1 notebooks are not rewritten. Where v3 changes a v1 figure or table,
the new notebook writes a new file and the report cites the new one.

### Notebook 03b — `03b_project_map` (must-have, week 1) — **F9**
Queue requests (every region, status at end-2024) and the operating fleet
(EIA-860M, exact coordinates) on one U.S. map: small multiples by region or
one panel with region colours, marker size by MW, operational / withdrawn /
active distinguished; a second panel with the share built by state. County
centroids from S11 for LBNL requests (91% have a FIPS; the rest counted and
shown as a note). The *Reading this* cell says what the geography means for
a book: where the three timing ISOs sit, where the queue is densest, where
the built fleet is.
Outputs: `figures/F9_project_map.*`, `results/map_counts_by_state.csv`,
`results/map_unmatched.csv`. Checks: every state's count on the map equals
the clean file's count; unmatched FIPS ≤ 10%; figure meets the figure standard of `src/plots.py`.

### Notebook 11 — `11_fair_baseline_and_scale` (must-have, week 1)
**First cell writes `results/success_criteria_v2.csv` before any test
metric is computed** (§8, decision #42). Then:
1. **Fair baseline** (`src/baselines.py`): Aalen–Johansen incidence of
   operation at 3/5/7 years per region × technology × size band (six bands,
   §7 of v2); cells under 50 training requests shrink to region ×
   technology, then to region. Written for every test request beside the
   v1 baseline.
2. **Utility-scale primary cohort**: test requests ≥ 20 MW (1,839 of 2,268
   by count, 98.9% of test MW) become the primary cohort; < 20 MW is the
   secondary track with its own lines.
3. **Three size-aware variants**, chosen on 2016 entrants as in v1:
   (a) LightGBM with a monotone-decreasing constraint on `log_mw`;
   (b) separate models per size regime (< 20, ≥ 20 MW);
   (c) size-band interactions in the discrete-time logit.
4. **Congestion artifact removed** (v1 issue, decision #26): the variants
   are fitted on congestion *at entry* only, so the fitted effect matches
   what is available at prediction time; the yearly value returns in nb 14
   as a landmark feature dated before L. The v1 artifact figure stays in the
   report as the diagnosis.
5. Every v1 metric rerun for v1 LightGBM, the chosen variant, and both
   baselines, on both cohorts.
Outputs: `results/fair_baseline_cells.csv`, `results/metrics_v2.csv`,
`results/metrics_v2_by_size.csv`, `results/variant_choice_2016.csv`,
`data/processed/predictions_v2.parquet`. Figure **F10** (gains over both
baselines by cohort and horizon). Checks: the fair baseline reproduces the
v1 baseline when size bands are collapsed; the variant choice is made on
2016 only (asserted in a test); the criteria file predates the metrics file
(timestamp test).

### Notebook 12 — `12_level_repair` (must-have, week 2)
The 2018–2019 shortfall (observed 5-year completion 8.3% and 9.6% against
predicted 13.1% and 13.6%) is a cohort effect trees cannot extrapolate.
1. **Diagnose**: observed vs predicted by entry year, region and size, with
   intervals; the 2020–2022 entrants' 1- and 2-year hazards from the 2025
   file (and the 2026 file once nb 01b runs) against the model's.
2. **Repair, cheapest first** (`src/drift.py`): (a) "years since 2010" in
   the logit so a linear trend extrapolates; (b) two-stage: LightGBM for
   ranking, then cohort-level logistic recalibration by region and horizon
   fitted on the newest *training-side* cohort available at prediction
   time (2016 for the 2017 test year, rolling forward for 2018 and 2019 —
   no test outcomes used to recalibrate the same year); (c) **stretch**:
   a Bayesian discrete-time hazard with a random walk on the cohort
   intercept (PyMC), giving an interval on the level itself.
3. Report calibration **slope and intercept** on 2018–2019 for every
   option; choose on 2016 and the rolling rule, not on the test cohort.
Outputs: `results/drift_by_cohort.csv`, `results/recalibration.csv`,
`results/early_hazards_2020_2022.csv`, predictions added to
`predictions_v2.parquet`. Figure **F11** (level by entry year, observed vs
each model, with the 2020–2022 early hazards). Checks: no test-year outcome
enters its own recalibration (test); intercept reported with interval for
every option.

### Notebook 01b — `01b_lbnl_2026_reconcile` (must-have once S6 exists, week 2)
Load the 2026 file beside the frozen 2025 file; match requests; tabulate
status transitions 2024 → 2025; list requests whose recorded *dates*
changed between editions (the "snapshot of snapshots" problem); compute the
2020–2022 entrants' 1- and 2-year incidence from the 2026 file for nb 12.
The 2026 file is **not** used to fit or score any registered model
(decision #43). Outputs: `results/lbnl_2026_reconciliation.csv`,
`results/lbnl_2026_date_changes.csv`. Checks: §5.2 S6 lines pass; the
2025 hash is unchanged.

### Notebook 13 — `13_iso_queue_files` (must-have for the landmark model, week 3)
Pull the current PJM, CAISO and ERCOT queue snapshots through `gridstatus`
and the ERCOT GIS monthly archive (2019 →); normalise columns; **snapshot
diffs** give the month a request changed phase or status; join to LBNL by
queue ID (exact), then by (region, MW ± 15%, county, name tokens via
`rapidfuzz`) for the rest; report match and agreement rates honestly, as
notebook 01's linkage test did. Extract per request: dated study phases,
IA executed date, suspension dates, withdrawal comment where present,
POI name.
Outputs: `data/interim/milestones.parquet`, `results/iso_join_rates.csv`,
`results/milestone_coverage.csv`. Checks: §5.2 S7 lines; a milestone date
is never earlier than the request date; LBNL `ia_date` agrees with the
ISO IA date within 3 months for ≥ 80% of joined requests.

### Notebook 14 — `14_landmark_models` (must-have, week 4)
Landmarks L ∈ {entry, +12 months, +24 months, IA executed}. At each L,
the risk set is every request still active at L; features are the entry
features plus phase reached, months in current phase, cluster or cycle,
congestion at L, interconnection cost estimate if available (nb 15), all
dated before L; outcome is P(online within h of L) for h = 1, 2, 3 years,
with withdrawal as the competing event. Same discrete-time machinery as
nb 06 (`src/landmark.py` builds the datasets), same temporal split, same
IPCW evaluation per landmark. This turns the v1 leakage ablation (0.715 →
0.990 AUC with post-entry columns) into legitimate, time-stamped signal.
**Fallback if nb 13 slips:** the LBNL file's own `ia_date` and
`IA_status_clean` define the "IA executed" landmark; the +12/+24-month
landmarks use entry features and congestion at L only.
Outputs: `data/processed/predictions_landmark.parquet`,
`results/landmark_metrics.csv`, `results/landmark_coverage.csv`. Figure
**F12** (AUC and calibration by landmark and horizon). Checks: a feature
test asserts every landmark feature is dated before L; metrics carry
intervals; the entry landmark reproduces nb 11's numbers.

### Notebook 15 — `15_value_and_cost` (must-have, week 5)
A published, explicit value proxy per request, stated as an assumption and
run through a sensitivity grid (`src/value.py`):
- **Value per MW-year** by region × technology × COD year = capacity value
  (PJM BRA clearing price for PJM; stated proxies for ERCOT and CAISO) +
  energy value (EIA capacity factor × a regional price proxy) + tax-credit
  eligibility by COD year (S10). Each term with its source and a low /
  base / high setting.
- **Sunk cost** = deposits and study costs by phase (ISO tariffs, cited) +
  interconnection cost per kW from S8 where a project-level estimate
  exists, otherwise the region × size-band median with a flag.
- **Expected value of a request at landmark L** = Σ_h P(online in year h |
  L) × MW × value(h) − sunk cost to the next decision point; also expected
  MW online by year.
Outputs: `results/value_table.csv`, `results/cost_table.csv`,
`results/expected_value_by_request.csv`, `results/value_sensitivity.csv`.
Figure **F13** (expected MW online and value by region under low / base /
high). Checks: every cell of the value table has a source; the sensitivity
grid changes the book ranking in a way the notebook states; no value number
is typed into the report by hand.

### Notebook 16 — `16_portfolio` (must-have, week 6) — the core of report v2
`src/portfolio.py`:
1. **Scorecards**: for each request in a book, P(online by 3/5/7) at the
   current landmark with intervals, the fair-baseline comparison, the top
   reason codes (SHAP, in words), and expected value.
2. **What-ifs** per request: the counterfactual P(online) if MW were cut
   below 20 MW or to the next band, technology swapped (solar ↔ solar +
   storage), service type changed, or entry delayed to a less congested
   month — only changes a developer can actually make, each with its value
   effect.
3. **Monte Carlo book**: outcomes drawn with a Gaussian copula whose
   region × cohort factor loading is estimated from the dispersion of
   observed vs predicted completion across training cohorts; 5,000 draws;
   expected MW online by year with 5–95% bands; probability the book
   misses a target.
4. **Budget-constrained choice** per region: choose requests to maximise
   expected value minus λ × downside (CVaR at 10%) subject to a deposit
   budget and per-region and per-technology caps; solved with `scipy.
   optimize.milp`; λ swept.
5. **Backtest** on 2017–2019 entrants: books chosen by the v2 model, by the
   fair baseline, by the v1 baseline and at random, with the same budget;
   realised MW online by end-2024 and realised value; paired bootstrap
   differences — the decision-focused criteria C9–C11 (§8).
Outputs: `results/scorecards.csv`, `results/whatifs.csv`,
`results/book_simulation.csv`, `results/book_choice_by_region.csv`,
`results/backtest_books.csv`. Figures **F14** (simulated book: expected MW
online by year with bands) and **F15** (backtest: realised MW online by
chooser, with intervals). Checks: simulated marginal probabilities equal
the model's (test); the optimiser respects every cap (test); the backtest
never uses outcome information to choose a book.

### Notebook 17 — `17_constraints_and_levers` (must-have core, stretch extras, week 7)
What the data can and cannot see about *why* projects stall, and what each
actor can do:
- **Congestion** at entry and at each landmark (already modelled), shown as
  a constraint map by region and year.
- **Regime**: every request predates Order No. 2023; cluster and cycle
  processes, PJM's reformed cycle and the MISO/SPP expedited lanes are
  handled as named scenarios on the hazards (multipliers with stated
  ranges), not as fitted effects.
- **Equipment** (gas turbine backlog, S13) as a COD-slippage scenario.
- **Siting** (S12, stretch): county ordinance flags joined by FIPS; tested
  as a feature on the ≥ 20 MW cohort; reported either way.
- **Levers by actor**: developer (size, hybridisation, service type, entry
  timing, region mix), ISO (what the attrition pattern says about process),
  policy (what the regime scenarios imply); each lever tied to a number
  from nb 09, 14 or 16 or marked as outside the data.
- **Region playbooks** (ERCOT, PJM, CAISO): one page each — base rates,
  level drift, what the model adds, attrition multipliers, recommended book
  shape under the base value case, and the main uncertainty.
Outputs: `results/constraint_map.csv`, `results/levers.csv`,
`results/playbooks.csv`, `results/scenarios.csv`. Figure **F16** (constraint
map by region). Checks: every lever row cites a results file or says "not
in the data".

### Notebook 18 — `18_evaluate_v2` (must-have, week 7)
Scores `results/success_criteria_v2.csv` (written in nb 11 before any of
this existed) and writes `results/success_criteria_v2_scored.csv`; reports
the v1 verdict beside it; lists what passed and failed and what that means
for the portfolio claims; reruns the leakage guard on the landmark model;
adds the Track B calibration plot v1 lacked and the Appendix A slopes with
intervals beside the bounds.
**Not added, and said so in one line of the report:** random survival
forests and deep survival nets (DeepSurv, DeepHit) — 13,000 requests with
ten features do not reward them over LightGBM; a text model on project
names — names are inconsistent across editions.

### Notebook 19 — `19_miso_spp_timing` (must-have, week 8; decision #49)
The 2026 file dates 97% / 94% of MISO's operations / withdrawals and 96% /
73% of SPP's, where the 2025 file had almost none. **First cell writes
criteria C13–C14 to `results/success_criteria_v3.csv`** before any test
metric. Then, on the 2026 file only (censor 2025-12-31): rules R1–R9 via
`config.LBNL_2026_RENAMES`; events and entry features as in notebook 04;
the fair baseline, the discrete-time logit and LightGBM as in notebooks 06
and 11, tuned on 2016 entrants, fitted on entrants to 2016 and tested on
2017–2019 entrants of MISO and SPP; the same IPCW metrics with intervals;
calibration by entry year. ERCOT is **not** refitted on the 2026 file
(its withdrawal dates are 49% complete there). Reported beside the
three-ISO results, never pooled with them.
Outputs: `data/processed/predictions_miso_spp.parquet`,
`results/miso_spp_metrics.csv`, `results/miso_spp_date_coverage.csv`,
`results/success_criteria_v3_scored.csv`. Figure **F17** (AUC, Brier and
calibration for MISO and SPP by horizon). Checks: the criteria file
predates the metrics file; every metric carries an interval; the 2025
pipeline's files are untouched (hash test on `predictions_trackA.parquet`).
Checks: the scored file has one row per registered line; failures are
reported, not removed; the v1 registered verdict is untouched.

---

## 7. Data specification (additions; the v2 specification stays valid)

- **Cohorts, counts** (from the clean file): Track A 13,366 requests;
  test cohort 2017–2019 2,268 (≥ 20 MW: 1,839); entrants from 2020 on,
  unused by v1: 6,122 in the three ISOs, 15,715 across all nine regions.
- **Locations**: `county`, `state` present for 100% / 99.8%; `fips_codes`
  for 91% (ERCOT 79%, MISO 65%, others ≥ 88%); no coordinates in the LBNL
  file; EIA-860M has coordinates for 100% of 28,324 operable generators.
- **Landmark dataset**: one row per (request, landmark) for requests
  active at L; `months_since_entry`, `phase_at_L`, `months_in_phase`,
  `ia_executed_before_L`, `congestion_at_L`, `cost_estimate_at_L`
  (missing flag); outcome within h of L; censoring at 2024-12-31.
- **Value table**: (region, technology, COD year) → capacity value,
  energy value, credit value, each with low / base / high and a source
  column; **cost table**: (region, size band, phase) → deposit, study
  cost, upgrade cost per kW, source.
- **Book simulation**: latent z_i = √ρ_r · F_{r,c} + √(1−ρ_r) · ε_i,
  built if Φ(z_i) < P_i; ρ_r per region from the training-cohort
  dispersion; documented in `src/portfolio.py` with its derivation.

---

## 8. Models and evaluation at a glance (v3)

| Layer | Must / stretch | What | Notebook |
|---|---|---|---|
| 0 | must | v1 baseline (region × technology AJ) and **fair baseline** (× size band, shrunk) | 05, 11 |
| 1–5 | built | KM/AJ; cause-specific Cox; discrete-time logit and LightGBM; Track B; SHAP | 03–09 |
| 6 | must | Size-aware variants (monotone MW; per-regime; interactions) | 11 |
| 7 | must | Level repair: trend term; two-stage cohort recalibration | 12 |
| 7s | stretch | Bayesian cohort intercept (PyMC) | 12 |
| 8 | must | Landmark models at entry, +12, +24 months, IA executed | 14 |
| 9 | must | Value and cost layer with sensitivity | 15 |
| 10 | must | Scorecards, what-ifs, Gaussian-copula book, `milp` choice, backtest | 16 |
| 11 | must | Scenarios (regime, equipment); levers; playbooks | 17 |
| 11s | stretch | Siting-ordinance feature; transport to MISO/SPP/West as a ranking model with Track B levels | 17 |

**Pre-registered v2 criteria** (written by nb 11's first cell to
`results/success_criteria_v2.csv`; 95% paired bootstrap intervals; scored
in nb 18; the v1 criteria C1–C5 stay as registered):

| Id | Line | Pass rule |
|---|---|---|
| C6 | ≥ 20 MW cohort: chosen v2 model vs **fair** baseline, Uno's C and Brier at 3 and 5 years | interval of the paired difference entirely on the better side |
| C7 | ≥ 20 MW cohort: calibration slope **and** intercept at 3 and 5 years after level repair, 2018–2019 entrants | slope interval within 0.8–1.2 and intercept interval covering 0 |
| C8 | Landmark model at +24 months and at IA executed: Uno's C vs the entry model on the same risk set, 3-year horizon | paired difference entirely on the better side |
| C9 | Backtest: realised MW online by end-2024 of the model-chosen book vs the fair-baseline book, same budget, 2017–2019 entrants | paired difference entirely on the better side |
| C10 | Backtest: realised value of the model-chosen book vs the fair-baseline book under the base value case | paired difference on the better side; reported under low and high too |
| C11 | Simulated book: the 5–95% band of expected MW online by 2024 for the 2017–2019 book covers the realised value | covered |
| C13 | MISO and SPP (2026 file, 2017–2019 entrants): LightGBM vs the fair baseline, Uno's C and Brier at 3 and 5 years, per region | paired difference entirely on the better side |
| C14 | MISO and SPP: calibration slope at 3 and 5 years | interval within 0.8–1.2 |
| C12 | Leakage guard: no landmark feature dated after its landmark (test) and the landmark model's AUC does not exceed the leakage-ablation AUC | both hold |

Failures are reported, not removed; the report's portfolio claims are
limited to the lines that pass.

---

## 9. Figure plan (v1 figures F1–F8 stay; no cap on the count)

| # | Figure | Notebook | Takeaway |
|---|---|---|---|
| F9 | U.S. map: queue requests by county centroid (colour = region, size = MW, status) and the operating fleet; built share by state | 03b | Where the queue and the fleet are; the three timing ISOs in context |
| F10 | Gains over the v1 and the fair baseline, ≥ 20 MW and < 20 MW cohorts, by horizon, intervals | 11 | What machine learning adds beyond a size lookup |
| F11 | Level by entry year: observed vs each model, with 2020–2022 early hazards | 12 | The drift and whether the repair holds |
| F12 | Landmark models: AUC and calibration by landmark and horizon | 14 | How much a later decision point knows |
| F13 | Expected MW online and value by region under low / base / high value cases | 15 | The size of the value assumption |
| F14 | Simulated book: expected MW online by year with 5–95% bands; probability of missing a target | 16 | What a book delivers, and how wrong it can go |
| F15 | Backtest: realised MW online and value by chooser (model, fair baseline, v1 baseline, random) | 16 | Whether the model's choices were better, in hindsight |
| F16 | Constraint map by region: congestion, regime scenarios, siting (if S12), equipment | 17 | Where the levers are |
| F17 | MISO and SPP timing models on the 2026 file: AUC, Brier, calibration by horizon | 19 | Whether the approach carries to two more regions |
| playbook maps | Per-region map insets for the playbooks (from `src/geo.py`) | 17 | Region context |

---

## 10. Report v2 skeleton (no word limit) mapped to the six questions and the grading checklist

| Section | Answers | Checklist item |
|---|---|---|
| Abstract | — | — |
| 1 The decision: who manages a queue portfolio, on what, with what today; opens for a reader who does not know what an interconnection queue is | — | Project statement |
| 2 Data: the LBNL file (2025 frozen; 2026 alongside), EIA-860M, ISO files, cost and value sources, cleaning, access; **F9 map** | — | Data access; Context |
| 3 How well can data science predict survival and timing? (v1 results, fair baseline, utility scale, level repair) F10, F11 | Q1 | Methodology; Evaluation |
| 4 Each request's probability, and why: scorecards at entry and at later landmarks; reason codes F12 | Q2 | Explainability; Translation |
| 5 What should a request have different? What-ifs and the constraint map F16 | Q3 | Translation |
| 6 Reducing the constraints: levers by actor; scenarios | Q4 | Broader impacts |
| 7 The right book per region: value layer, simulated book, budget-constrained choice, backtest, region playbooks F13–F15 | Q5 | Evaluation; Translation |
| 8 What an energy company should do: decision rules, stage gates, a monitoring loop, what not to do | Q6 | Translation |
| 9 Evaluation record: v1 and v2 criteria as registered, what passed, what failed, post-hoc labelled | — | Evaluation strategy |
| 10 Ethics and broader impacts | — | ≥ 1 ethical question |
| 11 Limitations and next steps | — | Technical writing |
| 12 Conclusion | all six | — |
| Statement of work; changes after mentor feedback; references; appendices (criteria tables, features, hyperparameters, value and cost assumptions with sources, reproduction) | — | Statement of work; Feedback |

Technical-depth mapping for the rubric: survival and competing risks;
gradient boosting with monotone constraints and SHAP; landmark models;
recalibration and non-stationarity; Monte Carlo with a copula; integer
optimisation; decision-focused backtesting; (stretch) Bayesian hierarchy.

---

## 11. Decisions (v3 additions; see `docs/decisions.md`)

42. v3 scope: portfolio-management report backed by data science; six
    questions; notebooks 11–18; v1 verdict untouched.
43. LBNL 2026 file added alongside the frozen 2025 file, for
    reconciliation and the 2020–2022 early-hazard check only.
44. Word, figure and page limits off for report v2.
45. `geopandas` (and its stack) added for F9 and the playbook maps.
46. Portfolio defaults; PyMC stretch wanted. 47. Report title. 48. The 2026
    file on disk; MISO/SPP dates; ERCOT caveat. 49. MISO and SPP timing
    models as a registered v3 extension (notebook 19).
Further decisions are numbered as they are made.

**Open items:** (a) the 2026 LBNL file — download and place it when
published; (b) value proxies: confirm the base case for ERCOT and CAISO
capacity value before nb 15 fixes it; (c) budget and caps for the book
choice (default: a deposit budget equal to the median 2019 book of 25
requests, caps of 50% per region and 60% per technology); (d) whether the
PyMC stretch is wanted.

---

## 13. v4 — From Queue to Capital, at capstone scale (added 2026-10-12, decision #59)

Alan's direction (2026-10-11/12): the reader is an energy company that owns a
book of interconnection-queue requests and must decide — invest, accelerate,
hold, acquire or exit; where, when, how much, which project. The report is one
data-science narrative built from what the 22 notebooks already produce. No
new notebooks: an addition goes into the notebook that owns the topic, as a
numbered section with a why-cell, a Reading-this cell and updated Takeaways.
Every section lands on a decision. No appendix; word limit off (decision #44).

### 13.1 Six engines, one decision

| Engine (question) | Already built | Added (where) |
|---|---|---|
| 01 Market intelligence: where, which technologies | F1–F3, F8, F9, F16, playbooks | 03b §5 state archetypes (PCA + k-means on state features that exist; validated on 2017–2019 outcomes); F25 |
| 02 Development forecasting: will it operate, and when | Cox, discrete-time logit and LightGBM, fair lookup, drift repair, landmark at +2 y, MISO/SPP | 08b §8 tournament (random survival forest pair, MLP discrete-time hazard, blend; protocol and C18–C19 committed before scoring; F22); 08 §11 timing error among the built; 03 §13 six drivers (F19) and §14 where and when requests die (F20); 09 §4b ten entry rules (F21) |
| 03 Asset economics: what is a project worth | value per MW-year, cost table, value index | 15 §8 project NPV per MW by region × technology × COD year from the value table and NREL ATB costs (one new public file, `data/raw/atb/`); F26; the index leaves the decision layer |
| 04 Risk intelligence: what fails together | book simulation, ρ = 0.041, scenarios | 16 §4b expected shortfall of book NPV with the cohort level as a common factor; the scenario multipliers as stresses |
| 05 Spatial: where and how much | F9, map tables | covered at state level by 01; county and node siting out of scope |
| 06 Portfolio optimisation: what to fund | budget choice, backtest, count book, managed book C15–C17 | 16 §9 stage gates G1 (entry) and G2 (+2 y) with `V_gate = −cost_to_next_gate + P × NPV`, four policies compared on 2017–2019 under one budget (equal regional split, NPV per dollar, ML without risk constraint, risk-adjusted E[NPV] − λ·CVaR95 with caps); F23; 20 §10 the book per region with a probability floor (F24); `results/decision_pack.csv` |

Out of scope, stated in the report: nodal and hourly prices, weather, land,
transmission network data, financing curves, multistate models, dashboards.
Dropped: request-level archetypes, levers at scale, a risk frontier figure,
gradient-boosted survival, enriched features, Bayesian cohort effects.

### 13.2 Decision rules

`C_gate` from `cost_table.csv` (low / base / high); hurdle `h` = 3 at entry
and 2 two years in (both also at 2, 3 and 5; decision #61); `p_floor` = the
observed outcome rate of the pool the decision is made in; NPV at the ATB
cost of capital per technology, in a merchant and a contracted revenue case. **G1:** P = fair-baseline cell at 5 y (the model only if C19
passes), `p_leaf` from the segments; INVEST if `min(P, p_leaf) ≥ p_floor` and
`V ≥ h·C`; EXIT if `max(P, p_leaf) < p_floor` or `V < 0` at the high cost;
HOLD otherwise. **G2:** P = landmark "agreement updated" P(operation within
3 y); ACCELERATE if `P ≥ p_floor` and `V ≥ h·C`; EXIT if `V < 0` at the low
cost or `P < p_floor/2`; HOLD / SELL otherwise. **Adding:** chooser M on the
registered pool, add per region while `p_M ≥ p_floor`, then the 50% cap.
Every class is scored on what happened, with 200 resamples.

### 13.3 Report v3 (sections)

1 The decision (five questions) · 2 Data, one paragraph (F9) · 3 Where is
the opportunity (F25, F16, playbooks) · 4 Which requests get built, and when
(Table 1, F22, F11, timing, F12) · 5 Why requests fail (F19, F20, F6, F21) ·
6 What a project is worth (F26, cost to each gate) · 7 The portfolio review
(F23, decision cards) · 8 The book (four policies, expected shortfall, F18,
F24; the committee memo per region) · 9 Evaluation record (C1–C19) ·
10 Broader impacts · 11 Limitations, one paragraph · 12 Conclusion.
Body figures: F6, F9, F11, F12, F16, F18, F19–F26. `report/appendix.md` is
retired; the Makefile gains a docx target.

### 13.4 Order

08b (registration first) → 03, 09, 08 → 15 (ATB file) → 03b → 16 → 20 →
report numbers, Makefile, tests → report v3 → journal, proposal text for
Oct 19, full `make all`. Each notebook is executed top to bottom and its
figures looked at before the next starts; existing result tables must come
out unchanged.

---

## 14. v5 — the integrated energy portfolio (added 2026-10-12, decision #62)

Alan's direction of 2026-10-12, recorded in decision #62. The sub-sections
below keep the numbering 0–12 of the plan written that day (cited as
§14.0 … §14.12); the merge map and the verification list are part of it.
Order: (0) ERCOT API test → (1) consolidation merge
22 → 10 → (2) notebook 01 v5 sources and gate → (3) proposal update for
19 Oct → (4) 02–03 → (5) 05 → (6) 07 → (7) 08 → (8) 09 → (9) 10 → (10)
dashboard, report v4 and decisions. Stop only at the open items.


1. **Reuse freely from Alan's other repositories and desktop folders** (same author, so disclosed as self-reuse in the statement of work, as Milestone II was): `Forecast to Dispatch` (desktop + public GitHub `alanmossinger/forecast-to-dispatch`: ERCOT 2024 hourly DAM/RTM at 15 settlement points incl. HB_HOUSTON/HB_NORTH, ancillary MCPCs, load, wind/solar; `optimize/dispatch.py` co-optimized battery LP; `forecast/conformal.py`; `features/build.py` with declared legal lags), `Electricity-Grid-Net-Load-Forecasting…` / `MADS_Milestone2` (EIA-930 pipeline, conformal intervals, regime clustering), `ai-enablement-proof` (governed agent patterns).
2a. **EIA key.** On 12 Oct Alan pasted an EIA API key into chat (as the "ercot key"). The CAPSTONE `.env` already holds an `EIA_API_KEY`; whether it is the same one was not checked (reading the secret was blocked, rightly). Handoff instruction: Alan sets `EIA_API_KEY` in `.env` himself, and **rotates it** at <https://www.eia.gov/opendata/> because it has passed through chat (same as the 6 Oct note, open question #31). The key is never printed, logged or committed.
2. **ERCOT data: the Forecast-to-Dispatch work is the source** (Alan, 12 Oct). On disk at `…\Área de Trabalho\Forecast to Dispatch\data\raw\`: `ercot_dam_spp_2024.parquet` (131,760 rows: hourly DAM settlement-point prices, 15 locations incl. HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, HB_HUBAVG and the load zones), `ercot_rtm_spp_2024.parquet` (808,128 rows, 15-minute RTM), `ercot_dam_mcpc_2024.parquet` (hourly REGUP/REGDN/RRS/NSPIN/ECRS clearing prices), `ercot_native_load_2024.parquet`, `ercot_wind_solar_2024.parquet` — full calendar 2024, pulled with `gridstatus` (no key). These are copied into CAPSTONE `data/raw/ercot/` with SHA-256 and become the **OBSERVED** ERCOT price basis: the battery dispatch (energy + ancillary, reusing FtD's `optimize/dispatch.py` LP, credited as self-reuse), the price-capture factors for solar/wind/gas (hourly generation shape × hourly price), and the 2024 anchor of `market_monthly`. Earlier years: ICE ERCOT North monthly 2017–2019 (on disk). For 2020–2023 the next step runs FtD's `fetch_ercot_prices(start, end)` (`src/forecast_to_dispatch/data/ingest.py`) for 2018→2023 **from a network that reaches ercot.com** (this machine is refused, decision #53) — to be run from the author's side; until then the 2020–2023 months stay ASSUMED and labelled.
   **ERCOT Public API (searched 12 Oct):** no `.env` on this machine holds ERCOT credentials; the names `ERCOT_SUBSCRIPTION_KEY`, `ERCOT_USERNAME`, `ERCOT_PASSWORD` appear only, empty, in the `.env.example` of `MADS_Milestone2`, `MADS_Milestone2 review` and `Grid Electricity MIlestone II FInal Project`. Alan's own client for that API — `MADS_Milestone2/src/price_loader.py` (`_ercot_credentials`, `_ercot_id_token`: B2C sign-in → one-hour bearer token + `Ocp-Apim-Subscription-Key`; `load_ercot_as_prices` paged 5,000 rows; marked "untested against the live API") — is ported into CAPSTONE `src/ercot_api.py` (self-reuse, credited) and extended to the DAM settlement-point-price report (`np4-190-cd/dam_stlmnt_pnt_prices`) so 2018→2023 hourly prices can be pulled **from this machine through api.ercot.com** (which is not the blocked ercot.com report servlet; the first call is a test). **To do by hand:** paste the three ERCOT values into CAPSTONE `.env` (from <https://apiexplorer.ercot.com/>, Profile → Show); `.env.example` gains the three empty names; never printed. Tried on 12 Oct: apiexplorer.ercot.com returns "Access Denied, Error 16" (Incapsula) to the automated Chrome tab even while Alan's own tab is signed in, and a credential must not pass through the assistant in any case — so the paste is Alan's. Seen read-only in Alan's signed-in Opera (12 Oct): the catalog lists two products, *ERCOT ESR API* and *ERCOT Public API* (EMIL market-information products); the subscription needed is **ERCOT Public API** (EMIL, 5,858 products in the list Alan pasted). Alan pasted his ERCOT username and password into chat on 12 Oct; they were **not** recorded anywhere — handoff instruction: Alan writes them into `.env` himself and then **changes the ERCOT password** (same treatment as the EIA key, open question #31). The reports to call are NP4-190-CD (DAM settlement point prices), NP6-905-CD (RTM settlement point prices, 15-min) and NP4-188-CD (DAM ancillary clearing prices), all paged 5,000 rows like `load_ercot_as_prices`. The first `api.ercot.com` call from this machine is a test: if Incapsula blocks it too, the 2018→2023 pull runs from Alan's side (FtD `fetch_ercot_prices` or the ported client) and the files are dropped into `data/raw/ercot/`.
3. **Figures:** every figure clear and readable at report size and on a slide — the standing `src/plots.py` rules plus: one finding per figure in the title; units on every axis; ≤ 7 series; annotations on the number the text cites; the provenance footnote (OBSERVED / DERIVED / FORECAST / ASSUMED); and **the code that draws it explains itself** — each figure is a named function with a docstring (what it shows, why it is in the report, which result table it reads) and commented steps, so a reader of the notebook understands the picture without the report. A figure-QA checklist is run on every figure before it is called done (`docs/figure_qa.md`).
4. **The report is an executive + data-science + portfolio report, "completely innovative."** Design (section 12 below): it opens with a one-page **Capital Allocation Memo** (the book to fund, the numbers, the downside, what to do first) and a **Decision Board** (the existing D0–D6 extended to the five sectors); every chapter ends in a decision card; the innovations the report can claim and prove — (a) the interconnection-queue survival models fused into asset valuation as a timing/completion risk, which no public portfolio study does; (b) an AI advisor that must cite the result table behind every number, argues *against* the human, and is scored against realized outcomes in a decision gym; (c) provenance on every figure; (d) pre-registered criteria for every claim. An executive deck (`poster/` or `report/deck.md`) is built from the same figures.
5. **Consolidate the notebooks.** 22 notebooks → **10 story notebooks**, one per stage of the pipeline Alan asked for; nothing registered is lost — every result table in `results/` must come out byte-identical after the merge (diffed), and the tests must pass. Merge map (old → new):

| New notebook | Absorbs | Notes |
|---|---|---|
| `01_problem_and_data` | 01, 01b, 02 + v5 sources (BSEE, EIA-923, prices, ERCOT, eGRID) | readiness gates (v1 and v5) in one place |
| `02_eda` | 03, 03b + energy EDA | queue survival curves, map, production/generation/market EDA |
| `03_statistics_and_features` | 04 + statistics and leakage-safe energy features | split protocols registered here |
| `04_forecast_queue` | 05, 06, 07, 11, 12, 13, 14, 19 | "will it be built, and when": entry models, fair baseline, level repair, milestones, landmark models, MISO/SPP |
| `05_forecast_energy` | new | production, generation, prices: baselines vs ML, rolling origins, calibration, SHAP |
| `06_evaluation_record` | 08, 08b, 09, 18 | every registered criterion C1–C24 scored in one notebook; explanation and segments |
| `07_economics` | 15 + candidates | value, ATB costs, WACC, NPV, the 40 candidates, provenance |
| `08_scenarios_and_risk` | 17 (scenarios) + new | joint scenarios, stresses, VaR/CVaR, correlation ablation |
| `09_portfolio` | 16, 20 + MILP | gates, policies, managed book, A–D books, frontier, ablations |
| `10_advisor_and_gym` | new | the LLM advisor, the challenge session, the decision gym, AI evaluation |

Dropped as notebooks (content kept as sections): 13 (into 04), 17's levers (into 09 and the report), 18 (into 06). `run_pipeline.py` PIPELINE, the Makefile targets, `src/report_numbers.py` collectors and `report/figure_notes.md` are updated with the new names; old notebooks are deleted in the same commit (no dead files). The merge is its own phase with its own acceptance check (results unchanged, 107 tests green) **before** any v5 code is added, so a regression is attributable.



The capstone repo (`C:\Users\alanm\OneDrive\Área de Trabalho\CAPSTONE`, private GitHub `alanmossinger/Capstone`, 13 commits ahead, committed today) already runs end to end: 22 notebooks, 107 tests, queue-survival models (Cox, discrete-time, LightGBM, landmark models at +2 y), a value/cost layer with NREL ATB costs and WACC, project NPV in merchant and contracted cases, stage gates, four allocation policies, a "book" with expected shortfall, and report v3 (6,543 words). Its subject is a book of **power-plant interconnection requests**.

The new proposal (`UMich_MADS_US_Integrated_Energy_Portfolio_Capstone_Proposal.pdf`, 12 Oct) widens the decision to a **real multi-energy portfolio**: offshore oil & gas + ERCOT gas power, solar, wind and battery storage, under technical, market and capital uncertainty — EDA → forecast → simulate → optimize — with an auditable dashboard.

Alan's decisions (12 Oct): **extend** the capstone (the queue work becomes the timing/completion engine for the power candidates; nothing built is discarded); **LLM advisor grounded only in result tables**, per scenario, that recommends and explains, *challenges the human's reasoning* (motivated-reasoning check + "ideological Turing test" opponent) until the pair converge, and a **decision gym** that replays historical situations and scores human vs advisor vs optimizer against realized NPV; **Anthropic API key in `.env`**; **all five sectors, small counts** (~40 candidates); **a dashboard anyway**. Code must run end to end; it need not be a complete book.

Due dates: proposal update **19 Oct 2026**; final **14 Dec 2026**.

House rules that bind every step: Alan is sole author; notebooks carry the story (Inputs→Outputs cell, why-cell before code, **Reading this** after every figure, **Takeaways**); every number the report cites is written by code to `results/`; figures via `src/plots.py` (PNG+SVG, Okabe–Ito, source footnote naming the author); criteria **registered before scoring** (`results/success_criteria_v6.csv` + a decision entry, committed first); decisions entries as they are made; relative paths via `src/paths.py`; new dependency ⇒ a line in `docs/decisions.md`; the EIA key is never printed.

---

### 0. Problem (what the report opens with)

An energy company with a fixed annual capital budget must choose, among ~40 documented U.S. opportunities — 20 federal offshore Gulf of Mexico lease redevelopments, 5 ERCOT gas combined-cycle, 5 utility solar, 5 onshore wind, 5 battery storage — which to fund, when, and how much, when (a) physical output must be forecast, (b) oil, gas and power prices move together, (c) a new power plant may never reach operation or may reach it late (the queue models answer this), and (d) costs are only partly observable. RQ1 Predict · RQ2 Quantify risk · RQ3 Allocate (A top-N NPV vs B equal-capital sectors vs C deterministic MILP vs D risk-aware MILP under the same budget and the same scenarios) · RQ4 Explain. H1–H3 as in the proposal; thresholds registered before scoring.

The audit rule from the proposal is a code rule: every exported figure/table carries a `provenance` ∈ {OBSERVED, DERIVED, FORECAST, ASSUMED} (new helper in `src/plots.py`, asserted by a test).

### 1. Get the data (notebook 21 `21_get_energy_data`) — v5 data gate

| ID | Source | Access (verified 12 Oct) | Grain |
|---|---|---|---|
| S13 | BSEE OGOR-A delimited, 2010–2024 (`https://www.data.bsee.gov/Production/Files/ogora<YYYY>delimit.zip`, 1.4–2.7 MB each, HTTP 200) | scripted download + SHA-256 | lease-month oil bbl, gas Mcf, water bbl, days on prod |
| S14 | EIA-923 plant/prime-mover monthly generation & fuel, **via EIA API v2** `electricity/facility-fuel` (eia.gov bulk zips returned 503 today; the API works with the key already in `.env`; reuse `src/eia_api.py` paging) | API | plant-month, Texas |
| S4 | EIA-860 generator inventory — **already on disk** (`data/raw/eia860m/eia860m_2026-07.parquet`) | reuse | generator |
| S6 | WTI Cushing monthly, Henry Hub monthly — EIA API (`petroleum/pri/spt`, `natural-gas/pri/fut`), fallback `…/hist_xls/RWTCm.xls`, `RNGWHHDm.xls` (HTTP 200) | API / xls | month |
| S7 | ERCOT power prices: ICE ERCOT North peak 2017–2019 (on disk, `value.ice_hub_prices`) + **ERCOT DAM/RTM hourly 2024 at HB_HOUSTON, already on disk** in `…\Área de Trabalho\Forecast to Dispatch\data\raw\ercot_dam_spp_2024.parquet`, `ercot_rtm_spp_2024.parquet` (copied with SHA-256 into `data/raw/ercot/`) | copy | hourly 2024, monthly 2017–19 |
| S8 | NREL ATB 2024 — **already on disk** (`data/raw/atb/ATBe_2024_v3.parquet`; `value.atb_costs`, `atb_wacc`, `atb_capacity_factors`) | reuse | technology-year |
| S9 | EPA eGRID 2023 plant emission rates (`epa.gov/egrid/download-data`, reachable) | download | plant |
| — | LBNL queue file + landmark predictions — **already on disk** (`data/processed/predictions_landmark.parquet`, `results/decision_pack.csv`) | reuse | request |

Outputs: `data/raw/<source>/` + `SHA256.txt`, `data/raw/manifest_v5.json` (URL, timestamp, vintage, checksum, units), `docs/data_readiness.md` gains a **v5 section ending in GO/NO-GO** (coverage ≥ 2018-01→2024-12 for every monthly series; ≥ 20 GOM leases with ≥ 60 producing months; ≥ 5 Texas plants per technology with ≥ 36 months of generation). No modelling notebook starts before GO.

**Open (data):** ERCOT monthly prices 2020–2023 are not on disk (ercot.com blocks this machine; `gridstatus` works from another network as it did for Forecast-to-Dispatch). Either Alan pulls `ERCOT DAM SPP 2018-01→2024-12` via `gridstatus` into `data/raw/ercot/`, or the 2020–2023 bridge stays `ASSUMED` (0.77 × PJM West, the existing assumption) and is labelled everywhere.

### 2. Build the panel (notebook 22 `22_build_energy_panel`) — reproducible joins

New module `src/energy_data.py` (parsers, unit standardisation: bbl, Mcf, MWh, nominal→real 2024 USD via CPI from EIA/BLS or a stated deflator) and `src/panel.py` (joins + audits). Tables in `data/interim/` (parquet) + a small `data/processed/energy_panel_summary.csv`:

`upstream_monthly(lease_id, month)` · `plant_year(plant_id, generator_id, year)` · `generation_monthly(plant_id, prime_mover, month)` (kept at EIA-923's reported grain, never split to generator) · `market_monthly(market_id, month)` with `wti_usd_bbl, hh_usd_mmbtu, ercot_usd_mwh` · `technology_costs(technology, atb_vintage, scenario)` · `release_lags.csv` (what was observable at each forecast origin: EIA-923 ~2-month lag, BSEE ~3-month, prices same month).

Audits logged as numbered rules (R10…, as R1–R9 were): one-to-many merge checks, duplicate lease-months, zero/negative production, plants with technology changes.

### 3. EDA (notebook 23 `23_explore_energy`)

Six families, each with a decision insight: data quality (missingness map, reporting lags, zero months); production profiles (lease cohort decline curves, oil/gas mix, water cut — Arps fit per lease as the physics baseline); generation (monthly capacity-factor distributions by technology × season, Texas); market regimes (WTI, HH, ERCOT: volatility, autocorrelation, 2014/2020/2022 episodes); spatial (GOM leases + Texas plants on the existing `src/geo.py` map, F9 style); multivariate (correlation heatmap, PCA; cautious clustering of operating profiles with stability check). Core report visuals: asset map, price/output/CF panels, cross-sector correlation heatmap.

### 4. Statistics (notebook 24, first half)

Block/moving-block bootstrap CIs for every descriptive figure (reuse the bootstrap helpers in `src/evaluation.py`); Pearson/Spearman and **lagged** cross-correlations among WTI, HH, ERCOT power and production; stationarity (ADF/KPSS) and structural breaks; calibration and uncertainty decomposition later in §6. Adds `statsmodels` (decision entry).

### 5. Feature engineering (notebook 24, second half) — leakage-safe

`src/energy_features.py`: lagged output 1/3/6/12, decline slope, water ratio, producing months, lease depth/vintage; lagged MWh, normalized generation, heat-rate proxy, fuel cost, season, downtime proxy; spread statistics for storage; trailing price volatility, macro period. Every feature lagged relative to the forecast origin using `release_lags.csv`; imputers/scalers fit inside each training fold; a **truncation test** proves no feature changes when post-origin data are removed (same proof pattern as Forecast-to-Dispatch). Split protocol registered: development 2018–2023 rolling origins, validation 2024-H1, holdout 2024-H2 (adjust after the data gate).

### 6. ML — supervised forecasts (notebook 25 `25_forecast_models`)

| Target | Baselines | Challengers | Metrics |
|---|---|---|---|
| lease oil & gas output 3/6/12 m ahead | last value, seasonal naive, Arps decline | ElasticNet, LightGBM, LightGBM quantile (P5–P95) | MAE/RMSE vs naive, bias, 90 % coverage |
| plant-month generation / CF | seasonal naive, technology-month median, linear panel | LightGBM pooled by technology | same |
| monthly WTI, HH, ERCOT price | random walk, seasonal naive | regularized regression, quantile LightGBM | MAE vs RW, coverage |

Rolling-origin backtest with expanding window; paired evaluation at matched origins with moving-block bootstrap CIs (reuse `src/evaluation.py`); conformal width scaling for intervals; leave-some-leases-out and technology cold-start check; SHAP summaries (stack already has `shap`). Pre-registered **C20** (H1): each ML challenger beats the best baseline on held-out MAE with the paired interval on the better side, per target; failures reported, not removed. Forecasting is evaluated separately from allocation.

### 7. Candidates and economics (notebook 26 `26_candidates_and_economics`) — the real portfolio

`results/investment_candidates.csv` (40 rows: `project_id, sector, asset_anchor, region, lat/lon, mw_or_boepd, capex, timing_source, provenance`):
- **Offshore O&G ×20**: real BSEE leases with ≥ 60 producing months, ranked by remaining production; decision = modeled redevelopment (incremental uplift vs the Arps baseline, 10/20/30 % as ASSUMED grid), cost from a documented low/base/high assumption grid (workover $/well, opex $/boe, 18.75 % federal royalty, abandonment) — never presented as company data.
- **ERCOT power ×20**: real ERCOT queue requests from the LBNL file (5 gas, 5 solar, 5 wind, 5 storage, 2017–2019 cohort so outcomes are known for the gym) with MW and county; CAPEX/FOM/VOM/heat rate from `results/atb_costs.csv`; CF from Texas EIA-923 distributions + ATB; **P(operation) and operation-year distribution from the existing landmark models** (`predictions_landmark.parquet`, `landmark.conditional_cif`) — this is where the queue work plugs in; credits/PPA cases from `value.py` as they stand.
- **Storage**: daily-spread dispatch on the real 2024 hourly ERCOT prices (simple LP per day via `scipy.optimize.linprog`, no cvxpy), scaled to monthly revenue; labelled "simplified, no ancillary services" (the stronger claim needs Forecast-to-Dispatch's co-optimization — out of scope, cited).

`src/economics.py`: monthly cash-flow engine per candidate × scenario (revenue formulas technology-specific, construction timing, carbon cost via eGRID factors as optional constraint input, taxes/credits as in `value.py`), NPV at the technology WACC (`value.atb_wacc`; 8 % stress) with a common valuation date; reuse `value.npv_per_mw`. Outputs `results/candidate_npv.csv`, break-even prices, low/base/high cost sensitivity.

### 8. Joint uncertainty and stress (notebook 27 `27_scenarios_and_risk`)

`src/scenarios.py`: 2,000 reproducible joint scenarios (seeded) — moving-block bootstrap of monthly joint log-changes of (WTI, HH, ERCOT) preserving cross-correlation; production/generation residual draws from notebook 25's quantile models; cost multipliers; **timing draws for power candidates from the landmark CIF with the shared factor ρ** (`portfolio.simulate_operation_years`). Named stresses: oil collapse (2020 path), high gas / low spark spread, weak wind year, solar curtailment, two-year delay, simultaneous downside. Risk measures per candidate and per portfolio: percentile bands, P(NPV < 0), VaR95, CVaR95 (`portfolio.expected_shortfall`). A second scenario generator (Gaussian copula on the same marginals) is held out for §9 evaluation. Ablation: correlations removed, marginals kept.

### 9. Portfolio building and optimization (notebook 28 `28_portfolio_optimization`)

`src/optimizer.py` on `scipy.optimize.milp` (HiGHS, already in scipy 1.17 — no new dependency): x_i ∈ {0,1}; maximize E[NPV] − λ·CVaR95 with the Rockafellar–Uryasev linearization over the scenario set; constraints: annual CAPEX limits, technology concentration ≤ 40 %, mutually exclusive alternatives, dependencies, optional emissions cap. Comparators under the same budget and scenarios: **A** top-N expected NPV, **B** equal-capital sectors, **C** deterministic budget MILP (base case only), **D** risk-aware MILP; plus oil/gas-only and power-only books. Out-of-sample: score every book on the held-out copula scenarios and on the realized 2018–2024 path. Efficient-frontier sweep over λ; capital-at-risk; sensitivity tornado (budget −20 %, WTI −30 %, HH +50 %, λ, horizon, carbon price). Ablations: naive forecasts + same optimizer; no oil/gas; no renewables/storage. Pre-registered **C21–C24** (H2, H3): D beats A and B on the registered risk/return metric out of sample with the paired interval on the better side; D's selection changes less than C's across stresses (Jaccard); the diversification benefit survives joint modelling. Reuse `portfolio.greedy_risk_adjusted` as a cross-check of the MILP.

### 10. AI advisor (notebook 29 `29_advisor` + `src/advisor.py`) — "AI helps the decision"

`anthropic` added to `requirements.txt` (decision entry); `ANTHROPIC_API_KEY` in `.env` via `dotenv`, never printed; model id, temperature and effort recorded with every call.

Grounding rule: the advisor sees **only** result tables (`investment_candidates.csv`, `candidate_npv.csv`, `scenario_summary.csv`, `portfolio_books.csv`, `stress_tests.csv`, `decision_pack.csv`) passed as structured context; every number in an answer must appear in those tables — `advisor.verify_numbers()` checks this (the same discipline as `tests/test_report.py`) and the check result is stored with the answer. Every call is appended to `results/advisor_runs.jsonl` (prompt, response, model, params, verification); **`replay=True` re-serves recorded responses so `make all` runs offline without a key** (reproducibility requirement).

Three modes:
1. **Recommend** — for the base case and each named stress: the recommended book, why (numbers cited), what would change the answer → `results/advisor_recommendations.csv`; compared with the optimizer's D book (agreement rate).
2. **Challenge** ("reason my thinking") — the human states a preferred decision; the advisor asks ≤ 5 targeted questions (context and stakes, what each party wants, emotional investment, evidence emphasised vs dismissed, framing), then names specific motivated-reasoning patterns (moving goalposts, double standards, working backward), argues the opposing book as a strong opponent (ideological Turing test), and the two iterate until they converge on a book or a documented disagreement; transcript saved. Alan's two prompts become the system prompt templates in `prompts/` (committed; the course wants an actual prompt in the appendix).
3. **Decision gym (scored backtest)** — historical situations built as-of their date with no hindsight (ERCOT queue requests at entry/+2 y with realized outcomes from `decision_pack.csv`; oil-price regimes 2014, 2020, 2022 applied to the lease candidates; a 2018 budget cut), human picks, advisor challenges, then the realized NPV is revealed and one score per situation is written for human, advisor, optimizer and "instinct" (top-N NPV) → `results/decision_gym_scores.csv`. "Defy the human instinct" is measured, not asserted.

Evaluation of AI outputs (checklist item): number-grounding rate, agreement with the optimizer, gym score vs instinct, and a labelled rubric on 10 answers — all in `results/advisor_evaluation.csv`.

### 11. Dashboard (`app/app.py`, Streamlit — decision entry)

Five pages reading `results/` only (no recomputation of models): Portfolio (budget, λ, price-shock sliders → optimizer re-solved on cached scenarios in < 2 s; books A–D side by side), Scenarios & risk, Candidates map, Advisor (modes 1–2, replay by default), Decision gym. Opened in Chrome via Claude in Chrome for verification (memory rule: never the built-in pane).

### 12. Deliverables, calendar and governance

- **Proposal update for 19 Oct**: `docs/proposal_update_2026-10-19.md` — the Group 13 form answered again (Q2–Q8, Q11) for the integrated portfolio with the queue models as the timing engine; data access and licences (BSEE/EIA/NREL/EPA public; LBNL as before).
- **Report v4**: sections added to `report/report.md` — the portfolio problem, data (S13–S14), EDA, forecasts, economics (with the provenance labels), scenarios, allocation (A–D), the advisor and the gym, evaluation record C20–C24, broader impacts (modeled costs ≠ company data; no "AI increases returns X %" headline unless computed with its envelope), limitations; `src/report_numbers.py` gains v6 collectors; `docs/ai_use.md` + workflow diagram (`figures/ai_workflow`) for the AI appendix; `prompts/` log.
- **Makefile**: `v5` target (21→29), `app`, `all` extended; `run_pipeline.py` PIPELINE gains `"21"…"29"`.
- **Tests** (`tests/`): `test_energy_data.py` (manifest, units, checksums), `test_panel.py` (join cardinality, release lags), `test_energy_features.py` (truncation/leakage proof), `test_economics.py` (NPV identities, provenance present on every export), `test_scenarios.py` (correlation preserved, stresses applied, seed reproducible), `test_optimizer.py` (budget/caps respected, D ≥ C on the objective, infeasible → clear error), `test_advisor.py` (grounding check, replay without key).
- **Notebook numbering in the sections above** (21→29) maps onto the consolidated set: 21/22 → `01`, 23 → `02`, 24 → `03`, 25 → `05`, 26 → `07`, 27 → `08`, 28 → `09`, 29 → `10`; the queue work lives in `04` and the scored criteria in `06`.
- **Calendar** (weeks from 12 Oct): W0 (this week) consolidation merge 22→10 with results diffed + proposal update (19 Oct) · W1 `01` v5 sources + data gate · W2 `02`–`03` · W3 `05` · W4 `07` + **scope gate** (if any sector lacks data: keep oil/gas + ≥ 2 others, reduce counts; never drop oil/gas) · W5 27 · W6 28 · W7 29 + app · W8 report v4 + AI appendix · W9–10 full `make all`, figures read, poster/video, README, mentor feedback, tag `v1.0` · buffer to 14 Dec.
- **To confirm before building**: ERCOT 2020–2023 prices (§1); the upstream cost grid defaults (workover $/well, opex $/boe, uplift %) to confirm or replace; `ANTHROPIC_API_KEY` into `.env`; EIA key rotation (carried); `git push` when wanted.

### Verification (end to end)

0. Consolidation gate: after the 22→10 merge, `make all` reproduces every file in `results/` byte-identical (or identical to the stated tolerance for the tournament tables, 1e-16) and `make test` passes before any v5 line is written.
1. `make v5` from the raw files: the v5 sections of notebooks `01`→`10` execute top to bottom (`nbconvert --execute --inplace`), each figure opened and read, every number in the report traced (`make numbers`, `tests/test_report.py`).
2. `make test`: all existing 107 tests still pass; new tests pass; the leakage truncation test and the advisor grounding test are the two that may not be skipped.
3. `make all`: the v1–v4 result tables come out **unchanged** (diff `results/` before/after) — the extension must not move a registered number.
4. `streamlit run app/app.py` → open `http://localhost:8501` in Chrome; change budget −20 % and λ; the books, the frontier and the advisor's replayed answer update; screenshot for the report.
5. Offline run: remove `ANTHROPIC_API_KEY` from the environment and rerun notebook 29 in replay mode — identical outputs.
6. Decisions #62+ (v5 scope, new dependencies, criteria C20–C24 registered first) recorded; commit.

### Addendum (Alan, 12 Oct, later) — the AI in the decision, the human's override

The advisor is part of every decision, not a commentator. For the forward book at 1, 2, 3, 5, 10
and 20 years it proposes the most likely book under the scenario distribution (expected NPV, P(NPV < 0),
CVaR per horizon) and explains it from the result tables; the human reviews and interacts in the
dashboard. **Override gate:** the human may override the advisor's book only after answering the
reasoning prompts (the motivated-reasoning questions and the opposing case); an override without the
answers is refused by the app. Every proposal, answer, override and later realized outcome is appended
to `results/decision_ledger.csv`, so the gym can score forward decisions as outcomes arrive. Replay mode
re-serves recorded exchanges; the live challenge of a new decision needs the key in `.env`.

### Addendum (Alan, 12 Oct, later) — two modes, one dashboard

The AI sits inside the portfolio process in two modes, in this order. **Learn from history:** the gym
page replays documented situations with past data; the human picks, the advisor challenges with the
reasoning prompts, the realized outcome is revealed, and NPV, constraints and the score appear at once.
**Decide forward:** the advisor proposes the most likely book from the forecasts and the scenario
distribution (expected NPV, P(NPV < 0), CVaR, binding constraints shown immediately); on request it
builds scenario plans with probabilities (named scenarios drawn from the scenario engine, each with its
weight and the book under it); the human reviews, interacts and may override through the override gate.
Clear and easy: one command (`make app`), result tables only, every number traceable, replay by default.

### Addendum (Alan, 12 Oct, later) — all data, one process, and the price of thin information

The candidate universe is not limited to ERCOT and the Gulf: every region the data describe is in the
pool (PJM and CAISO with dated timing models, MISO and SPP with the 2026-file models, the Gulf leases).
The AI process is the same everywhere. Where a region's data are thinner (no hourly prices, no dated
milestones, a short generation panel) the candidate carries a **data-completeness score** built from the
manifest and the panel coverage; the dashboard shows the warning when the human moves into such an
area; the scenarios widen the uncertainty for it (larger residual and timing spread) and the optimizer
tightens its constraints (lower concentration cap, higher risk charge). Nothing changes in the method;
the picture stays complete; less information shows up as more risk and more constraint, not as silence.

### Addendum (Alan, 12 Oct, evening) — the cost grid confirmed; impact visible to everyone

The upstream cost grid of decision #68 is confirmed. The dashboard shows, to every viewer, the assumption
grid and its impact: each candidate's NPV under low / base / high, the tornado of the book's expected NPV
and CVaR against every assumption, and every project's contribution to the portfolio's expected NPV, CVaR
and emissions ("project impact"). Results are never shown without the assumptions behind them.
