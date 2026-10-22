# Challenge round — all_leases

## The human's statement

I want the twenty leases and nothing else. The leases earn $8.2B at base and every one of them is positive; the power requests lose money at 2024 prices and most of them never reach operation. Oil has always paid for this company and I do not see why we should learn a new business now.

## The advisor's questions

1. You say the twenty leases earn $8.2B at base and every one is positive. If that book is wrong, which number carries the loss: the lease costs, the production forecasts, or the oil price? And how large is the worst case you have in mind, in dollars, if all twenty leases are hit by the same bad year at once?

2. What does each party want from this book? The committee that sets the budget, the lender who looks at the tail of the twenty-lease book, the operator who would run the leases, and the regulator or ERCOT, who decide whether a power request is ever built. Where do their wants differ from yours?

3. Where is your emotional investment in this choice? Are any of the twenty leases already held, or any queue deposits already paid, that make you want to keep or drop them? Is there a past position on oil or on power that you defended and would now have to revise? Does "a new business" describe a sector you dislike, or a risk you dislike?

4. Which table or figure did you lean on for "$8.2B at base," and which did you pass over? Did you look at the flat base path only, or also the stress scenarios, including the simultaneous downside? Did you read the mean or the median, the registered cost grid or the committee's own costs? And did you weigh the chance that a request is ever built against the chance that a lease is?

5. Which alternatives did you leave off the table? A mixed book under the same budget and 40% cap, a smaller lease-only book that leaves part of the budget unspent, waiting for better information, or funding nothing? If the leases-only book is the right answer, what would you have to see to change your mind?

## The human's answers

Q1. You say the twenty leases earn $8.2B at base and every one is positive. If that book is wrong, which number carries the loss: the lease costs, the production forecasts, or the oil price? And how large is the worst case you have in mind, in dollars, if all twenty leases are hit by the same bad year at once?
A1. If the leases are wrong the loss is the redevelopment capital, about $1.4B under the registered grid and four times that under the committee's; the worst case I have in mind is five years of $42 oil.

Q2. What does each party want from this book? The committee that sets the budget, the lender who looks at the tail of the twenty-lease book, the operator who would run the leases, and the regulator or ERCOT, who decide whether a power request is ever built. Where do their wants differ from yours?
A2. The committee wants the budget on what already produces; the lender wants a thin tail; the operator wants workovers it knows how to run; the grid operator decides nothing on the lease side, which is part of why I like it.

Q3. Where is your emotional investment in this choice? Are any of the twenty leases already held, or any queue deposits already paid, that make you want to keep or drop them? Is there a past position on oil or on power that you defended and would now have to revise? Does "a new business" describe a sector you dislike, or a risk you dislike?
A3. The company has run offshore oil for thirty years and I have defended the Gulf position in every budget round; the queue deposits already paid are small and I do not count them.

Q4. Which table or figure did you lean on for "$8.2B at base," and which did you pass over? Did you look at the flat base path only, or also the stress scenarios, including the simultaneous downside? Did you read the mean or the median, the registered cost grid or the committee's own costs? And did you weigh the chance that a request is ever built against the chance that a lease is?
A4. I leaned on the flat-path lease NPVs and on every lease being positive at base; I passed over the scenario median, the committee grid's high case and the contracted wind requests that are positive.

Q5. Which alternatives did you leave off the table? A mixed book under the same budget and 40% cap, a smaller lease-only book that leaves part of the budget unspent, waiting for better information, or funding nothing? If the leases-only book is the right answer, what would you have to see to change your mind?
A5. I did not put a mixed book on the table, nor a smaller lease book that leaves room for the four contracted wind requests.

## The motivated-reasoning check

# Motivated-reasoning check

Your factual claims mostly hold. The lease book is 8.19 $B at base, and all twenty leases are positive (lowest is G17001 at 62.2 $M). All twenty requests are negative in the merchant column. Only one request, 23INR0029, has a p_operation_7y above 0.5 (0.56). The problem is how you got to "nothing else", and what you left unchecked.

## 1 and 2. Patterns, and what the tables show

**Working backward from the conclusion.**
- Your sentences: "I want the twenty leases and nothing else." "I do not see why we should learn a new business now." "The grid operator decides nothing on the lease side, which is part of why I like it."
- The reasons are about identity and about who decides, not about numbers.
- The numbers do not refute you, but they do not give the margin you imply.

| Book | Expected NPV (oos) | CVaR95 loss | p_negative | Stage-one charge |
|---|---|---|---|---|
| leases only | 8.66 | -2.28 | 0.00 | 1.35 |
| D risk-aware MILP | 8.48 | -2.36 | 0.00 | 2.27 |
| C deterministic MILP | 8.54 | -2.27 | 0.00 | 2.31 |
| B equal capital | 8.27 | -2.47 | 0.00 | 2.02 |
| A top-N NPV | 8.29 | -2.08 | 0.00 | 2.30 |

- Your book has the highest expected NPV, 0.18 above D.
- On the tail, B (-2.47) and D (-2.36) are better than yours, and C (-2.27) and A (-2.08) are worse.
- So "thin tail" does not separate your book from the mixed ones.
- Your book spends 1.35 of the 2.31 budget. Your own rule says no technology above 40%. The mixed books hold 0.89 to 0.91 in leases, and 1.35 is well above that. The table does not say whether the cap was waived for this book.

**Moving the goalposts.**
- Your sentences: "every one of them is positive" (the test is positive at base, not the book's tail), and in A1 "the worst case I have in mind is five years of $42 oil."
- Q1 asked for a dollar loss if all twenty leases are hit at once. You gave a price path, and a capital figure that is not an NPV loss.
- The nearest table figure is the simultaneous downside: the lease book falls from 8.19 to 7.11. That is still positive, so it helps you. But it uses a cost multiplier of 1.20, which is ASSUMED.
- In A5 you list what you left out but give no result that would change your mind. That makes the position unfalsifiable.

**Double standard and cherry-picking.**
- Your sentence: "I leaned on the flat-path lease NPVs... passed over... the contracted wind requests that are positive."
- You judged leases on the flat path, and requests on merchant NPV and chance of operation.
- Under contract, ten requests are positive. The wind ones are 26INR0113 at 346.0 $M, 27INR0061 at 55.0, 28INR0033 at 53.5 and 30INR0004 at 38.3.
- The wind's weakness is real but you did not cite it. The power-only book has an expected NPV of 0.59, a CVaR95 loss of 0.03 (a loss) and p_negative of 0.58.
- The contracted case is ASSUMED PPA and credits, so that is the weakest label on that side.
- The stresses barely test leases. Weak wind, solar curtailment and two-year delay leave the lease book at 8.19. "Oil collapse" shows 8.21, a gain, and its wti_path cell reads "2,020", which looks like a year label, not a price. We cannot treat that row as an oil test.
- Where oil matters, the breakevens speak. G07963 is 50.3, G17001 is 50.6 and G07962 is 45.1 flat WTI $/bbl, all above your $42. G17565 is 41.4, just under it.

**Treating ASSUMED or FORECAST figures as fact.**
- Your sentence: "the redevelopment capital, about $1.4B under the registered grid and four times that under the committee's."
- The table shows 1.35, and lease costs are ASSUMED (the upstream grid). The tables hold no committee grid, so "four times" cannot be checked here.
- Every lease has data_completeness of 0.80. Every request has 1.00.
- Every lease shows p_operation_7y of 1.00, with no model behind it stated.
- The $8.2B is FORECAST production, ASSUMED costs, DERIVED NPV.
- The tables hold no scenario median either.

**Deposit already paid.** This pattern is not present. "The queue deposits already paid are small and I do not count them" is the right treatment, and the tables hold no deposit figure. The related pattern is commitment: "I have defended the Gulf position in every budget round." You also left unanswered whether any of the twenty leases are already held.

**The rejected book is not clean either.**
- D and C hold gas at 0.62 and 0.70 $B. Their members include 23INR0029 (-246.3 $M) and 25INR0008 (-281.8 $M) in the contracted case.
- That is a fair attack on the mixed books. It is not support for "nothing else".

## 3. Top three risks of your book

1. **Lease costs are ASSUMED and the stress is thin.**
   - All 8.66 and 8.19 rest on that grid. Only the simultaneous downside moves the lease book, by 1.08, and that run uses a 1.20 multiplier.
   - Mitigation: a different grid case. Re-score the book at the committee's costs before committing, and release capital lease by lease behind a later gate.
2. **Oil-price tail, with no real oil test in the tables.**
   - The six leases not in D have the lowest NPVs and the highest breakevens: G07963, G17565, G07962, G21447, G17001 and G07958 (38.4 to 50.6 $/bbl).
   - Mitigation: a smaller position that drops those six, and a flat-price run in place of the "2,020" row.
3. **Concentration and the cap.**
   - Four leases carry 3,711 $M of the 8.19 $B: G14658 at 1,318, G26253 at 845.0, G09982 at 802.5 and G15607 at 745.6. That is about 45%.
   - All twenty share one oil price and one cost grid, so the count of twenty overstates the diversification.
   - The book also exceeds the 40% technology cap as the tables stand.
   - Mitigation: a smaller position inside the cap. A contract (the wind PPA case) is the other lever. It leaves 0.96 of the 2.31 for other uses.

## 4. Verdict

It does not survive as stated: the single change is to re-score the leases-only book at the committee's cost grid inside the 40% cap, and to write down now the result that would make you add the contracted wind.

## The opposing case

## The case for Book D, argued as its advocate

**Strongest point: the book you want breaks the rule you set.** The budget is $2.31B and no technology may exceed 40% of it. The leases-only book puts $1.35B into lease redevelopment. Every scored mixed book stays under the cap: A $0.91B, B $0.87B, C $0.89B, D $0.89B. "The twenty leases and nothing else" is therefore an exception to the cap, not a book under it. Once the cap binds, the rest of the budget goes to something else or stays unspent. Book D puts it into the four contracted wind requests.

**Second point: the tables do not test your worst case.**
- You named five years of low oil and a committee cost grid four times the registered one. The tables hold neither figure. Lease costs are ASSUMED, and the only cost multiplier is 1.20, in the simultaneous downside. There the lease book falls from $8.19B to $7.11B.
- The oil-collapse row shows lease NPV of $8.21B, above the $8.19B base. A collapse that raises value means the stress did not bite, or its path averages above the flat path. The tables do not say which. "Every lease is positive" is therefore a flat-path fact.
- Three leases have breakevens of 50.6 (G17001), 50.3 (G07963) and 45.1 (G07962) flat WTI $/bbl. Your worst-case price is below all three. None of them is in Book D.
- Book D's fourteen leases have a highest breakeven of 39.5 (G20082), below the price you named, on the flat-price basis of that column.
- Lease data completeness is 0.80. For power requests it is 1.00.
- Book D also puts less at risk on the ASSUMED lease cost: $0.89B against $1.35B.

**Third point: the wind leg is positive.** The four contracted wind requests carry contracted NPVs of 346.0, 55.0, 53.5 and 38.3 ($M). Their P(operation) of 0.36, 0.03, 0.04 and 0.03 is already inside those figures, because expected NPVs are timing-weighted. You are right that 19 of the 20 power requests have P(operation) below 0.5. Book D does not buy those 19.

**Your best objection:** "Leases only scores $8.66B expected on $1.35B, against Book D's $8.48B on $2.27B, and its tail is -2.28 against -2.36. The forty-book loses $1.49B on power."
- I concede the numbers. The default forty includes sixteen requests Book D never funds, so the $1.49B loss does not describe D.
- On the 5% tail, D is better by $0.08B and gives up $0.18B of expected NPV. Both books have p_negative of 0.00. B's tail (-2.47) is better than D's.
- The tables do not score a lease book held to the cap, so I cannot say what compliance costs.
- I cannot defend the gas request 23INR0029 from the tables. Its NPV is -246.3 merchant and contracted, with P(operation) of 0.56. The tables do not show what it buys in the tail.

**The assumption D rests on, and where it fails:** the ASSUMED PPA behind the wind leg, which is the weakest label here. Without the contract the four requests are -63.5, -11.5, -10.9 and -7.95. Wind value also sits mostly in one request, 26INR0113 at 346.0. If that PPA is not real, D adds nothing the leases-only book lacks, and its edge is only the cap.

## In my own voice

On the tables the leases-only book is stronger on value, at $8.66B expected on $1.35B against Book D's $8.48B on $2.27B, and Book D wins only if the 40% cap binds on leases or lease costs prove worse than the ASSUMED grid. A signed PPA for 26INR0113, a scored lease book held to the cap, and a rerun at the committee's cost grid with an oil path that actually moves lease NPV would settle it.

CONVERGE: Book D, with gas request 23INR0029 re-scored before any commitment | DISAGREE: whether the 40% cap should bind on leases at all, since the leases-only book scores higher on expected NPV and the tables hold no fourfold-cost test
