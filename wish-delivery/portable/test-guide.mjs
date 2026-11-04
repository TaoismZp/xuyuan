import fs from 'node:fs';
if (!fs.existsSync('wish-delivery/portable/OPERATOR_GUIDE.md')) process.exit(1);
console.log('GUIDE_EXISTS');
