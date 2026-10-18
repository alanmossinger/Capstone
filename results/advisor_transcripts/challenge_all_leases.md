# Challenge round — all_leases

## The human's statement

I want the twenty leases and nothing else. The leases earn $8.2B at base and every one of them is positive; the power requests lose money at 2024 prices and most of them never reach operation. Oil has always paid for this company and I do not see why we should learn a new business now.

## The advisor's questions

1. You wrote that the leases earn $8.2B at base and that every one is positive. Which number in that statement carries the loss if the book is wrong: the oil price path, the production forecast, or the capital cost grid for the twenty leases? And how large a shortfall in the $8.2B do you have in mind as your worst case, and at what point would it hurt the company?

2. What does each party want from this book? Specifically, what does the committee that sets the budget want from a $1.79B book with a 40% cap per technology, what does the lender who sees the tail want, what does the operator who runs the twenty leases want, and what would the regulator or grid operator need to see before any ERCOT request is built?

3. Where is your emotional investment in an all-lease book? Are there deposits already paid or leases already held that you would find hard to walk away from, a past position on oil that you have defended, or a dislike of the power business that shapes how you read the requests?

4. You leaned on the base figure of $8.2B for the leases and on the losses of the power requests at 2024 prices. Which tables did you pass over: the stress scenarios, especially the oil collapse and the simultaneous downside, the mean versus the median, or the chance that each request is ever built? And did you take the lease cost grid as given, or did you ask who set it and whether the committee would use the same one?

5. Which alternatives did you leave off the table? You compared the twenty leases with the twenty power requests, but what about a smaller lease book, a book with a few power requests added for diversification, waiting for the queue or the oil price to clarify, or funding nothing this year?

## The human's answers

Q1. You wrote that the leases earn $8.2B at base and that every one is positive. Which number in that statement carries the loss if the book is wrong: the oil price path, the production forecast, or the capital cost grid for the twenty leases? And how large a shortfall in the $8.2B do you have in mind as your worst case, and at what point would it hurt the company?
A1. If the leases are wrong the loss is the redevelopment capital, about $1.4B under the registered grid and four times that under the committee's; the worst case I have in mind is five years of $42 oil.

Q2. What does each party want from this book? Specifically, what does the committee that sets the budget want from a $1.79B book with a 40% cap per technology, what does the lender who sees the tail want, what does the operator who runs the twenty leases want, and what would the regulator or grid operator need to see before any ERCOT request is built?
A2. The committee wants the budget on what already produces; the lender wants a thin tail; the operator wants workovers it knows how to run; the grid operator decides nothing on the lease side, which is part of why I like it.

Q3. Where is your emotional investment in an all-lease book? Are there deposits already paid or leases already held that you would find hard to walk away from, a past position on oil that you have defended, or a dislike of the power business that shapes how you read the requests?
A3. The company has run offshore oil for thirty years and I have defended the Gulf position in every budget round; the queue deposits already paid are small and I do not count them.

Q4. You leaned on the base figure of $8.2B for the leases and on the losses of the power requests at 2024 prices. Which tables did you pass over: the stress scenarios, especially the oil collapse and the simultaneous downside, the mean versus the median, or the chance that each request is ever built? And did you take the lease cost grid as given, or did you ask who set it and whether the committee would use the same one?
A4. I leaned on the flat-path lease NPVs and on every lease being positive at base; I passed over the scenario median, the committee grid's high case and the contracted wind requests that are positive.

Q5. Which alternatives did you leave off the table? You compared the twenty leases with the twenty power requests, but what about a smaller lease book, a book with a few power requests added for diversification, waiting for the queue or the oil price to clarify, or funding nothing this year?
A5. I did not put a mixed book on the table, nor a smaller lease book that leaves room for the four contracted wind requests.

## The motivated-reasoning check

# Motivated-reasoning check on the all-lease book

Provenance first. The lease case rests on ASSUMED costs, with FORECAST production and DERIVED NPV. The weakest label is ASSUMED. The power case rests on ASSUMED PPA and credits and FORECAST timing.

## 1 and 2. Patterns, and what the tables show

**Working backward from the conclusion**
- Your sentences: "I want the twenty leases and nothing else." "Oil has always paid for this company and I do not see why we should learn a new business now." "The grid operator decides nothing on the lease side, which is part of why I like it."
- The conclusion comes first, and the reasons are habit and comfort. None cites a table.
- The tables do favour your book on the measures they score. Leases only: expected NPV 8.71, CVaR95 loss -2.28, p_negative 0.00. Our nearest rival, book D: 7.59, -2.22, 0.00.
- You may be right, but not for the reasons you gave.

**Moving the goalposts**
- You set the problem as $1.79B with a 40% cap per technology. Your book holds 1.37 in leases. Books A to D hold 0.69 to 0.70.
- Your book sits outside your own cap. It also beats A to D partly because they were constrained and it was not.
- In Q1 we asked for a shortfall in the $8.2B. You answered with capital at risk and a $42 oil path, which is a different measure.

**Double standard**
- You judge the leases on the flat base ("every one of them is positive") and the requests on the merchant case and on "most of them never reach operation."
- The request NPVs are already weighted by P(operation), which runs from 0.01 to 0.32. The low chance is already inside the -1.24. You count it twice.
- The leases carry p_operation_7y of 1.00. The tables do not say how that was reached. The queue models cover the requests only.
- Data completeness is 0.80 for leases and 1.00 for requests. Your case rests on the thinner data.

**Cherry-picking a case, a stress and a grid**
- You admit it in A4: you passed over "the committee grid's high case and the contracted wind requests that are positive."
- Contracted case: six requests are positive, not four wind. One is solar (24INR0075, 25.8). Five are wind. The largest is 26INR0113: 208.0 contracted against -106.6 merchant.
- That does not rescue power. The power-only book scores expected NPV 0.39, CVaR95 loss 0.08 and p_negative 0.68. That supports your caution.
- Stresses: the leases fall from 8.23 to 7.15 in the simultaneous downside, and the whole book from 6.99 to 5.42. The leases stay positive under every stress listed.
- The oil collapse shows leases at 8.25, above base. That stress does not test oil risk, and the tables do not explain it. It sits oddly with flat-WTI breakevens of 31.0 to 53.2.
- The tables hold no median, so I cannot test your skipped "scenario median."
- The tables hold no committee grid. The only cost stress is the 1.20 multiplier inside the simultaneous downside.

**Treating ASSUMED as observed**
- "Every one of them is positive" is DERIVED from ASSUMED costs.
- Your "about $1.4B" matches the 1.37 in the tables, but it is an ASSUMED figure.
- Your "four times that under the committee's" appears nowhere in the tables. No NPV result covers it, so "every one is positive" is untested on that grid.
- The contracted wind gains also rest on an ASSUMED PPA, so this cuts both ways.

**Commitment to a past position**
- "I have defended the Gulf position in every budget round."
- On deposits you said you do not count them, and the tables hold no deposit figure, so I cannot check "small." I do not find the deposit pattern in your text. The defended-position pattern is there.

**Alternatives left off**
- Mixed books B, C and D score 7.58 / -1.90, 7.71 / -2.03 and 7.59 / -2.22. All sit below leases only on both expected NPV and tail. The tables show no tail gain from adding power.
- A smaller lease book, waiting, and funding nothing have no scored row in the tables.

**Data flag**
- The capex column in the book table (A 4.33, B 10.1, C 5.41, D 15.3, power only 9.63) conflicts with the technology table (1.78, 1.58, 1.79, 1.67, 0.66). Both sit against a $1.79B budget.
- The tables do not reconcile the two columns. I did not rely on the first one.

## 3. Top three risks of the all-lease book

1. **The ASSUMED cost grid.**
   - Every lease NPV rests on it, and the committee's high case is untested.
   - Mitigation: add a different grid case, the committee's high case, to the scoring before capital is released.

2. **Oil below breakeven on the weaker leases.**
   - Seven leases sit outside book D, with breakevens of 39.9 to 53.2 $/bbl flat WTI. Book D's thirteen leases run 31.0 to 35.4.
   - Three exceed your $42: G15607 at 46.2, G07962 at 48.0 and G17001 at 53.2. G17565 at 41.4 and G15610 at 41.7 sit within a dollar of it.
   - Mitigation: a later gate for those seven until the oil path clarifies.

3. **Concentration in one technology and one asset.**
   - Your book puts 1.37 in a single technology against 0.69 to 0.70 in A to D.
   - LEASE|G14658 alone carries 1,348 of the 8.23B, and the next largest is 862.1.
   - Mitigation: a smaller position, with lease capital held to the 0.69 to 0.70 that the cap allows.

## 4. Verdict

The decision does not survive as argued. The tables back the leases (8.71, -2.28, 0.00), but your book breaks your own cap and rests on an untested ASSUMED grid. The one change that would make it survive is to score the leases-only book on the committee's high-case grid under the same 40% cap as books A to D and show it still beats them.

## The opposing case

# The case for Book D, argued as its advocate

I am arguing for Book D: 13 leases, five wind requests, two gas combined cycle requests and one storage request. That is 21 members inside the $1.79B budget and the 40% cap per technology.

**1. The all-lease book is not the committee's book.**
You describe your book as one budget with a 40% cap per technology. But "the twenty leases and nothing else" puts $1.37B into one technology. Every cap-compliant book in the tables holds $0.69B or $0.70B of leases. Leases only is a different problem from the one the committee set. If the cap is waived, we should say so openly. I will not claim the table scores favor D here, and I address that below.

**2. Your worst case is not in the tables.**
Lease costs are ASSUMED. You put the committee's grid at four times the registered one, and your worst case is five years of $42 oil. The tables hold neither figure.
- The only cost stress is a 1.20 multiplier, inside the simultaneous downside. There the lease book falls from 8.23 to 7.15 ($B).
- The oil collapse row shows leases at 8.25, up from 8.23. It therefore cannot test an oil loss.
- "Every lease is positive" rests on one assumed cost grid and one flat price path.
- Four times $1.37B is well above the $1.79B budget. Lease exposure scales with lease capital, and D carries $0.69B against $1.37B.

**3. The leases we drop are the ones that fail first.**
D's 13 leases all have breakevens of 35.4 flat WTI $/bbl or lower. The seven it leaves out sit higher:

| Lease | Breakeven, flat WTI $/bbl |
|---|---|
| G07963 | 39.9 |
| G21447 | 39.9 |
| G17565 | 41.4 |
| G15610 | 41.7 |
| G15607 | 46.2 |
| G07962 | 48.0 |
| G17001 | 53.2 |

Against your $42 case, three of these (46.2, 48.0, 53.2) are above it. Two more (41.7, 41.4) have almost no room. The tables give flat-price breakevens, not a five-year path, so this is an indicator and not a test.

**4. The wind requests.**
There are five contracted wind requests with positive NPV, not four: 26INR0113 at 208.0, 27INR0061 at 46.2, 28INR0033 at 30.4, 28INR0113 at 18.7 and 30INR0004 at 31.9 ($M). Together they add to 335.2 ($M). That is small beside the leases, and it is not why I hold D. Merchant, all five are negative.

**Your best objection:** "D gives up expected NPV and does no better in the tail."
That is true on the tables. Leases only scores 8.71 expected against D's 7.59, a gap of 1.12 ($B). The tail is -2.28 against -2.22, and both have p_negative of 0.00. I do not claim D wins out of sample. My claim is narrower. Both rows use the same ASSUMED cost grid, so the 1.12 gap exists only inside that grid. The tables cannot say what the committee's grid does to it. D buys a smaller lease sleeve ($0.69B against $1.37B), a cap-compliant book, and no dependence on the seven highest-breakeven leases. It pays 1.12 ($B) of expected NPV for that.

**The assumption D rests on.**
The weakest labels are ASSUMED (lease costs, PPA and credits) and FORECAST (p_operation_7y). D's budget fit depends on the queue forecast. The books table puts D's capex at 15.3 ($B), while the technology table shows 1.67. The five wind requests alone add to 9.63 in the books table (power only), against 0.66 in the technology table. I read the gap as the p_operation weighting, but the tables do not say so. The wind probabilities are 0.26 for 26INR0113 and 0.03 to 0.04 for the other four. If more of them are built than forecast, D breaks the $1.79B budget. The power-only book also has p_negative of 0.68. The tables give no correlation, and in the simultaneous downside power falls from -1.24 to -1.72, so I cannot call it a hedge.

# In my own voice

On the tables, leases only is stronger: 8.71 against 7.59 expected, -2.28 against -2.22 at the 5% tail, and p_negative of 0.00 for both. D's case rests on the 40% cap and on lease costs the tables cannot stress. A re-run of the twenty leases under the committee's cost grid and a five-year $42 path would settle it. So would a cap-compliant lease book scored on the same held-out scenarios.

CONVERGE: the twenty leases, leases only at $1.37B, expected NPV 8.71, 5% tail -2.28, resting on ASSUMED lease costs | DISAGREE: whether the committee waives the 40% cap, and whether the leases still lead under its cost grid and a $42 oil path, neither of which the tables hold
