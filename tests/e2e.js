const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  page.on('pageerror', err => errors.push(String(err)));

  await page.goto('http://127.0.0.1:4173', { waitUntil: 'networkidle' });
  await page.getByText('开始这局市场人生').click();

  for (let i = 0; i < 18; i++) {
    const choices = page.locator('button.choice');
    if (await choices.count() !== 2) throw new Error(`Round ${i + 1}: expected 2 choices`);
    await choices.nth(i % 2).click();
    await page.getByText('继续', { exact: true }).click();
    const nextAct = page.getByText('进入下一幕', { exact: true });
    if (await nextAct.count() && await nextAct.isVisible()) await nextAct.click();
  }

  const code = (await page.locator('.code').textContent() || '').trim();
  if (!/^[RG][FM][SI][HT]$/.test(code)) throw new Error(`Invalid result code: ${code}`);
  if (errors.length) throw new Error(`Page errors: ${errors.join(' | ')}`);
  if (await page.getByText('再玩一局').count() !== 1) throw new Error('Replay CTA missing');

  await page.getByText('再玩一局').click();
  if (await page.getByText('开始这局市场人生').count() !== 1) throw new Error('Restart flow failed');

  console.log(`PASS: full 18-decision flow -> ${code}; replay works; no page errors.`);
  await browser.close();
})().catch(err => { console.error(err); process.exit(1); });
