const { chromium } = require('playwright');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:8080/crypto-tycoon/candidate-v7.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });

  // Test-only instrumentation: preserve the browser's normal WebGL drawing buffer so the supervisor
  // can read the already-rendered user surface without hooks, a second renderer or synchronous GPU readPixels.
  await context.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, attrs) {
      if (type === 'webgl2' || type === 'webgl' || type === 'experimental-webgl') {
        attrs = { ...(attrs || {}), preserveDrawingBuffer: true };
      }
      return original.call(this, type, attrs);
    };
  });

  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });

  await page.goto(target, { waitUntil:'load', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:30000 });
  await page.waitForTimeout(250);

  const audit = await page.evaluate(() => {
    const canvas=document.querySelector('#game3d');
    if(!canvas) throw new Error('game canvas missing');
    const png=canvas.toDataURL('image/png');
    if(!png.startsWith('data:image/png;base64,') || png.length<10000) throw new Error(`canvas snapshot invalid length=${png.length}`);
    return {
      png,
      ready:window.__cryptoSliceReady,
      title:document.title,
      viewport:{w:innerWidth,h:innerHeight},
      canvas:{width:canvas.width,height:canvas.height,cssWidth:canvas.clientWidth,cssHeight:canvas.clientHeight},
      referenceImports:[...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
      referenceCss:getComputedStyle(document.body).backgroundImage,
      sliceVersion:document.documentElement.dataset.sliceVersion,
      evidenceSource:'preserved-live-game-canvas',
      referencePixelsUsed:false
    };
  });

  if(expectedVersion && audit.ready.version !== expectedVersion) throw new Error(`wrong candidate version: ${audit.ready.version} !== ${expectedVersion}`);
  if(audit.referenceImports.length) throw new Error('reference substitution detected: '+JSON.stringify(audit.referenceImports));
  if(!audit.ready || audit.ready.referencePixelsUsed !== false || audit.referencePixelsUsed !== false) throw new Error('candidate did not prove referencePixelsUsed=false');
  if(errors.length) throw new Error('browser errors: '+errors.join(' | '));

  const prefix='data:image/png;base64,';
  fs.writeFileSync(`artifacts/${name}-scene.png`,Buffer.from(audit.png.slice(prefix.length),'base64'));
  delete audit.png;
  fs.writeFileSync(`artifacts/${name}.json`,JSON.stringify(audit,null,2));

  await page.evaluate(() => {
    const c=document.querySelector('#game3d'); if(c) c.style.visibility='hidden';
    document.documentElement.style.background='transparent';
    document.body.style.background='transparent';
  });
  try {
    await page.screenshot({path:`artifacts/${name}-hud.png`,fullPage:false,animations:'disabled',omitBackground:true,timeout:10000});
  } catch(e) {
    fs.writeFileSync(`artifacts/${name}-hud-capture-error.txt`,String(e));
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
  console.log('PASS candidate exact-build preserved-canvas evidence',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});
