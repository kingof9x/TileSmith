// Copies the shared TileSmith page (../app) into www/ for the mobile build and adds the two mobile scripts in front of
// the app's own script: Capacitor's runtime (capacitor.js) and TileSmith's mobile bridge (src/mobile-bridge.js).
// app/index.html itself is never changed, so the desktop and web builds stay exactly as they are.
// Run by "npm run sync", "npm run android" and "npm run ios".
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'), app = path.join(root, '..', 'app'), www = path.join(root, 'www');
const core = path.join(root, 'node_modules', '@capacitor', 'core', 'dist', 'capacitor.js');
if (!fs.existsSync(path.join(app, 'index.html'))) { console.error('[STOP] ../app/index.html not found. The mobile folder must stay inside the TileSmith project folder.'); process.exit(1); }
if (!fs.existsSync(core)) { console.error('[STOP] Capacitor is not installed yet. In the mobile folder run:  npm install'); process.exit(1); }
fs.rmSync(www, { recursive: true, force: true });
fs.cpSync(app, www, { recursive: true });
fs.copyFileSync(core, path.join(www, 'capacitor.js'));
fs.copyFileSync(path.join(root, 'src', 'mobile-bridge.js'), path.join(www, 'mobile-bridge.js'));
const f = path.join(www, 'index.html'); let html = fs.readFileSync(f, 'utf8');
// an app, not a web page: pinching zooms the TileSmith viewport, never the whole page
html = html.replace(/<meta name="viewport" content="([^"]*)">/, (m, c) => `<meta name="viewport" content="${c.replace(/,\s*(maximum-scale|user-scalable)=[^,]*/g, '')}, maximum-scale=1, user-scalable=no">`);
const at = html.indexOf('<script>');
if (at < 0) { console.error('[STOP] could not find the app script in index.html'); process.exit(1); }
html = html.slice(0, at) + '<script src="capacitor.js"></script><script src="mobile-bridge.js"></script>\n' + html.slice(at);
fs.writeFileSync(f, html);
const v = (html.match(/<title>([^<]*)<\/title>/) || [])[1] || 'TileSmith';
console.log(`[ok] www is ready: ${v} (${Math.round(html.length / 1024)} KB) + Capacitor runtime + mobile bridge`);
