// Runs after "npm run dist": leaves ONE stand-alone file in the project root and removes the folder-dependent exe.
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'), dist = path.join(root, 'dist');
const src = path.join(dist, 'TileSmith-Portable.exe');
if (!fs.existsSync(src)) { console.error('Portable exe not found in dist/. Build failed - see errors above.'); process.exit(1); }
const out = path.join(root, 'TileSmith-Portable.exe');
fs.copyFileSync(src, out);
fs.rmSync(path.join(dist, 'win-unpacked'), { recursive: true, force: true });
console.log('\nDONE. Stand-alone app (copy this one file anywhere):\n  ' + out + '\nSize: ' + Math.round(fs.statSync(out).size / 1048576) + ' MB\n');
