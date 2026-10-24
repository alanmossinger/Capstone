# Prompt for the next session (written 2026-10-24, after session 24)

Paste everything below the line into a new Claude Code session opened in the repository root.

---

You are continuing my SIADS 699 capstone, "Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization"
(Queue Survival, Group 13, a solo project; final due 14 December 2026). I am Alan Mössinger, the sole author of every
file.

## Before anything else

1. Read `CLAUDE.md` (standing rules), `PLAN.md`, the **top section** of `HANDOFF.md` (session 24) and the last three
   entries of `docs/journal.md`. Skim decisions #105–#112 at the end of `docs/decisions.md`.
2. Check `git status` and `git log --oneline -8` on branch `v8-corrections`. Do not switch branches, stash or reset.
3. Run `python -m pytest -q` (expect 274 passed) and `python -m src.report_numbers` before changing anything.
4. Tell me in at most five bullets what you will do this session, then start. Stop only for items marked ASK ALAN.

## Where the project stands

- The decision: twenty Gulf lease redevelopments and twenty ERCOT interconnection requests under one budget on
  1 January 2025, built only from what was public that day (decision #105).
- Report v10 (`report/report.md`) answers four questions with one primary line each: Q1 prediction (the queue model
  ranks better than the lookup, AUC 0.731 against 0.686, and overstates the level: 78 operations expected in 2025,
  30 happened); Q2 optimization (C33: the risk-aware book beats NPV ranking by $219M [+13, +401] on the registered
  metric; its $2.53B construction line still pays at a bank's price); Q3 governance (C34: the language model adds
  $43M [+9, +86] per case to the tools); Q0 attribution (tools +$76M, model +$43M, optimizer +$134M).
- The registered v10 test (176 calls, `results/v10/`): 6 of 8 graded lines pass; C37 (silence read as a zero tail
  weight) and C39 (numbers not on the fact sheet) failed and are reported as they fell.
- The poster and the demo video script follow report v10. The clean Linux run is done (decision #112): every
  registered verdict and 2,548 of the 2,561 cited numbers reproduce exactly.

## What to do this session, in order

1. **Alan's read of report v10:** apply his corrections, keeping every number a key in `results/report_numbers.csv`.
2. **Push** `v8-corrections` and fast-forward `main` — only on Alan's word (ASK ALAN). Tag a release only on his word.
3. **Journal and decisions** for anything done; commit with no trailers.

## Rules that matter most here

- Never report a number that was not printed by running code; add keys in `src/report_numbers.py`, never type numbers.
- Never edit the registered records (`results/v10/success_criteria_v10_registered.json`, `results/v9/`,
  `results/registered_v7/`), the v10 cases, paraphrases and injections, or the prompts: they are hashed, and notebooks
  11 and 12 refuse a change. Never re-score a registered line; label post-registration work.
- Figures: `plots.finish` and `plots.save_fig`; titles state the finding in at most 12 words; 11 inches wide. Open
  every figure before calling it done.
- Writing: first person singular, plain, finding first; no criterion codes, decision numbers or file paths in the
  report body.
- Commit messages carry no trailers or attribution of any kind. No AI-use section. Never swap the frozen LBNL file.
  Never print a key.
- Run notebooks from **PowerShell** (Git Bash's `pdftotext` breaks notebook 07), in the order of
  `run_pipeline.PIPELINE` (01, 03, 02, …); anything longer than two minutes in the background with the machine awake.
- Do not claim the language model beats the optimizer or raises returns by a percentage.

## Open questions to put to me (ASK ALAN)

- Push now? Tag a release after my read?
- Should the decision page (`app/decide.py`) expose the challenger before the final submission?
