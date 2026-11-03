const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  try{
    window.__supervisionAuditStage='waiting-v7-frame';
    for(let i=0;i<500 && window.__cryptoSliceReady?.version!=='candidate-v7';i++){
      await new Promise(r=>setTimeout(r,20));
    }
    if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');

    // Give the normal render loop one frame to paint all v7 additions.
    await new Promise(r=>setTimeout(r,180));
    const canvas=document.querySelector('#game3d');
    if(!canvas) throw new Error('audit: game canvas missing');
    const gl=canvas.getContext('webgl2') || canvas.getContext('webgl');
    if(!gl) throw new Error('audit: live WebGL context unavailable');

    window.__supervisionAuditStage='reading-native-framebuffer';
    const srcW=gl.drawingBufferWidth,srcH=gl.drawingBufferHeight;
    if(srcW<320||srcH<240) throw new Error(`audit: invalid drawing buffer ${srcW}x${srcH}`);
    const src=new Uint8Array(srcW*srcH*4);
    gl.readPixels(0,0,srcW,srcH,gl.RGBA,gl.UNSIGNED_BYTE,src);

    // Evidence does not need retina resolution. Downsample after readback to keep CI transfer small.
    const step=2;
    const width=Math.floor(srcW/step),height=Math.floor(srcH/step);
    const pixels=new Uint8Array(width*height*4);
    let nonBlack=0,lumaSum=0;
    for(let y=0;y<height;y++){
      for(let x=0;x<width;x++){
        const si=((y*step)*srcW+(x*step))*4;
        const di=(y*width+x)*4;
        const r=src[si],g=src[si+1],b=src[si+2],a=src[si+3];
        pixels[di]=r;pixels[di+1]=g;pixels[di+2]=b;pixels[di+3]=a;
        const l=r+g+b;lumaSum+=l;if(l>18)nonBlack++;
      }
    }
    const visibleRatio=nonBlack/(width*height);
    if(visibleRatio<.08 || lumaSum/(width*height)<12){
      throw new Error(`audit: framebuffer appears blank visibleRatio=${visibleRatio.toFixed(4)}`);
    }

    window.__supervisionAuditStage='encoding';
    let binary='';
    const chunk=0x8000;
    for(let i=0;i<pixels.length;i+=chunk){
      binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)));
    }
    const encoded=btoa(binary);

    window.__supervisionReadPixels=()=>({
      width,height,
      rgbaBase64:encoded,
      version:'candidate-v7',
      referencePixelsUsed:false,
      source:'native-live-canvas-framebuffer',
      visibleRatio,
      purpose:'Stage-1 composition/forms/density supervision only'
    });
    window.__supervisionSceneMeta={
      cssWidth:innerWidth,cssHeight:innerHeight,srcW,srcH,width,height,
      version:'candidate-v7',referencePixelsUsed:false,
      source:'native-live-canvas-framebuffer',visibleRatio
    };
    window.__supervisionAuditStage='ready';
    document.documentElement.dataset.auditReady='1';
  }catch(error){
    window.__supervisionAuditError=String(error?.stack||error);
    document.documentElement.dataset.auditReady='error';
    console.error('[supervision-audit]',window.__supervisionAuditStage,error);
  }
}
