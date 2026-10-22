"""The ERCOT candidates of 1 January 2025 rebuilt from what was public that day.

What: the pool of ERCOT requests a committee could see on the decision date —
the LBNL 2024 edition (requests through 2023) joined with ERCOT's monthly GIS
reports of April–November 2024 (the 2024 entrants and every request's status
in the last report before the date) — and the five largest per technology,
set beside the twenty candidates the 2025 edition gave.
Why: the 2025 edition, which defined the candidates until now, was released in
August 2025 (review of 21 October; decision #101). A request that entered
after the November 2024 report, or that ERCOT had not yet listed, was not
visible to a committee on 1 January 2025.
Reads: ``data/raw/lbnl/<LBNL_2024_FILENAME>``, ``data/raw/iso/gis_2024/*.xlsx``,
``results/candidate_npv.csv`` (the 2025-edition candidates, for comparison).
Writes: ``results/v10/asof_candidates.csv`` (``python -m src.asof_candidates``).
Used by: notebook 12; the decision whether v10 reruns notebooks 07–12 on a
changed candidate set.
"""

import numpy as np
import pandas as pd

from src import cleaning, config, decision_date, events, iso_files, paths

GIS_TYPE = {("WIN", "WT"): "Wind", ("SOL", "PV"): "Solar", ("OTH", "BA"): "Battery"}  # the reports' fuel and technology codes in the pipeline's labels
TECHNOLOGIES = ("Gas", "Solar", "Wind", "Battery")  # the pipeline's labels of the four candidate technologies (notebook 07 maps Gas to Gas CC, Battery to Storage)


def gis_type(fuel, technology):
    """The pipeline's technology label of a GIS row: any gas technology is Gas, as in the LBNL file."""
    if fuel == "GAS":
        return "Gas"
    return GIS_TYPE.get((fuel, technology), "Other")


def edition_2024():
    """The 2024 edition cleaned by the registered rules R1–R9 and coded for events at its own end (2023)."""
    raw = pd.read_excel(paths.RAW_LBNL / config.LBNL_2024_FILENAME, sheet_name="data", header=0)
    raw = raw.rename(columns={"county_1": "county"})
    for column in config.LBNL_DATE_COLS:  # the 2024 edition stores dates as text (m/d/Y); R1 reads Excel serial numbers, as the 2025 edition stores them
        dates = pd.to_datetime(raw[column], format="%m/%d/%Y", errors="coerce")
        raw[column] = (dates - pd.Timestamp("1899-12-30")).dt.days
    for column in ("cluster", "county_state_pairs", "fips_codes", "project_type"):
        if column not in raw:
            raw[column] = np.nan  # fields the 2024 edition does not carry; R5 keeps a missing project type
    log, clean = [], raw
    for rule in cleaning.RULES:  # R1-R9 as registered, except R7: the as-of view keys ERCOT requests by their INR, and R7's key is not unique across this edition's regions
        if rule is not cleaning.r7_project_key:
            clean = cleaning.apply_rule(rule, clean, log)
    return events.code_events(clean, censor_date="2023-12-31"), pd.DataFrame(log)


def gis_reports():
    """The monthly reports of 2024 stacked, one row per request and report month."""
    files = sorted((paths.DATA_RAW / "iso" / "gis_2024").glob("*.xlsx"), key=lambda f: iso_files.month_from_name(f.name))
    return pd.concat([iso_files.read_ercot_gis(f) for f in files], ignore_index=True)


def pool(edition, gis, as_of=config.DECISION_DATE):
    """Every ERCOT request a committee could see, each described by the most recent public record.

    Notes
    -----
    A request ERCOT's reports list takes its technology and size from the last
    report before the date (the newest public record; the 2024 edition gives a
    hybrid's combined size and a 2023 size that may since have changed), and
    its entry date and agreement date from the edition where the edition has
    it. A 2024 entrant only the reports show takes its entry date from the
    screening study's start, else from the first report that lists it. A
    request the reports never list keeps the edition's own record.
    """
    as_of = pd.Timestamp(as_of)
    e = edition[edition["region"] == "ERCOT"].copy()
    e["q_id"] = e["q_id"].astype(str).str.strip()
    hybrid = e["type_clean"].astype(str).str.contains("+", regex=False)
    e.loc[hybrid, "mw"] = e.loc[hybrid, "mw1"]  # a hybrid counted at its generator's size, as the 2025 edition and ERCOT count it
    e.loc[hybrid, "type_clean"] = e.loc[hybrid, "type1"]
    e = e.drop_duplicates("q_id").set_index("q_id")
    g = gis[gis["report_month"] < as_of].copy()
    g["q_id"] = g["q_id"].astype(str).str.strip()
    g = g.sort_values("report_month")
    first, latest = g.drop_duplicates("q_id", keep="first").set_index("q_id"), g.drop_duplicates("q_id", keep="last").set_index("q_id")
    rows = []
    for q in sorted(set(e.index) | set(latest.index)):
        in_e, in_g = q in e.index, q in latest.index
        row = {"q_id": q, "region": "ERCOT", "event": e.loc[q, "event"] if in_e else 0, "exit_date": e.loc[q, "exit_date"] if in_e else pd.NaT,
               "ia_date": e.loc[q, "ia_date"] if in_e else pd.NaT}
        if in_g:
            row["type_clean"] = gis_type(latest.loc[q, "fuel"], latest.loc[q, "technology"])
            row["mw"] = latest.loc[q, "mw"]
        else:
            row["type_clean"], row["mw"] = e.loc[q, "type_clean"], e.loc[q, "mw"]
        q_date = e.loc[q, "q_date"] if in_e else pd.NaT
        if pd.isna(q_date) and in_g:
            q_date = first.loc[q, "ss_started"] if pd.notna(first.loc[q, "ss_started"]) else first.loc[q, "report_month"]
        row["q_date"] = q_date
        row["source"] = "2024 edition and GIS" if in_e and in_g else ("2024 edition" if in_e else "GIS report only")
        rows.append(row)
    return pd.DataFrame(rows)


def live_pool(as_of=config.DECISION_DATE):
    """Every ERCOT request live on the date by the as-of rule, with its size and the agreement date public by then.

    Returns
    -------
    pandas.DataFrame
        ``q_id``, ``type_clean``, ``mw`` (from the last report before the date),
        ``ia_asof`` (the earliest agreement date public on the date: the 2024
        edition's, or the IA Signed date of a report before the date; NaT
        when none), ``source``.

    Notes
    -----
    Notebook 04 takes the live ERCOT requests, their sizes and their
    agreement dates from here, so the curves of the decision date condition
    on what a committee could read that day; notebook 07's rule (the five
    largest per technology) then gives the as-of candidates.
    """
    as_of = pd.Timestamp(as_of)
    edition, _ = edition_2024()
    gis = gis_reports()
    everyone = pool(edition, gis, as_of)
    g = gis[gis["report_month"] < as_of].copy()
    g["q_id"] = g["q_id"].astype(str).str.strip()
    latest = g[g["report_month"] == g["report_month"].max()]
    active = set(latest.loc[latest["listed_as"].str.startswith("active"), "q_id"])
    dead = set(g.loc[g["listed_as"].isin(["inactive", "cancelled"]), "q_id"])
    if "energization_approved" in g:
        dead |= set(g.loc[g["energization_approved"] <= as_of, "q_id"])
    live = everyone[everyone["q_id"].isin(active) & ~everyone["q_id"].isin(dead)].copy()
    signed = g[g["ia_signed"] <= as_of].groupby("q_id")["ia_signed"].min() if "ia_signed" in g else pd.Series(dtype="datetime64[ns]")
    edition_ia = live.set_index("q_id")["ia_date"].where(lambda d: d <= as_of)
    live["ia_asof"] = pd.concat([edition_ia, signed[signed.index.isin(live["q_id"])]], axis=1).min(axis=1).reindex(live["q_id"]).to_numpy()
    return live[["q_id", "type_clean", "mw", "ia_asof", "source"]].reset_index(drop=True)


def build(as_of=config.DECISION_DATE, per_tech=5):
    """The as-of candidates beside the 2025-edition candidates, one row per request in either set."""
    edition, _ = edition_2024()
    gis = gis_reports()
    everyone = pool(edition, gis, as_of)
    asof = decision_date.candidates_as_of(everyone, gis, as_of=as_of, per_tech=per_tech, technologies=TECHNOLOGIES, listing_complete=True)  # ERCOT's report lists every active request
    asof = asof.merge(everyone[["q_id", "source"]], on="q_id", how="left")
    old = pd.read_csv(paths.RESULTS / "candidate_npv.csv")
    old = old[old["sector"] == "ERCOT power"][["project_id", "technology", "mw", "agreement_known"]].copy()
    old["q_id"] = old["project_id"].str.split("|").str[-1]
    lbl = {"Gas": "Gas CC", "Battery": "Storage", "Solar": "Solar", "Wind": "Wind"}
    asof["technology"] = asof["type_clean"].map(lbl)
    table = old.rename(columns={"mw": "mw_2025_edition", "agreement_known": "agreement_known_2025_edition"}).merge(
        asof[["q_id", "technology", "mw", "agreement_known", "liveness_source", "source"]].rename(columns={"mw": "mw_asof", "agreement_known": "agreement_known_asof"}),
        on=["q_id"], how="outer", suffixes=("_2025_edition", "_asof"))
    table["in_2025_edition_build"] = table["project_id"].notna()
    table["in_asof_build"] = table["mw_asof"].notna()
    seen = set(gis.loc[gis["report_month"] < pd.Timestamp(as_of), "q_id"].astype(str).str.strip()) | set(everyone["q_id"])
    table["visible_on_the_date"] = table["q_id"].isin(seen)
    return table.sort_values(["in_asof_build", "in_2025_edition_build", "q_id"], ascending=[False, False, True]).reset_index(drop=True)


if __name__ == "__main__":
    table = build()
    out = paths.RESULTS / "v10"
    out.mkdir(exist_ok=True)
    table.to_csv(out / "asof_candidates.csv", index=False)
    both = int((table["in_asof_build"] & table["in_2025_edition_build"]).sum())
    only_old = table[table["in_2025_edition_build"] & ~table["in_asof_build"]]
    only_new = table[~table["in_2025_edition_build"] & table["in_asof_build"]]
    print(f"as-of candidates: {int(table['in_asof_build'].sum())}; in both builds: {both}; only in the 2025-edition build: {len(only_old)}; only in the as-of build: {len(only_new)}")
    print("only in the 2025-edition build:", only_old[["q_id", "technology_2025_edition", "mw_2025_edition", "visible_on_the_date"]].to_string(index=False))
    print("only in the as-of build:", only_new[["q_id", "technology_asof", "mw_asof", "source", "liveness_source", "agreement_known_asof"]].to_string(index=False))
