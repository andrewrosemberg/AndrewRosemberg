#!/usr/bin/env python3
"""masked-sobolev--direct-matching: the masked Sobolev figure (sobolev.drawio) with every derivative element deleted.

Same positions as paper Figure 1 for p, the network, the proxy output, the solver block, the store and y*;
the derivative column (AD, DiffOpt, both sensitivity boxes) is removed and the frame is cropped to the
remaining content, so the loss shrinks to its label and sits in the column of y-hat and y*."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram, BOX, ROLE  # noqa: E402

PROBLEM = ('\\begin{aligned}\n\\min_{\\mathbf{y}} &\\quad f(\\mathbf{y};p) \\\\\n'
           '\\text{s.t.} &\\quad c(\\mathbf{y};p)=\\mathbf{0} \\\\\n &\\quad h(\\mathbf{y};p)\\ge \\mathbf{0}\n\\end{aligned}')
LOSS = r'\ell(\hat{\mathbf{y}},\mathbf{y}^{\star})'

TAG = r'\text{value-only baseline}'

d = Diagram()
# ---------------------------------------------------------------- wide (paper Figure 1 coordinates, derivative column removed)
w = d.page('Page-1')
w.frame(200, 480, 525, 790)
w.line(200, 640, 525, 640, dashed=True)
w.lane_title(200, 480, 'Training')
w.lane_title(200, 640, 'Dataset')
w.text('tag', 395, 484, 120, 24, TAG)
w.store('p', 250, 530, 40, 60, 'p')
w.network(320, 520, prefix='net')
w.brace(340, 390, 598)
w.text('gh', 325, 600, 80, 30, r'\hat{g}_\theta')
w.box('yh', 460, 545, 30, 30, r'\hat{\mathbf{y}}', role='model')
w.box('loss', 440, 600, 70, 30, LOSS, role='loss')
w.vertex('gbox', 213.75, 670, 120, 76.25, BOX % ROLE['data'])
w.block('gtext', 218.88, 658.12, 110, 80, PROBLEM)
w.brace(213.75, 333.75, 751)
w.text('g', 258.75, 763, 30, 20, 'g')
w.store('ys', 455, 678, 40, 60, r'\mathbf{y}^{\star}')
w.edge('p', None, 'straight', exit=(1, 0.5), tgt_pt=(320, 560))
w.edge('p', 'gbox', 'value', exit=(0.5, 1), entry=(0.4688, 0))
w.edge(None, 'yh', 'value', src_pt=(390, 560), entry=(0, 0.5))
w.edge('yh', 'loss', 'value', exit=(0.5, 1), entry=(0.5, 0))
w.edge('ys', 'loss', 'value', exit=(0.5, 0), entry=(0.5, 1), extra='exitPerimeter=0;')
w.edge('gbox', 'ys', 'value', exit=(1, 0.5), entry=(0, 0.5), extra='entryPerimeter=0;')
w.edge('loss', 'net-h4-6', 'grad', exit=(0, 0.5), entry=(1, 0.5), points=[(420, 615), (420, 585)])

# ---------------------------------------------------------------- compact (phone)
c = d.page('compact')
c.frame(200, 480, 450, 805)
c.line(200, 660, 450, 660, dashed=True)
for y, t in ((480, 'Training'), (660, 'Dataset')):
    c.vertex(None, 250, y, 100, 30, 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;', '$$\\text{%s}$$' % t)
c.text('tag', 335, 482, 110, 24, TAG)
c.store('p', 212, 525, 40, 60, 'p')
c.network(270, 515, output='output', prefix='net')
c.brace(290, 340, 598)
c.text('gh', 275, 600, 80, 30, r'\hat{g}_\theta')
c.box('yh', 390, 540, 30, 30, r'\hat{\mathbf{y}}', role='model')
c.box('loss', 370, 605, 70, 30, LOSS, role='loss')
c.vertex('gbox', 212, 695, 122, 76.25, BOX % ROLE['data'])
c.block('gtext', 217, 683.12, 112, 80, PROBLEM)
c.brace(212, 334, 776)
c.text('g', 258, 786, 30, 20, 'g')
c.store('ys', 385, 703, 40, 60, r'\mathbf{y}^{\star}')
c.edge('p', None, 'straight', exit=(1, 0.5), tgt_pt=(270, 555))
c.edge('p', 'gbox', 'value', exit=(0.5, 1), entry=(0.1639, 0))
c.edge(None, 'yh', 'value', src_pt=(340, 555), entry=(0, 0.5))
c.edge('yh', 'loss', 'value', exit=(0.5, 1), entry=(0.5, 0))
c.edge('ys', 'loss', 'value', exit=(0.5, 0), entry=(0.5, 1), extra='exitPerimeter=0;')
c.edge('gbox', 'ys', 'value', exit=(1, 0.5), entry=(0, 0.5), extra='entryPerimeter=0;')
c.edge('loss', 'net-h4-6', 'grad', exit=(0, 0.5), entry=(1, 0.5), points=[(355, 620), (355, 585)])
d.write(os.path.join(HERE, '..', 'masked-sobolev--direct-matching.drawio'))
