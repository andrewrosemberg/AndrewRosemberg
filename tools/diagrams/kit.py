#!/usr/bin/env python3
"""Primitives for method diagrams in the visual identity of the Sobolev / DC2AC / TS-DDR paper figures.

Every style string below is copied from the draw.io source embedded in the paper PDFs
(diagram_sobolev.pdf, the DC2AC diagram.pdf) or measured from diagram_qualify_tsddr.pdf;
README.md documents each one. A diagram is a short script that imports this module:

    from kit import Diagram
    d = Diagram()
    d.frame(200, 480, 610, 770)
    d.lane_title(200, 480, 'Training')
    d.box('a', 250, 530, 60, 30, r'\\mathbf{x}^*', role='data')
    ...
    d.write('tools/diagrams/name.drawio')

Coordinates are draw.io px on the 10 px grid of the originals (5 px where they used it).
Labels are TeX (MathJax, typeset by draw.io); plain words go in \\text{...}.
"""
import html
import itertools
import os

# ---------------------------------------------------------------- styles (verbatim)
FONT = 'fontFamily=Arial;'  # see README "Fonts": reproduces the export server's Helvetica->Arial
ROLE = {
    # role: (fillColor, strokeColor) -- draw.io default swatches used by the originals
    'data': ('#ffe6cc', '#d79b00'),      # orange: data, stores, solver/ground-truth side
    'model': ('#dae8fc', '#6c8ebf'),     # blue: learned model and its outputs
    'output': ('#d5e8d4', '#82b366'),    # green: network output layer (and TS-DDR "reachable" map)
    'tool': ('#e1d5e7', '#9673a6'),      # purple: differentiation tools (AD, DiffOpt)
    'loss': ('#f8cecc', '#b85450'),      # red: loss / gradient objective
    'sheet': ('#f5f5f5', '#dedede'),     # grey: stacked sheets behind a per-stage network (TS-DDR)
}
BOX = 'rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;'
RBOX = 'rounded=1;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;'
STORE = 'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=%s;strokeColor=%s;'
NODE = 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=%s;strokeColor=%s;'
SYNAPSE = ('endArrow=none;html=1;rounded=0;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;'
           'strokeWidth=0.25;fillColor=#dae8fc;strokeColor=#6c8ebf;')
TEXT = 'text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;'
TEXT_LEFT = 'text;whiteSpace=wrap;'   # non-HTML text cell, left/top: the \begin{aligned} problem block
BRACE = ('shape=curlyBracket;whiteSpace=wrap;html=1;rounded=1;flipH=1;labelPosition=right;verticalLabelPosition=middle;'
         'align=left;verticalAlign=middle;rotation=90;')
LINE = 'endArrow=none;html=1;rounded=0;'                    # lane frame
SPLIT = 'endArrow=none;dashed=1;html=1;rounded=0;'          # lane split
ORTHO = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
EDGE = {
    'value': ORTHO,                                                            # black value flow
    'grad': ORTHO + 'strokeColor=#B85450;dashed=1;',                           # red dashed gradient return (Sobolev)
    'grad-solid': ORTHO + 'fillColor=#f8cecc;strokeColor=#b85450;',            # red solid gradient return (DC2AC)
    'tool': ORTHO + 'fillColor=#e1d5e7;strokeColor=#9673a6;dashed=1;',         # purple dashed tool link, arrow
    'tool-tail': ORTHO + 'dashed=1;endArrow=none;startFill=0;fillColor=#e1d5e7;strokeColor=#9673a6;',  # no arrow
    'straight': 'endArrow=classic;html=1;rounded=0;',                          # straight arrow (no routing)
}


def esc(s):
    return html.escape(s, quote=True)


class Page:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.ids = itertools.count(1)

    def _id(self, cid):
        return cid or '_k%d' % next(self.ids)

    def add(self, xml):
        self.cells.append(xml)

    # -------------------------------------------------------------- vertices
    def vertex(self, cid, x, y, w, h, style, value='', parent='1'):
        cid = self._id(cid)
        if value and FONT not in style:
            style += FONT
        self.add('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="%s">'
                 '<mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry" /></mxCell>'
                 % (cid, esc(value), style, parent, x, y, w, h))
        return cid

    def box(self, cid, x, y, w, h, tex, role='data', rounded=None):
        """Process box. Square corners for data/model boxes, rounded for tool and loss boxes."""
        if rounded is None:
            rounded = role in ('tool', 'loss')
        return self.vertex(cid, x, y, w, h, (RBOX if rounded else BOX) % ROLE[role], math(tex))

    def store(self, cid, x, y, w, h, tex, role='data'):
        """Data store (cylinder3, cap 15 px). Originals: 40x60 and 60x80."""
        return self.vertex(cid, x, y, w, h, STORE % ROLE[role], '<div>%s</div>' % math(tex) if tex else '')

    def text(self, cid, x, y, w, h, tex, left=False):
        """Free math label (no box). TeX in display mode; centred unless left=True."""
        style = TEXT if not left else 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;'
        return self.vertex(cid, x, y, w, h, style, math(tex))

    def block(self, cid, x, y, w, h, tex):
        """Left-aligned multi-line TeX (e.g. \\begin{aligned}...\\end{aligned}) as in the g-box of Sobolev."""
        return self.vertex(cid, x, y, w, h, TEXT_LEFT, tex)

    def lane_title(self, x, y, word, inset=False):
        """Lane title in the top-left corner of a lane whose corner is (x, y)."""
        if inset:  # left-aligned, 13 px in from the lane edge, so a line can pass along the edge
            return self.vertex(None, x + 13, y, 150, 30, 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;',
                               '$$\\text{%s}$$' % word)
        if word == 'Dataset':  # keeps the word's left edge where "Offline" began (README)
            return self.vertex(None, x + 3.3, y, 60, 30, TEXT, '$$\\text{Dataset}$$')
        return self.vertex(None, x, y, 70, 30, TEXT, '<div>$$\\text{%s}$$</div>' % word)

    def brace(self, x0, x1, ytop, depth=10):
        """Horizontal curly brace under the span [x0, x1], tip pointing down; label it with text()."""
        span = x1 - x0
        cx, cy = (x0 + x1) / 2.0, ytop + depth / 2.0
        return self.vertex(None, round(cx - depth / 2.0, 2), round(cy - span / 2.0, 2), depth, span, BRACE)

    def network(self, x, y, output='output', prefix=None):
        """Ellipse-grid network glyph exactly as in the originals: input column of 4 nodes,
        five columns of 8 nodes (10 px), last column green (output='output') or blue
        (output='model', as in DC2AC); 32 synapses of 0.25 px. Occupies (x, y)-(x+70, y+80);
        the input column is centred vertically (inputs at x..x+10, y+20..y+60)."""
        p = prefix or 'n%d' % next(self.ids)
        ins = []
        for i in range(4):
            ins.append(self.vertex('%s-i%d' % (p, i), x, y + 20 + 10 * i, 10, 10, NODE % ROLE['model']))
        first = []
        for c in range(5):
            role = output if c == 4 else 'model'
            for r in range(8):
                cid = self.vertex('%s-h%d-%d' % (p, c, r), x + 20 + 10 * c, y + 10 * r, 10, 10, NODE % ROLE[role])
                if c == 0:
                    first.append(cid)
        for a in ins:
            for b in first:
                self.add('<mxCell id="%s-s-%s-%s" value="" style="%s" edge="1" parent="1" source="%s" target="%s">'
                         '<mxGeometry relative="1" as="geometry" /></mxCell>'
                         % (p, a.split('-')[-1], b.split('-')[-1], SYNAPSE, a, b))
        return p

    def import_page(self, path, drop=(), relabel=None, geometry=None, restyle=None):
        """Copy every cell of page 1 of an existing .drawio (e.g. sobolev.drawio) into this page.
        drop: ids to delete (edges touching them are deleted too); relabel: id -> new value (raw);
        geometry: id -> (x, y, w, h); restyle: id -> style string."""
        import xml.etree.ElementTree as ET
        relabel, geometry, restyle = relabel or {}, geometry or {}, restyle or {}
        model = next(ET.parse(path).getroot().iter('mxGraphModel'))
        drop = set(drop)
        for c in model.iter('mxCell'):
            if c.get('id') in ('0', '1'):
                continue
            if c.get('id') in drop or c.get('source') in drop or c.get('target') in drop:
                continue
            if c.get('id') in relabel:
                c.set('value', relabel[c.get('id')])
            if c.get('id') in restyle:
                c.set('style', restyle[c.get('id')])
            if c.get('id') in geometry:
                g = c.find('mxGeometry')
                for k, v in zip(('x', 'y', 'width', 'height'), geometry[c.get('id')]):
                    g.set(k, '%g' % v)
            self.add(ET.tostring(c, encoding='unicode').strip())

    # ----------------------------------------------------------------- edges
    def line(self, x0, y0, x1, y1, dashed=False):
        """Frame line or lane split (dashed=True). Originals draw the frame as four lines."""
        self.add('<mxCell id="%s" value="" style="%s" edge="1" parent="1"><mxGeometry width="50" height="50" '
                 'relative="1" as="geometry"><mxPoint x="%g" y="%g" as="sourcePoint" />'
                 '<mxPoint x="%g" y="%g" as="targetPoint" /></mxGeometry></mxCell>'
                 % (self._id(None), SPLIT if dashed else LINE, x0, y0, x1, y1))

    def frame(self, x0, y0, x1, y1):
        self.line(x0, y0, x1, y0)
        self.line(x1, y1, x1, y0)
        self.line(x1, y1, x0, y1)
        self.line(x0, y1, x0, y0)

    def edge(self, src, tgt, kind='value', points=(), exit=None, entry=None, src_pt=None, tgt_pt=None, extra=''):
        """Connector. exit/entry = (fx, fy) port fractions; points = waypoints; src_pt/tgt_pt = free ends."""
        style = EDGE[kind]
        if exit:
            style += 'exitX=%g;exitY=%g;exitDx=0;exitDy=0;' % exit
        if entry:
            style += 'entryX=%g;entryY=%g;entryDx=0;entryDy=0;' % entry
        style += extra
        geo = ''
        if src_pt:
            geo += '<mxPoint x="%g" y="%g" as="sourcePoint" />' % src_pt
        if tgt_pt:
            geo += '<mxPoint x="%g" y="%g" as="targetPoint" />' % tgt_pt
        if points:
            geo += '<Array as="points">%s</Array>' % ''.join('<mxPoint x="%g" y="%g" />' % p for p in points)
        attrs = (' source="%s"' % src if src else '') + (' target="%s"' % tgt if tgt else '')
        self.add('<mxCell id="%s" value="" style="%s" edge="1" parent="1"%s><mxGeometry relative="1" as="geometry">'
                 '%s</mxGeometry></mxCell>' % (self._id(None), style, attrs, geo))


def math(tex):
    """Wrap TeX for a draw.io math label ($$...$$; HTML-escaped later)."""
    if tex is None or tex == '':
        return ''
    if tex.startswith('$$') or tex.startswith('<') or tex.startswith('\\begin'):
        return tex
    return '$$%s$$' % tex


class Diagram:
    def __init__(self):
        self.pages = []

    def page(self, name='Page-1'):
        p = Page(name)
        self.pages.append(p)
        return p

    def write(self, path):
        out = ['<mxfile host="drawio" version="32.6.1">']
        for i, p in enumerate(self.pages):
            out.append('  <diagram name="%s" id="p%d">' % (esc(p.name), i + 1))
            out.append('    <mxGraphModel dx="900" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                       'arrows="1" fold="1" page="1" pageScale="1" pageWidth="900" pageHeight="1600" math="1" shadow="0">')
            out.append('      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />')
            out.extend('        ' + c for c in p.cells)
            out.append('      </root>\n    </mxGraphModel>\n  </diagram>')
        out.append('</mxfile>\n')
        with open(path, 'w') as f:
            f.write('\n'.join(out))
        print('wrote', os.path.relpath(path))
