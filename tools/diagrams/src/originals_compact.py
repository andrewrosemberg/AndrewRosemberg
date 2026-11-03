#!/usr/bin/env python3
"""Adds a `compact` (phone) page to sobolev.drawio and dc2ac.drawio: the paper figures' own elements, labels and
styles, relaid with the lanes stacked (<= 256 px wide). Page 1 stays the exact rebuild.
Run after build_originals.py:  python3 tools/diagrams/build_originals.py && python3 tools/diagrams/src/originals_compact.py"""
import os
import re
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kit import Diagram, BOX, ROLE, EDGE  # noqa: E402

TOOLTAIL = EDGE['tool-tail']
SOB_BLOCK = '\\begin{aligned}\n\\min_{x\\ge 0} &\\quad f(x;p) \\\\\n\\text{s.t.} &\\quad c(x;p)=0\n\\end{aligned}'
DXT = r'$$\Bigg\{\frac{\partial \tilde{x}^*(p_i)}{\partial p_i}\Bigg\}_{i \in \mathcal{M}}$$'
DXS = r'$$\Bigg\{\frac{\partial x^*(p_i)}{\partial p_i}\Bigg\}_{i \in \mathcal{M}}$$'


def sobolev(c):
    c.frame(200, 480, 452, 970)
    c.line(200, 800, 452, 800, dashed=True)
    for y, t in ((480, 'Training'), (800, 'Dataset')):
        c.vertex(None, 245, y, 100, 30, 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;',
                 '$$\\text{%s}$$' % t)
    c.box('ad', 287.5, 512.5, 35, 25, r'\textit{AD}', role='tool')
    c.box('dxt', 345, 495, 100, 60, DXT, role='model')
    c.store('p', 212, 570, 40, 60, 'p')
    c.network(270, 560, output='output', prefix='net')
    c.brace(290, 340, 643)
    c.text('gh', 275, 651, 80, 30, r'\hat{g}')
    c.box('xt', 365, 585, 30, 30, r'\tilde{\mathbf{x}}', role='model')
    c.box('loss', 270, 690, 175, 30, r'<div>$$\text{Loss}$$</div>', role='loss')
    c.box('dxs', 285, 735, 100, 60, DXS, role='data')
    c.box('xs', 405, 750, 30, 30, r'{\mathbf{x}}^{*}', role='data')
    c.box('diffopt', 305, 825, 60, 30, r'\textit{DiffOpt}', role='tool')
    c.vertex('gbox', 215, 865, 112.5, 56.25, BOX % ROLE['data'])
    c.block('gtext', 216.13, 853.12, 103.12, 60, SOB_BLOCK)
    c.brace(215, 327.5, 926)
    c.text('g', 256.25, 937, 30, 20, 'g')
    c.store('s', 345, 863, 40, 60, r'\mathbf{s}')
    c.edge('p', None, 'straight', exit=(1, 0.5), tgt_pt=(270, 600))
    c.edge('p', 'gbox', 'value', exit=(0.5, 1), entry=(0.1511, 0))
    c.edge('ad', 'net-h1-0', 'tool', exit=(0.5, 1), entry=(0.5, 0))
    c.edge('ad', 'dxt', 'value', exit=(1, 0.5), entry=(0, 0.5))
    c.edge(None, 'xt', 'value', src_pt=(340, 600), entry=(0, 0.5))
    c.edge('xt', 'loss', 'value', exit=(0.5, 1), entry=(0.6286, 0))
    c.edge('dxt', 'loss', 'value', exit=(0.85, 1), entry=(0.9143, 0))
    c.edge('loss', 'net-h4-5', 'grad', exit=(0.4686, 0), entry=(1, 0.5), points=[(352, 615)])
    c.edge('dxs', 'loss', 'value', exit=(0.5, 0), entry=(0.3714, 1))
    c.edge('xs', 'loss', 'value', exit=(0.5, 0), entry=(0.8571, 1))
    c.edge('diffopt', 'dxs', 'value', exit=(0.5, 0), entry=(0.5, 1))
    c.edge('diffopt', 'gbox', 'tool-tail', exit=(0, 0.5), entry=(0.5, 0), points=[(271.25, 840)])
    c.edge('gbox', 's', 'value', exit=(1, 0.5), entry=(0, 0.5), extra='entryPerimeter=0;')
    c.edge('s', 'xs', 'value', exit=(1, 0.5), entry=(0.5, 1), points=[(420, 893)], extra='exitPerimeter=0;')


def dc2ac(c):
    c.frame(200, 470, 452, 965)
    c.line(200, 850, 452, 850, dashed=True)
    for y, t in ((470, 'Training'), (850, 'Dataset')):
        c.vertex(None, 245, y, 100, 30, 'text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;',
                 '$$\\text{%s}$$' % t)
    c.store('pd', 210, 510, 40, 60, r'{\mathbf{p}}^\text{d}')
    c.network(265, 500, output='model', prefix='net')
    c.box('gs', 355, 500, 30, 30, r'\tilde{g}^\text{s}', role='model')
    c.box('b', 355, 550, 30, 30, r'\tilde{b}', role='model')
    c.box('dcopf', 330, 610, 110, 40, r'\text{DC-OPF}', role='model')
    c.box('pg', 330, 680, 30, 30, r'\tilde{\mathbf{p}}^\text{g}', role='model')
    c.box('pf', 370, 680, 30, 30, r'\tilde{\mathbf{p}}^\text{f}', role='model')
    c.box('th', 410, 680, 30, 30, r'\tilde{\boldsymbol{\theta}}', role='model')
    c.box('loss', 330, 740, 110, 30, r'\text{Regression Loss}', role='loss')
    c.box('rpg', 330, 800, 30, 30, r'{\mathbf{p}}^\text{g}', role='data')
    c.box('rpf', 370, 800, 30, 30, r'{\mathbf{p}}^\text{f}', role='data')
    c.box('rth', 410, 800, 30, 30, r'{\boldsymbol{\theta}}', role='data')
    c.box('acopf', 212, 895, 90, 40, r'\text{AC-OPF}', role='data')
    c.store('ac', 355, 875, 60, 80, r'\text{AC}')
    c.edge('pd', None, 'straight', exit=(1, 0.5), tgt_pt=(265, 540))
    c.edge(None, 'gs', 'value', src_pt=(335, 540), points=[(345, 540), (345, 515)], entry=(0, 0.5))
    c.edge(None, 'b', 'value', src_pt=(335, 540), points=[(345, 540), (345, 565)], entry=(0, 0.5))
    c.edge('gs', 'dcopf', 'value', exit=(1, 0.5), entry=(0.6364, 0), points=[(400, 515)])
    c.edge('b', 'dcopf', 'value', exit=(0.5, 1), entry=(0.3636, 0))
    for k, x in (('pg', 345), ('pf', 385), ('th', 425)):
        c.edge('dcopf', k, 'value', exit=(0.5, 1), entry=(0.5, 0), points=[(385, 665), (x, 665)])
        c.edge(k, 'loss', 'value', exit=(0.5, 1), entry=((x - 330) / 110.0, 0))
    for k, x in (('rpg', 345), ('rpf', 385), ('rth', 425)):
        c.edge(k, 'loss', 'value', exit=(0.5, 0), entry=((x - 330) / 110.0, 1))
        c.edge('ac', k, 'value', exit=(0.5, 0), entry=(0.5, 1), points=[(385, 845), (x, 845)], extra='exitPerimeter=0;')
    c.edge('loss', 'net-h0-7', 'grad-solid', exit=(0, 0.5), entry=(0.5, 1), points=[(290, 755)])
    c.edge('pd', 'acopf', 'value', exit=(0.5, 1), entry=(0.2, 0))
    c.edge('acopf', 'ac', 'value', exit=(1, 0.5), entry=(0, 0.5), extra='entryPerimeter=0;')


def append(name, fill):
    path = os.path.join(HERE, '..', name + '.drawio')
    s = open(path).read()
    s = re.sub(r'\s*<diagram name="compact".*?</diagram>', '', s, flags=re.S)
    d = Diagram()
    fill(d.page('compact'))
    tmp = path + '.tmp'
    d.write(tmp)
    page = re.search(r'(  <diagram name="compact".*?</diagram>)', open(tmp).read(), re.S).group(1)
    os.remove(tmp)
    s = s.replace('</mxfile>', page.replace('id="p1"', 'id="compact"') + '\n</mxfile>')
    open(path, 'w').write(s)
    print('added compact page to', name + '.drawio')


if __name__ == '__main__':
    append('sobolev', sobolev)
    append('dc2ac', dc2ac)
