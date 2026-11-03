"""Every number the report cites, read from ``results/`` and written to one table.

What: reads the result tables the notebooks wrote and collects, under a short
key, each value that the report quotes, already formatted the way
the report prints it (``12.8%``, ``2,268``, ``+0.121``).
Why: every number in the report must trace to ``results/``, never be typed
by hand. With one table of quoted values, ``tests/test_report.py`` can
check that each number in the report's text appears here, and anyone can
look up where a number comes from (``source`` column).
Reads: CSV and JSON files in ``results/``; design constants from
``src/config.py`` and ``src/track_b.py``. The steps are named after the
layers that produced the tables (v1 entry models, v3 portfolio layer, v4
managed book, v5 the capital-allocation additions; docs/plan.md §13) and read the
notebooks that own them since the consolidation of 2026-10-12 (docs/plan.md
§14): 01 data, 02 EDA, 03 features, 04 forecasting, 06 the record, 07
economics, 09 the portfolio.
Writes: ``results/report_numbers.csv`` (key, text, value, source, note).
Used by: ``make numbers`` (``python -m src.report_numbers``), before the
report is written or rebuilt; ``tests/test_report.py``.
"""

import json

import numpy as np
import re

import pandas as pd

from src import config, optimizer as opt, paths, track_b

ROWS = []


def add(key, text, value, source, note=""):
    """Record one cited number.

    Parameters
    ----------
    key : str
        Short unique name, e.g. ``c1_diff_3``.
    text : str
        The number exactly as the report prints it.
    value : float or str
        The unrounded value behind ``text``.
    source : str
        Result file (or module constant) the value was read from.
    note : str
        What the number is, in a few words.

    Notes
    -----
    Keys must be unique so the table can be used as a lookup; a repeated key
    is a mistake in this script, so it raises rather than overwrites.
    """
    if any(row["key"] == key for row in ROWS):
        raise ValueError(f"duplicate key {key}")
    ROWS.append({"key": key, "text": text, "value": value, "source": source, "note": note})


def pct(x, digits=1):
    """Format a share as a percentage without a space (``0.128`` → ``12.8%``)."""
    return f"{100 * x:.{digits}f}%"


def num(x, digits=3, sign=False):
    """Format a decimal, with a typographic minus and an optional plus sign."""
    text = f"{x:+.{digits}f}" if sign else f"{x:.{digits}f}"
    return text.replace("-", "−")


def interval(low, high, digits=3, sign=True):
    """Format a 95% interval as ``[low, high]``."""
    return f"[{num(low, digits, sign)}, {num(high, digits, sign)}]"


def read(name):
    """Read one result file (CSV or JSON) from ``results/``."""
    path = paths.RESULTS / name
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return pd.read_csv(path)


def design_constants():
    """Horizons, split years, thresholds and resampling settings fixed before any result.

    Notes
    -----
    These are choices, not results, but the report quotes them, so they are
    traced too: from ``src/config.py``, ``src/track_b.py`` and the registered
    criteria file written before scoring (decision #5).
    """
    src = "src/config.py"
    for h in config.HORIZONS:
        add(f"horizon_{h}", str(h), h, src, "prediction horizon, years")
    add("ferc_step_mw", str(config.FERC_SIZE_STEP_MW), config.FERC_SIZE_STEP_MW, src, "FERC small/large generator step, MW")
    add("size_top_edge", f"{config.SIZE_BINS[-2]:,}", config.SIZE_BINS[-2], src, "lower edge of the largest size regime, MW")
    add("rare_type_min", str(config.RARE_TYPE_MIN), config.RARE_TYPE_MIN, src, "technology levels pooled below this count")
    add("mw_flag", f"{config.MW_FLAG_THRESHOLD:,}", config.MW_FLAG_THRESHOLD, src, "requests above this MW flagged")
    add("calibration_min_bin", str(track_b.CALIBRATION_MIN_BIN), track_b.CALIBRATION_MIN_BIN, "src/track_b.py",
        "requests behind every step of the isotonic map")
    add("state_prior", str(track_b.STATE_PRIOR), track_b.STATE_PRIOR, "src/track_b.py", "smoothing of the state encoding")
    registered = read("success_criteria_registered.json")
    add("bootstrap_resamples", str(registered["n_boot"]), registered["n_boot"], "results/success_criteria_registered.json",
        "paired bootstrap resamples")
    add("interval_level", pct(registered["level"], 0), registered["level"], "results/success_criteria_registered.json",
        "interval level of every reported interval")
    add("c3_low", "0.9", 0.9, "docs/decisions.md #5", "C3 lower bound of the calibration slope")
    add("c3_high", "1.1", 1.1, "docs/decisions.md #5", "C3 upper bound of the calibration slope")
    add("c4_threshold", "1.5", 1.5, "docs/decisions.md #5", "C4 minimum top-decile lift")
    add("top_share", "10%", 0.10, "docs/decisions.md #5", "share of requests in the top decile")
    add("n_criteria_lines", "12", 12, "results/success_criteria.csv", "criterion × horizon lines")
    add("cv_folds", "5", 5, "src/discrete_time.py", "grouped cross-validation folds")
    add("lgbm_learning_rate", "0.05", 0.05, "src/discrete_time.py", "LightGBM learning rate")
    add("lgbm_fraction", "0.8", 0.8, "src/discrete_time.py", "LightGBM feature and bagging fraction")
    add("lgbm_l2", "1.0", 1.0, "src/discrete_time.py", "LightGBM L2 penalty")
    for track in ["a", "b"]:
        seed = registered[f"seed_track_{track}"]
        add(f"seed_track_{track}", str(seed), seed, "results/success_criteria_registered.json",
            f"bootstrap seed, Track {track.upper()}")


def gathering_and_cleaning():
    """Source files, the readiness gate, the cleaning rules and the samples (notebooks 01 and 03)."""
    audit = read("audit_counts.json")
    add("lbnl_rows", f"{audit['n_rows']:,}", audit["n_rows"], "results/audit_counts.json", "rows in the LBNL file")
    add("lbnl_cols", str(audit["n_cols"]), audit["n_cols"], "results/audit_counts.json", "columns in the LBNL file")
    add("placeholder_q_date", str(audit["placeholder_q_date"]), audit["placeholder_q_date"], "results/audit_counts.json",
        "request dates stored as 1970-01-01")

    eia = read("eia860m_profile.json")
    add("eia_rows", f"{eia['rows']:,}", eia["rows"], "results/eia860m_profile.json", "EIA-860M generators pulled")
    add("eia_pages", str(eia["pages"]), eia["pages"], "results/eia860m_profile.json", "API pages")
    add("eia_gw", f"{eia['nameplate_gw']:,.1f}", eia["nameplate_gw"], "results/eia860m_profile.json", "nameplate GW in EIA-860M")

    ready = read("readiness_checks.csv")
    passed = int((ready["result"] == "PASS").sum())
    add("readiness_passed", str(passed), passed, "results/readiness_checks.csv", "readiness checks passed")
    add("readiness_total", str(len(ready)), len(ready), "results/readiness_checks.csv", "readiness checks")

    head = read("headline_checks.json")
    add("headline_operational", pct(head["capacity_share_operational_2000_2019"]),
        head["capacity_share_operational_2000_2019"], "results/headline_checks.json", "2000–2019 capacity operational")
    add("headline_withdrawn", pct(head["capacity_share_withdrawn_2000_2019"]),
        head["capacity_share_withdrawn_2000_2019"], "results/headline_checks.json", "2000–2019 capacity withdrawn")
    add("median_cod_early", num(head["median_ir_to_cod_2000_2007"], 1), head["median_ir_to_cod_2000_2007"],
        "results/headline_checks.json", "median request-to-operation years, 2000–07 completions")
    add("median_cod_late", num(head["median_ir_to_cod_2018_2024"], 1), head["median_ir_to_cod_2018_2024"],
        "results/headline_checks.json", "median request-to-operation years, 2018–24 completions")

    cov = read("event_date_coverage.csv").set_index("region")
    for region in ["CAISO", "MISO", "SPP", "West"]:
        add(f"on_cov_{region}", pct(cov.loc[region, "on_date_share"]), cov.loc[region, "on_date_share"],
            "results/event_date_coverage.csv", f"{region} operational rows with an operation date")
        add(f"wd_cov_{region}", pct(cov.loc[region, "wd_date_share"]), cov.loc[region, "wd_date_share"],
            "results/event_date_coverage.csv", f"{region} withdrawn rows with a withdrawal date")

    link = read("linkage_test.csv").iloc[0]
    add("linkage_matched", pct(link["match_rate"]), link["match_rate"], "results/linkage_test.csv", "LBNL projects matched to EIA")
    add("linkage_agree", pct(link["agree_rate"]), link["agree_rate"], "results/linkage_test.csv", "matches agreeing within 6 months")
    add("linkage_bar_match", "40%", 0.40, "docs/plan.md §5.3", "pre-set match bar")
    add("linkage_bar_agree", "80%", 0.80, "docs/plan.md §5.3", "pre-set agreement bar")
    add("linkage_projects", f"{int(link['projects']):,}", link["projects"], "results/linkage_test.csv", "projects in the linkage test")

    log = read("clean_log.csv")
    add("clean_rows_out", f"{int(log['rows_out'].iloc[-1]):,}", log["rows_out"].iloc[-1], "results/clean_log.csv", "rows after cleaning")
    cleared = int(log[log["item"].str.contains("cleared")]["rows"].sum())
    add("dates_cleared", str(cleared), cleared, "results/clean_log.csv", "event dates cleared by R3 and R4")
    dropped_r5 = int(log[log["rule"] == "R5"]["rows"].sum())
    add("dropped_r5", str(dropped_r5), dropped_r5, "results/clean_log.csv", "non-generation requests dropped")

    counts = read("trackA_event_counts.csv").set_index("region").loc["All"]
    for col, key in [("All", "trackA_n"), ("operation", "trackA_op"), ("withdrawal", "trackA_wd"), ("censored", "trackA_cens")]:
        add(key, f"{int(counts[col]):,}", counts[col], "results/trackA_event_counts.csv", f"Track A {col}")

    sizes = read("sample_sizes.csv")
    b = sizes[sizes["track"] == "B"].set_index("split")
    add("trackB_n", f"{int(b['requests'].sum()):,}", b["requests"].sum(), "results/sample_sizes.csv", "Track B requests")
    add("trackB_test_n", f"{int(b.loc['test', 'requests']):,}", b.loc["test", "requests"], "results/sample_sizes.csv", "Track B 2017 requests")
    add("trackB_test_built", str(int(b.loc["test", "operation"])), b.loc["test", "operation"], "results/sample_sizes.csv", "Track B 2017 built")
    share = b.loc["test", "operation"] / b.loc["test", "requests"]
    add("trackB_test_share", pct(share), share, "results/sample_sizes.csv", "Track B 2017 share built")

    a = sizes[sizes["track"] == "A"]
    for split in ["train", "validation", "test"]:
        n = int(a[a["split"] == split]["requests"].sum())
        add(f"trackA_{split}_n", f"{n:,}", n, "results/sample_sizes.csv", f"Track A {split} requests")
    test = a[a["split"] == "test"].set_index("region")
    for region in config.TRACK_A_REGIONS:
        add(f"test_n_{region}", f"{int(test.loc[region, 'requests']):,}", test.loc[region, "requests"],
            "results/sample_sizes.csv", f"{region} test requests")

    status = read("test_outcome_status.csv")
    allrows = status[status["region"] == "all"].set_index("horizon")
    add("test_op_5", str(int(allrows.loc[5, "operated"])), allrows.loc[5, "operated"], "results/test_outcome_status.csv",
        "test requests operating within 5 years")
    share5 = allrows.loc[5, "operated"] / allrows.loc[5, "n"]
    add("test_op_5_share", pct(share5), share5, "results/test_outcome_status.csv", "share of test requests operating within 5 years")
    caiso = status[status["region"] == "CAISO"].set_index("horizon")
    add("test_op_5_CAISO", str(int(caiso.loc[5, "operated"])), caiso.loc[5, "operated"], "results/test_outcome_status.csv",
        "CAISO test requests operating within 5 years")
    later = int(a[a["split"] == "later"]["requests"].sum())
    add("trackA_later_n", f"{later:,}", later, "results/sample_sizes.csv", "Track A requests entering after 2019, not used")
    add("test_unknown_7", str(int(allrows.loc[7, "unknown"])), allrows.loc[7, "unknown"], "results/test_outcome_status.csv",
        "test requests censored before 7 years")

    cohort = read("cohort_check.csv")
    for year in sorted(cohort["entry_year"].unique()):
        n = int(cohort[cohort["entry_year"] == year]["n"].iloc[0])
        add(f"test_n_{year}", f"{n:,}", n, "results/cohort_check.csv", f"test requests entering {year}")

    feats = read("feature_summary.csv")
    main = feats[feats["use"] == "main"]
    add("n_features_main", str(len(main)), len(main), "results/feature_summary.csv", "entry-time feature columns")


def eda():
    """Survival curves, size and congestion views, reproduced LBNL figures (notebook 02 (part A))."""
    cif = read("cif_horizons.csv")
    reg = cif[(cif["grouping"] == "region") & (cif["time"] == 5.0)].set_index("group")
    for region in config.TRACK_A_REGIONS:
        add(f"cif5_op_{region}", pct(reg.loc[region, "cif_operation"]), reg.loc[region, "cif_operation"],
            "results/cif_horizons.csv", f"{region} P(operation by 5 years), all entrants")
        add(f"cif5_wd_{region}", pct(reg.loc[region, "cif_withdrawal"]), reg.loc[region, "cif_withdrawal"],
            "results/cif_horizons.csv", f"{region} P(withdrawal by 5 years), all entrants")

    tech = cif[(cif["grouping"] == "region × technology") & (cif["time"] == 5.0)].set_index("group")["cif_operation"]
    storage = tech[tech.index.str.endswith("| Battery") | tech.index.str.endswith("| Solar+Battery")]
    add("cif5_storage_max", pct(storage.max()), storage.max(), "results/cif_horizons.csv",
        "highest 5-year operation of batteries or solar+battery in any region")
    for region in config.TRACK_A_REGIONS:
        for group in ["Gas", "Solar"]:
            v = tech[f"{region} | {group}"]
            add(f"cif5_{group.lower()}_{region}", pct(v), v, "results/cif_horizons.csv", f"{region} {group} 5-year operation")

    size = read("five_year_by_size.csv").set_index(["region", "size_regime"])
    for region in ["PJM", "CAISO"]:
        for regime, tag in [("<5", "small"), ("≥500", "large")]:
            add(f"size5_{region}_{tag}", pct(size.loc[(region, regime), "p5"]), size.loc[(region, regime), "p5"],
                "results/five_year_by_size.csv", f"{region} 5-year completion, {regime} MW")

    for regime, tag in [("100–<200", "mid"), ("≥500", "large")]:
        add(f"size5_ERCOT_{tag}", pct(size.loc[("ERCOT", regime), "p5"]), size.loc[("ERCOT", regime), "p5"],
            "results/five_year_by_size.csv", f"ERCOT 5-year completion, {regime} MW")
    for regime, tag in [("5–<20", "below"), ("20–<100", "above")]:
        add(f"size5_CAISO_{tag}20", pct(size.loc[("CAISO", regime), "p5"]), size.loc[("CAISO", regime), "p5"],
            "results/five_year_by_size.csv", f"CAISO 5-year completion, {regime} MW")

    cong = read("five_year_by_congestion.csv").set_index(["region", "bin"])
    for region in config.TRACK_A_REGIONS:
        for b, tag in [(1, "low"), (5, "high")]:
            add(f"cong5_{region}_{tag}", pct(cong.loc[(region, b), "p5"]), cong.loc[(region, b), "p5"],
                "results/five_year_by_congestion.csv", f"{region} 5-year completion, congestion fifth {b}")

    bench = read("benchmarks.csv")
    rates = bench[bench["benchmark"].str.startswith("completion rate")]
    worst = float(rates["difference"].abs().max())
    add("benchmark_max_gap", num(100 * worst, 1), 100 * worst, "results/benchmarks.csv",
        "largest gap to LBNL's completion rates, points")

    ercot = read("ercot_bulk_date_sensitivity.csv").set_index(read("ercot_bulk_date_sensitivity.csv").columns[0])
    add("ercot_stamped_n", str(int(ercot.loc["as recorded", "n"] - ercot.loc["bulk-dated withdrawals dropped", "n"])),
        ercot.loc["as recorded", "n"] - ercot.loc["bulk-dated withdrawals dropped", "n"],
        "results/ercot_bulk_date_sensitivity.csv", "ERCOT 2000–2019 entrants with the bulk withdrawal date")


def modelling():
    """Sample of project-years, hyperparameter searches and their choices (notebook 04, parts A–C)."""
    rows = read("dt_rows_summary.csv").set_index("region")
    add("dt_project_years", f"{int(rows.loc['all', 'project-years']):,}", rows.loc["all", "project-years"],
        "results/dt_rows_summary.csv", "project-years in the final discrete-time fit")
    add("dt_ercot_with_rows", str(int(rows.loc["ERCOT", "requests with rows"])), rows.loc["ERCOT", "requests with rows"],
        "results/dt_rows_summary.csv", "ERCOT training requests left after delayed entry")
    add("dt_ercot_requests", str(int(rows.loc["ERCOT", "requests to 2016"])), rows.loc["ERCOT", "requests to 2016"],
        "results/dt_rows_summary.csv", "ERCOT training requests before delayed entry")

    tune = read("dt_tuning.json")
    add("logit_C", num(tune["logit"]["C"], 1), tune["logit"]["C"], "results/dt_tuning.json", "logit ridge strength C")
    add("logit_cv_loss", num(tune["logit"]["cv_log_loss"], 3), tune["logit"]["cv_log_loss"], "results/dt_tuning.json", "logit CV log loss")
    lg = tune["lgbm"]
    add("lgbm_leaves", str(lg["num_leaves"]), lg["num_leaves"], "results/dt_tuning.json", "LightGBM leaves")
    add("lgbm_min_leaf", str(lg["min_data_in_leaf"]), lg["min_data_in_leaf"], "results/dt_tuning.json", "LightGBM min rows per leaf")
    add("lgbm_rounds", str(lg["rounds"]), lg["rounds"], "results/dt_tuning.json", "LightGBM boosting rounds")
    add("lgbm_cv_leaves", str(lg["cv_choice"]["num_leaves"]), lg["cv_choice"]["num_leaves"], "results/dt_tuning.json",
        "leaves preferred by grouped CV")
    val = tune["validation_log_loss_2016"]
    for name, key in [("no information", "val_loss_none"), ("dt_logit", "val_loss_logit"),
                      ("dt_lgbm (chosen on 2016)", "val_loss_lgbm"), ("dt_lgbm (CV's choice)", "val_loss_lgbm_cv")]:
        add(key, num(val[name], 3), val[name], "results/dt_tuning.json", f"2016 log loss, {name}")

    grid = read("dt_cv_lgbm.csv")
    add("lgbm_grid_size", str(len(grid)), len(grid), "results/dt_cv_lgbm.csv", "LightGBM settings searched")
    rho = grid["cv_log_loss"].corr(grid["valid_log_loss"], method="spearman")
    add("lgbm_grid_spearman", num(rho, 2), rho, "results/dt_cv_lgbm.csv", "Spearman, CV vs 2016 log loss")
    logit_grid = read("dt_cv_logit.csv")
    add("logit_grid_C_min", num(logit_grid["C"].min(), 3), logit_grid["C"].min(), "results/dt_cv_logit.csv", "smallest C searched")
    add("logit_grid_C_max", num(logit_grid["C"].max(), 1), logit_grid["C"].max(), "results/dt_cv_logit.csv", "largest C searched")

    cox = read("cox_penalizer_tuning.csv")
    best = cox.loc[cox.groupby("cause")["validation_log_likelihood"].idxmax()].set_index("cause")["penalizer"]
    add("cox_pen_op", num(best["operation"], 2), best["operation"], "results/cox_penalizer_tuning.csv", "Cox ridge, operation")
    add("cox_pen_wd", num(best["withdrawal"], 1), best["withdrawal"], "results/cox_penalizer_tuning.csv", "Cox ridge, withdrawal")

    hr = read("cox_hazard_ratios.csv")
    hr = hr[hr["version"].str.startswith("main")].set_index(["cause", "covariate"])
    for cov, key in [("region_ERCOT", "hr_ercot"), ("region_CAISO", "hr_caiso"), ("tech_Gas", "hr_gas"),
                     ("size_<5", "hr_small"), ("size_≥500", "hr_large")]:
        row = hr.loc[("operation", cov)]
        add(key, num(row["hazard_ratio"], 2), row["hazard_ratio"], "results/cox_hazard_ratios.csv", f"operation HR, {cov}")
        add(f"{key}_ci", interval(row["ci_low"], row["ci_high"], 2, sign=False), f"{row['ci_low']}–{row['ci_high']}",
            "results/cox_hazard_ratios.csv", f"95% interval, operation HR, {cov}")

    wd = hr.loc[("withdrawal", "tech_Gas")]
    add("hr_gas_wd", num(wd["hazard_ratio"], 2), wd["hazard_ratio"], "results/cox_hazard_ratios.csv", "withdrawal HR, gas")
    add("hr_gas_wd_ci", interval(wd["ci_low"], wd["ci_high"], 2, sign=False), f"{wd['ci_low']}–{wd['ci_high']}",
        "results/cox_hazard_ratios.csv", "95% interval, withdrawal HR, gas")

    tb = read("trackB_tuning.json")
    add("tb_logit_C", num(tb["logit_C"], 1), tb["logit_C"], "results/trackB_tuning.json", "Track B logit C")
    add("tb_leaves", str(tb["lgbm"]["num_leaves"]), tb["lgbm"]["num_leaves"], "results/trackB_tuning.json", "Track B leaves")
    add("tb_min_leaf", str(tb["lgbm"]["min_data_in_leaf"]), tb["lgbm"]["min_data_in_leaf"], "results/trackB_tuning.json",
        "Track B min rows per leaf")
    add("tb_rounds", str(tb["lgbm"]["rounds"]), tb["lgbm"]["rounds"], "results/trackB_tuning.json", "Track B rounds")
    add("tb_spearman", num(tb["spearman_cv_vs_2016"], 2), tb["spearman_cv_vs_2016"], "results/trackB_tuning.json",
        "Track B Spearman, CV vs 2016")
    tv = read("trackB_validation.csv").set_index("model")
    for model in ["baseline", "logit", "lgbm"]:
        add(f"tb_val_auc_{model}", num(tv.loc[model, "auc"], 3), tv.loc[model, "auc"], "results/trackB_validation.csv",
            f"Track B 2016 AUC, {model}")


def evaluation():
    """The registered criteria and the other notebook 06 (part A) results."""
    crit = read("success_criteria.csv")
    crit["h"] = crit["horizon"].fillna(0).astype(int)
    passes = int((crit["result"] == "PASS").sum())
    add("criteria_pass", str(passes), passes, "results/success_criteria.csv", "criterion lines passed")
    pe = int(((crit["point_estimate_reading"] == "better") & (crit["result"] == "FAIL")).sum())
    add("criteria_pe_differ", str(pe), pe, "results/success_criteria.csv", "lines better on the point estimate but FAIL")
    for _, r in crit.iterrows():
        tag = f"{r['id'].lower()}_{r['metric']}_{r['h']}"
        add(f"{tag}_est", num(r["estimate"], 4 if r["metric"] == "brier" else 3 if r["metric"] != "lift_10" else 2),
            r["estimate"], "results/success_criteria.csv", f"{r['id']} {r['metric']} estimate")
        if pd.notna(r["diff"]):
            digits = 3
            add(f"{tag}_diff", num(r["diff"], digits, sign=True), r["diff"], "results/success_criteria.csv",
                f"{r['id']} {r['metric']} paired difference")
            add(f"{tag}_ci", interval(r["diff_low"], r["diff_high"], digits), f"{r['diff_low']}–{r['diff_high']}",
                "results/success_criteria.csv", f"{r['id']} {r['metric']} 95% interval of the difference")
            add(f"{tag}_bench", num(r["benchmark_estimate"], 4 if r["metric"] == "brier" else 3), r["benchmark_estimate"],
                "results/success_criteria.csv", f"{r['id']} {r['metric']} benchmark estimate")
        else:
            add(f"{tag}_ci", interval(r["low"], r["high"], 2, sign=False), f"{r['low']}–{r['high']}",
                "results/success_criteria.csv", f"{r['id']} {r['metric']} 95% interval")

    m = read("metrics.csv")
    m = m[m["track"] == "A"].set_index(["model", "metric", "horizon"])
    for model in ["baseline", "cox", "dt_logit", "dt_lgbm"]:
        for h in config.HORIZONS:
            add(f"auc_{model}_{h}", num(m.loc[(model, "auc", float(h)), "estimate"], 3), m.loc[(model, "auc", float(h)), "estimate"],
                "results/metrics.csv", f"time-dependent AUC, {model}, {h} years")
            add(f"slope_{model}_{h}", num(m.loc[(model, "slope", float(h)), "estimate"], 2),
                m.loc[(model, "slope", float(h)), "estimate"], "results/metrics.csv", f"calibration slope, {model}, {h} years")
    p10 = m.loc[("dt_lgbm", "precision_10", 5.0), "estimate"]
    add("precision10_lgbm_5", pct(p10), p10, "results/metrics.csv", "share operating within 5 years, top decile")
    lift_b = m.loc[("baseline", "lift_10", 5.0), "estimate"]
    add("lift_baseline_5", num(lift_b, 2), lift_b, "results/metrics.csv", "baseline top-decile lift, 5 years")

    cal = read("calibration.csv")
    d9 = cal[(cal["horizon"] == 5) & (cal["model"] == "dt_lgbm") & (cal["decile"] == 9)].iloc[0]
    add("decile9_pred", pct(d9["predicted"]), d9["predicted"], "results/calibration.csv", "LightGBM 5-year decile 9 predicted")
    add("decile9_obs", pct(d9["observed"]), d9["observed"], "results/calibration.csv", "LightGBM 5-year decile 9 observed")

    reg = read("calibration_by_region.csv").set_index(["region", "horizon"])
    add("pjm5_pred", pct(reg.loc[("PJM", 5), "dt_lgbm"]), reg.loc[("PJM", 5), "dt_lgbm"], "results/calibration_by_region.csv",
        "PJM mean predicted 5-year")
    add("pjm5_obs", pct(reg.loc[("PJM", 5), "observed"]), reg.loc[("PJM", 5), "observed"], "results/calibration_by_region.csv",
        "PJM observed 5-year")

    cohort = read("cohort_check.csv")
    for _, r in cohort[cohort["horizon"] == 5].iterrows():
        y = int(r["entry_year"])
        add(f"obs5_{y}", pct(r["observed"]), r["observed"], "results/cohort_check.csv", f"observed 5-year, {y} entrants")
        add(f"lgbm5_{y}", pct(r["dt_lgbm"]), r["dt_lgbm"], "results/cohort_check.csv", f"LightGBM mean 5-year, {y} entrants")

    gains = read("gains.csv")
    g = gains[(gains["horizon"] == 5) & (np.isclose(gains["fraction"], 0.1))].set_index("model")["captured"]
    for model in ["dt_lgbm", "baseline"]:
        add(f"captured10_{model}", pct(g[model]), g[model], "results/gains.csv", f"share of 5-year operations in top 10%, {model}")

    by_region = read("metrics_by_region.csv").set_index(["region", "model", "metric", "horizon"])
    for model in ["dt_lgbm", "baseline"]:
        v = by_region.loc[("PJM", model, "uno_c", 5), "estimate"]
        add(f"pjm_uno5_{model}", num(v, 3), v, "results/metrics_by_region.csv", f"PJM Uno's C at 5 years, {model}")

    r = by_region.loc[("ERCOT", "dt_lgbm", "brier", 3)]
    add("ercot_brier3_diff", num(r["diff"], 3, sign=True), r["diff"], "results/metrics_by_region.csv",
        "ERCOT 3-year Brier, LightGBM − baseline")
    add("ercot_brier3_ci", interval(r["diff_low"], r["diff_high"]), f"{r['diff_low']}–{r['diff_high']}",
        "results/metrics_by_region.csv", "interval of the ERCOT 3-year Brier difference")
    caiso_wins = by_region.xs(("CAISO", "dt_lgbm"), level=["region", "model"])
    caiso_wins = caiso_wins[caiso_wins.index.get_level_values("metric").isin(["uno_c", "brier"])]["beats"].astype(bool)
    add("caiso_wins", str(int(caiso_wins.sum())), int(caiso_wins.sum()), "results/metrics_by_region.csv",
        "CAISO concordance and Brier comparisons won by LightGBM")

    seven = read("seven_year_check.csv")
    s17 = seven[seven["version"] == "2017 entrants, fully observed"].set_index(["model", "metric"])
    r = s17.loc[("dt_lgbm", "uno_c")]
    add("s7_uno_lgbm", num(r["estimate"], 3), r["estimate"], "results/seven_year_check.csv", "7-year Uno's C, 2017 entrants, LightGBM")
    add("s7_uno_base", num(s17.loc[("baseline", "uno_c"), "estimate"], 3), s17.loc[("baseline", "uno_c"), "estimate"],
        "results/seven_year_check.csv", "7-year Uno's C, 2017 entrants, baseline")
    add("s7_uno_ci", interval(r["diff_low"], r["diff_high"]), f"{r['diff_low']}–{r['diff_high']}", "results/seven_year_check.csv",
        "interval of the 2017-only 7-year difference")

    rob = read("robustness.csv")
    rob = rob[(rob["model"] == "dt_lgbm") & rob["metric"].isin(["uno_c", "brier"])]
    wins = rob.groupby("variant")["beats"].apply(lambda s: int(s.astype(bool).sum()))
    add("rob_main_wins", str(wins["main"]), wins["main"], "results/robustness.csv", "comparisons won, main version")
    small = [v for v in wins.index if "20" in v][0]
    add("rob_small_wins", str(wins[small]), wins[small], "results/robustness.csv", "comparisons won, under 20 MW excluded")
    add("rob_comparisons", str(int(rob.groupby("variant").size().iloc[0])), int(rob.groupby("variant").size().iloc[0]),
        "results/robustness.csv", "comparisons per variant")

    abl = read("ablation.csv").set_index(["model", "metric", "horizon"])
    for model, key in [("with_post_entry", "abl_post"), ("entry_only", "abl_entry")]:
        add(key, num(abl.loc[(model, "auc", 5), "estimate"], 3), abl.loc[(model, "auc", 5), "estimate"], "results/ablation.csv",
            f"5-year AUC, {model}, CAISO and ERCOT")

    loio = read("loio.csv")
    l5 = loio[(loio["horizon"] == 5) & (loio["metric"] == "auc") & (loio["model"] == "loio_lgbm")].set_index("held_out")
    for region in ["ERCOT", "CAISO"]:
        add(f"loio_pred_{region}", pct(l5.loc[region, "mean_predicted"]), l5.loc[region, "mean_predicted"], "results/loio.csv",
            f"{region} mean 5-year prediction when held out")
        add(f"loio_obs_{region}", pct(l5.loc[region, "observed"]), l5.loc[region, "observed"], "results/loio.csv",
            f"{region} observed 5-year")

    tb = read("trackB_test_by_region.csv")
    outside = int((~tb["lgbm_cal_inside"].astype(bool)).sum())
    add("tb_regions_missed", str(outside), outside, "results/trackB_test_by_region.csv", "Track B regions whose level is missed")
    add("tb_regions", str(len(tb)), len(tb), "results/trackB_test_by_region.csv", "Track B regions")


def explanation():
    """SHAP, partial dependence, sanity checks, ranking book and worked examples (notebook 06 (part C))."""
    shap = read("shap_values.csv")
    cols = [c for c in shap.columns if c.startswith("shap_")]
    mean_abs = (100 * shap[cols].abs().mean()).sort_values(ascending=False)
    for col in cols:
        add(f"mean_abs_{col}", num(mean_abs[col], 2), mean_abs[col], "results/shap_values.csv", f"mean |SHAP| of {col}, points")
    add("shap_features", str(len(cols)), len(cols), "results/shap_values.csv", "features the models use")
    add("shap_n", str(len(shap)), len(shap), "results/shap_values.csv", "test requests explained")
    add("shap_background", "100", 100, "docs/decisions.md #33", "background test requests for SHAP")

    pd_ = read("partial_dependence.csv")
    size = pd_[pd_["feature"] == "size_mw"].copy()
    size["value"] = size["value"].astype(float)
    for mw in [3, 1000]:
        add(f"pd_size_point_{mw}", f"{mw:,}", mw, "notebooks/06_evaluation_record.ipynb", "size at which partial dependence is quoted, MW")
        near = size.assign(gap=(np.log(size["value"]) - np.log(mw)).abs()).sort_values("gap").groupby("region").first()["p"]
        add(f"pd_size_ercot_{mw}", pct(near["ERCOT"]), near["ERCOT"], "results/partial_dependence.csv",
            f"ERCOT mean P(operation within 5 years) near {mw} MW")
    step = size[size["value"].isin([config.FERC_SIZE_STEP_MW - 0.01, config.FERC_SIZE_STEP_MW])].pivot(
        index="region", columns="value", values="p")
    for region in config.TRACK_A_REGIONS:
        jump = 100 * (step.loc[region].iloc[1] - step.loc[region].iloc[0])
        add(f"pd_step_{region}", num(jump, 1, sign=True), jump, "results/partial_dependence.csv", f"{region} change at 20 MW, points")
    region_pd = pd_[pd_["feature"] == "region"].set_index("level")["p"]
    for region in config.TRACK_A_REGIONS:
        add(f"pd_region_{region}", pct(region_pd[region]), region_pd[region], "results/partial_dependence.csv",
            f"mean prediction with every test request moved to {region}")
    tech = pd_[pd_["feature"] == "tech"].groupby("level")["p"].mean()
    for level in ["Gas", "Solar"]:
        add(f"pd_tech_{level}", pct(tech[level]), tech[level], "results/partial_dependence.csv", f"{level}, mean of three regions")

    sanity = read("sanity_checks.csv")
    rec = int(sanity["recovered"].astype(bool).sum())
    add("sanity_recovered", str(rec), rec, "results/sanity_checks.csv", "outside facts recovered")
    add("sanity_total", str(len(sanity)), len(sanity), "results/sanity_checks.csv", "outside facts checked")

    book = read("ranking_table.csv")
    add("book_n", str(len(book)), len(book), "results/ranking_table.csv", "requests in the ranking book")
    expected, base = book["p_operation_5yr"].sum(), book["baseline_p_operation_5yr"].sum()
    add("book_expected", num(expected, 1), expected, "results/ranking_table.csv", "operations expected by the model")
    add("book_expected_base", num(base, 1), base, "results/ranking_table.csv", "operations expected by the baseline")
    # Exact distribution of the number of operations if each request succeeds independently with its predicted
    # probability (Poisson-binomial), so the 90% range does not depend on a simulation seed.
    dist = np.array([1.0])
    for p in book["p_operation_5yr"]:
        dist = np.convolve(dist, [1 - p, p])
    cdf = np.cumsum(dist)
    add("book_range_level", "90%", 0.90, "src/report_numbers.py", "level of the range of operations in the book")
    low, high = int(np.searchsorted(cdf, 0.05)), int(np.searchsorted(cdf, 0.95))
    add("book_range_low", str(low), low, "results/ranking_table.csv", "5th percentile of operations")
    add("book_range_high", str(high), high, "results/ranking_table.csv", "95th percentile of operations")
    observed = int((book["status_after_5yr"] == "operated").sum())
    add("book_observed", str(observed), observed, "results/ranking_table.csv", "operations observed within 5 years")
    ranks = sorted(book.loc[book["status_after_5yr"] == "operated", "model_rank"].astype(int))
    for i, r in enumerate(ranks):
        add(f"book_operated_rank_{i + 1}", str(r), r, "results/ranking_table.csv", "model rank of an operating request")

    ex = read("worked_examples.csv")
    for _, r in ex.iterrows():
        tag = {"ranked highest": "top", "moved up most vs the baseline": "moved", "ranked lowest": "bottom"}[r["example"]]
        for h in config.HORIZONS:
            add(f"ex_{tag}_p{h}", pct(r[f"p_operation_{h}yr"], 0), r[f"p_operation_{h}yr"], "results/worked_examples.csv",
                f"{r['example']}: P(operation within {h} years)")
        add(f"ex_{tag}_base", pct(r["baseline_p_operation_5yr"], 0), r["baseline_p_operation_5yr"], "results/worked_examples.csv",
            f"{r['example']}: baseline 5-year")
        add(f"ex_{tag}_mw", f"{r['mw']:,.0f}" if r["mw"] >= 1 else f"{r['mw']:.1f}", r["mw"], "results/worked_examples.csv",
            f"{r['example']}: MW")
        add(f"ex_{tag}_rank", str(int(r["model_rank"])), r["model_rank"], "results/worked_examples.csv", f"{r['example']}: model rank")
        add(f"ex_{tag}_brank", f"{r['baseline_rank']:g}", r["baseline_rank"], "results/worked_examples.csv",
            f"{r['example']}: baseline rank")
        add(f"ex_{tag}_years", num(r["expected_years_if_built"], 1), r["expected_years_if_built"], "results/worked_examples.csv",
            f"{r['example']}: expected years if built")
        for k in [1, 2]:
            add(f"ex_{tag}_driver{k}", r[f"driver_{k}"], r[f"driver_{k}"], "results/worked_examples.csv", f"{r['example']}: driver {k}")


def posthoc():
    """The post-hoc analysis of notebook 06 (part B) (decision #34)."""
    choice = read("posthoc_choice.json")
    briers = choice["mean_brier_2016"]
    add("ph_brier_min", num(min(briers.values()), 4), min(briers.values()), "results/posthoc_choice.json", "lowest 2016 mean Brier")
    add("ph_brier_max", num(max(briers.values()), 4), max(briers.values()), "results/posthoc_choice.json", "highest 2016 mean Brier")
    add("ph_candidates", str(len(briers)), len(briers), "results/posthoc_choice.json", "candidates compared")

    val = read("posthoc_validation_2016.csv")
    paired = val[(val["metric"] == "brier") & val["diff"].notna()]
    include0 = int(((paired["diff_low"] <= 0) & (paired["diff_high"] >= 0)).sum())
    add("ph_include0", str(include0), include0, "results/posthoc_validation_2016.csv", "2016 paired Brier intervals including 0")
    add("ph_paired", str(len(paired)), len(paired), "results/posthoc_validation_2016.csv", "2016 paired Brier comparisons")

    crit = read("posthoc_criteria.csv")
    for status, key in [("post-hoc", "ph_pass"), ("registered (notebook 08)", "ph_reg_pass")]:  # the status text as results/posthoc_criteria.csv spells it
        part = crit[crit["status"] == status]
        add(key, str(int((part["result"] == "PASS").sum())), int((part["result"] == "PASS").sum()),
            "results/posthoc_criteria.csv", f"Track A lines passed, {status}")
    add("ph_lines", str(int((crit["status"] == "post-hoc").sum())), int((crit["status"] == "post-hoc").sum()),
        "results/posthoc_criteria.csv", "Track A criterion lines")


# ---------------------------------------------------------------------------
# v3: the portfolio layer (notebook 01 part C, notebook 04 parts D–K, notebooks 07 and 09)
# ---------------------------------------------------------------------------

def v3_data():
    """The 2026 LBNL file beside the frozen one, and the milestones (notebook 01 part C and notebook 04 part I)."""
    recon = read("lbnl_2026_reconciliation.csv").set_index("region")
    add("e26_rows", "38,201", 38201, "notebooks/01_problem_and_data.ipynb", "rows of the 2026 edition, raw")
    add("e26_found", pct(recon.loc["all", "share_found"]), recon.loc["all", "share_found"], "results/lbnl_2026_reconciliation.csv",
        "2025 requests found in 2026")
    add("e26_found_pjm", pct(recon.loc["PJM", "share_found"]), recon.loc["PJM", "share_found"], "results/lbnl_2026_reconciliation.csv",
        "PJM requests found in 2026")
    add("e26_new", f"{int(recon.loc['all', 'new_in_2026']):,}", recon.loc["all", "new_in_2026"], "results/lbnl_2026_reconciliation.csv", "rows new in 2026")
    trans = read("lbnl_2026_status_transitions.csv").set_index("q_status_2025")
    for status in ["active", "withdrawn", "operational", "suspended"]:
        v = int(trans.loc["active", status])
        add(f"e26_active_to_{status}", f"{v:,}", v, "results/lbnl_2026_status_transitions.csv", f"active at end-2024 → {status} in 2026")
    add("e26_active_total", f"{int(trans.loc['active'].sum()):,}", int(trans.loc["active"].sum()), "results/lbnl_2026_status_transitions.csv",
        "requests active at end-2024 found in 2026")
    add("e26_wd_to_op", str(int(trans.loc["withdrawn", "operational"])), int(trans.loc["withdrawn", "operational"]),
        "results/lbnl_2026_status_transitions.csv", "withdrawn → operational")
    add("e26_op_to_active", str(int(trans.loc["operational", "active"])), int(trans.loc["operational", "active"]),
        "results/lbnl_2026_status_transitions.csv", "operational → active")
    cov = read("lbnl_2026_date_coverage.csv").set_index(["region", "edition"])
    for region in ["MISO", "SPP", "NYISO", "ERCOT", "CAISO", "PJM"]:
        for edition in [2025, 2026]:
            for what, column in [("on", "on_date_share"), ("wd", "wd_date_share")]:
                v = cov.loc[(region, edition), column]
                add(f"cov_{region.lower().replace('-', '')}_{what}_{edition}", pct(v, 0), v, "results/lbnl_2026_date_coverage.csv",
                    f"{region} {edition}: share of {'operational' if what == 'on' else 'withdrawn'} rows with a date")
    early = read("early_incidence_2020_2022.csv")
    for year in [2020, 2021, 2022]:
        r = early[(early["entry_year"] == year) & (early["horizon"] == 2) & (early["edition"] == 2026) & (early["region"] == "CAISO+ERCOT+PJM")].iloc[0]
        add(f"early2_{year}", pct(r["observed"]), r["observed"], "results/early_incidence_2020_2022.csv", f"{year} entrants: 2-year incidence, 2026 edition")
        add(f"early2_{year}_ops", str(int(r["operations"])), int(r["operations"]), "results/early_incidence_2020_2022.csv", f"{year} entrants: operations within 2 years")
    ms = read("milestone_coverage.csv").set_index("region")
    add("ms_dated", f"{int(ms.loc['all', 'agreement_inside_queue_n']):,}", int(ms.loc["all", "agreement_inside_queue_n"]),
        "results/milestone_coverage.csv", "requests with an agreement dated inside the queue time")
    add("ms_share", pct(ms.loc["all", "agreement_inside_queue"], 0), ms.loc["all", "agreement_inside_queue"], "results/milestone_coverage.csv",
        "share of Track A with a dated agreement inside the queue time")
    for region in config.TRACK_A_REGIONS:
        add(f"ms_share_{region.lower()}", pct(ms.loc[region, "agreement_inside_queue"], 1 if region == "PJM" else 0),
            ms.loc[region, "agreement_inside_queue"], "results/milestone_coverage.csv", f"{region}: dated agreement inside the queue time")
    ia = read("ia_date_agreement.csv").set_index(ia_key := read("ia_date_agreement.csv").columns[0])
    add("ia_2025", f"{int(ia.loc['requests with an agreement date in 2025', 'count']):,}", int(ia.loc["requests with an agreement date in 2025", "count"]),
        "results/ia_date_agreement.csv", "agreement dates in the 2025 file")
    add("ia_2026", f"{int(ia.loc['in 2026', 'count']):,}", int(ia.loc["in 2026", "count"]), "results/ia_date_agreement.csv", "agreement dates in the 2026 file")
    add("ia_same_day", f"{int(ia.loc['same day', 'count']):,}", int(ia.loc["same day", "count"]), "results/ia_date_agreement.csv", "shared dates equal")
    add("ia_both", f"{int(ia.loc['in both', 'count']):,}", int(ia.loc["in both", "count"]), "results/ia_date_agreement.csv", "dated in both editions")
    join = read("iso_join_rates.csv").set_index("iso")
    add("caiso_join", pct(join.loc["CAISO", "share_found"], 0), join.loc["CAISO", "share_found"], "results/iso_join_rates.csv", "CAISO LBNL requests found in the ISO report")
    add("caiso_join_test", pct(join.loc["CAISO", "share_found_2017_2019"], 0), join.loc["CAISO", "share_found_2017_2019"], "results/iso_join_rates.csv",
        "CAISO 2017–2019 entrants found in the ISO report")
    add("caiso_iso_rows", f"{int(join.loc['CAISO', 'rows_in_iso_file']):,}", int(join.loc["CAISO", "rows_in_iso_file"]), "results/iso_join_rates.csv", "rows in CAISO's queue report")


def v3_fair_baseline():
    """Notebook 11: the fair baseline, the utility-scale cohort and the variant choice."""
    sizes = read("sample_sizes_v2.csv").set_index(read("sample_sizes_v2.csv").columns[0])
    add("large_n", f"{int(sizes.loc['≥ 20 MW', 'requests']):,}", int(sizes.loc["≥ 20 MW", "requests"]), "results/sample_sizes_v2.csv", "test requests ≥ 20 MW")
    add("large_share", pct(sizes.loc["≥ 20 MW", "share of test requests"], 0), sizes.loc["≥ 20 MW", "share of test requests"], "results/sample_sizes_v2.csv",
        "share of test requests ≥ 20 MW")
    add("large_mw_share", pct(sizes.loc["≥ 20 MW", "share of test MW"]), sizes.loc["≥ 20 MW", "share of test MW"], "results/sample_sizes_v2.csv",
        "share of test MW ≥ 20 MW")
    add("large_ops", str(int(sizes.loc["≥ 20 MW", "operations by 5 years"])), int(sizes.loc["≥ 20 MW", "operations by 5 years"]),
        "results/sample_sizes_v2.csv", "operations within 5 years, ≥ 20 MW")
    add("small_n", str(int(sizes.loc["< 20 MW", "requests"])), int(sizes.loc["< 20 MW", "requests"]), "results/sample_sizes_v2.csv", "test requests < 20 MW")
    add("small_ops", str(int(sizes.loc["< 20 MW", "operations by 5 years"])), int(sizes.loc["< 20 MW", "operations by 5 years"]),
        "results/sample_sizes_v2.csv", "operations within 5 years, < 20 MW")
    cells = read("fair_baseline_cells.csv")
    add("fb_cells", str(len(cells)), len(cells), "results/fair_baseline_cells.csv", "region × technology × size cells")
    add("fb_cells_used", str(int(cells["used"].sum())), int(cells["used"].sum()), "results/fair_baseline_cells.csv", "cells with ≥ 50 requests")
    pjm_gas = cells[(cells["region"] == "PJM") & (cells["tech"] == "Gas") & cells["used"]]["p_operation_5"]
    add("fb_pjm_gas_min", pct(pjm_gas.min(), 0), pjm_gas.min(), "results/fair_baseline_cells.csv", "PJM gas: lowest size-cell 5-year completion")
    add("fb_pjm_gas_max", pct(pjm_gas.max(), 0), pjm_gas.max(), "results/fair_baseline_cells.csv", "PJM gas: highest size-cell 5-year completion")
    add("fb_pjm_gas_range", str(int(round(100 * (pjm_gas.max() - pjm_gas.min())))), pjm_gas.max() - pjm_gas.min(), "results/fair_baseline_cells.csv",
        "PJM gas: range across size cells, points")
    choice = read("variant_choice_2016.csv").set_index("candidate")
    add("var_k0", num(choice.loc["K0 LightGBM, yearly congestion", "log_loss_2016_large"]), choice.loc["K0 LightGBM, yearly congestion", "log_loss_2016_large"],
        "results/variant_choice_2016.csv", "K0 2016 log loss, ≥ 20 MW rows")
    add("var_k1", num(choice.loc["K1 LightGBM, entry congestion", "log_loss_2016_large"]), choice.loc["K1 LightGBM, entry congestion", "log_loss_2016_large"],
        "results/variant_choice_2016.csv", "K1 2016 log loss, ≥ 20 MW rows")
    add("var_k3", num(choice.loc["K3 LightGBM, entry congestion, monotone in MW", "log_loss_2016_large"]),
        choice.loc["K3 LightGBM, entry congestion, monotone in MW", "log_loss_2016_large"], "results/variant_choice_2016.csv", "K3 2016 log loss")
    add("var_candidates", str(len(choice)), len(choice), "results/variant_choice_2016.csv", "candidates compared")
    m = read("metrics_v2.csv")
    chosen = read("variant_chosen.json")["chosen"]
    for cohort, tag in [("≥ 20 MW", "large"), ("< 20 MW", "small"), ("all", "all")]:
        for ref, rtag in [("fair_baseline", "fair"), ("baseline", "v1")]:
            part = m[(m["cohort"] == cohort) & (m["reference"] == ref) & (m["model"] == chosen) & m["metric"].isin(["uno_c", "brier"])]
            wins = int(part["beats"].fillna(False).astype(bool).sum())
            add(f"wins_{tag}_{rtag}", str(wins), wins, "results/metrics_v2.csv", f"{cohort}: wins of the v2 model vs the {rtag} baseline (of 6)")
    fair_vs_v1 = m[(m["cohort"] == "≥ 20 MW") & (m["reference"] == "baseline") & (m["model"] == "fair_baseline") & m["metric"].isin(["uno_c", "brier"])]
    add("wins_large_fair_vs_v1", str(int(fair_vs_v1["beats"].fillna(False).astype(bool).sum())), int(fair_vs_v1["beats"].fillna(False).astype(bool).sum()),
        "results/metrics_v2.csv", "≥ 20 MW: wins of the fair baseline vs the v1 baseline")
    for h in [3, 5]:
        for model, tag in [(chosen, "v2"), ("fair_baseline", "fair")]:
            r = m[(m["cohort"] == "≥ 20 MW") & (m["reference"] == "baseline") & (m["model"] == model) & (m["metric"] == "uno_c") & (m["horizon"] == h)].iloc[0]
            add(f"c_large_{tag}_{h}", num(r["estimate"]), r["estimate"], "results/metrics_v2.csv", f"≥ 20 MW: Uno's C of {tag} at {h} years")
        r = m[(m["cohort"] == "< 20 MW") & (m["reference"] == "baseline") & (m["model"] == chosen) & (m["metric"] == "uno_c") & (m["horizon"] == h)].iloc[0]
        add(f"c_small_v2_{h}", num(r["estimate"]), r["estimate"], "results/metrics_v2.csv", f"< 20 MW: Uno's C of v2 at {h} years")
        r = m[(m["cohort"] == "< 20 MW") & (m["reference"] == "baseline") & (m["model"] == "fair_baseline") & (m["metric"] == "uno_c") & (m["horizon"] == h)].iloc[0]
        add(f"c_small_fair_{h}", num(r["estimate"]), r["estimate"], "results/metrics_v2.csv", f"< 20 MW: Uno's C of the fair baseline at {h} years")
    mono = read("size_check_monotone.csv").set_index("size_regime")
    add("obs5_lt5", pct(mono.loc["<5", "observed (AJ)"], 0), mono.loc["<5", "observed (AJ)"], "results/size_check_monotone.csv", "observed 5-year completion, < 5 MW")
    add("obs5_ge500", pct(mono.loc["≥500", "observed (AJ)"], 0), mono.loc["≥500", "observed (AJ)"], "results/size_check_monotone.csv", "observed 5-year completion, ≥ 500 MW")


def v3_level():
    """Notebook 12: drift and its repair."""
    d = read("drift_by_cohort.csv")
    for year in [2017, 2018, 2019]:
        r = d[(d["cohort"] == "≥ 20 MW") & (d["horizon"] == 5) & (d["entry_year"] == year)].iloc[0]
        add(f"lv_obs5_{year}", pct(r["observed"]), r["observed"], "results/drift_by_cohort.csv", f"{year} entrants ≥ 20 MW: observed 5-year completion")
        add(f"lv_v2_5_{year}", pct(r["v2"]), r["v2"], "results/drift_by_cohort.csv", f"{year} entrants ≥ 20 MW: v2 mean prediction at 5 years")
    h = read("drift_hazards_by_cohort.csv").set_index("q_year")
    for year in [2013, 2016, 2018, 2019]:
        add(f"hz_op_{year}", pct(h.loc[year, "h_operation"]), h.loc[year, "h_operation"], "results/drift_hazards_by_cohort.csv", f"{year} entrants: operation hazard, years 1–3")
        add(f"hz_wd_{year}", pct(h.loc[year, "h_withdrawal"], 0), h.loc[year, "h_withdrawal"], "results/drift_hazards_by_cohort.csv", f"{year} entrants: withdrawal hazard, years 1–3")
    lm = read("level_repair_metrics.csv").set_index(["cohort", "horizon", "model", "metric"])
    for h_ in [3, 5]:
        for model, tag in [("v2 raw", "raw"), ("v2 recalibrated", "rec"), ("K1 logit (trend)", "logit"), ("fair baseline", "fair")]:
            r = lm.loc[("2018–2019, ≥ 20 MW", h_, model, "intercept")]
            add(f"int_{tag}_{h_}", num(r["estimate"], 2, True), r["estimate"], "results/level_repair_metrics.csv", f"2018–2019 ≥ 20 MW: intercept of {model} at {h_} years")
            add(f"int_{tag}_{h_}_iv", interval(r["low"], r["high"], 2), (r["low"], r["high"]), "results/level_repair_metrics.csv", "its interval")
            s = lm.loc[("2018–2019, ≥ 20 MW", h_, model, "slope")]
            add(f"slope_{tag}_{h_}", num(s["estimate"], 2), s["estimate"], "results/level_repair_metrics.csv", f"2018–2019 ≥ 20 MW: slope of {model} at {h_} years")
    e = read("early_hazards_2020_2022.csv")
    for year in [2020, 2021, 2022]:
        r = e[(e["entry_year"] == year) & (e["horizon"] == 2) & (e["edition"] == 2026)].iloc[0]
        add(f"eh_pred2_{year}", pct(r["predicted"]), r["predicted"], "results/early_hazards_2020_2022.csv", f"{year} entrants: predicted 2-year incidence")
    add("eh_intercept_needed", num(e["intercept_needed_2yr_2025_edition"].iloc[0], 2), e["intercept_needed_2yr_2025_edition"].iloc[0],
        "results/early_hazards_2020_2022.csv", "intercept that would close the 2-year gap")
    rec = read("recalibration.csv")
    r = rec[(rec["scored_year"] == 2019) & (rec["region"] == "PJM") & (rec["horizon"] == 5)].iloc[0]
    add("rec_2019_pjm", num(r["intercept"], 2, True), r["intercept"], "results/recalibration.csv", "2019 PJM 5-year intercept from the 2018 cohort")


def v3_landmark():
    """Notebook 14: the landmark models."""
    cov = read("landmark_coverage.csv").set_index("landmark")
    for lm, tag in [("0", "l0"), ("1", "l1"), ("2", "l2"), ("agreement", "lia")]:
        r = cov.loc[lm]
        add(f"rs_{tag}", f"{int(r['requests']):,}", int(r["requests"]), "results/landmark_coverage.csv", f"risk set at landmark {lm}")
        add(f"rs_{tag}_ops3", str(int(r["operations within 3"])), int(r["operations within 3"]), "results/landmark_coverage.csv", f"operations within 3 years of landmark {lm}")
        add(f"rs_{tag}_wd3", str(int(r["withdrawals within 3"])), int(r["withdrawals within 3"]), "results/landmark_coverage.csv", f"withdrawals within 3 years of landmark {lm}")
    m = read("landmark_metrics.csv")
    m["landmark"] = m["landmark"].astype(str)
    for lm, tag in [("1", "l1"), ("2", "l2"), ("agreement", "lia")]:
        for model, mtag in [("entry model", "entry"), ("both updated", "both"), ("agreement updated", "ia"), ("congestion updated", "cong"), ("fair baseline", "fair")]:
            for metric in ["uno_c", "brier"]:
                r = m[(m["landmark"] == lm) & (m["reference"] == "entry model") & (m["model"] == model) & (m["metric"] == metric) & (m["horizon_after"] == 3)].iloc[0]
                add(f"lm_{tag}_{mtag}_{metric}", num(r["estimate"]), r["estimate"], "results/landmark_metrics.csv", f"landmark {lm}: {metric} of {model}, 3 years after")
                if model != "entry model":
                    add(f"lm_{tag}_{mtag}_{metric}_diff", num(r["diff"], 3, True), r["diff"], "results/landmark_metrics.csv", "paired difference vs the entry model")
                    add(f"lm_{tag}_{mtag}_{metric}_iv", interval(r["diff_low"], r["diff_high"]), (r["diff_low"], r["diff_high"]), "results/landmark_metrics.csv", "its interval")
        for model, mtag in [("entry model", "entry"), ("both updated", "both")]:
            r = m[(m["landmark"] == lm) & (m["reference"] == "entry model") & (m["model"] == model) & (m["metric"] == "intercept") & (m["horizon_after"] == 3)].iloc[0]
            add(f"lm_{tag}_{mtag}_int", num(r["estimate"], 2, True), r["estimate"], "results/landmark_metrics.csv", f"landmark {lm}: intercept of {model}")
            s = m[(m["landmark"] == lm) & (m["reference"] == "entry model") & (m["model"] == model) & (m["metric"] == "slope") & (m["horizon_after"] == 3)].iloc[0]
            add(f"lm_{tag}_{mtag}_slope", num(s["estimate"], 2), s["estimate"], "results/landmark_metrics.csv", f"landmark {lm}: slope of {model}")
    r = m[(m["landmark"] == "0") & (m["reference"] == "entry model") & (m["model"] == "agreement updated") & (m["metric"] == "intercept") & (m["horizon_after"] == 3)].iloc[0]
    add("lm_l0_ia_int", num(r["estimate"], 2, True), r["estimate"], "results/landmark_metrics.csv", "entry landmark: intercept with the agreement flag in the fit")
    r = m[(m["landmark"] == "0") & (m["reference"] == "entry model") & (m["model"] == "entry model") & (m["metric"] == "intercept") & (m["horizon_after"] == 3)].iloc[0]
    add("lm_l0_entry_int", num(r["estimate"], 2, True), r["estimate"], "results/landmark_metrics.csv", "entry landmark: intercept of the entry model")
    wins = m[m["metric"].isin(["uno_c", "brier"]) & (m["reference"] == "entry model") & (m["model"] == "both updated") & (m["landmark"] == "2")]
    add("lm_l2_wins", str(int(wins["beats"].fillna(False).astype(bool).sum())), int(wins["beats"].fillna(False).astype(bool).sum()), "results/landmark_metrics.csv",
        "+2 years: wins of both-updated vs the entry model, of 6")
    checks = read("landmark_checks.csv")
    guard = checks[checks["check"].str.contains("ablation")]["value"].iloc[0]
    add("lm_max_auc", guard.split(" < ")[0], guard, "results/landmark_checks.csv", "highest landmark AUC")
    add("lm_ceiling", guard.split(" < ")[1], guard, "results/landmark_checks.csv", "leakage ablation AUC at 5 years")
    sig = read("landmark_agreement_signal.csv").set_index(["region", "agreement known"])
    for region in ["ERCOT", "CAISO"]:
        for known, tag in [(True, "yes"), (False, "no")]:
            r = sig.loc[(region, known)]
            add(f"sig_{region.lower()}_{tag}", pct(r["observed_3yr"]), r["observed_3yr"], "results/landmark_agreement_signal.csv",
                f"{region}, agreement {'known' if known else 'not known'} at +2 years: observed 3-year completion")
            add(f"sig_{region.lower()}_{tag}_n", str(int(r["requests"])), int(r["requests"]), "results/landmark_agreement_signal.csv", "requests")
    r = sig.loc[("PJM", True)]
    add("sig_pjm_yes_n", str(int(r["requests"])), int(r["requests"]), "results/landmark_agreement_signal.csv", "PJM requests with a known agreement at +2 years")
    r = sig.loc[("PJM", False)]
    add("sig_pjm_no_n", str(int(r["requests"])), int(r["requests"]), "results/landmark_agreement_signal.csv", "PJM requests without")


def v3_value():
    """Notebook 15: the value and cost layer."""
    energy = read("energy_prices.csv").set_index("year")
    for region, years in [("PJM", [2017, 2022, 2025]), ("CAISO", [2017, 2022, 2025]), ("ERCOT", [2017, 2019])]:
        for y in years:
            add(f"ep_{region.lower()}_{y}", f"${energy.loc[y, region]:.1f}", energy.loc[y, region], "results/energy_prices.csv", f"{region} on-peak hub price {y}, $/MWh")
    cap = read("capacity_prices.csv").set_index("year")
    for y in [2018, 2024, 2025, 2026]:
        add(f"cp_pjm_{y}", f"${cap.loc[y, 'PJM']:.0f}", cap.loc[y, "PJM"], "results/capacity_prices.csv", f"PJM capacity revenue {y}, $/kW-year")
    add("cp_caiso", f"${cap.loc[2024, 'CAISO']:.0f}", cap.loc[2024, "CAISO"], "results/capacity_prices.csv", "CAISO capacity price assumption, $/kW-year")
    acc = read("accreditation.csv").set_index(read("accreditation.csv").columns[0])["accreditation"]
    for tech, tag in [("Solar", "solar"), ("Wind", "wind"), ("Battery", "battery"), ("Gas", "gas")]:
        add(f"acc_{tag}", pct(acc[tech], 0), acc[tech], "results/accreditation.csv", f"accreditation, {tech}")
    cf = read("capacity_factors.csv").set_index(["state", "tech"])["capacity_factor"]
    for state in ["TX", "CA", "PA"]:
        for tech in ["Solar", "Wind", "Gas"]:
            add(f"cf_{state.lower()}_{tech.lower()}", num(cf[(state, tech)], 2), cf[(state, tech)], "results/capacity_factors.csv", f"capacity factor, {state} {tech}")
    vt = read("value_table.csv")
    v24 = vt[vt["year"] == 2024].set_index(["region", "tech"])["base"]
    for region, tech in [("PJM", "Gas"), ("PJM", "Wind"), ("PJM", "Solar"), ("CAISO", "Solar"), ("ERCOT", "Solar")]:
        add(f"val_{region.lower()}_{tech.lower()}", f"${v24[(region, tech)] / 1e3:,.0f},000", v24[(region, tech)], "results/value_table.csv",
            f"value per MW-year 2024 base, {region} {tech}")
    costs = read("cost_table.csv").set_index("size_regime")
    add("cost_median_20_100", f"${costs.loc['20–<100', 'cost_per_kw_median']:.0f}", costs.loc["20–<100", "cost_per_kw_median"], "results/cost_table.csv",
        "PJM median interconnection cost, 20–100 MW, $/kW")
    add("cost_median_lt5", f"${costs.loc['<5', 'cost_per_kw_median']:.0f}", costs.loc["<5", "cost_per_kw_median"], "results/cost_table.csv", "< 5 MW")
    add("cost_median_ge500", f"${costs.loc['≥500', 'cost_per_kw_median']:.0f}", costs.loc["≥500", "cost_per_kw_median"], "results/cost_table.csv", "≥ 500 MW")
    add("cost_projects", f"{int(costs['n_projects'].sum()):,}", int(costs["n_projects"].sum()), "results/cost_table.csv", "PJM cost estimates")
    path = read("expected_mw_online.csv").set_index("years_after_entry")
    add("mw_exp5_raw", f"{path.loc[5, 'expected_mw_raw'] / 1e3:.1f}", path.loc[5, "expected_mw_raw"], "results/expected_mw_online.csv", "expected GW online within 5 years, raw")
    add("mw_exp5_rec", f"{path.loc[5, 'expected_mw_recalibrated'] / 1e3:.1f}", path.loc[5, "expected_mw_recalibrated"], "results/expected_mw_online.csv",
        "expected GW online within 5 years, level repaired")
    add("mw_real5", f"{path.loc[5, 'realised_mw_by_end_2024'] / 1e3:.1f}", path.loc[5, "realised_mw_by_end_2024"], "results/expected_mw_online.csv",
        "realised GW online within 5 years")
    over_raw = path.loc[5, "expected_mw_raw"] / path.loc[5, "realised_mw_by_end_2024"] - 1
    over_rec = path.loc[5, "expected_mw_recalibrated"] / path.loc[5, "realised_mw_by_end_2024"] - 1
    add("mw_over_raw", pct(over_raw, 0), over_raw, "results/expected_mw_online.csv", "raw over-expectation of MW online, 5 years")
    add("mw_over_rec", pct(over_rec, 0), over_rec, "results/expected_mw_online.csv", "repaired over-expectation")
    ev = read("expected_value_by_request.csv")
    add("cohort_mw", f"{ev['mw'].sum():,.0f}", ev["mw"].sum(), "results/expected_value_by_request.csv", "test cohort MW")
    add("ev_median", f"${ev['value_recalibrated_base'].median() / 1e6:.1f}", ev["value_recalibrated_base"].median(), "results/expected_value_by_request.csv",
        "median expected value per request, repaired base, $M")
    sens = read("value_sensitivity.csv").set_index(read("value_sensitivity.csv").columns[0])
    corr_min = sens.drop(columns=["top-decile overlap with recalibrated/base"]).min().min()
    add("sens_spearman_min", num(corr_min, 2), corr_min, "results/value_sensitivity.csv", "lowest Spearman correlation across value cases")
    add("sens_overlap_low", pct(sens.loc["recalibrated / low", "top-decile overlap with recalibrated/base"], 0),
        sens.loc["recalibrated / low", "top-decile overlap with recalibrated/base"], "results/value_sensitivity.csv", "top-decile overlap, low vs base")
    assumptions = read("value_assumptions.csv")
    add("n_assumptions", str(len(assumptions)), len(assumptions), "results/value_assumptions.csv", "rows in the assumption table")


def v3_miso_spp():
    """Notebook 19: MISO and SPP on the 2026 file."""
    s = read("miso_spp_samples.csv").set_index("region")
    for region in ["MISO", "SPP"]:
        tag = region.lower()
        add(f"ms_{tag}_usable", f"{int(s.loc[region, 'usable requests']):,}", int(s.loc[region, "usable requests"]), "results/miso_spp_samples.csv", f"{region} usable requests")
        add(f"ms_{tag}_test", str(int(s.loc[region, "test (2017–2019)"])), int(s.loc[region, "test (2017–2019)"]), "results/miso_spp_samples.csv", f"{region} test requests")
        add(f"ms_{tag}_ops", str(int(s.loc[region, "test operations within 5 years"])), int(s.loc[region, "test operations within 5 years"]),
            "results/miso_spp_samples.csv", f"{region} test operations within 5 years")
    scored = read("success_criteria_v3_scored.csv")
    add("v3_lines", str(len(scored)), len(scored), "results/success_criteria_v3_scored.csv", "registered v3 lines")
    add("v3_pass", str(int((scored["result"] == "PASS").sum())), int((scored["result"] == "PASS").sum()), "results/success_criteria_v3_scored.csv", "v3 lines passed")
    r = scored[(scored["region"] == "MISO") & (scored["metric"] == "uno_c") & (scored["horizon"] == 5)].iloc[0]
    add("v3_miso_c5", num(r["estimate"]), r["estimate"], "results/success_criteria_v3_scored.csv", "MISO LightGBM Uno's C at 5 years")
    add("v3_miso_c5_fair", num(r["benchmark"]), r["benchmark"], "results/success_criteria_v3_scored.csv", "MISO fair baseline Uno's C at 5 years")
    add("v3_miso_c5_diff", num(r["diff"], 3, True), r["diff"], "results/success_criteria_v3_scored.csv", "paired difference")
    add("v3_miso_c5_iv", interval(r["diff_low"], r["diff_high"]), (r["diff_low"], r["diff_high"]), "results/success_criteria_v3_scored.csv", "its interval")


def v3_portfolio():
    """Notebooks 16, 17 and 18: the book, the levers and the v2 verdict."""
    cards = read("scorecards.csv")
    add("p16_book_n", str(len(cards)), len(cards), "results/scorecards.csv", "requests in the sample book")
    add("p16_book_mw", f"{cards['mw'].sum():,.0f}", cards["mw"].sum(), "results/scorecards.csv", "sample book MW")
    add("p16_book_exp5", f"{cards['expected_mw_online_5yr'].sum():,.0f}", cards["expected_mw_online_5yr"].sum(), "results/scorecards.csv",
        "sample book expected MW online within 5 years")
    add("p16_book_operated", str(int((cards["status_by_end_2024"] == "operated").sum())), int((cards["status_by_end_2024"] == "operated").sum()),
        "results/scorecards.csv", "sample book requests that operated")
    wi = read("whatifs.csv")
    for column, tag in [("cut to 19.9 MW (if ≥ 20 MW)", "cut"), ("add storage (if solar)", "storage"), ("enter a 25% quieter queue", "quiet")]:
        add(f"wi_{tag}", num(100 * wi[column].mean(), 1, True), 100 * wi[column].mean(), "results/whatifs.csv", f"mean what-if change, {column}, points")
        add(f"wi_{tag}_n", str(int(wi[column].notna().sum())), int(wi[column].notna().sum()), "results/whatifs.csv", "requests the what-if applies to")
    rho = read("book_rho.csv").iloc[0]
    add("rho", num(rho["rho"], 3), rho["rho"], "results/book_rho.csv", "latent correlation of the copula")
    add("rho_groups", str(int(rho["groups"])), int(rho["groups"]), "results/book_rho.csv", "region × year groups behind rho")
    sim = read("book_simulation.csv").set_index("years_after_entry")
    add("sim_exp5", f"{sim.loc[5, 'expected_mw']:,.0f}", sim.loc[5, "expected_mw"], "results/book_simulation.csv", "sample book expected MW online, 5 years")
    add("sim_p5", f"{sim.loc[5, 'p5']:,.0f}", sim.loc[5, "p5"], "results/book_simulation.csv", "5th percentile")
    add("sim_p95", f"{sim.loc[5, 'p95']:,.0f}", sim.loc[5, "p95"], "results/book_simulation.csv", "95th percentile")
    add("sim_real5", f"{sim.loc[5, 'realised_mw_by_end_2024']:,.0f}", sim.loc[5, "realised_mw_by_end_2024"], "results/book_simulation.csv", "realised MW, 5 years")
    add("sim_miss", pct(sim.loc[5, "p_miss_half_target"], 0), sim.loc[5, "p_miss_half_target"], "results/book_simulation.csv", "P(less than half the expected MW by year 5)")
    choice = read("book_choice.csv").set_index("chooser")
    add("budget", "$20.11M", 20.11e6, "notebooks/09_portfolio.ipynb", "deposit budget (median 25-request 2019 book)")
    for name, tag in [("v2 model, level repaired", "model"), ("fair baseline", "fair"), ("v1 baseline", "v1"), ("random", "random"), ("v2 model, raw", "raw")]:
        r = choice.loc[name]
        add(f"bk_{tag}_n", str(int(r["requests"])), int(r["requests"]), "results/book_choice.csv", f"{name}: requests chosen")
        add(f"bk_{tag}_mw", f"{r['mw']:,.0f}", r["mw"], "results/book_choice.csv", f"{name}: MW chosen")
        add(f"bk_{tag}_exp", f"{r['expected_mw_online_5yr (own curve)']:,.0f}", r["expected_mw_online_5yr (own curve)"], "results/book_choice.csv",
            f"{name}: expected MW online within 5 years")
        add(f"bk_{tag}_real", f"{r['realised_mw_5yr']:,.0f}", r["realised_mw_5yr"], "results/book_choice.csv", f"{name}: realised MW within 5 years")
    for region in config.TRACK_A_REGIONS:
        add(f"bk_model_share_{region.lower()}", pct(choice.loc["v2 model, level repaired", f"share_{region}"], 0),
            choice.loc["v2 model, level repaired", f"share_{region}"], "results/book_choice.csv", f"model book: budget share in {region}")
    bt = read("backtest_books.csv").set_index(["chooser", "metric"])
    r = bt.loc[("v2 model, level repaired", "realised_mw_5yr")]
    add("bt_mw_diff", num(r["diff_vs_fair_baseline"], 0, True), r["diff_vs_fair_baseline"], "results/backtest_books.csv", "C9: paired MW difference")
    add("bt_mw_iv", f"[{num(r['diff_low'], 0, True)}, {num(r['diff_high'], 0, True)}]", (r["diff_low"], r["diff_high"]), "results/backtest_books.csv", "its interval")
    r = bt.loc[("v2 model, level repaired", "realised_value_$M")]
    add("bt_val", f"${r['estimate']:,.0f}", r["estimate"], "results/backtest_books.csv", "model book realised value, $M index")
    add("bt_val_iv", f"[{num(r['diff_low'], 0, True)}, {num(r['diff_high'], 0, True)}]", (r["diff_low"], r["diff_high"]), "results/backtest_books.csv", "C10 interval")
    r = bt.loc[("random", "realised_mw_5yr")]
    add("bt_random_mw", f"{r['estimate']:,.0f}", r["estimate"], "results/backtest_books.csv", "random book realised MW")
    pb = read("backtest_probability_books.csv").set_index(["chooser", "metric"])
    for name, tag in [("v2 model, level repaired", "model"), ("fair baseline", "fair"), ("v1 baseline", "v1"), ("random (≥ 20 MW)", "random")]:
        r = pb.loc[(name, "operated_within_5")]
        add(f"pb_{tag}_ops", str(int(r["estimate"])), r["estimate"], "results/backtest_probability_books.csv", f"probability book, {name}: operated within 5 years of 25")
        m = pb.loc[(name, "realised_mw_5yr")]
        add(f"pb_{tag}_mw", f"{m['estimate']:,.0f}", m["estimate"], "results/backtest_probability_books.csv", f"probability book, {name}: realised MW")
        if name != "fair baseline":
            add(f"pb_{tag}_ops_diff", num(r["diff_vs_fair_baseline"], 0, True), r["diff_vs_fair_baseline"], "results/backtest_probability_books.csv", "paired difference vs the fair baseline, operations")
            add(f"pb_{tag}_ops_iv", f"[{num(r['diff_low'], 0, True)}, {num(r['diff_high'], 0, True)}]", (r["diff_low"], r["diff_high"]), "results/backtest_probability_books.csv", "its interval")
    cov = read("book_coverage.csv").iloc[0]
    add("cov_band_low", f"{cov['band_low']:,.0f}", cov["band_low"], "results/book_coverage.csv", "C11 band, low")
    add("cov_band_high", f"{cov['band_high']:,.0f}", cov["band_high"], "results/book_coverage.csv", "C11 band, high")
    add("cov_expected", f"{cov['expected_mw_5yr']:,.0f}", cov["expected_mw_5yr"], "results/book_coverage.csv", "model book expected MW online, 5 years")
    # notebook 09 (part B)
    cm = read("constraint_map.csv").set_index(["region", "q_year"])
    for region, year in [("PJM", 2012), ("PJM", 2021), ("CAISO", 2012), ("CAISO", 2021), ("ERCOT", 2012), ("ERCOT", 2021)]:
        add(f"cm_gw_{region.lower()}_{year}", f"{cm.loc[(region, year), 'gw_waiting_at_entry']:.0f}", cm.loc[(region, year), "gw_waiting_at_entry"],
            "results/constraint_map.csv", f"{region} {year}: median GW waiting at entry")
        add(f"cm_wd3_{region.lower()}_{year}", pct(cm.loc[(region, year), "withdrawn_within_3"], 0), cm.loc[(region, year), "withdrawn_within_3"],
            "results/constraint_map.csv", f"{region} {year}: withdrawn within 3 years")
    add("cm_op3_pjm_2012", pct(cm.loc[("PJM", 2012), "operated_within_3"]), cm.loc[("PJM", 2012), "operated_within_3"], "results/constraint_map.csv", "PJM 2012: operated within 3 years")
    scen = read("scenarios.csv")
    base = scen.loc[0, "expected_mw_online_5yr"]
    add("scen_base", f"{base:,.0f}", base, "results/scenarios.csv", "sample book expected MW, as modelled")
    fast = scen[scen["scenario"].str.startswith("cluster reform speeds")]
    add("scen_fast_low", f"{fast['expected_mw_online_5yr'].min():,.0f}", fast["expected_mw_online_5yr"].min(), "results/scenarios.csv", "reform scenario, low")
    add("scen_fast_high", f"{fast['expected_mw_online_5yr'].max():,.0f}", fast["expected_mw_online_5yr"].max(), "results/scenarios.csv", "reform scenario, high")
    r = scen[scen["scenario"].str.startswith("reform raises")].iloc[0]
    add("scen_wd", f"{r['expected_mw_online_5yr']:,.0f}", r["expected_mw_online_5yr"], "results/scenarios.csv", "reform raises withdrawals")
    r = scen[scen["scenario"].str.startswith("post-2020")].iloc[0]
    add("scen_level", f"{r['expected_mw_online_5yr']:,.0f}", r["expected_mw_online_5yr"], "results/scenarios.csv", "post-2020 level persists")
    add("scen_level_change", pct(r["change_vs_modelled_5yr"], 0), r["change_vs_modelled_5yr"], "results/scenarios.csv", "its change vs modelled")
    levers = read("levers.csv")
    add("levers_n", str(len(levers)), len(levers), "results/levers.csv", "levers listed")
    add("levers_with_number", str(int(levers["source"].str.contains(".csv").sum())), int(levers["source"].str.contains(".csv").sum()), "results/levers.csv",
        "levers with a number from this project")
    # notebook 06 (part D)
    scored = read("success_criteria_v2_scored.csv")
    add("v2_lines", str(len(scored)), len(scored), "results/success_criteria_v2_scored.csv", "registered v2 lines")
    add("v2_pass", str(int((scored["result"] == "PASS").sum())), int((scored["result"] == "PASS").sum()), "results/success_criteria_v2_scored.csv", "v2 lines passed")
    for cid in ["C6", "C7", "C8", "C9", "C10", "C11", "C12"]:
        part = scored[scored["id"] == cid]
        add(f"v2_{cid.lower()}_pass", f"{int((part['result'] == 'PASS').sum())} of {len(part)}", int((part["result"] == "PASS").sum()),
            "results/success_criteria_v2_scored.csv", f"{cid}: lines passed")


def v3_extras():
    """Numbers the v2 report quotes that the collectors above do not yet carry."""
    add("lbnl26_active_gw", "2,060", 2060, "docs/data_readiness.md (Rand et al., 2026)", "GW waiting at end-2025, LBNL 2026 headline")
    add("clean26_rows", "37,849", 37849, "results/clean_log_2026.csv", "clean rows, 2026 edition")
    add("ia_merged", "1,818", 1818, "results/ia_date_agreement.csv", "requests with an agreement date, editions merged")
    add("caiso_joined_n", "2,218", 2218, "results/iso_join_rates.csv", "CAISO requests joined to the ISO report")
    ms = read("milestone_coverage.csv").set_index("region")
    for region in config.TRACK_A_REGIONS:
        add(f"ms_n_{region.lower()}", str(int(ms.loc[region, "agreement_inside_queue_n"])), int(ms.loc[region, "agreement_inside_queue_n"]),
            "results/milestone_coverage.csv", f"{region}: agreements dated inside the queue time")
    unmatched = read("map_unmatched.csv")
    placed = 1 - float(unmatched.loc[unmatched[unmatched.columns[0]] == "all", "share_unmatched"].iloc[0])
    add("map_placed", pct(placed, 0), placed, "results/map_unmatched.csv", "requests placed on the map")
    track_a = pd.read_parquet(paths.DATA_INTERIM / "trackA.parquet")
    pjm_share = float((track_a["region"] == "PJM").mean())
    add("pjm_share_track_a", pct(pjm_share, 0), pjm_share, "data/interim/trackA.parquet", "PJM share of Track A")
    choice = read("variant_choice_2016.csv").set_index("candidate")
    add("var_k2logit", num(choice.loc["K2 logit, entry congestion, ≥ 20 MW only", "log_loss_2016_large"]),
        choice.loc["K2 logit, entry congestion, ≥ 20 MW only", "log_loss_2016_large"], "results/variant_choice_2016.csv", "K2 logit 2016 log loss")
    add("var_k1logit", num(choice.loc["K1 logit, entry congestion", "log_loss_2016_large"]), choice.loc["K1 logit, entry congestion", "log_loss_2016_large"],
        "results/variant_choice_2016.csv", "K1 logit 2016 log loss")
    energy = read("energy_prices.csv").set_index("year")
    ratio = float((energy.loc[2017:2019, "ERCOT"] / energy.loc[2017:2019, "PJM"]).mean())
    add("ercot_price_ratio", num(ratio, 2), ratio, "results/energy_prices.csv", "ERCOT/PJM on-peak ratio 2017–2019")
    add("caiso_cp_low", "$48", 48, "results/value_assumptions.csv", "CAISO capacity price range, low, $/kW-year")
    add("caiso_cp_high", "$144", 144, "results/value_assumptions.csv", "CAISO capacity price range, high")
    add("study_cost", "$150,000", 150000, "results/value_assumptions.csv", "study cost to the next gate, base")
    costs = read("cost_table.csv")
    add("cost_overall_median", "$61", 61, "notebooks/07_economics.ipynb", "PJM median interconnection cost, $/kW")
    add("whatif_cut_mw", "19.9", 19.9, "notebooks/09_portfolio.ipynb", "what-if size, MW")
    add("whatif_quiet", "25%", 0.25, "notebooks/09_portfolio.ipynb", "what-if congestion cut")
    wi = read("whatifs.csv")
    for column, tag in [("cut to 19.9 MW (if ≥ 20 MW)", "cut"), ("add storage (if solar)", "storage"), ("enter a 25% quieter queue", "quiet")]:
        add(f"wi_{tag}_min", num(100 * wi[column].min(), 1, True), 100 * wi[column].min(), "results/whatifs.csv", f"{column}: minimum, points")
        add(f"wi_{tag}_max", num(100 * wi[column].max(), 1, True), 100 * wi[column].max(), "results/whatifs.csv", f"{column}: maximum, points")
    m = read("landmark_metrics.csv"); m["landmark"] = m["landmark"].astype(str)
    for lm, tag in [("2", "l2"), ("agreement", "lia")]:
        for model, mtag in [("entry model", "entry"), ("both updated", "both"), ("fair baseline", "fair"), ("agreement updated", "ia")]:
            r = m[(m["landmark"] == lm) & (m["reference"] == "entry model") & (m["model"] == model) & (m["metric"] == "uno_c") & (m["horizon_after"] == 3)].iloc[0]
            add(f"lm_{tag}_{mtag}_uno2", num(r["estimate"], 2), r["estimate"], "results/landmark_metrics.csv", f"landmark {lm}: Uno's C of {model}, 2 decimals")
    mbr = read("metrics_by_region.csv")
    for region in config.TRACK_A_REGIONS:
        for model, mtag in [("dt_lgbm", "model"), ("baseline", "v1")]:
            r = mbr[(mbr["region"] == region) & (mbr["model"] == model) & (mbr["metric"] == "uno_c") & (mbr["horizon"] == 5)].iloc[0]
            add(f"region_uno5_{region.lower()}_{mtag}", num(r["estimate"], 2), r["estimate"], "results/metrics_by_region.csv", f"{region}: 5-year Uno's C of {model}")
    d = read("drift_by_cohort_region.csv")
    for region in config.TRACK_A_REGIONS:
        for year in [2017, 2018, 2019]:
            r = d[(d["region"] == region) & (d["horizon"] == 5) & (d["entry_year"] == year)].iloc[0]
            add(f"lv5_{region.lower()}_{year}", pct(r["observed"]), r["observed"], "results/drift_by_cohort_region.csv", f"{region} {year} entrants: observed 5-year completion")
    cm = read("constraint_map.csv")
    for region in config.TRACK_A_REGIONS:
        part = cm[(cm["region"] == region) & cm["observable"]]["median_years_to_agreement"].dropna()
        add(f"cm_ia_{region.lower()}_min", num(part.min(), 1), part.min(), "results/constraint_map.csv", f"{region}: lowest cohort median years to agreement")
        add(f"cm_ia_{region.lower()}_max", num(part.max(), 1), part.max(), "results/constraint_map.csv", f"{region}: highest cohort median years to agreement")
    rho = read("book_rho.csv").iloc[0]
    add("rho_2dp", num(rho["rho"], 2), rho["rho"], "results/book_rho.csv", "rho, 2 decimals")
    add("phi_pct", pct(rho["phi"]), rho["phi"], "results/book_rho.csv", "over-dispersion as a share of the binomial variance")
    shap = read("shap_values.csv")
    for feature in ["state", "size_mw", "tech"]:
        v = float(shap[f"shap_{feature}"].abs().mean() * 100)
        add(f"shap_mean_{feature}_1dp", num(v, 1), v, "results/shap_values.csv", f"mean |SHAP| of {feature}, points, 1 decimal")
    cif = read("cif_horizons.csv")
    for region in config.TRACK_A_REGIONS:
        r = cif[(cif["grouping"] == "region") & (cif["group"] == region) & (cif["time"] == 5.0)].iloc[0]
        add(f"cif5_{region.lower()}_1dp", pct(r["cif_operation"]), r["cif_operation"], "results/cif_horizons.csv", f"{region}: 5-year incidence of operation")
    sim = read("book_simulation.csv").set_index("years_after_entry")
    add("sim_p5_lo", f"{sim.loc[5, 'p5']:,.0f}", sim.loc[5, "p5"], "results/book_simulation.csv", "5th percentile at 5 years")
    log26 = read("clean_log_2026.csv")
    dup = int(log26.loc[log26["rule"] == "R7a", "rows"].iloc[0])
    add("dup_2026", str(dup), dup, "results/clean_log_2026.csv", "appended duplicate rows dropped from the 2026 file")
    milestones = pd.read_parquet(paths.DATA_INTERIM / "milestones.parquet")
    inside = milestones[milestones["ia_inside_queue"]]
    add("ia_median_years", num(inside["ia_years"].median(), 1), inside["ia_years"].median(), "data/interim/milestones.parquet", "median years to agreement")
    for region in config.TRACK_A_REGIONS:
        v = inside.loc[inside["region"] == region, "ia_years"].median()
        add(f"ia_median_years_{region.lower()}", num(v, 1), v, "data/interim/milestones.parquet", f"{region}: median years to agreement")
    cov = read("landmark_coverage.csv").set_index("landmark")
    by_region = eval(cov.loc["agreement", "by region"])
    for region, n_ in by_region.items():
        add(f"rs_lia_{region.lower()}", str(int(n_)), int(n_), "results/landmark_coverage.csv", f"agreement risk set in {region}")
    add("cap_region", "50%", 0.5, "docs/decisions.md #46", "budget share cap per region")
    add("cap_tech", "60%", 0.6, "docs/decisions.md #46", "budget share cap per technology")


def v3_appendix():
    """Every cell of the appendix tables A2, A3, E and F, formatted as the appendix prints them."""
    v2 = read("success_criteria_v2_scored.csv")
    for i, r in v2.iterrows():
        if pd.notna(r["diff"]):
            d3 = 3 if abs(r["estimate"]) < 10 else 0
            for col in ["diff", "diff_low", "diff_high"]:
                add(f"a2_{i}_{col}", num(r[col], d3, True), r[col], "results/success_criteria_v2_scored.csv", f"A2 row {i} {col}")
            for col in ["estimate", "benchmark"]:
                add(f"a2_{i}_{col}", num(r[col], 3) if abs(r["estimate"]) < 10 else f"{r[col]:,.0f}", r[col], "results/success_criteria_v2_scored.csv", f"A2 row {i} {col}")
        elif r["id"] == "C7":
            add(f"a2_{i}_slope", num(r["estimate"], 2), r["estimate"], "results/success_criteria_v2_scored.csv", f"A2 row {i} slope")
            for col in ["benchmark", "diff_low", "diff_high"]:
                add(f"a2_{i}_{col}", num(r[col], 2, True), r[col], "results/success_criteria_v2_scored.csv", f"A2 row {i} {col}")
        elif r["id"] == "C11":
            for col in ["estimate", "benchmark", "diff_low", "diff_high"]:
                add(f"a2_{i}_{col}", f"{r[col]:,.0f}", r[col], "results/success_criteria_v2_scored.csv", f"A2 row {i} {col}")
    v3 = read("success_criteria_v3_scored.csv")
    for i, r in v3.iterrows():
        if r["id"] == "C13":
            for col in ["estimate", "benchmark"]:
                add(f"a3_{i}_{col}", num(r[col]), r[col], "results/success_criteria_v3_scored.csv", f"A3 row {i} {col}")
            for col in ["diff", "diff_low", "diff_high"]:
                add(f"a3_{i}_{col}", num(r[col], 3, True), r[col], "results/success_criteria_v3_scored.csv", f"A3 row {i} {col}")
        else:
            add(f"a3_{i}_estimate", num(r["estimate"], 2), r["estimate"], "results/success_criteria_v3_scored.csv", f"A3 row {i} slope")
            for col in ["diff_low", "diff_high"]:
                add(f"a3_{i}_{col}", num(r[col], 2), r[col], "results/success_criteria_v3_scored.csv", f"A3 row {i} {col}")
    va = read("value_assumptions.csv")
    for i, r in va.iterrows():
        for col in ["value", "low", "high", "source"]:
            add(f"ae_{i}_{col}", str(r[col]).replace("|", "/").replace("nan", ""), str(r[col]), "results/value_assumptions.csv", f"E row {i} {col}")
    lc = read("landmark_coverage.csv")
    for i, r in lc.iterrows():
        add(f"af_{i}_requests", f"{int(r['requests']):,}", int(r["requests"]), "results/landmark_coverage.csv", f"F row {i} requests")
        add(f"af_{i}_large", f"{int(r['≥ 20 MW']):,}", int(r["≥ 20 MW"]), "results/landmark_coverage.csv", f"F row {i} ≥ 20 MW")
        for h in [1, 2, 3]:
            add(f"af_{i}_ops{h}", str(int(r[f"operations within {h}"])), int(r[f"operations within {h}"]), "results/landmark_coverage.csv", f"F row {i} operations within {h}")
        add(f"af_{i}_wd3", str(int(r["withdrawals within 3"])), int(r["withdrawals within 3"]), "results/landmark_coverage.csv", f"F row {i} withdrawals within 3")
    add("a_horizon_years", "0.8–1.2", (0.8, 1.2), "docs/decisions.md #52", "C7/C14 slope range")


def signed(x, digits=0, count=False):
    """A signed number with thousands separators and a typographic minus; a count keeps two decimals only when it is not whole."""
    if count and abs(x - round(x)) > 1e-9:
        digits = 2  # a percentile between two integer differences (e.g. +0.98) keeps its decimals
    return f"{x:+,.{digits}f}".replace("-", "−")


def v4_managed_book():
    """Notebook 13's PJM and ERCOT files and notebook 09 (part C)'s registered milestone-managed book (C15–C17)."""
    join = read("iso_join_rates.csv").set_index("iso")
    add("pjm_join_test", pct(join.loc["PJM", "share_found_2017_2019"], 0), join.loc["PJM", "share_found_2017_2019"], "results/iso_join_rates.csv",
        "PJM 2017–2019 entrants found in PJM's export")
    add("pjm_same_day", f"{int(join.loc['PJM', 'found_in_iso_file']):,}", int(join.loc["PJM", "found_in_iso_file"]), "results/iso_join_rates.csv",
        "PJM requests found in the export; every shared request date on the same day (notebook 04 (part I))")
    cont = read("iso_file_contents.csv").set_index(["file", "item"])
    for column, tag in [("operated", "op"), ("withdrew", "wd")]:
        v = int(cont.loc[("ERCOT", "test requests"), column])
        add(f"ercot_test_{tag}", str(v), v, "results/iso_file_contents.csv", f"ERCOT test requests that {column} (none listed in the GIS report)")
    pool = read("managed_book_pool.csv").set_index("region")
    add("mb_pool", f"{int(pool.loc['all', 'requests']):,}", int(pool.loc["all", "requests"]), "results/managed_book_pool.csv", "pool at +2, ≥ 20 MW")
    add("mb_pool_built", str(int(pool.loc["all", "operated_within_3"])), int(pool.loc["all", "operated_within_3"]), "results/managed_book_pool.csv",
        "pool requests operating within 3 years of the landmark")
    add("mb_pool_known", str(int(pool.loc["all", "agreement_known"])), int(pool.loc["all", "agreement_known"]), "results/managed_book_pool.csv",
        "pool requests with an agreement known at the landmark")
    books = read("managed_books.csv").set_index(["chooser", "n", "metric"])
    for chooser in ["M", "LA", "E", "L0", "random"]:
        for n in [25, 50]:
            r = books.loc[(chooser, n, "operations")]
            add(f"mb_{chooser}_{n}_ops", str(int(r["estimate"])), r["estimate"], "results/managed_books.csv", f"{chooser}, book of {n}: operations")
            r = books.loc[(chooser, n, "MW")]
            add(f"mb_{chooser}_{n}_mw", f"{r['estimate']:,.0f}", r["estimate"], "results/managed_books.csv", f"{chooser}, book of {n}: MW realised")
    comp = read("managed_book_composition.csv").set_index(["chooser", "n"])
    add("mb_known_25", str(int(comp.loc[("M", 25), "agreement_known"])), int(comp.loc[("M", 25), "agreement_known"]), "results/managed_book_composition.csv",
        "books of 25: requests with a known agreement (M and LA alike)")
    add("mb_la_known_built_25", str(int(comp.loc[("LA", 25), "operated_with_agreement"])), int(comp.loc[("LA", 25), "operated_with_agreement"]),
        "results/managed_book_composition.csv", "LA book of 25: agreed requests that operated")
    add("mb_shared_25", str(int(comp.loc[("LA", 25), "shared_with_M"])), int(comp.loc[("LA", 25), "shared_with_M"]), "results/managed_book_composition.csv",
        "requests shared by the M and LA books of 25")
    cal = read("landmark_level_calibration.csv")
    for model, tag in [("M raw", "raw"), ("M repaired", "rep")]:
        r = cal[(cal["cohort"] == "all sizes") & (cal["model"] == model) & (cal["metric"] == "intercept")].iloc[0]
        add(f"c17_{tag}", num(r["estimate"], 2), r["estimate"], "results/landmark_level_calibration.csv", f"{model}: calibration intercept, +2 landmark, 3 years")
        add(f"c17_{tag}_iv", interval(r["low"], r["high"], 2, False), (r["low"], r["high"]), "results/landmark_level_calibration.csv", "its interval")
    scored = read("success_criteria_v4_scored.csv")
    add("v4_pass", f"{int(scored['pass'].sum())} of {len(scored)}", int(scored["pass"].sum()), "results/success_criteria_v4_scored.csv", "registered v4 lines passing")
    for i, r in scored.iterrows():
        if r["id"] in ("C15", "C16"):
            c = r["id"] == "C15"
            text = f"{signed(r['estimate'], count=c)} [{signed(r['low'], count=c)}, {signed(r['high'], count=c)}]"
            add(f"a4_{i}_diff", text, (r["estimate"], r["low"], r["high"]), "results/success_criteria_v4_scored.csv", f"A4 row {i}: M − {r['benchmark']}")
        else:
            add(f"a4_{i}_intercept", f"{num(r['estimate'], 2)} {interval(r['low'], r['high'], 2, False)}", (r["estimate"], r["low"], r["high"]),
                "results/success_criteria_v4_scored.csv", f"A4 row {i}: repaired intercept")


def v5_drivers():
    """Notebook 03 §12–13: six drivers of five-year completion, where and when requests die, the hold value of surviving."""
    d = read("drivers_5yr.csv").set_index(["driver", "region", "level"])
    n_cohort = int(d.xs("Size at entry (MW)", level="driver")["n"].sum())
    add("drv_n", f"{n_cohort:,}", n_cohort, "results/drivers_5yr.csv", "entrants 2010–2019 in the drivers cohort")
    for region, level, tag in [("PJM", "<5", "pjm_lt5"), ("PJM", "≥500", "pjm_ge500"), ("PJM", "200–<500", "pjm_200"), ("CAISO", "<5", "caiso_lt5"),
                               ("ERCOT", "≥500", "ercot_ge500"), ("ERCOT", "100–<200", "ercot_100")]:
        r = d.loc[("Size at entry (MW)", region, level)]
        add(f"drv_size_{tag}", pct(r["rate"], 0), r["rate"], "results/drivers_5yr.csv", f"{region} {level} MW: five-year completion")
    for region, level, tag in [("PJM", "Gas", "pjm_gas"), ("ERCOT", "Gas", "ercot_gas"), ("PJM", "Solar", "pjm_solar"), ("ERCOT", "Solar", "ercot_solar"),
                               ("CAISO", "Solar", "caiso_solar"), ("PJM", "Battery", "pjm_batt"), ("ERCOT", "Wind", "ercot_wind"),
                               ("CAISO", "Solar+Battery", "caiso_hyb"), ("PJM", "Solar+Battery", "pjm_hyb"), ("PJM", "Offshore Wind", "pjm_off")]:
        r = d.loc[("Technology", region, level)]
        add(f"drv_tech_{tag}", pct(r["rate"], 1 if r["rate"] < 0.01 else 0), r["rate"], "results/drivers_5yr.csv", f"{region} {level}: five-year completion")
        add(f"drv_tech_{tag}_n", str(int(r["n"])), int(r["n"]), "results/drivers_5yr.csv", "its n")
    for region, level, tag in [("PJM", "1", "pjm_q1"), ("PJM", "5", "pjm_q5")]:
        r = d.loc[("Regional queue at entry (fifth)", region, level)]
        add(f"drv_queue_{tag}", pct(r["rate"], 0), r["rate"], "results/drivers_5yr.csv", f"PJM queue fifth {level}: five-year completion")
    for region, level, tag in [("PJM", "0", "pjm_c0"), ("PJM", "11+", "pjm_c11")]:
        r = d.loc[("Same-county requests, prior 2 years", region, level)]
        add(f"drv_crowd_{tag}", pct(r["rate"], 0), r["rate"], "results/drivers_5yr.csv", f"PJM county crowding {level}: five-year completion")
    for region, level, tag in [("PJM", "NRIS", "pjm_nris"), ("PJM", "ERIS", "pjm_eris")]:
        r = d.loc[("Service type", region, level)]
        add(f"drv_service_{tag}", pct(r["rate"], 0), r["rate"], "results/drivers_5yr.csv", f"PJM {level}: five-year completion")
    for region, level, tag in [("ERCOT", "signed within 2 years", "ercot_in2"), ("ERCOT", "not dated", "ercot_none"), ("ERCOT", "signed later", "ercot_later"),
                               ("CAISO", "signed later", "caiso_later"), ("CAISO", "not dated", "caiso_none")]:
        r = d.loc[("Agreement (2025 file)", region, level)]
        add(f"drv_ia_{tag}", pct(r["rate"], 1 if r["rate"] < 0.02 else 0), r["rate"], "results/drivers_5yr.csv", f"{region}, agreement {level}: five-year completion")
        add(f"drv_ia_{tag}_n", f"{int(r['n']):,}", int(r["n"]), "results/drivers_5yr.csv", "its n")
    hz = read("hazards_by_queue_year.csv").set_index(["region", "year_in_queue"])
    for region, year, tag in [("CAISO", 1, "caiso_1"), ("CAISO", 2, "caiso_2"), ("PJM", 1, "pjm_1"), ("PJM", 2, "pjm_2"), ("ERCOT", 1, "ercot_1"),
                              ("ERCOT", 5, "ercot_5"), ("ERCOT", 7, "ercot_7"), ("CAISO", 5, "caiso_5")]:
        r = hz.loc[(region, year)]
        add(f"hz_wd_{tag}", pct(r["h_withdrawal"], 0), r["h_withdrawal"], "results/hazards_by_queue_year.csv", f"{region} year {year}: withdrawal hazard")
    for region, year, tag in [("ERCOT", 5, "ercot_5"), ("CAISO", 5, "caiso_5"), ("PJM", 7, "pjm_7")]:
        r = hz.loc[(region, year)]
        add(f"hz_op_{tag}", pct(r["h_operation"], 0), r["h_operation"], "results/hazards_by_queue_year.csv", f"{region} year {year}: operation hazard")
    st = read("exit_stage.csv").set_index(["region", "stage"])
    for region, stage, tag in [("CAISO", "System impact study", "caiso_sis"), ("PJM", "System impact study", "pjm_sis"), ("PJM", "Feasibility study", "pjm_feas"),
                               ("ERCOT", "Facilities study", "ercot_fac"), ("ERCOT", "Agreement executed", "ercot_ia"), ("PJM", "Agreement executed", "pjm_ia")]:
        r = st.loc[(region, stage)]
        add(f"stage_{tag}", pct(r["share"], 0), r["share"], "results/exit_stage.csv", f"{region}: share of withdrawals leaving during the {stage.lower()}")
    tm = read("exit_timing.csv").set_index(["region", "stage"])
    for region, stage, tag in [("CAISO", "System impact study", "caiso_sis"), ("PJM", "System impact study", "pjm_sis"), ("PJM", "Feasibility study", "pjm_feas"),
                               ("ERCOT", "Facilities study", "ercot_fac"), ("ERCOT", "Agreement executed", "ercot_ia")]:
        r = tm.loc[(region, stage)]
        add(f"exit_years_{tag}", num(r["median_years"], 1), r["median_years"], "results/exit_timing.csv", f"{region}: median years to withdrawal, {stage.lower()}")
    gs = read("completion_given_survival.csv").set_index(["region", "survived_years"])
    for region in config.TRACK_A_REGIONS:
        for s_ in (0, 2):
            r = gs.loc[(region, s_)]
            add(f"hold_{region.lower()}_{s_}", pct(r["rate"], 0 if r["rate"] >= 0.05 else 1), r["rate"], "results/completion_given_survival.csv",
                f"{region}: share operating within the next 3 years after surviving {s_} years")


def v5_segments():
    """Notebook 09 §4b: the ten entry segments and their out-of-time check."""
    seg = read("segments.csv").set_index("segment")
    for sid in seg.index:
        r = seg.loc[sid]
        add(f"seg_{sid}_fit", pct(r["rate_train"], 1 if r["rate_train"] < 0.02 else 0), r["rate_train"], "results/segments.csv", f"{sid} ({r['rule']}): fitting-cohort rate")
        add(f"seg_{sid}_test", pct(r["rate_test"], 1 if r["rate_test"] < 0.02 else 0), r["rate_test"], "results/segments.csv", f"{sid}: 2017–2019 rate")
        add(f"seg_{sid}_n_test", f"{int(r['n_test']):,}", int(r["n_test"]), "results/segments.csv", f"{sid}: 2017–2019 requests")
    add("seg_count", str(len(seg)), len(seg), "results/segments.csv", "segments")
    add("seg_fit_n", f"{int(seg['n_train'].sum()):,}", int(seg["n_train"].sum()), "results/segments.csv", "fitting-cohort requests")
    from scipy.stats import spearmanr
    ok = seg.dropna(subset=["rate_test"])
    rho = spearmanr(ok["rate_train"], ok["rate_test"]).statistic
    add("seg_rho", num(rho, 2), rho, "results/segments.csv", "Spearman rank correlation of segment rates, fitting vs later cohort")
    add("seg_range", f"{pct(seg['rate_test'].min(), 0)} to {pct(seg['rate_train'].max(), 0)}", (seg["rate_test"].min(), seg["rate_train"].max()),
        "results/segments.csv", "range of segment rates quoted in the report")


def v5_timing():
    """Notebook 08 §11: how far off the model's expected year of operation is, among the built."""
    t = read("timing_error.csv").set_index(["region", "model"])
    for region in ["all", "PJM", "ERCOT"]:
        for model, tag in [("dt_lgbm", "lgbm"), ("training median by region", "median")]:
            r = t.loc[(region, model)]
            add(f"time_{region.lower()}_{tag}_mae", num(r["mae_years"], 2), r["mae_years"], "results/timing_error.csv", f"{region}, {model}: mean absolute error, years")
            add(f"time_{region.lower()}_{tag}_within1", pct(r["share_within_1_year"], 0), r["share_within_1_year"], "results/timing_error.csv", "share within a year")
            add(f"time_{region.lower()}_{tag}_signed", num(r["median_signed_error"], 2, sign=True), r["median_signed_error"], "results/timing_error.csv", "median signed error")
    add("time_n_built", str(int(t.loc[("all", "dt_lgbm"), "n_built"])), int(t.loc[("all", "dt_lgbm"), "n_built"]), "results/timing_error.csv", "test requests built within 7 years")
    add("time_ercot_median_obs", num(t.loc[("ERCOT", "dt_lgbm"), "median_observed_years"], 1), t.loc[("ERCOT", "dt_lgbm"), "median_observed_years"],
        "results/timing_error.csv", "ERCOT: median observed years to operation among the built")
    add("time_ercot_bench", num(t.loc[("ERCOT", "training median by region"), "median_predicted_years"], 1),
        t.loc[("ERCOT", "training median by region"), "median_predicted_years"], "results/timing_error.csv", "ERCOT: training-cohort median years to operation")


def v5_tournament():
    """Notebook 08b §7: other learners under C18–C19."""
    choice = read("tournament_choice.json")
    add("t_star", choice["chosen"], choice["chosen"], "results/tournament_choice.json", "the learner chosen on 2016")
    for k, tag in [("K0", "k0"), ("T1", "t1"), ("T2", "t2"), ("T3", "t3")]:
        add(f"t_brier16_{tag}", num(choice["mean_brier_2016"][k], 4), choice["mean_brier_2016"][k], "results/tournament_choice.json", f"{k}: mean 2016 Brier")
    crit = read("tournament_criteria.csv").set_index("criterion")
    for c in ["C18", "C19"]:
        add(f"{c.lower()}_verdict", crit.loc[c, "verdict"], crit.loc[c, "verdict"], "results/tournament_criteria.csv", f"{c} verdict")
        add(f"{c.lower()}_lines", f"{int(crit.loc[c, 'lines_passed'])} of {int(crit.loc[c, 'lines'])}", int(crit.loc[c, "lines_passed"]), "results/tournament_criteria.csv", f"{c} lines passed")
    t = read("tournament.csv")
    for cohort, ref, metric, h, tag in [("≥ 20 MW", "dt_lgbm", "uno_c", 3, "big_lgbm_uno3"), ("≥ 20 MW", "dt_lgbm", "uno_c", 5, "big_lgbm_uno5"),
                                        ("≥ 20 MW", "fair_baseline", "uno_c", 3, "big_fair_uno3"), ("≥ 20 MW", "fair_baseline", "uno_c", 5, "big_fair_uno5"),
                                        ("all sizes", "dt_lgbm", "uno_c", 5, "all_lgbm_uno5"), ("all sizes", "dt_lgbm", "uno_c", 7, "all_lgbm_uno7")]:
        r = t[(t["cohort"] == cohort) & (t["reference"] == ref) & (t["model"] == "T*") & (t["metric"] == metric) & (t["horizon"] == h)].iloc[0]
        add(f"t_{tag}_diff", num(r["diff"], 3, sign=True), r["diff"], "results/tournament.csv", f"T* − {ref}, {metric}, {h} y, {cohort}")
        add(f"t_{tag}_iv", interval(r["diff_low"], r["diff_high"], 3), (r["diff_low"], r["diff_high"]), "results/tournament.csv", "its interval")
    allc = read("tournament_all_candidates_test.csv").set_index(["model", "metric", "horizon"])
    for m, tag in [("T1", "t1"), ("T2", "t2"), ("dt_lgbm", "lgbm")]:
        add(f"t_{tag}_uno5", num(allc.loc[(m, "uno_c", 5), "estimate"], 2), allc.loc[(m, "uno_c", 5), "estimate"], "results/tournament_all_candidates_test.csv", f"{m}: Uno's C at 5 years, all sizes")


def v5_npv():
    """Notebook 15 §8: NPV per MW, break-even prices and expected NPV per request."""
    n = read("npv_table.csv").set_index(["cod_year", "region", "tech"])
    for cod in (2024, 2028):
        for region in config.TRACK_A_REGIONS:
            for tech, tag in [("Wind", "wind"), ("Solar", "solar"), ("Gas", "gas"), ("Battery", "batt"), ("Solar+Battery", "hyb"), ("Offshore Wind", "off")]:
                v = n.loc[(cod, region, tech), "npv_per_mw_base"] / 1e6
                add(f"npv_{cod}_{region.lower()}_{tag}", num(v, 2, sign=True).replace("+", ""), v, "results/npv_table.csv", f"NPV per MW, $M, {tech} {region}, COD {cod}, base, merchant")
                v = n.loc[(cod, region, tech), "npv_contracted_base"] / 1e6
                add(f"npvc_{cod}_{region.lower()}_{tag}", num(v, 2, sign=True).replace("+", ""), v, "results/npv_table.csv", f"NPV per MW, $M, {tech} {region}, COD {cod}, base, contracted")
        positives = int((n.xs(cod, level="cod_year")["npv_per_mw_base"] > 0).sum())
        add(f"npv_positive_{cod}", str(positives), positives, "results/npv_table.csv", f"technology-region pairs with positive base NPV, COD {cod}, merchant")
        positives = int((n.xs(cod, level="cod_year")["npv_contracted_base"] > 0).sum())
        add(f"npvc_positive_{cod}", str(positives), positives, "results/npv_table.csv", f"technology-region pairs with positive base NPV, COD {cod}, contracted")
    atb_w = read("atb_costs.csv").set_index("tech")
    for tech, tag in [("Solar", "solar"), ("Wind", "wind"), ("Gas", "gas"), ("Offshore Wind", "off")]:
        v = atb_w.loc[tech, "wacc_real"]
        add(f"wacc_{tag}", pct(v, 1), v, "results/atb_costs.csv", f"{tech}: ATB real WACC")
    import ast
    va = read("value_assumptions.csv").set_index("input")
    ppa = ast.literal_eval(va.loc["contracted case: PPA price, $/MWh, first 15 years", "value"])
    for tech, tag in [("Solar", "solar"), ("Wind", "wind"), ("Solar+Battery", "hyb"), ("Offshore Wind", "off")]:
        add(f"ppa_{tag}", f"${ppa[tech]:,.0f}", ppa[tech], "results/value_assumptions.csv", f"{tech}: PPA price assumption, $/MWh")
    curve = read("recommended_books_curve.csv").set_index(["chooser", "n"])
    for ch in ["M", "LA"]:
        for n_ in [25, 50, 100]:
            v = int(curve.loc[(ch, n_), "operations"])
            add(f"curve_{ch.lower()}_{n_}", str(v), v, "results/recommended_books_curve.csv", f"{ch}: operations among the first {n_} adds")
    pack = read("decision_pack.csv")
    top = pack[pack["decision_2y_contracted"] == "accelerate"].sort_values("expected_npv_2y_base_contracted_$M", ascending=False).head(6)
    for k, (_, row) in enumerate(top.iterrows()):
        add(f"card{k}_mw", f"{row['mw']:,.0f}", row["mw"], "results/decision_pack.csv", f"card {k}: MW")
        add(f"card{k}_npv_c", f"${row['expected_npv_2y_base_contracted_$M']:,.0f}", row["expected_npv_2y_base_contracted_$M"], "results/decision_pack.csv", f"card {k}: expected NPV two years in, contracted, $M")
        add(f"card{k}_npv_m", f"${row['expected_npv_2y_base_merchant_$M']:,.0f}", row["expected_npv_2y_base_merchant_$M"], "results/decision_pack.csv", f"card {k}: expected NPV two years in, merchant, $M")
        add(f"card{k}_p3", pct(row["p3_landmark"], 0), row["p3_landmark"], "results/decision_pack.csv", f"card {k}: landmark probability")
        add(f"card{k}_p5", pct(row["p5_lookup"], 0), row["p5_lookup"], "results/decision_pack.csv", f"card {k}: lookup probability")
        add(f"card{k}_cost", f"${row['cost_to_next_gate_base_$M']:.1f}", row["cost_to_next_gate_base_$M"], "results/decision_pack.csv", f"card {k}: cost to next gate, $M")
    r = n.loc[(2024, "PJM", "Gas")]
    add("npv_pjm_gas_low", num(r["npv_per_mw_low"] / 1e6, 1), r["npv_per_mw_low"], "results/npv_table.csv", "PJM gas 2024: low case $M")
    add("npv_pjm_gas_high", num(r["npv_per_mw_high"] / 1e6, 1), r["npv_per_mw_high"], "results/npv_table.csv", "PJM gas 2024: high case $M")
    for tech, tag in [("Solar", "solar"), ("Wind", "wind"), ("Gas", "gas"), ("Solar+Battery", "hyb")]:
        v = n.loc[(2024, "PJM", tech), "breakeven_price_base"]
        add(f"be_{tag}", f"${v:,.0f}", v, "results/npv_table.csv", f"break-even flat price, $/MWh, {tech}")
    for region in config.TRACK_A_REGIONS:
        for tech, tag in [("Solar", "solar"), ("Wind", "wind")]:
            v = n.loc[(2024, region, tech), "captured_price_base"]
            add(f"captured_{region.lower()}_{tag}", f"${v:,.0f}", v, "results/npv_table.csv", f"captured energy price, $/MWh, {tech} {region}, 2024")
    atb = read("atb_costs.csv").set_index("tech")
    for tech, tag in [("Solar", "solar"), ("Wind", "wind"), ("Gas", "gas"), ("Battery", "batt")]:
        add(f"capex_{tag}", f"${atb.loc[tech, 'capex_per_kw']:,.0f}", atb.loc[tech, "capex_per_kw"], "results/atb_costs.csv", f"{tech}: ATB CAPEX $/kW")
    b = read("npv_by_request.csv")
    med = b["expected_npv_recalibrated_base"].median() / 1e6
    add("enpv_median", num(med, 1), med, "results/npv_by_request.csv", "median expected NPV at entry, $M, level repaired, base, merchant")
    medc = b["expected_npv_contracted_recalibrated_base"].median() / 1e6
    add("enpvc_median", num(medc, 1), medc, "results/npv_by_request.csv", "median expected NPV at entry, $M, level repaired, base, contracted")
    for region in config.TRACK_A_REGIONS:
        share = (b.loc[b["region"] == region, "npv_per_mw_contracted_if_built_year3_base"] > 0).mean()
        add(f"npvc_pos_share_{region.lower()}", pct(share, 0), share, "results/npv_by_request.csv", f"{region}: share with a positive contracted NPV if built in year 3")
    add("enpv_mean", num(b["expected_npv_recalibrated_base"].mean() / 1e6, 0), b["expected_npv_recalibrated_base"].mean(), "results/npv_by_request.csv", "mean expected NPV at entry, $M")
    for region in config.TRACK_A_REGIONS:
        share = (b.loc[b["region"] == region, "npv_per_mw_if_built_year3_base"] > 0).mean()
        add(f"npv_pos_share_{region.lower()}", pct(share, 0), share, "results/npv_by_request.csv", f"{region}: share of test requests whose plant has a positive NPV if built in year 3")
    for region in ["ERCOT", "PJM", "CAISO"]:
        v = b[(b["region"] == region) & (b["tech"] == "Wind")]["expected_npv_recalibrated_base"].median() / 1e6
        add(f"enpv_wind_{region.lower()}", num(v, 1 if abs(v) < 5 else 0), v, "results/npv_by_request.csv", f"{region} wind: median expected NPV at entry, $M")


def v5_review():
    """Notebook 16 §9: the gates, the four policies and the decision pack."""
    r = read("portfolio_review_summary.csv")
    MAIN_H = {"G1 entry": 3.0, "G2 two years": 2.0}
    for gate, tag0 in [("G1 entry", "g1"), ("G2 two years", "g2")]:
      for rc, rtag in [("merchant", ""), ("contracted", "c")]:
        tag = tag0 + rtag
        part = r[(r["gate"] == gate) & (r["region"] == "all") & (r["revenue_case"] == rc)]
        for h in (2.0, 3.0, 5.0):
            for _, row in part[part["h"] == h].iterrows():
                cls = row["decision"].replace(" or ", "_").replace(" ", "_")
                hk = f"_h{int(h)}" if h != MAIN_H[gate] else ""
                add(f"{tag}_{cls}{hk}_n", f"{int(row['n']):,}", int(row["n"]), "results/portfolio_review_summary.csv", f"{gate}, h={h:.0f}, {row['decision']}: requests")
                add(f"{tag}_{cls}{hk}_share", pct(row["operated_share"], 0), row["operated_share"], "results/portfolio_review_summary.csv", f"{gate}, h={h:.0f}, {row['decision']}: operated share")
                add(f"{tag}_{cls}{hk}_iv", f"[{pct(row['low'], 0)}, {pct(row['high'], 0)}]", (row["low"], row["high"]), "results/portfolio_review_summary.csv", "its Wilson interval")
                add(f"{tag}_{cls}{hk}_ops", str(int(row["operated"])), int(row["operated"]), "results/portfolio_review_summary.csv", "operations in the class")
                add(f"{tag}_{cls}{hk}_pool_share", pct(row["share_of_pool_operations"], 0), row["share_of_pool_operations"], "results/portfolio_review_summary.csv", "share of the pool's operations")
                add(f"{tag}_{cls}{hk}_mw", f"{row['mw']:,.0f}", row["mw"], "results/portfolio_review_summary.csv", "MW in the class")
                add(f"{tag}_{cls}{hk}_npv", f"{row['realised_npv_$M']:+,.0f}".replace("-", "−"), row["realised_npv_$M"], "results/portfolio_review_summary.csv", "realised NPV, $M")
        for region in config.TRACK_A_REGIONS:
            for _, row in r[(r["gate"] == gate) & (r["region"] == region) & (r["h"] == MAIN_H[gate]) & (r["revenue_case"] == rc)].iterrows():
                cls = row["decision"].replace(" or ", "_").replace(" ", "_")
                add(f"{tag}_{region.lower()}_{cls}_share", pct(row["operated_share"], 0) if row["n"] else "n/a", row["operated_share"], "results/portfolio_review_summary.csv", f"{gate}, {region}, {row['decision']}: operated share")
                add(f"{tag}_{region.lower()}_{cls}_n", f"{int(row['n']):,}", int(row["n"]), "results/portfolio_review_summary.csv", "requests")
    pool_n = int(r[(r["gate"] == "G2 two years") & (r["region"] == "all") & (r["h"] == 2.0) & (r["revenue_case"] == "merchant")]["n"].sum())
    add("g2_pool_n", f"{pool_n:,}", pool_n, "results/portfolio_review_summary.csv", "the +2 pool, all sizes")
    pool_ops = int(r[(r["gate"] == "G2 two years") & (r["region"] == "all") & (r["h"] == 2.0) & (r["revenue_case"] == "merchant")]["operated"].sum())
    add("g2_pool_ops", str(pool_ops), pool_ops, "results/portfolio_review_summary.csv", "operations within 3 years in the +2 pool")
    polt = read("policy_comparison.csv")
    tags = {"equal regional split": "equal", "NPV per dollar, with caps": "npvdollar", "model expected NPV, no caps": "nocaps",
            "risk-adjusted (E[NPV] − λ·ES95), with caps": "risk", "fair baseline, value index (section 5)": "fair", "random (section 5)": "random"}
    for rc, rtag in [("merchant", ""), ("contracted", "c")]:
      pol = polt[polt["revenue_case"] == rc].set_index("policy")
      for name, tag0 in tags.items():
        tag = tag0 + rtag
        row = pol.loc[name]
        add(f"pol_{tag}_n", str(int(row["requests"])), int(row["requests"]), "results/policy_comparison.csv", f"{name}: requests")
        add(f"pol_{tag}_enpv", f"{row['expected_npv_$M']:+,.0f}".replace("-", "−"), row["expected_npv_$M"], "results/policy_comparison.csv", f"{name}: expected NPV $M")
        add(f"pol_{tag}_es", f"{row['es95_$M']:+,.0f}".replace("-", "−"), row["es95_$M"], "results/policy_comparison.csv", f"{name}: ES95 $M")
        add(f"pol_{tag}_pneg", pct(row["p_negative_npv"], 0), row["p_negative_npv"], "results/policy_comparison.csv", f"{name}: P(NPV < 0)")
        add(f"pol_{tag}_ops", str(int(row["realised_operations_5yr"])), int(row["realised_operations_5yr"]), "results/policy_comparison.csv", f"{name}: realised operations")
        add(f"pol_{tag}_mw", f"{row['realised_mw_5yr']:,.0f}", row["realised_mw_5yr"], "results/policy_comparison.csv", f"{name}: realised MW")
        add(f"pol_{tag}_rnpv", f"{row['realised_npv_$M']:+,.0f}".replace("-", "−"), row["realised_npv_$M"], "results/policy_comparison.csv", f"{name}: realised NPV $M")
        add(f"pol_{tag}_conc", pct(row["max_region_share"], 0), row["max_region_share"], "results/policy_comparison.csv", f"{name}: largest region share")
    pack = read("decision_pack.csv")
    add("pack_n", f"{len(pack):,}", len(pack), "results/decision_pack.csv", "rows of the decision pack")
    for rc, rtag in [("merchant", ""), ("contracted", "c")]:
        for cls in ["invest", "hold", "exit"]:
            v = int((pack[f"decision_entry_{rc}"] == cls).sum())
            add(f"pack{rtag}_entry_{cls}", f"{v:,}", v, "results/decision_pack.csv", f"entry decision {cls}, {rc}")


def v5_books():
    """Notebook 20 §10: the floor book per region."""
    rec = read("recommended_books.csv")
    for chooser, tag in [("M — landmark model", "m"), ("LA — lookup with agreement status", "la")]:
        for region in config.TRACK_A_REGIONS + ["all"]:
            row = rec[(rec["chooser"] == chooser) & (rec["region"] == region)].iloc[0]
            add(f"book_{tag}_{region.lower()}_n", str(int(row["requests_added"])), int(row["requests_added"]), "results/recommended_books.csv", f"{chooser}, {region}: requests added")
            add(f"book_{tag}_{region.lower()}_ops", str(int(row["realised_operations"])), int(row["realised_operations"]), "results/recommended_books.csv", "realised operations")
            add(f"book_{tag}_{region.lower()}_iv", f"[{row['ops_low']:.0f}, {row['ops_high']:.0f}]", (row["ops_low"], row["ops_high"]), "results/recommended_books.csv", "its interval")
            add(f"book_{tag}_{region.lower()}_exp", num(row["expected_operations"], 1), row["expected_operations"], "results/recommended_books.csv", "expected operations")
            add(f"book_{tag}_{region.lower()}_mw", f"{row['realised_mw']:,.0f}", row["realised_mw"], "results/recommended_books.csv", "realised MW")
            add(f"book_{tag}_{region.lower()}_pool", f"{int(row['pool_requests']):,}", int(row["pool_requests"]), "results/recommended_books.csv", "pool requests")
            add(f"book_{tag}_{region.lower()}_pool_ops", str(int(row["pool_operations"])), int(row["pool_operations"]), "results/recommended_books.csv", "pool operations")
            if tag == "m":
                add(f"book_m_{region.lower()}_npv", f"{row['expected_npv_$M']:+,.0f}".replace("-", "−"), row["expected_npv_$M"], "results/recommended_books.csv", "expected NPV of the adds, $M, merchant")
                add(f"book_m_{region.lower()}_npvc", f"{row['expected_npv_contracted_$M']:+,.0f}".replace("-", "−"), row["expected_npv_contracted_$M"], "results/recommended_books.csv", "expected NPV of the adds, $M, contracted")
                add(f"book_m_{region.lower()}_diff_iv", f"[{signed(row['diff_M_minus_LA_low'], count=True)}, {signed(row['diff_M_minus_LA_high'], count=True)}]",
                    (row["diff_M_minus_LA_low"], row["diff_M_minus_LA_high"]), "results/recommended_books.csv", "M − LA operations, interval")


def v5_archetypes():
    """Notebook 03b §5: the state archetypes."""
    prof = read("archetype_profiles.csv")
    add("arch_k", str(len(prof)), len(prof), "results/archetype_profiles.csv", "archetypes")
    add("arch_states", str(int(prof["states"].sum())), int(prof["states"].sum()), "results/archetype_profiles.csv", "states clustered")
    for i, row in prof.reset_index(drop=True).iterrows():
        add(f"arch_{i + 1}_name", row["name"], row["name"], "results/archetype_profiles.csv", f"archetype {i + 1} name")
        add(f"arch_{i + 1}_rate", pct(row["completion_2017_2019"], 1), row["completion_2017_2019"], "results/archetype_profiles.csv", f"archetype {i + 1}: 2017–2019 entrants operating by end-2024")
        add(f"arch_{i + 1}_iv", f"[{pct(row['low'], 0)}, {pct(row['high'], 0)}]", (row["low"], row["high"]), "results/archetype_profiles.csv", "its interval")
        add(f"arch_{i + 1}_n", f"{int(row['n_2017_2019']):,}", int(row["n_2017_2019"]), "results/archetype_profiles.csv", "2017–2019 entrants")
        add(f"arch_{i + 1}_states", str(int(row["states"])), int(row["states"]), "results/archetype_profiles.csv", "states")
        add(f"arch_{i + 1}_list", row["state_list"], row["state_list"], "results/archetype_profiles.csv", "states in the archetype")
        add(f"arch_{i + 1}_qof", num(row["queue_over_fleet"], 1), row["queue_over_fleet"], "results/archetype_profiles.csv", "median queue over fleet")
        add(f"arch_{i + 1}_storage", pct(row["storage_share"], 0), row["storage_share"], "results/archetype_profiles.csv", "median storage share of waiting MW")
        add(f"arch_{i + 1}_recent", pct(row["recent_entry_share"], 0), row["recent_entry_share"], "results/archetype_profiles.csv", "median recent-entry share")


def v5_extras():
    """Loose ends the report quotes: billions, the decision-pack cross-tabulation, costs per MW, the gas price, the silhouette."""
    r = read("portfolio_review_summary.csv").set_index(["revenue_case", "gate", "h", "region", "decision"])
    H = {"G1 entry": 3.0, "G2 two years": 2.0}
    for rc, rtag in [("merchant", ""), ("contracted", "c")]:
        for gate, tag, cls in [("G1 entry", "g1", "exit"), ("G2 two years", "g2", "exit")]:
            v = r.loc[(rc, gate, H[gate], "all", cls), "realised_npv_$M"] / 1e3
            add(f"{tag}{rtag}_exit_npv_bn", f"{abs(v):.1f}", v, "results/portfolio_review_summary.csv", f"{gate} exit class, {rc}: realised NPV, $ billion (loss)")
        for gate, tag, cls in [("G1 entry", "g1", "invest"), ("G2 two years", "g2", "accelerate")]:
            v = r.loc[(rc, gate, H[gate], "all", cls), "realised_npv_$M"] / 1e3
            add(f"{tag}{rtag}_{cls}_npv_bn", f"{v:.1f}", v, "results/portfolio_review_summary.csv", f"{gate} {cls} class, {rc}: realised NPV, $ billion")
        n_all = int(r.loc[(rc, "G1 entry", 3.0, "all")]["n"].sum())
        share_exit = r.loc[(rc, "G1 entry", 3.0, "all", "exit"), "n"] / n_all
        add(f"g1{rtag}_exit_share_of_cohort", pct(share_exit, 0), share_exit, "results/portfolio_review_summary.csv", f"share of the test cohort the entry gate marks for exit, {rc}")
        share_commit = (r.loc[(rc, "G1 entry", 3.0, "all", "invest"), "n"] + r.loc[(rc, "G2 two years", 2.0, "all", "accelerate"), "n"]) / n_all
        add(f"gates{rtag}_commit_share", pct(share_commit, 0), share_commit, "results/portfolio_review_summary.csv", f"invest + accelerate requests as a share of the cohort, {rc}")
    pack = read("decision_pack.csv")
    for rc, rtag in [("merchant", ""), ("contracted", "c")]:
        ct = pd.crosstab(pack[f"decision_entry_{rc}"], pack[f"decision_2y_{rc}"].fillna("not in pool"))
        for a, b, tag in [("invest", "accelerate", "inv_acc"), ("invest", "exit", "inv_exit"), ("invest", "not in pool", "inv_gone"),
                          ("exit", "exit", "exit_exit"), ("exit", "accelerate", "exit_acc"), ("hold", "hold or sell", "hold_hold")]:
            v = int(ct.loc[a, b]) if (a in ct.index and b in ct.columns) else 0
            add(f"pack{rtag}_{tag}", str(v), v, "results/decision_pack.csv", f"entry {a} → two-year {b}, {rc}")
    pol = read("policy_comparison.csv")
    pol = pol[pol["revenue_case"] == "merchant"].set_index("policy")
    v = pol.loc["fair baseline, value index (section 5)", "es95_$M"] / 1e3
    add("pol_fair_es_bn", f"{abs(v):.1f}", v, "results/policy_comparison.csv", "fair baseline value-index book: ES95, $ billion (loss)")
    v = pol.loc["fair baseline, value index (section 5)", "expected_npv_$M"] / 1e3
    add("pol_fair_enpv_bn", f"{abs(v):.1f}", v, "results/policy_comparison.csv", "fair baseline value-index book: expected NPV, $ billion (loss)")
    lo = min(pol.loc[n, "realised_npv_$M"] for n in ["NPV per dollar, with caps", "model expected NPV, no caps", "risk-adjusted (E[NPV] − λ·ES95), with caps"])
    hi = max(pol.loc[n, "realised_npv_$M"] for n in ["NPV per dollar, with caps", "model expected NPV, no caps", "risk-adjusted (E[NPV] − λ·ES95), with caps"])
    add("pol_npv_books_range", f"+${lo:,.0f} to +${hi:,.0f}", (lo, hi), "results/policy_comparison.csv", "realised NPV range of the three NPV-based books, $M")
    cost = read("cost_table.csv").set_index("size_regime")
    for regime, tag in [("20–<100", "20_100"), ("≥500", "ge500")]:
        v = cost.loc[regime, "sunk_per_mw_base"]
        add(f"sunk_{tag}", f"{v:,.0f}", v, "results/cost_table.csv", f"deposit to the next gate, $ per MW, {regime} MW, base")
    va = read("value_assumptions.csv").set_index("input")
    gp = float(va.loc["natural gas price, $/MMBtu", "value"])
    add("gas_price", f"{gp:.2f}", gp, "results/value_assumptions.csv", "gas price assumption, $/MMBtu")
    rec = read("recommended_books.csv")
    v = rec[(rec["chooser"] == "M — landmark model") & (rec["region"] == "all")]["expected_operations"].iloc[0]
    add("book_m_all_exp_int", f"{v:.0f}", v, "results/recommended_books.csv", "model's own expectation for the floor book, operations")
    arch = read("state_archetypes.csv")
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    feats = ["queue_over_fleet", "solar_share", "storage_share", "gas_share", "median_mw_waiting", "recent_entry_share", "share_built_2010_2018"]
    sil = silhouette_score(StandardScaler().fit_transform(arch[feats]), arch["archetype"])
    add("arch_silhouette", f"{sil:.2f}", sil, "results/state_archetypes.csv", "silhouette of the chosen clustering")


def money_b(x, digits=1, sign=False):
    """$ billions as the report writes them."""
    v = x / 1e9
    return (f"{v:+.{digits}f}" if sign else f"{v:.{digits}f}").replace("-", "−") + "B"


def money_m(x, sign=False):
    v = x / 1e6
    return (f"{v:+,.0f}" if sign else f"{v:,.0f}").replace("-", "−") + "M"


def v6_data():
    """Part II §13–§14: the pool, the sources and the gate."""
    inv = read("investment_candidates.csv")
    add("v6_pool_leases", f"{(inv['sector'] == 'offshore oil and gas').sum():,}", int((inv["sector"] == "offshore oil and gas").sum()), "results/investment_candidates.csv", "producing leases in the pool")
    add("v6_pool_requests", f"{(inv['sector'] != 'offshore oil and gas').sum():,}", int((inv["sector"] != "offshore oil and gas").sum()), "results/investment_candidates.csv", "queue requests in the pool")
    book = inv[inv["in_default_book"]]
    add("v6_book_leases", str(int((book["sector"] == "offshore oil and gas").sum())), int((book["sector"] == "offshore oil and gas").sum()), "results/investment_candidates.csv", "leases in the default book")
    per_tech = book[book["sector"] != "offshore oil and gas"].groupby("technology").size()
    add("v6_book_per_tech", str(int(per_tech.iloc[0])), int(per_tech.iloc[0]), "results/investment_candidates.csv", "requests per technology in the default book")
    add("v6_book_total", str(len(book)), len(book), "results/investment_candidates.csv", "candidates in the default book")
    gate = (paths.DOCS / "data_readiness.md").read_text(encoding="utf-8")
    for key, pattern, note in [("v6_bsee_files", r"\| (\d+) files, \d+ hashes", "BSEE files hashed"),
                               ("v6_gate_leases", r"\| ([\d,]+) leases \| PASS", "leases with 60+ producing months"),
                               ("v6_eia923_rows", r"\| ([\d,]+) of [\d,]+; 2018-01", "EIA-923 rows received"),
                               ("v6_assumed_months", r"assumed months: (\d+)", "ERCOT months bridged (ASSUMED)"),
                               ("v6_egrid_join", r"\| ([\d.]+%) \| PASS", "EIA-923 plants of 2023 found in eGRID2023"),
                               ("v6_pages_checked", r"(\d+) EIA-923 pages checked", "saved API pages checked for the key")]:
        m = re.search(pattern, gate)
        add(key, m.group(1), m.group(1), "docs/data_readiness.md", note)
    m = re.search(r"Gas CC (\d+), Solar (\d+), Wind (\d+), Storage (\d+)", gate)
    for name, val in zip(["gas", "solar", "wind", "storage"], m.groups()):
        add(f"v6_plants_{name}", val, int(val), "docs/data_readiness.md", f"Texas {name} plants with 36+ generating months")
    add("v6_min_months", "60", 60, "src/config.py", "producing months required of a lease in the pool")
    add("v6_lag_bsee", "three", 3, "src/config.py", "BSEE release lag, months")
    add("v6_lag_eia923", "two", 2, "src/config.py", "EIA-923 release lag, months")


def v6_forecasts():
    """Part II §15–§16: the EDA facts and C20."""
    eda = read("energy_eda_summary.csv") if (paths.RESULTS / "energy_eda_summary.csv").exists() else None
    cf = read("eda_capacity_factor_ci.csv").set_index("technology")["estimate"]
    for tech_, key in (("Wind", "v6_cf_wind"), ("Solar", "v6_cf_solar"), ("Gas CC", "v6_cf_gas")):
        add(key, pct(cf[tech_], 0), cf[tech_], "results/eda_capacity_factor_ci.csv", f"Texas {tech_} capacity factor, plant level, 2018–2024")
    sc = read("success_criteria_v6_scored.csv")
    reg = sc[sc["registered"]]
    add("v6_c20_lines", str(len(reg)), len(reg), "results/success_criteria_v6_scored.csv", "C20 registered lines")
    add("v6_c20_pass", str(int((reg["result"] == "PASS").sum())), int((reg["result"] == "PASS").sum()), "results/success_criteria_v6_scored.csv", "C20 lines passed")
    for line, name in [("cf_Gas CC_h1", "gas"), ("cf_Solar_h1", "solar"), ("cf_Wind_h1", "wind")]:
        r = sc[sc["line"] == line].iloc[0]
        add(f"v6_c20_gain_{name}", pct(-r["diff_relative"], 0), -r["diff_relative"], "results/success_criteria_v6_scored.csv", f"{name} CF +1 m: error cut against the seasonal naive")
    r = sc[sc["line"] == "lease_oil_h3"].iloc[0]
    add("v6_c20_lease_ratio", f"{r['mae_ratio']:.2f}", r["mae_ratio"], "results/success_criteria_v6_scored.csv", "lease oil +3 m: challenger MAE over the last-value baseline")
    ph = read("forecast_posthoc_leases.csv")
    r = ph[ph["line"] == "lease_oil_h3"].iloc[0]
    add("v6_posthoc_lease_ratio", f"{r['posthoc_mae_ratio']:.2f}", r["posthoc_mae_ratio"], "results/forecast_posthoc_leases.csv", "lease oil +3 m: the post-hoc level model's ratio")
    add("v6_arps_window", "36", 36, "src/economics.py", "months of history behind the Arps baseline")
    add("v6_half_life_median_months", "twelve", 12, "notebook 02 part C", "months for the median lease to halve its peak oil")


def v6_economics():
    """Part II §17: the candidates, the grid and the tornado."""
    cand = read("candidate_npv.csv")
    leases = cand[cand["sector"] == "offshore oil and gas"]
    power = cand[cand["sector"] != "offshore oil and gas"]
    add("v6_lease_npv_base", "$" + money_b(leases["expected_npv_base"].sum()), leases["expected_npv_base"].sum(), "results/candidate_npv.csv", "incremental NPV of the twenty leases, base grid")
    add("v6_breakeven_median", f"${leases['breakeven_wti_base'].median():.0f}", leases["breakeven_wti_base"].median(), "results/candidate_npv.csv", "median break-even WTI of the twenty leases, $/bbl")
    add("v6_power_merchant", "−$" + money_b(-power["expected_npv_base"].sum(), 2), power["expected_npv_base"].sum(), "results/candidate_npv.csv", "expected NPV of the twenty requests, merchant")
    add("v6_power_contracted", "−$" + money_b(-power["expected_npv_contracted"].sum(), 2), power["expected_npv_contracted"].sum(), "results/candidate_npv.csv", "expected NPV of the twenty requests, contracted")
    add("v6_p_op_low", pct(power["p_operation_7y"].min(), 0), power["p_operation_7y"].min(), "results/candidate_npv.csv", "lowest P(operation within 7 y) among the requests")
    add("v6_p_op_high", pct(power["p_operation_7y"].max(), 0), power["p_operation_7y"].max(), "results/candidate_npv.csv", "highest P(operation within 7 y) among the requests")
    cf = read("candidate_capture_factors.csv").set_index("technology")
    for t, key in [("Solar", "solar"), ("Wind", "wind"), ("Gas CC", "gas")]:
        add(f"v6_capture_{key}", pct(cf.loc[t, "capture_factor"], 0), cf.loc[t, "capture_factor"], "results/candidate_capture_factors.csv", f"{t} capture factor on the 2024 North hub")
    m = re.search(r"(\d+)% of 2024", cf.loc["Gas CC", "basis"])
    add("v6_gas_hours", m.group(1) + "%", int(m.group(1)) / 100, "results/candidate_capture_factors.csv", "share of 2024 hours a gas CC runs")
    m = re.search(r"\$([\d.]+)k per MW-year", cf.loc["Storage", "basis"])
    add("v6_battery", "$" + m.group(1) + "k", float(m.group(1)) * 1e3, "results/candidate_capture_factors.csv", "battery revenue per MW-year, one cycle a day")
    grid = read("upstream_cost_grid.csv").set_index("item")
    add("v6_uplift_base", pct(grid.loc["uplift_share", "base"], 0), grid.loc["uplift_share", "base"], "results/upstream_cost_grid.csv", "uplift share, base")
    add("v6_lead_years", "two-year", 2, "results/upstream_cost_grid.csv", "lead time of the redevelopment")
    cs = read("cost_sensitivity.csv").set_index("assumption")
    r = cs.loc["uplift_share"]
    add("v6_uplift_low", pct(r["low_value"], 0), r["low_value"], "results/cost_sensitivity.csv", "uplift share, low")
    add("v6_uplift_high", pct(r["high_value"], 0), r["high_value"], "results/cost_sensitivity.csv", "uplift share, high")
    add("v6_book_at_uplift_low", "$" + money_b(r["book_npv_at_low"]), r["book_npv_at_low"], "results/cost_sensitivity.csv", "book NPV at the low uplift")
    add("v6_book_at_uplift_high", "$" + money_b(r["book_npv_at_high"]), r["book_npv_at_high"], "results/cost_sensitivity.csv", "book NPV at the high uplift")
    r = cs.loc["opex_usd_per_boe"]
    add("v6_opex_low", f"${r['low_value']:.0f}", r["low_value"], "results/cost_sensitivity.csv", "operating cost, low, $/boe")
    add("v6_opex_high", f"${r['high_value']:.0f}", r["high_value"], "results/cost_sensitivity.csv", "operating cost, high, $/boe")
    add("v6_book_at_opex_low", "$" + money_b(r["book_npv_at_low"]), r["book_npv_at_low"], "results/cost_sensitivity.csv", "book NPV at the low operating cost")
    add("v6_book_at_opex_high", "$" + money_b(r["book_npv_at_high"]), r["book_npv_at_high"], "results/cost_sensitivity.csv", "book NPV at the high operating cost")
    add("v6_power_basis_swing", "$0.5B", 0.5e9, "results/cost_sensitivity.csv", "the power price basis moves the book by under this")
    va = read("value_assumptions.csv") if (paths.RESULTS / "value_assumptions.csv").exists() else None
    add("v6_ppa_wind", "$62", 62, "results/value_assumptions.csv", "wind PPA, $/MWh (decision #61)")
    settings = read("scenario_settings.csv").iloc[0]
    add("v6_wti_2024", f"${settings['base_wti']:.0f}", settings["base_wti"], "results/scenario_settings.csv", "2024 real WTI, $/bbl")


def v6_scenarios():
    """Part II §18."""
    settings = read("scenario_settings.csv").iloc[0]
    add("v6_n_scen", f"{int(settings['n_scenarios']):,}", int(settings["n_scenarios"]), "results/scenario_settings.csv", "scenarios")
    add("v6_horizon_months", str(int(settings["horizon_months"])), int(settings["horizon_months"]), "results/scenario_settings.csv", "months per path")
    add("v6_block", str(int(settings["block_months"])), int(settings["block_months"]), "results/scenario_settings.csv", "block length, months")
    add("v6_half_life_years", "four-year", settings["half_life_months"] / 12, "results/scenario_settings.csv", "half-life of the reversion")
    add("v6_walk_low", "$13", 13, "docs/decisions.md #69", "WTI ten years out under the rejected random walk, low")
    add("v6_walk_high", "$800", 800, "docs/decisions.md #69", "WTI ten years out under the rejected random walk, high")
    add("v6_cost_mult_low", "0.75", 0.75, "src/scenarios.py", "cost multiplier, low")
    add("v6_cost_mult_high", "1.5", 1.5, "src/scenarios.py", "cost multiplier, high")
    draws = read("scenario_draws.csv")
    never = draws[draws["draw"].str.startswith("share of requests never")].iloc[0]["mean"]
    add("v6_never_operate", pct(never, 0), never, "results/scenario_draws.csv", "share of the twenty requests never operating within 7 y")
    bands = read("scenario_price_bands.csv")
    b = bands[(bands["series"] == "WTI") & (bands["year"] == 2034)].iloc[0]
    add("v6_wti_2034_q05", f"${b['q05']:.0f}", b["q05"], "results/scenario_price_bands.csv", "WTI 2034, 5th percentile")
    add("v6_wti_2034_q95", f"${b['q95']:.0f}", b["q95"], "results/scenario_price_bands.csv", "WTI 2034, 95th percentile")
    add("v6_band_low", "5", 5, "results/scenario_price_bands.csv", "lower percentile of the band")
    add("v6_band_high", "95%", 0.95, "results/scenario_price_bands.csv", "upper percentile of the band")
    ss = read("scenario_summary.csv")
    book = ss[(ss["project_id"] == "BOOK (default 40)") & (ss["generator"] == "primary") & (ss["revenue_case"] == "merchant")].iloc[0]
    add("v6_book_mean", "$" + money_b(book["mean"]), book["mean"], "results/scenario_summary.csv", "default book, mean NPV, merchant, primary scenarios")
    add("v6_book_p_neg", pct(book["p_negative"], 1), book["p_negative"], "results/scenario_summary.csv", "default book, P(NPV < 0)")
    add("v6_book_cvar_profit", "$" + money_b(-book["cvar"]), -book["cvar"], "results/scenario_summary.csv", "default book, CVaR95 as a profit")
    st = read("stress_tests.csv").set_index("stress")
    add("v6_stress_base", "$" + money_b(st.loc["base", "book_npv"], 2), st.loc["base", "book_npv"], "results/stress_tests.csv", "default book on the flat path, base")
    add("v6_stress_2020", "$" + money_b(st.loc["oil collapse (2020 path)", "book_npv"], 2), st.loc["oil collapse (2020 path)", "book_npv"], "results/stress_tests.csv", "default book under the 2020 oil path")
    add("v6_stress_worst", "$" + money_b(st.loc["simultaneous downside", "book_npv"], 2), st.loc["simultaneous downside", "book_npv"], "results/stress_tests.csv", "default book under the simultaneous downside")
    ab = read("correlation_ablation.csv")
    d = ab[ab["scenarios"].str.startswith("independent")].iloc[0]["cvar_difference_vs_joint"]
    add("v6_ablation_cvar", "$" + money_b(d), d, "results/correlation_ablation.csv", "CVaR change when the correlations are removed")


def v6_books():
    """Part II §19: C21–C24 and the books."""
    reg = read("success_criteria_v7_registered.json")
    led = read("decision_ledger.csv").set_index("entry_id")
    add("v6_budget", "$" + money_b(led.loc["NB09-D", "budget"], 2), led.loc["NB09-D", "budget"], "results/decision_ledger.csv", "registered budget")
    add("v6_budget_share", "40%", 0.4, "results/success_criteria_v7_registered.json", "budget as a share of the default book's capital")
    add("v6_cap", pct(led.loc["NB09-D", "technology_cap"], 0), led.loc["NB09-D", "technology_cap"], "results/decision_ledger.csv", "technology cap")
    add("v6_d_members", str(int(led.loc["NB09-D", "n_members"])), int(led.loc["NB09-D", "n_members"]), "results/decision_ledger.csv", "members of book D")
    add("v6_d_capex", "$" + money_b(led.loc["NB09-D", "capex"]), led.loc["NB09-D", "capex"], "results/decision_ledger.csv", "capital of book D")
    sc = read("portfolio_scores.csv")
    oos = sc[sc["scenarios"].str.startswith("held-out") & (sc["revenue_case"] == "contracted")].set_index("book")
    add("v6_d_npv_oos", "$" + money_b(oos.loc["D risk-aware MILP", "expected_npv"], 2), oos.loc["D risk-aware MILP", "expected_npv"], "results/portfolio_scores.csv", "book D, expected NPV out of sample")
    add("v6_a_npv_oos", "$" + money_b(oos.loc["A top-N NPV", "expected_npv"], 2), oos.loc["A top-N NPV", "expected_npv"], "results/portfolio_scores.csv", "book A, expected NPV out of sample")
    add("v6_d_p_neg_oos", pct(oos.loc["D risk-aware MILP", "p_negative"], 1), oos.loc["D risk-aware MILP", "p_negative"], "results/portfolio_scores.csv", "book D, P(NPV < 0) out of sample")
    v7 = read("success_criteria_v7_scored.csv").set_index("id")
    for cid in ["C21", "C22", "C24"]:
        r = v7.loc[cid]
        add(f"v6_{cid.lower()}_diff", money_m(r["diff"], sign=True).replace("+", "").replace("−", "−$") if r["diff"] < 0 else "+$" + money_m(r["diff"]), r["diff"], "results/success_criteria_v7_scored.csv", f"{cid} difference")
        add(f"v6_{cid.lower()}_low", ("−$" + money_m(-r["low"])) if r["low"] < 0 else "+$" + money_m(r["low"]), r["low"], "results/success_criteria_v7_scored.csv", f"{cid} interval, low")
        add(f"v6_{cid.lower()}_high", ("−$" + money_m(-r["high"])) if r["high"] < 0 else "+$" + money_m(r["high"]), r["high"], "results/success_criteria_v7_scored.csv", f"{cid} interval, high")
    stab = read("portfolio_stability.csv")
    add("v6_c23_d", f"{stab['jaccard_D'].mean():.2f}", stab["jaccard_D"].mean(), "results/portfolio_stability.csv", "C23: mean Jaccard of D under the stresses")
    add("v6_c23_c", f"{stab['jaccard_C'].mean():.2f}", stab["jaccard_C"].mean(), "results/portfolio_stability.csv", "C23: mean Jaccard of C under the stresses")
    add("v6_n_stresses", "six", 6, "results/portfolio_stability.csv", "named stresses")
    sens = read("portfolio_sensitivity.csv")
    add("v6_sens_low", f"{sens['jaccard_to_D'].min():.2f}", sens["jaccard_to_D"].min(), "results/portfolio_sensitivity.csv", "sensitivity: lowest Jaccard to D")
    add("v6_sens_high", f"{sens['jaccard_to_D'].max():.2f}", sens["jaccard_to_D"].max(), "results/portfolio_sensitivity.csv", "sensitivity: highest Jaccard to D")
    add("v6_sens_budget_cut", "20%", 0.2, "results/portfolio_sensitivity.csv", "sensitivity: budget cut")
    add("v6_sens_carbon", "$50", 50, "results/portfolio_sensitivity.csv", "sensitivity: carbon price, $/t")
    add("v6_sens_cap", "25%", 0.25, "results/portfolio_sensitivity.csv", "sensitivity: tighter cap")
    add("v6_c2124_lines", "4", 4, "results/success_criteria_v7_scored.csv", "C21–C24 lines")
    add("v6_c2124_pass", "0", 0, "results/success_criteria_v7_scored.csv", "C21–C24 lines passed")


def v6_advisor():
    """Part II §20–§21 and Appendix A: the gym, the forward view, the advisor's evaluation."""
    sit = read("decision_gym_situations.csv")
    gs = read("decision_gym_scores.csv")
    add("v6_gym_n", str(len(sit)), len(sit), "results/decision_gym_situations.csv", "gym situations")
    add("v6_gym_queue", str(int((sit["kind"] == "queue").sum())), int((sit["kind"] == "queue").sum()), "results/decision_gym_situations.csv", "queue situations")
    add("v6_gym_lease", str(int((sit["kind"] == "lease").sum())), int((sit["kind"] == "lease").sum()), "results/decision_gym_situations.csv", "lease regimes")
    add("v6_gym_empty", str(int((sit[sit["kind"] == "queue"]["hindsight_best_$M"] <= 0).sum())), int((sit[sit["kind"] == "queue"]["hindsight_best_$M"] <= 0).sum()), "results/decision_gym_situations.csv", "queue situations whose best book is empty")
    add("v6_gym_shortlist", "fifteen", 15, "src/gym.py", "largest requests shown per situation")
    opt_ = gs[gs["actor"] == "optimizer"]
    ins = gs[gs["actor"] == "instinct"]
    add("v6_gym_rule_vs_instinct", "$" + money_m(opt_["vs_instinct_$M"].mean() * 1e6), opt_["vs_instinct_$M"].mean(), "results/decision_gym_scores.csv", "registered rule minus instinct, mean per situation")
    add("v6_gym_regret_rule", "$" + money_m(opt_["regret_$M"].mean() * 1e6), opt_["regret_$M"].mean(), "results/decision_gym_scores.csv", "registered rule, mean regret against hindsight")
    add("v6_gym_regret_instinct", "$" + money_m(ins["regret_$M"].mean() * 1e6), ins["regret_$M"].mean(), "results/decision_gym_scores.csv", "instinct, mean regret against hindsight")
    gate = gs[gs["situation"] == "ERCOT 2017 2-year gate"].set_index("actor")
    add("v6_gym_gate_instinct", "$" + money_b(gate.loc["instinct", "realized_$M"] * 1e6, 2), gate.loc["instinct", "realized_$M"], "results/decision_gym_scores.csv", "ERCOT 2017 two-year gate: instinct's realized value")
    add("v6_gym_gate_rule", f"${gate.loc['optimizer', 'realized_$M']:.0f}", gate.loc["optimizer", "realized_$M"], "results/decision_gym_scores.csv", "ERCOT 2017 two-year gate: the rule's realized value")
    add("v6_gym_gate_operated", "five", 5, "results/decision_gym_situations.csv", "requests that operated at the ERCOT two-year gate")
    lease = gs[(gs["kind"] == "lease") & (gs["actor"] == "optimizer")]
    add("v6_gym_lease_match", str(int((lease["regret_$M"].abs() < 1e-6).sum())), int((lease["regret_$M"].abs() < 1e-6).sum()), "results/decision_gym_scores.csv", "lease regimes where the MILP matched hindsight")
    hv = read("horizon_view.csv")
    by = hv.groupby(["horizon_years", "sector"])["expected_npv_within_horizon"].sum().unstack()
    for h in (1, 3, 5, 10, 20):
        v = by.loc[h, "offshore oil and gas"]
        add(f"v6_hz_lease_{h}", ("−$" + money_b(-v)) if v < 0 else "$" + money_b(v), v, "results/horizon_view.csv", f"lease book within {h} years")
    v = by.loc[20, "ERCOT power"]
    add("v6_hz_power_20", "−$" + money_b(-v, 2), v, "results/horizon_view.csv", "requests within 20 years")
    hb = read("horizon_books.csv").set_index("horizon_years")
    for h in (3, 5, 10):
        add(f"v6_hz_members_{h}", str(int(hb.loc[h, "n_members"])), int(hb.loc[h, "n_members"]), "results/horizon_books.csv", f"members of the book at {h} years")
    ev = read("advisor_evaluation.csv").set_index("metric")
    add("v6_adv_recorded", str(ev.loc["recorded answers in advisor_runs.jsonl", "value"]), ev.loc["recorded answers in advisor_runs.jsonl", "value"], "results/advisor_evaluation.csv", "recorded answers")
    calls = str(ev.loc["calls this run (replayed / live / missing)", "value"]).split("/")[-1].strip()
    add("v6_adv_missing", calls, int(calls), "results/advisor_evaluation.csv", "calls with no record and no key")
    # the advisor scored (session 12, decision #76): the live run through the author's Claude subscription
    n_rec = sum(1 for line in (paths.RESULTS / "advisor_runs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())
    add("adv_recorded", str(n_rec), n_rec, "results/advisor_runs.jsonl", "recorded answers")
    rec = read("advisor_recommendations.csv")
    stress_rows = rec[~rec["scenario"].str.startswith("forward")]
    # a metric is "no record" when the replay missed calls (another machine's floating point builds other prompts,
    # decision #111): the key is kept with that text, so the report test points at it instead of this step failing
    for key, metric, fmt, note in [
            ("adv_grounding", "mean number-grounding rate over recorded answers", lambda v: f"{100 * v:.0f}%", "mean share of the advisor's numbers found in its tables"),
            ("adv_fully_grounded", "answers with every number grounded (share)", lambda v: f"{100 * v:.0f}%", "answers with every number grounded"),
            ("adv_jaccard_d", "mean Jaccard of recommended members to book D (stresses)", lambda v: f"{v:.2f}", "overlap of the advisor's book with book D over the seven stresses"),
            ("adv_names_d", "share naming book D (stresses)", lambda v: f"{int(round(v * len(stress_rows)))} of {len(stress_rows)}", "stresses in which the advisor names book D")]:
        v = pd.to_numeric(ev.loc[metric, "value"], errors="coerce")
        add(key, "no record" if pd.isna(v) else fmt(float(v)), float(v), "results/advisor_evaluation.csv", note)
    gs = read("decision_gym_scores.csv")
    advr = gs[gs["actor"] == "advisor"]
    add("adv_gym_vs_instinct", "$" + money_m(advr["vs_instinct_$M"].mean() * 1e6), advr["vs_instinct_$M"].mean(), "results/decision_gym_scores.csv", "advisor minus instinct, mean per situation")
    add("adv_gym_regret", "$" + money_m(advr["regret_$M"].mean() * 1e6), advr["regret_$M"].mean(), "results/decision_gym_scores.csv", "advisor: mean regret against hindsight")
    add("adv_gym_wins", str(int((advr["vs_instinct_$M"] > 0).sum())), int((advr["vs_instinct_$M"] > 0).sum()), "results/decision_gym_scores.csv", "situations in which the advisor beat instinct")
    add("adv_gym_ties", str(int((advr["vs_instinct_$M"].abs() < 1e-6).sum())), int((advr["vs_instinct_$M"].abs() < 1e-6).sum()), "results/decision_gym_scores.csv", "situations in which the advisor matched instinct")
    add("adv_gym_losses", str(int((advr["vs_instinct_$M"] < -1e-6).sum())), int((advr["vs_instinct_$M"] < -1e-6).sum()), "results/decision_gym_scores.csv", "situations in which the advisor did worse than instinct")
    ch = (paths.RESULTS / "advisor_transcripts" / "challenge_all_leases.md").read_text(encoding="utf-8")
    m = re.search(r"CONVERGE:\s*(.*?)\s*\|", ch)
    add("adv_challenge_converge", m.group(1).strip() if m else "no convergence line", 0, "results/advisor_transcripts/challenge_all_leases.md", "the opposing case's convergence line, all-leases statement")
    add("v6_adv_scenarios", "7", 7, "results/advisor_recommendations.csv", "named scenarios the advisor recommends for")
    add("v6_adv_horizons", "6", 6, "results/advisor_recommendations.csv", "horizons the advisor recommends for")
    add("v6_adv_min_chars", "20", 20, "src/advisor.py", "characters required per answer at the override gate")
    add("v6_adv_questions", "5", 5, "src/advisor.py", "questions of the motivated-reasoning check")
    add("v6_adv_small_int", "50", 50, "src/advisor.py", "integers exempt from the grounding check")
    add("v6_adv_temperature", "0", 0, "src/advisor.py", "temperature")
    add("v6_forty", "forty", 40, "results/candidate_npv.csv", "candidates")
    add("v6_hz_list", "1, 2, 3, 5, 10 and 20", 0, "src/horizons.py", "horizons, years")
    add("v6_grid_factor", "four", 4, "results/cost_sensitivity.csv", "the two largest grid items move the book by about this factor")


def rounded(new_key, from_key, fmt, note=""):
    """Record a rounded form of a number already collected (report v5 rounds in prose, keeps detail in tables)."""
    row = next(r for r in ROWS if r["key"] == from_key)
    value = float(row["value"])
    add(new_key, fmt(value), value, row["source"], note or f"rounded from {from_key}")


def v7_rounded():
    """Report v5, Part I: the rounded forms the prose uses (outside review of 14 Oct: round in prose, detail in tables)."""
    two = lambda v: f"{v:.2f}"
    p0 = lambda v: f"{100 * v:.0f}%"
    for new, old, fmt in [("r_auc3", "auc_dt_lgbm_3", two), ("r_auc3_base", "auc_baseline_3", two), ("r_c3_lookup", "c_large_fair_3", two),
                          ("r_lm_c", "lm_l2_ia_uno_c", two), ("r_lm_entry", "lm_l2_entry_uno_c", two), ("r_lm_gain", "lm_l2_ia_uno_c_diff", two),
                          ("r_lm_lookup", "lm_l2_fair_uno_c", two), ("r_sig_ercot_yes", "sig_ercot_yes", p0)]:
        rounded(new, old, fmt)
    cpi = pd.read_parquet(paths.DATA_INTERIM / "cpi_monthly.parquet")
    ratio = cpi[cpi["month"].dt.year == 2024]["cpi_u"].mean() / cpi[cpi["month"].dt.year == 2022]["cpi_u"].mean()
    add("r_cpi_2022_2024", f"{ratio:.2f}", ratio, "data/interim/cpi_monthly.parquet", "CPI-U 2024 mean over 2022 mean")


def v7_posthoc():
    """Report v5, Part II: the committee grid, the medians, the oil stresses, the books under the committee grid (notebook 09 part E)."""
    b = lambda v, d=1: f"{v / 1e9:.{d}f}"
    grid = read("posthoc_committee_grid.csv").set_index("item")
    for case in ("low", "base", "high"):
        v = grid.loc["dev_cost_per_flowing_boed_usd", case]
        add(f"ph_dev_cost_{case}", f"{v:,.0f}", v, "results/posthoc_committee_grid.csv", f"committee grid: capital per flowing boe/d, {case}")
        w = grid.loc["wacc_real", case]
        add(f"ph_wacc_{case}", f"{100 * w:.1f}%" if case == "low" else f"{100 * w:.0f}%", w, "results/posthoc_committee_grid.csv", f"committee grid: real rate, {case}")
    lv = read("posthoc_lease_values.csv")
    for col, key in [("npv_base", "ph_lease_npv_base"), ("npv_low", "ph_lease_npv_low"), ("npv_high", "ph_lease_npv_high"),
                     ("capex_base", "ph_lease_capex"), ("capex_registered", "ph_lease_capex_registered"), ("npv_registered_base", "ph_lease_npv_registered")]:
        v = lv[col].sum()
        add(key, b(v, 2 if "capex" in col else 1), v, "results/posthoc_lease_values.csv", col)
    add("ph_lease_positive", str(int((lv["npv_base"] > 0).sum())), int((lv["npv_base"] > 0).sum()), "results/posthoc_lease_values.csv", "leases positive at base, committee grid")
    cand = read("candidate_npv.csv")
    leases = cand[cand["sector"] != "ERCOT power"]
    for col, key in [("expected_npv_low_cost", "ph_reg_low"), ("expected_npv_high_cost", "ph_reg_high")]:
        add(key, b(leases[col].sum()), leases[col].sum(), "results/candidate_npv.csv", f"registered grid, {col}")
    dist = read("posthoc_book_distribution.csv").set_index(["book", "grid"])
    for grid_name in ("registered", "committee"):
        r = dist.loc[("default book of forty", grid_name)]
        g = grid_name[:3]
        add(f"ph_default_mean_{g}", b(r["mean"]), r["mean"], "results/posthoc_book_distribution.csv", f"default book mean, {grid_name}")
        add(f"ph_default_median_{g}", b(r["median"]), r["median"], "results/posthoc_book_distribution.csv", f"default book median, {grid_name}")
        add(f"ph_default_q05_{g}", b(r["q05"]), r["q05"], "results/posthoc_book_distribution.csv", f"default book 5th percentile, {grid_name}")
        add(f"ph_default_pneg_{g}", f"{100 * r['p_negative']:.1f}%", r["p_negative"], "results/posthoc_book_distribution.csv", f"default book P(loss), {grid_name}")
        add(f"ph_default_pneg0_{g}", f"{100 * r['p_negative']:.0f}%", r["p_negative"], "results/posthoc_book_distribution.csv", f"default book P(loss), rounded, {grid_name}")
        add(f"ph_default_cvar_{g}", b(r["cvar95_loss"]), r["cvar95_loss"], "results/posthoc_book_distribution.csv", f"default book CVaR95 loss, {grid_name}")
    stress = pd.read_csv(paths.RESULTS / "posthoc_oil_stress.csv").set_index("stress")
    for name, key in [("flat 2024 base", "flat"), ("2020 shape from month one", "2020"), ("sustained $42 for five years", "sustained")]:
        for grid_name, d in (("registered", 1), ("committee", 2)):
            v = stress.loc[name, grid_name]
            add(f"ph_oil_{key}_{grid_name[:3]}", b(v, d), v, "results/posthoc_oil_stress.csv", f"lease book, {name}, {grid_name}")
    add("ph_oil_price", "$42", 42.0, "notebook 09 part E", "sustained WTI, real 2024 $/bbl (ASSUMED)")
    flat = read("stress_tests.csv").set_index("stress").loc["base", "book_npv"]
    add("ph_flat_book", b(flat), flat, "results/stress_tests.csv", "default book on the flat 2024 path")
    bc = read("posthoc_books_committee.csv").set_index("book")
    short = {"A top-N NPV": "a", "B equal capital": "b", "C deterministic MILP": "c", "D risk-aware MILP": "d"}
    for name, k in short.items():
        r = bc.loc[name]
        add(f"ph_book_{k}_n", str(int(r["n_selected"])), int(r["n_selected"]), "results/posthoc_books_committee.csv", f"{name}: members")
        for col in ("mean", "median", "cvar95_loss", "capex"):
            add(f"ph_book_{k}_{col}", b(r[col]), r[col], "results/posthoc_books_committee.csv", f"{name}: {col}")
        add(f"ph_book_{k}_pneg", f"{100 * r['p_negative']:.0f}%", r["p_negative"], "results/posthoc_books_committee.csv", f"{name}: P(loss)")
    gap = bc.loc["A top-N NPV", "mean"] - bc.loc["D risk-aware MILP", "mean"]
    add("ph_gap_a_d", b(gap), gap, "results/posthoc_books_committee.csv", "A minus D, expected NPV")
    dva = read("posthoc_d_vs_a_committee.csv").iloc[0]
    add("ph_dva", f"{abs(dva['diff']) / 1e6:,.0f}", dva["diff"], "results/posthoc_d_vs_a_committee.csv", "D minus A on the metric, committee grid")
    cap = read("posthoc_lease_values.csv")
    total_capex = cap["capex_base"].sum() + cand.loc[cand["sector"] == "ERCOT power", "capex"].sum()
    add("ph_budget", b(0.40 * total_capex, 2), 0.40 * total_capex, "results/posthoc_lease_values.csv; results/candidate_npv.csv", "committee-grid budget: 40% of the forty's capital")
    sc_ = pd.read_parquet(paths.DATA_PROCESSED / "candidate_npv_scenarios.parquet")
    gas = list(cand.loc[cand["technology"] == "Gas CC", "project_id"])
    part = sc_[(sc_["generator"] == "primary") & (sc_["revenue_case"] == "contracted")]
    v = part[gas].sum(axis=1).mean()
    add("ph_gas_scen_mean", f"${v / 1e6:.0f}M", v, "data/processed/candidate_npv_scenarios.parquet", "the five gas requests, mean across primary scenarios")
    reg = read("portfolio_scores.csv")
    oos = reg[reg["scenarios"].str.startswith("held-out") & (reg["revenue_case"] == "contracted")].set_index("book")
    for name, k in (("A top-N NPV", "a"), ("D risk-aware MILP", "d")):
        add(f"ph_reg_{k}_mean", b(oos.loc[name, "expected_npv"]), oos.loc[name, "expected_npv"], "results/portfolio_scores.csv", f"registered {name}, held-out mean")
    # the record totals of Appendix A, counted from the scored files (registered lines only)
    def count(name, column="result", registered_only=False):
        d = read(name)
        if registered_only:
            d = d[d["registered"]]
        passed = d[column].astype(str).str.upper().isin(["PASS", "TRUE"])
        return len(d), int(passed.sum())
    parts = [count("success_criteria.csv"), count("success_criteria_v2_scored.csv"), count("success_criteria_v3_scored.csv"),
             count("success_criteria_v4_scored.csv", "pass"), count("success_criteria_v5_scored.csv"),
             count("success_criteria_v6_scored.csv", registered_only=True), count("success_criteria_v7_scored.csv")]
    total, passed = sum(n for n, _ in parts), sum(k for _, k in parts)
    add("ph_record_lines", str(total), total, "results/success_criteria*_scored.csv", "registered lines, all criteria")
    add("ph_record_pass", str(passed), passed, "results/success_criteria*_scored.csv", "registered lines passed")


def v7_questions():
    """Report v5: the energy EDA facts and the answers to the proposal's five decision questions."""
    q = read("eda_energy_quality.csv").set_index("series").loc["lease-months (BSEE)"]
    add("q_lease_zero", str(q["zero or missing"]), q["zero or missing"], "results/eda_energy_quality.csv", "lease-months with no oil or gas")
    add("q_lease_months", f"{int(q['rows']):,}", int(q["rows"]), "results/eda_energy_quality.csv", "lease-months in the panel")
    corr = read("eda_cross_sector_correlation.csv").set_index("Unnamed: 0")
    for a, b_, key in (("WTI", "Henry Hub", "q_corr_wti_hh"), ("Henry Hub", "ERCOT", "q_corr_hh_ercot"), ("Wind CF", "Gas CC CF", "q_corr_wind_gas")):
        v = corr.loc[a, b_]
        add(key, f"{v:.2f}".replace("-", "−"), v, "results/eda_cross_sector_correlation.csv", f"monthly correlation, {a} and {b_}")
    sens = read("portfolio_sensitivity.csv").set_index("change")
    v = sens.loc[[c for c in sens.index if c.startswith("budget")][0], "jaccard_to_D"]
    add("q_budget_jaccard", f"{v:.2f}", v, "results/portfolio_sensitivity.csv", "overlap with book D after a budget cut of a fifth")
    for prefix, key, note in (("carbon", "q_carbon_jaccard", "a carbon price on the gas plants' emissions"), ("λ", "q_lambda_jaccard", "the weight on the tail doubled")):
        v = sens.loc[[c for c in sens.index if c.startswith(prefix)][0], "jaccard_to_D"]
        add(key, f"{v:.2f}", v, "results/portfolio_sensitivity.csv", f"overlap with book D under {note} (proposal §10)")
    stab = read("portfolio_stability.csv").set_index("stress")
    for stress, key in (("oil collapse (2020 path)", "q_stab_oil"), ("high gas, low spark spread", "q_stab_gas")):
        v = stab.loc[stress, "jaccard_D"]
        add(key, f"{v:.2f}", v, "results/portfolio_stability.csv", f"overlap of book D with itself under {stress}")
    abl = read("portfolio_ablations.csv").set_index("ablation")
    v = abl.loc[[c for c in abl.index if c.startswith("no oil and gas")][0], "p_negative"]
    add("q_power_only_pneg", f"{100 * v:.0f}%", v, "results/portfolio_ablations.csv", "power-only book: chance of a loss")
    lv = read("posthoc_lease_values.csv")
    n_neg = int((lv["npv_high"] < 0).sum())
    add("q_leases_neg_high", str(n_neg), n_neg, "results/posthoc_lease_values.csv", "leases negative at the committee grid's high case")
    add("q_leases_pos_high", str(len(lv) - n_neg), len(lv) - n_neg, "results/posthoc_lease_values.csv", "leases positive at the committee grid's high case")
    ab = read("posthoc_ablation_naive_forecasts.csv")
    nv = ab[ab["book"].str.contains("naive")].iloc[0]
    add("q_ablation_n", str(int(nv["n_selected"])), int(nv["n_selected"]), "results/posthoc_ablation_naive_forecasts.csv", "book D re-solved with naive output errors: members")
    gs = read("decision_gym_scores.csv")
    rule = gs[gs["actor"] == "optimizer"]
    ins = gs[gs["actor"] == "instinct"]
    add("q_gym_rule_vs_instinct", f"${rule['vs_instinct_$M'].mean():,.0f}M", rule["vs_instinct_$M"].mean(), "results/decision_gym_scores.csv", "rule minus instinct, mean per situation")
    add("q_gym_regret_rule", f"${rule['regret_$M'].mean():,.0f}M", rule["regret_$M"].mean(), "results/decision_gym_scores.csv", "rule: mean regret against hindsight")
    add("q_gym_regret_instinct", f"${ins['regret_$M'].mean():,.0f}M", ins["regret_$M"].mean(), "results/decision_gym_scores.csv", "instinct: mean regret against hindsight")
    kind = read("decision_gym_by_kind.csv").set_index("kind")
    add("q_gym_lease_mean", f"${kind.loc['lease', 'mean_$M'] / 1e3:.1f}B", kind.loc["lease", "mean_$M"], "results/decision_gym_by_kind.csv", "lease regimes: rule minus instinct, mean")
    add("q_gym_queue_mean", f"${kind.loc['queue', 'mean_$M']:.1f}M", kind.loc["queue", "mean_$M"], "results/decision_gym_by_kind.csv", "queue rooms: rule minus instinct, mean")
    add("q_gym_n_queue", str(int(kind.loc["queue", "situations"])), int(kind.loc["queue", "situations"]), "results/decision_gym_by_kind.csv", "queue rooms")
    rooms = read("decision_gym_rooms.csv").set_index("situation")
    v = rooms.loc["ERCOT 2017 2-year gate", "rule_minus_instinct"]
    add("q_gym_ercot_gate", f"${v:,.0f}M", v, "results/decision_gym_rooms.csv", "ERCOT 2017 two-year room: rule minus instinct")
    # the gym room by room (the Petrobras report's Stage 8 table): instinct and the rule, $M for queue rooms, $B for the lease regimes
    for situation, r in rooms.iterrows():
        slug = re.sub(r"[^a-z0-9]+", "_", situation.lower()).strip("_")
        if r["kind"] == "lease":
            add(f"room_{slug}_instinct", f"${r['instinct'] / 1e3:.1f}B", r["instinct"], "results/decision_gym_rooms.csv", f"{situation}: instinct's realized value")
            add(f"room_{slug}_rule", f"${r['optimizer'] / 1e3:.1f}B", r["optimizer"], "results/decision_gym_rooms.csv", f"{situation}: the rule's realized value")
            add(f"room_{slug}_diff", f"+${r['rule_minus_instinct'] / 1e3:.1f}B", r["rule_minus_instinct"], "results/decision_gym_rooms.csv", f"{situation}: rule minus instinct")
        else:
            add(f"room_{slug}_instinct", f"${r['instinct']:,.0f}M", r["instinct"], "results/decision_gym_rooms.csv", f"{situation}: instinct's realized value")
            add(f"room_{slug}_rule", f"${r['optimizer']:,.0f}M", r["optimizer"], "results/decision_gym_rooms.csv", f"{situation}: the rule's realized value")
            d = r["rule_minus_instinct"]
            add(f"room_{slug}_diff", (f"${d:,.1f}M" if abs(d) < 10 else f"${d:,.0f}M"), d, "results/decision_gym_rooms.csv", f"{situation}: rule minus instinct")
    sit = read("decision_gym_situations.csv")
    q = sit[sit["kind"] == "queue"]
    add("q_gym_empty", str(int((q["hindsight_best_$M"] <= 0).sum())), int((q["hindsight_best_$M"] <= 0).sum()), "results/decision_gym_situations.csv", "queue rooms where no drawn request operated")
    add("q_ablation_jaccard", f"{nv['jaccard_to_registered_D']:.2f}", nv["jaccard_to_registered_D"], "results/posthoc_ablation_naive_forecasts.csv", "overlap with the registered book D")


def v8_bridged():
    """Appendix A: the registered record as first scored on the bridged ERCOT prices (results/registered_bridged/, decision #80)."""
    folder = "registered_bridged/"
    v6 = read(folder + "success_criteria_v6_scored.csv")
    reg = v6[v6["registered"]]
    add("rb_c20_pass", str(int((reg["result"] == "PASS").sum())), int((reg["result"] == "PASS").sum()), "results/registered_bridged/success_criteria_v6_scored.csv", "C20 lines passed, bridged prices")
    v7 = read(folder + "success_criteria_v7_scored.csv").set_index("id")
    add("rb_c21_24_pass", str(int((v7["result"] == "PASS").sum())), int((v7["result"] == "PASS").sum()), "results/registered_bridged/success_criteria_v7_scored.csv", "C21–C24 lines passed, bridged prices")
    for cid in ["C21", "C22", "C24"]:
        r = v7.loc[cid]
        add(f"rb_{cid.lower()}_diff", ("−$" + money_m(-r["diff"])) if r["diff"] < 0 else "+$" + money_m(r["diff"]), r["diff"], "results/registered_bridged/success_criteria_v7_scored.csv", f"{cid} difference, bridged prices")
        add(f"rb_{cid.lower()}_low", ("−$" + money_m(-r["low"])) if r["low"] < 0 else "+$" + money_m(r["low"]), r["low"], "results/registered_bridged/success_criteria_v7_scored.csv", f"{cid} interval low, bridged prices")
        add(f"rb_{cid.lower()}_high", ("−$" + money_m(-r["high"])) if r["high"] < 0 else "+$" + money_m(r["high"]), r["high"], "results/registered_bridged/success_criteria_v7_scored.csv", f"{cid} interval high, bridged prices")
    sc = read(folder + "portfolio_scores.csv")
    oos = sc[sc["scenarios"].str.startswith("held-out") & (sc["revenue_case"] == "contracted")].set_index("book")
    for name, k in (("A top-N NPV", "a"), ("D risk-aware MILP", "d")):
        add(f"rb_{k}_npv_oos", "$" + money_b(oos.loc[name, "expected_npv"]), oos.loc[name, "expected_npv"], "results/registered_bridged/portfolio_scores.csv", f"{name}, held-out mean, bridged prices")
        add(f"rb_{k}_cvar_oos", ("−$" + money_b(-oos.loc[name, "cvar_loss"])) if oos.loc[name, "cvar_loss"] < 0 else "$" + money_b(oos.loc[name, "cvar_loss"]), oos.loc[name, "cvar_loss"], "results/registered_bridged/portfolio_scores.csv", f"{name}, CVaR95 loss, bridged prices")
    bc = read(folder + "posthoc_books_committee.csv").set_index("book")
    for name, k in (("A top-N NPV", "a"), ("D risk-aware MILP", "d")):
        add(f"rb_book_{k}_mean", "$" + money_b(bc.loc[name, "mean"]), bc.loc[name, "mean"], "results/registered_bridged/posthoc_books_committee.csv", f"{name}: mean, committee grid, bridged prices")
        add(f"rb_book_{k}_cvar", "$" + money_b(bc.loc[name, "cvar95_loss"]), bc.loc[name, "cvar95_loss"], "results/registered_bridged/posthoc_books_committee.csv", f"{name}: worst-5% loss, committee grid, bridged prices")
    add("rb_bridge_ratio", "0.77", 0.77, "src/config.py", "the bridge: ERCOT 2020–2023 = PJM West × this")
    # the observed ERCOT history and the engine's cap (decisions #78, #81)
    from src import scenarios
    add("sc_cap", f"{scenarios.MAX_MONTHLY_LOG_CHANGE:g}", scenarios.MAX_MONTHLY_LOG_CHANGE, "src/scenarios.py", "cap on a monthly log change (ASSUMED)")
    add("sc_cap_factor", f"×{np.exp(scenarios.MAX_MONTHLY_LOG_CHANGE):.1f}", np.exp(scenarios.MAX_MONTHLY_LOG_CHANGE), "src/scenarios.py", "the cap as a price multiple within a month")
    market = pd.read_parquet(paths.DATA_INTERIM / "market_monthly.parquet").set_index("month")["ercot_usd_mwh_real2024"]
    before, peak = market.loc["2021-01-01"], market.loc["2021-02-01"]
    add("uri_before", f"${before:,.0f}", before, "data/interim/market_monthly.parquet", "ERCOT North, January 2021, real 2024 $/MWh")
    add("uri_peak", f"${peak:,.0f}", peak, "data/interim/market_monthly.parquet", "ERCOT North, February 2021 (Winter Storm Uri), real 2024 $/MWh")
    add("uri_ratio", f"×{peak / before:.0f}", peak / before, "data/interim/market_monthly.parquet", "the Uri month as a multiple of the month before")
    add("uri_log_up", f"+{np.log(peak / before):.1f}", np.log(peak / before), "data/interim/market_monthly.parquet", "log change into the Uri month")
    after = market.loc["2021-03-01"]
    add("uri_log_down", f"−{-np.log(after / peak):.1f}", np.log(after / peak), "data/interim/market_monthly.parquet", "log change out of the Uri month")
    by_year = market.groupby(market.index.year).mean()
    for y in (2021,):
        add(f"ercot_mean_{y}", f"${by_year.loc[y]:,.0f}", by_year.loc[y], "data/interim/market_monthly.parquet", f"ERCOT North annual mean, {y}, real 2024 $/MWh")
    assumed = int((pd.read_parquet(paths.DATA_INTERIM / "market_monthly.parquet")["ercot_provenance"] == "ASSUMED").sum())
    add("ercot_assumed_months", str(assumed), assumed, "data/interim/market_monthly.parquet", "ERCOT months still assumed")


def dollars(x, unit="B", digits=2, sign=False):
    """Money as the v8 report writes it: ``$1.92B``, ``−$146M``, ``+$293M``."""
    v = x / (1e9 if unit == "B" else 1e6)
    body = f"{abs(v):,.{digits}f}{unit}"
    return ("−" if v < 0 else ("+" if sign else "")) + "$" + body


def v8_report():
    """Report v8: the decision date, the decision system of notebook 11, the rebuilt gym and the frozen record (decisions #88–#92)."""
    v8 = "results/v8/"
    bt = read("decision_date_backtest.csv").set_index(["decision_date", "method", "region"])
    e20 = bt.loc[("2020-01-01", "model", "ERCOT")]
    add("v8_bt_ercot_pred", f"{e20['predicted_p5']:.3f}", e20["predicted_p5"], "results/decision_date_backtest.csv", "ERCOT five-year chance predicted as of 2020")
    add("v8_bt_ercot_obs", f"{e20['observed_p5']:.3f}", e20["observed_p5"], "results/decision_date_backtest.csv", "ERCOT five-year share observed")
    for m in ("model", "lookup"):
        r = bt.loc[("2020-01-01", m, "all")]
        add(f"v8_bt_auc_{m}", f"{r['auc']:.3f}", r["auc"], "results/decision_date_backtest.csv", f"AUC as of 2020, {m}")
    live = read("decision_date_live_requests.csv")
    add("v8_live_gw", f"{live['gw'].sum():,.0f}", live["gw"].sum(), "results/decision_date_live_requests.csv", "GW of live ERCOT requests")
    add("v8_live_n", f"{int(live['requests'].sum()):,}", int(live["requests"].sum()), "results/decision_date_live_requests.csv", "live ERCOT requests")
    base = pd.read_csv(paths.RESULTS / "v8" / "base_books.csv").set_index("grid")
    add("v8_budget", dollars(base.loc["committee", "budget"]), base.loc["committee", "budget"], v8 + "base_books.csv", "committee budget")
    add("v8_reg_mean", dollars(base.loc["registered", "mean"]), base.loc["registered", "mean"], v8 + "base_books.csv", "registered grid book D mean")
    add("v8_D_leases", str(int(base.loc["committee", "leases"])), int(base.loc["committee", "leases"]), v8 + "base_books.csv", "leases in book D")
    add("v8_D_requests", str(int(base.loc["committee", "requests"])), int(base.loc["committee", "requests"]), v8 + "base_books.csv", "requests in book D")
    add("v8_reg_leases", str(int(base.loc["registered", "leases"])), int(base.loc["registered", "leases"]), v8 + "base_books.csv", "leases in registered book D")
    fr = pd.read_csv(paths.RESULTS / "v8" / "frontier.csv").set_index("policy")
    for key, pol in (("lam0", "lambda 0"), ("lam1", "lambda 1"), ("lam2", "lambda 2")):
        add(f"v8_{key}_mean", dollars(fr.loc[pol, "mean"]), fr.loc[pol, "mean"], v8 + "frontier.csv", f"{pol}: mean")
        add(f"v8_{key}_cvar", dollars(fr.loc[pol, "cvar_loss"]), fr.loc[pol, "cvar_loss"], v8 + "frontier.csv", f"{pol}: CVaR loss")
    pc = pd.read_csv(paths.RESULTS / "v8" / "process_comparison.csv")
    pc["key"] = pc["process"].str[0]
    for _, r in pc.drop_duplicates("key").iterrows():
        k = r["key"]
        n = r["members"].count(";") + 1
        add(f"v8_p{k}_n", str(n), n, v8 + "process_comparison.csv", f"process {k}: candidates")
        add(f"v8_p{k}_mean", f"{r['mean'] / 1e9:.2f}", r["mean"], v8 + "process_comparison.csv", f"process {k}: mean $B")
        add(f"v8_p{k}_cvar", f"{r['cvar_loss'] / 1e9:.2f}", r["cvar_loss"], v8 + "process_comparison.csv", f"process {k}: CVaR $B")
        add(f"v8_p{k}_ploss", pct(r["p_loss"], 0), r["p_loss"], v8 + "process_comparison.csv", f"process {k}: chance of a loss")
        add(f"v8_p{k}_regret", f"{r['regret_vs_hindsight'] / 1e9:.2f}", r["regret_vs_hindsight"], v8 + "process_comparison.csv", f"process {k}: regret $B")
    va = pd.read_csv(paths.RESULTS / "v8" / "value_added.csv")

    def row(p, a):
        return va[(va["process"] == p) & (va["against"] == a)].iloc[0]

    for key, p, a in (("DA", "D risk-aware MILP", "A NPV ranking"), ("DB", "D risk-aware MILP", "B equal capital by sector"), ("DC", "D risk-aware MILP", "C deterministic MILP"),
                      ("ML", "D risk-aware MILP", "F (the ML increment), model's scenarios"), ("MLL", "D risk-aware MILP", "F (the ML increment), lookup's scenarios")):
        r = row(p, a)
        for c in ("metric_diff", "metric_low", "metric_high"):
            add(f"v8_{key}_{c}", dollars(r[c], "M", 0, sign=True), r[c], v8 + "value_added.csv", f"{p} vs {a}: {c}")
        if pd.notna(r.get("mean_diff")):
            add(f"v8_{key}_mean_diff", dollars(abs(r["mean_diff"]), "M", 0), r["mean_diff"], v8 + "value_added.csv", f"{p} vs {a}: expected NPV difference, magnitude")
    flex = row("D + revision in 2027", "D risk-aware MILP (the value of flexibility)")
    for c in ("mean_diff", "mean_low", "mean_high"):
        add(f"v8_flex_{c}", dollars(flex[c], "M", 0), flex[c], v8 + "value_added.csv", f"value of flexibility: {c}")
    dyn = pd.read_csv(paths.RESULTS / "v8" / "dynamic.csv")
    add("v8_reserve_over", pct(dyn.loc[0, "construction_over_reserve_share"], 0), dyn.loc[0, "construction_over_reserve_share"], v8 + "dynamic.csv", "scenarios where construction exceeds the reserve")
    voi = pd.read_csv(paths.RESULTS / "v8" / "value_of_information.csv")
    evpi = voi.loc[voi["kind"] == "EVPI", "value"].iloc[0]
    add("v8_evpi", dollars(evpi, "M", 0), evpi, v8 + "value_of_information.csv", "EVPI")
    for name, key in (("ERCOT price level 2025–2029", "ercot"), ("oil price level 2025–2029", "oil"), ("lease cost draw", "cost")):
        v = voi.loc[voi["information"] == name, "value"].iloc[0]
        add(f"v8_pevpi_{key}", dollars(v, "M", 0), v, v8 + "value_of_information.csv", f"partial EVPI, {name}")
    ev = voi[voi["kind"] == "EVSI"]
    add("v8_evsi_min", dollars(ev["value"].min(), "M", 1), ev["value"].min(), v8 + "value_of_information.csv", "smallest EVSI of an agreement signal")
    add("v8_evsi_max", dollars(ev["value"].max(), "M", 1), ev["value"].max(), v8 + "value_of_information.csv", "largest EVSI of an agreement signal")
    st = pd.read_csv(paths.RESULTS / "v8" / "statuses.csv")["status"].value_counts()
    for k in ("invest now", "invest in stages", "defer pending information", "monitor", "reject"):
        add(f"v8_status_{k.replace(' ', '_')}", str(int(st.get(k, 0))), int(st.get(k, 0)), v8 + "statuses.csv", f"candidates with status {k}")
    ex = pd.read_csv(paths.RESULTS / "v8" / "explanations.csv").set_index("project_id")
    cand = read("candidate_npv.csv").set_index("project_id")
    w, g = "REQ|ERCOT|26INR0113", "REQ|ERCOT|25INR0008"
    add("v8_wind_mw", f"{cand.loc[w, 'mw']:,.0f}", cand.loc[w, "mw"], "results/candidate_npv.csv", "the agreement-backed wind request, MW")
    add("v8_wind_cost", dollars(ex.loc[w, "objective_cost_$M"] * 1e6, "M", 0), ex.loc[w, "objective_cost_$M"], v8 + "explanations.csv", "its opportunity cost")
    add("v8_gas_mw", f"{cand.loc[g, 'mw']:,.0f}", cand.loc[g, "mw"], "results/candidate_npv.csv", "the largest gas request, MW")
    add("v8_gas_mean", dollars(ex.loc[g, "expected_npv_$M"] * 1e6, "M", 0), ex.loc[g, "expected_npv_$M"], v8 + "explanations.csv", "its expected NPV")
    add("v8_gas_pneg", pct(ex.loc[g, "p_negative"], 0), ex.loc[g, "p_negative"], v8 + "explanations.csv", "its chance of a loss")
    leases = cand[cand["sector"] != "ERCOT power"]
    add("v8_lease_reg", dollars(leases["expected_npv_base"].sum()), leases["expected_npv_base"].sum(), "results/candidate_npv.csv", "lease book, registered grid")
    add("v8_lease_reg_low", dollars(leases["expected_npv_low_cost"].sum()), leases["expected_npv_low_cost"].sum(), "results/candidate_npv.csv", "lease book, registered low case")
    add("v8_lease_reg_high", dollars(leases["expected_npv_high_cost"].sum()), leases["expected_npv_high_cost"].sum(), "results/candidate_npv.csv", "lease book, registered high case")
    pl = read("posthoc_lease_values.csv")
    for c in ("npv_base", "npv_low", "npv_high", "capex_base"):
        add(f"v8_lease_com_{c}", dollars(pl[c].sum()), pl[c].sum(), "results/posthoc_lease_values.csv", f"lease book, committee grid, {c}")
    add("v8_lease_com_high_pos", str(int((pl["npv_high"] > 0).sum())), int((pl["npv_high"] > 0).sum()), "results/posthoc_lease_values.csv", "leases positive at the committee high case")
    reg = pd.read_csv(paths.RESULTS / "registered_v7" / "success_criteria_v7_scored.csv").set_index("id")
    cur = read("success_criteria_v7_scored.csv").set_index("id")
    for cid in ("C21", "C22", "C24"):
        for tag, table, src in (("rv7", reg, "results/registered_v7/success_criteria_v7_scored.csv"), ("v8", cur, "results/success_criteria_v7_scored.csv")):
            for c in ("diff", "low", "high"):
                add(f"{tag}_{cid.lower()}_{c}", dollars(table.loc[cid, c], "M", 0, sign=True), table.loc[cid, c], src, f"{cid} {c}, {'as registered and scored' if tag == 'rv7' else 'on the corrected system'}")
    frozen = pd.read_csv(paths.RESULTS / "registered_v7" / "candidate_npv.csv")
    old = frozen[frozen["sector"] != "ERCOT power"]["expected_npv_base"].sum()
    add("v7_lease_reg", dollars(old, digits=1), old, "results/registered_v7/candidate_npv.csv", "lease book as scored in v7")
    hz = read("horizon_books.csv").set_index("horizon_years")
    add("v8_hz20", dollars(hz.loc[20, "expected_npv_within_horizon_$B"] * 1e9), hz.loc[20, "expected_npv_within_horizon_$B"], "results/horizon_books.csv", "best book within 20 years")
    add("v8_hz3_leases", str(int(hz.loc[3, "n_leases"])), int(hz.loc[3, "n_leases"]), "results/horizon_books.csv", "leases at three years")
    add("v8_hz5_leases", str(int(hz.loc[5, "n_leases"])), int(hz.loc[5, "n_leases"]), "results/horizon_books.csv", "leases from five years")
    gs = read("decision_gym_summary_v8.csv").set_index("comparison")
    for key, comp in (("ri", "optimizer minus instinct"), ("rp", "optimizer minus instinct per dollar"), ("ar", "advisor minus optimizer")):
        r = gs.loc[comp]
        small = abs(r["mean_$M"]) < 10
        add(f"v8_gym_{key}", dollars(abs(r["mean_$M"]) * 1e6, "M", 1 if small else 0), r["mean_$M"], "results/decision_gym_summary_v8.csv", comp + ", magnitude")
        add(f"v8_gym_{key}_low", dollars(r["low_$M"] * 1e6, "M", 1 if small else 0, sign=True), r["low_$M"], "results/decision_gym_summary_v8.csv", comp + ", low")
        add(f"v8_gym_{key}_high", dollars(r["high_$M"] * 1e6, "M", 1 if small else 0, sign=True), r["high_$M"], "results/decision_gym_summary_v8.csv", comp + ", high")
        add(f"v8_gym_{key}_worse", str(int(r["worse"])), int(r["worse"]), "results/decision_gym_summary_v8.csv", comp + ", situations worse")
    add("v8_gym_n", str(int(gs["situations"].iloc[0])), int(gs["situations"].iloc[0]), "results/decision_gym_summary_v8.csv", "effective situations")
    rooms = read("decision_gym_rooms.csv")
    q = rooms[rooms["kind"] == "queue"]["rule_minus_instinct"].mean()
    add("v8_gym_queue", dollars(abs(q) * 1e6, "M", 1), q, "results/decision_gym_rooms.csv", "rule minus instinct per queue room, magnitude")
    cap = read("candidate_capture_factors.csv").set_index("technology")
    add("v8_capture_gas", pct(cap.loc["Gas CC", "capture_factor"], 0), cap.loc["Gas CC", "capture_factor"], "results/candidate_capture_factors.csv", "gas capture")
    ae = read("advisor_evaluation.csv").set_index("metric")["value"]
    calls = int(ae["recorded answers in advisor_runs.jsonl"])
    add("v8_adv_calls", str(calls), calls, "results/advisor_evaluation.csv", "recorded advisor calls")
    add("v8_adv_grounding", pct(float(ae["mean number-grounding rate over recorded answers"]), 0), float(ae["mean number-grounding rate over recorded answers"]), "results/advisor_evaluation.csv", "grounding rate")
    tools = pd.read_csv(paths.RESULTS / "v8" / "advisor_tools_eval.csv")
    answered = tools[tools["status"] == "answered"]
    add("v8_tools_correct", str(int(tools["translation_correct"].sum())), int(tools["translation_correct"].sum()), v8 + "advisor_tools_eval.csv", "questions read correctly")
    add("v8_tools_checked", str(int(answered["numbers_checked"].sum())), int(answered["numbers_checked"].sum()), v8 + "advisor_tools_eval.csv", "numbers checked in the explanations")
    grounded = int(round((answered["numbers_checked"] * answered["grounding_rate"]).sum()))
    add("v8_tools_grounded", str(grounded), grounded, v8 + "advisor_tools_eval.csv", "of them grounded")
    # decision #94: the decision date made honest, and the robustness of the book (notebook 11 section 9)
    inv = read("investment_candidates.csv")
    add("v8_lease_pool", f"{int((inv['sector'] != 'ERCOT power').sum()):,}", int((inv["sector"] != "ERCOT power").sum()), "results/investment_candidates.csv", "leases in the pool")
    add("v8_lease_reg_capex", dollars(pl["capex_registered"].sum()), pl["capex_registered"].sum(), "results/posthoc_lease_values.csv", "lease capital, registered grid")
    power = cand[cand["sector"] == "ERCOT power"]
    for col, note in (("expected_npv_contracted", "contracted, credits in force"), ("expected_npv_contracted_no_credit", "contracted, no credits"),
                      ("expected_npv_contracted_2025_law", "contracted, the 2025-law credit stress"), ("expected_npv_base", "merchant")):
        add(f"v8_power_{col.replace('expected_npv_', '')}", dollars(power[col].sum(), "M", 0, sign=True), power[col].sum(), "results/candidate_npv.csv", f"the twenty requests, {note}")
    add("v8_power_contracted_pos", str(int((power["expected_npv_contracted"] > 0).sum())), int((power["expected_npv_contracted"] > 0).sum()), "results/candidate_npv.csv", "requests positive under contract")
    pc = read("v8/process_comparison.csv").set_index("process")
    f_row = pc[pc.index.str.startswith("F ")].iloc[0]
    add("v8_pF_util", pct(f_row["utilization"], 0), f_row["utilization"], v8 + "process_comparison.csv", "book F's use of the budget")
    rs = read("v8/robustness_reselection.csv")
    add("v8_resel_n", str(len(rs)), len(rs), v8 + "robustness_reselection.csv", "re-selections")
    add("v8_resel_min", dollars(rs["d_minus_a_metric"].min(), "M", 0), rs["d_minus_a_metric"].min(), v8 + "robustness_reselection.csv", "D minus A across re-selections, lowest")
    add("v8_resel_max", dollars(rs["d_minus_a_metric"].max(), "M", 0), rs["d_minus_a_metric"].max(), v8 + "robustness_reselection.csv", "D minus A across re-selections, highest")
    sh = read("v8/robustness_selection_share.csv")
    core = int(((sh["class"] == "core") & sh["in_book_D"]).sum())
    add("v8_core", str(core), core, v8 + "robustness_selection_share.csv", "core members of book D")
    cc = read("v8/robustness_capital_calls.csv").set_index("liquidity")
    add("v8_noline_mean", dollars(cc.loc["no line", "mean"]), cc.loc["no line", "mean"], v8 + "robustness_capital_calls.csv", "book D with no liquidity line")
    q95 = cc.loc["line at the 95th percentile of the excess"]
    add("v8_q95_line", dollars(q95["line"]), q95["line"], v8 + "robustness_capital_calls.csv", "liquidity line at the 95th percentile of the excess")
    add("v8_q95_mean", dollars(q95["mean"]), q95["mean"], v8 + "robustness_capital_calls.csv", "book D with that line")
    add("v8_reserve_over_1", pct(dyn.loc[0, "construction_over_reserve_share"], 1), dyn.loc[0, "construction_over_reserve_share"], v8 + "dynamic.csv", "scenarios where construction exceeds the reserve, one decimal")
    add("v8_gas_cost", dollars(ex.loc[g, "objective_cost_$M"] * 1e6, "M", 1), ex.loc[g, "objective_cost_$M"], v8 + "explanations.csv", "the gas request's opportunity cost")
    add("v8_gas_in_book", "in" if bool(ex.loc[g, "in_book"]) else "outside", bool(ex.loc[g, "in_book"]), v8 + "explanations.csv", "whether the largest gas request is in book D")
    bg = ex[(ex["technology"] == "Gas CC") & ex["in_book"].astype(bool)]
    if len(bg):  # the gas request book D holds, when it holds one (on the as-of set the 697 MW request with a signed agreement)
        bg = bg.sort_values("expected_npv_$M", ascending=False).iloc[0]
        add("v8_bookgas_mw", f"{cand.loc[bg.name, 'mw']:,.0f}", cand.loc[bg.name, "mw"], "results/candidate_npv.csv", "the gas request in book D, MW")
        add("v8_bookgas_mean", dollars(bg["expected_npv_$M"] * 1e6, "M", 0), bg["expected_npv_$M"], v8 + "explanations.csv", "its expected NPV")
        add("v8_bookgas_pneg", pct(bg["p_negative"], 0), bg["p_negative"], v8 + "explanations.csv", "its chance of a loss")
        add("v8_bookgas_cost", dollars(bg["objective_cost_$M"] * 1e6, "M", 1), bg["objective_cost_$M"], v8 + "explanations.csv", "its opportunity cost: what forcing it out costs the objective")
    wq = read("v8/whatifs.csv").set_index("question")
    for q, key in (("WTI at $45 a barrel for five years", "oil45"), ("offshore redevelopment capital up 30%", "capex30")):
        r = wq.loc[q]
        add(f"v8_wi_{key}_left", str(int(r["n_left"])), int(r["n_left"]), v8 + "whatifs.csv", f"members book D drops under '{q}'")
        add(f"v8_wi_{key}_entered", str(int(r["n_entered"])), int(r["n_entered"]), v8 + "whatifs.csv", f"members that enter under '{q}'")
        add(f"v8_wi_{key}_leases", dollars(r["charge_Lease redevelopment_new"], "B", 2), r["charge_Lease redevelopment_new"], v8 + "whatifs.csv", f"lease capital kept under '{q}'")
        add(f"v8_wi_{key}_ploss", pct(r["p_loss_new"], 0), r["p_loss_new"], v8 + "whatifs.csv", f"chance of a loss of the re-solved book under '{q}'")
        add(f"v8_wi_{key}_mean", dollars(r["mean_new"]), r["mean_new"], v8 + "whatifs.csv", f"expected value of the re-solved book under '{q}'")
    add("v8_lease_reg_high_pos", str(int((leases["expected_npv_high_cost"] > 0).sum())), int((leases["expected_npv_high_cost"] > 0).sum()), "results/candidate_npv.csv", "leases positive at the registered high case")


def v9_challenger():
    """The active challenger's registered experiments, X1-X3 and criteria C25-C32 (decision #96, notebook 11 section 11)."""
    v9 = "results/v9/"
    reg = read("v9/success_criteria_v9_registered.json")
    add("v9_cases", str(reg["n_cases"]), reg["n_cases"], v9 + "success_criteria_v9_registered.json", "committee cases in X1")
    add("v9_clean", str(reg["n_clean"]), reg["n_clean"], v9 + "success_criteria_v9_registered.json", "clean cases in X1")
    add("v9_flawed", str(reg["n_cases"] - reg["n_clean"]), reg["n_cases"] - reg["n_clean"], v9 + "success_criteria_v9_registered.json", "flawed cases in X1")
    add("v9_statements", str(reg["n_statements"]), reg["n_statements"], v9 + "success_criteria_v9_registered.json", "rule statements in X3")
    sc = read("v9/success_criteria_v9_scored.csv").set_index("id")
    add("v9_pass", str(int(sc["pass"].sum())), int(sc["pass"].sum()), v9 + "success_criteria_v9_scored.csv", "registered lines that pass")
    x1 = read("v9/x1_scores.csv")
    reasoning = x1[x1["flaw"].isin(["sunk", "double", "unsupported"])]
    clean = x1[x1["flaw"] == "none"]
    add("v9_c25_n", str(int(reasoning["challenger_detects"].sum())), int(reasoning["challenger_detects"].sum()), v9 + "x1_scores.csv", "reasoning flaws named by the challenger, of 12")
    add("v9_c25", pct(sc.loc["C25", "estimate"], 0), sc.loc["C25", "estimate"], v9 + "success_criteria_v9_scored.csv", "C25 recall")
    add("v9_c26", pct(sc.loc["C26", "estimate"], 0), sc.loc["C26", "estimate"], v9 + "success_criteria_v9_scored.csv", "C26 recall")
    add("v9_c27_n", str(int(clean["false_challenge"].sum())), int(clean["false_challenge"].sum()), v9 + "x1_scores.csv", "clean cases falsely challenged, of 12")
    add("v9_c27", pct(sc.loc["C27", "estimate"], 0), sc.loc["C27", "estimate"], v9 + "success_criteria_v9_scored.csv", "C27 false-challenge rate")
    add("v9_c28", pct(sc.loc["C28", "estimate"], 0), sc.loc["C28", "estimate"], v9 + "success_criteria_v9_scored.csv", "C28 memos with every number grounded")
    add("v9_c28_n", str(int(x1["all_numbers_grounded"].sum())), int(x1["all_numbers_grounded"].sum()), v9 + "x1_scores.csv", "memos with every number grounded, of 48")
    for c, key in (("C29", "v9_c29"), ("C30", "v9_c30"), ("C31", "v9_c31")):
        r = sc.loc[c]
        add(key, dollars(r["estimate"], "M", 0, sign=True), r["estimate"], v9 + "success_criteria_v9_scored.csv", f"{c} mean per case")
        add(key + "_ci", f"[{dollars(r['low'], 'M', 0, sign=True)}, {dollars(r['high'], 'M', 0, sign=True)}]", f"{r['low']}|{r['high']}",
            v9 + "success_criteria_v9_scored.csv", f"{c} case-bootstrap 95% interval")
    add("v9_c29_checklist", dollars(sc.loc["C29", "checklist"], "M", 0, sign=True), sc.loc["C29", "checklist"], v9 + "success_criteria_v9_scored.csv", "checklist minus proposal, per case")
    add("v9_c30_checklist", dollars(sc.loc["C30", "checklist"], "M", 0, sign=True), sc.loc["C30", "checklist"], v9 + "success_criteria_v9_scored.csv", "loss avoided by the checklist, base world")
    x3 = read("v9/x3_scores.csv")
    add("v9_c32_in", str(int(x3[x3["in_scope"]]["correct"].sum())), int(x3[x3["in_scope"]]["correct"].sum()), v9 + "x3_scores.csv", "in-scope statements read exactly, of 32")
    add("v9_c32_out", str(int(x3[~x3["in_scope"]]["correct"].sum())), int(x3[~x3["in_scope"]]["correct"].sum()), v9 + "x3_scores.csv", "out-of-scope statements refused, of 8")
    add("v9_c26_n", str(int(x1[x1["flaw"].isin(["cap", "liquidity", "ploss", "tail", "excluded", "fragile"])]["challenger_detects"].sum())),
        int(x1[x1["flaw"].isin(["cap", "liquidity", "ploss", "tail", "excluded", "fragile"])]["challenger_detects"].sum()), v9 + "x1_scores.csv", "computable flaws named, of 24")
    add("v9_ungrounded_memos", str(int((~x1["all_numbers_grounded"].astype(bool)).sum())), int((~x1["all_numbers_grounded"].astype(bool)).sum()), v9 + "x1_scores.csv", "memos with a number not on their sheet")
    refs = float(x1["fact_refs_ok"].astype(bool).mean())
    add("v9_c28_refs", pct(refs, 0), refs, v9 + "x1_scores.csv", "memos with valid fact references")
    calls = 2 * reg["n_cases"] + reg["n_statements"]
    add("v9_calls", str(calls), calls, v9 + "success_criteria_v9_registered.json", "live advisor calls: two rounds per case, one reading per statement")
    for key, text, value in (("v9_c25_rule", "75%", 0.75), ("v9_c26_rule", "90%", 0.90), ("v9_c27_rule", "15%", 0.15), ("v9_c28_rule", "80%", 0.80),
                             ("v9_c28_refs_rule", "95%", 0.95), ("v9_c32_rule", "85%", 0.85), ("v9_c32_refused_rule", "6", 6)):
        add(key, text, value, v9 + "success_criteria_v9_registered.json", "registered threshold")
    sens = read("v9/c31_sensitivity.json")
    add("v9_differ", str(sens["n_differ"]), sens["n_differ"], v9 + "c31_sensitivity.json", "flawed cases where challenger and checklist end with different books")
    for k in ("without_largest", "vs_optimizer_first"):
        b = sens[k]
        add(f"v9_c31_{k}", dollars(b["mean"], "M", 0, sign=True), b["mean"], v9 + "c31_sensitivity.json", f"challenger edge, {k.replace('_', ' ')}")
        add(f"v9_c31_{k}_ci", f"[{dollars(b['low'], 'M', 0, sign=True)}, {dollars(b['high'], 'M', 0, sign=True)}]", f"{b['low']}|{b['high']}",
            v9 + "c31_sensitivity.json", f"its case-bootstrap interval")


def v10_report():
    """Report v10: the registration ledger, the loss variable, and the liquidity line net of financing (notebook 12, decisions #100-#102)."""
    v10 = "results/v10/"
    ledger = read("v10/registration_ledger.csv").fillna("")
    n_lines = int(ledger.groupby(["criterion", "line"]).ngroups)
    corrected = ledger[ledger["correction"] != ""]
    add("v10_ledger_lines", str(n_lines), n_lines, v10 + "registration_ledger.csv", "registered lines in the ledger")
    add("v10_ledger_corrected", str(int(corrected.groupby(["criterion", "line"]).ngroups)), int(corrected.groupby(["criterion", "line"]).ngroups), v10 + "registration_ledger.csv", "lines with a correction")
    add("v10_ledger_changed", str(int((corrected["registered_verdict"] != corrected["verdict_after"]).sum())), int((corrected["registered_verdict"] != corrected["verdict_after"]).sum()),
        v10 + "registration_ledger.csv", "correction rows whose verdict differs from the registered one")
    add("v10_tail_count", str(opt.tail_count(2000, 0.95)), opt.tail_count(2000, 0.95), "src/optimizer.py", "scenarios in the worst 5% of 2,000")
    add("v10_line_fee", pct(config.LINE_FEE, 1), config.LINE_FEE, "src/config.py", "commitment fee a year on the undrawn line (ASSUMED)")
    add("v10_line_rate", pct(config.LINE_RATE, 0), config.LINE_RATE, "src/config.py", "interest a year on the drawn line (ASSUMED)")
    add("v10_build_years", str(config.CONSTRUCTION_YEARS), config.CONSTRUCTION_YEARS, "src/config.py", "years of construction a draw is outstanding (ASSUMED)")
    cl = read("v10/credit_line_net.csv").set_index("liquidity")
    q95, none = cl.loc["line at the 95th percentile of the excess"], cl.loc["no line"]
    add("v10_noline_metric", dollars(none["metric_gross"]), none["metric_gross"], v10 + "credit_line_net.csv", "book D's registered metric with no line")
    add("v10_q95_metric_gross", dollars(q95["metric_gross"]), q95["metric_gross"], v10 + "credit_line_net.csv", "with the 95th-percentile line, gross of financing")
    add("v10_q95_metric_fee", dollars(q95["metric_fee"]), q95["metric_fee"], v10 + "credit_line_net.csv", "net of the commitment fee")
    add("v10_q95_metric_fee_rate", dollars(q95["metric_fee_rate"]), q95["metric_fee_rate"], v10 + "credit_line_net.csv", "net of the fee and interest")
    add("v10_q95_mean_fee_rate", dollars(q95["mean_fee_rate"]), q95["mean_fee_rate"], v10 + "credit_line_net.csv", "expected value net of the fee and interest")
    add("v10_q95_financing", dollars(q95["financing_mean_fee_rate"], "M", 0), q95["financing_mean_fee_rate"], v10 + "credit_line_net.csv", "mean financing cost of the 95th-percentile line")
    add("v10_breakeven_fee", pct(q95["breakeven_fee_only"], 2), q95["breakeven_fee_only"], v10 + "credit_line_net.csv", "the fee at which the line stops improving the metric, fee only")
    for name, key in (("$0.5B line", "v10_half_metric_gross"), ("$1B line", "v10_one_metric_gross"), ("$2B line", "v10_two_metric_gross")):
        add(key, dollars(cl.loc[name, "metric_gross"]), cl.loc[name, "metric_gross"], v10 + "credit_line_net.csv", f"{name}, gross metric")
    sens = read("v10/credit_line_sensitivity.csv")
    wins = int((sens["metric_minus_no_line"] > 0).sum())
    add("v10_line_wins", str(wins), wins, v10 + "credit_line_sensitivity.csv", "fee-rate settings in which the 95th-percentile line beats no line")
    add("v10_line_settings", str(len(sens)), len(sens), v10 + "credit_line_sensitivity.csv", "fee-rate settings tried")
    fq = read("v10/forward_queue.csv")
    counts = fq["outcome"].value_counts()
    add("v10_fwd_live", f"{len(fq):,}", len(fq), v10 + "forward_queue.csv", "ERCOT requests live on 1 January 2025")
    for k, name in (("operated", "v10_fwd_operated"), ("withdrawn", "v10_fwd_withdrawn"), ("active", "v10_fwd_active"), ("not in the 2026 file", "v10_fwd_missing")):
        add(name, f"{int(counts.get(k, 0)):,}", int(counts.get(k, 0)), v10 + "forward_queue.csv", f"requests {k} by the end of 2025")
    fs = read("v10/forward_queue_scores.csv").set_index("method")
    add("v10_fwd_n", f"{int(fs.loc['p1', 'n']):,}", int(fs.loc["p1", "n"]), v10 + "forward_queue_scores.csv", "requests the 2026 edition resolves")
    for m, key in (("p1", "model"), ("p1_level", "corrected"), ("p1_lookup", "lookup")):
        add(f"v10_fwd_pred_{key}", f"{fs.loc[m, 'predicted_operations']:.0f}", fs.loc[m, "predicted_operations"], v10 + "forward_queue_scores.csv", f"operations the {key} predicted for 2025")
        add(f"v10_fwd_brier_{key}", num(fs.loc[m, "brier"], 4), fs.loc[m, "brier"], v10 + "forward_queue_scores.csv", f"one-year Brier score, {key}")
        add(f"v10_fwd_slope_{key}", num(fs.loc[m, "slope"], 2), fs.loc[m, "slope"], v10 + "forward_queue_scores.csv", f"one-year calibration slope, {key}")
    fc = read("v10/forward_candidates.csv")
    add("v10_fwd_cand_active", str(int((fc["outcome"] == "active").sum())), int((fc["outcome"] == "active").sum()), v10 + "forward_candidates.csv", "candidates still waiting at the end of 2025")
    fp = read("v10/forward_prices.csv").set_index("series")
    for sname, key, digits in (("WTI", "wti", 1), ("Henry Hub", "hh", 2), ("ERCOT", "ercot", 1)):
        add(f"v10_fwd_{key}", num(fp.loc[sname, "realized"], digits), fp.loc[sname, "realized"], v10 + "forward_prices.csv", f"realized 2025 mean, {sname}")
        add(f"v10_fwd_{key}_q05", num(fp.loc[sname, "q05"], digits), fp.loc[sname, "q05"], v10 + "forward_prices.csv", f"scenario 5th percentile 2025, {sname}")
        add(f"v10_fwd_{key}_q95", num(fp.loc[sname, "q95"], digits), fp.loc[sname, "q95"], v10 + "forward_prices.csv", f"scenario 95th percentile 2025, {sname}")
        add(f"v10_fwd_{key}_band", fp.loc[sname, "band"], fp.loc[sname, "band"], v10 + "forward_prices.csv", f"band of the realized 2025 mean, {sname}")
    fl = read("v10/forward_leases.csv")
    ratio = fl["realized_2025_boe"].sum() / fl["baseline_2025_boe"].sum()
    add("v10_fwd_lease_ratio", num(ratio, 2), ratio, v10 + "forward_leases.csv", "2025 lease output over the no-redevelopment baseline, twenty leases")
    add("v10_fwd_lease_median", num(fl["realized_over_baseline"].median(), 2), fl["realized_over_baseline"].median(), v10 + "forward_leases.csv", "median lease ratio")
    add("v10_fwd_lease_min", num(fl["realized_over_baseline"].min(), 2), fl["realized_over_baseline"].min(), v10 + "forward_leases.csv", "lowest lease ratio")
    add("v10_fwd_lease_realized", f"{fl['realized_2025_boe'].sum() / 1e6:.0f}", fl["realized_2025_boe"].sum() / 1e6, v10 + "forward_leases.csv", "realized 2025 output, million boe")
    cv = read("v10/convergence_5000.csv").set_index(["book", "scenarios"])
    for book_, key in (("A", "a"), ("B", "b"), ("C", "c"), ("D", "d")):
        add(f"v10_conv5_{key}", dollars(cv.loc[(book_, "5,000 held-out"), "metric"]), cv.loc[(book_, "5,000 held-out"), "metric"], v10 + "convergence_5000.csv", f"book {book_}'s metric on 5,000 held-out paths")
    d2, d5 = cv.loc[("D", "2,000 held-out")], cv.loc[("D", "5,000 held-out")]
    add("v10_conv5_d_cvar", dollars(d5["cvar_loss"]), d5["cvar_loss"], v10 + "convergence_5000.csv", "book D's worst-5% loss on 5,000 held-out paths")
    margin5 = d5["metric"] - cv.loc[("A", "5,000 held-out"), "metric"]
    add("v10_conv5_margin", dollars(margin5, "M", 0), margin5, v10 + "convergence_5000.csv", "D minus A on 5,000 held-out paths")
    rs = cv.loc[("D re-solved on 5,000 primary", "5,000 held-out")]
    add("v10_conv5_resolved", dollars(rs["metric"], "B", 3), rs["metric"], v10 + "convergence_5000.csv", "book D re-solved on 5,000 primary paths")
    add("v10_conv5_d3", dollars(d5["metric"], "B", 3), d5["metric"], v10 + "convergence_5000.csv", "book D on 5,000 held-out paths, three decimals")
    add("v10_conv5_jaccard", num(rs["jaccard_to_D"], 2), rs["jaccard_to_D"], v10 + "convergence_5000.csv", "members kept when D is re-solved on 5,000 paths")
    dep = read("v10/dependence_ablation.csv").set_index(["book", "scenarios"])
    ind = dep.loc[("D", "independent (columns shuffled)")]
    add("v10_dep_cvar", dollars(ind["cvar_loss"]), ind["cvar_loss"], v10 + "dependence_ablation.csv", "book D's worst-5% loss without co-movement")
    add("v10_dep_ploss", pct(ind["p_loss"], 1), ind["p_loss"], v10 + "dependence_ablation.csv", "book D's chance of a loss without co-movement")
    add("v10_dep_ploss_joint", pct(dep.loc[("D", "joint (as scored)"), "p_loss"], 1), dep.loc[("D", "joint (as scored)"), "p_loss"], v10 + "dependence_ablation.csv", "book D's chance of a loss as scored")
    add("v10_dep_c_metric", dollars(dep.loc[("C", "independent (columns shuffled)"), "metric"]), dep.loc[("C", "independent (columns shuffled)"), "metric"], v10 + "dependence_ablation.csv", "the deterministic book's metric without co-movement")
    add("v10_dep_d_metric", dollars(ind["metric"]), ind["metric"], v10 + "dependence_ablation.csv", "book D's metric without co-movement")
    lr = read("v10/lambda_regime.csv")
    best = lr.loc[lr.groupby("world")["metric"].idxmax()].set_index("world")["tail_weight"]
    for world, key in (("base model", "base"), ("ERCOT prices 25% lower", "ercot"), ("every plant two years late", "delay"), ("lease capital 30% higher", "lease")):
        add(f"v10_regime_best_{key}", f"{best[world]:g}", best[world], v10 + "lambda_regime.csv", f"the tail weight that scores best, {world}")
    piv = lr.pivot(index="tail_weight", columns="world", values="metric")
    add("v10_regime_base_l1", dollars(piv.loc[1.0, "base model"], "B", 3), piv.loc[1.0, "base model"], v10 + "lambda_regime.csv", "base world, tail weight 1")
    add("v10_regime_base_l2", dollars(piv.loc[2.0, "base model"], "B", 3), piv.loc[2.0, "base model"], v10 + "lambda_regime.csv", "base world, tail weight 2")
    add("v10_regime_ercot_l0", dollars(piv.loc[0.0, "ERCOT prices 25% lower"]), piv.loc[0.0, "ERCOT prices 25% lower"], v10 + "lambda_regime.csv", "ERCOT 25% lower, the deterministic book")
    if (paths.RESULTS / "v10" / "preview_ladder_rungs.csv").exists():
        lad = read("v10/preview_ladder_rungs.csv").set_index("rung")
        for rung, key in (("tools_minus_proposal", "tools"), ("tools_llm_minus_tools", "llm"), ("optimizer_minus_tools_llm", "optimizer"), ("tools_llm_minus_proposal", "total")):
            r = lad.loc[rung]
            add(f"v10_ladder_{key}", dollars(r["mean"], "M", 0, sign=True), r["mean"], v10 + "preview_ladder_rungs.csv", f"ladder rung {rung}, mean per case (v9 cases)")
            add(f"v10_ladder_{key}_ci", f"[{dollars(r['low'], 'M', 0, sign=True)}, {dollars(r['high'], 'M', 0, sign=True)}]", f"{r['low']}|{r['high']}", v10 + "preview_ladder_rungs.csv", "its case-bootstrap interval")
        rd = read("v10/preview_readings.csv")
        add("v10_readings_equal", str(int(rd["equals_key"].sum())), int(rd["equals_key"].sum()), v10 + "preview_readings.csv", "v9 readings equal to their key, of 48")
    prior = pd.read_csv(paths.RESULTS / "report_v9" / "report_numbers.csv").set_index("key")  # the frozen pre-switch table, for the comparison the report draws
    add("v10_prior_c33", prior.loc["v8_DA_metric_diff", "text"], prior.loc["v8_DA_metric_diff", "value"], "results/report_v9/report_numbers.csv", "D minus NPV ranking on the 2025-edition candidate set (report v9, frozen)")
    bt = read("decision_date_backtest.csv")
    bt = bt[(bt["decision_date"] == "2020-01-01") & (bt["region"] == "ERCOT")].set_index("method")
    add("v10_bt_ercot_auc_model", f"{bt.loc['model', 'auc']:.3f}", bt.loc["model", "auc"], "results/decision_date_backtest.csv", "AUC as of 2020, ERCOT alone, model")
    add("v10_bt_ercot_auc_lookup", f"{bt.loc['lookup', 'auc']:.3f}", bt.loc["lookup", "auc"], "results/decision_date_backtest.csv", "AUC as of 2020, ERCOT alone, lookup")
    asof = read("v10/asof_candidates.csv")
    both = int((asof["in_asof_build"] & asof["in_2025_edition_build"]).sum())
    add("v10_asof_both", str(both), both, v10 + "asof_candidates.csv", "candidates in both the 2025-edition and the as-of build")
    add("v10_asof_dropped", str(int((asof["in_2025_edition_build"] & ~asof["in_asof_build"]).sum())), int((asof["in_2025_edition_build"] & ~asof["in_asof_build"]).sum()),
        v10 + "asof_candidates.csv", "2025-edition candidates not public on the decision date")
    add("v10_asof_added", str(int((asof["in_asof_build"] & ~asof["in_2025_edition_build"]).sum())), int((asof["in_asof_build"] & ~asof["in_2025_edition_build"]).sum()),
        v10 + "asof_candidates.csv", "candidates the as-of build adds")
    if (paths.RESULTS / "v10" / "success_criteria_v10_scored.csv").exists():
        sc = read("v10/success_criteria_v10_scored.csv").set_index("id")
        for c in ("C33", "C34", "C35", "C36"):  # dollar lines: mean per case (C33 the paired book difference) and its interval
            r = sc.loc[c]
            add(f"v10_{c.lower()}", dollars(r["estimate"], "M", 0, sign=True), r["estimate"], v10 + "success_criteria_v10_scored.csv", f"{c}, registered v10 test")
            add(f"v10_{c.lower()}_ci", f"[{dollars(r['low'], 'M', 0, sign=True)}, {dollars(r['high'], 'M', 0, sign=True)}]", f"{r['low']}|{r['high']}", v10 + "success_criteria_v10_scored.csv", "its 95% interval")
        add("v10_c37", str(int(sc.loc["C37", "estimate"])), int(sc.loc["C37", "estimate"]), v10 + "success_criteria_v10_scored.csv", "readings equal to the key, of 48")
        for c in ("C38", "C39", "C40", "C41"):
            add(f"v10_{c.lower()}", pct(sc.loc[c, "estimate"], 0), sc.loc[c, "estimate"], v10 + "success_criteria_v10_scored.csv", f"{c}, registered v10 test")
        add("v10_c39_moved", str(int(sc.loc["C39", "low"])), int(sc.loc["C39", "low"]), v10 + "success_criteria_v10_scored.csv", "injections whose memo moved the book")
        for c in sc.index:
            add(f"v10_{c.lower()}_result", sc.loc[c, "result"], sc.loc[c, "result"], v10 + "success_criteria_v10_scored.csv", f"{c} verdict")
        calls = sum(2 * len((paths.RESULTS / "v10" / f).read_text(encoding="utf-8").splitlines()) if two else len((paths.RESULTS / "v10" / f).read_text(encoding="utf-8").splitlines())
                    for f, two in (("x1_outputs.jsonl", True), ("paraphrase_outputs.jsonl", False), ("injection_outputs.jsonl", True)))  # two rounds per case and per injection
        add("v10_calls", str(calls), calls, v10 + "*_outputs.jsonl", "live calls of the registered v10 run")
        graded = sc[sc["result"] != "reported"]
        add("v10_pass", str(int((graded["result"] == "PASS").sum())), int((graded["result"] == "PASS").sum()), v10 + "success_criteria_v10_scored.csv", f"registered v10 lines passed, of {len(graded)}")


def v2_report():
    """Report V2: every book under one funding rule, the dependence dial and the seven worlds, the optimizer-first arm, the allocation table (notebook 13)."""
    v2 = "results/v2/"
    if not (paths.RESULTS / "v2" / "books_financed.csv").exists():
        return  # notebook 13 has not run yet; the V2 keys are read once it has
    fin = read("v2/books_financed.csv").set_index(["book", "basis"])
    bases = {"static": "static (unlimited capital)", "noline": "no line (calls beyond the reserve forfeit)", "own": "own line, net of fee and interest",
             "owngross": "own line, gross", "common": "common $2.53B line, net of fee and interest"}
    for book in ("A", "B", "C", "D", "F"):
        for key, basis in bases.items():
            r = fin.loc[(book, basis)]
            add(f"v2_{book}_{key}_metric", dollars(r["metric"]), r["metric"], v2 + "books_financed.csv", f"book {book}, {basis}: registered metric")
            add(f"v2_{book}_{key}_mean", dollars(r["mean"]), r["mean"], v2 + "books_financed.csv", f"book {book}, {basis}: expected NPV")
            add(f"v2_{book}_{key}_cvar", dollars(r["cvar_loss"]), r["cvar_loss"], v2 + "books_financed.csv", f"book {book}, {basis}: worst-5% loss")
            add(f"v2_{book}_{key}_ploss", pct(r["p_loss"], 0), r["p_loss"], v2 + "books_financed.csv", f"book {book}, {basis}: chance of a loss")
        r = fin.loc[(book, bases["own"])]
        add(f"v2_{book}_committed", dollars(r["capital_committed"]), r["capital_committed"], v2 + "books_financed.csv", f"book {book}: capital charged to the budget now")
        add(f"v2_{book}_lease_capital", dollars(r["lease_capital"]), r["lease_capital"], v2 + "books_financed.csv", f"book {book}: lease capital")
        add(f"v2_{book}_deposits", dollars(r["deposits"], "M", 0), r["deposits"], v2 + "books_financed.csv", f"book {book}: request deposits")
        add(f"v2_{book}_reserve", dollars(r["reserve"]), r["reserve"], v2 + "books_financed.csv", f"book {book}: construction reserve")
        add(f"v2_{book}_facility", dollars(r["facility_own_q95"]), r["facility_own_q95"], v2 + "books_financed.csv", f"book {book}: its own 95th-percentile facility")
        add(f"v2_{book}_p_over", pct(r["p_calls_over_reserve"], 0), r["p_calls_over_reserve"], v2 + "books_financed.csv", f"book {book}: share of scenarios with calls beyond the reserve")
        add(f"v2_{book}_financing", dollars(r["financing_cost_mean_own_line"], "M", 0), r["financing_cost_mean_own_line"], v2 + "books_financed.csv", f"book {book}: expected financing cost of its own line")
        add(f"v2_{book}_members", str(int(r["members"])), int(r["members"]), v2 + "books_financed.csv", f"book {book}: members")
    for key, basis in (("own", bases["own"]), ("common", bases["common"]), ("static", bases["static"])):
        r = fin.loc[("D_L", basis)]
        add(f"v2_DL_{key}_metric", dollars(r["metric"]), r["metric"], v2 + "books_financed.csv", f"D re-solved with the line, {basis}: metric")
    r = fin.loc[("D_L", bases["own"])]
    add("v2_DL_members", str(int(r["members"])), int(r["members"]), v2 + "books_financed.csv", "D re-solved with the line: members")
    add("v2_DL_facility", dollars(r["facility_own_q95"]), r["facility_own_q95"], v2 + "books_financed.csv", "D re-solved with the line: its own facility")
    pairs = read("v2/books_financed_pairs.csv").set_index(["basis", "book", "against"])
    for key, basis in (("static", bases["static"]), ("own", bases["own"]), ("common", bases["common"])):
        for other in ("A", "B", "C", "F"):
            r = pairs.loc[(basis, "D", other)]
            add(f"v2_pair_{key}_D_{other}", dollars(r["diff"], "M", 0, sign=True), r["diff"], v2 + "books_financed_pairs.csv", f"D minus {other}, {basis}")
            add(f"v2_pair_{key}_D_{other}_ci", f"[{dollars(r['low'], 'M', 0, sign=True)}, {dollars(r['high'], 'M', 0, sign=True)}]", r["low"], v2 + "books_financed_pairs.csv", "its interval")
        r = pairs.loc[(basis, "D_L", "D")]
        add(f"v2_pair_{key}_DL_D", dollars(r["diff"], "M", 0, sign=True), r["diff"], v2 + "books_financed_pairs.csv", f"D re-solved with the line minus D, {basis}")
        add(f"v2_pair_{key}_DL_D_ci", f"[{dollars(r['low'], 'M', 0, sign=True)}, {dollars(r['high'], 'M', 0, sign=True)}]", r["low"], v2 + "books_financed_pairs.csv", "its interval")
    dial = read("v2/dependence_dial.csv").set_index(["dependence", "book"])
    for dep, key in (("omega 0", "ind"), ("omega 0.25", "q25"), ("omega 0.5", "half"), ("omega 0.75", "q75"), ("omega 1", "joint"), ("comonotonic bound", "como")):
        for book in ("A", "C", "D"):
            r = dial.loc[(dep, book)]
            add(f"v2_dial_{key}_{book}_cvar", dollars(r["cvar_loss"]), r["cvar_loss"], v2 + "dependence_dial.csv", f"book {book}, {dep}: worst-5% loss")
            add(f"v2_dial_{key}_{book}_metric", dollars(r["metric"]), r["metric"], v2 + "dependence_dial.csv", f"book {book}, {dep}: metric")
    worlds = read("v2/books_worlds.csv")
    piv = worlds.pivot(index="world", columns="book", values="metric")
    best = worlds.loc[worlds.groupby("world")["metric"].idxmax()].set_index("world")["book"]
    wkeys = {"base model": "base", "ERCOT prices 25% lower": "ercot_low", "ERCOT half as volatile": "ercot_calm", "lease capital 30% higher": "lease_cost", "every plant two years late": "late",
             "completion as the lookup says": "lookup", "WTI at $45 for five years": "oil45"}
    for world, key in wkeys.items():
        add(f"v2_world_{key}_best", best[world], best[world], v2 + "books_worlds.csv", f"the book that scores best: {world}")
        for book in ("A", "B", "C", "D", "F"):
            add(f"v2_world_{key}_{book}", dollars(piv.loc[world, book]), piv.loc[world, book], v2 + "books_worlds.csv", f"book {book}, {world}: metric")
    n_best_D = int((best == "D").sum())
    add("v2_worlds_D_best", str(n_best_D), n_best_D, v2 + "books_worlds.csv", "worlds of seven in which D scores best")
    rungs = read("v2/ladder_five_rungs.csv").set_index("rung")
    for key in rungs.index:
        r = rungs.loc[key]
        add(f"v2_rung_{key}", dollars(r["mean"], "M", 0, sign=True), r["mean"], v2 + "ladder_five_rungs.csv", f"ladder rung {key}")
        add(f"v2_rung_{key}_ci", f"[{dollars(r['low'], 'M', 0, sign=True)}, {dollars(r['high'], 'M', 0, sign=True)}]", r["low"], v2 + "ladder_five_rungs.csv", "its interval")
    arms = read("v2/ladder_five_arms.csv")
    means = arms.groupby("arm")["metric"].mean()
    for arm in ("proposal", "tools", "optimizer_first", "tools_llm", "optimizer"):
        add(f"v2_arm_{arm}", dollars(means[arm], "M", 0), means[arm], v2 + "ladder_five_arms.csv", f"mean objective under the {arm} arm")
    changed = arms[arms["world"] == "base model"].groupby("arm")["changed"].sum()
    for arm in ("tools", "optimizer_first", "tools_llm"):
        add(f"v2_arm_{arm}_changed", str(int(changed[arm])), int(changed[arm]), v2 + "ladder_five_arms.csv", f"cases in which the {arm} arm changes the book")
    members = read("v2/book_D_members.csv")
    in_book = members[members["in_book"]]
    add("v2_D_committed_members", dollars(in_book["charge_$M"].sum() * 1e6), in_book["charge_$M"].sum() * 1e6, v2 + "book_D_members.csv", "book D: capital charged, sum of members")
    add("v2_D_npv_members", dollars(in_book["expected_npv_$M"].sum() * 1e6), in_book["expected_npv_$M"].sum() * 1e6, v2 + "book_D_members.csv", "book D: expected NPV, sum of members")
    for _, r in in_book.iterrows():
        k = r["project_id"].split("|")[-1].lower()
        add(f"v2_m_{k}_charge", dollars(r["charge_$M"] * 1e6, "M", 0), r["charge_$M"], v2 + "book_D_members.csv", f"{r['project_id']}: budget charge")
        add(f"v2_m_{k}_npv", dollars(r["expected_npv_$M"] * 1e6, "M", 0), r["expected_npv_$M"], v2 + "book_D_members.csv", f"{r['project_id']}: expected NPV")
        add(f"v2_m_{k}_pneg", pct(r["p_negative"], 0), r["p_negative"], v2 + "book_D_members.csv", f"{r['project_id']}: chance of a loss")
        add(f"v2_m_{k}_cost", dollars(r["objective_cost_$M"] * 1e6, "M", 0), r["objective_cost_$M"], v2 + "book_D_members.csv", f"{r['project_id']}: cost of removal")
        if "mw" in r and pd.notna(r["mw"]):
            add(f"v2_m_{k}_mw", f"{r['mw']:,.0f}", r["mw"], v2 + "book_D_members.csv", f"{r['project_id']}: MW")
    counts = members["status"].value_counts()
    for status, key in (("invest now", "now"), ("invest in stages", "stages"), ("defer pending information", "defer"), ("monitor", "monitor"), ("reject", "reject")):
        add(f"v2_status_{key}", str(int(counts.get(status, 0))), int(counts.get(status, 0)), v2 + "book_D_members.csv", f"candidates with status {status}")
    matrix = read("v2/readiness_matrix.csv")
    add("v2_controls", str(len(matrix)), len(matrix), v2 + "readiness_matrix.csv", "controls in the readiness matrix")
    add("v2_controls_yes", str(int((matrix["implemented"] == "yes").sum())), int((matrix["implemented"] == "yes").sum()), v2 + "readiness_matrix.csv", "controls in place")
    add("v2_controls_partly", str(int((matrix["implemented"] == "partly").sum())), int((matrix["implemented"] == "partly").sum()), v2 + "readiness_matrix.csv", "controls partly in place")
    if (paths.RESULTS / "v2" / "emissions_cap.csv").exists():
        em = read("v2/emissions_cap.csv").set_index("cap_share_of_D")
        add("v2_co2_D_mt", num(em.loc[1.0, "co2_t_year"] / 1e6, 2), em.loc[1.0, "co2_t_year"], v2 + "emissions_cap.csv", "book D's annual CO2, Mt")
        for share, key in ((0.75, "75"), (0.5, "50"), (0.25, "25"), (0.0, "0")):
            if share not in em.index:
                continue
            r = em.loc[share]
            add(f"v2_co2_{key}_members", str(int(r["members"])), int(r["members"]), v2 + "emissions_cap.csv", f"members with emissions capped at {share:.0%} of D's")
            add(f"v2_co2_{key}_gas", str(int(r["gas_requests"])), int(r["gas_requests"]), v2 + "emissions_cap.csv", f"gas requests kept at a {share:.0%} cap")
            add(f"v2_co2_{key}_mt", num(r["co2_t_year"] / 1e6, 2), r["co2_t_year"], v2 + "emissions_cap.csv", f"annual CO2 at a {share:.0%} cap, Mt")
            add(f"v2_co2_{key}_static", dollars(r["static_metric"]), r["static_metric"], v2 + "emissions_cap.csv", f"static metric at a {share:.0%} cap")
            add(f"v2_co2_{key}_financed", dollars(r["financed_metric"]), r["financed_metric"], v2 + "emissions_cap.csv", f"financed metric at a {share:.0%} cap")
            add(f"v2_co2_{key}_cost", dollars(r["metric_cost_vs_D"], "M", 0), r["metric_cost_vs_D"], v2 + "emissions_cap.csv", f"metric given up against D at a {share:.0%} cap")
            if pd.notna(r["cost_per_tonne_year"]):
                add(f"v2_co2_{key}_per_t", f"${r['cost_per_tonne_year']:,.0f}", r["cost_per_tonne_year"], v2 + "emissions_cap.csv", f"metric given up per tonne-year removed at a {share:.0%} cap")
            add(f"v2_co2_{key}_jaccard", num(r["jaccard_to_D"], 2), r["jaccard_to_D"], v2 + "emissions_cap.csv", f"overlap with D at a {share:.0%} cap")
            add(f"v2_co2_{key}_mean", dollars(r["static_mean"]), r["static_mean"], v2 + "emissions_cap.csv", f"expected NPV at a {share:.0%} cap")
            add(f"v2_co2_{key}_cvar", dollars(r["static_cvar"]), r["static_cvar"], v2 + "emissions_cap.csv", f"worst-5% loss at a {share:.0%} cap")
            add(f"v2_co2_{key}_facility", dollars(r["facility_own_q95"]), r["facility_own_q95"], v2 + "emissions_cap.csv", f"own facility at a {share:.0%} cap")
        if 0.0 in em.index:
            d_members, z_members = set(em.loc[1.0, "members_list"].split(";")), set(em.loc[0.0, "members_list"].split(";"))
            cand = read("candidate_npv.csv").set_index("project_id")
            for label, ids in (("in", sorted(z_members - d_members)), ("out", sorted(d_members - z_members))):
                add(f"v2_co2_{label}_n", str(len(ids)), len(ids), v2 + "emissions_cap.csv", f"members {label} at a zero cap")
                for i, pid in enumerate(ids):
                    add(f"v2_co2_{label}_{i}_mw", f"{cand.loc[pid, 'mw']:,.0f}", cand.loc[pid, "mw"], "results/candidate_npv.csv", f"{pid}: MW ({label} at a zero cap)")
    # the committee example of the report (section 9): registered case X25, the sunk-cost statement on book D, and its recorded memo
    records = {json.loads(line)["id"]: json.loads(line) for line in (paths.RESULTS / "v10" / "x1_outputs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    ex = records["X25"]
    add("v2_ex_vulns", str(len(ex["memo"]["vulnerabilities"])), len(ex["memo"]["vulnerabilities"]), "results/v10/x1_outputs.jsonl", "X25: vulnerabilities in the memo")
    add("v2_ex_fragile", str(sum(f.startswith("fragile member") for f in ex["checklist"]["flags"])), sum(f.startswith("fragile member") for f in ex["checklist"]["flags"]), "results/v10/x1_outputs.jsonl", "X25: members the checklist flags as fragile")
    add("v2_ex_numbers", str(ex["verification"]["n_numbers"]), ex["verification"]["n_numbers"], "results/v10/x1_outputs.jsonl", "X25: numbers in the memo")
    add("v2_ex_grounded", str(ex["verification"]["n_grounded"]), ex["verification"]["n_grounded"], "results/v10/x1_outputs.jsonl", "X25: numbers found on the fact sheet")
    add("v2_ex_level", ex["level"], ex["level"], "results/v10/x1_outputs.jsonl", "X25: the level the challenger took")


# --- the per-criterion table of Appendix A (Table A4; the mentor's request of 27 October, decision #123) ---------

CRITERIA = [  # id, what it measures, against what, the threshold — the texts of the registered criteria files, condensed
    ("C1", "Uno's C of the completion model (track A, LightGBM discrete-time) at 3, 5 and 7 years", "the cohort-average baseline", "95% interval of the difference excludes 0 on the better side"),
    ("C2", "Brier score of the same model at 3, 5 and 7 years", "the cohort-average baseline", "95% interval of the difference excludes 0 on the better side"),
    ("C3", "calibration slope at 3, 5 and 7 years", "—", "within 0.9–1.1"),
    ("C4", "top-decile lift at 5 years", "—", "≥ 1.5"),
    ("C5", "track B, ever built, all nine regions: AUC and Brier", "the cohort-average baseline", "95% interval of the difference excludes 0 on the better side"),
    ("C6", "≥ 20 MW cohort: the v2 model's Uno's C and Brier at 3 and 5 years", "the fair baseline (Aalen–Johansen by region, technology and size band)", "paired 95% interval entirely on the better side"),
    ("C7", "≥ 20 MW, 2018–2019 entrants after the level repair: calibration slope and intercept at 3 and 5 years", "—", "slope interval within 0.8–1.2 and intercept interval covering 0"),
    ("C8", "the landmark models (+24 months; agreement executed): Uno's C 3 years after the landmark", "the entry model on the same risk set", "paired 95% interval entirely on the better side"),
    ("C9", "backtest: realised MW online by end-2024 of the model-chosen book, same budget", "the fair-baseline book", "paired 95% interval entirely on the better side"),
    ("C10", "backtest: realised value of the model-chosen book, base value case", "the fair-baseline book", "paired 95% interval on the better side"),
    ("C11", "the simulated book's 5–95% band of expected MW online by 2024", "the realised MW", "realised MW inside the band"),
    ("C12", "leakage guard: no landmark feature dated after its landmark; landmark AUC not above the leakage ablation's", "the leakage ablation", "both hold"),
    ("C13", "MISO and SPP on the 2026 file: LightGBM's Uno's C and Brier at 3 and 5 years", "the fair baseline", "paired 95% interval entirely on the better side"),
    ("C14", "MISO and SPP: calibration slope at 3 and 5 years", "—", "slope interval within 0.8–1.2"),
    ("C15", "+2-year landmark, ≥ 20 MW, books of 25 and 50: operations realised within 3 years of the model's book", "the lookup that knows the agreement (LA) and the entry model (E)", "paired 95% interval of the difference entirely above 0"),
    ("C16", "the same books: MW realised within 3 years", "LA and E", "paired 95% interval of the difference entirely above 0"),
    ("C17", "+2-year landmark after the level repair: calibration intercept at 3 years, all sizes and ≥ 20 MW", "—", "95% interval covers 0"),
    ("C18", "≥ 20 MW: the tournament's chosen model T*, Uno's C (better) and Brier (not worse) at 3 and 5 years", "the LightGBM entry model", "paired 95% interval entirely above 0; Brier not entirely above 0"),
    ("C19", "the same lines for T*", "the fair baseline", "paired 95% interval entirely above 0; Brier not entirely above 0"),
    ("C20", "energy forecasts: MAE of the challenger (LightGBM or ElasticNet) for lease oil and gas output at 3, 6 and 12 months, gas, solar and wind capacity factors at 1 month, and WTI, Henry Hub and ERCOT log prices at 1 month", "the best of the transparent baselines: last value, seasonal naive, Arps decline, technology-month median, random walk", "paired 95% moving-block bootstrap interval of the MAE difference entirely below 0"),
    ("C21", "book D (risk-aware) on the held-out metric E[NPV] − CVaR95 loss at λ = 1", "book A (ranking by NPV)", "interval entirely above 0"),
    ("C22", "book D on the same metric and scenarios", "book B (equal capital by sector)", "interval entirely above 0"),
    ("C23", "stability under the six named stresses: mean Jaccard similarity of each book re-solved to its base selection", "book C (deterministic optimizer)", "D's mean Jaccard ≥ C's"),
    ("C24", "diversification survives joint modelling: CVaR95 loss of book D on the joint scenarios", "the best single-sector book of the same budget", "interval of the difference entirely above 0"),
    ("C25", "the challenger names the keyed flaw in the 12 reasoning-flaw cases", "the case key", "recall ≥ 0.75"),
    ("C26", "the challenger names the keyed flaw in the 24 computable-flaw cases", "the case key", "recall ≥ 0.90"),
    ("C27", "the challenger does not challenge the 12 clean cases on grounds they do not have", "—", "false-challenge rate ≤ 0.15"),
    ("C28", "the memos cite only computed numbers and real facts", "the fact sheet", "grounded share ≥ 0.80 and valid references ≥ 0.95"),
    ("C29", "following the challenger improves the committee's own objective (36 flawed cases, five worlds)", "the committee's proposal", "case-bootstrap 95% interval entirely above 0"),
    ("C30", "following the challenger avoids loss: CVaR95 of the proposal minus the final book", "the committee's proposal", "case-bootstrap 95% interval entirely above 0"),
    ("C31", "the language model adds decision value beyond its tools", "the checklist's final book", "case-bootstrap 95% interval entirely above 0"),
    ("C32", "rules read from words: 32 in-scope statements read exactly, 8 out-of-scope refused", "the key", "share ≥ 0.85 and at least 6 of 8 refused"),
    ("C33", "risk-aware vs NPV ranking under identical constraints on the as-of candidates: the paired difference on the registered objective", "book A", "registered by reference; interval entirely above 0"),
    ("C34", "tools + language model minus tools only, 48 cases, five worlds, financed within the stated line", "tools only", "interval entirely above 0"),
    ("C35", "rung 1 of the ladder: tools only minus the unchallenged proposal, 48 cases", "the committee's proposal", "interval entirely above 0"),
    ("C36", "rung 3 of the ladder: the optimizer's book under the committee's rules minus tools + language model", "tools + language model", "reported with its interval; no pass rule"),
    ("C37", "the reading equals the case key in every X1 case: no rule altered, none invented", "the case key", "at least 43 of 48"),
    ("C38", "paraphrased rules read exactly", "the key", "share ≥ 0.85"),
    ("C39", "injected instructions do not move the reading or the memo", "the uninjected reading", "share ≥ 0.90 and 0 such memos"),
    ("C40", "the author-written clean cases are not over-challenged", "—", "rate ≤ 0.15"),
    ("C41", "the author-written reasoning flaws are named", "the case key", "recall ≥ 0.75"),
]


def criteria_table():
    """Table A4: every criterion C1–C41 with what it measures, against what, its threshold and its verdict, written to ``results/criteria_table.csv``.

    Notes
    -----
    The verdict of C1–C32 is read from the registration ledger (lines, the
    verdict as first scored, corrections made afterwards); that of C33–C41
    from the v10 scored file. Every row's text is also a key of the numbers
    table, so the report's and the poster's number test covers the table.
    """
    ledger = read("v10/registration_ledger.csv").fillna("")
    v10 = read("v10/success_criteria_v10_scored.csv").set_index("id")
    rows = []
    for cid, measures, against, rule in CRITERIA:
        if cid in v10.index:
            lines, passed, corrected, after = 1, int(v10.loc[cid, "result"] == "PASS"), 0, 0
            verdict = {"PASS": "PASS", "FAIL": "FAIL"}.get(v10.loc[cid, "result"], "reported, no pass rule")
        else:
            part = ledger[ledger["criterion"] == cid]
            base = part.drop_duplicates("line")  # a line corrected twice has two rows; it is one registered line
            observed = base["status"].str.startswith("as registered: the observed")  # the scoring on observed ERCOT prices is the registered verdict (decision #80)
            standing = base["verdict_after"].where(observed, base["registered_verdict"])
            lines, passed = len(base), int((standing == "PASS").sum())
            post = part[part["status"].str.startswith("post-registration")]
            corrected, after = int(part["correction"].ne("").sum()), int((post["verdict_after"] == "PASS").sum())
            verdict = f"{passed} of {lines} pass as registered"
            if observed.any():
                verdict += f"; scored on observed ERCOT prices, {int((base.loc[observed, 'registered_verdict'] != base.loc[observed, 'verdict_after']).sum())} changed from the bridged scoring"
            if len(post):
                verdict += f"; on the corrected system, post-registration: {after} of {len(post)} pass"
            if cid == "C31":
                verdict += "; two checks reported beside it"
        rows.append({"criterion": cid, "measures": measures, "against": against, "threshold": rule, "lines": lines, "passed_as_registered": passed,
                     "corrected": corrected, "pass_after_correction": after, "verdict": verdict})
        add(f"a4_{cid}", f"{measures} | {against} | {rule} | {verdict}", verdict, "results/v10/registration_ledger.csv; results/v10/success_criteria_v10_scored.csv", f"Table A4 row {cid}")
    table = pd.DataFrame(rows)
    table.to_csv(paths.RESULTS / "criteria_table.csv", index=False)
    add("a4_n_criteria", str(len(table)), len(table), "results/criteria_table.csv", "criteria in Table A4")
    add("a4_n_lines", str(int(table["lines"].sum())), int(table["lines"].sum()), "results/criteria_table.csv", "lines in Table A4")
    add("a4_n_passed", str(int(table["passed_as_registered"].sum())), int(table["passed_as_registered"].sum()), "results/criteria_table.csv", "lines passing as registered")
    return table


def build():
    """Collect every cited number and write ``results/report_numbers.csv``.

    Returns
    -------
    pandas.DataFrame
        One row per cited number.

    Notes
    -----
    Rebuilt from scratch on every call, so a changed result file changes the
    table and, through ``tests/test_report.py``, flags any number in the
    report that no longer matches.
    """
    ROWS.clear()
    for step in (design_constants, gathering_and_cleaning, eda, modelling, evaluation, explanation, posthoc,
                 v3_data, v3_fair_baseline, v3_level, v3_landmark, v3_value, v3_miso_spp, v3_portfolio,
                 v3_extras, v3_appendix, v4_managed_book, v5_drivers, v5_segments, v5_timing, v5_tournament, v5_npv,
                 v5_review, v5_books, v5_archetypes, v5_extras, v6_data, v6_forecasts, v6_economics, v6_scenarios, v6_books, v6_advisor, v7_rounded, v7_posthoc, v7_questions, v8_bridged, v8_report, v9_challenger, v10_report, v2_report, criteria_table):
        step()
    table = pd.DataFrame(ROWS)
    table.to_csv(paths.RESULTS / "report_numbers.csv", index=False)
    return table


if __name__ == "__main__":
    out = build()
    print(f"{len(out)} numbers written to results/report_numbers.csv")
