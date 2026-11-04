import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {decide} from './decision-engine.mjs';

const base='wish-delivery/';
const active=JSON.parse(fs.readFileSync(base+'CURRENT.json','utf8'));
assert.equal(active.active_version,'v7.6','active version changed without authorized promotion');
assert.equal(active.active_spec,base+'versions/v7.6.md','active path changed');
const blob = bytes => crypto.createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
assert.equal(blob(fs.readFileSync(base+'versions/v7.6.md')),'955bdde3d332283ff6ccc89f943555824f741d59','frozen v7.6 modified');
assert.equal(blob(fs.readFileSync(base+'CURRENT.json')),'2a253140bbd097b05b273a1a4634669991c2fde9','CURRENT pointer modified');
assert(fs.existsSync(base+'versions/v7.7.md'),'v7.7 draft unexpectedly removed');
const candidate=fs.readFileSync(base+'candidates/v7.8-self-evolution-rc1.md','utf8');
for (const anchor of ['CANDIDATE / NOT ACTIVE','Gate 0','Gate 6.5','Gate 7','Recursive Integrity Gate','v7.6'])
  assert(candidate.includes(anchor),'missing candidate anchor '+anchor);
const cases=JSON.parse(fs.readFileSync('wish-delivery/self-evolution/2026-11-04/fixtures.json','utf8'));
for (const c of cases) {
  const got=decide(c.input);
  assert.equal(got.state,c.expected,c.name+' actual '+JSON.stringify(got));
  assert(got.next.length>0,c.name+' missing next action');
}
const liveStatus=JSON.parse(fs.readFileSync('personal-site-v1/recovery/state.json','utf8'));
assert.equal(liveStatus.gates.ownerAuthenticatedGitHubCommit,'PENDING_OWNER','Cannot silently promote owner publication');
assert.equal(liveStatus.gates.publicationAfterOwnerCommit,'PENDING_OWNER','Cannot silently promote public publication');
console.log(JSON.stringify({result:'PASS_SYNTHETIC_ONLY',active_version:active.active_version,baseline_blob:'955bdde3d332283ff6ccc89f943555824f741d59',cases:cases.length,owner_gate:'PENDING_OWNER',promotion:'PENDING_EXTERNAL',next:'Test a real writing and a real software task with a different reviewer'},null,2));
