# Windows and Mac installers, Check for updates (2026-11-18)

Callum asked for "a windows and a mac installer and the ability to check github for the latest release".

- Windows: `npm run dist` now builds the NSIS installer (`TileSmith-<ver>-windows-setup.exe`: per-user, choose folder,
  Start menu + desktop shortcuts, uninstaller) next to the portable exe. The release uploads it as
  `TileSmith-windows-setup.exe`.
- Mac: `npm run dist:mac` builds a `.pkg` installer (installs to /Applications, not relocatable, unsigned) next to the
  `.dmg`. The release uploads `TileSmith-mac-universal.pkg`.
- Info window > Updates: Check for updates asks api.github.com/repos/kingof9x/TileSmith/releases/latest, compares with
  `APP_VERSION` (new constant, stamped by scripts/set-version.js) and offers Download (the file for this platform:
  setup.exe, or the portable exe when running portable; .dmg on Mac; AppImage; APK on Android; else the release page)
  and Release notes. S key `updAuto` (default on): the desktop and phone apps check at most once a day, 4 s after
  start, and show a note bottom-right only when a newer release exists. The plain web page never checks by itself.
- Nothing is downloaded or installed inside the app: Download opens the link in the browser.
- Test: manual-src/tests/updates_test.py (GitHub mocked). The installers themselves are checked by the
  Build and release workflow (run it with an empty version box for a test build).

## Add-ons (NDI Runtime, ffmpeg), same day
Callum asked whether the installer can check for NDI / Spout / Syphon and let users download the third-party files
without TileSmith "distributing" NDI. Chose "Both" (app + installer) on 2026-11-18.
- Spout and Syphon are already built into the release downloads (BSD), so they are only shown as Built in.
- Info > Add-ons (desktop only, `addonUI()`): NDI via ndiFind(); ffmpeg via ffCands() (new; ffFind uses it) including
  addonDir() = %APPDATA%\TileSmith\addons, ~/Library/Application Support/TileSmith/addons, ~/.config/TileSmith/addons.
- Get NDI Runtime opens https://ndi.link/NDIRedistV6 (Windows) / NDIRedistV6Apple (Mac) in the browser; Linux opens
  ndi.video/tools. NDI's Software Distribution page allows linking users to the NDI-provided download (it even allows
  bundling the redist installer if the NDI licence terms are covered in the app).
- Download ffmpeg: gyan.dev release-full.7z (has HAP), else essentials.zip (Windows, unpacked with System32 tar.exe or
  PowerShell); osxexperts.net arm64 zip on Apple Silicon, else evermeet.cx (Mac, ditto). Verified by running -version.
- S key `addonAsk` (default on): note at start when NDI or ffmpeg is missing (Set up / Not now / Don't ask again).
- Windows installer: build/installer.nsh customInstall asks about the NDI Runtime at the end of setup (skipped on /S)
  and mentions Info > Add-ons for ffmpeg. The Mac .pkg is not interactive; the app note covers Mac.
- Not checked on a real PC/Mac yet: the NDI download links and the ffmpeg downloads (cloud has no access to those hosts).
- Test: manual-src/tests/addons_test.py.
