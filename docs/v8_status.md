# v8 deliverables: what is implemented, tested, partial or proposed

Status as of 2026-10-17 (branch `v8-corrections`). *Implemented* means the code exists and runs in the
pipeline; *tested* means `tests/` checks it; *partial* means part of the request is done and the rest is
named; *proposed* means not built.

| # | Deliverable | Status | Where | What is missing |
|---|---|---|---|---|
| 1 | Independent technical audit | Implemented | `docs/audit_2026-10-17.md` | — |
| 2 | Prioritized implementation plan | Implemented | `docs/implementation_plan_v8.md`; decisions #88–#92 | — |
| 3 | Prescriptive pipeline, corrected | Implemented, tested | notebooks 04 (part L), 07–09; `src/decision_date.py`, `src/valuation.py`, `src/decline.py`, `src/optimizer.py` | the narrative cells (titles aside) of notebooks 07–10 still describe v7 and are to be rewritten from their outputs |
| 4 | AI advisor with deterministic model execution | Implemented, tested | `src/advisor_tools.py`, `src/whatif.py`, `prompts/whatif_*.md` | live scoring depends on the `claude` command or an API key on the machine that runs notebook 11 |
| 5 | Scenario and reoptimization interface | Implemented, tested headless | `app/decide.py` (`make decide-page`) | not tried by a committee member; the interactive lab re-solves on 500 scenarios |
| 6 | Reproducible evaluation of decision processes | Implemented | notebook 11 §7; `results/v8/process_comparison.csv`, `value_added.csv` | the "AI-assisted" process has the optimizer's book, so its investment increment is zero by construction; a study with human committees is proposed, not run |
| 7 | Improved figures and tables | Implemented | F38–F44 (notebook 11); F34 and F33 retitled from their results | F37 and the v6 figures of notebook 09 are no longer cited by the report |
| 8 | Revised capstone report | Implemented, tested | `report/report.md` v8: eleven sections, core within 3,500 words, every number in `results/report_numbers.csv` | poster and the Petrobras edition still describe v7 (their number tests read the frozen v7 table) |
| 9 | Executive capital-allocation memorandum | Implemented | the memo at the head of `report/report.md` | — |
| 10 | Reproducibility and limitations statement | Implemented | report section 10 and Appendix C | a clean-environment run of v8 not yet done |

## Tests added for the brief's list

| Requirement | Test |
|---|---|
| Budget and diversification constraints | `test_optimizer.py::test_capped_comparators_stay_within_budget_and_cap_on_random_instances`, `::test_cvar_limit_binds…`, `test_dynamic.py::test_the_revision_respects_the_lease_cap` |
| Cash-flow consistency | `test_valuation.py::test_merchant_npv_matches_the_part_a_dcf…`, `::test_flat_scenario_equals_the_flat_path`, `test_economics.py::test_gas_revenue_converts…` |
| Scenario reproducibility | notebook 11 check "the engine reproduces its own matrix"; `test_scenarios.py` |
| No temporal leakage | `test_decision_date.py::test_censor_at_hides_exits_after_the_date…`, `::test_live_on…`; the gym's `lease_pool_as_of` (notebook 10) |
| Correct CVaR | `test_optimizer.py::test_cvar_averages_exactly_the_worst_five_percent_of_2000`, `::test_cvar_equals_the_ru_objective_at_the_optimum`, `::test_one_cvar_definition_across_modules` |
| Portfolio feasibility | `opt.violations` in notebooks 09 and 11 checks; `test_optimizer.py::test_without_the_cap_top_n_can_breach_it…` |
| Reoptimization behaviour | `test_optimizer.py::test_book_diff…`, `::test_forced_members_are_respected`; `test_whatif.py` |
| Numerical grounding of AI responses | `test_advisor_tools.py::test_numbers_must_come_from_the_result_and_keep_its_unit` |
| Decision logging | `test_ledger.py::test_the_ledger_is_append_only_and_an_edit_breaks_the_chain` |
| Human override authorization | `test_ledger.py::test_an_override_is_written_only_through_the_gate`, `test_decide_app.py` |
