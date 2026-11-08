// Poster V2 — Beyond Prediction, written to be explained in four minutes.
// Built with: typst compile --root . report/poster_V2.typ report/poster_V2.pdf
// Every number is one the edited V2 report prints (report/Beyond_Prediction_Edited_Full_Report_V2_revised.docx): sections 1–12 and Appendix M.
// The four columns are the report's four questions (Sections 4, 5, 6 and 8), in plain words, each answered by one stage of the system.
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
     #text(size: 21pt, fill: white.darken(12%))[A governed decision-intelligence system for risk, returns and investment-committee decisions across oil, gas, power, renewables and storage]],
    [#text(size: 18.5pt, fill: white)[*Alan Mössinger* \ SIADS 699 Capstone · University of Michigan \ MADS, Group 13 (a solo project) \ Mentor: Laura Danielle Stagnaro · November 2026]]
  )
])

#block(width: 100%, inset: (x: 20mm, y: 6mm), [
  // ---- the question and the answer ----------------------------------------------------------
  #grid(columns: (1fr, 1.55fr), column-gutter: 10mm, align: horizon,
    text(size: 33pt, weight: "bold", fill: navy)[Are good forecasts enough to spend a \$3.82 billion budget well?],
    text(size: 21pt, fill: ink)[*No.* The machine-learning model ranked projects better than a simple lookup, yet the portfolio built from it was not clearly better. The value came after prediction: modelling how projects lose money together, choosing the whole portfolio within the company's risk limits, arranging the money to build it, and an AI that questions the committee's reasoning while a person still decides.],
  )
  #v(5mm)

  // ---- the decision, in plain words ---------------------------------------------------------
  #grid(columns: (1fr, 1fr, 1fr, 1.15fr), gutter: 8mm, rows: 43mm,
    card("The decision · 1 January 2025", [\$3.82 billion to spread across 40 projects, using only what was public that day. No single technology may take more than 40% of the budget.]),
    card("20 Gulf of Mexico oil and gas leases", [Spend now to redevelop; output rises 20% after two years. They rarely lose money, but all sell the same oil, so when they lose, they lose together.], color: orange),
    card("20 Texas grid (ERCOT) requests", [New solar, wind, gas or storage plants: cheap to hold, expensive to build. Most never get built: of capacity that applied in 2000–2019, 12.6% was operating by 2024 and 76.9% had withdrawn.], color: blue),
    card("How to read the numbers", [*Worst-5% loss:* the average loss in the worst 5% of the simulated futures. *[a, b]:* the 95% range; if it includes zero, the gain is not proven. *Registered:* the pass rule was written before the result was seen.], color: green),
  )
  #v(5mm)

  // ---- how it works: the six stages (report Figure 1) ---------------------------------------
  #grid(columns: (auto, 1fr, 9mm, 1fr, 9mm, 1fr, 9mm, 1fr, 9mm, 0.75fr, 9mm, 0.95fr), rows: 21mm, column-gutter: 1mm,
    box(height: 100%, inset: (right: 4mm), align(horizon, text(size: 20pt, weight: "bold", fill: navy)[How it works])),
    step("1 Predict", [which plants get built, what each project produces], blue), arrow,
    step("2 Simulate", [2,000 futures of prices, output, cost and timing], blue), arrow,
    step("3 Optimize", [pick the portfolio within budget and risk limits], orange), arrow,
    step("4 Challenge", [an AI model questions the committee's reasoning], green), arrow,
    step("5 Decide", [a named person signs], grey), arrow,
    step("6 Score", [on 2,000 new futures], navy),
  )
  #v(5mm)

  // ---- four findings, the report's four questions -------------------------------------------
  #grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 8mm, rows: 314mm,
    finding("1", "Stage 1 · Prediction", blue,
      [Are better predictions enough?],
      [No. The model ranks well, but overestimates how many get built.],
      bars("Texas requests that started operating in 2025, of 1,441 waiting", (
        ("Model, as first fitted", 125, "125", pale(blue)),
        ("Model, corrected", 78, "78", blue),
        ("Simple lookup", 17, "17", grey),
        ([*What happened*], 30, "30", ink),
      ), 125, note: [Checked one year after the decision; nothing refitted (report Figure 3).]),
      [
        - *Ranking:* the model ordered requests better than the lookup (AUC 0.731 against 0.686; higher is better).
        - *Counting:* it gave a Texas request a 0.380 chance of operating within five years; 0.238 did.
        - Machine learning won 3 of 12 forecast contests, all for plant output. No price model beat "tomorrow looks like today".
      ],
      [+\$37M], [what the model's forecasts added to the portfolio: #ci[\[−\$76M, +\$151M\]], includes zero, *so not proven*]),
    finding("2", "Stages 2–3 · Risk", orange,
      [What happens when projects lose together?],
      [The losses pile up. Planning for them beats picking the highest values.],
      bars("Pick the highest values vs the risk-aware optimizer, $ billion", (
        ("Expected value · highest", 2.68, "2.68", grey),
        ("Expected value · risk-aware", 2.17, "2.17", orange),
        ("Worst-5% loss · highest", 1.55, "1.55", grey),
        ("Worst-5% loss · risk-aware", 0.82, "0.82", orange),
      ), 2.68, note: [Scored on 2,000 futures not used to choose (report Figure 4).]),
      [
        - Five leases ride one oil price, eight plants one power price. Break that link in the simulation and the worst-5% loss becomes a small profit.
        - The optimizer gave up \$508M of expected value to nearly halve the worst-5% loss.
        - It found a hedge that ranking never would: five cheap wind and solar deposits that pay when the leases do not.
      ],
      [+\$219M], [risk-adjusted value over picking the highest values #ci[\[+\$13M, +\$401M\]]. Registered test C33: passes, narrowly]),
    finding("3", "Stage 3 · Funding", navy,
      [What should the company actually fund?],
      [13 projects, and a credit line to build them.],
      bars("Expected value of the recommended portfolio, $ billion", (
        ("On paper", 2.17, "2.17", grey),
        ("No credit line", 1.71, "1.71", pale(navy)),
        ([With a \$2.53B credit line, after its cost], 1.98, "1.98", navy),
      ), 2.17, note: [Fee 0.5% and interest 8% are assumed terms, not a bank's offer (report Section 6).]),
      [
        - Five lease redevelopments and eight power requests: \$3.78B of the \$3.82B.
        - Building costs arrive in lumps: in half the futures the plants need more than was set aside.
        - It is the best of five ways to choose in all 7 modelled worlds. *Caveat:* with no credit line, an equal split by sector wins (\$0.87B against \$0.76B).
      ],
      [+\$312M], [over picking the highest values, when every portfolio gets its own credit line #ci[\[+\$110M, +\$506M\]]]),
    finding("4", "Stage 4 · AI challenger", green,
      [Can AI challenge a committee without replacing it?],
      [Yes. It argues well, but it does not pick better than the optimizer.],
      bars("Average gain per committee case, $M", (
        ("Checking tools, no AI", 76, "+76", pale(green)),
        ("AI challenger on top", 43, "+43", green),
        ("Optimizer's portfolio, beyond the AI", 134, "+134", grey),
      ), 134, note: [48 simulated committee proposals: from \$863M to \$1,116M per case (report Section 9).]),
      [
        - It spotted 12 of 12 flawed arguments, wrongly challenged 0 of 12 sound proposals, and read 40 of 40 reworded rules correctly.
        - A fixed "optimizer first" rule picked portfolios as well (AI edge −\$14M): its value is the argument, not the pick.
        - It failed 2 registered tests: 38 of 48 rules read exactly, and 15 of 20 planted instructions resisted. Human confirmation and a number checker caught both. A named person signs.
      ],
      [+\$43M], [per case from the AI, beyond the checking tools #ci[\[+\$9M, +\$86M\]]. Registered test C34: passes]),
  )
  #v(5mm)

  // ---- what to do, the lesson, the limits ---------------------------------------------------
  #grid(columns: (1.35fr, 1fr, 1fr), gutter: 8mm, rows: 58mm,
    block(width: 100%, height: 100%, inset: (x: 9mm, y: 5mm), radius: 5mm, fill: navy, [
      #text(size: 22pt, weight: "bold", fill: white)[What the committee should do on 1 January 2025]
      #v(1.5mm)
      #set text(size: 20.5pt, fill: white)
      #set enum(spacing: 3mm, body-indent: 2.5mm)
      + Say first how much downside you will accept; if it is left unstated, it is read as none.
      + Fund the risk-aware portfolio: 13 of 40 projects, \$3.78B. Invest now in 8, in stages in 5.
      + Arrange a \$2.53B standby credit line for construction.
      + Wait on 12 requests, watch 14 leases, reject 1. Run the challenger before signing.
    ]),
    block(width: 100%, height: 100%, inset: (x: 9mm, y: 5mm), radius: 5mm, fill: white, stroke: 1.2pt + line-c, [
      #text(size: 22pt, weight: "bold", fill: navy)[Beyond prediction is a decision discipline]
      #v(1.5mm)
      #set text(size: 21pt)
      #set list(marker: text(fill: navy)[▸], spacing: 3.2mm)
      - Test the forecasts; simulate what you cannot forecast.
      - Optimize within the company's own risk limits.
      - Finance what you commit to.
      - Let AI question the reasoning; a person signs.
    ]),
    block(width: 100%, height: 100%, inset: (x: 9mm, y: 5mm), radius: 5mm, fill: white, stroke: 1.2pt + line-c, [
      #text(size: 22pt, weight: "bold", fill: orange)[Read with care]
      #v(1.5mm)
      #text(size: 18.5pt)[These are modelled results, not real returns. The committees were simulated, lease costs and loan terms assumed, and the futures replay 2018–2024 markets. The main result clears zero by only \$13M. 41 criteria covering 87 tests were set in advance; 40 pass, and every failure stays on the record.]
    ]),
  )
  #v(3.5mm)
  #text(size: 12.5pt, fill: muted)[Data: LBNL *Queued Up* 2025 and 2026 editions (Rand et al., 2025, 2026), ERCOT interconnection reports and hourly prices, BSEE lease production, EIA prices and generation, NREL ATB 2024; author's analysis. Methods: LightGBM discrete-time hazard models; block-bootstrap futures (Künsch, 1989); a mixed-integer program on expected NPV minus the worst-5% loss (Rockafellar & Uryasev, 2000). Numbers from the report, Version 2 (revised); each traces to `results/report_numbers.csv`. Code: github.com/alanmossinger/Capstone]
])
