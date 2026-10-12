"""Why requests fail: driver rates, exit stages, annual hazards and entry-time segments.

What: five-year completion rates with Wilson intervals by any entry-time
attribute, crowding in the same county or at the same substation before
entry, the stage a withdrawn request had reached, annual cause-specific
hazards by year in the queue, and a shallow decision tree turned into a
table of rules with out-of-time rates.
Why: the report's "why do requests fail" section needs every rate to carry
an interval and an n, and the same cohort definition in every panel.
Keeping the arithmetic here keeps the notebooks to the story.
Reads / writes: nothing; the notebooks read ``data/interim/trackA.parquet``
and write ``results/``.
Used by: notebook 02 (part A) (sections 13-14), notebook 06 (part C) (section 4b), notebook 09 (part A)
(section 9, through ``results/segments_by_request.csv``).
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from src import config

HORIZON_YEARS = 5  # the completion horizon of every driver rate (PLAN.md §13)
COHORT_YEARS = (2010, 2019)  # entrants who all have five years of follow-up by CENSOR_DATE
CROWDING_WINDOW_YEARS = 2  # other requests at the same point of interconnection in the two years before entry
CROWDING_LABELS = ["0", "1–2", "3–5", "6+"]
CROWDING_BINS = [-0.5, 0.5, 2.5, 5.5, np.inf]
STAGE_ORDER = ["Feasibility study", "System impact study", "Facilities study", "Study (phase unknown)",
               "Agreement executed", "Unknown"]
# LBNL's IA_status_clean at the snapshot -> the stage a withdrawn request had reached.
# ERCOT has no feasibility stage; its "Facility Study" covers screening and the full study.
STAGE_MAP = {"Feasibility Study": "Feasibility study", "System Impact Study": "System impact study",
             "Facility Study": "Facilities study", "In Progress (unknown study)": "Study (phase unknown)",
             "IA Executed": "Agreement executed", "IA Pending": "Agreement executed"}


def wilson(k, n, z=1.96):
    """Wilson score interval for a proportion.

    Parameters
    ----------
    k, n : array-like
        Successes and trials.
    z : float
        Normal quantile; 1.96 for 95%.

    Returns
    -------
    tuple of numpy.ndarray
        Lower and upper bounds; NaN where ``n`` is 0.

    Notes
    -----
    The Wilson interval is used rather than the normal approximation because
    several cells (CAISO at 500 MW and more, for one) have rates near zero
    with a few dozen requests, where the normal interval would cross zero.
    """
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = k / n
        centre = (p + z**2 / (2 * n)) / (1 + z**2 / n)
        half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    low, high = centre - half, centre + half
    low = np.where(n > 0, np.clip(low, 0, 1), np.nan)
    high = np.where(n > 0, np.clip(high, 0, 1), np.nan)
    return low, high


def five_year_cohort(track_a, years=COHORT_YEARS, horizon=HORIZON_YEARS):
    """Track A entrants of the cohort years with a binary "operated within the horizon" outcome.

    Notes
    -----
    Every entrant of 2010–2019 has at least five years between its request
    and the censor date (2024-12-31), so the five-year outcome is observed
    for all of them and a plain proportion is the right estimator — no
    censoring correction is needed, unlike the 7-year curves of notebook 02 (part A).
    The function asserts that this holds rather than assuming it.
    """
    frame = track_a[track_a["q_year"].between(*years)].copy()
    followed = (pd.Timestamp(config.CENSOR_DATE) - frame["q_date"]).dt.days / config.DAYS_PER_YEAR
    assert (followed >= horizon).all(), "every cohort request must have the full horizon of follow-up"
    frame["built"] = (frame["event"] == 1) & (frame["duration_years"] <= horizon)
    return frame


def rate_by(frame, column, driver=None, group="region", min_n=20):
    """Completion rate with a Wilson interval by one attribute, within each region.

    Parameters
    ----------
    frame : pandas.DataFrame
        Output of ``five_year_cohort`` with the attribute column present.
    column : str
        The attribute (levels become rows).
    driver : str, optional
        Name written in the ``driver`` column (defaults to ``column``).
    group : str
        Second grouping, the region by default.
    min_n : int
        Cells with fewer requests are kept in the table but flagged ``thin``.
    """
    rows = (frame.groupby([group, column], observed=True)["built"]
            .agg(n="size", built="sum").reset_index())
    rows["rate"] = rows["built"] / rows["n"]
    rows["low"], rows["high"] = wilson(rows["built"], rows["n"])
    rows["thin"] = rows["n"] < min_n
    rows.insert(0, "driver", driver or column)
    return rows.rename(columns={column: "level"})


def poi_crowding(frame, window_years=CROWDING_WINDOW_YEARS, key="poi_name"):
    """Other requests at the same point of interconnection (or county) in the window before entry.

    Parameters
    ----------
    frame : pandas.DataFrame
        Needs ``region``, ``poi_name`` and ``q_date``.
    window_years : float
        Length of the look-back window.
    key : str
        ``"poi_name"`` for the substation, ``"fips_codes"`` for the county.

    Returns
    -------
    pandas.Series
        Count per request; NaN where the key or the request date is missing.

    Notes
    -----
    Only requests dated strictly before the entry date and no earlier than
    the window count, so the feature is known on the entry day and never
    sees a later request (the same rule as ``features.congestion_at_entry``).
    POI names are compared after lower-casing and collapsing whitespace,
    because the same substation is typed several ways in the file. A
    request never counts itself.
    """
    name = frame[key].astype("string").str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    key = frame["region"].astype(str) + "|" + name.astype(object).fillna("")
    known = name.notna() & frame["q_date"].notna()
    out = pd.Series(np.nan, index=frame.index, dtype=float)
    window = pd.Timedelta(days=window_years * config.DAYS_PER_YEAR).to_timedelta64()
    for _, idx in pd.Series(frame.index[known], index=key[known].to_numpy()).groupby(level=0):
        dates = frame.loc[idx.to_numpy(), "q_date"].sort_values()
        values = dates.to_numpy()
        before = np.searchsorted(values, values, side="left")  # strictly earlier requests
        since = np.searchsorted(values, values - window, side="left")
        out.loc[dates.index] = before - since
    return out


def crowding_bins(count):
    """Bin the crowding count into the four labels used in the figures."""
    return pd.cut(count, CROWDING_BINS, labels=CROWDING_LABELS)


def congestion_quintile(frame, column="congestion_gw"):
    """Within-region quintile (1 = quietest fifth) of the GW waiting at entry."""
    return (frame.groupby("region", observed=True)[column]
            .transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]))
            .astype("Int64"))


def stage_at_exit(status_clean):
    """Map LBNL's ``IA_status_clean`` to the ordered stage a withdrawn request had reached."""
    stage = pd.Series(status_clean).map(STAGE_MAP).fillna("Unknown")
    return pd.Categorical(stage, categories=STAGE_ORDER, ordered=True)


def annual_hazards(frame, by="region", max_years=7):
    """Discrete annual operation and withdrawal hazards by year in the queue.

    Returns
    -------
    pandas.DataFrame
        One row per group and year: ``at_risk``, ``operations``,
        ``withdrawals``, ``h_operation``, ``h_withdrawal`` and Wilson bounds.

    Notes
    -----
    Year k covers (k − 1, k] years after the request; a request is at risk
    in year k if it was still in the queue at the start of the year and was
    watched through the whole year (``survival_tools.expand_project_years``).
    Delayed entry is not applied here because the drivers cohort
    starts in 2010, after ERCOT's file begins to date withdrawals.
    """
    from src import survival_tools

    rows = survival_tools.expand_project_years(frame, max_years=max_years)
    rows[by] = frame.loc[rows["project"], by].to_numpy()
    table = (rows.groupby([by, "year_in_queue"], observed=True)["outcome"]
             .agg(at_risk="size", operations=lambda s: int((s == 1).sum()), withdrawals=lambda s: int((s == 2).sum()))
             .reset_index())
    table["h_operation"] = table["operations"] / table["at_risk"]
    table["h_withdrawal"] = table["withdrawals"] / table["at_risk"]
    table["h_operation_low"], table["h_operation_high"] = wilson(table["operations"], table["at_risk"])
    table["h_withdrawal_low"], table["h_withdrawal_high"] = wilson(table["withdrawals"], table["at_risk"])
    return table


def segment_design(frame, crowding):
    """Entry-time design for the segment tree.

    Notes
    -----
    Region, technology group and service type are one-hot; size is log MW;
    congestion is the within-region rank of the GW waiting at entry;
    crowding is log(1 + other requests in the same county in the two years
    before entry). Two things are left out on purpose. The entry year, so
    that a rule reads as a property of the request, not of its vintage (the
    level drift is the subject of notebook 04 (part G)). And the absolute GW waiting,
    because it rises with calendar time in every region, so a tree given it
    splits the cohort into early and late entrants instead of into kinds of
    request (a first prototype did exactly that, and its leaf rates did
    not hold on the later cohort).
    """
    X = pd.DataFrame(index=frame.index)
    X["log_mw"] = frame["log_mw"].astype(float)
    X["congestion_rank"] = frame["congestion_rank"].astype(float).fillna(frame["congestion_rank"].median())
    X["county_crowding"] = np.log1p(crowding.fillna(0).astype(float))
    X["hybrid"] = frame["hybrid"].astype(float)
    X["service_ERIS"] = (frame["service"] == "ERIS").astype(float)
    for region in config.TRACK_A_REGIONS:
        X[f"region_{region}"] = (frame["region"] == region).astype(float)
    for tech in sorted(frame["tech"].dropna().unique()):
        X[f"tech_{tech}"] = (frame["tech"] == tech).astype(float)
    return X


def fit_segment_tree(X, y, max_depth=4, min_samples_leaf=200, seed=0):
    """A shallow classification tree on the five-year outcome.

    Notes
    -----
    Depth four and at least 200 requests per leaf keep the rules short enough
    to read and the leaf rates estimable (a 200-request leaf at 10% has a
    Wilson interval of about ±4 points). The tree is a description, not the
    predictor; notebook 04 (parts A–C) and 06 (parts A–B) hold the predictive models.
    """
    tree = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=min_samples_leaf, random_state=seed)
    return tree.fit(X, y)


FEATURE_WORDS = {"congestion_gw": "GW waiting in region", "congestion_rank": "queue rank",
                 "hybrid": "hybrid", "service_ERIS": "energy-only service"}


def _condition(name, sign, threshold):
    """One split as a short phrase, with transformed features turned back into plain units."""
    le = sign == "le"
    if name == "log_mw":
        return f"{'≤' if le else '>'} {np.exp(threshold):,.0f} MW"
    if name == "county_crowding":
        count = int(np.floor(np.expm1(threshold)))  # the split falls between count and count + 1 earlier requests
        if le:
            return "no earlier request in county" if count == 0 else f"≤ {count} earlier requests in county"
        return "1+ earlier requests in county" if count == 0 else f"{count + 1}+ earlier requests in county"
    if name.startswith("region_") or name.startswith("tech_"):
        return f"{'not ' if le else ''}{name.split('_', 1)[1]}"
    if name in ("hybrid", "service_ERIS"):
        return f"{'not ' if le else ''}{FEATURE_WORDS[name]}"
    return f"{FEATURE_WORDS.get(name, name)} {'≤' if le else '>'} {threshold:.2f}"


def leaf_rules(tree, feature_names):
    """Rules of every leaf as a dictionary ``leaf_id -> list of conditions``."""
    t = tree.tree_
    rules = {}

    def walk(node, path):
        if t.children_left[node] == -1:
            rules[node] = path
            return
        name = feature_names[t.feature[node]]
        thr = t.threshold[node]
        walk(t.children_left[node], path + [_condition(name, "le", thr)])
        walk(t.children_right[node], path + [_condition(name, "gt", thr)])

    walk(0, [])
    return rules


def segment_table(tree, X_train, y_train, X_test, y_test):
    """Leaf rates on the fitting cohort and the later cohort, with intervals."""
    rules = leaf_rules(tree, list(X_train.columns))
    y_train, y_test = np.asarray(y_train), np.asarray(y_test)
    out = []
    for leaf, path in rules.items():
        in_train = tree.apply(X_train) == leaf
        in_test = tree.apply(X_test) == leaf
        n_tr, k_tr = int(in_train.sum()), int(y_train[in_train].sum())
        n_te, k_te = int(in_test.sum()), int(y_test[in_test].sum())
        out.append({"leaf": leaf, "rule": "; ".join(path), "n_train": n_tr, "built_train": k_tr,
                    "rate_train": k_tr / n_tr if n_tr else np.nan,
                    "n_test": n_te, "built_test": k_te, "rate_test": k_te / n_te if n_te else np.nan})
    table = pd.DataFrame(out)
    table["low_train"], table["high_train"] = wilson(table["built_train"], table["n_train"])
    table["low_test"], table["high_test"] = wilson(table["built_test"], table["n_test"])
    return table.sort_values("rate_train", ascending=False).reset_index(drop=True)

