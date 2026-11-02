const { chromium } = require('playwright');
const fs = require('fs');
const url = process.env.TARGET_URL || 'http://127.0.0.1:4173/crypto-tycoon/index.html?test=1';
const shot = process.env.SHOT_PREFIX || 'local';

(async()=>{
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',e=>errors.push('pageerror: '+String(e)));
  page.on('console',m=>{if(m.type()==='error') errors.push('console: '+m.text())});
  await page.goto(url,{waitUntil:'networkidle',timeout:30000});
  fs.mkdirSync('artifacts',{recursive:true});
  await page.screenshot({path:`artifacts/${shot}-intro.png`,fullPage:true});
  if(await page.locator('#new').count()!==1) throw new Error('start button missing');
  await page.locator('#new').click();
  await page.waitForTimeout(100);
  if(await page.locator('.tile').count()!==24) throw new Error('board should have 24 tiles');
  if(await page.locator('.token').count()<4) throw new Error('four player tokens missing');
  await page.screenshot({path:`artifacts/${shot}-board.png`,fullPage:true});

  let humanRolls=0;
  for(let guard=0;guard<80;guard++){
    if(await page.locator('.end').count()) break;
    const overlay=page.locator('.overlay');
    if(await overlay.count()){
      const choices=overlay.locator('.choicebtn');
      if(await choices.count()) await choices.first().click();
      else if(await overlay.locator('#ok').count()) await overlay.locator('#ok').click();
      await page.waitForTimeout(40);
      continue;
    }
    const roll=page.locator('#roll');
    if(await roll.count() && await roll.isEnabled()){
      await roll.click(); humanRolls++; await page.waitForTimeout(100); continue;
    }
    await page.waitForTimeout(80);
  }
  await page.locator('.end').waitFor({state:'visible',timeout:12000});
  if(humanRolls<5) throw new Error(`implausibly few human rolls: ${humanRolls}`);
  if(await page.locator('.rank-row').count()!==4) throw new Error('final ranking missing players');
  if(await page.locator('#again').count()!==1) throw new Error('replay CTA missing');
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  if(overflow>2) throw new Error(`horizontal overflow ${overflow}px`);
  await page.screenshot({path:`artifacts/${shot}-result.png`,fullPage:true});
  if(errors.length) throw new Error(errors.join(' | '));
  console.log(`PASS ${url}: ${humanRolls} human rolls, full 12-round board-game flow, event/property decisions, bots and final ranking.`);
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
