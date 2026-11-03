"""Project constants: data files, cohort cuts, horizons, thresholds and colors.

What: every number or name that more than one notebook relies on.
Why: a constant changed here changes everywhere, and each one carries a
comment saying where it comes from.
Reads / writes: nothing.
Used by: all notebooks (setup cell) and every ``src`` module.
"""

import numpy as np

# --- LBNL "Queued Up: 2025 Edition" project-level file (source S1) ----------
LBNL_PAGE_URL = "https://emp.lbl.gov/queues"  # landing page that links the file
LBNL_FILENAME = "lbnl_ix_queue_data_file_thru2024_v2.xlsx"  # frozen release (decision #2)
LBNL_SHA256 = "d816467f629a13ef4013dee000129d61f8e4d7fcd8ba514c404a4e140dfec991"  # hash of the copy first used on 2026-10-03
LBNL_SHEET = "03. Complete Queue Data"  # project-level sheet; other sheets are LBNL's own summaries
LBNL_HEADER_ROW = 1  # row 0 is a title banner

# --- LBNL "Queued Up: 2026 Edition" data file (source S6; alongside, decision #43) ---
LBNL_2024_FILENAME = "queues_2023_clean_data_r1.xlsx"  # the 2024 edition, data through 2023: revision r1, last modified 23 August 2024, the latest LBNL record public on 1 January 2025 (decision #101)
LBNL_2024_URL = "https://eta-publications.lbl.gov/sites/default/files/queues_2023_clean_data_r1.xlsx"  # the "Data File (XLSX)" of the 2024 edition's publication page
LBNL_2024_SHA256 = "832f21cf62a3c333b1834455deecbcbc99b80cb65e43855b7a48355fec838a39"  # hash of the copy downloaded 2026-10-22
ERCOT_GIS_2024_FILES = {  # ERCOT's monthly GIS reports of April-November 2024 (report type 15933, fetched on a U.S. runner 2026-10-22), the record of who was still in the queue on the decision date (decision #101)
    "RPT.00015933.0000000000000000.20240501.161916854.GIS_Report_April_2024.xlsx": "439911ea4f399fb05b22b20a10b5710eb732bdcefed85662ce302c35c11bc721",
    "RPT.00015933.0000000000000000.20240603.133844667.GIS_Report_May_2024.xlsx": "5d4f9681ac1c6329ba98926848a67eb400bdc4fa5fcb47a944216d42cfbe478d",
    "RPT.00015933.0000000000000000.20240701.152910365.GIS_Report_June_2024.xlsx": "8496f89956dad072d05b0aae11979c04091104299bbb08935e6b71a8266e62a0",
    "RPT.00015933.0000000000000000.20240801.160316902.GIS_Report_July_2024.xlsx": "5325eab4ee9ed4ca0b95729ab7dd9fd0f85334c981efd03368b51651ec147de2",
    "RPT.00015933.0000000000000000.20240903.150331562.GIS_Report_August_2024.xlsx": "d9a4de1de7a42139b94ce272aa0f270f4fef56c7406c5e9e0fb8399b0e6c471c",
    "RPT.00015933.0000000000000000.20241001.153955135.GIS_Report_September2024.xlsx": "cdcaf925b7cbce41c1e31ba2d08e1836e37f25e68466f4e037791e77d7287c4f",
    "RPT.00015933.0000000000000000.20241101.143132516.GIS_Report_October2024.xlsx": "c197c0f10c117d767f1324f4e221b672f99b51a2ff2f4115427d6517810ea085",
    "RPT.00015933.0000000000000000.20241202.111814411.GIS_Report_November2024.xlsx": "a5865940631872acd0ae9e037b2392f48501ab131ca75c22e32b0f76ca25699b",
}
LBNL_2026_FILENAME = "LBNL_Ix_Queue_Data_File_thru2025.xlsx"  # data through 2025; updated May 2026
LBNL_2026_SHA256 = "794582d3281c6a305e9615fcfec3fae9dc85be2165216d33760b677e976a08b6"  # hash of the copy downloaded 2026-10-06
LBNL_2026_REPORT = "Queued_Up_2026_Edition.pdf"  # the slide report, June 2026; sha256 in data/raw/lbnl/SHA256.txt
LBNL_2026_RENAMES = {  # 2026 column names -> the 2025 names the pipeline uses
    "IA_phase_raw": "IA_status_raw", "IA_phase_clean": "IA_status_clean", "fips_code": "fips_codes",
    "type_1": "type1", "type_2": "type2", "type_3": "type3", "mw_1": "mw1", "mw_2": "mw2", "mw_3": "mw3",
}  # county_state_pairs no longer exists; dates arrive as datetimes, not Excel serials
LBNL_DATE_COLS = ["q_date", "prop_date", "on_date", "wd_date", "ia_date"]  # stored as Excel serial numbers
EXCEL_ORIGIN = "1899-12-30"  # Excel's day-zero for serial dates (Windows 1900 system)
PLACEHOLDER_Q_DATE = "1970-01-01"  # Unix epoch used as a fill value for unknown request dates
CENSOR_DATE = "2024-12-31"  # end of LBNL data collection; every open project is censored here
EARLIEST_VALID_DATE = "1950-01-01"  # event dates before this are typing errors (rule R3)
MW_FLAG_THRESHOLD = 5000  # requests above this many MW are flagged for review, not dropped (rule R6)
ERCOT_BULK_WD_DATE = "2018-08-29"  # 441 ERCOT withdrawals share this recorded date (notebook 02 (part A), decision #21)
TRACK_B_MAX_YEAR = 2017  # Track B uses entrants up to this year, resolved ones only (docs/plan.md §6)
RARE_TYPE_MIN = 100  # technology levels with fewer requests are pooled into "Other" (docs/plan.md §6, notebook 03)

# --- NREL Annual Technology Baseline 2024, v3 (source S12; capital and O&M per kW for the NPV of notebook 07) ---
ATB_URL = "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2024/v3.0.0/ATBe.parquet"  # OEDI data lake, public
ATB_FILENAME = "ATBe_2024_v3.parquet"
ATB_SHA256 = "22e75dfcb93f8c61e94f9fa3390f04bf943d67ad224b1c6b428c71cfbea7350b"  # hash of the copy downloaded 2026-10-12
# --- Regions ------------------------------------------------------------------
TRACK_A_REGIONS = ["ERCOT", "PJM", "CAISO"]  # the three ISOs whose public file carries event dates (decision #6)
OTHER_REGIONS = ["MISO", "SPP", "NYISO", "ISO-NE", "West", "Southeast"]  # timing not usable; Track B only
ALL_REGIONS = TRACK_A_REGIONS + OTHER_REGIONS

# --- Cohorts, horizons, split ------------------------------------------------
HEADLINE_YEARS = (2000, 2019)  # request years behind LBNL's "13 % built / 77 % withdrawn" headline
MOCKUP_YEARS = (2010, 2018)  # entry years for the naive 5-year completion mock-up
TUNE_MAX_YEAR = 2015  # hyperparameters tuned on entrants up to this year
VALIDATION_YEAR = 2016  # validation cohort for tuning and calibration
TRAIN_MAX_YEAR = 2016  # final refit uses entrants up to this year
TEST_YEARS = (2017, 2019)  # held-out test cohorts, outcomes observed through CENSOR_DATE
HORIZONS = [3, 5, 7]  # years after entry at which P(operation) is reported
DAYS_PER_YEAR = 365.25  # converts day differences to years

# --- Size regimes (FERC small/large generator step at 20 MW) -----------------
SIZE_BINS = [0, 5, 20, 100, 200, 500, np.inf]  # MW edges, right-open
SIZE_LABELS = ["<5", "5–<20", "20–<100", "100–<200", "200–<500", "≥500"]
FERC_SIZE_STEP_MW = 20  # SGIP/LGIP threshold under FERC Orders 2003/2006

# --- 2026-10-03 audit counts the raw file must reproduce (readiness gate) ----
AUDIT_EXPECTED = {
    "n_rows": 36441,
    "n_cols": 31,
    "q_status": {"withdrawn": 20921, "active": 10538, "operational": 4432,
                 "suspended": 546, "unknown": 4},
    "region": {"PJM": 8152, "West": 7675, "MISO": 4978, "Southeast": 3950,
               "ERCOT": 3282, "CAISO": 2837, "SPP": 2469, "NYISO": 1817,
               "ISO-NE": 1281},
    "placeholder_q_date": 204,
    "negative_mw_rows": 17,
}

# --- Readiness thresholds (docs/plan.md §5.3) -------------------------------------
HEADLINE_OPERATIONAL_SHARE = 0.13  # LBNL: ≈13 % of 2000–2019 capacity reached operation
HEADLINE_WITHDRAWN_SHARE = 0.77  # LBNL: ≈77 % was withdrawn
HEADLINE_TOLERANCE = 0.01  # "≈" read as ±1 percentage point
MOCKUP_EXPECTED = {"CAISO": 0.04, "ERCOT": 0.21, "PJM": 0.15}  # naive 5-year completion, 2010–2018 entrants
COVERAGE_MIN_ON_DATE = 0.95  # share of operational rows with on_date in each Track A region
COVERAGE_MIN_WD_DATE = 0.82  # was 0.83 (the audit's rounded value); amended 2026-10-03, decision #15
TRACK_A_RANGE = (13500, 14500)  # expected size of the Track A candidate sample
TEST_MIN_PROJECTS = 2000  # was 2,500, unreachable (2,313 Track A rows entered 2017–2019); decision #15
TEST_MIN_COMPLETIONS = 150  # completions by CENSOR_DATE among those entrants
EIA_MIN_PERIOD = "2026-06"  # the API must serve at least this month
EIA860M_PERIOD = "2026-07"  # the EIA-860M month every result is built on; pinned so a rerun reads the bundled pull, not a newer month (decision #108)
EIA_MIN_FIELD_SHARE = {"operating-year-month": 0.95, "stateid": 0.99, "technology": 0.99,
                       "county": 0.95, "latitude": 0.95, "longitude": 0.95}

# --- EIA API v2, EIA-860M inventory of operable generators (source S2) -------
EIA_API_BASE = "https://api.eia.gov/v2"
EIA_ROUTE = "electricity/operating-generator-capacity"  # "Inventory of Operable Generators", monthly
EIA_DATA_FIELDS = ["nameplate-capacity-mw", "operating-year-month",
                   "planned-retirement-year-month", "county", "latitude", "longitude"]
EIA_PAGE_LENGTH = 5000  # the API's maximum rows per call
EIA_TIMEOUT_S = 120  # seconds per request

# --- ERCOT Public API (source S7; api.ercot.com, a different host from the blocked ercot.com report servlet) ---
ERCOT_API_BASE = "https://api.ercot.com/api/public-reports"
ERCOT_TOKEN_URL = ("https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/"
                   "B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token")  # ERCOT's published B2C sign-in flow
ERCOT_CLIENT_ID = "fec253ea-0d06-4272-a5e6-b478baeecd70"  # public client id of the ERCOT Public API (not a secret)
ERCOT_REPORTS = {  # EMIL report id -> API path; all paged at ERCOT_PAGE_SIZE rows
    "NP4-190-CD": "np4-190-cd/dam_stlmnt_pnt_prices",  # DAM settlement point prices, hourly
    "NP6-905-CD": "np6-905-cd/spp_node_zone_hub",  # RTM settlement point prices, 15-minute
    "NP4-188-CD": "np4-188-cd/dam_clear_price_for_cap",  # DAM ancillary-service clearing prices
}
ERCOT_HUBS = ["HB_HOUSTON", "HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HUBAVG"]  # trading hubs kept
ERCOT_PAGE_SIZE = 5000  # the API's maximum rows per call
ERCOT_TIMEOUT_S = 120  # seconds per request
ERCOT_TZ = "America/Chicago"  # ERCOT delivery dates and hour-endings are local prevailing time

# --- EIA technology → LBNL type_clean crosswalk (reviewed in notebook 01 (part A)) ----
# value = (LBNL type, note); "Other" always carries a note saying what it hides
EIA_TECHNOLOGY_MAP = {
    "Solar Photovoltaic": ("Solar", ""),
    "Solar Thermal with Energy Storage": ("Solar", "concentrating solar; LBNL codes it as Solar"),
    "Solar Thermal without Energy Storage": ("Solar", "concentrating solar; LBNL codes it as Solar"),
    "Onshore Wind Turbine": ("Wind", ""),
    "Offshore Wind Turbine": ("Offshore Wind", ""),
    "Batteries": ("Battery", ""),
    "Flywheels": ("Other", "LBNL 'Other Storage'; too few units to keep apart"),
    "Natural Gas Fired Combined Cycle": ("Gas", ""),
    "Natural Gas Fired Combustion Turbine": ("Gas", ""),
    "Natural Gas Internal Combustion Engine": ("Gas", ""),
    "Natural Gas Steam Turbine": ("Gas", ""),
    "Natural Gas with Compressed Air Storage": ("Gas", "gas-fired compressed-air storage"),
    "Other Natural Gas": ("Gas", ""),
    "Conventional Hydroelectric": ("Hydro", ""),
    "Hydroelectric Pumped Storage": ("Hydro", "pumped storage; LBNL files some under Other Storage"),
    "Nuclear": ("Nuclear", ""),
    "Conventional Steam Coal": ("Coal", ""),
    "Coal Integrated Gasification Combined Cycle": ("Coal", ""),
    "Geothermal": ("Geothermal", ""),
    "Petroleum Liquids": ("Other", "LBNL Oil and Diesel; folded into Other"),
    "Petroleum Coke": ("Other", "LBNL Oil; folded into Other"),
    "Wood/Wood Waste Biomass": ("Other", "biomass; LBNL Other"),
    "Other Waste Biomass": ("Other", "biomass; LBNL Other"),
    "Landfill Gas": ("Other", "waste gas; LBNL Other"),
    "Municipal Solid Waste": ("Other", "waste; LBNL Other"),
    "Other Gases": ("Other", "refinery and blast-furnace gases; LBNL Other"),
    "All Other": ("Other", "EIA residual category"),
}
CROSSWALK_TYPES = ["Solar", "Wind", "Offshore Wind", "Battery", "Gas", "Hydro",
                   "Nuclear", "Coal", "Geothermal", "Other"]  # docs/plan.md §5.2 item 5

# --- Quick linkage test (docs/plan.md §5.2 item 6) --------------------------------
LINK_REGIONS = ["ERCOT", "PJM"]  # regions where LBNL already has COD dates to compare against
LINK_MW_TOLERANCE = 0.15  # nameplate must agree within ±15 %
LINK_MONTHS_TOLERANCE = 6  # COD agreement window in months
LINK_MIN_MATCH_RATE = 0.40  # notebook 10 is viable only above this match rate ...
LINK_MIN_AGREE_RATE = 0.80  # ... and if this share of matches agree on COD

# --- Colors (Okabe–Ito; validated for color-vision deficiency) ---------------
REGION_COLORS = {  # the three Track A ISOs keep these colors in every figure
    "ERCOT": "#D55E00",  # vermillion
    "PJM": "#0072B2",  # blue
    "CAISO": "#E69F00",  # orange
}
OTHER_REGION_COLOR = "#999999"  # all other regions are drawn in grey, never in a new hue
TECH_COLORS = {  # technology groups for plots (≤ 7 series per panel)
    "Solar": "#E69F00",
    "Solar+Battery": "#009E73",
    "Wind": "#56B4E9",
    "Offshore Wind": "#0072B2",
    "Battery": "#CC79A7",
    "Gas": "#555555",  # dark grey: fossil
    "Other": "#BBBBBB",  # light grey: folded tail
}
STATUS_COLORS = {  # q_status; operation green and withdrawal purple everywhere
    "operational": "#009E73",
    "active": "#56B4E9",
    "suspended": "#999999",
    "withdrawn": "#CC79A7",
}
OUTCOME_COLORS = {"operation": "#009E73", "withdrawal": "#CC79A7"}

# --- Source notes printed under figures --------------------------------------
FIGURE_AUTHOR = "Figure: Alan Mössinger."  # every figure names its author (decision #50)
SOURCE_LBNL = FIGURE_AUTHOR + " Data: LBNL Queued Up: 2025 Edition (Rand et al., 2025)."
SOURCE_LBNL_2026 = "LBNL Queued Up: 2026 Edition (Rand et al., 2026)."  # the file added alongside (decision #43)
SOURCE_EIA = "EIA-860M Inventory of Operable Generators via EIA API v2."

# --- v5 energy sources (docs/plan.md §14.1; decision #64) --------------------------
BSEE_URL = "https://www.data.bsee.gov/Production/Files/ogora{year}delimit.zip"  # OGOR-A delimited, one zip per year
BSEE_YEARS = (2010, 2024)  # first and last production year pulled (inclusive)
BSEE_LAYOUT_URL = "https://www.data.bsee.gov/Main/HtmlPage.aspx?page=ogora"  # field definitions (accessed 2026-10-12)
EGRID_URL = "https://www.epa.gov/system/files/documents/2025-01/egrid2023_data_rev1.xlsx"  # eGRID2023, revision 1
EGRID_FILENAME = "egrid2023_data_rev1.xlsx"
EGRID_PLANT_SHEET = "PLNT23"  # plant-level sheet; row 0 is a title banner, headers on row 1
EIA_PRICE_FILES = {  # EIA monthly spot-price workbooks (sheet "Data 1", two header rows)
    "wti_usd_bbl": ("https://www.eia.gov/dnav/pet/hist_xls/RWTCm.xls", "RWTCm.xls"),  # Cushing, OK WTI spot FOB
    "hh_usd_mmbtu": ("https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDm.xls", "RNGWHHDm.xls"),  # Henry Hub spot
}
EIA923_ROUTE = "electricity/facility-fuel"  # EIA-923 plant × fuel × prime-mover monthly generation and consumption
EIA923_DATA_FIELDS = ["generation", "gross-generation", "total-consumption-btu", "consumption-for-eg-btu"]
EIA923_STATE = "TX"  # the power candidates are ERCOT requests
EIA923_START, EIA923_END = "2018-01", "2024-12"  # the development and holdout window of the forecasts
ERCOT_2024_FILES = {  # my Forecast-to-Dispatch pull (gridstatus, July 2026), copied with its hashes
    "ercot_dam_spp_2024.parquet": "dc212cf26ea601e2bd09e48ac44ddbc9154305e044e77b2dc7edd88f2218c083",
    "ercot_rtm_spp_2024.parquet": "cacfffbb1158bf42a965ad3539bd310e2c79006d93be910ca594a763e7f9b385",
    "ercot_dam_mcpc_2024.parquet": "7c481f7b8a5d992294af66d5223f774ed7a04a27d1280512bcaa708bce2fdc45",
    "ercot_native_load_2024.parquet": "9dad8c1a23ec12dea68b95264fb27146c279aecd0094da780ed1bdf6de64f1c4",
    "ercot_wind_solar_2024.parquet": "b08fab037aa3ef3a6d71fe0a100ab6b7e122dfcbddef2bee74f2bf9b4ade0397",
}
ERCOT_HISTORY_FILES = {  # ERCOT's yearly "Historical DAM Load Zone and Hub Prices" files parsed by src/ercot_history.py on a U.S. runner (2026-10-14)
    "ercot_dam_spp_2018.parquet": "3c01950a105297ab924d7e28d740e17381942ab8736b406be8000958259d9e91",
    "ercot_dam_spp_2019.parquet": "248498491439c250a1b0823b56d5c5b6f5a96baa0fea8ca4d10d3bfc195c4cd7",
    "ercot_dam_spp_2020.parquet": "68caf44dbae2e6cb1d9f8892d448c1e0c0a53a5a2105312bdf5afa678a59055c",
    "ercot_dam_spp_2021.parquet": "bdcc3a4281af99bf684e42035577b739d3dd317e58c604dea12da2cefe7d8074",
    "ercot_dam_spp_2022.parquet": "27d161f1ab2647eb6e06f04da74b0095cdb0e64fee4441a4f29ad5f6bfc9a16c",
    "ercot_dam_spp_2023.parquet": "10e135cbf56914e0d566383baa152539305486e5885f7fa07b7f528d2d1328f1",
}
ERCOT_PRICE_HUB = "HB_NORTH"  # the hub carried as "the ERCOT price": it is the hub the ICE ERCOT North series quotes
PRIME_MOVER_TECH = {  # EIA-923 prime mover -> the candidate technologies (combined-cycle parts, PV, wind, batteries)
    "CA": "Gas CC", "CT": "Gas CC", "CS": "Gas CC", "PV": "Solar", "WT": "Wind", "BA": "Storage",
}
V5_COVERAGE = ("2018-01", "2024-12")  # every monthly series must span this window
V5_MIN_LEASES, V5_MIN_PRODUCING_MONTHS = 20, 60  # candidate pool: leases with at least this many producing months
V5_MIN_PLANTS_PER_TECH, V5_MIN_GENERATION_MONTHS = 5, 36  # Texas plants per technology with this much history
PROVENANCE = ("OBSERVED", "DERIVED", "FORECAST", "ASSUMED")  # the audit labels every v5 export carries
SOURCE_BSEE = "BSEE OGOR-A production (data.bsee.gov)."
SOURCE_EIA923 = "EIA-923 via EIA API v2 (electricity/facility-fuel)."
SOURCE_EIA_PRICES = "EIA WTI and Henry Hub monthly spot prices."
SOURCE_ERCOT = "ERCOT DAM/RTM settlement point prices (gridstatus pull, 2024; ERCOT yearly DAM files, 2018–2023)."
SOURCE_EGRID = "EPA eGRID2023."
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"  # public, no key; 10 years per call (source S18)
CPI_SERIES = "CUUR0000SA0"  # CPI-U, all items, U.S. city average, not seasonally adjusted (1982–84 = 100)
CPI_YEARS = (2016, 2024)  # window pulled; real dollars are stated in REAL_DOLLAR_YEAR
REAL_DOLLAR_YEAR = 2024  # every v5 cash flow is in 2024 dollars (the ATB file is in 2022 dollars; converted the same way)
ERCOT_BRIDGE_RATIO = 0.77  # ERCOT price 2020–2023 = PJM West × this (ratio of the 2017–2019 means; results/value_assumptions.csv)
ICE_HUB_ERCOT, ICE_HUB_PJM_WEST = "ERCOT North 345KV Peak", "PJM WH Real Time Peak"  # hub names in EIA's ICE files
RELEASE_LAGS = {  # months after the observation month a source is public (docs/plan.md §14.2; from each publisher's schedule)
    "BSEE OGOR-A": 3,  # operators file within 45 days, BSEE posts and revises for about three months
    "EIA-923 monthly": 2,  # the monthly file appears about two months after the data month
    "EIA-860M": 2,  # the monthly generator inventory lags about two months
    "WTI, Henry Hub": 0,  # spot prices are known the same month
    "ERCOT DAM/RTM": 0,  # settlement point prices are published next day
    "BLS CPI-U": 1,  # the index is released mid-month for the previous month
}
DECISION_DATE = "2025-01-01"  # one decision date for both sectors (decision #90): leases valued and requests still active on CENSOR_DATE
LINE_FEE = 0.005  # commitment fee a year on the undrawn part of the liquidity line (ASSUMED, decisions #102, #104: registered with the interest; range 0.0025–0.01)
LINE_RATE = 0.08  # interest a year on the drawn part, from the construction draw to operation (ASSUMED, decisions #102, #104: registered; range 0.06–0.10)
LINE_DISCOUNT = 0.08  # the rate the line's costs are discounted at: the committee grid's real hurdle (economics.COMMITTEE_GRID)
CONSTRUCTION_YEARS = 2  # years a plant's capital is drawn before it operates (ASSUMED, decision #102)
LINE_YEARS = 7  # the commitment period: the seven-year window in which a request can operate (HORIZON_YEARS)
LEASE_TERMINAL_DECLINE = 0.08  # effective annual decline the lease baselines switch to (modified hyperbolic; ASSUMED, decision #90)
LEASE_TERMINAL_DECLINE_RANGE = (0.05, 0.12)  # the sensitivity range reported beside the base
LEASE_MIN_POST_PEAK_MONTHS = 12  # fewer positive months after the peak and the lease is still ramping: it declines from its recent level at the floor
