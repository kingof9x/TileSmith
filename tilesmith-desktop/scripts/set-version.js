// Stamps a version into the files that carry it, so a release built from the workflow (Actions > Build and release >
// Run workflow, version box) names its files and shows its version in the app. Usage: node scripts/set-version.js 3.4
// (also accepts v3.4). Anything that is not a version number (for example a branch name) is ignored.
const fs = require('fs'), path = require('path');
const v = String(process.argv[2] || '').replace(/^v/, '');
if (!/^\d+(\.\d+){1,2}$/.test(v)) { console.log('[set-version] "' + (process.argv[2] || '') + '" is not a version number, nothing changed.'); process.exit(0); }
const root = path.join(__dirname, '..'), today = new Date().toISOString().slice(0, 10);
const full = v.split('.').length == 2 ? v + '.0' : v;                 // 3.4 -> 3.4.0 for package.json and file names
const code = String(v.split('.').concat(['0']).slice(0, 3).reduce((a, x) => a * 100 + (+x), 0));   // 3.4 -> 30400 (Android versionCode)
function sub(rel, pat, rep) {
  const p = path.join(root, rel); if (!fs.existsSync(p)) { console.log('[set-version] missing ' + rel); return; }
  const s = fs.readFileSync(p, 'utf8'), t = s.replace(pat, rep);
  console.log('[set-version] ' + rel + (s === t ? ' (unchanged)' : ' updated'));
  fs.writeFileSync(p, t);
}
sub('app/index.html', /<title>TileSmith v[\d.]+ - LED Wall Builder<\/title>/, `<title>TileSmith v${v} - LED Wall Builder</title>`);
sub('app/index.html', /color:var\(--am\)">v[\d.]+<\/span><\/h1>/, `color:var(--am)">v${v}</span></h1>`);
sub('app/index.html', />Version [\d.]+ ·[^<]*<\/div>/, `>Version ${v} · build ${today}</div>`);
sub('main.js', /title: 'TileSmith v[\d.]+ - LED Wall Builder'/, `title: 'TileSmith v${v} - LED Wall Builder'`);
sub('package.json', /"version": "[\d.]+"/, `"version": "${full}"`);
sub('mobile/package.json', /"version": "[\d.]+"/, `"version": "${full}"`);
sub('mobile/android/app/build.gradle', /versionCode \d+/, `versionCode ${code}`);
sub('mobile/android/app/build.gradle', /versionName "[^"]*"/, `versionName "${v}"`);
