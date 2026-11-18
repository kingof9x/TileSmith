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
