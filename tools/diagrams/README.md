# Method diagrams: the paper identity

Every method diagram on the site is a draw.io file in this folder, drawn with the same choices as the
author's paper figures, and exported by `export.sh` to `src/assets/img/diagrams/`. The only deliberate
change from the papers: the lane the papers call "Offline" is named **Dataset**.

## The three reference figures (the gate)

| Gate | Reference | Rebuilt as | How |
|---|---|---|---|
| A | `~/Workspace/Sobolev-NEURIPS-Andrew-2026/diagram_sobolev.pdf` | `sobolev-original.drawio` | draw.io source embedded in the PDF (`/Subject`), extracted by `build_originals.py` |
| B | `~/Workspace/diffopt_mlopt_policy/diagram.pdf` (DC2AC paper, Fig. 1) | `dc2ac-original.drawio` | same |
| C | `~/Workspace/PhD Proposal Report/diagram_qualify_tsddr.pdf` (TS-DDR training loop) | `tsddr-original.drawio` | no source survives (re-saved by Preview): shapes read off the PDF vector paths, labels typeset and positioned glyph by glyph (`src/tsddr_original.py`) |

`python3 tools/diagrams/gate.py OUTDIR` re-exports the three with the draw.io 32 CLI, rasterizes original
and rebuild at 200 and 600 dpi, and writes red/cyan overlays (red: only in the rebuild, cyan: only in the
original). Results (2026-11-01):

| | page (pt) | AE, fuzz 10 %, 200 dpi | RMSE 200 dpi | AE 600 dpi | RMSE 600 dpi |
|---|---|---|---|---|---|
| A Sobolev | 309.12 × 211.92, identical | 37 px of 505 951 (0.007 %) | 0.0045 | 324 (0.007 %) | 0.0059 |
| B DC2AC | 333.12 × 204.00, identical | 179 px of 525 042 (0.034 %) | 0.0096 | 1408 (0.030 %) | 0.0124 |
| C TS-DDR | 414.00 × 250.08, identical | 5714 px of 799 200 (0.71 %) | 0.035 | 36 955 (0.51 %) | 0.046 |

Residuals, all measured:
- A, B: every shape coincides. MathJax 4.1.3 (the only MathJax in draw.io 32) places a few accents and one
  superscript (`\hat g`, `\tilde x`, `\tilde g^{s}`) up to 0.5 px (at 12 px type) from where MathJax 3 put them.
  Glyph outlines, sizes and baselines coincide.
- B: draw.io 32's print-to-PDF reaches the original page but its content scale is 0.19 % smaller (Electron's
  shrink-to-fit is quantised); the gate rasterizes the rebuild at 200 × 1.0019 dpi to compare like with like.
- C: all 484 shape outlines within 0.05 px; all 165 glyphs within 0.68 px (mean 0.23 px). HTML labels snap to
  whole pixels in draw.io, so a label's sub-pixel offset from MathJax 3 cannot be reproduced exactly.

## Fonts and math (why `fontFamily=Arial` on every label)

All labels are TeX typeset by draw.io's MathJax (SVG output, TeX font = Computer Modern), with `math="1"` on
the page. MathJax scales formulas to the ex-height of the surrounding HTML font. The originals were exported by
the diagrams.net export server (HeadlessChrome on Windows), where the default label font "Helvetica" resolves to
Arial. On macOS, Helvetica is real Helvetica and every formula came out 0.77 % larger. Hence **every labelled
cell carries `fontFamily=Arial;`** and the default font size (12 px): with it, the glyphs match the papers
exactly (1 em = 14.07 px). Never set `fontSize`.

## Web export (`export.sh`)

`drawio -x -f pdf --crop` (draw.io typesets the math) → `pdftocairo -svg` (every glyph becomes a path) →
`pdf2svg.py` (drops the PDF's invisible text layer, maps back to draw.io coordinates, shares repeated glyph
outlines via `<use>`, crops to the ink plus 6 px, puts a white rectangle underneath, rounds to 0.03 px).
The SVG needs no fonts, no MathJax and no `foreignObject`; its `width`/`height` are the diagram's own size in
draw.io px (1 draw.io px = 1 CSS px). Checked: the optimized SVG against the unoptimized conversion
differs by at most 18/255 in any pixel (rsvg); Chrome renders it identically as `<img>` in light and dark
colour schemes; WebKit (Quick Look) renders the same glyphs, dashes and colours. Ellipses become `<circle>`,
Chrome's filled dash rectangles become `h/v` path segments, repeated glyphs share one `<path>`. Sizes: 36–133 KB.
`padframe.py` adds an invisible 20 px frame before export so the cropped PDF page never clips the outer strokes.

draw.io's native SVG export was rejected: labels are HTML in `foreignObject` (Safari's `<img>` support is
fragile), positions depend on the viewer's Arial metrics (`ex` units), and colours are emitted as
`light-dark()`, so a dark-mode page would recolour the figure.

Pages: page 1 of `NAME.drawio` → `NAME.svg`; a page named `compact` → `NAME-compact.svg` (phone layout,
convention: portrait, at most ~360 px wide so 12 px type stays legible at 390 px viewports); any other page
`P` → `NAME-P.svg`. `*-original.drawio` and `kit.drawio` are not exported.

Site CSS for the paper-figure treatment (the SVG already has a white background):

```css
.fig .frame img[src*="/diagrams/"] { display:block; width:100%; height:auto; max-width:var(--diagram-max, 760px);
  margin:0 auto; background:#fff; border-radius:6px; padding:12px; box-sizing:border-box; }
:root[data-theme="dark"] .fig .frame img[src*="/diagrams/"] { box-shadow:0 0 0 1px rgba(255,255,255,.08); }
```

## Style bible

Coordinates on a 10 px grid (5 px where the originals use it). Default stroke 1 px, black value arrows with the
default `classic` head, square corners for data/model boxes, rounded corners (`rounded=1`, default arc) for
tool and loss boxes. Every string below is verbatim from the reference sources; `kit.py` emits them and
`check_style.py` rejects anything else. Append `fontFamily=Arial;` to every labelled cell.

### Colour roles (as used in the originals)

| Role | fill / stroke | Meaning in the papers |
|---|---|---|
| data (orange) | `#ffe6cc` / `#d79b00` | ground truth and its producers: samples, data stores, the solver's problem, solver outputs `x*`, Jacobians from the solver |
| model (blue) | `#dae8fc` / `#6c8ebf` | the learned model and everything it outputs: network nodes, predictions `x̃`, its Jacobians, the DC-OPF layer of DC2AC |
| output (green) | `#d5e8d4` / `#82b366` | the network's output layer (Sobolev); the TS-DDR "reachable target" map |
| tool (purple) | `#e1d5e7` / `#9673a6` | differentiation machinery (`AD`, `DiffOpt`) |
| loss (red) | `#f8cecc` / `#b85450` | loss / gradient objective; gradient-return arrows |
| sheet (grey) | `#f5f5f5` / `#dedede` | stacked per-stage copies of a network (TS-DDR) |
| AD red | stroke / text `#AC3C0C` | TS-DDR: AD expression text, the 8-8 dashed return, the outlined "Duality" box |
| TeX red | `{\color{red} ...}` | TS-DDR: inputs that enter the problem as parameters (`w_t`, `x̂_t`) |

### Elements

| Element | Style string |
|---|---|
| Lane frame (four lines, as drawn in the originals) | `endArrow=none;html=1;rounded=0;` |
| Lane split | `endArrow=none;dashed=1;html=1;rounded=0;` |
| Lane title, cell 70×30 at the lane corner | `text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;` value `<div>$$\text{Training}$$</div>` |
| "Dataset" title, cell 60×30 at corner + (3.3, 0) | same style, value `$$\text{Dataset}$$` (the word starts where "Offline" did) |
| Process box (data / model) | `rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;` (blue: `#dae8fc`/`#6c8ebf`) |
| Loss box | `rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;` |
| Tool box | `rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;` |
| Data store | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffe6cc;strokeColor=#d79b00;` (40×60 or 60×80) |
| Network node (10×10) | `ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dae8fc;strokeColor=#6c8ebf;` (output column `#d5e8d4`/`#82b366`) |
| Synapse (input → first hidden column) | `endArrow=none;html=1;rounded=0;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeWidth=0.25;fillColor=#dae8fc;strokeColor=#6c8ebf;` |
| Brace (under a span; tip down) | `shape=curlyBracket;whiteSpace=wrap;html=1;rounded=1;flipH=1;labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;rotation=90;` (cell w = 10.55, h = span) |
| Free math label | `text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;` |
| Problem block (left-aligned `aligned`) | `text;whiteSpace=wrap;` value `\begin{aligned}...\end{aligned}` (no `$$`) |
| Value arrow | `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;` |
| Gradient return (Sobolev) | `...;html=1;strokeColor=#B85450;dashed=1;` (value-arrow prefix) |
| Gradient return (DC2AC) | `...;html=1;fillColor=#f8cecc;strokeColor=#b85450;` (solid) |
| Tool link | `...;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;dashed=1;` ; no head: `...;dashed=1;endArrow=none;startFill=0;fillColor=#e1d5e7;strokeColor=#9673a6;` |
| Straight arrow between free points | `endArrow=classic;html=1;rounded=0;` (the head's tip sits 1.12 px before the target point) |
| Dotted line (TS-DDR) | `endArrow=none;dashed=1;html=1;dashPattern=1 2;strokeWidth=2;` or draw.io's "Dotted Line" `...dashPattern=1 3;strokeWidth=2;` |
| AD return (TS-DDR) | `endArrow=classic;html=1;rounded=0;dashed=1;dashPattern=8 8;strokeColor=#AC3C0C;` |
| Duality box (TS-DDR) | `rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#AC3C0C;` |

### Network glyph geometry

Origin (x, y): input column of 4 nodes at (x, y+20…y+50); five columns of 8 nodes at x+20…x+60, y…y+70
(10 px pitch, touching); the last column green for the Sobolev identity (blue in DC2AC); 32 synapses from
every input to every node of the first hidden column. Bounding box 70 × 80. TS-DDR stacks three copies
on grey 80×85 sheets offset by (−10, +5)/(−9.7, +7.5), with `t` on the front sheet. Label the glyph with a
brace under the hidden columns and a math label below it (`\hat g`, `\pi_t(\cdot)`).

### Labels

- Everything is TeX: `$$...$$` (display style, as in the originals). Words go in `\text{}` (upright CM);
  software/tools in `\textit{}`; vectors bold `\mathbf{x}`, `\boldsymbol\theta`; learned quantities carry a
  tilde (`\tilde{\mathbf x}`), solver quantities a star (`\mathbf x^*`). Superscript tags upright: `^\text{d}`.
- Plain-text-only cells do not exist in the originals; do not add sans-serif text.
- 12 px default type everywhere; small boxes are 30×30 (one symbol), process boxes 90×50 / 100×60,
  loss 120–140 × 30, tool 35×25 / 60×30, stores 40×60 / 60×80.
- Lanes: frame and splits on the 10 px grid, titles at the lane's top-left corner, the dashed split runs
  from the frame to the frame. Keep ≥ 10 px between boxes and lane lines.
- Margins: the exported SVG adds 6 px of white around the ink; nothing else is needed on the page.

### Worked XML

```xml
<mxCell id="xt" value="$$\tilde{\mathbf{x}}$$" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Arial;" vertex="1" parent="1">
  <mxGeometry x="460" y="545" width="30" height="30" as="geometry" /></mxCell>
<mxCell id="loss" value="&lt;div&gt;$$\text{Loss}$$&lt;/div&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Arial;" vertex="1" parent="1">
  <mxGeometry x="450" y="610" width="140" height="30" as="geometry" /></mxCell>
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#B85450;dashed=1;entryX=1;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="loss" target="net-h4-6">
  <mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="440" y="625" /><mxPoint x="440" y="582" /></Array></mxGeometry></mxCell>
```

## Files

- `kit.py`: the primitives (`Diagram`, `Page.box/store/network/brace/text/block/lane_title/frame/line/edge`).
  Diagrams are generated by short scripts in `src/` (one per figure), so a style lives in one place.
- `kit.drawio`: a page of every primitive to copy from in the draw.io editor (`src/kit_page.py`).
- `check_style.py`: the linter (run by `export.sh` before each export).
- `build_originals.py`: extracts gates A/B and writes `sobolev.drawio`, `dc2ac.drawio` (site versions).
- `gate.py`: the overlay gate. `pdf2svg.py`, `padframe.py`, `export.sh`: the web export.
- `src/*.py`: one generator per site figure (rerun it, then `export.sh NAME`); `src/tsddr_original.py` writes gate C.
- `LearningToOptimize.jl/docs/L2O.drawio` was mined too: it is a different, older style (tables, gradients,
  no math) and is not part of this identity.

## Legibility gate (site figures)

The article column is about 826 CSS px at 1440 and 316 px at 390, and build.py caps display at 1.6 px per draw.io px.
With the paper type (12 px labels, 8.5 px scripts) that means: wide figures at most ~600 px wide (scripts ≥ 11 CSS px),
`compact` pages at most ~266 px wide (scripts ≥ 10 CSS px). No `\scriptstyle` captions and no second-level scripts
(e.g. write `\sup\{\cdot:\mathbb Q\in\mathcal A_\varepsilon\}`, `\partial\Pi/\partial\mathbf g_a`). Measure, don't estimate:
`tools/lock.sh node tools/diagrams/measure.js 1440,390 research/<slug>/ > m.jsonl; python3 tools/diagrams/textsize.py m.jsonl`.
The outer frame stays: all three reference figures draw one (four lines).
