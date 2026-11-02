import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/+esm';
import { KEY_ART } from './keyart-data.js';

const TEST=new URLSearchParams(location.search).get('test')==='1';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<400&&!window.__chainTycoon3d;i++) await sleep(25);
const game=window.__chainTycoon3d;if(!game)throw new Error('game engine unavailable');

const bg=document.querySelector('#keyArtLayer');
const canvas=document.querySelector('#overlayScene');
if(!bg||!canvas)throw new Error('visual v3 surface missing');
const img=new Image();img.src=KEY_ART;try{await img.decode()}catch{}
bg.style.backgroundImage=`url("${KEY_ART}")`;

// The old renderer still owns game state/animations, but it no longer needs to paint pixels.
if(game.renderer&&!game.renderer.__v3Disabled){game.renderer.__v3Disabled=true;game.renderer.render=()=>{};game.renderer.shadowMap.enabled=false;}

const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:!TEST,powerPreference:'high-performance'});
renderer.setClearColor(0x000000,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.45;
const scene=new THREE.Scene();
const camera=new THREE.OrthographicCamera(0,1,1,0,-200,200);camera.position.z=100;
const root=new THREE.Group();scene.add(root);
const lightA=new THREE.HemisphereLight(0xd8e8ff,0x2a1235,4.5);scene.add(lightA);
const key=new THREE.DirectionalLight(0xffe5ae,5.2);key.position.set(-4,8,10);scene.add(key);
const rim=new THREE.DirectionalLight(0x5ee6ff,3.4);rim.position.set(8,4,7);scene.add(rim);

const COLORS=[0xffd66b,0x65e8ff,0xb98cff,0x6df0a8];
const ref={w:1672,h:941};
let view={w:innerWidth,h:innerHeight,scale:1,ox:0,oy:0};
function resize(){
 const w=innerWidth,h=innerHeight,s=Math.max(w/ref.w,h/ref.h),rw=ref.w*s,rh=ref.h*s;
 view={w,h,scale:s,ox:(w-rw)/2,oy:(h-rh)/2};
 renderer.setPixelRatio(Math.min(devicePixelRatio,TEST?1:1.45));renderer.setSize(w,h,false);
 camera.left=0;camera.right=w;camera.top=h;camera.bottom=0;camera.updateProjectionMatrix();
}
resize();addEventListener('resize',resize,{passive:true});
function mapRef(p,z=0){const x=view.ox+p.x*view.scale,sy=view.oy+p.y*view.scale;return new THREE.Vector3(x,view.h-sy,z)}

const anchors=[
 [835,795],[1000,768],[1140,724],[1248,655],[1320,570],[1382,470],[1372,380],[1290,315],
 [1180,270],[1052,235],[920,218],[790,226],[655,250],[530,305],[430,372],[365,460],
 [365,548],[410,624],[495,686],[610,730],[725,758],[835,795]
].map(([x,y])=>({x,y}));
function sampleRing(n){const seg=[];let total=0;for(let i=0;i<anchors.length-1;i++){const a=anchors[i],b=anchors[i+1],l=Math.hypot(b.x-a.x,b.y-a.y);seg.push({a,b,l,start:total});total+=l}return Array.from({length:n},(_,i)=>{const d=(i/n)*total;const s=seg.find(q=>d>=q.start&&d<=q.start+q.l)||seg[seg.length-1],t=(d-s.start)/s.l;return{x:s.a.x+(s.b.x-s.a.x)*t,y:s.a.y+(s.b.y-s.a.y)*t}})}
const tileRef=sampleRing(24);

const phys=(c,m=.18,r=.22,cc=.9,e=0,ei=0)=>new THREE.MeshPhysicalMaterial({color:c,metalness:m,roughness:r,clearcoat:cc,clearcoatRoughness:.09,emissive:e,emissiveIntensity:ei});
const std=(c,m=.1,r=.35,e=0,ei=0)=>new THREE.MeshStandardMaterial({color:c,metalness:m,roughness:r,emissive:e,emissiveIntensity:ei});
const gold=phys(0xffc84d,.72,.13,1,0x8f4d00,.16),white=phys(0xfff7e8,.05,.14,1),black=std(0x0e1220,.45,.45),cyan=std(0x5cecff,.06,.16,0x18bce8,1.8),purple=phys(0x7a4cc9,.14,.2,.8,0x3b176f,.15),tan=phys(0xdca65c,.02,.45,.4),dark=phys(0x211c25,.18,.3,.6);
const box=(w,h,d,m)=>{const x=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);x.castShadow=false;return x};
const sph=(r,m,s=20)=>new THREE.Mesh(new THREE.SphereGeometry(r,s,Math.max(10,s/2)),m);
const cyl=(r,h,m,s=24)=>new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,s),m);
const cone=(r,h,m,s=16)=>new THREE.Mesh(new THREE.ConeGeometry(r,h,s),m);
function pedestal(color){const g=new THREE.Group(),base=cyl(.55,.16,phys(color,.5,.14,1,color,.16),28);g.add(base);const ring=new THREE.Mesh(new THREE.TorusGeometry(.47,.06,8,32),std(color,.05,.15,color,1.8));ring.rotation.x=Math.PI/2;ring.position.y=.1;g.add(ring);return g}
function astronaut(color){const g=pedestal(color),body=cyl(.25,.66,white,18);body.position.y=.53;g.add(body);const head=sph(.34,white,20);head.position.y=1.13;g.add(head);const visor=sph(.27,phys(0x173856,.08,.08,1,0x0c6d94,.28),18);visor.scale.z=.55;visor.position.set(0,1.14,.2);g.add(visor);const badge=cyl(.08,.05,gold,18);badge.rotation.x=Math.PI/2;badge.position.set(0,.57,.27);g.add(badge);return g}
function dog(color){const g=pedestal(color),body=sph(.34,tan);body.position.y=.52;g.add(body);const head=sph(.32,tan);head.position.y=1.02;g.add(head);for(const s of [-1,1]){const ear=cone(.14,.34,tan,12);ear.position.set(s*.21,1.36,0);g.add(ear)}const shades=box(.54,.1,.1,black);shades.position.set(0,1.07,.28);g.add(shades);const medal=cyl(.11,.05,gold,20);medal.rotation.x=Math.PI/2;medal.position.set(0,.55,.34);g.add(medal);return g}
function nft(color){const g=pedestal(color),body=box(.5,.62,.42,purple);body.position.y=.48;g.add(body);const head=box(.48,.46,.46,phys(0xf0b08a,.02,.42,.35));head.position.y=1.01;g.add(head);for(let i=0;i<5;i++){const hair=box(.1,.25,.12,phys(color,.1,.25,.6,color,.1));hair.position.set(-.22+i*.11,1.36,(i%2)*.04);g.add(hair)}const shades=box(.53,.1,.1,cyan);shades.position.set(0,1.03,.28);g.add(shades);return g}
function bull(color){const g=pedestal(color),body=sph(.38,dark);body.position.y=.53;g.add(body);const head=sph(.32,phys(0x77513b,.02,.42,.35));head.position.y=1.03;g.add(head);for(const s of [-1,1]){const h=cone(.1,.5,gold,12);h.rotation.z=s*.9;h.position.set(s*.33,1.35,0);g.add(h)}const shades=box(.55,.1,.1,black);shades.position.set(0,1.06,.28);g.add(shades);return g}
const factories=[astronaut,dog,nft,bull];
const tokens=factories.map((fn,i)=>{const g=fn(COLORS[i]);g.scale.setScalar(22);root.add(g);return g});
const lastPos=[-1,-1,-1,-1];

const halo=new THREE.Group();const haloRing=new THREE.Mesh(new THREE.TorusGeometry(1,.085,8,48),std(0xffdc6a,.04,.12,0xffbd31,2.6));haloRing.rotation.x=Math.PI/2;halo.add(haloRing);const haloCore=cyl(.78,.025,new THREE.MeshBasicMaterial({color:0xffc84d,transparent:true,opacity:.08,depthWrite:false}),32);halo.add(haloCore);halo.scale.setScalar(25);root.add(halo);

function die(){const g=new THREE.Group(),cube=box(1,1,1,white);g.add(cube);for(const [x,y,z] of [[0,.51,0],[0,-.51,0],[.51,0,0],[-.51,0,0],[0,0,.51],[0,0,-.51]]){const p=sph(.08,black,10);p.position.set(x,y,z);g.add(p)}return g}
const dice=[die(),die()];dice.forEach((d,i)=>{d.scale.setScalar(23);root.add(d)});

const sparkGeo=new THREE.BufferGeometry();const sparkCount=40,sparkPos=new Float32Array(sparkCount*3);sparkGeo.setAttribute('position',new THREE.BufferAttribute(sparkPos,3));const sparks=new THREE.Points(sparkGeo,new THREE.PointsMaterial({color:0xffd46b,size:3.2,transparent:true,opacity:.58,depthWrite:false}));root.add(sparks);
let sparkCenter=new THREE.Vector3();function burstAt(v){sparkCenter.copy(v);for(let i=0;i<sparkCount;i++){const a=Math.random()*Math.PI*2,r=6+Math.random()*34;sparkPos[i*3]=v.x+Math.cos(a)*r;sparkPos[i*3+1]=v.y+Math.sin(a)*r;sparkPos[i*3+2]=15}sparkGeo.attributes.position.needsUpdate=true;sparks.material.opacity=.75}

let state=null,started=false;
function sync(){state=game.getState?.()||null;started=!!state;if(!state){tokens.forEach(t=>t.visible=false);halo.visible=false;return}tokens.forEach(t=>t.visible=true);halo.visible=true;const groups=new Map();state.players.forEach((p,i)=>{if(p.dead){tokens[i].visible=false;return}const key=String(p.pos);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(i)});groups.forEach((ids,key)=>{const p=mapRef(tileRef[+key],25),count=ids.length;ids.forEach((id,k)=>{const a=count===1?0:(k/(count))*Math.PI*2,off=count===1?0:20*view.scale;tokens[id].userData.target=new THREE.Vector3(p.x+Math.cos(a)*off,p.y+Math.sin(a)*off,35+id);if(lastPos[id]!==state.players[id].pos){lastPos[id]=state.players[id].pos;burstAt(p)}})});const active=state.players[state.turn]||state.players[0],hp=mapRef(tileRef[active.pos],20);halo.position.copy(hp);const d1=mapRef({x:790,y:605},45),d2=mapRef({x:895,y:610},45);dice[0].position.copy(d1);dice[1].position.copy(d2);const sc=23*view.scale;dice[0].scale.setScalar(sc);dice[1].scale.setScalar(sc)}
setInterval(sync,80);sync();

let last=0;function loop(now){requestAnimationFrame(loop);const cap=TEST?50:16;if(now-last<cap)return;const dt=Math.min(.04,(now-last)/1000||.016);last=now;sync();tokens.forEach((t,i)=>{const target=t.userData.target;if(target)t.position.lerp(target,TEST?1:Math.min(1,dt*9));t.rotation.y+=dt*(.35+i*.06);t.position.y+=Math.sin(now*.004+i)*.15});halo.rotation.z+=dt*.85;const pulse=1+Math.sin(now*.006)*.1;haloRing.scale.setScalar(pulse);const rolling=started&&document.querySelector('#roll')?.disabled;dice.forEach((d,i)=>{d.rotation.x+=dt*(rolling?5.5:.35+i*.08);d.rotation.y+=dt*(rolling?6.5:.45);d.rotation.z+=dt*(rolling?3.6:.2)});sparks.material.opacity=Math.max(0,sparks.material.opacity-dt*.55);renderer.render(scene,camera)}requestAnimationFrame(loop);

document.documentElement.dataset.visualPipeline='v3';
window.__cryptoVisualV3={version:'v3.0-reference-composite',scene,renderer,keyArt:{loaded:img.complete,width:img.naturalWidth||ref.w,height:img.naturalHeight||ref.h},diagnostics:()=>({geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,dpr:renderer.getPixelRatio(),tokens:tokens.length,keyArtLoaded:img.complete,pipeline:document.documentElement.dataset.visualPipeline})};
