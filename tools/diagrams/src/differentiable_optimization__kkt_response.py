#!/usr/bin/env python3
"""differentiable-optimization--kkt-response: one solve forward, one adjoint solve back (DiffOpt.jl).

Solve lane: w -> phi_theta -> p -> JuMP model -> Solver -> z* -> L. Differentiate lane: the adjoint system at z*,
fed by z* and by the loss gradient, run by DiffOpt; its parameter cotangent returns to the learned map, parallel
beneath the forward path. Nothing returns to the solver: its iterations are not differentiated."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram, BOX, ROLE  # noqa: E402

MODEL = '\\begin{aligned}\n\\min_{\\mathbf{y}\\ge\\mathbf{0}} &\\quad f(\\mathbf{y};p) \\\\\n\\text{s.t.} &\\quad c(\\mathbf{y};p)=\\mathbf{0}\n\\end{aligned}'
LOSS = r'L(\mathbf{y}^\star,\boldsymbol\lambda^\star;w)'
ADJ = r'$$\begin{gathered}\textit{DiffOpt}\\ M^{\top}v=\nabla_{\mathbf{z}}L\\ \bar p=\partial_pL-N^{\top}v\end{gathered}$$'

d = Diagram()
w = d.page('Page-1')
w.frame(200, 470, 770, 720)
w.line(200, 622, 770, 622, dashed=True)
w.lane_title(200, 470, 'Solve', inset=True)
w.lane_title(200, 622, 'Differentiate', inset=True)
w.store('w', 212, 515, 40, 60, 'w')
w.network(270, 505, prefix='phi')
w.brace(290, 330, 588)
w.text('phl', 270, 598, 80, 24, r'\phi_\theta')
w.box('p', 358, 530, 30, 30, 'p', role='model')
w.vertex('mbox', 406, 516.88, 112.5, 56.25, BOX % ROLE['data'])
w.block('mtext', 407.13, 505, 103.12, 60, MODEL)
w.brace(406, 518.5, 578)
w.text('jump', 412, 590, 100, 24, r'\text{JuMP model}')
w.box('solver', 536.5, 530, 60, 30, r'\textit{Solver}', role='tool')
w.box('zs', 614.5, 530, 30, 30, r'\mathbf{z}^\star', role='data')
w.box('loss', 662.5, 525, 95, 40, LOSS, role='loss')
w.box('adj', 417.5, 640, 125, 66, ADJ, role='tool')
w.box('seed', 614.75, 658, 110, 30, r'(\mathbf{z}^\star,\nabla_{\mathbf{z}}L)', role='data')
w.edge('w', None, 'value', exit=(1, 0.5), tgt_pt=(270, 545))
w.edge(None, 'p', 'value', src_pt=(340, 545), entry=(0, 0.5))
w.edge('p', 'mbox', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('mbox', 'solver', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('solver', 'zs', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('zs', 'loss', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('zs', 'seed', 'value', exit=(0.5, 1), entry=(0.1341, 0))
w.edge('loss', 'seed', 'grad', exit=(0.5, 1), entry=(0.8705, 0))
w.text('gz', 717, 586, 44, 22, r'\nabla_{\mathbf{z}}L', left=True)
w.edge('seed', 'adj', 'value', exit=(0, 0.5), entry=(1, 0.5))
w.edge('adj', 'phi-h4-7', 'grad', exit=(0, 0.5), entry=(0.5, 1), points=[(335, 673)])
w.text('pbar', 361, 649, 30, 18, r'\bar p')

c = d.page('compact')
c.frame(200, 470, 452, 815)
c.line(200, 640, 340, 640, dashed=True)
c.line(340, 640, 340, 815, dashed=True)
c.lane_title(200, 470, 'Solve', inset=True)
c.lane_title(200, 640, 'Differentiate', inset=True)
c.store('w', 207, 505, 40, 60, 'w')
c.network(259, 495, prefix='phi')
c.brace(279, 319, 578)
c.text('phl', 259, 587, 80, 22, r'\phi_\theta')
c.box('p', 380, 520, 30, 30, 'p', role='model')
c.box('mbox', 347.5, 580, 95, 30, r'\text{JuMP model}', role='data')
c.box('solver', 365, 635, 60, 30, r'\textit{Solver}', role='tool')
c.box('zs', 380, 690, 30, 30, r'\mathbf{z}^\star', role='data')
c.box('loss', 380, 750, 30, 30, 'L', role='loss')
c.box('adj', 212, 672, 120, 66, ADJ, role='tool')
c.edge('w', None, 'value', exit=(1, 0.5), tgt_pt=(259, 535))
c.edge(None, 'p', 'value', src_pt=(329, 535), entry=(0, 0.5))
c.edge('p', 'mbox', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('mbox', 'solver', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('solver', 'zs', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('zs', 'loss', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('zs', 'adj', 'value', exit=(0, 0.5), entry=(1, 0.3485))
c.edge('loss', 'adj', 'grad', exit=(0, 0.5), entry=(0.5, 1), points=[(272, 765)])
c.text('gz', 286, 771, 36, 20, r'\nabla_{\mathbf{z}}L')  # under its own segment, left of the lane split
c.edge('adj', 'phi-h4-7', 'grad', exit=(0.9333, 0), entry=(0.5, 1))
c.text('pbar', 300, 612, 18, 20, r'\bar p')
d.write(os.path.join(HERE, '..', 'differentiable-optimization--kkt-response.drawio'))
