# Challenge round — renewables_only

## The human's statement

I want to drop oil and gas and fund the contracted wind and solar requests only. The energy transition will strand the leases within ten years, the PPA makes wind safe, and a book of renewables is what our lenders want to see.

## The advisor's questions

1. You wrote that the PPA makes wind safe and that the leases will be stranded within ten years. If the contracted wind and solar book is wrong, which of those two beliefs carries the loss? How large a shortfall against the budget could the company and its lenders absorb before you would call the choice a mistake?

2. You said lenders want to see renewables. Do they care about the label on the book, or about the worst 5% of outcomes in it? What does the budget committee want from this book: the highest expected NPV, a floor on losses, or a story it can defend? What does the operator who runs the leases lose or keep if we drop them? And what do you expect the grid operator's queue process to do to the timing of the wind and solar requests you pick?

3. Where does your conviction come from? Is any deposit already paid or any lease already held, so that dropping the leases feels like writing off a sunk cost? Have you defended this view in public or to the committee before? Do you simply like renewables and dislike oil and gas?

4. You leaned on the PPA and on the ten-year stranding argument. Which table or figure did you look at, and which did you skip? Did you check the flat-price path against the named scenarios, especially the simultaneous downside? Did you compare the mean with the median, and the contracted revenue case with the merchant case? Did you look at how likely each wind or solar request is to be built at all? Did you ask what price or breakeven would make the leases lose money?

5. You framed this as leases against contracted wind and solar. With a 40% cap per technology, can a wind-and-solar-only book even spend the whole budget? What did you leave off the table: a mixed book, a smaller book, a book that keeps some leases for a fixed period, waiting for queue or price news, or funding nothing this round?

## The human's answers

Q1. You wrote that the PPA makes wind safe and that the leases will be stranded within ten years. If the contracted wind and solar book is wrong, which of those two beliefs carries the loss? How large a shortfall against the budget could the company and its lenders absorb before you would call the choice a mistake?
A1. If the renewables book is wrong the loss is the deposits and study costs on requests that never operate, plus the lease value we gave up; the worst case is a queue in which none of the requests is built.

Q2. You said lenders want to see renewables. Do they care about the label on the book, or about the worst 5% of outcomes in it? What does the budget committee want from this book: the highest expected NPV, a floor on losses, or a story it can defend? What does the operator who runs the leases lose or keep if we drop them? And what do you expect the grid operator's queue process to do to the timing of the wind and solar requests you pick?
A2. The committee wants a book that holds its value; the lender wants the PPA and a thin tail; the operator has no renewables experience; the grid operator decides whether any request is built at all.

Q3. Where does your conviction come from? Is any deposit already paid or any lease already held, so that dropping the leases feels like writing off a sunk cost? Have you defended this view in public or to the committee before? Do you simply like renewables and dislike oil and gas?
A3. I want the company to be seen as part of the transition and I have argued that position in public; that is a past position I am defending.

Q4. You leaned on the PPA and on the ten-year stranding argument. Which table or figure did you look at, and which did you skip? Did you check the flat-price path against the named scenarios, especially the simultaneous downside? Did you compare the mean with the median, and the contracted revenue case with the merchant case? Did you look at how likely each wind or solar request is to be built at all? Did you ask what price or breakeven would make the leases lose money?
A4. I leaned on the contracted wind NPVs and on the PPA making wind safe; I passed over the chance of operating within seven years, the solar requests that are negative even under contract, and the leases' expected NPV.

Q5. You framed this as leases against contracted wind and solar. With a 40% cap per technology, can a wind-and-solar-only book even spend the whole budget? What did you leave off the table: a mixed book, a smaller book, a book that keeps some leases for a fixed period, waiting for queue or price news, or funding nothing this round?
A5. I left off the table a mixed book in which the leases carry the budget and the contracted wind rides alongside, and a smaller renewables position inside book D.

## The motivated-reasoning check

# Motivated-reasoning check

Your book, as the tables define it, is "power only (D rule)". It holds five requests, all wind, and no solar. The book you rejected is "leases only (D rule)", and book D is the nearest mixed alternative.

## 1. The patterns, with your sentences

1. **Working backward from the conclusion.** "I want to drop oil and gas and fund the contracted wind and solar requests only." The answer comes first and the reasons follow. In A1 you did not name a shortfall you could absorb, so nothing could prove the choice wrong.
2. **Treating ASSUMED and FORECAST figures as observed.** "The PPA makes wind safe." You also treat the queue as if it will deliver.
3. **Cherry-picking the column and the sector.** A4: "I leaned on the contracted wind NPVs." You passed over the chance of operating, the solar that is negative under contract, and the lease NPVs.
4. **A double standard.** "The energy transition will strand the leases within ten years." The leases are judged on a story from outside the tables. The wind is judged on the most favourable column in the tables.
5. **Moving the goalposts.** "A book of renewables is what our lenders want to see." In A2 this becomes "the lender wants the PPA and a thin tail." The test changed from a label to a tail.
6. **Defending a past position.** A3: "I have argued that position in public; that is a past position I am defending." The tables hold no deposit figure, so this is not a deposit sunk cost. It is the same pattern with a reputation as the sunk cost.
7. **Narrowing the option set.** A5: you left off the table "a mixed book in which the leases carry the budget" and "a smaller renewables position inside book D."

## 2. What the tables show

**The two books side by side.** The scoring is out of sample, in the contracted revenue case, and is a FORECAST.

| book | expected NPV | 5% tail (CVaR95 loss) | p_negative | capex |
|---|---|---|---|---|
| power only (D rule) | $0.39B | 0.08 | 0.68 | $9.63B |
| leases only (D rule) | $8.71B | -2.28 | 0.00 | $1.37B |
| D risk-aware MILP | $7.59B | -2.22 | 0.00 | $15.3B |

A negative tail means the worst 5% is still a profit. Your book's tail is a loss of $0.08B.

- **Pattern 1.** The tables do not support the preferred book on any of the three measures. Expected NPV is $0.39B against $8.71B. The tail is a loss against a profit. The chance of a loss is 0.68 against 0.00.
- **Pattern 2.** The scoring already uses the contracted revenue case, so the PPA is already in your $0.39B. Even so, 0.68 of scenarios are negative.
  - The PPA is ASSUMED. The timing is FORECAST. The weakest label behind your case is ASSUMED.
  - Without the PPA, all five wind requests are negative in the merchant case: -106.6, -19.1, -32.7, -13.2 and -13.4 ($M).
  - The chance of operating within seven years is 0.26 for 26INR0113 and 0.03, 0.04, 0.03 and 0.03 for the other four.
- **Pattern 3.** Solar is not in your book. Its capital is 0.00 in the technology table.
  - Four of the five solar requests are negative even under contract: -24.9, -9.82, -25.9 and -9.67 ($M).
  - The fifth, 24INR0075, is +25.8 under contract and -196.0 merchant, with a 0.29 chance of operating.
  - The lease expected NPVs you skipped run from 56.9 to 1,348 ($M).
- **Pattern 4.** The tables hold no ten-year stranding case. They hold flat 2024 prices.
  - The only oil stress, "oil collapse (2020 path)", shows lease NPV of $8.25B against $8.23B in base. It does not test your thesis either way.
  - The table does not state the current WTI price, so we cannot say how far the market sits from the lease breakevens.
  - The 13 leases in book D break even between 31.0 and 35.4 flat WTI $/bbl.
  - The simultaneous downside, which you did not mention, moves the default book of forty from $6.99B to $5.42B (-1.56). Leases stay at $7.15B. Power falls from -1.24 to -1.72.
  - The same standard cuts against the leases. Lease costs are ASSUMED, and their data completeness is 0.80 against 1.00 for the requests. Many lease NPVs are large against small capex (for example G14658, $1,348M on $96.0M). That ratio rests on the ASSUMED cost grid.
- **Pattern 5.** On the tail, the leases-only book is -2.28 and book D is -2.22. Your book is +0.08. By the standard you named in A2, the tables favour the book you rejected.
- **Pattern 6.** The tables carry no price on a public position. Nothing in them depends on it.
- **Pattern 7.** The tables score mixed books.
  - Book C has $7.71B expected NPV and a -2.03 tail.
  - Book D has $7.59B and -2.22. It holds $0.69B of leases and $0.66B of wind, and all of its figures are in the tables.
  - The budget is $1.79B and the cap is 40% per technology, which is about $0.72B per technology. Wind and solar together can hold at most about $1.43B, so a wind-and-solar-only book cannot spend the whole budget.
  - Your book shows $9.63B of capex in one table and $0.66B in the capital-by-technology table. The tables do not say why. If $9.63B is the real commitment, it is far above the budget.
  - The same applies to the rejected book. Leases-only holds $1.37B of leases, above the 40% cap as the tables define it. That book is not a cap-compliant alternative, so the fair comparison for your book is book D or book C.

## 3. Top three risks of your book

1. **Loss is the likely outcome.** The chance of a negative outcome is 0.68, and the 5% tail is a loss of $0.08B. *Mitigation:* a smaller position, sized to a loss limit you state in dollars. You did not give one in A1.
2. **Queue timing.** Four of the five requests have a 0.03 to 0.04 chance of operating within seven years, and the fifth has 0.26. That is FORECAST. In the stress table, the two-year delay takes the power side from -1.24 to -1.36 ($B). *Mitigation:* a later gate. Release capital only after a request clears a queue step.
3. **The PPA is an assumption and one request carries it.** 26INR0113 is worth 208.0 ($M) under contract against 46.2, 30.4, 18.7 and 31.9 for the others. All five are negative without the PPA. *Mitigation:* a signed contract before funding, which turns an ASSUMED input into an OBSERVED one.

## 4. Verdict

The decision does not survive the check. The change that would make it survive is a signed contract plus a queue gate that moves the wind book's chance of a loss from 0.68 and its 5% tail from a $0.08B loss to a profit, because without that the label is the only thing the book has over the leases.

## The opposing case

## The case for Book D, argued as its advocate

**Corrections first.** Book D holds 13 leases, not twenty. The twenty-lease book is the "leases only" row. Book D's `capex_$B` column reads 15.3, against a budget of $1.79B. The technology table puts D at 1.67. I use the technology table and cannot reconcile the two from the data.

**Strongest point: your book cannot be funded and does not hold its value.** The only scored wind-and-solar book is "power only", and it holds just five wind requests.
- It spends 0.66 of the $1.79B budget.
- Its expected NPV is 0.39 ($B), and its 5% tail is +0.08, a loss.
- Its probability of a negative outcome is 0.68.
- Book D scores 7.59, a tail of -2.22 (the worst 5% is still a profit) and a probability of loss of 0.00.

You asked for a book that holds its value. Power-only loses money in 68% of the held-out scenarios.

**The PPA does not make wind safe.**
- The only wind request with a meaningful contracted NPV is 26INR0113 at 208.0 ($M), and its p_operation_7y is 0.26.
- Its merchant NPV is -106.6. The gap between the two is the PPA, and the PPA is ASSUMED.
- The other four wind requests have p_operation_7y of 0.03, 0.04, 0.03 and 0.03. Their contracted NPVs are 46.2, 30.4, 18.7 and 31.9.
- That is your answer to your own Q1: the loss is carried by the queue, not by the leases.

**Solar does not help.**
- Four of the five solar requests are negative even under contract: -24.9, -9.82, -25.9 and -9.67.
- The fifth, 24INR0075, is +25.8 with p_operation_7y of 0.29. No book in the tables holds any solar.

**Leases are the only candidates with certain operation.**
- Every lease has p_operation_7y of 1.00. G14658 alone is 1,348 ($M) at 96.0 capex.
- The leases-only book scores 8.71 expected and -2.28 at the tail.
- In the simultaneous downside (WTI path, gas, wind, solar, two-year delay, cost 1.20 together), the lease sleeve of the default forty is still 7.15. The power sleeve there is -1.72.

**Your best objection** is that lenders and the committee want the transition story, and D still holds oil and gas. My answer:
- D already contains your wind. Its wind capital is 0.66, the same as the power-only book. Every one of the five wind requests is in D.
- The leases carry the budget (0.69) so that the wind can be held without the loss in the power-only row.
- You named this book in A5 as one you left off the table.
- On the stranding argument, the tables give a flat-price breakeven for each lease. D's leases run from 31.0 to 35.4 flat WTI $/bbl.
- The tables contain no ten-year price path, so I cannot test "stranded within ten years" against them.

**The assumption my case rests on** is the ASSUMED lease cost grid, on top of FORECAST production.
- The case fails if flat WTI falls below 35.4 for D's weakest lease. It fails across the whole lease sleeve below 53.2, the highest breakeven in the table, which belongs to G17001, a lease not in D.
- The tables do not give the base WTI price, so I cannot state the margin.
- The oil-collapse row shows lease NPV of 8.25, against 8.23 in the base. Its WTI path reads "2,020", which is not a price. I cannot reconcile that row with the breakevens and do not rely on it.
- The stress rows also describe the whole default forty, not the wind-only sleeve.

## In my own voice

On the tables, Book D beats your power-only book on every column (7.59 against 0.39, and -2.22 against +0.08). But the leases-only book beats D on both expected NPV (8.71) and tail (-2.28), so D's two gas CC members (-43.2 and -60.9) and its storage member (-12.2) are not paid for in the scored results. Replacing the lease cost grid with operator quotes, getting queue status for 26INR0113, and adding a ten-year price path would settle most of what is open.

CONVERGE: Book D, with the leases carrying the budget and the five contracted wind requests as the renewable sleeve | DISAGREE: whether leases are stranded within ten years, which the tables cannot test
