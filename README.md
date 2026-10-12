# From Queue to Grid: AI-Driven Portfolio Management for the U.S. Power-Plant Pipeline

SIADS 699 Capstone (Master of Applied Data Science, University of Michigan), Group 13.
Author: Alan Mössinger.

> **Status (2026-10-12):** the 22 notebooks of v1–v4 were consolidated into
> the story layout of PLAN.md §14 (01 data, 02 EDA, 03 features, 04
> forecasting the queue, 06 the evaluation record, 07 economics, 09 the
> portfolio; 05, 08 and 10 are the v5 additions to come). Every result table
> came out byte-identical after the merge (decision #63). `make all` runs
> them end to end; the registered verdicts are untouched.

## About

At the end of 2024 about 10,300 projects — roughly 1,400 GW of generation and
890 GW of storage — were waiting in U.S. interconnection queues. Most will
never be built: of the capacity that requested interconnection in 2000–2019,
about 13% reached commercial operation and 77% was withdrawn, and the median
wait from request to operation has more than doubled to over four years
(Rand et al., 2025). Developers, lenders and grid operators still reason about
this pipeline with cohort averages.

## Question

For a portfolio of proposed plants: which requests get built, when, and which
book of requests to back — from what is known on the request date and again at
each milestone. Six questions, each answered by a notebook: how well the models
predict survival and timing (11–12), each request's probability and why (09,
14, 16), what a request should have different and the constraints (16–17), how
to reduce them (17), the right book per region (15–16) and what an energy
company should do with the result (report). The v1 question — can a model
beat cohort averages at entry — is answered by notebooks 05–09, and the
answer for utility-scale requests turned out to be *no beyond a size lookup*
(notebook 11); the value is at the milestones (notebook 14), where a
registered test finds the model's book holds more requests that reach
operation than a lookup that knows the agreement status, though not more MW
(notebook 20).

## Data

| Source | What | Access |
|---|---|---|
| LBNL *Queued Up: 2025 Edition* project file (frozen) | 36,441 interconnection requests through end-2024 — the basis of every registered result | download by hand from <https://emp.lbl.gov/queues>; not redistributed |
| LBNL *Queued Up: 2026 Edition* project file (alongside) | 38,201 requests through end-2025: reconciliation, the newest cohorts' early outcomes, MISO/SPP dates | same page; CC BY 4.0 |
| EIA-860M via the EIA API v2 | inventory of operable U.S. generators (operating month, location) | free API key in `.env` |
| CAISO public queue report (via `gridstatus`) | cluster, study-phase and agreement status of CAISO requests | `data/raw/iso/` |
| PJM queue export and ERCOT GIS report | PJM request, exit and status fields; ERCOT phase dates for requests still active (notebook 13) | fetched from pjm.com and ercot.com; `data/raw/iso/`, not redistributed |
| EIA wholesale prices, PJM market-monitor report, LBNL PJM cost data, IRS Notice 2025-42, Census boundaries | the value and cost layer and the map | `data/raw/value/`, `data/raw/lbnl_costs/`, `data/raw/geo/` |

The full data access statement, terms and data dictionary are in
[`data/README.md`](data/README.md).

## How to run

Requires Python 3.11 and GNU make.

```bash
make setup     # .venv, pinned packages, Jupyter kernel "queue-survival"
```

1. Save `lbnl_ix_queue_data_file_thru2024_v2.xlsx` in `data/raw/lbnl/`.
2. Copy `.env.example` to `.env` and add your EIA API key.
3. Run:

```bash
make all       # notebooks 01 → 10 in dependency order (06, the record, runs last), stopping at the first error
make test      # pytest
make report    # report/report.pdf and report/report.docx from report/report.md + references.md (needs pandoc and typst)
```

Each notebook also has its own target (`make data`, `make eda`, `make features`,
`make forecast`, `make economics`, `make portfolio`, `make record`, …; see the
`Makefile`). `python run_pipeline.py --only 01` runs a single notebook.

## Map of the repository

```
notebooks/   01_problem_and_data (sources, cleaning rules, the 2026 edition, readiness gates)
             02_eda (survival curves, drivers, the map, state archetypes)
             03_statistics_and_features (outcomes, samples, split, entry-time features)
             04_forecast_queue (entry models, fair baseline, entry rules, level repair, ablation,
                milestones, landmark models, MISO/SPP — the completion and timing engine)
             06_evaluation_record (every registered criterion scored, post-hoc and tournament,
                explanation, the decision board; runs last)
             07_economics (value, cost, project NPV)
             09_portfolio (scorecards, books, gates, levers, the managed book)
             Each notebook is made of lettered parts; a part header says which old notebook it was.
src/         small helper package used by the notebooks (paths, config, data access, plots)
data/        raw/ (not committed) · interim/ (not committed) · processed/ (small final tables)
results/     every number the report cites, written by the notebooks
figures/     every figure, PNG + SVG; figures/<notebook>/ holds each notebook's exploratory figures
report/      report.md, references.md, playbooks.md, figure_notes.md (caption stubs from the notebooks);
             `make report` builds report.pdf and report.docx (needs pandoc and typst)
docs/        journal.md (work log), decisions.md, data_readiness.md, mentor_feedback.md
tests/       pytest checks on the audit, cleaning, features, metrics, baselines, drift, landmarks, value and the book
```

## Results at a glance

From `results/` (notebooks 01–03):

- The public file reproduces LBNL's headline: 12.6% of 2000–2019 requested
  capacity reached operation and 76.9% was withdrawn
  (`results/headline_checks.json`).
- Naive five-year completion for 2010–2018 generation entrants:
  CAISO 4.2%, PJM 15.2%, ERCOT 21.3% (`results/naive_mockup.csv`) — the
  baseline the models must beat.
- Only CAISO, ERCOT and PJM record both operation and withdrawal dates
  (`results/event_date_coverage.csv`), so the timing model covers those three.
- Five years after the request, 18.4% of ERCOT, 13.2% of PJM and 4.8% of
  CAISO projects are operating (Aalen–Johansen, `results/cif_horizons.csv`;
  figure `figures/F1_cif_by_region.png`).
- The clean file reproduces LBNL's published completion rates within 1.2
  points for every technology and region (`results/benchmarks.csv`).

## References

Rand, J., Manderlink, N., Zhang, S., Talley, C., Gorman, W., Wiser, R., Seel, J.,
Mulvaney Kemp, J., Jeong, S., & Kahrl, F. (2025). *Queued up: 2025 edition —
Characteristics of power plants seeking transmission interconnection as of the
end of 2024.* Lawrence Berkeley National Laboratory. https://emp.lbl.gov/queues

U.S. Energy Information Administration. (2026). *Preliminary monthly electric
generator inventory (EIA-860M)* [Data set, accessed through the EIA API v2].
https://www.eia.gov/electricity/data/eia860m/
