# V2 review and correction register

*Deliverable A of the executive review of 23 October 2026. Reviewed: report v10 (`report/report.md`, built as `report/report.pdf` on 22 October), the notebooks and `src/`, the registered records in `results/v9/` and `results/v10/`, and the reproduction record of decision #112. Written before the V2 manuscript; the computed items were run in notebook 13 (`notebooks/13_executive_corrections.ipynb`) and their results are quoted here from its outputs.*

## 1. What is already defensible

| Finding | Evidence | Standing |
|---|---|---|
| The queue model ranks requests better than the lookup and overstates the level | backtest as of 2020 (AUC 0.731 against 0.686); the one-year forward test (30 operated, 78 and 17 expected) | registered (C1–C5) and post-hoc; keep as is |
| Under equal constraints the risk-aware book beats NPV ranking on the registered metric | C33 +$219M [+$13M, +$401M], 20 re-selections all positive, 5,000-path check | registered, PASS; narrow, and the report says so |
| The tail is the candidates' co-movement | dependence ablation (notebook 12 section 4) | post-registration; strengthened by the dial in notebook 13 |
| The construction line pays once priced | $0.76B with no line, $1.03B net of fee and interest, 12 of 12 settings | post-registration; now extended to every book (notebook 13) |
| The language model adds value beyond its tools, less than the tools and the optimizer | C34 +$43M [+$9M, +$86M]; C35 +$76M; C36 +$134M | registered; the stronger baseline is added beside it (notebook 13) |
| It reads stated rules and names flaws of argument without crying wolf | C38 40 of 40; C41 12 of 12; C40 0 of 12 | registered, PASS |
| It reads silence badly and embellishes with numbers | C37 38 of 48; C39 15 of 20, 7 ungrounded memos | registered, FAIL; reported as they fell |
| The case material was not written by the model under test | `results/v10/cases_v10.json` (`_source`): statements written by the author on 22 October 2026 before any model saw them; committed 09:16 (d6b8531), registration committed 12:11 (62b2100), the run scored 14:19 (a425ae8); every file hashed in the registration | verified from the git history; Issue 1 closed |
| The pipeline reproduces | a clean Linux container and a second Linux environment reproduced every registered verdict and 2,548 of 2,561 cited numbers (decision #112) | verified twice |

## 2. Corrections, ranked by materiality

| # | Materiality | Issue | What was wrong in v10 | What V2 does | New computation? |
|---|---|---|---|---|---|
| 1 | **High** | Financing consistency (Issue 2) | Table 2 compared the five decision processes on a static basis (every agreement built, capital unlimited); the construction line was then priced for book D alone. A reader could take the $219M margin as a financed result. | Notebook 13 section 1 scores every book on four bases — static, no line, its own 95th-percentile line net of the fee and the interest, and a common $2.53B line — with capital committed, reserved and contingent separated; paired intervals on the financed basis; the risk-aware book re-solved with the line as a constraint. Figure F51. | Yes (done) |
| 2 | **High** | The strength of the LLM baseline (Issue 5) | The registered checklist guides to the repair; the first test showed an optimizer-first rule removed the model's edge (+$1M, decision #97). v10 did not re-ask this on the final cases. | Notebook 13 section 3 adds the optimizer-first rule as a fifth arm on the 48 registered cases and their recorded outputs, scored as the ladder is; reported beside C34, not in its place. Figure F53. | Yes (done) |
| 3 | **Medium** | Scenario realism and dependence (Issue 4) | One ablation (independent columns) showed the tail vanishes without co-movement; no reader could tell whether the tail hangs on the dependence model. Stresses were scattered over notebooks 11 and 12. | Notebook 13 section 2 dials the co-movement from independent to joint and to the comonotonic bound, and scores every book in seven worlds on one table. Figure F52. Regime-switching and extreme-event scenarios are proposed, registered before use, not run. | Yes (done); further tests proposed |
| 4 | **Medium** | Operational positioning (Issues 6, Q6) | The report answered "does the model help" and "where does it fail" but gave no committee workflow, no level rules, and no control matrix; a reader could read the two failed lines as "not usable". | A readiness and control matrix (twelve controls: implemented, tested, limitation, validation required), the operational workflow with the five levels, and an illustrative committee conversation from a real registered case. Figures F55, F56. | Diagrams only |
| 5 | **Medium** | Structure and audience | v10 was structured by research questions and estimands; the executive reader met C33 and C34 before the decision. | V2 opens with the decision brief and the recommended allocation; the methods follow the findings; criteria codes stay in the tables and appendices. | No |
| 6 | **Low** | The allocation as a table | Book D's members were described in prose; no table gave charge, expected NPV, chance of a loss and status per member. | Notebook 13 section 4 writes `results/v2/book_D_members.csv`; Figure F54 and Table 2 of V2. | Yes (done) |
| 7 | **Low** | Claims of realized value | None made; kept so. Every value is a model-based comparison on held-out scenarios. | V2 states the three claims apart: computes a better book in the experiment; helps a simulated committee decide; not validated for a real commitment. | No |

## 3. Results of the corrections (notebook 13)

**Financing (Issue 2).** On the same funded basis — each book within its own 95th-percentile construction line, net of the 0.5% fee and 8% interest — the risk-aware book D scores $1.03B on the registered metric against $0.82B for the deterministic optimizer (C), $0.72B for NPV ranking (A), $0.71B for equal capital (B) and $0.96B for the lookup book (F). D's margin over A widens from +$219M (static) to +$312M [+$110M, +$506M]; it beats C clear of zero (+$213M [+$17M, +$412M]) where the static comparison did not; against F the interval still includes zero (+$70M [−$51M, +$201M]). A common $2.53B line gives the same order (D over A +$313M [+$111M, +$507M]). With no line at all equal capital scores best ($0.87B against D's $0.76B): the recommendation is the book and its facility together. Every process needs a facility of $2.46B–$3.15B, called in 45–50% of scenarios, costing $126M–$147M in expected present value. Capital committed on the day: $3.42B–$3.81B of the $3.82B budget, almost all lease capital and construction reserve. The risk-aware book re-solved with the $2.53B line as a hard constraint holds 9 members, needs $1.31B, and scores −$49M [−$127M, +$23M] against D: the recommended book stands. *Status: computed, post-registration; Figure F51; `results/v2/books_financed.csv`, `books_financed_pairs.csv`.*

**Dependence and worlds (Issue 4).** Book D's worst-5% loss as the share of co-moving scenarios rises from 0 to 1: −$0.03B, $0.20B, $0.53B, $0.69B, $0.82B; comonotonic bound $2.19B (A $3.66B, C $3.43B). D keeps the smallest tail at every setting and loses the metric lead only below ω = 0.5. In seven worlds D scores best in all 7 and is the only book with a positive metric when ERCOT prices are 25% lower ($0.54B; A −$0.84B, C −$0.75B) or oil is $45 for five years ($0.22B; A −$0.06B, C −$0.03B). *Status: computed; Figure F52; `results/v2/dependence_dial.csv`, `books_worlds.csv`.*

**The stronger baseline (Issue 5).** A fixed optimizer-first rule leaves the committee at $995M per case, the challenger at $981M: the language model against the rule is −$14M [−$36M, +$2M]; the rule against the checklist +$56M [+$19M, +$100M]; the optimizer above the rule +$121M [+$59M, +$195M]. The registered rungs reproduce exactly (+$76M, +$43M, +$134M). The model's incremental decision value over a strong automated process is not demonstrated; its distinct value is naming flaws of argument (12 of 12) without over-challenging (0 of 12). *Status: computed, reported beside C34, which stays as scored; Figure F53; `results/v2/ladder_five_arms.csv`, `ladder_five_rungs.csv`.*

**The allocation table (item 6).** Book D: 5 leases ($1.42B, each losing in 13–18% of scenarios), 3 requests with agreements ($535M–$759M each, losing in 62–64%), 5 waiting requests ($43M–$87M of deposits and reserve each, losing in 91–97%); $3.78B committed; removal costs from $3M to $539M. Outside the book: 12 defer pending information, 14 monitor, 1 reject. *Status: joined from notebook 11; Figure F54; `results/v2/book_D_members.csv`.*

## 4. Scenario methodology: assessment

The scenario engine (notebook 08) resamples calendar-year blocks of the 2018–2024 monthly log changes of WTI, Henry Hub and ERCOT prices together, reverts them toward their 2018–2024 real means with a four-year half-life, and carries output, cost and timing draws; 2,000 primary paths choose the books and 2,000 held-out paths score them, redrawn in every component.

- *What it captures:* the joint movement of the three prices in one calendar year, including 2020 and 2022; the lumpiness of construction calls; completion uncertainty by request age and agreement status; cost uncertainty by a triangular multiplier.
- *What it cannot:* a joint tail worse than 2018–2024 (no 2008, no 2014–2016 oil collapse in the sample); a structural break in ERCOT's price formation (the sample straddles Winter Storm Uri, which the capping at ±1.5 a month in log terms attenuates); correlated completion failures beyond the modelled ρ; inflation and financing shocks (costs are real, the line's rate is fixed); a change in the tax-credit law after the decision date is a stress, not a scenario.
- *Mean reversion:* the four-year half-life lifts gas and ERCOT prices above 2024's, which is what makes the gas requests' scenario values exceed their flat-path values; the report says so and the ERCOT −25% world removes most of it.
- *The dependence finding:* removing co-movement cuts book D's worst-5% loss from $0.82B to $0.02B. The dial (section 3 above) shows the tail grows monotonically with the share of co-moving scenarios and that the comonotonic bound is not far above the joint tail: the risk is a real concentration — five leases on one oil path, eight requests on one ERCOT path — not an artefact of one dependence model. It would be an artefact only if the true co-movement were much weaker than 2018–2024's, and the first year after the decision (oil and ERCOT inside the bands, gas above) does not suggest so.
- *Recommended, not run:* (i) a regime-switching price model with a recession state drawn from 1990–2024 oil and gas history; (ii) a correlation stress that raises the inter-sector correlation of annual returns to its 2020 value for the whole horizon; (iii) a construction-delay-and-cost-overrun scenario with correlated delays across ERCOT requests; (iv) a financing shock that moves the line's rate with the oil path. Each should be registered with a criterion before it is scored.

## 5. Governance controls: what exists and what should change

| Control | Exists | Recommend |
|---|---|---|
| Reading shown and confirmed before computation | yes (`src/challenge.py`; the workflow's stage 3) | keep; add a stated default for every unstated rule in the prompt (post-registration test) |
| Missing rule against explicit zero | the reading leaves an unstated rule unset; the model wrote 0 for the tail weight in 8 of 48 cases (C37) | the confirmation step asks "you stated no tail weight; the registered default is 1" before anything is computed |
| Numbers verified outside the model | yes (`advisor_tools.verify_attributed`; every number checked against the fact sheet) | block a memo carrying any ungrounded number from being shown; today it is flagged and recorded |
| Guide rule in code | yes (guide only toward a book that keeps every rule and fixes a breach or beats the proposal clear of zero; downgrades recorded) | keep |
| Injection resistance | partly (15 of 20 held) | screen the statement for instructions before the reading; route any changed reading to a person |
| Human approval and override | yes (`src/ledger.py`: named authorizer; override needs five answers and the opposing case) | a second signature above a commitment threshold |
| Hash-chained audit records | yes | an external time-stamp of the chain |
| Model monitoring | the models are re-fitted by the pipeline; no schedule | a re-fit and re-registration schedule tied to the LBNL and ERCOT release cycle |

## 6. Editorial and structural shortcomings of v10, and the V2 remedy

- The executive summary was one paragraph per research question; V2 opens with a two-page decision brief that answers what to fund, for how much, with what risk, and under what conditions.
- Criteria codes (C33, C34) appeared in the body; V2 keeps them in Table 4 and the appendices.
- The risk-aware book was never shown as a table of its members; V2 has Table 2 and Figure F54.
- Financing was a paragraph of section 5; V2 gives it a section and a figure with every process on the same basis.
- The committee workflow existed only as code and a paragraph of Appendix B; V2 draws it and defines the five levels.
- Section titles were labels ("Q2 — Optimization"); V2's state the finding.
- Nothing in v10 claimed realized gains; V2 keeps that discipline and says in one place what is demonstrated, what is simulated and what is not yet validated.

## 7. What requires new computation and what does not

Computed in notebook 13 (done, post-registration, labelled): every book on the same funding basis with the line priced; the risk-aware book re-solved with the line as a constraint; the dependence dial and the comonotonic bound; the seven-world table; the optimizer-first arm; the member table. Proposed and not computed: the regime-switching and extreme-event scenarios, the correlation stress, the financing shock, a study with real committees. Changed by rewriting alone: the structure, the decision brief, the tables, the control matrix, the operational workflow, the committee example (quoted from a registered case and its recorded memo).
