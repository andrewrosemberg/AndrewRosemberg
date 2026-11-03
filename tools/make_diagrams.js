// Generate the theme-aware decision-process diagrams in src/_partials/diagrams/.
//
//   npm install --no-save mathjax-full@3.2.2
//   node tools/make_diagrams.js
//
// Formulas are typeset by MathJax into SVG paths (fill="currentColor"), so the
// diagrams need no runtime math library and take their colors from the site's
// CSS variables. Each diagram comes in a two-column layout and a single-column
// layout for narrow screens; build.py inlines both and CSS picks one.
// Every component and edge carries data-part, which the page uses to highlight
// the computation a section is about (see .dg-focus-* in site.css).
'use strict';
const fs = require('fs');
const path = require('path');
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');

const OUT = path.join(__dirname, '..', 'src', '_partials', 'diagrams');
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', { InputJax: new TeX({ packages: AllPackages }), OutputJax: new SVG({ fontCache: 'none' }) });

// Typeset TeX and place it with its baseline at (x, y); anchor = start | middle | end.
function tex(src, x, y, size = 15, anchor = 'middle') {
  const node = doc.convert(src, { display: false });
  const html = adaptor.outerHTML(node);
  const svg = html.match(/<svg[\s\S]*<\/svg>/)[0];
  const [vx, vy, vw, vh] = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  const w = (vw / 1000) * size, h = (vh / 1000) * size;
  const left = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x;
  const top = y + (vy / 1000) * size;
  const inner = svg.replace(/^<svg[^>]*>/, '').replace(/<\/svg>$/, '').replace(/ data-[\w-]+="[^"]*"/g, '');
  return { markup: `<svg class="dg-math" x="${r(left)}" y="${r(top)}" width="${r(w)}" height="${r(h)}" viewBox="${vx} ${vy} ${vw} ${vh}" aria-hidden="true">${inner}</svg>`, width: w };
}
const r = v => Math.round(v * 10) / 10;
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

function text(s, x, y, cls, anchor = 'middle') {
  return `<text class="${cls}" x="${r(x)}" y="${r(y)}" text-anchor="${anchor}">${esc(s)}</text>`;
}

// Coloured top edge that follows the rounded corners of a box.
const tab = (x, y, w, rx = 9) => `<path class="dg-tab" d="M${x} ${y + rx} A${rx} ${rx} 0 0 1 ${x + rx} ${y} H${x + w - rx} A${rx} ${rx} 0 0 1 ${x + w} ${y + rx}"/>`;

// A component box: title, formula lines, caption lines.
function box(part, x, y, w, h, title, formulas, captions, opts = {}) {
  const cx = x + w / 2;
  let out = `<g class="dg-part dg-box" data-part="${part}">`;
  out += `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="9"/>`;
  out += tab(x, y, w);
  let yy = y + (opts.titleY || 24);
  out += text(title, cx, yy, 'dg-title');
  yy += opts.gapAfterTitle || 25;
  for (const f of formulas) {
    out += tex(f, cx, yy, opts.mathSize || 14.5).markup;
    yy += opts.lineGap || 21;
  }
  yy += (opts.captionGap || 0) - 3;
  for (const c of captions) {
    out += text(c, cx, yy, 'dg-cap');
    yy += 15;
  }
  return out + '</g>';
}

// Arrow along a polyline; arrowhead drawn as a path at the final point (no marker ids).
function arrow(part, pts, { dashed = false, label, lx, ly, lanchor = 'middle', math = false, head = true } = {}) {
  const d = 'M' + pts.map(p => p.map(r).join(' ')).join(' L');
  let out = `<g class="dg-part dg-edge${dashed ? ' dashed' : ''}" data-part="${part}"><path class="dg-line" d="${d}"/>`;
  if (head) {
    const [x2, y2] = pts[pts.length - 1], [x1, y1] = pts[pts.length - 2];
    const a = Math.atan2(y2 - y1, x2 - x1), L = 7.5, Wd = 4.2;
    const bx = x2 - L * Math.cos(a), by = y2 - L * Math.sin(a);
    const p1 = [bx + Wd * Math.sin(a), by - Wd * Math.cos(a)], p2 = [bx - Wd * Math.sin(a), by + Wd * Math.cos(a)];
    out += `<path class="dg-head" d="M${r(x2)} ${r(y2)} L${r(p1[0])} ${r(p1[1])} L${r(p2[0])} ${r(p2[1])} Z"/>`;
  }
  if (label) out += math ? tex(label, lx, ly, 13, lanchor).markup.replace('class="dg-math"', 'class="dg-math dg-lab"') : text(label, lx, ly, 'dg-elab', lanchor);
  return out + '</g>';
}

// Chips inside the information band.
function chips(lines, x0, y, maxW) {
  let out = '', row = 0;
  for (const line of lines) {
    const total = line.reduce((s, it) => s + it.w, 0) + 8 * (line.length - 1);
    let xx = x0 + (maxW - total) / 2;
    for (const it of line) {
      out += `<rect class="dg-chip" x="${r(xx)}" y="${r(y + row * 30)}" width="${it.w}" height="23" rx="11.5"/>`;
      if (it.math) out += tex(it.math, xx + 10, y + row * 30 + 16, 13.5, 'start').markup;
      const tx = it.math ? xx + 10 + tex(it.math, 0, 0, 13.5).width + 5 : xx + it.w / 2;
      out += text(it.label, tx, y + row * 30 + 15.5, 'dg-chip-t', it.math ? 'start' : 'middle');
      xx += it.w + 8;
    }
    row++;
  }
  return out;
}

const INFO_ITEMS = [
  [{ label: 'history', math: 'w_{[t]}', w: 98 }, { label: 'observations', w: 104 }, { label: 'forecasts', w: 82 }],
  [{ label: 'estimated law', math: '\\widehat{\\mathbb P}', w: 128 }, { label: 'ambiguity set', math: '\\mathcal A', w: 124 }],
];

const F = {
  value: ['\\mathcal V_{t+1}(\\hat{\\mathbf x}_t;w_{[t]})=\\mathbb E\\big[V_{t+1}\\mid w_{[t]}\\big]'],
  state: ['\\hat{\\mathbf x}_t=\\pi(w_{[t]},\\hat{\\mathbf x}_{t-1};\\theta)'],
  recourse: ['\\mathbf y_t^\\star\\in\\arg\\min_{\\mathbf y}\\ f(\\hat{\\mathbf x}_t,\\mathbf y)', '\\mathbf y\\in\\mathcal Y_t(\\hat{\\mathbf x}_{t-1},\\hat{\\mathbf x}_t;w_t)'],
  duals: ['(\\boldsymbol\\mu_t,\\bar{\\boldsymbol\\lambda}_t)=\\partial q_t/\\partial(\\hat{\\mathbf x}_{t-1},\\hat{\\mathbf x}_t)'],
  sens: ['\\partial\\mathbf y_t^\\star/\\partial(\\hat{\\mathbf x}_{t-1},\\hat{\\mathbf x}_t)'],
};
const T = {
  info: 'Stochastic process and information',
  value: 'Future value',
  state: 'State decisions',
  recourse: 'Recourse decisions',
  duals: 'Value sensitivity',
  sens: 'Solution sensitivity',
};
const C = {
  value: ['value function, critic, or rollout'],
  state: ['policy, target, or optimized state'],
  recourse: ['optimizer, controller, market, or proxy'],
  duals: ['multipliers: how the cost changes'],
  sens: ['how the decision itself changes'],
};

function wrap(cls, w, h, label, body) {
  return `<svg class="dg ${cls}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(label)}" xmlns="http://www.w3.org/2000/svg">${body}</svg>`;
}

const STAGE_LABEL = 'One stage of a sequential decision process. A stochastic process supplies the observed history, forecasts, an estimated law, and an ambiguity set. State decisions prescribe the state passed to the next stage, informed by the future value of that state; recourse decisions implement the transition; value sensitivities (dual multipliers) and solution sensitivities return local response information to the state decision.';

// ---------------------------------------------------------------- stage, two columns
function stageGrid() {
  const W = 548;
  const L = 14, LW = 252, R = 290, RW = 244; // columns
  const yB = 12, hB = 98, yV = 150, hV = 104, yS = 302, hS = 112, yD = 462, hD = 96;
  let b = '';
  // information band
  b += `<g class="dg-part dg-box dg-band" data-part="info"><rect x="${L}" y="${yB}" width="${R + RW - L}" height="${hB}" rx="10"/>${tab(L, yB, R + RW - L, 10)}`;
  b += text(T.info, W / 2, yB + 25, 'dg-title');
  b += chips(INFO_ITEMS, L + 14, yB + 38, R + RW - L - 28);
  b += '</g>';
  // boxes
  b += box('value', L, yV, 200, hV, T.value, F.value, C.value, { mathSize: 13, gapAfterTitle: 30, captionGap: 10 });
  b += box('state', L, yS, LW, hS, T.state, F.state, C.state, { gapAfterTitle: 30, captionGap: 12 });
  b += box('recourse', R, yS, RW, hS, T.recourse, F.recourse, C.recourse, { gapAfterTitle: 24, lineGap: 22 });
  b += box('duals', L, yD, LW, hD, T.duals, F.duals, C.duals, { gapAfterTitle: 28, captionGap: 6 });
  b += box('sens', R, yD, RW, hD, T.sens, F.sens, C.sens, { gapAfterTitle: 28, captionGap: 6 });
  // edges: information
  b += arrow('info value', [[114, yB + hB], [114, yV]], { label: 'w_{[t]}', lx: 120, ly: yV - 16, lanchor: 'start', math: true });
  b += arrow('info state', [[240, yB + hB], [240, yS]], { label: 'w_{[t]}', lx: 246, ly: yV + 46, lanchor: 'start', math: true });
  b += arrow('info recourse', [[R + RW - 44, yB + hB], [R + RW - 44, yS]], { label: 'w_t', lx: R + RW - 38, ly: yV + 46, lanchor: 'start', math: true });
  // value <-> state
  b += arrow('state value', [[60, yS], [60, yV + hV]], { label: '\\hat{\\mathbf x}_t', lx: 54, ly: yV + hV + 29, lanchor: 'end', math: true });
  b += arrow('value state', [[150, yV + hV], [150, yS]], { dashed: true, label: '\\mathcal V_{t+1},\\,\\nabla\\mathcal V_{t+1}', lx: 156, ly: yV + hV + 29, lanchor: 'start', math: true });
  // state -> recourse
  b += arrow('state recourse', [[L + LW, yS + 38], [R, yS + 38]], { label: '\\hat{\\mathbf x}_t', lx: (L + LW + R) / 2, ly: yS + 30, math: true });
  // recourse -> duals, duals -> state
  b += arrow('recourse duals', [[R + 34, yS + hS], [R + 34, yS + hS + 24], [L + LW - 40, yS + hS + 24], [L + LW - 40, yD]], { dashed: true });
  b += arrow('duals state', [[60, yD], [60, yS + hS]], { dashed: true, label: '\\bar{\\boldsymbol\\lambda}_t', lx: 54, ly: yD - 14, lanchor: 'end', math: true });
  // recourse -> sens, sens -> state (through the gutter)
  b += arrow('recourse sens', [[R + RW - 60, yS + hS], [R + RW - 60, yD]], { dashed: true });
  b += arrow('sens state', [[R, yD + hD / 2], [(L + LW + R) / 2, yD + hD / 2], [(L + LW + R) / 2, yS + hS - 26], [L + LW, yS + hS - 26]], { dashed: true });
  return wrap('dg-stage dg-grid', W, yD + hD + 12, STAGE_LABEL, b);
}

// ---------------------------------------------------------------- stage, one column
function stageStack() {
  const W = 360, X = 36, BW = 288; // left gutter carries returns, right gutter carries information
  const yB = 10, hB = 128, yV = 176, hV = 100, yS = 314, hS = 98, yR = 450, hR = 118, yD = 606, hD = 90, yN = 726, hN = 90;
  let b = '';
  b += `<g class="dg-part dg-box dg-band" data-part="info"><rect x="${X}" y="${yB}" width="${BW}" height="${hB}" rx="10"/>${tab(X, yB, BW, 10)}`;
  b += text(T.info, W / 2, yB + 25, 'dg-title');
  const [[hist, obs, fc], [law, amb]] = INFO_ITEMS;
  b += chips([[hist, obs], [fc, law], [amb]], X + 10, yB + 36, BW - 20);
  b += '</g>';
  b += box('value', X, yV, BW, hV, T.value, F.value, C.value, { mathSize: 13.5, gapAfterTitle: 28, captionGap: 8 });
  b += box('state', X, yS, BW, hS, T.state, F.state, C.state);
  b += box('recourse', X, yR, BW, hR, T.recourse, F.recourse, C.recourse, { gapAfterTitle: 24, lineGap: 22 });
  b += box('duals', X, yD, BW, hD, T.duals, F.duals, C.duals);
  b += box('sens', X, yN, BW, hN, T.sens, F.sens, C.sens);
  // information down the right gutter
  b += arrow('info value', [[W / 2, yB + hB], [W / 2, yV]]);
  b += arrow('info state', [[X + BW, yB + hB - 30], [X + BW + 16, yB + hB - 30], [X + BW + 16, yS + 30], [X + BW, yS + 30]]);
  b += arrow('info recourse', [[X + BW + 16, yS + 30], [X + BW + 16, yR + 30], [X + BW, yR + 30]]);
  // value -> state, state -> recourse
  b += arrow('value state', [[W / 2, yV + hV], [W / 2, yS]], { dashed: true });
  b += arrow('state recourse', [[W / 2, yS + hS], [W / 2, yR]], { label: '\\hat{\\mathbf x}_t', lx: W / 2 + 8, ly: yS + hS + 24, lanchor: 'start', math: true });
  // recourse -> duals; recourse -> sensitivities along the right gutter
  b += arrow('recourse duals', [[W / 2, yR + hR], [W / 2, yD]], { dashed: true });
  b += arrow('recourse sens', [[X + BW, yR + hR - 24], [X + BW + 16, yR + hR - 24], [X + BW + 16, yN + 30], [X + BW, yN + 30]], { dashed: true });
  // returns to the state decision along the left gutter
  b += arrow('duals state', [[X, yD + 30], [X - 18, yD + 30], [X - 18, yS + 60], [X, yS + 60]], { dashed: true });
  b += arrow('sens state', [[X, yN + 30], [X - 18, yN + 30], [X - 18, yD + 30]], { dashed: true, head: false });
  return wrap('dg-stage dg-stack', W, yN + hN + 10, STAGE_LABEL, b);
}

// ---------------------------------------------------------------- an optimization with its own objective
const THROUGH_LABEL = 'A learned map sets the parameters p of an optimization model that minimizes its own objective; the returned decision y* and multipliers are scored by a different evaluation L. Forward arrows carry p and the solution; dashed arrows return the derivative of L through the solution sensitivity D_p(y*, λ*).';
const TB = {
  map: ['Learned map', ['p=\\phi_\\theta(w)'], ['offers, targets, or model coefficients']],
  opt: ['Optimization with its own objective', ['\\mathbf y^\\star(p;w)\\in\\operatorname*{arg\\,min}_{\\mathbf y\\in\\mathcal Y(p;w)} f(\\mathbf y;p,w)'], ['market clearing, simplified model, or controller']],
  evals: ['Evaluation', ['L(\\mathbf y^\\star,\\boldsymbol\\lambda^\\star;w)'], ['the decision maker’s criterion']],
};
function throughWide() {
  const W = 920, y = 14, h = 110, w1 = 214, w2 = 280, gap = (W - 28 - w1 * 2 - w2) / 2;  // gap fits the return-arrow labels
  const x1 = 14, x2 = x1 + w1 + gap, x3 = x2 + w2 + gap;
  let b = '';
  b += box('map', x1, y, w1, h, ...TB.map, { gapAfterTitle: 32, captionGap: 12 });
  b += box('opt', x2, y, w2, h, ...TB.opt, { gapAfterTitle: 32, captionGap: 12, mathSize: 14 });
  b += box('evals', x3, y, w1, h, ...TB.evals, { gapAfterTitle: 32, captionGap: 12 });
  const fy = y + 40, by = y + h - 30;
  b += arrow('map opt', [[x1 + w1, fy], [x2, fy]], { label: 'p', lx: (x1 + w1 + x2) / 2, ly: fy - 9, math: true });
  b += arrow('opt evals', [[x2 + w2, fy], [x3, fy]], { label: '\\mathbf y^\\star,\\boldsymbol\\lambda^\\star', lx: (x2 + w2 + x3) / 2, ly: fy - 9, math: true });
  b += arrow('evals opt', [[x3, by], [x2 + w2, by]], { dashed: true, label: '\\partial L/\\partial(\\mathbf y^\\star,\\boldsymbol\\lambda^\\star)', lx: (x2 + w2 + x3) / 2, ly: by + 23, math: true });
  b += arrow('opt map', [[x2, by], [x1 + w1, by]], { dashed: true, label: 'D_p(\\mathbf y^\\star,\\boldsymbol\\lambda^\\star)', lx: (x1 + w1 + x2) / 2, ly: by + 23, math: true });
  return wrap('dg-through dg-grid', W, y + h + 16, THROUGH_LABEL, b);
}
function throughStack() {
  const W = 360, X = 50, BW = 270, h = 104, g = 58;
  const y1 = 10, y2 = y1 + h + g, y3 = y2 + h + g;
  let b = '';
  b += box('map', X, y1, BW, h, ...TB.map, { gapAfterTitle: 30, captionGap: 10 });
  b += box('opt', X, y2, BW, h + 10, TB.opt[0], ['\\mathbf y^\\star(p;w)\\in\\operatorname*{arg\\,min}_{\\mathbf y\\in\\mathcal Y(p;w)} f(\\mathbf y;p,w)'], ['market clearing, simplified model,', 'or controller'], { gapAfterTitle: 30, mathSize: 13.5, captionGap: 8 });
  b += box('evals', X, y3 + 10, BW, h, ...TB.evals, { gapAfterTitle: 30, captionGap: 10 });
  const fx = X + BW - 70, bx = X + 70;
  b += arrow('map opt', [[fx, y1 + h], [fx, y2]], { label: 'p', lx: fx + 8, ly: y1 + h + 34, lanchor: 'start', math: true });
  b += arrow('opt evals', [[fx, y2 + h + 10], [fx, y3 + 10]], { label: '\\mathbf y^\\star,\\boldsymbol\\lambda^\\star', lx: fx + 8, ly: y2 + h + 44, lanchor: 'start', math: true });
  b += arrow('evals opt', [[bx, y3 + 10], [bx, y2 + h + 10]], { dashed: true, label: '\\partial L/\\partial(\\mathbf y^\\star,\\boldsymbol\\lambda^\\star)', lx: bx - 8, ly: y2 + h + 44, lanchor: 'end', math: true });
  b += arrow('opt map', [[bx, y2], [bx, y1 + h]], { dashed: true, label: 'D_p(\\mathbf y^\\star,\\boldsymbol\\lambda^\\star)', lx: bx - 8, ly: y1 + h + 34, lanchor: 'end', math: true });
  return wrap('dg-through dg-stack', W, y3 + 10 + h + 12, THROUGH_LABEL, b);
}

fs.mkdirSync(OUT, { recursive: true });
fs.writeFileSync(path.join(OUT, 'stage.svg.html'), stageGrid() + '\n' + stageStack() + '\n');
fs.writeFileSync(path.join(OUT, 'through.svg.html'), throughWide() + '\n' + throughStack() + '\n');
console.log('wrote', fs.readdirSync(OUT).join(', '));
