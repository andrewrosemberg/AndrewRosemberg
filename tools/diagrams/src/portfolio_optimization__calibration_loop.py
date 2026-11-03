#!/usr/bin/env python3
"""portfolio-optimization--calibration-loop (round 3, rubric 49 + critic review).

Message: the size eps of the ambiguity set is chosen by comparing the certificate with the holdout loss of the
decision it produced; the fitted law and the calibrated eps are handed to deployment together.

Wide (lanes stacked, columns shared by both rows):
  A:  P^(.|w) -> A_eps(w) -> Robust solve -(u^,J^)-> rho_holdout vs J^      return: comparison -> A_eps above the row
  B:  fit (up into P^)   (P^, eps) handoff      holdout (up into comparison)
  C:  w -> A_eps(w) -> Robust solve -> (u^(w), J^(w))                     handoff -> A_eps(w) crosses the split
Compact: Calibration column (fit, P^, A_eps, solve, comparison, holdout) | Deployment column (w, A_eps(w), solve,
output); the handoff (P^, eps) is the one edge crossing the vertical split."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _r2 import two, lab, e  # noqa: E402
from kit import TEXT  # noqa: E402

EST = r'\widehat{\mathbb{P}}(\cdot\mid w)'
SET = r'\mathcal{A}_\varepsilon(w)'
DRO = r'\min_{u}\ \sup_{\mathbb{Q}\in\mathcal{A}}\ \rho_{\mathbb{Q}}[-u^{\top}\xi]'
OUT = r'\hat u_\varepsilon,\ \widehat J_\varepsilon'
OUTD = r'\hat u_\varepsilon(w),\ \widehat J_\varepsilon(w)'
EVAL = r'\rho_{\text{holdout}}[-\hat u_\varepsilon^{\top}\xi]\ \text{vs.}\ \widehat J_\varepsilon'
EPS = r'\varepsilon'

d = Diagram()
SOLVE = r'\text{Robust solve}'
SOLVE2 = two(r'\text{Robust}', r'\text{solve}')
CMP = r'\rho_{\text{holdout}}\ \text{vs.}\ \widehat J_\varepsilon'
HAND = r'(\widehat{\mathbb{P}},\,\varepsilon)'
# ------------------------------------------------------------------ wide
w = d.page('Page-1')
W, SPL, H = 500, 195, 282
YA, YB, YC = 75, 145, 250
C0, C1, C2, C3 = 45, 155, 275, 435
w.frame(0, 0, W, H)
w.line(0, SPL, W, SPL, dashed=True)
w.lane_title(0, 0, 'Calibration', inset=True)
w.lane_title(0, SPL, 'Deployment', inset=True)
w.box('est', C0 - 35, YA - 18, 70, 36, EST, role='model')
w.box('set', C1 - 35, YA - 18, 70, 36, SET, role='model')
w.box('dro', C2 - 45, YA - 18, 90, 36, SOLVE, role='data')
w.box('ev', C3 - 55, YA - 18, 110, 36, CMP, role='loss')
w.store('fit', C0 - 30, YB - 25, 60, 50, r'\text{fit}')
w.box('hand', C1 - 35, YB - 18, 70, 36, HAND, role='model')
w.store('ho', C3 - 30, YB - 25, 60, 50, r'\text{holdout}')
w.store('w', C0 - 30, YC - 25, 60, 50, 'w')
w.box('setd', C1 - 35, YC - 18, 70, 36, SET, role='model')
w.box('drod', C2 - 45, YC - 18, 90, 36, SOLVE, role='data')
w.box('outd', C3 - 55, YC - 18, 110, 36, OUTD, role='data')
for a, b in (('est', 'set'), ('set', 'dro'), ('dro', 'ev'), ('w', 'setd'), ('setd', 'drod'), ('drod', 'outd')):
    e(w, a, b, (1, 0.5), (0, 0.5))
lab(w, (C2 + 45 + C3 - 55) / 2.0, YA - 12, OUT, w=56)
e(w, 'fit', 'est', (0.5, 0), (0.5, 1))
e(w, 'ho', 'ev', (0.5, 0), (0.5, 1))
e(w, 'ev', 'set', (0.5, 0), (0.5, 0), [(C3, 40), (C1, 40)], kind='grad')
lab(w, (C1 + C3) / 2.0, 29, r'\text{choose }\varepsilon', w=70)
e(w, 'set', 'hand', (0.5, 1), (0.5, 0))
e(w, 'hand', 'setd', (0.5, 1), (0.5, 0))

# ------------------------------------------------------------------ compact
c = d.page('compact')
CW, SPX, H2 = 234, 152, 392
L, R = 74, 193
c.frame(0, 0, CW, H2)
c.line(SPX, 0, SPX, H2, dashed=True)
for x0, x1, word in ((0, SPX, 'Calibration'), (SPX, CW, 'Deployment')):   # title centred in its lane
    c.vertex(None, x0, 0, x1 - x0, 30, TEXT, '$$\\text{%s}$$' % word)
c.store('fit', L - 30, 32, 60, 46, r'\text{fit}')
c.box('est', L - 35, 98, 70, 30, EST, role='model')
c.box('set', L - 30, 150, 60, 30, SET, role='model')
c.box('dro', L - 45, 202, 90, 30, SOLVE, role='data')
c.box('ev', L - 52.5, 268, 105, 30, CMP, role='loss')
c.store('ho', L - 30, 320, 60, 46, r'\text{holdout}')
e(c, 'fit', 'est', (0.5, 1), (0.5, 0))
e(c, 'est', 'set', (0.5, 1), (0.5, 0))
e(c, 'set', 'dro', (0.5, 1), (0.5, 0))
e(c, 'dro', 'ev', (0.5, 1), (0.5, 0))
lab(c, L + 6, 250, OUT, w=48, align='l')
e(c, 'ho', 'ev', (0.5, 0), (0.5, 1))
e(c, 'ev', 'set', (0, 0.5), (0, 0.5), [(10, 283), (10, 165)], kind='grad')
lab(c, 20, 224, EPS, w=14)
c.store('w', R - 25, 90, 50, 46, 'w')
c.box('setd', R - 30, 150, 60, 30, SET, role='model')
c.box('drod', R - 30, 198, 60, 44, SOLVE2, role='data')
c.box('outd', R - 32, 262, 64, 44, two(r'\hat u_\varepsilon(w)', r'\widehat J_\varepsilon(w)'), role='data')
e(c, 'set', 'setd', (1, 0.5), (0, 0.5))
lab(c, (L + 30 + SPX) / 2.0, 152, HAND, w=44)
e(c, 'w', 'setd', (0.5, 1), (0.5, 0))
e(c, 'setd', 'drod', (0.5, 1), (0.5, 0))
e(c, 'drod', 'outd', (0.5, 1), (0.5, 0))
d.write(os.path.join(HERE, '..', 'portfolio-optimization--calibration-loop.drawio'))
