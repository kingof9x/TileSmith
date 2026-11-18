// Runs after "npm run dist": copies the two Windows downloads to the project root and removes the folder-dependent exe.
//   TileSmith-Portable.exe          stand-alone app, no install (copy this one file anywhere)
//   TileSmith-<ver>-windows-setup.exe  installer: Start menu and desktop shortcuts, an uninstaller, installs per user
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'), dist = path.join(root, 'dist');
const src = path.join(dist, 'TileSmith-Portable.exe');
if (!fs.existsSync(src)) { console.error('Portable exe not found in dist/. Build failed - see errors above.'); process.exit(1); }
const setup = fs.readdirSync(dist).find(n => /-windows-setup\.exe$/.test(n));
if (!setup) { console.error('Installer (TileSmith-*-windows-setup.exe) not found in dist/. Build failed - see errors above.'); process.exit(1); }
const out = path.join(root, 'TileSmith-Portable.exe'), outSetup = path.join(root, setup);
fs.copyFileSync(src, out);
fs.copyFileSync(path.join(dist, setup), outSetup);
fs.rmSync(path.join(dist, 'win-unpacked'), { recursive: true, force: true });
const mb = f => Math.round(fs.statSync(f).size / 1048576) + ' MB';
console.log('\nDONE.\n  Stand-alone app (copy this one file anywhere): ' + out + '  (' + mb(out) + ')' +
  '\n  Installer (Start menu, desktop shortcut, uninstaller): ' + outSetup + '  (' + mb(outSetup) + ')\n');
