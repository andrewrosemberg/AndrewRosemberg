#!/usr/bin/env python3
"""Writes tools/diagrams/kit.drawio: one page of copy-paste primitives (run from the repo root)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from kit import Diagram, BOX, ROLE, TEXT_LEFT  # noqa: E402

d = Diagram()
p = d.page('Page-1')
p.frame(200, 480, 720, 800)
p.line(200, 640, 460, 640, dashed=True)          # lane split (horizontal part)
p.line(460, 640, 460, 800, dashed=True)          # lane split (vertical part)
p.lane_title(200, 480, 'Training')
p.lane_title(200, 640, 'Dataset')
p.store('p', 250, 530, 40, 60, 'p')
p.network(320, 520, output='output', prefix='net')
p.brace(325, 395, 600)                           # under the network: span of the hidden columns
p.text('ghat', 320, 610, 80, 30, r'\hat{g}')
p.box('ad', 345, 485, 35, 25, r'\textit{AD}', role='tool')
p.box('xt', 460, 545, 30, 30, r'\tilde{\mathbf{x}}', role='model')
p.box('dxt', 520, 515, 100, 60, r'\Bigg\{\frac{\partial \tilde{x}^*(p_i)}{\partial p_i}\Bigg\}_{i \in \mathcal{M}}', role='model')
p.box('loss', 470, 610, 140, 30, r'\text{Loss}', role='loss')
p.box('xs', 480, 670, 30, 30, r'{\mathbf{x}}^{*}', role='data')
p.box('acopf', 560, 665, 90, 50, r'\text{AC-OPF}', role='data')
p.box('diffopt', 315, 650, 60, 30, r'\textit{DiffOpt}', role='tool')
p.vertex('gbox', 213.75, 681.88, 112.5, 56.25, BOX % ROLE['data'])
p.block('gtext', 215, 670, 103.12, 60,
        '\\begin{aligned}\n\\min_{x\\ge 0} &\\quad f(x;p) \\\\\n\\text{s.t.} &\\quad c(x;p)=0\n\\end{aligned}')
p.brace(213.75, 326.25, 743)
p.text('g', 255, 755, 30, 20, 'g')
p.store('s', 380, 690, 40, 60, r'\mathbf{s}')
p.vertex('sheet', 640, 690, 60, 70, BOX % ROLE['sheet'])
# connectors
p.edge('p', 'net-i1', 'value', exit=(1, 0.5), entry=(0, 0.5))
p.edge('net-h4-6', 'xt', 'value', exit=(1, 0.5), entry=(0, 0.5), points=[(430, 560)])
p.edge('xt', 'loss', 'value', exit=(0.5, 1), entry=(0.1, 0))
p.edge('loss', 'net-h4-6', 'grad', exit=(0, 0.5), entry=(1, 0), points=[(440, 625), (440, 582)])
p.edge('ad', 'net-h0-0', 'tool', exit=(0, 0.5), entry=(0, 0), points=[(320, 497.5), (320, 510)])
p.edge('diffopt', 'gbox', 'tool-tail', exit=(0.5, 1), entry=(1, 0.4))
p.edge('diffopt', 's', 'value', exit=(1, 0.5), entry=(0.5, 0), points=[(400, 665)])
p.edge('gbox', 's', 'value', exit=(1, 0.5), entry=(0, 0.5))
p.edge('s', 'xs', 'value', exit=(1, 0.5), entry=(0.5, 1), points=[(495, 720)])
p.edge('xs', 'loss', 'value', exit=(0.5, 0), entry=(0.25, 1))
p.edge('acopf', 'loss', 'grad-solid', exit=(0.5, 0), entry=(0.75, 1))
p.add('<mxCell id="dots" value="" style="endArrow=none;dashed=1;html=1;dashPattern=1 2;strokeWidth=2;" edge="1" parent="1">'
      '<mxGeometry width="50" height="50" relative="1" as="geometry"><mxPoint x="640" y="775" as="sourcePoint" />'
      '<mxPoint x="700" y="775" as="targetPoint" /></mxGeometry></mxCell>')
p.add('<mxCell id="adret" value="" style="endArrow=classic;html=1;rounded=0;dashed=1;dashPattern=8 8;strokeColor=#AC3C0C;" '
      'edge="1" parent="1"><mxGeometry width="50" height="50" relative="1" as="geometry">'
      '<mxPoint x="710" y="600" as="sourcePoint" /><mxPoint x="710" y="680" as="targetPoint" /></mxGeometry></mxCell>')
d.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kit.drawio'))
