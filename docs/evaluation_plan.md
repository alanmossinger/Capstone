*Evaluation plan — Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization (Group 13, Alan Mössinger)*
_Section 3 of the report, "How the work is evaluated". Every number is in `results/report_numbers.csv`._

*1. What I measure, and what I compare against*
Each claim has a metric and a baseline a careful analyst could build without my models. Every criterion was written and committed before the data it scores were seen. Of 70 registered lines, 28 pass; failures are reported as registered and never re-scored.
• *Completion and timing (RQ1).* Uno's C, time-dependent AUC and Brier score at 3, 5 and 7 years, and calibration by entry cohort, against the cohort average and the *lookup* — the share built among earlier requests in the same region × technology × size cell. The lookup is the comparison that matters: at 20 MW and above the model ties it at entry (Uno's C 0.78 for both), so the claim moves to two years in, where the landmark model with the agreement flag reaches 0.80 against 0.59.
• *Output forecasts (RQ1).* The challenger's error against the best of five transparent baselines (last value, seasonal naive, Arps decline, technology-month median, random walk), with paired moving-block bootstrap intervals. An ablation swaps naive forecasts into the optimizer and asks whether the book changes.
• *The prescription (RQ2–RQ3).* Four books under one budget — A top-N NPV, B equal capital by sector, C maximum expected NPV, D expected NPV minus the worst-5% average loss — scored on held-out scenarios by that metric, by stability under six stresses (Jaccard), and by the tail against a single-sector book.
• *Decisions (RQ4).* A decision gym of 16 past situations rebuilt as of their date: instinct, the registered rule, an AI advisor and the human each pick a book and are scored on realized value against hindsight. The advisor is also scored on grounding, the share of the numbers it writes that its tables hold.
• *Changes since the proposal.* On Oct 12 the scope widened from queue requests to one budget across Gulf of Mexico leases and ERCOT power (criteria C20–C24, the gym). On Oct 17 the framing changed to make the prescriptive step the contribution; the criteria and verdicts are unchanged.

*2. What I evaluate on, and how it stays separate*
• *Queue:* fitted on entrants through 2016, tested once on 2017–2019 entrants with outcomes through 2024. The 2026 LBNL file adds MISO, SPP and the post-2020 cohorts as out-of-time checks.
• *Forecasts:* rolling origins; the challenger is named on validation before scoring; a truncation test proves no feature uses data after its origin.
• *Books:* chosen on 2,000 primary scenario paths, scored on a second draw of 2,000 with its own seed.
• *Gym:* each situation shows only what was known on its date.
• *Pre-registration:* each criteria file is committed before the notebook that scores it runs; verdicts are never edited.

*3. How I could fool myself, and what I do about it*
• *A weak baseline.* Against cohort averages the model looks strong (AUC 0.86 against 0.73); against the lookup at utility scale it wins none of six comparisons at entry. I lead with the lookup.
• *Post-entry leakage.* Agreement dates and study phase are known only after entry; they enter only the landmark model, and a registered criterion checks the entry model.
• *Level drift.* Every cohort since 2017 completes below the model's level: the 2017–2019 cohort brought 18.8 GW online of the 29.2 GW expected. Ranking metrics hide this, so I report calibration by cohort and size books to the newest cohort.
• *Rescoring until it passes.* When observed ERCOT prices replaced a bridge from PJM prices, verdicts moved. The first scoring is kept beside the second, and post-scoring work is labelled.
• *Assumptions doing the work.* Lease costs are assumptions, so every book is shown under the registered grid, fixed before any result, and the harder committee grid. Under the registered grid book D does not beat book A; under the committee grid it cuts the worst-5% loss from $1.3B to $0.3B for $1.9B of expected value — a policy choice, not a statistical win.
• *Machine learning that does not matter.* With naive forecasts the risk-aware book is unchanged (overlap 1.00), so I do not credit the allocation to machine learning.
• *Grading an LLM on its prose.* The advisor is scored on checked numbers and gym outcomes, every call recorded and replayable offline. It mostly agrees with the rule, so its edge over instinct is not claimed for the AI alone.
• *Thin evidence.* In 6 of the 13 queue rooms nothing operated, and the gym's edge comes mostly from the three lease regimes. I say so.
• *Regime change.* Every queue outcome predates FERC Order No. 2023's cluster studies, and the ERCOT history holds one Winter Storm Uri. The results describe that regime.
