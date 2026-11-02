import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/+esm';
import k0 from './keyart-chunk-0.js';
import k1 from './keyart-chunk-1.js';
import k2 from './keyart-chunk-2.js';
import k3 from './keyart-chunk-3.js';

const TEST=new URLSearchParams(location.search).get('test')==='1';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<400&&!window.__chainTycoon3d;i++) await sleep(25);
const game=window.__chainTycoon3d;
if(!game) throw new Error('game engine unavailable');

const bg=document.querySelector('#keyArtLayer');
const canvas=document.querySelector('#overlayScene');
if(!bg||!canvas) throw new Error('visual v3 surface missing');

const b64=(k0+k1+k2+k3).replace(/\s+/g,'');
if(b64.length!==90124) throw new Error(`key art chunk length mismatch: ${b64.length} !== 90124`);
if(!/^[A-Za-z0-9+/]+={0,2}$/.test(b64)) throw new Error('key art chunks contain invalid base64 characters');
let raw;
try{raw=atob(b64)}catch(e){throw new Error('key art base64 decode failed: '+e.message)}
const bytes=new Uint8Array(raw.length);
for(let i=0;i<raw.length;i++) bytes[i]=raw.charCodeAt(i);
const blobUrl=URL.createObjectURL(new Blob([bytes],{type:'image/webp'}));
const img=new Image();
img.src=blobUrl;
await img.decode();
if(img.naturalWidth!==640||img.naturalHeight!==360) throw new Error(`key art dimensions mismatch: ${img.naturalWidth}x${img.naturalHeight}`);
bg.style.backgroundImage=`url(${JSON.stringify(blobUrl)})`;

if(game.renderer&&!game.renderer.__v3Disabled){
  game.renderer.__v3Disabled=true;
  game.renderer.render=()=>{};
  game.renderer.shadowMap.enabled=false;
}

const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:!TEST,powerPreference:'high-performance'});
renderer.setClearColor(0x000000,0);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.42;
const scene=new THREE.Scene();
const camera=new THREE.OrthographicCamera(0,1,1,0,-200,200);
camera.position.z=100;
const root=new THREE.Group();scene.add(root);
scene.add(new THREE.HemisphereLight(0xe3efff,0x27112d,4.1));
const key=new THREE.DirectionalLight(0xffe4a4,5.0);key.position.set(-4,8,10);scene.add(key);
const rim=new THREE.DirectionalLight(0x55e6ff,3.2);rim.position.set(8,4,8);scene.add(rim);

const REF={w:1672,h:941};
let view={w:innerWidth,h:innerHeight,scale:1,ox:0,oy:0};
function resize(){
  const w=innerWidth,h=innerHeight,s=Math.max(w/REF.w,h/REF.h),rw=REF.w*s,rh=REF.h*s;
  view={w,h,scale:s,ox:(w-rw)/2,oy:(h-rh)/2};
  renderer.setPixelRatio(Math.min(devicePixelRatio,TEST?1:1.45));
  renderer.setSize(w,h,false);
  camera.left=0;camera.right=w;camera.top=h;camera.bottom=0;camera.updateProjectionMatrix();
}
resize();addEventListener('resize',resize,{passive:true});
const mapRef=(p,z=0)=>new THREE.Vector3(view.ox+p.x*view.scale,view.h-(view.oy+p.y*view.scale),z);

const anchors=[[835,795],[1000,768],[1140,724],[1248,655],[1320,570],[1382,470],[1372,380],[1290,315],[1180,270],[1052,235],[920,218],[790,226],[655,250],[530,305],[430,372],[365,460],[365,548],[410,624],[495,686],[610,730],[725,758],[835,795]].map(([x,y])=>({x,y}));
function sampleRing(n){
  const seg=[];let total=0;
  for(let i=0;i<anchors.length-1;i++){
    const a=anchors[i],b=anchors[i+1],l=Math.hypot(b.x-a.x,b.y-a.y);
    seg.push({a,b,l,start:total});total+=l;
  }
  return Array.from({length:n},(_,i)=>{
    const d=(i/n)*total,s=seg.find(q=>d>=q.start&&d<=q.start+q.l)||seg[seg.length-1],t=(d-s.start)/s.l;
    return{x:s.a.x+(s.b.x-s.a.x)*t,y:s.a.y+(s.b.y-s.a.y)*t};
  });
}
const tileRef=sampleRing(24);

const phys=(c,m=.18,r=.22,cc=.9,e=0,ei=0)=>new THREE.MeshPhysicalMaterial({color:c,metalness:m,roughness:r,clearcoat:cc,clearcoatRoughness:.09,emissive:e,emissiveIntensity:ei});
const std=(c,m=.1,r=.35,e=0,ei=0)=>new THREE.MeshStandardMaterial({color:c,metalness:m,roughness:r,emissive:e,emissiveIntensity:ei});
const GOLD=phys(0xffc84d,.72,.13,1,0x8f4d00,.16),WHITE=phys(0xfff7e8,.05,.14,1),BLACK=std(0x0e1220,.45,.45),CYAN=std(0x5cecff,.06,.16,0x18bce8,1.8),PURPLE=phys(0x7a4cc9,.14,.2,.8,0x3b176f,.15),TAN=phys(0xdca65c,.02,.45,.4),DARK=phys(0x211c25,.18,.3,.6);
const box=(w,h,d,m)=>new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);
const sph=(r,m,s=20)=>new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(10,s/2)),m);
const cyl=(r,h,m,s=24)=>new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),m);
const cone=(r,h,m,s=16)=>new THREE.Mesh(new THREE.ConeGeometry(r,h,s),m);
function pedestal(color){const g=new THREE.Group(),b=cyl(.55,.16,phys(color,.5,.14,1,color,.16),28);g.add(b);const ring=new THREE.Mesh(new THREE.TorusGeometry(.47,.06,8,32),std(color,.05,.15,color,1.8));ring.rotation.x=Math.PI/2;ring.position.y=.1;g.add(ring);return g}
function astronaut(color){const g=pedestal(color),body=cyl(.25,.66,WHITE,18);body.position.y=.53;g.add(body);const head=sph(.34,WHITE);head.position.y=1.13;g.add(head);const visor=sph(.27,phys(0x173856,.08,.08,1,0x0c6d94,.28),18);visor.scale.z=.55;visor.position.set(0,1.14,.2);g.add(visor);return g}
function dog(color){const g=pedestal(color),body=sph(.34,TAN);body.position.y=.52;g.add(body);const head=sph(.32,TAN);head.position.y=1.02;g.add(head);for(const s of [-1,1]){const ear=cone(.14,.34,TAN,12);ear.position.set(s*.21,1.36,0);g.add(ear)}const shades=box(.54,.1,.1,BLACK);shades.position.set(0,1.07,.28);g.add(shades);return g}
function nft(color){const g=pedestal(color),body=box(.5,.62,.42,PURPLE);body.position.y=.48;g.add(body);const head=box(.48,.46,.46,phys(0xf0b08a,.02,.42,.35));head.position.y=1.01;g.add(head);for(let i=0;i<5;i++){const hair=box(.1,.25,.12,phys(color,.1,.25,.6,color,.1));hair.position.set(-.22+i*.11,1.36,(i%2)*.04);g.add(hair)}const shades=box(.53,.1,.1,CYAN);shades.position.set(0,1.03,.28);g.add(shades);return g}
function bull(color){const g=pedestal(color),body=sph(.38,DARK);body.position.y=.53;g.add(body);const head=sph(.32,phys(0x77513b,.02,.42,.35));head.position.y=1.03;g.add(head);for(const s of [-1,1]){const h=cone(.1,.5,GOLD,12);h.rotation.z=s*.9;h.position.set(s*.33,1.35,0);g.add(h)}const shades=box(.55,.1,.1,BLACK);shades.position.set(0,1.06,.28);g.add(shades);return g}
const COLORS=[0xffd66b,0x65e8ff,0xb98cff,0x6df0a8];
const tokens=[astronaut,dog,nft,bull].map((fn,i)=>{const g=fn(COLORS[i]);g.scale.setScalar(22);root.add(g);return g});
const lastPos=[-1,-1,-1,-1];

const halo=new THREE.Group();
const haloRing=new THREE.Mesh(new THREE.TorusGeometry(1,.085,8,48),std(0xffdc6a,.04,.12,0xffbd31,2.6));haloRing.rotation.x=Math.PI/2;halo.add(haloRing);halo.scale.setScalar(25);root.add(halo);
function die(){const g=new THREE.Group(),cube=box(1,1,1,WHITE);g.add(cube);for(const [x,y,z] of [[0,.51,0],[0,-.51,0],[.51,0,0],[-.51,0,0],[0,0,.51],[0,0,-.51]]){const p=sph(.08,BLACK,10);p.position.set(x,y,z);g.add(p)}return g}
const dice=[die(),die()];dice.forEach(d=>{d.scale.setScalar(23);root.add(d)});

const sparkGeo=new THREE.BufferGeometry(),sparkCount=36,sparkPos=new Float32Array(sparkCount*3);sparkGeo.setAttribute('position',new THREE.BufferAttribute(sparkPos,3));
const sparks=new THREE.Points(sparkGeo,new THREE.PointsMaterial({color:0xffd46b,size:3.2,transparent:true,opacity:0,depthWrite:false}));root.add(sparks);
function burstAt(v){for(let i=0;i<sparkCount;i++){const a=Math.random()*Math.PI*2,r=6+Math.random()*34;sparkPos[i*3]=v.x+Math.cos(a)*r;sparkPos[i*3+1]=v.y+Math.sin(a)*r;sparkPos[i*3+2]=15}sparkGeo.attributes.position.needsUpdate=true;sparks.material.opacity=.75}

let started=false;
function sync(){
  const state=game.getState?.()||null;started=!!state;
  if(!state){tokens.forEach(t=>t.visible=false);halo.visible=false;return}
  tokens.forEach(t=>t.visible=true);halo.visible=true;
  const groups=new Map();
  state.players.forEach((p,i)=>{if(p.dead){tokens[i].visible=false;return}const k=String(p.pos);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(i)});
  groups.forEach((ids,k)=>{const p=mapRef(tileRef[+k],25),count=ids.length;ids.forEach((id,j)=>{const a=count===1?0:j/count*Math.PI*2,off=count===1?0:20*view.scale;tokens[id].userData.target=new THREE.Vector3(p.x+Math.cos(a)*off,p.y+Math.sin(a)*off,35+id);if(lastPos[id]!==state.players[id].pos){lastPos[id]=state.players[id].pos;burstAt(p)}})});
  const active=state.players[state.turn]||state.players[0],hp=mapRef(tileRef[active.pos],20);halo.position.copy(hp);
  const d1=mapRef({x:790,y:605},45),d2=mapRef({x:895,y:610},45),sc=23*view.scale;dice[0].position.copy(d1);dice[1].position.copy(d2);dice[0].scale.setScalar(sc);dice[1].scale.setScalar(sc);
}
setInterval(sync,80);sync();
let last=0;
function loop(now){requestAnimationFrame(loop);const cap=TEST?50:16;if(now-last<cap)return;const dt=Math.min(.04,(now-last)/1000||.016);last=now;sync();tokens.forEach((t,i)=>{const target=t.userData.target;if(target)t.position.lerp(target,TEST?1:Math.min(1,dt*9));t.rotation.y+=dt*(.35+i*.06)});halo.rotation.z+=dt*.85;const rolling=started&&document.querySelector('#roll')?.disabled;dice.forEach((d,i)=>{d.rotation.x+=dt*(rolling?5.5:.35+i*.08);d.rotation.y+=dt*(rolling?6.5:.45);d.rotation.z+=dt*(rolling?3.6:.2)});sparks.material.opacity=Math.max(0,sparks.material.opacity-dt*.55);renderer.render(scene,camera)}
requestAnimationFrame(loop);

document.documentElement.dataset.visualPipeline='v3';
window.__cryptoVisualV3={
  version:'v3.0-reference-composite',scene,renderer,keyArt:{loaded:true,width:img.naturalWidth,height:img.naturalHeight,blobUrl,base64Length:b64.length},
  diagnostics:()=>({geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,dpr:renderer.getPixelRatio(),tokens:tokens.length,keyArtLoaded:!!img.naturalWidth,keyArtBase64Length:b64.length,pipeline:document.documentElement.dataset.visualPipeline})
};
