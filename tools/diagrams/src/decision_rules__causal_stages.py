#!/usr/bin/env python3
"""decision-rules--causal-stages: penalized targets, decomposed by stages and solved causally (page section 07;
proposal, "Penalized Targets and Their Decomposition", eqs. penalized-stage and stage-gradient).

Two generic stages t, t+1 of the rollout. Unlike decision-rules--parallel-stages, the stage problems are solved in
sequence: stage t receives the state x*_{t-1} realized by stage t-1, implements its target up to a penalized
discrepancy, and hands x*_t to the next stage and to the policy (closed loop). The gradient of a target then has
two parts: its multiplier bar-lambda_t, and its effect on later stages, dG_{t+1}/dx*_t times the solution
sensitivity dX_t/dx_t, which the dashed chain carries backward along the path (purple: differentiation of the
stage problem itself, the tool role of the kit)."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram, ROLE, RBOX  # noqa: E402
from _tsddr_band import (AD, STRAIGHT, LINE, LEFT, RED_LEFT, RED_TEXT, GRAD_BOX, red, seg,  # noqa: E402
                         target, wbox, lam_box)

TOOL_TAIL = ('edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;endArrow=none;'
             'startFill=0;fillColor=#e1d5e7;strokeColor=#9673a6;')
X = lambda s: r'\mathbf{x}_{%s}' % s
XS = lambda s: r'\mathbf{x}^\star_{%s}' % s
GRAD = (r'$$\frac{d\mathcal{Q}^\delta}{d\theta}=\sum_{t=1}^{T}\Big[\bar{\boldsymbol\lambda}_t^{\top}'
        r'+\frac{dG_{t+1}}{d\mathbf{x}^\star_t}\,\frac{\partial X_t}{\partial\hat{\mathbf{x}}_t}\Big]'
        r'\frac{\partial\pi_t}{\partial\theta}$$')
GRAD_C = (r'$$\begin{array}{r}\displaystyle\frac{d\mathcal{Q}^\delta}{d\theta}=\sum_{t=1}^{T}\Big[\bar{\boldsymbol\lambda}_t^{\top}'
          r'+\frac{dG_{t+1}}{d\mathbf{x}^\star_t}\,\frac{\partial X_t}{\partial\hat{\mathbf{x}}_t}\Big]\\[2pt]'
          r'\displaystyle\cdot\,\frac{\partial\pi_t}{\partial\theta}\end{array}$$')


def stage(c, p):
    """Penalized stage problem q^delta_c: the incoming state is the realized one, the target a penalized row."""
    W = red('w_{%s}' % c)
    return (r'$$\begin{aligned}\min\ &f(%(xc)s,\mathbf{y}_{%(c)s})+C^\delta_{%(c)s}\lVert\boldsymbol\delta_{%(c)s}\rVert\\[2pt]'
            r'\text{s.t.}\ &\mathcal{T}(%(xp)s,%(xc)s,%(w)s,\mathbf{y}_{%(c)s})=\mathbf{0},\\'
            r'&h(%(xc)s,\mathbf{y}_{%(c)s},%(w)s)\ge\mathbf{0},\\[2pt]'
            r'&%(xp)s=%(xsp)s\quad(:\boldsymbol\mu_{%(c)s}),\\'
            r'&%(xc)s+\boldsymbol\delta_{%(c)s}=%(xhc)s\quad(:\bar{\boldsymbol\lambda}_{%(c)s})\end{aligned}$$'
            % dict(c=c, xc=X(c), xp=X(p), w=W, xsp=red(XS(p)), xhc=red(r'\hat{\mathbf{x}}_{%s}' % c)))


def stage_compact(c, p):
    W = red('w_{%s}' % c)
    return (r'$$\begin{aligned}&\min\ F^\delta_{%(c)s}(%(xc)s,\mathbf{y}_{%(c)s},\boldsymbol\delta_{%(c)s})\\[2pt]'
            r'&\mathbf{y}_{%(c)s}\in\mathcal{Y}_{%(c)s}(%(xp)s,%(xc)s;%(w)s),\\[2pt]'
            r'&%(xp)s=%(xsp)s\quad(:\boldsymbol\mu_{%(c)s}),\\'
            r'&%(xc)s+\boldsymbol\delta_{%(c)s}=%(xhc)s\quad(:\bar{\boldsymbol\lambda}_{%(c)s})\end{aligned}$$'
            % dict(c=c, xc=X(c), xp=X(p), w=W, xsp=red(XS(p)), xhc=red(r'\hat{\mathbf{x}}_{%s}' % c)))


def sens(c, p):
    return (r'$$\begin{gathered}\partial X_{%s}/\partial\hat{\mathbf{x}}_{%s},\\[1pt] \partial X_{%s}/\partial%s'
            r'\end{gathered}$$' % (c, c, c, XS(p)))


def frac(num, den):
    return r'$$\frac{%s}{d%s}$$' % (num, den)


STG = [('1', '0', '2'), ('2', '1', '3')]
d = Diagram()
# =============================================================================================== wide
w = d.page('Page-1')
# Layout: row 0 theta box and bus | row 1 policy (zeta_0 in, copy 1, (x_1, zeta_1), copy 2, (x_2, zeta_2)) |
# row 2 w_t under each copy | row 3 q^delta_1 -> x*_1 -> q^delta_2 -> x*_2 (forward), dG/dx* beneath (backward) |
# row 4 bar-lambda_t and the solution sensitivities of each stage | row 5 brace, gradient formula.
TOP = 10
NETY, TY = 56, 96
WY, BY, BH = 168, 202, 116
LEAD, BW, GAP = 62, 196, 80
QX = [LEAD, LEAD + BW + GAP]
FR = QX[1] + BW + LEAD
FY = BY + 40                           # forward realized-state arrows
KY = BY + 82                           # backward chain
for k, (c, p, n) in enumerate(STG):
    qx = QX[k]
    nx = qx + 32
    cx = nx + 35
    w.network(nx, NETY, output='output', prefix='n%d' % k)
    w.box('th%d' % k, cx - 15, TOP, 30, 24, r'\theta', role='model')
    seg(w, STRAIGHT, (cx, TOP + 24), (cx, NETY))                                # theta (shared) -> copy t
    tc = qx + BW - 36
    target(w, 'x%d' % k, tc, TY, c, w=44)
    seg(w, STRAIGHT, (nx + 70, TY), (tc - 22, TY))
    seg(w, STRAIGHT, (tc, TY + 23), (tc, BY))                                   # target -> its stage only
    wbox(w, 'w%d' % k, cx, WY, c)
    seg(w, STRAIGHT, (cx, WY - 13), (cx, NETY + 80))
    seg(w, STRAIGHT, (cx, WY + 13), (cx, BY))
    # incoming realized state: into the stage problem and into the policy (closed loop)
    bx = qx - 18
    if k == 0:                                     # x_0 = x*_0 and zeta_0: into copy 1 and into q_1
        seg(w, STRAIGHT, (30, TY + 23), (qx, FY), [(30, FY)])
        seg(w, STRAIGHT, (50, TY + 15), (nx, NETY + 55), [(nx - 12, TY + 15), (nx - 12, NETY + 55)])
        seg(w, STRAIGHT, (50, TY - 8), (nx, TY - 8))
    else:
        seg(w, STRAIGHT, (QX[0] + BW, FY), (qx, FY))
        seg(w, STRAIGHT, (bx, FY), (nx, NETY + 55), [(bx, NETY + 55)])
    w.box('q%d' % k, qx, BY, BW, BH, '', role='data')
    w.vertex('qx%d' % k, qx + 4, BY, BW - 8, BH, LEFT, stage(c, p))
    w.text('qt%d' % k, qx + BW - 30, BY + 3, 28, 22, r'q^\delta_{%s}' % c)
    # backward chain: dG_{t+1}/dx*_t enters from the right, beneath the forward arrow
    seg(w, AD, (qx + BW + (20 if k == 1 else GAP), KY), (qx + BW, KY))
    # the multiplier and the solution sensitivities (tool) of each stage
    lam_box(w, 'lb%d' % k, qx + 30, BY + BH + 24, r'\bar{\boldsymbol\lambda}_{%s}' % c, w=40)
    seg(w, AD, (qx + 30, BY + BH), (qx + 30, BY + BH + 24))
    w.vertex('s%d' % k, qx + BW - 128, BY + BH + 15, 118, 44, RBOX % ROLE['tool'], sens(c, p))
    w.edge('q%d' % k, 's%d' % k, 'tool-tail', exit=(1 - 69.0 / BW, 1), entry=(0.5, 0))
seg(w, STRAIGHT, (QX[0] + BW - 14, TY), (QX[1] + 32, TY))                       # zeta_1 -> copy 2
w.box('x0in', 10, TY - 23, 40, 46, r'\begin{gathered}\mathbf{x}_0\\[1pt] \boldsymbol\zeta_0\end{gathered}', role='model')
w.text('z1', QX[0] + BW + 30, TY - 22, 40, 20, r'\boldsymbol\zeta_1', left=True)
w.text('xs1', QX[0] + BW + 26, FY + 3, 40, 20, XS('1'), left=True)
RX = QX[1] + BW + 20                               # the remaining stages q_3, ..., q_T
w.vertex('rest', RX, BY, FR - 10 - RX, BH, 'rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#dedede;', r'$$\vdots$$')
seg(w, STRAIGHT, (QX[1] + BW, FY), (RX, FY))
w.vertex('g1', QX[0] + BW + 12, KY + 4, 56, 44, RED_TEXT, frac('dG_2', XS('1')))
LY = BY + BH + 70
w.brace(QX[0] + 4, QX[1] + BW - 4, LY)
GW, GH = 300, 54
gbox = ((QX[0] + QX[1] + BW) / 2.0 - GW / 2.0, LY + 18, GW, GH)
w.vertex('G', gbox[0], gbox[1], GW, GH, GRAD_BOX, GRAD)
w.frame(0, 0, FR, gbox[1] + GH + 10)

# ============================================================================================ compact
# time runs downward; the per-stage readouts (bar-lambda_t, sensitivities) live in the gradient formula
c = d.page('compact')
PX, TRK, BX, BW2, CH, CG = 44, 16, 86, 158, 112, 76
QY = [100, 100 + CH + CG]
EXF, EXB = BX + 46, BX + 118                    # forward realized state, backward chain
c.box('x0in', PX - 20, 34, 40, 46, r'\begin{gathered}\mathbf{x}_0\\[1pt] \boldsymbol\zeta_0\end{gathered}', role='model')
seg(c, STRAIGHT, (PX + 20, 57), (EXF, QY[0]), [(EXF, 57)])                      # x*_0 = x_0 -> q_1
for k, (cc, p, n) in enumerate(STG):
    qy = QY[k]
    piy = qy + 22
    c.box('pi%d' % k, PX - 13, piy - 13, 26, 26, r'\pi', role='model')
    c.box('th%d' % k, 4, piy - 10, 20, 20, r'\theta', role='model')
    seg(c, STRAIGHT, (24, piy), (PX - 13, piy))                            # theta (shared) -> copy t
    ty = qy + 84
    target(c, 'x%d' % k, PX, ty, cc, w=40)
    seg(c, STRAIGHT, (PX, piy + 13), (PX, ty - 23))
    seg(c, STRAIGHT, (PX + 20, ty), (BX, ty))                                   # target -> its stage only
    c.box('q%d' % k, BX, qy, BW2, CH, '', role='data')
    c.vertex('qx%d' % k, BX + 5, qy, BW2 - 10, CH, LEFT, stage_compact(cc, p))
    c.text('qt%d' % k, BX + BW2 - 28, qy + 3, 26, 22, r'q^\delta_{%s}' % cc)
seg(c, STRAIGHT, (PX, 80), (PX, QY[0] + 9))                                     # x_0, zeta_0 -> pi_1
# between the stages: x*_1 forward into q_2 and into pi_2, zeta_1 into pi_2, dG_2/dx*_1 backward
mid = QY[0] + CH
seg(c, STRAIGHT, (EXF, mid), (EXF, QY[1]))
c.text('xs1', EXF + 4, mid + 6, 30, 20, XS('1'), left=True)
seg(c, STRAIGHT, (EXF, mid + 14), (PX + 8, QY[1] + 9), [(PX + 8, mid + 14)])
seg(c, STRAIGHT, (PX - 8, QY[0] + 84 + 23), (PX - 8, QY[1] + 9))
seg(c, AD, (EXB, QY[1]), (EXB, mid))
c.vertex('g1', EXB + 4, mid + 14, 40, 44, RED_LEFT, frac('dG_2', XS('1')))
# after stage 2
end = QY[1] + CH
seg(c, STRAIGHT, (EXF, end), (EXF, end + 50))
c.text('xs2', EXF + 4, end + 6, 30, 20, XS('2'), left=True)
seg(c, AD, (EXB, end + 50), (EXB, end))
c.vertex('g2', EXB + 4, end + 3, 40, 44, RED_LEFT, frac('dG_3', XS('2')))
c.vertex('rest', BX, end + 50, BW2, 26, 'rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#dedede;', r'$$q^\delta_3,\dots,q^\delta_T$$')     # the remaining stages
GY = end + 96
c.vertex('G', 8, GY, BX + BW2 - 8, 56, GRAD_BOX, GRAD)
c.frame(0, 0, BX + BW2 + 10, GY + 68)
d.write(os.path.join(HERE, '..', 'decision-rules--causal-stages.drawio'))
