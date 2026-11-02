const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:4173/crypto-tycoon-3d/index.html?test=1';
const shot = process.env.SHOT_PREFIX || 'crypto3d-local';

(async()=>{
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{ if(m.type()==='error') errors.push('console: '+m.text()); });
  fs.mkdirSync('artifacts',{recursive:true});

  await page.goto(target,{waitUntil:'networkidle',timeout:30000});
  await page.screenshot({path:`artifacts/${shot}-intro.png`,fullPage:true});
  if(await page.getByRole('button',{name:'开始一局'}).count()!==1) throw new Error('start button missing');
  await page.getByRole('button',{name:'开始一局'}).click();
  if(await page.locator('.tile').count()!==24) throw new Error('board must have 24 tiles');
  if(await page.locator('.player-row').count()!==4) throw new Error('player HUD must have 4 players');
  if(await page.locator('.scene.tilt').count()!==1) throw new Error('3D tilted board missing');
  await page.screenshot({path:`artifacts/${shot}-board.png`,fullPage:true});

  let humanTurns=0, purchases=0;
  for(let guard=0;guard<18;guard++){
    if(await page.locator('.end').count()) break;
    await page.waitForFunction(()=>{
      const end=document.querySelector('.end');
      const roll=document.querySelector('#rollBtn');
      return !!end || (!!roll && !roll.disabled);
    },null,{timeout:12000});
    if(await page.locator('.end').count()) break;

    await page.locator('#rollBtn').click();
    humanTurns++;

    for(let modalGuard=0;modalGuard<80;modalGuard++){
      if(await page.locator('.end').count()) break;
      const overlay=page.locator('.overlay');
      if(await overlay.count() && await overlay.isVisible()){
        const buy=page.locator('[data-buy]');
        const skip=page.locator('[data-skip]');
        const up=page.locator('[data-up]');
        if(await buy.count() && await buy.isVisible()){
          if(purchases<2){ await buy.click(); purchases++; }
          else if(await skip.count()) await skip.click();
          break;
        }
        if(await up.count() && await up.isVisible()){
          if(humanTurns%3===0) await up.click();
          else if(await skip.count()) await skip.click();
          break;
        }
      }
      const roll=page.locator('#rollBtn');
      if(await roll.count() && await roll.isEnabled()) break;
      await page.waitForTimeout(30);
    }
  }

  const live=JSON.parse(await page.evaluate(()=>window.render_game_to_text()));
  if(live.players.length!==4) throw new Error('player count changed');
  if(humanTurns<2 && !live.gameover) throw new Error('representative gameplay did not advance');
  if(purchases<1 && !live.gameover) throw new Error('asset purchase path was not exercised');

  if(!live.gameover){
    for(let guard=0;guard<16 && !(await page.locator('.end').count());guard++){
      await page.waitForFunction(()=>{
        const end=document.querySelector('.end');
        const roll=document.querySelector('#rollBtn');
        return !!end || (!!roll && !roll.disabled);
      },null,{timeout:12000});
      if(await page.locator('.end').count()) break;
      await page.locator('#rollBtn').click();
      for(let m=0;m<80;m++){
        if(await page.locator('.end').count()) break;
        const buy=page.locator('[data-buy]'), skip=page.locator('[data-skip]'), up=page.locator('[data-up]');
        if(await buy.count() && await buy.isVisible()){ if(await skip.count()) await skip.click(); break; }
        if(await up.count() && await up.isVisible()){ if(await skip.count()) await skip.click(); break; }
        const roll=page.locator('#rollBtn');
        if(await roll.count() && await roll.isEnabled()) break;
        await page.waitForTimeout(30);
      }
    }
  }

  await page.locator('.end').waitFor({state:'visible',timeout:12000});
  const parsed=JSON.parse(await page.evaluate(()=>window.render_game_to_text()));
  if(!parsed.gameover) throw new Error('end state did not render');
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  if(overflow>3) throw new Error(`horizontal overflow ${overflow}`);
  await page.screenshot({path:`artifacts/${shot}-end.png`,fullPage:true});
  if(await page.getByRole('button',{name:'再开一局'}).count()!==1) throw new Error('replay missing');
  await page.getByRole('button',{name:'再开一局'}).click();
  if(await page.locator('.tile').count()!==24) throw new Error('replay did not reset board');
  if(errors.length) throw new Error(errors.join(' | '));

  console.log(`PASS ${target}; humanTurns=${humanTurns}; purchases=${purchases}; board/end/replay verified; no overflow/errors.`);
  await browser.close();
})().catch(e=>{ console.error(e); process.exit(1); });
