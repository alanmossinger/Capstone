"""Positions for the project map: county centroids for queue requests, state outlines.

What: reads the Census cartographic boundary files (states and counties,
1:20m), gives every queue request a county centroid from its FIPS code,
and turns EIA-860M coordinates into points in the same projection.
Why: the LBNL file has county and FIPS for 91% of requests but no
coordinates, so a county centroid is the finest position the public data
allows; the operating fleet (EIA-860M) has exact coordinates. Both are
drawn in the Albers equal-area projection for the contiguous states so
distances and areas read correctly.
Reads: ``data/raw/geo/cb_2020_us_state_20m.zip``,
``data/raw/geo/cb_2020_us_county_20m.zip`` (public domain, U.S. Census
Bureau). The 2020 vintage is used because LBNL's county codes predate the
2022 change of Connecticut's counties to planning regions.
Writes: nothing.
Used by: notebook 03b (figure F9) and notebook 17 (playbook maps).
"""

import geopandas as gpd
import pandas as pd

from src import paths

RAW_GEO = paths.DATA_RAW / "geo"
STATE_FILE = RAW_GEO / "cb_2020_us_state_20m.zip"
COUNTY_FILE = RAW_GEO / "cb_2020_us_county_20m.zip"
CONUS_CRS = "EPSG:5070"  # NAD83 / Conus Albers equal-area
NOT_CONUS = {"02", "15", "60", "66", "69", "72", "78"}  # AK, HI and the territories; the queue data are CONUS
# EIA balancing-authority codes of the three Track A ISOs, so the fleet uses the same colors as the queue
BA_TO_REGION = {"ERCO": "ERCOT", "PJM": "PJM", "CISO": "CAISO"}
FIPS_ALIASES = {"46113": "46102"}  # Shannon County, SD became Oglala Lakota County in 2015; LBNL keeps the old code


def load_states():
    """State outlines of the contiguous United States, projected.

    Returns
    -------
    geopandas.GeoDataFrame
        One row per state with ``STUSPS`` (postal code) and geometry.

    Notes
    -----
    Alaska, Hawaii and the territories are left out: the LBNL queue covers
    the contiguous grid, and drawing them would shrink the map that matters.
    """
    states = gpd.read_file(f"zip://{STATE_FILE}")
    states = states[~states["STATEFP"].isin(NOT_CONUS)]
    return states.to_crs(CONUS_CRS)


def load_county_centroids():
    """County centroids keyed by five-digit FIPS, projected.

    Returns
    -------
    geopandas.GeoDataFrame
        Columns ``GEOID``, ``STUSPS``, ``NAME`` and a point geometry.

    Notes
    -----
    ``representative_point`` is used rather than the geometric centroid so
    the point always falls inside the county (a centroid can fall outside a
    concave or multi-part county).
    """
    counties = gpd.read_file(f"zip://{COUNTY_FILE}")
    counties = counties[~counties["STATEFP"].isin(NOT_CONUS)].to_crs(CONUS_CRS)
    counties["geometry"] = counties.representative_point()
    return counties[["GEOID", "STUSPS", "NAME", "geometry"]]


def first_fips(fips_codes):
    """The first five-digit county FIPS in LBNL's ``fips_codes`` column.

    Parameters
    ----------
    fips_codes : pandas.Series
        LBNL's column: a number such as ``4005.0`` (leading zero lost) or a
        concatenation of several codes (``4800148003.0``) when a request
        spans counties.

    Returns
    -------
    pandas.Series
        Five-character strings, ``NA`` where missing.

    Notes
    -----
    Codes are stored as floats, so ``04005`` arrives as ``4005``; the
    length of the digit string says whether a leading zero was lost
    (4 digits) or several codes were concatenated (10, 15, 20 digits). A
    multi-county request is placed in its first county, which is how the
    source lists it.
    """
    codes = pd.to_numeric(fips_codes, errors="coerce")
    # formatted, not cast: four rows concatenate four codes (20 digits), beyond int64
    digits = codes[codes > 0].map("{:.0f}".format)
    # 4, 9, 14, 19 digits: a leading zero was lost from the first code
    digits = digits.where(digits.str.len() % 5 == 0, "0" + digits)
    return digits.str[:5].replace(FIPS_ALIASES).reindex(fips_codes.index)


def queue_points(queue):
    """Attach a county centroid to every queue request that has a FIPS code.

    Parameters
    ----------
    queue : pandas.DataFrame
        The clean queue table (notebook 02) with ``fips_codes``.

    Returns
    -------
    geopandas.GeoDataFrame
        The input rows with ``fips`` and a point geometry; rows without a
        usable FIPS have an empty geometry and ``matched == False``.
    """
    centroids = load_county_centroids().set_index("GEOID")["geometry"]
    out = queue.copy()
    out["fips"] = first_fips(out["fips_codes"])
    out["geometry"] = out["fips"].map(centroids)
    out["matched"] = out["geometry"].notna()
    return gpd.GeoDataFrame(out, geometry="geometry", crs=CONUS_CRS)


def eia_points(generators):
    """EIA-860M generators as projected points with a Track A region label.

    Parameters
    ----------
    generators : pandas.DataFrame
        The EIA-860M pull (notebook 01) with ``latitude``, ``longitude`` and
        ``balancing_authority_code``.

    Returns
    -------
    geopandas.GeoDataFrame
        Rows with coordinates inside the contiguous states, a point geometry
        and ``region`` ∈ {ERCOT, PJM, CAISO, Other} from the balancing
        authority.
    """
    gens = generators.dropna(subset=["latitude", "longitude"]).copy()
    gens["latitude"] = pd.to_numeric(gens["latitude"], errors="coerce")
    gens["longitude"] = pd.to_numeric(gens["longitude"], errors="coerce")
    gens = gens[gens["latitude"].between(24, 50) & gens["longitude"].between(-125, -66)]
    gens["region"] = gens["balancing_authority_code"].map(BA_TO_REGION).fillna("Other")
    points = gpd.points_from_xy(gens["longitude"], gens["latitude"], crs="EPSG:4326")
    return gpd.GeoDataFrame(gens, geometry=points).to_crs(CONUS_CRS)
