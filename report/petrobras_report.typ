// Petrobras Report — the executive edition of report v9. Built by `make petrobras` (typst) into report/Petrobras_Report.pdf.
// Every number is one the report prints (results/report_numbers.csv); tests/test_report.py checks this file too.
// The figures are the executive SVGs of figures/executive/, placed where the text discusses them.

#let blue = rgb("#1F4E79")
#let green = rgb("#008542")
#let red = rgb("#C00000")
#let ink = rgb("#222222")
#let muted = rgb("#595959")
#let title = "Beyond Prediction: AI-Driven Energy Portfolio Decisions Under Uncertainty"
#let short = "AI-Driven Energy Portfolio Decisions · A. Mössinger · October 2026"

#set text(font: "Calibri", size: 10.5pt, fill: ink)
#set par(justify: true, leading: 0.62em, spacing: 0.9em)
#set page(
  paper: "us-letter", margin: (x: 1in, top: 0.95in, bottom: 0.9in),
  header: context {
    if counter(page).get().first() > 1 { align(right, text(fill: red, size: 8pt, weight: "bold")[INTERNAL — CONFIDENTIAL]) }
  },
  footer: context {
    if counter(page).get().first() > 1 {
      text(size: 8pt, fill: muted)[#short #h(1fr) Page #counter(page).display() of #counter(page).final().first()]
    }
  },
)
#set heading(numbering: none)
#show heading.where(level: 1): it => { v(10pt); block(sticky: true, text(fill: blue, size: 16pt, weight: "bold")[#it.body]); v(6pt) }  // sticky: never the last line of a page
#show heading.where(level: 2): it => { v(6pt); block(sticky: true, text(fill: blue, size: 12.5pt, weight: "bold")[#it.body]); v(3pt) }
#show figure.caption: it => block(width: 100%, align(left, text(size: 9pt, style: "italic", fill: muted)[#it]))
#show figure: set block(breakable: false, above: 10pt, below: 10pt)
#show table: set block(breakable: false)  // short tables stay whole, so a floated figure never splits one

#set figure(gap: 6pt)
#show table: set text(size: 9.2pt)
#show table.cell.where(y: 0): set text(weight: "bold")
#set table(stroke: (x, y) => if y == 0 { (bottom: 0.8pt + ink) } else { (bottom: 0.3pt + rgb("#BBBBBB")) }, inset: 5pt)
#show link: set text(fill: blue)

// a figure from figures/, full text width, with the finding as caption and the consequence for the committee
#let fig(path, caption, consequence, width: 88%) = figure(
  placement: auto,  // floats to the top or bottom of a page, so an unbreakable figure leaves no half-empty page
  image("../figures/executive/" + path.split("/").last(), width: width),  // the executive copy: the finding and one line inside, the source in the caption
  caption: [#caption #text(fill: ink)[_Business consequence:_ #consequence]],
)
#let callout(body) = block(width: 100%, inset: 9pt, radius: 3pt, fill: rgb("#EEF3F8"), stroke: (left: 2.5pt + blue))[#text(size: 10pt)[#body]]

// ===================================================================== cover
#page(header: none, footer: none)[
  #v(2.6in)
  #align(center)[
    #text(fill: green, size: 13pt, weight: "bold")[PETROBRAS] \
    #v(2pt) #text(size: 9pt, fill: muted)[Strategic Advisory · Artificial Intelligence]
    #v(14pt) #line(length: 60%, stroke: 0.6pt + muted) #v(14pt)
    #text(fill: blue, size: 20pt, weight: "bold")[#title]
    #v(8pt)
    #text(size: 11pt, style: "italic", fill: muted)[From prediction to a challenged, human, measured decision — a working proof on public data, an AI challenger that tests the committee's own proposal, and its application to Petrobras.]
    #v(1.5in)
    #text(fill: red, size: 10pt, weight: "bold")[INTERNAL — CONFIDENTIAL] \
    #v(4pt)
    #text(size: 9.5pt)[Author: Alan Mössinger — Strategic Advisor, AI & Energy] \
    #text(size: 9.5pt)[Distribution: Executive Committee] \
    #text(size: 9.5pt)[October 2026]
  ]
]

= Cover letter

To the Executive Committee,

Every consequential decision Petrobras makes shares one structure: commit capital now, under uncertainty, and be able to defend the decision later — to our own controls, to the TCU and CGU, and to the market through our SEC filings. The question that decides whether artificial intelligence creates value or risk in that structure is no longer whether a model is accurate. It is whether a committee can trust a recommendation it did not compute, whether the committee's own reasoning is tested before it signs, and whether the record shows afterwards what it knew, what it assumed and why it decided.

This report presents a complete, working answer, built end to end on public data so that every number can be checked. The problem is one Petrobras faces in its own terms: one capital budget on 1 January 2025, split between assets that already produce — twenty offshore Gulf of Mexico lease redevelopments — and projects that may never be built — twenty power requests waiting in the Texas (ERCOT) interconnection queue. Only what was public that day is used. The system predicts which requests get built and when, draws 2,000 joint scenarios of prices, output, costs and timing, allocates the budget with a stated appetite for the tail, and then challenges the committee's own proposal before a named person decides.

Four results matter for this Committee. First, there is no single right book, only a trade-off to price: the risk-aware book expects \$2.05B with a worst-5% loss of \$1.02B, the return-seeking book \$2.36B with \$1.60B. Second, the capital plan is the weak point: construction calls exceed the reserve in 44.5% of scenarios, and without a contingent line the book is worth \$1.40B, not \$2.05B. Third, better predictions did not by themselves produce a better decision: the machine-learning queue model ranks requests better than a simple lookup, yet the book built on it is not demonstrably better. Fourth, an AI challenger that tests the committee's own proposal with computed tools improved the committee's own objective by \$192M per flawed proposal and avoided \$240M of worst-5% loss — though the same tools without the language model achieved most of that. What only the language model adds is understanding the committee: reading its rules from its words and naming flaws of argument that numbers cannot see.

The dollars belong to a demonstration portfolio, not to a Petrobras forecast. What transfers is the chain — registered criteria, provenance on every figure, a scenario engine that keeps history's shocks, an optimizer with a stated risk appetite, a challenger whose every number is checked, and a ledger that records who decided and why — and that chain describes our mature-field revitalization, our thermal and transition portfolio and our capital program equally well.

I submit it as a working artifact for the Committee's consideration: every number in it can be reproduced from public files, and every exchange with the language model is on the record.

Respectfully,

*Alan Mössinger* \
Strategic Advisor — AI & Energy \
#text(size: 9.5pt, fill: muted)[Master of Applied Data Science candidate, University of Michigan]

#pagebreak()
= Contents
#outline(title: none, depth: 2, indent: 1.2em)

#pagebreak()
= Executive summary

Petrobras allocates capital under uncertainty for a living. A mature field to revitalize, a thermal plant to build, a renewable project waiting for its grid connection: each is a forecast of an uncertain future, a decision constrained by physics, contracts and a budget, and an obligation — statutory in our case — to explain the decision afterwards. The frontier is no longer the forecast. It is the decision built on it, the challenge the decision survives, and the record that makes it defensible.

#fig("F43_architecture.svg", [The decision workflow in six stages — prediction, uncertainty, prescription, AI challenge, the human decision and the measured outcome — and what is measured on the same held-out scenarios.], [the language model works in one stage only: it reads and argues, and never computes a value or decides; everything it says is checked against computed facts.])

The headline results, all reproduced by code from the public files:

- *The trade-off.* At the registered tail weight the risk-aware book expects \$2.05B with a worst-5% loss of \$1.02B and a 10% chance of losing money; the return-seeking book expects \$2.36B with \$1.60B; a defensive book \$1.55B with \$0.52B. The committee must choose its appetite first.
- *The risk-aware book wins under equal constraints.* Held to the same budget and cap, it beats ranking by NPV by \$320M on the registered risk–return metric, giving up \$274M of expected value for a thinner tail, and keeps winning when re-chosen on 20 resampled scenario sets.
- *The capital plan needs a contingent line.* Construction calls exceed the reserve in 44.5% of scenarios; a line of \$3.28B restores \$2.02B of the book's value.
- *Machine learning does not demonstrably improve this decision.* The book chosen with the lookup's queue curves is not beaten on the registered metric; the decision turns on a few large requests whose chance of operating neither method knows well.
- *The AI challenger improves the committee's decision, mostly through its tools.* On 36 flawed committee proposals, following it raised the committee's own objective by \$192M per case and avoided \$240M of worst-5% loss; a checklist with the same tools and no language model achieved \$145M and \$257M. The language model named 11 of 12 flaws of argument the checklist cannot see and read 40 of 40 rules correctly; it over-challenged 2 of 12 sound proposals.

#callout[*The recommendation* is deliberately modest in scope and specific in mechanics: adopt the governed decision loop — registered criteria, provenance, scenarios, a stated risk appetite, a contingent capital line priced with the book, and a challenger that tests the committee's proposal on the record — on one Petrobras capital decision, then scale it through the structures the company already operates. The reference implementation runs end to end offline; verification is an analyst-week, not a procurement cycle.]

= Purpose and context

Why should governed, prescriptive decision-making be an executive concern in 2026, rather than a technical one delegated downward? Three developments answer that.

- *The transition has made capital allocation a portfolio problem across asset classes.* A producing field, a gas plant, a wind farm and a battery no longer compete inside their own divisions; they compete for the same budget, under correlated prices, with very different odds of being built on time. A company that prices them on separate bases, or that treats a modelled value as an observed one, will allocate to the assumption rather than to the asset.
- *The credibility of model-projected value has become the bottleneck.* The question asked of every AI business case has shifted from "how much" to "can I trust the number" — and a methodology that registers its criteria before scoring, labels the provenance of every figure and shows its failures is itself a competitive asset.
- *Oversight expectations have hardened into obligations.* Record-keeping, human oversight, monitoring and reversibility are the entry ticket for deploying decision-making AI at a state-controlled, SEC-listed company. A language model that cannot show what it read, what it cited and who decided against it is a liability, however fluent.

This project was built to demonstrate, with running code, that all three concerns can be answered at once. The next sections walk through how, in the order the decision is made.

#callout[*How to read the figures.* Every figure states its finding in its title and its method in one line beneath; the caption says what the figure shows and what it means for the Committee. The queue figures rest on the Lawrence Berkeley National Laboratory's _Queued Up_ files; the energy figures on BSEE production, EIA generation and prices, ERCOT settlement prices and the NREL Annual Technology Baseline — all public. Every number is OBSERVED (a public record), DERIVED (arithmetic on records), FORECAST (a model's output) or ASSUMED (a stated assumption); the captions say where a figure rests on an assumption. Portfolio dollars are 2024 dollars. Intervals are drawn wherever a number is uncertain.]

// ===================================================================== stage 1
= Stage 1 — The decision and the data

The decision is taken on 1 January 2025 with only what was public that day: lease output to September 2024, interconnection agreements as the 2025 edition of the queue file dates them, and the tax credits of the law then in force. An independent audit of an earlier version found five errors that no test of forecast accuracy would have caught — among them comparison books held to different constraints and power candidates already withdrawn or built — and a later review removed three inputs that were not yet public on the decision date. Every result below is on the corrected system.

#fig("F9_project_map.svg", [Requests waiting in U.S. queues at the end of 2024 by county (left; area proportional to MW) and the operating fleet (right).], [the capacity waiting to connect is larger than the fleet that operates; where a project sits decides its odds before any model is run.])

The forty candidates are the twenty leases with the most output in the twelve months published by the decision date, among the 506 producing in 2024, and the five largest requests of each technology — gas combined cycle, solar, wind, storage — among the 1,649 ERCOT requests of 20 MW and more still waiting on that day, about 359 GW. Most of the twenty requests are recent entrants of 500 MW and more, the size and age at which requests are least likely to operate, so their chances sit far below the queue's averages unless an agreement is signed.

// ===================================================================== stage 2
= Stage 2 — Will it be built, and when: the queue engine

A developer who wants to build a power plant must first ask the grid operator for a connection. The request enters a queue and leaves years later as an operating plant or a withdrawal; most leave as withdrawals. Every request costs money to keep alive, so the first decision is which requests to fund, which to hold and which to drop.

== Where the opportunity is, and what decides the odds

#fig("F1_cif_by_region.svg", [Share of requests operating (and withdrawn) by years since the request, by region; Aalen–Johansen estimates with 95% intervals.], [ERCOT is where requests get built — 18.4% of entrants operate within five years against 4.8% in CAISO — so the region decides the base rate before the project does.])

The regions also run on different clocks: 48% of CAISO's waiting requests leave in their first year, while ERCOT culls late, after year four. Size, technology and the agreement decide the odds, and they can be read off public records without a model. On the 5,497 entrants of 2010–2019, five-year completion runs 12.8% overall; in PJM it falls from 24% for requests under 5 MW to 4% at 500 MW and up. The executed interconnection agreement dominates everything: where the file dates one within two years of the request, 63% of ERCOT's requests were operating within five years; where none is dated, 0.8%.

#fig("F19_drivers.svg", [Five-year completion by six drivers within each region, 2010–2019 entrants, 95% Wilson intervals.], [an investment committee can screen requests on size, technology and the agreement before paying for a model; the agreement alone separates a 63% chance from a 0.8% one.])

== What a model adds at entry, two years in, and on the decision date

Three predictors were compared, always in the same order: *the model*, a gradient-boosted discrete-time hazard model that sees only what is known on the request date; *the lookup*, the share built among earlier requests of the same region, technology and size — what a careful analyst computes by hand; and *the cohort average*. At entry the model beats cohort averages (AUC 0.86 against 0.73 at three years) but ties the lookup at utility scale. Two years in, with the agreement known, the landmark model ranks the next three years at a concordance of 0.80 against 0.69 for the entry model, while the lookup falls to 0.59; a book of 25 it chose held 19 requests that reached operation, against 11 for the lookup.

#fig("F18_managed_book.svg", [Operations and MW realised within three years of the two-year landmark, for books of 25 and 50 chosen by the landmark model, the agreement-aware lookup, the entry lookup and at random; 95% intervals.], [the review moment is worth more than the model; a company that re-scores at the milestone holds more of the plants that get built.])

For the 2025 decision the models were refitted on what was known on each of two earlier dates and scored on what followed. As of 2020 the model ranked better than the lookup (AUC 0.731 against 0.686) but put ERCOT's five-year chance at 0.380 where 0.238 operated. That ratio, knowable on the decision date, corrects the 2025 curves. Every cohort since 2017 completes below the model's level — 11.0% of 2017 entrants of 20 MW and more operated within five years against about 12% predicted — so a book must be sized to the newest cohort, not to the model.

== Fund, hold or exit: the gates, scored on what happened

The rules are two gates. At entry and two years in, the company compares the chance the request operates, its value if it does, and the cost of the next gate. It *funds* when the chance is at least the pool's expected rate and the value is at least _h_ times the cost — _h_ is 3 at entry and 2 two years in; it *exits* when the chance is well below the pool or the value is negative even in the best case; it *holds* otherwise.

#table(
  columns: (2.2fr, 0.9fr, 0.9fr, 0.9fr, 1.3fr, 1.3fr, 1.4fr),
  [Gate, revenue], [Funded], [Held], [Exited], [Funded, operated], [Exited, operated], [Funded value, \$M],
  [Entry, merchant], [166], [560], [1,542], [33%], [6%], [+4,079],
  [Entry, contracted], [203], [550], [1,515], [29%], [6%], [+9,137],
  [Two years in, merchant], [178], [620], [500], [29%], [7%], [+3,642],
  [Two years in, contracted], [251], [554], [493], [30%], [7%], [+8,975],
)

At entry the funded requests were built three times as often as the cohort; two years in, the accelerated requests were built four times as often as the exits.

#callout[*The rule, region by region.* _ERCOT:_ invest; enter wind, enter solar with a contract, hold storage, and review every request at the agreement. _PJM:_ invest in gas, wind and solar, prefer the light queues and requests under 66 MW, and review after the system impact study. _CAISO:_ hold capital; enter only with a signed agreement and a contract. Every rule here was scored on the 2017–2019 requests after it was written.]

// ===================================================================== stage 3
= Stage 3 — What each candidate is worth, and what that rests on

== Forecasts: machine learning helps for plants, not for leases

Every feature is built only from what was public at the forecast date, and a truncation test proves it. Twelve forecast lines were registered before scoring; three pass, all for plant capacity factors. The lease lines fail — the registered challenger's error at three months is 1.35 times the last-value baseline's — and prices behave as random walks.

#fig("F27_forecast_gains.svg", [Forecast error of the challenger relative to the best baseline, by registered line, with paired moving-block bootstrap intervals.], [machine learning helps where there is a seasonal shape to learn; where a decline curve already carries the physics, the honest answer is that it does not.])

== Two kinds of asset, one valuation

A lease redevelopment is an uplift on a producing asset: an Arps decline baseline fitted after the lease's peak, declining at least 8% a year, a 20% uplift after a two-year lead time, and the value of the cash flow it adds over doing nothing. Redevelopment costs are not public, so every result is shown under two grids: the registered grid fixed before any result, and the harder *committee grid*, which prices capital at \$40,000 per incremental flowing barrel of oil equivalent a day and discounts at 8%.

#table(
  columns: (2.2fr, 1fr, 1fr),
  [Twenty leases, flat 2024 prices], [Registered grid], [Committee grid],
  [Capital], [\$1.35B], [\$5.12B],
  [Incremental NPV, base], [\$8.19B], [\$2.73B],
  [Incremental NPV, low and high grid cases], [\$5.69B and \$5.10B], [\$4.77B and −\$4.77B],
  [Leases positive at the high case], [19 of 20], [0 of 20],
)

A power request is a plant that may never be built. Its value if built uses the 2024 hourly prices — solar earns 92% of the flat hub price, wind 83%, gas combined cycle 136% because it runs only when prices clear its fuel cost — with ATB costs and the tax credits of the law in force, weighted by the chance of operating in each of seven years and net of the deposits. On the flat 2024 path, under contract, all ten wind and solar requests are positive (+\$70M together) — but only with the credits: −\$615M without them, −\$284M under the 2027 deadline a July 2025 law later set. Every gas and storage request is negative on that path.

#fig("F28_candidates.svg", [The forty candidates: incremental NPV of the lease redevelopments and timing-weighted expected NPV of the ERCOT requests. Lease costs are ASSUMED; production is FORECAST.], [the leases carry the book; wind and solar earn their capital only under contract and with the credits in force; the chance of never operating is the power side's cost.])

== Scenarios and risk

Prices, output, costs and timing are drawn together. 2,000 joint twenty-year paths resample calendar-year blocks of the 2018–2024 monthly changes of WTI, Henry Hub and ERCOT prices, the same months for all three, so a spike stays with its reversal; they revert toward their means with a four-year half-life (ASSUMED). A second set of 2,000 paths, redrawn in every component, is used only to score books. Seven historical years are thin material for a twenty-year tail, and the reversion lifts gas and ERCOT prices well above 2024's — which is what makes the gas requests valuable in the scenarios.

// ===================================================================== stage 4
= Stage 4 — Allocating the budget

The budget is the registered rule: 40% of what the forty candidates charge it today, \$3.42B, with no technology above 40%. A lease spends its capital now; a request needs only its deposits now, plus a reserve for the construction it will call if it reaches its agreement. The risk-aware book maximises expected NPV minus a weight times the worst-5% average loss, solved exactly; the conventional books — ranking by expected NPV, and equal capital by sector — are held to the same budget and cap.

#fig("F38_frontier.svg", [The frontier over risk policies on held-out scenarios, the registered books on it, and capital by technology along it.], [there is no single right book, only a trade-off; the committee should choose its tail weight first and the book second.])

#table(
  columns: (2.4fr, 1fr, 1fr, 1.1fr, 1fr, 1fr),
  [Committee grid, held-out], [NPV ranking], [Equal capital], [Determin\-istic], [Risk-aware], [Lookup curves],
  [Candidates funded], [16], [16], [17], [13], [18],
  [Expected NPV, \$B], [2.33], [2.08], [2.36], [2.05], [1.84],
  [Worst-5% loss, \$B], [1.61], [1.26], [1.60], [1.02], [0.83],
  [Chance of a loss], [13%], [12%], [13%], [10%], [9%],
  [Regret against perfect information, \$B], [0.60], [0.84], [0.57], [0.87], [1.08],
)

Under equal constraints the risk-aware book beats NPV ranking by \$320M \[+\$142M, +\$511M\] and equal capital by \$213M on the registered metric, while giving up \$274M of expected value against NPV ranking. Re-chosen on 20 resampled scenario sets it beats NPV ranking every time, by \$116M to \$352M; 11 of its members are chosen in at least 80% of them.

#fig("F42_value_added.svg", [Each decision process against its comparator on the same held-out scenarios, with paired bootstrap intervals.], [the risk-aware book buys a thinner tail with expected value; the machine-learning forecasts and the 2027 revision add nothing that the intervals can distinguish from zero.])

*Machine learning does not demonstrably improve this decision.* The book chosen with the model's queue curves scores +\$22M \[−\$168M, +\$207M\] against the book chosen with the lookup's; the interval includes zero. The model ranks requests better, but the decision turns on a few large requests whose chance of operating neither method knows well. The simpler forecast is enough here.

== What drives value and downside

The risk-aware book holds six leases and seven requests. The position whose removal costs the most is an 836 MW wind request with a signed agreement: forcing it out lowers the objective by \$549M. The largest power position, a 1,350 MW gas request, expects \$512M yet loses money in 77% of scenarios; its place is worth only \$7.7M at the registered tail weight.

#fig("F39_reallocation.svg", [The risk-aware book's capital by technology, re-solved under each committee question.], [cheaper oil or dearer redevelopment removes every lease; calmer ERCOT prices remove the gas request — the book's least secure line rests on price spikes recurring.])

#callout[*What would change it.* Oil at \$45 a barrel for five years, or redevelopment capital 30% higher, removes every lease from the book. The two largest power positions rest on ERCOT prices spiking as they did in 2021 and on prices reverting upward from 2024's low level.]

// ===================================================================== stage 5
= Stage 5 — Capital, timing and information

== The capital plan is the weak point

The construction reserve is an average. The capital the book's requests actually call exceeds it in 44.5% of held-out scenarios, and in one scenario in twenty the excess is \$3.28B or more. Without a contingent line, requests that reach their agreement cannot be built and the book is worth \$1.40B, not \$2.05B; a line at that size restores \$2.02B.

#fig("F45_robustness.svg", [Left: the book's construction calls beyond its reserve on held-out scenarios. Right: how often each candidate is chosen when the book is re-chosen on 20 resampled scenario sets.], [the commitment is the stage-one budget plus a contingent construction line, priced with the book — not the budget alone.])

== What to do with each candidate

Invest now in six leases and two requests with signed agreements. Invest in stages in five requests: pay the deposit now, commit construction at the agreement. Wait for information on thirteen requests whose agreement signal is worth more than their deposit. Monitor thirteen; reject one.

== Revising later, and what information is worth

Revising the book on 1 January 2027, after two years of prices and agreement signals, is worth −\$9M on held-out scenarios: the cap leaves no room to start a deferred lease, so the revision can only drop requests, and its estimates drop some that would have paid. This says the revision rule's estimates are noisy, not that flexibility has no value. Perfect knowledge before committing would be worth at most \$571M; knowing the 2025–2029 ERCOT price level, \$52M; one request's agreement signal, at most \$11.5M.

// ===================================================================== stage 6
= Stage 6 — The AI layer: an advisor, a challenger and a person who decides

The language model never produces a number the decision uses. It does two jobs, and a named person decides.

#fig("F44_advisor_tools.svg", [The path of a committee question through the advisor: translation into parameters, validation, computation, the fact sheet, the explanation, the check, the decision and the ledger.], [the advisor cannot invent a number or run without a trace; a question it cannot represent is refused, not answered.])

*The advisor answers questions.* A committee question in words becomes parameters from a fixed schema, or a refusal if the model cannot represent it. The engine validates the parameters and re-solves; the language model explains only the computed fact sheet, and a checker holds every number to that sheet in its unit. All six committee questions were read correctly — five into parameters, the sixth, about interest rates, refused as outside the model — and its five explanations cited 119 numbers, all in the computed fact sheet. Its investment increment is zero: the book is the optimizer's.

*The challenger questions the committee.* First, the language model reads the committee's statement into rules — tail weight, chance-of-loss and tail limits, exclusions, a liquidity line — and may ask the engine to test up to two of the committee's beliefs as what-ifs. Then tools, not the language model, diagnose the proposal on held-out scenarios — the rules it breaks, the construction calls it cannot fund, the members that lose in most scenarios — and compute two alternatives under the committee's own rules: the fewest changes that make the proposal keep its rules, and the optimizer's book. Finally the language model writes a memo: at most three vulnerabilities, each tied to numbered facts and typed; a level — explain, challenge or guide; the loss the change avoids; and what would change its mind. Code checks every number and lets it guide only toward an alternative that keeps every rule and either repairs a broken one or beats the proposal with an interval clear of zero.

*A person decides.* The committee sees its rules read back as numbers before anything is computed. Leaving a book the challenger guided toward is allowed, but the ledger records the decision only with the contrary evidence acknowledged, and each row is chained to the one before so an edited row is detected.

// ===================================================================== stage 7
= Stage 7 — Does challenging the committee improve its decision?

I tested the challenger before trusting it. I wrote 48 committee proposals from ten personas: 36 carry one flaw — a broken rule, unfunded construction calls, a fragile position, a sunk cost, a double standard or an unsupported claim — and 12 are sound. Each flawed proposal ends as the committee's book under three policies: keep it; follow a checklist that uses the same tools with fixed rules and no language model; or follow the challenger. Each is scored on the committee's own objective in five worlds, from the base model to ERCOT prices 25% lower and lease capital 30% higher. The cases, the prompts and the model were fixed and recorded before the first call; 6 of 8 registered tests pass.

#fig("F46_challenger.svg", [Left: flaws named, by type, by the challenger and by the checklist. Right: the committee's objective and the loss avoided, per flawed case, with case-bootstrap intervals.], [challenging is worth doing before every signature; most of its value comes from the computed tools, and the language model's part is to understand the committee's rules and arguments.])

#table(
  columns: (2.6fr, 1.6fr, 1.6fr),
  [48 committee cases], [Challenger], [Checklist, no language model],
  [Computable flaws named], [24 of 24], [24 of 24],
  [Flaws of argument named], [11 of 12], [0 of 12],
  [Sound proposals over-challenged], [2 of 12], [0 of 12],
  [Committee objective against its proposal, per case], [+\$192M \[+\$108M, +\$281M\]], [+\$145M],
  [Worst-5% loss avoided, per case], [\$240M \[+\$133M, +\$345M\]], [\$257M],
  [Rules read from words], [40 of 40], [—],
)

- *Yes — and it mostly avoids loss.* The challenged books stayed near break-even on the committee's objective where the model was wrong in the proposal's disfavour, while the proposals lost.
- *Most of the gain is the tools'.* The challenger's further \$46M over the checklist came from four cases in which it chose the optimizer's book where the checklist takes the smaller repair; a fixed rule that prefers the optimizer's book does as well (+\$1M).
- *What only the language model adds is understanding.* It named 11 of the 12 flaws of argument — a sunk cost, a double standard, a belief no fact supports — which live in the committee's words, and it read every rule it could represent and refused every one it could not, from a carbon price to a partner's appetite. In this test that understanding did not change what was bought: every flaw of argument that warranted a different book also broke a computed rule. A test in which only the argument is wrong is the next experiment.
- *It has costs.* It challenged 2 of the 12 sound proposals with a claim they did not earn, and 10 of 48 memos carried a number not on their fact sheet — listed beside the memo by the checker, never used by the engine.

#callout[*Why this is the right shape for Petrobras.* The challenger never decides; the committee does. But the committee decides after seeing its own rules read back as numbers, after hearing where its proposal breaks them and what the computed alternative is, and with every number it was shown traceable to a computed fact. That is the difference between an AI that flatters a decision and one that tests it — and the record is what an auditor asks for.]

#pagebreak()
= Results at a glance

#table(
  columns: (1.3fr, 3fr, 1fr),
  [Question], [Finding], [Verdict],
  [Where to look], [ERCOT builds most often: 18.4% of requests operate within five years, against 4.8% in CAISO.], [Observed],
  [Predict, at entry], [The model beats cohort averages (AUC 0.86 against 0.73) but ties the lookup at utility scale.], [Partly],
  [Predict, two years in], [A book of 25 chosen by the landmark model held 19 operations, against 11 for the lookup.], [Supported],
  [Predict, on the decision date], [Backtested as of 2020 the model ranks better than the lookup (AUC 0.731 against 0.686) but over-predicts ERCOT's level.], [Supported for ranking],
  [Forecast output], [Machine learning beats baselines for plant output, not for leases or prices.], [Partly],
  [Does ML change the decision?], [The book chosen with the lookup's curves is not beaten on the registered metric.], [Not supported],
  [Allocate], [Under equal constraints the risk-aware book beats NPV ranking by \$320M on the registered metric, for \$274M of expected value.], [Post-registration],
  [Capital], [Construction calls exceed the reserve in 44.5% of scenarios; without a line the book is worth \$1.40B instead of \$2.05B.], [Post-registration],
  [Information], [Perfect information is worth at most \$571M; the ERCOT price level \$52M; an agreement signal at most \$11.5M.], [Post-registration],
  [The advisor], [It read six questions correctly and cited only computed numbers; its investment increment is zero.], [Post-registration],
  [The challenger], [Following it improves the committee's objective by \$192M per flawed case and avoids \$240M of worst-5% loss; the checklist achieves \$145M and \$257M.], [Post-registration],
  [The language model], [It names 11 of 12 flaws of argument and reads 40 of 40 rules; against a fixed rule its decision value is +\$1M.], [Post-registration],
)

// ===================================================================== petrobras
= Why this matters for Petrobras

Strip away the market specifics and the system above is a template: (1) a timing engine that turns "will it be built" into a probability; (2) a valuation that carries its assumptions in the open, with a committee grid beside the registered one; (3) a scenario engine that keeps history's shocks and correlations; (4) an optimizer with a stated risk appetite and a priced capital line, scored on held-out scenarios against criteria registered first; and (5) a challenger that reads the committee's rules, tests its proposal with computed tools and records who decided and why. Written that way, it is not a description of a Texas queue and a Gulf lease. It is a description of Petrobras's capital program.

Consider the correspondences. A Gulf lease redevelopment is a mature-field revitalization in the Campos basin: an uplift on a producing asset, whose value is decided by the uplift share, the operating cost and the capital per incremental barrel — the committee grid's items. A queue request is a transition project waiting on a grid connection, a licence or a partner: a plant that may never be built, whose value must be weighted by the chance it operates and by when, and whose construction calls arrive only if it does. The joint scenarios are the Brent, gas and power paths every investment case already carries, drawn together rather than one at a time. And the committee grid is our own investment committee's prices, which this report shows can cut the lease book from \$8.19B to \$2.73B and turn every lease negative at its high-cost case.

What the company has not yet institutionalized — what almost no company has — is the full governed loop: criteria written before scoring and failures reported as registered; provenance on every figure a committee sees; a stated risk appetite instead of an implicit one; and an AI challenger that reads the committee's own words, must cite computed facts, may guide only when the evidence allows, and can be overruled only with the evidence acknowledged on the record. That is the specific capability this reference implementation demonstrates end to end.

== The transfer map

#table(
  columns: (1.2fr, 1.6fr, 1.6fr, 1.4fr),
  [Domain], [The "will it happen, and when"], [The decision], [The audit stake],
  [Mature-field revitalization], [Decline baseline and uplift; capital per incremental barrel], [Which fields, in what order, under one budget and a tail limit], [Reserves governance; SEC Form 20-F; TCU/CGU review of public-asset value],
  [Transition power projects], [Chance of reaching operation by year; contract against merchant], [Fund, hold or exit at each gate; stage construction at the agreement], [Investment-decision records; partner and lender diligence],
  [Thermal and gas-to-power], [Joint price scenarios with the spikes kept], [Dispatch, hedges and the capacity to hold], [Trading compliance; transfer pricing],
  [The capital program], [One budget across the classes above, with its contingent line], [The book, its risk appetite and its horizon, stated, challenged and scored], [The investment committee's own record of what it knew, assumed and overrode],
)

// ===================================================================== management model
= Driving executive decisions: the management model

A decision system of this kind yields a small set of standing, executive-legible instruments — few enough for a monthly committee page, each demonstrated in the reference build:

- *The book and its tail (are we taking the risk we said we would?).* Expected value, the chance of a loss and the worst-5% average, on held-out scenarios, under the registered grid and the committee's. Movements in the tail, not in the mean, are what warrant executive attention.
- *The capital line (can we fund what the book will call?).* The construction calls beyond the reserve, scenario by scenario, and the contingent line that funds them; a book whose calls cannot be met is worth what the calls leave of it.
- *The register (did we decide the test before the result?).* Criteria written and committed before scoring, with failures reported as registered: 28 of 70 lines pass across the original record, and 6 of 8 for the challenger.
- *Provenance (which number is an assumption?).* Every figure labels OBSERVED, DERIVED, FORECAST or ASSUMED; a book that rests on an ASSUMED cost is presented as such, with the committee grid beside it.
- *The challenge record (what was tested, what was guided, who overrode it?).* The rules the committee stated, the flaws the challenger named, the books it guided toward, the numbers the checker refused, and every departure with its evidence acknowledged — the audit trail of every decision.

These instruments slot into the structures Petrobras already operates: the investment committee reviews the book, its tail and its capital line, and the data and AI function owns the reference implementation. No new committee is required; what changes is that the committee reviews a stated risk appetite, a register and a ledger instead of a pilot narrative.

#callout[*One cultural instrument matters as much as the quantitative ones.* A result that looks too good is a risk to investigate, not a success to announce. This project encodes that norm: an independent audit found that the earlier version's recommendation rested on errors no accuracy test would catch, a later review removed inputs that were not yet public on the decision date, and both corrections were made before this report.]

// ===================================================================== recommendations
= Recommendations and next steps

The recommendation is deliberately modest in scope and specific in mechanics: prove the governed decision loop on one Petrobras capital decision, then scale what works through the structures that already exist.

+ *Phase 1 — Diagnostic (about six weeks).* Select one recurring capital decision — the transfer map's strongest candidates are mature-field revitalization ranking and the transition power portfolio — and run a structured diagnostic: define the decision moment, inventory what is knowable at it, write the cost grid with its ranges and the criteria that will score the books, and state the risk appetite and the liquidity the company can commit. Deliverable: a one-page decision dossier with the register, before any model is built.
+ *Phase 2 — Proof of value (about one quarter).* Reproduce this project's loop on that decision with Petrobras data: the timing engine where projects can fail to happen, the valuation with provenance, the joint scenarios, the books with a priced capital line, and the challenger on the committee's real proposals from day one — including cases where only the argument is wrong. Success criteria declared in advance and scored on held-out scenarios; failures reported as registered.
+ *Phase 3 — Scale (following quarters).* The data and AI function owns the reference implementation, the register and the ledger; each business unit owns its decisions and its overrides; the investment committee reviews the instruments across deployed decisions. Add domains by repeating Phases 1–2, not by bespoke builds.

*Verification and handling.* The reference build behind this report runs end to end offline from public files; a reviewer can reproduce every figure and every number in this document, and replay every recorded exchange with the language model without a new call. This report is internal; distribution should follow normal information-classification handling, and nothing in Phase 2 requires exposing Petrobras data outside company infrastructure — the pattern travels to the data, not the reverse.

*What I am asking of the Committee:* sponsorship for Phase 1 on one named decision, an owner in the relevant business unit, and thirty minutes at a future session to run the challenger live on that decision's real proposal.

// ===================================================================== closing
= Closing note and limitations

Candour about limits is part of the method, so this report closes with its own:

- The results are model-based comparisons on public data and assumed costs, not demonstrated improvements in a company's capital allocation. The lease costs are assumptions; the registered and committee grids bracket them.
- The scenarios resample seven years of history, so a worse tail than 2018–2024 cannot appear, and the mean reversion lifts gas and ERCOT prices well above 2024's. The 2025 queue curves rest on two backtests that disagree about the level.
- The committees of the challenger test are personas I wrote, the language model is one model, and there are 36 flawed cases; a study with real committees is proposed, not run. No case tested a proposal whose only flaw is its argument.
- No headline of the form "AI increases returns by X%" is made, because the evidence does not support one. Every number here traces to a results table written by code, and a test fails if the text and the tables disagree.

#pagebreak()
= Appendix — The registered record and the data

#table(
  columns: (1fr, 2.6fr, 0.6fr, 0.7fr, 3fr),
  [Criteria], [What they test], [Lines], [Passed], [What they say],
  [C1–C5], [the model against cohort averages at entry], [12], [8], [the model ranks better at three and five years; its calibration slope fails],
  [C6–C12], [the portfolio layer], [12], [3], [at utility scale the lookup ties at entry; the landmark model wins two years in; the simulated band covers the realised book; no leakage],
  [C13–C14], [MISO and SPP on the 2026 file], [12], [3], [the model beats the lookup in MISO at five years; SPP is too thin],
  [C15–C17], [the milestone-managed book], [10], [4], [more operations than the lookup two years in, not more MW],
  [C18–C19], [other learners], [8], [5], [they tie LightGBM and do not beat the lookup],
  [C20], [machine learning against baselines for output and prices], [12], [3], [the plant capacity-factor lines pass; the lease lines fail on the log transform's bias],
  [C21–C24], [the four books under one budget], [4], [2], [as scored, before the audit; on the corrected system the risk-aware book beats NPV ranking and ties equal capital],
)

*The challenger's registered record.* Registered before the first call, on simulated committees; scored once.

#table(
  columns: (2.6fr, 1.2fr, 1.8fr),
  [Test], [Rule], [Result],
  [Flaws of argument named], [at least 75%], [11 of 12 — pass],
  [Computable flaws named], [at least 90%], [24 of 24 — pass],
  [Sound proposals over-challenged], [at most 15%], [2 of 12 — fail],
  [Memos fully grounded; valid fact references], [80%; 95%], [79%; 100% — fail],
  [Committee objective, challenger against proposal], [interval above zero], [+\$192M \[+\$108M, +\$281M\] — pass],
  [Worst-5% loss avoided], [interval above zero], [+\$240M \[+\$133M, +\$345M\] — pass],
  [Challenger against checklist], [interval above zero], [+\$46M \[+\$4M, +\$116M\] — pass],
  [Rules read; out-of-scope refused], [85%; 6 of 8], [32 of 32; 8 of 8 — pass],
)

*Data.* LBNL _Queued Up_ 2025 (Rand et al., 2025) and its 2026 edition; BSEE OGOR-A production; EIA-923 generation and EIA WTI and Henry Hub spot prices; ERCOT day-ahead settlement prices; NREL ATB 2024; BLS CPI-U. All public. The repository `alanmossinger/Capstone` holds the notebooks, the tests, the results tables and the record of every exchange with the language model.
