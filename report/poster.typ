// Poster — Beyond Prediction (report v9). Built by `make poster` (typst). Every number is one the report prints (results/report_numbers.csv).
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
   #text(size: 30pt, fill: muted)[An AI-assisted decision system for risk-aware capital allocation across oil, gas, power, renewables and storage]],
  [#text(size: 22pt)[Alan Mössinger · SIADS 699 Capstone, University of Michigan · Group 13 (a solo project) · 2026]]
)
#v(5mm)
#line(length: 100%, stroke: 2pt + ink)
#v(5mm)

#grid(columns: (1fr, 1.2fr, 1fr), gutter: 12mm,
  // column 1: the decision and what prediction adds
  [
    #box("The decision", color: blue)[
      One budget, forty candidates, 1 January 2025, and only what was public that day: twenty Gulf of Mexico lease redevelopments and twenty ERCOT interconnection requests still waiting in the queue. A committee must choose how much expected value to give up for a thinner tail, and how to fund the construction its requests may call. Four questions: can machine learning *predict* better than transparent baselines, how does risk change value, which book should be *prescribed*, and how much does each part — the forecasts, the optimizer, the language model — add?
    ]
    #v(7mm)
    #box("Prediction is not the decision", color: blue)[
      #align(center)[#image("../figures/F28_candidates.svg", width: 86%)]
      #note[Every lease adds value at the base cost; wind and solar requests pay only under contract. Backtested as of 2020, the queue model ranked requests better than a lookup (AUC 0.731 against 0.686) — yet the book chosen with its curves scores +\$22M [−\$168M, +\$207M] against the book chosen with the lookup's: not demonstrably better. The decision turns on a few large requests whose chance of operating neither method knows well.]
    ]
    #v(7mm)
    #box("What each part adds, on the same scenarios", color: blue)[
      #align(center)[#image("../figures/F42_value_added.svg", width: 86%)]
      #note[The optimizer adds value only when held to the same constraints as the rules it is compared with. Revising the book in 2027 is worth −\$9M; knowing everything in advance would be worth at most \$571M.]
    ]
  ],
  // column 2: the system and the trade-off
  [
    #box("The system in one picture", color: rgb("#BBBBBB"))[
      #align(center)[#image("../figures/F43_architecture.svg", width: 92%)]
      #note[The language model works in one stage only: it reads and argues; it never computes a value or decides. A named person signs, and the ledger records every decision with what it saw.]
    ]
    #v(7mm)
    #box("The trade-off the committee must price", color: orange)[
      #align(center)[#image("../figures/F38_frontier.svg", width: 92%)]
      #note[On 2,000 held-out scenarios the risk-aware book expects \$2.05B with a worst-5% loss of \$1.02B; the return-seeking book \$2.36B with \$1.60B. Under equal constraints the risk-aware book beats NPV ranking by \$320M [+\$142M, +\$511M] on expected NPV minus the tail, and does so in all 20 re-selections.]
    ]
  ],
  // column 3: the challenger and the recommendation
  [
    #box("Does an AI challenger improve the committee's decision?", color: green)[
      #align(center)[#image("../figures/F46_challenger.svg", width: 90%)]
      #note[Registered before it ran, on 48 proposals from simulated committees. Following the challenger improved the committee's own objective by \$192M per flawed case [+\$108M, +\$281M] and avoided \$240M of worst-5% loss. A checklist with the same tools and no language model achieved \$145M and \$257M: most of the gain is the tools'. What only the language model adds is understanding — 11 of 12 flaws of argument named (the checklist 0), 40 of 40 rules read from words. It over-challenged 2 of 12 sound proposals; 6 of 8 registered lines pass.]
    ]
    #v(7mm)
    #box("The capital plan is the weak point", color: orange)[
      #align(center)[#image("../figures/F45_robustness.svg", width: 82%)]
      #note[Construction calls exceed the reserve in 44.5% of scenarios; without a contingent line the requests that reach their agreement cannot be built and the book is worth \$1.40B.]
    ]
    #v(7mm)
    #box("Recommendation", color: orange)[
      *Choose the tail weight first.* At the registered weight, fund the risk-aware book — six leases, five wind, one solar and one gas request — with a contingent construction line of \$3.28B, which restores \$2.02B of value. Defer the requests whose agreement signal is worth more than their deposit. *Use the challenger before signing*, and record any departure from its guidance with the evidence acknowledged.
      #v(2mm)
      #note[Prediction is necessary and not sufficient: the decision is made by the constraints, the capital plan and the tail — and a committee is helped most by tools that test its own rules. Model-based results on public data and assumed lease costs; simulated committees. Data: LBNL Queued Up 2025 (Rand et al., 2025); BSEE OGOR-A; EIA; ERCOT settlement-point prices; NREL ATB. Author's analysis.]
    ]
  ]
)
