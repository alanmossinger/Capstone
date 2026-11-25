"""Figure O1 of the report: where AI fit in the project.

What: a two-lane diagram. The upper lane is the development loop (the author
sets a task, the coding assistant proposes, the tests check, the author
accepts or rejects, the decision log and the commit keep it). The lower lane
is the one stage of the decision process a language model fills (it reads the
committee's words and writes the memo; tools compute and check, a person
decides). Each box is coloured by who acts: a person, the model, or code.
Why: the capstone specification asks for a diagram of how AI fit into the
workflow; Appendix O of the report explains it and names the models.
Reads: nothing.
Writes: ``figures/F58_ai_use.png`` and ``figures/F58_ai_use.svg``.
Used by: ``make ai-figure`` (``python -m src.ai_use_figure``).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from src import paths

INK, MUTED = "#1f2933", "#52606d"  # titles and box text; subtitles, arrows and the legend
FILL_EDGE = {"person": ("#e8f1fb", "#2b6cb0"), "model": ("#fdf0e2", "#c05621"), "code": ("#e9f5ec", "#2f855a")}  # who acts in a box
WIDTH_IN, HEIGHT_IN = 11, 5.6  # the report's standard figure width
DPI = 450

DEVELOPMENT = [("person", "The author sets\nthe task"), ("model", "The assistant proposes\na plan, code or text"),
               ("code", "Automated tests check\nthe code and every\nreport number"),
               ("person", "The author reads the\nchange and accepts\nor rejects it"), ("code", "Decision log\nand commit")]
DECISION = [("person", "The committee\nstates its proposal\nin words"), ("model", "The model reads\nthe words into\nrules"),
            ("code", "Tools compute\nthe numbered\nfact sheet"), ("model", "The model writes\nthe challenge\nmemo"),
            ("code", "Code checks\nevery number\nin the memo"), ("person", "The committee\ndecides; a person\nsigns the ledger")]
LEGEND = [("person", "A person"), ("model", "The language model"), ("code", "Code, without a model")]


def _lane(ax, y, title, subtitle, boxes):
    """Draw one lane: its title, its subtitle and its boxes joined by arrows, with the boxes' lower edge at ``y``."""
    ax.text(0.15, y + 1.18, title, fontsize=13.5, fontweight="bold", color=INK, va="bottom")
    ax.text(0.15, y + 0.98, subtitle, fontsize=10.5, color=MUTED, va="bottom")
    gap, height = 0.28, 0.82
    width = (10.7 - gap * (len(boxes) - 1)) / len(boxes)
    for i, (who, text) in enumerate(boxes):
        x = 0.15 + i * (width + gap)
        fill, edge = FILL_EDGE[who]
        ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.6))
        ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=10.5, color=INK, linespacing=1.2)
        if i < len(boxes) - 1:
            ax.annotate("", xy=(x + width + gap - 0.03, y + height / 2), xytext=(x + width + 0.03, y + height / 2),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4))


def draw():
    """Draw the diagram and return the figure."""
    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN))
    ax.set_xlim(0, WIDTH_IN)
    ax.set_ylim(0, HEIGHT_IN)
    ax.axis("off")
    ax.text(0.15, 5.45, "AI assisted the development and filled one stage of the decision", fontsize=15, fontweight="bold", color=INK, va="top")
    _lane(ax, 3.15, "Building the project", "Claude Code, mainly Claude Opus 5.5, reasoning effort high", DEVELOPMENT)
    _lane(ax, 1.0, "Inside the decision process", "Claude Sonnet 5.5, default temperature, no tools, no web, no memory", DECISION)
    for i, (who, label) in enumerate(LEGEND):
        x = 0.15 + i * 2.6
        fill, edge = FILL_EDGE[who]
        ax.add_patch(FancyBboxPatch((x, 0.28), 0.32, 0.22, boxstyle="round,pad=0.02,rounding_size=0.04", fc=fill, ec=edge, lw=1.4))
        ax.text(x + 0.45, 0.39, label, fontsize=10.5, color=MUTED, va="center")
    fig.subplots_adjust(0, 0, 1, 1)
    return fig


def save(name="F58_ai_use"):
    """Write the diagram as PNG and SVG in ``figures/`` and return the PNG path."""
    fig = draw()
    paths.FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(paths.FIGURES / f"{name}.svg", facecolor="white", metadata={"Date": None})
    fig.savefig(paths.FIGURES / f"{name}.png", dpi=DPI, facecolor="white")
    plt.close(fig)
    return paths.FIGURES / f"{name}.png"


if __name__ == "__main__":
    print(f"written: {save()}")
