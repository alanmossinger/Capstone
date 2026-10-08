# Queue Survival — one command per pipeline step. `make all` rebuilds everything.

ifeq ($(OS),Windows_NT)
PYTHON := .venv/Scripts/python.exe
else
PYTHON := .venv/bin/python
endif

.PHONY: setup data clean explore features models evaluate explain v3 figures numbers report test all

setup:            ## create .venv, install pinned packages, register the notebook kernel
	python -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m ipykernel install --user --name queue-survival --display-name "Python 3.11 (queue-survival)"

data:             ## 01: get LBNL + EIA-860M, readiness gate
	$(PYTHON) run_pipeline.py --only 01

clean:            ## 02: cleaning rules R1–R9
	$(PYTHON) run_pipeline.py --only 02

explore:          ## 03: survival curves, F1 F2 F3 F8; 03b: project map F9
	$(PYTHON) run_pipeline.py --only 03 03b

features:         ## 04: events, Track A/B samples, entry-time features
	$(PYTHON) run_pipeline.py --only 04

models:           ## 05–07: Cox, discrete-time, all-regions models
	$(PYTHON) run_pipeline.py --only 05 06 07

evaluate:         ## 08: metrics, calibration, F4 F5; 08b: post-hoc improvements
	$(PYTHON) run_pipeline.py --only 08 08b

explain:          ## 09: forest plot, SHAP, ranking table, F6 F7
	$(PYTHON) run_pipeline.py --only 09

v3:               ## 01b, 11-20: the portfolio layer (fair baseline, level, milestones, landmarks, value, book, levers, verdict, MISO/SPP, managed book)
	$(PYTHON) run_pipeline.py --only 01b 11 12 13 14 15 16 17 18 19 20

figures:          ## every notebook that draws figures
	$(PYTHON) run_pipeline.py --only 01 03 03b 08 09 01b 11 12 13 14 15 16 17 18 19

numbers:          ## results/report_numbers.csv: every number the report cites, read from results/
	$(PYTHON) -m src.report_numbers

report: numbers   ## report.md + references.md + appendix.md → report/report.pdf (needs pandoc and typst)
	pandoc report/report.md report/references.md report/appendix.md -f markdown-implicit_figures --resource-path=report --pdf-engine=typst -o report/report.pdf

test:
	$(PYTHON) -m pytest

all:              ## notebooks 01 → 09 (with 03b and 08b), then 01b and 11 → 19, stop at the first error
	$(PYTHON) run_pipeline.py
