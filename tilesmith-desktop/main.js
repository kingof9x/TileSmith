// TileSmith desktop: Electron's main process. It is deliberately small: it opens one window on app/index.html (the
// whole app, see the map at the top of its main script) and gives the page the few things a web page cannot do itself:
//   - keep running at full speed when covered or minimised (switches below) and stop the system sleeping while an output runs
//   - list the displays (ts-displays) and place full-screen output windows on them (window open handler)
//   - capture the window for bug reports (ts-capture), and start the updater job, then quit (ts-update-run, ts-quit)
// Everything else (files, NDI®, Spout / Syphon, ffmpeg) the page does itself through Node.js (nodeIntegration on). That
// is why this file refuses to let the window or its child windows show any page other than the app (see below).
const { app, BrowserWindow, ipcMain, powerSaveBlocker, screen, shell } = require('electron');

// http(s) and mailto links: the only kinds handed to the system browser / mail app
const isWeb = (u) => /^(https?|mailto):/i.test(u || '');

// Keep full speed when TileSmith is behind other windows or minimised, so NDI®, Spout and Syphon output and video recording
// do not slow down while you watch the output in another app. Without these, Chromium lowers the priority of
// covered or hidden windows (and Windows 11 can put them in "Efficiency mode").
app.commandLine.appendSwitch('disable-renderer-backgrounding');
app.commandLine.appendSwitch('disable-background-timer-throttling');
app.commandLine.appendSwitch('disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('disable-features', 'CalculateNativeWinOcclusion');

// While NDI®, Spout or Syphon output or a recording is running, stop the system from suspending or napping the app (macOS App Nap).
let blocker = null;
ipcMain.on('output-active', (e, on) => {
  if (on && blocker === null) blocker = powerSaveBlocker.start('prevent-app-suspension');
  else if (!on && blocker !== null) { powerSaveBlocker.stop(blocker); blocker = null; }
});

// Displays for "Send this canvas to a display": size in device pixels, scaling, and which one shows the TileSmith window.
ipcMain.handle('ts-displays', (e) => {
  const win = BrowserWindow.fromWebContents(e.sender), here = win ? screen.getDisplayMatching(win.getBounds()).id : null;
  return screen.getAllDisplays().map((d) => ({ id: d.id, label: d.label || '', bounds: d.bounds, scale: d.scaleFactor,
    px: [Math.round(d.bounds.width * d.scaleFactor), Math.round(d.bounds.height * d.scaleFactor)], main: d.id === here, primary: d.id === screen.getPrimaryDisplay().id }));
});
// Report a bug: a screenshot of the whole app window (panels, toolbar and canvases), not just the wall canvas
// Update now: the page has started the new version's installer and asks to close (the installer waits for this process)
ipcMain.on('ts-quit', () => app.quit());
// Update now: start the installer job from this (main) process, which keeps running after the window closes, then quit.
// The job waits for this process (%TSPID%) to end before it installs.
ipcMain.on('ts-update-run', (e, job) => {
  try {
    if (job && job.cmd) require('child_process').spawn(job.cmd, job.args.map((a) => String(a).split('%TSPID%').join(String(process.pid))),
      { detached: true, stdio: 'ignore', windowsHide: true }).unref();
  } catch (err) { console.error('update job', err); }
  app.quit();
});
ipcMain.handle('ts-capture', async (e) => (await e.sender.capturePage()).toDataURL());
// an output window: borderless and full screen on the display named in its frame name ("tsout:<display id>:<canvas>")
const outDisplay = (name) => { const m = /^tsout:([^:]+):/.exec(name || ''); return m ? screen.getAllDisplays().find((d) => String(d.id) === m[1]) : null; };

app.whenReady().then(() => {
  const w = new BrowserWindow({
    width: 1500, height: 900, backgroundColor: '#0d1217', title: 'TileSmith v3.5 - LED Wall Builder',
    icon: require('path').join(__dirname, 'app', 'icon.png'), autoHideMenuBar: true,
    webPreferences: { nodeIntegration: true, contextIsolation: false, backgroundThrottling: false }
  });
  // Windows the page opens: output windows (borderless, one per display) and blank windows the page writes into itself
  // (spec sheet, label print preview), which get a normal title bar so they can be moved and closed. The page runs with
  // Node.js (nodeIntegration) and these same-origin child windows share its process and its Node.js access (checked in
  // Electron 44), so they may only ever show what the page writes into them: any address other than about:blank is
  // refused, and web links go to the system browser instead of opening inside the app.
  w.webContents.setWindowOpenHandler(({ url, frameName }) => {
    if (isWeb(url)) { shell.openExternal(url); return { action: 'deny' }; }
    if (url && url !== 'about:blank') return { action: 'deny' };
    const d = outDisplay(frameName);
    if (d) return { action: 'allow', overrideBrowserWindowOptions: { ...d.bounds, frame: false, resizable: false, movable: false, fullscreenable: true, hasShadow: false,
      enableLargerThanScreen: true, backgroundColor: '#000000', autoHideMenuBar: true, title: 'TileSmith output', webPreferences: { backgroundThrottling: false } } };
    return { action: 'allow', overrideBrowserWindowOptions: { width: 900, height: 900, backgroundColor: '#ffffff', autoHideMenuBar: true } };
  });
  // The app window only ever shows app/index.html. A link or a dropped file that would navigate it elsewhere is stopped;
  // web and mail links open in the system browser / mail app instead.
  w.webContents.on('will-navigate', (e, url) => {
    if (url === w.webContents.getURL()) return;   // a reload of the app itself
    e.preventDefault();
    if (isWeb(url)) shell.openExternal(url);
  });
  // put each output window exactly over its display, above the taskbar / menu bar
  w.webContents.on('did-create-window', (child, { frameName }) => {
    const d = outDisplay(frameName); if (!d) return;
    child.setBounds(d.bounds);
    if (process.platform === 'darwin') child.setSimpleFullScreen(true); else child.setFullScreen(true);
    child.setAlwaysOnTop(true, 'screen-saver'); child.setMenuBarVisibility(false);
  });
  const changed = () => { if (!w.isDestroyed()) w.webContents.send('ts-displays-changed'); };
  screen.on('display-added', changed); screen.on('display-removed', changed); screen.on('display-metrics-changed', changed);
  // closing the main window closes the outputs too
  w.on('closed', () => app.quit());
  w.loadFile('app/index.html');
});
app.on('window-all-closed', () => app.quit());
