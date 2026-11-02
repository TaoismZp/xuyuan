import crypto from 'node:crypto';
import k0 from '../crypto-tycoon/keyart-chunk-0.js';
import k1 from '../crypto-tycoon/keyart-chunk-1.js';
import k2 from '../crypto-tycoon/keyart-chunk-2.js';
import k3 from '../crypto-tycoon/keyart-chunk-3.js';

const chunks=[k0,k1,k2,k3];
const expectedChunkLengths=[23000,23000,23000,21124];
for(let i=0;i<chunks.length;i++){
  if(chunks[i].length!==expectedChunkLengths[i]) throw new Error(`chunk-${i} length ${chunks[i].length} !== ${expectedChunkLengths[i]}`);
  if(!/^[A-Za-z0-9+/]+={0,2}$/.test(chunks[i])) throw new Error(`chunk-${i} contains non-base64 characters`);
}
const b64=chunks.join('');
if(b64.length!==90124) throw new Error(`combined base64 length ${b64.length} !== 90124`);
const raw=Buffer.from(b64,'base64');
if(raw.length!==67592) throw new Error(`decoded bytes ${raw.length} !== 67592`);
const reencoded=raw.toString('base64');
if(reencoded!==b64) throw new Error('base64 does not round-trip exactly');
if(raw.subarray(0,4).toString('ascii')!=='RIFF'||raw.subarray(8,12).toString('ascii')!=='WEBP') throw new Error('decoded asset is not a WebP RIFF payload');
const sha=crypto.createHash('sha256').update(raw).digest('hex');
const expected='8cf2f51890c2c2fa681784833b819a986bf8931125ae5a2210bc4020e96dfac5';
if(sha!==expected) throw new Error(`key art sha256 ${sha} !== ${expected}`);
console.log(`PASS key art integrity: chunks=${chunks.map(x=>x.length).join('+')}; base64=${b64.length}; bytes=${raw.length}; sha256=${sha}`);
