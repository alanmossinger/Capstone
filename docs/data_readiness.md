# Data readiness report (Phase 0 gate)

*Written by `notebooks/01_get_data.ipynb` on 2026-10-03. Every number below was computed by that notebook; thresholds are in `src/config.py`.*

## Sources

- **S1** LBNL Queued Up 2025 project file `lbnl_ix_queue_data_file_thru2024_v2.xlsx`, sheet `03. Complete Queue Data`, 36,441 × 31, SHA-256 `d816467f629a13ef4013dee000129d61f8e4d7fcd8ba514c404a4e140dfec991`. Release check on the LBNL page: unreachable HTTP 403 (bot filter or page change).

- **S2** EIA-860M via EIA API v2, route `electricity/operating-generator-capacity`, period 2026-07: 28,324 generators in 6 pages.

## Checks

| check | pass condition | observed | result |
|---|---|---|---|
| S1 present, SHA-256 recorded, loads | frozen file verified; 36,441 rows × 31 columns | SHA-256 match = True; 36,441 × 31 | PASS |
| S1 counts match the 2026-10-03 audit | status, region, 204 placeholder q_date, 17 negative-MW rows | 18 of 18 items equal | PASS |
| S1 headline: capacity outcome of 2000–2019 requests | ≈13% operational / ≈77% withdrawn (±1 point) | 12.6% / 76.9% | PASS |
| S1 headline: median request-to-operation time | < 2 yr for 2000–07 completions; > 4 yr for 2018–24 | 1.82 yr (n = 240) / 4.14 yr (n = 884) | PASS |
| S1 naive mock-up reproduces | 5-yr completion CAISO 4% / ERCOT 21% / PJM 15% (±1 point) | CAISO 4.2% / ERCOT 21.3% / PJM 15.2% | PASS |
| S1 event-date coverage: operation dates | ≥ 95% of operational rows have on_date in each Track A region | ERCOT 98.4%, PJM 97.8%, CAISO 95.2% | PASS |
| S1 event-date coverage: withdrawal dates | ≥ 83% of withdrawn rows have wd_date in each Track A region | ERCOT 100.0%, PJM 96.9%, CAISO 82.6% | FAIL |
| S1 Track A candidate sample | 13,500–14,500 projects | 13,733 (with a valid request date: 13,438) | PASS |
| S1 enough events for a held-out test | 2017–2019 Track A entrants ≥ 2,500 with ≥ 150 completions by end-2024 | 2,292 projects; 304 completions; 1,358 withdrawals | FAIL |
| S2 API works with the key | metadata returns; latest period ≥ 2026-06; rows = response.total | latest 2026-07; 28,324 rows of 28,324 in 6 pages | PASS |
| S2 fields usable | operating month ≥ 95% of OP rows; state, technology ≥ 99%; county, lat/long ≥ 95% | operating-year-month 100.0%, stateid 100.0%, technology 100.0%, county 100.0%, latitude 100.0%, longitude 100.0% | PASS |
| Crosswalk complete | every EIA technology maps to one type, or to Other with a note | 27 technologies; complete = True | PASS |
| Linkage test | match rate reported; notebook 10 viable if ≥ 40% matched and ≥ 80% of matches agree ±6 months | 31.1% matched, 74.9% agree → notebook 10 not viable, dropped | PASS |
| Licenses documented | data/README.md gives source, terms, how to obtain, what is redistributed for S1 and S2 | all sections present = True | PASS |
| Secrets safe | .env git-ignored; the key appears in no committed file; no key assigned outside .env | .env ignored = True; files containing the key = 0; key assignments = 0 | PASS |

## Event-date coverage by region (%)

| region | n_projects | n_operational | on_date_share | n_withdrawn | wd_date_share | q_date_share |
|---|---|---|---|---|---|---|
| ERCOT | 3282 | 489 | 98.4 | 955 | 100.0 | 91.8 |
| PJM | 8152 | 1195 | 97.8 | 4885 | 96.9 | 99.7 |
| CAISO | 2837 | 228 | 95.2 | 1971 | 82.6 | 99.8 |
| MISO | 4978 | 492 | 1.4 | 2272 | 41.8 | 99.7 |
| SPP | 2469 | 287 | 4.9 | 1531 | 0.0 | 98.7 |
| NYISO | 1817 | 112 | 0.9 | 1303 | 0.0 | 99.9 |
| ISO-NE | 1281 | 219 | 4.1 | 663 | 97.9 | 99.3 |
| West | 7675 | 966 | 21.5 | 4871 | 7.5 | 97.8 |
| Southeast | 3950 | 444 | 57.4 | 2470 | 33.7 | 92.8 |

## Notes for the next notebooks

- Track A candidates: 13,733; with a valid request date 13,438 (notebook 04 needs the request date, so its sample will be the smaller number before cleaning).

- Rows above 5,000 MW: 2 (largest 16,875 MW); missing q_year: 607; duplicate (q_id, entity) rows: 2.

- Linkage: 31.1% of ERCOT/PJM operational projects matched an EIA plant and 74.9% of matches agree on the operation month within six months.

**Outcome (2026-10-03): NO-GO (failed: S1 event-date coverage: withdrawal dates; S1 enough events for a held-out test)**
