const { chromium } = require('playwright');
const path = require('path');

const url = process.env.AOT_URL || 'https://activeoahutours.com/';
const outDir = process.env.AOT_SCREENSHOT_DIR || '/tmp';
const desktopPath = process.env.AOT_DESKTOP_SCREENSHOT || path.join(outDir, 'aot-desktop-nav-working.png');
const mobilePath = process.env.AOT_MOBILE_SCREENSHOT || path.join(outDir, 'aot-mobile-nav-working.png');

async function isVisible(locator) {
  return locator.evaluate(el => {
    const cs = window.getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity || '1') !== 0 && r.width > 0 && r.height > 0;
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await desktop.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await desktop.locator('#primary-menu > li').first().locator('a').first().hover();
  await desktop.waitForTimeout(800);
  const desktopVisible = await isVisible(desktop.locator('#primary-menu > li').first().locator('ul.sub-menu').first());
  const desktopTopLinks = await desktop.locator('#primary-menu > li > a').evaluateAll(els => els.map(a => ({
    text: a.textContent.trim(), href: a.href, visible: !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length)
  })));
  if (!desktopVisible) throw new Error('Desktop submenu did not become visible on hover.');
  if (desktopTopLinks.length < 4 || desktopTopLinks.some(x => !x.visible)) throw new Error('Desktop top-level nav links not all visible: ' + JSON.stringify(desktopTopLinks));
  await desktop.screenshot({ path: desktopPath, fullPage: false });
  await desktop.close();

  const mobile = await browser.newPage({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
  });
  await mobile.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await mobile.locator('button.menu-toggle').scrollIntoViewIfNeeded();
  await mobile.locator('button.menu-toggle').click();
  await mobile.waitForTimeout(800);
  const expanded = await mobile.locator('button.menu-toggle').getAttribute('aria-expanded');
  const mobileMenuVisible = await isVisible(mobile.locator('#primary-menu'));
  const mobileLinks = await mobile.locator('#primary-menu > li > a').evaluateAll(els => els.map(a => ({
    text: a.textContent.trim(), href: a.href, visible: !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length)
  })));
  if (expanded !== 'true') throw new Error('Mobile menu toggle aria-expanded was not true after click; got ' + expanded);
  if (!mobileMenuVisible) throw new Error('Mobile primary menu did not become visible after toggle.');
  if (mobileLinks.length < 4 || mobileLinks.some(x => !x.visible)) throw new Error('Mobile top-level nav links not all visible: ' + JSON.stringify(mobileLinks));
  await mobile.screenshot({ path: mobilePath, fullPage: false });
  await mobile.close();

  await browser.close();
  console.log(JSON.stringify({ ok: true, desktopPath, mobilePath, desktopTopLinks, mobileLinks }, null, 2));
})().catch(err => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
