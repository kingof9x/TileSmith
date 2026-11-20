# Update now: installer handoff (after 3.9)

- Update now downloaded the new version and closed TileSmith, but the installer never ran (reported on Windows, 3.8).
  The installer job was started from the page (renderer) and waited on the page's process id. It is now started by
  the main process, waits for the main TileSmith process (and on Windows for every TileSmith.exe from the same
  folder) to close, then installs. On Windows it writes update.log next to the downloaded installer
  (%TEMP%\tilesmith-update-*) with the setup exit code.
