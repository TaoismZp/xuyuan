#!/usr/bin/env node
// Git-only, dependency-free recovery contract validation. Does not log secrets.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));
const repoFile = (p) => {
  if (typeof p !== 'string' || p.startsWith('/') || p.includes('..')) throw new Error('Unsafe repository path: ' + p);
  return path.join(root,p);
};
const read = (p) => fs.readFileSync(repoFile(p));
const sha = (bytes) => crypto.createHash('sha1').update(Buffer.from('blob ' + bytes.length + '\0')).update(bytes).digest('hex');
const requireThat = (condition,message) => {if(!condition) throw new Error(message);};

const data = JSON.parse(read('personal-site-v1/recovery/state.json').toString('utf8'));
requireThat(data.schema === 'wish-recovery/v1','Unexpected checkpoint schema');
requireThat(data.repository === 'TaoismZp/xuyuan','Wrong repository');
requireThat(data.project === 'personal-site-v1','Wrong project');
requireThat(data.rulebook.version === 'v7.5','Unreviewed wish delivery version');
requireThat(read(data.rulebook.path).toString('utf8').includes('Binding Chain Gate'),'Missing canonical v7.5 instructions');
for (const label of ['vision','blueprint']) {
  const fixture = data.bindingChain[label];
  requireThat(/^[a-f0-9]{40}$/.test(fixture.blobSha),label + ' is missing immutable Git blob SHA');
  requireThat(sha(read(fixture.path)) === fixture.blobSha,label + ' content changed: update locked fixture and binding chain after review');
}
requireThat(/^[a-f0-9]{40}$/.test(data.bindingChain.lastShippedCommit),'Invalid delivered commit identity');
for (const label of ['deployment','publicSameSurfaceVerification','independentSupervision']) {
  const evidence = data.bindingChain[label];
  requireThat(Number.isSafeInteger(evidence.runId) && evidence.runId > 0,'Invalid run ID for ' + label);
  requireThat(evidence.conclusion === 'success','Unverified historical evidence: ' + label);
}
const projectState = read(data.canonicalStatus).toString('utf8');
requireThat(projectState.includes(data.bindingChain.lastShippedCommit),'Manifest conflicts with PROJECT_STATE release identity');
requireThat(projectState.includes('PENDING_OWNER'),'The pending author publication gate must not be suppressed');
const gates = data.gates;
requireThat(gates.publicReader === 'PASS_PINNED_RELEASE','Public reader PASS must be scoped to pinned release');
requireThat(gates.tokenlessComposer === 'PASS_PINNED_RELEASE','Composer PASS must be scoped to pinned release');
for(const label of ['ownerAuthenticatedGitHubCommit','publicationAfterOwnerCommit','cmsAuthenticatedSave'])
  requireThat(gates[label] === 'PENDING_OWNER','Unauthorized upgrade of author gate: ' + label);
for (const file of [
  'personal-site-v1/RECOVERY.md',
  'personal-site-v1/OWNER_ACCEPTANCE.md',
  'personal-site-v1/WRITE_ASSISTANT_CONTRACT.md',
  'personal-site-v1/index.html',
  'personal-site-v1/write/index.html',
  'personal-site-v1/admin/index.html',
  data.authorContent,
  '.github/workflows/deploy-pages.yml',
  '.github/workflows/verify-personal-site-v1-public.yml'
]) requireThat(fs.statSync(repoFile(file)).isFile(),'Missing recovery dependency: ' + file);
for(const label of ['publicReader','authorPreparation','optionalCMS'])
  requireThat(data.delivery[label]?.startsWith('https://taoismzp.github.io/xuyuan/personal-site-v1/'),'Wrong delivery surface: '+label);
const realPost = read(data.authorContent).toString('utf8');
requireThat(realPost.includes('天才交易员') && /status:\\s*published/.test(realPost),'Missing canonical published article; never replace with a CI fixture');
const output = {
  status:'RECOVERY_CHECKPOINT_CONSISTENT',
  project:data.project,
  rulebook:data.rulebook.version,
  verifiedRelease:data.bindingChain.lastShippedCommit,
  publicReader:data.delivery.publicReader,
  writer:data.delivery.authorPreparation,
  pendingGates:Object.entries(gates).filter(([,value])=>value.startsWith('PENDING')).map(([key])=>key),
  caveat:'Offline archival integrity only. Historical GitHub Actions identities and current public surface require independent checks. Owner authentication has not been tested.'
};
console.log(JSON.stringify(output,null,2));
