# Challenge round — renewables_only

## The human's statement

I want to drop oil and gas and fund the contracted wind and solar requests only. The energy transition will strand the leases within ten years, the PPA makes wind safe, and a book of renewables is what our lenders want to see.

## The advisor's questions

1. Your book is wind and solar requests only, with the leases dropped. Which number in your statement carries the loss if you are wrong: the ten-year stranding of the leases, the PPA price that makes wind "safe", or the chance that a request is ever built? How large is the worst case you have in mind, in dollars, for the whole book?

2. What does each party want from this book? Who sits on the committee that sets the budget, and what do they say about the 40% cap per technology? What does the lender who sees the tail ask to see beyond "renewables"? What does the operator who runs the leases lose or gain if we drop them? What does the grid operator's queue process decide about when, or whether, your wind and solar requests are built?

3. Where is your own stake in this choice? Have we already paid deposits on any of the wind or solar requests, or do we already hold any of the twenty leases? Have you argued for this position before, and would dropping it cost you something? Do you like renewables, or dislike oil and gas, in a way that colors how you read the numbers?

4. Which table or figure did you lean on to say the PPA makes wind safe, and which did you pass over? Did you look at the flat-price path or the stress scenarios? The mean or the median? The registered queue or the committee's own list of requests? The chance that each wind and solar request reaches operation within seven years, or only its value if built?

5. Which alternatives did you leave off the table? You said "only" renewables, so did you test a book that keeps some leases, a smaller book that leaves part of the budget unspent, waiting for the queue to clear, or funding nothing? And how would you fill the whole budget with wind and solar alone, given the 40% cap per technology?

## The human's answers

Q1. Your book is wind and solar requests only, with the leases dropped. Which number in your statement carries the loss if you are wrong: the ten-year stranding of the leases, the PPA price that makes wind "safe", or the chance that a request is ever built? How large is the worst case you have in mind, in dollars, for the whole book?
A1. If the renewables book is wrong the loss is the deposits and study costs on requests that never operate, plus the lease value we gave up; the worst case is a queue in which none of the requests is built.

Q2. What does each party want from this book? Who sits on the committee that sets the budget, and what do they say about the 40% cap per technology? What does the lender who sees the tail ask to see beyond "renewables"? What does the operator who runs the leases lose or gain if we drop them? What does the grid operator's queue process decide about when, or whether, your wind and solar requests are built?
A2. The committee wants a book that holds its value; the lender wants the PPA and a thin tail; the operator has no renewables experience; the grid operator decides whether any request is built at all.

Q3. Where is your own stake in this choice? Have we already paid deposits on any of the wind or solar requests, or do we already hold any of the twenty leases? Have you argued for this position before, and would dropping it cost you something? Do you like renewables, or dislike oil and gas, in a way that colors how you read the numbers?
A3. I want the company to be seen as part of the transition and I have argued that position in public; that is a past position I am defending.

Q4. Which table or figure did you lean on to say the PPA makes wind safe, and which did you pass over? Did you look at the flat-price path or the stress scenarios? The mean or the median? The registered queue or the committee's own list of requests? The chance that each wind and solar request reaches operation within seven years, or only its value if built?
A4. I leaned on the contracted wind NPVs and on the PPA making wind safe; I passed over the chance of operating within seven years, the solar requests that are negative even under contract, and the leases' expected NPV.

Q5. Which alternatives did you leave off the table? You said "only" renewables, so did you test a book that keeps some leases, a smaller book that leaves part of the budget unspent, waiting for the queue to clear, or funding nothing? And how would you fill the whole budget with wind and solar alone, given the 40% cap per technology?
A5. I left off the table a mixed book in which the leases carry the budget and the contracted wind rides alongside, and a smaller renewables position inside book D.

## The motivated-reasoning check

# Motivated-reasoning check: the wind-and-solar-only book

**Proxy.** No table scores a book of wind and solar only. The closest is "power only (D rule)". It holds five wind requests, no solar, and $0.81B of the $2.31B budget. Solar gets $0.00B in all six books. I use that book as your book, and I use leases only (D rule) and book D as the books you rejected.

## Steps 1 and 2: patterns and what the tables show

**1. Working backward from the conclusion, and a criterion that shifts**
- Your sentences: "I want to drop oil and gas and fund the contracted wind and solar requests only." Then, in A3: "I want the company to be seen as part of the transition." In the statement, the lender wants "a book of renewables". In A2, the lender wants "the PPA and a thin tail".
- The answer came first, and the test moved from a label to a tail. On the tail test your book fails.
- Power only: expected NPV $0.59B, CVaR95 loss 0.03 (a loss, not a profit), p_negative 0.58, capital $0.81B.
- Leases only: expected NPV $8.66B, CVaR95 loss -2.28, p_negative 0.00, capital $1.35B.
- Book D: expected NPV $8.48B, CVaR95 loss -2.36, p_negative 0.00, capital $2.27B.
- A thin tail means a profit in the worst 5%. Your book has a 0.58 chance of a loss. The rejected books have 0.00.

**2. Cherry-picking the revenue case**
- Your sentence: "the PPA makes wind safe."
- You used the contracted column. The merchant column is negative for all five wind requests: -63.5, -11.5, -10.9, -5.63 and -7.95.
- Contracted, they are 346.0, 55.0, 53.5, 26.9 and 38.3. One request, 26INR0113, carries 346.0.
- The figure rests on "ASSUMED PPA and credits". That is the weakest label in your case. No stress in the tables tests the PPA.

**3. A double standard: stranding risk for the leases, no queue risk for the requests**
- Your sentences: "The energy transition will strand the leases within ten years." In A4 you passed over the chance of operating within seven years.
- Leases show p_operation_7y of 1.00. The five wind requests show 0.36, 0.03, 0.04, 0.03 and 0.03.
- Stranding is a forecast with no table behind it. The tables hold no stranding case. The nearest tests are:
  - Oil collapse (2020 path): lease NPV $8.21B against $8.19B at base.
  - Simultaneous downside: lease NPV $7.11B.
- Lease breakevens run from 30.6 to 50.6 flat WTI $/bbl.
- This cuts both ways. Lease costs are ASSUMED and production is FORECAST. Stranding past the horizon is untested, so we cannot rule it out. But you applied that doubt to one sector only.

**4. Treating ASSUMED and FORECAST figures as observed, and misreading the table**
- Your sentence in A4: "the solar requests that are negative even under contract."
- The tables say otherwise. Solar contracted NPVs are positive: 50.4, 9.95, 34.4, 8.91 and 6.62. Solar is negative only merchant, from -292.0 to -43.9.
- The requests negative under contract are the gas combined-cycle plants: -246.3, -281.8, -52.2, -44.1 and -32.7.
- So the table was not read closely. Solar's contracted NPVs are small against stage-one charges, for example 50.4 against 758.5 for 24INR0075. Solar still gets $0.00B in every book.

**5. Defending a past position**
- Your sentence: "that is a past position I am defending."
- This is commitment, not evidence. The tables hold no deposits paid and no leases held, and you did not say whether we have either.
- In Q1 you gave no dollar worst case. The tables hold none for "no request is built". The closest figures are the $0.81B stage-one charge, which mixes deposits and construction reserve, and the CVaR95 loss of 0.03.

**6. Alternatives left untested**
- Your sentence in A5: you "left off the table" a mixed book and a smaller renewables position.
- The tables test both.
  - Book D holds $0.76B of wind inside a $2.27B book at expected NPV $8.48B.
  - Leases only does better on expected NPV ($8.66B) with $1.35B of capital.
- Wind and solar alone cannot fill the budget. Two technologies at a 40% cap each reach at most 80% of $2.31B. Your proxy uses $0.81B.

## Step 3: top three risks of your book

1. **The request never reaches operation.**
   - Four of the five wind requests have p_operation_7y of 0.03 or 0.04. The best has 0.36.
   - Mitigation: a later gate. Commit beyond the stage-one charge only after a queue milestone. Full capital runs from 1,348 to 2,770 against stage-one charges of 42.5 to 535.3.
2. **The PPA is an assumption, and without it wind is negative.**
   - Merchant NPVs are all negative. p_negative is 0.58.
   - Mitigation: an executed contract before capital is committed, not an assumed one.
3. **The value is concentrated in one request, and we give up the leases' value.**
   - 26INR0113 carries 346.0 of the contracted wind value. Your book's expected NPV is $0.59B against $8.66B for leases only.
   - Mitigation: a smaller wind position inside a book where the leases carry the budget, as in book D.

## Step 4

Your decision does not survive the check. It would survive only with a tested stranding case that pushes lease value below the wind book's $0.59B, because the worst stress in our tables leaves the lease half of the forty at $7.11B.

## The opposing case

## The case for Book D, argued by its advocate

**Strongest point: the PPA prices the electricity, not the queue.**
You say the PPA makes wind safe. The tables do not show that.

- The chance each wind request operates within seven years is 0.36 for 26INR0113, then 0.03 for 27INR0061, 0.04 for 28INR0033, 0.03 for 28INR0113 and 0.03 for 30INR0004. The grid operator's queue decides those numbers, and no contract changes them.
- The book built on your logic is "power only (D rule)": five wind requests, $0.81B of stage-one charge. Out of sample it earns an expected NPV of $0.59B. Its 5% tail is a loss of $0.03B, and its p_negative is 0.58.
- Book D has an expected NPV of $8.48B. Its 5% tail is a profit of $2.36B (CVaR95 loss -2.36), and its p_negative is 0.00.
- A lender who asks for a thin tail beyond the word "renewables" gets a positive tail loss and a 0.58 chance of a negative result from the renewables book. Book D is the one that shows a tail profit.

**Second point: the leases carry the value.**
Our lease sleeve in D is 14 leases, $0.89B of capital. Every lease has a documented breakeven between $30.6 and $39.5 flat WTI per barrel. G14658 alone has an expected NPV of $1,318M on $96.0M of stage-one charge. The leases-only book earns $8.66B on $1.35B of capital. Dropping the leases gives up that value for $0.59B.

**Third point: your book cannot fill the budget.**
- Wind alone absorbs $0.81B of the $2.31B.
- Solar appears in none of the six scored books ($0.00B in each).
- Forty percent of $2.31B is $0.924B per technology (my arithmetic, not a table figure). Two technologies therefore cap at $1.848B, below the budget.
- You would leave capital unspent or break the cap.

**Your best objection: "the leases strand within ten years."**
I take it seriously, and I answer it with the tables.
- The tables hold no stranding scenario. They hold stresses.
- In the simultaneous downside (WTI path, HH 1.50, wind CF 0.85, solar 0.90, delay 2.00, cost 1.20), the forty-candidate book's lease NPV falls from $8.19B to $7.11B. It stays positive.
- The forty-candidate book's power sleeve is negative in every stress shown. It runs from -1.36 to -1.93 (base -1.49, simultaneous downside -1.92).
- The "oil collapse (2020 path)" row moves the lease book by only +0.02. I do not lean on it. Its wti_path cell reads "2,020", which looks like a label, not a price path.
- The breakevens are the cleaner test. A lease fails at a flat WTI below its breakeven, and D's leases range from $30.6 to $39.5.

**Where I concede.**
- Contracted revenue does turn wind positive. 26INR0113 moves from -63.5 merchant to 346.0 contracted. That is why D holds wind too, at $0.76B.
- Your A4 says solar is negative even under contract. The table shows the opposite: contracted solar NPVs are 50.4, 9.95, 34.4, 8.91 and 6.62, and only the merchant case is negative. Solar is still small against its stage-one charges, and 24INR0075 is 0.45 likely to operate.

**The assumption that carries my case.**
- The weakest label under D is ASSUMED lease costs, on top of FORECAST production and a data_completeness of 0.80.
- The queue chances are FORECAST. The PPA behind your wind is also ASSUMED.
- My case fails if actual lease costs push a lease's breakeven above the WTI we expect. It fails for D's lease sleeve as a whole if the sleeve loses roughly $7.89B (8.48 less 0.59). That is the gap that would put D level with the power-only book.
- The tables do not give a cost-multiplier level at which that happens. The only cost stress shown, 1.20, was combined with other shocks.

## In my own voice

On the tables, Book D is stronger than the renewables-only book: $8.48B against $0.59B expected NPV, and a tail profit of $2.36B against a tail loss of $0.03B. D is not the best lease-heavy book either, since leases only has a higher expected NPV ($8.66B) on less capital, and D's gas leg (23INR0029, -246.3 under both cases) is its weakest member. Evidence that would settle the open point is a lease-stranding scenario run through the same out-of-sample books, plus audited lease costs to replace the ASSUMED grid.

CONVERGE: lease core plus contracted wind, Book D without the 23INR0029 gas member | DISAGREE: whether the leases strand within ten years, which the tables cannot test
