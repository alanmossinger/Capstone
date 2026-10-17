# Data readiness report (Phase 0 gate)

*Written by `notebooks/01_problem_and_data.ipynb` on 2026-10-17. Every number below was computed by that notebook; thresholds are in `src/config.py`.*

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
| S1 event-date coverage: withdrawal dates | ≥ 82% of withdrawn rows have wd_date in each Track A region | ERCOT 100.0%, PJM 96.9%, CAISO 82.6% | PASS |
| S1 Track A candidate sample | 13,500–14,500 projects | 13,733 (with a valid request date: 13,438) | PASS |
| S1 enough events for a held-out test | 2017–2019 Track A entrants ≥ 2,000 with ≥ 150 completions by end-2024 | 2,292 projects; 304 completions; 1,358 withdrawals | PASS |
| S2 API works with the key | metadata returns; latest period ≥ 2026-06; rows = response.total | latest 2026-07; 28,324 rows of 28,324 in 6 pages | PASS |
| S2 fields usable | operating month ≥ 95% of OP rows; state, technology ≥ 99%; county, lat/long ≥ 95% | operating-year-month 100.0%, stateid 100.0%, technology 100.0%, county 100.0%, latitude 100.0%, longitude 100.0% | PASS |
| Crosswalk complete | every EIA technology maps to one type, or to Other with a note | 27 technologies; complete = True | PASS |
| Linkage test | match rate reported; notebook 10 viable if ≥ 40% matched and ≥ 80% of matches agree ±6 months | 31.1% matched, 74.9% agree → notebook 10 not viable, dropped | PASS |
| Licenses documented | data/README.md gives source, terms, how to obtain, what is redistributed for S1 and S2 | all sections present = True | PASS |
| Secrets safe | .env git-ignored; the key appears in no committed file; no key assigned outside .env | .env ignored = True; files containing the key = 0; key assignments = 0 | PASS |

**Threshold changes.** Two thresholds were amended by Alan after the first evaluation, which had read NO-GO on exactly these two checks (decision #15): withdrawal-date coverage in each Track A region ≥ 83% → ≥ 82%, and the held-out test cohort ≥ 2,500 → ≥ 2,000 projects (≥ 150 completions unchanged).

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

**Outcome (2026-10-17): GO**

## v3 sources — S6, the LBNL 2026 data file (notebook 01, part C)

Written by `notebooks/01_problem_and_data.ipynb`. File `LBNL_Ix_Queue_Data_File_thru2025.xlsx`, SHA-256 `794582d3…a08b6`.

| Check (PLAN.md §5.2) | Value | Result |
|---|---|---|
| S6 loads and is the stated edition | 38,201 rows × 30 columns; sheet and header as in 2025; 9 columns renamed, 10 dropped; SHA-256 verified | PASS |
| ≥ 95% of 2025 requests found in 2026 by (q_id, entity, region) | 96.9% (lowest region PJM 92.9%); 2,759 new rows; 0 duplicate keys | PASS |
| status transitions tabulated | active at end-2024 → active 6,336, withdrawn 2,963, operational 278, suspended 238; withdrawn → operational 63; operational → active 80 | PASS |
| requests whose dates changed listed | q_date: 926 changed, 1 lost; on_date: 123 changed, 107 lost; wd_date: 54 changed, 476 lost; ia_date: 115 changed, 187 lost; ERCOT wd_date == 2018-08-29 (decision #21): 0 changed, 441 lost | PASS |
| 2020–2022 early outcomes available | 3,672 entrants in the three ISOs (2026 edition) | PASS |
| the 2025 file is unchanged | SHA-256 of the frozen file matches src/config.py | PASS |

Event-date coverage by region in both editions: `results/lbnl_2026_date_coverage.csv` (figure 01b_01). The 2025 file stays the basis of every registered result (decisions #43, #48).

## v5 sources — the energy panel (notebook 01, parts D and E)

*Written by `notebooks/01_problem_and_data.ipynb` on 2026-10-17. Every number below was computed by that notebook; thresholds are in `src/config.py` (PLAN.md §14.1).*

| Check | Pass condition | Observed | Result |
|---|---|---|---|
| S13 BSEE files present and hashed | 15 files, SHA-256 in SHA256.txt and the manifest | 15 files, 15 hashes | PASS |
| S13 lease-months cover the window | 2018-01 to 2024-12 | 2010-01 to 2024-12 | PASS |
| S13 candidate pool | >= 20 leases with >= 60 producing months | 1,041 leases | PASS |
| S14 EIA-923 pull complete | rows received = total reported; window covered | 186,744 of 186,744; 2018-01 to 2024-12 | PASS |
| S14 Texas plants per technology | >= 5 plants with >= 36 generating months for each of Gas CC, Solar, Wind, Storage | Gas CC 69, Solar 108, Wind 201, Storage 18 | PASS |
| S15/S16 monthly prices cover the window | WTI, Henry Hub and ERCOT present for every month (ERCOT: observed, derived or labelled assumed) | wti_usd_bbl complete, hh_usd_mmbtu complete, ercot_usd_mwh complete | PASS |
| S16 ERCOT 2024 files verified | five files, SHA-256 as pinned in src/config.py | 5 of 5 | PASS |
| S16 ERCOT hourly prices 2018–2023 on disk and hashed | ercot_dam_spp_<year>.parquet for 2018–2023 from ERCOT's yearly files, SHA-256 as pinned in src/config.py | years on disk: [2018, 2019, 2020, 2021, 2022, 2023, 2024]; verified: 6 of 6; assumed months: 0 | PASS |
| S17 eGRID joins the generation panel | >= 95% of the EIA-923 plants generating in 2023 found in eGRID2023 | 98.8% | PASS |
| S18 CPI-U covers the window | 2016–2024 monthly | 2016-01 to 2024-12, 108 months | PASS |
| Manifest complete | every raw file of S13–S18 hashed with URL, vintage, units, grain | 6 sources, 25 files | PASS |
| Audits R10–R13 | no duplicate keys, no negative volumes, no missing priced month | R10 duplicate (lease, month) keys: 0; R10 duplicate (plant, prime mover, month) keys: 0; R11 lease-months with a negative volume: 0; R11 lease-months with zero oil and gas: 51603; R13 wti_usd_bbl: months missing in 2018-01→2024-12: 0; R13 hh_usd_mmbtu: months missing in 2018-01→2024-12: 0; R13 ercot_usd_mwh: months missing in 2018-01→2024-12: 0; R13 wti_usd_bbl_real2024: months missing in 2018-01→2024-12: 0; R13 hh_usd_mmbtu_real2024: months missing in 2018-01→2024-12: 0; R13 ercot_usd_mwh_real2024: months missing in 2018-01→2024-12: 0 | PASS |
| Secrets safe | no API key in any saved page | 38 EIA-923 pages checked | PASS |

Non-blocking lines are reported for the record; with the 2018–2023 hourly files on disk (decision #78) no ERCOT month is assumed, and without them the bridge of decision #64 fills 2020–2023.

**Outcome (2026-10-17): GO**
