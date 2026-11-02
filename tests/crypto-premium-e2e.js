const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:4173/crypto-tycoon/premium.html?test=1';
const shot = process.env.SHOT_PREFIX || 'crypto-premium';
const width = +(process.env.VIEW_W || 1366), height = +(process.env.VIEW_H || 900);
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-webgl']});
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  page.setDefaultTimeout(30000);
  const cdp=await page.context().newCDPSession(page);
  const errors=[];
  page.on('pageerror',e=>errors.push('page: '+String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push('console: '+m.text())});
  fs.mkdirSync('artifacts',{recursive:true});
  const snap=async path=>{const {data}=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});fs.writeFileSync(path,Buffer.from(data,'base64'));};
  await page.goto(target,{waitUntil:'networkidle',timeout:60000});
  await page.waitForFunction(()=>!!window.__chainTycoon3d,{timeout:30000});
  await snap(`artifacts/${shot}-intro.png`);
  await page.getByRole('button',{name:'进入牌桌'}).click();
  await page.waitForFunction(()=>JSON.parse(window.render_game_to_text()).players?.length===4);
  let state=JSON.parse(await page.evaluate(()=>window.render_game_to_text()));
  if(state.tiles!==24) throw new Error(`expected 24 tiles, got ${state.tiles}`);
  if(state.players.length!==4) throw new Error('expected four players');
  await page.waitForTimeout(900);
  await snap(`artifacts/${shot}-board.png`);
  for(let turn=0;turn<3;turn++){
    await page.waitForFunction(()=>{const b=document.querySelector('#roll');const s=JSON.parse(window.render_game_to_text());return s.gameover||!!(b&&!b.disabled)},{timeout:20000});
    state=JSON.parse(await page.evaluate(()=>window.render_game_to_text())); if(state.gameover) break;
    await page.locator('#roll').click();
    for(let guard=0;guard<60;guard++){
      const modal=page.locator('#modal.show');
      if(await modal.count()){
        const primary=modal.locator('button.primaryBtn');
        const any=modal.locator('button');
        if(await primary.count()) await primary.first().click(); else if(await any.count()) await any.first().click();
      }
      const ready=await page.evaluate(()=>{const s=JSON.parse(window.render_game_to_text());const b=document.querySelector('#roll');return s.gameover||!!(b&&!b.disabled)});
      if(ready) break;
      await page.waitForTimeout(120);
    }
  }
  state=JSON.parse(await page.evaluate(()=>window.render_game_to_text()));
  if(state.round<2&&!state.gameover) throw new Error('gameplay did not advance');
  await snap(`artifacts/${shot}-active.png`);
  if(!state.gameover) await page.evaluate(()=>window.__chainTycoon3d.finish());
  await page.locator('#end.show').waitFor({state:'visible',timeout:5000});
  await snap(`artifacts/${shot}-end.png`);
  const overflow=await page.evaluate(()=>Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth));
  if(overflow>2) throw new Error(`horizontal overflow ${overflow}`);
  const boardShot=fs.statSync(`artifacts/${shot}-board.png`).size;
  if(boardShot<80000) throw new Error(`board screenshot suspiciously small: ${boardShot}`);
  if(errors.length) throw new Error(errors.join(' | '));
  console.log(`PASS ${target}; ${width}x${height}; three human rounds; board/end; screenshot=${boardShot} bytes; no browser errors.`);
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
