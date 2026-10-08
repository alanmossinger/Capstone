# Review of report v2 — read as a sceptical mentor would (2026-10-08)

Scope: `report/report.md`, notebooks 11, 14, 16 and 20 and their result
tables. For each of the report's six questions: what is proven, what is
partial, what is unsupported, and the one change that would most
strengthen it. Every judgement carries the number behind it.

A note on order: the plan was to write this before building notebook 20.
It was written after notebook 20 had been registered and scored, so it
can judge that result too. The registration was committed before scoring
(decision #58), so the order of this review did not shape the test.

## Q1 — How well can data science predict which requests get built, and when? (section 3)

- **Proven.** On the whole test cohort the v1 model beats the region ×
  technology average (8 of 12 registered lines, Uno's C +0.121 at 3
  years). On requests of 20 MW and more it does **not** beat a region ×
  technology × size lookup: 0 of 6 comparisons, Uno's C 0.779 against
  0.783 at 3 years and 0.734 against 0.752 at 5 (C6 fails).
- **Partial.** The gain under 20 MW (Uno's C 0.773 against 0.729) holds,
  but that segment is 19% of requests and 1.1% of MW. The report is right
  not to lead with it.
- **Unsupported.** Any statement that the model's *level* can be trusted.
  Five-year completion fell from 11.0% to 5.9% between the 2017 and 2018
  cohorts while the model stayed near 12%. The rolling repair closes about
  40% of the gap, and C7 fails.
- **Strongest change.** Stop reporting entry-time discrimination against
  the v1 baseline in the headline numbers. The fair baseline is the
  honest comparator, and the abstract already says so. The remaining v1
  phrasing in section 3.2 should say once that the 8 of 12 compare with a
  baseline that ignores size.

## Q2 — Each request's probability, and why (section 4)

- **Proven.** Two years in, the dated agreement flag lifts Uno's C from
  0.687 to 0.797 (+0.101 [+0.062, +0.136]); C8 passes. The leakage guard
  holds (highest landmark AUC 0.972 against the ablation's 0.990).
- **Partial.** The gain is ERCOT's and CAISO's. In the +2 pool, 111 of the
  118 requests with a known agreement are in ERCOT and none is in PJM, so
  for 59% of the cohort the landmark model is the entry model. Notebook 13
  now shows that PJM's own export does not change this: it dates no study
  and no agreement (decision #57).
- **Unsupported.** "Why" at the milestone. SHAP explanations exist for
  the entry model only. The landmark model's ranking *within* the
  agreement group drives the notebook 20 result, and nothing explains it
  yet.
- **Strongest change.** Explain the landmark model inside the
  agreement-known group: which features order the 118 agreed requests.
  That is where the stronger thesis lives.

## Q3 — What should a request have different, and what are the constraints? (section 5)

- **Proven.** The descriptive constraint map: PJM entrants' queue grew
  from 107 GW (2012) to 238 GW (2021) while 3-year withdrawals fell from
  56% to 16%; requests wait rather than leave.
- **Partial.** The what-ifs are model statements, not effects. Cutting to
  19.9 MW gives +3.0 points and adding storage +3.5, but the report's own
  sanity check finds that hybrids lag solar in the raw data.
- **Unsupported.** The congestion what-if (−0.7 points) carries the
  artefact's wrong sign. It should not appear as advice anywhere, and the
  report says so.
- **Strongest change.** Drop the congestion what-if from the table the
  reader sees, and keep it only in the artefact discussion.

## Q4 — Reducing the constraints: levers by actor (section 6)

- **Proven.** The ISO lever with a number behind it: the early-year
  operation hazard fell from 9.1% (2013 entrants) to 2.3% (2018–2019)
  while withdrawals barely moved.
- **Partial.** Six of ten levers carry a number, and the sizing lever is
  the best measured (41.8% against 7.4% across ERCOT size) and the least
  causal.
- **Unsupported.** The policy and reform levers are scenarios with stated
  multipliers (decision #56), not estimates; the report labels them.
- **Strongest change.** Tie each lever to the actor's decision and the
  registered evidence. "Gate on the executed agreement, then rank with the
  model" is now the one lever with a registered test behind it (C15).

## Q5 — The right book per region (section 7)

- **Proven, new.** At the two-year milestone, the model-managed book
  holds more requests that reach operation than a lookup that knows the
  agreement status: 19 against 11 in a book of 25 (+8 [+1, +11]) and 33
  against 24 in a book of 50 (+9 [+0.98, +13]). It also beats the
  unchanged entry ranking: +11 and +14. C15 passes on all four lines.
- **Partial.** The book-of-50 interval clears zero by less than one
  request. That is the narrowest pass in the project, and it should be
  described that way every time it is cited. The result is one cohort
  window (2017–2019 entrants), pre-Order No. 2023, and ERCOT-weighted.
- **Unsupported.** Any claim about megawatts. The lookup's books realised
  more MW (1,681 against 1,078 in a book of 25; −604 [−2,196, +155]), and
  C16 fails on all four lines. The entry-time backtest (C9, C10) is a tie,
  and the exploratory count-limited book at entry favours the lookup
  (13 against 7 operations).
- **Strongest change.** A registered MW-aware objective at the milestone,
  for example expected MW under a count limit, would show whether the
  model's ranking can be turned into megawatts without chasing size.

## Q6 — What an energy company should do with this (section 8)

- **Proven.** The decision rule's first two parts: use the lookup at
  entry, then gate on the agreement and rank with the model at the
  milestone.
- **Partial.** "Repair the level before sizing a book" is right but has no
  working method. The rolling repair at entry fails (C7), and the new
  repair at the landmark moves the intercept the wrong way (−0.29 to
  −0.44; C17 fails), because the 2019 cohort's early completions (30
  against 14.3 predicted in year one) did not foretell its later rate.
- **Unsupported.** Any dollar statement about a book's worth. The value
  index has no discounting, an assumed CAISO capacity price and ERCOT
  prices extended after 2019.
- **Strongest change.** State the level as a range a lender can use: the
  observed post-2020 two-year rates (1.1%, 0.3%, 0.7%) against predicted
  (4.3%, 3.4%, 3.6%). Do not offer a point repair.

## What the report must not do

- Call the managed-book result "robust" or "significant" in MW, or
  anywhere for PJM.
- Drop the failed lines. The verdict is 4 of 10, with the thesis rule met
  on its own registered terms.
- Present the exploratory entry book as evidence for or against C9–C10.
