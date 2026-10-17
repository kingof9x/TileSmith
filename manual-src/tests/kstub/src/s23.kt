@file:Suppress("unused", "UNUSED_PARAMETER")
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

