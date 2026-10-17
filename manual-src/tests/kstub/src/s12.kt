@file:Suppress("unused", "UNUSED_PARAMETER")
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

