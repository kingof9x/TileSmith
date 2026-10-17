@file:Suppress("unused", "UNUSED_PARAMETER")
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

