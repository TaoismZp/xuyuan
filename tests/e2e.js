const { chromium } = require('playwright');
const fs = require('fs');
const url = process.env.TARGET_URL || 'http://127.0.0.1:4173';
const shot = process.env.SHOT_PREFIX || 'local';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type()==='error') errors.push('console: '+m.text()) });
  for (let tries=0; tries<4; tries++) {
    try { await page.goto(url, { waitUntil: 'networkidle', timeout: 25000 }); break; }
    catch(e){ if(tries===3) throw e; await page.waitForTimeout(2500); }
  }
  fs.mkdirSync('artifacts', { recursive:true });
  await page.screenshot({path:`artifacts/${shot}-intro.png`, fullPage:true});
  if (await page.getByRole('button',{name:'进入市场'}).count() !== 1) throw new Error('Start CTA missing');
  await page.getByRole('button',{name:'进入市场'}).click();
  await page.screenshot({path:`artifacts/${shot}-question.png`, fullPage:true});
  for (let i=0;i<12;i++) {
    const choices=page.locator('button.choice');
    if(await choices.count()!==3) throw new Error(`Round ${i+1}: expected 3 choices`);
    await choices.nth(i%3).click();
    const settle=page.locator('.settle');
    if(await settle.count()!==1) throw new Error(`Round ${i+1}: settlement screen missing`);
    const next=i===11?page.getByRole('button',{name:'查看你的 FIN·TYPE'}):page.getByRole('button',{name:'继续下一手'});
    await next.click();
    const enter=page.getByRole('button',{name:'进入下一幕'});
    if(await enter.count() && await enter.isVisible()) await enter.click();
  }
  const code=(await page.locator('.code').textContent()||'').trim();
  if(!/^[RG][FM][SI][HT]$/.test(code)) throw new Error(`Invalid FIN·TYPE: ${code}`);
  if(await page.locator('.result-name').count()!==1) throw new Error('Result name missing');
  if(await page.getByRole('button',{name:'复制结果卡文案'}).count()!==1) throw new Error('Share CTA missing');
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  if(overflow>2) throw new Error(`Horizontal overflow: ${overflow}px`);
  await page.screenshot({path:`artifacts/${shot}-result.png`, fullPage:true});
  await page.getByRole('button',{name:'Chaos Mode 再来一局'}).click();
  if(await page.locator('button.choice').count()!==3) throw new Error('Chaos replay failed');
  if(errors.length) throw new Error(errors.join(' | '));
  console.log(`PASS ${url} -> ${code}; 12 rounds + settlements + result + chaos replay; no overflow/errors.`);
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
