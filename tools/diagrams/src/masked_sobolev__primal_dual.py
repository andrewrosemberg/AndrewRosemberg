#!/usr/bin/env python3
"""masked-sobolev--primal-dual: self-supervised primal-dual learning (Park & Van Hentenryck 2023), kit identity.

Wide: the two losses sit side by side between the two output boxes, so each output reaches both losses
by a short tree (no crossing); the frozen copy sits between the two networks and feeds the dual loss.
Compact: one column, primal row over dual row."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram  # noqa: E402

PRIMAL = r'\mathcal{L}_\rho(\hat{\mathbf{y}},\hat{\boldsymbol\lambda},\hat{\boldsymbol\mu};p)'   # augmented Lagrangian (page display)
DUAL = r'\big\lVert(\hat{\boldsymbol\lambda},\hat{\boldsymbol\mu})-(\boldsymbol\lambda_k+\rho c,\,[\boldsymbol\mu_k-\rho h]_+)\big\rVert'
DOUT = r'(\hat{\boldsymbol\lambda},\hat{\boldsymbol\mu})'
FROZEN = r'\Lambda_{\psi}^{(k)}\ (\text{frozen})'   # no second-level script

d = Diagram()
w = d.page('Page-1')
w.frame(200, 470, 775, 850)
w.line(270, 470, 270, 850, dashed=True)
w.lane_title(200, 470, 'Dataset')
w.lane_title(270, 470, 'Training')
w.store('p', 215, 620, 40, 60, 'p')
w.network(290, 510, prefix='pn')
w.brace(310, 360, 593)
w.text('pl', 295, 603, 80, 26, r'\hat{g}_\theta')
w.box('frz', 280, 635, 90, 30, FROZEN, role='model')
w.network(290, 720, prefix='dn')
w.brace(310, 360, 803)
w.text('dl', 295, 813, 80, 26, r'\Lambda_\psi')
w.box('yh', 488, 535, 30, 30, r'\hat{\mathbf{y}}', role='model')
w.box('dloss', 395, 635, 216, 30, DUAL, role='loss')
w.box('ploss', 631, 635, 130, 30, PRIMAL, role='loss')
w.box('do', 668.5, 745, 55, 30, DOUT, role='model')
# value flow
w.edge('p', None, 'value', exit=(0.5, 0), points=[(235, 550)], tgt_pt=(290, 550))
w.edge('p', None, 'value', exit=(0.5, 1), points=[(235, 760)], tgt_pt=(290, 760))
w.edge('p', 'frz', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge('frz', 'dloss', 'value', exit=(1, 0.5), entry=(0, 0.5))
w.edge(None, 'yh', 'value', src_pt=(360, 550), entry=(0, 0.5))
w.edge(None, 'do', 'value', src_pt=(360, 760), entry=(0, 0.5))
w.edge('yh', 'dloss', 'value', exit=(0.5, 1), entry=(0.5, 0), points=[(503, 600)])
w.edge('yh', 'ploss', 'value', exit=(0.5, 1), entry=(0.5, 0), points=[(503, 600), (696, 600)])
w.edge('do', 'dloss', 'value', exit=(0.5, 0), entry=(0.5, 1), points=[(696, 710), (503, 710)])
w.edge('do', 'ploss', 'value', exit=(0.5, 0), entry=(0.5, 1), points=[(696, 710)])
# gradient returns: one per network, alternating
w.edge('ploss', 'pn-h4-1', 'grad', exit=(0.6538, 0), entry=(1, 0.5), points=[(716, 525)])
w.text('ps', 493, 500, 90, 20, r'\text{primal step}')
w.edge('dloss', 'dn-h4-1', 'grad', exit=(0.2083, 1), entry=(1, 0.5), points=[(440, 735)])
w.text('ds', 370, 708, 60, 20, r'\text{dual step}')
w.edge('dn-h1-0', 'frz', 'value', exit=(0.5, 0), entry=(0.5, 1))
w.text('cp', 331, 682, 32, 20, r'\text{copy}')

c = d.page('compact')
# phone: the two alternating updates as two panels, each with its own inputs
c.frame(200, 480, 452, 945)
c.line(200, 690, 452, 690, dashed=True)
c.lane_title(200, 480, 'Primal step', inset=True)
c.lane_title(200, 690, 'Dual step', inset=True)
c.store('p', 212, 525, 40, 60, 'p')
c.network(267, 515, prefix='pn')
c.brace(287, 327, 598)
c.text('pl', 267, 607, 80, 24, r'\hat{g}_\theta')
c.box('yh', 357, 540, 30, 30, r'\hat{\mathbf{y}}', role='model')
c.box('dfix', 230, 645, 55, 30, DOUT, role='model')
c.box('ploss', 307, 645, 130, 30, PRIMAL, role='loss')
c.edge('p', None, 'straight', exit=(1, 0.5), tgt_pt=(267, 555))
c.edge(None, 'yh', 'value', src_pt=(337, 555), entry=(0, 0.5))
c.edge('yh', 'ploss', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('dfix', 'ploss', 'value', exit=(1, 0.5), entry=(0, 0.5))
c.edge('ploss', 'pn-h4-7', 'grad', exit=(0.1923, 0), entry=(0.5, 1))
c.store('p2', 212, 735, 40, 60, 'p')
c.network(267, 725, prefix='dn')
c.brace(287, 327, 808)
c.text('dl', 267, 817, 80, 24, r'\Lambda_\psi')
c.box('do', 357, 750, 55, 30, DOUT, role='model')
c.box('dloss', 224, 855, 216, 30, DUAL, role='loss')
c.box('frz', 242, 905, 60, 30, r'\Lambda_\psi^{(k)}(p)', role='model')
c.box('yfix', 369.5, 905, 30, 30, r'\hat{\mathbf{y}}', role='model')
c.edge('p2', None, 'straight', exit=(1, 0.5), tgt_pt=(267, 765))
c.edge(None, 'do', 'value', src_pt=(337, 765), entry=(0, 0.5))
c.edge('do', 'dloss', 'value', exit=(0.5, 1), entry=(0.7431, 0))
c.edge('frz', 'dloss', 'value', exit=(0.5, 0), entry=(0.2222, 1))
c.edge('yfix', 'dloss', 'value', exit=(0.5, 0), entry=(0.7431, 1))
c.edge('dloss', 'dn-h4-7', 'grad', exit=(0.5, 0), entry=(0.5, 1))
d.write(os.path.join(HERE, '..', 'masked-sobolev--primal-dual.drawio'))
