import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

await import('./candidate-v7-augment.js');
const scene=window.__ctCapturedScene,root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v8 scene missing');

const gold=new THREE.MeshPhysicalMaterial({color:0xf2b841,metalness:.82,roughness:.13,clearcoat:1,clearcoatRoughness:.05});
const goldLite=new THREE.MeshPhysicalMaterial({color:0xffe9a6,metalness:.58,roughness:.13,clearcoat:1});
const navy=new THREE.MeshPhysicalMaterial({color:0x0a1736,metalness:.46,roughness:.22,clearcoat:.92,clearcoatRoughness:.08});
const cyan=new THREE.MeshStandardMaterial({color:0x64e9ff,metalness:.12,roughness:.18,emissive:0x0b7897,emissiveIntensity:.65});
const purple=new THREE.MeshStandardMaterial({color:0xb76fff,metalness:.08,roughness:.2,emissive:0x4c136d,emissiveIntensity:.48});
const red=new THREE.MeshPhysicalMaterial({color:0xf05f63,metalness:.12,roughness:.25,clearcoat:.72});
const ivory=new THREE.MeshPhysicalMaterial({color:0xf8edcf,metalness:.02,roughness:.22,clearcoat:.8});
const glass=new THREE.MeshPhysicalMaterial({color:0x9eefff,metalness:.02,roughness:.05,transmission:.42,transparent:true,opacity:.62,clearcoat:1});
const darkGlass=new THREE.MeshPhysicalMaterial({color:0x173e63,metalness:.06,roughness:.08,transmission:.24,transparent:true,opacity:.78,clearcoat:1});

function cast(m,receive=true){m.castShadow=true;m.receiveShadow=receive;return m}
function rb(w,h,d,mat,r=.1,s=3){return cast(new THREE.Mesh(new RoundedBoxGeometry(w,h,d,s,r),mat))}
function cyl(r,h,mat,s=32){return cast(new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),mat))}
function sph(r,mat,s=24){return cast(new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(12,s/2)),mat))}
function cone(r,h,mat,s=20){return cast(new THREE.Mesh(new THREE.ConeGeometry(r,h,s),mat))}
function torus(r,t,mat,s=40){return cast(new THREE.Mesh(new THREE.TorusGeometry(r,t,10,s),mat))}
function plane(w,h,texture){const m=new THREE.MeshBasicMaterial({map:texture,transparent:true,toneMapped:false,side:THREE.DoubleSide});const p=new THREE.Mesh(new THREE.PlaneGeometry(w,h),m);p.renderOrder=24;return p}

function titleTexture(){
 const c=document.createElement('canvas');c.width=1800;c.height=520;const x=c.getContext('2d');x.clearRect(0,0,c.width,c.height);x.textAlign='center';x.textBaseline='middle';x.lineJoin='round';
 x.shadowColor='rgba(255,170,42,.52)';x.shadowBlur=22;x.font='1000 250px "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif';x.lineWidth=34;x.strokeStyle='#522307';x.strokeText('币圈大富翁',900,240);
 const g=x.createLinearGradient(0,80,0,370);g.addColorStop(0,'#fffbdc');g.addColorStop(.28,'#ffe78d');g.addColorStop(.7,'#eeb035');g.addColorStop(1,'#b96a08');x.fillStyle=g;x.fillText('币圈大富翁',900,240);
 x.shadowBlur=0;x.font='900 52px Arial,sans-serif';x.fillStyle='#93ebff';x.fillText('CRYPTO TYCOON',900,430);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
function smallTexture(title,sub,color='#ffe18a'){
 const c=document.createElement('canvas');c.width=800;c.height=360;const x=c.getContext('2d');const g=x.createLinearGradient(0,0,800,360);g.addColorStop(0,'#09152f');g.addColorStop(1,'#122d59');x.fillStyle=g;x.fillRect(0,0,800,360);x.strokeStyle=color;x.lineWidth=14;x.strokeRect(12,12,776,336);x.textAlign='center';x.textBaseline='middle';x.fillStyle=color;x.font='1000 82px "Noto Sans CJK SC","PingFang SC",Arial,sans-serif';x.fillText(title,400,142);x.fillStyle='#d9efff';x.font='800 30px Arial,"Noto Sans CJK SC",sans-serif';x.fillText(sub,400,252);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}

// A1 — clear the hero depth band. Hide previous broad center signs/crests, but never the stage itself.
let centerSignsHidden=0;
for(const o of root.children){
 if(!o.visible)continue;
 const box=new THREE.Box3().setFromObject(o);if(box.isEmpty())continue;const size=new THREE.Vector3(),center=new THREE.Vector3();box.getSize(size);box.getCenter(center);
 if(Math.abs(center.x)<1.4 && center.y>2.55 && center.y<5.8 && size.x>4.2 && size.y<3.5 && size.z<2.7){o.visible=false;centerSignsHidden++}
}

// Rebuild title as a rear architectural landmark, leaving the dice/stage unobstructed.
const hero=new THREE.Group();hero.name='v8HeroTitle';root.add(hero);
for(const sx of [-1,1]){
 const pillar=rb(.34,3.05,.42,navy,.09,3);pillar.position.set(sx*3.05,3.22,-2.42);hero.add(pillar);
 const cap=rb(.62,.22,.66,gold,.07,3);cap.position.set(sx*3.05,4.74,-2.42);hero.add(cap);
 const base=rb(.72,.22,.72,gold,.07,3);base.position.set(sx*3.05,1.68,-2.42);hero.add(base);
}
const beam=rb(6.7,.25,.52,gold,.08,4);beam.position.set(0,4.82,-2.42);hero.add(beam);
const back=rb(6.15,1.38,.18,new THREE.MeshPhysicalMaterial({color:0x08152f,metalness:.48,roughness:.18,clearcoat:.9}),.09,4);back.position.set(0,3.95,-2.38);hero.add(back);
const word=plane(5.78,1.67,titleTexture());word.position.set(0,4.0,-2.26);hero.add(word);
const crown=torus(.55,.075,goldLite,44);crown.rotation.x=Math.PI/2;crown.scale.y=.55;crown.position.set(0,5.16,-2.35);hero.add(crown);
for(let i=-2;i<=2;i++){const p=cone(.11,i===0?.62:(Math.abs(i)===1?.48:.36),goldLite,12);p.position.set(i*.23,5.5+(i===0?.05:0),-2.34);hero.add(p)}

// A3 — reduce procedural shelf repetition further.
const skyline=root.children.find(o=>o.isGroup && o.children.filter(c=>c.isGroup).length>=15);
let skylineTrimmed=0;
if(skyline){skyline.children.forEach((b,i)=>{if(b.visible && (i%2===1 || i%7===0)){b.visible=false;skylineTrimmed++}})}

// Add two unmistakable city silhouettes: mining-rig rack and DeFi ring tower.
const mining=new THREE.Group();mining.name='v8MiningRig';root.add(mining);
const miningBase=rb(2.7,.28,1.35,gold,.09,3);miningBase.position.y=.14;mining.add(miningBase);
const rack=rb(2.42,3.15,.82,navy,.08,3);rack.position.y=1.82;mining.add(rack);
for(let i=-1;i<=1;i++){
 const fan=torus(.43,.085,cyan,32);fan.position.set(i*.72,2.0,.47);mining.add(fan);
 const hub=cyl(.11,.12,goldLite,20);hub.rotation.x=Math.PI/2;hub.position.set(i*.72,2.0,.49);mining.add(hub);
 for(let k=0;k<6;k++){const blade=rb(.05,.31,.035,goldLite,.01,1);blade.position.set(i*.72,2.0,.53);blade.rotation.z=k*Math.PI/3;mining.add(blade)}
}
const miningSign=plane(2.1,.66,smallTexture('算力矿场','HASH · POWER · BLOCK','#80efff'));miningSign.position.set(0,3.38,.48);mining.add(miningSign);
mining.position.set(-9.0,-.68,-6.0);mining.rotation.y=.14;root.add(mining);

const defi=new THREE.Group();defi.name='v8DefiTower';
const defiBase=cyl(1.05,.26,gold,40);defiBase.position.y=.13;defi.add(defiBase);
const defiCore=cyl(.36,4.2,navy,28);defiCore.position.y=2.22;defi.add(defiCore);
for(let i=0;i<4;i++){const r=torus(.78+i*.09,.065,i%2?purple:cyan,48);r.rotation.x=Math.PI/2;r.rotation.z=i*.35;r.position.y=1.25+i*.82;defi.add(r)}
const defiGem=new THREE.Mesh(new THREE.OctahedronGeometry(.62,0),glass);defiGem.position.y=4.75;defiGem.scale.y=1.3;defiGem.castShadow=true;defi.add(defiGem);
defi.position.set(9.25,-.68,-7.6);defi.rotation.y=-.14;root.add(defi);

// A2 — strengthen the four player-piece silhouettes using distinct collectible-toy language.
function perimeterPositions(){const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];xs.forEach(x=>a.push([x,-5.4]));zs.forEach(z=>a.push([5.4,z]));[...xs].reverse().forEach(x=>a.push([x,5.4]));[...zs].reverse().forEach(z=>a.push([-5.4,z]));return a}
const positions=perimeterPositions(),indices=[17,10,13,20];let collectibleUpgrades=0;
for(let i=0;i<indices.length;i++){
 const [x,z]=positions[indices[i]];let token=null,dist=1e9;
 for(const o of root.children){if(!o.isGroup||o.position.y<.7||o.position.y>1.25)continue;const d=(o.position.x-x)**2+(o.position.z-z)**2;if(d<dist){dist=d;token=o}}
 if(!token||dist>.35)continue;
 token.scale.multiplyScalar(1.06);
 const pedestal=torus(.42,.045,i===0?cyan:i===1?gold:i===2?purple:red,40);pedestal.rotation.x=Math.PI/2;pedestal.position.y=.18;token.add(pedestal);
 if(i===0){
   const dome=sph(.36,glass,28);dome.scale.y=.88;dome.position.set(0,1.42,.03);token.add(dome);
   const visor=rb(.42,.14,.09,darkGlass,.06,3);visor.position.set(0,1.43,.32);token.add(visor);
   const pack=rb(.38,.56,.24,navy,.08,3);pack.position.set(0,.88,-.31);token.add(pack);
 }
 if(i===1){
   for(const sx of [-1,1]){const ear=cone(.16,.48,goldLite,12);ear.rotation.z=sx*.22;ear.position.set(sx*.28,1.6,.03);token.add(ear)}
   const muzzle=rb(.38,.24,.25,ivory,.1,3);muzzle.position.set(0,1.23,.31);token.add(muzzle);
   const chain=torus(.28,.035,gold,32);chain.rotation.x=Math.PI/2;chain.position.set(0,.93,.23);token.add(chain);
 }
 if(i===2){
   for(let k=-2;k<=2;k++){const px=rb(.13,.28+(.16*(2-Math.abs(k))),.13,k%2?cyan:purple,.025,2);px.position.set(k*.15,1.67,.02);token.add(px)}
   for(const sx of [-1,1]){const shoulder=rb(.28,.22,.32,purple,.06,3);shoulder.position.set(sx*.36,.88,0);token.add(shoulder)}
   const face=rb(.46,.28,.08,darkGlass,.05,2);face.position.set(0,1.35,.34);token.add(face);
 }
 if(i===3){
   for(const sx of [-1,1]){const horn=cone(.12,.74,goldLite,14);horn.rotation.z=sx*.9;horn.position.set(sx*.43,1.52,.02);token.add(horn)}
   const brow=rb(.62,.16,.16,red,.06,3);brow.position.set(0,1.35,.25);token.add(brow);
   const scarf=torus(.28,.055,red,34);scarf.rotation.x=Math.PI/2;scarf.position.set(0,.98,.08);token.add(scarf);
 }
 collectibleUpgrades++;
}

// A4 — center lighting must reveal geometry rather than erase it.
let centerLightsReduced=0;
scene.traverse(o=>{
 if(o.isPointLight && Math.abs(o.position.x)<4.8 && Math.abs(o.position.z)<4.8 && o.intensity>1.2){o.intensity*=.58;centerLightsReduced++}
});
const softFill=new THREE.DirectionalLight(0xbdd9ff,.28);softFill.position.set(5,10,11);scene.add(softFill);

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v8',referencePixelsUsed:false,constructionProtocol:'wish-delivery-v7.6',centerSignsHidden,skylineTrimmed,collectibleUpgrades,heroTitleRearMounted:true,authoredCityLandmarksAdded:2,centerLightsReduced};
document.documentElement.dataset.sliceVersion='v8';
document.documentElement.dataset.sliceReady='1';
