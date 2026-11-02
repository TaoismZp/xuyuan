const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  for(let i=0;i<500 && (window.__cryptoSliceReady?.version!=='candidate-v7' || !window.__ctLiveRenderer || !window.__ctLiveComposer || !window.__ctLiveCamera);i++) await new Promise(r=>setTimeout(r,20));
  if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
  const renderer=window.__ctLiveRenderer;
  const composer=window.__ctLiveComposer;
  const camera=window.__ctLiveCamera;
  if(!renderer||!composer||!camera) throw new Error('audit: live renderer probe missing');

  window.__supervisionReadPixels=()=>{
    const cssW=innerWidth,cssH=innerHeight;
    const width=Math.max(320,Math.round(cssW*.5));
    const height=Math.max(240,Math.round(cssH*.5));
    const oldAspect=camera.aspect,oldFov=camera.fov;
    const oldRenderToScreen=composer.renderToScreen;

    renderer.setPixelRatio(1);
    renderer.setSize(width,height,false);
    composer.setSize(width,height);
    camera.aspect=width/height;
    if(width/height<1.25) camera.fov=38; else if(width/height<1.5) camera.fov=36; else camera.fov=34;
    camera.updateProjectionMatrix();

    composer.renderToScreen=false;
    composer.render();
    const target=composer.readBuffer;
    const pixels=new Uint8Array(target.width*target.height*4);
    renderer.readRenderTargetPixels(target,0,0,target.width,target.height,pixels);

    composer.renderToScreen=oldRenderToScreen;
    renderer.setSize(cssW,cssH,false);
    composer.setSize(cssW,cssH);
    camera.aspect=oldAspect;camera.fov=oldFov;camera.updateProjectionMatrix();

    let binary='';
    const chunk=0x8000;
    for(let i=0;i<pixels.length;i+=chunk) binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)));
    return {
      width:target.width,height:target.height,
      rgbaBase64:btoa(binary),
      version:'candidate-v7',referencePixelsUsed:false,
      source:'live-composer-half-res-readpixels',
      purpose:'stage-1 composition/forms/density supervision; final acceptance still requires real delivery surface'
    };
  };

  window.__supervisionSceneMeta={cssWidth:innerWidth,cssHeight:innerHeight,scale:.5,version:'candidate-v7',referencePixelsUsed:false,source:'live-composer-half-res-readpixels'};
  document.documentElement.dataset.auditReady='1';
}
