@file:Suppress("unused", "UNUSED_PARAMETER")
package androidx.webkit

class WebViewAssetLoader { fun shouldInterceptRequest(url: android.net.Uri): android.webkit.WebResourceResponse? = TODO()
  interface PathHandler
  class AssetsPathHandler(c: android.content.Context) : PathHandler
  class Builder { fun setDomain(d: String): Builder = this; fun addPathHandler(path: String, h: PathHandler): Builder = this; fun build(): WebViewAssetLoader = TODO() } }

