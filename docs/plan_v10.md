# Plan v10 — one simulated decision loop (proposed 2026-10-21, for Alan's approval)

Status: **proposed, nothing changed yet.** Alan asked for a simpler project that keeps the challenge and the
"reason my thinking" questions and runs simulations instead of the historical decision gym. This plan says what
v10 would be, what moves, what stays frozen, and what it costs in time before 14 December 2026.

## 1. The project in one sentence

A committee decides how to split one budget across forty energy projects on 1 January 2025; a simulation prices
every book; an AI challenger tests the committee's proposal against the committee's own rules and makes the
committee reason before it signs; the outcome is measured on held-out scenarios, against the same tools without
the language model.

## 2. The loop (every notebook and figure serves it)

| Step | What happens | Already built in |
|---|---|---|
| 1 Simulate | 2,000 joint paths of prices, output, cost and completion; a second 2,000 for scoring only. Completion from the lookup curves (the model's curves did not change the decision; they stay in the appendix). | `src/scenarios.py`, `src/whatif.py`, `src/valuation.py`, `src/portfolio.py` |
| 2 Propose | A committee states a book and its reasons in words. The risk-aware optimizer's book is the reference, not the answer. | `src/optimizer.py`, the personas in `src/challenge_experiments.py` |
| 3 Challenge | The language model reads the rules; tools diagnose the proposal, compute the repair and the optimizer's book under those rules; the model writes a memo; code checks every number and the guide rule. | `src/challenge.py`, `prompts/challenge_*.md` |
| 4 Reason | Before signing, the committee answers the five questions tied to its statement, reads the motivated-reasoning verdict and the opposing case. | `src/advisor.py` (`REASONING_QUESTIONS`, the challenge round), `prompts/motivated_reasoning_*.md`, `prompts/ideological_turing_test.md` |
| 5 Decide and score | A named person signs; a departure from a guided book needs the evidence acknowledged; the ledger records it; the held-out scenarios and five worlds score the book the committee ends with. | `src/ledger.py`, `src/challenge_experiments.py` (X2 worlds) |

## 3. What is simulated instead of replayed from history

The decision gym (sixteen past situations rebuilt as of their date) is retired from the core and kept in the
appendix. In its place, **simulated committee sessions** run the whole loop:

- **Sessions** = personas × flaws × worlds, as X1/X2 already do (48 cases, 5 worlds), extended with step 4.
- **Step 4 is scripted, not generated.** Each persona carries fixed answers to the five questions, written by me
  before the run — a sunk-cost persona answers question 4 ("which evidence was used and which dismissed") by
  citing the money already spent, and so on. The language model's verdict and opposing case are then tested on
  whether they change the book. Generated answers would let the model grade itself.
- **New cases, the ones v9 could not test:** proposals where *only the argument is wrong* — no computed rule
  broken, no fragile member — so that a changed book can come only from the reasoning round. Eight to twelve
  cases, two per reasoning flaw, keyed and registered before any call.
- **Control stays the checklist** (same tools, no language model), and for step 4 a second control: the five
  questions shown with no verdict and no opposing case.

## 4. What the report claims, and the registered lines it would need

Registered before any run (decision #100 when approved), in `results/v10/success_criteria_v10_registered.json`
with hashes of cases, scripted answers, prompts and model:

| Line | Claim | Rule |
|---|---|---|
| C33 | On the argument-only cases, the committee's book after step 4 beats its proposal on its own objective | case-bootstrap interval above zero |
| C34 | The reasoning round changes the book in argument-only cases more often than the questions alone | share with the verdict and opposing case > share with questions alone, binomial test p < 0.05 |
| C35 | The reasoning round does not change the book in clean cases | at most 1 of 12 |
| C36 | The memo's and the verdict's numbers are grounded | 90% of sessions fully grounded (the v9 rule of 80% failed by one memo; the new target is set knowing that) |

C25–C32 stay as scored in v9 (6 of 8 pass) and are reported, not re-run. H5–H7 keep their v9 verdicts.

## 5. What moves where

**Core (the report body, five notebooks):**

| New notebook | From | Keeps |
|---|---|---|
| 01 data and candidates | 01, 07 | the forty candidates, provenance, the two cost grids |
| 02 simulation | 08 | scenarios, held-out set, valuation per path |
| 03 the book | 09 | frontier, risk-aware vs NPV ranking under equal constraints, capital calls, re-selection |
| 04 challenge and reasoning | 10 §challenge, 11 §11, new | the loop end to end on one example, then the simulated sessions |
| 05 evaluation | 11 | the three books (NPV ranking, optimizer, committee after the loop), the registered lines, F46 and the new figure |

**Appendix (kept, run, cited, not in the story):** queue modelling (04, 06, Parts I of the report), the energy
forecast tournament (05), MISO and SPP, value of information, the 2027 revision, the decision gym, the advisor's
what-if scoring. Their notebooks are renumbered A1–A5 and still run with `make all`; their results stay cited by
`src/report_numbers.py`.

**Frozen and untouched:** `results/registered_v7/`, `results/v9/` (the registration, outputs and scores), every
registered verdict C1–C32. Nothing is re-scored.

**Deleted:** nothing. Code the core no longer imports stays in `src/` while the appendix notebooks use it.

## 6. The report

- Title unchanged. Core of about 3,500 words (the executive report's 4,500 limit stays; the simpler story needs
  less): executive summary, memo, the loop (one figure, F43 redrawn with "reason" as its own stage), the book,
  the challenge, the reasoning round, what is measured, limits, conclusion.
- Four figures in the core: the loop, the frontier, the challenger (F46), the reasoning round (new: the share of
  argument-only cases whose book changed, with and without the verdict, against the checklist).
- Appendix A keeps the whole registered record (C1–C36).

## 7. What this does not change

- The language model never computes a value and never decides. The human decides; the ledger records.
- The evidence standard: every number from code, registered criteria scored once, post-registration labelled.
- The committees are still simulated. The report says so in the first paragraph of the limits.

## 8. Cost and order (seven weeks to 14 December)

| Week | Work | Output |
|---|---|---|
| 1 | Write and register the argument-only cases and the scripted answers; wire step 4 into `challenge_experiments` (one function: `reason_round(advisor, persona, case, memo)`); the two controls | decision #100, `results/v10/` registration committed before any call |
| 2 | Run the sessions live (about 60 cases × 4 calls ≈ 2 hours); score C33–C36; figure | notebook 04/05 sections, `results/v10/` scored |
| 3 | Reorder the notebooks (core 01–05, appendix A1–A5), rerun end to end | `make all` green, 250+ tests |
| 4 | Report v10 (core and appendices), poster, Petrobras edition | PDFs |
| 5 | Clean Linux run, demo video, buffer | reproduction record |
| 6–7 | Alan's own sessions through the loop (the reserved slot), final read, tag | submission |

If week 1 slips, the fallback is the story-only simplification (reorder, rewrite, no new experiment): the
reasoning round is then governance, required before a signature and recorded, with no outcome claim.

## 9. Decisions Alan has to make (ASK ALAN)

1. Approve the loop as the project's story, with the gym and the queue modelling in the appendix.
2. Approve the new experiment (C33–C36) with scripted persona answers, or choose the fallback.
3. Completion curves in the core: the lookup (recommended: simpler, and the model did not change the decision) or
   the model.
4. Whether to renumber the notebooks (cleaner repository; every path in `docs/` and the tests changes) or keep
   the numbers and reorder only the report.
