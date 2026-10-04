# Queue Survival — one command per pipeline step. `make all` rebuilds everything.

ifeq ($(OS),Windows_NT)
PYTHON := .venv/Scripts/python.exe
else
PYTHON := .venv/bin/python
endif

.PHONY: setup data clean explore features models evaluate explain figures report test all

setup:            ## create .venv, install pinned packages, register the notebook kernel
	python -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m ipykernel install --user --name queue-survival --display-name "Python 3.11 (queue-survival)"

data:             ## 01: get LBNL + EIA-860M, readiness gate
	$(PYTHON) run_pipeline.py --only 01

clean:            ## 02: cleaning rules R1–R9
	$(PYTHON) run_pipeline.py --only 02

explore:          ## 03: survival curves, F1 F2 F3 F8
	$(PYTHON) run_pipeline.py --only 03

features:         ## 04: events, Track A/B samples, entry-time features
	$(PYTHON) run_pipeline.py --only 04

models:           ## 05–07: Cox, discrete-time, all-regions models
	$(PYTHON) run_pipeline.py --only 05 06 07

evaluate:         ## 08: metrics, calibration, F4 F5
	$(PYTHON) run_pipeline.py --only 08

explain:          ## 09: forest plot, SHAP, ranking table, F6 F7
	$(PYTHON) run_pipeline.py --only 09

figures:          ## every notebook that draws figures
	$(PYTHON) run_pipeline.py --only 01 03 08 09

report:           ## report/report.md → report/report.pdf (needs pandoc)
	pandoc report/report.md --citeproc -o report/report.pdf

test:
	$(PYTHON) -m pytest

all:              ## notebooks 01 → 09 in order, stop at the first error
	$(PYTHON) run_pipeline.py
