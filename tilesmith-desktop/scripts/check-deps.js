// Runs before every build. TileSmith only needs koffi at run time (electron and electron-builder are build tools).
// Anything else in "dependencies" gets packed into the app, so stop and explain how to remove it.
// Common cause: typing "npm install dist" or "npm i dist" instead of "npm run dist".
const p = require('../package.json');
const allowed = { dependencies: ['koffi'], devDependencies: ['electron', 'electron-builder'] };
const extra = [];
for (const k of Object.keys(allowed)) for (const name of Object.keys(p[k] || {})) if (!allowed[k].includes(name)) extra.push(name);
if (extra.length) {
  console.error('\n[STOP] package.json contains package(s) TileSmith does not use: ' + extra.join(', '));
  if (extra.includes('dist')) console.error('  "dist" is an old, unrelated npm package (it pulls in a vulnerable uglify-js). It gets installed by');
  if (extra.includes('dist')) console.error('  typing "npm install dist" instead of "npm run dist".');
  console.error('  Remove it, then build again:');
  console.error('     npm uninstall ' + extra.join(' '));
  console.error('     npm run clean');
  console.error('     npm install');
  console.error('     npm run dist        (Mac: npm run dist:mac)\n');
  process.exit(1);
}
console.log('[ok] dependencies: only koffi (plus electron and electron-builder for building).');
