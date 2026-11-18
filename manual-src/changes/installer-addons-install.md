# Installer installs the add-ons itself (2026-11-18)

Callum: "the installer is stuck. I don't like how the installer just downloads the 3rd party software and saves the
installers on the desktop. Can the installer not install them if they are missing? I already have the ndi runtime
installed. The installer should check if that is there before it tells the user to install it again."
- build/installer.nsh rewritten: NDI check looks at NDI_RUNTIME_DIR_V6/V5 (HKLM and HKCU, 64-bit view, and the
  process env) and every folder under C:\Program Files\NDI (\, v6, v5, Runtime, Bin\x64). Missing + Yes: inetc
  downloads ndi.link/NDIRedistV6 to $PLUGINSDIR (progress popup) and ExecShellWait runs it /verysilent /norestart
  (UAC prompt). ffmpeg: inetc downloads gyan.dev release-full.7z, Nsis7z unpacks it, CopyFiles puts bin\ffmpeg.exe in
  %APPDATA%\TileSmith\addons. No browser, no PowerShell (build/get-ffmpeg.ps1 removed; that step showed no progress,
  which looked stuck). $PLUGINSDIR is deleted when setup ends.
- App: Install NDI® Runtime downloads and runs NDI's installer (Windows Start-Process -Verb RunAs -Wait /verysilent;
  Mac open -W .pkg). .7z unpack falls back to 7-zip.org's 7zr.exe when Windows 10 tar cannot read 7z.
- Not yet run on Callum's PC; CI checks the installer compiles (inetc and Nsis7z come with electron-builder's NSIS).
- Unknown: why his installed Runtime was not detected before (only HKLM V6/V5 and env V6 were checked).
