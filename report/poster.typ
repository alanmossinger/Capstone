// Poster — Beyond Prediction (report V2). Built by `make poster` (typst). Every number is one the report prints (results/report_numbers.csv).
// A1 landscape, read from three metres: one headline, four numbers, five pictures, one recommendation.
#set page(width: 841mm, height: 594mm, margin: 0mm, fill: white)
#set text(font: "Calibri", size: 18pt, fill: rgb("#222222"))
#set par(justify: false, leading: 0.48em)
#let ink = rgb("#222222")
#let muted = rgb("#5F6368")
#let navy = rgb("#13294B")
#let orange = rgb("#D55E00")
#let blue = rgb("#0072B2")
#let green = rgb("#009E73")
#let paper = rgb("#F4F5F7")

// a tile with a big number, a label under it and one line of reading
#let kpi(number, label, reading, color: navy) = block(width: 100%, height: 100%, inset: (x: 10mm, y: 7mm), radius: 5mm, fill: white, stroke: 1.5pt + color.lighten(40%), [
  #text(size: 46pt, weight: "bold", fill: color)[#number] \
  #v(-3mm)
  #text(size: 20pt, weight: "bold")[#label] \
  #v(0.5mm)
  #text(size: 15.5pt, fill: muted)[#reading]
])

// a panel: a finding as its title, a picture, one line of reading
#let panel(title, body, color: navy) = block(width: 100%, inset: (x: 8mm, y: 6mm), radius: 5mm, fill: white, stroke: 1.2pt + rgb("#D0D3D8"), [
  #block(width: 100%, inset: (bottom: 2mm), stroke: (bottom: 3pt + color))[#text(size: 22pt, weight: "bold", fill: ink)[#title]]
  #v(2mm)
  #body
])
#let reading(body) = text(size: 16pt, fill: ink)[#body]

// ---- header band ------------------------------------------------------------------------------
#block(width: 100%, inset: (x: 20mm, y: 9mm), fill: navy, [
  #grid(columns: (3.4fr, 1fr), align: (left + horizon, right + horizon), gutter: 10mm,
    [#text(size: 44pt, weight: "bold", fill: white)[Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation] \
     #v(1mm)
     #text(size: 22pt, fill: white.darken(12%))[A governed decision-intelligence system for an investment committee — one budget, forty candidates, a thinner tail, a funded plan, and a challenger that reads the committee's own rules]],
    [#text(size: 19pt, fill: white)[*Alan Mössinger* \ SIADS 699 Capstone · University of Michigan \ MADS, Group 13 (a solo project) · October 2026]]
  )
])

#block(width: 100%, inset: (x: 20mm, y: 7mm), fill: paper, [
  // ---- the headline -------------------------------------------------------------------------
  #text(size: 27pt, weight: "bold", fill: ink)[Better predictions did not make better decisions. The constraints, the capital plan and the tail did — and a language model earned its place by challenging the committee's reasons, not by picking the book.]
  #v(5mm)

  // ---- four numbers -------------------------------------------------------------------------
  #grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 8mm, rows: 54mm,
    kpi([\$3.78B], "committed of a $3.82B budget", "Five Gulf lease redevelopments and eight ERCOT interconnection requests, chosen on 1 January 2025 from what was public that day.", color: navy),
    kpi([+\$312M], "over NPV ranking, funded the same way", "Pre-registered: +$219M [+$13M, +$401M] on a static basis; +$312M [+$110M, +$506M] once every process pays for its own construction line. Best in 7 of 7 modelled worlds.", color: orange),
    kpi([\$2.53B], "contingent construction facility", "In half the scenarios the book's requests call more capital than their reserve. Priced at a bank's fee and interest the facility still pays; without one, a different book wins.", color: blue),
    kpi([+\$43M], "per case from the language model", "On 48 simulated committees: tools +$76M, the model +$43M more, the optimizer +$134M beyond. An optimizer-first rule matches the model's book (−$14M): its value is the argument.", color: green),
  )
  #v(6mm)

  // ---- three columns ------------------------------------------------------------------------
  #grid(columns: (1fr, 1fr, 1fr), gutter: 8mm,
    // column 1: what to fund, and the recommendation
    [
      #panel("What to fund: each member's cost, value and risk", color: navy)[
        #align(center)[#image("../figures/executive/F54_allocation.svg", width: 100%)]
        #reading[Three requests with signed agreements carry the construction reserve and lose in 62–64% of scenarios; five waiting requests cost only deposits and pay in exactly the scenarios in which the leases do not. Outside the book: 12 requests deferred, 14 leases monitored, 1 rejected.]
      ]
      #v(6mm)
      #block(width: 100%, inset: (x: 10mm, y: 8mm), radius: 5mm, fill: navy, [
        #text(size: 24pt, weight: "bold", fill: white)[Recommendation to the committee] \
        #v(3mm)
        #text(size: 17.5pt, fill: white)[
          *1. Choose the tail weight first* — and say it; an unstated one is read as zero. \
          #v(1.5mm)
          *2. Fund the risk-aware book* — five leases and eight requests, \$3.78B — *with a \$2.53B contingent construction facility.* If no facility can be arranged, fund equal capital by sector instead. \
          #v(1.5mm)
          *3. Defer the twelve waiting requests* until their agreements are signed; reject nothing on the strength of money already spent. \
          #v(1.5mm)
          *4. Run the challenger before signing*, confirm its reading of your rules, and record any departure from its guidance with the evidence acknowledged.
        ]
        #v(3mm)
        #text(size: 14.5pt, fill: white.darken(15%))[Model-based results on public data, assumed redevelopment costs and simulated committees — not realized returns. Before a real commitment: a bank's term sheet, the company's own costs, extreme-event scenarios, a study with real committees.]
      ])
    ],
    // column 2: financing and what can go wrong
    [
      #panel("Funded the same way, the risk-aware book still scores best", color: orange)[
        #align(center)[#image("../figures/executive/F51_true_economics.svg", width: 100%)]
        #reading[Every process pays for its own construction line: the risk-aware book scores \$1.03B on expected NPV minus the worst-5% loss, against \$0.82B for the deterministic optimizer and \$0.72B for NPV ranking. With no line at all, equal capital by sector would lead — the recommendation is the book *and* its facility.]
      ]
      #v(6mm)
      #panel("What can go wrong: the tail is the candidates' co-movement", color: blue)[
        #align(center)[#image("../figures/executive/F52_what_can_go_wrong.svg", width: 100%)]
        #reading[Five leases on one oil price, eight requests on one power price. Dial the co-movement from none to as scored and the worst-5% loss rises from a small profit to \$0.82B. The risk-aware book keeps the smallest tail at every setting and is the only one positive when ERCOT prices fall 25% or oil sits at \$45.]
      ]
    ],
    // column 3: the AI and how a committee uses it
    [
      #panel("Where the value of AI comes from: optimizer, tools, then the model", color: green)[
        #align(center)[#image("../figures/executive/F53_ladder_five_arms.svg", width: 100%)]
        #reading[Registered before 176 model calls, scored once. The model reads rules from words, argues from a computed fact sheet and never computes a number: 12 of 12 flaws of argument named, 0 of 12 sound proposals over-challenged. It read silence as a zero tail weight and wrote 7 memos with a number not on its sheet — caught by the controls. 6 of 8 lines pass.]
      ]
      #v(6mm)
      #panel("How a committee uses it: nine stages, three hands", color: navy)[
        #align(center)[#image("../figures/executive/F55_committee_workflow.svg", width: 100%)]
        #reading[The committee decides, tools compute every number, the model reads and argues — explain, challenge or guide only toward a book that keeps every rule; abstain or escalate when the evidence is thin. A named person signs into a hash-chained ledger. Ten of twelve controls in place.]
      ]
    ],
  )
  #v(4mm)
  #text(size: 13.5pt, fill: muted)[Data: LBNL *Queued Up* (Rand et al.), ERCOT interconnection reports and prices, BSEE lease production, EIA, NREL ATB, EPA eGRID; author's analysis. Every number traces to `results/report_numbers.csv`; nine evaluation lines were registered before the final test and scored once, failures included. `make all` rebuilds thirteen notebooks, every table and every figure from the raw files.]
])
