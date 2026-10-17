# The registered record as scored on the observed ERCOT prices (v7, frozen 2026-10-17)

These files are the scored criteria C20–C24, the four books, the committee-grid tables, the stresses, the
candidate values, the decision gym and the advisor's scores as they stood at commit `61a8177`, before the
audit of 17 October 2026 (`docs/audit_2026-10-17.md`). They are kept unchanged so the verdicts registered
before any result was seen can be read as they were scored.

The audit found that the code did not do what the registration said in a few places — the top-N and
equal-capital books were not held to the 40% technology cap (A1), CVaR averaged 101 of 2,000 scenarios (A13),
the gate rule's floor was the test cohort's own rate (G2). The main `results/` tables are rerun with those
corrections and labelled *implementation corrections*; the scoring here is never edited. `manifest.json`
holds the hash of every file; `tests/test_registered_frozen.py` fails if one changes.

The earlier scoring on the bridged prices is in `results/registered_bridged/`.
