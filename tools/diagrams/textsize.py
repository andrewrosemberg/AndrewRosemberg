#!/usr/bin/env python3
"""Smallest typeset text in each diagram SVG, in draw.io px of font size.

    python3 tools/diagrams/textsize.py [measure.jsonl]

Every glyph in an exported SVG carries matrix(a 0 0 -a e f), where a is draw.io px per MathJax
glyph unit. With the kit's 12 px Arial labels, 1 em = 14.07 px = 1000 units, so a glyph's font
size is a * 1000 / 1.1725 px: 12 for normal labels, 8.49 for sub/superscripts and \\scriptstyle.
Given the output of measure.js, also prints the displayed size (font px * shown / natural).
"""
import collections, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'src', 'assets', 'img', 'diagrams')


def sizes(path):
    s = open(path).read()
    vals = [abs(float(m.group(1))) for m in re.finditer(r'matrix\(([-\d.e]+) [-\d.e]+ [-\d.e]+ ([-\d.e]+)', s)]
    fs = collections.Counter(round(v * 1000 / 1.1725, 1) for v in vals if 1e-3 < v < 0.1)
    return fs


def main():
    meas = {}
    if len(sys.argv) > 1:
        for line in open(sys.argv[1]):
            if line.startswith('{'):
                r = json.loads(line)
                meas.setdefault(r['src'], []).append(r)
    for f in sorted(glob.glob(os.path.join(OUT, '*.svg'))):
        name = os.path.basename(f)
        fs = sizes(f)
        if not fs:
            continue
        small, main = min(fs), max(fs, key=lambda k: fs[k])
        line = '%-55s font px: smallest %.1f, most common %.1f' % (name, small, main)
        for r in meas.get(name, []):
            k = r['shown'] / r['natural']
            line += ' | %d px: %.0f/%.0f wide -> smallest %.1f, main %.1f' % (r['viewport'], r['shown'], r['natural'], small * k, main * k)
        print(line)


if __name__ == '__main__':
    main()
