# Route A: the prompt for Google AI Studio (exact TileSmith app)

Paste everything between `=== PROMPT START ===` and `=== PROMPT END ===` as the first prompt of a new **Android** app
in AI Studio's Build mode. Attach `screenshots/tablet/t01-first-launch.png` and
`screenshots/phone/p01-phone-portrait.png`. Then follow step 4 of `00-START-HERE.md` to add the TileSmith page
(`android-assets/tilesmith/`).

The prompt contains every Kotlin and XML file of the finished app (the same files as `android-project/`), so AI
Studio only has to set them up. It should not design anything itself.

```
=== PROMPT START ===
Build "TileSmith" ({{VERSION}}), an Android app for LED video technicians, as a thin native shell around an existing,
finished web app. Do NOT rewrite or redesign TileSmith in Compose: its whole user interface (settings panels, viewport,
engineering panel, animations) is an HTML page that I will add as an asset. The native app only shows that page full
screen in a WebView and gives it a few Android services through a JavaScript interface. Use exactly the code below.

REQUIREMENTS
1. Kotlin + Jetpack Compose, single activity (MainActivity), single module. Phone and tablet, any orientation.
   namespace and applicationId: com.tilesmith.android (if your project must keep another package, keep yours and change
   only the package lines). App name: TileSmith. versionName "{{VERSION}}", versionCode {{VERSION_CODE}}. minSdk 24,
   targetSdk and compileSdk 36.
2. Dependencies (newer stable versions are fine): androidx.activity:activity-compose, androidx.core:core-ktx,
   androidx.webkit:webkit (for WebViewAssetLoader), Compose BOM with ui, foundation, material3.
3. The page lives in app/src/main/assets/tilesmith/ (index.html + webview-bridge.js). I add those files myself; they
   are too big for this chat. Until they are there, the app shows the "page is not in this app yet" screen in
   MainActivity.kt. Do not create placeholder files with those names.
4. The WebView loads https://appassets.androidplatform.net/assets/tilesmith/index.html through WebViewAssetLoader
   (AssetsPathHandler on "/assets/"), with JavaScript and DOM storage on, file access off and page zoom off. It is
   full screen inside the safe drawing area (status bar, navigation bar, display cut-out and keyboard insets are
   padding), on a background of #0D1217 in dark mode and #F1F3F5 in light mode.
5. Light/dark: the page switches its colours with the CSS prefers-color-scheme, which the WebView takes from the app
   theme. So the theme must be DayNight: res/values/themes.xml with parent android:Theme.Material.Light.NoActionBar and
   res/values-night/themes.xml with parent android:Theme.Material.NoActionBar (both named Theme.TileSmith).
6. The activity handles configuration changes itself (configChanges in the manifest), so turning the device or switching
   light/dark never reloads the page.
7. JavaScript interface "TileSmithAndroid" (TileSmithBridge.kt) with exactly these methods, each returning "" on success
   or an error message: writeChunk(name, base64, append), deleteFile(name), shareFile(name, mime, callbackId),
   openUrl(url), keepAwake(on). Files go to <cacheDir>/exports and are shared with ACTION_SEND through a FileProvider
   (authority <applicationId>.fileprovider, res/xml/file_paths.xml with cache-path "exports/"). When the share sheet
   closes, call window.__tsmDone(callbackId, ok, error) in the page: ok = true when the sheet returned RESULT_OK or the
   app went to the background while it was open (an app was picked), otherwise false.
8. <input type="file"> in the page must open the system picker (WebChromeClient.onShowFileChooser). Links to other
   sites and mailto: open outside the app with an Intent. JavaScript alert/confirm use the WebView defaults.
9. Keep the screen on while the page asks for it (FLAG_KEEP_SCREEN_ON on the UI thread).
10. Launcher icon: keep the default for now (I will replace the mipmap files).

FILES (use as they are)

--- app/src/main/AndroidManifest.xml ---
{{MANIFEST}}

--- app/src/main/res/xml/file_paths.xml ---
{{FILE_PATHS}}

--- app/src/main/res/values/themes.xml ---
{{THEMES}}

--- app/src/main/res/values-night/themes.xml ---
{{THEMES_NIGHT}}

--- app/src/main/res/values/colors.xml ---
{{COLORS}}

--- app/src/main/res/values-night/colors.xml ---
{{COLORS_NIGHT}}

--- app/src/main/java/com/tilesmith/android/MainActivity.kt ---
{{MAIN_KT}}

--- app/src/main/java/com/tilesmith/android/TileSmithBridge.kt ---
{{BRIDGE_KT}}

--- app/build.gradle.kts (dependencies and android block; keep your plugin setup) ---
{{GRADLE_APP}}

When it builds, the app should open on the "The TileSmith page is not in this app yet." screen. That is the correct
result for this step.
=== PROMPT END ===
```

## Checks after the page is added

The kit's `TileSmith-Mobile-Manual.pdf` explains each of these. Compare with `screenshots/`.

| Check | Expected |
|---|---|
| App opens | Dark (or light) TileSmith screen with "TileSmith v{{VERSION}}" at the top left, the canvas with a 6 × 4 wall in the middle, Engineering on the right (tablet) or below (phone). No white flash. |
| Top bar | New Project, Save, Open, Info, Undo, Reset fit, Next pattern, Export PNG, Export CSV, Spec sheet, Resolume XML ▾. **No** Start NDI® or Spout/Syphon button. |
| Turn the device | The page stays as it was (no reload), and a running build animation keeps going. |
| Pinch on the canvas | Zooms the canvas, not the whole page. Two fingers pan; one finger drags a wall. |
| LED build > Start | The technician walks in, carries tiles and builds the wall. |
| Export PNG | Android share sheet "Save or send tilesmith-canvas.png". Pick Drive or Files, and a toast says "Saved tilesmith-canvas.png.". Close the sheet instead, and it says "Not saved: tilesmith-canvas.png". |
| Export CSV, Spec sheet, Resolume XML | The same, with patching.csv, tilesmith-spec.html and tilesmith-1920x1080.xml. |
| Video export > Export video (LED build ticked) | The status shows ● REC blank, then building, then hold. The screen stays on. Then the share sheet opens for tilesmith-build-YYYYMMDD-HHMMSS.mp4. Pressing Export video again while recording cancels it ("Recording cancelled"). |
| Upload test pattern (Test pattern section, pattern "custom") | The system picker opens; the picture appears on the wall. |
| ⓘ Info › Ko-fi link / e-mail | Opens the browser or e-mail app. |
| Close and reopen the app | Every setting is still there (it is saved in the WebView's storage). |
| Switch the phone to light mode | The page turns light and the system bar icons turn dark. |

## Fix-up prompts (only if needed)

- *The app shows a blank white page:* "The WebView must load https://appassets.androidplatform.net/assets/tilesmith/index.html
  through WebViewAssetLoader in shouldInterceptRequest, exactly as in MainActivity.kt. Check that the asset is at
  app/src/main/assets/tilesmith/index.html and that javaScriptEnabled and domStorageEnabled are true."
- *The page is always light (or always dark):* "Use the two themes.xml files from the first prompt: Theme.TileSmith must be
  Theme.Material.Light.NoActionBar in values and Theme.Material.NoActionBar in values-night, and the manifest must
  use @style/Theme.TileSmith."
- *Turning the phone reloads TileSmith:* "Add the android:configChanges list from the manifest in the first prompt to
  MainActivity, and create the WebView once in onCreate (not inside a composable)."
- *Export does nothing / says the file was not found:* "TileSmithBridge must write to File(cacheDir, "exports") and the
  FileProvider in the manifest must point to res/xml/file_paths.xml with <cache-path name="exports" path="exports/" />."
- *Upload buttons do nothing:* "Implement WebChromeClient.onShowFileChooser with an ActivityResultLauncher as in
  MainActivity.kt, and pass WebChromeClient.FileChooserParams.parseResult(resultCode, data) back to the callback."
- *The page sits under the status bar or the keyboard covers inputs:* "Wrap the AndroidView in a Box with
  Modifier.windowInsetsPadding(WindowInsets.safeDrawing) and call enableEdgeToEdge() in onCreate."

## The JavaScript side (already in android-assets, shown for reference)

`webview-bridge.js` is loaded in front of TileSmith's own script. It turns `window.TileSmithAndroid` into
`window.TSM`, the same interface the Capacitor build's bridge provides, so `index.html` is unchanged:

```js
{{BRIDGE_JS}}
```
