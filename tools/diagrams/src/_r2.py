"""Small helpers shared by the round-2 redesigns (plan-realize, model-relations, calibration-loop,
sequential-market, derivative-path). Kit styles only; labels are free math cells placed 6-8 px off a
straight edge segment, so every label belongs to one edge."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import EDGE, TEXT  # noqa: E402

LEFT = 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;'
DOTTED = 'endArrow=none;dashed=1;html=1;dashPattern=1 2;strokeWidth=2;'


def two(a, b):
    return r'$$\begin{gathered}%s\\ %s\end{gathered}$$' % (a, b)


def lab(p, x, y, tex, w=120, h=20, align='c'):
    """Label centred at (x, y) (align='c'), or starting at x (align='l'), or ending at x (align='r')."""
    if align == 'c':
        return p.vertex(None, x - w / 2.0, y - h / 2.0, w, h, TEXT, '$$%s$$' % tex)
    if align == 'l':
        return p.vertex(None, x, y - h / 2.0, w, h, LEFT, '$$%s$$' % tex)
    # right-aligned text is not in the reference styles: centre a cell whose width is the label's width
    return p.vertex(None, x - w, y - h / 2.0, w, h, TEXT, '$$%s$$' % tex)


def e(p, s, t, exit, entry, pts=(), kind='value', extra=''):
    p.edge(s, t, kind, exit=exit, entry=entry, points=pts, extra=extra)


def free(p, style, a, b, pts=()):
    """Edge between free points (no source/target)."""
    p.add('<mxCell id="%s" value="" style="%s" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
          '<mxPoint x="%g" y="%g" as="sourcePoint" /><mxPoint x="%g" y="%g" as="targetPoint" />%s</mxGeometry></mxCell>'
          % (p._id(None), style, a[0], a[1], b[0], b[1],
             ('<Array as="points">%s</Array>' % ''.join('<mxPoint x="%g" y="%g" />' % q for q in pts)) if pts else ''))

# orthogonal dotted connector without heads (TS-DDR "Dotted Line" pattern): a relation that is not a flow
EDGE.setdefault('dotted', EDGE['value'] + 'endArrow=none;dashed=1;dashPattern=1 2;strokeWidth=2;')


def three(a, b, c):
    return r'$$\begin{gathered}%s\\ %s\\ %s\end{gathered}$$' % (a, b, c)
