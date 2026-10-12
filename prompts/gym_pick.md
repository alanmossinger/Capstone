# Prompt — the decision gym: pick a book as of {as_of}

It is {as_of}. You are choosing which of the candidates in the table to fund. The table holds only what was knowable on that date: size, technology, the models' probability of reaching operation, the cost to the next gate, the break-even price and the expected NPV at entry. No outcome is shown; do not guess at any.

Budget for this situation: {budget}. The sum of the chosen candidates' cost must not exceed it. Situation: {situation}.

Answer with this JSON object and nothing else:

```json
{{"members": ["<project_key>", "..."],
  "cost_used": <sum of their cost from the table>,
  "why": "<two sentences, every number cited as shown in the table>",
  "what_i_rejected_and_why": "<one sentence>"}}
```
