"""Source-table evidence for Policies for Multistage Decisions.

Run with .venv/bin/python tools/figures/decision-rules.py.
[P] ~/Downloads/TSGDR_2026_New.pdf, Tables I–II.
[S] ~/Downloads/TSGDR_2026_New (1).pdf, Table S3.
[T] ~/Workspace/PhD Proposal Report/main.pdf, Sections 4.7–4.8.
All observations are also recorded in .editorial/claims/decision-rules.tsv.
Wide and phone plots share the same data below; only their layout changes.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "src/assets/img/research"
INK, MUTED, LINE = "#202a33", "#535d66", "#dddcd5"
# Each method has one color throughout the page, including both SDDP variants.
COLORS = {
    "TS-DDR": "#7551a7", "SDDP-DC-AC": "#2b7a73",
    "SDDP-SOC-AC": "#3568a1", "TS-LDR": "#70777e",
    "SAC": "#b9741f", "REINFORCE": "#ad4964",
    "TD3": "#657a2e", "PPO": "#865c3d",
}
# [P] Table I: method, excess cost (%), time per weekly decision; decision times follow
# the 2026-10-27 manuscript (~/Workspace/TSGDR-2026 New/main.tex, Table I), in wall-clock hours.
HYDRO = [
    ("TS-DDR", .15, "0.03 s"), ("SDDP-DC-AC", .35, "1.6 h re-solve"),
    ("SAC", 2.42, "0.03 s"), ("REINFORCE", 16.53, "0.03 s"),
    ("TD3", 16.55, "0.03 s"), ("PPO", 16.81, "0.03 s"),
    ("TS-LDR", 17.46, "0.03 s"),
]
# [T] Section 4.7: norm (% of full) and cosine, in horizon order 8, 126 weeks.
CREDIT = ([26.5, 5.9], [.879, .673])
# [P] Table II: excess cost (%) and unserved energy (MWh), same method order.
BATTERY_METHODS = ["TS-DDR", "SDDP-DC-AC", "TS-LDR", "SDDP-SOC-AC"]
BATTERY = [
    ("Without ramp limits", "159-dimensional state",
     [.31, .70, 4.55, 61.98], [0, 0, 21.27, 494.23]),
    ("With ramp limits", "241-dimensional state",
     [2.37, 4.76, 112.09, 101.99], [0, 36.47, 796.43, 875.00]),
]
# [S] Table S3; [T] Section 4.8. Each panel has its own reference.
STRESS = [
    ("Scarcity invisible to the DC model", "Full-horizon AC reference",
     [1.52, 17.07], [4.8, 147.2], 20, [0, 5, 10, 15, 20]),
    ("Uncertain demand, 100 test paths", "Mean perfect-information AC cost",
     [7.4, 11.1], [18, 76], 12, [0, 4, 8, 12]),
]
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "svg.fonttype": "none", "svg.hashsalt": "decision-rules",
    "font.size": 12, "axes.labelsize": 12,
    "axes.edgecolor": LINE, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": INK, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#eceae4", "grid.linewidth": .8,
    "figure.dpi": 100,
})


def save(fig, name):
    path = OUT / f"decision-rules-{name}.svg"
    fig.savefig(path, transparent=False, facecolor="none",
                bbox_inches="tight", pad_inches=.12, metadata={"Date": None})
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def row_axes(ax, labels):
    y = np.arange(len(labels))[::-1]
    ax.set_yticks(y, labels)
    ax.set_ylim(-.6, len(labels) - .4)
    ax.tick_params(axis="y", length=0, pad=7)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_axisbelow(True)
    return y


def hydro(phone=False):
    fig, ax = plt.subplots(figsize=(4.4, 4.4) if phone else (8.4, 3.8))
    fig.subplots_adjust(left=.30 if phone else .21, right=.97 if phone else .73,
                        bottom=.18, top=.90)
    labels = [r[0] for r in HYDRO]
    y = row_axes(ax, labels)
    values = [r[1] for r in HYDRO]
    colors = [COLORS[r[0]] for r in HYDRO]
    ax.barh(y, values, color=colors, height=.58, zorder=2)
    # Mark the exact bar ends so the two near-reference policies remain visible.
    ax.scatter(values[:2], y[:2], c=colors[:2], s=42, zorder=3, clip_on=False)
    ax.set_xlim(0, 24)
    ticks = [0, 10, 20] if phone else [0, 5, 10, 15, 20]
    ax.set_xticks(ticks, [f"{v}%" for v in ticks])
    ax.set_xlabel("Mean AC cost above SDDP-SOC-AC", labelpad=10)
    for yi, (method, value, time) in zip(y, HYDRO):
        ax.text(value + .45, yi, f"+{value:.2f}%", va="center")
        if not phone:
            ax.text(1.08, yi, time, transform=ax.get_yaxis_transform(), va="center", color=MUTED)
    if not phone:
        ax.text(1.08, 1.08, "Per weekly decision", transform=ax.transAxes, color=MUTED)
    save(fig, "hydro-tall" if phone else "hydro")


def credit(phone=False):
    fig, axes = plt.subplots(2 if phone else 1, 1 if phone else 2,
                             figsize=(4.4, 4.5) if phone else (8.4, 2.7))
    fig.subplots_adjust(left=.27 if phone else .17, right=.95, bottom=.13 if phone else .24,
                        top=.90, hspace=.95, wspace=1.0)
    for i, (ax, values, top) in enumerate(zip(axes.flat, CREDIT, [100, 1])):
        y = row_axes(ax, ["8 weeks", "126 weeks"])
        ax.barh(y, values, color="#70777e", height=.53, zorder=2)
        ax.set_xlim(0, top * 1.15)
        ticks = [0, 50, 100] if i == 0 else [0, .5, 1]
        ax.set_xticks(ticks, [f"{v}%" for v in ticks] if i == 0 else ["0", "0.5", "1.0"])
        ax.set_title("Truncated gradient norm\n(% of full gradient)" if i == 0
                     else "Cosine with\nthe full gradient", loc="left", fontsize=12, pad=10)
        for yi, value in zip(y, values):
            ax.text(value + top * .025, yi,
                    f"{value:.1f}%" if i == 0 else f"{value:.3f}", va="center")
    save(fig, "credit-tall" if phone else "credit")


def battery(phone=False):
    fig, axes = plt.subplots(2 if phone else 1, 1 if phone else 2,
                             figsize=(4.4, 8.8) if phone else (9.2, 3.9))
    fig.subplots_adjust(left=.31 if phone else .15, right=.74 if phone else .87,
                        top=.83 if phone else .75, bottom=.11 if phone else .20,
                        hspace=.93, wspace=1.45)
    for ax, (title, dimension, excess, shed) in zip(axes.flat, BATTERY):
        y = row_axes(ax, BATTERY_METHODS)
        # A dot encodes a positive value on the log axis. Neutral leaders only
        # connect each row to the axis; their length does not encode a bar value.
        ax.set_xscale("log")
        ax.set_xlim(.1, 200)
        ax.hlines(y, .1, excess, color=LINE, linewidth=1, zorder=1)
        ax.scatter(excess, y, c=[COLORS[m] for m in BATTERY_METHODS], s=48, zorder=3)
        ax.set_xticks([.1, 1, 10, 100], ["0.1%", "1%", "10%", "100%"])
        ax.minorticks_off()
        ax.set_title(f"{title}\n{dimension}", loc="left", fontsize=12, pad=38)
        ax.text(1.07, 1.025, "Cost excess\nEnergy shed", transform=ax.transAxes,
                fontsize=12, color=MUTED, va="bottom")
        for yi, v, s in zip(y, excess, shed):
            ax.text(1.07, yi, f"{v:.2f}%\n{s:g} MWh", transform=ax.get_yaxis_transform(),
                    va="center", linespacing=1.35, fontsize=12)
        ax.set_xlabel("Excess AC cost · log scale", labelpad=10)
    save(fig, "battery-tall" if phone else "battery")


def stress(phone=False):
    # Separate panels vertically and label both references: these are different
    # experiments, so a shared comparison axis would give the wrong impression.
    fig, axes = plt.subplots(2, 1, figsize=(4.4, 5.7) if phone else (8.4, 5.5))
    fig.subplots_adjust(left=.31 if phone else .18, right=.73 if phone else .79,
                        top=.82, bottom=.10, hspace=1.9)
    fig.add_artist(plt.Line2D([.06, .98], [.49, .49], transform=fig.transFigure,
                              color=LINE, linewidth=1))
    for i, (ax, (title, reference, excess, shed, top, ticks)) in enumerate(zip(axes, STRESS)):
        y = row_axes(ax, ["TS-DDR", "SDDP-DC-AC"])
        ax.set_facecolor("#f2f6f8" if i else "white")
        ax.barh(y, excess, color=[COLORS[m] for m in ["TS-DDR", "SDDP-DC-AC"]], height=.52)
        ax.set_xlim(0, top)
        ax.set_xticks(ticks, [f"{v}%" for v in ticks])
        ax.set_xlabel("AC cost above reference", labelpad=10)
        ax.set_title(f"{title}\nReference: {reference}" if not phone else
                     f"{title}\nReference: " + ("Full-horizon AC" if i == 0 else "Mean perfect-information AC"),
                     loc="left", fontsize=12, pad=35)
        ax.text(1.07, 1.05, "Cost excess\nEnergy shed", transform=ax.transAxes,
                va="bottom", color=MUTED)
        for yi, v, s in zip(y, excess, shed):
            ax.text(1.07, yi, f"{v:g}%\n{s:g} MWh", transform=ax.get_yaxis_transform(),
                    va="center", linespacing=1.35)
    save(fig, "stress-tall" if phone else "stress")


def author_figures():
    """Re-export source artwork with larger original vector labels.

    Only label scale/placement and the media crop change. Robot geometry,
    force arrows, frames and the step are preserved. Original glyph outlines
    keep the author's typography, including the subscripts.
    """
    import subprocess
    import tempfile
    import xml.etree.ElementTree as ET
    from PIL import Image
    proposal = Path.home() / "Workspace/PhD Proposal Report"
    svg_ns, xlink = "http://www.w3.org/2000/svg", "http://www.w3.org/1999/xlink"
    # Each tuple identifies a consecutive source label's glyphs, its original
    # baseline anchor and its new baseline. Subscript offsets scale together.
    stance = [
        (2, (578.25033, 451.096334), (578, 475)),  # p_i
        (2, (597.279548, 381.191151), (603, 381)),  # f_i
        (2, (540.581061, 274.898951), (550, 300)),  # q_j
        (1, (76.326028, 386.110608), (90, 380)),   # world y
        (1, (91.423672, 426.973033), (105, 420)),  # world x
        (1, (33.867024, 373.717169), (20, 350)),   # world z
        (1, (12.842084, 389.223935), (-25, 395)),  # W
        (1, (411.657363, 35.761458), (430, 15)),   # body y
        (1, (426.096418, 73.350898), (455, 43)),   # body x
        (1, (369.178402, 23.358040), (345, 2)),    # body z
        (1, (352.384394, 68.690885), (320, 75)),   # B
    ]
    swing = [
        (2, (488.129675, 290.951215), (500, 285)), # p_t
        (4, (601.667071, 173.153653), (600, 160)), # p_{t+k}
    ]
    # Source body spans measured in the PDF's coordinate system; both bodies
    # render at 960 pixels in the resulting 1440-pixel canvases.
    specs = [
        ("stance", "go2_representation.pdf", stance, (-45, -25, 800, 530), 600),
        ("swing", "go2_representation_step.pdf", swing, (-5, -25, 725, 390), 470),
    ]
    with tempfile.TemporaryDirectory(prefix="decision-rules-") as tmp:
        for name, source, labels, crop, body_width in specs:
            vector = Path(tmp) / f"{name}.svg"
            subprocess.run(["pdftocairo", "-svg", str(proposal / source), str(vector)], check=True)
            tree = ET.parse(vector)
            root = tree.getroot()
            groups = [g for g in root if g.tag == f"{{{svg_ns}}}g"
                      and any(u.get(f"{{{xlink}}}href", "").startswith("#glyph-") for u in g)]
            count = 0
            for n, (x, y), (tx, ty) in labels:
                for group in groups[count:count + n]:
                    group.set("transform", f"translate({tx} {ty}) scale(2.8) translate({-x} {-y})")
                count += n
            # The final three-dot continuation mark in the swing source is
            # punctuation in the artwork, rather than a mathematical label.
            assert len(groups) == count + (1 if name == "swing" else 0)
            x, y, w, h = crop
            root.set("viewBox", f"{x} {y} {w} {h}")
            root.set("width", str(w)); root.set("height", str(h))
            tree.write(vector, encoding="unicode")
            png = Path(tmp) / f"{name}.png"
            subprocess.run(["rsvg-convert", "-w", str(round(w * 960 / body_width)),
                            str(vector), "-o", str(png)], check=True)
            art = Image.open(png).convert("RGBA")
            canvas = Image.new("RGBA", (1440, art.height + 32), "white")
            canvas.alpha_composite(art, ((1440 - art.width) // 2, 16))
            canvas.convert("RGB").save(OUT / f"decision-rules-contact-{name}.webp", lossless=True)


if __name__ == "__main__":
    for phone in (False, True):
        hydro(phone)
        credit(phone)
        battery(phone)
        stress(phone)
    author_figures()
