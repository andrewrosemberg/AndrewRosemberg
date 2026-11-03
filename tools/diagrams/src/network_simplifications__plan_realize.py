#!/usr/bin/env python3
"""network-simplifications--plan-realize (round 3, rubric 49 + critic review).

Message: SDDP fits the cuts by backward passes on the planning model at the states that forward passes reach on
the operating model; only the cuts cross into operation, which solves each stage on the operating model and hands
its state to the next stage.

Wide (lanes stacked):  Planning:  in-sample w_t -> Forward (Y^op) -x_t-> Backward (Y^plan) -(alpha,beta)-> Cuts,
                                   cuts return to Forward directly above the row;
                       Operation: out-of-sample w_t -> stage solve (Y^op, with cuts) -x_t-> stage t+1.
Compact: the same, stacked in one column (return on the right of the planning column)."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _r2 import two, lab, e  # noqa: E402

YP, YO = r'\mathcal{Y}_t^{\mathrm{plan}}', r'\mathcal{Y}_t^{\mathrm{op}}'
VH = r'\widehat{\mathcal{V}}_{t+1}'
FWD = two(r'\text{Forward pass}', r'\text{on }' + YO)
BWD = two(r'\text{Backward pass}', r'\text{on }' + YP)
CUT = two(VH, r'\text{cuts}')
R1 = (r'$$\begin{aligned}&\min\ f(\mathbf{x}_t,\mathbf{y}_t)+' + VH + r'(\mathbf{x}_t)\\'
      r'&\text{s.t. }\mathbf{y}_t\in' + YO + r'(\mathbf{x}_{t-1},\mathbf{x}_t;w_t)\end{aligned}$$')
R1C = (r'$$\begin{aligned}&\min\ f(\mathbf{x}_t,\mathbf{y}_t)\\&\quad+' + VH + r'(\mathbf{x}_t)\\'
       r'&\text{s.t. }\mathbf{y}_t\in' + YO + r'(\mathbf{x}_{t-1},\mathbf{x}_t;w_t)\end{aligned}$$')
JOP = r'J^{\mathrm{op}}'

d = Diagram()
SOLVE = two(r'\text{Stage solve}', r'\text{on }' + YO)
NEXT = r'\text{stage }t+1'
# ------------------------------------------------------------------ wide
w = d.page('Page-1')
W, SPL, H = 500, 155, 270
Y1, Y2 = 95, 220
w.frame(0, 0, W, H)
w.line(0, SPL, W, SPL, dashed=True)
w.lane_title(0, 0, 'Planning', inset=True)
w.lane_title(0, SPL, 'Operation', inset=True)
w.store('sin', 10, Y1 - 35, 70, 70, two('w_t', r'\text{in-sample}'))
w.box('f', 110, Y1 - 22, 100, 44, FWD, role='data')
w.box('b', 250, Y1 - 22, 100, 44, BWD, role='data')
w.store('c', 420, Y1 - 35, 70, 70, CUT)
e(w, 'sin', 'f', (1, 0.5), (0, 0.5))
e(w, 'f', 'b', (1, 0.5), (0, 0.5))
lab(w, 230, Y1 - 12, r'\mathbf{x}_t', w=24)
e(w, 'b', 'c', (1, 0.5), (0, 0.5))
lab(w, 385, Y1 - 12, r'(\alpha_k,\boldsymbol\beta_k)', w=58)
e(w, 'c', 'f', (0.5, 0), (0.5, 0), [(455, 42), (160, 42)])
w.store('sout', 10, Y2 - 35, 104, 70, two('w_t', r'\text{out-of-sample}'))
w.box('r1', 144, Y2 - 30, 190, 60, R1, role='data')
w.box('nx', 374, Y2 - 18, 84, 36, NEXT, role='data')
e(w, 'sout', 'r1', (1, 0.5), (0, 0.5))
e(w, 'r1', 'nx', (1, 0.5), (0, 0.5))
lab(w, 354, Y2 - 12, r'\mathbf{x}_t', w=24)
e(w, 'c', 'r1', (0.5, 1), (0.5, 0), [(455, 172), (239, 172)])

# ------------------------------------------------------------------ compact
c = d.page('compact')
CW, SP, CX = 234, 350, 117
c.frame(0, 0, CW, 512)
c.line(0, SP, CW, SP, dashed=True)
c.lane_title(0, 0, 'Planning', inset=True)
c.lane_title(0, SP, 'Operation', inset=True)
c.store('sin', CX - 35, 18, 70, 66, two('w_t', r'\text{in-sample}'))
c.box('f', CX - 48, 103, 96, 44, FWD, role='data')
c.box('b', CX - 48, 178, 96, 44, BWD, role='data')
c.store('c', CX - 33, 255, 66, 70, CUT)
e(c, 'sin', 'f', (0.5, 1), (0.5, 0))
e(c, 'f', 'b', (0.5, 1), (0.5, 0))
lab(c, CX - 6, 162.5, r'\mathbf{x}_t', w=22, align='r')
e(c, 'b', 'c', (0.5, 1), (0.5, 0))
lab(c, CX - 6, 236, r'(\alpha_k,\boldsymbol\beta_k)', w=56, align='r')
e(c, 'c', 'f', (1, 0.5), (1, 0.5), [(190, 290), (190, 125)])
c.store('sout', 6, 378, 104, 66, two('w_t', r'\text{out-of-sample}'))
c.box('r1', 128, 389, 96, 44, SOLVE, role='data')
c.box('nx', 134, 463, 84, 36, NEXT, role='data')
e(c, 'sout', 'r1', (1, 0.5), (0, 0.5))
e(c, 'c', 'r1', (0.5, 1), (0.5, 0), [(CX, 365), (176, 365)])
e(c, 'r1', 'nx', (0.5, 1), (0.5, 0))
lab(c, 170, 448, r'\mathbf{x}_t', w=22, align='r')
d.write(os.path.join(HERE, '..', 'network-simplifications--plan-realize.drawio'))
