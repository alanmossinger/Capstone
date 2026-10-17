# Demo video script — Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization (about 4 minutes)

Spoken text in plain type; what is on screen in *italics*. About 560 spoken words at roughly 140 words a
minute. Every number below is one the report prints from `results/`; if a rerun changes a number, change it here
from the report, never from memory.

## 0:00–0:30 — The decision

*Report Figure 1 (F0, the project in one picture).*

An energy company has one budget and two kinds of choice. It holds requests to connect new power plants to the
grid, and most of those requests are never built. It also holds oil and gas leases that already produce. This
project goes one step past prediction: it asks what the company should do — which projects, how much capital,
what risk to accept — and whether that recommendation beats the conventional ways of deciding. Predict,
quantify, prescribe, evaluate. Every answer is scored on what actually happened.

## 0:30–1:30 — Part I: which queue requests get built

*Appendix Figure E2 (F1, operation and withdrawal by region), then Figure E4 (F12, the landmark gain).*

Part I uses 13,366 requests in CAISO, ERCOT and PJM. ERCOT is where requests get built: about one entrant in
five operates within five years, against one in twenty in CAISO.

At entry, a gradient-boosted hazard model ranks requests better than cohort averages, but no better than a careful
lookup by region, technology and size. Two years in, with the executed agreement known, the model earns its keep.

*Appendix Figure E9 (F18, the managed book).*

A book of 25 requests chosen by the landmark model held 19 that reached operation, against 11 for the lookup.
The lesson for a developer: do not pay for prediction at entry; re-score at the milestone.

## 1:30–2:45 — Part II: one budget across leases and power

*Appendix Figure F2 (F28, the forty candidates), then Figure 4 (F37, the committee grid).*

Part II places twenty Gulf of Mexico lease redevelopments and twenty ERCOT requests under one budget and 2,000
joint price scenarios. Under the registered cost assumptions the leases are worth $14.6 billion and carry the
book.

Those assumptions turned out to be generous, so I added a committee grid after the registered results, and I
label it as post-hoc work. It charges capital per incremental barrel and discounts at 8%. The lease book halves
to $7.0 billion, and its tail becomes a real loss.

*Table 7, the four books under the committee grid.*

Under that grid the risk-aware book holds ten leases, four contracted wind requests and one gas request. It
expects $8.1 billion and halves the worst-5% loss, to $2.7 billion. Ranking by expected NPV expects more,
$11.5 billion, with twice the tail. Which to fund is a choice about risk appetite, and the memo says so.

## 2:45–3:30 — Did the rules beat instinct?

*Figure 5 (F34, the decision gym).*

The decision gym rebuilds sixteen past situations as of their date and reveals what happened afterwards. The
registered rules beat instinct by $236 million a situation, almost all of it in the three oil-price regimes.
Registered criteria were written before scoring, and where they failed, the report says they failed: all four
allocation criteria fail under the registered grid.

## 3:30–4:00 — The AI advisor, and what I would tell a committee

*Appendix Figure B1 (F36, the advisor's workflow).*

An LLM advisor reads only the result tables. It must cite a table for every number, it argues the opposing book,
and a human can override it only after answering five questions about their reasoning. Its live scoring is the
one step still open.

*Back to the memo page.*

The takeaway: prediction is necessary but not sufficient. The decision is made by the assumptions, the timing and
the tail, and this project puts each of them next to the number it moves.

## Recording notes

- Record the screen at 1920 × 1080 from the PDF (`report/report.pdf`), zoomed to one figure at a time.
- If the advisor has been scored by the time of recording, replace the first sentence of 3:30 with its measured
  grounding rate and agreement with book D from `results/advisor_evaluation.csv`.
- Do not show the dashboard.
