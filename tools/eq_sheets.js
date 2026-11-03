// Render every visible display equation of a page into one numbered contact sheet, so the
// typography can be reviewed at a glance (wide and phone layouts).
//
//   tools/lock.sh node tools/eq_sheets.js <outdir> research/<slug>/ [more pages]
//
// Writes <outdir>/<slug>-<width>.png sheets (1440 and 390 px viewports) plus the single crops.
'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const puppeteer = require('puppeteer-core');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = process.env.SITE_BASE || 'http://127.0.0.1:8767/AndrewRosemberg/';
const [out, ...pages] = process.argv.slice(2);

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true });
  try {
    for (const p of pages) {
      const slug = p.replace(/\/$/, '').split('/').pop() || 'home';
      for (const w of [1440, 390]) {
        const page = await browser.newPage();
        await page.setViewport({ width: w, height: 900, deviceScaleFactor: 2, isMobile: w < 600 });
        await page.goto(BASE + p, { waitUntil: 'networkidle0' });
        await page.addStyleTag({ content: '.site-header,.toc{position:static!important}' });
        await new Promise((r) => setTimeout(r, 400));
        const boxes = await page.$$('.eq');
        const files = [];
        let i = 0;
        for (const b of boxes) {
          if (!(await b.evaluate((e) => !!e.offsetParent))) continue;
          i++;
          const f = path.join(out, `${slug}-${w}-${String(i).padStart(2, '0')}.png`);
          await b.screenshot({ path: f });
          files.push(f);
        }
        await page.close();
        if (files.length) {
          execFileSync('magick', ['montage', ...files.flatMap((f) => ['-label', path.basename(f, '.png').split('-').pop(), f]),
            '-tile', w < 600 ? '3x' : '2x', '-geometry', w < 600 ? '+12+12' : '+16+16', '-pointsize', '22',
            '-background', '#ffffff', path.join(out, `${slug}-${w}.png`)]);
        }
        console.log(`${slug} ${w}: ${files.length} equations`);
      }
    }
  } finally {
    await browser.close();
  }
})();
