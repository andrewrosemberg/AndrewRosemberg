#!/usr/bin/env python3
"""strategic-bidding--derivative-path (round 3, rubric 49 + critic review).

Message: profit reaches the offer through the clearing's dispatch and price; the two partial derivatives of profit
(one per path, row by row: g_a* <-> lambda_a* - c_o, lambda_a* <-> g_a*) enter ONE adjoint solve with the
clearing's KKT matrix, whose output is the gradient on the offer. The linear-clearing case is stated in the caption.

Wide: forward row u -> Market clearing -> (g_a*, lambda_a*) -> Pi; reverse row directly below it, right to left:
Pi -> (lambda_a* - c_o, g_a*) -> adjoint F_z^T v = grad_z Pi -> grad_u Pi -> u. The adjoint sits under the clearing,
linked by the kit's purple tool link. Compact: forward column on the left, reverse column on the right."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _r2 import two, lab, e  # noqa: E402

U = r'u=(\mathbf{c}_a,\mathbf{Q}_a)'
CLR = two(r'\min_{\mathbf{g}}\ \textstyle\sum_i c_i g_i', r'\text{s.t. network},\ \mathbf{0}\le\mathbf{g}_a\le\mathbf{Q}_a')
ADJ = r'F_{\mathbf{z}}^{\top}\mathbf{v}=\nabla_{\mathbf{z}}\Pi'
G, L = r'\mathbf{g}_a^\star', r'\boldsymbol\lambda_a^\star'
PI = r'\Pi=(\boldsymbol\lambda_a^\star-\mathbf{c}_o)^{\top}\mathbf{g}_a^\star'
SG, SL = r'\boldsymbol\lambda_a^\star-\mathbf{c}_o', r'\mathbf{g}_a^\star'
GU = r'\nabla_u\Pi'
CUT = r'\times'

d = Diagram()
CLR = two(r'\text{Market clearing}', r'F(\mathbf{z};u,\xi)=\mathbf{0}')
TUP = two(G, L)
SEN = two(SG, SL)
# ------------------------------------------------------------------ wide
w = d.page('Page-1')
YF, YR = 60, 145
w.frame(0, 18, 562, 182)
w.box('u', 10, YF - 18, 92, 36, U, role='model')
w.box('clr', 142, YF - 22, 115, 44, CLR, role='data')
w.box('tup', 297, YF - 22, 80, 44, TUP, role='data')
w.box('pi', 417, YF - 22, 135, 44, PI, role='loss')
w.box('adj', 142, YR - 18, 115, 36, ADJ, role='tool')
w.box('sen', 297, YR - 22, 80, 44, SEN, role='loss')
for a, b in (('u', 'clr'), ('clr', 'tup'), ('tup', 'pi')):
    e(w, a, b, (1, 0.5), (0, 0.5))
w.edge('clr', 'adj', 'tool-tail', exit=(0.5, 1), entry=(0.5, 0))
e(w, 'pi', 'sen', (0.5, 1), (1, 0.5), [(484.5, YR)], kind='grad')
e(w, 'sen', 'adj', (0, 0.5), (1, 0.5), kind='grad')
e(w, 'adj', 'u', (0, 0.5), (0.5, 1), [(56, YR)], kind='grad')
lab(w, 99, YR + 12, GU, w=36)

# ------------------------------------------------------------------ compact
c = d.page('compact')
L, R = 51, 165.5
c.frame(0, 0, 234, 282)
c.box('u', 6, 12, 90, 36, U, role='model')
c.box('clr', 6, 78, 90, 44, two(r'\text{Market}', r'\text{clearing}'), role='data')
c.box('tup', L - 30, 153, 60, 44, TUP, role='data')
c.box('pi', 103, 230, 125, 40, PI, role='loss')
c.box('adj', R - 55, 82, 110, 36, ADJ, role='tool')
c.box('sen', R - 35, 153, 70, 44, SEN, role='loss')
e(c, 'u', 'clr', (0.5, 1), (0.5, 0))
e(c, 'clr', 'tup', (0.5, 1), (0.5, 0))
e(c, 'tup', 'pi', (0.5, 1), (0, 0.5), [(L, 250)])
c.edge('clr', 'adj', 'tool-tail', exit=(1, 0.5), entry=(0, 0.5))
e(c, 'pi', 'sen', (0.5, 0), (0.5, 1), kind='grad')
e(c, 'sen', 'adj', (0.5, 0), (0.5, 1), kind='grad')
e(c, 'adj', 'u', (0.5, 0), (1, 0.5), [(R, 30)], kind='grad')
lab(c, (96 + R) / 2.0, 19, GU, w=36)
d.write(os.path.join(HERE, '..', 'strategic-bidding--derivative-path.drawio'))
