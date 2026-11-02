import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

// Capture the scene/root created by the v1 construction without changing its source.
const originalSceneAdd = THREE.Scene.prototype.add;
THREE.Scene.prototype.add = function(...objects) {
  if (!window.__ctCapturedScene) window.__ctCapturedScene = this;
  if (!window.__ctCapturedRoot) {
    const firstGroup = objects.find(o => o && o.isGroup);
    if (firstGroup) window.__ctCapturedRoot = firstGroup;
  }
  return originalSceneAdd.apply(this, objects);
};

await import('./candidate-v1.js');
for (let i=0; i<300 && !window.__cryptoSliceReady; i++) await new Promise(r=>setTimeout(r,20));
THREE.Scene.prototype.add = originalSceneAdd;

const scene = window.__ctCapturedScene;
const root = window.__ctCapturedRoot;
if (!scene || !root) throw new Error('v2 scene capture failed');

const gold = new THREE.MeshPhysicalMaterial({color:0xf3b934,metalness:.78,roughness:.14,clearcoat:1,clearcoatRoughness:.06,emissive:0x683000,emissiveIntensity:.12});
const goldLite = new THREE.MeshPhysicalMaterial({color:0xffdf7a,metalness:.66,roughness:.12,clearcoat:1,clearcoatRoughness:.05});
const navy = new THREE.MeshPhysicalMaterial({color:0x0b1637,metalness:.38,roughness:.2,clearcoat:.95,clearcoatRoughness:.08});
const dark = new THREE.MeshStandardMaterial({color:0x10182c,metalness:.62,roughness:.28});
const cyan = new THREE.MeshStandardMaterial({color:0x56e8ff,metalness:.12,roughness:.17,emissive:0x0d7da3,emissiveIntensity:.9});
const purple = new THREE.MeshStandardMaterial({color:0xc365ff,metalness:.08,roughness:.2,emissive:0x5b1878,emissiveIntensity:.55});
const green = new THREE.MeshStandardMaterial({color:0x5cf7a0,metalness:.12,roughness:.22,emissive:0x14733e,emissiveIntensity:.35});
const red = new THREE.MeshStandardMaterial({color:0xff646c,metalness:.12,roughness:.22,emissive:0x741b28,emissiveIntensity:.32});

function cast(m, receive=true){m.castShadow=true;m.receiveShadow=receive;return m}
function rb(w,h,d,mat,r=.1,s=3){return cast(new THREE.Mesh(new RoundedBoxGeometry(w,h,d,s,r),mat))}
function cyl(r,h,mat,s=32){return cast(new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),mat))}
function sphere(r,mat,s=28){return cast(new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(12,s/2)),mat))}
function cone(r,h,mat,s=20){return cast(new THREE.Mesh(new THREE.ConeGeometry(r,h,s),mat))}
function textTexture(title, subtitle='', accent='#ffe27f'){
  const c=document.createElement('canvas');c.width=1024;c.height=512;const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,1024,512);g.addColorStop(0,'#07142f');g.addColorStop(.55,'#10295a');g.addColorStop(1,'#071126');x.fillStyle=g;x.fillRect(0,0,1024,512);
  x.strokeStyle='rgba(255,208,93,.82)';x.lineWidth=14;x.strokeRect(14,14,996,484);
  x.textAlign='center';x.textBaseline='middle';x.fillStyle=accent;x.font='900 120px Arial,sans-serif';x.fillText(title,512,220);
  if(subtitle){x.fillStyle='#80eaff';x.font='700 44px Arial,sans-serif';x.fillText(subtitle,512,340)}
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
function plane(w,h,texture,emissive=0x112c54){const m=new THREE.MeshStandardMaterial({map:texture,emissive,emissiveIntensity:.24,metalness:.1,roughness:.3});return cast(new THREE.Mesh(new THREE.PlaneGeometry(w,h),m),false)}

// 1) Raise the authored landmark/token scale: the reference uses collectible-toy proportions.
const heroGroups=[];
for(const o of root.children){
  if(o.isGroup && o.position.y>.93 && o.position.y<1.02 && (Math.abs(o.position.x)>3.8 || Math.abs(o.position.z)>3.8)){
    o.scale.multiplyScalar(1.16); heroGroups.push(o);
  }
}

// 2) Replace the weak center read with an additional physical hero monument.
const hero=new THREE.Group();hero.position.set(0,0,0);root.add(hero);
const backing=rb(5.45,1.42,.36,navy,.18,5);backing.position.set(0,4.42,.92);hero.add(backing);
const frame=rb(5.72,1.65,.18,gold,.2,5);frame.position.set(0,4.42,.69);hero.add(frame);backing.position.z=.82;
const inset=rb(5.34,1.28,.16,navy,.15,4);inset.position.set(0,4.42,1.03);hero.add(inset);
for(const s of [-1,1]){
  for(let i=0;i<6;i++){
    const leaf=cone(.105,.42,goldLite,5);leaf.rotation.z=s*(.72-i*.075);leaf.position.set(s*(2.72+i*.17),4.05+i*.13,.98);hero.add(leaf);
  }
}
const btc=cyl(.38,.12,goldLite,40);btc.rotation.x=Math.PI/2;btc.position.set(0,3.74,1.17);hero.add(btc);
const btcFace=plane(.55,.55,textTexture('₿','','#382100'));btcFace.material.transparent=true;btcFace.position.set(0,3.74,1.245);hero.add(btcFace);

let titleBuilt=false;
try{
  const font=await new FontLoader().loadAsync('https://cdn.jsdelivr.net/npm/three@0.180.0/examples/fonts/helvetiker_bold.typeface.json');
  const geo=new TextGeometry('CRYPTO TYCOON',{font,size:.55,depth:.13,curveSegments:8,bevelEnabled:true,bevelThickness:.025,bevelSize:.018,bevelSegments:3});
  geo.computeBoundingBox();const b=geo.boundingBox;const width=b.max.x-b.min.x;const scale=Math.min(1,4.65/width);geo.scale(scale,scale,scale);geo.computeBoundingBox();const bb=geo.boundingBox;geo.translate(-(bb.max.x+bb.min.x)/2,-(bb.max.y+bb.min.y)/2,0);
  const txt=cast(new THREE.Mesh(geo,goldLite));txt.position.set(0,4.46,1.13);hero.add(txt);titleBuilt=true;
}catch(e){
  const fallback=plane(4.8,.92,textTexture('CRYPTO TYCOON','SURVIVE THE CYCLE','#ffe38c'));fallback.position.set(0,4.46,1.13);hero.add(fallback);
}
// Crown becomes a real layered object over the monument.
const crownBase=rb(1.5,.2,.34,goldLite,.07,3);crownBase.position.set(0,5.23,.97);hero.add(crownBase);
for(let i=-2;i<=2;i++){const spike=cone(.17,i===0?.82:(Math.abs(i)===1?.66:.48),goldLite,16);spike.position.set(i*.29,5.58+(i===0?.12:0),.96);hero.add(spike)}

// 3) Add authored skyline anchors so the city no longer reads as repeated boxes.
function exchangeSpire(){
  const g=new THREE.Group();
  const b0=rb(2.15,.38,1.7,gold,.18,4);b0.position.y=.19;g.add(b0);
  const lower=rb(1.72,3.0,1.3,new THREE.MeshPhysicalMaterial({color:0x122b58,metalness:.55,roughness:.2,clearcoat:.6}),.12,3);lower.position.y=1.82;g.add(lower);
  for(let i=0;i<5;i++){const ledge=rb(1.9,.1,1.42,i%2?gold:cyan,.03,2);ledge.position.y=.62+i*.54;g.add(ledge)}
  const top=rb(1.28,1.55,1.06,new THREE.MeshPhysicalMaterial({color:0x19396d,metalness:.5,roughness:.18,clearcoat:.65}),.1,3);top.position.y=4.02;g.add(top);
  const roof=cone(.82,.82,goldLite,4);roof.rotation.y=Math.PI/4;roof.position.y=5.18;g.add(roof);
  const signFrame=rb(2.0,.7,.16,gold,.08,3);signFrame.position.set(0,2.55,.75);g.add(signFrame);
  const sign=plane(1.76,.52,textTexture('EXCHANGE','BUY · SELL','#ffe58a'));sign.position.set(0,2.55,.845);g.add(sign);
  return g;
}
function ethSpire(){
  const g=new THREE.Group();const base=rb(1.75,.34,1.45,gold,.15,3);base.position.y=.17;g.add(base);
  const tower=rb(1.2,3.45,1.05,new THREE.MeshPhysicalMaterial({color:0x102a58,metalness:.55,roughness:.18,clearcoat:.6}),.1,3);tower.position.y=2.05;g.add(tower);
  for(let y=.65;y<3.6;y+=.38){const v=rb(.055,.3,1.08,y%1>.5?purple:cyan,.015,1);v.position.set(-.4+(y%.8),y,.55);g.add(v)}
  const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.72,0),new THREE.MeshPhysicalMaterial({color:0x8bdcff,metalness:.18,roughness:.08,transmission:.25,transparent:true,opacity:.9,emissive:0x235fad,emissiveIntensity:.6,clearcoat:1}));gem.scale.y=1.35;gem.position.y=4.85;gem.castShadow=true;g.add(gem);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.95,.055,8,40),cyan);ring.rotation.x=Math.PI/2;ring.position.y=4.82;g.add(ring);return g;
}
function btcBeacon(){
  const g=new THREE.Group();const base=cyl(.92,.3,gold,40);base.position.y=.15;g.add(base);const p=cyl(.7,2.3,navy,40);p.position.y=1.45;g.add(p);
  const disk=cyl(.68,.12,goldLite,48);disk.rotation.x=Math.PI/2;disk.position.set(0,2.65,.72);g.add(disk);
  const f=plane(.92,.92,textTexture('₿','','#402500'));f.material.transparent=true;f.position.set(0,2.65,.8);g.add(f);
  const halo=new THREE.Mesh(new THREE.TorusGeometry(1.0,.065,8,48),cyan);halo.position.set(0,2.65,.73);g.add(halo);return g;
}
const ex=exchangeSpire();ex.position.set(-7.3,-.68,-9.1);ex.scale.setScalar(1.08);root.add(ex);
const eth=ethSpire();eth.position.set(6.85,-.68,-9.35);root.add(eth);
const beacon=btcBeacon();beacon.position.set(9.05,-.68,-7.2);beacon.rotation.y=-.25;root.add(beacon);

// Market billboard inspired by financial terminals, created procedurally (not reference pixels).
function chartTexture(){
  const c=document.createElement('canvas');c.width=1200;c.height=420;const x=c.getContext('2d');
  const bg=x.createLinearGradient(0,0,0,420);bg.addColorStop(0,'#07142f');bg.addColorStop(1,'#0d2149');x.fillStyle=bg;x.fillRect(0,0,1200,420);
  x.strokeStyle='rgba(94,221,255,.16)';x.lineWidth=2;for(let i=0;i<12;i++){x.beginPath();x.moveTo(i*100,0);x.lineTo(i*100,420);x.stroke()}for(let j=0;j<6;j++){x.beginPath();x.moveTo(0,j*70);x.lineTo(1200,j*70);x.stroke()}
  let y=260;for(let i=0;i<24;i++){const up=(i*7)%5!==0;const open=y;const delta=((i*17)%70)+22;y=Math.max(80,Math.min(335,y+(up?-delta:delta)*.45));const close=y;const cx=35+i*47;const col=up?'#55f1a0':'#ff6570';x.strokeStyle=col;x.lineWidth=6;x.beginPath();x.moveTo(cx,Math.min(open,close)-32);x.lineTo(cx,Math.max(open,close)+32);x.stroke();x.fillStyle=col;x.fillRect(cx-13,Math.min(open,close),26,Math.max(12,Math.abs(open-close)))}
  x.fillStyle='#f5d778';x.font='900 44px Arial';x.fillText('MARKET · BTC 87,420  +7.2%',38,55);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
const chartFrame=rb(7.5,2.6,.22,gold,.16,4);chartFrame.position.set(0,6.2,-10.55);root.add(chartFrame);
const chart=plane(7.16,2.25,chartTexture(),0x153a68);chart.position.set(0,6.2,-10.41);root.add(chart);

// 4) Give tiles real semantic labels while keeping the physical tile geometry.
const labels=['EXCHANGE','BULL','MINING','AIRDROP','HALVING','NFT','DEFI','WHALE','RUG','BEAR','STAKING','MEME','EVENT','VAULT','GAS','ETF','DEX','L2','AI','FUNDING','START','HACK','LIQUID','YIELD'];
const tileGroups=root.children.filter(o=>o.isGroup && Math.abs(o.position.y-.68)<.04 && (Math.abs(Math.abs(o.position.x)-5.4)<.2 || Math.abs(Math.abs(o.position.z)-5.4)<.2));
function labelTex(t){const c=document.createElement('canvas');c.width=512;c.height=128;const x=c.getContext('2d');x.clearRect(0,0,512,128);x.fillStyle='rgba(5,12,30,.72)';x.beginPath();x.roundRect(12,14,488,100,24);x.fill();x.fillStyle='#fff1b1';x.textAlign='center';x.textBaseline='middle';x.font='900 42px Arial';x.fillText(t,256,66);const tx=new THREE.CanvasTexture(c);tx.colorSpace=THREE.SRGBColorSpace;return tx}
tileGroups.forEach((g,i)=>{const p=new THREE.Mesh(new THREE.PlaneGeometry(1.18,.3),new THREE.MeshBasicMaterial({map:labelTex(labels[i%labels.length]),transparent:true,depthWrite:false}));p.rotation.x=-Math.PI/2;p.position.set(0,.415,.46);g.add(p)});

// 5) Foreground density: real chips, coins and event-card stacks.
function chipStack(x,z,n,colorMat){for(let i=0;i<n;i++){const c=cyl(.29,.075,i%2?goldLite:colorMat,32);c.position.set(x+(i%2)*.025,.82+i*.072,z);root.add(c)}}
chipStack(-6.6,5.7,6,purple);chipStack(-5.9,5.95,4,cyan);chipStack(5.85,5.8,5,green);chipStack(6.45,5.55,3,purple);chipStack(-7.35,3.75,4,red);
for(let i=0;i<3;i++){const card=rb(1.05,.08,1.42,i%2?purple:navy,.08,3);card.position.set(-8.1+i*.09,.78+i*.08,4.9+i*.04);card.rotation.y=-.23;root.add(card)}

// Practical glow around signature skyline.
for(const [x,y,z,c] of [[-7.3,2.3,-8.3,0x65e9ff],[6.85,3.6,-8.6,0xa068ff],[9.05,2.5,-6.4,0xffba48]]){const l=new THREE.PointLight(c,18,10,1.7);l.position.set(x,y,z);root.add(l)}

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v2',referencePixelsUsed:false,heroGroupsScaled:heroGroups.length,titleBuilt,authoredSkylineAnchors:3,tileLabels:tileGroups.length};
document.documentElement.dataset.sliceReady='1';
document.documentElement.dataset.sliceVersion='v2';
