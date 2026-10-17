# TileSmith

LED wall pixel-mapping and test-pattern generator with an animated technician who builds the wall tile by tile.
Current version: **3.3**.

Concept and development: Callum Davenport-Lambton · tilesmithapp@gmail.com · https://ko-fi.com/kingof9x

## What is in this repository

| Folder or file | What it is |
|---|---|
| `tilesmith-desktop/app/index.html` | The whole app in one page (HTML, CSS, JavaScript). Every build uses this same page. |
| `tilesmith-desktop/` | The Windows and Mac desktop app (Electron): `main.js`, `package.json`, `scripts/`, `build/` icons, `bin/` (Spout and Syphon). |
| `tilesmith-desktop/mobile/` | The Android and iOS app (Capacitor 8). |
| `tilesmith-desktop/android-aistudio/` | The Android app as Kotlin + Jetpack Compose (for Google AI Studio or Android Studio). |
| `tilesmith-desktop/BUILD-*.txt` | Step-by-step build guides: Windows, Mac, Android, iOS. |
| `tilesmith-desktop/TileSmith-Manual.pdf` | User manual (desktop). |
| `tilesmith-desktop/TileSmith-Mobile-Manual.pdf` | User manual (Android and iOS). |
| `tilesmith-desktop/TileSmith-App-Spec.md` | Full specification of the app, for rebuilding it elsewhere. |
| `manual-src/` | The tools that make the manuals, the spec, the Google AI Studio kit and the version bump, plus their tests. `WORKFLOW.md` explains how a release is put together. |

## Building

Read the guide for your platform in `tilesmith-desktop/`. In short:

- **Windows**: Node.js LTS, plus the NDI® SDK and an ffmpeg "full" build on the build computer. Then, in Command Prompt
  in `tilesmith-desktop`: `npm run clean`, `npm install`, `npm run dist`. The result is `TileSmith-Portable.exe`.
- **Mac**: Node.js, the NDI® SDK and ffmpeg (BUILD-MAC.txt explains each), then `npm run dist:mac`. The result is a
  universal `.dmg`.
- **Android / iOS**: `npm install`, then `npm run android` or `npm run ios` in `tilesmith-desktop/mobile`, then Android
  Studio or Xcode.

Not stored here (each build computer adds them, as the guides explain):

- ffmpeg;
- the NDI® runtime;
- `node_modules`;
- build output: `dist/`, `.exe`, `.dmg`, APKs.

Spout (`bin/spout`) and Syphon (`bin/mac/syphon`) are included, with their licences.

On a Mac, clone the repository rather than downloading a ZIP. `Syphon.framework` contains symbolic links that a clone
keeps.

## Licence and third-party notices

No licence has been chosen yet, so all rights are reserved. This repository is private.

- **Spout** SDK (SpoutDX.dll) by Lynn Jarvis, https://spout.zeal.co/, Simplified BSD licence (`bin/spout/Spout-licence.txt`).
- **Syphon** framework, BSD licence; **node-syphon**, MIT licence (`bin/mac/syphon/`).
- **NDI®** is a registered trademark of Vizrt NDI AB, https://ndi.video/. The NDI® runtime is not stored here. Builds take
  it from the NDI® SDK under the NDI® SDK License Agreement (https://ndi.link/ndisdk_license). NDI® Tools:
  https://ndi.video/tools/.
- The built-in disguise test-pattern images and ffmpeg need checking before any public release.

## Licence

Copyright (c) 2026 Callum Davenport-Lambton.

- **Program code:** GNU General Public License v3 or later, see [`LICENSE`](LICENSE).
- **Animated technician** (character design, artwork, animations, the TileSmith name and logo): all rights reserved,
  not GPL. See [`tilesmith-desktop/COPYRIGHT-AND-ARTWORK.txt`](tilesmith-desktop/COPYRIGHT-AND-ARTWORK.txt).
- **Third parties** (NDI runtime, Spout, Syphon, ffmpeg, npm packages) keep their own licences, listed in the same file.

## Downloads and builds

Open **Actions > Build and release > Run workflow**, type a version such as `3.3` and run it. GitHub builds the Windows portable
app, the Mac universal installer and Linux packages (`.AppImage` and `.deb`, no Spout/Syphon/NDI there yet) and attaches them
to a release named `v3.3` together with the manuals. The builds are unsigned. On Ubuntu 24.04 and newer, the AppImage may need
`--no-sandbox` (or install the `.deb`).
