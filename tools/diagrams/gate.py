#!/usr/bin/env python3
"""Acceptance gate: re-export the reference diagrams with draw.io and overlay them on the paper PDFs.

    python3 tools/diagrams/gate.py OUTDIR

For each of sobolev-original.drawio and dc2ac-original.drawio this exports a PDF with
the draw.io CLI (through tools/lock.sh), reads the page size and the content transform
of both PDFs (pdftocairo -svg), rasterizes both at 200 and 600 dpi, and reports
`compare -metric AE -fuzz 10%` and `compare -metric RMSE`. It writes a red/cyan
overlay (red = only in the draw.io 32 export, cyan = only in the original, grey = both)
and an auto-levelled difference image into OUTDIR.

The draw.io 32 PDF pipeline (Electron's print-to-PDF with shrink-to-fit) cannot reach
every page scale; for DC2AC it lands 0.19 % below the original. When the content scales
differ, the export is rasterized at a compensating resolution (dpi * s_orig / s_new)
and cropped at the page origin, so both rasters put every diagram coordinate at the
same pixel. The report states when that happens.
"""
import collections
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(ROOT, 'tools', 'diagrams')
LOCK = os.path.join(ROOT, 'tools', 'lock.sh')
HOME = os.path.expanduser('~')
GATES = [
    # name, original PDF, draw.io export scale (-s) that reproduces the original page
    ('sobolev', os.path.join(HOME, 'Workspace/Sobolev-NEURIPS-Andrew-2026/diagram_sobolev.pdf'), 0.879105),
    ('dc2ac', os.path.join(HOME, 'Workspace/diffopt_mlopt_policy/diagram.pdf'), 1.00022),
    # rebuilt by measurement (no embedded source): tools/diagrams/src/tsddr_original.py
    ('tsddr', os.path.join(HOME, 'Workspace/PhD Proposal Report/diagram_qualify_tsddr.pdf'), 0.911352),
]


def run(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def page_and_transform(pdf, tmp):
    info = run('pdfinfo', '-box', pdf).stdout
    media = [float(v) for v in re.search(r'MediaBox:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', info).groups()]
    run('pdftocairo', '-svg', '-nocrop', pdf, tmp)
    mats = re.findall(r'transform="matrix\(([-\d.]+), 0, 0, [-\d.]+, ([-\d.]+), ([-\d.]+)\)"', open(tmp).read())
    s, ox, oy = map(float, collections.Counter(mats).most_common(1)[0][0])
    return (media[2] - media[0], media[3] - media[1]), (s, ox, oy)


def metric(a, b, *extra):
    r = run('compare', '-metric', *extra, a, b, 'null:')
    return r.stderr.strip()


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    for name, orig, scale in GATES:
        src = os.path.join(HERE, name + '-original.drawio')
        new = os.path.join(out, name + '-drawio32.pdf')
        r = run(LOCK, 'drawio', '-x', '-f', 'pdf', '--crop', '-s', '%g' % scale, '-o', new, src)
        if r.returncode:
            sys.exit(r.stderr)
        (pw0, ph0), (s0, ox0, oy0) = page_and_transform(orig, os.path.join(out, name + '-orig.svg'))
        (pw1, ph1), (s1, ox1, oy1) = page_and_transform(new, os.path.join(out, name + '-drawio32.svg'))
        print('== %s' % name)
        print('  page    original %.2f x %.2f pt   draw.io 32 %.2f x %.2f pt' % (pw0, ph0, pw1, ph1))
        print('  content original scale %.6f origin (%.3f, %.3f) px   draw.io 32 scale %.6f origin (%.3f, %.3f) px'
              % (s0, -ox0 / s0, -oy0 / s0, s1, -ox1 / s1, -oy1 / s1))
        for dpi in (200, 600):
            a = os.path.join(out, '%s-orig-%d.png' % (name, dpi))
            b = os.path.join(out, '%s-drawio32-%d.png' % (name, dpi))
            run('pdftocairo', '-png', '-r', str(dpi), '-singlefile', orig, a[:-4])
            comp = dpi * s0 / s1
            if abs(comp - dpi) > 1e-3:
                run('pdftocairo', '-png', '-r', '%.6f' % comp, '-singlefile', new, b[:-4] + '-raw')
                size = run('magick', 'identify', '-format', '%wx%h', a).stdout
                run('magick', b[:-4] + '-raw.png', '-background', 'white', '-extent', size + '+0+0', b)
                note = ' (export rasterized at %.4f dpi to match the original content scale)' % comp
            else:
                run('pdftocairo', '-png', '-r', str(dpi), '-singlefile', new, b[:-4])
                note = ''
            print('  %d dpi: AE(fuzz 10%%) = %s   RMSE = %s%s' % (
                dpi, metric(a, b, 'AE', '-fuzz', '10%'), metric(a, b, 'RMSE'), note))
            ov = os.path.join(out, '%s-overlay-%d.png' % (name, dpi))
            run('magick', '(', a, '-colorspace', 'gray', ')', '(', b, '-colorspace', 'gray', ')',
                '(', b, '-colorspace', 'gray', ')', '-combine', ov)
            run('magick', a, b, '-compose', 'difference', '-composite', '-colorspace', 'gray', '-auto-level',
                os.path.join(out, '%s-diff-%d.png' % (name, dpi)))
        print('  overlay: %s' % os.path.join(out, name + '-overlay-200.png'))


if __name__ == '__main__':
    main()
