# The AI inside the decision: how the advisor is used, bounded and scored

This note describes the AI component of the project — the LLM advisor of notebook 10 and the dashboard — as a system: what it sees, what it may say, how every call is recorded, how its outputs are checked and scored, and where the human keeps the last word. It is the source for the report's AI appendix.

## 1. Where the advisor sits

The advisor is one actor in a decision process with four: instinct (top-N expected NPV), the registered rule (the gate verdict of notebook 09 part B for queue requests; the risk-aware MILP for the book), the advisor (an Anthropic model, called through the Messages API with a key or, without one, through the `claude` command line on a Claude subscription) and the human. It works in two modes, in this order:

- **Learn from history.** The decision gym replays sixteen documented situations as of their date — queue requests at entry and at the two-year gate in ERCOT, PJM and CAISO; the lease candidates at the start of the 2014, 2020 and 2022 oil-price regimes; a 2018 budget cut. Each actor picks a book under the same budget from the same as-of table; the realized value is revealed; one score per actor per situation goes to `results/decision_gym_scores.csv`.
- **Decide forward.** For the book of 2025–2044 the advisor recommends a book for the base case and each named stress, and for each horizon (1, 2, 3, 5, 10, 20 years), from the result tables; the human reviews it in the dashboard, may challenge it, and may override it through the gate.

## 2. What the advisor sees: the grounding rule

The model receives a system prompt (`prompts/advisor_system.md`) and a user message that holds the task template and a **DATA** block: result tables of `results/` rendered as text by one formatter (`advisor.format_table`). Nothing else — no web, no memory across calls, no company data. The tables carry their provenance labels (OBSERVED, DERIVED, FORECAST, ASSUMED), and the prompt requires the answer to name the weakest label behind a recommendation.

Every number in an answer is checked mechanically (`advisor.verify_numbers`): it must appear in the DATA block as the same token. Years and counts up to 50 are exempt. A number the model rounded differently from the table counts as ungrounded on purpose: the rule the prompt states is "exactly as shown". The grounding rate and the ungrounded tokens are stored with every answer and summarised in `results/advisor_evaluation.csv`.

## 3. Record and replay

The "reason my thinking" round runs with the human in the loop (decision #79): the advisor asks five questions tied to the human's statement, the human answers, and only then does it judge and argue the opposing book; at the keyboard this is `python -m src.advisor`. Every call is appended to `results/advisor_runs.jsonl` with the model id, the backend, the sampling setting, the token limit, the full system and user prompts, the response, the token usage and the verification. The key of a record is the hash of (model, system prompt, user message). A call whose key is recorded is served from the record; so `make all` runs offline, the report's AI section reproduces without a key, and a reader can audit each answer against the prompt that produced it. With no key and no record, the advisor's rows read "not recorded" and nothing else in the pipeline changes.

The key, when used, lives in `.env` (`ANTHROPIC_API_KEY`), read by `python-dotenv`; it is never printed, logged, written into a notebook output or committed. Without a key, `src/advisor.ask_cli` runs `claude -p` signed in to the author's Claude subscription, with the system prompt replaced, no tools, no MCP servers, no CLAUDE.md or memory, in an empty folder, so the model receives exactly the system prompt and user message the API would (decision #76). Model id: `claude-sonnet-5-5`, at the model's default sampling, because this model rejects any other temperature and the command line exposes none.

## 4. The three modes and their prompts

1. **Recommend** (`prompts/recommend.md`): a JSON object — the book, its members, the expected NPV and the 5% tail cited from the tables, the binding constraint, three sentences of why, one sentence on what would change the answer, the weakest provenance. Agreement with the optimizer is measured as the Jaccard similarity of the recommended members to book D.
2. **Challenge** ("reason my thinking"): two rounds. The motivated-reasoning check (`prompts/motivated_reasoning_check.md`) asks at most five questions — context and stakes, what each party wants, emotional investment, evidence emphasised against dismissed, framing — then names the patterns (moving goalposts, double standards, working backward, cherry-picking, a modeled number read as observed) with the sentence that shows each and the table figure that answers it. The ideological Turing test (`prompts/ideological_turing_test.md`) argues the opposing book as its strongest advocate, answers the human's best objection, names the assumption the opposing case rests on, steps out of role, and ends with `CONVERGE: … | DISAGREE: …`, which the dashboard reads.
3. **Decision gym** (`prompts/gym_pick.md`): a pick within the budget from an as-of table that shows no outcome, with two sentences of why and one of what was rejected.

The two reasoning prompts are the author's instruments for a decision meeting, written as templates; the files in `prompts/` are the actual prompts used, as the course asks.

## 5. The override gate

In the dashboard the human may override the advisor's (or the optimizer's) book only after answering the five questions of the motivated-reasoning check — at least twenty characters each — and confirming that the opposing case was read (`advisor.override_allowed`). An override without the answers is refused with the missing items named. Every proposal, answer, override and later realized outcome is appended to `results/decision_ledger.csv` (actor, mode, horizon, budget, λ, cap, members, capital, out-of-sample expected NPV and CVaR, override flag, the answers, the realized value and what it was scored on).

## 6. How the AI outputs are evaluated

`results/advisor_evaluation.csv` (notebook 10): the number-grounding rate over every recorded answer and the share of answers with every number grounded; the agreement with the optimizer (mean Jaccard to book D and the share naming D) over the seven named scenarios; the gym score — the advisor's realized value minus instinct's, the number of situations won, the mean regret against hindsight for each actor; the number of challenge rounds recorded; the model id. `results/advisor_rubric.csv` holds up to ten answers with the mechanical rubric items (names a book, cites three grounded numbers, every number grounded, states what would change the answer, names the weakest provenance) and an empty `human_label` column for the author's own reading.

## 7. What the advisor is not

It is not a forecaster, an optimizer or a source of numbers: every figure it can cite was produced by notebooks 07–09 from the data of notebook 01. It is not the decision maker: the gate gives the human the last word, and the ledger makes that word accountable. Its value is measured in the gym, against realized outcomes, next to the rule it is meant to improve on; where the record is empty the report says "not recorded" rather than describing an answer that does not exist.
