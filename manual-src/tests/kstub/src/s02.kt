@file:Suppress("unused", "UNUSED_PARAMETER")
package android.net

abstract class Uri : android.os.Parcelable { abstract val host: String?; abstract val scheme: String?
  companion object { @JvmStatic fun parse(s: String?): Uri = TODO() } }

