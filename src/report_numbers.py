"""Every number the report cites, read from ``results/`` and written to one table.

What: reads the result tables the notebooks wrote and collects, under a short
key, each value that ``report/report.md`` quotes, already formatted the way
the report prints it (``12.8%``, ``2,268``, ``+0.121``).
Why: every number in the report must trace to ``results/``, never be typed
by hand. With one table of quoted values, ``tests/test_report.py`` can
check that each number in the report's text appears here, and anyone can
look up where a number comes from (``source`` column).
Reads: CSV and JSON files in ``results/``; design constants from
``src/config.py`` and ``src/track_b.py``.
Writes: ``results/report_numbers.csv`` (key, text, value, source, note).
Used by: ``make numbers`` (``python -m src.report_numbers``), before the
report is written or rebuilt; ``tests/test_report.py``.
"""

import json

import numpy as np
import pandas as pd

from src import config, paths, track_b

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
    """Source files, the readiness gate, the cleaning rules and the samples (notebooks 01, 02, 04)."""
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
    add("linkage_bar_match", "40%", 0.40, "PLAN.md §5.3", "pre-set match bar")
    add("linkage_bar_agree", "80%", 0.80, "PLAN.md §5.3", "pre-set agreement bar")
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
    """Survival curves, size and congestion views, reproduced LBNL figures (notebook 03)."""
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
    """Sample of project-years, hyperparameter searches and their choices (notebooks 05–07)."""
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
    """The registered criteria and the other notebook 08 results."""
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
    """SHAP, partial dependence, sanity checks, ranking book and worked examples (notebook 09)."""
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
        add(f"pd_size_point_{mw}", f"{mw:,}", mw, "notebooks/09_explain_and_rank.ipynb", "size at which partial dependence is quoted, MW")
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
    """The post-hoc analysis of notebook 08b (decision #34)."""
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
    for status, key in [("post-hoc", "ph_pass"), ("registered (notebook 08)", "ph_reg_pass")]:
        part = crit[crit["status"] == status]
        add(key, str(int((part["result"] == "PASS").sum())), int((part["result"] == "PASS").sum()),
            "results/posthoc_criteria.csv", f"Track A lines passed, {status}")
    add("ph_lines", str(int((crit["status"] == "post-hoc").sum())), int((crit["status"] == "post-hoc").sum()),
        "results/posthoc_criteria.csv", "Track A criterion lines")


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
    for step in (design_constants, gathering_and_cleaning, eda, modelling, evaluation, explanation, posthoc):
        step()
    table = pd.DataFrame(ROWS)
    table.to_csv(paths.RESULTS / "report_numbers.csv", index=False)
    return table


if __name__ == "__main__":
    out = build()
    print(f"{len(out)} numbers written to results/report_numbers.csv")
