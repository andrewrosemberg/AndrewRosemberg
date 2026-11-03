"""Evidence charts for research/differentiable-optimization/.

    .venv/bin/python tools/figures/differentiable-optimization.py

Both charts are recomputed from the models stated in the DiffOpt paper
(Rosemberg et al., arXiv:2510.25986v1, Section 5); no point is read off the
published raster figures.

1. Economic dispatch (Section 5.1, Figure 1). Data exactly as printed in the
   paper: c = (20, 30), c2 = (0.2, 0.1), G = (150, 80), c_varsigma = 1000, demand d
   swept over (0, 300] MWh. The QP is separable with one coupling constraint, so
   the selected solution is obtained in closed form from the equal-marginal-cost
   condition; with balance written d - g1 - g2 - varsigma = 0, the multiplier
   lambda(d) is the value derivative dq/dd, and the solution derivatives dg_i*/dd are the slopes of the
   piecewise-affine solution map on each active set. At the three demands where
   the active set changes, the derivative does not exist and the curves are
   broken. The exact breakpoints are d = 25, 145 and 230 MWh; the paper's text
   quotes 27 and 148. The documented sweep (DiffOpt.jl
   docs/src/examples/Thermal_Generation_Dispatch_sweep.jl) uses 11:4:300:
   27 is the first sample after 25, 147 is the first after 145, and 148 is not
   on that grid. The paper's Figure 1 uses a 10,000 $/MWh penalty, as in that
   sweep; this chart uses the 1000 $/MWh penalty of the paper's code listing.

2. Two-link inverse kinematics (Section 5.3, Figure 4 left). Model as printed:
   l1 = l2 = 1, min alpha1^2 + alpha2^2 s.t. f(alpha) = (r1, r2). With two
   equality constraints in two unknowns the KKT matrix is nonsingular exactly when
   the kinematic Jacobian J(alpha) is, and then d alpha*/d r = J^{-1},
   independent of the objective. Its spectral norm 1/sigma_min(J) depends only on
   alpha2, i.e. on the target radius r. The paper's heat map plots the same
   quantity multiplied by the forward seed 0.01 used in the documented example
   (docs/src/examples/Planar_Arm_Example.jl); here it is plotted in its own units.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm

matplotlib.use("Agg")
OUT = Path(__file__).resolve().parents[2] / "src" / "assets" / "img" / "research"
SLUG = "differentiable-optimization"

# Site palette and type, identical to tools/make_figures.py.
INK, MUTED, LINE = "#202a33", "#687078", "#dddcd5"
ACCENT, ACCENT_SOFT, TEAL, AMBER, GREY = "#7551a7", "#c9b6e4", "#2b7a73", "#b9741f", "#9aa1a8"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "path",            # math labels must not depend on reader fonts
    # At 826 px (desktop) and 316 px (phone), labels stay about 12–14 px.
    "font.size": 14,
    "mathtext.fontset": "cm",
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})


def save(fig, name):
    fig.savefig(OUT / f"{SLUG}-{name}.svg", transparent=True)
    fig.savefig(OUT / f"{SLUG}-{name}.png", dpi=200, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 1. Economic dispatch: value derivative versus solution derivatives
# --------------------------------------------------------------------------- #
C, C2, G, CPHI = np.array([20.0, 30.0]), np.array([0.2, 0.1]), np.array([150.0, 80.0]), 1000.0


def dispatch(d):
    """Selected primal-dual solution (g, phi, lambda) for demand d > 0."""
    lo, hi = 0.0, CPHI
    for _ in range(200):                      # bisection on the balance multiplier
        lam = (lo + hi) / 2
        g = np.clip((lam - C) / (2 * C2), 0, G)
        lo, hi = (lam, hi) if g.sum() < d else (lo, lam)
    lam = (lo + hi) / 2
    g = np.clip((lam - C) / (2 * C2), 0, G)
    phi = max(d - g.sum(), 0.0)
    return g, phi, (CPHI if phi > 1e-9 else lam)


def breakpoints():
    """Demands at which the active set changes, from the marginal-cost conditions."""
    d1 = (C[1] - C[0]) / (2 * C2[0])                       # plant 2 becomes marginal
    lam2 = C[1] + 2 * C2[1] * G[1]                         # plant 2 reaches capacity
    d2 = (lam2 - C[0]) / (2 * C2[0]) + G[1]
    d3 = G.sum()                                           # both plants at capacity
    return d1, d2, d3


def solution_derivatives(d, bps):
    """d g_i*/dd and d phi*/dd on each active set (undefined at breakpoints)."""
    d1, d2, d3 = bps
    s1, s2 = 1 / (2 * C2[0]), 1 / (2 * C2[1])              # d g_i / d lambda when marginal
    if d < d1:
        return 1.0, 0.0, 0.0
    if d < d2:
        return s1 / (s1 + s2), s2 / (s1 + s2), 0.0
    if d < d3:
        return 1.0, 0.0, 0.0
    return 0.0, 0.0, 1.0


def broken(x, y, bps, eps=0.6):
    y = np.array(y, dtype=float)
    for b in bps:
        y[np.abs(x - b) < eps] = np.nan
    return y


def fig_dispatch(tall=False):
    bps = breakpoints()
    d = np.linspace(0.25, 300, 1200)
    sol = [dispatch(x) for x in d]
    g = np.array([s[0] for s in sol]); phi = np.array([s[1] for s in sol]); lam = np.array([s[2] for s in sol])
    der = np.array([solution_derivatives(x, bps) for x in d])

    fig, axes = plt.subplots(3, 1, figsize=(4.4, 10.6)) if tall else plt.subplots(1, 3, figsize=(12.0, 4.1))

    ax = axes[0]
    ax.stackplot(d, g[:, 0], g[:, 1], phi, colors=[ACCENT, TEAL, AMBER],
                 labels=[r"$g_1^{\ast}$ (plant 1)", r"$g_2^{\ast}$ (plant 2)", r"$\varsigma^{\ast}$ (unmet)"], zorder=2)
    ax.set_title("Selected solution", loc="left", fontsize=15)
    ax.set_xlabel(r"Demand $d$ (MWh)", color=MUTED); ax.set_ylabel("MWh", color=MUTED)
    ax.set_xlim(0, 300); ax.set_ylim(0, 300)
    ax.legend(frameon=False, fontsize=14, loc="upper left")

    ax = axes[1]
    ax.plot(d, broken(d, lam, bps[2:]), color=INK, lw=2, zorder=3)
    ax.set_yscale("log"); ax.set_ylim(15, 1600)
    ax.set_yticks([20, 50, 100, 200, 500, 1000], ["20", "50", "100", "200", "500", "1000"])
    ax.minorticks_off()
    ax.set_title("Value derivative", loc="left", fontsize=15)
    ax.set_xlabel(r"Demand $d$ (MWh)", color=MUTED); ax.set_ylabel("$/MWh (log scale)", color=MUTED)
    ax.set_xlim(0, 300)

    ax = axes[2]
    ax.plot(d, broken(d, der[:, 0], bps), color=ACCENT, lw=2.2, label=r"$g_1^{\ast}$", zorder=4)
    ax.plot(d, broken(d, der[:, 1], bps), color=TEAL, lw=2.2, label=r"$g_2^{\ast}$", zorder=3)
    ax.plot(d, broken(d, der[:, 2], bps), color=AMBER, lw=1.8, ls=(0, (4, 2)),
            label=r"$\varsigma^{\ast}$", zorder=2)
    ax.set_title("Solution derivatives", loc="left", fontsize=15)
    ax.set_xlabel(r"Demand $d$ (MWh)", color=MUTED)
    ax.set_ylabel(r"$\partial(\cdot)/\partial d$", color=MUTED)
    ax.set_xlim(0, 300); ax.set_ylim(-.05, 1.3)
    ax.set_yticks([0, 1 / 3, 2 / 3, 1], ["0", "1/3", "2/3", "1"])
    ax.legend(frameon=False, fontsize=14, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.02),
              handlelength=1.2, columnspacing=.7)

    for a in axes:
        for b in bps:
            a.axvline(b, color=GREY, lw=.9, ls=(0, (3, 3)), zorder=1)
    fig.tight_layout(w_pad=2.4, h_pad=1.8)
    save(fig, "dispatch-tall" if tall else "dispatch")
    return bps


# --------------------------------------------------------------------------- #
# 2. Inverse kinematics: conditioning of the selected solution response
# --------------------------------------------------------------------------- #
L1 = L2 = 1.0
CMAP = LinearSegmentedColormap.from_list("site_seq", ["#f4f0fa", ACCENT_SOFT, ACCENT, "#3a2463", "#140a24"])


def response_norm(r):
    """Spectral norm of d alpha*/d r = J(alpha*)^{-1} at target radius r."""
    c2 = (r ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
    c2 = np.clip(c2, -1, 1)
    tr = L1 ** 2 + L2 ** 2 + 2 * L1 * L2 * c2 + L2 ** 2       # trace of J^T J
    det = (L1 * L2) ** 2 * (1 - c2 ** 2)                     # det of J^T J = (l1 l2 sin theta2)^2
    smin2 = (tr - np.sqrt(np.maximum(tr ** 2 - 4 * det, 0))) / 2
    with np.errstate(divide="ignore"):
        return 1 / np.sqrt(smin2)


def fig_ik(tall=False):
    reach = L1 + L2
    n = 601
    xs = np.linspace(-reach, reach, n)
    X, Y = np.meshgrid(xs, xs)
    R = np.hypot(X, Y)
    Z = np.where((R > 1e-3) & (R < reach - 1e-3), response_norm(R), np.nan)
    vmin, vmax = 0.9, 40.0

    if tall:
        fig, axes = plt.subplots(2, 1, figsize=(4.4, 9.4), gridspec_kw={"height_ratios": [1.15, 1]})
    else:
        fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.4), gridspec_kw={"width_ratios": [1.05, 1]})

    ax = axes[0]
    im = ax.imshow(np.ma.masked_invalid(Z), extent=(-reach, reach, -reach, reach), origin="lower",
                   cmap=CMAP, norm=LogNorm(vmin=vmin, vmax=vmax), interpolation="bilinear", zorder=2)
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(reach * np.cos(t), reach * np.sin(t), color=INK, lw=.9, zorder=3)
    ax.set_aspect("equal"); ax.grid(False)
    ax.set_xlim(-2.15, 2.15); ax.set_ylim(-2.15, 2.15)
    ax.set_xticks([-2, -1, 0, 1, 2]); ax.set_yticks([-2, -1, 0, 1, 2])
    ax.set_xlabel(r"Target $r_1$", color=MUTED); ax.set_ylabel(r"Target $r_2$", color=MUTED)
    ax.set_title("Reachable workspace", loc="left", fontsize=15)
    cb = fig.colorbar(im, ax=ax, fraction=.046, pad=.04)
    cb.set_ticks([1, 2, 5, 10, 20, 40]); cb.set_ticklabels(["1", "2", "5", "10", "20", "40"])
    cb.minorticks_off()
    cb.outline.set_edgecolor(LINE); cb.ax.tick_params(color=MUTED, labelcolor=MUTED, labelsize=14)
    cb.set_label(r"$\|\partial\mathbf{\alpha}^{\ast}/\partial\mathbf{r}\|_2$", color=INK)

    ax = axes[1]
    r = np.linspace(0.004, reach - 0.0005, 3000)
    ax.plot(r, response_norm(r), color=ACCENT, lw=2.2, zorder=3)
    ax.set_yscale("log"); ax.set_ylim(vmin, 300)
    ax.set_yticks([1, 10, 100], ["1", "10", "100"]); ax.minorticks_off()
    ax.set_xlim(0, reach)
    ax.set_xticks([0, 0.5, 1, 1.5, 2])
    ax.set_xlabel(r"Target radius $r=\|\mathbf{r}\|$", color=MUTED)
    ax.set_ylabel(r"$\|\partial\mathbf{\alpha}^{\ast}/\partial\mathbf{r}\|_2$", color=MUTED)
    ax.set_title("Along any ray", loc="left", fontsize=15)
    ax.annotate("Arm folded\n" + r"($\alpha_2=\pi$)", xy=(0.03, 120), xytext=(0.28, 90), fontsize=14,
                color=MUTED, arrowprops=dict(arrowstyle="->", color=MUTED, lw=.8))
    ax.annotate("Arm fully\nextended\n" + r"($\alpha_2=0$)", xy=(1.985, 30), xytext=(1.18, 60), fontsize=14,
                color=MUTED, arrowprops=dict(arrowstyle="->", color=MUTED, lw=.8))
    fig.tight_layout(w_pad=2.6, h_pad=2.0)
    save(fig, "ik-conditioning-tall" if tall else "ik-conditioning")
    return response_norm(np.array([np.sqrt(2.0)]))[0]


if __name__ == "__main__":
    bps = fig_dispatch(); fig_dispatch(tall=True)
    k = fig_ik(); fig_ik(tall=True)
    print("dispatch breakpoints (MWh):", [round(b, 6) for b in bps])
    print("IK response norm at r = sqrt(2):", round(float(k), 6))
    for x in (10.0, 100.0, 200.0, 250.0):
        g, phi, lam = dispatch(x)
        print(f"d={x:6.1f}  g={np.round(g, 4)}  phi={phi:.4f}  lambda={lam:.4f}")
