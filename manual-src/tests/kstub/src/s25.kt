@file:Suppress("unused", "UNUSED_PARAMETER")
package androidx.compose.ui.viewinterop
import androidx.compose.runtime.Composable
@Composable fun <T : android.view.View> AndroidView(factory: (android.content.Context) -> T, modifier: androidx.compose.ui.Modifier = androidx.compose.ui.Modifier, update: (T) -> Unit = {}) {}

