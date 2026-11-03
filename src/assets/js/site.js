'use strict';
// Small progressive enhancements. Every page is complete without JavaScript.

// Copy BibTeX to the clipboard.
document.addEventListener('click', async event => {
  const button = event.target.closest('.copy-bib');
  if (!button) return;
  const text = button.parentElement.querySelector('code').textContent;
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = 'Copied';
  } catch {
    button.textContent = 'Select & copy';
  }
  setTimeout(() => { button.textContent = 'Copy'; }, 1600);
});

// Publication type filters.
const filters = document.querySelector('.pub-filters');
if (filters) {
  const items = [...document.querySelectorAll('.pub-year .pub')];
  const buttons = [...filters.querySelectorAll('button')];
  for (const button of buttons) {
    const types = button.dataset.types ? button.dataset.types.split(' ') : null;
    const count = types ? items.filter(item => types.includes(item.dataset.type)).length : items.length;
    button.insertAdjacentHTML('beforeend', `<span class="count">${count}</span>`);
    button.addEventListener('click', () => {
      for (const other of buttons) other.setAttribute('aria-pressed', String(other === button));
      for (const item of items) item.hidden = types !== null && !types.includes(item.dataset.type);
      for (const year of document.querySelectorAll('.pub-year')) {
        year.hidden = !year.querySelector('.pub:not([hidden])');
      }
    });
  }
}

// Highlight the current section in a project page's table of contents.
const tocLinks = [...document.querySelectorAll('.toc a')];
if (tocLinks.length && 'IntersectionObserver' in window) {
  const sections = tocLinks.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      for (const link of tocLinks) link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`);
    }
  }, { rootMargin: '-20% 0px -70% 0px' });
  sections.forEach(section => observer.observe(section));
}

// Economic-dispatch explorer (differentiable optimization page).
// Same data as Case Study 1 of arXiv:2510.25986; solved in closed form.
const explorer = document.querySelector('[data-dispatch]');
if (explorer) {
  const c = [20, 30], c2 = [0.2, 0.1], cap = [150, 80], penalty = 1000;
  const solve = d => {
    let lo = 0, hi = penalty, g = [0, 0];
    for (let k = 0; k < 80; k++) {
      const lam = (lo + hi) / 2;
      g = c.map((ci, i) => Math.min(Math.max((lam - ci) / (2 * c2[i]), 0), cap[i]));
      if (g[0] + g[1] < d) lo = lam; else hi = lam;
    }
    const lam = (lo + hi) / 2;
    g = c.map((ci, i) => Math.min(Math.max((lam - ci) / (2 * c2[i]), 0), cap[i]));
    const unmet = Math.max(d - g[0] - g[1], 0);
    // Sensitivities: plants strictly between their bounds share demand changes
    // in proportion to 1 / (2 c2_i); unmet demand absorbs them once both are full.
    const free = g.map((gi, i) => gi > 1e-6 && gi < cap[i] - 1e-6);
    const weights = free.map((f, i) => (f ? 1 / (2 * c2[i]) : 0));
    const total = weights[0] + weights[1];
    const sens = total > 0 ? weights.map(w => w / total) : [0, 0];
    return { g, unmet, price: unmet > 1e-6 ? penalty : lam, sens };
  };
  const input = explorer.querySelector('input');
  const out = name => explorer.querySelector(`[data-out="${name}"]`);
  const bar = name => explorer.querySelector(`[data-bar="${name}"]`);
  const render = () => {
    const d = Number(input.value);
    const r = solve(d);
    out('d').textContent = `${d} MWh`;
    out('g1').textContent = r.g[0].toFixed(1);
    out('g2').textContent = r.g[1].toFixed(1);
    out('phi').textContent = r.unmet.toFixed(1);
    out('price').textContent = r.price >= penalty ? '1000 (penalty)' : r.price.toFixed(1);
    out('s1').textContent = r.sens[0].toFixed(2);
    out('s2').textContent = r.sens[1].toFixed(2);
    out('regime').textContent =
      d < 25 ? 'Only plant 1 is marginal: it absorbs every extra MWh.'
      : r.g[1] < cap[1] - 1e-6 ? 'Both plants are marginal: extra demand splits 1/3 to plant 1 and 2/3 to plant 2, in inverse proportion to their cost curvature.'
      : r.g[0] < cap[0] - 1e-6 ? 'Plant 2 is at capacity: its sensitivity drops to zero and plant 1 takes everything.'
      : 'Both plants are full: extra demand goes unserved and the price jumps to the penalty.';
    bar('g1').style.width = `${(r.g[0] / 260) * 100}%`;
    bar('g2').style.width = `${(r.g[1] / 260) * 100}%`;
    bar('phi').style.width = `${(r.unmet / 260) * 100}%`;
    bar('s1').style.width = `${r.sens[0] * 100}%`;
    bar('s2').style.width = `${r.sens[1] * 100}%`;
  };
  input.addEventListener('input', render);
  explorer.hidden = false;
  render();
}

// Dark-mode toggle (light by default, like the paper websites).
for (const button of document.querySelectorAll('[data-theme-toggle]')) {
  button.addEventListener('click', () => {
    const dark = document.documentElement.dataset.theme !== 'dark';
    if (dark) document.documentElement.dataset.theme = 'dark';
    else delete document.documentElement.dataset.theme;
    try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch {}
  });
}

// Quick search: ⌘K / Ctrl+K or "/" opens a palette over pages, projects and papers.
const palette = document.querySelector('dialog.palette');
if (palette && typeof palette.showModal === 'function') {
  const root = palette.dataset.root;
  const input = palette.querySelector('input');
  const list = palette.querySelector('.palette-results');
  let index = null, results = [], active = 0;
  const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const load = async () => {
    if (index) return index;
    const response = await fetch(`${root}assets/search.json`);
    index = (await response.json()).map(item => ({ ...item, hay: norm(`${item.title} ${item.meta || ''} ${item.keywords || ''}`) }));
    return index;
  };
  const resolve = url => (/^(https?:|mailto:)/.test(url) ? url : root + url);
  const render = () => {
    const terms = norm(input.value).split(/\s+/).filter(Boolean);
    results = (index || []).filter(item => terms.every(t => item.hay.includes(t))).slice(0, 12);
    active = 0;
    list.replaceChildren();
    if (!results.length) {
      list.innerHTML = '<li class="empty">No matches. Try “OPF”, “SDDP”, “DiffOpt” or “teaching”.</li>';
      return;
    }
    results.forEach((item, i) => {
      const li = document.createElement('li');
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', String(i === active));
      const a = document.createElement('a');
      a.href = resolve(item.url);
      a.innerHTML = `<small></small><span></span>`;
      a.querySelector('small').textContent = item.type;
      a.querySelector('span').textContent = item.title;
      if (item.meta) { const em = document.createElement('em'); em.textContent = item.meta; a.querySelector('span').append(em); }
      li.append(a);
      list.append(li);
    });
  };
  const move = step => {
    const items = [...list.querySelectorAll('[role="option"]')];
    if (!items.length) return;
    active = (active + step + items.length) % items.length;
    items.forEach((li, i) => li.setAttribute('aria-selected', String(i === active)));
    items[active].scrollIntoView({ block: 'nearest' });
  };
  const open = async () => {
    if (palette.open) return;
    palette.showModal();
    input.value = '';
    await load();
    render();
    input.focus();
  };
  document.querySelectorAll('[data-search-open]').forEach(b => b.addEventListener('click', open));
  document.addEventListener('keydown', event => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
    if ((event.key === 'k' && (event.metaKey || event.ctrlKey)) || (event.key === '/' && !typing)) {
      event.preventDefault();
      open();
    }
  });
  input.addEventListener('input', render);
  input.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown') { event.preventDefault(); move(1); }
    if (event.key === 'ArrowUp') { event.preventDefault(); move(-1); }
    if (event.key === 'Enter') {
      event.preventDefault();
      const link = list.querySelectorAll('[role="option"] a')[active];
      if (link) location.href = link.href;
    }
  });
  palette.addEventListener('click', event => { if (event.target === palette) palette.close(); });
  if (!/Mac|iPhone|iPad/.test(navigator.platform)) document.querySelectorAll('.search-btn kbd').forEach(k => { k.textContent = 'Ctrl K'; });
}

// Thesis diagram: hovering a block or its description highlights the other (and nothing else).
for (const thesis of document.querySelectorAll('.thesis-block')) {
  const items = [...thesis.querySelectorAll('[data-key]')];
  const keysOf = el => el.dataset.key.split(' ');
  const light = keys => items.forEach(el => el.classList.toggle('is-lit', keys !== null && keysOf(el).some(k => keys.includes(k))));
  for (const el of items) {
    el.addEventListener('mouseenter', () => light(keysOf(el)));
    el.addEventListener('mouseleave', () => light(null));
    el.addEventListener('focus', () => light(keysOf(el)));
    el.addEventListener('blur', () => light(null));
  }
}

// Click a figure to see it larger (diagrams are dense). Esc or click closes.
(() => {
  const imgs = document.querySelectorAll('.fig .frame img, .tool-media img, .direction-media img');
  if (!imgs.length || typeof HTMLDialogElement === 'undefined') return;
  const box = document.createElement('dialog');
  box.className = 'lightbox';
  box.innerHTML = '<img alt=""><p></p>';
  document.body.append(box);
  const big = box.querySelector('img'), cap = box.querySelector('p');
  for (const img of imgs) {
    img.classList.add('zoomable');
    img.addEventListener('click', event => {
      event.preventDefault();
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      const fc = img.closest('figure')?.querySelector('figcaption');
      cap.textContent = fc ? fc.textContent : '';
      box.showModal();
    });
  }
  box.addEventListener('click', () => box.close());
})();

// Display equations: choose the layout that fits the space actually available.
// A responsive pair (.eq-r: .eq-wide + .eq-narrow) shows the wide form whenever it fits at
// 85% of the text size or more, and the narrow form only when it does not. Any display still
// wider than its box is scaled down (to 70% at most) instead of being clipped.
window.fitEquations = () => {
  const natural = (box) => {
    const k = box.querySelector('.katex-display > .katex');
    if (!k) return 0;
    k.style.display = 'inline-block';  // natural width (centered overflow is not counted by scrollWidth)
    const w = k.getBoundingClientRect().width;
    k.style.display = '';
    return w;
  };
  const room = (box) => {
    const cs = getComputedStyle(box);
    return box.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  };
  const scale = (box, need, floor) => {
    box.style.fontSize = '';
    const r = room(box);
    if (need > r + 1) {
      const base = parseFloat(getComputedStyle(box).fontSize);
      box.style.fontSize = `${Math.max(base * floor, base * (r / need) * 0.99)}px`;
    }
  };
  // Variants are ordered from widest (e.g. a one-line statement) to narrowest (a phone layout);
  // the first one that fits at 85% of the text size or more is shown.
  for (const pair of document.querySelectorAll('.eq-r')) {
    const vs = [...pair.children].filter((c) => c.classList.contains('eq'));
    if (!vs.length || !pair.offsetParent) continue;
    for (const v of vs) { v.style.fontSize = ''; v.style.display = 'block'; }
    const r = room(vs[0]);
    const needs = vs.map(natural);
    let pick = vs.length - 1;
    for (let i = 0; i < vs.length; i++) if (needs[i] && needs[i] <= r / 0.85) { pick = i; break; }
    vs.forEach((v, i) => { v.style.display = i === pick ? 'block' : 'none'; });
    scale(vs[pick], needs[pick], 0.7);
  }
  for (const box of document.querySelectorAll('.eq')) {
    if (box.parentElement.classList.contains('eq-r') || !box.offsetParent) continue;
    scale(box, natural(box), 0.7);
  }
};
let fitTimer;
window.addEventListener('resize', () => { clearTimeout(fitTimer); fitTimer = setTimeout(() => window.fitEquations(), 120); });
