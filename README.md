# Queue Survival: Which Proposed Power Plants Get Built, and When?

SIADS 699 Capstone (Master of Applied Data Science, University of Michigan), Group 13.
Author: Alan Mössinger.

> **Status (2026-10-04):** the data gate reads GO
> ([`docs/data_readiness.md`](docs/data_readiness.md)); notebooks 01 (data),
> 02 (cleaning), 03 (survival curves), 04 (samples and features), 05
> (baseline and Cox models), 06 (discrete-time models) and 07 (all-regions
> model) run end to end.
> Next: evaluation (08).

## About

At the end of 2024 about 10,300 projects — roughly 1,400 GW of generation and
890 GW of storage — were waiting in U.S. interconnection queues. Most will
never be built: of the capacity that requested interconnection in 2000–2019,
about 13% reached commercial operation and 77% was withdrawn, and the median
wait from request to operation has more than doubled to over four years
(Rand et al., 2025). Developers, lenders and grid operators still reason about
this pipeline with cohort averages.

## Question

For a proposed plant, at the moment it enters the queue and using only what is
known then: what is the probability that it reaches commercial operation within
3, 5 and 7 years, and how long is it likely to take? And can those estimates be
calibrated and ranked well enough for a developer or lender to act on?

## Data

| Source | What | Access |
|---|---|---|
| LBNL *Queued Up: 2025 Edition* project file | 36,441 interconnection requests through end-2024 | download by hand from <https://emp.lbl.gov/queues>; not redistributed |
| EIA-860M via the EIA API v2 | inventory of operable U.S. generators (operating month, location) | free API key in `.env` |

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
make all       # executes notebooks 01 → 09 in order, stopping at the first error
make test      # pytest
```

Each step also has its own target (`make data`, `make clean`, `make explore`, …;
see the `Makefile`). `python run_pipeline.py --only 01` runs a single notebook.

## Map of the repository

```
notebooks/   01_get_data … 09_explain_and_rank — the analysis, run in order
src/         small helper package used by the notebooks (paths, config, data access, plots)
data/        raw/ (not committed) · interim/ (not committed) · processed/ (small final tables)
results/     every number the report cites, written by the notebooks
figures/     every figure, PNG + SVG; figures/<notebook>/ holds each notebook's exploratory figures
report/      report.md and figure_notes.md (caption stubs collected from the notebooks)
docs/        journal.md (work log), decisions.md, data_readiness.md, mentor_feedback.md
tests/       pytest checks on the audit, cleaning, features and metrics
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
