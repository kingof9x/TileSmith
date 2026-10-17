@file:Suppress("unused", "UNUSED_PARAMETER")
package android.content.res

class Configuration { @JvmField var uiMode: Int = 0
  companion object { const val UI_MODE_NIGHT_MASK = 48; const val UI_MODE_NIGHT_YES = 32 } }
class Resources { val configuration: Configuration get() = TODO() }
class AssetManager { fun list(path: String): Array<String>? = TODO() }

