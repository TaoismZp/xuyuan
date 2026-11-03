const { chromium }=require('playwright');
const fs=require('fs');
fs.mkdirSync('artifacts',{recursive:true});
const base=process.env.TARGET_URL||'http://127.0.0.1:8080/crypto-tycoon/candidate-v11.html';
const expected=process.env.EXPECTED_VERSION||'candidate-v11';
function assert(v,m){if(!v)throw new Error(m)}
function rectOK(r,w,h){return r.left>=-1&&r.top>=-1&&r.right<=w+1&&r.bottom<=h+1&&r.width>0&&r.height>0}

async function productionBudget(browser){
  const context=await browser.newContext({viewport:{width:393,height:852},deviceScaleFactor:2,isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  await page.goto(base,{waitUntil:'load',timeout:60000});
  await page.waitForFunction(v=>document.documentElement.dataset.sliceReady==='1'&&window.__cryptoSliceReady?.version===v,expected,{timeout:60000});
  const audit=await page.evaluate(()=>{
    const scene=window.__ctCapturedScene;
    if(!scene)throw new Error('captured production scene missing');
    let meshes=0,lights=0,triangles=0,materials=0;const mats=new Set();
    scene.traverse(o=>{
      if(o.isLight)lights++;
      if(o.isMesh){
        meshes++;const g=o.geometry;
        if(g){const n=g.index?.count ?? g.attributes?.position?.count ?? 0;triangles+=Math.floor(n/3)}
        const arr=Array.isArray(o.material)?o.material:[o.material];arr.filter(Boolean).forEach(m=>mats.add(m.uuid));
      }
    });
    materials=mats.size;
    const canvas=document.querySelector('#game3d');
    const ratioX=canvas.width/Math.max(1,canvas.clientWidth),ratioY=canvas.height/Math.max(1,canvas.clientHeight);
    const R=e=>{const r=e.getBoundingClientRect();return{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};
    const actions=[...document.querySelectorAll('.actions button')].map(R);
    return{
      version:window.__cryptoSliceReady.version,
      viewport:{w:innerWidth,h:innerHeight,dpr:devicePixelRatio},
      canvas:{width:canvas.width,height:canvas.height,cssWidth:canvas.clientWidth,cssHeight:canvas.clientHeight,ratioX,ratioY},
      complexity:{meshes,lights,triangles,materials},
      layout:{roll:R(document.querySelector('.roll')),round:R(document.querySelector('.round-card')),leaderboard:R(document.querySelector('.leaderboard')),ticker:R(document.querySelector('.ticker')),actions},
      overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},
      referencePixelsUsed:window.__cryptoSliceReady.referencePixelsUsed
    };
  });
  assert(audit.referencePixelsUsed===false,'reference pixel substitution proof missing');
  assert(audit.overflow.body<=1&&audit.overflow.doc<=1,'iPhone production page has horizontal overflow');
  assert(audit.canvas.ratioX<=1.7&&audit.canvas.ratioY<=1.7,`mobile render DPR cap exceeded: ${audit.canvas.ratioX.toFixed(2)}x${audit.canvas.ratioY.toFixed(2)}`);
  assert(audit.complexity.meshes<=1200,`mesh budget exceeded: ${audit.complexity.meshes}`);
  assert(audit.complexity.lights<=100,`light budget exceeded: ${audit.complexity.lights}`);
  assert(audit.complexity.triangles<=1500000,`triangle budget exceeded: ${audit.complexity.triangles}`);
  const {w,h}=audit.viewport;
  assert(rectOK(audit.layout.roll,w,h),'roll control clipped on iPhone');
  assert(rectOK(audit.layout.round,w,h),'round card clipped on iPhone');
  assert(rectOK(audit.layout.leaderboard,w,h),'leaderboard clipped on iPhone');
  assert(rectOK(audit.layout.ticker,w,h),'ticker clipped on iPhone');
  assert(audit.layout.actions.length===4,'four gameplay action controls not present');
  for(const [i,r] of audit.layout.actions.entries()){
    assert(rectOK(r,w,h),`action ${i} clipped on iPhone`);
    assert(r.width>=44&&r.height>=44,`action ${i} touch target below 44px: ${r.width}x${r.height}`);
  }
  assert(audit.layout.roll.width>=88&&audit.layout.roll.height>=64,'roll touch target too small');
  assert(errors.length===0,'production browser errors: '+errors.join(' | '));
  fs.writeFileSync('artifacts/mobile-production-budget.json',JSON.stringify(audit,null,2));
  await context.close();
  return audit;
}

async function touchLoop(browser){
  const context=await browser.newContext({viewport:{width:393,height:852},deviceScaleFactor:2,isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const page=await context.newPage();
  await page.goto(base+'?test=1',{waitUntil:'load',timeout:60000});
  await page.waitForFunction(v=>document.documentElement.dataset.sliceReady==='1'&&window.__cryptoSliceReady?.version===v&&window.__cryptoFullGame?.getState()?.phase==='await-roll',expected,{timeout:60000});
  await page.evaluate(()=>{window.requestAnimationFrame=()=>0});
  await page.waitForTimeout(60);
  const roll=await page.locator('.roll').boundingBox();assert(roll,'roll bounding box missing');
  await page.touchscreen.tap(roll.x+roll.width/2,roll.y+roll.height/2);
  await page.waitForFunction(()=>document.querySelector('.stage2-decision')?.getAttribute('aria-hidden')==='false'&&window.__cryptoFullGame?.getState()?.players?.[0]?.pos===5,null,{timeout:8000,polling:50});
  const buy=await page.locator('.stage2-decision .buy').boundingBox();assert(buy,'buy bounding box missing');
  assert(buy.width>=44&&buy.height>=44,'decision primary touch target below 44px');
  await page.touchscreen.tap(buy.x+buy.width/2,buy.y+buy.height/2);
  await page.waitForFunction(()=>window.__cryptoFullGame?.getState()?.round===2&&window.__cryptoFullGame?.getState()?.phase==='await-roll',null,{timeout:12000,polling:50});
  const result=await page.evaluate(()=>({state:window.__cryptoFullGame.getState(),overflow:{body:document.body.scrollWidth-innerWidth,doc:document.documentElement.scrollWidth-innerWidth},decision:document.querySelector('.stage2-decision').getAttribute('aria-hidden')}));
  assert(result.state.owners['5']===0&&result.state.players[0].cash===108000,'touch interaction did not buy SOL through production handlers');
  assert(result.overflow.body<=1&&result.overflow.doc<=1,'touch interaction caused horizontal overflow');
  assert(result.decision==='true','decision panel did not close after touch buy');
  fs.writeFileSync('artifacts/mobile-touch-loop.json',JSON.stringify(result,null,2));
  await context.close();
}

(async()=>{
  const launch={headless:true,args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist'],channel:process.env.PW_CHANNEL||'chrome'};
  const browser=await chromium.launch(launch);
  const budget=await productionBudget(browser);
  await touchLoop(browser);
  await browser.close();
  console.log('PASS iPhone mobile/performance gate',JSON.stringify(budget.complexity),`renderRatio=${budget.canvas.ratioX.toFixed(2)}`);
})().catch(e=>{console.error(e);process.exit(1)});
