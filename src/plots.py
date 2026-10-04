"""One figure style for the whole project, and one way to save figures.

What: ``set_style()`` (fonts, sizes, grid), ``finish()`` (finding title,
subtitle and source note), ``save_fig()`` (PNG 300 dpi + SVG, plus a
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
        "savefig.dpi": 300,
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


def finish(fig, title, subtitle, cohort, eia=False, lbnl=True):
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
        source = config.SOURCE_LBNL + (" " + config.SOURCE_EIA if eia else "")
    else:
        source = "Source: " + config.SOURCE_EIA.rstrip(".") + "; author's analysis."
    source_lines = textwrap.wrap(f"{source} Cohort: {cohort}", 125)
    # line heights in figure fractions (points → inches → fraction, 1.25 leading)
    title_h, sub_h, src_h = (size * 1.25 / 72 / height for size in (16, 13, 10.5))
    sub_y = 0.98 - title_h * len(title_lines) - 0.008
    top = sub_y - sub_h * len(subtitle_lines) - 0.02
    bottom = 0.012 + src_h * len(source_lines) + 0.012
    fig.tight_layout(rect=[0, bottom, 1, top])
    renderer = fig.canvas.get_renderer()
    left = min(ax.get_tightbbox(renderer).x0 for ax in fig.axes) / fig.bbox.width
    left = max(left, 0.01)
    fig.text(left, 0.98, "\n".join(title_lines), ha="left", va="top",
             fontsize=16, fontweight="bold", color=INK, linespacing=1.15)
    fig.text(left, sub_y, "\n".join(subtitle_lines), ha="left", va="top",
             fontsize=13, color=MUTED, linespacing=1.15)
    fig.text(left, 0.012, "\n".join(source_lines), ha="left", va="bottom",
             fontsize=10.5, color=MUTED, linespacing=1.15)


def save_fig(fig, name, caption, notebook, folder=None):
    """Save a figure as PNG (300 dpi) and SVG and record its caption stub.

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
    out_dir = paths.FIGURES / folder if folder else paths.FIGURES
    out_dir.mkdir(parents=True, exist_ok=True)
    png, svg = out_dir / f"{name}.png", out_dir / f"{name}.svg"
    fig.savefig(png)
    fig.savefig(svg, metadata={"Date": None})  # no timestamp: identical reruns give identical files
    rel = png.relative_to(paths.REPO).as_posix()
    block = (f"<!-- fig:{name} -->\n### {name}\n\n"
             f"![{name}](../{rel})\n\n"
             f"*Notebook:* `notebooks/{notebook}.ipynb` · *Files:* `{rel}`, `.svg`\n\n"
             f"**Caption (stub).** {caption}\n<!-- /fig:{name} -->\n")
    _upsert_figure_note(name, block)
    return png


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
