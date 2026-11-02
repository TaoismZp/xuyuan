import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

await import('./candidate-v6-augment.js');
const scene=window.__ctCapturedScene, root=window.__ctCapturedRoot;
if(!scene||!root) throw new Error('v7 scene missing');

const gold=new THREE.MeshPhysicalMaterial({color:0xf8c553,metalness:.78,roughness:.12,clearcoat:1,clearcoatRoughness:.05});
const goldLite=new THREE.MeshPhysicalMaterial({color:0xffe69c,metalness:.55,roughness:.12,clearcoat:1});
const navy=new THREE.MeshPhysicalMaterial({color:0x12234c,metalness:.44,roughness:.2,clearcoat:.82});
const dark=new THREE.MeshPhysicalMaterial({color:0x0e1833,metalness:.56,roughness:.25,clearcoat:.52});
const cyan=new THREE.MeshStandardMaterial({color:0x67edff,emissive:0x0e7595,emissiveIntensity:.74,metalness:.12,roughness:.2});
const purple=new THREE.MeshStandardMaterial({color:0xb76fff,emissive:0x541970,emissiveIntensity:.5,metalness:.08,roughness:.22});
const green=new THREE.MeshStandardMaterial({color:0x66ef9f,emissive:0x14683d,emissiveIntensity:.25,metalness:.08,roughness:.24});
const red=new THREE.MeshPhysicalMaterial({color:0xff777b,metalness:.08,roughness:.25,clearcoat:.7});

function cast(m,receive=true){m.castShadow=true;m.receiveShadow=receive;return m}
function rb(w,h,d,mat,r=.1,s=3){return cast(new THREE.Mesh(new RoundedBoxGeometry(w,h,d,s,r),mat))}
function cyl(r,h,mat,s=32){return cast(new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),mat))}
function sph(r,mat,s=24){return cast(new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(12,s/2)),mat))}
function cone(r,h,mat,s=20){return cast(new THREE.Mesh(new THREE.ConeGeometry(r,h,s),mat))}
function texPlane(w,h,texture){const m=new THREE.MeshBasicMaterial({map:texture,transparent:true,alphaTest:.01,toneMapped:false,side:THREE.DoubleSide});const p=new THREE.Mesh(new THREE.PlaneGeometry(w,h),m);p.renderOrder=20;return p}

function logoTexture(){
 const c=document.createElement('canvas');c.width=1900;c.height=620;const x=c.getContext('2d');x.clearRect(0,0,c.width,c.height);
 x.textAlign='center';x.textBaseline='middle';x.lineJoin='round';
 x.shadowColor='rgba(255,158,20,.72)';x.shadowBlur=36;
 x.font='1000 285px "Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif';
 x.lineWidth=52;x.strokeStyle='#5f2a08';x.strokeText('币圈大富翁',950,294);
 const g=x.createLinearGradient(0,110,0,430);g.addColorStop(0,'#fff9cf');g.addColorStop(.2,'#ffe993');g.addColorStop(.58,'#f9bc37');g.addColorStop(1,'#d47d08');x.fillStyle=g;x.fillText('币圈大富翁',950,294);
 x.shadowBlur=0;x.lineWidth=8;x.strokeStyle='rgba(255,250,211,.72)';x.strokeText('币圈大富翁',950,294);
 x.font='900 58px Arial,sans-serif';x.fillStyle='#fff1bd';x.fillText('CRYPTO TYCOON · SURVIVE THE CYCLE',950,520);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}
function signTexture(title,sub,accent='#ffe078'){
 const c=document.createElement('canvas');c.width=900;c.height=450;const x=c.getContext('2d');
 const bg=x.createLinearGradient(0,0,0,450);bg.addColorStop(0,'#0a1736');bg.addColorStop(1,'#132c5a');x.fillStyle=bg;x.fillRect(0,0,900,450);x.strokeStyle=accent;x.lineWidth=18;x.strokeRect(14,14,872,422);
 x.textAlign='center';x.textBaseline='middle';x.fillStyle=accent;x.font='1000 108px "Noto Sans CJK SC","PingFang SC",Arial,sans-serif';x.fillText(title,450,180);x.fillStyle='#e8f2ff';x.font='800 42px "Noto Sans CJK SC","PingFang SC",Arial,sans-serif';x.fillText(sub,450,310);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;
}

// 1) Stop-work correction: hide the two opaque center monuments that competed with the market stage.
let hiddenCenterGroups=0;
for(const o of root.children){
 if(!o.isGroup) continue;
 const b=new THREE.Box3().setFromObject(o);if(b.isEmpty())continue;const size=new THREE.Vector3(),center=new THREE.Vector3();b.getSize(size);b.getCenter(center);
 if(size.x>5.1 && size.y>1.25 && center.y>3.1 && center.z>0.35 && center.z<3.2){o.visible=false;hiddenCenterGroups++}
}

// 2) Replace the wall-like plaque with an open logo crest: transparent text + physical crown/laurel only.
const crest=new THREE.Group();root.add(crest);
const logo=texPlane(7.15,2.25,logoTexture());logo.position.set(0,3.62,2.02);crest.add(logo);
const crownRing=new THREE.Mesh(new THREE.TorusGeometry(.72,.105,10,48),gold);crownRing.rotation.x=Math.PI/2;crownRing.scale.y=.58;crownRing.position.set(0,4.83,1.97);crest.add(crownRing);
for(let i=-2;i<=2;i++){const s=cone(.15,i===0?.86:(Math.abs(i)===1?.7:.54),goldLite,16);s.position.set(i*.28,5.2+(i===0?.12:0),1.95);crest.add(s)}
for(const side of [-1,1]) for(let i=0;i<8;i++){const leaf=cone(.095,.42,goldLite,5);leaf.rotation.z=side*(.94-i*.065);leaf.position.set(side*(3.42+i*.12),2.83+i*.15,1.94);crest.add(leaf)}
const crestGlow=new THREE.PointLight(0xffc55e,4.4,8,2);crestGlow.position.set(0,4.0,4.0);root.add(crestGlow);

// 3) Suppress repetitive skyline mass instead of piling more boxes behind it.
const skyline=root.children.find(o=>o.isGroup && o.children.filter(c=>c.isGroup).length>=15);
let skylineHidden=0;
if(skyline){skyline.children.forEach((b,i)=>{if(i%3===1 || i%5===2){b.visible=false;skylineHidden++}})}

function facadeMat(color){return new THREE.MeshPhysicalMaterial({color,metalness:.52,roughness:.2,clearcoat:.6})}
function signatureTower(kind){
 const g=new THREE.Group();
 if(kind==='exchange'){
  const b=rb(2.25,.34,1.75,gold,.14,4);b.position.y=.17;g.add(b);
  const core=rb(1.78,3.5,1.32,facadeMat(0x17366b),.12,3);core.position.y=2.05;g.add(core);
  for(let y=.55;y<3.65;y+=.48){const strip=rb(1.94,.07,1.38,y%1>.5?cyan:purple,.02,1);strip.position.y=y;g.add(strip)}
  const shoulder=rb(1.42,1.55,1.08,facadeMat(0x21487d),.1,3);shoulder.position.y=4.2;g.add(shoulder);const roof=cone(.9,.86,goldLite,4);roof.rotation.y=Math.PI/4;roof.position.y=5.42;g.add(roof);
  const frame=rb(2.15,.88,.16,gold,.08,3);frame.position.set(0,2.65,.77);g.add(frame);const sign=texPlane(1.92,.68,signTexture('交易所','买卖 · 交易 · 上市'));sign.position.set(0,2.65,.86);g.add(sign);
 }
 if(kind==='btc'){
  const base=cyl(1.05,.28,gold,42);base.position.y=.14;g.add(base);const stem=cyl(.72,2.75,navy,42);stem.position.y=1.52;g.add(stem);
  const halo=new THREE.Mesh(new THREE.TorusGeometry(1.18,.085,10,56),cyan);halo.position.set(0,3.15,.18);g.add(halo);const coin=cyl(.75,.13,goldLite,48);coin.rotation.x=Math.PI/2;coin.position.set(0,3.15,.2);g.add(coin);const f=texPlane(1.04,1.04,signTexture('₿','','#5b3106'));f.position.set(0,3.15,.3);g.add(f);
 }
 if(kind==='eth'){
  const base=rb(1.72,.3,1.48,gold,.13,3);base.position.y=.15;g.add(base);const stem=rb(1.16,3.25,1.0,facadeMat(0x17366a),.1,3);stem.position.y=1.9;g.add(stem);
  const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.86,0),new THREE.MeshPhysicalMaterial({color:0xa5e9ff,metalness:.16,roughness:.06,transmission:.25,transparent:true,opacity:.93,emissive:0x3368bb,emissiveIntensity:.52,clearcoat:1}));gem.scale.y=1.42;gem.position.y=4.45;gem.castShadow=true;g.add(gem);const ring=new THREE.Mesh(new THREE.TorusGeometry(1.08,.065,8,48),purple);ring.rotation.x=Math.PI/2;ring.position.y=4.45;g.add(ring);
 }
 return g;
}
const ex=signatureTower('exchange');ex.position.set(-7.9,-.68,-8.25);ex.scale.setScalar(1.08);ex.rotation.y=.08;root.add(ex);
const btc=signatureTower('btc');btc.position.set(8.8,-.68,-6.85);btc.rotation.y=-.18;root.add(btc);
const eth=signatureTower('eth');eth.position.set(6.5,-.68,-9.3);root.add(eth);

// 4) Add one close finance terminal to establish a designed midground rather than a flat wall.
const terminalFrame=rb(4.45,2.35,.22,gold,.14,4);terminalFrame.position.set(-5.8,4.9,-8.75);terminalFrame.rotation.y=.14;root.add(terminalFrame);
const terminal=texPlane(4.12,2.04,signTexture('BTC 87,420','▲ +7.2% · ETF FLOW +12%','#78efac'));terminal.position.set(-5.8,4.9,-8.61);terminal.rotation.y=.14;root.add(terminal);

// 5) Upgrade the four existing tokens with differentiated collectible accessories rather than generic glow.
function perimeterPositions(){const a=[],xs=[-5.4,-3.6,-1.8,0,1.8,3.6,5.4],zs=[-3.6,-1.8,0,1.8,3.6];xs.forEach(x=>a.push([x,-5.4]));zs.forEach(z=>a.push([5.4,z]));[...xs].reverse().forEach(x=>a.push([x,5.4]));[...zs].reverse().forEach(z=>a.push([-5.4,z]));return a}
const pos=perimeterPositions(), tokenIndices=[17,10,13,20];let upgradedTokens=0;
for(let i=0;i<tokenIndices.length;i++){
 const [x,z]=pos[tokenIndices[i]];let best=null,bd=1e9;
 for(const o of root.children){if(!o.isGroup||o.position.y<.75||o.position.y>1.2)continue;const d=(o.position.x-x)**2+(o.position.z-z)**2;if(d<bd){bd=d;best=o}}
 if(!best||bd>.3)continue;
 best.scale.multiplyScalar(1.075);
 if(i===0){const ring=new THREE.Mesh(new THREE.TorusGeometry(.34,.035,8,32),cyan);ring.position.set(0,1.34,.24);ring.scale.y=.8;best.add(ring);const antenna=rb(.035,.34,.035,goldLite,.015,1);antenna.position.set(.2,1.68,0);antenna.rotation.z=-.22;best.add(antenna);const tip=sph(.055,cyan,12);tip.position.set(.24,1.85,0);best.add(tip)}
 if(i===1){for(let k=-1;k<=1;k++){const c=cone(.09,k===0?.34:.25,goldLite,10);c.position.set(k*.11,1.61,0);best.add(c)}const med=cyl(.12,.045,goldLite,20);med.rotation.x=Math.PI/2;med.position.set(0,.86,.39);best.add(med)}
 if(i===2){for(let k=0;k<6;k++){const h=rb(.055,.32,.065,k%2?cyan:purple,.015,1);h.position.set(-.17+k*.07,1.67,(k%2)*.03);best.add(h)}const shoulderL=rb(.18,.14,.24,purple,.05,2);shoulderL.position.set(-.34,.85,0);best.add(shoulderL);const shoulderR=shoulderL.clone();shoulderR.position.x=.34;best.add(shoulderR)}
 if(i===3){for(const s of [-1,1]){const horn=cone(.09,.52,goldLite,12);horn.rotation.z=s*.78;horn.position.set(s*.36,1.54,.04);best.add(horn)}const jacket=rb(.56,.34,.38,red,.1,3);jacket.position.set(0,.68,-.03);best.add(jacket)}
 upgradedTokens++;
}

// 6) Fix value balance: remove hot local spots, then add controlled broad fill.
scene.traverse(o=>{if(o.isPointLight && o.position.y<3.6 && o.intensity>4)o.intensity*=.52});
scene.add(new THREE.HemisphereLight(0xd9ebff,0x33233d,.18));
const broadKey=new THREE.DirectionalLight(0xffe5b5,.48);broadKey.position.set(-3,11,8);scene.add(broadKey);
const cityFill=new THREE.PointLight(0x6eeaff,2.4,18,2);cityFill.position.set(0,6,-6);scene.add(cityFill);

window.__cryptoSliceReady={...window.__cryptoSliceReady,version:'candidate-v7',referencePixelsUsed:false,constructionProtocol:'wish-delivery-v7.4',hiddenCenterGroups,skylineHidden,signatureHeroStructures:3,upgradedTokens,openCenterCrest:true};
document.documentElement.dataset.sliceVersion='v7';
document.documentElement.dataset.sliceReady='1';
