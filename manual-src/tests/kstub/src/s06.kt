@file:Suppress("unused", "UNUSED_PARAMETER")
package android.view

open class View(c: android.content.Context?) { var layoutParams: ViewGroup.LayoutParams? = null; val parent: ViewParent? get() = TODO()
  open fun setBackgroundColor(c: Int) {} }
interface ViewParent
abstract class ViewGroup(c: android.content.Context?) : View(c), ViewParent { fun removeView(v: View?) {}
  open class LayoutParams(w: Int, h: Int) { companion object { const val MATCH_PARENT = -1 } } }
class Window { fun addFlags(f: Int) {} ; fun clearFlags(f: Int) {} }
class WindowManager { class LayoutParams { companion object { const val FLAG_KEEP_SCREEN_ON = 128 } } }

