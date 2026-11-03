#!/usr/bin/env python3
"""Turn a draw.io PDF export into a compact, self-contained SVG for the web.

    python3 tools/diagrams/pdf2svg.py in.pdf out.svg [--pad 6]

Pipeline: `pdftocairo -svg` outlines every glyph (MathJax formulas included) as a path,
so the result needs no fonts, no MathJax and no foreignObject, and renders the same in
any browser as an <img>. This script then
  * drops the invisible text layer draw.io adds to PDFs (fill-opacity 0.0039) and the
    font glyphs only it used, and the PDF page background;
  * maps everything back to draw.io coordinates (1 user unit = 1 draw.io px), so shape
    paths carry no transform and the numbers in the SVG are the numbers in the .drawio;
  * stores each repeated MathJax glyph outline once (<use>);
  * crops to the ink bounding box plus a uniform margin of PAD draw.io px, with one
    white rectangle underneath (the paper-figure background);
  * sets width/height to the diagram's own size in px;
  * rounds coordinates to about 0.03 draw.io px and writes colours as hex.
Only stdlib Python plus the poppler and ImageMagick command-line tools are used.
"""
import argparse
import collections
import math
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
XL = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', XL)
Q = lambda t: '{%s}%s' % (SVG, t)
HREF = '{%s}href' % XL
NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')
MATRIX = re.compile(r'matrix\(([-\d.e]+),\s*([-\d.e]+),\s*([-\d.e]+),\s*([-\d.e]+),\s*([-\d.e]+),\s*([-\d.e]+)\)')
DEFAULTS = {'fill-rule': 'nonzero', 'fill-opacity': '1', 'stroke-opacity': '1',
            'stroke-linecap': 'butt', 'stroke-linejoin': 'miter', 'stroke-width': '1'}
TOL = 0.03  # coordinate rounding tolerance, draw.io px


def fmt(v, decimals):
    s = ('%.*f' % (decimals, v)) if decimals > 0 else str(int(round(v)))
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def hexcolor(v):
    m = re.fullmatch(r'rgb\(([\d.]+)%,\s*([\d.]+)%,\s*([\d.]+)%\)', v.strip())
    if not m:
        return v
    return '#' + ''.join('%02x' % int(round(float(c) * 2.55)) for c in m.groups())


RECT = re.compile(r'M (\S+) (\S+) L (\S+) \2 L \3 (\S+) L \1 \4 (?:Z(?: M \1 \2)?)?')
RECTV = re.compile(r'M (\S+) (\S+) L \1 (\S+) L (\S+) \3 L \4 \2 (?:Z(?: M \1 \2)?)?')


def minify(d, filled_only=False):
    """Shorter path data: axis-aligned rectangles (Chrome fills each dash as one) become
    M x y h w v h h -w z, and spaces next to command letters go."""
    d = re.sub(r'\s+', ' ', d).strip()
    num = lambda v: fmt(v, 3)
    if filled_only:  # closing an open rectangle changes nothing for a fill without stroke
        d = RECT.sub(lambda m: 'M %s %s h%s v%s h%s z ' % (m.group(1), m.group(2),
                     num(float(m.group(3)) - float(m.group(1))), num(float(m.group(4)) - float(m.group(2))),
                     num(float(m.group(1)) - float(m.group(3)))), d + ' ')
        d = RECTV.sub(lambda m: 'M %s %s v%s h%s v%s z ' % (m.group(1), m.group(2),
                      num(float(m.group(3)) - float(m.group(2))), num(float(m.group(4)) - float(m.group(1))),
                      num(float(m.group(2)) - float(m.group(3)))), d + ' ')
    d = re.sub(r' ?([MLCZHVmlchvz]) ?', r'\1', d.strip())
    return d.replace(' -', '-')


def ink_bbox(pdf, dpi=288):
    """Non-white bounding box of the rendered PDF page, in PDF points."""
    with tempfile.TemporaryDirectory() as d:
        base = os.path.join(d, 'r')
        subprocess.run(['pdftocairo', '-png', '-r', str(dpi), '-singlefile', pdf, base], check=True)
        out = subprocess.run(['magick', base + '.png', '-fuzz', '1%', '-format', '%@', 'info:'],
                             capture_output=True, text=True, check=True).stdout
    w, h, x, y = map(int, re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', out).groups())
    k = 72.0 / dpi
    return x * k, y * k, w * k, h * k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('svg')
    ap.add_argument('--pad', type=float, default=6.0, help='margin around the ink, in draw.io px')
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as d:
        raw = os.path.join(d, 'raw.svg')
        subprocess.run(['pdftocairo', '-svg', a.pdf, raw], check=True)
        tree = ET.parse(raw)
    root = tree.getroot()
    parent = {c: p for p in root.iter() for c in p}

    # 1. Invisible text layer, PDF page background, unused definitions.
    for g in list(root.iter(Q('g'))):
        if g.get('fill-opacity') and float(g.get('fill-opacity')) < 0.01 and all(c.tag == Q('use') for c in g):
            parent[g].remove(g)
    for g in list(root.iter(Q('g'))):
        if g.get('clip-path') and len(g) == 1 and g[0].tag == Q('path') and \
                hexcolor(g[0].get('fill', '')) == '#ffffff' and not g[0].get('stroke'):
            parent[g].remove(g)
    while True:
        used = set(re.findall(r'#([\w.-]+)', ET.tostring(root, encoding='unicode')))
        dead = [e for e in root.iter() if e.get('id') and e.get('id') not in used and e in parent]
        if not dead:
            break
        for e in dead:
            parent[e].remove(e)
    for defs in list(root.iter(Q('defs'))):
        for g in list(defs):
            if len(g) == 0 and not g.get('id'):
                defs.remove(g)
        if len(defs) == 0:
            parent[defs].remove(defs)
    if any(e.tag in (Q('use'), Q('image'), Q('text')) for e in root.iter()):
        raise SystemExit('unexpected <use>/<image>/<text> left in the PDF conversion')

    # 2. Back to draw.io coordinates: the most common transform maps draw.io px to pt.
    mats = collections.Counter(e.get('transform') for e in root.iter(Q('path')) if e.get('transform'))
    main_tr = max((t for t in mats if abs(float(MATRIX.match(t).group(1))) > 0.1), key=lambda t: mats[t])
    s, _, _, _, tx, ty = map(float, MATRIX.match(main_tr).groups())
    for e in root.iter(Q('path')):
        tr = e.get('transform')
        if tr is None:
            # Already in page points (Chrome's PDF backend fills dashes as polygons):
            # map the absolute coordinate pairs into draw.io px.
            toks = re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?', e.get('d'))
            if any(t.isalpha() and t not in 'MLCZ' for t in toks):
                raise SystemExit('unexpected path command in ' + e.get('d')[:80])
            vals, i = [], 0
            for t in toks:
                if t.isalpha():
                    vals.append(t)
                else:
                    vals.append(repr(((float(t) - (tx if i % 2 == 0 else ty)) / s)))
                    i += 1
            e.set('d', ' '.join(vals))
            tr = 'matrix(%r, 0, 0, %r, %r, %r)' % (s, s, tx, ty)
        A, B, C, D, E, F = map(float, MATRIX.match(tr).groups())
        A, B, C, D, E, F = A / s, B / s, C / s, D / s, (E - tx) / s, (F - ty) / s
        if max(abs(A - 1), abs(B), abs(C), abs(D - 1), abs(E), abs(F)) < 1e-6:
            e.attrib.pop('transform', None)
            local = 1.0
        else:
            e.set('transform', 'matrix(%.5g %.5g %.5g %.5g %s %s)' % (A, B, C, D, fmt(E, 2), fmt(F, 2)))
            local = math.hypot(A, B)
        dec = max(0, math.ceil(-math.log10(TOL / local)))
        e.set('d', minify(NUM.sub(lambda m: fmt(float(m.group(0)), dec), e.get('d')),
                          filled_only=e.get('stroke') in (None, 'none') and e.get('fill') not in (None, 'none')))
        for k in list(e.attrib):
            v = e.attrib[k]
            if DEFAULTS.get(k) == v:
                del e.attrib[k]
            elif k in ('fill', 'stroke'):
                e.attrib[k] = hexcolor(v)
            elif k == 'stroke-width' and local < 0.1:
                e.attrib[k] = fmt(float(v), 1)   # MathJax glyph halo, in glyph units
            elif k == 'stroke-dasharray':
                e.attrib[k] = NUM.sub(lambda m: fmt(float(m.group(0)), 3), v)
        if e.get('stroke-miterlimit') == '10':
            del e.attrib['stroke-miterlimit']   # set once on the root

    # 2b. draw.io ellipses arrive as Bezier arcs: write them as <circle>/<ellipse>.
    for e in list(root.iter(Q('path'))):
        dd = re.sub(r'Z\s*M[^A-Za-z]*$', 'Z', e.get('d', '').strip())
        if e.get('transform') or dd.count('M') != 1 or not dd.startswith('M') or \
                re.search(r'[LHVhvlcSQTA]', dd) or dd.count('C') < 4:
            continue
        v = [float(t) for t in NUM.findall(dd)]
        xs, ys = v[0::2], v[1::2]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        rx, ry = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2
        on = [(xs[0], ys[0])] + [(xs[k], ys[k]) for k in range(3, len(xs), 3)]
        if rx < 0.5 or ry < 0.5 or (len(xs) - 1) % 3 or \
                any(abs(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 - 1) > 0.02 for x, y in on):
            continue
        attrs = {k: val for k, val in e.attrib.items() if k != 'd'}
        e.tag = Q('ellipse') if abs(rx - ry) > 0.01 else Q('circle')
        e.attrib.clear()
        e.attrib.update(attrs)
        e.set('cx', fmt(cx, 3))
        e.set('cy', fmt(cy, 3))
        if e.tag == Q('circle'):
            e.set('r', fmt((rx + ry) / 2, 3))
        else:
            e.set('rx', fmt(rx, 3))
            e.set('ry', fmt(ry, 3))

    # 3. Repeated glyph outlines -> one definition each.
    paths = [e for e in root.iter(Q('path')) if e.get('transform')]
    counts = collections.Counter(e.get('d') for e in paths)
    defs = ET.Element(Q('defs'))
    ids = {}
    for e in paths:
        d = e.get('d')
        if counts[d] < 2 or len(d) < 120:
            continue
        if d not in ids:
            ids[d] = 'g%d' % len(ids)
            ET.SubElement(defs, Q('path'), {'id': ids[d], 'd': d})
        e.tag = Q('use')
        del e.attrib['d']
        e.set(HREF, '#' + ids[d])

    # 3b. Runs of glyphs with identical paint share one <g> that carries the paint.
    for par in list(root.iter()):
        kids = list(par)
        i = 0
        while i < len(kids):
            k = kids[i]
            if k.tag != Q('use'):
                i += 1
                continue
            paint = {a: v for a, v in k.attrib.items() if a not in ('transform', HREF)}
            j = i
            while j + 1 < len(kids) and kids[j + 1].tag == Q('use') and \
                    {a: v for a, v in kids[j + 1].attrib.items() if a not in ('transform', HREF)} == paint:
                j += 1
            if j > i and paint:
                g = ET.Element(Q('g'), paint)
                pos = list(par).index(k)
                for u in kids[i:j + 1]:
                    par.remove(u)
                    for key in paint:
                        del u.attrib[key]
                    g.append(u)
                par.insert(pos, g)
            i = j + 1

    # 4. Crop to ink + margin, white paper underneath, intrinsic size in draw.io px.
    x, y, w, h = ink_bbox(a.pdf)
    vb = ((x - tx) / s - a.pad, (y - ty) / s - a.pad, w / s + 2 * a.pad, h / s + 2 * a.pad)
    for k in list(root.attrib):
        del root.attrib[k]
    root.set('width', fmt(vb[2], 1))
    root.set('height', fmt(vb[3], 1))
    root.set('viewBox', ' '.join(fmt(v, 2) for v in vb))
    root.set('stroke-miterlimit', '10')
    if any(e.get('mask') or e.get('filter') for e in root.iter()):
        raise SystemExit('masks or filters left in the PDF conversion')
    # MathJax's stretchy delimiters arrive as clipped pieces: keep those clip paths (already
    # mapped to draw.io coordinates above, like every other path).
    for c in list(root):
        if c.tag == Q('defs'):
            for cp in c.iter(Q('clipPath')):
                defs.append(cp)
            root.remove(c)
    root.insert(0, ET.Element(Q('rect'), {'x': fmt(vb[0], 2), 'y': fmt(vb[1], 2), 'width': fmt(vb[2], 2),
                                          'height': fmt(vb[3], 2), 'fill': '#ffffff'}))
    if len(defs):
        root.insert(0, defs)

    out = ET.tostring(root, encoding='unicode')
    out = re.sub(r'>\s+<', '><', out)
    with open(a.svg, 'w') as f:
        f.write(out + '\n')
    print('%s: %s x %s px, %.1f KB' % (a.svg, root.get('width'), root.get('height'), len(out) / 1024))


if __name__ == '__main__':
    main()
