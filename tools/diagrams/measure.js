// Measure how large each diagram <img> is displayed on the built site.
//   tools/lock.sh node tools/diagrams/measure.js 1440,390 research/dc2ac/ ...   (server: python3 tools/serve.py on :8767)
// Prints one JSON line per diagram: page, viewport width, file actually shown (picture/source aware),
// displayed CSS width and the SVG's own width, so px-per-diagram-px = shown / natural.
'use strict';
const puppeteer = require('puppeteer-core');
const BASE = process.env.SITE_BASE || 'http://127.0.0.1:8767/AndrewRosemberg/';
(async () => {
  const [widths, ...pages] = process.argv.slice(2);
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new' });
  try {
    for (const w of widths.split(',').map(Number)) {
      const p = await b.newPage();
      await p.setViewport({ width: w, height: 900, deviceScaleFactor: 1 });
      for (const pg of pages) {
        await p.goto(BASE + pg, { waitUntil: 'networkidle0' });
        const rows = await p.$$eval('img', (imgs) => imgs.filter((i) => /\/diagrams\//.test(i.currentSrc || i.src)).map((i) => ({
          src: (i.currentSrc || i.src).split('/').pop(), shown: i.getBoundingClientRect().width, natural: i.naturalWidth })));
        for (const r of rows) console.log(JSON.stringify({ page: pg, viewport: w, ...r }));
      }
      await p.close();
    }
  } finally { await b.close(); }
})();
