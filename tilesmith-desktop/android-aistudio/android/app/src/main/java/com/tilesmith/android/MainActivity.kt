package com.tilesmith.android

// TileSmith for Android (Google AI Studio build). One activity, Jetpack Compose UI. The whole TileSmith app is the
// shared page app/src/main/assets/tilesmith/index.html (the same page as the desktop, web and Capacitor builds), shown
// full screen in a WebView. TileSmithBridge.kt gives the page what it needs from Android: saving and sharing files,
// streaming a video recording to a file, opening links and keeping the screen on.

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.res.Configuration
import android.net.Uri
import android.os.Bundle
import android.view.ViewGroup
import android.view.WindowManager
import android.webkit.MimeTypeMap
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.FileProvider
import androidx.webkit.WebViewAssetLoader
import org.json.JSONObject
import java.io.File

class MainActivity : ComponentActivity() {

    companion object {
        // WebViewAssetLoader serves app/src/main/assets/ at this https address, so the page gets a normal secure
        // origin: localStorage (saved settings), canvas capture and MediaRecorder all work as in a browser
        const val HOST = "appassets.androidplatform.net"
        const val START_URL = "https://$HOST/assets/tilesmith/index.html"
        val DARK_BG = Color(0xFF0D1217)   // the page's dark background (--bg)
        val LIGHT_BG = Color(0xFFF1F3F5)  // the page's light background
    }

    private var web: WebView? = null

    // <input type="file"> in the page (pattern image, logo, face photo uploads)
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private val pickFiles = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        fileCallback?.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(r.resultCode, r.data))
        fileCallback = null
    }

    // the share sheet. Like Capacitor's Share plugin: it counts as shared when the sheet returns OK or when this app
    // was sent to the background while it was open (an app was picked); otherwise the person closed it
    private var shareId: String? = null
    private var leftWhileSharing = false
    private val shareSheet = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val id = shareId ?: return@registerForActivityResult
        shareId = null
        done(id, r.resultCode != RESULT_CANCELED || leftWhileSharing, null)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        cleanOldExports()
        val hasPage = try { assets.list("tilesmith")?.contains("index.html") == true } catch (e: Exception) { false }
        if (hasPage) web = makeWebView()
        setContent {
            val bg = if (isSystemInDarkTheme()) DARK_BG else LIGHT_BG
            // the page never sits under the status bar, navigation bar, camera cut-out or keyboard
            Box(Modifier.fillMaxSize().background(bg).windowInsetsPadding(WindowInsets.safeDrawing)) {
                val w = web
                if (w != null) {
                    AndroidView(factory = { (w.parent as? ViewGroup)?.removeView(w); w }, modifier = Modifier.fillMaxSize())
                } else {
                    MissingPage(bg)
                }
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun makeWebView(): WebView {
        WebView.setWebContentsDebuggingEnabled((applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0)
        val loader = WebViewAssetLoader.Builder()
            .setDomain(HOST)
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()
        return WebView(this).apply {
            layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
            val night = (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES
            setBackgroundColor(if (night) 0xFF0D1217.toInt() else 0xFFF1F3F5.toInt()) // no white flash while loading
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true            // saved settings live in localStorage
            settings.mediaPlaybackRequiresUserGesture = false
            settings.allowFileAccess = false             // everything comes through the asset loader
            settings.setSupportZoom(false)               // pinch zooms the TileSmith viewport, not the page
            settings.builtInZoomControls = false
            addJavascriptInterface(TileSmithBridge(this@MainActivity), "TileSmithAndroid")
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? =
                    request?.let { loader.shouldInterceptRequest(it.url) }

                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                    val url = request?.url ?: return false
                    if (url.host == HOST) return false
                    openExternal(url.toString())   // web links, Ko-fi, e-mail: open outside the app
                    return true
                }
            }
            webChromeClient = object : WebChromeClient() {
                // alert() and confirm() use WebView's own dialogs (WebChromeClient's defaults)
                override fun onShowFileChooser(view: WebView?, callback: ValueCallback<Array<Uri>>?, params: FileChooserParams?): Boolean {
                    if (callback == null || params == null) return false
                    val pick = params.createIntent() ?: return false
                    fileCallback?.onReceiveValue(null)
                    fileCallback = callback
                    return try {
                        pickFiles.launch(pick); true
                    } catch (e: ActivityNotFoundException) {
                        fileCallback = null; false
                    }
                }
            }
            loadUrl(START_URL)
        }
    }

    // ---- called by TileSmithBridge (always on the UI thread)

    fun share(file: File, mime: String, id: String) {
        if (shareId != null) { done(id, false, "Can't share while sharing is in progress"); return }
        try {
            val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file)
            val type = mime.ifBlank { MimeTypeMap.getSingleton().getMimeTypeFromExtension(file.extension.lowercase()) ?: "application/octet-stream" }
            val send = Intent(Intent.ACTION_SEND).apply {
                setType(type)
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, file.name)
                clipData = ClipData.newRawUri("", uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            shareId = id
            leftWhileSharing = false
            shareSheet.launch(Intent.createChooser(send, "Save or send ${file.name}"))
        } catch (e: Exception) {
            shareId = null
            done(id, false, e.message ?: "could not open the share sheet")
        }
    }

    fun openExternal(url: String) {
        val uri = Uri.parse(url)
        val intent = if (uri.scheme == "mailto") Intent(Intent.ACTION_SENDTO, uri) else Intent(Intent.ACTION_VIEW, uri)
        try {
            startActivity(intent)
        } catch (e: ActivityNotFoundException) {
            Toast.makeText(this, "No app on this device can open $url", Toast.LENGTH_LONG).show()
        }
    }

    fun keepScreenOn(on: Boolean) {
        if (on) window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        else window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }

    // tells the page how a share ended: window.__tsmDone(id, ok, error)
    private fun done(id: String, ok: Boolean, err: String?) {
        val e = if (err == null) "null" else JSONObject.quote(err)
        web?.evaluateJavascript("window.__tsmDone&&window.__tsmDone(${JSONObject.quote(id)},$ok,$e)", null)
    }

    // exported files are shared straight away; anything older than a day is left over and only takes up space
    private fun cleanOldExports() {
        val old = System.currentTimeMillis() - 24L * 60 * 60 * 1000
        File(cacheDir, "exports").listFiles()?.forEach { if (it.lastModified() < old) it.delete() }
    }

    // ---- lifecycle

    override fun onStop() {
        super.onStop()
        if (shareId != null) leftWhileSharing = true
    }

    override fun onPause() {
        super.onPause()
        web?.onPause()      // the page sees "hidden" and saves its settings
    }

    override fun onResume() {
        super.onResume()
        web?.onResume()
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        enableEdgeToEdge()  // status bar icons follow a light/dark switch (the activity is not recreated)
    }

    override fun onDestroy() {
        web?.apply { removeJavascriptInterface("TileSmithAndroid"); destroy() }
        web = null
        super.onDestroy()
    }
}

// shown only when app/src/main/assets/tilesmith/index.html is missing from the project
@Composable
fun MissingPage(bg: Color) {
    val fg = if (bg == MainActivity.DARK_BG) Color(0xFFE6EDF3) else Color(0xFF16202A)
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("TileSmith", color = Color(0xFF22D3EE), fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Text("The TileSmith page is not in this app yet.", color = fg, fontSize = 18.sp)
        Text(
            "Add the folder android-assets/tilesmith from the TileSmith AI Studio kit as " +
                "app/src/main/assets/tilesmith (it holds index.html and webview-bridge.js), then build and run again.",
            color = fg, fontSize = 15.sp
        )
    }
}
