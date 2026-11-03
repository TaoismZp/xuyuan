import fs from 'node:fs';
import path from 'node:path';

const folder = process.argv[2];
if (!folder || path.basename(path.resolve(folder)) !== 'pages-publish') {
  throw new Error('Usage: node verify-pages-artifact.mjs /safe/path/pages-publish');
}
const root = path.resolve(folder);
const requirePath = (name) => {
  if (!fs.existsSync(path.join(root, name))) throw new Error('Missing public path: ' + name);
};
const forbidPath = (name) => {
  if (fs.existsSync(path.join(root, name))) throw new Error('Sensitive source in public artifact: ' + name);
};
for (const p of [
  'index.html', 'app.js', 'styles.css', 'crypto-tycoon-3d',
  'crypto-tycoon', 'essays', 'longform-v2', 'personal-site-lab',
  'personal-site-v1/index.html', 'personal-site-v1/essays/index.html',
  'personal-site-v1/projects/index.html', 'personal-site-v1/about/index.html',
  'personal-site-v1/admin/index.html', 'personal-site-v1/admin/config.yml',
  'personal-site-v1/assets/site.css'
]) requirePath(p);
for (const p of [
  '.github', '.git', 'README.md', 'tests', 'wish-delivery',
  'personal-site-v1/content', 'personal-site-v1/scripts',
  'personal-site-v1/node_modules', 'personal-site-v1/PROJECT_STATE.md',
  'personal-site-v1/package.json', 'personal-site-v1/BACKEND_BUILD_BLUEPRINT.md'
]) forbidPath(p);
const allowed = new Set(['index.html', 'assets', 'essays', 'projects', 'about', 'admin', 'media']);
for (const entry of fs.readdirSync(path.join(root, 'personal-site-v1'))) {
  if (!allowed.has(entry)) throw new Error('Unexpected personal-site public entry: ' + entry);
}
console.log('PASS: only allowlisted personal-site files enter public deployment.');
