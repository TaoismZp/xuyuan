const { chromium }=require('playwright');
const fs=require('fs');
fs.mkdirSync('artifacts',{recursive:true});
const target=process.env.TARGET_URL||'http://127.0.0.1:8080/crypto-tycoon/candidate-v13.html?test=1';
function assert(v,m){if(!v)throw new Error(m)}
async function poll(page,fn,timeout=30000){await page.waitForFunction(fn,null,{timeout,polling:50})}

async function runSurface(browser,viewport,name){
  const context=await browser.newContext({viewport,deviceScaleFactor:1,reducedMotion:'no-preference'});
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.goto(target,{waitUntil:'load',timeout:90000});
  await page.waitForFunction(()=>window.__cryptoSliceReady?.version==='candidate-v13'&&window.__cryptoFullGame?.getState()?.phase==='await-roll'&&window.__cryptoV13Proof?.version==='candidate-v13',null,{timeout:60000});
  const initial=await page.evaluate(()=>({
    ready:window.__cryptoSliceReady,state:window.__cryptoFullGame.getState(),proof:window.__cryptoV13.getProof(),
    soundRect:document.querySelector('.v13-sound')?.getBoundingClientRect().toJSON?.()||null,
    overflow:Math.max(document.body.scrollWidth-innerWidth,document.documentElement.scrollWidth-innerWidth)
  }));
  assert(initial.ready.heroInteraction&&initial.ready.authoredAudio,'v13 identity missing');
  assert(initial.soundRect?.width>=44&&initial.soundRect?.height>=44,'sound control too small');
  assert(initial.overflow<=1,'initial horizontal overflow');

  await page.click('.roll');
  await poll(page,()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&document.body.classList.contains('v13-hero-beat')===false&&window.__cryptoV13Proof?.landingCount===1,45000);
  const atDecision=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),proof:window.__cryptoV13.getProof(),title:document.querySelector('.stage2-decision h2').textContent,
    heroVisible:getComputedStyle(document.querySelector('.hero-dice-stage')).opacity,
    overflow:Math.max(document.body.scrollWidth-innerWidth,document.documentElement.scrollWidth-innerWidth)
  }));
  assert(atDecision.title.includes('SOL'),'first landing not SOL');
  assert(JSON.stringify(atDecision.state.lastRoll)==='[2,3]','deterministic roll changed');
  assert(atDecision.state.players[0].pos===5,'human destination changed');
  assert(atDecision.proof.rollCount===1,'roll choreography count wrong');
  assert(atDecision.proof.stepSequenceCount===5,`expected exactly 5 semantic steps, got ${atDecision.proof.stepSequenceCount}`);
  assert(atDecision.proof.landingCount===1,`expected exactly 1 landing, got ${atDecision.proof.landingCount}`);
  assert(atDecision.proof.diceImpactCount===3,`expected 3 dice impacts, got ${atDecision.proof.diceImpactCount}`);
  assert(atDecision.proof.authoredAssetsFetched.length===5,'not all authored WAVs fetched');
  assert(atDecision.proof.authoredAssetsLoaded.length===5,`not all authored WAVs decoded: ${JSON.stringify(atDecision.proof)}`);
  assert(atDecision.proof.authoredAssetsFailed.length===0,'authored asset failure');
  assert(atDecision.proof.mixDuckEvents>=2,'mix duck choreography missing');
  assert(atDecision.proof.hapticAttempts>=3,'haptic punctuation attempts missing');
  const types=atDecision.proof.rollSequenceEvents.map(x=>x.type);
  for(const required of ['input','result-known','dice-start','dice-impact','dice-settle','step','landing','decision-reveal'])assert(types.includes(required),`sequence event missing: ${required}`);
  assert(atDecision.overflow<=1,'decision overflow');

  await page.locator('.stage2-decision .buy').click({force:true});
  await poll(page,()=>window.__cryptoV13Proof?.humanPurchaseCelebrations===1&&window.__cryptoFullGame?.getState()?.owners?.['5']===0,15000);
  await poll(page,()=>window.__cryptoFullGame?.getState()?.round===2&&window.__cryptoFullGame?.getState()?.phase==='await-roll',30000);
  await page.waitForTimeout(100);
  const after=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),proof:window.__cryptoV13.getProof(),
    overflow:Math.max(document.body.scrollWidth-innerWidth,document.documentElement.scrollWidth-innerWidth),
    interactionError:window.__cryptoInteractionError||null
  }));
  assert(after.state.players[0].cash===108000,'SOL cash result changed');
  assert(after.state.owners['5']===0,'SOL ownership result changed');
  assert(after.proof.humanPurchaseCelebrations===1,'human hero purchase must happen once');
  assert(after.proof.botPurchaseCelebrations===0,'bot purchase must not steal hero celebration');
  assert(after.proof.interactionErrors.length===0,'v13 errors: '+after.proof.interactionErrors.join(' | '));
  assert(!after.interactionError,'baseline interaction error: '+after.interactionError);
  assert(after.overflow<=1,'post-turn overflow');
  assert(errors.length===0,'browser errors: '+errors.join(' | '));

  await page.locator('.v13-sound').click({force:true});
  assert((await page.evaluate(()=>window.__cryptoV13.getProof().muted))===true,'mute failed');
  await page.locator('.v13-sound').click({force:true});
  assert((await page.evaluate(()=>window.__cryptoV13.getProof().muted))===false,'unmute failed');

  fs.writeFileSync(`artifacts/${name}-v13.json`,JSON.stringify({target,viewport,initial,atDecision,after,pass:true},null,2));
  await context.close();
}

(async()=>{
  const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']});
  await runSurface(browser,{width:1194,height:834},'v13-ipad');
  await runSurface(browser,{width:393,height:852},'v13-iphone');
  await browser.close();
  console.log('PASS candidate-v13 strict hero interaction slice');
})().catch(e=>{console.error(e);process.exit(1)});