"""Figures for Uncertainty and Ambiguity (src/research/portfolio-optimization/).

Evidence figures.  The underlying series of the three source plots are not available
(the PJM study and the time-varying study were run by the author with PortfolioOpt.jl
and a Wishart-process forecaster; only the rendered plots survive), so these figures are
the original plot rasters embedded in the author's ICCOPT 2022 deck (S-04,
~/Downloads/"DRO ICCOPT.pptx.pdf"), extracted losslessly with ``pdfimages -j``.  The only
edits remove a plot title or a legend made of file names and redraw axis annotations
outside the original plotting areas for legibility. No data marks are reconstructed.

    pjm-dependence   S-04 slide 6  "Electricity Market Problem: The Pattern"
                     (PJM real-time MCC + MLC at two nodes; Wishart-process covariance
                     estimates).  Unaltered copy of the embedded 1200 x 850 JPEG.
    fixed-radius     S-04 slide 14 "(Real) Results Fixed Ambiguity Set".  Embedded 998 x 610
                     plot cropped to remove its title and file-name legend. The source's
                     already-clipped y-axis title is replaced outside the plotting area.
    time-varying     S-04 slide 23 "Results time varying Ambiguity Set" (the final build of
                     slides 20-23).  Embedded 1844 x 1078 plot cropped to its plotting
                     area: the title ("Culmulative Wealth") and the legend of code names
                     are removed; the caption carries the legend.

Illustration (synthetic points, no empirical content).

    values-laws      A set of values (convex hull of J past return vectors, the data-driven
                     polyhedral set of Fernandes et al. 2016 used in Rosemberg, Reis and
                     Valladao 2018) next to a set of laws (empirical atoms and a law at
                     Wasserstein-1 distance eps that moves the tail atoms, which is how the
                     worst case of CVaR_alpha is attained for a linear loss on R^m).

    moment interval  Exact boundary of 0 <= M <= gamma_2 Sigma_0 in the PSD order,
                     from S-04 slide 19. Illustrative matrices, no fitted data. The two
                     boundary sheets are rank-one matrices and their complements.

    .venv/bin/python tools/figures/portfolio-optimization.py
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "src" / "assets" / "img" / "research"
DECK = Path.home() / "Downloads" / "DRO ICCOPT.pptx.pdf"
PREFIX = "portfolio-optimization-"

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


def slide_image(tmp, page, index=0):
    """Extract the index-th embedded image of a deck page, losslessly (JPEG passthrough)."""
    stem = Path(tmp) / f"p{page}"
    subprocess.run(["pdfimages", "-j", "-f", str(page), "-l", str(page), str(DECK), str(stem)], check=True)
    path = Path(f"{stem}-{index:03d}.jpg")
    if not path.exists():
        raise SystemExit(f"slide {page}: embedded JPEG {index} not found")
    return path


def source_figures():
    with tempfile.TemporaryDirectory() as tmp:
        # Slide 6: the PJM dependence plot, copied byte for byte.
        src = slide_image(tmp, 6)
        assert Image.open(src).size == (1200, 850), "unexpected PJM plot size"
        shutil.copyfile(src, OUT / f"{PREFIX}pjm-dependence.jpg")

        # Slide 14: the embedded source itself clips the first glyph of its y-title.
        # Preserve the plot as a raster; draw readable axes outside it. Tick positions
        # are source-image pixels, not digitized or reconstructed series values.
        src = Image.open(slide_image(tmp, 14))
        assert src.size == (998, 610), "unexpected fixed-set plot size"
        frame_source_plot(src, (78, 32, 616, 558), "fixed-radius",
                          [91, 345, 598], ["2016", "2018", "2020"],
                          [532, 423, 314, 205, 95], ["0", "1M", "2M", "3M", "4M"],
                          "Year", "Cumulative wealth ($)")

        # Slide 23: crop away the misspelled plot title (top 50 px) and the legend of strategy code
        # names (x >= 1215); the caption carries the legend.  The plotting area is untouched.
        src = Image.open(slide_image(tmp, 23))
        assert src.size == (1844, 1078), "unexpected time-varying plot size"
        frame_source_plot(src, (128, 50, 1191, 963), "time-varying",
                          [177, 467, 765, 1063], ["Feb", "May", "Aug", "Nov"],
                          [899, 727, 555, 383, 211], ["0.95", "1.00", "1.05", "1.10", "1.15"],
                          "2010", "Wealth")


def frame_source_plot(src, crop, name, xticks, xlabels, yticks, ylabels, xlabel, ylabel):
    """Place the original plot under legible axis annotations at the same linear scale.

    The axes use source-image pixel coordinates, so the source tick locations align
    exactly with the preserved raster grid. No curve is digitized or recolored.
    """
    left, top, right, bottom = crop
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    ax.imshow(src.crop(crop), extent=(left, right, bottom, top),
              aspect="auto", interpolation="nearest")
    ax.set_xlim(left, right); ax.set_ylim(bottom, top)
    ax.set_xticks(xticks, xlabels); ax.set_yticks(yticks, ylabels)
    ax.tick_params(labelsize=13, length=3)
    ax.set_xlabel(xlabel, fontsize=13); ax.set_ylabel(ylabel, fontsize=13)
    fig.subplots_adjust(left=.23, right=.97, bottom=.16, top=.98)
    fig.savefig(OUT / f"{PREFIX}{name}.jpg", dpi=200, bbox_inches=None,
                facecolor="white", pil_kwargs={"quality": 95, "subsampling": 0})
    plt.close(fig)


def convex_hull(pts):
    """Andrew's monotone chain; returns the closed hull polygon (counter-clockwise)."""
    p = sorted(map(tuple, pts))
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for seq, out in ((p, lower), (reversed(p), upper)):
        for x in seq:
            while len(out) >= 2 and cross(out[-2], out[-1], x) <= 0:
                out.pop()
            out.append(x)
    hull = lower[:-1] + upper[:-1]
    return np.array(hull + hull[:1])


def fig_values_laws(compact=False):
    """Illustration: a set of values versus a set of laws, on the same synthetic sample.

    compact=True stacks the two panels for phone widths (same data and marks)."""
    rng = np.random.default_rng(7)
    J = 12
    cov = np.array([[1.0, 0.55], [0.55, 0.8]])
    pts = rng.multivariate_normal([0.6, 0.4], cov, size=J)
    q = np.array([0.7, 0.45])                      # a fixed allocation; loss = -q^T xi
    loss = -pts @ q
    fig, axes = (plt.subplots(2, 1, figsize=(5.0, 9.4), sharex=True, sharey=True) if compact else
                 plt.subplots(1, 2, figsize=(10.2, 4.3), sharex=True, sharey=True))
    lims = (pts.min(0) - 1.0, pts.max(0) + 1.0)
    label_size = 14 if compact else 11.5
    note_size = 13.5 if compact else 11.5
    title_size = 16 if compact else 13

    # Left: polyhedral set of values; the robust constraint binds at a vertex.
    poly = convex_hull(pts)
    ax = axes[0]
    ax.fill(poly[:, 0], poly[:, 1], color=ACCENT_SOFT, alpha=.75, zorder=1)
    ax.plot(poly[:, 0], poly[:, 1], color=ACCENT, lw=1.6, zorder=2)
    ax.scatter(pts[:, 0], pts[:, 1], s=26, color=INK, zorder=3)
    worst = pts[np.argmax(loss)]
    ax.scatter(*worst, s=90, facecolor="none", edgecolor=AMBER, lw=2, zorder=4)
    xs = np.linspace(lims[0][0], lims[1][0], 50)
    c = q @ worst
    ax.plot(xs, (c - q[0] * xs) / q[1], color=AMBER, lw=1.3, ls=(0, (4, 3)), zorder=2)
    ax.text(worst[0] - .15, worst[1] - .55, "worst vertex", color=AMBER, fontsize=label_size, ha="right")
    ax.text(.03, .97, "Uncertainty set", transform=ax.transAxes, va="top", fontsize=title_size, fontweight="bold")
    ax.text(.03, .88, "Convex hull of past returns;\nthe loss limit holds at every vertex",
            transform=ax.transAxes, va="top", fontsize=note_size, color=MUTED, linespacing=1.35)

    # Right: a law at transport distance eps that moves only the tail atoms.
    ax = axes[1]
    alpha = 2 / J
    tail = np.argsort(loss)[-2:]                    # the alpha-tail of the loss under the empirical law
    d = -q / np.linalg.norm(q)                      # direction that increases the loss fastest (Euclidean)
    shift = 0.55 / alpha * 0.18                     # eps / alpha, drawn to scale of the axes
    ax.scatter(pts[:, 0], pts[:, 1], s=26, color=GREY, zorder=2, label="empirical law (mass 1/J each)")
    for i in tail:
        a, b = pts[i], pts[i] + shift * d
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.6, shrinkA=4, shrinkB=2))
        ax.scatter(*b, s=34, color=TEAL, zorder=3)
        ax.scatter(*a, s=70, facecolor="none", edgecolor=TEAL, lw=1.4, zorder=3)
    ax.text(.03, .97, "Ambiguity set", transform=ax.transAxes, va="top", fontsize=title_size, fontweight="bold")
    ax.text(.03, .88, "Average transport cost ≤ ε;\ntail atoms move by ε/α\nalong the loss direction",
            transform=ax.transAxes, va="top", fontsize=note_size, color=MUTED, linespacing=1.35)

    for ax in axes:
        ax.set_xlim(lims[0][0], lims[1][0]); ax.set_ylim(lims[0][1], lims[1][1] + 1.2)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
        ax.set_xlabel("return of asset 1", color=MUTED, fontsize=label_size)
        ax.set_ylabel("return of asset 2", color=MUTED, fontsize=label_size)
        ax.spines["left"].set_color(LINE)
    fig.tight_layout(w_pad=2.5, h_pad=1.5)
    name = f"{PREFIX}values-laws" + ("-compact" if compact else "")
    fig.savefig(OUT / f"{name}.svg", transparent=True)
    fig.savefig(OUT / f"{name}.png", dpi=200, facecolor="white")
    plt.close(fig)


def moment_boundary():
    """Congruence of the exact boundary of [0, I], not an ellipsoid fit.

    Every lower-boundary matrix is t vv^T, 0 <= t <= 1, ||v||=1.
    Every upper-boundary matrix is I - t vv^T. Congruence by the Cholesky
    factor of B = gamma_2 Sigma_0 preserves the PSD order. At t=1 the
    sheets meet; t=0 gives the two sharp tips. No empirical data are used.
    """
    sigma0 = np.array([[1., .5], [.5, .7]])
    gamma2 = 2.
    bound = gamma2 * sigma0
    chol = np.linalg.cholesky(bound)
    angle = np.linspace(0, np.pi, 181)
    t = np.linspace(0, 1, 61)
    v = np.stack([np.cos(angle), np.sin(angle)], axis=-1)
    rank_one = t[:, None, None, None] * v[None, :, :, None] * v[None, :, None, :]
    lower = chol @ rank_one @ chol.T
    upper = bound - lower
    # Verify both matrix inequalities and the singular boundary equation.
    for sheet in (lower, upper):
        assert np.linalg.eigvalsh(sheet).min() > -1e-12
        assert np.linalg.eigvalsh(bound - sheet).min() > -1e-12
    assert np.abs(np.linalg.det(lower)).max() < 1e-12
    assert np.abs(np.linalg.det(bound - upper)).max() < 1e-12
    return sigma0, bound, lower, upper


def fig_moment_interval():
    sigma0, bound, lower, upper = moment_boundary()
    fig = plt.figure(figsize=(5.4, 5.22))
    ax = fig.add_subplot(projection="3d", computed_zorder=False)
    for sheet in (lower, upper):
        ax.plot_surface(sheet[..., 0, 0], sheet[..., 1, 1], sheet[..., 0, 1],
                        color=ACCENT, alpha=.32, linewidth=0, shade=False,
                        rcount=61, ccount=181, zorder=1)
    # A few exact generating lines make the two cone sheets inspectable.
    for sheet in (lower, upper):
        for k in range(0, 180, 15):
            ax.plot(sheet[:, k, 0, 0], sheet[:, k, 1, 1], sheet[:, k, 0, 1],
                    color=ACCENT, lw=.65, alpha=.45, zorder=2)
    seam = lower[-1]
    ax.plot(seam[:, 0, 0], seam[:, 1, 1], seam[:, 0, 1], color=ACCENT, lw=1.5, zorder=3)
    coords = lambda m: (m[0, 0], m[1, 1], m[0, 1])
    ax.plot([0, bound[0, 0]], [0, bound[1, 1]], [0, bound[0, 1]],
            color=INK, ls=(0, (4, 3)), lw=1.2, zorder=4)
    for m, color in ((np.zeros((2, 2)), INK), (bound, INK), (sigma0, AMBER)):
        ax.scatter(*coords(m), s=45, color=color, depthshade=False, zorder=5)
    ax.text(0, 0, -.13, "0", fontsize=21, ha="center", zorder=6)
    ax.text(bound[0, 0], bound[1, 1], bound[0, 1] + .09,
            r"$\gamma_2\Sigma_0$", fontsize=21, ha="center", zorder=6)
    ax.text(sigma0[0, 0] + .15, sigma0[1, 1] - .1, sigma0[0, 1] - .11,
            r"$\Sigma_0$", color=AMBER, fontsize=21, zorder=6)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.line.set_color(LINE)
    # Symbolic axes: the matrix is an illustration, not estimated study data.
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.set_xlabel(r"$\sigma_{11}$", fontsize=21, labelpad=-5)
    ax.set_ylabel(r"$\sigma_{22}$", fontsize=21, labelpad=-5)
    ax.set_zlabel(r"$\sigma_{12}$", fontsize=21, labelpad=-4)
    ax.set_box_aspect((1, .85, 1.15))
    ax.view_init(elev=17, azim=-64)
    fig.subplots_adjust(left=0, right=1, bottom=.03, top=1)
    fig.savefig(OUT / "portfolio-ambiguity-set.png", dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    source_figures()
    fig_values_laws()
    fig_values_laws(compact=True)
    fig_moment_interval()
