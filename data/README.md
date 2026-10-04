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
