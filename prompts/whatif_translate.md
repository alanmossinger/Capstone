# Prompt — turn a committee question into a what-if the model can compute

> Status: v8 (decision #91). The model chooses parameters; it never computes a number.

The investment committee asked:

> {question}

Translate the question into the parameters below, so the portfolio model can compute the answer. Change only what the question asks; leave everything else out. If the question asks for something these parameters cannot represent — a market, a cost, a project or a measure that is not in the list — do not approximate it: say so.

{schema}

Answer with one JSON object and nothing else, either

```json
{{"whatif": {{"<parameter>": <value>, "...": "..."}}, "reading": "<one sentence: how you read the question>"}}
```

or

```json
{{"cannot_answer": "<one sentence: what the question needs that the parameters do not have>"}}
```
