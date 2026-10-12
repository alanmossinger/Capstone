# Prompt — recommend a book for one scenario

Scenario: **{scenario}**. {scenario_description}

Budget: {budget}. Technology cap: {technology_cap} of the budget in any one technology. Revenue case: {revenue_case}.

Using only the tables, recommend the book for this scenario. Answer with this JSON object and nothing else:

```json
{{"book": "<name of the book you recommend, one of the names in the books table, or 'custom'>",
  "members": ["<project_id>", "..."],
  "expected_npv_usd_billion": <number from the tables>,
  "tail_usd_billion": <the 5% tail (CVaR) from the tables, a loss as a positive number, a profit as a negative number>,
  "binding_constraint": "<budget | technology cap | nothing binds | not in tables>",
  "why": "<three sentences, every number cited as shown in the tables>",
  "what_would_change_the_answer": "<one sentence naming the figure and the level at which the recommendation flips>",
  "weakest_provenance": "<OBSERVED | DERIVED | FORECAST | ASSUMED>"}}
```
