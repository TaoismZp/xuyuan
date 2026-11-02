import * as THREE from 'three';

await import('./candidate-v3-augment.js');
const scene=window.__ctCapturedScene, root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v4 scene missing');

// Supervisor-only correction: preserve v3 geometry, remove the lighting regression.
for(const l of scene.children){
  if(l.isAmbientLight && Math.abs(l.intensity-.72)<.05) l.intensity=.16;
  if(l.isDirectionalLight && Math.abs(l.intensity-2.45)<.08 && Math.abs(l.position.x-6)<.5) l.intensity=.55;
  if(l.isPointLight && l.position.distanceTo(new THREE.Vector3(0,5.2,6.2))<.5) l.intensity=4.2;
  if(l.isPointLight && l.position.distanceTo(new THREE.Vector3(0,4,-3.2))<.5) l.intensity=3.2;
}
if(scene.fog && 'density' in scene.fog) scene.fog.density=.019;
scene.background=new THREE.Color(0x061024);

// Story panels are information surfaces. Keep their authored color independent of scene-light peaks.
const tileGroups=root.children.filter(o=>o.isGroup && Math.abs(o.position.y-.68)<.04 && (Math.abs(Math.abs(o.position.x)-5.4)<.2 || Math.abs(Math.abs(o.position.z)-5.4)<.2));
let stabilized=0;
for(const g of tileGroups){
  for(const m of g.children){
    const p=m.geometry?.parameters;
    if(!m.isMesh || !p) continue;
    if(Math.abs((p.width||0)-1.32)<.03 && Math.abs((p.height||0)-1.12)<.03 && m.material?.map){
      m.material=new THREE.MeshBasicMaterial({map:m.material.map,color:0xf0f0f0,side:THREE.DoubleSide,toneMapped:false});
      m.renderOrder=8;stabilized++;
    }
  }
}

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v4',referencePixelsUsed:false,lightingRegressionFixed:true,storyPanelsStabilized:stabilized};
document.documentElement.dataset.sliceVersion='v4';
document.documentElement.dataset.sliceReady='1';
