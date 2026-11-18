; TileSmith Windows installer (NSIS, used by electron-builder automatically as build/installer.nsh).
; At the end of setup: if the NDI(R) Runtime is not on this PC (and not built into this TileSmith), offer to open Vizrt's
; own download of it. Nothing third-party is shipped in or downloaded by this installer: the user downloads NDI's installer
; from NDI and accepts NDI's licence there. ffmpeg (video export) can be downloaded later in TileSmith: Info > Add-ons.
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
  MessageBox MB_OK|MB_ICONINFORMATION "Video export (HAP, H.264, ProRes) uses ffmpeg, free software by the FFmpeg developers. It is not part of TileSmith.$\r$\n$\r$\nWhen you want it, open TileSmith > Info > Add-ons > Download ffmpeg. TileSmith downloads it from gyan.dev into its own folder."
  tsAddonsDone:
!macroend
