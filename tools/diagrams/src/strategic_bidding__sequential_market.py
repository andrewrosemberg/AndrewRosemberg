#!/usr/bin/env python3
"""strategic-bidding--sequential-market (round 4: action-reaction loop, after the author's presentation figure).

Message: the participant acts and the operator's two clearings react. The offer u enters day-ahead clearing
(and, for a physical participant, real-time clearing); day-ahead returns (q, pi) to the participant and the
state x to real-time clearing; real-time returns (g, lambda); the context xi enters each clearing.

Wide: participant problem on top, the two clearing problems side by side below, xi under each clearing.
Compact: participant, day-ahead and real-time stacked on one centre line; xi at the left of each clearing,
u to real time on the right, (g, lambda) returned around the outside to the top of the participant box."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _r2 import two, lab, e  # noqa: E402

PART = r'\max_{u\in\mathcal{B}}\ \rho_\xi\big[R(\mathbf{q},\boldsymbol\pi,\mathbf{g},\boldsymbol\lambda)\big]'
DA = two(r'\text{Day-ahead clearing}', r'\mathcal{M}^{\mathrm{DA}}(u,\xi)')
RT = two(r'\text{Real-time clearing}', r'\mathcal{M}^{\mathrm{RT}}(u,\mathbf{x},\xi)')
U, QP, GL, X = r'u', r'(\mathbf{q},\boldsymbol\pi)', r'(\mathbf{g},\boldsymbol\lambda)', r'\mathbf{x}'

d = Diagram()
# ------------------------------------------------------------------ wide
w = d.page('Page-1')
w.frame(0, 0, 520, 265)
w.box('p', 150, 20, 220, 44, PART, role='model')
w.box('da', 40, 124, 140, 50, DA, role='data')
w.box('rt', 340, 124, 140, 50, RT, role='data')
w.store('xi1', 90, 206, 40, 44, r'\xi')
w.store('xi2', 390, 206, 40, 44, r'\xi')
e(w, 'p', 'da', (0, 0.5), (30 / 140.0, 0), [(70, 42)])
lab(w, 64, 94, U, w=12, align='r')
e(w, 'da', 'p', (125 / 140.0, 0), (15 / 220.0, 1))
lab(w, 171, 94, QP, w=36, align='l')
e(w, 'p', 'rt', (205 / 220.0, 1), (15 / 140.0, 0))
lab(w, 361, 94, U, w=12, align='l')
e(w, 'rt', 'p', (110 / 140.0, 0), (1, 0.5), [(450, 42)])
lab(w, 456, 94, GL, w=36, align='l')
e(w, 'da', 'rt', (1, 0.5), (0, 0.5))
lab(w, 260, 138, X, w=16)
e(w, 'xi1', 'da', (0.5, 0), (0.5, 1))
e(w, 'xi2', 'rt', (0.5, 0), (0.5, 1))

# ------------------------------------------------------------------ compact
c = d.page('compact')
c.frame(0, 0, 295, 330)
c.box('p', 50, 25, 200, 44, PART, role='model')
c.box('da', 80, 119, 140, 50, DA, role='data')
c.box('rt', 80, 239, 140, 50, RT, role='data')
c.store('xi1', 15, 122, 40, 44, r'\xi')
c.store('xi2', 15, 242, 40, 44, r'\xi')
e(c, 'p', 'da', (50 / 200.0, 1), (20 / 140.0, 0))
lab(c, 106, 94, U, w=12, align='l')
e(c, 'da', 'p', (120 / 140.0, 0), (150 / 200.0, 1))
lab(c, 206, 94, QP, w=36, align='l')
e(c, 'da', 'rt', (0.5, 1), (0.5, 0))
lab(c, 156, 204, X, w=16, align='l')
e(c, 'p', 'rt', (1, 15 / 44.0), (1, 0.5), [(260, 40), (260, 264)])
lab(c, 251, 204, U, w=12)
e(c, 'rt', 'p', (0.5, 1), (0.5, 0), [(150, 305), (285, 305), (285, 10), (150, 10)])
lab(c, 217, 316, GL, w=36)
e(c, 'xi1', 'da', (1, 0.5), (0, 0.5))
e(c, 'xi2', 'rt', (1, 0.5), (0, 0.5))
d.write(os.path.join(HERE, '..', 'strategic-bidding--sequential-market.drawio'))
