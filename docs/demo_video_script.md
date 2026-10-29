# Demo video script — Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization (about 4½ minutes)

Spoken text in plain type; what is on screen in *italics*. About 600 spoken words at roughly 140 words a
minute. Figure and table numbers are those of the official report's body
(`report/Beyond_Prediction_Capstone_Report_Final.docx`, decision #124); every number below is one it prints from `results/`
(keyed in `results/report_numbers.csv`); if a rerun changes a number, change it here from the report, never from memory.

## 0:00–0:45 — The decision

*Report title page, then Figure 1 (F43, the decision workflow in six stages).*

An energy company has one budget on the first of January 2025, and forty places to put it: twenty oil and gas
leases in the Gulf of Mexico that already produce, and twenty requests to connect new power plants to the Texas
grid — most of which are never built. I use only what was public that day. I ask three questions of that one
decision. Can prediction improve the estimates? Can optimization turn them into a better allocation? Can a
language model improve the committee's governance without taking its authority? And a fourth: which part deserves
the credit?

## 0:45–1:15 — Q1: prediction ranks, but misjudges the level

*Figure 3 (F49, the one-year forward test).*

My queue model, tested as of 2020, ranks requests better than a careful lookup — an AUC of 0.731 against 0.686.
But it overstates how many get built. One year after the decision, 30 of the 1,441 live requests operated; the
level-corrected model expected 78, the lookup 17. So the model orders requests well and sets their level badly —
and the book is sized to the level. Built on the lookup's curves instead, the book is not demonstrably worse.

## 1:15–2:15 — Q2: the trade-off, and what it costs to fund

*Figure 4 (F38, the frontier over tail weights), then Figure 5 (F51, the true economics before and after financing).*

There is no single right book, only a trade-off. Held to the same budget and cap, the risk-aware book — five leases
and eight requests — beats ranking by expected value by 219 million dollars on the registered risk-return metric,
with an interval from 13 to 401 million. It gives up 508 million of expected value to cut the worst-five-percent
loss from 1.55 billion to 0.82. On the candidates public that day the result holds, but narrowly.

Its weak point is capital. The construction its requests call exceeds the reserve in half the scenarios. Without a
contingent line the book is worth 0.76 billion on the metric; a line of 2.53 billion restores 1.27. Priced as a
bank would, with the fee and the interest, it is still worth 1.03 billion, and every price I tried beats no line.

## 2:15–3:40 — Q3 and Q0: does an AI challenger help the committee?

*Figure 2 (F55, the committee workflow), pointing at the challenge stage; then Figure 6 (F53, the ladder), then Table 1 (the nine registered lines).*

The language model never computes a number. It reads the committee's rules from its words, tools test the
committee's own proposal against them, and the model writes a memo whose every number is checked. A named person
signs.

I registered the test before running it: 48 proposals from simulated committees, 176 model calls, none failed.
Tools alone improved the committee's own objective by 76 million dollars per case. Adding the language model to the
same tools added 43 million more, with an interval from 9 to 86 million. The optimizer's own book would add a
further 134 million. The tools do more than the model, and the optimizer more than both.

The model read all 40 paraphrased rules exactly, named all 12 flaws of argument and over-challenged none of the 12
sound proposals. It failed two of the registered lines: it read a committee's silence as a zero tail weight, and
seven memos carried a number not on their fact sheet. The tools check both: the reading is shown to the
committee before anything is computed, and the verifier marks every ungrounded number. Six of eight graded lines
pass.

## 3:40–4:30 — What I would tell a committee

*Appendix I, the capital allocation memo, then the executive summary's recommendation.*

Choose your tail weight first — and say it, because the model will not guess it right. At the registered weight,
fund the risk-aware book with a contingent construction line of 2.53 billion. Before you sign, state your rules in
words and let the challenger test your proposal against them; if you depart from its guidance, the ledger records
that you saw the evidence.

Better predictions did not, by themselves, make better decisions here. The decision is made by the constraints,
the capital plan and the tail — and a committee is helped most by tools that test its own rules.

## Recording notes

- Record the screen at 1920 × 1080 from the official report exported to PDF from Word (zoom to one figure at a time).
- Say "simulated committees" once, as scripted: the challenger was not tested with real committees.
- The dashboard is not part of the evaluated result; if time allows after 4:30, show the *A worked example* page of
  `make app` for ten seconds as "how a committee would use it", and say so.
