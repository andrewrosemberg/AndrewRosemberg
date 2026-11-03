// Render pages in the installed Chrome and measure what a reader would see.
//
//   npm install --no-save puppeteer-core@23.11.1
//   python3 tools/serve.py &                      # _site/ under /AndrewRosemberg/ on :8767
//   tools/lock.sh node tools/render_check.js [--shots DIR] [--widths 1440,842,390] [--themes light,dark] [page ...]
//
// Pages are site paths such as research/dc2ac/ (default: home, research overview
// and every research page). For each page × width × theme it records document
// overflow, elements wider than the viewport, images that failed to load,
// KaTeX errors and unrendered TeX delimiters, failed requests and console
// errors. With --shots it also saves full-page JPEG screenshots. Exit status is
// 1 when any check fails. Run it through tools/lock.sh: one browser at a time.
'use strict';
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = process.env.SITE_BASE || 'http://127.0.0.1:8767/AndrewRosemberg/';

const args = process.argv.slice(2);
function opt(name, dflt) {
  const i = args.indexOf(name);
  if (i < 0) return dflt;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
}
const shots = opt('--shots', null);
const widths = opt('--widths', '1440,842,390').split(',').map(Number);
const themes = opt('--themes', 'light,dark').split(',');
const SITE = path.join(__dirname, '..', '_site');
const pages = args.length ? args : ['', 'research/', ...fs.readdirSync(path.join(SITE, 'research'))
  .filter((d) => fs.existsSync(path.join(SITE, 'research', d, 'index.html'))).map((d) => `research/${d}/`)];

// Runs in the page: scroll through once so lazy content loads, then measure.
async function measure() {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (let y = 0; y < document.body.scrollHeight; y += innerHeight * 0.8) { scrollTo(0, y); await sleep(60); }
  scrollTo(0, 0);
  const imgs = [...document.images].filter((im) => !im.closest('.lightbox'));
  for (const im of imgs) im.loading = 'eager';
  await Promise.all(imgs.map((im) => im.complete ? 0 : new Promise((r) => { im.onload = im.onerror = r; setTimeout(r, 4000); })));
  await document.fonts.ready;
  await sleep(300);
  const W = document.documentElement.clientWidth;
  const clipped = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox !== 'visible') return true;
    }
    return false;
  };
  const name = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const wide = [];
  for (const el of document.querySelectorAll('main *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || getComputedStyle(el).position === 'fixed') continue;
    if ((r.right > W + 1 || r.left < -1) && !clipped(el)) {
      const parentWide = el.parentElement && (() => { const q = el.parentElement.getBoundingClientRect(); return q.right > W + 1 || q.left < -1; })();
      if (!parentWide) wide.push(`${name(el)} [${Math.round(r.left)},${Math.round(r.right)}]`);
    }
  }
  const brokenImages = imgs.filter((im) => !im.complete || im.naturalWidth === 0).map((im) => (im.currentSrc || im.getAttribute('src') || im.outerHTML).slice(0, 120));
  const katexErrors = [...document.querySelectorAll('.katex-error')].map((e) => (e.getAttribute('title') || e.textContent).slice(0, 120));
  const rawTex = [];
  const walk = document.createTreeWalker(document.querySelector('main') || document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walk.nextNode());) {
    if (n.parentElement.closest('pre, code, script, style, .katex')) continue;
    if (/\\\(|\\\)|\\\[|\\\]|\$\$/.test(n.textContent)) rawTex.push(n.textContent.trim().slice(0, 100));
    else if (n.parentElement.closest('.katex') === null && /\[-?[\d.]+(em|pt|ex|mm)\]/.test(n.textContent)) rawTex.push('spacing token: ' + n.textContent.trim().slice(0, 80));
  }
  // Equations that fitEquations had to shrink (a responsive .eq-r pair should make this unnecessary).
  const eqShrunk = [];
  for (const box of document.querySelectorAll('.eq')) {
    if (!box.offsetParent || !box.style.fontSize) continue;
    const set = parseFloat(box.style.fontSize);
    box.style.fontSize = '';
    const base = parseFloat(getComputedStyle(box).fontSize);
    box.style.fontSize = set + 'px';
    if (set / base < 0.8) eqShrunk.push(`${Math.round(100 * set / base)}% ${(box.textContent || '').trim().slice(0, 50)}`);
  }
  return {
    eqShrunk: eqShrunk.slice(0, 12),
    overflow: document.documentElement.scrollWidth > W + 1 ? document.documentElement.scrollWidth - W : 0,
    wide: wide.slice(0, 12), brokenImages, katexErrors, rawTex: rawTex.slice(0, 12),
    height: document.documentElement.scrollHeight,
  };
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: true,
    args: ['--no-first-run', '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars'],
  });
  const report = [];
  let failed = 0;
  try {
    for (const p of pages) {
      for (const theme of themes) {
        for (const w of widths) {
          const page = await browser.newPage();
          const errors = [];
          page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 160)); });
          page.on('pageerror', (e) => errors.push('js: ' + String(e).slice(0, 160)));
          page.on('requestfailed', (r) => errors.push('failed: ' + r.url().slice(0, 160)));
          page.on('response', (r) => { if (r.status() >= 400) errors.push(`${r.status()}: ${r.url().slice(0, 160)}`); });
          const mobile = w < 600;
          await page.setViewport({ width: w, height: mobile ? 844 : 900, deviceScaleFactor: mobile ? 2 : 1, isMobile: mobile, hasTouch: mobile });
          await page.evaluateOnNewDocument((t) => { try { localStorage.setItem('theme', t); } catch (e) {} }, theme);
          await page.goto(BASE + p, { waitUntil: 'networkidle0', timeout: 60000 });
          const m = await page.evaluate(measure);
          m.errors = errors;
          const bad = m.eqShrunk.length || m.overflow || m.wide.length || m.brokenImages.length || m.katexErrors.length || m.rawTex.length || errors.length;
          if (bad) failed++;
          report.push({ page: p || '/', width: w, theme, ok: !bad, ...m });
          if (shots) {
            fs.mkdirSync(shots, { recursive: true });
            const file = path.join(shots, `${(p || 'home').replace(/\/$/, '').replace(/\//g, '_') || 'home'}-${w}-${theme}.jpg`);
            // Chrome cannot capture more than ~16k device pixels in one shot; longer pages
            // are saved as consecutive segments (-p1, -p2, ...).
            const dpr = mobile ? 2 : 1, seg = Math.floor(15000 / dpr);
            if (m.height <= seg) {
              await page.screenshot({ path: file, fullPage: true, type: 'jpeg', quality: 60 });
            } else {
              // Sticky elements would be painted at every segment's viewport offset.
              await page.addStyleTag({ content: '.site-header,.toc,.research-focus-grid>.dg-figure{position:static!important} .skip-link{display:none!important}' });
              for (let y = 0, k = 1; y < m.height; y += seg, k++) {
                await page.screenshot({ path: file.replace(/\.jpg$/, `-p${k}.jpg`), type: 'jpeg', quality: 60, captureBeyondViewport: true,
                  clip: { x: 0, y, width: w, height: Math.min(seg, m.height - y) } });
              }
            }
          }
          await page.close();
          console.log(`${bad ? 'FAIL' : 'ok  '} ${(p || '/').padEnd(42)} ${String(w).padStart(4)} ${theme.padEnd(5)}` +
            (bad ? '  ' + JSON.stringify({ eqShrunk: m.eqShrunk, overflow: m.overflow, wide: m.wide, brokenImages: m.brokenImages, katexErrors: m.katexErrors, rawTex: m.rawTex, errors }) : ''));
        }
      }
    }
  } finally {
    await browser.close();
  }
  if (shots) fs.writeFileSync(path.join(shots, 'report.json'), JSON.stringify(report, null, 1));
  console.log(`${report.length - failed}/${report.length} renders clean`);
  process.exit(failed ? 1 : 0);
})();
