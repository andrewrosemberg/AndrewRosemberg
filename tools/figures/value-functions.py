"""Figures for src/research/value-functions/ (Continuation-Value Representations).

    .venv/bin/python tools/figures/value-functions.py

Writes src/assets/img/research/value-functions-*.{svg,png}.

Sources (every plotted number is also in .editorial/claims/value-functions.tsv):
  * ac-errors: Rosemberg, Tanneau, Fanzeres, Garcia, Van Hentenryck, "Learning optimal
    power flow value functions with input-convex neural networks", Electric Power Systems
    Research 235 (2024) 110643, Table 2, rows "AC" of the four systems. The DC and SOC
    columns report the gap of the DC-approximation and SOC-relaxation optimal values to the
    row's reference value (their diagonal entries are 0.00 on the DC and SOC rows).
  * rte6k-errors: the paper's own Fig. 5(c) panels (AC-OPF, rte6k), copied unaltered from
    ~/Workspace/PSCC-Learning-Value-Functions (byte-identical to the existing
    src/assets/img/research/icnn-error-{distribution,vs-load}.png) and only placed side by
    side (wide) or stacked (phones). The paper does not tabulate per-instance errors, so the scatter is
    reproduced from the paper rather than replotted.
  * cuts-schematic: an illustrative toy (no data). It shows which function a cut bounds.
"""

import subprocess
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "src" / "assets" / "img" / "research"

INK, INK2, MUTED, LINE = "#202a33", "#3a4550", "#687078", "#dddcd5"
ACCENT, ACCENT_SOFT, TEAL, AMBER, GREY = "#7551a7", "#c9b6e4", "#2b7a73", "#b9741f", "#9aa1a8"
ROSE = "#b85450"
# Match the opaque marker colors in the paper's Fig. 5(c). The histogram
# uses the same colors with transparency. Keep this encoding in every chart.
ICNN_BLUE, DNN_ORANGE = "#009bfa", "#e36f47"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none",
    "font.size": 11,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})


def save(fig, name):
    svg = OUT / f"{name}.svg"
    fig.savefig(svg, transparent=True)
    # Matplotlib's multiline path coordinates include trailing spaces.
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    if not name.endswith("-tall"):  # the tall SVGs serve phones only; no raster copy needed
        fig.savefig(OUT / f"{name}.png", dpi=200, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 1. AC value-prediction error by system (EPSR 2024, Table 2, AC rows)
# --------------------------------------------------------------------------- #
SYSTEMS = [("IEEE-300", "300 buses"), ("PEGASE-1k", "1,354 buses"),
           ("PEGASE-2k", "2,869 buses"), ("RTE-6k", "6,468 buses")]
#            ieee300 pegase1k pegase2k rte6k
MEAN = {"ICNN": [0.39, 0.33, 0.24, 0.25], "DNN": [0.39, 0.68, 0.27, 0.33],
        "SOC": [1.98, 1.32, 0.80, 0.33], "DC": [7.35, 2.91, 3.02, 3.05]}
WORST = {"ICNN": [15.81, 2.37, 8.59, 2.71], "DNN": [14.56, 1.95, 8.89, 3.08],
         "SOC": [16.47, 1.89, 9.13, 0.36], "DC": [21.95, 3.49, 8.88, 3.67]}
SERIES = [  # key, legend label, color, marker, vertical offset inside a system row
    ("ICNN", "Input-convex network (ICNN)", ICNN_BLUE, "o", .30),
    ("DNN", "Unrestricted network (NN)", DNN_ORANGE, "s", .10),
    ("SOC", "SOC relaxation value", TEAL, "D", -.10),
    ("DC", "DC approximation value", MUTED, "^", -.30),
]


def dot_panel(ax, data, title, ticks, xlim, show_labels):
    ys = np.arange(len(SYSTEMS))[::-1].astype(float)
    for key, label, color, marker, off in SERIES:
        vals = data[key]
        ax.scatter(vals, ys + off, s=46, marker=marker, color=color, edgecolor="white", linewidth=1.2,
                   zorder=3, label=label)
        for v, y in zip(vals, ys + off):
            ax.text(v * 1.13, y, f"{v:.2f}", va="center", ha="left", fontsize=11.5, color=INK2, zorder=4)
    for y in ys[:-1] - .5:
        ax.axhline(y, color=LINE, lw=.8, zorder=1)
    ax.set_xscale("log")
    ax.set_xlim(*xlim)
    ax.set_xticks(ticks, [f"{t:g}" for t in ticks])
    ax.minorticks_off()
    ax.set_ylim(-.55, len(SYSTEMS) - .45)
    ax.set_yticks(ys, [f"{n}\n{b}" for n, b in SYSTEMS])
    ax.tick_params(axis="y", length=0, labelsize=11.5, labelcolor=INK, labelleft=show_labels)
    ax.grid(axis="y", visible=False)
    ax.set_title(title, fontsize=13, loc="left", pad=10)
    ax.set_xlabel("AC-OPF value error (%) · log scale", color=MUTED, fontsize=11.5)
    ax.tick_params(axis="x", labelsize=11.5)


def fig_ac_errors(tall=False):
    if tall:
        fig, axes = plt.subplots(2, 1, figsize=(4.2, 12.0))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.8), sharey=True)
    dot_panel(axes[0], MEAN, "Mean absolute error",
              [.2, .5, 1, 2, 5, 10], (.15, 16), True)
    dot_panel(axes[1], WORST, "Worst absolute error", [.5, 1, 2, 5, 10, 20, 40], (.25, 55), tall)
    handles, labels = axes[0].get_legend_handles_labels()
    if tall:
        fig.legend(handles, labels, loc="lower center", ncol=1, frameon=False, fontsize=11.5,
                   bbox_to_anchor=(.5, -.09))
        fig.tight_layout(h_pad=2.2)
    else:
        fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=11.5,
                   bbox_to_anchor=(.5, -.10))
        fig.tight_layout(w_pad=2.2)
    save(fig, "value-functions-ac-errors" + ("-tall" if tall else ""))


# --------------------------------------------------------------------------- #
# 2. Schematic (no data): a cut bounds the function it was taken from
# --------------------------------------------------------------------------- #
def base(x):
    return 1.0 + .8 * x + 1.25 * x ** 2


def data_cost(x):
    # convex trend with one local dip: the operating cost of a nonconvex data model
    return base(x) - .17 * np.exp(-((x - .6) / .045) ** 2)


def fig_cuts(tall=False):
    x = np.linspace(0, 1, 600)
    if tall:
        fig, axes = plt.subplots(2, 1, figsize=(4.2, 9.0), sharey=True)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.5), sharey=True)

    # left: convex fit and its cuts
    ax = axes[0]
    fit = base(x) + .012
    xs = [.22, .6, .88]
    cuts = []
    for xb in xs:
        fb, gb = base(xb) + .012, .8 + 2.5 * xb
        cuts.append(fb + gb * (x - xb))
    env = np.max(cuts, axis=0)
    above = env > data_cost(x)
    ax.fill_between(x, data_cost(x), env, where=above, color="#e8c4c2", lw=0, zorder=1,
                    label="Cut above the data-model cost")
    ax.plot(x, data_cost(x), color=INK, lw=2.2, zorder=3, label="Operating cost of the data model")
    ax.plot(x, fit, color=ICNN_BLUE, lw=2.0, zorder=4, label="Convex fit")
    for i, c in enumerate(cuts):
        ax.plot(x, c, color=ICNN_BLUE, lw=1.1, ls=(0, (4, 3)), alpha=.85, zorder=2,
                label="Cuts of the convex fit" if i == 0 else None)
    ax.plot(xs, [base(v) + .012 for v in xs], "o", color=ICNN_BLUE, ms=6.5, zorder=5)
    ax.set_title("Convex fit", fontsize=13, loc="left", pad=10)

    # right: unrestricted fit and one tangent
    ax = axes[1]
    xs2 = np.linspace(.05, .95, 8)
    wig = data_cost(x) + .07 * np.sin(2 * np.pi * (x - .05) / (.9 / 3.5))
    g = lambda t: np.interp(t, x, wig)
    xb = .555
    slope = (g(xb + 1e-3) - g(xb - 1e-3)) / 2e-3
    tan = g(xb) + slope * (x - xb)
    ax.fill_between(x, wig, tan, where=tan > wig, color="#e8c4c2", lw=0, zorder=1,
                    label="Tangent above the fit")
    ax.plot(x, data_cost(x), color=INK, lw=2.2, zorder=3, label="Operating cost of the data model")
    ax.plot(x, wig, color=DNN_ORANGE, lw=2.0, zorder=4, label="Unrestricted fit")
    ax.plot(x, tan, color=DNN_ORANGE, lw=1.1, ls=(0, (4, 3)), zorder=2, label="Tangent of the fit")
    ax.plot([xb], [g(xb)], "o", color=DNN_ORANGE, ms=6.5, zorder=5)
    ax.set_title("Unrestricted fit", fontsize=13, loc="left", pad=10)

    for ax in axes:
        ax.set_xlim(0, 1); ax.set_ylim(.55, 3.2)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlabel("Demand", color=MUTED, fontsize=11.5)
        ax.grid(False)
        handles, labels = ax.get_legend_handles_labels()
        labels = [label.replace("Operating cost of the data model", "Data-model operating cost")
                       .replace("Cut above the data-model cost", "Cut above data-model cost")
                  for label in labels]
        ax.legend(handles, labels, frameon=False, fontsize=11.5, loc="upper left")
    axes[0].set_ylabel("Operating cost", color=MUTED, fontsize=11.5)
    if tall:
        axes[1].set_ylabel("Operating cost", color=MUTED, fontsize=11.5)
    fig.tight_layout(w_pad=2.5, h_pad=2.0)
    save(fig, "value-functions-cuts-schematic" + ("-tall" if tall else ""))


# --------------------------------------------------------------------------- #
# 3. Paper Fig. 5(c): AC-OPF errors on rte6k, unaltered panels side by side
# --------------------------------------------------------------------------- #
def fig_rte6k():
    left = OUT / "icnn-error-distribution.png"
    right = OUT / "icnn-error-vs-load.png"
    subprocess.run(["magick", str(left), str(right), "+append", "-strip",
                    str(OUT / "value-functions-rte6k-errors.png")], check=True)
    subprocess.run(["magick", str(left), str(right), "-append", "-strip",
                    str(OUT / "value-functions-rte6k-errors-tall.png")], check=True)


if __name__ == "__main__":
    fig_ac_errors(); fig_ac_errors(tall=True)
    fig_cuts(); fig_cuts(tall=True)
    fig_rte6k()
    print("wrote", sorted(p.name for p in OUT.glob("value-functions-*")))
