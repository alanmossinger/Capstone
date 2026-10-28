# Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation

*A governed decision-intelligence system for risk, returns and investment-committee decisions across oil, gas, power, renewables and storage*

SIADS 699 Capstone — Master of Applied Data Science, University of Michigan — Group 13 (solo project).
Author: **Alan Mössinger**. Mentor: Laura Danielle Stagnaro. October 2026.

## The deliverables

| Deliverable | Where |
|---|---|
| **The capstone report** (official) | [`report/Beyond_Prediction_Capstone_Report_Final.docx`](report/Beyond_Prediction_Capstone_Report_Final.docx) — abstract, nine sections, statement of work, appendices A–I; every number in it is checked against `results/report_numbers.csv` by `tests/test_report.py` |
| The report's Markdown source and the course-length edition | [`report/report.md`](report/report.md) (`make report`), [`report/report_course.md`](report/report_course.md) (`make report-course`, about 2,900 words) |
| The poster (A1, one page) | [`report/poster.pdf`](report/poster.pdf) from [`report/poster.typ`](report/poster.typ) (`make poster`) |
| The dashboard | `make app` — three pages: *Decide*, *A worked example*, *The report's decision* (see below) |
| The code | thirteen notebooks run in order by `make all`; the `src/` package; 283 tests (`make test`) |
| The proposal and its update | [`docs/SIADS699_Project_Proposal_Group13_2026-10-19.pdf`](docs/SIADS699_Project_Proposal_Group13_2026-10-19.pdf), [`docs/proposal_update_2026-10-19.md`](docs/proposal_update_2026-10-19.md) |
| The evaluation plan (2 November) | [`docs/SIADS699_Evaluation_Plan_Group13.pdf`](docs/SIADS699_Evaluation_Plan_Group13.pdf), [`docs/evaluation_plan.md`](docs/evaluation_plan.md) |
| Mentor feedback and my reply | [`docs/mentor_feedback.md`](docs/mentor_feedback.md) (every item, what changed, where), [`docs/mentor_reply_2026-10-27.md`](docs/mentor_reply_2026-10-27.md) |
| The demo video script | [`docs/demo_video_script.md`](docs/demo_video_script.md) |
| The record of the work | [`docs/decisions.md`](docs/decisions.md) (121 numbered decisions with reasons), [`docs/journal.md`](docs/journal.md) (dated log), [`docs/registration_ledger.md`](docs/registration_ledger.md) (every pre-registered line, its verdict as first scored, every correction); the index is [`docs/README.md`](docs/README.md) |

## The question

Energy companies allocate one capital budget across investments — oil and gas, conventional generation, renewables and storage — that differ in return, market exposure, execution risk and downside. Forecasts and project valuations rank these investments one at a time; they do not show that a set of individually attractive projects can carry a concentrated tail, an unplanned call on liquidity and an exposure to one adverse market. The question this project answers is prescriptive: **given limited capital, uncertain markets, competing investments and stated risk preferences, which projects should a company fund, stage, defer or reject — and why?**

The system runs in six stages, kept apart so that each one's contribution can be measured on its own: **prediction** (which interconnection requests get built and when; lease output, plant output and prices), **uncertainty** (2,000 joint scenarios of prices, output, costs and timing), **prescription** (a risk-aware optimizer choosing a book under a budget and caps), **AI challenge** (a language model that reads the committee's reasons into rules and argues against the proposal from computed facts, holding no authority), **human decision** (an override gate and a hash-chained ledger) and **measured outcome** (pre-registered criteria, scored once).

## The decision, and the answer

The case: on 1 January 2025 a company decides one budget of **$3.82B** across twenty producing Gulf of Mexico leases to redevelop and twenty ERCOT interconnection requests, built only from what was public that day, scored on 2,000 held-out scenarios against criteria registered before scoring.

- **Fund the risk-aware book** — five leases and eight requests, **$3.78B committed** ($1.42B of lease capital, $7M of deposits, a $2.35B construction reserve) — **together with a $2.53B contingent construction facility**, because construction calls exceed the reserve in 50% of scenarios. Defer the 12 waiting requests until their agreements are signed; monitor 14 leases; reject 1.
- On the registered risk-adjusted metric (expected NPV minus the average loss in the worst 5% of scenarios) the risk-aware book beats ranking by NPV by **+$219M [+$13M, +$401M]** as pre-registered, and by **+$312M [+$110M, +$506M]** once every decision process is financed the same way (+$213M [+$17M, +$412M] over the deterministic optimizer). It expects $2.17B with a $0.82B worst-5% average loss and a 9% chance of a loss ($1.98B and $0.95B financed), and it scores best in **7 of 7** modelled worlds. Without a facility, equal capital by sector would lead: the recommendation is the book *and* its facility.
- **Better prediction did not make a better decision.** At utility scale the completion model ties a size lookup at entry; the book chosen with the model's queue curves is not demonstrably better than the book chosen with the lookup's. The decision turns on a few large requests, on the capital plan and on the tail, not on the forecast.
- **The AI's value is in the argument, not the choice.** In a registered test on 48 simulated committee proposals, deterministic tools improve the committee's own decision by **+$76M** per case and the language-model challenger adds **+$43M [+$9M, +$86M]** more; against a fixed optimizer-first rule that reads no words the model's edge disappears (**−$14M [−$36M, +$2M]**). The model named 12 of 12 author-written flaws of argument and over-challenged 0 of 12 sound proposals; every number it writes is checked against its fact sheet by code.
- **Reported as they fell.** 28 of the 70 lines registered at proposal time pass; of the nine registered lines of the final experiment, two fail. No registered verdict was re-scored; corrections are added beside the original in the ledger. Of the 12 controls of the governance layer, 10 are in place and 2 partly (injection resistance, scenario realism). All results are model-based on public data and assumed lease costs, not realized returns.

## How the work is organized

Each notebook has the same shape: inputs and outputs, numbered sections, a *Reading this* cell under every table and figure, and takeaways that say what goes to the report. `make all` runs them in dependency order and writes every number the report cites to `results/`.

| Notebook | What it does |
|---|---|
| `01_problem_and_data` | the queue sources (LBNL *Queued Up* 2025 and 2026, EIA-860M, the ISO files), the energy sources (BSEE, EIA-923, prices, ERCOT, eGRID), cleaning rules R1–R13 with row counts, the manifest, the data-readiness gate |
| `02_eda` | survival curves, what drives withdrawal, the project map, state archetypes; the energy series |
| `03_statistics_and_features` | queue outcomes and entry-time features; leakage-safe features at rolling origins (the truncation proof); criterion C20 registered |
| `04_forecast_queue` | the completion-and-timing engine: discrete-time competing-risks models against the fair baseline and the size lookup, the level repair, the landmark models, MISO/SPP on the 2026 file |
| `05_forecast_energy` | lease output, plant capacity factors and three prices at rolling origins against five transparent baselines; C20 scored |
| `06_evaluation_record` | every registered criterion scored as registered (C1–C24), post-hoc and tournament, explanations, the decision board; runs after 09 |
| `07_economics` | the forty candidates' cash flows and NPV under the documented cost grid, with a provenance label on every value |
| `08_scenarios_and_risk` | joint price, output, cost and timing scenarios with mean reversion; named stresses; risk measures per candidate |
| `09_portfolio` | the four books under one budget (NPV ranking, equal capital, the deterministic and the risk-aware optimizer); C21–C24 |
| `10_advisor_and_gym` | the grounded language-model advisor, the challenge round and the override gate, the decision gym on sixteen past situations, the forward view at 1–20 years |
| `11_decision_system` | the decision system: the frontier over tail weights, what-ifs, value of information, staged decisions, the processes compared on held-out scenarios, the active challenger; the as-of candidates and the forward test |
| `12_three_questions` | the registered experiment on 48 simulated committees: the four-arm ladder (proposal → tools → tools + model → optimizer), paraphrases and injections, the credit line priced; C25–C41 |
| `13_executive_corrections` | the executive review answered: every process financed the same way, the co-movement dial and seven worlds, the optimizer-first rule as a fifth arm, the allocation line by line, the committee workflow and the control matrix, an emissions cap, and one executive's worked round through the decision page |

`src/` holds the functions the notebooks share, each module with a docstring that says what it does, why, what it reads and writes, and who uses it:

| Group | Modules |
|---|---|
| Data and cleaning | `get_lbnl`, `get_data`, `eia_api`, `ercot_api`, `ercot_gis`, `ercot_history`, `energy_data`, `iso_files`, `audit_queue`, `cleaning`, `linkage`, `geo`, `asof_candidates`, `decision_date` |
| Queue models and their evaluation | `events`, `features`, `discrete_time`, `survival_tools`, `baselines`, `benchmarks`, `drift`, `drivers`, `landmark`, `variants`, `track_b`, `explain`, `evaluation`, `posthoc`, `forward` |
| Energy forecasts | `decline`, `energy_features`, `energy_models`, `energy_stats` |
| Economics, scenarios and the book | `value`, `economics`, `valuation`, `scenarios`, `optimizer`, `portfolio`, `robustness`, `whatif`, `voi`, `dynamic`, `horizons` |
| The AI challenger and governance | `advisor`, `advisor_tools`, `challenge`, `challenge_experiments`, `challenge_v10`, `gym`, `ledger`, `registration_ledger`, `worked_example` |
| Plumbing | `paths`, `config`, `plots`, `report_numbers`, `report_course` |

**The dashboard** (`make app`, `app/`) reads `results/` only and recomputes no model. *Decide*: the options, your book and your reasons, the advisor's challenge with its five reasoning questions, your result against the advisor's solution. *A worked example*: one executive's recorded round through those steps, for a new reader. *The report's decision*: the recommendation on one screen in seven tabs, the last one the committee's own call. Challenging your own book needs a language-model key from any provider (see *How to run*); the recorded rounds replay without one, and the dashboard says so at the top.

**Tests** (`tests/`, pytest): the audit, the cleaning rules, the features and the truncation proof, the metrics and baselines, the economics identities, the scenarios, the optimizer's constraints, the advisor's grounding and replay, the gym, the ledger's gate, the challenger, the dashboard pages headless, and that every number in the report, the poster and the course edition is in `results/report_numbers.csv`.

## Data

| Source | What | Access |
|---|---|---|
| LBNL *Queued Up: 2025 Edition* project file (frozen) | 36,441 interconnection requests through end-2024 — the basis of every registered result | download by hand from <https://emp.lbl.gov/queues>; not redistributed |
| LBNL *Queued Up: 2026 Edition* project file (alongside) | 38,201 requests through end-2025: reconciliation, the forward test, MISO/SPP dates | same page; CC BY 4.0 |
| EIA-860M via the EIA API v2 | inventory of operable U.S. generators (operating month, location) | free API key in `.env` |
| CAISO public queue report (via `gridstatus`) | cluster, study-phase and agreement status of CAISO requests | `data/raw/iso/` |
| PJM queue export and ERCOT GIS reports | PJM request, exit and status fields; ERCOT phase dates and the 2024 reports the candidates are built from | fetched from pjm.com and ercot.com; `data/raw/iso/`, not redistributed |
| BSEE OGOR-A, EIA-923, EIA and ERCOT prices, NREL ATB 2024, EPA eGRID | lease production, plant generation, the market months, the cost and emissions layer | `data/raw/`; every file listed with its hash in `data/raw_manifest.csv` |
| EIA wholesale prices, PJM market-monitor report, LBNL PJM cost data, IRS Notice 2025-42, Census boundaries | the value and cost layer and the map | `data/raw/value/`, `data/raw/lbnl_costs/`, `data/raw/geo/` |

The full data access statement, terms and data dictionary are in [`data/README.md`](data/README.md).

## How to run

Requires Python 3.11, GNU make and poppler's `pdftotext` on the PATH (notebook 07 reads two tables of the
PJM market monitor's report from its PDF; `pdftotext -v` must report a poppler version — the `pdftotext` that Git for
Windows ships is xpdf's and lays the table out differently, so put poppler's directory first on the PATH). On Linux
LightGBM also needs the OpenMP runtime (`libgomp1`).

```bash
make setup     # .venv, pinned packages, Jupyter kernel "queue-survival"
```

1. Get the raw files. `data/raw/` is not in the repository (the LBNL file carries no redistribution grant);
   `data/raw_manifest.csv` lists all 111 files it must hold, each with its source and SHA-256. With the author's bundle
   (`raw_data_bundle.zip`, 137 MB, available on request), unzip it into the repository root and run `make check-data`,
   which must end with "111 of 111 raw files present with the recorded hash". Without the bundle, `make get-data`
   downloads every file a script can fetch and prints, for each file it cannot, the route in [`data/README.md`](data/README.md).
   A file whose hash differs from the manifest is reported, never used silently.
2. Copy `.env.example` to `.env`. The EIA key is needed only to pull a missing EIA file again. For a live call to the
   advisor add a language-model key from any provider — `ANTHROPIC_API_KEY`, or `LLM_API_KEY` with `LLM_BASE_URL` and
   `LLM_MODEL` for any OpenAI-compatible service (OpenAI, Gemini, Mistral, a local server) — or sign in to the `claude`
   command line; with none, the advisor replays its record (`results/advisor_runs.jsonl`), so `make all` runs offline.
   The replay is keyed on the exact prompt text; on another platform, floating-point differences in the last decimals of
   a table can miss the record for a few calls (decision #111). A clean Linux run from the bundle reproduced 2,548 of
   the 2,561 numbers the report cites exactly as printed and every registered verdict (decision #112).
3. Run:

```bash
make all       # notebooks 01 → 13 in dependency order (03 before 02; 06, the record, after 09), stopping at the first error
make test      # pytest, 283 tests
make report    # report/report.pdf and report/report.docx from report/report.md + references.md (needs pandoc and typst)
make report-course  # the course-length edition: report/report_course.pdf and .docx
make poster    # report/poster.pdf from report/poster.typ (needs typst)
make app       # the dashboard at http://localhost:8501
```

Each notebook also has its own target (`make data`, `make eda`, …, `make corrections`; see the `Makefile`);
`python run_pipeline.py --only 04` runs one notebook. `python -m src.advisor` challenges your own decision at the
keyboard.

## Map of the repository

```
notebooks/   01 → 13, run in order by make all; each made of numbered sections with a Reading-this cell under every result
src/         the shared functions, grouped above; src/config.py holds every constant with a comment, src/paths.py every path
app/         app.py (make app) → decide.py, example.py, executive.py; reads results/ only
prompts/     the advisor's system prompt and every prompt template it is given, verbatim
data/        raw/ (not committed; the manifest lists it) · interim/ (not committed, rebuilt) · processed/ (small final tables) · README.md
results/     every number the report cites, written by the notebooks; report_numbers.csv keys them; v8/, v9/, v10/, v2/ the registered records
figures/     every figure, PNG + SVG; figures/<notebook>/ holds each notebook's exploratory figures; figures/executive/ the report's
report/      the official Word report; report.md, references.md, report_course.md, poster.typ; figure_notes.md (captions from the notebooks)
docs/        the course submissions, the mentor exchange, the record of decisions and the reviews the report cites; docs/README.md indexes them
tests/       pytest
```

## Statement of work

All components of this project — data engineering, modeling, evaluation, visualization and writing — were carried
out by Alan Mössinger. Code adapted from an external source is credited in-line where it appears. The ERCOT price
client and the battery dispatch model are reused, with credit, from the author's own earlier projects (*Forecast to
Dispatch*; MADS Milestone II).

## References

Rand, J., Manderlink, N., Zhang, S., Talley, C., Gorman, W., Wiser, R., Seel, J., Mulvaney Kemp, J., Jeong, S., &
Kahrl, F. (2025). *Queued up: 2025 edition — Characteristics of power plants seeking transmission interconnection as
of the end of 2024.* Lawrence Berkeley National Laboratory. https://emp.lbl.gov/queues

U.S. Energy Information Administration. (2026). *Preliminary monthly electric generator inventory (EIA-860M)* [Data
set, accessed through the EIA API v2]. https://www.eia.gov/electricity/data/eia860m/

The full reference list is in [`report/references.md`](report/references.md) and in the report.
