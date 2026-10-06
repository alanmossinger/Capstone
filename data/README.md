# Data access statement and data dictionary

Everything the project reads or produces lives under `data/`:

| Folder | Contents | In git? |
|---|---|---|
| `data/raw/` | files exactly as downloaded, never edited | no (see terms below) |
| `data/interim/` | tables written by notebooks 02–09 | no (rebuilt by `make all`) |
| `data/processed/` | small final tables (≤ 5 MB) used by figures and the report | yes |

## Sources

### S1 — LBNL "Queued Up: 2025 Edition" project-level file (required)

- **What:** `lbnl_ix_queue_data_file_thru2024_v2.xlsx` (14.1 MB), sheet
  `03. Complete Queue Data`: one row per interconnection request in U.S.
  queues active at any time through the end of 2024 (36,441 rows × 31
  columns). The study population of this project.
- **Publisher:** Lawrence Berkeley National Laboratory, Energy Markets & Policy
  department. Rand, J., Manderlink, N., Zhang, S., Talley, C., Gorman, W.,
  Wiser, R., Seel, J., Mulvaney Kemp, J., Jeong, S., & Kahrl, F. (2025).
  *Queued up: 2025 edition — Characteristics of power plants seeking
  transmission interconnection as of the end of 2024.* Lawrence Berkeley
  National Laboratory. <https://emp.lbl.gov/queues>
- **How to obtain:** download the workbook from <https://emp.lbl.gov/queues>
  and save it as `data/raw/lbnl/lbnl_ix_queue_data_file_thru2024_v2.xlsx`.
  The site blocks scripted downloads, so this is a manual step;
  `src/get_lbnl.py` then verifies the file against the SHA-256 recorded in
  `src/config.py` (`d816467f…dfec991`) and writes `SHA256.txt` next to it.
  The release is frozen for this project (decision #2).
- **Terms:** prepared under U.S. Department of Energy contract
  DE-AC02-05CH11231. The U.S. Government holds a non-exclusive license to
  publish and reproduce the work; it is provided without warranty. No
  redistribution grant is stated, so **the raw file is not committed**.
  Derived tables, results and figures are distributed with citation.
- **Known limits:** the public file has no latitude, longitude, voltage or
  interconnecting entity, although the codebook lists them. Operation and
  withdrawal dates are largely missing outside CAISO, ERCOT and PJM (see the
  dictionary and `docs/data_readiness.md`). LBNL notes that parts of the
  report use non-public data from transmission providers, so some published
  figures cannot be reproduced exactly from the public file.

### S6 — LBNL "Queued Up: 2026 Edition" data file (alongside the frozen 2025 file)

- **What:** `LBNL_Ix_Queue_Data_File_thru2025.xlsx` (15.6 MB), sheet
  `03. Complete Queue Data`: 38,201 rows × 30 columns, interconnection data
  through the end of 2025, last updated May 2026. Used only by notebook 01b
  (reconciliation with the 2025 file; 1- and 2-year outcomes of 2020–2022
  entrants) and notebook 12 (level check). No registered model is fitted or
  scored on it (decision #43).
- **Publisher and citation:** Rand, J., Cheyette, A., Talley, C., Zhang, S.,
  Gorman, W., Wiser, R., Seel, J., Jeong, S., & Kahrl, F. (2026). *Queued up:
  2026 edition — Characteristics of power plants seeking transmission
  interconnection as of the end of 2025.* Lawrence Berkeley National
  Laboratory, with GridTracker. <https://emp.lbl.gov/queues>. The slide
  report `Queued_Up_2026_Edition.pdf` (18.4 MB, June 2026, 71 pages) sits
  beside it for the published benchmark numbers.
- **How to obtain:** both files are linked under "Attachment" on
  <https://emp.lbl.gov/queues>; the page itself sits behind a bot check, the
  file links do not. SHA-256 of both in `data/raw/lbnl/SHA256.txt` and
  `src/config.py`.
- **Terms:** the 2026 data file is licensed **CC BY 4.0** (attribution to
  Lawrence Berkeley National Laboratory and GridTracker), a stated grant the
  2025 page did not carry. It is still kept out of git with the rest of
  `data/raw/`; derived tables are redistributed with that attribution.
- **Layout differences from the 2025 file** (handled by
  `config.LBNL_2026_RENAMES` in notebook 01b): `IA_phase_raw/clean` replace
  `IA_status_raw/clean`; `fips_code` replaces `fips_codes`;
  `type_1..3`/`mw_1..3` replace `type1..3`/`mw1..3`; `county_state_pairs`
  is gone; the date columns are real dates, not Excel serials; `q_status`
  has 10 "unknown" rows. The workbook also carries 18 summary sheets
  (completion rates by region and type, IR→COD by region/type/size, post-IA
  completion) that notebook 01b reads as published benchmarks.

### S2 — EIA-860M through the EIA API v2 (required)

- **What:** route `electricity/operating-generator-capacity`, "Inventory of
  Operable Generators" (Forms EIA-860 and EIA-860M), one row per operable
  generator for the latest month: plant, technology, status, nameplate
  capacity, operating month, county, latitude and longitude, balancing
  authority.
- **How to obtain:** register for a free key at
  <https://www.eia.gov/opendata/register.php> and put it in a file `.env` in
  the repository root as `EIA_API_KEY=<key>` (see `.env.example`). Notebook 01
  calls `src/eia_api.py`, which pages through the API 5,000 rows at a time and
  saves each page as returned (`data/raw/eia860m/api_<period>_page<N>.json`)
  plus the combined table (`eia860m_<period>.parquet`). A second run uses
  these files instead of calling the API again.
- **Terms:** EIA data are U.S. Government works in the public domain; EIA
  asks users to cite it as the source. The key is personal: it lives only in
  `.env`, which git ignores, and it is never printed or written to any other
  file.

### S3 — EIA-860M monthly workbook (fallback only)

The same inventory as a monthly Excel file from
<https://www.eia.gov/electricity/data/eia860m/> (no key needed). Used only if
the API fails; not needed so far.

### S7 — ISO-native queue files (CAISO obtained; PJM and ERCOT pending)

- **What:** `data/raw/iso/caiso_queue_2026-10-06.parquet`, CAISO's public
  queue report as pulled by `gridstatus` 0.36.0 on 2026-10-06 (2,278 rows:
  queue ID, cluster, study-phase statuses, agreement status, queue,
  withdrawal and completion dates). PJM's queue export and ERCOT's GIS
  report could not be fetched from this machine (decision #53); when they
  are placed in `data/raw/iso/`, notebook 13 reads them.
- **How to obtain:** `gridstatus.CAISO().get_interconnection_queue()`
  (source: <http://www.caiso.com/PublishedDocuments/PublicQueueReport.xlsx>);
  PJM: the "Export" of <https://www.pjm.com/planning/service-requests/services-request-status>;
  ERCOT: the monthly "GIS Report" on <https://www.ercot.com/gridinfo/resource>.
- **Terms:** public ISO data; each ISO's terms of use apply; raw files not
  committed.

### S8 — LBNL interconnection cost data, PJM (notebook 15)

- **What:** `data/raw/lbnl_costs/pjm_costs_2022_clean_data.xlsx` (1.8 MB):
  1,127 PJM projects with interconnection cost estimates in $2022/kW by
  study (LBNL, *Interconnection Cost Analysis in the PJM Territory*, 2023).
- **How to obtain:** the "Data File XLSX" link on
  <https://emp.lbl.gov/publications/interconnection-cost-analysis-pjm>;
  SHA-256 in `data/raw/lbnl_costs/SHA256.txt`. Downloaded 2026-10-06 with
  Alan's permission.
- **Terms:** LBNL publication; derived tables only are redistributed.

### S9/S10 — value-layer sources (notebook 15), `data/raw/value/`

- `ice_electric-2017final.xlsx` … `ice_electric-2025final.xlsx`: EIA's
  republication of ICE daily traded electricity prices by hub
  (<https://www.eia.gov/electricity/wholesale/>, public domain).
- `2024-som-pjm-sec5.pdf`: Monitoring Analytics, *2024 State of the Market
  Report for PJM*, Section 5 (Capacity): Table 5-23 (RPM revenue by
  calendar year) and Table 5-13 (ELCC class ratings), parsed by
  `src/value.py` (<https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2024.shtml>).
- `irs_notice_2025-42.pdf`: IRS Notice 2025-42 (begin-construction rules
  for the wind and solar credits), <https://www.irs.gov/pub/irs-drop/n-25-42.pdf>.
- `eia_generation_2024.json`: the EIA API response cached by notebook 15
  (annual net generation by state and fuel, 2024; the key is not in the file).
- SHA-256 of the files in `data/raw/value/SHA256.txt`. All public; not
  committed with the rest of `data/raw/`.

### S11 — U.S. Census Bureau cartographic boundary files (positions for the map)

- **What:** `cb_2020_us_county_20m.zip` and `cb_2020_us_state_20m.zip`,
  the 1:20,000,000 generalised county and state outlines (2020 vintage).
  Notebook 03b places each queue request at the representative point of
  its county (the LBNL file gives a FIPS code for 91% of requests and no
  coordinates) and draws the state outlines behind the map (figure F9).
  The 2020 vintage matches LBNL's county codes, which predate the 2022
  change of Connecticut's counties to planning regions.
- **How to obtain:** `https://www2.census.gov/geo/tiger/GENZ2020/shp/<file>`;
  SHA-256 of both files in `data/raw/geo/SHA256.txt`.
- **Terms:** U.S. Government work, public domain. Not committed, because
  `data/raw/` is not; the files are 0.3 and 0.9 MB.

## What is redistributed

`data/processed/` tables, `results/` and `figures/` are derived from S1 and S2
and are committed. Nothing in `data/raw/` or `data/interim/` is committed.

<!-- dictionary:start -->
## Data dictionary

*This section is written by `notebooks/01_get_data.ipynb`; edit the notebook, not this text.*

### LBNL sheet `03. Complete Queue Data` (36,441 rows × 31 columns)

Codebook fields absent from the public sheet: `interconnecting_entity`, `interconnection_voltage_kv`, `latitude`, `longitude`.

| column | type | filled | meaning (LBNL codebook) |
|---|---|---|---|
| q_id | object | 100% | queue ID number |
| q_status | object | 100% | current queue status (active, withdrawn, suspended, or operational) |
| q_date | Excel serial date | 98% | interconnection request date (date project entered queue) |
| prop_date | Excel serial date | 80% | proposed online date from interconnection application |
| on_date | Excel serial date | 8% | date project became operational (if applicable) |
| wd_date | Excel serial date | 28% | date project withdrawn from queue (if applicable) |
| ia_date | Excel serial date | 7% | date of signed interconnection agreement (if applicable) |
| IA_status_raw | object | 67% | interconnection study phase / status from queue |
| IA_status_clean | object | 85% | standardized interconnection study phase / status |
| county | object | 93% | county where project is located |
| state | object | 100% | state where project is located |
| county_state_pairs | object | 92% | concatenated county and state |
| fips_codes | float64 | 91% | 5-digit FIPS code |
| poi_name | object | 92% | point of interconnection name |
| region | object | 100% | region where project is located (ISO or non-ISO region) |
| project_name | object | 33% | project name |
| utility | object | 83% | utility name |
| entity | object | 100% | transmission provider entity name (ISO or utility) |
| developer | object | 18% | project developer name |
| cluster | object | 26% | queue cluster |
| service | object | 75% | interconnection service type (e.g., ERIS or NRIS, energy or capacity) |
| project_type | object | 92% | type of project or interconnection request (load/transmission/generation) |
| type1 | object | 100% | resource type 1 |
| type2 | object | 12% | resource type 2 |
| type3 | object | 0% | resource type 3 |
| mw1 | float64 | 100% | capacity of type 1 (MW) |
| mw2 | float64 | 3% | capacity of type 2 (MW) |
| mw3 | float64 | 0% | capacity of type 3 (MW) |
| type_clean | object | 100% | resource type - standardized |
| q_year | float64 | 98% | year project entered queue |
| prop_year | float64 | 80% | proposed online year from interconnection application |

### EIA-860M, route `electricity/operating-generator-capacity`, period 2026-07 (28,324 rows)

| column | type | filled | meaning |
|---|---|---|---|
| period | object | 100% | inventory month (YYYY-MM) |
| stateid | object | 100% | state postal code |
| stateName | object | 100% | state name |
| sector | object | 100% | EIA sector code (electric utility, IPP, commercial, industrial …) |
| sectorName | object | 100% | EIA sector name |
| entityid | object | 100% | EIA id of the operating entity |
| entityName | object | 98% | name of the operating entity |
| plantid | object | 100% | EIA plant code |
| plantName | object | 100% | plant name |
| generatorid | object | 100% | generator id within the plant |
| technology | object | 100% | EIA technology description (crosswalked to LBNL type_clean) |
| energy_source_code | object | 100% | primary energy source code |
| energy-source-desc | object | 100% | primary energy source description |
| prime_mover_code | object | 100% | prime mover code (PV, WT, CT, CA, ST, BA …) |
| balancing_authority_code | object | 98% | balancing authority code (e.g. ERCO, PJM, CISO) |
| balancing-authority-name | object | 98% | balancing authority name |
| status | object | 100% | operating status: OP operating, SB standby, OS/OA out of service |
| statusDescription | object | 100% | operating status description |
| nameplate-capacity-mw | float64 | 100% | nameplate capacity (MW) |
| operating-year-month | object | 100% | month the generator entered commercial operation (YYYY-MM) |
| planned-retirement-year-month | object | 2% | planned retirement month, if reported |
| county | object | 100% | county of the plant |
| latitude | float64 | 100% | plant latitude (decimal degrees) |
| longitude | float64 | 100% | plant longitude (decimal degrees) |
| unit | object | 8% | unit code grouping generators of one combined-cycle unit |
| nameplate-capacity-mw-units | object | 100% | units of nameplate capacity (MW) |

### Derived tables

| table | columns | made by |
|---|---|---|
| data/processed/technology_crosswalk.csv | eia_technology, type_clean, note, n_generators, nameplate_gw | notebook 01 §5 |
| data/processed/linkage_test_matches.csv | q_id, entity, region, state, project_name, type1, mw1, on_date, link_type, matched, reason, eia_plantid, eia_plant_name, eia_mw, months_apart | notebook 01 §6 |
<!-- dictionary:end -->

## Model outputs

Written by the modelling notebooks; one section per table, kept by hand.

### `data/processed/predictions_trackA.parquet` (notebook 06)

One row per validation or test request (Track A entrants of 2016–2019) and
horizon (3, 5, 7 years): 2,841 requests × 3 horizons.

| column | meaning |
|---|---|
| project_key | request key: LBNL `entity` and `q_id` joined by a vertical bar (rule R7) |
| region, q_year | region and request year |
| split | `validation` (2016 entrants) or `test` (2017–2019) |
| horizon | years after the request (3, 5 or 7) |
| baseline, baseline_cell | P(operation by horizon) from the region × technology Aalen–Johansen cell of entrants to 2016 (notebook 05); which cell was used |
| cox | P(operation by horizon) from the cause-specific Cox models (notebook 05) |
| dt_logit, dt_lgbm | P(operation by horizon) from the discrete-time multinomial logit and LightGBM hazard models (notebook 06) |
| dt_logit_expected_years, dt_lgbm_expected_years | expected years from request to operation among requests that operate within 10 years |
| event, duration_years | observed outcome through 2024-12-31 (0 still waiting, 1 operation, 2 withdrawal) and years to it — scored only in notebook 08 |
| entry_years, wd_bulk_date | ERCOT delayed-entry time and bulk-withdrawal flag (decision #21), for the sensitivity runs |

### `data/processed/predictions_trackB.parquet` (notebook 07)

One row per resolved Track B request of the 2016 (validation) and 2017 (test)
cohorts, all nine regions: 2,980 rows.

| column | meaning |
|---|---|
| project_key, region, q_year, split | request key, region, request year, `validation` or `test` |
| baseline | share built in the request's region × technology cell of earlier entrants (to 2015 for 2016 requests, to 2016 for 2017 requests) |
| logit, lgbm | raw P(built) from the logistic regression and LightGBM fitted on entrants to 2015 |
| logit_cal, lgbm_cal | the same after isotonic calibration on the 2016 cohort (cross-fitted for 2016 requests; decision #30) |
| built | observed outcome (1 built, 0 withdrawn) — scored only in notebook 08 |
