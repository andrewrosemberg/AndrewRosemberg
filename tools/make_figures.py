"""Regenerate the site-styled charts in src/assets/img/research/.

Every number here is copied from a published paper or the cited source table,
noted next to each dataset; the convexity panel is an illustrative toy.

    python3 -m venv .venv && .venv/bin/pip install matplotlib numpy
    .venv/bin/python tools/make_figures.py
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")
OUT = Path(__file__).resolve().parents[1] / "src" / "assets" / "img" / "research"

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
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})


def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", transparent=True)
    fig.savefig(OUT / f"{name}.png", dpi=200, facecolor="white")
    plt.close(fig)


def hbar(ax, labels, values, colors, fmt, xlabel, xmax=None):
    y = np.arange(len(labels))[::-1]
    ax.barh(y, values, color=colors, height=.62, zorder=2)
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", length=0, labelsize=11.5, labelcolor=INK)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=10.5)
    top = xmax or max(values) * 1.18
    ax.set_xlim(0, top)
    for yi, v in zip(y, values):
        ax.text(v + top * .012, yi, fmt(v), va="center", fontsize=10.5, color=INK)


# --------------------------------------------------------------------------- #
# 1. Convexity toy: one cut is valid everywhere (ICNN + SDDP pages, card art)
#    Illustrative only: merit-order dispatch with quadratic generator costs.
# --------------------------------------------------------------------------- #
def merit_order_cost(d):
    # three generators: cost c*g + a/2 g^2 on [0, cap]; equal-marginal-cost dispatch
    c = np.array([10.0, 22.0, 40.0]); a = np.array([.10, .06, .05]); cap = np.array([90.0, 120.0, 140.0])
    lo, hi = 0.0, 200.0
    for _ in range(80):
        lam = (lo + hi) / 2
        g = np.clip((lam - c) / a, 0, cap)
        lo, hi = (lam, hi) if g.sum() < d else (lo, lam)
    g = np.clip((lam - c) / a, 0, cap)
    return float((c * g + a / 2 * g**2).sum()), lam


def fig_convexity():
    d = np.linspace(5, 330, 400)
    v = np.array([merit_order_cost(x)[0] for x in d]) / 1e3
    rng = np.random.default_rng(3)
    xs = np.array([40.0, 130.0, 230.0, 300.0])
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9), sharey=True)
    # left: convex value with supporting cuts
    ax = axes[0]
    ax.plot(d, v, color=INK, lw=2.4, zorder=3, label="True operating cost (convex)")
    for i, x0 in enumerate(xs):
        v0, lam = merit_order_cost(x0)
        cut = (v0 + lam * (d - x0)) / 1e3
        ax.plot(d, cut, color=ACCENT, lw=1.3, alpha=.85, zorder=2, label="Cuts from value + slope" if i == 0 else None)
        ax.plot([x0], [v0 / 1e3], "o", color=ACCENT, ms=6, zorder=4)
    env = np.max([(merit_order_cost(x0)[0] + merit_order_cost(x0)[1] * (d - x0)) / 1e3 for x0 in xs], axis=0)
    ax.fill_between(d, env, v, color=ACCENT_SOFT, alpha=.35, zorder=1, lw=0)
    ax.set_title("Convex: every cut is a global under-estimate", fontsize=12, loc="left", pad=10)
    ax.set_xlabel("Demand", color=MUTED); ax.set_ylabel("Operating cost", color=MUTED)
    ax.set_ylim(-1, v.max() * 1.08); ax.set_xticks([]); ax.set_yticks([])
    ax.legend(frameon=False, fontsize=9.8, loc="upper left")
    # right: an unrestricted fit from the same samples can bend the wrong way
    ax = axes[1]
    ax.plot(d, v, color=INK, lw=2.4, zorder=3, label="True operating cost")
    xs2 = np.sort(np.concatenate([xs, [90.0, 180.0, 265.0]]))
    ys2 = np.array([merit_order_cost(x)[0] for x in xs2]) / 1e3 + rng.normal(0, .55, xs2.size)
    coeff = np.polyfit(xs2, ys2, 5)
    ax.plot(d, np.polyval(coeff, d), color=AMBER, lw=1.8, zorder=2, label="Unrestricted fit")
    ax.plot(xs2, ys2, "o", color=AMBER, ms=5, zorder=4)
    ax.set_title("Unrestricted: accurate at samples, no global guarantee", fontsize=12, loc="left", pad=10)
    ax.set_xlabel("Demand", color=MUTED); ax.set_xticks([])
    ax.legend(frameon=True, framealpha=.92, facecolor="white", edgecolor="none", fontsize=9.8, loc="lower right")
    fig.tight_layout(w_pad=2.5)
    save(fig, "convexity-cuts")


# --------------------------------------------------------------------------- #
# 2. TS-DDR, hydrothermal: mean AC cost gap to SDDP with conic cuts
#    (proposal / storage manuscript Table 2, 490 paired test scenarios)
# --------------------------------------------------------------------------- #
def fig_hydro():
    rows = [("TS-DDR", .15, "0.4 h", ACCENT), ("SDDP-DC", .35, "1.6 h", TEAL),
            ("SAC", 2.42, "16.9 h", GREY), ("REINFORCE", 16.53, "3.0 h", GREY),
            ("TD3", 16.55, "10.1 h", GREY), ("PPO", 16.81, "3.1 h", GREY), ("TS-LDR (affine)", 17.46, "0.3 h", GREY)]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    hbar(ax, [r[0] for r in rows], [r[1] for r in rows], [r[3] for r in rows],
         lambda v: f"{v:.2f}%", "Mean AC operating cost above SDDP-SOC", xmax=24.5)
    ax.set_xticks([0, 5, 10, 15, 20])
    for yi, r in zip(np.arange(len(rows))[::-1], rows):
        ax.text(24.4, yi, r[2], va="center", ha="right", fontsize=10, color=MUTED)
    ax.text(24.4, len(rows) - .35, "train / solve time", ha="right", fontsize=9, color=MUTED)
    save(fig, "tsddr-hydro-gaps")


# --------------------------------------------------------------------------- #
# 3. TS-DDR, 793-bus battery network: excess cost over best-known AC reference
#    (proposal / storage manuscript Table 3)
# --------------------------------------------------------------------------- #
def fig_battery():
    policies = ["TS-DDR", "SDDP-DC", "TS-LDR (affine)", "SDDP-SOC"]
    no_ramp = [0.31, 0.70, 4.55, 61.98]
    ramp = [2.37, 4.76, 112.09, 101.99]
    colors = [ACCENT, TEAL, GREY, GREY]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 2.9), sharey=True)
    for ax, vals, title in [(axes[0], no_ramp, "Without ramp limits (159 states)"),
                            (axes[1], ramp, "With ramp limits (241 states)")]:
        y = np.arange(4)[::-1]
        ax.barh(y, vals, color=colors, height=.6, zorder=2)
        ax.set_xscale("log"); ax.set_xlim(.1, 400)
        ax.set_yticks(y, policies); ax.tick_params(axis="y", length=0, labelsize=11, labelcolor=INK)
        ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
        for yi, v in zip(y, vals):
            ax.text(v * 1.12, yi, f"{v:.2f}%", va="center", fontsize=10.5)
        ax.set_title(title, fontsize=11.5, loc="left")
        ax.set_xlabel("Excess AC cost over reference (log scale)", color=MUTED, fontsize=10)
    fig.tight_layout(w_pad=3)
    save(fig, "tsddr-battery-gaps")


# --------------------------------------------------------------------------- #
# Strategic bidding (Rosemberg et al., strategic bidding through AC clearing; PhD
# proposal, differentiable optimization chapter): DC search on IEEE-118 against the
# exact MPEC (about 70% and 25% below it); AC best-vs-best table, mean ± s.d.
# --------------------------------------------------------------------------- #
def fig_bidding_search():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 2.9), gridspec_kw={"width_ratios": [1, 1.15]})
    y = np.array([1, 0])
    a.barh(y, [30, 75], color=[ACCENT, TEAL], height=.56, zorder=2)
    a.axvline(100, color=INK, lw=1.2, ls=(0, (3, 2)), zorder=3)
    a.text(98, 1.42, "exact bilevel optimum", ha="right", va="center", fontsize=9.5, color=MUTED)
    for yi, v in zip(y, [30, 75]):
        a.text(v + 2, yi, f"≈{v}%", va="center", fontsize=10.5)
    a.set_yticks(y, ["Gradient-based", "Derivative-free"])
    a.set_xlim(0, 108); a.set_ylim(-.6, 1.7)
    a.set_title("Linear clearing (IEEE-118)", fontsize=11.5, loc="left")
    a.set_xlabel("Profit reached, % of the optimum", color=MUTED, fontsize=10)
    systems = ["PEGASE-2869", "PEGASE-1354", "RTE-2868", "GOC-2000", "IEEE-300"]
    mean = np.array([110.0, 102.1, 28.3, 2.2, -1.1]); sd = np.array([11.7, 12.7, 8.0, 1.0, 19.9])
    yb = np.arange(len(systems))[::-1]
    b.barh(yb, mean, xerr=sd, color=ACCENT, height=.56, zorder=2,
           error_kw=dict(ecolor=MUTED, elinewidth=1, capsize=2.5))
    b.axvline(0, color=INK, lw=.9, zorder=3)
    for yi, v, s in zip(yb, mean, sd):
        b.text(max(v + s, 0) + 4, yi, f"{v:+.0f}%".replace("-", "−"), va="center", fontsize=10.5)
    b.set_yticks(yb, systems)
    b.set_xlim(-25, 150)
    b.set_title("Nonlinear clearing", fontsize=11.5, loc="left")
    b.set_xlabel("Gain of best gradient-based over best derivative-free (%)", color=MUTED, fontsize=10)
    for ax in (a, b):
        ax.tick_params(axis="y", length=0, labelsize=11, labelcolor=INK)
        ax.grid(axis="y", visible=False); ax.spines["left"].set_visible(False)
    fig.tight_layout(w_pad=3)
    save(fig, "bidding-search-comparison")


# --------------------------------------------------------------------------- #
# 4. Network simplifications (IEEE TSTE 2022, Table II, 28-bus Bolivian system)
# --------------------------------------------------------------------------- #
def fig_network():
    models = ["NFA", "DC", "DC + losses", "SOC"]
    plan = [0.58687, 0.58714, 0.61310, 0.60818]
    impl = [0.68735, 0.64523, 0.60941, 0.60935]
    gap = [17.067, 9.855, -0.602, 0.193]
    x = np.arange(len(models)); w = .36
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.bar(x - w / 2, plan, w, color=ACCENT_SOFT, label="Planned cost (planning model)", zorder=2)
    ax.bar(x + w / 2, impl, w, color=ACCENT, label="Implemented cost (AC operation)", zorder=2)
    for xi, g, i in zip(x, gap, impl):
        ax.text(xi + w / 2, i + .004, f"{g:+.1f}%", ha="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_xticks(x, [m + " planning" for m in models]); ax.tick_params(axis="x", length=0, labelsize=11, labelcolor=INK)
    ax.set_ylim(.55, .71); ax.set_ylabel("Expected cost ($ million)", color=MUTED)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    save(fig, "network-simplifications")


# --------------------------------------------------------------------------- #
# 5. ICNN vs DNN mean AC-OPF value error (EPSR 2024 / arXiv:2310.04605, Table II)
# --------------------------------------------------------------------------- #
def fig_icnn():
    systems = ["IEEE-300", "PEGASE-1k", "PEGASE-2k", "RTE-6k"]
    icnn = [.39, .33, .24, .25]; dnn = [.39, .68, .27, .33]
    x = np.arange(4); w = .36
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.bar(x - w / 2, icnn, w, color=ACCENT, label="ICNN (convex by construction)", zorder=2)
    ax.bar(x + w / 2, dnn, w, color=GREY, label="Unrestricted DNN", zorder=2)
    for xi, a, b in zip(x, icnn, dnn):
        ax.text(xi - w / 2 - .03, a + .012, f"{a:.2f}", ha="center", fontsize=9.5)
        ax.text(xi + w / 2 + .03, b + .012, f"{b:.2f}", ha="center", fontsize=9.5, color="#3a4550")
    ax.set_xticks(x, systems); ax.tick_params(axis="x", length=0, labelcolor=INK)
    ax.set_ylabel("Mean error (%)", color=MUTED); ax.set_ylim(0, .8); ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    save(fig, "icnn-ac-errors")


# --------------------------------------------------------------------------- #
# 6. DiffOpt economic-dispatch case study (arXiv:2510.25986, Case Study 1):
#    min sum c_i g_i + c2_i g_i^2 + c_phi phi, sum g + phi = d, 0 <= g <= G.
#    Solved in closed form (equal marginal cost); same data as the paper.
# --------------------------------------------------------------------------- #
C, C2, G, CPHI = np.array([20.0, 30.0]), np.array([0.2, 0.1]), np.array([150.0, 80.0]), 1000.0


def dispatch(d):
    lo, hi = 0.0, CPHI
    for _ in range(100):
        lam = (lo + hi) / 2
        g = np.clip((lam - C) / (2 * C2), 0, G)
        lo, hi = (lam, hi) if g.sum() < d else (lo, lam)
    g = np.clip((lam - C) / (2 * C2), 0, G)
    return g, max(d - g.sum(), 0.0), lam


def fig_dispatch(tall=False):
    """Three panels in a row, or stacked (tall=True) for narrow screens."""
    d = np.linspace(0, 260, 1041)
    gs = np.array([dispatch(x)[0] for x in d]); phi = np.array([dispatch(x)[1] for x in d])
    lam = np.array([dispatch(x)[2] for x in d])
    sens = np.gradient(gs, d, axis=0)
    fig, axes = plt.subplots(3, 1, figsize=(5.2, 9.0)) if tall else plt.subplots(1, 3, figsize=(11.6, 3.3))
    ax = axes[0]
    ax.stackplot(d, gs[:, 0], gs[:, 1], phi, colors=[ACCENT, TEAL, "#d9b38c"],
                 labels=["Plant 1 (cheaper)", "Plant 2", "Unmet demand"], zorder=2)
    ax.set_title("Optimal dispatch", loc="left", fontsize=12); ax.set_xlabel("Demand d (MWh)", color=MUTED)
    ax.set_ylabel("MWh", color=MUTED); ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    ax = axes[1]
    ax.plot(d, np.minimum(lam, 80), color=INK, lw=2, zorder=2)
    ax.set_title("Price λ(d) = ∂cost/∂d", loc="left", fontsize=12); ax.set_xlabel("Demand d (MWh)", color=MUTED)
    ax.set_ylabel("$/MWh (clipped at 80)", color=MUTED); ax.set_ylim(15, 82)
    ax.annotate("jumps to the\nunmet-demand penalty", xy=(232, 80), xytext=(40, 64), fontsize=9.5, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=.8))
    ax = axes[2]
    ax.plot(d, sens[:, 0], color=ACCENT, lw=2, label="∂g₁/∂d", zorder=3)
    ax.plot(d, sens[:, 1], color=TEAL, lw=2, label="∂g₂/∂d", zorder=2)
    ax.set_title("Solution sensitivities", loc="left", fontsize=12); ax.set_xlabel("Demand d (MWh)", color=MUTED)
    ax.set_ylim(-.05, 1.22); ax.legend(frameon=False, fontsize=10, ncol=2, loc="upper center", bbox_to_anchor=(0.36, 1.0))
    for a in axes:
        for x in (25, 145, 230):
            a.axvline(x, color=LINE, lw=1, ls="--", zorder=1)
    fig.tight_layout(w_pad=2.2, h_pad=1.6)
    save(fig, "diffopt-dispatch-sweep-tall" if tall else "diffopt-dispatch-sweep")


# --------------------------------------------------------------------------- #
# 7. PortfolioOpt.jl docs backtest (illustrative): six stocks, 2010, no costs.
#    tools/data/portfolioopt_backtest_2010.csv was produced by re-running the
#    package's documented strategies (docs/src/examples) on its test data.
# --------------------------------------------------------------------------- #
def fig_portfolio():
    import csv
    from datetime import date
    rows = list(csv.DictReader(open(Path(__file__).parent / "data" / "portfolioopt_backtest_2010.csv")))
    t = [date.fromisoformat(r["date"]) for r in rows]
    series = [("EP_markowitz_limit_var", "Markowitz (variance limit)", INK, "-"),
              ("EP_markowitz_with_soyster_l1", "Markowitz + robust floor + L1", GREY, "-"),
              ("Ben-Tal", "Robust: ellipsoidal set", ACCENT, "-"),
              ("Bertsimas", "Robust: budget set", TEAL, "-")]
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    for key, label, color, ls in series:
        ax.plot(t, [float(r[key]) for r in rows], color=color, lw=1.8, ls=ls, label=label)
    ax.set_ylabel("Cumulative wealth", color=MUTED)
    ax.legend(frameon=False, fontsize=9.8, ncol=2, loc="upper left")
    fig.autofmt_xdate()
    save(fig, "portfolio-backtest")


# --------------------------------------------------------------------------- #
# 8. Moment-based (Delage–Ye) ambiguity set over 2x2 covariance matrices:
#    {Sigma : 0 <= Sigma <= gamma2 * Sigma0} drawn in (s11, s22, s12) space.
# --------------------------------------------------------------------------- #
def fig_ambiguity_set():
    from scipy.spatial import ConvexHull
    from matplotlib.colors import LightSource
    S0 = np.array([[1.0, 0.35], [0.35, 0.7]]); g2 = 2.0
    rng = np.random.default_rng(1)
    # sample the boundary: either Sigma or g2*S0 - Sigma is singular PSD
    pts = []
    for _ in range(6000):
        th = rng.uniform(0, 2 * np.pi); v = np.array([np.cos(th), np.sin(th)])
        r = rng.uniform(0, 1) ** 0.5
        for base, sign in ((np.zeros((2, 2)), 1), (g2 * S0, -1)):
            # rank-one directions from each apex: base + sign * t * u u^T, u on a circle scaled into the set
            M = base + sign * r * g2 * np.outer(v, v) * 1.6
            if np.linalg.eigvalsh(M).min() >= -1e-9 and np.linalg.eigvalsh(g2 * S0 - M).min() >= -1e-9:
                pts.append((M[0, 0], M[1, 1], M[0, 1]))
    for _ in range(40000):
        a, b = rng.uniform(0, g2 * 1.1, 2); c = rng.uniform(-g2, g2)
        M = np.array([[a, c], [c, b]])
        if np.linalg.eigvalsh(M).min() >= 0 and np.linalg.eigvalsh(g2 * S0 - M).min() >= 0:
            pts.append((a, b, c))
    pts = np.array(pts); hull = ConvexHull(pts)
    fig = plt.figure(figsize=(6.6, 5.4)); ax = fig.add_subplot(projection="3d", computed_zorder=False)
    ls = LightSource(azdeg=225, altdeg=35)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("acc", ["#3f2a63", "#7551a7", "#c9b6e4", "#f1eaf9"])
    ax.plot_trisurf(pts[:, 0], pts[:, 1], pts[:, 2], triangles=hull.simplices, cmap=cmap, lightsource=ls,
                    linewidth=0, antialiased=True, alpha=0.62, shade=True, zorder=1)
    ax.plot([0, g2 * S0[0, 0]], [0, g2 * S0[1, 1]], [0, g2 * S0[0, 1]], color=INK, lw=1, ls=(0, (3, 3)), zorder=20)
    ax.scatter([S0[0, 0]], [S0[1, 1]], [S0[0, 1]], color=AMBER, s=52, depthshade=False, zorder=21)
    ax.scatter([0, g2 * S0[0, 0]], [0, g2 * S0[1, 1]], [0, g2 * S0[0, 1]], color=INK, s=16, depthshade=False, zorder=22)
    ax.text(0, 0, -0.45, "0", color=INK, fontsize=10, zorder=30)
    ax.text(g2 * S0[0, 0] + .12, g2 * S0[1, 1] + .1, g2 * S0[0, 1] + .12, "γ₂Σ₀", color=INK, fontsize=11, zorder=30)
    ax.text(S0[0, 0] + .08, S0[1, 1], S0[0, 1] - .32, "Σ₀ (estimate)", color=AMBER, fontsize=10.5, fontweight="bold", zorder=30)
    ax.set_xlabel("σ₁₁", color=MUTED, labelpad=2); ax.set_ylabel("σ₂₂", color=MUTED, labelpad=2); ax.set_zlabel("σ₁₂", color=MUTED, labelpad=0)
    ax.view_init(elev=14, azim=-122)
    ax.set_box_aspect((1, 0.8, 0.9))
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((1, 1, 1, 0)); axis._axinfo["grid"]["color"] = (0.88, 0.88, 0.85, 1)
    ax.set_xticks([0, 1, 2]); ax.set_yticks([0, 0.7, 1.4]); ax.set_zticks([-1, 0, 1])
    ax.tick_params(labelsize=8, colors=MUTED, pad=0)
    save(fig, "portfolio-ambiguity-set")


# --------------------------------------------------------------------------- #
# 9. Uncertainty sets for two mean returns (teaching figure, house style):
#    box (Soyster), budget (Bertsimas–Sim, Gamma = 1) and ellipsoid (Ben-Tal–Nemirovski).
# --------------------------------------------------------------------------- #
def fig_uncertainty_sets():
    r = np.array([2.0, 1.0]); D = np.array([1.6, 1.0])
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    box = np.array([[r[0]-D[0], r[1]-D[1]], [r[0]+D[0], r[1]-D[1]], [r[0]+D[0], r[1]+D[1]], [r[0]-D[0], r[1]+D[1]], [r[0]-D[0], r[1]-D[1]]])
    ax.fill(box[:, 0], box[:, 1], color="#eceae4", zorder=1, label="Box (Γ = 2)")
    ax.plot(box[:, 0], box[:, 1], color=GREY, lw=1.2, zorder=2)
    dia = np.array([[r[0]-D[0], r[1]], [r[0], r[1]+D[1]], [r[0]+D[0], r[1]], [r[0], r[1]-D[1]], [r[0]-D[0], r[1]]])
    ax.fill(dia[:, 0], dia[:, 1], color=ACCENT_SOFT, alpha=.8, zorder=3, label="Budget (Γ = 1)")
    ax.plot(dia[:, 0], dia[:, 1], color=ACCENT, lw=1.6, zorder=4)
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r[0] + .78 * D[0] * np.cos(t), r[1] + .78 * D[1] * np.sin(t), color=TEAL, lw=1.8, zorder=5, label="Ellipsoid")
    ax.plot(*r, "o", color=AMBER, ms=8, zorder=6); ax.text(r[0] + .08, r[1] + .1, "estimate r̂", color=INK, fontsize=10.5)
    ax.annotate("", xy=(r[0]+D[0], r[1]+D[1]+.18), xytext=(r[0], r[1]+D[1]+.18), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1))
    ax.text(r[0] + D[0]/2, r[1] + D[1] + .26, "Δ₁", ha="center", color=MUTED)
    ax.annotate("", xy=(r[0]+D[0]+.18, r[1]+D[1]), xytext=(r[0]+D[0]+.18, r[1]), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1))
    ax.text(r[0] + D[0] + .26, r[1] + D[1]/2, "Δ₂", va="center", color=MUTED)
    ax.set_xlabel("mean return of asset 1", color=MUTED); ax.set_ylabel("mean return of asset 2", color=MUTED)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_aspect("equal")
    ax.set_xlim(r[0]-D[0]-.3, r[0]+D[0]+.7); ax.set_ylim(r[1]-D[1]-.3, r[1]+D[1]+.55)
    ax.legend(frameon=True, framealpha=.92, facecolor="white", edgecolor="none", fontsize=9.5, loc="upper left", bbox_to_anchor=(1.01, 1))
    save(fig, "portfolio-budget-set")


if __name__ == "__main__":
    fig_convexity(); fig_hydro(); fig_battery(); fig_bidding_search(); fig_network(); fig_icnn(); fig_dispatch(); fig_dispatch(tall=True); fig_portfolio(); fig_ambiguity_set(); fig_uncertainty_sets()
    print("figures written to", OUT)
