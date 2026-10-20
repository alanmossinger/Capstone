# Challenge round — all_leases

## The human's statement

I want the twenty leases and nothing else. The leases earn $8.2B at base and every one of them is positive; the power requests lose money at 2024 prices and most of them never reach operation. Oil has always paid for this company and I do not see why we should learn a new business now.

## The advisor's questions

1. You want the twenty leases and nothing else, and you cite $8.2B at base with every lease positive. If that book is wrong, which number carries the loss: the lease costs, the production forecasts, or the flat oil price? And what is the worst case you have in mind for the $1.35B you would commit, in dollars and in the share of the $1.91B budget left unspent?

2. The committee that sets the budget, the lender who looks at the tail, the operator who runs the leases, and the grid operator who decides whether a request is built each want something different. What does each of them want from this book? In particular, would the committee or lender accept a book that uses only $1.35B of a $1.91B budget, and would the operator have the capacity to redevelop all twenty leases at once?

3. You say oil has always paid for this company and you see no reason to learn a new business. Where is your emotional investment: deposits already paid, leases we already hold, a past position you defended, or simply a sector you like and one you dislike? Would you still choose all twenty leases if none of them were held today?

4. Your case leans on the base figure and on the fact that the power requests lose money at 2024 prices and mostly never reach operation. Which table or figure did you rely on, and which did you pass over? Did you look at the scenario results, including the simultaneous downside, or only the flat path? Did you look at the mean or the tail? Did you consider that the lease costs are assumed, not observed? And did you look at the contracted revenue case for the wind requests, or only the merchant one?

5. Your book has two alternatives you left off the table. One is a mixed book that spends the full $1.91B and respects the 40% technology cap. The other is a smaller or staged book: fund only the leases with the lowest breakeven oil price, wait for the queue to clear, or fund nothing yet. Which of these did you consider, and why did you reject each?

## The human's answers

Q1. You want the twenty leases and nothing else, and you cite $8.2B at base with every lease positive. If that book is wrong, which number carries the loss: the lease costs, the production forecasts, or the flat oil price? And what is the worst case you have in mind for the $1.35B you would commit, in dollars and in the share of the $1.91B budget left unspent?
A1. If the leases are wrong the loss is the redevelopment capital, about $1.4B under the registered grid and four times that under the committee's; the worst case I have in mind is five years of $42 oil.

Q2. The committee that sets the budget, the lender who looks at the tail, the operator who runs the leases, and the grid operator who decides whether a request is built each want something different. What does each of them want from this book? In particular, would the committee or lender accept a book that uses only $1.35B of a $1.91B budget, and would the operator have the capacity to redevelop all twenty leases at once?
A2. The committee wants the budget on what already produces; the lender wants a thin tail; the operator wants workovers it knows how to run; the grid operator decides nothing on the lease side, which is part of why I like it.

Q3. You say oil has always paid for this company and you see no reason to learn a new business. Where is your emotional investment: deposits already paid, leases we already hold, a past position you defended, or simply a sector you like and one you dislike? Would you still choose all twenty leases if none of them were held today?
A3. The company has run offshore oil for thirty years and I have defended the Gulf position in every budget round; the queue deposits already paid are small and I do not count them.

Q4. Your case leans on the base figure and on the fact that the power requests lose money at 2024 prices and mostly never reach operation. Which table or figure did you rely on, and which did you pass over? Did you look at the scenario results, including the simultaneous downside, or only the flat path? Did you look at the mean or the tail? Did you consider that the lease costs are assumed, not observed? And did you look at the contracted revenue case for the wind requests, or only the merchant one?
A4. I leaned on the flat-path lease NPVs and on every lease being positive at base; I passed over the scenario median, the committee grid's high case and the contracted wind requests that are positive.

Q5. Your book has two alternatives you left off the table. One is a mixed book that spends the full $1.91B and respects the 40% technology cap. The other is a smaller or staged book: fund only the leases with the lowest breakeven oil price, wait for the queue to clear, or fund nothing yet. Which of these did you consider, and why did you reject each?
A5. I did not put a mixed book on the table, nor a smaller lease book that leaves room for the four contracted wind requests.

## The motivated-reasoning check

**Reference numbers (all from the tables)**

| Book | Expected NPV (out of sample) | 5% tail (CVaR95 loss) | Chance of a loss | Capital vs $1.91B budget |
|---|---|---|---|---|
| Yours: leases only (20) | $8.66B | -2.28 | 0.00 | $1.35B |
| D risk-aware MILP (21) | $7.67B | -2.20 | 0.00 | $1.85B (technology table) |
| C deterministic MILP (21) | $7.73B | -2.18 | 0.00 | $1.91B (technology table) |
| Power only (4 wind) | $0.56B | 0.06 | 0.60 | $0.76B |

A negative tail means the worst 5% is still a profit. The weakest label behind your book is ASSUMED (lease costs), under FORECAST production. The book table shows capex of $4.31B to $15.2B for books A to D, above the budget. The technology table shows at most $1.91B. We cannot reconcile the two, so we use the technology table for budget and cap.

The numbers do not refute your book. It scores best on expected NPV and tail. The weakness is in how you got there.

**1 and 2. Patterns and what the tables show**

1. **Working backward from the conclusion.**
   - Your sentences: "I want the twenty leases and nothing else" and "I do not see why we should learn a new business now."
   - The conclusion comes first. None of your five answers cites the out-of-sample table.
   - The lease edge is real: $8.66B against $7.67B for D, and a tail of -2.28 against -2.20. You never used it.
   - Your Q3 answer, "I have defended the Gulf position in every budget round", does not say whether you would pick the leases if none were held.

2. **A dropped criterion (moving the goalposts).**
   - You open with "one budget and a 40% cap per technology." Your book then puts $1.35B in one technology.
   - 40% of $1.91B is $0.764B. C and D each hold $0.76B of leases.
   - Your book is about $0.59B over the cap and about 71% of the budget in leases. It also leaves $0.56B unspent, about 29% of the budget. You did not answer that part of Q1.
   - The table calls it "leases only (D rule)", a comparison book. It beats D partly because it is not held to the cap D is held to.

3. **A double standard.**
   - You judged the leases on "flat-path lease NPVs" and the requests on "lose money at 2024 prices."
   - Leases carry p_operation_7y of 1.00 in the table. Requests carry 0.01 to 0.36, with 0.36 the highest.
   - You treat the request odds as settled ("never reach operation") and the lease 1.00 as fact. Both are modelled.
   - You gave a mean ($8.2B) and no tail, though your lender answer says "a thin tail."
   - Your dismissal of power partly stands. In the contracted case the power-only book has a 0.60 chance of a loss and a tail of 0.06.

4. **Cherry-picking.**
   - Your sentence: "I leaned on the flat-path lease NPVs… I passed over the scenario median, the committee grid's high case and the contracted wind requests."
   - The simultaneous downside takes the leases from 8.19 to 7.11 and the whole forty from 7.09 to 5.69, a change of -1.40. That would not have hurt your case, but you never tested it.
   - The oil-collapse row shows leases at 8.21 against 8.19 at base. That row cannot show oil protection, and its wti_path reads "2,020". Do not lean on it.
   - The tables hold no "scenario median" and no "committee grid", so we cannot check those.
   - Ten requests are positive when contracted: five solar and five wind. You named four. The four wind requests in the book are 346.0, 55.0, 53.5 and 38.3, and all are negative merchant (-63.5, -11.5, -10.9, -7.95). The contracted case rests on an ASSUMED PPA.

5. **Treating ASSUMED as observed.**
   - Your sentences: "$8.2B at base and every one of them is positive", and "four times that under the committee's."
   - Every lease is positive in the table, the lowest at 62.2. The provenance is "FORECAST production; ASSUMED costs; DERIVED NPV", with data_completeness 0.80 against 1.00 for the requests.
   - The tables hold one cost grid. The only cost test is the 1.20 multiplier inside the simultaneous downside, mixed with oil and delay. "Four times" and "$42 oil" are not in the tables.
   - You did not say which of the three (costs, production, oil) carries the loss.

6. **Commitment to a past position.**
   - You say you do not count the queue deposits. That part passes.
   - "Thirty years" and "defended… in every budget round" are the same pull, and neither appears in any table.
   - "The grid operator decides nothing… part of why I like it" is a preference. The tables hold nothing on operator capacity for twenty leases at once or on whether the committee accepts an unspent $0.56B, and you did not answer either.

**3. Top three risks in your book**

1. **ASSUMED lease costs behind 100% of the capital.**
   - Leases fall from 8.19 to 7.11 in the one stress that includes a cost multiplier (1.20).
   - Mitigation: rerun the book on the committee's cost grid, a different grid case, and read the tail there.
2. **Concentration and the cap breach.** The book holds $1.35B in one technology against a $0.764B ceiling.
   - Mitigation: a smaller position. D's 14 leases total $0.76B, with breakevens of 30.6 to 39.9 flat WTI $/bbl. Otherwise get a written waiver of the cap.
3. **Oil price on the high-breakeven leases.**
   - Three leases break even above your $42: G17001 at 50.6, G07963 at 50.3 and G07962 at 45.1. Together they carry $248M of capex (our sum). G17565 sits at 41.4.
   - The stress table does not test this.
   - Mitigation: a later gate, funding those three only after a price test.

**4.** Your decision does not survive the check as reasoned. It would survive if you resolve the cap breach, by shrinking the lease sleeve to about $0.76B or getting the committee's written waiver, and then show the numbers still favor it.

## The opposing case

**The case for Book D, argued as its advocate**

We start from your own worst case: five years of $42 oil. Three of your twenty leases fail it. G07963 breaks even at 50.3, G07962 at 45.1 and G17001 at 50.6, all in flat WTI $/bbl. G17565 clears it by 0.6 (41.4). Your A1 answer names the loss, but the leases-only book commits capital to these four anyway. Book D holds 14 leases, and the highest breakeven among them is 39.9. D screens against the exact case you fear.

The stress table cannot show that the lease book survives $42 oil. Its oil-collapse row moves the lease book from 8.19 to 8.21, which is up, not down. That row tests nothing, so your comfort about oil rests on the base case alone. All twenty leases also share one label: FORECAST production on ASSUMED costs, with data completeness of 0.80. The four wind requests have 1.00 completeness and revenue that does not depend on oil. Their contracted NPVs are 346.0, 55.0, 53.5 and 38.3. Merchant wind loses money, so D holds it only under contract.

Your best objection is that D does worse on every number we can score. We concede that below. The one point we hold is that those scores share the same weak label. A lease cost shock hits both books, but the leases-only book carries 1.35 of lease capital against D's 0.76, so it is more exposed to that shock. The tables do not size this.

**Where this case rests, and where it fails**
- It rests on the ASSUMED PPA behind the contracted wind figures and on the FORECAST chance of operation. Three of the four wind requests have p_operation of 0.03 to 0.04. Of the 492.8 total contracted wind NPV, 346.0 sits in one request, 26INR0113, at p_operation 0.36.
- It fails at the book table's own numbers. The wind-only book has expected NPV of 0.56 and p_negative of 0.60. D's expected NPV is 7.67 against 8.66 for leases only.
- D also holds gas CC and storage. Their NPVs are negative even under contract, for example -44.1, -62.1 and -12.4.

**Out of role**

On the tables, leases only is the stronger book. It earns 8.66 against 7.67 for D, its CVaR95 is -2.28 against -2.20, p_negative is 0.00 for both, and it uses 1.35 of capital against 1.85. What would settle it is a stress run of the leases-only book itself at a $42 oil path and a lease-cost multiplier, plus the PPA terms for 26INR0113.

Three flags on the data:
- The books table shows D's capex at 14.0. The technology table shows 1.85. I used 1.85.
- Your "four times that under the committee's grid", the scenario median and the committee high case are not in the tables, so I cannot check them.
- I cannot show that leaving 0.56 of the 1.91 unspent (about 29%) costs or saves anything.

CONVERGE: the leases-only book of twenty leases (capex 1.35, expected NPV 8.66, CVaR95 -2.28) | DISAGREE: whether to hold back G07963, G07962 and G17001, whose breakevens exceed $42, and whether to put part of the unspent 0.56 into contracted wind 26INR0113
