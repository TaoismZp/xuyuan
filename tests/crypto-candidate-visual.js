const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'https://taoismzp.github.io/xuyuan/crypto-tycoon/candidate-v1.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });
  await context.addInitScript(() => {
    const nativeRAF = window.requestAnimationFrame.bind(window);
    let last = 0;
    window.requestAnimationFrame = cb => nativeRAF(ts => {
      const delay = Math.max(0, 150 - (ts - last));
      setTimeout(() => { last = performance.now(); cb(last); }, delay);
    });
  });

  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });

  await page.goto(target, { waitUntil:'networkidle', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:45000 });
  await page.waitForFunction(() => document.documentElement.dataset.auditReady === '1' && !!window.__supervisionScenePng, null, { timeout:45000 });

  const audit = await page.evaluate(() => ({
    scenePng: window.__supervisionScenePng,
    sceneMeta: window.__supervisionSceneMeta,
    ready: window.__cryptoSliceReady,
    title: document.title,
    viewport: { w: innerWidth, h: innerHeight },
    referenceImports: [...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
    referenceCss: getComputedStyle(document.body).backgroundImage,
    sliceVersion: document.documentElement.dataset.sliceVersion
  }));

  if(expectedVersion && audit.ready.version !== expectedVersion) throw new Error(`wrong candidate version: ${audit.ready.version} !== ${expectedVersion}`);
  if(audit.referenceImports.length) throw new Error('reference substitution detected: '+JSON.stringify(audit.referenceImports));
  if(!audit.ready || audit.ready.referencePixelsUsed !== false || audit.sceneMeta?.referencePixelsUsed !== false) throw new Error('candidate did not prove referencePixelsUsed=false');
  if(errors.length) throw new Error('browser errors: '+errors.join(' | '));

  const prefix='data:image/png;base64,';
  if(!audit.scenePng.startsWith(prefix)) throw new Error('audit framebuffer PNG missing');
  fs.writeFileSync(`artifacts/${name}-scene.png`, Buffer.from(audit.scenePng.slice(prefix.length),'base64'));
  delete audit.scenePng;
  fs.writeFileSync(`artifacts/${name}.json`, JSON.stringify(audit,null,2));

  // HUD proof is captured separately so a software-WebGL compositing stall cannot erase scene evidence.
  await page.evaluate(() => {
    window.requestAnimationFrame = () => 0;
    const c=document.querySelector('#game3d'); if(c) c.style.visibility='hidden';
    document.documentElement.style.background='transparent';
    document.body.style.background='transparent';
  });
  try {
    await page.screenshot({path:`artifacts/${name}-hud.png`,fullPage:false,animations:'disabled',omitBackground:true,timeout:10000});
  } catch(e) {
    fs.writeFileSync(`artifacts/${name}-hud-capture-error.txt`, String(e));
  }

  await context.close();
}

(async()=>{
  const launch = { headless:true, args:['--use-angle=swiftshader','--enable-webgl','--ignore-gpu-blocklist'] };
  if (process.env.PW_CHANNEL) launch.channel = process.env.PW_CHANNEL;
  const browser=await chromium.launch(launch);
  await capture(browser,{width:1672,height:941},'candidate-desktop');
  await capture(browser,{width:1194,height:834},'candidate-ipad');
  await browser.close();
  console.log('PASS candidate exact-build framebuffer evidence',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});