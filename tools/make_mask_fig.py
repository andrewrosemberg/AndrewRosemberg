"""Illustrative schematic for the masked Sobolev page (not paper data).

Left: a one-dimensional solution map y*(p) = clip(phi(p), lo, hi), i.e. the
projection of a smooth unconstrained optimum onto bound constraints. Its
sensitivity is phi'(p) where no bound is active and zero where one is, so each
sample's linearization describes the map only inside its own regime.
Right: the stochastic mask, which selects k of the n*d Jacobian entries at each
update and redraws them at the next.

Style copied from tools/make_figures.py. Run: .venv/bin/python tools/make_mask_fig.py
"""
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

matplotlib.use("Agg")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "src" / "assets" / "img" / "research"

INK, MUTED, LINE = "#202a33", "#687078", "#dddcd5"
ACCENT, ACCENT_SOFT, TEAL, AMBER, GREY = "#7551a7", "#c9b6e4", "#2b7a73", "#b9741f", "#9aa1a8"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none",
    "font.size": 11,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})

LO, HI = -0.35, 0.55


def phi(p):
    return 0.75 * np.sin(0.62 * p + 0.2) + 0.04 * p


def dphi(p):
    return 0.75 * 0.62 * np.cos(0.62 * p + 0.2) + 0.04


def ystar(p):
    return np.clip(phi(p), LO, HI)


def dystar(p):
    v = phi(p)
    return np.where((v > LO) & (v < HI), dphi(p), 0.0)


def draw(axL, axR):

    # ----------------------------------------------------------------- left panel
    ax = axL
    p = np.linspace(0.0, 10.0, 1200)
    y = ystar(p)
    v = phi(p)
    active = (v >= HI) | (v <= LO)
    edges = np.flatnonzero(np.diff(active.astype(int))) + 1
    for s in np.split(np.arange(p.size), edges):
        if active[s[0]]:
            ax.axvspan(p[s[0]], p[s[-1]], color=ACCENT_SOFT, alpha=.32, lw=0, zorder=0)
            up = v[s[len(s) // 2]] >= HI
            ax.text((p[s[0]] + p[s[-1]]) / 2, 0.035, "upper bound\nactive" if up else "lower bound\nactive",
                    ha="center", va="bottom", fontsize=9.6, color=ACCENT, transform=ax.get_xaxis_transform(),
                    linespacing=1.15)
    ax.plot(p, y, color=INK, lw=2.6, zorder=3, solid_capstyle="round")

    samples = np.array([0.45, 2.3, 4.15, 5.25, 7.2, 9.1])
    half = 0.7
    for x0 in samples:
        y0, s0 = float(ystar(x0)), float(dystar(x0))
        xs = np.array([x0 - half, x0 + half])
        ax.plot(xs, y0 + s0 * (xs - x0), color=TEAL, lw=2.0, zorder=4, solid_capstyle="round")
        ax.plot([x0], [y0], "o", color=TEAL, ms=7, zorder=5, mec="white", mew=1.3)

    x0 = 0.45
    y0, s0 = float(ystar(x0)), float(dystar(x0))
    xe = 1.95
    xs = np.linspace(x0 + half, xe, 20)
    ax.plot(xs, y0 + s0 * (xs - x0), color=TEAL, lw=1.5, ls=(0, (3, 2.5)), zorder=4)
    ax.annotate("linearization carried\ninto the next regime",
                xy=(xe, y0 + s0 * (xe - x0)), xytext=(2.35, y0 + s0 * (xe - x0) - 0.04),
                fontsize=9.6, color=MUTED, va="center", linespacing=1.15,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=.8, shrinkA=2, shrinkB=3))

    ax.set_xlim(0, 10)
    ax.set_ylim(LO - 0.38, HI + 0.62)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("problem data  p", color=MUTED)
    ax.set_ylabel("selected solution  y*(p)", color=MUTED)
    ax.set_title("Smooth only within regimes of active constraints", fontsize=12, loc="left", pad=10)
    ax.plot([], [], color=TEAL, lw=2.0, marker="o", ms=6.5, mec="white", label="sample and its sensitivity")
    ax.legend(frameon=False, fontsize=9.6, loc="upper right", handlelength=1.8, borderaxespad=0.2)

    # ---------------------------------------------------------------- right panel
    ax = axR
    ax.set_axis_off()
    n, d, k = 5, 7, 4
    rng = np.random.default_rng(7)
    cell, gap = 1.0, 1.2
    W, H = d * cell, n * cell


    def grid(x0, y0, chosen, color_on):
        for r in range(n):
            for c in range(d):
                on = chosen is None or (r * d + c) in chosen
                ax.add_patch(Rectangle((x0 + c * cell + .07, y0 + (n - 1 - r) * cell + .07), cell - .14, cell - .14,
                                       facecolor=color_on if on else "#ecebe6", edgecolor="none", zorder=2))


    total_w = 3 * W + 2 * gap
    # top row: dense matching
    yt = H + 3.4
    grid(0, yt, None, AMBER)
    ax.text(W + gap, yt + H - 0.2, "Dense matching", fontsize=10.5, color=INK, va="top")
    ax.text(W + gap, yt + H - 1.45, "all nd entries, from samples in\ndifferent regimes, act on every update",
            fontsize=9.8, color=MUTED, va="top", linespacing=1.2)
    # bottom row: masked
    for g in range(3):
        chosen = set(rng.choice(n * d, size=k, replace=False).tolist())
        x0 = g * (W + gap)
        grid(x0, 0, chosen, ACCENT)
        ax.text(x0 + W / 2, H + 0.35, ["update t", "update t+1", "update t+2"][g],
                ha="center", va="bottom", fontsize=10, color=INK)
    ax.text(0, -0.55, "Masked: k of nd entries, redrawn at every update",
            fontsize=10.5, color=INK, va="top")
    ax.text(0, -1.75, "over training every entry is drawn; within one update only a few act",
            fontsize=9.8, color=MUTED, va="top")
    ax.set_xlim(-0.2, total_w + 0.2)
    ax.set_ylim(-2.9, yt + H + 0.3)
    ax.set_aspect("equal")
    ax.set_anchor("N")
    ax.set_title("How many local conditions act at once", fontsize=12, loc="left", pad=10)


fig = plt.figure(figsize=(10.6, 3.9))
gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.08)
draw(fig.add_subplot(gs[0]), fig.add_subplot(gs[1]))
fig.savefig(OUT / "sobolev-mask-regimes.svg", transparent=True)
fig.savefig(OUT / "sobolev-mask-regimes.png", dpi=200, facecolor="white")
plt.close(fig)

fig = plt.figure(figsize=(5.6, 7.6))
gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.95], hspace=0.28)
draw(fig.add_subplot(gs[0]), fig.add_subplot(gs[1]))
fig.savefig(OUT / "sobolev-mask-regimes-tall.svg", transparent=True)
plt.close(fig)
print("ok")
