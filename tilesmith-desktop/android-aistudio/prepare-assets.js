// Makes the "tilesmith" assets folder for the Google AI Studio / Kotlin Android app: a copy of the shared TileSmith page
// (../app/index.html, never changed itself) with webview-bridge.js loaded in front of the app's script, plus the bridge.
// The Android project expects it at  app/src/main/assets/tilesmith/
//   node prepare-assets.js              -> writes android/app/src/main/assets/tilesmith (the Android project next to this file)
//   node prepare-assets.js <folder>     -> writes <folder>/tilesmith (for example the assets folder of the AI Studio project)
const fs = require('fs'), path = require('path');
const here = __dirname, app = path.join(here, '..', 'app', 'index.html');
const out = path.join(path.resolve(process.argv[2] || path.join(here, 'android', 'app', 'src', 'main', 'assets')), 'tilesmith');
if (!fs.existsSync(app)) { console.error('[STOP] ../app/index.html not found. Keep this folder inside the TileSmith project folder.'); process.exit(1); }
let html = fs.readFileSync(app, 'utf8');
// an app, not a web page: pinching zooms the TileSmith viewport, never the whole page (same as the Capacitor build)
html = html.replace(/<meta name="viewport" content="([^"]*)">/, (m, c) => `<meta name="viewport" content="${c.replace(/,\s*(maximum-scale|user-scalable)=[^,]*/g, '')}, maximum-scale=1, user-scalable=no">`);
const at = html.indexOf('<script>');
if (at < 0) { console.error('[STOP] could not find the app script in index.html'); process.exit(1); }
html = html.slice(0, at) + '<script src="webview-bridge.js"></script>\n' + html.slice(at);
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, 'index.html'), html);
fs.copyFileSync(path.join(here, 'webview-bridge.js'), path.join(out, 'webview-bridge.js'));
const v = (html.match(/<title>([^<]*)<\/title>/) || [])[1] || 'TileSmith';
console.log(`[ok] ${out} is ready: ${v} (${Math.round(html.length / 1024)} KB) + webview-bridge.js`);
