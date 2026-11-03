#!/usr/bin/env python3
"""decision-rules--parallel-stages: state-consistent targets separate the second stage into independent stage
problems, solved in parallel. Rebuild of the proposal's figure (figures/diagram_tsddr_strict.pdf, Fig.
"tsddr-training") in the kit identity: a recurrent policy shares theta across stages and emits (x_t, zeta_t);
stage problem q_t receives the adjacent targets and w_t; the multipliers of a target as the outgoing state of
q_t and the incoming state of q_{t+1} add up, lambda_t = bar-lambda_t + mu_{t+1}; the gradient returns to every
copy of theta. No arrow joins two stage problems: their independence is the point.

Same skeleton as decision-rules--two-stage (one full-horizon problem), so the pair reads as one step."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _tsddr_band import (AD, STRAIGHT, LEFT, GRAD_BOX, GRAD, LAMS, red, seg, lam_box,  # noqa: E402
                         wide_policy, compact_policy, BY, CQ, CT, CP, CTY, CQY)

X = lambda s: r'\mathbf{x}_{%s}' % s
XH = lambda s: red(r'\hat{\mathbf{x}}_{%s}' % s)


def targets_rows(c, p, nested):
    """The two target equalities with their multipliers. nested=True aligns them at '=' (unequal subscripts,
    stage T) and pads the shorter right side so the multiplier labels form one column."""
    if nested:
        return (r'&\begin{aligned}%s&=%s\quad(:\boldsymbol\mu_{%s}),\\'
                r'%s&=%s\phantom{_{-1}}\quad(:\bar{\boldsymbol\lambda}_{%s})\end{aligned}'
                % (X(p), XH(p), c, X(c), XH(c), c))
    return (r'&%s=%s\quad(:\boldsymbol\mu_{%s}),\\&%s=%s\quad(:\bar{\boldsymbol\lambda}_{%s})'
            % (X(p), XH(p), c, X(c), XH(c), c))


def stage(c, p, nested=False):
    """Stage problem q_c (wide): the operating constraints written out, as on the page."""
    W = red('w_{%s}' % c)
    return (r'$$\begin{aligned}\min\ &f(%(xc)s,\mathbf{y}_{%(c)s})\\[2pt]'
            r'\text{s.t.}\ &\mathcal{T}(%(xp)s,%(xc)s,%(w)s,\mathbf{y}_{%(c)s})=\mathbf{0},\\'
            r'&h(%(xc)s,\mathbf{y}_{%(c)s},%(w)s)\ge\mathbf{0},\\[2pt]' % dict(c=c, xc=X(c), xp=X(p), w=W)
            + targets_rows(c, p, nested) + r'\end{aligned}$$')


def stage_compact(c, p, nested=False):
    """Stage problem q_c (phone): the operating constraints as the admissible-control set Y_t of the page."""
    W = red('w_{%s}' % c)
    return (r'$$\begin{aligned}&\min\ f(%(xc)s,\mathbf{y}_{%(c)s})\\[2pt]'
            r'&\mathbf{y}_{%(c)s}\in\mathcal{Y}_{%(c)s}(%(xp)s,%(xc)s;%(w)s)\\[2pt]'
            % dict(c=c, xc=X(c), xp=X(p), w=W) + targets_rows(c, p, nested) + r'\end{aligned}$$')


STAGES = [('1', '0', False), ('2', '1', False), ('T', 'T-1', True)]

d = Diagram()
# =============================================================================================== wide
# Layout (columns = targets x_0, x_1, x_2, ..., x_{T-1}, x_T with a policy copy between consecutive targets):
#   row 0  theta box above x_0, its bus above the policy row, one drop into each copy
#   row 1  x_0 -> pi -> x_1 -> pi -> x_2 ... x_{T-1} -> pi -> x_T
#   row 2  w_1, w_2, w_T under their copies
#   row 3  q_1 | q_2 | ... | q_T  (each fed by w_t at its centre and the adjacent targets 24 px in from its edges)
#   row 4  lambda_1 under the q_1|q_2 junction, lambda_2, ..., lambda_T under the outgoing-target side
#   row 5  brace over the multipliers, gradient box
w = d.page('Page-1')
BH = 112
QX = [(10, 178), (202, 178), (408, 194)]            # (left, width) of q_1, q_2, q_T
R = lambda k: QX[k][0] + QX[k][1]
IN, OUT = (lambda k: QX[k][0] + 24), (lambda k: R(k) - 24)   # where the incoming / outgoing target enters
TC = [IN(0), (R(0) + QX[1][0]) / 2.0, OUT(1), IN(2), OUT(2)]
wide_policy(w, TC)
for k, (c, pp, nested) in enumerate(STAGES):
    w.box('q%d' % k, QX[k][0], BY, QX[k][1], BH, stage(c, pp, nested), role='data')
    w.text('qt%d' % k, R(k) - 30, BY + 3, 28, 20, 'q_{%s}' % c)
FK = BY - 12                                        # fork of x_1 into q_1 and q_2
seg(w, STRAIGHT, (TC[0], 119), (IN(0), BY))
seg(w, STRAIGHT, (TC[1], 119), (OUT(0), BY), [(TC[1], FK), (OUT(0), FK)])
seg(w, STRAIGHT, (TC[1], 119), (IN(1), BY), [(TC[1], FK), (IN(1), FK)])
seg(w, STRAIGHT, (TC[2], 119), (OUT(1), BY))
seg(w, STRAIGHT, (TC[3], 119), (IN(2), BY))
seg(w, STRAIGHT, (TC[4], 119), (OUT(2), BY))
DOTX = (R(1) + QX[2][0]) / 2.0
w.text('qdots', DOTX - 15, BY + BH / 2.0 - 10, 30, 20, r'\cdots')
B = BY + BH
LY = B + 30
MJ = B + 14                                         # merge of bar-lambda_1 and mu_2
lam_box(w, 'l0', TC[1], LY, LAMS[0])
lam_box(w, 'l1', OUT(1), LY, LAMS[1])
lam_box(w, 'l2', R(2) - 66, LY, LAMS[2])
seg(w, AD, (OUT(0), B), (TC[1], LY), [(OUT(0), MJ), (TC[1], MJ)])
seg(w, AD, (IN(1), B), (TC[1], LY), [(IN(1), MJ), (TC[1], MJ)])
seg(w, AD, (OUT(1), B), (OUT(1), LY))
seg(w, AD, (OUT(2), B), (R(2) - 66, LY), [(OUT(2), MJ), (R(2) - 66, MJ)])
w.text('ldots', (OUT(1) + 56 + R(2) - 122) / 2.0 - 15, LY + 3, 30, 20, r'\cdots')
bx0, bx1 = TC[1] - 56, R(2) - 10
w.brace(bx0, bx1, LY + 32)
GW, GH = 220, 50
gx = (bx0 + bx1) / 2.0 - GW / 2.0
w.vertex('G', gx, LY + 50, GW, GH, GRAD_BOX, GRAD)
w.frame(0, 0, R(2) + 10, LY + 50 + GH + 10)  # theta row starts 10 px inside

# ============================================================================================ compact
# The wide figure in miniature (stages 1 and 2): each stage problem is written by its value q_t and multipliers.
c = d.page('compact')
compact_policy(c)
QH = 52
for k, (cc, pp) in enumerate([('1', '0'), ('2', '1')]):
    x, wq = CQ[k]
    c.box('q%d' % k, x, CQY, wq, QH,
          r'$$\begin{gathered}q_{%s}(\hat{\mathbf{x}}_{%s},\hat{\mathbf{x}}_{%s};w_{%s})\\[2pt]'
          r'(:\boldsymbol\mu_{%s},\ \bar{\boldsymbol\lambda}_{%s})\end{gathered}$$' % (cc, pp, cc, cc, cc, cc), role='data')
FK = CQY - 14
seg(c, STRAIGHT, (CT[0], CTY + 22), (CT[0], CQY))                                         # x_0 -> q_1
seg(c, STRAIGHT, (CT[1], CTY + 22), (CQ[0][0] + CQ[0][1] - 12, CQY), [(CT[1], FK), (CQ[0][0] + CQ[0][1] - 12, FK)])
seg(c, STRAIGHT, (CT[1], CTY + 22), (CQ[1][0] + 12, CQY), [(CT[1], FK), (CQ[1][0] + 12, FK)])
seg(c, STRAIGHT, (CT[2], CTY + 22), (CT[2], CQY))                                         # x_2 -> q_2
LY = CQY + QH + 26
lam_box(c, 'l0', CQ[0][0] + CQ[0][1] / 2.0, LY, LAMS[0], w=CQ[0][1])
lam_box(c, 'l1', CQ[1][0] + CQ[1][1] / 2.0, LY, LAMS[1], w=CQ[1][1])
B = CQY + QH
c1, c2 = CQ[0][0] + CQ[0][1] / 2.0, CQ[1][0] + CQ[1][1] / 2.0
seg(c, AD, (c1, B), (c1, LY))                                                             # bar-lambda_1
seg(c, AD, (CQ[1][0] + 12, B), (CQ[0][0] + CQ[0][1] - 12, LY), [(CQ[1][0] + 12, B + 12), (CQ[0][0] + CQ[0][1] - 12, B + 12)])  # mu_2
seg(c, AD, (c2 + 20, B), (c2 + 20, LY))                                                   # bar-lambda_2
c.brace(CQ[0][0] + 4, CQ[1][0] + CQ[1][1] - 4, LY + 32)
GY = LY + 50
c.vertex('G', 22, GY, 210, 50, GRAD_BOX, GRAD)
c.frame(0, 0, 254, GY + 62)
d.write(os.path.join(HERE, '..', 'decision-rules--parallel-stages.drawio'))
