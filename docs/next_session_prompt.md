# Prompt for the next session (written 2026-10-20, after session 19)

Paste everything below the line into a new Claude Code session opened in the repository root.

---

You are continuing my SIADS 699 capstone, "Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization"
(Queue Survival, Group 13, a solo project; final due 14 December 2026). I am Alan Mössinger, the sole author of every
file.

## Before anything else

1. Read `CLAUDE.md` (standing rules), `PLAN.md`, the **top section** of `HANDOFF.md` (session 19) and the last three
   entries of `docs/journal.md`. Skim decisions #93–#98 at the end of `docs/decisions.md`.
2. Check `git status` and `git log --oneline -8` on branch `v8-corrections`. Do not switch branches, stash or reset.
3. Run `python -m pytest -q` (expect 250 passed) and `python -m src.report_numbers` before changing anything.
4. Tell me in at most five bullets what you will do this session, then start. Stop only for items marked ASK ALAN.

## Where the project stands

- The decision: twenty Gulf lease redevelopments and twenty ERCOT interconnection requests under one budget on
  1 January 2025, using only what was public that day.
- A risk-aware MILP (expected NPV − λ·CVaR95, 40% technology cap, two-stage budget) beats NPV ranking by $320M on
  the registered metric. Its capital plan needs a contingent construction line of $3.28B. Machine-learning queue
  forecasts do not demonstrably improve the decision.
- An **active challenger** (`src/challenge.py`) reads the committee's rules from its words, diagnoses its proposal
  with computed tools, computes a repair and the optimizer's book under those rules, and writes a memo whose numbers
  are checked.
- In a **registered** test on 48 simulated committee cases (`results/v9/`, notebook 11 section 11), 6 of 8 lines pass:
  - Following the challenger improves the committee's own objective by $192M per flawed case and avoids $240M of
    worst-5% loss.
  - A checklist with the same tools and no language model gets $145M and $257M.
  - The language model's own contribution is understanding: it names 11 of 12 flaws of argument (the checklist 0)
    and reads 40 of 40 rules.
  - It over-challenged 2 of 12 sound cases (C27 FAIL), and C28 fails by one memo.
- I chose to report the case-design limit as it is.
- Report v9 (`report/report.md`) is the executive version: core 4,223 words, limit 4,500.

## What to do this session, in order

Phase 5 is done (decision #99): the poster and the Petrobras edition describe v9 and are tested against the live
numbers table, the README and `docs/v8_status.md` describe v9, and `main` was fast-forwarded to `v8-corrections` and
pushed on 2026-10-21. What remains:

1. **A clean-environment run of v9** (Linux, Python 3.11, `requirements.txt`, `make setup`, `make all`, `pytest`), as
   decision #87 did for v6: report which cited numbers, if any, differ, and why. Notebook 11 replays every advisor call
   from `results/advisor_runs.jsonl`, so it needs no API key. WSL Ubuntu is on this machine but lacks Python 3.11 and
   poppler, and `sudo` needs my password: ASK ALAN to run
   `sudo apt install -y python3.11 python3.11-venv poppler-utils` (via the deadsnakes PPA if 3.11 is not in the
   release), then clone the repository inside the Linux file system, copy `data/raw/` and `.env` across, and run there.
2. **`docs/demo_video_script.md`** was rewritten for v10 on 2026-10-23 (about 4½ minutes): record from `report/report.pdf` when
   Alan is ready; nothing to do unless a number changes.
3. **The decision page** (`app/decide.py`, `make decide-page`): ASK ALAN whether to expose the challenger (statement in,
   rules read back, memo and alternatives out) before the final submission; if yes, build it on `src/challenge.py`
   with replay, and test it headless.
4. **Journal and decisions** for anything done; commit with no trailers; push the branch you worked on. ASK ALAN
   before tagging.

## Rules that matter most here

- Never report a number that was not printed by running code. Every number in the report, poster and Petrobras
  edition must be a key in `results/report_numbers.csv`; add keys in `src/report_numbers.py`, never type numbers by
  hand.
- Never edit `results/v9/success_criteria_v9_registered.json`, `src/challenge_experiments.py`'s CASES and
  STATEMENTS, or `prompts/challenge_read.md` and `prompts/challenge_memo.md`. They are hashed in the registration,
  and notebook 11 refuses to run if any of them changes.
- Never re-score a registered line. Label post-registration work.
- Figures: `plots.finish` and `plots.save_fig`; titles state the finding in at most 12 words; 11 inches wide. Open
  every figure and look at it before calling it done.
- Writing: first person singular, plain, finding first; no criterion codes, decision numbers or file paths in the
  report body.
- Commit messages carry no trailers or attribution of any kind. No AI-use section. Never swap the frozen LBNL file.
  Never print the EIA key.
- Run notebooks from **PowerShell**: Git Bash's `pdftotext` breaks notebook 07. Run anything longer than about two
  minutes in the background and keep the machine awake.
- Do not claim the language model beats the optimizer or raises returns by a percentage. The evidence is that the
  challenged decision beats the committee's proposal, mostly through the tools, and that the language model's own
  part is reading rules and arguments.

## Open questions to put to me (ASK ALAN)

- Tag the release (v2.0) once the clean-environment run passes?
- When will I write my own decision cases for the reserved slot of the challenger's registration?
- Should the decision page (`app/decide.py`) expose the challenger before the final submission?
