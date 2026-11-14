# Visuals mini-deliverable — Beyond Prediction (Group 13)

Posted to the team + mentor Slack channel on 12 November 2026. The three figures are drawn and sit in the report draft as Figures 5, 6 and 7 (`figures/F57_book_distributions.png`, `figures/F51_true_economics.png`, `figures/F53_ladder_five_arms.png`); every number on them comes from `results/report_numbers.csv`.

---

*Visuals plan — Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation (Group 13, solo)*

The project asks one prescriptive question: given one budget ($3.82B on 1 January 2025), forty candidate investments (20 Gulf of Mexico leases, 20 ERCOT interconnection requests) and stated risk preferences, which should a company fund, and does prediction, optimization or an AI challenger change that answer? Three figures carry the findings; a new reader who sees only these three gets the story.

*Figure 1 — The highest expected return is not the best investment*
• Variables: the twenty-year NPV of a portfolio ("book") in each of 2,000 held-out scenarios (x axis, $ billion), the number of scenarios per bin (y axis), one panel per decision process (NPV ranking, equal capital by sector, deterministic optimizer, risk-aware optimizer, and the risk-aware optimizer fed the lookup's forecasts). Each panel marks the expected NPV and the worst-5% average loss (CVaR95), the two numbers the registered metric subtracts.
• Type: small-multiple histograms on a shared axis, the 100 worst scenarios shaded, two dashed reference lines per panel.
• Takeaway: ranking by expected NPV buys upside with a fat left tail. The risk-aware book gives up about $0.5B of expected value to cut the worst-5% loss from $1.55B to $0.82B and the worst future from −$4.0B to −$2.0B, and it scores best on the registered metric. The last panel adds the prediction finding: the same optimizer fed a simple lookup instead of the machine-learning forecasts lands almost in the same place, so better prediction did not make a better decision.

*Figure 2 — Funded the same way, the risk-aware book still scores best (and the recommendation is a book plus its credit line)*
• Variables: left, the registered metric (expected NPV minus worst-5% loss, $ billion) for each of the five decision processes under three funding bases (static: every plant that signs is built; no construction line: calls beyond the reserve forfeit the plant; each book's own line, net of a 0.5% fee and 8% interest). Right, the capital each process commits: lease capital spent now, deposits, the construction reserve, the contingent facility sized to the 95th-percentile calls, and that facility's financing cost.
• Type: grouped bar chart (process × funding basis) beside a stacked bar chart with the facility hatched and the budget as a dashed line.
• Takeaway: the ranking of strategies depends on how construction is funded. With no credit line, equal capital by sector would win; with each book given a priced line, the risk-aware book leads NPV ranking by $312M. Every book needs a facility of $2.5–3.2B, almost as large as the budget itself, so the recommendation is the book and its facility together, not the book alone.

*Figure 3 — The AI's value is in the argument, not the choice*
• Variables: left, the committee's own objective ($ million per case, mean over 48 simulated committee proposals and five modelled worlds) under five arms: the committee's own proposal, deterministic checks (tools only), a fixed optimizer-first rule, tools plus the language-model challenger, and the optimizer under the committee's true rules. Right, the paired per-case difference between arms with a 95% bootstrap interval, the three rungs registered before the test and the two added after.
• Type: bar chart beside a dot-and-interval (forest) plot, intervals that cross zero visibly.
• Takeaway: deterministic tools do most of the work (+$76M per case over the committee's proposal); the language model adds +$43M on top of the tools by reading the committee's arguments, but against a plain rule that takes the optimizer's book first its edge disappears (−$14M, interval crossing zero). The model earns its place by exposing weak reasoning, not by picking the portfolio.

Design rules for all three: the title states the finding in one sentence, one colour for the recommended book across figures, intervals drawn rather than quoted, and the data, provenance and cohort printed under every figure.
