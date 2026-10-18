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
sub('android-aistudio/android/app/build.gradle.kts', /versionCode = \d+/, `versionCode = ${code}`);
sub('android-aistudio/android/app/build.gradle.kts', /versionName = "[^"]*"/, `versionName = "${v}"`);
sub('mobile/ios/App/App.xcodeproj/project.pbxproj', /MARKETING_VERSION = [\d.]+;/g, `MARKETING_VERSION = ${v};`);
sub('mobile/ios/App/App.xcodeproj/project.pbxproj', /CURRENT_PROJECT_VERSION = \d+;/g, `CURRENT_PROJECT_VERSION = ${code};`);
for (const f of ['BUILD-WINDOWS.txt', 'BUILD-MAC.txt', 'BUILD-ANDROID.txt', 'BUILD-IOS.txt']) {
  sub(f, /TILESMITH v[\d.]+/g, `TILESMITH v${v}`);
  sub(f, /header say "v[\d.]+"/g, `header say "v${v}"`);
  sub(f, /TileSmith-[\d.]+-mac-universal\.dmg/g, `TileSmith-${full}-mac-universal.dmg`);
  sub(f, /TileSmith v[\d.]+ \.\.\./g, `TileSmith v${v} ...`);
}

// Check: the app must now carry the version that was typed. If a pattern above stopped matching (the page text
// changed), fail the build instead of shipping an app that shows the wrong version.
const app = fs.readFileSync(path.join(root, 'app', 'index.html'), 'utf8');
const need = [`<title>TileSmith v${v} - LED Wall Builder</title>`, `color:var(--am)">v${v}</span></h1>`, `>Version ${v} · build `];
const miss = need.filter(x => !app.includes(x));
if (miss.length) { console.error('[set-version] ERROR: the app does not show version ' + v + '. Missing: ' + miss.join(' | ')); process.exit(1); }
console.log('[set-version] OK: the app shows version ' + v);
