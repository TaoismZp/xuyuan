const { chromium } = require('playwright');
const { PNG } = require('pngjs');
const fs = require('fs');
const target = process.env.TARGET_URL || 'http://127.0.0.1:8080/crypto-tycoon/candidate-v7.html?test=1';
const expectedVersion = process.env.EXPECTED_VERSION || null;
fs.mkdirSync('artifacts', { recursive: true });

function writeRgbaPng(path,width,height,rgba){
  const src=Buffer.from(rgba,'base64');
  if(src.length!==width*height*4) throw new Error(`RGBA size mismatch ${src.length} !== ${width*height*4}`);
  const png=new PNG({width,height});
  const row=width*4;
  for(let y=0;y<height;y++) src.copy(png.data,y*row,(height-1-y)*row,(height-y)*row);
  fs.writeFileSync(path,PNG.sync.write(png));
}

async function capture(browser, viewport, name) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion:'reduce' });
  const page = await context.newPage();
  const errors=[];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if(m.type()==='error') errors.push(m.text()); });

  await page.goto(target, { waitUntil:'load', timeout:60000 });
  await page.waitForFunction(v => document.documentElement.dataset.sliceReady === '1' && !!window.__cryptoSliceReady && (!v || window.__cryptoSliceReady.version === v), expectedVersion, { timeout:30000 });

  // Monitor the final user-visible WebGL surface directly. No in-product audit module, renderer hook,
  // second Three.js world or screenshot compositor is required. We register after the normal game loop,
  // so the next rAF paints the candidate first and then this callback reads the live framebuffer.
  const audit = await page.evaluate(() => new Promise((resolve,reject) => {
    requestAnimationFrame(() => {
      try {
        const canvas=document.querySelector('#game3d');
        if(!canvas) throw new Error('game canvas missing');
        const gl=canvas.getContext('webgl2') || canvas.getContext('webgl');
        if(!gl) throw new Error('live WebGL context unavailable');
        const srcW=gl.drawingBufferWidth,srcH=gl.drawingBufferHeight;
        if(srcW<320||srcH<240) throw new Error(`invalid drawing buffer ${srcW}x${srcH}`);
        const src=new Uint8Array(srcW*srcH*4);
        gl.readPixels(0,0,srcW,srcH,gl.RGBA,gl.UNSIGNED_BYTE,src);

        const step=2,width=Math.floor(srcW/step),height=Math.floor(srcH/step);
        const pixels=new Uint8Array(width*height*4);
        let nonBlack=0,lumaSum=0;
        for(let y=0;y<height;y++) for(let x=0;x<width;x++){
          const si=((y*step)*srcW+(x*step))*4,di=(y*width+x)*4;
          const r=src[si],g=src[si+1],b=src[si+2],a=src[si+3];
          pixels[di]=r;pixels[di+1]=g;pixels[di+2]=b;pixels[di+3]=a;
          const l=r+g+b;lumaSum+=l;if(l>18)nonBlack++;
        }
        const visibleRatio=nonBlack/(width*height);
        const avgLuma=lumaSum/(width*height);
        if(visibleRatio<.08 || avgLuma<12) throw new Error(`framebuffer appears blank visibleRatio=${visibleRatio.toFixed(4)} avgLuma=${avgLuma.toFixed(2)}`);

        let binary='';const chunk=0x8000;
        for(let i=0;i<pixels.length;i+=chunk) binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)));
        resolve({
          pixels:{width,height,rgbaBase64:btoa(binary),version:window.__cryptoSliceReady.version,referencePixelsUsed:false,source:'direct-live-canvas-framebuffer',visibleRatio,avgLuma},
          ready:window.__cryptoSliceReady,
          title:document.title,
          viewport:{w:innerWidth,h:innerHeight},
          referenceImports:[...document.scripts].map(s=>s.src).filter(src=>/keyart|visual-v3/i.test(src)),
          referenceCss:getComputedStyle(document.body).backgroundImage,
          sliceVersion:document.documentElement.dataset.sliceVersion
        });
      }catch(e){ reject(String(e?.stack||e)); }
    });
  }));

  if(expectedVersion && audit.ready.version !== expectedVersion) throw new Error(`wrong candidate version: ${audit.ready.version} !== ${expectedVersion}`);
  if(audit.referenceImports.length) throw new Error('reference substitution detected: '+JSON.stringify(audit.referenceImports));
  if(!audit.ready || audit.ready.referencePixelsUsed !== false || audit.pixels?.referencePixelsUsed !== false) throw new Error('candidate did not prove referencePixelsUsed=false');
  if(errors.length) throw new Error('browser errors: '+errors.join(' | '));

  writeRgbaPng(`artifacts/${name}-scene.png`,audit.pixels.width,audit.pixels.height,audit.pixels.rgbaBase64);
  delete audit.pixels.rgbaBase64;
  fs.writeFileSync(`artifacts/${name}.json`, JSON.stringify(audit,null,2));

  await page.evaluate(() => {
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
  console.log('PASS candidate exact-build direct framebuffer evidence',target,expectedVersion||'any-version');
})().catch(e=>{console.error(e);process.exit(1)});
