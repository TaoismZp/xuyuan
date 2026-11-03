import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

await import('./candidate-v8-augment.js');
const scene=window.__ctCapturedScene,root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v9 scene missing');

// Find the original central stage created by candidate-v1.
const stage=root.children.find(o=>o.isGroup && Math.abs(o.position.x)<.05 && Math.abs(o.position.z)<.05 && Math.abs(o.position.y-.86)<.12 && o.children.length>=5);
let legacyStageSignHidden=false,globeReduced=false;
if(stage){
  // Exact nested legacy sign: local y≈3.55,z≈0.45. This was the v8 duplicate plaque.
  for(const child of stage.children){
    if(child.isGroup && Math.abs(child.position.y-3.55)<.35 && Math.abs(child.position.z-.45)<.5){
      child.visible=false;legacyStageSignHidden=true;
    }
  }
  // Original globe group: local y≈1.92. Keep it as market ambience, not a competing hero.
  const globeGroup=stage.children.find(child=>child.isGroup && Math.abs(child.position.y-1.92)<.35 && child.children.length>=4);
  if(globeGroup){
    globeGroup.scale.setScalar(.72);
    globeGroup.position.y=1.56;
    globeGroup.position.z=-.38;
    globeReduced=true;
  }
}

// Reduce the original high-energy lighting rig enough to recover toy materials and facial/visor contrast.
let keyLightsReduced=0,hotPointsReduced=0;
scene.traverse(o=>{
  if(o.isDirectionalLight && o.intensity>2.2){o.intensity*=.74;keyLightsReduced++}
  if(o.isPointLight && o.intensity>8){o.intensity*=.68;hotPointsReduced++}
  if(o.isSpotLight && o.intensity>30){o.intensity*=.78}
});
scene.add(new THREE.HemisphereLight(0xcde5ff,0x24182c,.12));

// Improve the two weakest collectible reads with broad face/material shapes rather than more micro-detail.
function perimeterPositions(){const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];xs.forEach(x=>a.push([x,-5.4]));zs.forEach(z=>a.push([5.4,z]));[...xs].reverse().forEach(x=>a.push([x,5.4]));[...zs].reverse().forEach(z=>a.push([-5.4,z]));return a}
const positions=perimeterPositions();
function findToken(idx){const [x,z]=positions[idx];let best=null,dist=1e9;for(const o of root.children){if(!o.isGroup||o.position.y<.7||o.position.y>1.25)continue;const d=(o.position.x-x)**2+(o.position.z-z)**2;if(d<dist){dist=d;best=o}}return dist<.4?best:null}
const darkVisor=new THREE.MeshPhysicalMaterial({color:0x071326,metalness:.18,roughness:.08,clearcoat:1,emissive:0x082344,emissiveIntensity:.18});
const warmCream=new THREE.MeshPhysicalMaterial({color:0xf2d49c,metalness:.03,roughness:.28,clearcoat:.65});
let faceReadsUpgraded=0;
const astro=findToken(17);
if(astro){
  const visor=new THREE.Mesh(new RoundedBoxGeometry(.52,.18,.09,3,.055),darkVisor);visor.position.set(0,1.43,.39);visor.castShadow=true;astro.add(visor);faceReadsUpgraded++;
}
const dog=findToken(10);
if(dog){
  const muzzle=new THREE.Mesh(new RoundedBoxGeometry(.44,.25,.15,3,.085),warmCream);muzzle.position.set(0,1.23,.39);muzzle.castShadow=true;dog.add(muzzle);
  for(const sx of [-1,1]){const eye=new THREE.Mesh(new THREE.SphereGeometry(.045,12,8),darkVisor);eye.position.set(sx*.11,1.36,.47);dog.add(eye)}
  faceReadsUpgraded++;
}

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v9',referencePixelsUsed:false,constructionProtocol:'wish-delivery-v7.6',legacyStageSignHidden,globeReduced,keyLightsReduced,hotPointsReduced,faceReadsUpgraded,stage1Intent:'center-subtraction'};
document.documentElement.dataset.sliceVersion='v9';
document.documentElement.dataset.sliceReady='1';
