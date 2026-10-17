@file:Suppress("unused", "UNUSED_PARAMETER")
package androidx.activity.result

fun interface ActivityResultCallback<O> { fun onActivityResult(result: O) }
abstract class ActivityResultContract<I, O>
class ActivityResult(val resultCode: Int, val data: android.content.Intent?)
abstract class ActivityResultLauncher<I> { abstract fun launch(input: I) }

