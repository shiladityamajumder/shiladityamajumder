/* Optional browser validation: Node 20+ and Playwright. Run after preview.py. */
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'preview');

function files(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(e => e.isDirectory() ? files(path.join(dir, e.name)) : [path.join(dir, e.name)]);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  try {
    const page = await browser.newPage({ reducedMotion: 'reduce' });
    for (const width of [360, 390, 600, 768, 960]) {
      for (const theme of ['light', 'dark']) {
        await page.setViewportSize({ width, height: 1000 });
        await page.emulateMedia({ colorScheme: theme, reducedMotion: 'reduce' });
        await page.goto(pathToFileURL(path.join(output, 'index.html')).href);
        await page.evaluate(() => Promise.all([...document.images].map(image => image.decode())));
        const layout = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > innerWidth,
          images: [...document.images].map(i => ({ source: i.currentSrc, loaded: i.complete && i.naturalWidth > 0 })),
        }));
        assert(!layout.overflow, `Page overflow at ${width}px / ${theme}`);
        assert(layout.images.every(i => i.loaded), `Missing image at ${width}px`);
        assert(layout.images.every(i => /-mobile(?:-static)?\.svg$/.test(i.source) === (width <= 600)), `Incorrect picture selection at ${width}px`);
        assert(layout.images.filter(i => /\/hero\/|\/terminal\//.test(i.source)).every(i => i.source.endsWith('-static.svg')), 'Reduced motion must select explicit static sources');
        if ([360, 390, 960].includes(width)) {
          await page.screenshot({ path: path.join(output, `${width}-${theme}.png`), fullPage: true });
        }
      }
    }
    // Inspect native SVG geometry rather than inferring clipping from raster screenshots.
    for (const file of files(path.join(root, 'assets')).filter(f => f.endsWith('.svg'))) {
      await page.goto(pathToFileURL(file).href);
      const result = await page.evaluate(() => {
        const svg = document.querySelector('svg'), vb = svg.viewBox.baseVal;
        const inv = svg.getScreenCTM().inverse();
        const all = [...svg.querySelectorAll('text')].map(el => {
          const b = el.getBBox(), m = inv.multiply(el.getScreenCTM());
          const points = [new DOMPoint(b.x, b.y), new DOMPoint(b.x + b.width, b.y + b.height)].map(p => p.matrixTransform(m));
          return { text: el.textContent, left: points[0].x, top: points[0].y, right: points[1].x, bottom: points[1].y };
        });
        const clipped = all.filter(b => b.left < 0 || b.top < 0 || b.right > vb.width || b.bottom > vb.height);
        const overlaps = [];
        for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) {
          const a = all[i], b = all[j];
          if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1) overlaps.push([a.text, b.text]);
        }
        return { clipped, overlaps, dimensions: [vb.width, vb.height] };
      });
      if (result.clipped.length || result.overlaps.length) errors.push({ file: path.relative(root, file), ...result });
    }
    assert.deepEqual(errors, [], 'SVG clipping or overlapping text: ' + JSON.stringify(errors));
    await page.goto(pathToFileURL(path.join(root, 'assets/hero/hero.svg')).href);
    // Reduced motion hides SMIL packets; the complete architecture remains visible.
    assert(await page.locator('.motion').first().evaluate(el => getComputedStyle(el).display === 'none'));
    assert(await page.locator('.process').evaluate(el => getComputedStyle(el).animationName === 'none'));
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    const cycle = await page.evaluate(() => {
      const svg = document.querySelector('svg');
      svg.pauseAnimations();
      return [.8, 2.2, 3.8, 5.2, 6.5, 7.7, 8.9, 10.2, 11.3, 12.7].map(time => {
        svg.setCurrentTime(time);
        return [...svg.querySelectorAll('.motion circle')].filter(el => Number(getComputedStyle(el).opacity) > .5).map(el => {
          const m = el.getCTM(); return [Math.round(m.e), Math.round(m.f)];
        });
      });
    });
    assert(cycle.every(positions => positions.length === 1), 'Expected one purposeful packet per sampled request phase');
    // The image embedding context is checked separately from opening SVGs directly.
    await page.setViewportSize({ width: 960, height: 1000 });
    await page.goto(pathToFileURL(path.join(output, 'index.html')).href);
    await page.evaluate(() => Promise.all([...document.images].map(i => i.decode())));
    const hero = page.locator('img').first();
    const a = await hero.screenshot();
    await page.waitForTimeout(650);
    const b = await hero.screenshot();
    assert(!a.equals(b), 'Hero motion did not render when embedded as an image');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.waitForTimeout(100);
    const c = await hero.screenshot();
    await page.waitForTimeout(650);
    const d = await hero.screenshot();
    assert(c.equals(d), 'Reduced-motion image was not static');
    console.log('Passed: 22 SVG geometries; 10 viewport/theme layouts; picture selection; request-cycle motion; reduced motion; SVG image animation.');
    fs.writeFileSync(path.join(output, 'validation.json'), JSON.stringify({ widths: [360, 390, 600, 768, 960], themes: ['light', 'dark'], svgCount: 22, errors, cycle }, null, 2) + '\n');
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e.message); process.exitCode = 1; });
