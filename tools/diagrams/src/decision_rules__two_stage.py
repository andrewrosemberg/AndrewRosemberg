#!/usr/bin/env python3
"""decision-rules--two-stage: a fixed rule induces a two-stage program. The policy (one shared theta) fixes every
target of a sampled path; ONE recourse problem over the whole horizon implements them, and the multipliers of its
target constraints, lambda_t = dQ/dx_t, form the gradient with respect to theta.

From the qualification-report figure (diagram_qualify_tsddr.pdf, rebuilt exactly as tsddr-original.drawio) we keep
what is correct for this step: one orange multi-period problem whose parameters (w_t, the targets) are in red, the
outlined "Duality" box on the target row, the AD dark red for multipliers and the pink gradient box. Its per-stage
networks pi_t(.; theta_t) and its slack penalty belong to other formulations; the policy band here is the recurrent
rule of the proposal's figure, identical to decision-rules--parallel-stages, so that the two figures differ only in
the recourse: one problem here, independent stage problems there.

Layout (wide): rows = theta bus | policy row (x_0, pi, x_1, ..., x_T) | w_t under each copy | ONE problem across the
full width | lambda_t under each target column | brace, gradient. Compact: time downward, policy column left, the
one problem spanning the column on the right."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _tsddr_band import (AD, STRAIGHT, LEFT, OUTLINE, RED_TEXT, GRAD_BOX, GRAD, red, seg, lam_box,  # noqa: E402
                         wide_policy, compact_policy, BY, CQ, CT, CP, CTY, CQY)

W = red('w_t')
XHT = red(r'\hat{\mathbf{x}}_t')
FULL = (r'$$\begin{aligned}Q(\mathbf{w},\hat{\mathbf{x}})=\min_{\mathbf{x},\mathbf{y}}\ \ '
        r'&\sum_{t=1}^{T}f(\mathbf{x}_t,\mathbf{y}_t)\\[2pt]'
        r'\text{s.t.}\ \ &\mathcal{T}(\mathbf{x}_{t-1},\mathbf{x}_t,' + W + r',\mathbf{y}_t)=\mathbf{0},\\'
        r'&h(\mathbf{x}_t,\mathbf{y}_t,' + W + r')\ge\mathbf{0},\\'
        r'&\mathbf{x}_t=' + XHT + r'\quad(:\boldsymbol\lambda_t),\\[2pt]'
        r'&t=1,\dots,T\end{aligned}$$')
FULL_C = (r'$$\begin{aligned}&\min_{\mathbf{x},\mathbf{y}}\ \sum_{t=1}^{T}f(\mathbf{x}_t,\mathbf{y}_t)\\[2pt]'
          r'&\mathbf{y}_t\in\mathcal{Y}_t(\mathbf{x}_{t-1},\mathbf{x}_t;' + W + r'),\\'
          r'&\mathbf{x}_t=' + XHT + r'\quad(:\boldsymbol\lambda_t),\\[2pt]'
          r'&t=1,\dots,T\end{aligned}$$')
DUAL = r'$$\boldsymbol\lambda_t=\partial Q/\partial\hat{\mathbf{x}}_t$$'
DUALITY = r'$$\textit{Duality}$$'

d = Diagram()
# =============================================================================================== wide
w = d.page('Page-1')
BH = 136
QX = [(10, 178), (202, 178), (408, 194)]             # same columns as decision-rules--parallel-stages
R = lambda k: QX[k][0] + QX[k][1]
IN, OUT = (lambda k: QX[k][0] + 24), (lambda k: R(k) - 24)
TC = [IN(0), (R(0) + QX[1][0]) / 2.0, OUT(1), IN(2), OUT(2)]
wide_policy(w, TC)
w.box('Q', QX[0][0], BY, R(2) - QX[0][0], BH, '', role='data')
w.vertex('Qtext', 92, BY + 4, 330, BH - 8, LEFT, FULL)
DX, DY = 432, BY + 83                                # Duality box on the target row (qualify figure)
w.vertex('dual', DX, DY, 120, 26, OUTLINE, DUAL)
w.vertex('duality', DX + 30, DY + 26, 60, 20, RED_TEXT, DUALITY)
for k in (1, 2, 3, 4):
    seg(w, STRAIGHT, (TC[k], 119), (TC[k], BY))     # every target enters the one problem
B = BY + BH
LY = B + 30
for k, (cx, s) in enumerate(zip(TC[1:], ['1', '2', 'T-1', 'T'])):
    lam_box(w, 'l%d' % k, cx, LY, r'\boldsymbol\lambda_{%s}' % s, w=44)
    seg(w, AD, (cx, B), (cx, LY))
w.text('ldots', (TC[2] + TC[3]) / 2.0 - 15, LY + 3, 30, 20, r'\cdots')
bx0, bx1 = TC[1] - 56, R(2) - 10                     # same brace and gradient box as the stage-separated figure
w.brace(bx0, bx1, LY + 32)
GW, GH = 220, 50
gx = (bx0 + bx1) / 2.0 - GW / 2.0
w.vertex('G', gx, LY + 50, GW, GH, GRAD_BOX, GRAD)
w.frame(0, 0, R(2) + 10, LY + 50 + GH + 10)

# ============================================================================================ compact
# The wide figure in miniature (stages 1 and 2): one problem across the columns, its multipliers, the gradient.
c = d.page('compact')
compact_policy(c)
QH = 108
c.box('Q', CQ[0][0], CQY, CQ[1][0] + CQ[1][1] - CQ[0][0], QH, '', role='data')
c.vertex('Qtext', 30, CQY + 2, 200, QH - 4, LEFT, FULL_C)
c.text('Qt', CQ[1][0] + CQ[1][1] - 26, CQY + 3, 24, 20, 'Q')
for k in (1, 2):
    seg(c, STRAIGHT, (CT[k], CTY + 22), (CT[k], CQY))                                     # targets -> the one problem
B = CQY + QH
LY = B + 26
lam_box(c, 'lt', 127, LY, r'\boldsymbol\lambda_t=\partial Q/\partial\hat{\mathbf{x}}_t', w=160)
seg(c, AD, (127, B), (127, LY))
GY = LY + 50
seg(c, AD, (127, LY + 26), (127, GY))
c.vertex('G', 22, GY, 210, 50, GRAD_BOX, GRAD)
c.frame(0, 0, 254, GY + 62)
d.write(os.path.join(HERE, '..', 'decision-rules--two-stage.drawio'))
