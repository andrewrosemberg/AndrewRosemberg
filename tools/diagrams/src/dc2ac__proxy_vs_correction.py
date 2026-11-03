#!/usr/bin/env python3
"""dc2ac--proxy-vs-correction: direct map vs corrected retained model, same reference data.

Three lanes: the direct map on top, the shared Dataset lane in the middle, the correction at the bottom.
The reference store sits between the two losses and feeds both by straight edges; each gradient return
runs parallel to its own row (above the direct map, below the correction, under the retained model)."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402

LA = r'L(\hat{\mathbf{y}},\mathbf{y}^{\mathrm{ref}})'
LB = r'L(\mathbf{y}^\star,\mathbf{y}^{\mathrm{ref}})'
G = lambda *rows: r'$$\begin{gathered}' + r'\\ '.join(rows) + r'\end{gathered}$$'
RET = G(r'\text{retained model}', r'\mathbf{y}^\star(p;w)')
GHAT = r'\hat g_{\omega\raise{0.22em}{\prime}}'   # script-size prime, raised (a superscript prime would be second-level)
YREF = r'\mathbf{y}^{\mathrm{ref}}(w)'

d = Diagram()
w = d.page('Page-1')
# top row: Direct map panel | Dataset panel; bottom row: Correction. Each panel has its own context input.
w.frame(200, 480, 720, 840)
w.line(530, 480, 530, 685, dashed=True)
w.line(200, 685, 720, 685, dashed=True)
w.lane_title(200, 480, 'Direct map', inset=True)
w.lane_title(530, 480, 'Dataset', inset=True)
w.lane_title(200, 685, 'Correction', inset=True)
# direct map
w.store('wa', 215, 565, 40, 60, 'w')
w.network(270, 555, prefix='na')
w.brace(290, 340, 638)
w.text('ga', 275, 647, 80, 26, GHAT)
w.box('yh', 360, 580, 30, 30, r'\hat{\mathbf{y}}', role='model')
w.box('lossA', 410, 575, 105, 40, LA, role='loss')
w.edge('wa', None, 'straight', exit=(1, 0.5), tgt_pt=(270, 595))
w.edge(None, 'yh', 'value', src_pt=(340, 595), entry=(0, 0.5))
w.edge('yh', 'lossA', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('lossA', 'na-h4-0', 'grad', exit=(0.5, 0), entry=(1, 0.5), points=[(462.5, 560)])
w.text('ga2', 365, 534, 70, 20, r'\nabla_{\hat{\mathbf{y}}}L')
# dataset
w.store('wd', 545, 500, 40, 60, 'w')
w.box('det', 600, 510, 110, 40, r'\text{Detailed model}', role='data')
w.store('ref', 620, 565, 60, 60, YREF)
w.edge('wd', 'det', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('det', 'ref', 'value', exit=(0.4545, 1), entry=(0.5, 0), extra='entryPerimeter=0;')
w.edge('ref', 'lossA', 'value', exit=(0, 0.5), entry=(1, 0.5), extra='exitPerimeter=0;')
# correction
w.store('wb', 215, 735, 40, 60, 'w')
w.network(270, 725, prefix='nb')
w.brace(290, 340, 808)
w.text('phi', 275, 817, 80, 26, r'\phi_\omega')
w.box('p', 360, 750, 30, 30, 'p', role='model')
w.box('ret', 410, 740, 105, 50, RET, role='model')
w.box('ys', 535, 750, 30, 30, r'\mathbf{y}^\star', role='model')
w.box('lossB', 597.5, 745, 105, 40, LB, role='loss')
w.edge('wb', None, 'straight', exit=(1, 0.5), tgt_pt=(270, 765))
w.edge(None, 'p', 'value', src_pt=(340, 765), entry=(0, 0.5))
w.edge('p', 'ret', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('ret', 'ys', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('ys', 'lossB', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('ref', 'lossB', 'value', exit=(0.5, 1), entry=(0.5, 0), extra='exitPerimeter=0;')
w.edge('lossB', 'nb-h4-7', 'grad', exit=(0.5, 1), entry=(1, 0.5), points=[(650, 800)])
w.text('gb', 410, 804, 150, 26, r'D_p\mathbf{y}^\star(p;w)^{\top}\nabla_{\mathbf{y}}L')

c = d.page('compact')
# phone: Direct map, Dataset, Correction stacked; the context store sits between the two networks and feeds
# their input columns by two short vertical edges (no rail).
c.frame(200, 480, 452, 920)
c.line(200, 650, 452, 650, dashed=True)
c.line(200, 760, 452, 760, dashed=True)
for y, t in ((480, 'Direct map'), (650, 'Dataset'), (760, 'Correction')):
    c.vertex(None, 262, y, 150, 30, 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;',
             '$$\\text{%s}$$' % t)
c.network(230, 525, prefix='na')
c.brace(250, 300, 608)
c.text('ga', 235, 617, 80, 24, GHAT)
c.box('lossA', 412, 550, 30, 30, 'L', role='loss')
c.store('w', 215, 685, 40, 60, 'w')
c.box('det', 290, 695, 64, 40, G(r'\text{Detailed}', r'\text{model}'), role='data')
c.store('ref', 407, 685, 40, 60, r'\mathbf{y}^{\mathrm{ref}}')
c.network(230, 800, prefix='nb')
c.brace(250, 300, 883)
c.text('phi', 235, 892, 80, 24, r'\phi_\omega')
c.box('ret', 324, 820, 64, 40, G(r'\text{retained}', r'\text{model}'), role='model')
c.box('lossB', 412, 825, 30, 30, 'L', role='loss')
c.edge('w', 'na-i3', 'value', exit=(0.5, 0), entry=(0.5, 1), extra='exitPerimeter=0;')
c.edge('w', 'nb-i0', 'value', exit=(0.5, 1), entry=(0.5, 0), extra='exitPerimeter=0;')
c.edge('w', 'det', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.edge('det', 'ref', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.edge(None, 'lossA', 'value', src_pt=(300, 565), entry=(0, 0.5))
c.text('yh', 344, 543, 24, 20, r'\hat{\mathbf{y}}')
c.edge(None, 'ret', 'value', src_pt=(300, 840), entry=(0, 0.5))
c.text('pl', 302, 818, 20, 20, 'p')
c.edge('ret', 'lossB', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.text('ysl', 390, 816, 20, 20, r'\mathbf{y}^\star')
c.edge('ref', 'lossA', 'value', exit=(0.5, 0), entry=(0.5, 1))
c.edge('ref', 'lossB', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('lossA', 'na-h4-0', 'grad', exit=(0.5, 0), entry=(1, 0.5), points=[(427, 530)])
c.text('ga2', 333, 506, 60, 20, r'\nabla_{\hat{\mathbf{y}}}L')
c.edge('lossB', 'nb-h4-7', 'grad', exit=(0.5, 1), entry=(1, 0.5), points=[(427, 875)])
c.text('gb', 318, 880, 90, 22, r'D_p\mathbf{y}^{\star\top}\nabla_{\mathbf{y}}L')
d.write(os.path.join(HERE, '..', 'dc2ac--proxy-vs-correction.drawio'))
