import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const TEST = new URLSearchParams(location.search).get('test') === '1';
const canvas = document.querySelector('#game3d');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: !TEST, powerPreference: 'high-performance' });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setPixelRatio(Math.min(devicePixelRatio, TEST ? 1 : 1.65));

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050817);
scene.fog = new THREE.FogExp2(0x071027, 0.026);

const camera = new THREE.PerspectiveCamera(34, innerWidth / innerHeight, 0.1, 100);
camera.position.set(12.8, 12.6, 17.2);
camera.lookAt(0, 0.7, 0);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), TEST ? 0.35 : 0.52, 0.7, 0.86);
composer.addPass(bloom);

const MAT = {
  gold: new THREE.MeshPhysicalMaterial({ color: 0xe9a92d, metalness: 0.78, roughness: 0.18, clearcoat: 0.9, clearcoatRoughness: 0.08 }),
  goldBright: new THREE.MeshPhysicalMaterial({ color: 0xffd66c, metalness: 0.7, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.05, emissive: 0x7a3d00, emissiveIntensity: 0.12 }),
  lacquer: new THREE.MeshPhysicalMaterial({ color: 0x08142f, metalness: 0.38, roughness: 0.22, clearcoat: 1, clearcoatRoughness: 0.11 }),
  darkMetal: new THREE.MeshStandardMaterial({ color: 0x151b2c, metalness: 0.68, roughness: 0.32 }),
  ivory: new THREE.MeshPhysicalMaterial({ color: 0xf6e8c2, metalness: 0.04, roughness: 0.23, clearcoat: 0.78, clearcoatRoughness: 0.08 }),
  cyanGlass: new THREE.MeshPhysicalMaterial({ color: 0x5fe8ff, metalness: 0.05, roughness: 0.08, transmission: 0.4, transparent: true, opacity: 0.68, emissive: 0x0e8dab, emissiveIntensity: 0.42, clearcoat: 1 }),
  cyan: new THREE.MeshStandardMaterial({ color: 0x53ddff, metalness: 0.16, roughness: 0.22, emissive: 0x0b668f, emissiveIntensity: 0.66 }),
  magenta: new THREE.MeshStandardMaterial({ color: 0xe35dff, metalness: 0.1, roughness: 0.24, emissive: 0x651276, emissiveIntensity: 0.5 }),
  green: new THREE.MeshPhysicalMaterial({ color: 0x41d989, metalness: 0.18, roughness: 0.27, clearcoat: 0.7 }),
  red: new THREE.MeshPhysicalMaterial({ color: 0xe85a61, metalness: 0.16, roughness: 0.26, clearcoat: 0.7 }),
  blue: new THREE.MeshPhysicalMaterial({ color: 0x3d76e5, metalness: 0.18, roughness: 0.24, clearcoat: 0.72 }),
  purple: new THREE.MeshPhysicalMaterial({ color: 0x7f54d7, metalness: 0.15, roughness: 0.25, clearcoat: 0.72 }),
  orange: new THREE.MeshPhysicalMaterial({ color: 0xf0a442, metalness: 0.14, roughness: 0.26, clearcoat: 0.72 }),
  cream: new THREE.MeshPhysicalMaterial({ color: 0xe7c992, metalness: 0.04, roughness: 0.42, clearcoat: 0.4 }),
  black: new THREE.MeshStandardMaterial({ color: 0x080b13, metalness: 0.25, roughness: 0.36 }),
  glassDark: new THREE.MeshPhysicalMaterial({ color: 0x142f4b, metalness: 0.08, roughness: 0.08, transmission: 0.32, transparent: true, opacity: 0.72, clearcoat: 1 }),
};

const tileMats = [MAT.red, MAT.blue, MAT.purple, MAT.green, MAT.orange, MAT.cyan];
const root = new THREE.Group();
scene.add(root);

function cast(mesh, receive = true) {
  mesh.castShadow = true;
  mesh.receiveShadow = receive;
  return mesh;
}
function rb(w, h, d, mat, radius = 0.12, seg = 3) {
  return cast(new THREE.Mesh(new RoundedBoxGeometry(w, h, d, seg, radius), mat));
}
function cyl(r, h, mat, seg = 32) {
  return cast(new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat));
}
function sphere(r, mat, seg = 32) {
  return cast(new THREE.Mesh(new THREE.SphereGeometry(r, seg, Math.max(12, seg / 2)), mat));
}
function tube(points, radius, mat, tubular = 24, radial = 8) {
  const curve = new THREE.CatmullRomCurve3(points);
  return cast(new THREE.Mesh(new THREE.TubeGeometry(curve, tubular, radius, radial, false), mat));
}
function cone(r, h, mat, seg = 24) {
  return cast(new THREE.Mesh(new THREE.ConeGeometry(r, h, seg), mat));
}
function labelTexture(text, fg = '#f8db7c', bg = 'rgba(9,18,43,.92)', sub = '') {
  const c = document.createElement('canvas'); c.width = 512; c.height = 256;
  const x = c.getContext('2d');
  const g = x.createLinearGradient(0, 0, 512, 256); g.addColorStop(0, bg); g.addColorStop(1, 'rgba(20,42,89,.94)');
  x.fillStyle = g; x.fillRect(0, 0, 512, 256);
  x.strokeStyle = 'rgba(255,220,125,.75)'; x.lineWidth = 10; x.strokeRect(8, 8, 496, 240);
  x.textAlign = 'center'; x.textBaseline = 'middle';
  x.fillStyle = fg; x.font = '900 58px system-ui,-apple-system,PingFang SC,sans-serif'; x.fillText(text, 256, 112);
  if (sub) { x.fillStyle = '#8feaff'; x.font = '700 26px system-ui,-apple-system,sans-serif'; x.fillText(sub, 256, 174); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
function iconTexture(icon, color = '#ffffff') {
  const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d');
  x.clearRect(0,0,256,256); x.textAlign='center'; x.textBaseline='middle'; x.fillStyle=color;
  x.font='900 132px system-ui,-apple-system,Segoe UI Symbol,sans-serif'; x.fillText(icon,128,132);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
}
function screenPanel(w, h, text, sub, color = '#ffe077') {
  const m = new THREE.MeshStandardMaterial({ map: labelTexture(text, color, 'rgba(7,16,39,.96)', sub), emissive: 0x163a66, emissiveIntensity: .25, metalness: .15, roughness: .34 });
  return cast(new THREE.Mesh(new THREE.PlaneGeometry(w, h), m), false);
}

// Lighting rig
scene.add(new THREE.HemisphereLight(0x8bc9ff, 0x1e0e2a, 1.55));
const key = new THREE.DirectionalLight(0xffd89a, 5.1); key.position.set(-8, 14, 10); key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.camera.left=-16;key.shadow.camera.right=16;key.shadow.camera.top=16;key.shadow.camera.bottom=-16; scene.add(key);
const rim = new THREE.SpotLight(0x3de7ff, 115, 38, Math.PI / 4.2, .58, 1.1); rim.position.set(10, 10, -9); rim.target.position.set(0,1,0); scene.add(rim, rim.target);
const magenta = new THREE.PointLight(0xb14cff, 38, 28, 1.8); magenta.position.set(-8, 5, -7); scene.add(magenta);
const warmFront = new THREE.PointLight(0xffb447, 34, 24, 1.8); warmFront.position.set(-4, 4, 9); scene.add(warmFront);

// Ground / platform
const ground = new THREE.Mesh(new THREE.CircleGeometry(25, 80), new THREE.MeshStandardMaterial({ color: 0x040713, roughness: .72, metalness: .1 })); ground.rotation.x=-Math.PI/2; ground.position.y=-.72; ground.receiveShadow=true; root.add(ground);
const underGlow = new THREE.Mesh(new THREE.RingGeometry(8.3, 10.8, 64), new THREE.MeshBasicMaterial({ color: 0x1c7ba8, transparent:true, opacity:.12, side:THREE.DoubleSide })); underGlow.rotation.x=-Math.PI/2; underGlow.position.y=-.69; root.add(underGlow);

const board = rb(15.5, .86, 15.5, MAT.lacquer, .55, 5); board.position.y=-.12; root.add(board);
const boardTop = rb(14.85, .25, 14.85, new THREE.MeshPhysicalMaterial({ color:0x101c3d, metalness:.32, roughness:.25, clearcoat:.9 }), .48, 5); boardTop.position.y=.42; root.add(boardTop);
const centerInset = rb(8.15, .36, 8.15, new THREE.MeshPhysicalMaterial({ color:0x071126, metalness:.42, roughness:.28, clearcoat:.8 }), .72, 5); centerInset.position.y=.64; root.add(centerInset);

// Gold edge rails
for (const [x,z,w,d] of [[0,-7.12,13.6,.13],[0,7.12,13.6,.13],[-7.12,0,.13,13.6],[7.12,0,.13,13.6]]) {
  const rail=rb(w,.12,d,MAT.goldBright,.05,2);rail.position.set(x,.86,z);root.add(rail);
}
for (const [x,z] of [[-7.12,-7.12],[7.12,-7.12],[7.12,7.12],[-7.12,7.12]]) {
  const cap=cyl(.32,.2,MAT.goldBright,24);cap.position.set(x,.86,z);root.add(cap);
}

function perimeterPositions() {
  const a=[]; const xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4]; const zs=[-3.6,-1.8,0,1.8,3.6];
  xs.forEach(x=>a.push([x,-5.4]));
  zs.forEach(z=>a.push([5.4,z]));
  [...xs].reverse().forEach(x=>a.push([x,5.4]));
  [...zs].reverse().forEach(z=>a.push([-5.4,z]));
  return a;
}
const tilePos = perimeterPositions();
const icons=['₿','Ξ','↗','⚙','◆','◎','₿','⇧','◈','☁','★','↘','◉','Ξ','⚡','◇','₿','⇄','⬡','▲','◎','✦','⚙','◈'];
const tiles=[];
tilePos.forEach(([x,z],i)=>{
  const g=new THREE.Group();g.position.set(x,.68,z);
  const base=rb(1.62,.24,1.62,MAT.gold,.18,3);base.position.y=.03;g.add(base);
  const top=rb(1.47,.27,1.47,tileMats[i%tileMats.length],.16,3);top.position.y=.22;g.add(top);
  const iconMat=new THREE.MeshBasicMaterial({map:iconTexture(icons[i],i%3===0?'#ffe177':'#ffffff'),transparent:true,depthWrite:false});
  const badge=new THREE.Mesh(new THREE.PlaneGeometry(.66,.66),iconMat);badge.rotation.x=-Math.PI/2;badge.position.y=.37;g.add(badge);
  const owner=new THREE.Mesh(new THREE.TorusGeometry(.62,.035,8,32),new THREE.MeshBasicMaterial({color:i%4===0?0xffd760:0x54dfff,transparent:true,opacity:.48}));owner.rotation.x=Math.PI/2;owner.position.y=.39;g.add(owner);
  g.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});root.add(g);tiles.push(g);
});

// Central stage
const stage=new THREE.Group();stage.position.y=.86;root.add(stage);
const p0=cyl(3.45,.34,MAT.darkMetal,64);p0.position.y=.12;stage.add(p0);
const p1=cyl(2.95,.28,MAT.gold,64);p1.position.y=.4;stage.add(p1);
const p2=cyl(2.72,.32,MAT.lacquer,64);p2.position.y=.66;stage.add(p2);
const stageRing=new THREE.Mesh(new THREE.TorusGeometry(2.38,.08,10,64),new THREE.MeshStandardMaterial({color:0x67eaff,emissive:0x1687b5,emissiveIntensity:1.4,metalness:.25,roughness:.2}));stageRing.rotation.x=Math.PI/2;stageRing.position.y=.88;stage.add(stageRing);

const globeGroup=new THREE.Group();globeGroup.position.y=1.92;stage.add(globeGroup);
const globe=sphere(1.25,MAT.cyanGlass,36);globe.castShadow=false;globeGroup.add(globe);
for(let i=0;i<3;i++){const r=new THREE.Mesh(new THREE.TorusGeometry(1.34,.025,8,72),new THREE.MeshBasicMaterial({color:i===0?0x67efff:0xbe72ff,transparent:true,opacity:.7}));r.rotation.set(i===0?Math.PI/2:Math.PI/2+i*.55,i*.8,0);globeGroup.add(r)}
for(let i=0;i<18;i++){
  const a=(i/18)*Math.PI*2;const h=.18+((i*7)%6)*.09;const m=i%3===0?MAT.green:(i%4===0?MAT.red:MAT.cyan);
  const bar=rb(.09,h,.09,m,.025,2);bar.position.set(Math.cos(a)*1.72,.25+Math.sin(i*.7)*.12,Math.sin(a)*1.72);bar.rotation.y=-a;globeGroup.add(bar);
}

const sign=new THREE.Group();sign.position.set(0,3.55,.45);stage.add(sign);
const signFrame=rb(5.15,1.35,.42,MAT.goldBright,.2,4);sign.add(signFrame);
const signFace=screenPanel(4.62,1.02,'币圈大富翁','CRYPTO TYCOON','#ffe692');signFace.position.set(0,0,.225);sign.add(signFace);
const crownBase=rb(1.46,.22,.38,MAT.goldBright,.09,3);crownBase.position.set(0,.88,.03);sign.add(crownBase);
for(let i=-2;i<=2;i++){const spike=cone(.19,i===0?.7:(Math.abs(i)===1?.57:.44),MAT.goldBright,18);spike.position.set(i*.29,1.18+(i===0?.12:0),.02);sign.add(spike)}

// Landmarks
function exchangeTower(){
  const g=new THREE.Group();
  const base=rb(1.24,.18,1.24,MAT.gold,.14,3);base.position.y=.09;g.add(base);
  const body=rb(.94,2.45,.94,new THREE.MeshPhysicalMaterial({color:0x182d5a,metalness:.55,roughness:.2,clearcoat:.75}),.12,3);body.position.y=1.38;g.add(body);
  for(let y=.45;y<2.45;y+=.36){const strip=rb(.99,.06,.99,MAT.cyan,.025,2);strip.position.y=y;g.add(strip)}
  const roof=cone(.72,.62,MAT.goldBright,4);roof.rotation.y=Math.PI/4;roof.position.y=2.92;g.add(roof);
  const coin=cyl(.27,.08,MAT.goldBright,32);coin.rotation.x=Math.PI/2;coin.position.set(0,2.12,.51);g.add(coin);
  const coinMark=new THREE.Mesh(new THREE.PlaneGeometry(.3,.3),new THREE.MeshBasicMaterial({map:iconTexture('₿','#2b1b03'),transparent:true}));coinMark.position.set(0,2.12,.56);g.add(coinMark);
  return g;
}
function bullSculpture(){
  const g=new THREE.Group(); const pedestal=rb(1.35,.23,1.15,MAT.gold,.13,3);pedestal.position.y=.12;g.add(pedestal);
  const body=sphere(.58,new THREE.MeshPhysicalMaterial({color:0x593728,roughness:.34,clearcoat:.36}),24);body.scale.set(1.32,.76,.72);body.position.set(0,.82,0);g.add(body);
  const chest=sphere(.42,new THREE.MeshPhysicalMaterial({color:0x6c4430,roughness:.32,clearcoat:.4}),24);chest.scale.set(.9,1.1,.85);chest.position.set(0,.95,.34);g.add(chest);
  const head=sphere(.42,new THREE.MeshPhysicalMaterial({color:0x7b5239,roughness:.36,clearcoat:.3}),24);head.scale.set(.9,.9,.82);head.position.set(0,1.42,.55);g.add(head);
  const muzzle=sphere(.24,MAT.cream,20);muzzle.scale.set(1.05,.58,.85);muzzle.position.set(0,1.28,.86);g.add(muzzle);
  for(const s of [-1,1]){
    const horn=tube([new THREE.Vector3(s*.26,1.63,.58),new THREE.Vector3(s*.52,1.83,.57),new THREE.Vector3(s*.72,1.83,.46),new THREE.Vector3(s*.82,1.67,.36)],.075,MAT.ivory,22,8);g.add(horn);
    const leg=rb(.22,.62,.22,new THREE.MeshPhysicalMaterial({color:0x4f3025,roughness:.38}),.09,3);leg.position.set(s*.34,.48,s>.0?.16:-.18);g.add(leg);
    const ear=cone(.12,.34,new THREE.MeshPhysicalMaterial({color:0x69432f,roughness:.36}),12);ear.rotation.z=s*.7;ear.position.set(s*.35,1.63,.55);g.add(ear);
  }
  const glasses=rb(.65,.12,.08,MAT.black,.04,2);glasses.position.set(0,1.47,.9);g.add(glasses);
  const arrow=tube([new THREE.Vector3(-.55,.32,-.55),new THREE.Vector3(-.15,.58,-.38),new THREE.Vector3(.18,.72,-.12),new THREE.Vector3(.62,1.05,.04)],.06,MAT.green,20,8);g.add(arrow);
  return g;
}
function bearSculpture(){
  const g=new THREE.Group();const p=rb(1.3,.22,1.12,MAT.gold,.12,3);p.position.y=.11;g.add(p);
  const body=sphere(.62,new THREE.MeshPhysicalMaterial({color:0x392a32,roughness:.52,clearcoat:.1}),24);body.scale.set(.9,1.1,.76);body.position.y=.92;g.add(body);
  const head=sphere(.45,new THREE.MeshPhysicalMaterial({color:0x46323a,roughness:.5}),24);head.position.set(0,1.65,.22);g.add(head);
  for(const s of [-1,1]){const ear=sphere(.16,new THREE.MeshPhysicalMaterial({color:0x4b343e,roughness:.48}),16);ear.position.set(s*.31,1.96,.14);g.add(ear);const arm=rb(.22,.7,.26,new THREE.MeshPhysicalMaterial({color:0x3b2b34,roughness:.5}),.11,3);arm.position.set(s*.48,1.05,.18);arm.rotation.z=s*.28;g.add(arm)}
  const muzzle=sphere(.24,MAT.cream,20);muzzle.scale.set(1,.6,.75);muzzle.position.set(0,1.56,.56);g.add(muzzle);
  const arrow=tube([new THREE.Vector3(-.6,1.18,-.44),new THREE.Vector3(-.18,.95,-.32),new THREE.Vector3(.2,.68,-.2),new THREE.Vector3(.6,.38,-.05)],.06,MAT.red,20,8);g.add(arrow);
  return g;
}
function whaleLandmark(){
  const g=new THREE.Group();const base=cyl(.82,.18,MAT.gold,40);base.position.y=.09;g.add(base);
  const water=cyl(.72,.12,new THREE.MeshStandardMaterial({color:0x1b8eb6,roughness:.24,emissive:0x075b78,emissiveIntensity:.35}),40);water.position.y=.23;g.add(water);
  const body=sphere(.58,new THREE.MeshPhysicalMaterial({color:0x4aa9d4,roughness:.3,clearcoat:.55}),28);body.scale.set(1.35,.68,.72);body.position.set(0,.9,0);body.rotation.y=-.28;g.add(body);
  const belly=sphere(.46,new THREE.MeshPhysicalMaterial({color:0xb8e8f0,roughness:.42}),24);belly.scale.set(1.18,.42,.55);belly.position.set(.05,.68,.34);g.add(belly);
  for(const s of [-1,1]){const fin=cone(.2,.65,new THREE.MeshPhysicalMaterial({color:0x3f91bd,roughness:.34}),3);fin.rotation.set(0,0,s*1.1);fin.position.set(s*.48,.72,.08);g.add(fin)}
  const tail1=cone(.24,.58,new THREE.MeshPhysicalMaterial({color:0x3f91bd,roughness:.34}),3);tail1.rotation.set(0,0,1.0);tail1.position.set(-.78,.9,-.05);g.add(tail1);
  const tail2=tail1.clone();tail2.rotation.z=-1.0;tail2.position.x=-.9;g.add(tail2);
  const eye=sphere(.045,MAT.black,12);eye.position.set(.55,1.03,.42);g.add(eye);
  const badge=cyl(.23,.08,MAT.goldBright,28);badge.rotation.x=Math.PI/2;badge.position.set(.25,.94,.55);g.add(badge);
  return g;
}
function rocketLandmark(){
  const g=new THREE.Group();const base=rb(1.25,.22,1.25,MAT.gold,.12,3);base.position.y=.11;g.add(base);
  const gantry=rb(.14,2.1,.14,MAT.darkMetal,.04,2);gantry.position.set(-.48,1.2,-.2);g.add(gantry);
  for(let y=.45;y<2.05;y+=.38){const cross=rb(.65,.08,.08,MAT.darkMetal,.025,2);cross.position.set(-.2,y,-.2);g.add(cross)}
  const body=cyl(.28,1.45,MAT.ivory,28);body.position.set(.2,1.27,.08);g.add(body);
  const nose=cone(.29,.58,MAT.red,28);nose.position.set(.2,2.28,.08);g.add(nose);
  const window=sphere(.13,MAT.cyanGlass,18);window.scale.z=.4;window.position.set(.2,1.52,.35);g.add(window);
  for(const s of [-1,1]){const fin=cone(.18,.52,MAT.red,3);fin.rotation.z=s*.42;fin.position.set(.2+s*.28,.7,.08);g.add(fin)}
  const plume=cone(.34,.82,new THREE.MeshStandardMaterial({color:0xff8b39,emissive:0xff4b12,emissiveIntensity:1.6,transparent:true,opacity:.72}),24);plume.rotation.x=Math.PI;plume.position.set(.2,.15,.08);g.add(plume);
  return g;
}
function vaultLandmark(){
  const g=new THREE.Group();const base=rb(1.35,.2,1.2,MAT.gold,.13,3);base.position.y=.1;g.add(base);
  const safe=rb(1.04,1.35,.75,new THREE.MeshPhysicalMaterial({color:0x27375a,metalness:.7,roughness:.24,clearcoat:.45}),.16,4);safe.position.set(0,.88,0);g.add(safe);
  const door=cyl(.4,.1,MAT.darkMetal,36);door.rotation.x=Math.PI/2;door.position.set(0,.95,.43);g.add(door);
  const wheel=new THREE.Mesh(new THREE.TorusGeometry(.24,.045,8,32),MAT.goldBright);wheel.position.set(0,.95,.49);g.add(wheel);
  for(let i=0;i<6;i++){const spoke=rb(.04,.32,.04,MAT.goldBright,.02,2);spoke.position.set(0,.95,.5);spoke.rotation.z=i*Math.PI/3;g.add(spoke)}
  for(let i=0;i<3;i++){const coin=cyl(.18,.1,MAT.goldBright,28);coin.position.set(.52+i*.03,.25+i*.11,.12);g.add(coin)}
  const yld=screenPanel(.72,.38,'12.8%','STAKING','#77f6a5');yld.position.set(0,1.72,.05);g.add(yld);
  return g;
}
function nftGallery(){
  const g=new THREE.Group();const base=rb(1.3,.2,1.05,MAT.gold,.12,3);base.position.y=.1;g.add(base);
  const frame=rb(.95,1.28,.18,MAT.goldBright,.08,3);frame.position.set(0,.95,0);g.add(frame);
  const pic=screenPanel(.78,1.02,'NFT','PIXEL CLUB','#ff8ff7');pic.position.set(0,.96,.105);g.add(pic);
  const spot=new THREE.SpotLight(0xd56bff,18,5,Math.PI/5,.7,1.5);spot.position.set(0,2.1,.6);spot.target.position.set(0,.9,0);g.add(spot,spot.target);
  return g;
}
function miningRig(){
  const g=new THREE.Group();const base=rb(1.45,.2,1.15,MAT.gold,.12,3);base.position.y=.1;g.add(base);
  for(let r=0;r<2;r++)for(let c=0;c<3;c++){
    const gpu=rb(.38,.38,.16,MAT.darkMetal,.05,2);gpu.position.set((c-1)*.42,.55+r*.48,0);g.add(gpu);
    const fan=cyl(.12,.04,MAT.cyan,18);fan.rotation.x=Math.PI/2;fan.position.set((c-1)*.42,.55+r*.48,.11);g.add(fan);
  }
  for(const s of [-1,1]){const post=rb(.08,1.2,.08,MAT.gold,.025,2);post.position.set(s*.66,.72,0);g.add(post)}
  return g;
}

function placeLandmark(obj,index,scale=1){const [x,z]=tilePos[index];obj.position.set(x,.97,z);obj.scale.setScalar(scale);root.add(obj);return obj}
const landmarks=[];
landmarks.push(placeLandmark(exchangeTower(),2,.92));
landmarks.push(placeLandmark(rocketLandmark(),5,.9));
landmarks.push(placeLandmark(bullSculpture(),9,.88));
landmarks.push(placeLandmark(whaleLandmark(),12,.9));
landmarks.push(placeLandmark(bearSculpture(),16,.85));
landmarks.push(placeLandmark(vaultLandmark(),19,.92));
landmarks.push(placeLandmark(nftGallery(),21,.92));
landmarks.push(placeLandmark(miningRig(),23,.88));

// Character tokens
function tokenBase(color){const g=new THREE.Group();const base=cyl(.52,.17,new THREE.MeshPhysicalMaterial({color,metalness:.48,roughness:.18,clearcoat:.9,emissive:color,emissiveIntensity:.1}),32);base.position.y=.085;g.add(base);const ring=new THREE.Mesh(new THREE.TorusGeometry(.43,.045,8,32),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.8}));ring.rotation.x=Math.PI/2;ring.position.y=.19;g.add(ring);return g}
function astronaut(){const g=tokenBase(0xffca54);const torso=rb(.46,.68,.35,MAT.ivory,.14,4);torso.position.y=.72;g.add(torso);const belt=rb(.5,.09,.38,MAT.gold,.04,2);belt.position.y=.58;g.add(belt);const helmet=sphere(.38,MAT.ivory,28);helmet.position.y=1.32;g.add(helmet);const visor=sphere(.31,MAT.glassDark,24);visor.scale.set(1,.82,.52);visor.position.set(0,1.32,.2);g.add(visor);const pack=rb(.34,.52,.2,MAT.darkMetal,.08,3);pack.position.set(0,.78,-.27);g.add(pack);for(const s of [-1,1]){const arm=rb(.14,.52,.14,MAT.ivory,.07,3);arm.position.set(s*.34,.76,.02);arm.rotation.z=s*.22;g.add(arm);const leg=rb(.17,.46,.17,MAT.ivory,.08,3);leg.position.set(s*.15,.3,.02);g.add(leg)}return g}
function doge(){const g=tokenBase(0xff7b5a);const body=sphere(.36,new THREE.MeshPhysicalMaterial({color:0xd79b55,roughness:.42,clearcoat:.28}),24);body.scale.set(.85,1.15,.72);body.position.y=.68;g.add(body);const head=sphere(.36,new THREE.MeshPhysicalMaterial({color:0xe0a65f,roughness:.4,clearcoat:.26}),24);head.position.set(0,1.23,.07);g.add(head);const muzzle=sphere(.19,MAT.cream,18);muzzle.scale.set(1,.62,.8);muzzle.position.set(0,1.15,.37);g.add(muzzle);for(const s of [-1,1]){const ear=cone(.16,.4,new THREE.MeshPhysicalMaterial({color:0xb8733f,roughness:.43}),12);ear.rotation.z=s*.25;ear.position.set(s*.22,1.58,0);g.add(ear);const leg=rb(.16,.42,.16,new THREE.MeshPhysicalMaterial({color:0xc98649,roughness:.42}),.07,3);leg.position.set(s*.14,.28,.01);g.add(leg)}const glasses=rb(.55,.1,.08,MAT.black,.04,2);glasses.position.set(0,1.3,.38);g.add(glasses);const chain=new THREE.Mesh(new THREE.TorusGeometry(.22,.04,8,28),MAT.goldBright);chain.position.set(0,.78,.31);g.add(chain);return g}
function cyber(){const g=tokenBase(0x6e9bff);const torso=rb(.48,.7,.38,MAT.purple,.08,3);torso.position.y=.7;g.add(torso);const head=rb(.46,.43,.42,new THREE.MeshPhysicalMaterial({color:0xe7a685,roughness:.34,clearcoat:.32}),.06,3);head.position.y=1.25;g.add(head);const visor=rb(.5,.11,.06,MAT.cyan,.025,2);visor.position.set(0,1.29,.24);g.add(visor);for(let i=0;i<5;i++){const h=rb(.07,.23,.08,i%2?MAT.cyan:MAT.magenta,.02,2);h.position.set(-.18+i*.09,1.58,(i%2)*.03);g.add(h)}for(const s of [-1,1]){const arm=rb(.14,.5,.14,MAT.darkMetal,.05,2);arm.position.set(s*.34,.72,0);g.add(arm);const leg=rb(.16,.44,.16,MAT.darkMetal,.05,2);leg.position.set(s*.14,.29,0);g.add(leg)}return g}
function bullToken(){const g=tokenBase(0x55e58c);const body=sphere(.38,new THREE.MeshPhysicalMaterial({color:0x65412f,roughness:.4,clearcoat:.24}),24);body.scale.set(.85,1.1,.78);body.position.y=.69;g.add(body);const head=sphere(.34,new THREE.MeshPhysicalMaterial({color:0x79503a,roughness:.38,clearcoat:.25}),24);head.position.set(0,1.24,.05);g.add(head);const muzzle=sphere(.19,MAT.cream,18);muzzle.scale.set(1,.6,.8);muzzle.position.set(0,1.14,.34);g.add(muzzle);for(const s of [-1,1]){const horn=tube([new THREE.Vector3(s*.2,1.46,.05),new THREE.Vector3(s*.35,1.62,.04),new THREE.Vector3(s*.48,1.58,-.02)],.055,MAT.ivory,14,7);g.add(horn);const leg=rb(.16,.44,.16,new THREE.MeshPhysicalMaterial({color:0x563628,roughness:.42}),.07,3);leg.position.set(s*.14,.29,0);g.add(leg)}const glasses=rb(.52,.1,.07,MAT.black,.035,2);glasses.position.set(0,1.28,.36);g.add(glasses);return g}
const tokens=[astronaut(),doge(),cyber(),bullToken()];
const tokenTiles=[17,10,13,20];
tokens.forEach((t,i)=>{const [x,z]=tilePos[tokenTiles[i]];t.position.set(x,.98,z);t.rotation.y=[.2,-.5,.35,-.2][i];t.scale.setScalar(.88);root.add(t)});

// Dice and foreground chips
function die(){const g=new THREE.Group();const b=rb(1.12,1.12,1.12,MAT.ivory,.22,5);g.add(b);const pipMat=new THREE.MeshStandardMaterial({color:0x34240c,metalness:.15,roughness:.32});const faces=[[[0,.57,0]],[[.57,.22,.22],[.57,-.22,-.22]],[[0,.22,.57],[0,0,.57],[0,-.22,.57]],[[-.57,.23,.23],[-.57,.23,-.23],[-.57,-.23,.23],[-.57,-.23,-.23]]];faces.forEach((pts,fi)=>pts.forEach(p=>{const q=sphere(.075,pipMat,12);q.position.set(...p);g.add(q)}));return g}
const dice=[die(),die()];dice[0].position.set(-1.2,1.22,5.45);dice[0].rotation.set(.3,.45,.16);dice[1].position.set(.15,1.15,5.7);dice[1].rotation.set(-.18,-.32,.26);root.add(...dice);
function coinStack(x,z,n=4){for(let i=0;i<n;i++){const c=cyl(.22,.08,MAT.goldBright,28);c.position.set(x+(i%2)*.03,.83+i*.075,z+(i%2)*.02);c.rotation.y=i*.35;root.add(c)}}
coinStack(-3.0,5.75,5);coinStack(2.9,5.55,4);coinStack(4.2,4.8,3);

// Skyline with depth variation
const skyline=new THREE.Group();root.add(skyline);
const rand=n=>{const x=Math.sin(n*91.173+17.7)*43758.5453;return x-Math.floor(x)};
function building(i,layer){
  const g=new THREE.Group();const w=.75+rand(i+layer*40)*1.25;const d=.7+rand(i+4)*.8;const h=1.8+rand(i+9+layer*10)*(layer===0?4.8:3.2);
  const mat=new THREE.MeshPhysicalMaterial({color:layer===0?0x112447:0x0b1730,metalness:.42,roughness:.32,clearcoat:.28});
  const b=rb(w,h,d,mat,.08,2);b.position.y=h/2;g.add(b);
  const crownType=i%3;
  if(crownType===0){const roof=cone(w*.44,.65,i%2?MAT.gold:MAT.cyan,4);roof.rotation.y=Math.PI/4;roof.position.y=h+.32;g.add(roof)}
  else if(crownType===1){const roof=rb(w*.66,.26,d*.74,MAT.darkMetal,.05,2);roof.position.y=h+.13;g.add(roof);const ant=rb(.04,.9,.04,MAT.cyan,.02,2);ant.position.y=h+.7;g.add(ant)}
  else {const roof=cyl(w*.28,.28,MAT.gold,20);roof.position.y=h+.14;g.add(roof)}
  const rows=Math.min(8,Math.floor(h/.46));for(let r=0;r<rows;r++){const strip=rb(w*.76,.035,d+.014,r%3===0?MAT.magenta:MAT.cyan,.01,1);strip.position.y=.42+r*.43;strip.position.z=d*.51;g.add(strip)}
  return g;
}
for(let layer=0;layer<3;layer++){
  const z=-9.4-layer*2.2;const count=layer===0?11:9;
  for(let i=0;i<count;i++){
    const g=building(i+layer*17,layer);const span=21;g.position.set(-span/2+(i/(count-1))*span,z+(rand(i+layer*5)-.5)*1.2,0); // temporary
    g.position.set(-10.5+(i/(count-1))*21,-.68,z+(rand(i+layer*7)-.5)*.7);g.scale.setScalar(layer===0?1:.78);skyline.add(g);
  }
}
// Side skyline pieces to avoid flat wall
for(let i=0;i<5;i++){const l=building(70+i,1);l.position.set(-10.6-i*.9,-.68,-5+i*.9);l.rotation.y=.35;skyline.add(l);const r=l.clone();r.position.x*=-1;r.rotation.y=-.35;skyline.add(r)}

// Market billboard
const billFrame=rb(4.3,2.15,.22,MAT.gold,.14,3);billFrame.position.set(-7.2,3.55,-9.0);billFrame.rotation.y=.16;root.add(billFrame);
const bill=screenPanel(3.95,1.83,'BTC  87,420','+7.2%  ▲  ETF FLOW','#82f6a9');bill.position.set(-7.2,3.55,-8.87);bill.rotation.y=.16;root.add(bill);

// Floating neon coins / symbols
for(const [x,y,z,t,c] of [[7.9,4.5,-8.5,'₿',0xffd45b],[9.2,2.7,-6.8,'Ξ',0x70e6ff],[-9.2,4.7,-7.6,'◆',0xcf71ff]]){
  const tex=iconTexture(t,'#ffffff');const m=new THREE.SpriteMaterial({map:tex,color:c,transparent:true,opacity:.78,depthWrite:false});const s=new THREE.Sprite(m);s.position.set(x,y,z);s.scale.set(1.4,1.4,1.4);root.add(s);
}

// Practical perimeter lights
for(let i=0;i<24;i+=2){const [x,z]=tilePos[i];const lamp=cyl(.055,.32,MAT.goldBright,12);lamp.position.set(x,.98,z);root.add(lamp);const glow=new THREE.PointLight(i%4===0?0x64e9ff:0xffc55a,2.6,2.4,2);glow.position.set(x,1.18,z);root.add(glow)}

// Resize
function resize(){
  const w=innerWidth,h=innerHeight;renderer.setSize(w,h,false);composer.setSize(w,h);camera.aspect=w/h;
  if(w/h<1.25){camera.position.set(15.8,14.8,20.8);camera.fov=38}else if(w/h<1.5){camera.position.set(14.3,13.6,19.1);camera.fov=36}else{camera.position.set(12.8,12.6,17.2);camera.fov=34}
  camera.updateProjectionMatrix();camera.lookAt(0,.75,0);
}
addEventListener('resize',resize,{passive:true});resize();

const clock=new THREE.Clock();let ready=false;
function animate(){
  const t=clock.getElapsedTime();
  globeGroup.rotation.y=t*.18;stageRing.rotation.z=t*.12;
  dice[0].rotation.y=.45+Math.sin(t*.7)*.08;dice[1].rotation.x=-.18+Math.sin(t*.64+1)*.06;
  tokens.forEach((g,i)=>{g.position.y=.98+Math.sin(t*1.5+i)*.025;g.rotation.y += .0018*(i%2?1:-1)});
  landmarks[3].rotation.y=Math.sin(t*.45)*.035;
  composer.render();
  if(!ready){ready=true;window.__cryptoSliceReady={version:'candidate-v1',referencePixelsUsed:false,tiles:24,landmarks:landmarks.length,tokens:tokens.length};document.documentElement.dataset.sliceReady='1'}
  requestAnimationFrame(animate);
}
animate();
