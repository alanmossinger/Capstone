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
ERCOT_BULK_WD_DATE = "2018-08-29"  # 441 ERCOT withdrawals share this recorded date (notebook 03, decision #21)
TRACK_B_MAX_YEAR = 2017  # Track B uses entrants up to this year, resolved ones only (PLAN.md §6)
RARE_TYPE_MIN = 100  # technology levels with fewer requests are pooled into "Other" (PLAN.md §6, notebook 04)

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

# --- Readiness thresholds (PLAN.md §5.3) -------------------------------------
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
EIA_MIN_FIELD_SHARE = {"operating-year-month": 0.95, "stateid": 0.99, "technology": 0.99,
                       "county": 0.95, "latitude": 0.95, "longitude": 0.95}

# --- EIA API v2, EIA-860M inventory of operable generators (source S2) -------
EIA_API_BASE = "https://api.eia.gov/v2"
EIA_ROUTE = "electricity/operating-generator-capacity"  # "Inventory of Operable Generators", monthly
EIA_DATA_FIELDS = ["nameplate-capacity-mw", "operating-year-month",
                   "planned-retirement-year-month", "county", "latitude", "longitude"]
EIA_PAGE_LENGTH = 5000  # the API's maximum rows per call
EIA_TIMEOUT_S = 120  # seconds per request

# --- EIA technology → LBNL type_clean crosswalk (reviewed in notebook 01) ----
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
                   "Nuclear", "Coal", "Geothermal", "Other"]  # PLAN.md §5.2 item 5

# --- Quick linkage test (PLAN.md §5.2 item 6) --------------------------------
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
