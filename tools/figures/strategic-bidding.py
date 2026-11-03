"""Evidence charts for the Endogenous Response page (src/research/strategic-bidding/).

Every plotted number is copied from the strategic-bidding paper
(Rosemberg et al., "Strategic Bidding in Energy Markets with Gradient-Based
Iterative Methods", SEGAN 2025 / IREP 2025; version of 12 Jun 2025) and is
recorded in .editorial/claims/strategic-bidding.tsv.

    .venv/bin/python tools/figures/strategic-bidding.py

The profit cross sections use the original vector paths from the author's
paper PDFs, copied into strategic-bidding-profit-source.json. That file keeps
the original page coordinates, source hashes, and tick calibration. It is not
an experimental rerun or a digitization of the raster images.

Writes src/assets/img/research/strategic-bidding-<name>.svg and replaces the
older bidding-{dc,ac}-profit.png assets without changing their HTML layout.
"""

from decimal import ROUND_HALF_UP, Decimal
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "src" / "assets" / "img" / "research"

# Site palette and type, as in tools/make_figures.py.
INK, MUTED, LINE = "#202a33", "#687078", "#dddcd5"
GREY, AMBER = "#46515b", "#b9741f"
NOMINAL = "#a43e42"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none",
    "path.simplify": False,
    "font.size": 11,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})


def save(fig, name):
    fig.savefig(OUT / f"strategic-bidding-{name}.svg", transparent=True)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Nonlinear (AC) clearing, five PGLib systems. Paper Table I (profit) and
# Table II (OPF evaluations), mean and standard deviation over case variations.
#   "Best"    = best gradient-based solver vs best derivative-free solver
#   "Overall" = average over all gradient-based vs all derivative-free solvers
# Ordered by the best-vs-best profit gain.
# --------------------------------------------------------------------------- #
SYSTEMS = ["PEGASE 2869", "PEGASE 1354", "RTE 2868", "GOC 2000", "IEEE 300"]
PROFIT_BEST = np.array([109.996, 102.119, 28.299, 2.179, -1.087])
PROFIT_BEST_SD = np.array([11.721, 12.700, 7.964, 0.967, 19.881])
PROFIT_ALL = np.array([95.730, 80.188, 27.699, 7.533, 12.162])
PROFIT_ALL_SD = np.array([22.919, 31.25, 9.047, 5.312, 39.075])
EVALS_BEST = np.array([23.7, 41.0, 44.4, 36.5, 19.0])
EVALS_BEST_SD = np.array([22.731, 25.342, 5.602, 12.869, 24.833])
EVALS_ALL = np.array([42.508, 49.632, 48.250, 44.100, 41.260])
EVALS_ALL_SD = np.array([16.638, 16.573, 16.797, 16.244, 8.133])

SERIES = [("Best vs best", GREY), ("Averages over methods", AMBER)]


def pct(v):
    """One-decimal percentage, rounding half away from zero (48.250 -> 48.3)."""
    q = Decimal(str(v)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{q}%".replace("-", "\u2212")


def paired_hbar(ax, best, best_sd, allm, all_sd, xlim, xlabel, title, labels=True, compact=False):
    y = np.arange(len(SYSTEMS))[::-1].astype(float)
    h = .34
    err = dict(ecolor=MUTED, elinewidth=.9, capsize=2.2, capthick=.9)
    for vals, sd, off, (_, color) in ((best, best_sd, h / 2 + .02, SERIES[0]), (allm, all_sd, -h / 2 - .02, SERIES[1])):
        ax.barh(y + off, vals, height=h, color=color, xerr=sd, error_kw=err, zorder=2)
        for yi, v, s in zip(y + off, vals, sd):
            x = max(v + s, 0) + (xlim[1] - xlim[0]) * .015
            ax.text(x, yi, pct(v), va="center", fontsize=12 if compact else 10.5, color=INK)
    ax.axvline(0, color=INK, lw=.9, zorder=3)
    ax.set_yticks(y, SYSTEMS if labels else [""] * len(SYSTEMS))
    ax.set_xlim(*xlim)
    ax.set_ylim(-.6, len(SYSTEMS) - .4)
    ax.tick_params(axis="y", length=0, labelsize=12 if compact else 11.5, labelcolor=INK)
    ax.tick_params(axis="x", labelsize=12 if compact else 11)
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=12 if compact else 11)
    ax.set_title(title, fontsize=13, loc="left", pad=12)


def legend(fig, y, ncol):
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in SERIES]
    fig.legend(handles, [s for s, _ in SERIES], loc="upper left", bbox_to_anchor=(0.01, y), ncol=ncol,
               frameon=False, fontsize=12, handlelength=1.1, handleheight=.9, columnspacing=1.6)


def fig_nonlinear(compact=False):
    profit = (PROFIT_BEST, PROFIT_BEST_SD, PROFIT_ALL, PROFIT_ALL_SD, (-32, 160),
              "Profit gain (%)", "Profit")
    # IEEE 300's best-vs-best mean minus one SD is negative; retain that whisker.
    evals = (EVALS_BEST, EVALS_BEST_SD, EVALS_ALL, EVALS_ALL_SD, (-10, 88),
             "Fewer clearing evaluations (%)", "Clearing evaluations")
    if compact:
        fig, axes = plt.subplots(2, 1, figsize=(4.25, 8.8))
        paired_hbar(axes[0], *profit, compact=True)
        paired_hbar(axes[1], *evals, compact=True)
        fig.tight_layout(h_pad=2.8, rect=(0, 0, 1, .90))
        legend(fig, 1.0, 1)
        save(fig, "nonlinear-compact")
    else:
        fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.9), gridspec_kw={"width_ratios": [1.25, 1]})
        paired_hbar(axes[0], *profit)
        paired_hbar(axes[1], *evals, labels=False)
        fig.tight_layout(w_pad=2.5, rect=(0, 0, 1, .88))
        legend(fig, 1.0, 2)
        save(fig, "nonlinear")


def profit_coordinates(panel, vertices):
    """Affine unit conversion only; retain every original polyline vertex."""
    xy = np.asarray(vertices)
    (x0, px0), (x1, px1) = panel["x_ticks"][:2]
    (y0, py0), (y1, py1) = panel["y_ticks"][:2]
    x = x0 + (xy[:, 0] - px0) * (x1 - x0) / (px1 - px0)
    y = y0 + (xy[:, 1] - py0) * (y1 - y0) / (py1 - py0)
    return x, y / 1000  # dollars -> thousands of dollars, stated on the axis


def fig_profit():
    """Legible cross sections in the existing paired-image layout.

    Reader question: how does the clearing model change scenario-level profit
    along the same offer direction? Figs. 4–5 supply the evidence. Twenty
    evenly spaced source-order paths, the original mean, and the nominal curve
    are plotted without smoothing. Identical axes preserve comparability.
    Quantile bands are omitted to expose the individual scenario paths.
    """
    source = json.loads((OUT / "strategic-bidding-profit-source.json").read_text())
    for model, title in (("dc", "Linear (DC) clearing"), ("ac", "Nonlinear (AC) clearing")):
        panel = source[model]
        # At 316 CSS px, 13 pt becomes about 12 px. The existing image aspect
        # ratio is retained, so this needs only caption/alt edits in the page.
        fig, ax = plt.subplots(figsize=(4.4, 4.4 * 1042 / 1459))
        fig.subplots_adjust(left=.17, right=.97, bottom=.23, top=.76)
        for vertices in panel["scenarios"]:
            ax.plot(*profit_coordinates(panel, vertices), color=GREY, alpha=.3, lw=.9)
        ax.plot(*profit_coordinates(panel, panel["nominal"]), color=NOMINAL, lw=1.3,
                ls="--", zorder=3)
        ax.plot(*profit_coordinates(panel, panel["mean"]), color=INK, lw=2, zorder=4)
        ax.set(xlim=(0, 1), ylim=(0, 50), xticks=[0, .5, 1], yticks=[0, 25, 50])
        ax.set_xlabel("Offer (% market share)", fontsize=13, labelpad=7)
        ax.set_ylabel("Profit ($1,000)", fontsize=13, labelpad=5)
        ax.tick_params(labelsize=13)
        ax.set_title(title, loc="left", fontsize=14, pad=32)
        handles = [plt.Line2D([], [], color=GREY, lw=1, alpha=.5),
                   plt.Line2D([], [], color=INK, lw=2),
                   plt.Line2D([], [], color=NOMINAL, lw=1.3, ls="--")]
        fig.legend(handles, ["Scenarios", "Mean", "Nominal"], loc="upper center",
                   bbox_to_anchor=(.53, .91), ncol=3, frameon=False, fontsize=12,
                   handlelength=1, handletextpad=.4, columnspacing=.8)
        # Fixed canvas preserves the legacy HTML width/height ratio.
        with plt.rc_context({"savefig.bbox": None}):
            fig.savefig(OUT / f"bidding-{model}-profit.png", dpi=300, facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    fig_nonlinear()
    fig_nonlinear(compact=True)
    fig_profit()
