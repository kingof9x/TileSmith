# Windows installer downloads ffmpeg (2026-11-18)

Callum: "can the installer also install ffmpeg like it does for ndi?"
- build/installer.nsh: after the NDI question, if ffmpeg is in neither resources\ nor %APPDATA%\TileSmith\addons, a Yes/No
  asks to download it. Yes runs build/get-ffmpeg.ps1 (packed into $PLUGINSDIR, run with nsExec + PowerShell): gyan.dev
  release-full.7z (System32 tar.exe) then essentials.zip (Expand-Archive), copies ffmpeg.exe to the add-ons folder the
  app already searches (addonDir()), checks it runs. Failure shows a message pointing to Info > Add-ons. Skipped on /S.
- Not run on a real PC yet (cloud cannot reach gyan.dev); the CI Windows build checks the installer compiles.
