# Queue Survival — one command per pipeline step. `make all` rebuilds everything.

ifeq ($(OS),Windows_NT)
PYTHON := .venv/Scripts/python.exe
else
PYTHON := .venv/bin/python
endif

.PHONY: setup data eda features forecast energy economics scenarios portfolio record advisor decide figures numbers report poster petrobras app challenge decide-page test all

setup:            ## create .venv, install pinned packages, register the notebook kernel
	python -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m ipykernel install --user --name queue-survival --display-name "Python 3.11 (queue-survival)"

data:             ## 01: sources, cleaning rules R1–R9, the 2026 edition, readiness gates
	$(PYTHON) run_pipeline.py --only 01

eda:              ## 02: survival curves, drivers, map, archetypes (F1–F3, F8, F9, F19, F20, F25)
	$(PYTHON) run_pipeline.py --only 02

features:         ## 03: outcomes, Track A/B samples, entry-time features
	$(PYTHON) run_pipeline.py --only 03

forecast:         ## 04: entry models, fair baseline, entry rules, level repair, ablation, milestones, landmarks, MISO/SPP
	$(PYTHON) run_pipeline.py --only 04

energy:           ## 05: production, generation and price forecasts (v5)
	$(PYTHON) run_pipeline.py --only 05

economics:        ## 07: value, cost, project NPV, candidates
	$(PYTHON) run_pipeline.py --only 07

scenarios:        ## 08: joint scenarios, stresses, risk (v5)
	$(PYTHON) run_pipeline.py --only 08

portfolio:        ## 09: scorecards, books, gates, levers, managed book, MILP (v5)
	$(PYTHON) run_pipeline.py --only 09

record:           ## 06: every registered criterion scored, explanation, decision board — runs after 09
	$(PYTHON) run_pipeline.py --only 06

advisor:          ## 10: the LLM advisor and the decision gym (v5; replay mode runs offline)
	$(PYTHON) run_pipeline.py --only 10

decide:           ## 11: the decision system of v8 — frontier, what-ifs, explanations, value of information, staged decisions, processes compared, the advisor with tools
	$(PYTHON) run_pipeline.py --only 11

figures:          ## every notebook that draws figures, in pipeline order
	$(PYTHON) run_pipeline.py --only 01 02 04 05 07 08 09 06 10 11

numbers:          ## results/report_numbers.csv: every number the report cites, read from results/
	$(PYTHON) -m src.report_numbers

report: numbers   ## report.md + references.md → report/report.pdf and report/report.docx (needs pandoc and typst)
	sed 's/\.png)/.svg)/' report/report.md > report/report_vector.md  # the PDF embeds the vector SVGs: sharp at any zoom
	pandoc report/report_vector.md report/references.md -f markdown-implicit_figures --resource-path=report --include-in-header=report/typst_header.typ --pdf-engine=typst -o report/report.pdf
	rm report/report_vector.md
	pandoc report/report.md report/references.md -f markdown-implicit_figures --resource-path=report -o report/report.docx

poster:           ## report/poster.pdf from report/poster.typ (needs typst)
	typst compile --root . report/poster.typ report/poster.pdf

petrobras:        ## report/Petrobras_Report.pdf, the executive edition, from report/petrobras_report.typ (needs typst)
	typst compile --root . report/petrobras_report.typ report/Petrobras_Report.pdf

app:              ## the Streamlit dashboard (reads results/ only)
	$(PYTHON) -m streamlit run app/app.py

challenge:        ## the challenge round as one page: state the book, answer the five questions, read the verdict (app/challenge.py)
	$(PYTHON) -m streamlit run app/challenge.py

decide-page:      ## the v8 decision page: alternatives, your book, the models' answers, a decision through the gated ledger (app/decide.py)
	$(PYTHON) -m streamlit run app/decide.py

test:
	$(PYTHON) -m pytest

all:              ## notebooks 01 → 11 in dependency order (06 after 09), stop at the first error
	$(PYTHON) run_pipeline.py
