# Prompt — read the committee's rules from its own words

> Status: decision #94. You turn the committee's words into rules the model can enforce and tests it can run; you compute nothing.

The investment committee proposes a book and explains why:

> {statement}

Its proposed book: {proposal}

**1. The rules.** Read the statement into the preference fields below. Fill in only what the statement says or clearly implies — a stated limit, a technology the committee will not fund, a construction budget beyond the reserve. Leave a field out when the statement is silent; do not guess a number the statement does not give.

{schema}

**2. The assumptions to test.** If the statement rests on a belief about markets or costs that one of the what-if parameters below can represent (an oil price, ERCOT price volatility or level, a cost multiplier, a delay), you may ask for up to two what-ifs, so the model can show how the proposal fares if the belief is wrong. Ask only for what tests the statement; leave the list empty otherwise.

{whatif_schema}

Answer with one JSON object and nothing else:

```json
{{"preferences": {{"<field>": <value>, "...": "..."}},
  "whatifs": [{{"<parameter>": <value>}}],
  "reading": "<one sentence: the committee's objective and rules as you read them>",
  "not_representable": "<what the statement asks that these fields cannot hold, or an empty string>"}}
```
