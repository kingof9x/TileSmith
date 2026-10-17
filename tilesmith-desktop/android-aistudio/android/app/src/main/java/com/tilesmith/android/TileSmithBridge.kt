package com.tilesmith.android

// window.TileSmithAndroid inside the page. webview-bridge.js (loaded before the app's script) wraps these methods into
// window.TSM, the same interface the Capacitor build has. Methods run on WebView's JavaBridge thread, so anything that
// touches the activity or its window is posted to the UI thread. Every method that can fail returns "" when it worked,
// otherwise the error message (the page shows it in a toast).

import android.util.Base64
import android.webkit.JavascriptInterface
import java.io.File
import java.io.FileOutputStream

class TileSmithBridge(private val activity: MainActivity) {

    // files are written to the app's cache folder, then shared from there through the FileProvider (res/xml/file_paths.xml)
    private fun file(name: String): File {
        val dir = File(activity.cacheDir, "exports")
        dir.mkdirs()
        val safe = File(name).name.replace(Regex("[\\\\/:*?\"<>|]+"), "-").ifBlank { "tilesmith" }
        return File(dir, safe)
    }

    /** Writes one piece of a file. base64 = the bytes; append = false starts a new file. */
    @JavascriptInterface
    fun writeChunk(name: String, base64: String, append: Boolean): String = try {
        val bytes = Base64.decode(base64, Base64.DEFAULT)
        FileOutputStream(file(name), append).use { it.write(bytes) }
        ""
    } catch (e: Throwable) {
        e.message ?: e.toString()
    }

    /** Deletes a file (a cancelled video recording). */
    @JavascriptInterface
    fun deleteFile(name: String): String {
        file(name).delete()
        return ""
    }

    /** Opens the share sheet for a written file. The answer comes back later as window.__tsmDone(callbackId, ok, error). */
    @JavascriptInterface
    fun shareFile(name: String, mime: String, callbackId: String): String {
        val f = file(name)
        if (!f.exists()) return "file not found: $name"
        activity.runOnUiThread { activity.share(f, mime, callbackId) }
        return ""
    }

    /** Opens a web link in the browser or a mailto: link in the e-mail app. */
    @JavascriptInterface
    fun openUrl(url: String): String {
        activity.runOnUiThread { activity.openExternal(url) }
        return ""
    }

    /** Keeps the screen on while a video records. */
    @JavascriptInterface
    fun keepAwake(on: Boolean) {
        activity.runOnUiThread { activity.keepScreenOn(on) }
    }
}
