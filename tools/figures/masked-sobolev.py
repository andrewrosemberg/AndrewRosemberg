"""Evidence charts and light assets for Learning Solution Maps (research/masked-sobolev).

Experimental chart values come from the camera-ready masked-Sobolev paper
(~/Workspace/Sobolev-NEURIPS-Andrew-2026/main.pdf, NeurIPS 2026) and are recorded in
.editorial/claims/masked-sobolev.tsv. Geometry illustrations use the solved JSON
grids from the paper website; the regime schematic has no empirical data.
No evidence value is estimated or smoothed.

    .venv/bin/python tools/figures/masked-sobolev.py            # charts only
    .venv/bin/python tools/figures/masked-sobolev.py --assets   # also redraw the animated geometry toys

The --assets step renders the unchanged solved JSON grids in the read-only paper-site
repo. It never invokes an optimizer or changes the data. The dexterous image is retained.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "masked-sobolev-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "src" / "assets" / "img" / "research"
PAPER_SITE = Path.home() / "Workspace" / "NeurIPS2026-Masked-Sobolev-Optimization-Proxies" / "docs" / "assets"

# Match the retained paper learning curves throughout this page.
INK, MUTED, LINE = "#202a33", "#687078", "#dddcd5"
SOB, VAL = "#c0501f", "#2a6fb5"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none",
    "font.size": 13,
    "svg.hashsalt": "masked-sobolev",
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})


def write_svg(fig, path):
    fig.savefig(path, facecolor="white", metadata={"Date": None})
    # Matplotlib leaves trailing spaces in path commands; normalize the source.
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


def save(fig, name):
    write_svg(fig, OUT / f"masked-sobolev-{name}.svg")
    if "--previews" in sys.argv:
        preview = Path(tempfile.gettempdir()) / "masked-sobolev-previews"
        preview.mkdir(exist_ok=True)
        fig.savefig(preview / f"{name}.png", dpi=130, facecolor="white")
    plt.close(fig)


def title(ax, text, pad=12):
    ax.set_title(text, fontsize=14, loc="left", pad=pad, color=INK, fontweight="bold")


def paired_hbar(ax, values, fmt, xmax, labels=("Masked Sobolev", "Value-only")):
    """Two horizontal bars (Sobolev on top), directly labeled."""
    y = np.array([1.0, 0.0])
    ax.barh(y, values, color=[SOB, VAL], height=.6, zorder=2)
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", length=0, labelsize=13, labelcolor=INK)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, xmax)
    for yi, v in zip(y, values):
        ax.text(v + xmax * .015, yi, fmt(v), va="center", fontsize=13, color=INK)


# --------------------------------------------------------------------------- #
# 1. Smooth map: control-policy distillation (paper Sec. 5.1, App. I, Table 10)
# --------------------------------------------------------------------------- #
def fig_smooth():
    fig, axes = plt.subplots(2, 1, figsize=(4.2, 4.2), gridspec_kw={"hspace": 1.35})
    ax = axes[0]
    paired_hbar(ax, [1349, 3446], lambda v: f"{v:,.0f}", 4300)
    title(ax, "First run to reach\n95% of teacher performance")
    ax.set_xlabel("Training iteration", color=MUTED)
    ax.set_xticks([0, 2000, 4000])
    ax = axes[1]
    paired_hbar(ax, [95.4, 4.2], lambda v: f"{v:.1f}%", 118)
    title(ax, "Sweep runs reaching\n95% of teacher performance")
    ax.set_xlabel("Share of sweep traces (%)", color=MUTED)
    ax.set_xticks([0, 50, 100])
    save(fig, "smooth")


# --------------------------------------------------------------------------- #
# 2. Many active-set regimes: AC-OPF (paper Table 1 and Table 2)
# --------------------------------------------------------------------------- #
def fig_acopf():
    fig, axes = plt.subplots(2, 1, figsize=(4.8, 5.0), gridspec_kw={"hspace": .62, "height_ratios": [1, 1.05]})
    # (a) mean absolute infeasibility, Table 1
    ax = axes[0]
    nets = ["IEEE-300", "PEGASE-1k", "RTE-6k"]
    sob = [0.0099, 0.0066, 0.0042]
    val = [0.0116, 0.0098, 0.0059]
    x = np.arange(len(nets))
    w = .36
    ax.bar(x - w / 2 - .01, sob, w, color=SOB, zorder=2, label="Masked Sobolev")
    ax.bar(x + w / 2 + .01, val, w, color=VAL, zorder=2, label="Value-only")
    for xi, s, v in zip(x, sob, val):
        ax.text(xi - w / 2 - .01, s + .0003, f"{s:.4f}", ha="center", va="bottom", fontsize=13, color=INK)
        ax.text(xi + w / 2 + .01, v + .0003, f"{v:.4f}", ha="center", va="bottom", fontsize=13, color=INK)
    ax.set_xticks(x, nets)
    ax.tick_params(axis="x", length=0, labelsize=13, labelcolor=INK)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, .018)
    ax.set_yticks([0, .005, .010])
    ax.set_ylabel("Mean absolute infeasibility", color=MUTED, fontsize=13)
    ax.legend(frameon=False, fontsize=13, loc="upper center", ncol=2, bbox_to_anchor=(.5, 1.18), columnspacing=.7, handlelength=1)
    title(ax, "Average infeasibility")
    # (b) IEEE-300 mask-density ablation, Table 2; value-only reference from Table 1
    ax = axes[1]
    dens = ["5%", "10%", "25%", "100%\n(dense)"]
    inf = [0.0099, 0.0094, 0.0141, 0.0517]
    xb = np.arange(len(dens))
    ax.bar(xb, inf, .56, color=SOB, zorder=2)
    for xi, v in zip(xb, inf):
        ax.text(xi, v + .0012, f"{v:.4f}", ha="center", va="bottom", fontsize=13, color=INK, zorder=5,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.2))
    ax.axhline(.0116, color=VAL, lw=1.6, ls=(0, (4, 3)), zorder=3, label="Value-only proxy, 0.0116")
    ax.legend(frameon=False, fontsize=13, loc="upper left")
    ax.set_xticks(xb, dens)
    ax.tick_params(axis="x", length=0, labelsize=13, labelcolor=INK)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, .06)
    ax.set_yticks([0, .02, .04, .06])
    ax.set_xlabel("Jacobian entries retained (IEEE-300)", color=MUTED, fontsize=13)
    ax.set_ylabel("Mean absolute infeasibility", color=MUTED, fontsize=13)
    title(ax, "Infeasibility against mask density")
    save(fig, "acopf")


# --------------------------------------------------------------------------- #
# 3. Sparse solutions: mean-variance portfolio (paper Table 3, test set)
#    Means only; the reported standard deviations are printed, because
#    symmetric error bars would extend below a gap of zero.
# --------------------------------------------------------------------------- #
def fig_portfolio():
    fig, ax = plt.subplots(figsize=(4.8, 3.8))
    groups = ["Looser risk limit\nσmax > 10% of budget", "Tight risk limit\nσmax ≤ 10% of budget"]
    sob = [(8.7, 9.5), (29.5, 26.9)]
    val = [(18.9, 20.2), (14.7, 21.2)]
    x = np.arange(2)
    w = .34
    ax.bar(x - w / 2 - .01, [m for m, _ in sob], w, color=SOB, zorder=2, label="Masked Sobolev")
    ax.bar(x + w / 2 + .01, [m for m, _ in val], w, color=VAL, zorder=2, label="Value-only")
    for xi, (m, s) in zip(x, sob):
        ax.text(xi - w / 2 - .01, m + .8, f"{m:.1f}\n± {s:.1f}", ha="center", va="bottom", fontsize=13, color=INK,
                linespacing=1.15)
    for xi, (m, s) in zip(x, val):
        ax.text(xi + w / 2 + .01, m + .8, f"{m:.1f}\n± {s:.1f}", ha="center", va="bottom", fontsize=13, color=INK,
                linespacing=1.15)
    ax.set_xticks(x, groups)
    ax.tick_params(axis="x", length=0, labelsize=13, labelcolor=INK)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, 40)
    ax.set_yticks([0, 10, 20, 30, 40])
    ax.set_ylabel("Test optimality gap, mean (%)", color=MUTED, fontsize=13)
    ax.legend(frameon=False, fontsize=13, loc="upper left", ncol=2, bbox_to_anchor=(0, 1.14), handlelength=1, columnspacing=1)
    title(ax, "Optimality gap by risk regime", pad=42)
    save(fig, "portfolio")


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


def draw_mask_regimes(axL, axR):

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
                    ha="center", va="bottom", fontsize=15, color=ACCENT, transform=ax.get_xaxis_transform(),
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
    ax.annotate("Sensitivity extended\npast its regime",
                xy=(xe, y0 + s0 * (xe - x0)), xytext=(4.5, 1.0),
                fontsize=15, color=MUTED, va="center", linespacing=1.15,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=.8, shrinkA=2, shrinkB=3))

    ax.set_xlim(0, 10)
    ax.set_ylim(LO - 0.38, HI + 0.62)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("Problem data p", color=MUTED, fontsize=16)
    ax.set_ylabel("Selected solution y*(p)", color=MUTED, fontsize=16)
    ax.set_title("Local sensitivities", fontsize=16, loc="left", pad=10)
    ax.plot([], [], color=TEAL, lw=2.0, marker="o", ms=6.5, mec="white", label="sample and its sensitivity")

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
    grid(0, yt, None, "#8b949b")
    ax.text(W + gap, yt + H - 0.2, "Dense matching", fontsize=15, color=INK, va="top")
    ax.text(W + gap, yt + H - 1.45, "all n·d entries\n(n outputs × d parameters)",
            fontsize=15, color=MUTED, va="top", linespacing=1.2)
    # bottom row: masked
    for g in range(3):
        chosen = set(rng.choice(n * d, size=k, replace=False).tolist())
        x0 = g * (W + gap)
        grid(x0, 0, chosen, SOB)
        ax.text(x0 + W / 2, H + 0.35, ["update t", "update t+1", "update t+2"][g],
                ha="center", va="bottom", fontsize=15, color=INK)
    ax.text(0, -0.55, "Masked: K of n·d entries per update",
            fontsize=15, color=INK, va="top")
    ax.text(0, -1.75, "A fresh mask at each update",
            fontsize=15, color=MUTED, va="top")
    ax.set_xlim(-0.2, total_w + 0.2)
    ax.set_ylim(-2.9, yt + H + 0.3)
    ax.set_aspect("equal")
    ax.set_anchor("N")
    ax.set_title("Jacobian masks", fontsize=16, loc="left", pad=10)


def fig_mask_regimes():
    global ACCENT, ACCENT_SOFT, TEAL
    ACCENT, ACCENT_SOFT, TEAL = "#7551a7", "#c9b6e4", "#2b7a73"
    for tall in (False, True):
        fig = plt.figure(figsize=(5.6, 9.0) if tall else (11.8, 4.8))
        gs = fig.add_gridspec(2, 1, height_ratios=[1, .95], hspace=.38) if tall else fig.add_gridspec(1, 2, width_ratios=[1.25, 1], wspace=.18)
        with plt.rc_context({"axes.grid": False}):
            draw_mask_regimes(fig.add_subplot(gs[0]), fig.add_subplot(gs[1]))
        name = "sobolev-mask-regimes" + ("-tall" if tall else "")
        write_svg(fig, OUT / f"{name}.svg")
        if "--previews" in sys.argv:
            preview = Path(tempfile.gettempdir()) / "masked-sobolev-previews"
            preview.mkdir(exist_ok=True)
            fig.savefig(preview / f"{name}.png", dpi=100, facecolor="white")
        plt.close(fig)


# --------------------------------------------------------------------------- #
# Solved illustrative grids (not experimental data). Do not rerun the solvers.
# All surface vertices and moving samples are read unchanged from the paper site.
# The control surface fixes initial velocities to zero; its moving dot therefore
# visits stored grid vertices, rather than the nonzero-velocity swing-up rollout.
# --------------------------------------------------------------------------- #
def assets():
    cmap = LinearSegmentedColormap.from_list(
        "paper", ["#4f386f", "#9774bc", "#eee7f2", "#e8c9aa", "#b96d39"])
    cases = [
        ("acrobot", "control", "Bounded-torque swing-up",
         "First torque, u₀* (N·m)", "Initial angle\nq₁ − π (rad)", "Initial angle\nq₂ (rad)"),
        ("dispatch", "dispatch", "A line limit creates a plateau",
         "Cheaper generation, P₀* (p.u.)", "Active demand\nP (p.u.)", "Reactive demand\nQ (p.u.)"),
        ("portfolio", "portfolio", "Sparse allocation creates a flat region",
         "Allocation to asset A, x*_A", "Expected return\nAsset A", "Expected return\nAsset B"),
    ]
    for name, source, heading, zlabel, xlabel, ylabel in cases:
        data = json.loads((PAPER_SITE / f"{source}-toy.json").read_text())
        x, y, z = np.array(data["x"]), np.array(data["y"]), np.array(data["z"])
        X, Y = np.meshgrid(x, y)
        fig = plt.figure(figsize=(4, 4.4125), dpi=160, facecolor="white")
        # Keep every piece of type legible in the existing two-column layout.
        # External horizontal axis labels avoid the cramped 3D label rotations.
        fig.text(.04, .96, heading, fontsize=12.3, weight="bold", va="top")
        fig.text(.04, .85, zlabel, fontsize=12, color=INK)
        fig.text(.73, .065, xlabel, fontsize=12, color=INK, ha="center", va="center")
        fig.text(.23, .065, ylabel, fontsize=12, color=INK, ha="center", va="center")
        ax = fig.add_axes([-.045, .11, 1.06, .72], projection="3d", computed_zorder=False)
        ax.plot_surface(X, Y, z, cmap=cmap, linewidth=.2,
                        edgecolor=(1, 1, 1, .18), rstride=1, cstride=1, shade=True)
        ax.view_init(elev=27, azim=-125)
        ax.set_box_aspect((1.15, 1, .72))
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.set_major_locator(MaxNLocator(3))
            axis.pane.fill = False
            axis.pane.set_edgecolor(LINE)
            axis._axinfo["grid"]["color"] = "#e5e4df"
            axis.line.set_color("#b2b0ad")
        ax.tick_params(colors=MUTED, labelsize=11, pad=0)
        dot, = ax.plot([], [], [], "o", color=INK, mec="white", mew=1.4, ms=7, zorder=10)
        inset = None
        if source == "dispatch":
            # Original shared-proxy gradient inset, now one third of the width:
            # L_k = ||theta - Dg_k||², theta=(.5,0), grad L_k=2(theta-Dg_k).
            # Its two arrows are different output rows at the SAME sample.
            inset = fig.add_axes([.65, .64, .33, .20], facecolor="white", zorder=20)
            inset.set(xlim=(-2.3, 2.3), ylim=(-2.3, 2.3), aspect="equal")
            inset.set_axis_off()
        if source == "control":
            # A closed tour of actual grid vertices; no interpolation or new solve.
            n = len(x) - 1
            samples = [(i, 0) for i in range(n)] + [(n, j) for j in range(n)]
            samples += [(i, n) for i in range(n, 0, -1)] + [(0, j) for j in range(n, 0, -1)]
        else:
            samples = data["path"]
        indices = np.linspace(0, len(samples) - 1, 48, dtype=int)
        frames = []
        for index in indices:
            sample = samples[index]
            if source == "control":
                i, j = sample
                px, py, pz = x[i], y[j], z[j, i]
            elif source == "dispatch":
                px, py, pz = sample["pd"], sample["qd"], sample["p0"]
                inset.clear()
                inset.set(xlim=(-2.3, 2.3), ylim=(-2.3, 2.3), aspect="equal")
                inset.set_axis_off()
                inset.axhline(0, color=LINE, lw=1)
                inset.axvline(0, color=LINE, lw=1)
                for row, color in zip(sample["jacobian"], ("#2b7a73", "#687078")):
                    gx, gy = 2 * (np.array([.5, 0]) - np.array(row))
                    inset.annotate("", xy=(gx, gy), xytext=(0, 0),
                                   arrowprops=dict(arrowstyle="-|>", color=color, lw=2.5))
            else:
                px, py, pz = sample["mu"][0], sample["mu"][1], sample["allocation"][0]
            dot.set_data_3d([px], [py], [pz])
            fig.canvas.draw()
            frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert("RGB"))
        frames[0].save(OUT / f"masked-sobolev-geometry-{name}-still.webp", quality=85)
        frames[0].save(OUT / f"masked-sobolev-geometry-{name}.webp", save_all=True,
                       append_images=frames[1:], duration=200, loop=0, quality=80, method=4)
        plt.close(fig)
        print(f"{name}: {len(frames)} frames from unchanged solved samples")


if __name__ == "__main__":
    fig_smooth()
    fig_acopf()
    fig_portfolio()
    fig_mask_regimes()
    if "--assets" in sys.argv:
        assets()
