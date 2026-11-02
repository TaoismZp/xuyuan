const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:4173/crypto-tycoon/index.html?test=1';
const shot = process.env.SHOT_PREFIX || 'crypto-local';
(async()=>{
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push('console: '+m.text())});
  fs.mkdirSync('artifacts',{recursive:true});
  await page.goto(target,{waitUntil:'networkidle',timeout:30000});
  await page.screenshot({path:`artifacts/${shot}-intro.png`,fullPage:true});
  if(await page.getByRole('button',{name:'开一局'}).count()!==1) throw new Error('start button missing');
  await page.getByRole('button',{name:'开一局'}).click();
  if(await page.locator('.tile').count()!==24) throw new Error('board must have 24 tiles');
  await page.screenshot({path:`artifacts/${shot}-board.png`,fullPage:true});
  let turns=0;
  while(turns<14){
    if(await page.locator('.end').count()) break;
    const roll=page.locator('#roll');
    await roll.waitFor({state:'visible',timeout:20000});
    await page.waitForFunction(()=>{const b=document.querySelector('#roll');return !!b&&!b.disabled},null,{timeout:20000});
    await roll.click(); turns++;
    await page.waitForTimeout(60);
    for(let g=0;g<10;g++){
      if(await page.locator('.end').count()) break;
      const buy=page.locator('#buy'),pass=page.locator('#pass'),hold=page.locator('#hold'),ev=page.locator('[data-c]');
      if(await buy.count()&&await buy.isVisible()){turns%3===0&&await pass.count()?await pass.click():await buy.click();break}
      if(await hold.count()&&await hold.isVisible()){await hold.click();break}
      if(await ev.count()&&await ev.first().isVisible()){await ev.nth(turns%2).click();break}
      await page.waitForTimeout(30);
    }
  }
  await page.waitForFunction(()=>document.querySelector('.end')||(window.__chainTycoon&&window.__chainTycoon.getState().gameover),null,{timeout:30000});
  const parsed=JSON.parse(await page.evaluate(()=>window.render_game_to_text()));
  if(!parsed.gameover) throw new Error('game did not finish');
  if(parsed.players.length!==4) throw new Error('player count changed');
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  if(overflow>2) throw new Error(`horizontal overflow ${overflow}`);
  await page.screenshot({path:`artifacts/${shot}-end.png`,fullPage:true});
  if(await page.getByRole('button',{name:'再开一局'}).count()!==1) throw new Error('replay missing');
  if(errors.length) throw new Error(errors.join(' | '));
  console.log(`PASS ${target}; turns=${turns}; final=${parsed.players[0].worth}`);
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
