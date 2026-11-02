import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/+esm';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(let i=0;i<400&&!window.__cryptoVisualV2;i++) await sleep(25);
const api=window.__cryptoVisualV2;if(!api)throw new Error('visual v2 unavailable');
const {scene,renderer}=api;const root=scene.children.find(o=>o.isGroup);if(!root)throw new Error('visual root missing');
renderer.toneMappingExposure=1.86;
const oldCity=root.children[1];if(oldCity)oldCity.visible=false;
const oldLogo=scene.getObjectByName('reference-logo-v3');if(oldLogo)oldLogo.visible=false;
const gold=new THREE.MeshPhysicalMaterial({color:0xffc947,metalness:.76,roughness:.13,clearcoat:1,clearcoatRoughness:.07,emissive:0x8d4d00,emissiveIntensity:.16});
const goldHi=new THREE.MeshPhysicalMaterial({color:0xffe17d,metalness:.62,roughness:.1,clearcoat:1,emissive:0x9c5d04,emissiveIntensity:.13});
const navy=new THREE.MeshPhysicalMaterial({color:0x142552,metalness:.35,roughness:.2,clearcoat:.9});
const purple=new THREE.MeshPhysicalMaterial({color:0x42205d,metalness:.32,roughness:.18,clearcoat:.9,emissive:0x3f145f,emissiveIntensity:.18});
const cyan=new THREE.MeshStandardMaterial({color:0x55e8ff,metalness:.05,roughness:.18,emissive:0x19bce8,emissiveIntensity:2.2});
const magenta=new THREE.MeshStandardMaterial({color:0xff6bd4,metalness:.05,roughness:.2,emissive:0xd934a6,emissiveIntensity:1.9});
const green=new THREE.MeshStandardMaterial({color:0x44efae,metalness:.04,roughness:.2,emissive:0x18aa72,emissiveIntensity:1.55});
function box(w,h,d,m,cast=true){const x=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);x.castShadow=cast;x.receiveShadow=cast;return x}
function tex(draw,w=800,h=300){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t}
function sprite(text,{w=900,h=250,size=110,color='#fff0a5',stroke='#7d4300',sub=''}={}){const t=tex((c,W,H)=>{c.clearRect(0,0,W,H);c.textAlign='center';c.textBaseline='middle';c.lineJoin='round';c.font=`1000 ${size}px -apple-system,"PingFang SC",sans-serif`;c.lineWidth=Math.max(8,size*.105);c.strokeStyle=stroke;c.strokeText(text,W/2,H*.43);c.fillStyle=color;c.fillText(text,W/2,H*.43);if(sub){c.font='900 29px sans-serif';c.lineWidth=4;c.strokeStyle='rgba(3,9,31,.95)';c.strokeText(sub,W/2,H*.81);c.fillStyle='#8be9ff';c.fillText(sub,W/2,H*.81)}},w,h);const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true,depthWrite:false}));s.scale.set(w/100,h/100,1);s.renderOrder=140;return s}
function roundedPanel(w,h,r,depth,material){const s=new THREE.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);const g=new THREE.ExtrudeGeometry(s,{depth,bevelEnabled:true,bevelThickness:.06,bevelSize:.06,bevelSegments:3,curveSegments:8});g.translate(0,0,-depth/2);const m=new THREE.Mesh(g,material);m.castShadow=true;m.receiveShadow=true;return m}

// Authored neon-finance skyline: varied silhouettes, roof caps, readable windows and signs.
const skyline=new THREE.Group();skyline.name='authored-skyline-v4';
const palettes=[0x17356e,0x213877,0x34286d,0x1d456f,0x263b67];
const specs=[[-13,-18,2.3,8.5],[-10.2,-19.5,2.0,11.2],[-7.5,-18.4,2.8,7.1],[-4.4,-20.2,2.1,12.8],[-1.4,-19.0,2.7,8.9],[2.0,-20.5,2.2,11.7],[5.0,-18.7,2.8,7.8],[8.2,-20.0,2.2,12.1],[11.2,-18.5,2.4,9.3],[-15.2,-24,3.1,10.2],[-11.5,-25,2.5,14.0],[-7.8,-23.5,3.2,9.5],[-3.6,-25.5,2.9,15.4],[.2,-24,3.0,11.1],[4.1,-25.4,2.6,14.8],[7.6,-23.8,3.0,10.4],[11.0,-25.0,2.7,13.5],[14.2,-23.4,3.1,9.8]];
specs.forEach((s,i)=>{const [x,z,w,h]=s,g=new THREE.Group(),body=box(w,h,w*.72,new THREE.MeshPhysicalMaterial({color:palettes[i%palettes.length],metalness:.3,roughness:.28,clearcoat:.45}),false);body.position.y=h/2;g.add(body);const cap=box(w*1.08,.28,w*.8,i%3===0?goldHi:navy,false);cap.position.y=h+.15;g.add(cap);for(let y=.8;y<h-.45;y+=.8){for(let col=-1;col<=1;col++){if((Math.round(y*10)+col+i)%4===0)continue;const wm=(i+col+Math.round(y))%3===0?magenta:cyan,win=box(.22,.34,.055,wm,false);win.position.set(col*w*.27,y,w*.365+.035);g.add(win)}}if(i%4===0){const sp=sprite(i%8===0?'BTC':'WEB3',{w:270,h:90,size:55,color:i%8===0?'#ffe17d':'#7defff',stroke:'#14214c'});sp.position.set(0,h*.72,w*.39);sp.scale.set(1.8,.6,1);g.add(sp)}g.position.set(x,0,z);skyline.add(g)});
// mid-depth smaller towers so skyline has layers instead of one wall.
for(let i=0;i<13;i++){const x=-14+i*2.35,z=-14.3-(i%3)*.65,h=3.5+(i%5)*1.1,w=1.25+(i%2)*.38,g=new THREE.Group(),b=box(w,h,w*.7,new THREE.MeshPhysicalMaterial({color:i%2?0x24518d:0x31327d,metalness:.24,roughness:.3,clearcoat:.4}),false);b.position.y=h/2;g.add(b);const strip=box(w*.78,.12,.05,i%3===0?magenta:cyan,false);strip.position.set(0,h*.7,w*.36);g.add(strip);g.position.set(x,0,z);skyline.add(g)}
const horizonGlow=new THREE.PointLight(0x596cff,135,42,2);horizonGlow.position.set(0,8,-17);skyline.add(horizonGlow);const leftGlow=new THREE.PointLight(0xff4dca,78,25,2);leftGlow.position.set(-10,7,-14);skyline.add(leftGlow);const rightGlow=new THREE.PointLight(0x42dfff,92,27,2);rightGlow.position.set(10,7,-14);skyline.add(rightGlow);root.add(skyline);

// Hero logo: rounded, layered, winged game-sign silhouette instead of a flat UI bar.
const logo=new THREE.Group();logo.name='reference-logo-v4';
const outer=roundedPanel(9.0,2.18,.48,.42,gold);outer.position.set(0,4.05,.3);logo.add(outer);const mid=roundedPanel(8.45,1.76,.38,.5,purple);mid.position.set(0,4.05,.54);logo.add(mid);const inner=roundedPanel(7.95,1.46,.3,.54,new THREE.MeshPhysicalMaterial({color:0x401c29,metalness:.38,roughness:.17,clearcoat:1,emissive:0x4a160f,emissiveIntensity:.14}));inner.position.set(0,4.05,.78);logo.add(inner);
for(const side of [-1,1]){for(let i=0;i<4;i++){const feather=new THREE.Mesh(new THREE.ConeGeometry(.16,.9-.08*i,18),goldHi);feather.rotation.z=side*(1.0+i*.12);feather.position.set(side*(4.72+i*.3),3.78-i*.05,.58);logo.add(feather)}const orb=new THREE.Mesh(new THREE.SphereGeometry(.14,16,10),cyan);orb.position.set(side*4.53,4.48,.76);logo.add(orb)}
const title=sprite('币圈大富翁',{w:1100,h:270,size:132,color:'#ffe58d',stroke:'#854800',sub:'CRYPTO TYCOON'});title.position.set(0,4.1,1.23);title.scale.set(9.55,2.35,1);logo.add(title);
const crownBase=roundedPanel(1.95,.3,.12,.22,goldHi);crownBase.position.set(0,5.28,.82);logo.add(crownBase);for(let i=-2;i<=2;i++){const h=i===0?1.05:Math.abs(i)===1?.82:.63,p=new THREE.Mesh(new THREE.ConeGeometry(.16,h,16),goldHi);p.position.set(i*.38,5.42+h*.38,.83);logo.add(p)}for(const [x,m] of [[-.55,cyan],[0,magenta],[.55,cyan]]){const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.11),m);gem.position.set(x,5.3,1.02);logo.add(gem)}scene.add(logo);

// A few cinematic foreground bokeh lights to mimic the reference depth without fog-as-detail.
for(let i=0;i<16;i++){const material=new THREE.MeshBasicMaterial({color:i%3===0?0xffc85c:i%3===1?0x4de5ff:0xff6bd5,transparent:true,opacity:.32,depthWrite:false}),orb=new THREE.Mesh(new THREE.SphereGeometry(.07+(i%3)*.035,10,8),material);orb.position.set(-13+(i*3.7)%26,1.5+(i%5)*1.25,-11-(i%4)*1.6);scene.add(orb)}
window.__cryptoVisualTune2={version:'v2.2-art-direction'};
