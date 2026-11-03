const { chromium }=require('playwright');
const fs=require('fs');
fs.mkdirSync('artifacts',{recursive:true});
const target=process.env.TARGET_URL||'http://127.0.0.1:8080/crypto-tycoon/candidate-v12.html?test=1';
function assert(v,m){if(!v)throw new Error(m)}
async function poll(page,fn,timeout=20000){await page.waitForFunction(fn,null,{timeout,polling:50})}

async function runSurface(browser,viewport,name){
  const context=await browser.newContext({viewport,deviceScaleFactor:1,reducedMotion:'no-preference'});
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.goto(target,{waitUntil:'load',timeout:90000});
  await page.waitForFunction(()=>window.__cryptoSliceReady?.version==='candidate-v12'&&window.__cryptoFullGame?.getState()?.phase==='await-roll'&&window.__cryptoFeelProof?.version==='candidate-v12',null,{timeout:45000});

  const initial=await page.evaluate(()=>({
    ready:window.__cryptoSliceReady,
    state:window.__cryptoFullGame.getState(),
    feel:window.__cryptoFeel.getProof(),
    sound:{exists:!!document.querySelector('.sound-toggle'),rect:document.querySelector('.sound-toggle')?.getBoundingClientRect().toJSON?.()||null},
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth}
  }));
  assert(initial.ready.gameFeel===true,'v12 game-feel identity missing');
  assert(initial.sound.exists,'sound toggle missing');
  assert(initial.overflow.body<=1&&initial.overflow.doc<=1,'initial overflow');

  // Trusted pointer interaction: must unlock the experience layer and preserve v11 gameplay.
  await page.click('.roll');
  await poll(page,()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&window.__cryptoFullGame?.getState()?.players?.[0]?.pos===5,30000);
  await page.waitForTimeout(120);
  const atDecision=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),feel:window.__cryptoFeel.getProof(),title:document.querySelector('.stage2-decision h2').textContent,
    buyRect:document.querySelector('.stage2-decision .buy')?.getBoundingClientRect().toJSON?.()||null,
    buyVisible:getComputedStyle(document.querySelector('.stage2-decision .buy')).visibility!=='hidden'
  }));
  assert(atDecision.title.includes('SOL'),'first deterministic landing must still be SOL');
  assert(atDecision.buyVisible&&atDecision.buyRect?.width>0&&atDecision.buyRect?.height>0,'animated buy control is not visibly actionable');
  assert((atDecision.feel.cueCounts.ui||0)>=1,'input cue missing');
  assert((atDecision.feel.cueCounts.charge||0)>=1,'anticipation cue missing');
  assert((atDecision.feel.cueCounts['dice-rattle']||0)>=1,'dice-rattle cue missing');
  assert((atDecision.feel.cueCounts.event||0)>=1,'decision reveal cue missing');
  assert(atDecision.feel.landingPulses>=1,'landing feedback missing');

  // The control is intentionally animated. Once visibility/geometry are proven, do not require Playwright's
  // "stable for two frames" heuristic to suppress product motion.
  await page.locator('.stage2-decision .buy').click({force:true});
  await poll(page,()=>window.__cryptoFullGame?.getState()?.round===2&&window.__cryptoFullGame?.getState()?.phase==='await-roll',30000);
  await page.waitForTimeout(120);
  const after=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),feel:window.__cryptoFeel.getProof(),
    layer:document.querySelector('.feel-layer')?.className,
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},
    interactionError:window.__cryptoInteractionError||null
  }));
  assert(after.state.owners['5']===0&&after.state.players[0].cash===108000,'v12 broke accepted SOL purchase loop');
  assert((after.feel.cueCounts.buy||0)>=1,'purchase sound feedback missing');
  assert(after.feel.positiveBursts>=1,'positive visual feedback missing');
  assert(after.feel.stepCues>=1,'movement step feedback missing');
  assert(after.feel.interactionErrors.length===0,'feel layer errors: '+after.feel.interactionErrors.join(' | '));
  assert(!after.interactionError,'game interaction error: '+after.interactionError);
  assert(after.overflow.body<=1&&after.overflow.doc<=1,'post-turn overflow');
  assert(errors.length===0,'browser errors: '+errors.join(' | '));

  // Sound control is a product control, not a developer flag.
  await page.locator('.sound-toggle').click({force:true});
  assert((await page.evaluate(()=>window.__cryptoFeel.getProof().muted))===true,'mute control failed');
  await page.locator('.sound-toggle').click({force:true});
  assert((await page.evaluate(()=>window.__cryptoFeel.getProof().muted))===false,'unmute control failed');

  fs.writeFileSync(`artifacts/${name}-feel-v12.json`,JSON.stringify({target,viewport,initial,atDecision,after,pass:true},null,2));
  await context.close();
}

(async()=>{
  const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']});
  await runSurface(browser,{width:1194,height:834},'v12-ipad');
  await runSurface(browser,{width:393,height:852},'v12-iphone');
  await browser.close();
  console.log('PASS candidate-v12 game-feel vertical slice');
})().catch(e=>{console.error(e);process.exit(1)});