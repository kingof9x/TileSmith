# TileSmith {{VERSION}} for Android: Google AI Studio kit

This kit lets Google AI Studio build the TileSmith Android app. AI Studio's Android builder writes **Kotlin with Jetpack
Compose**: one activity and one module, client side only. TileSmith itself is a 600 KB web page: JavaScript drawing on an
HTML canvas, with its test-pattern pictures built in. So the kit gives AI Studio two ways to build it.

| Route | What AI Studio builds | Result |
|---|---|---|
| **A. Exact app (recommended)** | A small Compose app that shows TileSmith's own page in a WebView and connects it to Android (share sheet, video file, links, screen-on). Prompt: `01-PROMPT-exact-app.md` | The same app as the desktop, web and Capacitor builds: the same layout, behaviour, maths and animations, because it runs the same code. |
| **B. Native rewrite** | TileSmith rebuilt screen by screen in Compose and Android Canvas from the spec, screenshots and animation guide. Prompts: `02-NATIVE-REWRITE-GUIDE.md` | A separate code base. It will look close, but it is only as exact as AI Studio's rewrite, and it needs many rounds of prompts and checks. |

There is also a **route C**: `android-project/` is the finished route A project, Kotlin and Compose, with the TileSmith
page already inside. Open it in Android Studio and press Run. It is what the AI Studio prompt asks for, so you can
compare AI Studio's result with it, or skip AI Studio altogether.

## What is in the kit

| File or folder | What it is |
|---|---|
| `00-START-HERE.md` | This file. |
| `01-PROMPT-exact-app.md` | The prompt for route A, ready to paste into AI Studio. It includes all the Kotlin source. |
| `02-NATIVE-REWRITE-GUIDE.md` | Route B: architecture, porting map and an overview of the 12 prompts. |
| `route-b-prompts/` | Route B, ready to paste: `B01` … `B12`, each with its instructions, spec sections and original code already in it and the screenshots to attach listed at the top. Start with `B00-HOW-TO-USE.md`. |
| `03-SCREENS.md` | A catalogue of every screenshot, what it shows and how to reach that screen. |
| `04-ANIMATIONS.md` | Every animation: timings, motion formulas, drawing rules, frame strips and GIFs. |
| `TileSmith-Mobile-Manual.pdf` | User manual for the mobile app (Android and iOS). It is separate from the desktop manual. |
| `TileSmith-App-Spec.md` | The full app specification: settings, presets, formulas, patterns, wiring, power, outputs and checks. |
| `android-assets/tilesmith/` | The TileSmith page for the Android app: `index.html` (the app) and `webview-bridge.js` (the link to Kotlin). It goes in `app/src/main/assets/tilesmith/`. |
| `android-project/` | Route C: the complete Android Studio project (Kotlin + Compose + Gradle). |
| `source/index.html` | The exact app, one file, as shipped in v{{VERSION}}. |
| `source/readable/` | The same app split and formatted for reading and porting: `app.js` ({{JS_LINES}} lines), `style.css`, `index.html`, `images/`, plus `FUNCTIONS.md`, an index of the code. |
| `source/android/` | The Kotlin, manifest and resource files on their own, plus `webview-bridge.js` and `prepare-assets.js`. |
| `source/capacitor/` | How the existing Capacitor build connects the same page, for reference. |
| `screenshots/` | {{N_SHOTS}} pictures: `tablet/`, `phone/`, `panels/`, `patterns/`, `wiring/`, `shapes/`, `animations/` (PNG frame strips and GIFs). |

## Route A, step by step

1. Open **https://aistudio.google.com**, go to **Build**, and start a new **Android** app.
2. Open `01-PROMPT-exact-app.md`, copy everything between the two `=== PROMPT START ===` / `=== PROMPT END ===` lines,
   and paste it as the first prompt. Attach `screenshots/tablet/t01-first-launch.png` and
   `screenshots/phone/p01-phone-portrait.png` so it can see the target.
3. Wait for the build. In the emulator the app first shows **"The TileSmith page is not in this app yet."** This is
   expected: the page is a 600 KB file that cannot go through a prompt.
4. Add the page. Either way works:
   - **In AI Studio**: if the **Code** tab lets you add or upload files, create the folder
     `app/src/main/assets/tilesmith/` and upload `android-assets/tilesmith/index.html` and
     `android-assets/tilesmith/webview-bridge.js` into it. The emulator reloads and shows TileSmith. You can then
     install it on your phone (**Install on Device**, Chrome or Edge with USB debugging on) or publish it to the Play
     internal testing track from AI Studio.
   - **In Android Studio** (always works): in AI Studio click **Download** (ZIP), unzip it, and open the folder in
     Android Studio. Right-click **app** in the Project panel, choose **New > Folder > Assets Folder**, then **Finish**.
     Copy the `tilesmith` folder from `android-assets/` into the new `app/src/main/assets` folder (in Explorer or
     Finder, or by pasting it in Android Studio). You should end up with
     `app/src/main/assets/tilesmith/index.html`. Then press **Run**.
5. Check it with the list at the end of `01-PROMPT-exact-app.md`. If something is off, paste the matching fix-up prompt
   from that file.

To update TileSmith later, replace the two files in `app/src/main/assets/tilesmith/` with a newer
`android-assets/tilesmith/`. To make that folder yourself from a newer project, run `node prepare-assets.js <folder>` in
the project's `android-aistudio` folder.

## Route B in short

Open `route-b-prompts/B00-HOW-TO-USE.md`. Start a new AI Studio Android app. For each of `B01` … `B12` in turn, attach
the screenshots listed at the top of the file and paste the text between its COPY lines. Check the result against the
screenshots before going on. `02-NATIVE-REWRITE-GUIDE.md` explains the plan behind the prompts. Keep `TileSmith-App-Spec.md` and `04-ANIMATIONS.md`
open: every number, formula and colour the rewrite needs is in them. When a prompt says so, attach the matching part of
`source/readable/app.js`; the line numbers are in `source/readable/FUNCTIONS.md`.

## Good to know

- **Package name.** The prompt uses `com.tilesmith.android`. The Capacitor build (BUILD-ANDROID.txt) uses
  `com.tilesmith.app`, so both can be installed on one device side by side.
- **Light and dark.** The page follows the phone's light or dark setting, so the Android theme must be DayNight. The
  prompt covers this.
- **Phones.** On a phone the panels stack under each other (see `screenshots/phone/`). A dedicated phone layout is
  planned and will reach this app automatically, through a newer `index.html`.
- **What I could check here.** `webview-bridge.js` was tested in Chromium with a stand-in for the Kotlin side: saving
  PNG, CSV, the spec sheet and XML; a 2.5 MB file in pieces; a cancelled share; a failed write; links; recording and
  cancelling a video; and the plain web page without Kotlin. The Kotlin files were type-checked against the Android
  APIs they use. Building an APK, AI Studio itself and a real device could not be tried from here. Test on a device
  before you rely on it.

NDI® is a registered trademark of Vizrt NDI AB (https://ndi.video/). NDI®, Spout and Syphon output are desktop
features and are hidden in the mobile app.

TileSmith: concept and development by Callum Davenport-Lambton · tilesmithapp@gmail.com · https://ko-fi.com/kingof9x
