"""Evidence chart for Planning and Realization Mismatch (src/research/network-simplifications/).

Every number is copied from Rosemberg et al., "Assessing the Cost of Network Simplifications in
Long-Term Hydrothermal Dispatch Planning Models", IEEE Trans. Sustain. Energy 13(1):196-206, 2022:
Table I (3-bus loop) and Table II (28-bus Bolivian system). Columns: planning cost (10^6 $),
implementation cost under AC power flow (10^6 $), GAP (%), time (min). The SDP planning model has no
row in Table II: the run was stopped after four weeks without converging (Section IV-B).
The values are also recorded in .editorial/claims/network-simplifications.tsv.

    .venv/bin/python tools/figures/network-simplifications.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = Path(__file__).resolve().parents[2] / "src" / "assets" / "img" / "research"

# Site palette and type (same as tools/make_figures.py).
INK, MUTED, LINE = "#202a33", "#687078", "#dddcd5"
ACCENT, TEAL = "#7551a7", "#2b7a73"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none",
    "font.size": 12.5,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})

# (planning model, kind, planning cost, implementation cost, GAP % and time in min as printed in the table);
# None = no row in the table.
TABLE_I = [  # 3-bus loop, fully meshed
    ("NFA", "relax", 43.2317, 54.7234, "26.4", "5.40"),
    ("SOC", "relax", 45.0477, 54.9197, "21.7", "23.92"),
    ("SDP", "relax", 45.4524, 48.2853, "6.1", "47.47"),
    ("DC", "approx", 43.3940, 48.8891, "12.5", "5.41"),
    ("DCLL", "approx", 45.4158, 48.0700, "5.68", "16.09"),
]
TABLE_II = [  # 28-bus Bolivian system, mostly radial (3 cycles)
    ("NFA", "relax", 0.58687, 0.68735, "17.067", "4.67"),
    ("SOC", "relax", 0.60818, 0.60935, "0.193", "119.23"),
    ("SDP", "relax", None, None, None, None),
    ("DC", "approx", 0.58714, 0.64523, "9.855", "5.22"),
    ("DCLL", "approx", 0.61310, 0.60941, "−0.602", "54.33"),
]
COLOR = {"relax": ACCENT, "approx": TEAL}


YS = [4.6, 3.6, 2.6, 1.0, 0.0]  # relaxations on top, approximations below, a gap between the groups
YLIM = (-.7, 5.5)


def panel(ax, side, rows, title, xlim, ticks):
    for (name, kind, plan, imp, gap, minutes), y in zip(rows, YS):
        c = COLOR[kind]
        if plan is None:
            ax.text(xlim[0] + (xlim[1] - xlim[0]) * .02, y, "Not converged",
                    va="center", fontsize=12.5, color=MUTED, style="italic")
            continue
        ax.plot([plan, imp], [y, y], color=c, lw=2, alpha=.55, zorder=2, solid_capstyle="round")
        ax.plot([plan], [y], "o", ms=10, mfc="white", mec=c, mew=2, zorder=3)
        ax.plot([imp], [y], "o", ms=7, color=c, mec="white", mew=1.2, zorder=4)
        sign = "" if gap.startswith("\u2212") else "+"
        side.text(.48, y, f"{sign}{gap}", va="center", ha="right", fontsize=12.5, color=INK)
        side.text(1.0, y, minutes, va="center", ha="right", fontsize=12.5, color=INK)
    ax.set_yticks(YS, [r[0] for r in rows])
    ax.tick_params(axis="y", length=0, labelsize=12.5, labelcolor=INK)
    ax.set_ylim(*YLIM)
    ax.set_xlim(*xlim)
    ax.set_xticks(ticks)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Expected cost (10⁶ $)", color=MUTED, fontsize=12.5)
    ax.set_title(title, fontsize=14, loc="left", pad=44)
    ax.text(xlim[0], 5.25, "Relaxations", fontsize=12.5, color=ACCENT, fontweight="bold")
    ax.text(xlim[0], 1.55, "Approximations", fontsize=12.5, color=TEAL, fontweight="bold")
    side.set_xlim(0, 1); side.set_ylim(*YLIM); side.axis("off")
    # Preserve the published GAP column, including its varying precision.
    # It is not recomputed from the rounded expected costs.
    side.text(.48, 5.65, "Gap (%)\nas reported", ha="right", va="center", fontsize=12.5, color=MUTED)
    side.text(1.0, 5.65, "SDDP\ntime (min)", ha="right", va="center", fontsize=12.5, color=MUTED)


def legend(fig, y, tall):
    h = [plt.Line2D([], [], ls="none", marker="o", ms=8, mfc="white", mec=INK, mew=1.8),
         plt.Line2D([], [], ls="none", marker="o", ms=8, color=INK)]
    fig.legend(h, ["Planned (planning model)", "Implemented (AC operation)"], loc="upper center",
               bbox_to_anchor=(.5, y), ncol=1 if tall else 2, frameon=False, fontsize=12.5,
               handletextpad=.4, columnspacing=1.6)


def make(tall=False):
    if tall:
        # At the phone's ~316 px image width, 12.5 pt labels remain >= 11 px.
        fig = plt.figure(figsize=(4.5, 9.3))
        gs = fig.add_gridspec(2, 2, width_ratios=[2.05, 1.8], wspace=.08, hspace=.85,
                              left=.16, right=.98, top=.79, bottom=.07)
        cells = [(gs[0, 0], gs[0, 1]), (gs[1, 0], gs[1, 1])]
        top = .985
    else:
        fig = plt.figure(figsize=(10.6, 4.7))
        gs = fig.add_gridspec(1, 5, width_ratios=[3.0, 1.8, .7, 3.0, 1.8], wspace=.06,
                              left=.07, right=.99, top=.70, bottom=.15)
        cells = [(gs[0, 0], gs[0, 1]), (gs[0, 3], gs[0, 4])]
        top = 1.0
    specs = [(TABLE_I, "3-bus loop (meshed)", (42, 56), [42, 46, 50, 54]),
             (TABLE_II, "28-bus system (mostly radial)", (.58, .70), [.58, .62, .66, .70])]
    for (a, b), (rows, title, xlim, ticks) in zip(cells, specs):
        ax = fig.add_subplot(a); side = fig.add_subplot(b, sharey=ax)
        panel(ax, side, rows, title, xlim, ticks)
    legend(fig, top, tall)
    name = "network-simplifications-policies" + ("-tall" if tall else "")
    path = OUT / f"{name}.svg"
    fig.savefig(path, transparent=True)
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)
    return name


if __name__ == "__main__":
    for t in (False, True):
        print("wrote", make(t))
