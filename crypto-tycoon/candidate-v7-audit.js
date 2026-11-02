const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  for(let i=0;i<500 && (window.__cryptoSliceReady?.version!=='candidate-v7' || !window.__ctLiveRenderer || !window.__ctLiveComposer);i++) await new Promise(r=>setTimeout(r,20));
  if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
  const renderer=window.__ctLiveRenderer;
  const composer=window.__ctLiveComposer;
  if(!renderer||!composer) throw new Error('audit: live renderer probe missing');

  // Render the accepted candidate once more and export in the same JS turn before WebGL clears
  // its presentation buffer. No second renderer/world is created.
  composer.render();
  const png=renderer.domElement.toDataURL('image/png');
  if(!png.startsWith('data:image/png;base64,') || png.length<5000) throw new Error('audit: live framebuffer export invalid');

  window.__supervisionScenePng=png;
  window.__supervisionSceneMeta={
    width:renderer.domElement.width,
    height:renderer.domElement.height,
    cssWidth:renderer.domElement.clientWidth,
    cssHeight:renderer.domElement.clientHeight,
    bytes:Math.round((png.length-22)*.75),
    version:'candidate-v7',
    referencePixelsUsed:false,
    source:'live-renderer-same-turn'
  };
  document.documentElement.dataset.auditReady='1';
}
