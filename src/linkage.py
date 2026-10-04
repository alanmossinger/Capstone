"""Match LBNL queue projects to EIA-860M generators.

What: a deliberately simple record-linkage rule. An LBNL project matches an
EIA plant vintage (one plant, one technology group, one operating month)
when they share the state and technology group, their capacities agree
within ±15 %, and their names share at least one distinctive word. The
operating date is *not* used to match, so it can be used afterwards to test
whether the match is right.
Why: the public LBNL file has no operation dates for MISO, SPP, the West and
most of the Southeast. If projects can be linked to EIA-860M, the EIA
operating month could fill that gap (stretch notebook 10). The quick test in
notebook 01 measures the rule where both sources have dates (ERCOT, PJM).
Reads: the raw LBNL DataFrame (with dates) and the EIA-860M pull.
Writes: nothing (notebook 01 saves the summary to ``results/``).
Used by: notebook 01 (quick test) and notebook 10 (stretch).
"""

import re

import numpy as np
import pandas as pd

from src import config

# Words that appear in many plant names and say nothing about which plant it is.
_STOPWORDS = set("""
solar wind energy project projects llc inc lp farm farms center centre power station
generating generation battery batteries storage facility renewable renewables the of
and park plant phase unit units ii iii iv county kv ess bess pv wf sf gas north south
east west new city road ranch co company holdings partners dg cogen cogeneration hybrid
""".split())


def name_tokens(*names):
    """Split names into distinctive lowercase words.

    Parameters
    ----------
    *names : str or None
        Any number of names; missing values are skipped.

    Returns
    -------
    set of str
        Alphabetic words of three or more letters that are not stopwords.

    Notes
    -----
    Digits are dropped because phase numbers ("2", "II") and voltages
    ("345kV") match unrelated plants.
    """
    tokens = set()
    for name in names:
        if isinstance(name, str):
            tokens.update(word for word in re.findall(r"[a-z]+", name.lower())
                          if len(word) >= 3 and word not in _STOPWORDS)
    return tokens


def eia_plant_vintages(generators):
    """Collapse EIA generators to plant × technology group × operating month.

    Parameters
    ----------
    generators : pandas.DataFrame
        EIA-860M pull from ``eia_api.pull_generators``.

    Returns
    -------
    pandas.DataFrame
        ``plantid``, ``plantName``, ``stateid``, ``type_clean``,
        ``op_month`` (timestamp), ``mw`` (summed nameplate) and ``tokens``.

    Notes
    -----
    A queue request usually covers a whole project phase that EIA reports as
    several generators coming online in the same month, so units are summed
    within plant, technology group and month before comparing capacities.
    """
    table = generators.assign(
        type_clean=generators["technology"].map(
            lambda t: config.EIA_TECHNOLOGY_MAP.get(t, ("Other", ""))[0]),
        op_month=pd.to_datetime(generators["operating-year-month"]))
    vintages = (table.groupby(["plantid", "plantName", "stateid", "type_clean", "op_month"],
                              as_index=False)["nameplate-capacity-mw"].sum()
                .rename(columns={"nameplate-capacity-mw": "mw"}))
    vintages["tokens"] = vintages["plantName"].map(name_tokens)
    return vintages


def lbnl_link_type(type1):
    """Map an LBNL primary resource type (``type1``) to a crosswalk group.

    Notes
    -----
    Oil, Diesel and LBNL's own "Other" fall into "Other", mirroring how the
    EIA crosswalk folds petroleum and biomass technologies.
    """
    return type1 if type1 in config.CROSSWALK_TYPES else "Other"


def match_projects(projects, vintages, mw_tolerance=config.LINK_MW_TOLERANCE):
    """Find the best EIA plant vintage for each LBNL project, without using dates.

    Parameters
    ----------
    projects : pandas.DataFrame
        LBNL rows with ``state``, ``type1``, ``mw1``, ``project_name``,
        ``region`` and ``on_date``.
    vintages : pandas.DataFrame
        Output of ``eia_plant_vintages``.
    mw_tolerance : float
        Allowed relative capacity difference.

    Returns
    -------
    pandas.DataFrame
        One row per project (same index): ``region``, ``link_type``,
        ``matched``, ``reason`` (why a project did not match, or
        "matched"), ``eia_plantid``, ``eia_plant_name``, ``eia_mw`` and
        ``months_apart`` (EIA operating month minus LBNL ``on_date``, in
        whole months; missing when unmatched).

    Notes
    -----
    Candidates share state and technology group, share at least one name
    word and lie within ±15 % of the project's primary capacity ``mw1``.
    Among them the one sharing the most words wins, then the closest
    capacity. The project name alone is used: the point-of-interconnection
    name is a substation, which often shares words with unrelated plants.
    The name filter is applied before the capacity filter only so that
    ``reason`` can separate "the plant exists but its size differs" (typical
    of uprates and partial phases) from "no plant with that name".
    """
    by_cell = {key: group for key, group in vintages.groupby(["stateid", "type_clean"])}
    results = []
    for project in projects.itertuples():
        link_type = lbnl_link_type(project.type1)
        best, reason = _best_candidate(project, by_cell.get((project.state, link_type)),
                                       mw_tolerance)
        row = {"region": project.region, "link_type": link_type, "matched": best is not None,
               "reason": reason, "eia_plantid": np.nan, "eia_plant_name": np.nan,
               "eia_mw": np.nan, "months_apart": np.nan}
        if best is not None:
            row.update(eia_plantid=best["plantid"], eia_plant_name=best["plantName"],
                       eia_mw=best["mw"],
                       months_apart=(best["op_month"].year - project.on_date.year) * 12
                       + (best["op_month"].month - project.on_date.month))
        results.append(row)
    return pd.DataFrame(results, index=projects.index)


def _best_candidate(project, cell, mw_tolerance):
    """Return (best EIA vintage row or None, reason) for one project."""
    tokens = name_tokens(project.project_name)
    if not tokens:
        return None, "no usable project name"
    if cell is None or not (project.mw1 > 0):
        return None, "no EIA plant of that type in the state"
    named = cell.assign(shared=cell["tokens"].map(lambda t: len(t & tokens)))
    named = named[named["shared"] > 0]
    if named.empty:
        return None, "no EIA plant shares a name word"
    close = named[(named["mw"] - project.mw1).abs() <= mw_tolerance * project.mw1]
    if close.empty:
        return None, "name found, capacity differs >15 %"
    close = close.assign(gap=np.abs(np.log(close["mw"] / project.mw1)))
    return close.sort_values(["shared", "gap"], ascending=[False, True]).iloc[0], "matched"


def summarise_matches(matches, months=config.LINK_MONTHS_TOLERANCE, by=None):
    """Match rate and COD agreement rate, overall or by group.

    Parameters
    ----------
    matches : pandas.DataFrame
        Output of ``match_projects``.
    months : int
        Agreement window (|months_apart| ≤ months).
    by : str or list of str, optional
        Grouping columns; overall when omitted.

    Returns
    -------
    pandas.DataFrame
        ``projects``, ``matched``, ``match_rate``, ``agree``, ``agree_rate``.
    """
    keys = [by] if isinstance(by, str) else list(by or [])
    frame = matches.assign(agree=matches["matched"] & (matches["months_apart"].abs() <= months))
    if not keys:
        frame["group"] = "all"
        keys = ["group"]
    table = frame.groupby(keys).agg(projects=("matched", "size"), matched=("matched", "sum"),
                                    agree=("agree", "sum")).reset_index()
    table["match_rate"] = table["matched"] / table["projects"]
    table["agree_rate"] = table["agree"] / table["matched"].where(table["matched"] > 0)
    return table[keys + ["projects", "matched", "match_rate", "agree", "agree_rate"]]
