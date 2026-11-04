import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {resolveRevival,decideContinuation,parseRevival} from './revival-router.mjs';
const read = p => fs.readFileSync(p);
const blobSha = b => crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');
const root = 'wish-delivery/';
const current = JSON.parse(read(root+'CURRENT.json'));
assert.equal(current.active_version, 'v7.6','A candidate must never promote itself');
assert.equal(blobSha(read(root+'CURRENT.json')),'2a253140bbd097b05b273a1a4634669991c2fde9','Current pointer unexpectedly modified');
assert.equal(blobSha(read(root+'versions/v7.6.md')),'955bdde3d332283ff6ccc89f943555824f741d59','Frozen active spec unexpectedly modified');
assert(read(root+'candidates/v7.8-self-evolution-rc2-revival.md').includes('CANDIDATE / NOT ACTIVE'), 'RC2 must remain candidate');
assert(read(root+'recovery/REVIVAL.md').includes('断档重生'), 'Trigger contract absent');
const sample = JSON.parse(read(root+'recovery/revival-fixtures.json'));
assert.equal(sample.schema,'wish-revival-fixtures/v1');
for(const x of sample.routes) {
  const got = resolveRevival(x);
  assert.equal(got.status,x.expected.status,x.label+' '+JSON.stringify(got));
  if(x.expected.id) assert.equal(got.id,x.expected.id,x.label+' wrong target');
  if(x.expected.optionCount) assert.equal(got.options.length,x.expected.optionCount,x.label+' ambiguous candidate count');
  assert(typeof got.next === 'string' && got.next.length>0,x.label+' missing next action');
  if(got.status === 'VERIFY_CHECKPOINT') assert(got.reason && got.id,x.label+' must identify source');
}
for(const x of sample.continuation) {
  const got = decideContinuation(x.input);
  assert.equal(got.status,x.expected,x.label+' '+JSON.stringify(got));
  assert(typeof got.next === 'string' && got.next.length>0,x.label+' missing next action');
}
assert.equal(parseRevival('断档重生').triggered,true);
assert.equal(parseRevival('我喜欢“断档重生”这个名字').triggered,false);
const site = JSON.parse(read('personal-site-v1/recovery/state.json'));
assert.equal(site.gates.ownerAuthenticatedGitHubCommit,'PENDING_OWNER','Owner-authenticated publishing cannot be inferred');
console.log(JSON.stringify({outcome:'PASS_SYNTHETIC_ONLY',route_cases:sample.routes.length,continuation_cases:sample.continuation.length,active_version:current.active_version,real_cold_start:'PENDING',global_custom_instructions_installed:'UNVERIFIED'},null,2));
