import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

await import('./candidate-v2-augment.js');
const scene=window.__ctCapturedScene, root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v3 scene missing');

const gold=new THREE.MeshPhysicalMaterial({color:0xf5bd3f,metalness:.76,roughness:.14,clearcoat:1,clearcoatRoughness:.06});
const ivory=new THREE.MeshPhysicalMaterial({color:0xfff0c9,metalness:.03,roughness:.2,clearcoat:.9,clearcoatRoughness:.08});
const pipMat=new THREE.MeshStandardMaterial({color:0x34220b,metalness:.22,roughness:.3});
const cyan=new THREE.MeshStandardMaterial({color:0x5cecff,emissive:0x1387a5,emissiveIntensity:.72,metalness:.12,roughness:.2});
const purple=new THREE.MeshStandardMaterial({color:0xbe6cff,emissive:0x5e1977,emissiveIntensity:.5,metalness:.1,roughness:.22});
function cast(m,receive=true){m.castShadow=true;m.receiveShadow=receive;return m}
function rb(w,h,d,mat,r=.1,s=3){return cast(new THREE.Mesh(new RoundedBoxGeometry(w,h,d,s,r),mat))}
function cyl(r,h,mat,s=32){return cast(new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),mat))}
function sph(r,mat,s=18){return cast(new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(10,s/2)),mat))}

// Brighter value structure: reveal authored geometry instead of using darkness as style.
scene.background=new THREE.Color(0x071329);
if(scene.fog && 'density' in scene.fog) scene.fog.density=.017;
scene.add(new THREE.AmbientLight(0xffeed7,.72));
const warm=new THREE.DirectionalLight(0xffdfae,2.45);warm.position.set(6,10,10);scene.add(warm);
const centerWarm=new THREE.PointLight(0xffc45e,18,18,1.7);centerWarm.position.set(0,5.2,6.2);scene.add(centerWarm);
const centerCyan=new THREE.PointLight(0x5cecff,12,16,1.8);centerCyan.position.set(0,4,-3.2);scene.add(centerCyan);

// One final toy-scale correction for existing player and landmark groups.
let heroBoosted=0;
for(const o of root.children){
  if(o.isGroup && o.position.y>.93 && o.position.y<1.02 && (Math.abs(o.position.x)>3.8 || Math.abs(o.position.z)>3.8)){
    o.scale.multiplyScalar(1.075);heroBoosted++;
  }
}

// Turn each tile into a readable game surface: large title + consequence/subline.
const tileData=[
 ['EXCHANGE','BUY / SELL','#d8c5ff'],['BULL','ASSET +50%','#8ff2ad'],['MINING','BTC REWARD','#f6d28e'],['AIRDROP','FREE TOKEN','#d6b9ff'],['HALVING','SUPPLY SHOCK','#f3c58d'],['NFT','RARE ASSET','#d9b4ff'],
 ['DEFI','YIELD','#b8e8ff'],['WHALE','MARKET MOVE','#a9d9ff'],['RUG','ASSET -50%','#ffaaa8'],['BEAR','ASSET -50%','#ffaaa8'],['STAKING','STEADY YIELD','#aeece6'],['MEME','HIGH RISK','#ffd0aa'],
 ['EVENT','DRAW CARD','#c6bdff'],['VAULT','SAFE ASSET','#f1d49b'],['GAS','PAY FEE','#b9ddff'],['ETF','FLOW BOOST','#b8f0d1'],['DEX','SWAP','#c9c0ff'],['L2','LOW FEE','#a9e7f0'],
 ['AI','NARRATIVE','#d6b4ff'],['FUNDING','PAY / RECEIVE','#f0c4ac'],['START','+ CASH','#c69cff'],['HACK','LOSE CASH','#ffabab'],['LIQUID','FORCED SELL','#ff9e9e'],['YIELD','INCOME','#c0edc0']
];
function tileTexture(title,sub,bg){
  const c=document.createElement('canvas');c.width=768;c.height=620;const x=c.getContext('2d');
  x.fillStyle=bg;x.beginPath();x.roundRect(12,12,744,596,54);x.fill();
  const g=x.createLinearGradient(0,0,0,620);g.addColorStop(0,'rgba(255,255,255,.36)');g.addColorStop(.5,'rgba(255,255,255,.06)');g.addColorStop(1,'rgba(13,25,55,.07)');x.fillStyle=g;x.beginPath();x.roundRect(12,12,744,596,54);x.fill();
  x.strokeStyle='rgba(255,237,177,.9)';x.lineWidth=18;x.beginPath();x.roundRect(16,16,736,588,50);x.stroke();
  x.fillStyle='#12182a';x.textAlign='center';x.textBaseline='middle';x.font='1000 112px Arial Black,Arial,sans-serif';x.fillText(title,384,270);
  x.fillStyle='#263755';x.font='800 48px Arial,sans-serif';x.fillText(sub,384,400);
  x.fillStyle='rgba(255,255,255,.75)';x.fillRect(190,478,388,9);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
const tileGroups=root.children.filter(o=>o.isGroup && Math.abs(o.position.y-.68)<.04 && (Math.abs(Math.abs(o.position.x)-5.4)<.2 || Math.abs(Math.abs(o.position.z)-5.4)<.2));
tileGroups.forEach((g,i)=>{
  const [title,sub,bg]=tileData[i%tileData.length];
  const mat=new THREE.MeshPhysicalMaterial({map:tileTexture(title,sub,bg),metalness:.03,roughness:.28,clearcoat:.75,clearcoatRoughness:.1});
  const p=cast(new THREE.Mesh(new THREE.PlaneGeometry(1.32,1.12),mat),false);p.rotation.x=-Math.PI/2;p.position.set(0,.44,0);p.renderOrder=4;g.add(p);
});

// Move the primary dice into the center foreground, where the reference uses them as hero props.
const oldDice=root.children.filter(o=>o.isGroup && o.position.y>1.05 && o.position.y<1.35 && o.position.z>5 && Math.abs(o.position.x)<2.2);
oldDice.forEach(o=>o.visible=false);
function die(){
  const g=new THREE.Group();const body=rb(1.12,1.12,1.12,ivory,.23,5);g.add(body);
  // Front and top pips create a readable toy-die silhouette from the locked camera.
  for(const [x,y,z] of [[0,.57,0],[-.23,.57,-.23],[.23,.57,.23],[-.23,.57,.23],[.23,.57,-.23],[-.26,0,.57],[.26,0,.57],[0,.27,.57],[0,-.27,.57]]){const p=sph(.075,pipMat,12);p.position.set(x,y,z);g.add(p)}
  return g;
}
const d1=die(),d2=die();d1.position.set(-.72,2.05,2.62);d1.rotation.set(.22,.34,.12);d2.position.set(.75,2.0,2.5);d2.rotation.set(-.16,-.28,.2);root.add(d1,d2);

// Center chips and coins remove the large dead zone and reinforce the finance-board fantasy.
function stack(x,y,z,n,matA,matB=gold){for(let i=0;i<n;i++){const c=cyl(.27,.075,i%2?matA:matB,30);c.position.set(x+(i%2)*.025,y+i*.07,z);root.add(c)}}
stack(-1.8,1.7,2.82,5,purple);stack(1.82,1.7,2.78,5,cyan);stack(-2.25,1.7,1.92,4,gold,gold);stack(2.26,1.7,1.9,4,gold,gold);

// Break repeated horizontal-window rhythm with vertical facade ribs on skyline buildings.
const skyline=root.children.find(o=>o.isGroup && o.children.filter(c=>c.isGroup).length>=15);
let facadeRibs=0;
if(skyline){
  skyline.children.filter(c=>c.isGroup).forEach((b,i)=>{
    if(i%2) return;
    const box=new THREE.Box3().setFromObject(b);if(box.isEmpty())return;
    const size=new THREE.Vector3(),center=new THREE.Vector3();box.getSize(size);box.getCenter(center);
    if(size.y<1.2||size.y>9)return;
    for(const sx of [-.22,.22]){const rib=rb(.055,size.y*.72,.055,i%4===0?gold:(i%4===2?cyan:purple),.015,1);rib.position.set(center.x+size.x*sx,center.y,box.max.z+.035);root.add(rib);facadeRibs++}
  });
}

// Finance/neon signs add distinct authored landmarks without adding more generic towers.
function signTexture(title,sub,color){const c=document.createElement('canvas');c.width=800;c.height=360;const x=c.getContext('2d');x.fillStyle='rgba(5,15,38,.96)';x.fillRect(0,0,800,360);x.strokeStyle=color;x.lineWidth=16;x.strokeRect(12,12,776,336);x.textAlign='center';x.textBaseline='middle';x.fillStyle=color;x.font='1000 104px Arial Black,Arial';x.fillText(title,400,145);x.fillStyle='#e6efff';x.font='700 40px Arial';x.fillText(sub,400,245);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t}
for(const [x,y,z,title,sub,col] of [[-10.0,3.4,-6.5,'CEX','SPOT · PERP','#ffd56b'],[9.7,4.6,-8.1,'DEFI','TVL ↑','#62eaff'],[-5.0,6.0,-10.2,'HASH','MINING POWER','#9a7bff'],[5.0,5.7,-10.1,'ETF','FLOW +12%','#6cf0a4']]){
  const f=rb(2.15,1.16,.16,darkFacade(),.1,3);f.position.set(x,y,z);root.add(f);const p=new THREE.Mesh(new THREE.PlaneGeometry(1.95,.96),new THREE.MeshStandardMaterial({map:signTexture(title,sub,col),emissive:new THREE.Color(col),emissiveIntensity:.22,metalness:.08,roughness:.32}));p.position.set(x,y,z+.095);root.add(p);
}
function darkFacade(){return new THREE.MeshPhysicalMaterial({color:0x0d1835,metalness:.48,roughness:.23,clearcoat:.55})}

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v3',referencePixelsUsed:false,tileStoryPanels:tileGroups.length,oldDiceHidden:oldDice.length,facadeRibs,heroBoosted};
document.documentElement.dataset.sliceVersion='v3';
document.documentElement.dataset.sliceReady='1';
