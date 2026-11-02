const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  for(let i=0;i<500 && (window.__cryptoSliceReady?.version!=='candidate-v7' || !window.__ctLiveRenderer || !window.__ctLiveComposer);i++) await new Promise(r=>setTimeout(r,20));
  if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
  const renderer=window.__ctLiveRenderer;
  const composer=window.__ctLiveComposer;
  if(!renderer||!composer) throw new Error('audit: live renderer probe missing');

  window.__supervisionReadPixels=()=>{
    const old=composer.renderToScreen;
    composer.renderToScreen=false;
    composer.render();
    const target=composer.readBuffer;
    const width=target.width,height=target.height;
    const pixels=new Uint8Array(width*height*4);
    renderer.readRenderTargetPixels(target,0,0,width,height,pixels);
    composer.renderToScreen=old;

    let binary='';
    const chunk=0x8000;
    for(let i=0;i<pixels.length;i+=chunk){binary+=String.fromCharCode(...pixels.subarray(i,Math.min(i+chunk,pixels.length)))}
    return {
      width,height,
      rgbaBase64:btoa(binary),
      version:'candidate-v7',
      referencePixelsUsed:false,
      source:'threejs-render-target-readpixels'
    };
  };

  window.__supervisionSceneMeta={
    width:renderer.domElement.width,
    height:renderer.domElement.height,
    cssWidth:renderer.domElement.clientWidth,
    cssHeight:renderer.domElement.clientHeight,
    version:'candidate-v7',
    referencePixelsUsed:false,
    source:'threejs-render-target-readpixels'
  };
  document.documentElement.dataset.auditReady='1';
}
