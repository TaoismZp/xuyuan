const { chromium } = require('playwright');
const fs = require('fs');
const url = process.env.TARGET_URL || 'http://127.0.0.1:4173';
const shot = process.env.SHOT_PREFIX || 'local';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()) });

  for (let tries = 0; tries < 4; tries++) {
    try { await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 }); break; }
    catch (e) { if (tries === 3) throw e; await page.waitForTimeout(2500); }
  }

  fs.mkdirSync('artifacts', { recursive: true });
  await page.screenshot({ path: `artifacts/${shot}-intro.png`, fullPage: true });

  const start = page.getByRole('button', { name: '进入第一幕' });
  if (await start.count() !== 1) throw new Error('Start CTA missing');
  await start.click();

  for (let i = 0; i < 10; i++) {
    const act = page.getByRole('button', { name: '进入这一幕' });
    if (await act.count() && await act.isVisible()) await act.click();

    const choices = page.locator('button.choice');
    if (await choices.count() !== 4) throw new Error(`Round ${i + 1}: expected 4 balanced choices`);
    if (i === 0) await page.screenshot({ path: `artifacts/${shot}-question.png`, fullPage: true });

    await choices.nth(i % 4).click();

    const reveal = page.locator('.reveal');
    if (await reveal.count() !== 1) throw new Error(`Round ${i + 1}: reveal screen missing`);

    const nextName = i === 9 ? '揭晓我的 FIN·TYPE' : '继续下一手';
    const next = page.getByRole('button', { name: nextName });
    if (await next.count() !== 1) throw new Error(`Round ${i + 1}: next CTA missing`);
    await next.click();
  }

  const code = (await page.locator('.typecode').textContent() || '').trim();
  if (!/^[RG][FM][SI][HT]$/.test(code)) throw new Error(`Invalid FIN·TYPE: ${code}`);
  if (await page.locator('.typename').count() !== 1) throw new Error('Result name missing');
  if (await page.getByRole('button', { name: '分享我的 FIN·TYPE' }).count() !== 1) throw new Error('Share CTA missing');

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  if (overflow > 2) throw new Error(`Horizontal overflow: ${overflow}px`);

  await page.screenshot({ path: `artifacts/${shot}-result.png`, fullPage: true });

  await page.getByRole('button', { name: '再来一局' }).click();
  if (await page.getByRole('button', { name: '进入第一幕' }).count() !== 1) throw new Error('Replay reset failed');

  if (errors.length) throw new Error(errors.join(' | '));
  console.log(`PASS ${url} -> ${code}; 10 dilemmas + 5 acts + result + replay; no overflow/errors.`);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
