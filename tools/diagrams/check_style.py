#!/usr/bin/env python3
"""Style linter for method diagrams: everything must come from the three reference figures.

    python3 tools/diagrams/check_style.py [file.drawio ...]   # default: tools/diagrams/*.drawio

Fails (exit 1) on any fill, stroke or font colour, font, font size, stroke width, arrow,
dash pattern, shape or style key that the reference figures (diagram_sobolev.pdf, the
DC2AC diagram.pdf, diagram_qualify_tsddr.pdf) do not use, on a labelled cell without
fontFamily=Arial, on a \\color{} in a label outside the reference colours, and on a page
without math="1". The whitelist is the README's style bible in machine form.
"""
import glob
import html
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = r'-?\d+(\.\d+)?'
ALLOWED = {
    # key: regex of allowed values (lower-cased)
    'fillcolor': r'#dae8fc|#d5e8d4|#ffe6cc|#e1d5e7|#f8cecc|#f5f5f5|none',
    'strokecolor': r'#6c8ebf|#82b366|#d79b00|#9673a6|#b85450|#dedede|#ac3c0c|#000000|none',
    'fontcolor': r'#ac3c0c|#000000',
    'fontfamily': r'arial',
    'strokewidth': r'0\.25|1|2',
    'dashed': r'0|1',
    'dashpattern': r'1 2|1 3|8 8',
    'endarrow': r'classic|none',
    'startfill': r'0',
    'shape': r'cylinder3|curlybracket',
    'edgestyle': r'orthogonaledgestyle',
    'rounded': r'0|1',
    'orthogonalloop': r'1',
    'jettysize': r'auto',
    'html': r'1',
    'whitespace': r'wrap',
    'boundedlbl': r'1',
    'backgroundoutline': r'1',
    'size': r'15',
    'aspect': r'fixed',
    'fliph': r'1',
    'rotation': r'90',
    'labelposition': r'right',
    'verticallabelposition': r'middle',
    'align': r'left|center',
    'verticalalign': r'middle|top',
    'resizable': r'0',
    'points': r'\[\]',
    'autosize': r'1',
    'exitx': NUM, 'exity': NUM, 'exitdx': NUM, 'exitdy': NUM, 'exitperimeter': r'0|1',
    'entryx': NUM, 'entryy': NUM, 'entrydx': NUM, 'entrydy': NUM, 'entryperimeter': r'0|1',
}
BASE = {'ellipse', 'text', 'group'}
TEX_COLORS = {'red', '#ac3c0c', '#AC3C0C'}
RULES = [
    # (condition on parsed style, message)
    (lambda s: s.get('strokewidth') == '0.25' and s.get('endarrow') != 'none', '0.25 px is only for network synapses'),
    (lambda s: s.get('strokewidth') == '2' and s.get('dashpattern') not in ('1 2', '1 3'), '2 px is only for dotted lines'),
    (lambda s: s.get('dashpattern') == '8 8' and s.get('strokecolor', '').lower() != '#ac3c0c',
     'the 8 8 dash is only for the dark-red AD return (TS-DDR)'),
    (lambda s: s.get('fontcolor', '').lower() == '#ac3c0c' and s.get('fillcolor', 'none').lower() not in ('#f8cecc', 'none'),
     'dark-red text only in the loss box or as free text'),
]


def parse(style):
    out, base = {}, set()
    for tok in filter(None, (style or '').split(';')):
        if '=' in tok:
            k, v = tok.split('=', 1)
            out[k.lower()] = v
        else:
            base.add(tok)
    return base, out


def check(path):
    errs = []
    root = ET.parse(path).getroot()
    for diagram in root.iter('diagram'):
        page = diagram.get('name')
        model = diagram.find('mxGraphModel')
        if model is None:
            errs.append('%s: page %r is compressed; save uncompressed' % (path, page))
            continue
        if model.get('math') != '1':
            errs.append('%s: page %r must set math="1"' % (path, page))
        ids = [c.get('id') for c in model.iter('mxCell')]
        for dup in sorted(set(i for i in ids if ids.count(i) > 1)):
            errs.append('%s: page %r has duplicate cell id %r' % (path, page, dup))
        for c in model.iter('mxCell'):
            cid, style, value = c.get('id'), c.get('style'), c.get('value') or ''
            if style is None:
                continue
            base, kv = parse(style)
            where = '%s [%s] %s' % (os.path.basename(path), page, cid)
            for b in base - BASE:
                errs.append('%s: style token %r not in the reference figures' % (where, b))
            for k, v in kv.items():
                pat = ALLOWED.get(k)
                if pat is None:
                    errs.append('%s: style key %r not used by the reference figures' % (where, k))
                elif not re.fullmatch(pat, v.lower()):
                    errs.append('%s: %s=%s not in the reference palette/styles' % (where, k, v))
            for test, msg in RULES:
                if test(kv):
                    errs.append('%s: %s' % (where, msg))
            if value.strip() and c.get('vertex') == '1' and kv.get('fontfamily', '').lower() != 'arial':
                errs.append('%s: labelled cell needs fontFamily=Arial' % where)
            for col in re.findall(r'\\color\{([^}]*)\}', html.unescape(value)):
                if col not in TEX_COLORS:
                    errs.append('%s: \\color{%s} not a reference colour' % (where, col))
    return errs


def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, '*.drawio')))
    errs = []
    for f in files:
        errs += check(f)
    for e in errs:
        print(e)
    print('%d file(s), %d problem(s)' % (len(files), len(errs)))
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
