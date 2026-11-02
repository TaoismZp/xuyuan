import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

await import('./candidate-v4-augment.js');
const scene=window.__ctCapturedScene, root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v5 scene missing');

const gold=new THREE.MeshPhysicalMaterial({color:0xf4bc3d,metalness:.76,roughness:.14,clearcoat:1,clearcoatRoughness:.06});
const ivory=new THREE.MeshPhysicalMaterial({color:0xffedc5,metalness:.03,roughness:.28,clearcoat:.72});
const dark=new THREE.MeshPhysicalMaterial({color:0x0e1934,metalness:.55,roughness:.25,clearcoat:.5});
const cyan=new THREE.MeshStandardMaterial({color:0x5cecff,emissive:0x117a99,emissiveIntensity:.65,metalness:.12,roughness:.22});
const orange=new THREE.MeshPhysicalMaterial({color:0xffaa45,metalness:.08,roughness:.3,clearcoat:.65});
const purple=new THREE.MeshPhysicalMaterial({color:0x9b6cff,metalness:.1,roughness:.27,clearcoat:.65});
const green=new THREE.MeshPhysicalMaterial({color:0x60e79a,metalness:.1,roughness:.26,clearcoat:.7});
function cast(m,receive=true){m.castShadow=true;m.receiveShadow=receive;return m}
function rb(w,h,d,mat,r=.1,s=3){return cast(new THREE.Mesh(new RoundedBoxGeometry(w,h,d,s,r),mat))}
function cyl(r,h,mat,s=32){return cast(new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),mat))}
function sph(r,mat,s=24){return cast(new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(12,s/2)),mat))}
function cone(r,h,mat,s=20){return cast(new THREE.Mesh(new THREE.ConeGeometry(r,h,s),mat))}
function lineTube(a,b,r,mat){const dir=new THREE.Vector3().subVectors(b,a),len=dir.length();const m=cyl(r,len,mat,10);m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize());return m}
function simpleTextTexture(title,sub='',accent='#ffe188'){
 const c=document.createElement('canvas');c.width=512;c.height=320;const x=c.getContext('2d');x.fillStyle='#08142f';x.fillRect(0,0,512,320);x.strokeStyle=accent;x.lineWidth=12;x.strokeRect(10,10,492,300);x.textAlign='center';x.textBaseline='middle';x.fillStyle=accent;x.font='1000 70px Arial Black,Arial';x.fillText(title,256,130);if(sub){x.fillStyle='#dcecff';x.font='700 30px Arial';x.fillText(sub,256,220)}const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}
function signPlane(w,h,title,sub,accent){const m=new THREE.MeshStandardMaterial({map:simpleTextTexture(title,sub,accent),emissive:0x18315a,emissiveIntensity:.18,roughness:.35});return cast(new THREE.Mesh(new THREE.PlaneGeometry(w,h),m),false)}

// AIRDROP: strong canopy + suspended BTC crate, placed on the upper-left board edge.
function airdrop(){
 const g=new THREE.Group();
 const canopyMat=new THREE.MeshPhysicalMaterial({color:0xffc267,roughness:.24,clearcoat:.75});
 const canopy=new THREE.Mesh(new THREE.SphereGeometry(.82,32,16,0,Math.PI*2,0,Math.PI/2),canopyMat);canopy.scale.y=.55;canopy.position.y=2.6;canopy.castShadow=true;g.add(canopy);
 for(let i=0;i<6;i++){const a=-.64+i*.255;const stripe=lineTube(new THREE.Vector3(a*.82,2.58,0),new THREE.Vector3(a*.35,2.15,.05),.025,ivory);g.add(stripe)}
 const crate=rb(.76,.58,.7,dark,.1,3);crate.position.y=.84;g.add(crate);
 const lid=rb(.84,.12,.78,gold,.06,2);lid.position.y=1.18;g.add(lid);
 const coin=cyl(.2,.07,gold,28);coin.rotation.x=Math.PI/2;coin.position.set(0,.86,.37);g.add(coin);
 for(const sx of [-.55,.55]){const rope=lineTube(new THREE.Vector3(sx,2.45,0),new THREE.Vector3(sx*.34,1.25,0),.018,ivory);g.add(rope)}
 const glow=new THREE.PointLight(0xffc760,5,5,2);glow.position.set(0,1.3,.2);g.add(glow);return g;
}

// MINING: real framed rig with visible fan geometry and cables.
function miningRigHero(){
 const g=new THREE.Group();
 const base=rb(1.58,.18,1.16,gold,.1,3);base.position.y=.09;g.add(base);
 for(const sx of [-.7,.7]){const post=rb(.08,1.5,.08,gold,.025,2);post.position.set(sx,.86,0);g.add(post)}
 for(const y of [.28,.82,1.36]){const beam=rb(1.46,.07,.08,dark,.02,2);beam.position.set(0,y,0);g.add(beam)}
 for(let r=0;r<2;r++) for(let c=0;c<3;c++){
   const gpu=rb(.4,.42,.18,dark,.05,2);gpu.position.set((c-1)*.45,.55+r*.52,.02);g.add(gpu);
   const fan=cyl(.125,.045,cyan,20);fan.rotation.x=Math.PI/2;fan.position.set((c-1)*.45,.55+r*.52,.135);g.add(fan);
   const hub=cyl(.035,.055,gold,12);hub.rotation.x=Math.PI/2;hub.position.copy(fan.position);hub.position.z+=.025;g.add(hub);
 }
 const cable=lineTube(new THREE.Vector3(-.62,.25,-.15),new THREE.Vector3(.58,1.48,-.12),.025,purple);g.add(cable);
 const screen=signPlane(.9,.42,'HASH','BTC / BLOCK','#69e9ff');screen.position.set(0,1.72,.08);g.add(screen);return g;
}

// VAULT: readable gold safe/chest that anchors the lower-left economy side of the board.
function vaultHero(){
 const g=new THREE.Group();
 const base=rb(1.35,.18,1.05,gold,.1,3);base.position.y=.09;g.add(base);
 const safe=rb(.96,.98,.72,dark,.15,4);safe.position.set(0,.66,0);g.add(safe);
 const door=cyl(.34,.09,gold,36);door.rotation.x=Math.PI/2;door.position.set(0,.68,.405);g.add(door);
 const wheel=new THREE.Mesh(new THREE.TorusGeometry(.2,.04,8,28),ivory);wheel.position.set(0,.68,.46);g.add(wheel);
 for(let i=0;i<5;i++){const spoke=rb(.035,.28,.035,ivory,.015,1);spoke.position.set(0,.68,.47);spoke.rotation.z=i*Math.PI/2.5;g.add(spoke)}
 for(let i=0;i<5;i++){const coin=cyl(.15,.07,gold,24);coin.position.set(.55+(i%2)*.05,.18+i*.07,.12);g.add(coin)}
 return g;
}

const a=airdrop();a.position.set(-3.7,1.0,-5.05);a.scale.setScalar(.95);root.add(a);
const mine=miningRigHero();mine.position.set(-5.15,1.0,-2.0);mine.scale.setScalar(.92);mine.rotation.y=.18;root.add(mine);
const vault=vaultHero();vault.position.set(-4.4,1.0,4.6);vault.scale.setScalar(.9);vault.rotation.y=-.12;root.add(vault);

// Local practical lights so the added landmarks read without changing the accepted v4 global lighting.
for(const [x,y,z,c] of [[-3.7,2.3,-4.7,0xffc765],[-5.15,2.0,-1.6,0x59e8ff],[-4.4,1.8,5.0,0xffd467]]){const l=new THREE.PointLight(c,4.5,5.5,2);l.position.set(x,y,z);root.add(l)}

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v5',referencePixelsUsed:false,authoredLandmarksAdded:['airdrop','mining','vault']};
document.documentElement.dataset.sliceVersion='v5';
document.documentElement.dataset.sliceReady='1';
