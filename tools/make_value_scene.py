"""Continuation-value scene: the state stored now (large photograph, left) branches into the scenarios
that may follow (three photographs, right), each with its cost (amber bar). The value of the stored state
(violet outline under the first photograph) holds each scenario's cost weighed by its probability. Same palette
and tree grammar as the Policies composites: paper background, violet = value, amber = scenario costs.

    python tools/make_value_scene.py OUT ROOT SCEN1 SCEN2 SCEN3 [COST1 COST2 COST3]"""
import sys
from PIL import Image, ImageDraw

BG, VIOLET, AMBER = (248, 247, 243), (117, 81, 168), (225, 159, 65)
W, H, SS = 1200, 900, 3

def photo(path, w, h):
    im = Image.open(path).convert('RGB'); iw, ih = im.size
    if iw / ih > w / h: nw = round(ih * w / h); im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else: nh = round(iw * h / w); im = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

def paste(c, im, x, y, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    c.paste(im, (x, y), m)

def curve(d, p0, p1, width, fill, n=60):
    (x0, y0), (x1, y1) = p0, p1
    pts = []
    for i in range(n + 1):                                   # cubic with horizontal tangents
        t = i / n; a, b, cc, dd = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        xm = (x0 + x1) / 2
        pts.append((a * x0 + b * xm + cc * xm + dd * x1, a * y0 + b * y0 + cc * y1 + dd * y1))
    d.line(pts, fill=fill, width=width, joint='curve')
    for p in (pts[0], pts[-1]): d.ellipse([p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2], fill=fill)

def main(out, root, scen, costs):
    s = lambda v: int(round(v * SS))
    c = Image.new('RGB', (W * SS, H * SS), BG); d = ImageDraw.Draw(c)
    rw, rh, rx, ry = 560, 420, 24, 200                       # the state stored now
    bw, bh, bx = 300, 225, 735                               # the scenarios that may follow
    bys = [30, 337, 645]
    node = (rx + rw + 52, ry + rh / 2)
    d.line([s(rx + rw - 2), s(node[1]), s(node[0]), s(node[1])], fill=VIOLET, width=s(10))
    for by in bys:
        curve(d, (s(node[0]), s(node[1])), (s(bx + 2), s(by + bh / 2)), s(9), AMBER)
    d.ellipse([s(node[0] - 15), s(node[1] - 15), s(node[0] + 15), s(node[1] + 15)], fill=VIOLET, outline=(255, 255, 255), width=s(4))
    paste(c, photo(root, s(rw), s(rh)), s(rx), s(ry), s(16))
    for by, p in zip(bys, scen):
        paste(c, photo(p, s(bw), s(bh)), s(bx), s(by), s(12))
    unit = 130 / max(costs)                                  # cost bars, right of each scenario
    for by, L in zip(bys, costs):
        y = by + bh / 2
        d.rounded_rectangle([s(bx + bw + 14), s(y - 20), s(bx + bw + 14 + L * unit), s(y + 20)], s(10), fill=AMBER)
    # value of the stored state: each scenario's cost weighed by its probability (equal here), in a violet outline
    x, y, g, pad = rx + 8, ry + rh + 34, 6, 8
    for L in costs:
        w = L * unit / len(costs)
        d.rounded_rectangle([s(x), s(y), s(x + w), s(y + 40)], s(8), fill=AMBER); x += w + g
    d.rounded_rectangle([s(rx + 8 - pad), s(y - pad), s(x - g + pad), s(y + 40 + pad)], s(14), outline=VIOLET, width=s(6))
    c.resize((W, H), Image.LANCZOS).save(out, 'PNG')

if __name__ == '__main__':
    out, root, a, b, cc, *L = sys.argv[1:]
    main(out, root, [a, b, cc], [float(v) for v in L] if L else [1, 3, 6])
