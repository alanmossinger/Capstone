// Poster — Beyond Prediction (report v5). Built by `make poster` (typst). Every number is one the report prints (results/report_numbers.csv).
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
  [#text(size: 44pt, weight: "bold")[Beyond Prediction: AI-Driven Energy Portfolio Decisions Under Uncertainty] \
   #text(size: 30pt, fill: muted)[From Machine Learning to Risk-Aware Capital Allocation]],
  [#text(size: 22pt)[Alan Mössinger · SIADS 699 Capstone, University of Michigan · Group 13 (a solo project) · 2026]]
)
#v(5mm)
#line(length: 100%, stroke: 2pt + ink)
#v(5mm)

#grid(columns: (1fr, 1.2fr, 1fr), gutter: 12mm,
  // column 1: the decision and Part I
  [
    #box("The decision", color: blue)[
      An energy company holds interconnection-queue requests and producing oil and gas leases. It must decide, request by request, whether to fund, hold or exit, and, across the whole book, how to split one budget. Both decisions are built from public records and scored on what happened. Four questions were set first: can machine learning *predict* better than transparent baselines, how do forecast error and correlated prices change *risk*, does a risk-aware book *allocate* better, and what *explains* the choice.
    ]
    #v(7mm)
    #box("Part I — which queue requests get built", color: blue)[
      13,366 requests in CAISO, ERCOT and PJM; tested once on the 2,268 that entered in 2017–2019. ERCOT builds most often: 18.4% of entrants operate within five years, against 4.8% in CAISO.
      #align(center)[#image("../figures/F1_cif_by_region.png", width: 100%)]
      At entry the model beats cohort averages (AUC 0.86 against 0.73) but ties a careful lookup at utility scale. *Two years in, with the agreement known, it earns its keep:*
      #align(center)[#image("../figures/F18_managed_book.png", width: 100%)]
      #note[A book of 25 chosen by the landmark model held 19 requests that reached operation, against 11 for the lookup. Every cohort since 2017 completes below the model's level, so books are sized to the newest cohort.]
    ]
  ],
  // column 2: the project in one picture and Part II
  [
    #box("The work in one picture", color: rgb("#BBBBBB"))[
      #align(center)[#image("../figures/F0_overview.png", width: 88%)]
    ]
    #v(7mm)
    #box("Part II — one budget across twenty leases and twenty ERCOT requests", color: orange)[
      2,000 joint price scenarios; Part I's models time every power request. Under the registered cost grid the leases are worth \$14.6B and carry the book. *Priced as an investment committee would* — \$40k per incremental flowing barrel a day and an 8% real rate, added after the registered results and labelled post-hoc — they fall to \$7.0B on four times the capital, and five years of \$42 oil take them to \$4.25B.
      #align(center)[#image("../figures/F37_committee_grid.png", width: 88%)]
      #note[Under the registered grid the four allocation criteria fail as registered: the risk-aware book earns \$20.7B against \$21.1B for NPV ranking, and none of the four books' held-out tail is a loss. Under the committee grid the risk-aware book halves the tail; on the registered metric NPV ranking still wins by \$755M.]
    ]
  ],
  // column 3: the gym, the AI, the recommendation
  [
    #box("The decision gym: rules against instinct, on outcomes", color: green)[
      #align(center)[#image("../figures/F34_decision_gym.png", height: 150mm)]
      #note[Sixteen past situations rebuilt as of their date. The registered rules beat instinct by \$236M a situation (regret against hindsight \$18M against \$253M), almost all of it in the three oil-price regimes.]
    ]
    #v(7mm)
    #box("The AI inside the decision", color: green)[
      #align(center)[#image("../figures/F36_ai_workflow.png", height: 95mm)]
      An LLM advisor reads only the result tables, must match every number it writes to them, argues the opposing book, and can be overridden only after the human answers five questions about the decision. Every call is recorded and replays offline.
    ]
    #v(7mm)
    #box("Recommendation", color: orange)[
      *Fund the risk-aware book:* ten lease redevelopments, four wind requests under 15-year contracts and one gas request, \$6.6B of a \$7.81B budget. It expects \$8.1B (median \$6.7B), loses money in 9% of scenarios, and its worst 5% averages a \$2.7B loss. *The alternative* for a committee with more appetite for risk: all twenty leases and three gas requests, \$11.5B expected with a \$5.3B worst-5% loss. No solar or storage at 2024 prices.
      #v(2mm)
      #note[Prediction is necessary and not sufficient: the decision is made by the assumptions, the timing and the tail. Data: LBNL Queued Up 2025 (Rand et al., 2025); BSEE OGOR-A; EIA-923 and EIA spot prices; ERCOT settlement-point prices; EPA eGRID; NREL ATB. Author's analysis.]
    ]
  ]
)
