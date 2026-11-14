# Revised Outline — Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation

SIADS 699, Group 13 (solo) · Alan Mössinger · Mentor: Laura Danielle Stagnaro · 13 November 2026

**Status: modelling finished and frozen, results scored, report in final editing, about 80% done.**

## What changed since the first outline

The structure changed twice, both times after review, and the current one is the one I am keeping. The first outline followed the proposal's paper order (introduction, data, methods, evaluation, results, discussion). That order tells a methods story; the reviews asked for a decision.

1. **Decision-first body, paper kept whole as an appendix.** The 3,000-word body opens with the recommendation (fund, defer, monitor, reject) and walks the committee's four questions; the full paper in the original order is Appendix K.
2. **A fourth question and a sixth stage.** The expert review of 19 October added the AI challenger as a question in its own right, tested in a registered experiment on 48 simulated committees.
3. **Financing became part of the answer.** The executive review of 23 October showed that the ranking of strategies depends on how construction calls are funded; notebook 13 finances every process the same way, and the recommendation became "the book and its $2.53B contingent facility".

Unchanged: the frozen LBNL 2025 file as the basis of every registered result, the pre-registered criteria and their verdicts, and the rule that no verdict is re-scored.

## 1. The problem and the question

Energy companies allocate one capital budget across investments that differ in return, market exposure, execution risk and downside. Forecasts and valuations rank these one at a time; they do not show that a set of individually attractive projects can carry a concentrated tail, an unplanned call on liquidity and one shared market exposure. The question is prescriptive: **given limited capital, uncertain markets, competing investments and stated risk preferences, which projects should a company fund, stage, defer or reject, and why?**

The case: on 1 January 2025 a company decides one budget of $3.82B across twenty producing Gulf of Mexico leases and twenty ERCOT interconnection requests, using only what was public that day, scored on 2,000 held-out scenarios against criteria registered before scoring. Four questions, each with a registered test and a section of the report: (1) are better predictions enough? (2) what happens when projects lose together? (3) what should the company actually fund? (4) can AI challenge a committee without replacing it?

## 2. Data (assembled, frozen, hashed)

All data are public: 111 raw files, each with its SHA-256 in a manifest. Three panels meet at the candidate level: the *queue panel* (LBNL *Queued Up* 2025 edition, frozen; the 2026 edition for the forward test; EIA-860M; ISO queue files) for which plants get built and when; the *energy panel* (BSEE lease production, EIA-923 generation, WTI, Henry Hub and ERCOT prices) for output and the price paths the scenarios resample; the *cost layer* (NREL ATB 2024, LBNL interconnection costs, IRS Notice 2025-42, EPA eGRID) behind every NPV, each value with a provenance label. Every feature is lagged by its release lag, a truncation test proves none uses post-origin data, and the candidate set uses only what was public on the decision date.

## 3. Method as built: six stages, thirteen notebooks

Six stages kept apart so each contribution is measured on its own; thirteen notebooks run end to end with one command and write every cited number to one results table that the test suite checks against the report and the poster.

| Stage | What it does | Notebooks |
| --- | --- | --- |
| 1. Prediction | Discrete-time competing-risks models for which requests get built and when, against a fair size lookup; lease, plant and price forecasts at rolling origins against five baselines | 01–05 |
| 2. Uncertainty | 2,000 joint scenarios of prices, output, costs and timing; block bootstrap in aligned calendar-year blocks so markets keep moving together; mean reversion; named stresses | 08 |
| 3. Prescription | Mixed-integer optimizer under budget and caps; objective expected NPV minus worst-5% average loss (CVaR); four books compared | 07, 09, 11 |
| 4. AI challenge | A language model reads the committee's reasons into rules and argues against the proposal from computed facts; no authority; every number checked by code | 10, 12 |
| 5. Human decision | Override gate and hash-chained ledger | 10, 11 |
| 6. Measured outcome | 41 pre-registered criteria, 87 lines, scored once; corrections beside the original | 06, 12, 13 |

## 4. Results so far (scored, in the report)

| Question | Finding |
| --- | --- |
| Risk-aware optimization vs ranking by NPV | Yes. The risk-aware book leads NPV ranking on the registered metric by +$219M [+$13M, +$401M], and by +$312M [+$110M, +$506M] once every process is financed the same way; it trades about $0.5B of expected value for half the tail and is best in 7 of 7 worlds |
| Better prediction, better decision? | No. The completion model ranks better than a size lookup (AUC 0.73 vs 0.69) but overstates completions (38% vs 24% at five years); the book built from its curves is no better than the lookup's |
| Where the AI adds value | In the argument, not the choice. Tools add +$76M per case, the model +$43M [+$9M, +$86M] on top; against an optimizer-first rule its edge disappears (−$14M [−$36M, +$2M]) |
| What to fund | Five leases and eight requests, $3.78B committed, plus a $2.53B contingent facility (calls exceed the reserve in 50% of scenarios). Defer 12, monitor 14, reject 1 |

Reported as they fell: 40 of 87 registered lines pass; 10 of 12 governance controls in place, 2 partly. All results are model-based on public data and assumed lease costs, not realized returns.

## 5. Final report: section-by-section outline

Twelve short sections for an investment committee inside 3,000 words; appendices carry the depth. Each section leads with its finding.

| Section | Says | Figure or table |
| --- | --- | --- |
| Abstract; Executive decision in one minute | The recommendation and what the committee must decide | Allocation table |
| 1. The problem: one budget, risks that move together | Why one-at-a-time ranking fails: co-movement | Shuffle test |
| 2. The decision and the questions it creates | The case, the forty candidates, the four questions | Candidate map |
| 3. The solution: six separated stages | The pipeline | Pipeline figure |
| 4. Are better predictions enough? | Model vs lookup; level drift; forward test | Forward test |
| 5. What happens when projects lose together? | Joint scenarios, block bootstrap, the tail term | Frontier over tail weights |
| 6. What should the company actually fund? | The risk-aware book, member by member | Five books' outcome distributions |
| 7. Four strategies and a forecast check | The metric under three funding bases; the facility priced | Process × funding bars; capital stack |
| 8. Can AI challenge a committee without replacing it? | The challenger's design and limits | Workflow figure |
| 9. What the challenger added, and where it failed | Five-arm ladder on 48 committees | Ladder with paired intervals |
| 10. What the registered evidence supports | 41 criteria, 87 lines, 40 pass | Ledger summary |
| 11. Limitations and the next decisions | Simulated committees, one price regime, assumed costs | Control matrix |
| 12. Conclusion | The book and its facility together | |
| Appendices A–M | Evaluation record; advisor; figures; the two parts in full; every verdict; the audit; memo; glossary; the paper in full (K); scenarios (L); the challenger's workflow (M) | |

## 6. Other deliverables

The **poster** (A1) is drawn from the report's numbers and passes the same number test. The second **stand-up video** was recorded on 12 November; the final demo video is next. The **repository** runs the thirteen notebooks with one command, with a pytest suite over the cleaning rules, the truncation proof, the optimizer, the challenger's grounding and every cited number; a clean Linux run reproduced 2,548 of 2,561 cited numbers. A **dashboard** replays the recorded decisions offline, and the **record** holds 131 numbered decisions, the registration ledger and the mentor-feedback table.

## 7. Remaining work to 14 December

| Week | Work | Course event |
| --- | --- | --- |
| 16–22 Nov | Body back to 3,000 words (now about 3,640): decide what moves to Appendix K. Per-criterion table (measure, baseline, threshold, verdict) into Appendix A. PDF re-exported | Revised outline, 23 Nov |
| 23–29 Nov | Final video scripted and recorded; poster refreshed | |
| 30 Nov – 6 Dec | Full pipeline run from a fresh clone; tests green; README checked; tag | |
| 7–13 Dec | Final read of report, poster and video together; last mentor comments | Due 14 Dec |

## 8. Open questions for the mentor

- **Length.** Does the 3,000-word body exclude the two-page executive decision? That determines what moves to Appendix K.
- **Simulated committees.** The 48 proposals are author-written with planted flaws. A real-committee study is presented as the next step, not this term's. Is that boundary stated strongly enough?
- **Registered vs added findings.** The financed comparison (+$312M) and the optimizer-first arm (−$14M) sit beside the registered lines (+$219M, +$43M), labelled as added after review. Is the distinction clear to a reader who did not follow the project?
