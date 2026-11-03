# Generates the inline decomposition diagram (wide + stacked variants) using the site's dg-* classes.
rows = [
    ("Full horizon", "1 problem per path", 1, ["Reference: the full-horizon", "transcription"]),
    ("Windows of 24 stages", "4 problems · 3 boundaries", 4, ["Trained close to the", "full-horizon transcription"]),
    ("Windows of 6 stages", "16 problems · 15 boundaries", 16, ["Plateaued at a", "higher cost"]),
    ("Single stages", "96 problems · 95 boundaries", 96, ["No feasible policy within", "the training budget"]),
]
T = 96

def boxes(x0, width, y, h, K, gap):
    pitch = (width + gap) / K
    w = pitch - gap
    out = []
    for k in range(K):
        x = x0 + k * pitch
        rx = 6 if K == 1 else (3 if K <= 16 else 0.8)
        out.append(f'<g class="dg-box" data-part="recourse"><rect x="{x:.2f}" y="{y}" width="{w:.2f}" height="{h}" rx="{rx}"/></g>')
    return "".join(out)

def gap_for(K):
    return {1: 0, 4: 7, 16: 3.5, 96: 1.05}[K]

aria = ("Four ways of solving the penalized second stage of one 96-stage hydrothermal path, each drawn as a bar split into "
        "the optimization problems it solves: the full horizon as one problem; windows of 24 stages (4 problems); windows of 6 stages "
        "(16 problems); and single stages (96 problems). Preliminary outcomes: windows of 24 trained close to the full-horizon "
        "transcription, windows of 6 plateaued at a higher cost, and single stages did not reach a feasible policy within the training budget.")

# wide
W = 760
parts = [f'<svg class="dg dg-grid" viewBox="0 0 {W} 262" role="img" aria-label="{aria}" xmlns="http://www.w3.org/2000/svg">']
parts.append('<text class="dg-cap" x="0" y="14">Second stage solved as</text>')
parts.append('<text class="dg-cap" x="196" y="14">Horizon of 96 weekly stages</text>')
parts.append('<text class="dg-cap" x="560" y="14">Preliminary outcome</text>')
y = 32
for title, cap, K, res in rows:
    parts.append(f'<text class="dg-title" x="0" y="{y+17}">{title}</text>')
    parts.append(f'<text class="dg-cap" x="0" y="{y+35}">{cap}</text>')
    parts.append(boxes(196, 344, y + 6, 30, K, gap_for(K)))
    parts.append(f'<text class="dg-elab" x="560" y="{y+17}">{res[0]}</text>')
    parts.append(f'<text class="dg-elab" x="560" y="{y+33}">{res[1]}</text>')
    y += 58
parts.append('</svg>')
wide = "".join(parts)

# stacked
W2 = 360
parts = [f'<svg class="dg dg-stack" viewBox="0 0 {W2} 352" role="img" aria-label="{aria}" xmlns="http://www.w3.org/2000/svg">']
parts.append('<text class="dg-cap" x="0" y="13">Problems along one sampled path of 96 stages</text>')
y = 26
for title, cap, K, res in rows:
    parts.append(f'<text class="dg-title" x="0" y="{y+15}">{title}</text>')
    parts.append(f'<text class="dg-cap" x="{W2}" y="{y+15}" text-anchor="end">{cap.split(" · ")[0]}</text>')
    parts.append(boxes(0, W2, y + 23, 24, K, {1: 0, 4: 6, 16: 3, 96: 0.9}[K]))
    parts.append(f'<text class="dg-elab" x="0" y="{y+65}">{res[0]} {res[1]}</text>')
    y += 81
parts.append('</svg>')
stack = "".join(parts)

html = f'<div class="dg-wrap">{wide}{stack}</div>'
open(__file__.replace("make_decomp.py", "decomp_svg.html"), "w").write(html)
print(len(html))
