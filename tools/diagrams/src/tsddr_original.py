#!/usr/bin/env python3
"""Gate C: rebuild of diagram_qualify_tsddr.pdf (TS-DDR training loop) by measurement.

That PDF carries no embedded draw.io source (it was re-saved by macOS Preview), so every
shape below was read off the PDF's own vector paths (pdftocairo -svg, mapped back to
draw.io px through the page transform), and every label was typeset and positioned until
its glyphs coincide with the original's. Run from the repository root:

    python3 tools/diagrams/src/tsddr_original.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from kit import Diagram, Page, ROLE, BOX, RBOX, STORE, TEXT, LINE, EDGE  # noqa: E402

LEFT = 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;'
DOT2 = 'endArrow=none;dashed=1;html=1;dashPattern=1 2;strokeWidth=2;'      # dotted, 2 px dots every 6 px
DOT3 = 'endArrow=none;dashed=1;html=1;dashPattern=1 3;strokeWidth=2;'      # draw.io "Dotted Line" template
AD_RED = '#AC3C0C'
DASH_AD = 'endArrow=classic;html=1;rounded=0;dashed=1;dashPattern=8 8;strokeColor=%s;' % AD_RED

# label cells: id -> (x, y, w, h, style-extra, TeX)
LABELS = {
    'title': (198, 480, 70, 30, TEXT, r'<div>$$\text{TS-DDR}$$</div>'),
    't': (287.95, 660, 20, 20, TEXT, r'$$t$$'),
    'pi': (275, 695, 140, 30, LEFT, r'$$\pi_t(\{w_j\}_{j=2..t},\mathbf{x}_0;\theta_t)$$'),
    'row1': (450.34, 529, 290, 40, LEFT,
             r'$$\min_{\mathbf{x},\mathbf{u},\delta}\ \ J(w,\hat{\mathbf{x}})=\sum_t c(\mathbf{x}_t,\mathbf{u}_t)+C^\delta_t||\delta_t||$$'),
    'row2': (450.5, 583.34, 160, 20, LEFT,
             r'$$\text{s.t.}\ f(\mathbf{x}_t,\mathbf{x}_{t-1},{\color{red}w_t},\mathbf{u}_t)=0$$'),
    'all2': (612.94, 583.12, 20, 20, LEFT, r'$$\forall t$$'),
    'row3': (481.62, 602.64, 90, 20, LEFT, r'$$\mathbf{x}_t+\delta_t=\;{\color{red}\hat{\mathbf{x}}_t}$$'),
    'all3': (615.48, 602.3, 26, 20, LEFT, r'$$\forall t:$$'),
    'row4': (475.35, 639.11, 90, 20, LEFT, r'$$h(\mathbf{x}_t,\mathbf{u}_t)\geq 0$$'),
    'all4': (613.8, 638.9, 20, 20, LEFT, r'$$\forall t$$'),
    'lam': (643.5, 602.64, 95, 21.19, LEFT, r'$$\lambda\!=\nabla_{\hat{\mathbf{x}}}J(w,\hat{\mathbf{x}})$$'),
    'duality': (668, 625, 56, 20, LEFT, r'$$\textit{Duality}$$'),
}


def build(labels=LABELS, frame=None):
    d = Diagram()
    p = d.page('Page-1')

    def lab(k, color=None):
        x, y, w, h, st, tex = labels[k]
        if color:
            st += 'fontColor=%s;' % color
        p.vertex(k, x, y, w, h, st, tex)

    def seg(style, a, b, pts=()):
        geo = '<mxPoint x="%g" y="%g" as="sourcePoint" /><mxPoint x="%g" y="%g" as="targetPoint" />' % (a + b)
        if pts:
            geo += '<Array as="points">%s</Array>' % ''.join('<mxPoint x="%g" y="%g" />' % q for q in pts)
        p.add('<mxCell id="%s" value="" style="%s" edge="1" parent="1"><mxGeometry width="50" height="50" '
              'relative="1" as="geometry">%s</mxGeometry></mxCell>' % (p._id(None), style, geo))

    if frame:
        p.vertex('gate-page-frame', *frame, 'rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;')
    # dotted perspective lines behind the stack of per-stage networks
    seg(DOT3, (300.041, 599.980), (275.084, 623.072))
    seg(DOT2, (287, 610), (430, 611))
    p.vertex('omega', 225, 598.81, 40, 60, STORE % ROLE['data'], r'<div>$$\omega$$</div>')
    seg(EDGE['straight'], (260, 635), (291, 625), [(273, 625)])
    seg(DOT2, (278, 620), (421, 621))
    # stack: back, middle, front sheet, each with a network
    p.vertex('sheet3', 308, 580, 80, 85, BOX % ROLE['sheet'])
    p.network(312.72, 582.5, output='model', prefix='net3')
    p.vertex('sheet2', 298, 585, 80, 85, BOX % ROLE['sheet'])
    p.network(302.72, 587.5, output='model', prefix='net2')
    seg(LINE, (200, 730), (200.377676, 479.849182))
    seg(LINE, (770, 730), (770, 480))
    seg(LINE, (770, 480), (200, 480))
    lab('title')
    seg(EDGE['straight'], (260, 635), (286.84, 635.25))
    seg(LINE, (770, 730), (200, 730))
    p.vertex(None, 323.0, 658.81, 10.55, 66.19,
             'shape=curlyBracket;whiteSpace=wrap;html=1;rounded=1;flipH=1;labelPosition=right;'
             'verticalLabelPosition=middle;align=left;verticalAlign=middle;rotation=90;')
    lab('pi')
    seg(LINE, (406, 635), (414, 627))
    seg(LINE, (378, 627.36), (414, 627.4))
    seg(DOT3, (423.414, 615.586), (422, 617))
    seg(DOT2, (284, 614), (286, 614))
    p.vertex('opt', 440, 530, 310, 135, BOX % ROLE['data'])
    lab('row1'); lab('row2'); lab('all2'); lab('row3'); lab('all3'); lab('row4'); lab('all4')
    p.edge('omega', None, 'value', points=[(245, 570), (550, 570)], exit=(0.5, 0), tgt_pt=(550, 590))
    p.edge(None, None, 'value', points=[(555.72, 635)], src_pt=(344, 635), tgt_pt=(555.72, 623))
    p.vertex('sheet1', 288.28, 592.5, 80, 85, BOX % ROLE['sheet'])
    p.network(293, 595, output='model', prefix='net1')
    lab('t')
    seg(DASH_AD, (691.5, 603), (348, 580), [(696, 603), (696, 513), (348, 513)])
    p.vertex('dual', 643, 603, 97, 21.19, 'rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=%s;' % AD_RED)
    lab('lam')
    lab('duality', AD_RED)
    p.vertex('ad', 360, 500, 310, 25, RBOX % ROLE['loss'] + 'fontColor=%s;' % AD_RED,
             r'$$AD=\nabla_{\hat{\mathbf{x}}}J(w,\hat{\mathbf{x}})\odot\nabla_\theta\pi(\{w_j\}_{j=2..T},\mathbf{x}_0;\theta)$$')
    return d


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'tsddr-original.drawio')
    # Page extent of the original export (diagram px), solved against its PDF transform; export with -s 0.911352.
    build(frame=(169.2561, 460.9562, 629.7068, 379.7376)).write(out)
