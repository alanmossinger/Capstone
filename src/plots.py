"""One figure style for the whole project, and one way to save figures.

What: ``set_style()`` (fonts, sizes, grid), ``finish()`` (finding title,
subtitle and source note), ``save_fig()`` (PNG 450 dpi + SVG, plus a
caption stub in ``report/figure_notes.md``) and small color helpers.
Why: every figure readable at report size, colorblind-safe,
ERCOT/PJM/CAISO always in the same colors, a title that states the finding
and a source line on every figure.
Reads: nothing.
Writes: ``figures/<folder>/<name>.png|.svg`` and ``report/figure_notes.md``.
Used by: every notebook that draws a figure.

Colors: the Okabe–Ito palette. The region and technology sets were checked
with a color-vision-deficiency validator; the weakest technology pair
(Battery vs Solar+Battery) is never stacked next to each other and every
multi-series figure carries a legend, so identity never rests on color alone.
Regions outside the three Track A ISOs are drawn in grey rather than in new
hues.
"""

import re
import textwrap
import time

import matplotlib as mpl

from src import config, paths

INK = "#222222"  # titles, labels and values
MUTED = "#666666"  # subtitles, source notes, axes
GRID = "#E5E5E5"  # recessive solid grid


def set_style():
    """Apply the project's matplotlib defaults.

    Notes
    -----
    Sizes follow the project figure standard: 11 × 6.5 in, base 13 pt, axis labels 14,
    ticks 12, legend 12 (the 16 pt finding title is drawn by ``finish``).
    Lines are at least 2 pt; the grid is a light solid hairline drawn under
    the data; SVG text stays editable text.
    """
    mpl.rcParams.update({
        "figure.figsize": (11, 6.5),
        "figure.dpi": 100,
        "figure.facecolor": "white",
        "font.size": 13,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 14,
        "axes.labelcolor": INK,
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "legend.fontsize": 12,
        "legend.frameon": False,
        "lines.linewidth": 2.2,
        "lines.markersize": 7,
        "patch.linewidth": 0,
        "text.color": INK,
        "savefig.dpi": 450,  # readable when a figure is printed at page width (outside review, 14 Oct)
        "savefig.facecolor": "white",
        "svg.fonttype": "none",
        "svg.hashsalt": "queue-survival",  # stable element ids, so reruns do not churn git
    })


def region_color(region):
    """Fixed color for a Track A region, grey for every other region."""
    return config.REGION_COLORS.get(region, config.OTHER_REGION_COLOR)


def tech_group(type_clean):
    """Fold LBNL ``type_clean`` (or a crosswalk type) into the seven plot groups.

    Notes
    -----
    Seven is the most series a panel may carry. Solar+Battery
    is kept apart because hybrids are a large and growing share of the queue;
    every other hybrid and minor technology goes to "Other".
    """
    return type_clean if type_clean in config.TECH_COLORS else "Other"



# Report-figure titles: the finding in twelve words or fewer (outside review, 14 Oct 2026). The long sentence a
# notebook passes to ``finish`` carries numbers; those live in the report's text and in each notebook's
# *Reading this* cell, and ``save_fig`` redraws the title from this table for every figure named here.
SHORT_TITLES = {
    "02_C5_asset_map": "Two areas hold most Gulf oil; Texas plants cluster by fuel",
    "02_C6_correlation_and_clusters": "Prices and output barely move together; decline shapes split in two",
    "F1_cif_by_region": "ERCOT requests reach operation most often; CAISO's least",
    "F2_operation_by_technology": "Gas is built fastest; batteries and hybrids slowest",
    "F3_five_year_by_size": "Small requests are built more often in PJM and CAISO",
    "F4_calibration_by_horizon": "The model's probabilities run high in the middle range",
    "F5_auc_brier_by_horizon": "The model ranks requests better than cohort averages",
    "F6_hazard_ratios": "Gas requests reach operation fastest; ERCOT leads the three regions",
    "F7_shap_summary": "State, size and technology drive the model's predictions",
    "F8_congestion_vs_completion": "In PJM, a crowded queue lowers the chance of operation",
    "F9_project_map": "Three grid regions hold about 40% of the capacity waiting to connect",
    "F10_gains_over_baselines": "At entry, a careful lookup matches the model at utility scale",
    "F11_level_by_entry_year": "Recent cohorts complete far below the historical level",
    "F12_landmark_models": "Two years in, knowing the agreement status sharpens the model's ranking",
    "F13_expected_mw_and_value": "Raw model levels overstate the megawatts a cohort delivers",
    "F14_simulated_book": "The simulated band brackets what a book delivers",
    "F15_backtest": "At entry, the model's book delivers what the lookup's does",
    "F16_constraint_map": "Queues swell; recent entrants neither leave nor get built as before",
    "F17_miso_spp": "In MISO the model beats the lookup; SPP is too thin",
    "F18_managed_book": "The model's two-year picks operate more often but deliver no more megawatts",
    "F19_drivers": "Size, technology and the agreement decide which requests get built",
    "F20_when_requests_die": "CAISO and PJM lose requests in year one; ERCOT after year four",
    "F21_segments": "Ten entry rules sort requests by their odds of completion",
    "F22_tournament": "Other machine-learning models beat neither the chosen model nor the lookup",
    "F23_portfolio_review": "Funded requests operated more often than exits, except ERCOT's at entry",
    "F24_book_per_region": "Two years in, the model's picks operate at twice the average rate",
    "F25_state_archetypes": "States fall into market types with different completion rates",
    "F26_npv_per_mw": "With capital counted, few plants pay at merchant prices",
    "F27_forecast_gains": "Machine learning beats baselines for plant output, not for leases",
    "F28_candidates": "Leases add value; wind and solar requests pay only under contract",
    "F29_cost_tornado": "The uplift share and operating cost decide the lease book",
    "F30_price_scenarios": "Simulated prices keep history's jumps and drift back to the average",
    "F31_candidate_risk": "Leases rarely lose money; most power requests usually do",
    "F32_stresses": "Every stress test leaves the default book's expected value positive",
    "F33_four_books": "Four books under one budget and cap, scored out of sample",
    "F35_horizon_view": "Leases pay from year three; queue requests stay a cost",
    "F36_ai_workflow": "The advisor sees only result tables; humans override through a gate",
    # the decision figures of notebook 11, reviewed against their charts on 26 November 2026 (mentor review of the report figures)
    "F38_frontier": "Weighting risk more heavily gives up expected value for smaller worst-case losses",
    "F39_reallocation": "Cheap oil empties the book of leases; wind stays in every case",
    "F42_value_added": "The risk-aware book earns less on average but outscores two rivals clearly",
}

# Report-figure subtitles in plain English (mentor review of the report figures, 26 November 2026): two or three short
# sentences a general reader can follow, saying what each panel shows and how to read it, with no project shorthand
# (registered, rungs, static basis, committee grid, criterion codes). The notebook's own subtitle keeps the technical
# detail (cohort, n, resamples) and shows in the notebook's *Reading this* cell; ``save_fig`` redraws the subtitle from
# this table for every figure named here, exactly as it redraws the title from ``SHORT_TITLES``. Figure F51's subtitle
# names a leader computed in notebook 13, so it is written there.
SHORT_SUBTITLES = {
    "02_C5_asset_map": "Left: 2024 oil production by offshore area of the Gulf of Mexico. Right: Texas power plants by fuel; larger markers are larger plants.",
    "02_C6_correlation_and_clusters": "Left: how closely monthly changes in prices, Gulf output and Texas plant output move together (1 = perfectly, 0 = not at all). Right: the two typical ways an oil lease's output declines in the three years after its peak month.",
    "F1_cif_by_region": "The share of grid-connection requests that have started operating (left) or been withdrawn (right), by years since the request. Shaded bands are 95% intervals. ERCOT is the Texas grid, PJM the mid-Atlantic grid and CAISO California's.",
    "F6_hazard_ratios": "How much faster (right of 1) or slower (left of 1) each kind of request reaches operation or withdraws, compared with a mid-sized solar request in PJM. Bars are 95% intervals.",
    "F9_project_map": "Left: projects waiting to connect to the grid at the end of 2024, one bubble per county, sized by capacity. Right: power plants operating today. Colours mark the three grid regions studied: ERCOT (Texas), PJM (mid-Atlantic) and CAISO (California).",
    "F12_landmark_models": "Change in forecast quality when the model is told what has happened since a request joined the queue, at four checkpoints. Left: ranking accuracy. Right: probability error. Above zero is an improvement; bars are 95% intervals.",
    "F16_constraint_map": "By region and the year a request joined the queue: the capacity already waiting there (left), and the shares withdrawn (middle) and operating (right) within three years. Grey lines are the six other regions.",
    "F18_managed_book": "Requests operating (left) and megawatts operating (right) within three years, for sets of 25 and 50 requests picked two years into the queue by the model, by three lookup tables of past completion rates, and at random. Bars are 95% intervals.",
    "F19_drivers": "The share of requests operating within five years, split six ways: size, technology, how crowded the regional queue and the county were, the type of grid service, and whether a connection agreement was signed. Bars are 95% intervals.",
    "F20_when_requests_die": "Left: the yearly chance that a waiting request withdraws or starts operating. Middle: the study stage reached when requests withdrew. Right: the chance of operating within three years for requests that have already waited 0, 1 or 2 years.",
    "F21_segments": "Ten simple rules built from what is known when a request joins the queue, each with its five-year completion rate: for the 2010–2016 requests the rules were built on (circles) and for later requests (blue, 95% intervals).",
    "F22_tournament": "The best alternative model against two references, the chosen model (LightGBM) and a lookup table of past completion rates, at three, five and seven years. Left: ranking accuracy (above 0 is better). Right: probability error (below 0 is better). Bars are 95% intervals.",
    "F23_portfolio_review": "The share of requests that reached operation, grouped by what the decision rule said at entry (left) and two years in (right): invest or accelerate, hold, or exit. Top: selling at market prices. Bottom: under a fixed-price contract. Bars are 95% intervals.",
    "F24_book_per_region": "Left: requests operating within three years as more are added in each method's preferred order (dashed: what the method expected). Right: operations by region for the requests each method would keep; the two methods keep different numbers, so the bars are not like for like.",
    "F25_state_archetypes": "Left: states grouped by seven features of their grid-connection queues. Right: the share of 2017–2019 requests operating by the end of 2024 in each group, an outcome the grouping never used. Bars are 95% intervals.",
    "F26_npv_per_mw": "Value per megawatt of a new plant over twenty years, after its building cost, by technology and region. Merchant means selling at market prices; contracted means a fixed-price 15-year sales agreement. Lines run from the low case to the high case.",
    "F27_forecast_gains": "Forecast error of the machine-learning model relative to the best simple method, for each quantity forecast; left of zero means machine learning is better. Green lines passed a test set in advance, orange failed it, grey were reported only. Bars are 95% intervals.",
    "F28_candidates": "Left: the value added by redeveloping each of twenty Gulf oil and gas leases, with its low-cost to high-cost range. Right: the expected value of twenty Texas power requests at market prices (bars) and under a fixed-price contract (dots), after counting the chance they are never built.",
    "F30_price_scenarios": "2,000 simulated price paths for oil (WTI), natural gas (Henry Hub) and Texas power (ERCOT), built by reshuffling the monthly changes of 2018–2024 around a level that drifts back to the 2018–2024 average.",
    "F32_stresses": "The expected value of the forty-candidate default book under six stress tests: an oil-price collapse, dearer gas, weak wind, lower solar revenue, a two-year delay, and all of them at once with costs 20% higher.",
    "F34_decision_gym": "What four ways of choosing would have earned in past situations, replayed with only the information available at the time: two rules of thumb (instinct), the project's fixed rule and the AI advisor. The black tick is the best choice with hindsight.",
    "F35_horizon_view": "Left: the expected value of the forty candidates counted over 1 to 20 years, for offshore leases and Texas power requests. Right: how many of each a value-maximising book holds at each horizon.",
    "F38_frontier": "A book is the set of projects one decision process funds. Left: each point is a book chosen with a different weight on risk (λ), scored on 2,000 simulated futures it was not chosen on. Right: what the books along the line spend, by technology; the dashed line is the budget.",
    "F39_reallocation": "What the risk-aware book (book D) spends by technology when it is chosen again under each of five what-if questions a committee might ask.",
    "F41_staged": "The risk-aware book (book D) is either held for twenty years or revised on 1 January 2027 after two years of new information. Left: the difference in value in each simulated future. Right: the two ranges of outcomes, which overlap.",
    "F42_value_added": "Each row compares two ways of deciding on the same 2,000 simulated futures, with 95% intervals. Left: the difference in expected value. Right: the difference in the score, expected value minus the average loss in the worst 5% of futures. An interval that crosses zero means no clear difference.",
    "F43_architecture": "The six steps of the decision process. The language model works only in step 4: it reads and argues, and never calculates a value or decides.",
    "F44_advisor_tools": "How a committee's question is answered: the language model translates and explains, the calculation engine computes, and a person decides.",
    "F45_robustness": "Left: how much construction money the risk-aware book (book D) needs beyond its reserve in each simulated future. Right: how often each candidate is picked when the book is chosen again on 20 reshuffled sets of futures; a core member is picked at least 80% of the time.",
    "F46_challenger": "Left: how often the language model's memo (blue) and a plain checklist (grey) name each type of flaw planted in a proposal. Right: what each adds to a simulated committee's result per case, with 95% intervals; *a fixed rule that takes the optimizer's answer first. Below the dotted line: worst-case loss avoided.",
    "F47_ladder": "The gain per case from each step of support for a simulated investment committee: tools only, tools plus the language model, then the optimizer. Bars are 95% intervals. This was a trial run on earlier cases, before the final test was fixed in advance.",
    "F48_credit_line_net": "The risk-aware book's score (expected value minus the average loss in the worst 5% of futures) by the size of a credit line for construction overruns: before financing costs, after a 0.5% yearly fee, and after the fee plus 8% interest on money drawn.",
    "F49_forward_calibration": "Left: the predicted one-year chance of operating against the share of requests that did operate in 2025; the dashed line is a perfect forecast. Right: the twenty candidate requests, their predicted chance and what happened to each in 2025.",
    "F50_ladder_v10": "The gain per case from each step of support for a simulated investment committee, on 48 test cases whose scoring rules were fixed in writing before the results were seen (pre-registered). Bars are 95% intervals.",
    "F52_what_can_go_wrong": "Left: each book's average loss in the worst 5% of futures as its projects are made to rise and fall together, from independently (0) to as modelled (1); triangles mark the extreme where every project has its worst outcome at once. Right: each book's score if the model is wrong in one of six ways.",
    "F53_ladder_five_arms": "Left: the average result for simulated investment committees under five ways of reviewing a proposal. Right: the gain from one way to the next, with 95% intervals; an interval that crosses zero means no clear difference. The optimizer-first rule takes the optimizer's answer and uses no language model.",
    "F54_allocation": "Each project in the risk-aware book: the capital it takes now (solid) and its expected value (hatched), with how often it loses money and what the book's score loses if it is removed.",
    "F55_committee_workflow": "How a proposal moves from the committee's words to a signed, tamper-evident record. At stage 5 the language model may only explain, challenge or guide, and code checks every number it writes.",
    "F56_readiness_matrix": "Twelve safeguards of the system: whether each is in place, how it was tested, its known limitation, and what a committee should verify before committing real money.",
    "F57_book_distributions": "A book is the set of projects one decision process funds. Each panel shows one book's twenty-year value in the same 2,000 simulated futures, with the 100 worst shaded. Dashed lines mark the average of all futures and the average of the 100 worst.",
}


def finish(fig, title, subtitle, cohort, eia=False, lbnl=True, lbnl_2026=False, sources=None, provenance=None):
    """Add the finding title, the subtitle and the source note, then lay out.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        A drawn figure.
    title : str
        The finding, as a sentence.
    subtitle : str
        What is plotted, the cohort and n.
    cohort : str
        Cohort named in the source note.
    eia : bool
        Credit EIA-860M.
    lbnl : bool
        Credit the LBNL file (False for figures drawn from EIA data only).
    lbnl_2026 : bool
        Also credit the 2026 edition (figures of notebook 01 (part C) and notebook 04 (parts F, G and K)).
    sources : list of str, optional
        Data credits for the v5 energy sources (``config.SOURCE_BSEE`` …);
        when given and ``lbnl`` is False, they replace the LBNL credit.
    provenance : str, optional
        One of ``config.PROVENANCE`` (OBSERVED, DERIVED, FORECAST, ASSUMED):
        the audit label printed at the end of the source note on every v5
        figure (docs/plan.md §14.0). A label outside the set raises.

    Notes
    -----
    Long lines are wrapped rather than shrunk. The height the wrapped text
    needs is reserved first and the axes are laid out in what is left, so a
    two-line title never overlaps the plot. The text block is aligned with
    the left edge of the tick labels, not of the axes, so long category
    labels cannot push the title off the page.
    """
    height = fig.get_figheight()
    title_lines = textwrap.wrap(title, 72)
    subtitle_lines = textwrap.wrap(subtitle, 100)
    if lbnl:
        source = config.SOURCE_LBNL + (" " + config.SOURCE_LBNL_2026 if lbnl_2026 else "") + (" " + config.SOURCE_EIA if eia else "")
    elif sources:
        source = config.FIGURE_AUTHOR + " Data: " + " ".join(sources) + (" " + config.SOURCE_EIA if eia else "")
    else:
        source = config.FIGURE_AUTHOR + " Data: " + config.SOURCE_EIA
    if provenance is not None:
        if provenance not in config.PROVENANCE:
            raise ValueError(f"provenance must be one of {config.PROVENANCE}, got {provenance!r}")
        source = f"{source} Provenance: {provenance}."
    source_lines = textwrap.wrap(f"{source} Cohort: {cohort}", 125)
    # line heights in figure fractions (points → inches → fraction, 1.25 leading)
    title_h, sub_h, src_h = (size * 1.25 / 72 / height for size in (16, 13, 10.5))
    sub_y = 0.98 - title_h * len(title_lines) - 0.008
    top = sub_y - sub_h * len(subtitle_lines) - 0.02
    bottom = 0.012 + src_h * len(source_lines) + 0.012
    fig.tight_layout(rect=[0, bottom, 1, top])
    renderer = fig.canvas.get_renderer()
    # a y-label taller than its axes runs into the subtitle or the source note: shrink it until it fits (outside review, 14 Oct)
    shrunk = False
    for ax in fig.axes:
        label = ax.yaxis.label
        if not label.get_text():
            continue
        while label.get_window_extent(renderer).height > ax.get_window_extent(renderer).height and label.get_fontsize() > 9:
            label.set_fontsize(label.get_fontsize() - 0.5)
            shrunk = True
    if shrunk:
        fig.tight_layout(rect=[0, bottom, 1, top])
    left = min(ax.get_tightbbox(renderer).x0 for ax in fig.axes) / fig.bbox.width
    left = max(left, 0.01)
    texts = [fig.text(left, 0.98, "\n".join(title_lines), ha="left", va="top",
                      fontsize=16, fontweight="bold", color=INK, linespacing=1.15),
             fig.text(left, sub_y, "\n".join(subtitle_lines), ha="left", va="top",
                      fontsize=13, color=MUTED, linespacing=1.15),
             fig.text(left, 0.012, "\n".join(source_lines), ha="left", va="bottom",
                      fontsize=10.5, color=MUTED, linespacing=1.15)]
    # kept so save_fig can redraw the title from SHORT_TITLES and the subtitle from SHORT_SUBTITLES without the notebook changing
    fig._finish = {"texts": texts, "title": title, "subtitle": subtitle, "cohort": cohort, "eia": eia, "lbnl": lbnl, "lbnl_2026": lbnl_2026,
                   "sources": sources, "provenance": provenance}


def save_fig(fig, name, caption, notebook, folder=None):
    """Save a figure as PNG (450 dpi) and SVG and record its caption stub.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Finished figure (after ``finish``).
    name : str
        File stem, e.g. ``"01_03_status_mix_by_region"`` or ``"F1_cif_by_region"``.
    caption : str
        One or two sentences: what the figure shows. The interpretation lives
        in the notebook's *Reading this* cell.
    notebook : str
        Notebook that drew it, e.g. ``"01_get_data"``.
    folder : str, optional
        Subfolder of ``figures/``; report figures (F1–F9) sit at the top level.

    Returns
    -------
    pathlib.Path
        Path of the PNG.

    Notes
    -----
    ``report/figure_notes.md`` holds one block per figure between HTML
    comment markers. Re-running a notebook replaces the figure's block
    instead of appending a duplicate, and blocks stay sorted by name so the
    file reads as a gallery the report's captions are chosen from.
    """
    if (name in SHORT_TITLES or name in SHORT_SUBTITLES) and getattr(fig, "_finish", None):
        kept = fig._finish
        for text in kept["texts"]:
            text.remove()
        finish(fig, SHORT_TITLES.get(name, kept["title"]), SHORT_SUBTITLES.get(name, kept["subtitle"]), kept["cohort"], eia=kept["eia"], lbnl=kept["lbnl"],
               lbnl_2026=kept["lbnl_2026"], sources=kept["sources"], provenance=kept["provenance"])
    out_dir = paths.FIGURES / folder if folder else paths.FIGURES
    out_dir.mkdir(parents=True, exist_ok=True)
    png, svg = out_dir / f"{name}.png", out_dir / f"{name}.svg"
    _save_with_retry(fig, png)
    _save_with_retry(fig, svg, metadata={"Date": None})  # no timestamp: identical reruns give identical files
    save_executive(fig, name)
    rel = png.relative_to(paths.REPO).as_posix()
    block = (f"<!-- fig:{name} -->\n### {name}\n\n"
             f"![{name}](../{rel})\n\n"
             f"*Notebook:* `notebooks/{notebook}.ipynb` · *Files:* `{rel}`, `.svg`\n\n"
             f"**Caption (stub).** {caption}\n<!-- /fig:{name} -->\n")
    _upsert_figure_note(name, block)
    return png


EXECUTIVE_WIDTH = 9.0  # inches; placed at a 6.5-inch text width the 13-pt base type reads at about 9.5 pt, the size of an executive report's figures
EXECUTIVE_DIR = paths.FIGURES / "executive"
EXECUTIVE_KEEP_WIDTH = {"F0_overview", "F36_ai_workflow", "F43_architecture", "F55_committee_workflow"}  # diagrams drawn in figure coordinates: their boxes and labels are placed for the 11-inch width


def _shorten(text, limit):
    """The text cut at the last sentence or clause boundary before ``limit`` characters; whole if it fits."""
    if len(text) <= limit:
        return text
    cut = max(text.rfind(". ", 0, limit), text.rfind("; ", 0, limit))  # a sentence or clause end, never a comma inside a parenthesis
    if cut <= 40:
        return text[:limit].rstrip() + "…"
    return text[:cut].rstrip(" ,;") + ("." if text[cut] == "." else "")


def save_executive(fig, name, out_dir=EXECUTIVE_DIR):
    """Save the executive copy of a finished figure: narrower, the finding and one short subtitle inside, no source footer.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        A figure after ``finish`` (and after ``save_fig``'s academic copies).
    name : str
        File stem; the copy goes to ``figures/executive/<name>.svg`` and ``.png``.

    Notes
    -----
    The executive copy of a figure places it at
    full text width with the source and provenance in the caption, as an
    executive report does, so the copy drops the source footer and keeps a
    subtitle of at most two lines; the finding stays in the image. The
    figure is 9 inches wide (its height scaled; a figure of two or more
    panels keeps its width) and saved with a tight bounding box, so at the report's 6.5-inch width the type reads at about
    0.72 of its point size: 15-pt titles at 11 pt, 12-pt ticks at 9 pt. The academic figure is restored afterwards, so
    the notebook shows what ``save_fig`` saved.
    """
    kept = getattr(fig, "_finish", None)
    if kept is None:
        return None
    width, height = fig.get_size_inches()
    for text in kept["texts"]:
        text.remove()
    panels = {round(ax.get_position().x0, 2) for ax in fig.axes if ax.get_position().width > 0.12}  # columns of panels (colour bars excluded)
    keep = len(panels) >= 2 or name in EXECUTIVE_KEEP_WIDTH  # two or more panels, or a diagram laid out in figure coordinates, keep their width: their titles and labels are set for it
    exec_width = width if keep else EXECUTIVE_WIDTH
    fig.set_size_inches(exec_width, height * exec_width / width)
    exec_height = fig.get_figheight()
    title_lines = textwrap.wrap(kept["title"], 62)
    subtitle_lines = textwrap.wrap(_shorten(kept["subtitle"], 200), 100)[:2]
    title_h, sub_h = (size * 1.25 / 72 / exec_height for size in (15, 10.5))
    sub_y = 0.985 - title_h * len(title_lines) - 0.006
    top = sub_y - sub_h * len(subtitle_lines) - 0.025
    fig.tight_layout(rect=[0, 0.01, 1, top])
    renderer = fig.canvas.get_renderer()
    left = max(min(ax.get_tightbbox(renderer).x0 for ax in fig.axes) / fig.bbox.width, 0.01)
    texts = [fig.text(left, 0.985, "\n".join(title_lines), ha="left", va="top", fontsize=15, fontweight="bold", color=INK, linespacing=1.15),
             fig.text(left, sub_y, "\n".join(subtitle_lines), ha="left", va="top", fontsize=10.5, color=MUTED, linespacing=1.15)]
    out_dir.mkdir(parents=True, exist_ok=True)
    _save_with_retry(fig, out_dir / f"{name}.svg", metadata={"Date": None}, bbox_inches="tight", pad_inches=0.06)  # the canvas grows to hold every label
    _save_with_retry(fig, out_dir / f"{name}.png", bbox_inches="tight", pad_inches=0.06)
    for text in texts:
        text.remove()
    fig.set_size_inches(width, height)
    finish(fig, kept["title"], kept["subtitle"], kept["cohort"], eia=kept["eia"], lbnl=kept["lbnl"], lbnl_2026=kept["lbnl_2026"],
           sources=kept["sources"], provenance=kept["provenance"])
    return out_dir / f"{name}.svg"


def _save_with_retry(fig, path, attempts=6, wait_s=0.5, **kwargs):
    """Save a figure, retrying briefly when the file is locked.

    Notes
    -----
    The repository lives in a OneDrive folder, and OneDrive holds a file it
    is uploading for a moment; a rewrite in that moment raises ``OSError``
    (errno 22 or 13). A few short retries clear it without changing the
    figure; the last failure is raised as it was.
    """
    for attempt in range(attempts):
        try:
            fig.savefig(path, **kwargs)
            return
        except OSError as err:
            if err.errno not in (22, 13) or attempt == attempts - 1:
                raise
            time.sleep(wait_s * (attempt + 1))


def _upsert_figure_note(name, block):
    """Insert or replace one figure's block in figure_notes.md, keeping name order."""
    header = ("# Figure notes\n\n"
              "Caption stubs collected by `src/plots.save_fig()` each time a notebook "
              "runs. The interpretation of each figure is in the *Reading this* cell "
              "under it in the notebook. Report captions are written from these.\n\n")
    text = paths.FIGURE_NOTES.read_text(encoding="utf-8") if paths.FIGURE_NOTES.exists() else ""
    pattern = re.compile(r"(?s)<!-- fig:(.+?) -->.*?<!-- /fig:\1 -->\n")
    blocks = {match.group(1): match.group(0) for match in pattern.finditer(text)}
    blocks[name] = block
    body = "\n".join(blocks[key] for key in sorted(blocks))
    paths.FIGURE_NOTES.parent.mkdir(parents=True, exist_ok=True)
    paths.FIGURE_NOTES.write_text(header + body, encoding="utf-8")
