const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL;
const expected = process.env.EXPECTED_VERSION || 'candidate-v11';
fs.mkdirSync('artifacts', { recursive: true });
function assert(v,m){if(!v)throw new Error(m)}

async function verifySurface(browser, contextOptions, prefix, useTouch=false) {
  const context = await browser.newContext({...contextOptions,reducedMotion:'reduce'});
  const page = await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});

  await page.goto(target,{waitUntil:'load',timeout:90000});
  await page.waitForFunction(v=>document.documentElement.dataset.sliceReady==='1'&&window.__cryptoSliceReady?.version===v&&window.__cryptoSliceReady?.fullGameplay===true&&window.__cryptoFullGame?.getState()?.phase==='await-roll',expected,{timeout:90000});

  const initial=await page.evaluate(()=>({
    href:location.href,
    ready:window.__cryptoSliceReady,
    text:JSON.parse(window.render_game_to_text()),
    state:window.__cryptoFullGame.getState(),
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth}
  }));
  assert(initial.ready.version===expected,'public entry resolved wrong candidate');
  assert(initial.ready.referencePixelsUsed===false,'public entry reference pixel proof missing');
  assert(initial.text.candidate===expected&&initial.text.tiles===24&&initial.text.fullGameplay===true,'public render_game_to_text identity mismatch');
  assert(initial.state.players.length===4&&initial.state.round===1,'public initial game state mismatch');
  assert(initial.overflow.body<=1&&initial.overflow.doc<=1,'public initial horizontal overflow');

  // Stage-1 already proved continuous 3D rendering. Freeze its expensive loop only after public identity
  // is established; test-mode gameplay animations use timers, so the real production handlers still run.
  await page.evaluate(()=>{window.requestAnimationFrame=()=>0});
  await page.waitForTimeout(60);

  const roll=await page.locator('.roll').boundingBox();
  assert(roll,'public roll control missing');
  if(useTouch) await page.touchscreen.tap(roll.x+roll.width/2,roll.y+roll.height/2);
  else await page.evaluate(()=>document.querySelector('.roll')?.click());

  await page.waitForFunction(()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&window.__cryptoFullGame?.getState()?.players?.[0]?.pos===5,null,{timeout:12000,polling:50});
  const decision=await page.evaluate(()=>({title:document.querySelector('.stage2-decision h2').textContent,state:window.__cryptoFullGame.getState()}));
  assert(decision.title.includes('SOL'),'public deterministic landing did not reach SOL');

  const buy=await page.locator('.stage2-decision .buy').boundingBox();
  assert(buy,'public buy control missing');
  if(useTouch) await page.touchscreen.tap(buy.x+buy.width/2,buy.y+buy.height/2);
  else await page.evaluate(()=>document.querySelector('.stage2-decision .buy')?.click());

  await page.waitForFunction(()=>window.__cryptoFullGame?.getState()?.round===2&&window.__cryptoFullGame?.getState()?.phase==='await-roll',null,{timeout:18000,polling:50});
  const after=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),
    text:JSON.parse(window.render_game_to_text()),
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},
    decisionHidden:document.querySelector('.stage2-decision').getAttribute('aria-hidden'),
    interactionError:window.__cryptoInteractionError||null
  }));
  assert(!after.interactionError,'public interaction error: '+after.interactionError);
  assert(after.state.owners['5']===0&&after.state.players[0].cash===108000,'public SOL buy loop failed');
  assert(after.state.round===2&&after.text.candidate===expected,'public game did not advance to round 2');
  assert(after.overflow.body<=1&&after.overflow.doc<=1,'public post-interaction horizontal overflow');
  assert(after.decisionHidden==='true','public decision did not close');
  assert(errors.length===0,'public browser errors: '+errors.join(' | '));

  fs.writeFileSync(`artifacts/${prefix}-public.json`,JSON.stringify({target,initial,after,pass:true},null,2));
  await context.close();
}

(async()=>{
  if(!target)throw new Error('TARGET_URL required');
  const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  await verifySurface(browser,{viewport:{width:1672,height:941},deviceScaleFactor:1},'desktop',false);
  await verifySurface(browser,{viewport:{width:393,height:852},deviceScaleFactor:2,isMobile:true,hasTouch:true},'iphone',true);
  await browser.close();
  console.log('PASS exact-build public v11 desktop+iPhone loop',target);
})().catch(e=>{console.error(e);process.exit(1)});
