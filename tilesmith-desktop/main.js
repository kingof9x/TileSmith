const { app, BrowserWindow, ipcMain, powerSaveBlocker, screen } = require('electron');

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
// an output window: borderless and full screen on the display named in its frame name ("tsout:<display id>:<canvas>")
const outDisplay = (name) => { const m = /^tsout:([^:]+):/.exec(name || ''); return m ? screen.getAllDisplays().find((d) => String(d.id) === m[1]) : null; };

app.whenReady().then(() => {
  const w = new BrowserWindow({
    width: 1500, height: 900, backgroundColor: '#0d1217', title: 'TileSmith v3.5 - LED Wall Builder',
    icon: require('path').join(__dirname, 'app', 'icon.png'), autoHideMenuBar: true,
    webPreferences: { nodeIntegration: true, contextIsolation: false, backgroundThrottling: false }
  });
  // Windows the page opens (the spec sheet) get a normal title bar so they can be moved and closed.
  w.webContents.setWindowOpenHandler(({ frameName }) => {
    const d = outDisplay(frameName);
    if (d) return { action: 'allow', overrideBrowserWindowOptions: { ...d.bounds, frame: false, resizable: false, movable: false, fullscreenable: true, hasShadow: false,
      enableLargerThanScreen: true, backgroundColor: '#000000', autoHideMenuBar: true, title: 'TileSmith output', webPreferences: { backgroundThrottling: false } } };
    return { action: 'allow', overrideBrowserWindowOptions: { width: 900, height: 900, backgroundColor: '#ffffff', autoHideMenuBar: true } };
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
