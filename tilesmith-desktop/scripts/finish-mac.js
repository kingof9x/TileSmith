// Runs after "npm run dist:mac": copies the .dmg and the .pkg installer to the project folder so they are easy to find.
//   .dmg  open it and drag TileSmith to Applications
//   .pkg  installer: double-click, Continue, Install; puts TileSmith in /Applications
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'), dist = path.join(root, 'dist');
const files = fs.existsSync(dist) ? fs.readdirSync(dist) : [];
const out = [];
for (const ext of ['.dmg', '.pkg']) {
  const f = files.find(n => n.endsWith(ext));
  if (!f) { console.error('No ' + ext + ' found in dist/. The build failed - see the errors above.'); process.exit(1); }
  fs.copyFileSync(path.join(dist, f), path.join(root, f)); out.push(path.join(root, f));
}
console.log('\nDONE. Mac downloads (Apple Silicon + Intel):\n' + out.map(f => '  ' + f + '  (' + Math.round(fs.statSync(f).size / 1048576) + ' MB)').join('\n') + '\n');
