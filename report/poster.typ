// Poster — Beyond Prediction (report v10). Built by `make poster` (typst). Every number is one the report prints (results/report_numbers.csv).
#set page(width: 841mm, height: 594mm, margin: (x: 20mm, y: 14mm), fill: white)
#set text(font: "Calibri", size: 17pt, fill: rgb("#222222"))
#set par(justify: false, leading: 0.55em)
#let ink = rgb("#222222")
#let muted = rgb("#666666")
#let orange = rgb("#D55E00")
#let blue = rgb("#0072B2")
#let green = rgb("#009E73")
#let box(title, body, color: rgb("#E5E5E5")) = block(width: 100%, inset: 10mm, radius: 4mm, stroke: 1.2pt + ink, fill: color.lighten(80%), [
  #text(size: 25pt, weight: "bold")[#title]
  #v(2mm)
  #body
])
#let note(body) = text(size: 15pt, fill: muted)[#body]

// header
#grid(columns: (1fr, auto), align: (left, right),
  [#text(size: 44pt, weight: "bold")[Beyond Prediction: Prescriptive AI for Energy Portfolio Optimization] \
   #text(size: 30pt, fill: muted)[An AI-assisted decision intelligence framework for risk-aware capital allocation across oil, gas, power, renewables and storage]],
  [#text(size: 22pt)[Alan Mössinger · SIADS 699 Capstone, University of Michigan · Group 13 (a solo project) · 2026]]
)
#v(5mm)
#line(length: 100%, stroke: 2pt + ink)
#v(5mm)

#grid(columns: (1fr, 1.2fr, 1fr), gutter: 12mm,
  // column 1: the decision and Q1
  [
    #box("The decision, and three questions", color: blue)[
      One budget, forty candidates, 1 January 2025, and only what was public that day: twenty Gulf of Mexico lease redevelopments and twenty ERCOT interconnection requests that ERCOT's own reports listed as live. A committee must choose how much expected value to give up for a thinner tail, and how to fund the construction its requests may call. *Q1* Can predictive models improve estimates of energy investment outcomes? *Q2* Can mathematical optimization turn those estimates into better capital-allocation decisions? *Q3* Can a language model improve the quality of investment governance without taking authority away from decision-makers? And *Q0*: which part deserves the credit?
    ]
    #v(7mm)
    #box("Q1 — Prediction ranks; it does not set the level", color: blue)[
      #align(center)[#image("../figures/F49_forward_calibration.svg", width: 90%)]
      #note[Backtested as of 2020, the queue model ranked requests better than a transparent lookup (AUC 0.731 against 0.686; in ERCOT alone 0.656 against 0.591) but put ERCOT's five-year chance at 0.380 where 0.238 operated. One year after the decision, 30 of the 1,441 live requests had operated where the level-corrected model expected 78 and the lookup 17. The book chosen with the model's curves scores +\$37M [−\$76M, +\$151M] against the book chosen with the lookup's: not demonstrably better. Partly yes.]
    ]
  ],
  // column 2: the system and Q2
  [
    #box("The system in one picture", color: rgb("#BBBBBB"))[
      #align(center)[#image("../figures/F43_architecture.svg", width: 92%)]
      #note[The language model works in one stage only: it reads and argues; it never computes a value or decides. The reading is shown to the committee before anything is computed, a named person signs, and the ledger records every decision with what it saw.]
    ]
    #v(7mm)
    #box("Q2 — Optimization wins under one cap, narrowly, and must be funded", color: orange)[
      #align(center)[#image("../figures/F38_frontier.svg", width: 92%)]
      #note[On 2,000 held-out scenarios the risk-aware book expects \$2.17B with a worst-5% loss of \$0.82B; the return-seeking book \$2.73B with \$1.52B. Held to the same budget and cap, the risk-aware book beats NPV ranking by \$219M [+\$13M, +\$401M] on expected NPV minus the tail (C33, registered, passes), in all 20 re-selections, for \$508M of expected value. Its construction calls exceed the reserve in 50.3% of scenarios; a \$2.53B contingent line is worth \$1.03B on the metric net of a 0.5% fee and 8% interest, against \$0.76B with no line. Yes, if the constraints are shared and the line exists.]
    ]
  ],
  // column 3: Q3, Q0 and the recommendation
  [
    #box("Q3 and Q0 — What the language model adds, and what it does not", color: green)[
      #align(center)[#image("../figures/F50_ladder_v10.svg", width: 90%)]
      #note[Registered before it ran: 48 proposals from simulated committees, 24 written by me with their keys, 176 calls, scored once. Tools alone improve the committee's own objective by \$76M per case over its proposal; adding the language model adds \$43M [+\$9M, +\$86M] more (C34, passes); the optimizer's own book would add \$134M beyond that. The model read 40 of 40 paraphrased rules, named 12 of 12 flaws of argument and over-challenged 0 of 12 sound proposals. It failed two lines: 38 of 48 readings equal their key — it reads an unstated tail weight as zero — and 7 injected memos carried a number not on the sheet. 6 of 8 graded lines pass. Yes, because the tools, not the model, hold authority.]
    ]
    #v(7mm)
    #box("The capital plan, priced as a bank would", color: orange)[
      #align(center)[#image("../figures/F48_credit_line_net.svg", width: 82%)]
      #note[Without a line the book is worth \$1.71B in expectation; the \$2.53B line restores \$1.98B net of fee and interest, and the cost lands on the tail. The fee alone breaks even at 2.04% a year.]
    ]
    #v(7mm)
    #box("Recommendation", color: orange)[
      *Choose the tail weight first.* At the registered weight, fund the risk-aware book — five leases and eight requests — with a contingent construction line of \$2.53B. Defer the twelve requests whose agreement signal is worth more than their deposit. *State every rule, including the tail weight*, and *use the challenger before signing*; record any departure from its guidance with the evidence acknowledged.
      #v(2mm)
      #note[Prediction is necessary and not sufficient: the decision is made by the constraints, the capital plan and the tail, and a committee is helped most by tools that test its own rules. Model-based results on public data and assumed lease costs; simulated committees; failures reported as registered. Data: LBNL Queued Up (Rand et al.), ERCOT, BSEE, EIA, NREL ATB; author's analysis.]
    ]
  ]
)
