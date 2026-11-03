#!/usr/bin/env python3
"""network-simplifications--model-relations (round 3, rubric 49 + critic review).

Message: the relaxations form a chain of feasible-set inclusions from NFA down to AC (arrow A -> B: A contains B,
in dispatch and storage decisions); the DC approximations descend from NFA but are not nested with AC.
All boxes are mathematical problems (orange); the text names the class.
Wide: 3 x 2 grid, every edge straight. Compact: left column NFA, SOC, SDP, AC; right column DC, DCLL;
"not nested" sits under the horizontal DCLL-AC segment."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402
from _r2 import two, lab, e, DOTTED  # noqa: E402

SUP = r'\supseteq'
WIDE = {
    'nfa': (two(r'\text{NFA relaxation}', r'\text{no KVL}'), 'model'),
    'soc': (two(r'\text{SOC relaxation}', r'|w_{nm}|^2\le w_{nn}w_{mm}'), 'model'),
    'sdp': (two(r'\text{SDP relaxation}', r'W\succeq 0'), 'model'),
    'ac': (two(r'\text{AC power flow}', r'W=\mathbf{v}\mathbf{v}^{*}'), 'data'),
    'dc': (two(r'\text{DC approximation}', r'\text{linear KVL, lossless}'), 'output'),
    'dcll': (two(r'\text{DCLL approximation}', r'\text{quadratic losses}'), 'output'),
}
COMPACT = {
    'nfa': (two(r'\text{NFA}', r'\text{relaxation}'), 'model'),
    'soc': (two(r'\text{SOC}', r'\text{relaxation}'), 'model'),
    'sdp': (two(r'\text{SDP}', r'\text{relaxation}'), 'model'),
    'ac': (two(r'\text{AC}', r'\text{power flow}'), 'data'),
    'dc': (two(r'\text{DC}', r'\text{approximation}'), 'output'),
    'dcll': (two(r'\text{DCLL}', r'\text{approximation}'), 'output'),
}

d = Diagram()
from _r2 import three  # noqa: E402
NAMES = {'nfa': ('NFA', 'relaxation', r'\text{no KVL}'), 'soc': ('SOC', 'relaxation', r'|w_{nm}|^2\le w_{nn}w_{mm}'),
         'sdp': ('SDP', 'relaxation', r'W\succeq 0'), 'ac': ('AC', 'power flow', r'W=\mathbf{v}\mathbf{v}^{*}'),
         'dc': ('DC', 'approximation', r'\text{linear KVL, lossless}'), 'dcll': ('DCLL', 'approximation', r'\text{quadratic losses}')}
# ------------------------------------------------------------------ wide
w = d.page('Page-1')
BW, BH, G, M = 136, 62, 84, 8
X = [M + k * (BW + G) for k in range(3)]
R1, R2 = M + BH / 2.0, M + BH + 40 + BH / 2.0
w.frame(0, 0, X[2] + BW + M, R2 + BH / 2.0 + M)
pos = {'nfa': (0, R1), 'soc': (1, R1), 'sdp': (2, R1), 'dc': (0, R2), 'dcll': (1, R2), 'ac': (2, R2)}
for k, (i, y) in pos.items():
    a, b, c3 = NAMES[k]
    w.box(k, X[i], y - BH / 2.0, BW, BH, three(r'\text{%s}' % a, r'\text{%s}' % b, c3), role='data')
for a, b, i in (('nfa', 'soc', 1), ('soc', 'sdp', 2), ('dc', 'dcll', 1)):
    e(w, a, b, (1, 0.5), (0, 0.5))
    lab(w, X[i] - G / 2.0, pos[a][1] - 12, SUP, w=20)
for a, b, i in (('nfa', 'dc', 0), ('sdp', 'ac', 2)):
    e(w, a, b, (0.5, 1), (0.5, 0))
    lab(w, X[i] + BW / 2.0 + 13, (R1 + R2) / 2.0, SUP, w=16)
e(w, 'dcll', 'ac', (1, 0.5), (0, 0.5), kind='dotted')
lab(w, X[2] - G / 2.0, R2 - 13, r'\text{not nested}', w=G - 10)

# ------------------------------------------------------------------ compact
c = d.page('compact')
CB, CH, GX, GY, M = 104, 44, 14, 26, 6
CX = [M, M + CB + GX]
CC = [x + CB / 2.0 for x in CX]
YS = [M + CH / 2.0 + k * (CH + GY) for k in range(4)]
c.frame(0, 0, CX[1] + CB + M, YS[3] + CH / 2.0 + 16)
cpos = {'nfa': (0, 0), 'soc': (0, 1), 'sdp': (0, 2), 'ac': (0, 3), 'dc': (1, 1), 'dcll': (1, 2)}
for k, (i, j) in cpos.items():
    a, b, _ = NAMES[k]
    c.box(k, CX[i], YS[j] - CH / 2.0, CB, CH, two(r'\text{%s}' % a, r'\text{%s}' % b), role='data')
for a, b, i, j in (('nfa', 'soc', 0, 0), ('soc', 'sdp', 0, 1), ('sdp', 'ac', 0, 2), ('dc', 'dcll', 1, 1)):
    e(c, a, b, (0.5, 1), (0.5, 0))
    lab(c, CC[i] + 13, (YS[j] + YS[j + 1]) / 2.0, SUP, w=16)
e(c, 'nfa', 'dc', (1, 0.5), (0.5, 0), [(CC[1], YS[0])])
lab(c, CC[1] + 13, (YS[0] + YS[1] - CH / 2.0) / 2.0 + 4, SUP, w=16)
e(c, 'dcll', 'ac', (0.5, 1), (1, 0.5), [(CC[1], YS[3])], kind='dotted')
lab(c, (CX[0] + CB + CC[1]) / 2.0, YS[3] + 13, r'\text{not nested}', w=64)
d.write(os.path.join(HERE, '..', 'network-simplifications--model-relations.drawio'))
