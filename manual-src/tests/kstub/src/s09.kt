@file:Suppress("unused", "UNUSED_PARAMETER")
package android.webkit
import android.net.Uri
annotation class JavascriptInterface
fun interface ValueCallback<T> { fun onReceiveValue(value: T?) }
class MimeTypeMap { fun getMimeTypeFromExtension(e: String?): String? = TODO(); companion object { @JvmStatic fun getSingleton(): MimeTypeMap = TODO() } }
class WebResourceResponse
interface WebResourceRequest { val url: Uri }
class WebSettings { var javaScriptEnabled = false; var domStorageEnabled = false; var mediaPlaybackRequiresUserGesture = true
  var allowFileAccess = true; var builtInZoomControls = false; fun setSupportZoom(b: Boolean) {} }
open class WebViewClient {
  open fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? = null
  open fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean = false }
open class WebChromeClient {
  abstract class FileChooserParams { abstract fun createIntent(): android.content.Intent?
    companion object { @JvmStatic fun parseResult(resultCode: Int, data: android.content.Intent?): Array<Uri>? = TODO() } }
  open fun onShowFileChooser(webView: WebView?, filePathCallback: ValueCallback<Array<Uri>>?, fileChooserParams: FileChooserParams?): Boolean = false }
open class WebView(c: android.content.Context?) : android.view.ViewGroup(c) {
  val settings: WebSettings get() = TODO(); var webViewClient: WebViewClient = WebViewClient(); var webChromeClient: WebChromeClient? = null
  fun addJavascriptInterface(o: Any?, name: String?) {}; fun removeJavascriptInterface(name: String?) {}
  fun loadUrl(u: String?) {}; fun evaluateJavascript(s: String?, cb: ValueCallback<String>?) {}
  fun onPause() {}; fun onResume() {}; fun destroy() {}
  companion object { @JvmStatic fun setWebContentsDebuggingEnabled(b: Boolean) {} } }

// ---------------------------------------------------------------- androidx.*
