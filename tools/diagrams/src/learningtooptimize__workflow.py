#!/usr/bin/env python3
"""learningtooptimize--workflow: the LearningToOptimize.jl pipeline (README "Flowchart Summary", docs/src/assets/L2O.png),
redrawn in the kit identity. Message: a parametric model and sampled parameters define a dataset of solved instances,
and the recorded solutions supervise a proxy.

Layout (grid, two lanes):
  Dataset   | {p_i} store -> parametric problem -> {y*_i, lambda*_i} store
  Training  |      (p_i)  -> network g_theta -> y_hat -> Loss <- (y*_i)     ; dashed return Loss -> network, beneath
API names (ProblemIterator, solve_batch, Recorder, Flux) belong to the caption."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402

PROB = r'$$\begin{aligned}\min_{\mathbf{y}}\ \ &f(\mathbf{y};p_i)\\ \text{s.t.}\ \ &\mathbf{y}\in\mathcal{Y}(p_i)\end{aligned}$$'
OUT = r'\begin{gathered}\mathbf{y}^\star_i\\[2pt] \boldsymbol\lambda^\star_i\end{gathered}'


def build(p, s):
    """s: geometry dict (wide or compact)."""
    X0, X1, SPLIT, Y1 = s['frame']
    p.frame(X0, 0, X1, Y1)
    p.line(X0, SPLIT, X1, SPLIT, dashed=True)
    p.lane_title(X0, 0, 'Dataset')
    p.lane_title(X0, SPLIT, 'Training')
    sx, sy, sw, sh = s['pstore']
    p.store('pin', sx, sy, sw, sh, r'\{p_i\}')
    bx, by, bw, bh = s['prob']
    p.box('prob', bx, by, bw, bh, PROB, role='data')
    ox, oy, ow, oh = s['ostore']
    p.store('pout', ox, oy, ow, oh, OUT)
    cy = by + bh / 2.0
    p.edge('pin', 'prob', 'value', exit=(1, (cy - sy) / sh), entry=(0, 0.5))
    p.edge('prob', 'pout', 'value', exit=(1, 0.5), entry=(0, (cy - oy) / oh))
    nx, ny = s['net']
    p.network(nx, ny, output='output', prefix='net')
    p.brace(nx + 20, nx + 70, ny + 82)
    p.text('ghat', nx + 15, ny + 94, 60, 22, r'\hat g_\theta')
    hx, hy = s['yhat']
    p.box('yhat', hx, hy, 30, 30, r'\hat{\mathbf{y}}_i', role='model')
    lx, ly, lw = s['loss']
    p.box('loss', lx, ly, lw, 30, r'\text{Loss}', role='loss')
    fy = hy + 15
    scx = sx + sw / 2.0
    p.edge('pin', None, 'value', exit=(0.5, 1), points=[(scx, ny + 40)], tgt_pt=(nx, ny + 40))
    p.edge(None, 'yhat', 'value', src_pt=(nx + 70, fy), entry=(0, 0.5))
    p.edge('yhat', 'loss', 'value', exit=(1, 0.5), entry=(0, 0.5))
    ocx = ox + ow / 2.0
    p.edge('pout', 'loss', 'value', exit=(0.5, 1), entry=((ocx - lx) / lw, 0))
    ry = ny + 72                                 # return beneath the forward path, into the output layer
    p.edge('loss', None, 'grad', exit=((ocx - lx) / lw, 1), points=[(ocx, ry)], tgt_pt=(nx + 70, ry))


d = Diagram()
build(d.page('Page-1'), dict(frame=(0, 450, 140, 300), pstore=(40, 34, 60, 80), prob=(150, 44, 170, 60),
                             ostore=(360, 34, 60, 80), net=(190, 175), yhat=(290, 200), loss=(345, 200, 90)))
build(d.page('compact'), dict(frame=(0, 252, 130, 280), pstore=(10, 38, 42, 64), prob=(64, 42, 122, 56),
                              ostore=(198, 38, 46, 64), net=(66, 160), yhat=(152, 185), loss=(198, 185, 48)))
d.write(os.path.join(HERE, '..', 'learningtooptimize--workflow.drawio'))
