# TileSmith

LED wall pixel-mapping and test-pattern generator with an animated technician who builds the wall tile by tile.
Current version: **3.3**.

Concept and development: Callum Davenport-Lambton · tilesmithapp@gmail.com · https://ko-fi.com/kingof9x

## Software to install before you use a downloaded build

The downloads on the **Releases** page do not contain the NDI® runtime or ffmpeg (their licences do not allow it), so these two
features need a free install on the computer that runs TileSmith. Everything else works straight away. **Spout and Syphon are
included in the Windows and Mac downloads, so they need nothing extra** (their licences are in `tilesmith-desktop/bin`).

| Feature | Windows | Mac | Linux |
|---|---|---|---|
| Test patterns, wiring, labels, exports, animation | Nothing to install | Nothing to install | Nothing to install |
| **NDI® output** (needs this install) | NDI® Runtime: <https://ndi.link/NDIRedistV6> or the free NDI® Tools: <https://ndi.video/tools/> | NDI® Runtime for Mac: <https://ndi.link/NDIRedistV6Apple> or NDI® Tools: <https://ndi.video/tools/> | NDI® Runtime (`libndi.so.6`): get "NDI SDK for Linux" or the Linux tools from <https://ndi.video/for-developers/ndi-sdk/> and copy `libndi.so.6` to `/usr/local/lib` (then run `sudo ldconfig`), or point `NDI_RUNTIME_DIR_V6` at its folder |
| **Spout output** | Included. Needs a DirectX 11 graphics card. Pick the card under *Spout options* if the picture is black | not applicable | not applicable |
| **Syphon output** | not applicable | Included | not applicable |
| **Video export** (needs this install) | An ffmpeg "full" build with the HAP encoder: <https://www.gyan.dev/ffmpeg/builds/> (`ffmpeg-release-full`). Unzip it and put `ffmpeg.exe` in the same folder as `TileSmith-Portable.exe` | `brew install ffmpeg` (Homebrew: <https://brew.sh/>). For HAP video see step 5 in `tilesmith-desktop/BUILD-MAC.txt` | `sudo apt install ffmpeg` (Debian, Ubuntu), `sudo dnf install ffmpeg` (Fedora, needs RPM Fusion), `sudo pacman -S ffmpeg` (Arch). HAP video needs an ffmpeg built with the HAP encoder; otherwise use the MP4 formats. You can also set `TILESMITH_FFMPEG` to your ffmpeg path |

You also need a program to receive the picture, for example Resolume, vMix, OBS, MadMapper or TouchDesigner.
If NDI® or video export is not set up, TileSmith shows a message saying what is missing; nothing else is affected.
The Mac and Windows apps are unsigned: on Windows click *More info > Run anyway*; on a Mac right-click the app and choose *Open*.

NDI® is a registered trademark of Vizrt NDI AB. Learn more about NDI® at <https://ndi.video/>.

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
app, the Mac universal installer and the Linux packages (`.AppImage`, `.deb`, `.rpm`, `.pacman` for Arch, `.snap` and `.flatpak`;
no Spout/Syphon/NDI there yet), attaches them to a release named `v3.3` together with the manuals, and stores them under the
repository's **Packages** (ghcr.io, for example `oras pull ghcr.io/kingof9x/tilesmith:3.3`). The builds are unsigned. On Ubuntu
24.04 and newer, the AppImage may need `--no-sandbox` (or install the `.deb`).
