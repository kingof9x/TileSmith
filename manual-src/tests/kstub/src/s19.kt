@file:Suppress("unused", "UNUSED_PARAMETER")
package androidx.compose.ui.unit

@JvmInline value class Dp(val value: Float)
@JvmInline value class TextUnit(val packed: Long)
val Int.dp: Dp get() = TODO()
val Int.sp: TextUnit get() = TODO()

