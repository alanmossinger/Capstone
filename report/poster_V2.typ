// Poster V2 — Beyond Prediction, written to be explained in four minutes.
// Built with: typst compile --root . report/poster_V2.typ report/poster_V2.pdf
// Every number is one the V2 report prints (report/Beyond_Prediction_Capstone_Report_V2.docx): sections 2–9, Tables 1–3, Appendix I.
// The four columns are the report's four conclusions (Section 9), each answered by one stage of the system.
// The charts are drawn here from the report's own numbers, so their type is read at poster size.
#set page(width: 841mm, height: 594mm, margin: 0mm, fill: rgb("#F4F5F7"))
#set text(font: ("Calibri", "Carlito"), size: 18pt, fill: rgb("#222222"))
#set par(justify: false, leading: 0.5em)
#let ink = rgb("#222222")
#let muted = rgb("#5F6368")
#let line-c = rgb("#D0D3D8")
#let navy = rgb("#13294B")
#let orange = rgb("#D55E00")
#let blue = rgb("#0072B2")
#let green = rgb("#009E73")
#let grey = rgb("#B8BEC6")
#let pale(c) = c.lighten(55%)
#let bar-w = 78%      // the longest bar, as a share of the row
#let bar-min = 0.004  // so a zero value still shows a sliver

// ---- building blocks ---------------------------------------------------------------------------
// horizontal bars, one per row: (label, value, shown text, colour)
#let bars(title, rows, maxv, note: none) = block(width: 100%, inset: (x: 5mm, y: 4mm), radius: 3mm, fill: rgb("#FAFAFB"), stroke: 1pt + line-c, [
  #text(size: 18.5pt, weight: "bold")[#title]
  #v(2mm)
  #grid(columns: (72mm, 1fr), row-gutter: 3.6mm, column-gutter: 3mm, align: (right + horizon, left + horizon),
    ..rows.map(r => (
      text(size: 17.5pt)[#r.at(0)],
      grid(columns: (calc.max(r.at(1) / maxv, bar-min) * bar-w, auto), column-gutter: 2.5mm, align: horizon,
        box(width: 100%, height: 13.5mm, fill: r.at(3), radius: 1.5mm),
        text(size: 22pt, weight: "bold")[#r.at(2)]),
    )).flatten()
  )
  #if note != none [#v(2mm) #text(size: 15pt, fill: muted)[#note]]
])

// one of the four findings: the stage, the question, the answer, one chart, three facts, one result
#let ci(body) = box[#body]   // keeps an interval on one line
#let finding(n, stage, color, question, answer, chart, facts, big, label) = block(width: 100%, height: 100%, inset: (x: 8mm, y: 6mm), radius: 5mm, fill: white, stroke: (top: 6pt + color, rest: 1.2pt + line-c), [
  #grid(columns: (auto, 1fr), column-gutter: 4mm, align: horizon,
    circle(radius: 8.5mm, fill: color, stroke: none)[#align(center + horizon)[#text(size: 28pt, weight: "bold", fill: white)[#n]]],
    text(size: 18pt, weight: "bold", fill: color)[#upper(stage)])
  #v(2.5mm)
  #text(size: 21pt, style: "italic", fill: muted)[#question]
  #v(0.5mm)
  #text(size: 33pt, weight: "bold", fill: ink)[#answer]
  #v(4mm)
  #chart
  #v(4mm)
  #block[
    #set text(size: 19.5pt)
    #set list(marker: text(fill: color)[●], spacing: 4.5mm, indent: 0mm, body-indent: 3mm)
    #facts
  ]
  #v(1fr)
  #block(width: 100%, inset: (x: 6mm, y: 4mm), radius: 3mm, fill: pale(color).lighten(40%), stroke: 1.5pt + color, [
    #grid(columns: (auto, 1fr), column-gutter: 5mm, align: horizon,
      text(size: 40pt, weight: "bold", fill: color)[#big],
      text(size: 16.5pt, fill: ink)[#label])
  ])
])

#let card(title, body, color: navy) = block(width: 100%, height: 100%, inset: (x: 7mm, y: 5mm), radius: 4mm, fill: white, stroke: 1.2pt + line-c, [
  #text(size: 19pt, weight: "bold", fill: color)[#title] \
  #v(-0.5mm)
  #text(size: 17pt)[#body]
])

#let step(n, body, color) = box(height: 100%, inset: (x: 4mm, y: 2mm), radius: 3mm, fill: pale(color), [
  #align(horizon)[#text(size: 16.5pt)[*#n* #body]]
])
#let arrow = align(center + horizon)[#text(size: 26pt, fill: muted)[→]]

// ---- header band -------------------------------------------------------------------------------
#block(width: 100%, inset: (x: 20mm, y: 8mm), fill: navy, [
  #grid(columns: (3.3fr, 1fr), align: (left + horizon, right + horizon), gutter: 10mm,
    [#text(size: 46pt, weight: "bold", fill: white)[Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation] \
     #v(0.5mm)
     #text(size: 21pt, fill: white.darken(12%))[A Governed Decision Intelligence System for Risk, Returns, and Investment Committee Choices Across Oil, Gas, Power, Renewables, and Storage]],
    [#text(size: 18.5pt, fill: white)[*Alan Mössinger* \ SIADS 699 Capstone · University of Michigan \ MADS, Group 13 (a solo project) \ Mentor: Laura Danielle Stagnaro · November 2026]]
  )
])

#block(width: 100%, inset: (x: 20mm, y: 6mm), [
  // ---- the question and the answer ----------------------------------------------------------
  #grid(columns: (1fr, 1.55fr), column-gutter: 10mm, align: horizon,
    text(size: 33pt, weight: "bold", fill: navy)[Is prediction enough to spend a \$3.82 billion budget well?],
    text(size: 21pt, fill: ink)[*No.* Machine learning ranked the candidates better than a hand-built lookup, but did not produce a demonstrably better portfolio. The value lay past prediction: in pricing the tail, in optimizing under the company's own rules, and in a challenger that argues but never decides.],
  )
  #v(5mm)

  // ---- the decision, in plain words ---------------------------------------------------------
  #grid(columns: (1fr, 1fr, 1fr, 1.15fr), gutter: 8mm, rows: 43mm,
    card("The decision · 1 January 2025", [\$3.82 billion to commit across forty candidates, using only what was public that day. No technology may take more than 40% of the budget.]),
    card("20 Gulf of Mexico leases", [Redevelop now: capital spent today, output up 20% after two years. They rarely lose money, but all sell the same oil, so they lose together.], color: orange),
    card("20 ERCOT queue requests", [Cheap to hold, expensive once the interconnection agreement is signed. Most never get there: of 2000–2019 capacity, 12.6% was operating by 2024 and 76.9% had withdrawn.], color: blue),
    card("Four words used here", [*Book:* the candidates funded together. *Worst-5% loss:* the loss to budget for in the one year in twenty that goes badly. *Registered:* the pass rule was written before the result was seen. *[a, b]:* the 95% interval.], color: green),
  )
  #v(5mm)

  // ---- how it works: the six stages (report Figure 1) ---------------------------------------
  #grid(columns: (auto, 1fr, 9mm, 1fr, 9mm, 1fr, 9mm, 1fr, 9mm, 0.75fr, 9mm, 0.95fr), rows: 21mm, column-gutter: 1mm,
    box(height: 100%, inset: (right: 4mm), align(horizon, text(size: 20pt, weight: "bold", fill: navy)[How it works])),
    step("1 Predict", [which plants get built, what each asset produces], blue), arrow,
    step("2 Simulate", [2,000 futures of prices, output, cost and timing], blue), arrow,
    step("3 Optimize", [the book, under the budget and the risk appetite], orange), arrow,
    step("4 Challenge", [a governed language model argues with the committee], green), arrow,
    step("5 Decide", [a named person signs], grey), arrow,
    step("6 Score", [on 2,000 different futures], navy),
  )
  #v(5mm)

  // ---- four findings, the report's four conclusions -----------------------------------------
  #grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 8mm, rows: 314mm,
    finding("1", "Stage 1 · Prediction", blue,
      [Can a model predict which plants get built?],
      [It ranks well, but sizes badly.],
      bars("Requests that started operating in 2025, of 1,441 live", (
        ("Raw model expected", 125, "125", pale(blue)),
        ("Corrected model expected", 78, "78", blue),
        ("Lookup expected", 17, "17", grey),
        ([*What happened*], 30, "30", ink),
      ), 125, note: [One year after the decision; nothing refitted (report Figure 3).]),
      [
        - The model ordered requests better than the lookup: AUC 0.731 against 0.686.
        - It put ERCOT's five-year chance at 0.380; 0.238 operated.
        - Machine learning won 3 of 12 forecast contests, all for plant output; prices behaved as random walks.
      ],
      [+\$37M], [what the model's curves added to the book: #ci[\[−\$76M, +\$151M\]], *not clear of zero*]),
    finding("2", "Stages 2–3 · Risk", orange,
      [Is the highest expected return the best investment?],
      [No. Pricing the tail beat ranking by value.],
      bars("Rank by value vs the risk-aware optimizer, $ billion", (
        ("Expected NPV · rank", 2.68, "2.68", grey),
        ("Expected NPV · risk-aware", 2.17, "2.17", orange),
        ("Worst-5% loss · rank", 1.55, "1.55", grey),
        ("Worst-5% loss · risk-aware", 0.82, "0.82", orange),
      ), 2.68, note: [2,000 held-out futures (report Figure 4, Table 1).]),
      [
        - The tail is in the co-movement: five leases on one oil price, eight plants on one power price.
        - The optimizer gave up \$508M of expected value to nearly halve the worst-5% loss.
        - It found a hedge ranking never would: five cheap wind and solar deposits that pay when the leases do not.
      ],
      [+\$219M], [over ranking by value #ci[\[+\$13M, +\$401M\]]. Registered (C33): it holds, narrowly]),
    finding("3", "Stage 3 · Financing", navy,
      [Can the company pay for what it chose?],
      [Only with a credit line: choose the book and its financing together.],
      bars("The risk-aware book's expected NPV, $ billion", (
        ("On paper", 2.17, "2.17", grey),
        ("No facility", 1.71, "1.71", pale(navy)),
        ([With a \$2.53B facility, after its cost], 1.98, "1.98", navy),
      ), 2.17, note: [Fee 0.5% and interest 8% are assumed terms (report Section 5, Appendix K.4).]),
      [
        - The construction reserve is an average: in half the futures the plants call more than it.
        - The risk-aware book is the best of five ways to choose in 7 of 7 modelled worlds.
        - *Caveat:* with no facility at all, equal capital by sector wins (\$0.87B against \$0.76B).
      ],
      [+\$312M], [over ranking once every book is financed the same way #ci[\[+\$110M, +\$506M\]]]),
    finding("4", "Stage 4 · AI challenger", green,
      [Does a language model help the committee decide?],
      [Yes, as a challenger that argues, not as the one who decides.],
      bars("What each step adds to the committee's objective, $M per case", (
        ("Tools, no language model", 76, "+76", pale(green)),
        ("Language model on top", 43, "+43", green),
        ("Optimizer's own book", 134, "+134", grey),
      ), 134, note: [48 simulated committee proposals; from \$863M to \$1,116M per case (report Table 2).]),
      [
        - It named 12 of 12 flaws of argument, challenged 0 of 12 sound proposals and read 40 of 40 paraphrased rules exactly.
        - A fixed optimizer-first rule chose books as well (−\$14M): its value is the argument, not the pick.
        - It failed 2 registered lines (8 of 48 readings missed the tail weight; 15 of 20 injections held); the controls caught both. A named person signs.
      ],
      [+\$43M], [per case from the language model #ci[\[+\$9M, +\$86M\]]. Registered (C34)]),
  )
  #v(5mm)

  // ---- what to do, the lesson, the limits ---------------------------------------------------
  #grid(columns: (1.35fr, 1fr, 1fr), gutter: 8mm, rows: 58mm,
    block(width: 100%, height: 100%, inset: (x: 9mm, y: 5mm), radius: 5mm, fill: navy, [
      #text(size: 22pt, weight: "bold", fill: white)[What the committee should do on 1 January 2025]
      #v(1.5mm)
      #set text(size: 20.5pt, fill: white)
      #set enum(spacing: 3mm, body-indent: 2.5mm)
      + State the tail weight first; an unstated one is read as zero.
      + Fund the risk-aware book: 13 of 40 candidates, \$3.78B. Invest now in 8, in stages in 5.
      + Arrange a \$2.53B contingent construction facility.
      + Wait on 12 requests, monitor 14 leases, reject 1. Run the challenger before signing.
    ]),
    block(width: 100%, height: 100%, inset: (x: 9mm, y: 5mm), radius: 5mm, fill: white, stroke: 1.2pt + line-c, [
      #text(size: 22pt, weight: "bold", fill: navy)[Beyond prediction lies a discipline]
      #v(1.5mm)
      #set text(size: 21pt)
      #set list(marker: text(fill: navy)[▸], spacing: 3.2mm)
      - Simulate what you cannot forecast.
      - Optimize against the risk you are willing to bear.
      - Price the capital you will need.
      - Let AI argue with the decision-maker, not replace them.
    ]),
    block(width: 100%, height: 100%, inset: (x: 9mm, y: 5mm), radius: 5mm, fill: white, stroke: 1.2pt + line-c, [
      #text(size: 22pt, weight: "bold", fill: orange)[Read with care]
      #v(1.5mm)
      #text(size: 18.5pt)[Modelled, not realized returns. The committees are simulated, the lease costs assumed, the futures resample 2018–2024, and the primary result clears zero by only \$13M. 41 criteria and 87 lines were registered; 40 pass, and every failure is kept as scored.]
    ]),
  )
  #v(3.5mm)
  #text(size: 12.5pt, fill: muted)[Data: LBNL *Queued Up* 2025 and 2026 editions (Rand et al., 2025, 2026), ERCOT interconnection reports and hourly prices, BSEE lease production, EIA prices and generation, NREL ATB 2024; author's analysis. Methods: LightGBM discrete-time hazard models; block-bootstrap futures (Künsch, 1989); a mixed-integer program on expected NPV minus the worst-5% loss (Rockafellar & Uryasev, 2000). Numbers from the report, Version 2; each traces to `results/report_numbers.csv`. Code: github.com/alanmossinger/Capstone]
])
