// TileSmith Android bridge for the Google AI Studio build: a Kotlin + Jetpack Compose app that shows the TileSmith page
// (app/index.html, unchanged) in a WebView. The Kotlin side adds window.TileSmithAndroid (an @JavascriptInterface
// object, see TileSmithBridge.kt). This file turns it into the same window.TSM the Capacitor build gets from
// mobile/src/mobile-bridge.js, so the page behaves exactly like the Capacitor Android app:
//   saveFile(data, name, mime)  write the file, open the Android share sheet; resolves true when an app was picked
//   openStream(name)            a file written piece by piece (video recording); finish(true) shares it, finish(false) deletes it
//   openUrl(url)                open a link in the browser / mail app
//   keepAwake(on)               keep the screen on while a video records
// It must load before the app's own script (prepare-assets.js puts its <script> tag in front of it).
(function () {
  var A = window.TileSmithAndroid;
  if (!A) return; // not inside the Android app: do nothing, the page runs as the plain web version
  // the page treats itself as the mobile app when window.Capacitor.isNativePlatform() is true; there is no Capacitor
  // here, so answer that question (nothing else of Capacitor is used)
  if (!window.Capacitor) window.Capacitor = { isNativePlatform: function () { return true; }, getPlatform: function () { return 'android'; } };
  var CHUNK = 768 * 1024; // raw bytes per call (about 1 MB of base64): big files never cross the bridge as one huge string
  var waits = {}, seq = 0;
  // Kotlin calls this when the share sheet closes: ok = an app was picked, err = a message when sharing failed
  window.__tsmDone = function (id, ok, err) {
    var w = waits[id]; if (!w) return; delete waits[id];
    if (err) w.rej(new Error(err)); else w.res(!!ok);
  };
  function b64(blob) {
    return new Promise(function (res, rej) {
      var r = new FileReader();
      r.onload = function () { var s = String(r.result); res(s.slice(s.indexOf(',') + 1)); };
      r.onerror = function () { rej(r.error || new Error('could not read the data')); };
      r.readAsDataURL(blob);
    });
  }
  // every Kotlin method returns "" when it worked, otherwise the error message
  function check(r) { if (r) throw new Error(String(r)); }
  async function write(name, blob, append) {
    for (var i = 0, first = !append; i < blob.size || first; i += CHUNK) {
      check(A.writeChunk(name, await b64(blob.slice(i, i + CHUNK)), !first));
      first = false;
      if (!blob.size) break;
    }
  }
  function share(name, mime) {
    return new Promise(function (res, rej) {
      var id = 's' + (++seq);
      waits[id] = { res: res, rej: rej };
      try { check(A.shareFile(name, mime || '', id)); } catch (e) { delete waits[id]; rej(e); }
    });
  }
  var safe = function (n) { return String(n || 'tilesmith').replace(/[\\/:*?"<>|]+/g, '-'); };
  window.TSM = {
    platform: 'android',
    saveFile: async function (data, name, mime) {
      var blob = data instanceof Blob ? data : new Blob([data], { type: mime || 'application/octet-stream' }), n = safe(name);
      await write(n, blob, false);
      return share(n, mime || blob.type);
    },
    openStream: function (name) {
      var n = safe(name), q = Promise.resolve(), err = null, started = false;
      return {
        append: function (blob) {
          q = q.then(function () { return write(n, blob, started).then(function () { started = true; }); }).catch(function (e) { err = err || e; });
        },
        finish: async function (keep) {
          await q;
          if (!keep) { if (started) try { A.deleteFile(n); } catch (e) {} return false; }
          if (err) throw err;
          if (!started) throw new Error('nothing was recorded');
          return share(n, 'video/mp4');
        }
      };
    },
    openUrl: function (url) { try { check(A.openUrl(String(url))); } catch (e) { console.error(e); } },
    keepAwake: function (on) { try { A.keepAwake(!!on); } catch (e) {} }
  };
})();
