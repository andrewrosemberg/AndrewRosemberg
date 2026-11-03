"""Evidence charts for Learned Model Correction (src/research/dc2ac/).

Source: Rosemberg, Klamkin and Van Hentenryck, "Differentiable Optimization for Deep
Learning-Enhanced DC Approximation of AC Optimal Power Flow", arXiv:2504.01970 (R-09),
Figure 2 (a)-(c) and Table 2.

The per-sample validation errors are not published as a table.  They are recovered
exactly from the paper's own vector figures (pg_accuracy.pdf, pf_accuracy.pdf,
va_accuracy.pdf, Matplotlib PDFs in the paper source, read-only): every scatter marker
is a translated form XObject, and the axis transform is fixed by the major and minor tick
marks.  The script refuses to plot unless the recovered points reproduce the paper's
Table 2 means (two decimals) and its per-sample statements (DC2AC below both baselines on
95% of samples for generation, 97% for branch flows, 13% for voltage angles).

    .venv/bin/python tools/figures/dc2ac.py
"""

import re
import zlib
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "src" / "assets" / "img" / "research"
PAPER = Path.home() / "Workspace" / "diffopt_mlopt_policy"

INK, MUTED, LINE = "#202a33", "#687078", "#dddcd5"
ACCENT, TEAL, GREY = "#7551a7", "#2b7a73", "#8d949b"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none",
    "svg.hashsalt": "dc2ac",
    "font.size": 11,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100, "savefig.bbox": "tight", "savefig.pad_inches": .12,
})

# Paper series colours (Matplotlib RGB, 3 decimals) -> method.
PAPER_COLORS = {(0.929, 0.267, 0.188): "DC2AC", (0.208, 0.588, 0.718): "Proxy", (0.016, 0.161, 0.298): "DC-OPF"}
# Exponents of the labelled major y ticks, read from each source figure.
MAJOR_EXP = {"pg": [-5, -4, -3, -2, -1, 0, 1], "pf": [1, 2], "va": [0]}
# Paper Table 2 (per unit) and Section 4.1 per-sample statements.
TABLE2 = {"pg": {"DC-OPF": 0.90, "Proxy": 0.74, "DC2AC": 0.22},
          "pf": {"DC-OPF": 9.72, "Proxy": 12.83, "DC2AC": 7.57},
          "va": {"DC-OPF": 1.12, "Proxy": 0.95, "DC2AC": 1.08}}
WIN_SHARE = {"pg": 0.95, "pf": 0.97, "va": 0.13}


def recover(var):
    """Return {method: (total_demand, l1_error)} from the paper's vector figure."""
    raw = (PAPER / f"{var}_accuracy.pdf").read_bytes()
    stream = re.search(rb"9 0 obj.*?stream\r?\n(.*?)\r?\nendstream", raw, re.S).group(1)
    s = zlib.decompress(stream).decode("latin-1").replace("\r", "\n")

    series, cur, color = {}, None, None
    for ln in (x.strip() for x in s.split("\n")):
        m = re.match(r"^([\d.]+) ([\d.]+) ([\d.]+) rg$", ln)
        if m:
            color = tuple(round(float(v), 3) for v in m.groups())
        if ln == "q" and color in PAPER_COLORS:
            cur, x, y = [], 0.0, 0.0
            continue
        m = re.match(r"^1 0 0 1 (\S+) (\S+) cm /M\d Do$", ln)
        if m and cur is not None:
            x += float(m.group(1)); y += float(m.group(2)); cur.append((x, y))
            continue
        if ln == "Q" and cur is not None:
            series[PAPER_COLORS[color]] = np.array(cur); cur = None

    X, Y = (float(v) for v in re.search(r"q ([\d.]+) ([\d.]+) [\d.]+ [\d.]+ re W n", s).groups())
    seg = re.findall(r"\n([-\d.]+) ([-\d.]+) m\n([-\d.]+) ([-\d.]+) l", s)
    xmaj = sorted({float(a) for a, b, c, d in seg if a == c and abs(float(b) - Y) < .01 and abs(float(d) - (Y - 3.5)) < .01})
    ymaj = sorted({float(b) for a, b, c, d in seg if b == d and abs(float(a) - X) < .01 and abs(float(c) - (X - 3.5)) < .01})
    ymin = sorted({float(b) for a, b, c, d in seg if b == d and abs(float(a) - X) < .01 and abs(float(c) - (X - 2)) < .01})

    # x: major ticks at 35, 40, ..., 60 (total demand, per unit).
    assert len(xmaj) == 6, xmaj
    bx = np.polyfit(xmaj, [35, 40, 45, 50, 55, 60], 1)
    # y: log10 scale from two majors, or from one major and the 2x10^k minor tick above it.
    exps = MAJOR_EXP[var]
    assert len(ymaj) == len(exps), (var, ymaj)
    if len(ymaj) >= 2:
        by = np.polyfit(ymaj, exps, 1)
    else:
        above = min(v for v in ymin if v > ymaj[0])
        k = np.log10(2) / (above - ymaj[0])
        by = np.array([k, exps[0] - k * ymaj[0]])
    # Every minor tick must land on m x 10^k, m in 2..9: validates the transform.
    mant = 10 ** np.mod(np.polyval(by, np.array(ymin)), 1)
    assert np.allclose(mant, np.round(mant), atol=2e-3), mant

    return {k: (np.polyval(bx, v[:, 0]), 10 ** np.polyval(by, v[:, 1])) for k, v in series.items()}


def load():
    data = {v: recover(v) for v in ("pg", "pf", "va")}
    for var, d in data.items():
        assert set(d) == {"DC2AC", "Proxy", "DC-OPF"} and all(len(d[m][0]) == 2000 for m in d)
        assert all(np.allclose(d["DC2AC"][0], d[m][0], atol=1e-3) for m in d), "samples are not aligned"
        for m, ref in TABLE2[var].items():
            # Table 2 is rounded to two decimals; marker positions carry ~1e-6 relative precision.
            assert abs(float(d[m][1].mean()) - ref) <= .0051, (var, m, d[m][1].mean(), ref)
        e = {m: d[m][1] for m in d}
        share = np.mean((e["DC2AC"] < e["Proxy"]) & (e["DC2AC"] < e["DC-OPF"]))
        assert round(share, 2) == WIN_SHARE[var], (var, share)
        print(f"{var}: means {[round(float(d[m][1].mean()), 3) for m in ('DC-OPF', 'Proxy', 'DC2AC')]}, "
              f"DC2AC lowest on {share:.4f}, DC2AC min {d['DC2AC'][1].min():.2e}")
    return data


STYLE = [("DC-OPF", "Unadjusted DC-OPF", GREY), ("Proxy", "Direct proxy", TEAL), ("DC2AC", "Corrected DC-OPF (DC2AC)", ACCENT)]


def panel(ax, d, title, ylabel=True, plain_ticks=None, unit=" (per unit)", fontsize=14.5):
    for key, _, color in STYLE:
        x, y = d[key]
        ax.scatter(x, y, s=4, color=color, alpha=.55, linewidths=0, rasterized=True, zorder=2)
    ax.set_yscale("log")
    if plain_ticks is None:
        # Plain scientific notation keeps the exponents at the same readable
        # type size as every other tick, including in the phone composition.
        plain_ticks = [10. ** k for k in range(-5, 2)]
    if plain_ticks:
        ax.yaxis.set_major_locator(FixedLocator(plain_ticks))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="both", labelsize=fontsize)
    ax.set_title(title, loc="left", fontsize=fontsize + 1, pad=8)
    ax.set_xlabel("Total active demand (per unit)", color=MUTED, fontsize=fontsize)
    if ylabel:
        ax.set_ylabel("L1 distance to AC-OPF" + unit, color=MUTED, fontsize=fontsize)
    ax.set_xlim(31, 63)
    ax.grid(which="minor", visible=False)


def legend(fig, ncol, y, fontsize=14.5):
    handles = [plt.Line2D([], [], ls="", marker="o", ms=6, color=c, label=l) for _, l, c in STYLE]
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False, fontsize=fontsize,
               bbox_to_anchor=(.5, y), handletextpad=.3, columnspacing=1.)


def save(fig, name):
    path = OUT / f"{name}.svg"
    fig.savefig(path, transparent=True, dpi=220,
                metadata={"Date": None})
    # Matplotlib adds spaces before newlines inside SVG path attributes.
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def fig_accuracy(data):
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    panel(axes[0], data["pg"], "Generation")
    panel(axes[1], data["pf"], "Branch flows", ylabel=False, plain_ticks=[5, 10, 20, 50, 100])
    fig.tight_layout(rect=(0, .08, 1, 1), w_pad=2.5)
    legend(fig, 3, -.01)
    save(fig, "dc2ac-accuracy")

    # At the phone's 316 CSS-pixel image width, 12 pt / ~300 pt
    # viewBox width gives at least 12 CSS pixels for ticks and labels.
    fig, axes = plt.subplots(2, 1, figsize=(4.2, 8.2))
    panel(axes[0], data["pg"], "Generation", fontsize=12)
    panel(axes[1], data["pf"], "Branch flows", plain_ticks=[5, 10, 20, 50, 100], fontsize=12)
    fig.tight_layout(rect=(0, .1, 1, 1), h_pad=2.2)
    handles = [plt.Line2D([], [], ls="", marker="o", ms=6, color=c, label=l) for _, l, c in STYLE]
    fig.legend(handles=handles, loc="lower left", ncol=1, frameon=False, fontsize=12,
               bbox_to_anchor=(.08, 0), handletextpad=.3)
    save(fig, "dc2ac-accuracy-compact")


def fig_angles(data):
    # A single composition stays legible in the 600-pixel inset and on phones.
    fig, ax = plt.subplots(figsize=(4.2, 4.7))
    panel(ax, data["va"], "Voltage angles", plain_ticks=[.5, .6, .8, 1, 2, 3, 4], unit="", fontsize=12)
    fig.tight_layout(rect=(0, .2, 1, 1))
    handles = [plt.Line2D([], [], ls="", marker="o", ms=6, color=c, label=l) for _, l, c in STYLE]
    fig.legend(handles=handles, loc="lower left", ncol=1, frameon=False, fontsize=12,
               bbox_to_anchor=(.1, -.01), handletextpad=.3)
    save(fig, "dc2ac-angles")


if __name__ == "__main__":
    d = load()
    fig_accuracy(d)
    fig_angles(d)
