// Petrobras Report — the executive edition of report v5. Built by `make petrobras` (typst) into report/Petrobras_Report.pdf.
// Every number is one the report prints (results/report_numbers.csv); tests/test_report.py checks this file too.
// The figures are the SVGs of figures/, placed where the text discusses them.

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
#show heading.where(level: 1): it => { v(10pt); block(sticky: true, text(fill: blue, size: 16pt, weight: "bold")[#it.body]); v(6pt) }  // sticky: never the last line of a page; a stage follows the last one, as in the example
#show heading.where(level: 2): it => { v(6pt); block(sticky: true, text(fill: blue, size: 12.5pt, weight: "bold")[#it.body]); v(3pt) }
#show figure.caption: it => block(width: 84%, align(left, text(size: 9pt, style: "italic", fill: muted)[#it]))
#show figure: set block(breakable: false, above: 10pt, below: 10pt)
#set figure(gap: 6pt)
#show table: set text(size: 9.2pt)
#show table.cell.where(y: 0): set text(weight: "bold")
#set table(stroke: (x, y) => if y == 0 { (bottom: 0.8pt + ink) } else { (bottom: 0.3pt + rgb("#BBBBBB")) }, inset: 5pt)
#show link: set text(fill: blue)

// a figure from figures/, full text width, with the finding as caption and the consequence for the committee
#let fig(path, caption, consequence, width: 80%) = figure(
  image("../figures/" + path, width: width),  // four fifths of the text width: a figure and two paragraphs share a page
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
    #text(size: 11pt, style: "italic", fill: muted)[From machine learning to risk-aware capital allocation — a working proof on public data, an AI advisor that challenges the human, and its application to Petrobras.]
    #v(1.5in)
    #text(fill: red, size: 10pt, weight: "bold")[INTERNAL — CONFIDENTIAL] \
    #v(4pt)
    #text(size: 9.5pt)[Author: Alan Mössinger — Strategic Advisor, AI & Energy] \
    #text(size: 9.5pt)[Distribution: Executive Committee · AI Steering Committee] \
    #text(size: 9.5pt)[October 2026]
  ]
]

= Cover letter

To the Executive Committee and the AI Steering Committee,

Every consequential decision Petrobras makes shares one structure: commit capital now, under uncertainty, and be able to defend the decision later — to our own controls, to the TCU and CGU, and to the market through our SEC filings. The question that decides whether artificial intelligence creates value or risk in that structure is no longer whether a model is accurate. It is whether a committee can trust a recommendation it did not compute, challenge it, and show afterwards what it knew, what it assumed and why it decided.

This report presents a complete, working answer, built end to end on public data so that every number can be checked. The problem is one Petrobras faces in its own terms: one capital budget, split between assets that already produce — twenty offshore Gulf of Mexico lease redevelopments — and projects that may never be built — twenty power requests waiting in the Texas (ERCOT) interconnection queue, where most requests are withdrawn before they operate. The system predicts which requests get built and when, forecasts output and prices, draws 2,000 joint scenarios, allocates the budget with and without aversion to the tail, and scores every rule on what happened.

Three results matter for this Committee. First, the value of the producing assets is an assumption before it is a forecast: priced as our own investment committee would price them, the lease book halves, from \$14.6B to \$7.0B, and its tail becomes a real loss. Second, risk-aware allocation is a choice about appetite, not a free improvement: under the committee's prices it cuts the worst-5% loss from \$1.3B to \$0.3B at a cost of \$1.9B of expected value. Third, an AI advisor can sit inside the decision without taking it over: it reads only the result tables, must cite them for every number it writes, asks the decision-maker five questions before judging, argues the opposing book as its strongest advocate would, and can be overridden only after the answers are on record. Run live, 94% of its numbers were in its tables and it beat instinct by \$228M a situation in a replay of sixteen past decisions.

The dollars belong to a demonstration portfolio, not to a Petrobras forecast. What transfers is the chain — registered criteria, provenance on every figure, a scenario engine that keeps history's shocks, an optimizer with a stated risk appetite, and a human-in-the-loop advisor that challenges rather than flatters — and that chain describes our mature-field revitalization, our thermal and transition portfolio and our capital program equally well.

I built Petrobras's first enterprise AI Center of Excellence and chaired its Executive AI Steering Committee; this project is the same discipline, advanced to capital allocation and proven in public. I submit it as a working artifact for the Committee's consideration.

Respectfully,

*Alan Mössinger* \
Strategic Advisor — AI & Energy · Founder, VEX AI-Tech Global \
#text(size: 9.5pt, fill: muted)[20+ years at Petrobras · built the enterprise AI Center of Excellence · chaired the Executive AI Steering Committee · Master of Applied Data Science candidate, University of Michigan]

#pagebreak()
= Contents
#outline(title: none, depth: 2, indent: 1.2em)

#pagebreak()
= Executive summary

Petrobras allocates capital under uncertainty for a living. A mature field to revitalize, a thermal plant to build, a renewable project waiting for its grid connection and a trading book all share the same anatomy: a forecast of an uncertain future, a decision constrained by physics, contracts and a budget, and an obligation — statutory in our case — to explain the decision afterwards. The frontier is no longer the forecast. It is the decision built on it, and the record that makes the decision defensible.

This report is a completed, working proof of that frontier, built on public records so that nothing in it is illustrative. An energy company holds twenty producing offshore leases it could redevelop and twenty requests to connect new power plants — gas, solar, wind and storage — to the Texas grid. It must decide, request by request, whether to fund, hold or exit, and across the whole book how to split one budget. The system answers both questions and scores its answers on what happened.

#fig("F0_overview.svg", width: 92%, [The work in one picture: four asset classes under one budget, the queue engine that times every power project, the five steps from data to decision, and the decision they produce.], [one process serves every asset class; less information shows up as more risk and more constraint, never as silence.])

The headline results, all reproduced by code from the public files:

- *Which requests get built.* Of the capacity that asked to connect in 2000–2019, 12.6% was operating by the end of 2024 and 76.9% had withdrawn. At entry a gradient-boosted hazard model ranks requests better than cohort averages (AUC 0.86 against 0.73 at three years) but no better than a careful lookup; two years in, with the interconnection agreement known, a book of 25 it chose held 19 requests that reached operation, against 11 for the lookup. Every cohort since 2017 completes below the model's level, so books must be sized to the newest cohort.
- *What each asset is worth.* Under the cost grid registered before any result was seen, the twenty leases are worth \$14.6B and every one is positive. Priced as an investment committee would — \$40,000 per incremental flowing barrel of oil equivalent a day and an 8% real rate — they are worth \$7.0B on four times the capital, and 17 of the 20 turn negative at the committee grid's high-cost case. Only wind under a 15-year contract earns its capital among the power requests on the flat path.
- *How to split the budget.* Across 2,000 joint price scenarios drawn from observed prices, Winter Storm Uri included, a risk-aware optimizer cannot beat NPV ranking on the registered metric under either grid. Under the committee's grid it cuts the worst-5% loss from \$1.3B to \$0.3B for \$1.9B of expected value — a choice about appetite the committee must make, stated here rather than decided.
- *Rules against instinct.* In sixteen past situations rebuilt as of their date, the registered rules beat instinct by \$236M a situation, almost all of it in the oil-price regimes.
- *The AI advisor.* Run live on 96 recorded calls, 94% of the numbers it wrote were in its tables, its book overlapped the optimizer's by 0.89, and it beat instinct by \$228M a situation. Its challenge round — five questions, the human's answers, a verdict on the reasoning and the opposing case — is the human-in-the-loop instrument this report proposes for the Committee.

#callout[*The recommendation* is deliberately modest in scope and specific in mechanics: adopt the governed decision loop — registered criteria, provenance, scenarios, a stated risk appetite, and an advisor that challenges the decision-maker on the record — on one Petrobras capital decision, then scale it through the AI Center of Excellence and the Steering Committee. The reference implementation runs end to end offline; verification is an analyst-week, not a procurement cycle.]

#pagebreak()
= Purpose and context

Why should governed, prescriptive decision-making be an executive concern in 2026, rather than a technical one delegated downward? Three developments answer that.

- *The transition has made capital allocation a portfolio problem across asset classes.* A producing field, a gas plant, a wind farm and a battery no longer compete inside their own divisions; they compete for the same budget, under correlated prices, with very different odds of being built on time. A company that prices them on separate bases, or that treats a modelled value as an observed one, will allocate to the assumption rather than to the asset.
- *The credibility of model-projected value has become the bottleneck.* Investors, auditors and boards have learned that model-generated returns are routinely inflated. The question asked of every AI business case has shifted from "how much" to "can I trust the number" — and a methodology that registers its criteria before scoring, labels the provenance of every figure and shows its failures is itself a competitive asset.
- *Oversight expectations have hardened into obligations.* Record-keeping, human oversight, monitoring and reversibility are the entry ticket for deploying decision-making AI at a state-controlled, SEC-listed company. An advisor that cannot show what it knew, what it cited and who overrode it is a liability, however accurate.

This project was built to demonstrate, with running code, that all three concerns can be answered at once: a portfolio decision across asset classes, measured honestly, with an AI advisor whose every claim is checked and whose every exchange with the human is on the record. The next sections walk through how, in the order the decision is made.

#callout[*How to read the figures.* Every figure states its finding in its title, its method and cohort in the subtitle, and the provenance of its numbers in the footnote: OBSERVED (a public record), DERIVED (arithmetic on records), FORECAST (a model's output) or ASSUMED (a stated assumption). Dollar figures for the queue are in 2022 dollars, for the portfolio in 2024 dollars. Intervals are drawn wherever a number is uncertain.]

// ===================================================================== stage 1
= Stage 1 — The data and the candidates

The data are public. The queue side is the project-level file of Lawrence Berkeley National Laboratory's _Queued Up_ series: 13,366 requests in CAISO, ERCOT and PJM, the three grid operators that date both operation and withdrawal, fitted on requests that entered up to 2016 and tested once on the 2,268 that entered in 2017–2019. The energy side is BSEE monthly lease production for 2010–2024, EIA plant generation for Texas, EIA's WTI and Henry Hub prices, ERCOT's hourly settlement prices for 2018–2024 and the EPA's eGRID. A readiness gate checked each source before any model was fitted, and every gate line passed.

#fig("F9_project_map.svg", [Requests waiting in U.S. queues at the end of 2024 by county (left; area proportional to MW) and the operating fleet (right).], [the capacity waiting to connect is larger than the fleet that operates; where a project sits decides its odds before any model is run.])

The forty candidates are the twenty leases with the most 2024 output among the 513 still producing at the end of 2024, and the five largest ERCOT requests of 2017–2019 in each of four technologies: gas combined cycle, solar, wind and storage. The leases are the Gulf's largest producers, concentrated in two protraction areas; the Texas plants sit where their fuel is — wind in the west and north, solar in the west, gas along the coast and near the cities.

#fig("02_eda/02_C5_asset_map.svg", [Gulf of Mexico oil by protraction area in 2024, and Texas plants by fuel and size.], [the candidate set mirrors a real portfolio: a few large producing assets and many small, uncertain projects.])

// ===================================================================== stage 2
= Stage 2 — Will it be built, and when: the queue engine

A developer who wants to build a power plant must first ask the grid operator for a connection. The request enters a queue and leaves years later as an operating plant or a withdrawal; most leave as withdrawals. Every request costs money to keep alive — a deposit, a study, a larger deposit, a longer study — so the first decision is which requests to fund, which to hold and which to drop.

#fig("F1_cif_by_region.svg", [Share of requests operating (and withdrawn) by years since the request, by region; Aalen–Johansen estimates with 95% intervals.], [ERCOT is where requests get built — 18.4% of entrants operate within five years against 4.8% in CAISO — so the region decides the base rate before the project does.])

Three predictors were compared, always in the same order: *the model*, a gradient-boosted discrete-time hazard model that sees only what is known on the request date; *the lookup*, the share built among earlier requests of the same region, technology and size — what a careful analyst computes by hand; and *the cohort average*. At entry the model beats cohort averages (AUC 0.86 against 0.73 at three years) but ties the lookup at utility scale. Two years in, with the executed interconnection agreement known, the picture changes: the landmark model ranks the next three years at a concordance of 0.80 against 0.69 for the entry model, a gain of 0.11, while the lookup conditioned on surviving two years falls to 0.59.

#fig("F12_landmark_models.svg", [Gain in ranking (Uno's C) and calibration (Brier score) over the entry model at each landmark, three years ahead; 95% intervals.], [do not pay for prediction at entry; re-score every request still held two years in, when the agreement is known.])

The test that settles the question is a book. Two years in, a book of 25 requests chosen by the landmark model held 19 that reached operation within three years, against 11 for the lookup that knew the same agreement status; a book of 50 held 33 against 24. The same books held fewer megawatts: the model picks more plants that get built, not more capacity.

#fig("F18_managed_book.svg", [Operations and MW realised within three years of the two-year landmark, for books of 25 and 50 chosen by the landmark model, the agreement-aware lookup, the entry lookup and at random; 95% intervals.], [the review moment is worth more than the model; a company that re-scores at the milestone holds twice the operations of one that ranks at entry.])

Two further facts set the rules a company can apply by hand. Size, technology and the agreement decide the odds: in PJM five-year completion falls from 24% for requests under 5 MW to 4% at 500 MW and up; gas is built most often; and where the agreement is dated within two years of the request, 63% of ERCOT's requests were operating within five years, against 0.8% where none is dated. And every cohort since 2017 completes below the model's level — 11.0% of 2017 entrants of 20 MW and more operated within five years against about 12% predicted — so a book must be sized to the newest cohort, not to the model.

#fig("F11_level_by_entry_year.svg", [Five-year completion observed and predicted by entry year, requests of 20 MW and more.], [the cohort level is the risk a model does not see; size every book to the newest completed cohort.])

#callout[*The gate rules, scored on what happened.* At entry the rule funds a request when its chance of operating is at least the pool's and its value at least three times the cost of the next gate; two years in, twice. On the 2017–2019 requests the funded class reached operation 26% of the time against 10% for the cohort and returned +\$4.1B at merchant prices; the accelerated class two years in operated 18–20% of the time against 8% for the exits.]

// ===================================================================== stage 3
= Stage 3 — What the energy data say, and what the models may know

A quarter of lease-months produce nothing — 25.3% of 203,963 — because leases are shut in for maintenance, storms and workovers; the forecasts treat those months as part of the process, not as missing data. Prices and output barely move together month to month, except gas and power: WTI and Henry Hub correlate at 0.06, Henry Hub and the ERCOT price at 0.63 because gas sets the Texas power price in most hours, and Gulf output with any price at almost zero. Wind output in Texas runs against gas-plant output (−0.55), because gas fills the hours the wind leaves. This is why the scenario engine draws prices jointly but output separately.

#fig("02_eda/02_C6_correlation_and_clusters.svg", [Correlation of monthly log changes across the three prices, Gulf output and Texas capacity factors, and the two shapes of lease oil decline after the peak.], [the diversification a portfolio can claim lives in these correlations; the ones that are near zero are where it comes from.])

Every feature is built only from what was public at the forecast date. Each source has a release lag — BSEE production three months, EIA generation two, prices none — and a truncation test proves it: features rebuilt after deleting all later data are identical. Twelve forecast lines were registered before scoring. Three pass, all for plants: the challengers cut the seasonal-naive error for gas, solar and wind capacity factors by 8%, 12% and 15%. The lease lines fail — the registered challenger's error at three months is 1.35 times the last-value baseline's — and prices behave as random walks, as they should.

#fig("F27_forecast_gains.svg", [Forecast error of the challenger relative to the best baseline, by registered line, with paired moving-block bootstrap intervals.], [machine learning helps where there is a seasonal shape to learn; where a decline curve already carries the physics, the honest answer is that it does not.])

Does the forecast change the decision? No. With the naive baseline's errors in place of the machine-learning model's, the risk-aware book picks exactly the same 26 candidates (overlap 1.00). The allocation comes from the cost grid and the optimizer; the forecasts move the size of the tail, not the choice.

// ===================================================================== stage 4
= Stage 4 — What each candidate is worth, and what that rests on

A lease redevelopment is an uplift on a producing asset: an Arps decline baseline from its last 36 months, a 20% uplift after a two-year lead time, and the value of the cash flow it adds over doing nothing. A power request is a plant that may never be built: its value if built uses the 2024 hourly prices — solar earns 92% of the flat hub price, wind 83% and gas 135%, because Texas wind blows at night, solar produces at midday and a gas plant runs only in the hours when prices clear its fuel cost — weighted by the queue engine's chance of operating in each of seven years, net of the cost of keeping the request alive.

#fig("F28_candidates.svg", [The forty candidates: incremental NPV of the lease redevelopments and timing-weighted expected NPV of the ERCOT requests, with provenance.], [on the flat path the leases carry the book and only contracted wind among the requests earns its capital; the chance of never operating is the power side's cost.])

That result rests on two generous assumptions, and the committee grid replaces them. The registered grid prices a 20% uplift on the largest deepwater leases as a workover of existing wells, at \$4–15 million a well; on the largest lease the uplift alone is nearly twenty thousand barrels of oil equivalent a day, a development whose capital scales with the barrels it buys. The registered grid also discounts the leases at 5.1% real, where an oil and gas committee uses 8–10%. The *committee grid* prices capital at \$40,000 per incremental flowing barrel of oil equivalent a day (range \$25,000–\$60,000) and discounts at 8% (range 5.1–10%). It was added after the registered results, at an outside reviewer's request, and is labelled as such.

#fig("F29_cost_tornado.svg", [Change in the book's NPV when each registered grid item moves across its range, one at a time.], [the uplift and the operating cost decide the lease side under the registered grid; the capital per barrel decides it under the committee's — every one of them an assumption the committee should own.])

#table(
  columns: (2.2fr, 1fr, 1fr),
  [Twenty leases, flat 2024 prices], [Registered grid], [Committee grid],
  [Capital], [\$1.37B], [\$5.51B],
  [Incremental NPV, base], [\$14.6B], [\$7.0B],
  [Incremental NPV, low and high grid cases], [\$10.0B and \$9.6B], [\$8.9B and −\$2.0B],
  [Leases positive at base], [20 of 20], [20 of 20],
)

Under the committee grid the leases still pay, at half the value and four times the capital; every lease stays positive at base, but 17 of the 20 turn negative at the high-cost case. The conclusion that capital goes where the asset already produces survives; the size of the prize does not.

#fig("F37_committee_grid.svg", [Left: mean and median (with 5–95% range) of the default book and book D under the two grids. Right: the twenty leases on the flat path under the 2020 shape and under five years at \$42 oil.], [the stress that matters is a sustained one — five years of \$42 oil takes the lease book to \$4.25B under the committee grid — not a replay of a collapse that recovered before the barrels arrived.])

// ===================================================================== stage 5
= Stage 5 — Scenarios and risk

Prices, output, costs and timing are drawn together. 2,000 joint paths of twenty years resample calendar-year blocks of the 2018–2024 monthly changes of WTI, Henry Hub and ERCOT, the same months for all three, so the 2020, 2021 and 2022 episodes travel together and a spike stays with its reversal. Monthly changes are capped at ±1.5, a ×4.5 move, the largest the history shows outside February 2021: Winter Storm Uri took the hub from \$26 to \$1,772 a MWh and back in two months, and an uncapped draw that lands the spike without its reversal holds a ×69 price for years. The log prices revert toward their 2018–2024 real geometric means with a four-year half-life. A second, held-out set of 2,000 paths with its own seed is used only to score books.

#fig("F30_price_scenarios.svg", [The joint price scenarios against the real-dollar history: median, interquartile and 5–95% bands by year.], [the scenarios keep history's jumps and its correlations; what they add is a stated level to revert to, which is the one assumption a committee can argue with.])

#table(
  columns: (2.2fr, 1fr, 1fr),
  [Default book of forty], [Registered grid], [Committee grid],
  [Median NPV], [\$14.9B], [\$7.0B],
  [Mean NPV], [\$15.8B], [\$7.7B],
  [5th percentile], [\$6.2B], [−\$0.3B],
  [Chance of a loss], [0.0%], [6.1%],
  [Worst-5% average (CVaR95)], [a \$4.9B profit], [a \$1.7B loss],
)

The tail is the committee grid's. Under the registered grid the default book never loses money in 2,000 scenarios; under the committee grid it loses money in 6% of them and its worst 5% averages a \$1.7B loss. Removing the correlations between prices changes the book's tail by \$0.6B, which is what modelling them jointly is worth. The named deterministic stresses — the 2020 oil path, high gas, a weak wind year, solar curtailment, a two-year delay, all at once — leave the default book positive on the flat path; the stress that bites is a sustained one.

#fig("F32_stresses.svg", [The default book under the registered named stresses, on the flat path.], [single stresses are survivable; a committee should ask for the sustained one and for the joint scenarios, not for a list of one-at-a-time shocks.])

// ===================================================================== stage 6
= Stage 6 — Allocating the budget

Four books compete under one budget — 40% of the candidates' capital — and one cap of 40% per technology. *A* takes candidates by expected NPV; *B* splits the budget equally by sector; *C* maximises expected NPV; *D* maximises expected NPV minus the worst-5% average loss. Books are chosen on the primary scenarios and scored on the held-out ones, against four criteria registered before any book was solved.

#fig("F33_four_books.svg", [The four books and two single-sector books on the held-out scenarios, the frontier over risk aversion, and capital by technology.], [under the registered grid every book's worst 5% is still a profit, so there is little tail for risk aversion to buy; the books converge on the leases plus contracted wind and gas.])

On the observed prices two of the four criteria pass and two fail. Book D earns \$15.9B against \$16.1B for book A on the held-out scenarios, a shortfall of \$61M on the registered metric, and no more than book B; its selection is as stable as the deterministic book's under the six stresses, and its tail beats the single-sector comparator's by \$159M. Under the committee grid the choice becomes real:

#table(
  columns: (2fr, 1fr, 1fr, 1fr, 1fr),
  [Committee grid, held-out scenarios], [A top-N NPV], [B equal capital], [C deterministic], [D risk-aware],
  [Members], [22], [18], [17], [17],
  [Mean NPV, \$B], [7.7], [6.9], [5.8], [5.8],
  [Median NPV, \$B], [7.0], [6.2], [5.3], [5.3],
  [Chance of a loss], [5%], [4%], [3%], [3%],
  [Worst-5% average loss, \$B], [1.3], [0.6], [0.3], [0.3],
)

With the budget set by the same rule (\$7.81B), book A takes eighteen leases and four gas requests and expects \$7.7B, with a 5% chance of a loss and a worst-5% loss of \$1.3B. Book D takes ten leases, three contracted wind requests and four gas requests and expects \$5.8B, with a 3% chance of a loss and a worst-5% loss of \$0.3B. On the registered metric A still wins by \$888M, with an interval entirely on A's side. Whether D is the better book depends on how much the committee will pay to cut its tail — a policy choice, not a statistical one, and the first question this report puts to the Committee.

#callout[*Two settings a committee might change barely move book D.* A carbon price of \$50 a tonne on the gas plants' emissions drops one gas request (overlap 0.88); doubling the weight on the tail changes nothing (overlap 1.00); a budget cut of a fifth keeps most of the book (overlap 0.82). The gas requests are the least secure line: negative on the flat path, worth \$427M between them in the scenarios because ERCOT prices spike, as they did in 2019, 2021 and 2023.]

// ===================================================================== stage 7
= Stage 7 — When: the book at one to twenty years

A twenty-year NPV says nothing about what the owner holds at year three. Counting only the cash that falls within each horizon, the lease book is −\$1.4B within two years (the redevelopment capital), turns positive in year three and reaches \$14.6B at twenty under the registered grid; a queue request is a carrying cost until it operates, and the twenty are −\$0.84B at twenty years. The best book holds nothing at one or two years, twelve leases at three and all twenty from ten.

#fig("F35_horizon_view.svg", [Expected NPV counted within 1, 2, 3, 5, 10 and 20 years, by sector, and the composition of the best book at each horizon.], [an owner with a one- or two-year horizon funds nothing; the horizon is a parameter of the decision and should be stated with the budget.])

// ===================================================================== stage 8
= Stage 8 — The decision gym: rules against instinct, scored on outcomes

The gym scores decisions on outcomes, not prose. Sixteen past situations are rebuilt as of their date, with no outcome shown: fifteen requests drawn at random from each region's 2017, 2018 and 2019 entrants, the 2017 entrants again two years in, ERCOT 2018 with a budget cut of a fifth, and the twenty leases at the start of the 2014, 2020 and 2022 oil-price regimes. In each, instinct (top-N expected NPV), the registered rule, the AI advisor and the human pick a book under the same budget; then the realized value is revealed.

#fig("F34_decision_gym.svg", width: 72%, [Realized value of the book chosen by instinct, the registered rule and the advisor in each past situation, against the best book with hindsight. Top: queue rooms. Bottom: lease regimes.], [the registered rules beat instinct by \$236M a situation and the advisor by \$228M, almost all of it in the oil-price regimes where a budget-bound optimizer beats a greedy ranking by about \$1.2B each.])

Over the sixteen situations the rule's mean regret against hindsight was \$18M, the advisor's \$26M and instinct's \$253M. In the 13 queue rooms the rule is ahead by only \$3.7M a room: in 6 of them none of the drawn requests operated, so the best any rule can do is spend nothing on gate costs. In the room the queue engine calls decisive — ERCOT's 2017 entrants two years in — the rule beat instinct by \$41M.

// ===================================================================== stage 9
= Stage 9 — The AI advisor: help the decision, challenge the decision-maker

The advisor is one actor in a decision process with four — instinct, the registered rule, the advisor and the human — and it is built to be trusted the way a committee trusts a colleague: on the record, and with the right to be overruled.

#fig("F36_ai_workflow.svg", width: 90%, [The advisor's workflow: result tables as the only input, the number check, the record and replay, the five questions and the override gate, the ledger and the gym.], [the advisor cannot invent a number, cannot be run without a trace, and cannot be overridden without the reasoning on record.])

== What it sees and how it is checked

The advisor receives a system prompt, a task, and a block of result tables rendered by one formatter, each with its provenance label. It sees no web, no memory across calls and no company data. A mechanical check accepts a number in its answer only if the same token appears in the tables; a number rounded differently counts as ungrounded on purpose. Every call is appended to a record with the model id, the prompts, the response, the token use and the verification, and a recorded call is served from the record, so the whole pipeline reproduces offline.

== How it helps

For the base case and each named stress the advisor recommends a book, names the expected NPV and the tail it cites, the binding constraint, and what would change the answer; it does the same for each horizon. Run live, its stress books overlapped the optimizer's by 0.89 and it named the risk-aware book in 3 of 7 stresses, choosing the leases alone in the simultaneous downside — a defensible reading, stated with its reasons.

== How it challenges — the human in the loop

The instrument this report proposes for the Committee is the challenge round, written for this decision. The decision-maker states the book they prefer and why. The advisor then:

+ *Asks five questions tied to the statement*, one for each item the override gate later requires — the stakes, what each party wants, where the emotional investment lies, which evidence was leaned on and which passed over, and what alternative was left off the table — and nothing else: no verdict, no numbers, no recommendation.
+ *Takes the answers*, and only then judges: it names the motivated-reasoning patterns this decision invites, with the sentence that shows each — judging the leases on the flat path and the requests on the scenarios, treating an assumed cost or a forecast chance of operation as observed, counting a deposit already paid as a reason to keep paying — and says what the tables show instead, cited as written.
+ *Argues the opposing book* as its strongest advocate would, against what the human actually said, names the assumption the opposing case rests on and the number at which it fails, then steps out of the role and says which case is stronger on the tables, ending with a convergence line.
+ *Opens the override gate* only now: the human may override the advisor's book because the five answers and the opposing case are on record, and the decision — override or not — is written to a ledger that the gym scores as outcomes arrive.

In the scripted all-leases round the advisor asked which number carried the loss and how long the company could carry it, whether the reluctance to learn a new business was a view about risk or about the sector, and whether the chance of operation had been counted twice. In its verdict it named the double standard of judging the leases on one flat path and the requests on their chance of being built, and found that the lease-only book had the lowest expected value and no tail advantage over the risk-aware book. Its opposing case kept the leases and added only the contracted wind, and said so in its convergence line. At the keyboard the same exchange runs live; the transcript and the ledger row are the audit trail.

#callout[*Why this is the right shape for Petrobras.* The advisor never decides; the committee does. But the committee decides after answering five questions on the record, after hearing the strongest case against its own view, and with every number it was shown traceable to a table with a provenance label. That is the difference between an AI that flatters a decision and one that defends it to an auditor.]

== What it is not

The advisor reasons like the rule because it reads the rule's tables; it is not a second source of truth. Its ungrounded remainder — 6% of the numbers it writes — is arithmetic it did itself, such as the capital of two requests added together, which the check refuses on purpose. It was scored against a rule it mostly agrees with, matching the rule in 11 of 16 gym situations, beating it in 4 and losing once. No headline of the form "AI increases returns by X%" is made.

#pagebreak()
= Results at a glance

#table(
  columns: (1.3fr, 3fr, 1fr),
  [Question], [Finding], [Verdict],
  [Where to look], [ERCOT builds most often: 18.4% of requests operate within five years, against 4.8% in CAISO.], [Observed],
  [Predict, at entry], [The model beats cohort averages (AUC 0.86 against 0.73) but ties the lookup at utility scale.], [Partly],
  [Predict, two years in], [A book of 25 chosen by the landmark model held 19 operations, against 11 for the lookup.], [Supported],
  [Size the book], [The 2017–2019 cohort brought 18.8 GW of the 29.2 GW expected; every later cohort runs lower.], [Observed],
  [Fund, hold or exit], [Funded requests operated 26% of the time against 10% for the cohort, and returned +\$4.1B at merchant prices.], [Scored on outcomes],
  [Forecast output], [Machine learning beats baselines for plant output (three of twelve lines), not for leases or prices.], [Partly],
  [Does ML change the book?], [No: with naive forecasts in its place the risk-aware book is identical.], [Derived],
  [Risk], [Under the committee grid the default book loses money in 6% of scenarios; modelling correlations moves the tail by \$0.6B.], [Derived],
  [Allocate], [The risk-aware book does not beat NPV ranking on the registered metric; under the committee grid it cuts the worst-5% loss from \$1.3B to \$0.3B for \$1.9B of expected value.], [Partly],
  [When to invest], [Nothing at one or two years; twelve leases at three; the full lease book from ten.], [Derived],
  [Rules against instinct], [The registered rules beat instinct by \$236M a situation over sixteen past situations.], [Scored on outcomes],
  [The AI advisor], [94% of its numbers are in its tables; its book overlaps the optimizer's by 0.89; +\$228M a situation.], [Scored on outcomes],
)

// ===================================================================== petrobras
= Why this matters for Petrobras

Strip away the market specifics and the system above is a template: (1) a timing engine that turns "will it be built" into a probability; (2) a valuation that carries its assumptions in the open, with a committee grid beside the registered one; (3) a scenario engine that keeps history's shocks and correlations; (4) an optimizer with a stated risk appetite, scored on held-out scenarios against criteria registered first; and (5) an advisor that explains, challenges and records. Written that way, it is not a description of a Texas queue and a Gulf lease. It is a description of Petrobras's capital program.

Consider the correspondences. A Gulf lease redevelopment is a mature-field revitalization in the Campos basin: an uplift on a producing asset, whose value is decided by the uplift share, the operating cost and the capital per incremental barrel — the committee grid's items. A queue request is a transition project waiting on a grid connection, a licence or a partner: a plant that may never be built, whose value must be weighted by the chance it operates and by when. The joint scenarios are the Brent, gas and power paths every investment case already carries, drawn together rather than one at a time. And the committee grid is our own investment committee's prices, which this report shows can halve a book and turn a free improvement into a policy choice.

What the company has not yet institutionalized — what almost no company has — is the full governed loop: criteria written before scoring and failures reported as registered; provenance on every figure a committee sees; a stated risk appetite instead of an implicit one; and an AI advisor that must cite its tables, must ask before it judges, and must be overruled through a gate that leaves the reasoning on record. That is the specific capability this reference implementation demonstrates end to end.

== The transfer map

#table(
  columns: (1.2fr, 1.6fr, 1.6fr, 1.4fr),
  [Domain], [The "will it happen, and when"], [The decision], [The audit stake],
  [Mature-field revitalization], [Decline baseline and uplift; capital per incremental barrel], [Which fields, in what order, under one budget and a tail limit], [Reserves governance; SEC Form 20-F; TCU/CGU review of public-asset value],
  [Transition power projects], [Chance of reaching operation by year; contract against merchant], [Fund, hold or exit at each gate; re-score at the milestone], [Investment-decision records; partner and lender diligence],
  [Thermal and gas-to-power], [Joint price scenarios with the spikes kept], [Dispatch, hedges and the capacity to hold], [Trading compliance; transfer pricing],
  [The capital program], [One budget across the classes above], [The book, its risk appetite and its horizon, stated and scored], [The investment committee's own record of what it knew and assumed],
)

// ===================================================================== management model
= Driving executive decisions: the management model

A decision system of this kind yields a small set of standing, executive-legible instruments — few enough for a monthly committee page, each demonstrated in the reference build:

- *The book and its tail (are we taking the risk we said we would?).* Expected value, the median beside it, the chance of a loss and the worst-5% average, on held-out scenarios, under the registered grid and the committee's. Movements in the tail, not in the mean, are what warrant executive attention.
- *The register (did we decide the test before the result?).* Criteria written and committed before scoring, with failures reported as registered: 28 of 70 lines pass across this project, and the ones that fail are the ones a reader learns most from.
- *Provenance (which number is an assumption?).* Every figure labels OBSERVED, DERIVED, FORECAST or ASSUMED; a book that rests on an ASSUMED cost is presented as such, with the committee grid beside it.
- *The gym (do our rules beat instinct where it counts?).* Past situations rebuilt as of their date and scored on what happened, for the rule, the advisor and the human — the instrument that turns "AI helps" from a slogan into a number.
- *The advisor's record (what did it cite, what did it ask, who overrode it?).* The grounding rate, the challenge transcripts and the override ledger — the audit trail of every decision in which the advisor took part.

These instruments slot into the structures Petrobras already operates — the AI Steering Committee for portfolio-level review and the Center of Excellence as the owner of the reference implementation. No new committee is required; what changes is that the committee reviews a stated risk appetite, a register and a ledger instead of a pilot narrative.

#callout[*One cultural instrument matters as much as the five quantitative ones.* A book that looks too good is a risk to investigate, not a success to announce. This project encodes that norm twice: a cost grid that doubles the capital and halves the prize was added because the first result was generous, and a scenario engine that put expected values three orders of magnitude above their medians was repaired before any number from it was reported.]

// ===================================================================== recommendations
= Recommendations and next steps

The recommendation is deliberately modest in scope and specific in mechanics: prove the governed decision loop on one Petrobras capital decision, then scale what works through the structures that already exist.

+ *Phase 1 — Diagnostic (about six weeks).* Select one recurring capital decision — the transfer map's strongest candidates are mature-field revitalization ranking and the transition power portfolio — and run a structured diagnostic: define the decision moment, inventory what is knowable at it, write the cost grid with its ranges and the criteria that will score the books, and state the risk appetite. Deliverable: a one-page decision dossier with the register, before any model is built.
+ *Phase 2 — Proof of value (about one quarter).* Reproduce this project's loop on that decision with Petrobras data: the timing engine where projects can fail to happen, the valuation with provenance, the joint scenarios, the four books, the gym on past decisions, and the advisor with its challenge round from day one. Success criteria declared in advance and scored on held-out scenarios; failures reported as registered.
+ *Phase 3 — Scale through the CoE (following quarters).* The Center of Excellence owns the reference implementation, the register and the ledger; each business unit owns its decisions and its overrides; the AI Steering Committee reviews the five instruments across deployed decisions. Add domains by repeating Phases 1–2, not by bespoke builds.

*Verification and handling.* The reference build behind this report runs end to end offline from public files; a reviewer can reproduce every figure and every number in this document, and replay every one of the advisor's recorded answers without a model call. This report is internal; distribution should follow normal information-classification handling, and nothing in Phase 2 requires exposing Petrobras data outside company infrastructure — the pattern travels to the data, not the reverse.

*What I am asking of the Committee:* sponsorship for Phase 1 on one named decision, an owner in the relevant business unit, and thirty minutes at a future session to run the challenge round live on that decision.

// ===================================================================== closing
= Closing note and limitations

Candour about limits is part of the method, so this report closes with its own:

- The lease costs are assumptions, not company data; the registered and committee grids bracket them, and no modelled NPV in this report is presented as an observed one.
- The power requests' values rest on the queue engine's chance of operating, calibrated on 2017–2019 entrants in a regime before interconnection reform; no entry-time model is calibrated to the post-2020 level, and the report sizes books to the newest cohort for that reason.
- The ERCOT price history holds one Winter Storm Uri in seven years; the scenario engine caps its monthly jump to keep it an event and not a level, and how often such a month recurs is the least known number on the power side.
- The advisor was scored against a rule it mostly agrees with, on sixteen past situations and 96 recorded calls; its challenge rounds were run on two scripted statements with the author's own answers. The instrument is the exchange, not the model.
- Every number here traces to a results table written by code, and a test fails if the text and the tables disagree.

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
  [C21–C24], [the four books under one budget], [4], [2], [on the observed prices book D ties NPV ranking and equal capital, is as stable as the deterministic book and beats the single-sector comparator's tail; on the bridged prices all four failed],
)

*Scored twice.* C20–C24 were first scored when ERCOT's 2020–2023 prices were a bridge from PJM West prices; that scoring is kept unchanged in the repository and the observed prices replace the bridge in every table above.

*Data.* LBNL _Queued Up_ 2025 (Rand et al., 2025) and its 2026 edition; BSEE OGOR-A production; EIA-923 generation and EIA WTI and Henry Hub spot prices; ERCOT day-ahead settlement prices (2024 pull and the 2018–2023 yearly files); EPA eGRID2023; NREL ATB 2024; BLS CPI-U. All public. The repository `alanmossinger/Capstone` holds the ten notebooks, the tests, the results tables and the advisor's record.
