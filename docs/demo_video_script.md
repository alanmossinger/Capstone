# Demo video script — Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization (about 4½ minutes)

Spoken text in plain type; what is on screen in *italics*. About 620 spoken words at roughly 140 words a
minute. Every number below is one report v9 prints from `results/` (keyed in `results/report_numbers.csv`); if a
rerun changes a number, change it here from the report, never from memory.

## 0:00–0:35 — The decision

*Report title page, then Figure 1 (F43, the decision workflow).*

An energy company has one budget on the first of January 2025, and forty places to put it: twenty oil and gas
leases in the Gulf of Mexico that already produce, and twenty requests to connect new power plants to the Texas
grid — most of which are never built. I use only what was public that day. The project goes past prediction: it
asks which projects to fund, how much risk to accept, and whether that answer beats the conventional ways of
deciding. Then it asks a second question: can a language model help the committee make a better decision of its
own?

## 0:35–1:20 — Prediction is not the decision

*Appendix Figure F2 (F28, the forty candidates), then Figure 3 (F42, value added).*

Every lease adds value at the base cost; the wind and solar requests pay only under contract. My queue model,
tested as of 2020, ranks requests better than a careful lookup — an AUC of 0.731 against 0.686. But when I let each
method choose the book, the model's book is not demonstrably better: plus 22 million dollars, with an interval
from minus 168 to plus 207. The decision turns on a few large requests whose chance of being built neither method
knows well. For this decision, the simpler forecast is enough.

## 1:20–2:20 — The trade-off, and the weak point

*Figure 2 (F38, the frontier), then Figure 4 (F45, capital calls).*

There is no single right book, only a trade-off. The risk-aware book expects 2.05 billion dollars with a
worst-five-percent loss of 1.02 billion; the return-seeking book expects 2.36 billion with 1.60 billion. Held to the
same budget and cap, the risk-aware book beats ranking by expected value by 320 million dollars on the registered
risk-return metric — and it does so in all 20 re-selections.

Its weak point is capital. The construction its requests call exceeds the reserve in 44.5 percent of scenarios.
Without a contingent line, the requests that reach their agreement cannot be built and the book is worth 1.40
billion, not 2.05. A line of 3.28 billion restores 2.02 billion. That is what the committee is really committing to.

## 2:20–3:45 — Does an AI challenger improve the committee's decision?

*Figure 1 again, pointing at stage 4, the AI challenge; then Figure 5 (F46, the challenger), then Table 3.*

The language model never computes a number. It reads the committee's rules from its words, tools test the
committee's own proposal against them, and the model writes a memo whose every number is checked. A named person
decides.

I registered the test before running it: 48 proposals from simulated committees, 36 with a flaw. Following the
challenger improved the committee's own objective by 192 million dollars per flawed case and avoided 240 million of
worst-five-percent loss. Avoiding loss was the larger effect.

But a checklist with the same tools and no language model achieved 145 million and 257 million. Most of the gain is
the tools'. What only the language model adds is understanding: it named 11 of 12 flaws of argument — a sunk
cost, a double standard, a belief no fact supports — which the checklist cannot see, and it read 40 of 40 rules
from plain words. It also over-challenged 2 of 12 sound proposals, and 6 of 8 registered lines pass.

## 3:45–4:30 — What I would tell a committee

*The Capital Allocation Memo page, then the executive summary's recommendation.*

Choose your tail weight first. At the registered weight, fund the risk-aware book with a contingent construction
line. Before you sign, state your rules in words and let the challenger test your proposal against them; if you
depart from its guidance, the ledger asks you to acknowledge the evidence.

Better predictions did not, by themselves, make better decisions here. The decision is made by the constraints,
the capital plan and the tail — and a committee is helped most by tools that test its own rules.

## Recording notes

- Record the screen at 1920 × 1080 from `report/report.pdf` (the figures are vector; zoom to one figure at a time).
- Say "simulated committees" once, as scripted: the challenger was not tested with real committees.
- Do not show the dashboard or the decision page; neither is part of the evaluated result.
