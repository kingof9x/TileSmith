# TileSmith working rules (from the user, 2026-10-13)

- Do NOT bump the version number while working through changes. Keep it at the last released version.
- Only when the user asks for an updated package to download:
  1. python3 bump.py <new version>
  2. add the collected changes below to HISTORY in make_manual.py, then python3 make_manual.py
  3. python3 make_spec.py (TileSmith-App-Spec.md, a detailed description for another AI such as Google AI Studio to
     build an Android clone; ship it with every package). Update its hand-written sections (KEYDESC, PATSPEC and the
     prose) when features change.
  3b. python3 make_aistudio_kit.py (full run: screenshots, animations, TileSmith-Mobile-Manual.pdf, readable source,
      Android project; writes /mnt/user-data/outputs/TileSmith-Android-AIStudio-Kit.zip). It also regenerates the spec.
  4. copy app/index.html, BUILD-*.txt (Windows, Mac, Android, iOS), TileSmith-Manual.pdf, TileSmith-Mobile-Manual.pdf
     and TileSmith-App-Spec.md to
     /mnt/user-data/outputs, rebuild tilesmith-desktop.zip with `zip -ry` (keeps the Syphon.framework symlinks; the spec
     sits in the project root) EXCLUDING mobile/node_modules, mobile/www, mobile/android/app/src/main/assets/public,
     mobile/ios/App/App/public, android/ios build folders, mobile/package-lock.json and
     android-aistudio/android/app/src/main/assets (they are regenerated), then send zip + both manuals + build guides +
     spec + the AI Studio kit
- Between packages: edit the source, test it, and update the web artifact for preview (version label unchanged).
- Keep the manual text in make_manual.py and the spec text in make_spec.py up to date as features change.
- Test runs: MANUAL_OUT=/tmp/x.pdf python3 make_manual.py and SPEC_OUT=/tmp/x.md python3 make_spec.py write elsewhere.
- Always mark NDI with ® and keep "NDI® is a registered trademark of Vizrt NDI AB" plus the ndi.video links.
- Show design options before building them.
- Web preview artifact: https://claude.ai/artifact/92aCkLvXfqAL9WHBb8U9bj (update with Artifact publish + url).
- Work in progress since the last release is backed up in /mnt/user-data/outputs/tilesmith-wip-backup.zip
  (tilesmith-desktop + manual-src, made with zip -ry). If /home/claude is reset, restore from it before the release zip,
  and refresh the backup after each round of changes.
- Spout/Syphon binaries DO ship in the zip (bin/spout: SpoutDX.dll MT build + Spout-licence.txt; bin/mac/syphon:
  bin/syphon.node, Frameworks/Syphon.framework with symlinks, licences). They are BSD/MIT; keep their licence files.
  (An earlier, unfinished attempt used the texture-bridge add-on downloaded at build time; it was replaced on 2026-10-14
  by the simpler direct SpoutDX / node-syphon output in the page itself.)

Last released: v3.3 (2026-10-14): Spout/Syphon output, Horizontal/Vertical wiring preferences, Android and iOS apps.

## Google AI Studio kit (added 2026-10-14, after v3.3)
- Project folder android-aistudio/: webview-bridge.js (window.TileSmithAndroid -> window.TSM, same as the Capacitor
  bridge), prepare-assets.js, README.txt, android/ (Kotlin + Compose Android Studio project, app ID
  com.tilesmith.android; bump.py sets its versionCode/versionName).
- manual-src: kit-docs/*.md (00-04 kit documents with {{placeholders}} filled by the builder), make_kit_shots.py (UI
  screenshots, tablet + phone, dark), make_kit_anims.py (canvas renders, frame strips, GIFs, stepping the app's own
  tick()), make_readable_source.py (split + Prettier 3 + FUNCTIONS.md), make_mobile_manual.py, make_aistudio_kit.py,
  make_route_b_prompts.py (route-b-prompts/B01-B12: each prompt assembled with its spec sections and app.js regions,
  found by top-level names with tools/toplevel.js; prompt texts live in that script).
- tools/: run `npm install` there once per session (acorn + prettier, used by the two scripts above).
- tests/: android_test.py (bridge with a stand-in Kotlin interface; must print ALL OK) and kstub/ (Kotlin type check
  of MainActivity.kt / TileSmithBridge.kt against API stubs with the Kotlin compiler inside Gradle: tests/kstub/check.sh).
- Not testable here: APK build (no Android SDK/Maven), AI Studio itself, real devices.

## Changes since the last release (roll into HISTORY at the next package)
- TileSmith-App-Spec.md now lists all 25 test patterns (make_spec.py had a duplicate PATS key that cut the table to
  the 7 new-wall patterns) and describes the android-aistudio app in section 15.
- New TileSmith-Mobile-Manual.pdf (separate mobile app manual); BUILD-ANDROID.txt / BUILD-IOS.txt and the desktop
  manual's chapter 21 point to it. BUILD-ANDROID.txt has a section on the android-aistudio app.
- New android-aistudio folder (Kotlin + Compose app for Google AI Studio) and the AI Studio kit.
- Spout fix (user report 2026-10-14: Resolume listed TileSmith but showed black/frozen): the sender's DirectX 11 device
  used the default card, often the built-in chip on two-GPU laptops while Resolume runs on the fast one. New Spout
  options › Graphics card (shGpu: Automatic = SetPreferredAdapter high performance, else first non-Intel/Microsoft card;
  or a named card), device opened explicitly and checked, card shown in the status line, restart on change, Spout log
  at %APPDATA%/TileSmith/spout-log.txt named in errors, check-share.js checks the new exports. Test:
  tests/spout_gpu_test.py (+ tests/share_test.py). NOT yet confirmed by the user on the real PC.
- Cable labels (user request 2026-10-17): new "Label printing options" section below Animation Options, shown only when
  data or power wiring is defined (lblVis/labelList/labelPages/labelsHTML/printLabels in index.html; S keys lbl*; LBL sheet
  presets). Design chosen by the user: selectable sheet presets, big ID + route, two labels per cable side by side.
  Test: tests/labels_test.py (ALL OK). Manual: chapter 18 "Cable labels"; spec: "Cable labels" paragraph + KEYDESC.
  Wrap-around revision (2026-10-17): labels are wrap strips with text on both halves; user-selectable Wrap layout (identical /
  fold-over / colour ends), Colour flag style (end blocks / bars / corner squares), Wall mark (block / always / tint), green
  primary + red return flags, wall flag = wall shadeC; default sheet Avery 5163; power phase B is now orange.
  TODO before package: add to HISTORY, mention in mobile manual / kit docs if wanted, refresh WIP backup + git repo.

## GitHub (2026-10-14)
- Private repository prepared for the user (they publish it from GitHub Desktop or connect GitHub so Claude can push).
  Layout: repo root = README.md, .gitignore, .gitattributes, tilesmith-desktop/, manual-src/ (same layout as
  /home/claude, so every script path still works after a clone into /home/claude). Not committed: node_modules,
  lock files, mobile/www, generated assets, ffmpeg, the NDI® runtime, manual-src/kit, manual-src/shots.
- Staging copy: /home/claude/tilesmith (first commit "TileSmith 3.3"). Once it is on GitHub, commit each round of
  changes there (with the attribution trailers) as well as refreshing the WIP backup. Repository URL: (not known yet).

## Open questions for the user
- Phone layout for the mobile app: A bottom tabs, B split screen (recommended), C slide-in drawers
  (mock-ups in /mnt/user-data/outputs/tilesmith-phone-layout-options.png). Tablets use the desktop layout.
- Licence for the project (MIT discussed; disguise test-pattern images, ffmpeg GPL and the NDI® runtime need care).
