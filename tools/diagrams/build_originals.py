#!/usr/bin/env python3
"""Rebuild the two reference diagrams from the draw.io source embedded in the paper PDFs.

    python3 tools/diagrams/build_originals.py

Both paper figures were exported from app.diagrams.net with "include a copy of my
diagram", so the PDF /Subject field holds the URL-encoded <mxfile>. This script
extracts it (read-only; the paper repos are never touched) and writes

    tools/diagrams/sobolev-original.drawio   (gate A: diagram_sobolev.pdf)
    tools/diagrams/dc2ac-original.drawio     (gate B: diagram.pdf of the DC2AC paper)
    tools/diagrams/sobolev.drawio            (site version: "Offline" lane -> "Dataset")
    tools/diagrams/dc2ac.drawio              (site version: "Offline" lane -> "Dataset")

Edits applied to the embedded source, and why (all measured; see README.md, "Gate"):

1. fontFamily=Arial on every labelled vertex. The originals were rendered by the
   diagrams.net export server (HeadlessChrome on Windows), where the default label
   font "Helvetica" resolves to Arial. MathJax scales its glyphs to the ex-height of
   the surrounding font, so on macOS (real Helvetica) every formula came out 0.77 %
   larger. With Arial the math matches the originals glyph for glyph.
2. Sobolev only: the \\begin{aligned} label of the g-box moves 2.0 px left. draw.io 32
   (MathJax 4) insets that non-HTML label 2.0 px further right than draw.io 26 did.
3. Gate files only: an invisible "gate-page-frame" cell reproduces the page extent of
   the old export (its bounds came from the raw TeX source width, before typesetting),
   and dc2ac's "Training" label uses \\( \\) instead of $$ $$ so that MathJax 4's
   display-math margins do not enlarge the page. Neither changes a visible pixel.
4. Site files only: the lane label "Offline" becomes "Dataset" (the author's decision),
   in the same treatment ($$\\text{...}$$, upright Computer Modern, centred text cell).
   The cell is shifted so the word starts where "Offline" started (ink at x = 209.5).
"""
import os
import re
import subprocess
import sys
import urllib.parse
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
SOURCES = {
    'sobolev': os.path.join(HOME, 'Workspace/Sobolev-NEURIPS-Andrew-2026/diagram_sobolev.pdf'),
    'dc2ac': os.path.join(HOME, 'Workspace/diffopt_mlopt_policy/diagram.pdf'),
}
# Page extent of each original export, in diagram coordinates (x, y, w, h); solved
# numerically against the original PDF transform (see README.md, "Gate").
GATE_FRAME = {
    'sobolev': (153.0180, 458.0503, 486.9261, 333.0317),
    'dc2ac': (182.9587, 478.4450, 461.3950, 279.0940),
}
# x of the "Dataset" cell (originally x=200, width 60): puts the ink start at 209.5,
# where "Offline" started in both originals.
DATASET_X = 203.3


def embedded_mxfile(pdf):
    out = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, check=True).stdout
    m = re.search(r'^Subject:\s*(%3Cmxfile.*?)\n(?=[A-Z][A-Za-z ]+:)', out, re.S | re.M)
    if not m:
        sys.exit('no embedded diagram in ' + pdf)
    raw = m.group(1).replace('\\(', '(').replace('\\)', ')')
    s = urllib.parse.unquote(raw)
    xml.dom.minidom.parseString(s)  # must be well-formed
    assert s.rstrip().endswith('</mxfile>')
    return s


def add_arial(s):
    def fix(m):
        cell = m.group(0)
        if 'edge="1"' in cell or 'value=""' in cell or 'value=' not in cell or 'fontFamily=' in cell:
            return cell
        return re.sub(r'style="([^"]*)"',
                      lambda mm: 'style="%s%sfontFamily=Arial;"' % (mm.group(1), '' if mm.group(1).endswith(';') else ';'),
                      cell, count=1)
    return re.sub(r'<mxCell [^>]*>', fix, s)


def replace_once(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)


def add_frame(s, box):
    frame = ('<mxCell id="gate-page-frame" value="" style="rounded=0;whiteSpace=wrap;html=1;'
             'fillColor=none;strokeColor=none;" vertex="1" parent="1">'
             '<mxGeometry x="%.4f" y="%.4f" width="%.4f" height="%.4f" as="geometry" /></mxCell>' % box)
    return replace_once(s, '<mxCell id="1" parent="0" />', '<mxCell id="1" parent="0" />\n        ' + frame)


def dataset(s):
    s = replace_once(s, 'value="$$\\text{Offline}$$"', 'value="$$\\text{Dataset}$$"')
    i = s.index('value="$$\\text{Dataset}$$"')
    j = s.index('<mxGeometry x="200" y="630" width="60" height="30"', i)
    return s[:j] + '<mxGeometry x="%g" y="630" width="60" height="30"' % DATASET_X + \
        s[j + len('<mxGeometry x="200" y="630" width="60" height="30"'):]


def write(name, s):
    xml.dom.minidom.parseString(s)
    with open(os.path.join(HERE, name), 'w') as f:
        f.write(s)
    print('wrote', os.path.join('tools/diagrams', name))


def main():
    sob = add_arial(embedded_mxfile(SOURCES['sobolev']))
    sob = replace_once(sob, '<mxGeometry x="3.1299999999999955" width="103.12" height="60" as="geometry" />',
                       '<mxGeometry x="1.13" width="103.12" height="60" as="geometry" />')
    dc = add_arial(embedded_mxfile(SOURCES['dc2ac']))

    write('sobolev-original.drawio', add_frame(sob, GATE_FRAME['sobolev']))
    dc_gate = replace_once(dc, 'value="&lt;div&gt;$$\\text{Training}$$&lt;/div&gt;"',
                           'value="&lt;div&gt;\\(\\text{Training}\\)&lt;/div&gt;"')
    write('dc2ac-original.drawio', add_frame(dc_gate, GATE_FRAME['dc2ac']))

    write('sobolev.drawio', dataset(sob))
    write('dc2ac.drawio', dataset(dc))


if __name__ == '__main__':
    main()
