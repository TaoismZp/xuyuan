import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const argument = process.argv[2];
if (!argument) throw new Error('Usage: node assemble-pages.mjs /safe/path/pages-publish');
const output = path.resolve(argument);
if (path.basename(output) !== 'pages-publish' || output === root ||
    root.startsWith(output + path.sep) || output.startsWith(root + path.sep)) {
  throw new Error('Refusing unsafe public artifact output path');
}
fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });

function copy(requiredPath, destination = requiredPath, optional = false) {
  const source = path.join(root, requiredPath);
  if (!fs.existsSync(source)) {
    if (optional) return;
    throw new Error('Required public asset missing: ' + requiredPath);
  }
  const target = path.join(output, destination);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.cpSync(source, target, { recursive: true, force: true });
}

// Preserve every previously deployed product route; do not ship the repo root.
for (const file of ['index.html', 'app.js', 'data.js', 'scoring-fix.js', 'styles.css']) copy(file);
for (const directory of ['crypto-tycoon-3d', 'crypto-tycoon', 'essays', 'longform-v2', 'personal-site-lab']) copy(directory);

// Personal publication: ship ONLY the finished reading surface and CMS entry.
// Never copy canonical Markdown, draft files, builder, CI or node_modules.
for (const entry of ['index.html', 'feed.xml', 'sitemap.xml', 'assets', 'essays', 'projects', 'about', 'admin', 'write']) {
  copy('personal-site-v1/' + entry);
}
copy('personal-site-v1/media', 'personal-site-v1/media', true);
console.log('Assembled allowlisted Pages artifact: ' + output);
