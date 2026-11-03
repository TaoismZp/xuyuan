const { chromium } = require('playwright');
const fs=require('fs');
const target=process.env.TARGET_URL||'http://127.0.0.1:8080/crypto-tycoon/candidate-v10.html?test=1';
const expectedVersion=process.env.EXPECTED_VERSION||'candidate-v10';
fs.mkdirSync('artifacts',{recursive:true});

function assert(condition,message){if(!condition)throw new Error(message)}
function mark(checkpoint,extra={}){console.log('STAGE2_CHECKPOINT',JSON.stringify({...extra,checkpoint,at:new Date().toISOString()}))}

async function capture(browser,viewport,name){
  mark('capture-start',{surface:name,viewport});
  const context=await browser.newContext({viewport,deviceScaleFactor:1,reducedMotion:'reduce'});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});

  await page.goto(target,{waitUntil:'load',timeout:60000});
  await page.waitForFunction(v=>document.documentElement.dataset.sliceReady==='1'&&window.__cryptoSliceReady?.version===v&&window.__cryptoStage2?.state?.phase==='await-roll',expectedVersion,{timeout:30000});
  mark('candidate-ready',{surface:name});

  // Stage-1 already owns continuous visual supervision. In deterministic Stage-2 acceptance,
  // stop the expensive background Three.js rAF loop after readiness so SwiftShader cannot starve
  // functional state transitions. Stage-2 test tweens intentionally use setTimeout when ?test=1,
  // so dice/human/bot animation-proof counters still execute through the production handlers.
  await page.evaluate(()=>{window.requestAnimationFrame=()=>0});
  await page.waitForTimeout(60);
  mark('background-render-loop-frozen',{surface:name});

  const before=await page.evaluate(()=>({
    ready:window.__cryptoSliceReady,
    state:window.__cryptoStage2.getState(),
    refs:[...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth}
  }));
  assert(before.ready.referencePixelsUsed===false,'reference pixel proof missing');
  assert(before.refs.length===0,'reference substitution detected: '+JSON.stringify(before.refs));
  assert(before.state.human.tile===17&&before.state.bot.tile===10,'unexpected Stage-2 initial token positions');
  assert(before.overflow.body<=1&&before.overflow.doc<=1,'initial horizontal overflow');

  // Native DOM click reaches the same production click handler without Playwright's actionability/stability wait.
  await page.evaluate(()=>document.querySelector('.roll')?.click());
  mark('roll-click-dispatched',{surface:name});
  await page.waitForFunction(()=>window.__cryptoStage2?.state?.phase==='decision'||!!window.__cryptoInteractionError,null,{timeout:5000});
  const rollError=await page.evaluate(()=>window.__cryptoInteractionError||null);
  assert(!rollError,'roll interaction error: '+rollError);
  const decision=await page.evaluate(()=>window.__cryptoStage2.getState());
  mark('decision-open',{surface:name,tile:decision.human.tile,roll:decision.lastRoll});
  assert(JSON.stringify(decision.lastRoll)==='[2,3]','deterministic test roll must be [2,3]');
  assert(decision.human.tile===22,`human token expected tile 22, got ${decision.human.tile}`);
  assert(decision.decision?.asset==='SOL'&&decision.decision?.cost===12000,'landing decision mismatch');
  assert(await page.locator('.stage2-decision').getAttribute('aria-hidden')==='false','buy/pass decision not visible');

  await page.evaluate(()=>document.querySelector('.stage2-decision .buy')?.click());
  mark('buy-click-dispatched',{surface:name});
  await page.waitForFunction(()=>window.__cryptoStage2?.state?.stage2Complete===true||!!window.__cryptoInteractionError,null,{timeout:5000});
  const decisionError=await page.evaluate(()=>window.__cryptoInteractionError||null);
  assert(!decisionError,'decision interaction error: '+decisionError);
  await page.waitForTimeout(80);
  mark('state-complete',{surface:name});

  const after=await page.evaluate(()=>({
    state:window.__cryptoStage2.getState(),
    text:JSON.parse(window.render_game_to_text()),
    humanHud:{cash:document.querySelectorAll('.player')[0].querySelector('.identity small').textContent,net:document.querySelectorAll('.player')[0].querySelector('strong').textContent},
    marketHud:document.querySelector('.round-card p').textContent,
    roundHud:document.querySelector('.round-card b').textContent,
    ticker:document.querySelector('.ticker').textContent,
    decisionHidden:document.querySelector('.stage2-decision').getAttribute('aria-hidden'),
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},
    interactionError:window.__cryptoInteractionError||null
  }));

  const s=after.state;
  assert(!after.interactionError,'interaction error: '+after.interactionError);
  assert(s.phase==='stage2-complete','Stage 2 did not finish');
  assert(s.turnsCompleted===1,'turn counter mismatch');
  assert(s.human.tile===22,'human token final tile mismatch');
  assert(s.bot.tile===14,'bot token final tile mismatch');
  assert(s.human.cash===108000,`human cash expected 108000, got ${s.human.cash}`);
  assert(s.human.holdings.length===1&&s.human.holdings[0].symbol==='SOL','SOL holding not serialized');
  assert(s.human.holdings[0].value===12960,'SOL holding did not reprice +8%');
  assert(s.human.netWorth===169360,`net worth expected 169360, got ${s.human.netWorth}`);
  assert(s.market.id==='mania'&&s.market.returnPct===25,'market did not transition bull→mania');
  assert(s.round===7,'round did not advance to 7');
  assert(s.history.some(x=>x.type==='buy')&&s.history.some(x=>x.type==='bot-turn')&&s.history.some(x=>x.type==='market-transition'),'history missing required events');
  assert(s.animationProof.diceFrames>=2&&s.animationProof.humanMoveFrames>=10&&s.animationProof.botMoveFrames>=8,'animation proof incomplete');
  assert(after.text.tiles===24&&after.text.referencePixelsUsed===false,'render_game_to_text proof mismatch');
  assert(after.humanHud.cash.includes('108,000')&&after.humanHud.net.includes('169,360'),'HUD cash/net worth out of sync');
  assert(after.marketHud.includes('狂热期')&&after.roundHud.includes('07'),'market/round HUD out of sync');
  assert(after.ticker.includes('SOL +8.0%'),'ticker out of sync');
  assert(after.decisionHidden==='true','decision UI did not close');
  assert(after.overflow.body<=1&&after.overflow.doc<=1,'post-interaction horizontal overflow');
  assert(errors.length===0,'browser errors: '+errors.join(' | '));
  mark('functional-assertions-pass',{surface:name});

  // The continuous render loop is already frozen above. Reuse the proven CDP evidence path.
  const cdp=await context.newCDPSession(page);
  const shot=await Promise.race([
    cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false}),
    new Promise((_,reject)=>setTimeout(()=>reject(new Error('CDP post-interaction screenshot timeout')),12000))
  ]);
  assert(shot?.data?.length>10000,'post-interaction screenshot invalid');
  fs.writeFileSync(`artifacts/${name}-post-interaction.png`,Buffer.from(shot.data,'base64'));
  fs.writeFileSync(`artifacts/${name}-stage2.json`,JSON.stringify({target,viewport,before,after},null,2));
  mark('evidence-written',{surface:name});

  await context.close();
}

(async()=>{
  const launch={headless:true,args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist']};
  if(process.env.PW_CHANNEL)launch.channel=process.env.PW_CHANNEL;
  const browser=await chromium.launch(launch);
  await capture(browser,{width:1672,height:941},'stage2-desktop');
  await capture(browser,{width:1194,height:834},'stage2-ipad');
  await browser.close();
  console.log('PASS Stage-2 exact-build interaction loop',target);
})().catch(e=>{console.error(e);process.exit(1)});
