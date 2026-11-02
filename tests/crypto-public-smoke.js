const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL;
fs.mkdirSync('artifacts', { recursive: true });

async function verifySurface(browser, viewport, prefix, doRoll = false) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(target, { waitUntil: 'networkidle', timeout: 60000 });
  try {
    await page.waitForFunction(() => !!window.__chainTycoon3d, { timeout: 35000 });
  } catch (e) {
    const diag = await page.evaluate(() => ({
      url: location.href,
      title: document.title,
      text: document.body.innerText.slice(0, 600),
      bootError: document.body.dataset.bootError || null,
      scripts: [...document.scripts].map(s => ({ type: s.type, src: s.src, text: s.textContent.slice(0, 120) }))
    }));
    throw new Error('boot timeout ' + JSON.stringify(diag) + ' console=' + errors.join(' | '));
  }
  await page.screenshot({ path: `artifacts/${prefix}-intro.png`, fullPage: true });
  await page.getByRole('button', { name: '进入牌桌' }).click();
  await page.waitForFunction(() => JSON.parse(window.render_game_to_text()).players?.length === 4, { timeout: 15000 });
  const before = JSON.parse(await page.evaluate(() => window.render_game_to_text()));
  if (before.tiles !== 24 || before.players.length !== 4) throw new Error('bad public state ' + JSON.stringify(before));
  await page.waitForFunction(() => !document.querySelector('#roll').disabled, { timeout: 10000 });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: `artifacts/${prefix}-active.png`, fullPage: true });
  if (doRoll) {
    await page.locator('#roll').click();
    await page.waitForFunction(() => {
      const s = JSON.parse(window.render_game_to_text());
      return s.players[0].pos !== 0 || document.querySelector('#modal.show');
    }, { timeout: 15000 });
    await page.waitForTimeout(700);
    await page.screenshot({ path: `artifacts/${prefix}-after-roll.png`, fullPage: true });
  }
  await page.close();
}

(async () => {
  if (!target) throw new Error('TARGET_URL required');
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-webgl'] });
  await verifySurface(browser, { width: 1672, height: 941 }, 'reference-view', true);
  await verifySurface(browser, { width: 1194, height: 834 }, 'ipad-landscape', false);
  console.log('PASS public boot/start/roll + visual evidence', target);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
