// TileSmith mobile bridge (Android and iOS). Loaded before the app page in the mobile build only; the desktop and web
// builds never see it. Gives the shared page (app/index.html) what it needs from the phone or tablet through Capacitor
// plugins: saving and sharing files (share sheet: Save to Files, Google Drive, AirDrop, e-mail ...), streaming a long
// recording to a file, opening links in the system browser, and keeping the screen on while recording.
(function () {
  var C = window.Capacitor;
  if (!C || typeof C.isNativePlatform !== 'function' || !C.isNativePlatform()) return;
  var reg = function (n) { return C.registerPlugin(n); };
  var Filesystem = reg('Filesystem'), Share = reg('Share'), Browser = reg('Browser'), KeepAwake = reg('KeepAwake');
  var DIR = 'CACHE', CHUNK = 3 * 1024 * 1024; // 3 MB pieces: big files never sit in memory as one huge string
  function b64(blob) {
    return new Promise(function (res, rej) {
      var r = new FileReader();
      r.onload = function () { var s = String(r.result); res(s.slice(s.indexOf(',') + 1)); };
      r.onerror = function () { rej(r.error || new Error('could not read the data')); };
      r.readAsDataURL(blob);
    });
  }
  async function write(path, blob, append) {
    for (var i = 0, first = !append; i < blob.size || first; i += CHUNK) {
      var data = await b64(blob.slice(i, i + CHUNK));
      if (first) await Filesystem.writeFile({ path: path, data: data, directory: DIR, recursive: true });
      else await Filesystem.appendFile({ path: path, data: data, directory: DIR });
      first = false;
      if (!blob.size) break;
    }
  }
  async function share(path, name) {
    var uri = (await Filesystem.getUri({ path: path, directory: DIR })).uri;
    try { await Share.share({ title: name, files: [uri], dialogTitle: 'Save or send ' + name }); }
    catch (e) { if (!/cancel/i.test(String(e && (e.message || e)))) throw e; return false; }
    return true;
  }
  var safe = function (n) { return String(n || 'tilesmith').replace(/[\\/:*?"<>|]+/g, '-'); };
  window.TSM = {
    platform: C.getPlatform(),
    // save a Blob or text to a file and open the share sheet; resolves true when shared, false when the sheet was closed
    saveFile: async function (data, name, mime) {
      var blob = data instanceof Blob ? data : new Blob([data], { type: mime || 'application/octet-stream' }), path = 'exports/' + safe(name);
      await write(path, blob, false);
      return share(path, safe(name));
    },
    // a file written piece by piece (video recording); finish(true) opens the share sheet, finish(false) deletes it
    openStream: function (name) {
      var path = 'exports/' + safe(name), q = Promise.resolve(), err = null, started = false;
      return {
        append: function (blob) {
          q = q.then(function () { return write(path, blob, started).then(function () { started = true; }); }).catch(function (e) { err = err || e; });
        },
        finish: async function (keep) {
          await q;
          if (!keep) { if (started) try { await Filesystem.deleteFile({ path: path, directory: DIR }); } catch (e) {} return false; }
          if (err) throw err;
          if (!started) throw new Error('nothing was recorded');
          return share(path, safe(name));
        }
      };
    },
    openUrl: function (url) { if (/^https?:/i.test(url)) return Browser.open({ url: url }); location.href = url; },
    keepAwake: function (on) { try { return on ? KeepAwake.keepAwake() : KeepAwake.allowSleep(); } catch (e) {} }
  };
})();
