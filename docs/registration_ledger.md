# Registration ledger

Every registered line with its verdict as first scored, each correction made afterwards with its date, and its status now. A registered verdict is never re-scored: a correction adds a row and the original stands. 78 lines; 17 with a correction; 3 correction rows whose verdict differs from the registered one. Built by `src/registration_ledger.py` from the scored files in `results/`.

| criterion | line | registered_on | registered_verdict | correction | correction_date | verdict_after | status |
|---|---|---|---|---|---|---|---|
| C1 | uno_c at 3 years, track A, dt_lgbm | 2026-10-04 | PASS |  |  |  | as registered |
| C1 | uno_c at 5 years, track A, dt_lgbm | 2026-10-04 | PASS |  |  |  | as registered |
| C1 | uno_c at 7 years, track A, dt_lgbm | 2026-10-04 | FAIL |  |  |  | as registered |
| C2 | brier at 3 years, track A, dt_lgbm | 2026-10-04 | PASS |  |  |  | as registered |
| C2 | brier at 5 years, track A, dt_lgbm | 2026-10-04 | PASS |  |  |  | as registered |
| C2 | brier at 7 years, track A, dt_lgbm | 2026-10-04 | FAIL |  |  |  | as registered |
| C3 | slope at 3 years, track A, dt_lgbm | 2026-10-04 | FAIL |  |  |  | as registered |
| C3 | slope at 5 years, track A, dt_lgbm | 2026-10-04 | FAIL |  |  |  | as registered |
| C3 | slope at 7 years, track A, dt_lgbm | 2026-10-04 | PASS |  |  |  | as registered |
| C4 | lift_10 at 5 years, track A, dt_lgbm | 2026-10-04 | PASS |  |  |  | as registered |
| C5 | auc, track B, lgbm_cal | 2026-10-04 | PASS |  |  |  | as registered |
| C5 | brier, track B, lgbm_cal | 2026-10-04 | PASS |  |  |  | as registered |
| C6 | ≥ 20 MW: v2 vs fair baseline, brier at 3 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C6 | ≥ 20 MW: v2 vs fair baseline, brier at 5 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C6 | ≥ 20 MW: v2 vs fair baseline, uno_c at 3 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C6 | ≥ 20 MW: v2 vs fair baseline, uno_c at 5 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C7 | 2018–2019 ≥ 20 MW, level repaired: slope and intercept at 3 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C7 | 2018–2019 ≥ 20 MW, level repaired: slope and intercept at 5 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C8 | landmark +24 months: both updated vs entry model, Uno's C 3 years after | 2026-10-06 | PASS |  |  |  | as registered |
| C8 | landmark agreement executed: both updated vs entry model, Uno's C 3 years after | 2026-10-06 | FAIL |  |  |  | as registered |
| C9 | backtest: model book vs fair-baseline book, realised MW online within 5 years | 2026-10-06 | FAIL |  |  |  | as registered |
| C10 | backtest: model book vs fair-baseline book, realised value, base case | 2026-10-06 | FAIL |  |  |  | as registered |
| C11 | simulated 5–95% band covers the realised MW of the model's book | 2026-10-06 | PASS |  |  |  | as registered |
| C12 | leakage guard: dated features (test) and landmark AUC below the ablation's | 2026-10-06 | PASS |  |  |  | as registered |
| C13 | MISO: LightGBM vs fair baseline, brier at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C13 | MISO: LightGBM vs fair baseline, brier at 5 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C13 | MISO: LightGBM vs fair baseline, uno_c at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C13 | MISO: LightGBM vs fair baseline, uno_c at 5 years | 2026-10-08 | PASS |  |  |  | as registered |
| C13 | SPP: LightGBM vs fair baseline, brier at 3 years | 2026-10-08 | PASS |  |  |  | as registered |
| C13 | SPP: LightGBM vs fair baseline, brier at 5 years | 2026-10-08 | PASS |  |  |  | as registered |
| C13 | SPP: LightGBM vs fair baseline, uno_c at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C13 | SPP: LightGBM vs fair baseline, uno_c at 5 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C14 | MISO: LightGBM calibration slope at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C14 | MISO: LightGBM calibration slope at 5 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C14 | SPP: LightGBM calibration slope at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C14 | SPP: LightGBM calibration slope at 5 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C15 | +2 landmark, ≥ 20 MW, book of 25: operations realised within 3 years, M vs E | 2026-10-08 | PASS |  |  |  | as registered |
| C15 | +2 landmark, ≥ 20 MW, book of 25: operations realised within 3 years, M vs LA | 2026-10-08 | PASS |  |  |  | as registered |
| C15 | +2 landmark, ≥ 20 MW, book of 50: operations realised within 3 years, M vs E | 2026-10-08 | PASS |  |  |  | as registered |
| C15 | +2 landmark, ≥ 20 MW, book of 50: operations realised within 3 years, M vs LA | 2026-10-08 | PASS |  |  |  | as registered |
| C16 | +2 landmark, ≥ 20 MW, book of 25: MW realised within 3 years, M vs E | 2026-10-08 | FAIL |  |  |  | as registered |
| C16 | +2 landmark, ≥ 20 MW, book of 25: MW realised within 3 years, M vs LA | 2026-10-08 | FAIL |  |  |  | as registered |
| C16 | +2 landmark, ≥ 20 MW, book of 50: MW realised within 3 years, M vs E | 2026-10-08 | FAIL |  |  |  | as registered |
| C16 | +2 landmark, ≥ 20 MW, book of 50: MW realised within 3 years, M vs LA | 2026-10-08 | FAIL |  |  |  | as registered |
| C17 | +2 landmark, all sizes: M after the level repair, calibration intercept at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C17 | +2 landmark, ≥ 20 MW: M after the level repair, calibration intercept at 3 years | 2026-10-08 | FAIL |  |  |  | as registered |
| C18 | ≥ 20 MW, 3 years: Brier score, T* vs dt_lgbm | 2026-10-12 | PASS |  |  |  | as registered |
| C18 | ≥ 20 MW, 3 years: Uno's C, T* vs dt_lgbm | 2026-10-12 | PASS |  |  |  | as registered |
| C18 | ≥ 20 MW, 5 years: Brier score, T* vs dt_lgbm | 2026-10-12 | PASS |  |  |  | as registered |
| C18 | ≥ 20 MW, 5 years: Uno's C, T* vs dt_lgbm | 2026-10-12 | FAIL |  |  |  | as registered |
| C19 | ≥ 20 MW, 3 years: Brier score, T* vs fair_baseline | 2026-10-12 | PASS |  |  |  | as registered |
| C19 | ≥ 20 MW, 3 years: Uno's C, T* vs fair_baseline | 2026-10-12 | FAIL |  |  |  | as registered |
| C19 | ≥ 20 MW, 5 years: Brier score, T* vs fair_baseline | 2026-10-12 | PASS |  |  |  | as registered |
| C19 | ≥ 20 MW, 5 years: Uno's C, T* vs fair_baseline | 2026-10-12 | FAIL |  |  |  | as registered |
| C20 | ERCOT log price +1 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | Gas CC CF +1 m | 2026-10-12 | PASS | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | PASS | as registered: the observed-price scoring is the registered verdict |
| C20 | Henry Hub log price +1 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | Solar CF +1 m | 2026-10-12 | PASS | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | PASS | as registered: the observed-price scoring is the registered verdict |
| C20 | WTI log price +1 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | Wind CF +1 m | 2026-10-12 | PASS | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | PASS | as registered: the observed-price scoring is the registered verdict |
| C20 | lease gas +12 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | lease gas +3 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | lease gas +6 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | lease oil +12 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | lease oil +3 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C20 | lease oil +6 m | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C21 | D vs A, out-of-sample metric | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C21 | D vs A, out-of-sample metric | 2026-10-12 | FAIL | applied to the corrected system (comparators under the cap, the 2025 candidates as seen that day, the decline floor, the two-stage budget, inputs public on the decision date) as a post-registration result | 2026-10-20 | PASS | post-registration result on the corrected system: PASS; the registered verdict stands |
| C22 | D vs B, out-of-sample metric | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | FAIL | as registered: the observed-price scoring is the registered verdict |
| C22 | D vs B, out-of-sample metric | 2026-10-12 | FAIL | applied to the corrected system (comparators under the cap, the 2025 candidates as seen that day, the decline floor, the two-stage budget, inputs public on the decision date) as a post-registration result | 2026-10-20 | FAIL | post-registration result on the corrected system: FAIL; the registered verdict stands |
| C23 | stability under stresses, mean Jaccard D vs C | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | PASS | as registered: the observed-price scoring is the registered verdict |
| C23 | stability under stresses, mean Jaccard D vs C | 2026-10-12 | FAIL | applied to the corrected system (comparators under the cap, the 2025 candidates as seen that day, the decline floor, the two-stage budget, inputs public on the decision date) as a post-registration result | 2026-10-20 | FAIL | post-registration result on the corrected system: FAIL; the registered verdict stands |
| C24 | CVaR95 loss, power only (D rule) minus D, joint scenarios | 2026-10-12 | FAIL | rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it | 2026-10-14 | PASS | as registered: the observed-price scoring is the registered verdict |
| C24 | CVaR95 loss, power only (D rule) minus D, joint scenarios | 2026-10-12 | FAIL | applied to the corrected system (comparators under the cap, the 2025 candidates as seen that day, the decline floor, the two-stage budget, inputs public on the decision date) as a post-registration result | 2026-10-20 | FAIL | post-registration result on the corrected system: FAIL; the registered verdict stands |
| C25 | the challenger names the keyed flaw in the 12 reasoning-flaw cases (sunk cost, double standard, unsupported claim) | 2026-10-20 | PASS |  |  |  | as registered |
| C26 | the challenger names the keyed flaw in the 24 computable-flaw cases (cap, liquidity, chance of loss, tail, exclusion, fragile position) | 2026-10-20 | PASS |  |  |  | as registered |
| C27 | the challenger does not challenge the 12 clean cases on grounds they do not have | 2026-10-20 | FAIL |  |  |  | as registered |
| C28 | the memos cite only computed numbers and real facts | 2026-10-20 | FAIL |  |  |  | as registered |
| C29 | following the challenger improves the committee's own objective over its proposal | 2026-10-20 | PASS |  |  |  | as registered |
| C30 | following the challenger avoids loss | 2026-10-20 | PASS |  |  |  | as registered |
| C31 | the language model adds decision value beyond its tools | 2026-10-20 | PASS | two checks reported and not registered: the edge without its largest case, and against a fixed rule that takes the optimizer's book first | 2026-10-20 | PASS | as registered (PASS); without the largest case +$19M, against the optimizer-first rule +$1M, reported beside it |
| C32 | the challenger reads the committee's rules from words | 2026-10-20 | PASS |  |  |  | as registered |
