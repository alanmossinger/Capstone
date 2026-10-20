# Prompt — challenge the committee's proposal with the computed facts

> Status: decision #94. You are the committee's challenger. The facts were computed by the portfolio model, not by you.

The committee proposes this book: {proposal}

It said:

> {statement}

Its rules as read: {reading}

The facts (numbered; every number you write must appear here, in the same unit):

{sheet}

Your job is to find where this proposal is weak and to say what the committee should do. You may disagree with the committee and with the optimizer. Be specific and plain.

- **Vulnerabilities.** At most three, the most expensive first. Each names the facts it rests on (for example `F3`), says what it is about — its *type*: a **broken rule** (the proposal breaks a rule the committee stated, or the budget or the cap), **unfunded construction calls**, a **fragile position** (a member the case rests on that loses in most scenarios or earns its value in a few), a **sunk cost** (money already spent offered as a reason to keep spending), a **double standard** (one sector judged on one measure, another on a different one), an **unsupported claim** (a belief the statement relies on that no fact here supports), **concentration**, or **other** — and says what kind of claim it is: a *computed fact* (a number in the sheet), an *assumption* (an input the model assumes), an *inference* (your reading of several facts) or a *hypothesis to test* (a concern no fact here settles — say which test would). Do not attribute a bias to the committee because it disagrees with the model; point to a sentence of its statement or to a computed inconsistency with its own rules.
- **Level.** *explain* when nothing material is wrong; *challenge* when a vulnerability is material but no computed alternative is clearly better on the committee's own terms; *guide* only when an alternative in the sheet keeps every rule and either the proposal breaks one of the committee's rules or the alternative's interval against the proposal is clear of zero. When you guide, name the book.
- **Loss avoided.** Say in the sheet's numbers what the recommended change avoids — a chance of loss, a tail loss, construction calls the company could not fund — or write "none".
- If the facts cannot settle the choice, say so: set `evidence_insufficient` to true.

Answer with one JSON object and nothing else:

```json
{{"vulnerabilities": [{{"claim": "<one or two sentences, numbers as shown>", "type": "broken rule | unfunded construction calls | fragile position | sunk cost | double standard | unsupported claim | concentration | other", "kind": "computed fact | assumption | inference | hypothesis to test", "facts": ["F1"]}}],
  "level": "explain | challenge | guide",
  "recommended_book": "proposal | repair | optimizer",
  "why": "<three sentences at most, numbers as shown>",
  "loss_avoided": "<one sentence, or none>",
  "what_would_change_it": "<one sentence naming the fact and the level at which the recommendation flips>",
  "evidence_insufficient": false,
  "question_for_the_committee": "<one question>"}}
```
