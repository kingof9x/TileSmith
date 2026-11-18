; TileSmith Windows installer (NSIS, used by electron-builder automatically as build/installer.nsh).
; At the end of setup: if the NDI(R) Runtime is not on this PC (and not built into this TileSmith), offer to open Vizrt's
; own download of it (the user downloads NDI's installer from NDI and accepts NDI's licence there). Then, if ffmpeg (video
; export) is missing, offer to download it from gyan.dev into TileSmith's add-ons folder with build/get-ffmpeg.ps1.
; Nothing third-party is shipped inside the installer.
; Silent installs (/S) skip the questions.

!macro customInstall
  IfSilent tsAddonsDone
  StrCpy $R1 ""
  ; built into this build (bin\ndi at build time)?
  IfFileExists "$INSTDIR\resources\ndi\Processing.NDI.Lib.x64.dll" tsNdiOk
  ; the NDI Runtime / NDI Tools installers set NDI_RUNTIME_DIR_V6 (or V5) for the whole machine
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "NDI_RUNTIME_DIR_V6"
  StrCmp $R0 "" 0 tsNdiOk
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "NDI_RUNTIME_DIR_V5"
  StrCmp $R0 "" 0 tsNdiOk
  ReadEnvStr $R0 "NDI_RUNTIME_DIR_V6"
  StrCmp $R0 "" 0 tsNdiOk
  MessageBox MB_YESNO|MB_ICONINFORMATION "TileSmith can send live video over your network with NDI(R).$\r$\n$\r$\nNDI(R) output needs the free NDI(R) Runtime from Vizrt NDI AB. It is not part of TileSmith and is not installed on this PC.$\r$\n$\r$\nOpen NDI's own download of the Runtime installer now? You run it and accept NDI's licence there.$\r$\n$\r$\n(Everything else in TileSmith works without it. You can also get it later under Info > Add-ons.)" IDNO tsNdiOk
  ExecShell "open" "https://ndi.link/NDIRedistV6"
  tsNdiOk:
  ; ffmpeg for video export: packed in, or already downloaded by TileSmith?
  IfFileExists "$INSTDIR\resources\ffmpeg.exe" tsAddonsDone
  IfFileExists "$APPDATA\TileSmith\addons\ffmpeg.exe" tsAddonsDone
  MessageBox MB_YESNO|MB_ICONQUESTION "Video export (HAP, H.264, ProRes) uses ffmpeg, free software by the FFmpeg developers (GPL). It is not part of TileSmith.$\r$\n$\r$\nDownload ffmpeg from gyan.dev now and set it up for TileSmith? (About 50-100 MB. It goes in TileSmith's own folder: $APPDATA\TileSmith\addons)$\r$\n$\r$\nYou can also do this later in TileSmith: Info > Add-ons." IDNO tsAddonsDone
  InitPluginsDir
  File "/oname=$PLUGINSDIR\get-ffmpeg.ps1" "${BUILD_RESOURCES_DIR}\get-ffmpeg.ps1"
  DetailPrint "Downloading ffmpeg from gyan.dev..."
  nsExec::ExecToLog 'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$PLUGINSDIR\get-ffmpeg.ps1" -Dest "$APPDATA\TileSmith\addons"'
  Pop $R2
  StrCmp $R2 "0" tsAddonsDone
  MessageBox MB_OK|MB_ICONEXCLAMATION "ffmpeg could not be downloaded (check the internet connection). Everything else is installed. You can try again later in TileSmith: Info > Add-ons > Download ffmpeg."
  tsAddonsDone:
!macroend
