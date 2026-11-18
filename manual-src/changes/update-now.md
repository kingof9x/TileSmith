# Update now (2026-11-18)

Callum: "I don't like how the update tool works. It just downloads an installer. Can it kill the program and start the
install/update process like the white rabbit update does?"
- updPlan(u) picks the in-app install: win-setup (setup.exe /S --force-run after this process exits), win-portable
  (copy over PORTABLE_EXECUTABLE_FILE, start it), mac-app (mount the .dmg, ditto TileSmith.app over the running bundle,
  open it), mac-pkg (when the bundle or /Applications is not writable: open the .pkg in Installer), appimage (replace
  $APPIMAGE, start it). Otherwise Download as before (web, phone, deb/rpm/snap/flatpak).
- updInstall(u): addonGet download with progress, saveNow(), detached helper (PowerShell / sh) waits for the pid,
  then ipc 'ts-quit' (main.js) closes the app.
- Tested: updPlan in tests/updates_test.py; the AppImage path ran end to end under Node in the cloud. Windows and Mac
  paths not yet run on a real machine.
