// Runs the real desktop app (tilesmith-desktop/main.js) in Electron, waits for the page, runs the JavaScript in ETEST_JS
// inside it, prints "RESULT <json>" and quits. Used by electron_test.py; ETEST_DIR is the tilesmith-desktop folder.
const { app, BrowserWindow } = require('electron');
const DIR=process.env.ETEST_DIR;process.chdir(DIR);
// main.js loads 'app/index.html' relative to the app folder; this harness is the app here, so point it at ETEST_DIR
const _lf = BrowserWindow.prototype.loadFile; BrowserWindow.prototype.loadFile = function (f, o) { return _lf.call(this, require('path').resolve(DIR, f), o); };
require(require('path').join(DIR, 'main.js'));
app.on('browser-window-created', (e, w) => {
  w.webContents.on('console-message', (ev, level, msg) => { if (level >= 2 && !/Security Warning/.test(msg)) console.log('[renderer]', msg.slice(0, 300)); });
  w.webContents.on('did-finish-load', async () => {
    if (w.__done || w.getParentWindow()) return; w.__done = true;   // the main window only, not output / print windows
    await new Promise(r => setTimeout(r, 2500));
    const js = process.env.ETEST_JS || '1';
    try { console.log('RESULT', JSON.stringify(await w.webContents.executeJavaScript(js))); } catch (err) { console.log('RESULT-ERR', err.message); }
    console.log('windows', BrowserWindow.getAllWindows().length, 'mem MB', Math.round(process.memoryUsage().rss/1048576));
    setTimeout(() => app.exit(0), 500);
  });
});
