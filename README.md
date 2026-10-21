# Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization

*From Machine Learning to Risk-Aware Capital Allocation Across Oil, Gas, Power, Renewables, and Storage*

SIADS 699 Capstone (Master of Applied Data Science, University of Michigan), Group 13.
Author: Alan Mössinger.

> **Status (2026-10-20, v9, branch `v8-corrections`):** an executive report
> (core of about 4,200 words) on one decision — twenty Gulf of Mexico lease
> redevelopments and twenty ERCOT requests under one budget on 1 January
> 2025, with only what was public that day. A risk-aware optimizer beats NPV
> ranking under equal constraints, at the price of expected value and with a
> capital plan that needs a contingent construction line; the machine-learning
> queue forecasts do not demonstrably improve the decision. An AI *challenger*
> (`src/challenge.py`) reads a committee's rules from its words, tests its
> proposal with computed tools and recommends a computed alternative; in a
> registered test on simulated committees (`results/v9/`, notebook 11
> section 11) following it improves the committee's own objective and avoids
> loss, mostly through its tools, while the language model's own part is
> reading rules and arguments. Eleven notebooks run end to end (`make all`);
> every registered criterion is scored as registered. The session log is
> `docs/journal.md`; the reasons are in `docs/decisions.md` (#93–#99).

## About

At the end of 2024 about 10,300 projects — roughly 1,400 GW of generation and
890 GW of storage — were waiting in U.S. interconnection queues. Most will
never be built: of the capacity that requested interconnection in 2000–2019,
about 13% reached commercial operation and 77% was withdrawn, and the median
wait from request to operation has more than doubled to over four years
(Rand et al., 2025). Developers, lenders and grid operators still reason about
this pipeline with cohort averages.

## Question

Part I, the queue: for a portfolio of proposed plants, which requests get
built, when, and which book of requests to back — from what is known on the
request date and again at each milestone. Six questions, each answered by a
notebook: how well the models predict survival and timing (04), each
request's probability and why (04, 06), what a request should have
different and the constraints (09), how to reduce them (09), the right book
per region (09) and what an energy company should do with the result
(report). The v1 question — can a model beat cohort averages at entry — is
answered in notebooks 04 and 06, and the answer for utility-scale requests
turned out to be *no beyond a size lookup*; the value is at the milestones,
where a registered test finds the model's book holds more requests that
reach operation than a lookup that knows the agreement status, though not
more MW (notebook 09).

Part II, the integrated portfolio: an energy company with one budget
chooses among twenty offshore Gulf lease redevelopments and twenty ERCOT
power requests. Can machine learning improve the physical forecasts (05)?
How do forecast error, price uncertainty and correlation change the book's
risk (08)? Does a risk-aware book beat NPV ranking and sector-only books
out of sample under the same budget (09, C21–C24)? Which features and
constraints change the selection (09)? And can an LLM advisor, grounded in
the result tables, recommend, challenge the human and be scored against
realized outcomes (10)?

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

Requires Python 3.11, GNU make and poppler's `pdftotext` on the PATH (notebook 07 reads two tables of the
PJM market monitor's report from its PDF; the parser uses `pdftotext -layout`, so any poppler version works).

```bash
make setup     # .venv, pinned packages, Jupyter kernel "queue-survival"
```

1. Save `lbnl_ix_queue_data_file_thru2024_v2.xlsx` in `data/raw/lbnl/`.
2. Copy `.env.example` to `.env` and add your EIA API key. For live advisor calls either add `ANTHROPIC_API_KEY` or sign in to the `claude` command line with a Claude subscription (`claude auth login`); with neither, the advisor replays its record. The replay is keyed on the exact prompt text, which includes the result tables, so it reproduces exactly on the machine that recorded it; on another platform, floating-point differences in the last decimals of a table can miss the record for a few calls, which then need a live backend. To challenge your own decision at the keyboard, run `python -m src.advisor`: state the book you prefer, answer the advisor's five questions, and read its verdict and the opposing case (the transcript goes to `results/advisor_transcripts/`).
3. Run:

```bash
make all       # notebooks 01 → 10 in dependency order (06, the record, runs last), stopping at the first error
make test      # pytest
make report    # report/report.pdf and report/report.docx from report/report.md + references.md (needs pandoc and typst)
make poster    # report/poster.pdf from report/poster.typ (needs typst)
make app       # the dashboard at http://localhost:8501 (reads results/ only)
```

Each notebook also has its own target (`make data`, `make eda`, `make features`,
`make forecast`, `make economics`, `make portfolio`, `make record`, …; see the
`Makefile`). `python run_pipeline.py --only 01` runs a single notebook.

## Map of the repository

```
notebooks/   01_problem_and_data (queue sources and cleaning; the v5 sources BSEE, EIA-923, prices, ERCOT 2024, eGRID; manifest; readiness gates)
             02_eda (survival curves, drivers, the map, state archetypes; the energy EDA)
             03_statistics_and_features (queue outcomes and features; the energy statistics and leakage-safe features; C20 registered)
             04_forecast_queue (entry models, fair baseline, entry rules, level repair, ablation,
                milestones, landmark models, MISO/SPP — the completion and timing engine)
             05_forecast_energy (lease output, capacity factors and prices at rolling origins; C20 scored)
             06_evaluation_record (every registered criterion scored, post-hoc and tournament,
                explanation, the decision board; runs after 09)
             07_economics (queue value and cost; the forty candidates under the upstream cost grid, provenance labels)
             08_scenarios_and_risk (joint price, output, cost and timing scenarios; stresses; risk measures)
             09_portfolio (scorecards, books, gates, levers, the managed book; the four books A–D, C21–C24)
             10_advisor_and_gym (the grounded LLM advisor, the challenge round and the override gate,
                the decision gym, the forward view at 1–20 years; replay mode runs offline)
             Each notebook is made of lettered parts; a part header says which old notebook it was.
src/         small helper package used by the notebooks (paths, config, data access, plots, models, economics,
             scenarios, optimizer, advisor, gym, horizons)
app/         app.py — the Streamlit dashboard: decide forward (re-solved book, grid and impact, forward view,
             advisor, override gate), learn from history (the gym), scenarios, candidates, the ledger
prompts/     the advisor's system prompt, the recommend and gym templates, the two reasoning prompts
data/        raw/ (not committed) · interim/ (not committed) · processed/ (small final tables)
results/     every number the report cites, written by the notebooks; advisor_runs.jsonl is the replay record
figures/     every figure, PNG + SVG; figures/<notebook>/ holds each notebook's exploratory figures
report/      report.md, references.md, playbooks.md, figure_notes.md (caption stubs from the notebooks), poster.typ;
             `make report` builds report.pdf and report.docx (needs pandoc and typst)
docs/        journal.md (work log), decisions.md, data_readiness.md, mentor_feedback.md, ai_use.md,
             proposal_update_2026-10-19.md
tests/       pytest checks on the audit, cleaning, features, metrics, baselines, drift, landmarks, value, the book,
             the energy data and features (the truncation proof), economics, scenarios, the optimizer,
             the advisor (grounding, replay), the gym and the horizons
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

From `results/` (Part II, notebooks 05–10):

- Under the registered cost grid the twenty lease redevelopments carry
  $14.6B of incremental NPV; priced as an investment committee would
  (capital per incremental barrel, an 8% real rate) they carry $7.0B on
  four times the capital (`results/posthoc_lease_values.csv`, labelled
  post-hoc, decision #74). Contracted wind is the only power request that
  earns its capital, in either draw of candidates.
- The registered allocation criteria C21–C24 fail as registered: on the
  held-out scenarios the worst 5% of each optimised book is still a
  profit, so risk aversion buys nothing. Under the committee grid the
  risk-aware book halves the tail at a cost in expected value
  (`results/posthoc_books_committee.csv`).
- The decision gym scores Part I's gate rule against instinct in sixteen
  past situations (`results/decision_gym_scores.csv`); the LLM advisor is
  built and gated, and is scored once `ANTHROPIC_API_KEY` is in `.env`.

## References

Rand, J., Manderlink, N., Zhang, S., Talley, C., Gorman, W., Wiser, R., Seel, J.,
Mulvaney Kemp, J., Jeong, S., & Kahrl, F. (2025). *Queued up: 2025 edition —
Characteristics of power plants seeking transmission interconnection as of the
end of 2024.* Lawrence Berkeley National Laboratory. https://emp.lbl.gov/queues

U.S. Energy Information Administration. (2026). *Preliminary monthly electric
generator inventory (EIA-860M)* [Data set, accessed through the EIA API v2].
https://www.eia.gov/electricity/data/eia860m/
