const { chromium }=require('playwright');
const fs=require('fs');
const target=process.env.TARGET_URL||'http://127.0.0.1:8080/crypto-tycoon/candidate-v11.html?test=1';
const expectedVersion=process.env.EXPECTED_VERSION||'candidate-v11';
fs.mkdirSync('artifacts',{recursive:true});

function assert(v,m){if(!v)throw new Error(m)}
function mark(checkpoint,extra={}){console.log('STAGE3_CHECKPOINT',JSON.stringify({...extra,checkpoint,at:new Date().toISOString()}))}
async function poll(page,fn,timeout=8000){await page.waitForFunction(fn,null,{timeout,polling:50})}

async function runSurface(browser,viewport,name){
  mark('capture-start',{surface:name,viewport});
  const context=await browser.newContext({viewport,deviceScaleFactor:1,reducedMotion:'reduce'});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});

  await page.goto(target,{waitUntil:'load',timeout:60000});
  await page.waitForFunction(v=>document.documentElement.dataset.sliceReady==='1'&&window.__cryptoSliceReady?.version===v&&window.__cryptoFullGame?.getState()?.phase==='await-roll',expectedVersion,{timeout:30000});
  mark('candidate-ready',{surface:name});

  // Stage-1 already supervises the animated 3D renderer. Freeze its continuous rAF loop only in
  // deterministic Stage-3 acceptance; v11 test-mode gameplay tweens use setTimeout and remain real.
  await page.evaluate(()=>{window.requestAnimationFrame=()=>0});
  await page.waitForTimeout(60);

  const initial=await page.evaluate(()=>({state:window.__cryptoFullGame.getState(),ready:window.__cryptoSliceReady,overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth}}));
  assert(initial.ready.referencePixelsUsed===false&&initial.ready.fullGameplay===true,'full-game identity proof missing');
  assert(initial.state.round===1&&initial.state.phase==='await-roll','unexpected initial round/phase');
  assert(initial.state.players.every(p=>p.pos===0),'all four players must start on tile 0');
  assert(Object.keys(initial.state.owners).length===0,'fresh game must start with no owners');
  assert(initial.overflow.body<=1&&initial.overflow.doc<=1,'initial horizontal overflow');

  // Round 1: deterministic [2,3] -> tile 5 SOL.
  await page.evaluate(()=>document.querySelector('.roll')?.click());
  await poll(page,()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&window.__cryptoFullGame?.getState()?.players?.[0]?.pos===5);
  const firstDecision=await page.evaluate(()=>({state:window.__cryptoFullGame.getState(),title:document.querySelector('.stage2-decision h2').textContent,primary:document.querySelector('.stage2-decision .buy').textContent}));
  mark('round1-decision',{surface:name,title:firstDecision.title,pos:firstDecision.state.players[0].pos});
  assert(firstDecision.title.includes('SOL'),'round 1 must land on SOL');
  assert(firstDecision.primary.includes('买入'),'SOL decision must offer buy');
  await page.evaluate(()=>document.querySelector('.stage2-decision .buy')?.click());
  await poll(page,()=>window.__cryptoFullGame?.getState()?.round===2&&window.__cryptoFullGame?.getState()?.phase==='await-roll',12000);
  const after1=await page.evaluate(()=>window.__cryptoFullGame.getState());
  assert(after1.owners['5']===0,'SOL ownership did not persist through bot turns');
  assert(after1.players[0].pos===5,'human position after round 1 mismatch');
  assert(after1.players[0].cash===108000,`human cash after SOL expected 108000, got ${after1.players[0].cash}`);
  assert(after1.history.filter(x=>x.type==='roll').length>=4,'full four-player round did not execute');
  mark('round1-complete',{surface:name,round:after1.round,regime:after1.regime});

  // Round 2: deterministic queue returns [1,1] for human after the three bot rolls -> tile 7 MEME.
  await page.evaluate(()=>document.querySelector('.roll')?.click());
  await poll(page,()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&window.__cryptoFullGame?.getState()?.players?.[0]?.pos===7);
  const secondDecision=await page.evaluate(()=>({state:window.__cryptoFullGame.getState(),title:document.querySelector('.stage2-decision h2').textContent}));
  assert(secondDecision.title.includes('Meme'),'round 2 must land on Meme asset');
  await page.evaluate(()=>document.querySelector('.stage2-decision .buy')?.click());
  await poll(page,()=>window.__cryptoFullGame?.getState()?.round===3&&window.__cryptoFullGame?.getState()?.phase==='await-roll',12000);

  const after2=await page.evaluate(()=>({
    state:window.__cryptoFullGame.getState(),
    text:JSON.parse(window.render_game_to_text()),
    proof:window.__cryptoFullGame.getProof(),
    hud:{cash:document.querySelector('[data-player="0"] .identity small').textContent,net:document.querySelector('[data-player="0"] strong').textContent,round:document.querySelector('.round-card b').textContent,market:document.querySelector('.round-card p').textContent},
    overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},
    interactionError:window.__cryptoInteractionError||null
  }));
  const s=after2.state;
  assert(!after2.interactionError,'interaction error: '+after2.interactionError);
  assert(s.round===3&&s.phase==='await-roll','game did not remain repeatable after two full rounds');
  assert(s.owners['5']===0&&s.owners['7']===0,'human assets did not persist across rounds');
  assert(s.players[0].cash===101000,`human cash after two buys expected 101000, got ${s.players[0].cash}`);
  assert(s.players[0].pos===7,'human final tile after round 2 mismatch');
  assert(s.turnsCompleted>=8,'two complete four-player rounds were not recorded');
  assert(s.history.filter(x=>x.type==='roll'&&x.pid===0).length===2,'human roll history must contain two rounds');
  assert([1,2,3].every(pid=>s.history.some(x=>x.type==='roll'&&x.pid===pid)),'bot turns missing from history');
  assert(after2.text.tiles===24&&after2.text.fullGameplay===true&&after2.text.referencePixelsUsed===false,'render_game_to_text full-game proof mismatch');
  assert(after2.proof.diceFrames>=16&&after2.proof.humanMoveFrames>=14&&after2.proof.botMoveFrames>=20,'animation proof too small for repeated turns');
  assert(after2.hud.cash.includes('101,000')&&after2.hud.round.includes('03'),'HUD did not synchronize after repeated rounds');
  assert(after2.overflow.body<=1&&after2.overflow.doc<=1,'post-round horizontal overflow');
  assert(errors.length===0,'browser errors: '+errors.join(' | '));
  mark('two-round-loop-pass',{surface:name,round:s.round,cash:s.players[0].cash,owners:s.owners});

  // Portfolio must read from the same live ownership state.
  await page.evaluate(()=>document.querySelector('[data-action="portfolio"]')?.click());
  await poll(page,()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false');
  const portfolio=await page.evaluate(()=>({title:document.querySelector('.stage2-decision h2').textContent,body:document.querySelector('.stage2-decision p').textContent}));
  assert(portfolio.body.includes('SOL')&&portfolio.body.includes('Meme'),'portfolio UI is not backed by live holdings');
  await page.evaluate(()=>document.querySelector('.stage2-decision .buy')?.click());
  await poll(page,()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='true');
  mark('portfolio-pass',{surface:name});

  // Restart must produce a genuinely fresh playable state.
  await page.evaluate(()=>document.querySelector('[data-action="restart"]')?.click());
  await poll(page,()=>window.__cryptoFullGame?.getState()?.round===1&&Object.keys(window.__cryptoFullGame.getState().owners).length===0);
  const restarted=await page.evaluate(()=>window.__cryptoFullGame.getState());
  assert(restarted.players.every(p=>p.pos===0),'restart did not reset positions');
  assert(restarted.players[0].cash===120000,'restart did not reset cash');
  mark('restart-pass',{surface:name});

  // Exercise the production end-state renderer and replay affordance without simulating twelve redundant rounds.
  await page.evaluate(()=>window.__cryptoFullGame.finish());
  await poll(page,()=>document.querySelector('.end-panel')?.getAttribute('aria-hidden')==='false');
  const endState=await page.evaluate(()=>({state:window.__cryptoFullGame.getState(),rows:document.querySelectorAll('.rank-item').length,title:document.querySelector('.end-card h2').textContent}));
  assert(endState.state.gameover===true&&endState.rows===4,'end-state ranking did not render four players');
  await page.evaluate(()=>document.querySelector('.end-panel .again')?.click());
  await poll(page,()=>window.__cryptoFullGame?.getState()?.gameover===false&&window.__cryptoFullGame.getState().round===1);
  mark('end-replay-pass',{surface:name});

  const finalState=await page.evaluate(()=>({state:window.__cryptoFullGame.getState(),text:JSON.parse(window.render_game_to_text()),overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth}}));
  fs.writeFileSync(`artifacts/${name}-stage3.json`,JSON.stringify({target,viewport,initial,after1,after2,portfolio,restarted,endState,finalState,functionalPass:true},null,2));
  mark('evidence-written',{surface:name});
  await context.close();
}

(async()=>{
  const launch={headless:true,args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist']};
  if(process.env.PW_CHANNEL)launch.channel=process.env.PW_CHANNEL;
  const browser=await chromium.launch(launch);
  await runSurface(browser,{width:1672,height:941},'stage3-desktop');
  await runSurface(browser,{width:1194,height:834},'stage3-ipad');
  await browser.close();
  console.log('PASS Stage-3 full gameplay integration',target);
})().catch(e=>{console.error(e);process.exit(1)});
