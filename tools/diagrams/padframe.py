#!/usr/bin/env python3
"""Copy a .drawio file adding, on every page, an invisible cell 20 px larger than the content.

    python3 tools/diagrams/padframe.py in.drawio out.drawio

draw.io's cropped PDF export puts the page edge exactly on the outermost geometry, so the
outer half of a frame line's stroke is clipped. The invisible frame moves the page edge
out; pdf2svg.py then crops the SVG to the real ink plus its own margin.
"""
import math
import sys
import xml.etree.ElementTree as ET

PAD = 20


def bounds(model):
    cells = {c.get('id'): c for c in model.iter('mxCell')}
    xs, ys = [], []

    def origin(c):
        x = y = 0.0
        while c is not None and c.get('parent') not in (None, '0', '1'):
            c = cells.get(c.get('parent'))
            g = c.find('mxGeometry') if c is not None else None
            if g is not None:
                x += float(g.get('x', 0))
                y += float(g.get('y', 0))
        return x, y

    for c in model.iter('mxCell'):
        g = c.find('mxGeometry')
        if g is None:
            continue
        ox, oy = origin(c)
        if c.get('vertex') == '1':
            x, y = float(g.get('x', 0)) + ox, float(g.get('y', 0)) + oy
            w, h = float(g.get('width', 0)), float(g.get('height', 0))
            r = max(w, h) / 2.0 if g is not None and 'rotation=' in (c.get('style') or '') else 0
            cx, cy = x + w / 2.0, y + h / 2.0
            hw, hh = (r, r) if r else (w / 2.0, h / 2.0)
            xs += [cx - hw, cx + hw]
            ys += [cy - hh, cy + hh]
        for p in g.iter('mxPoint'):
            xs.append(float(p.get('x', 0)) + ox)
            ys.append(float(p.get('y', 0)) + oy)
    return min(xs), min(ys), max(xs), max(ys)


def main():
    src, dst = sys.argv[1:3]
    tree = ET.parse(src)
    for model in tree.getroot().iter('mxGraphModel'):
        x0, y0, x1, y1 = bounds(model)
        root = model.find('root')
        cell = ET.SubElement(root, 'mxCell', {'id': 'export-pad-frame', 'value': '', 'vertex': '1', 'parent': '1',
                                              'style': 'rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;'})
        ET.SubElement(cell, 'mxGeometry', {'x': '%g' % math.floor(x0 - PAD), 'y': '%g' % math.floor(y0 - PAD),
                                           'width': '%g' % math.ceil(x1 - x0 + 2 * PAD),
                                           'height': '%g' % math.ceil(y1 - y0 + 2 * PAD), 'as': 'geometry'})
        root.remove(cell)
        root.insert(2, cell)  # behind everything
    tree.write(dst)


if __name__ == '__main__':
    main()
