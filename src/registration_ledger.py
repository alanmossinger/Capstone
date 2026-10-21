"""The three-column registration ledger: every registered line, what was corrected after it, and its status now.

What: one table over the registered criteria C1–C32 with, for each line, the
verdict as first scored, each correction made afterwards with its date, and
the line's status now (as registered; a post-registration result on the
corrected system; reported beside the registered verdict).
Why: the critique of 21 October asked how a reader tells a registered verdict
from a later correction. The scored files keep every scoring, and
``docs/decisions.md`` records every correction, but no single table joins
them; this one does, from those files, so the report's Appendix A cites it.
Reads: ``results/success_criteria*.csv`` (C1–C19), ``results/tournament_criteria.csv``,
``results/registered_bridged/`` and ``results/registered_v7/`` (C20–C24 as
first scored on the bridged prices and as registered on the observed prices),
``results/success_criteria_v7_scored.csv`` (C21–C24 on the corrected system),
``results/v9/success_criteria_v9_scored.csv`` and ``c31_sensitivity.json``.
Writes: ``results/v10/registration_ledger.csv`` and ``docs/registration_ledger.md``.
Used by: notebook 12, ``src/report_numbers.py``; ``tests/test_registration_ledger.py``.
"""

import json

import pandas as pd

from src import paths

R = paths.RESULTS
AS_REGISTERED = "as registered"

# Every correction after a registration, in the words of docs/decisions.md; the number is the source, not part of the text.
CORRECTIONS = {
    "observed prices": ("rescored on the observed ERCOT prices in place of the PJM bridge; the bridged verdict kept beside it", "2026-10-14", "#80"),
    "corrected system": ("applied to the corrected system (comparators under the cap, the 2025 candidates as seen that day, the decline floor, "
                         "the two-stage budget, inputs public on the decision date) as a post-registration result", "2026-10-20", "#89, #94"),
    "c31 checks": ("two checks reported and not registered: the edge without its largest case, and against a fixed rule that takes the "
                   "optimizer's book first", "2026-10-20", "#97"),
}


def _verdict(v):
    """One spelling of a verdict whatever the file's column holds (PASS/FAIL, True/False)."""
    if isinstance(v, str):
        return v.upper()
    return "PASS" if bool(v) else "FAIL"


def _rows(ids, lines, verdicts, registered_on, source):
    return [{"criterion": i, "line": l, "registered_on": registered_on, "registered_verdict": _verdict(v), "source_file": source}
            for i, l, v in zip(ids, lines, verdicts)]


def registered_lines():
    """The 78 registered lines (C1–C32) with their verdict as first scored, from the scored files."""
    out = []
    d = pd.read_csv(R / "success_criteria.csv")
    out += _rows(d["id"], [f"{m}{'' if pd.isna(h) else f' at {int(h)} years'}, track {t}, {mod}" for m, h, t, mod in zip(d["metric"], d["horizon"], d["track"], d["model"])],
                 d["result"], "2026-10-04", "results/success_criteria.csv")
    d = pd.read_csv(R / "success_criteria_v2_scored.csv")
    out += _rows(d["id"], d["line"], d["result"], "2026-10-06", "results/success_criteria_v2_scored.csv")
    d = pd.read_csv(R / "success_criteria_v3_scored.csv")
    out += _rows(d["id"], d["line"], d["result"], "2026-10-08", "results/success_criteria_v3_scored.csv")
    d = pd.read_csv(R / "success_criteria_v4_scored.csv")
    out += _rows(d["id"], d["line"], d["pass"], "2026-10-08", "results/success_criteria_v4_scored.csv")
    d = pd.read_csv(R / "success_criteria_v5_scored.csv")
    out += _rows(d["id"], d["line"], d["result"], "2026-10-12", "results/success_criteria_v5_scored.csv")
    d = pd.read_csv(R / "registered_bridged" / "success_criteria_v6_scored.csv")
    d = d[d["registered"]]
    out += _rows(d["id"], d["label"], d["result"], "2026-10-12", "results/registered_bridged/success_criteria_v6_scored.csv")
    d = pd.read_csv(R / "registered_bridged" / "success_criteria_v7_scored.csv")
    out += _rows(d["id"], d["line"], d["result"], "2026-10-12", "results/registered_bridged/success_criteria_v7_scored.csv")
    d = pd.read_csv(R / "v9" / "success_criteria_v9_scored.csv")
    out += _rows(d["id"], d["line"], d["result"], "2026-10-20", "results/v9/success_criteria_v9_scored.csv")
    return pd.DataFrame(out)


def corrections():
    """One row per (line, correction): what changed, when, and the verdict after it."""
    rows = []
    text, date, src = CORRECTIONS["observed prices"]
    v6 = pd.read_csv(R / "registered_v7" / "success_criteria_v6_scored.csv")
    for _, r in v6[v6["registered"]].iterrows():
        rows.append({"criterion": r["id"], "line": r["label"], "correction": text, "correction_date": date, "decision": src,
                     "verdict_after": _verdict(r["result"]), "status": f"{AS_REGISTERED}: the observed-price scoring is the registered verdict",
                     "source_file": "results/registered_v7/success_criteria_v6_scored.csv"})
    # C21–C24 have one line each; the registered text is the bridged file's (C24's comparator was relabelled "leases only" when the
    # single-sector rule picked the leases, decision #71), so the later scorings are keyed by criterion.
    registered_line = pd.read_csv(R / "registered_bridged" / "success_criteria_v7_scored.csv").set_index("id")["line"]
    v7 = pd.read_csv(R / "registered_v7" / "success_criteria_v7_scored.csv")
    for _, r in v7.iterrows():
        rows.append({"criterion": r["id"], "line": registered_line[r["id"]], "correction": text, "correction_date": date, "decision": src,
                     "verdict_after": _verdict(r["result"]), "status": f"{AS_REGISTERED}: the observed-price scoring is the registered verdict",
                     "source_file": "results/registered_v7/success_criteria_v7_scored.csv"})
    text, date, src = CORRECTIONS["corrected system"]
    v8 = pd.read_csv(R / "success_criteria_v7_scored.csv")
    for _, r in v8.iterrows():
        rows.append({"criterion": r["id"], "line": registered_line[r["id"]], "correction": text, "correction_date": date, "decision": src,
                     "verdict_after": _verdict(r["result"]), "status": f"post-registration result on the corrected system: {_verdict(r['result'])}; the registered verdict stands",
                     "source_file": "results/success_criteria_v7_scored.csv"})
    text, date, src = CORRECTIONS["c31 checks"]
    sens = json.loads((R / "v9" / "c31_sensitivity.json").read_text(encoding="utf-8"))
    v9 = pd.read_csv(R / "v9" / "success_criteria_v9_scored.csv").set_index("id")
    rows.append({"criterion": "C31", "line": v9.loc["C31", "line"], "correction": text, "correction_date": date, "decision": src,
                 "verdict_after": _verdict(v9.loc["C31", "result"]),
                 "status": f"{AS_REGISTERED} ({_verdict(v9.loc['C31', 'result'])}); without the largest case +${sens['without_largest']['mean'] / 1e6:.0f}M, "
                           f"against the optimizer-first rule +${sens['vs_optimizer_first']['mean'] / 1e6:.0f}M, reported beside it",
                 "source_file": "results/v9/c31_sensitivity.json"})
    return pd.DataFrame(rows)


def build():
    """The ledger: the registered lines joined with their corrections; a line with none reads "as registered".

    Returns
    -------
    pandas.DataFrame
        Columns ``criterion, line, registered_on, registered_verdict, correction,
        correction_date, decision, verdict_after, status, source_file``; one
        row per line and, for a corrected line, one more per correction.

    Notes
    -----
    Registered verdicts are never re-scored (decision #88): a correction adds
    a row, it does not change one. The C20–C24 lines were first scored on
    bridged ERCOT prices, so their registered verdict here is that first
    scoring and the observed-price verdict is their first correction row.
    """
    lines = registered_lines()
    corr = corrections()
    merged = lines.merge(corr.drop(columns=["source_file"]), on=["criterion", "line"], how="left")
    merged["status"] = merged["status"].fillna(AS_REGISTERED)
    for c in ("correction", "correction_date", "decision", "verdict_after"):
        merged[c] = merged[c].fillna("")
    order = {f"C{i}": i for i in range(1, 40)}
    merged["_k"] = merged["criterion"].map(order)
    return merged.sort_values(["_k", "line", "correction_date"], kind="stable").drop(columns="_k").reset_index(drop=True)


def write(ledger):
    """Write the CSV and the markdown table; return the counts the report cites."""
    out = R / "v10"
    out.mkdir(exist_ok=True)
    ledger.to_csv(out / "registration_ledger.csv", index=False)
    n_lines = int(ledger.groupby(["criterion", "line"]).ngroups)
    corrected = ledger[ledger["correction"] != ""]
    n_corrected = int(corrected.groupby(["criterion", "line"]).ngroups)
    n_changed = int((corrected["registered_verdict"] != corrected["verdict_after"]).sum())
    head = ("# Registration ledger\n\n"
            "Every registered line with its verdict as first scored, each correction made afterwards with its date, and its status now. "
            "A registered verdict is never re-scored: a correction adds a row and the original stands. "
            f"{n_lines} lines; {n_corrected} with a correction; {n_changed} correction rows whose verdict differs from the registered one. "
            "Built by `src/registration_ledger.py` from the scored files in `results/`.\n\n")
    cols = ["criterion", "line", "registered_on", "registered_verdict", "correction", "correction_date", "verdict_after", "status"]
    table = "| " + " | ".join(cols) + " |\n|" + "|".join(["---"] * len(cols)) + "|\n"
    for _, r in ledger.iterrows():
        table += "| " + " | ".join(str(r[c]).replace("|", "/") for c in cols) + " |\n"
    (paths.DOCS / "registration_ledger.md").write_text(head + table, encoding="utf-8")
    return {"lines": n_lines, "corrected": n_corrected, "verdict_changed": n_changed}


if __name__ == "__main__":
    counts = write(build())
    print(f"{counts['lines']} registered lines; {counts['corrected']} with a correction; {counts['verdict_changed']} correction rows with a different verdict")
