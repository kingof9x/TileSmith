TILESMITH - ANDROID APP FOR GOOGLE AI STUDIO (Kotlin + Jetpack Compose)
=======================================================================
A second way to make the Android app, next to the Capacitor build in the "mobile" folder (BUILD-ANDROID.txt).
Google AI Studio's Android builder writes Kotlin with Jetpack Compose, so this app is a small Compose activity that
shows the same TileSmith page (../app/index.html, unchanged) in a WebView. It gives the page the same window.TSM
interface the Capacitor build has, so the app behaves the same: files go out through the share sheet, video records
as MP4, links open outside the app, and the screen stays on while recording.

WHAT IS HERE
  webview-bridge.js    The JavaScript side: wraps the Kotlin interface (TileSmithAndroid) into window.TSM.
  prepare-assets.js    Makes the assets folder (index.html with the bridge loaded first, plus webview-bridge.js).
  android/             The complete Android Studio project (Kotlin, Compose, Gradle), app ID com.tilesmith.android.
                       The Capacitor app is com.tilesmith.app, so both can be installed side by side.

BUILD IT IN ANDROID STUDIO
  1) In this folder:      node prepare-assets.js
     (it fills android/app/src/main/assets/tilesmith with the current TileSmith page)
  2) Android Studio > Open > the "android" folder, wait for Gradle sync, plug in the device, press Run.
  Run step 1 again after every change to TileSmith.

BUILD IT IN GOOGLE AI STUDIO
  Use the TileSmith Android AI Studio kit (TileSmith-Android-AIStudio-Kit.zip): 00-START-HERE.md explains it and
  01-PROMPT-exact-app.md is the prompt to paste. To put a newer TileSmith page into an AI Studio project:
     node prepare-assets.js <folder>       then copy <folder>/tilesmith to app/src/main/assets/tilesmith
