import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const TEST=new URLSearchParams(location.search).get('test')==='1';
if(TEST){
  for(let i=0;i<400 && window.__cryptoSliceReady?.version!=='candidate-v7';i++) await new Promise(r=>setTimeout(r,25));
  if(window.__cryptoSliceReady?.version!=='candidate-v7') throw new Error('audit: v7 not ready');
  const scene=window.__ctCapturedScene;
  if(!scene) throw new Error('audit: captured scene missing');

  const w=innerWidth,h=innerHeight;
  const auditCanvas=document.createElement('canvas');
  auditCanvas.width=w;auditCanvas.height=h;
  const renderer=new THREE.WebGLRenderer({canvas:auditCanvas,antialias:false,preserveDrawingBuffer:true,powerPreference:'low-power'});
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.18;
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.setPixelRatio(1);
  renderer.setSize(w,h,false);

  const camera=new THREE.PerspectiveCamera(34,w/h,.1,100);
  if(w/h<1.25){camera.position.set(15.8,14.8,20.8);camera.fov=38}
  else if(w/h<1.5){camera.position.set(14.3,13.6,19.1);camera.fov=36}
  else{camera.position.set(12.8,12.6,17.2);camera.fov=34}
  camera.updateProjectionMatrix();camera.lookAt(0,.75,0);

  const composer=new EffectComposer(renderer);
  composer.setSize(w,h);
  composer.addPass(new RenderPass(scene,camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(w,h),.35,.7,.86));
  composer.render();

  const png=auditCanvas.toDataURL('image/png');
  window.__supervisionScenePng=png;
  window.__supervisionSceneMeta={width:w,height:h,bytes:Math.round((png.length-22)*.75),version:'candidate-v7',referencePixelsUsed:false};
  renderer.dispose();
  document.documentElement.dataset.auditReady='1';
}
