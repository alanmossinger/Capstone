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
    "F6_hazard_ratios": "ERCOT and gas requests reach operation fastest",
    "F7_shap_summary": "State, size and technology drive the model's predictions",
    "F8_congestion_vs_completion": "In PJM, a crowded queue lowers the chance of operation",
    "F9_project_map": "Three ISOs hold most of the capacity waiting to connect",
    "F10_gains_over_baselines": "At entry, a careful lookup matches the model at utility scale",
    "F11_level_by_entry_year": "Recent cohorts complete far below the historical level",
    "F12_landmark_models": "Two years in, updated information sharpens the model's ranking",
    "F13_expected_mw_and_value": "Raw model levels overstate the megawatts a cohort delivers",
    "F14_simulated_book": "The simulated band brackets what a book delivers",
    "F15_backtest": "At entry, the model's book delivers what the lookup's does",
    "F16_constraint_map": "Queues swell; recent entrants neither leave nor get built as before",
    "F17_miso_spp": "In MISO the model beats the lookup; SPP is too thin",
    "F18_managed_book": "Two years in, the model's book holds more operations",
    "F19_drivers": "Size, technology and the agreement decide which requests get built",
    "F20_when_requests_die": "CAISO and PJM cull in year one; ERCOT after year four",
    "F21_segments": "Ten entry rules sort requests by their odds of completion",
    "F22_tournament": "Other learners tie LightGBM and do not beat the lookup",
    "F23_portfolio_review": "Funded requests operated more often than exits, except ERCOT's at entry",
    "F24_book_per_region": "Two years in, the floor book operates at twice the pool rate",
    "F25_state_archetypes": "State markets fall into archetypes that separate completion",
    "F26_npv_per_mw": "With capital counted, few plants pay at merchant prices",
    "F27_forecast_gains": "Machine learning beats baselines for plant output, not for leases",
    "F28_candidates": "Leases add value; wind and solar requests pay only under contract",
    "F29_cost_tornado": "The uplift share and operating cost decide the lease book",
    "F30_price_scenarios": "Scenarios keep history's price jumps around a reverting level",
    "F31_candidate_risk": "Leases rarely lose money; most power requests usually do",
    "F32_stresses": "Every named stress leaves the default book positive",
    "F33_four_books": "Four books under one budget and cap, scored out of sample",
    "F35_horizon_view": "Leases pay from year three; queue requests stay a cost",
    "F36_ai_workflow": "The advisor sees only result tables; humans override through a gate",
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
        figure (PLAN.md §14.0). A label outside the set raises.

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
    # kept so save_fig can redraw the title from SHORT_TITLES without the notebook changing
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
    if name in SHORT_TITLES and getattr(fig, "_finish", None):
        kept = fig._finish
        for text in kept["texts"]:
            text.remove()
        finish(fig, SHORT_TITLES[name], kept["subtitle"], kept["cohort"], eia=kept["eia"], lbnl=kept["lbnl"], lbnl_2026=kept["lbnl_2026"],
               sources=kept["sources"], provenance=kept["provenance"])
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
EXECUTIVE_KEEP_WIDTH = {"F0_overview", "F36_ai_workflow", "F55_committee_workflow"}  # diagrams drawn in figure coordinates: their boxes and labels are placed for the 11-inch width


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
    The executive report (``report/petrobras_report.typ``) places figures at
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
