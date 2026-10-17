// Minimal stand-ins for the Android / AndroidX / Compose APIs MainActivity.kt and TileSmithBridge.kt use, with the real
// signatures (Java platform types shown as nullable where Java allows null). Only for a type check of the Kotlin code.
@file:Suppress("unused", "UNUSED_PARAMETER")
package android.annotation
annotation class SuppressLint(vararg val value: String)

// ---------------------------------------------------------------- android.*
package android.os
class Bundle

package android.net
abstract class Uri { abstract val host: String?; abstract val scheme: String?
  companion object { @JvmStatic fun parse(s: String?): Uri = TODO() } }

package android.content.pm
class ApplicationInfo { @JvmField var flags: Int = 0; companion object { const val FLAG_DEBUGGABLE = 2 } }

package android.content.res
class Configuration { @JvmField var uiMode: Int = 0
  companion object { const val UI_MODE_NIGHT_MASK = 48; const val UI_MODE_NIGHT_YES = 32 } }
class Resources { val configuration: Configuration get() = TODO() }
class AssetManager { fun list(path: String): Array<String>? = TODO() }

package android.content
import android.net.Uri
open class Context { val cacheDir: java.io.File get() = TODO(); val packageName: String get() = TODO()
  val resources: android.content.res.Resources get() = TODO(); val assets: android.content.res.AssetManager get() = TODO()
  val applicationInfo: android.content.pm.ApplicationInfo get() = TODO()
  open fun startActivity(i: Intent?) {} }
class ActivityNotFoundException : RuntimeException()
class ClipData { companion object { @JvmStatic fun newRawUri(label: CharSequence?, uri: Uri?): ClipData = TODO() } }
class Intent(action: String?, uri: Uri? = null) {
  fun setType(t: String?): Intent = this
  fun putExtra(n: String?, v: android.os.Parcelable?): Intent = this
  fun putExtra(n: String?, v: String?): Intent = this
  var clipData: ClipData? = null
  fun addFlags(f: Int): Intent = this
  companion object { const val ACTION_SEND = "s"; const val ACTION_SENDTO = "t"; const val ACTION_VIEW = "v"
    const val EXTRA_STREAM = "x"; const val EXTRA_SUBJECT = "y"; const val FLAG_GRANT_READ_URI_PERMISSION = 1
    @JvmStatic fun createChooser(target: Intent?, title: CharSequence?): Intent = TODO() } }

package android.os
interface Parcelable

package android.view
open class View(c: android.content.Context?) { var layoutParams: ViewGroup.LayoutParams? = null; val parent: ViewParent? get() = TODO()
  open fun setBackgroundColor(c: Int) {} }
interface ViewParent
abstract class ViewGroup(c: android.content.Context?) : View(c), ViewParent { fun removeView(v: View?) {}
  open class LayoutParams(w: Int, h: Int) { companion object { const val MATCH_PARENT = -1 } } }
class Window { fun addFlags(f: Int) {} ; fun clearFlags(f: Int) {} }
class WindowManager { class LayoutParams { companion object { const val FLAG_KEEP_SCREEN_ON = 128 } } }

package android.util
object Base64 { const val DEFAULT = 0; @JvmStatic fun decode(s: String?, flags: Int): ByteArray = TODO() }

package android.widget
class Toast { fun show() {}; companion object { const val LENGTH_LONG = 1; const val LENGTH_SHORT = 0
  @JvmStatic fun makeText(c: android.content.Context?, t: CharSequence?, d: Int): Toast = TODO() } }

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
package androidx.activity.result
fun interface ActivityResultCallback<O> { fun onActivityResult(result: O) }
abstract class ActivityResultContract<I, O>
class ActivityResult(val resultCode: Int, val data: android.content.Intent?)
abstract class ActivityResultLauncher<I> { abstract fun launch(input: I) }

package androidx.activity.result.contract
object ActivityResultContracts { class StartActivityForResult : androidx.activity.result.ActivityResultContract<android.content.Intent, androidx.activity.result.ActivityResult>() }

package androidx.activity
import androidx.activity.result.*
open class ComponentActivity : android.content.Context() {
  val window: android.view.Window get() = TODO()
  open fun onCreate(savedInstanceState: android.os.Bundle?) {}
  open fun onStop() {}; open fun onPause() {}; open fun onResume() {}; open fun onDestroy() {}
  open fun onConfigurationChanged(newConfig: android.content.res.Configuration) {}
  fun runOnUiThread(action: Runnable) {}
  fun <I, O> registerForActivityResult(contract: ActivityResultContract<I, O>, callback: ActivityResultCallback<O>): ActivityResultLauncher<I> = TODO()
  companion object { const val RESULT_CANCELED = 0; const val RESULT_OK = -1 } }
class SystemBarStyle
fun ComponentActivity.enableEdgeToEdge(statusBarStyle: SystemBarStyle? = null, navigationBarStyle: SystemBarStyle? = null) {}

package androidx.activity.compose
fun androidx.activity.ComponentActivity.setContent(parent: Any? = null, content: @androidx.compose.runtime.Composable () -> Unit) {}

package androidx.core.content
object FileProvider { @JvmStatic fun getUriForFile(c: android.content.Context, authority: String, f: java.io.File): android.net.Uri = TODO() }

package androidx.webkit
class WebViewAssetLoader { fun shouldInterceptRequest(url: android.net.Uri): android.webkit.WebResourceResponse? = TODO()
  interface PathHandler
  class AssetsPathHandler(c: android.content.Context) : PathHandler
  class Builder { fun setDomain(d: String): Builder = this; fun addPathHandler(path: String, h: PathHandler): Builder = this; fun build(): WebViewAssetLoader = TODO() } }

package org.json
class JSONObject { companion object { @JvmStatic fun quote(s: String?): String = TODO() } }

// ---------------------------------------------------------------- Compose
package androidx.compose.runtime
@Target(AnnotationTarget.FUNCTION, AnnotationTarget.TYPE, AnnotationTarget.TYPE_PARAMETER, AnnotationTarget.PROPERTY_GETTER)
annotation class Composable

package androidx.compose.ui.graphics
@JvmInline value class Color(val v: ULong)
fun Color(color: Long): Color = TODO()

package androidx.compose.ui.unit
@JvmInline value class Dp(val value: Float)
@JvmInline value class TextUnit(val packed: Long)
val Int.dp: Dp get() = TODO()
val Int.sp: TextUnit get() = TODO()

package androidx.compose.ui.text.font
class FontWeight(val weight: Int) { companion object { val Bold: FontWeight = TODO() } }

package androidx.compose.ui
interface Modifier { companion object : Modifier }

package androidx.compose.foundation
import androidx.compose.runtime.Composable
fun androidx.compose.ui.Modifier.background(color: androidx.compose.ui.graphics.Color): androidx.compose.ui.Modifier = this
@Composable fun isSystemInDarkTheme(): Boolean = TODO()

package androidx.compose.foundation.layout
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
interface BoxScope
interface ColumnScope
interface WindowInsets { companion object }
val WindowInsets.Companion.safeDrawing: WindowInsets @Composable get() = TODO()
fun Modifier.fillMaxSize(fraction: Float = 1f): Modifier = this
fun Modifier.padding(all: androidx.compose.ui.unit.Dp): Modifier = this
fun Modifier.windowInsetsPadding(insets: WindowInsets): Modifier = this
object Arrangement { interface Vertical; fun spacedBy(space: androidx.compose.ui.unit.Dp): Vertical = TODO() ; val Top: Vertical = TODO() }
@Composable fun Box(modifier: Modifier = Modifier, content: @Composable BoxScope.() -> Unit) {}
@Composable fun Column(modifier: Modifier = Modifier, verticalArrangement: Arrangement.Vertical = Arrangement.Top, content: @Composable ColumnScope.() -> Unit) {}

package androidx.compose.material3
import androidx.compose.runtime.Composable
@Composable fun Text(text: String, modifier: androidx.compose.ui.Modifier = androidx.compose.ui.Modifier,
  color: androidx.compose.ui.graphics.Color = TODO(), fontSize: androidx.compose.ui.unit.TextUnit = TODO(),
  fontWeight: androidx.compose.ui.text.font.FontWeight? = null) {}

package androidx.compose.ui.viewinterop
import androidx.compose.runtime.Composable
@Composable fun <T : android.view.View> AndroidView(factory: (android.content.Context) -> T, modifier: androidx.compose.ui.Modifier = androidx.compose.ui.Modifier, update: (T) -> Unit = {}) {}
