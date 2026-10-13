// Poster — From Queue to Capital. Built by `make poster` (typst). Every number is the report's (results/report_numbers.csv).
#set page(width: 841mm, height: 594mm, margin: (x: 20mm, y: 14mm), fill: white)
#set text(font: "Calibri", size: 17pt, fill: rgb("#222222"))
#set par(justify: false, leading: 0.55em)
#let ink = rgb("#222222")
#let muted = rgb("#666666")
#let orange = rgb("#D55E00")
#let blue = rgb("#0072B2")
#let green = rgb("#009E73")
#let box(title, body, color: rgb("#E5E5E5")) = block(width: 100%, inset: 11mm, radius: 4mm, stroke: 1.2pt + ink, fill: color.lighten(80%), [
  #text(size: 26pt, weight: "bold")[#title]
  #v(3mm)
  #body
])

// header
#grid(columns: (1fr, auto), align: (left, right),
  [#text(size: 54pt, weight: "bold")[From Queue to Capital] \
   #text(size: 30pt, fill: muted)[AI-driven portfolio management for an integrated U.S. energy book: 20 offshore Gulf lease redevelopments and 20 ERCOT queue requests under one budget and 2,000 joint scenarios]],
  [#text(size: 22pt)[Alan Mössinger · SIADS 699 Capstone, University of Michigan · Group 13 · 2026] \
   #text(size: 18pt, fill: muted)[github.com/alanmossinger/Capstone]]
)
#v(6mm)
#line(length: 100%, stroke: 2pt + ink)
#v(6mm)

#grid(columns: (1fr, 1.25fr, 1fr), gutter: 12mm,
  // column 1
  [
    #box("The decision", color: blue)[
      An energy company holds a budget of \$6.15B (40% of forty candidates' capital), no technology above 40% of it, over 2025–2044. The candidates: the 20 largest producing federal offshore Gulf of Mexico leases (BSEE, 2010–2024), to be redeveloped; and 20 ERCOT power requests in the interconnection queue (5 gas combined cycle, 5 solar, 5 wind, 5 storage) that may never reach operation. The queue-survival models of Part I are the timing engine of the power side.

      *Four questions, criteria registered before scoring.* RQ1 can machine learning improve the physical forecasts (C20)? RQ2 how do forecast error, price uncertainty and correlation change risk? RQ3 does a risk-aware book beat NPV ranking and sector-only books out of sample (C21–C24)? RQ4 which constraints change the selection?
    ]
    #v(8mm)
    #box("What each candidate is worth", color: orange)[
      Under the confirmed upstream cost grid (ASSUMED, shown before it is used) the twenty leases carry *\$14.6B* of incremental NPV at base, every one positive, median break-even *\$33 a barrel* against a 2024 real WTI of \$77. The twenty requests are worth *−\$0.76B merchant* and *−\$0.28B contracted* once the queue models' chance of operating within seven years (6%–23%) and the cost to carry are priced in; only wind under a \$62 PPA is positive.

      #align(center)[#image("../figures/F29_cost_tornado.png", height: 100mm)]
      #text(size: 15pt, fill: muted)[The uplift share (10%–30%: \$5.9B to \$21.8B) and the operating cost (\$12–\$28 per boe: \$16.6B to \$9.2B) decide the lease side; the power price basis moves the book by under \$0.5B.]
    ]
  ],
  // column 2
  [
    #box("The four books under one budget — C21–C24 fail, and why", color: orange)[
      #align(center)[#image("../figures/F33_four_books.png", height: 140mm)]
      A top-N NPV · B equal capital by sector · C deterministic MILP · D risk-aware MILP (E[NPV] − λ·CVaR95, HiGHS), selected on block-bootstrap scenarios and scored on a held-out copula set. Out of sample D earns *\$20.65B* against *\$21.07B* for A (C21: −\$420M [−\$659M, −\$210M]); no more than B (C22); its selection moves more than C's under six stresses (Jaccard 0.95 vs 0.99, C23); its tail is not below the single-sector comparator's (C24). *The finding:* no book of these forty loses money in any of 2,000 joint scenarios under the confirmed grid, so risk aversion has nothing to buy — a statement about the grid and the prices, not the method.
    ]
    #v(8mm)
    #box("The decision gym: AI and rule against instinct, scored on outcomes", color: green)[
      #align(center)[#image("../figures/F34_decision_gym.png", height: 150mm)]
      Sixteen situations built as of their date with no hindsight: the fifteen largest requests of ERCOT, PJM and CAISO in each 2017–2019 cohort at entry, the 2017 cohort at its two-year gate, a 2018 budget cut, and the lease candidates at the 2014, 2020 and 2022 oil-price regimes. The registered rule beat instinct by *\$100M a situation* (regret against hindsight \$197M vs \$297M); in nine queue rooms none of the largest requests operated, and the rule's edge is the money it did not spend.
    ]
  ],
  // column 3
  [
    #box("The AI inside the decision", color: green)[
      #align(center)[#image("../figures/F36_ai_workflow.png", height: 105mm)]
      An LLM advisor (Anthropic Messages API, temperature 0) sees only the result tables; every number it writes is checked against them; every call is recorded and replayed, so the pipeline runs offline. It recommends per scenario and horizon, runs the motivated-reasoning check and argues the opposing book (ideological Turing test); the human overrides only after answering the five questions. Every decision goes to a ledger; the dashboard (`make app`) carries both modes.
    ]
    #v(8mm)
    #box("When: the book at one to twenty years", color: blue)[
      #align(center)[#image("../figures/F35_horizon_view.png", height: 100mm)]
      The lease book is −\$1.4B within two years (the workovers), \$0.2B at three, \$14.6B at twenty; a request is a carry cost until it operates (−\$0.84B at twenty). A one-year owner funds nothing; a three-year owner funds twelve leases; the twenty-year owner buys the contracted wind.
    ]
    #v(8mm)
    #box("Recommendation and record")[
      *Fund the twenty leases and the contracted wind; hold gas to its gate; no solar or storage at 2024 prices* — book D: 24 candidates, \$4.2B, P(NPV \< 0) 1.8%, the worst 5% still a profit. What would change it: the uplift share and the operating cost (ASSUMED); the hub price and the PPA on the power side. Registered record: C1–C5 8/12 · C6–C12 3/12 · C13–C14 3/12 · C15–C17 4/10 · C18–C19 fail · C20 3/12 · C21–C24 0/4. Every number traces to `results/`; every figure carries its provenance.
      #v(2mm)
      #text(size: 15pt, fill: muted)[Data: BSEE OGOR-A; EIA-923 and EIA spot prices; ERCOT settlement-point prices; EPA eGRID; NREL ATB; LBNL Queued Up 2025 (Rand et al., 2025). Author's analysis.]
    ]
  ]
)
