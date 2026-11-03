#!/usr/bin/env python3
"""strategic-bidding--price-process: the statistical approach, drawn on the layout of sequential-market.

Message: the same participant and the same two boxes, but each clearing is replaced by a price law conditioned
on the context (real-time prices also on day-ahead prices). No offer arrow enters either box: prices do not
respond to u. Coordinates are those of sequential-market, so the pair reads as one substitution."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _r2 import two, lab, e  # noqa: E402

PI, LA = r'\tilde{\boldsymbol\pi}', r'\tilde{\boldsymbol\lambda}'
PART = r'\max_{u\in\mathcal{B}}\ \rho_\xi\big[R(u;%s,%s)\big]' % (PI, LA)
DA = two(r'\text{Day-ahead prices}', r'%s\sim\mathbb{P}(\cdot\mid\xi)' % PI)
RT = two(r'\text{Real-time prices}', r'%s\sim\mathbb{P}(\cdot\mid%s,\xi)' % (LA, PI))

d = Diagram()
# ------------------------------------------------------------------ wide
w = d.page('Page-1')
w.frame(0, 0, 520, 265)
w.box('p', 150, 20, 220, 44, PART, role='model')
w.box('da', 40, 124, 140, 50, DA, role='model')
w.box('rt', 340, 124, 140, 50, RT, role='model')
w.store('xi1', 90, 206, 40, 44, r'\xi')
w.store('xi2', 390, 206, 40, 44, r'\xi')
e(w, 'da', 'p', (125 / 140.0, 0), (15 / 220.0, 1))
lab(w, 171, 94, PI, w=16, align='l')
e(w, 'rt', 'p', (110 / 140.0, 0), (1, 0.5), [(450, 42)])
lab(w, 456, 94, LA, w=16, align='l')
e(w, 'da', 'rt', (1, 0.5), (0, 0.5))
lab(w, 260, 138, PI, w=16)
e(w, 'xi1', 'da', (0.5, 0), (0.5, 1))
e(w, 'xi2', 'rt', (0.5, 0), (0.5, 1))

# ------------------------------------------------------------------ compact
c = d.page('compact')
c.frame(0, 0, 295, 330)
c.box('p', 50, 25, 200, 44, PART, role='model')
c.box('da', 80, 119, 140, 50, DA, role='model')
c.box('rt', 80, 239, 140, 50, RT, role='model')
c.store('xi1', 15, 122, 40, 44, r'\xi')
c.store('xi2', 15, 242, 40, 44, r'\xi')
e(c, 'da', 'p', (120 / 140.0, 0), (150 / 200.0, 1))
lab(c, 206, 94, PI, w=16, align='l')
e(c, 'da', 'rt', (0.5, 1), (0.5, 0))
lab(c, 156, 204, PI, w=16, align='l')
e(c, 'rt', 'p', (0.5, 1), (0.5, 0), [(150, 305), (285, 305), (285, 10), (150, 10)])
lab(c, 217, 316, LA, w=16)
e(c, 'xi1', 'da', (1, 0.5), (0, 0.5))
e(c, 'xi2', 'rt', (1, 0.5), (0, 0.5))
d.write(os.path.join(HERE, '..', 'strategic-bidding--price-process.drawio'))
