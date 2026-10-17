// Runs after "npm run dist:mac": copies the .dmg to the project folder so it is easy to find.
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'), dist = path.join(root, 'dist');
const f = fs.existsSync(dist) ? fs.readdirSync(dist).find(n => n.endsWith('.dmg')) : null;
if (!f) { console.error('No .dmg found in dist/. The build failed - see the errors above.'); process.exit(1); }
const out = path.join(root, f);
fs.copyFileSync(path.join(dist, f), out);
console.log('\nDONE. Mac installer (Apple Silicon + Intel):\n  ' + out + '\nSize: ' + Math.round(fs.statSync(out).size / 1048576) + ' MB\n');
