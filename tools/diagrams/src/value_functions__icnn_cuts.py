#!/usr/bin/env python3
"""value-functions--icnn-cuts: values of a detailed model train an input-convex network; its cuts enter the stage problem.

Lanes top to bottom: Dataset (detailed solves), Training (projected gradient fit), Deployment (cutting-plane loop).
The samples enter the network's input from above, the queried state from below; the network's output feeds the
training loss to the right and, through AD, the cut below. The skip connections are stated in the caption."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram, BOX, ROLE, NODE, SYNAPSE  # noqa: E402

PROB = '\\begin{aligned}\n\\min_{\\mathbf{y}} &\\quad f(\\mathbf{y};p) \\\\\n\\text{s.t.} &\\quad \\mathbf{y}\\in\\mathcal{Y}(p)\n\\end{aligned}'
S1 = (r'$$\begin{aligned}&\min\ f(\mathbf{x}_t,\mathbf{y}_t)+\vartheta\\'
      r'&\text{s.t.}\ \ \mathbf{y}_t\in\mathcal{Y}_t(\mathbf{x}_{t-1},\mathbf{x}_t;w_t)\\'
      r'&\phantom{\text{s.t.}}\ \ \vartheta\ge\alpha_k+\boldsymbol\beta_k^{\top}\mathbf{x}_t,\ k\le K\end{aligned}$$')
S1C = (r'$$\begin{aligned}&\min\ f+\vartheta\\ &\text{s.t.}\ \mathbf{y}_t\in\mathcal{Y}_t\\'
       r'&\phantom{\text{s.t.}}\ \vartheta\ge\alpha_k+\boldsymbol\beta_k^{\top}\mathbf{x}_t\end{aligned}$$')
PROBC = '\\begin{aligned}\n\\min_{\\mathbf{y}} &\\ \\ f(\\mathbf{y};p) \\\\\n\\text{s.t.} &\\ \\ \\mathbf{y}\\in\\mathcal{Y}(p)\n\\end{aligned}'
VH = r'\widehat{\mathcal{V}}_{t+1}'
C1 = (r'$$\begin{aligned}\ell(\mathbf{x})&=%s(\bar{\mathbf{x}})+\boldsymbol\beta^{\top}(\mathbf{x}-\bar{\mathbf{x}})\\'
      r'\boldsymbol\beta&\in\partial %s(\bar{\mathbf{x}})\end{aligned}$$') % (VH, VH)
C1C = (r'$$\begin{aligned}\ell(\mathbf{x})&=%s(\bar{\mathbf{x}})+\boldsymbol\beta^{\top}(\mathbf{x}-\bar{\mathbf{x}})\\'
       r'\boldsymbol\beta&\in\partial %s(\bar{\mathbf{x}})\end{aligned}$$') % ((r'\widehat{\mathcal{V}}',) * 2)


def icnn(p, x, y, rows=6, pre='q'):
    """Network glyph in the kit's grammar for a scalar value: input column of 4 nodes (x..x+10, y..y+40),
    three hidden columns of `rows` nodes at x+25, x+50, x+75, one green output node at (x+100, y+15)."""
    top = y + (4 - rows) * 5
    ins = [p.vertex('%s-i%d' % (pre, i), x, y + 10 * i, 10, 10, NODE % ROLE['model']) for i in range(4)]
    cols = [[p.vertex('%s-h%d-%d' % (pre, c, r), x + 25 * (c + 1), top + 10 * r, 10, 10, NODE % ROLE['model'])
             for r in range(rows)] for c in range(3)]
    out = p.vertex('%s-o' % pre, x + 100, y + 15, 10, 10, NODE % ROLE['output'])
    for a_col, b_col in zip([ins] + cols, cols + [[out]]):
        for a in a_col:
            for b in b_col:
                p.add('<mxCell id="%s-%s-%s" value="" style="%s" edge="1" parent="1" source="%s" target="%s">'
                      '<mxGeometry relative="1" as="geometry" /></mxCell>' % (pre, a.split('-', 1)[1], b.split('-', 1)[1], SYNAPSE, a, b))
    return out, top + 10 * rows


VB = r'\widehat{\mathcal{V}}_{t+1}'
d = Diagram()
w = d.page('Page-1')
w.frame(200, 470, 605, 1015)
w.line(200, 600, 605, 600, dashed=True)
w.line(200, 785, 605, 785, dashed=True)
w.lane_title(200, 470, 'Dataset', inset=True)
w.lane_title(200, 600, 'Training', inset=True)
w.lane_title(200, 785, 'Deployment', inset=True)
# dataset
w.store('d0', 285, 500, 40, 60, 'p')
w.vertex('d1', 351, 501.88, 112.5, 56.25, BOX % ROLE['data'])
w.block('d1t', 352.13, 490, 103.12, 60, PROB)
w.brace(351, 463.5, 563)
w.text('qp', 377, 574, 60, 22, r'q(p)')
w.store('d2', 490, 500, 95, 60, r'\{(p_i,z_i)\}_{i=1}^N')
w.edge('d0', 'd1', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('d1', 'd2', 'value', exit=(1, 0.5), entry=(0, 0.5))
# training: projected gradient fit of the input-convex network
out, bot = icnn(w, 300, 680)
w.brace(325, 385, bot + 4)
w.text('qh', 315, bot + 15, 80, 24, r'\hat q')
w.box('pi', 323, 622, 64, 26, r'\Pi_{W\ge 0}', role='tool')
w.box('zh', 440, 685, 30, 30, r'\hat z_i', role='model')
w.box('loss', 490, 680, 95, 40, r'\text{Loss}(\hat z_i,z_i)', role='loss')
w.edge('d0', 'q-i0', 'value', exit=(0.5, 1), entry=(0.5, 0))
w.edge(out, 'zh', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('zh', 'loss', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('d2', 'loss', 'value', exit=(0.5, 1), entry=(0.5, 0))
w.edge('loss', 'pi', 'grad', exit=(0.2105, 0), entry=(1, 0.5), points=[(510, 635)])
w.edge('pi', 'q-h1-0', 'tool', exit=(0.5, 1), entry=(0.5, 0))
# deployment: the trained network, frozen, is queried inside the stage problem's cutting-plane loop
w.box('vf', 380, 810, 50, 30, VB, role='model')
w.edge(out, 'vf', 'value', exit=(0.5, 1), entry=(0.5, 0))
w.text('frz', 412, 752, 60, 20, r'\text{trained}', left=True)
w.box('xb', 320, 810, 30, 30, r'\bar{\mathbf{x}}', role='data')
w.box('ad', 450, 812.5, 35, 25, r'\textit{AD}', role='tool')
w.box('c1', 355, 865, 225, 50, C1, role='model')
w.box('s1', 286, 940, 230, 60, S1, role='data')
w.edge('xb', 'vf', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('vf', 'ad', 'tool-tail', exit=(1, 0.5), entry=(0, 0.5))
w.edge('ad', 'c1', 'value', exit=(0.5, 1), entry=(0.5, 0))
w.edge('c1', 's1', 'value', exit=(0.5, 1), entry=(0.7891, 0))
w.text('cut', 475, 916, 60, 22, r'\text{add cut}', left=True)
w.edge('s1', 'xb', 'value', exit=(0.2130, 0), entry=(0.5, 1))

c = d.page('compact')
c.frame(200, 470, 452, 1085)
c.line(200, 620, 452, 620, dashed=True)
c.line(200, 805, 452, 805, dashed=True)
for y, t in ((470, 'Dataset'), (620, 'Training'), (805, 'Deployment')):
    c.vertex(None, 242, y, 150, 30, 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;',
             '$$\\text{%s}$$' % t)
c.store('d0', 210, 515, 40, 60, 'p')
c.vertex('d1', 265, 516.88, 98, 56.25, BOX % ROLE['data'])
c.block('d1t', 269, 505, 92, 60, PROBC)
c.brace(265, 363, 578)
c.text('qp', 284, 588, 60, 22, r'q(p)')
c.store('d2', 375, 510, 70, 70, r'\{(p_i,z_i)\}')
c.edge('d0', 'd1', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.edge('d1', 'd2', 'value', exit=(1, 0.5), entry=(0, 0.5))
cout, cbot = icnn(c, 225, 705, rows=5, pre='c')
c.brace(250, 310, cbot + 4)
c.text('qh', 240, cbot + 13, 80, 22, r'\hat q')
c.box('pi', 248, 650, 64, 26, r'\Pi_{W\ge 0}', role='tool')
c.box('loss', 382.5, 710, 55, 30, r'\text{Loss}', role='loss')
c.edge('d0', 'c-i0', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge(cout, 'loss', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.text('zh', 345, 701, 30, 20, r'\hat z_i')
c.edge('d2', 'loss', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('loss', 'pi', 'grad', exit=(0.2, 0), entry=(1, 0.5), points=[(393.5, 663)])
c.edge('pi', 'c-h1-0', 'tool', exit=(0.5, 1), entry=(0.5, 0))
c.box('vf', 305, 840, 50, 30, VB, role='model')
c.edge(cout, 'vf', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.text('frz', 337, 780, 60, 20, r'\text{trained}', left=True)
c.box('xb', 212, 840, 30, 30, r'\bar{\mathbf{x}}', role='data')
c.box('ad', 312.5, 890, 35, 25, r'\textit{AD}', role='tool')
c.box('c1', 240, 935, 190, 50, C1C, role='model')
c.box('s1', 267.5, 1010, 125, 60, S1C, role='data')
c.edge('xb', 'vf', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.edge('vf', 'ad', 'tool-tail', exit=(0.5, 1), entry=(0.5, 0))
c.edge('ad', 'c1', 'value', exit=(0.5, 1), entry=(0.4737, 0))
c.edge('c1', 's1', 'value', exit=(0.4737, 1), entry=(0.5, 0))
c.text('cut', 337, 987, 60, 22, r'\text{add cut}', left=True)
c.edge('s1', 'xb', 'value', exit=(0, 0.5), entry=(0.5, 1), points=[(227, 1040)])
d.write(os.path.join(HERE, '..', 'value-functions--icnn-cuts.drawio'))
