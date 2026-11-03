"""Shared pieces of the Policies training diagrams (decision-rules--two-stage, --parallel-stages, --causal-stages).

The policy band is the proposal's figure (figures/diagram_tsddr_strict.pdf): one recurrent network unrolled over the
stages, every copy carrying the same parameters theta, each copy reading w_t and the previous (target, latent state)
and emitting the next. Drawn with the kit's primitives in the TS-DDR paper identity: network glyph, blue for the
learned model and its outputs, orange for sampled data (w_t), TeX red for the parameters a problem receives, the AD
dark red #AC3C0C with the 8-8 dash for multipliers and gradients, a pink loss box for the gradient formula.

Design rubric (.editorial/49): grid layout, no crossings, no edge around the frame. Hence ONE theta box whose bus
runs directly above the policy row, with a drop into every copy (the sharing is drawn, not repeated), and no edge
from the gradient back to theta (the formula names d/dtheta; the caption says where it goes).

Wide layout: time runs left to right, stages 1, 2, ..., T. Compact layout: time runs downward."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import ROLE, RBOX, TEXT  # noqa: E402

ADR = '#AC3C0C'
AD = 'endArrow=classic;html=1;rounded=0;dashed=1;dashPattern=8 8;strokeColor=%s;' % ADR      # dual return
STRAIGHT = 'endArrow=classic;html=1;rounded=0;'
LINE = 'endArrow=none;html=1;rounded=0;'
OUTLINE = 'rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=%s;' % ADR
LEFT = 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;'
RED_TEXT = TEXT + 'fontColor=%s;' % ADR
RED_LEFT = LEFT + 'fontColor=%s;' % ADR
GRAD_BOX = RBOX % ROLE['loss'] + 'fontColor=%s;' % ADR

GRAD = (r'$$\frac{d\mathcal{Q}(\mathbf{w};\theta)}{d\theta}=\sum_{t=1}^{T}\boldsymbol\lambda_t^{\top}'
        r'\,\frac{d\hat{\mathbf{x}}_t}{d\theta}$$')
LAMS = [r'\boldsymbol\lambda_1=\bar{\boldsymbol\lambda}_1+\boldsymbol\mu_2',
        r'\boldsymbol\lambda_2=\bar{\boldsymbol\lambda}_2+\boldsymbol\mu_3',
        r'\boldsymbol\lambda_T=\bar{\boldsymbol\lambda}_T']


def red(s):
    return r'{\color{red}%s}' % s


def seg(p, style, a, b, pts=()):
    """Free polyline from a to b (draw.io px), through pts."""
    geo = '<mxPoint x="%g" y="%g" as="sourcePoint" /><mxPoint x="%g" y="%g" as="targetPoint" />' % (a + b)
    if pts:
        geo += '<Array as="points">%s</Array>' % ''.join('<mxPoint x="%g" y="%g" />' % q for q in pts)
    p.add('<mxCell id="%s" value="" style="%s" edge="1" parent="1"><mxGeometry width="50" height="50" '
          'relative="1" as="geometry">%s</mxGeometry></mxCell>' % (p._id(None), style, geo))


def target(p, cid, cx, cy, sub, w=40, h=46):
    """A policy output: the target and the latent state of stage `sub` (blue: learned model outputs)."""
    tex = r'\begin{gathered}\hat{\mathbf{x}}_{%s}\\[1pt] \boldsymbol\zeta_{%s}\end{gathered}' % (sub, sub)
    return p.box(cid, cx - w / 2.0, cy - h / 2.0, w, h, tex, role='model')


def wbox(p, cid, cx, cy, sub):
    """A sampled realization w_t (orange: data)."""
    return p.box(cid, cx - 15, cy - 13, 30, 26, 'w_{%s}' % sub, role='data')


def lam_box(p, cid, cx, y, tex, w=112):
    """A multiplier (outlined in AD red, as the Duality box of the TS-DDR paper figure)."""
    return p.vertex(cid, cx - w / 2.0, y, w, 26, OUTLINE, '$$%s$$' % tex)


# ------------------------------------------------------------------------------------------- wide band
SUBS = ['0', '1', '2', 'T-1', 'T']
PAIRS = [(0, 1, '1'), (1, 2, '2'), (3, 4, 'T')]     # (incoming target, outgoing target, stage)
NETY, TY, TOP = 56, 96, 10                          # net top, policy-row centre line, theta box top
WY = 168                                            # centre of the w_t boxes
BY = 202                                            # top of the recourse row


def wide_policy(p, TC):
    """Unrolled policy: targets centred at TC, a net between consecutive targets, the parameters theta on top of every
    copy (the same theta: the rule is shared), w_t under each copy feeding the copy (up) and the recourse below (down,
    to y=BY). Returns the x of every copy's centre (where w_t enters the recourse)."""
    for k, (cx, s) in enumerate(zip(TC, SUBS)):
        target(p, 'x%d' % k, cx, TY, s, w=44 if s == 'T-1' else 40)
    p.text('pdots', (TC[2] + TC[3]) / 2.0 - 15, TY - 10, 30, 20, r'\cdots')
    centres = []
    for k, (a, b, t) in enumerate(PAIRS):
        nx = (TC[a] + TC[b]) / 2.0 - 35
        cx = nx + 35
        centres.append(cx)
        p.network(nx, NETY, output='output', prefix='n%d' % k)
        seg(p, STRAIGHT, (TC[a] + (22 if a == 3 else 20), TY), (nx, TY))      # (x_{t-1}, zeta_{t-1}) -> copy t
        seg(p, STRAIGHT, (nx + 70, TY), (TC[b] - 20, TY))                      # copy t -> (x_t, zeta_t)
        p.box('th%d' % k, cx - 15, TOP, 30, 24, r'\theta', role='model')
        seg(p, STRAIGHT, (cx, TOP + 24), (cx, NETY))                           # theta -> copy t
        wbox(p, 'w%d' % k, cx, WY, t)
        seg(p, STRAIGHT, (cx, WY - 13), (cx, NETY + 80))                       # w_t -> copy t
        seg(p, STRAIGHT, (cx, WY + 13), (cx, BY))                              # w_t -> recourse
    return centres


# compact (phone) grid, shared by the two-stage and parallel-stages phone versions: the wide figure in miniature,
# stages 1 and 2. Row 1: theta above each policy copy | row 2: x_0 -> pi -> x_1 -> pi -> x_2 | row 3: w_t under each
# copy | row 4: recourse (q_1 | q_2, or one Q) | row 5: multipliers | row 6: gradient.
CQ = [(10, 112), (132, 112)]               # recourse columns (left, width)
CT = [30, 127, 224]                        # target centres
CP = [78.5, 175.5]                         # policy-copy centres
CTY, CWY, CQY = 64, 104, 144               # target row centre, w row centre, recourse top


def compact_policy(p):
    for k, cx in enumerate(CT):
        target(p, 'x%d' % k, cx, CTY, str(k))
    for k, cx in enumerate(CP):
        p.box('pi%d' % k, cx - 13, CTY - 13, 26, 26, r'\pi', role='model')
        seg(p, STRAIGHT, (CT[k] + 20, CTY), (cx - 13, CTY))
        seg(p, STRAIGHT, (cx + 13, CTY), (CT[k + 1] - 20, CTY))
        p.box('th%d' % k, cx - 11, 8, 22, 20, r'\theta', role='model')
        seg(p, STRAIGHT, (cx, 28), (cx, CTY - 13))
        p.box('w%d' % k, cx - 12, CWY - 11, 24, 22, 'w_{%d}' % (k + 1), role='data')
        seg(p, STRAIGHT, (cx, CWY - 11), (cx, CTY + 13))
        seg(p, STRAIGHT, (cx, CWY + 11), (cx, CQY))
