# Challenge round — all_leases

## The human's statement

I want the twenty leases and nothing else. The leases earn $8.2B at base and every one of them is positive; the power requests lose money at 2024 prices and most of them never reach operation. Oil has always paid for this company and I do not see why we should learn a new business now.

## The advisor's questions

1. You say the leases earn $8.2B at base and every one is positive. If the twenty-lease book is wrong, which number in that sentence carries the loss: the production forecast, the oil price, or the lease costs? What is the worst case you have in mind, and how much of the budget would it take with it?

2. The committee that sets the budget, the lender who sees the tail, the operator who runs the leases, and the grid operator who decides whether a request is built each want something different. What do you think each of them wants from this book? Which of them would object to twenty leases and nothing else, and why?

3. You wrote that oil has always paid for this company and that you do not see why you should learn a new business. Is any of that a sunk cost, such as a lease already held, deposits already paid, or a position you have defended before? Or is it a preference for a sector you know? How much of your choice would survive if the company had no history in oil?

4. You leaned on the base case, where the leases are positive, and on the fact that most power requests never reach operation. Did you look at the scenarios or the simultaneous downside for the leases, rather than only the flat 2024 path? Did you check whether the lease costs come from a grid you accepted or from the committee's own grid? And when you say "most never reach operation," are you using the chance that each request is built, or a general impression of the queue?

5. You offered one book, all twenty leases, against one alternative, the power requests. Did you consider a smaller lease book that leaves part of the budget unspent? Did you consider a mixed book that respects the 40% technology cap, or waiting for the lease costs and the queue to become clearer? What about funding nothing this year? Which of these did you rule out, and on what grounds?

## The human's answers

Q1. You say the leases earn $8.2B at base and every one is positive. If the twenty-lease book is wrong, which number in that sentence carries the loss: the production forecast, the oil price, or the lease costs? What is the worst case you have in mind, and how much of the budget would it take with it?
A1. If the leases are wrong the loss is the redevelopment capital, about $1.4B under the registered grid and four times that under the committee's; the worst case I have in mind is five years of $42 oil.

Q2. The committee that sets the budget, the lender who sees the tail, the operator who runs the leases, and the grid operator who decides whether a request is built each want something different. What do you think each of them wants from this book? Which of them would object to twenty leases and nothing else, and why?
A2. The committee wants the budget on what already produces; the lender wants a thin tail; the operator wants workovers it knows how to run; the grid operator decides nothing on the lease side, which is part of why I like it.

Q3. You wrote that oil has always paid for this company and that you do not see why you should learn a new business. Is any of that a sunk cost, such as a lease already held, deposits already paid, or a position you have defended before? Or is it a preference for a sector you know? How much of your choice would survive if the company had no history in oil?
A3. The company has run offshore oil for thirty years and I have defended the Gulf position in every budget round; the queue deposits already paid are small and I do not count them.

Q4. You leaned on the base case, where the leases are positive, and on the fact that most power requests never reach operation. Did you look at the scenarios or the simultaneous downside for the leases, rather than only the flat 2024 path? Did you check whether the lease costs come from a grid you accepted or from the committee's own grid? And when you say "most never reach operation," are you using the chance that each request is built, or a general impression of the queue?
A4. I leaned on the flat-path lease NPVs and on every lease being positive at base; I passed over the scenario median, the committee grid's high case and the contracted wind requests that are positive.

Q5. You offered one book, all twenty leases, against one alternative, the power requests. Did you consider a smaller lease book that leaves part of the budget unspent? Did you consider a mixed book that respects the 40% technology cap, or waiting for the lease costs and the queue to become clearer? What about funding nothing this year? Which of these did you rule out, and on what grounds?
A5. I did not put a mixed book on the table, nor a smaller lease book that leaves room for the four contracted wind requests.

## The motivated-reasoning check

We found one place where the tables back your preference. That is the right starting point for a motivated-reasoning check. On the two numbers that matter most, the leases-only book beats the mixed books:

| Book | Expected NPV (out of sample) | CVaR95 loss | Chance of loss |
|---|---|---|---|
| Leases only (D rule) | 8.66 | -2.28 | 0.00 |
| D risk-aware MILP | 7.67 | -2.20 | 0.00 |
| C deterministic MILP | 7.73 | -2.18 | 0.00 |
| Power only (D rule) | 0.56 | 0.06 | 0.60 |

NPVs and CVaR are in $B. The weak points are in how you got to the conclusion and in what you left out.

## 1 and 2. Patterns and what the tables show

**Working backward from the conclusion.**
- Your sentences: "I want the twenty leases and nothing else." and "I do not see why we should learn a new business now." In A5 you add: "I did not put a mixed book on the table."
- The answer came first and the option set was built around it. You tested no smaller lease book and no wind sleeve.
- The leases-only book uses $1.35B of the $1.91B budget, so $0.56B sits unspent. You never said whether that is intended.

**Moving the goalposts.**
- You framed the problem as one budget with a 40% cap per technology. Your book then ignores the cap.
- 40% of $1.91B is about $0.76B. That is the lease capital in books C and D.
- Leases only carries $1.35B of lease capital, about 71% of the budget. The 8.66 is not a figure you can reach under your own rule.

**Double standard (case and stress).**
- Your sentences: "the power requests lose money at 2024 prices" and, in A4, "I leaned on the flat-path lease NPVs."
- The "lose money" claim uses the merchant case. All twenty requests are negative there, and the power book is -1.09 at base.
- The books are scored in the contracted case. Ten of the twenty requests are positive there. Five are wind, all five positive: 346.0, 55.0, 53.5, 38.3 and 26.9.
- The four-wind book itself is weak: expected NPV 0.56, CVaR95 loss 0.06, chance of a loss 0.60. Your rejection survives that test, but not for the reason you gave.
- You judged leases on the flat path and power on its downside. In the simultaneous downside the leases fall from 8.19 to 7.11, a drop of 1.08. Power falls from -1.09 to -1.42, a drop of 0.33. The leases lose more in dollars.

**Cherry-picking a scenario, stress or grid.**
- You say in A4 that you passed over the scenario median, the committee grid's high case and the contracted wind requests.
- The tables hold no scenario median and no committee grid. We cannot test those, and neither can you.
- The tables do hold five single stresses and one combined stress. You cited none of them.
- The "oil collapse (2020 path)" row shows leases at 8.21 against 8.19 at base, a gain of 0.02. That row does not test your own worst case of five years of $42 oil.

**ASSUMED and FORECAST treated as observed.**
- Your sentences: "every one of them is positive" and "about $1.4B under the registered grid and four times that under the committee's."
- Lease costs are ASSUMED, production is FORECAST, and the NPV is DERIVED. Lease data completeness is 0.80, against 1.00 for every request.
- The tables show $1.35B of lease capital, not $1.4B. They hold no "four times" figure and no committee grid.
- Lease breakevens run from 30.6 to 50.6 flat WTI $/bbl. $42 is your figure and appears in no table. Against it, three leases break even above: G07963 at 50.3, G07962 at 45.1 and G17001 at 50.6.
- "Most never reach operation" is a FORECAST, not an observation. By the queue model, 16 of 20 requests are at 0.11 or lower and the highest is 0.36.
- That chance is already inside the expected NPVs, which are timing-weighted. Citing it again counts it twice.
- Your wind case rests on ASSUMED PPA and credits. The weakest label sits behind both sides, and you applied it to only one.

**Position defended before, and questions dodged.**
- Your sentences: "The company has run offshore oil for thirty years and I have defended the Gulf position in every budget round."
- You handled deposits correctly by not counting them. The tables do not split deposits from the construction reserve, so we cannot size them anyway.
- The weaker point is the defended position and the preference for a sector you know. You gave no answer on how much of the choice survives without that history.
- Q1 asked which number carries the loss: production, price or cost. You answered with the capital.
- Q2 asked who would object to twenty leases and nothing else. You listed what each party wants and named no objector.
- You like that the grid operator "decides nothing on the lease side." The tables show the other side of that. A lease's stage-one charge equals its full capital, so the whole $1.35B is committed at once with no gate. A request such as 26INR0113 shows 535.3 at stage one against 1,503 in full capital.

## 3. Top three risks of your book

1. **ASSUMED lease costs.** All of the 8.19 (base) and 8.66 (out of sample) rests on an ASSUMED cost grid. The combined downside, which includes a 1.20 cost multiplier, takes leases to 7.11. *Mitigation:* re-run the book on the committee's grid and compare it with the registered one before committing.
2. **Single-technology concentration with no gate.** All $1.35B is lease capital, committed in full at stage one. The cap allows about $0.76B. One lease, G14658, carries 1,318 of the 8.19. *Mitigation:* a smaller position at the cap, or a later gate on the largest lease.
3. **Untested oil downside.** The tables have no flat low-oil case. The "oil collapse" row moves leases up 0.02, and the out-of-sample chance of a loss is 0.00 for every lease book. That zero may reflect the scenario set, not safety. Three leases have breakevens of 45.1 to 50.6, with $248M of capital (computed from the three leases' stage-one charges: 80 + 112 + 56). *Mitigation:* run a flat low-oil case at your own $42 and defer those three leases until it is run.

## 4. Verdict

Your preference for leases is supported on expected NPV and tail, but the decision does not survive as stated, because "nothing else" breaks the 40% cap and the case rests on an untested ASSUMED cost grid. The single change that would make it survive is to hold lease capital to the cap of about $0.76B and show, on the committee's grid, that the leases-only edge of 0.99 in expected NPV over book D still holds.

## The opposing case

# The case for Book D

Your opening line describes the full forty-candidate book, but your answers describe twenty leases and nothing else. I argue against the leases-only book.

**1. Your book breaks the cap you named.**
The budget is $1.91B of stage-one charges and no technology may exceed 40% of it, which is about $0.76B. The twenty leases need $1.35B, so your book is $0.59B over. Under the cap, lease capital tops out near $0.76B, and Book D holds exactly that: $0.76B in 14 of your 20 leases. Your A5 says you never put a mixed book or a smaller lease book on the table. Under the cap, the choice is between leaving the rest of the budget unspent and spending it on something else. Book D spends $1.09B on wind, gas and storage.

**2. Your own worst case is not covered by "every lease is positive."**
That statement holds on the flat 2024 path. You named five years of $42 oil. The breakevens, which rest on ASSUMED costs, put three of your twenty leases above $42:
- G07962 at 45.1 flat WTI $/bbl
- G07963 at 50.3
- G17001 at 50.6

A fourth, G17565, sits at 41.4, a margin of 0.6. Book D holds none of these four. Its highest lease breakeven is 39.9 (G21447), a margin of 2.1 under $42.

**3. The wind requests are priced for the objection you raised.**
Expected NPVs are already weighted by the chance of operation. The four contracted wind requests carry 346.0, 55.0, 53.5 and 38.3, which sum to 492.8. Their chances are 0.36, 0.03, 0.04 and 0.03. "Most never reach operation" is true, and it is already inside those figures.

**Your best objections, answered:**

*"The stress table shows leases surviving."*
Leases are 7.11 in the simultaneous downside against 8.19 at base, and still positive. That is true. But the stress table does not test $42. Its WTI column reads 2,020, which names a path and gives no price. The oil-collapse row moves lease NPV by +0.02, so that stress does not test your $42 either. The breakevens are the only price test in the tables, and they fail three leases. The tables also hold no committee grid and no five-year path, so I cannot size the loss in dollars.

*"The tables score leases-only above Book D."*
They do:

| | Leases only | Book D |
|---|---|---|
| Expected NPV, out of sample | 8.66 | 7.67 |
| CVaR95 loss | -2.28 | -2.20 |
| Stage-one charge | 1.35 | 1.85 |

I concede all of that. But that book exceeds the cap by $0.59B, so the $0.99B gap is the price of the cap. It does not show the cap is wrong. I also cannot show that wind hedges oil. The tables hold no correlations, and the held-out oil range is not shown.

**What I will not defend.**
Book D holds three negative-NPV members: gas 26INR0261 at -44.1, gas 27INR0071 at -62.1 and storage 26INR0465 at -12.4, a sum of -118.6. Their case is a portfolio one that these tables do not decompose. Book B also scores a deeper tail than D (-2.26 against -2.20), and Book C scores a higher expected NPV (7.73 against 7.67).

**The assumptions the case rests on, and where it fails.**
The weakest labels are ASSUMED: the lease costs behind the breakevens and the PPA behind the contracted wind NPVs.
- The cap argument fails if the cap is lifted. Leases-only then beats D on both measures above.
- The $42 argument fails if flat WTI stays above 50.6, the highest breakeven, or if lease costs come in below the assumed grid.
- The wind argument fails without the contract. The four requests go from 492.8 contracted to -93.85 merchant (the sum of -63.5, -11.5, -10.9 and -7.95). It also leans on one request: 26INR0113 supplies 346.0 of the 492.8 and takes a stage-one charge of 535.3 at a 0.36 chance of operation.

# In our own voice

On the tables, leases-only is the stronger book on expected NPV, tail and capital, but it exceeds the 40% cap by $0.59B and holds three leases whose breakevens sit above your $42 worst case. A scored, cap-feasible lease book of at most $0.76B, run on a flat $42 path under both cost grids, would settle whether Book D's extra $1.09B earns its place.

CONVERGE: Book D (14 leases, 4 contracted wind, 2 gas CC, 1 storage; $1.85B, expected NPV 7.67, CVaR95 loss -2.20) while the 40% cap stands | DISAGREE: whether the cap should stand, since leases-only scores 8.66 and -2.28 against D's 7.67 and -2.20
