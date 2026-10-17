const { app, BrowserWindow, ipcMain, powerSaveBlocker } = require('electron');

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

app.whenReady().then(() => {
  const w = new BrowserWindow({
    width: 1500, height: 900, backgroundColor: '#0d1217', title: 'TileSmith v3.3 - LED Wall Builder',
    icon: require('path').join(__dirname, 'app', 'icon.png'), autoHideMenuBar: true,
    webPreferences: { nodeIntegration: true, contextIsolation: false, backgroundThrottling: false }
  });
  // Windows the page opens (the spec sheet) get a normal title bar so they can be moved and closed.
  w.webContents.setWindowOpenHandler(() => ({
    action: 'allow',
    overrideBrowserWindowOptions: { width: 900, height: 900, backgroundColor: '#ffffff', autoHideMenuBar: true }
  }));
  w.loadFile('app/index.html');
});
app.on('window-all-closed', () => app.quit());
