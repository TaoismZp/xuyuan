const { webkit }=require('playwright');
const fs=require('fs');
fs.mkdirSync('artifacts',{recursive:true});
const target=(process.env.TARGET_URL||'http://127.0.0.1:8080/crypto-tycoon/candidate-v11.html')+'?test=1';
const expected=process.env.EXPECTED_VERSION||'candidate-v11';
function assert(v,m){if(!v)throw new Error(m)}

(async()=>{
  const browser=await webkit.launch({headless:true});
  const context=await browser.newContext({viewport:{width:393,height:852},deviceScaleFactor:2,isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.goto(target,{waitUntil:'load',timeout:90000});
  await page.waitForFunction(v=>document.documentElement.dataset.sliceReady==='1'&&window.__cryptoSliceReady?.version===v&&window.__cryptoFullGame?.getState()?.phase==='await-roll',expected,{timeout:90000});
  const initial=await page.evaluate(()=>({
    ready:window.__cryptoSliceReady,
    state:window.__cryptoFullGame.getState(),
    webgl:!!(document.querySelector('#game3d')?.getContext('webgl2')||document.querySelector('#game3d')?.getContext('webgl')),
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth}
  }));
  assert(initial.ready.fullGameplay===true&&initial.ready.referencePixelsUsed===false,'WebKit loaded wrong candidate');
  assert(initial.webgl,'WebKit WebGL context unavailable');
  assert(initial.overflow.body<=1&&initial.overflow.doc<=1,'WebKit iPhone layout overflow');

  // Freeze only the expensive accepted Stage-1 background renderer. Test-mode v11 gameplay uses timers.
  await page.evaluate(()=>{window.requestAnimationFrame=()=>0});
  await page.waitForTimeout(60);
  await page.evaluate(()=>document.querySelector('.roll')?.click());
  await page.waitForFunction(()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&window.__cryptoFullGame?.getState()?.players?.[0]?.pos===5,null,{timeout:12000,polling:50});
  await page.evaluate(()=>document.querySelector('.stage2-decision .buy')?.click());
  await page.waitForFunction(()=>window.__cryptoFullGame?.getState()?.round===2&&window.__cryptoFullGame?.getState()?.phase==='await-roll',null,{timeout:15000,polling:50});

  const after=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),
    text:JSON.parse(window.render_game_to_text()),
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},
    interactionError:window.__cryptoInteractionError||null
  }));
  assert(!after.interactionError,'WebKit interaction error: '+after.interactionError);
  assert(after.state.owners['5']===0&&after.state.players[0].cash===108000,'WebKit did not complete SOL buy loop');
  assert(after.text.fullGameplay===true&&after.text.tiles===24,'WebKit render_game_to_text mismatch');
  assert(after.overflow.body<=1&&after.overflow.doc<=1,'WebKit post-interaction overflow');
  assert(errors.length===0,'WebKit browser errors: '+errors.join(' | '));
  fs.writeFileSync('artifacts/webkit-iphone-smoke.json',JSON.stringify({target,initial,after,pass:true},null,2));
  await context.close();await browser.close();
  console.log('PASS WebKit iPhone Safari-compatibility smoke');
})().catch(e=>{console.error(e);process.exit(1)});
