; TileSmith Windows installer (NSIS, used by electron-builder automatically as build/installer.nsh).
; At the end of setup, for each add-on that is missing (and only then):
;  - NDI(R) Runtime (NDI output): asks, then downloads Vizrt's own Runtime installer from NDI (ndi.link) into a temporary
;    folder and runs it silently (Windows asks for administrator approval). NDI's Software Distribution notes allow
;    installing the NDI redistributable from your own installer; the NDI licence notice is in TileSmith's Info window.
;  - ffmpeg (video export): asks, then downloads the gyan.dev "full" build (has the HAP encoder) into a temporary folder,
;    unpacks it and copies ffmpeg.exe to %APPDATA%\TileSmith\addons, where TileSmith looks for it.
; Downloads show a progress window (inetc) and nothing is left on the desktop or in Downloads: the temporary folder
; ($PLUGINSDIR) is deleted when setup ends. Nothing third-party is shipped inside the installer. Silent installs (/S,
; also used by Update now) skip the questions.

!define TS_NDI_URL "https://ndi.link/NDIRedistV6"
!define TS_FF_URL "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z"
!define TS_NDI_DLL "Processing.NDI.Lib.x64.dll"

; $R9 = 1 when the NDI Runtime (any version 5 or 6, Runtime or NDI Tools) is found, else 0
!macro tsFindNdi
  StrCpy $R9 0
  SetRegView 64
  ; the variables the NDI Runtime / NDI Tools installers set, for the machine or for this user
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "NDI_RUNTIME_DIR_V6"
  StrCmp $R0 "" 0 +2
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "NDI_RUNTIME_DIR_V5"
  StrCmp $R0 "" 0 +2
  ReadRegStr $R0 HKCU "Environment" "NDI_RUNTIME_DIR_V6"
  StrCmp $R0 "" 0 +2
  ReadRegStr $R0 HKCU "Environment" "NDI_RUNTIME_DIR_V5"
  StrCmp $R0 "" 0 +2
  ReadEnvStr $R0 "NDI_RUNTIME_DIR_V6"
  StrCmp $R0 "" 0 +2
  ReadEnvStr $R0 "NDI_RUNTIME_DIR_V5"
  SetRegView lastused
  StrCmp $R0 "" +3 0
  IfFileExists "$R0\${TS_NDI_DLL}" 0 +2
  StrCpy $R9 1
  ; built into this TileSmith
  IfFileExists "$INSTDIR\resources\ndi\${TS_NDI_DLL}" 0 +2
  StrCpy $R9 1
  ; or anywhere under C:\Program Files\NDI (for example "NDI 6 Runtime\v6", "NDI 6 Tools\Runtime")
  StrCmp $R9 1 tsNdiSearchDone
  FindFirst $R1 $R2 "$PROGRAMFILES64\NDI\*"
  tsNdiLoop:
    StrCmp $R2 "" tsNdiClose
    StrCmp $R2 "." tsNdiNext
    StrCmp $R2 ".." tsNdiNext
    IfFileExists "$PROGRAMFILES64\NDI\$R2\${TS_NDI_DLL}" tsNdiYes
    IfFileExists "$PROGRAMFILES64\NDI\$R2\v6\${TS_NDI_DLL}" tsNdiYes
    IfFileExists "$PROGRAMFILES64\NDI\$R2\v5\${TS_NDI_DLL}" tsNdiYes
    IfFileExists "$PROGRAMFILES64\NDI\$R2\Runtime\${TS_NDI_DLL}" tsNdiYes
    IfFileExists "$PROGRAMFILES64\NDI\$R2\Bin\x64\${TS_NDI_DLL}" tsNdiYes
    Goto tsNdiNext
    tsNdiYes:
    StrCpy $R9 1
    Goto tsNdiClose
    tsNdiNext:
    FindNext $R1 $R2
    Goto tsNdiLoop
  tsNdiClose:
  FindClose $R1
  tsNdiSearchDone:
!macroend

!macro customInstall
  IfSilent tsAddonsDone
  InitPluginsDir

  ; ---------- NDI(R) Runtime ----------
  !insertmacro tsFindNdi
  StrCmp $R9 1 tsNdiOk
  MessageBox MB_YESNO|MB_ICONQUESTION "TileSmith can send live video over your network with NDI(R).$\r$\n$\r$\nNDI(R) output needs the free NDI(R) Runtime from Vizrt NDI AB. It is not installed on this PC.$\r$\n$\r$\nDownload it from NDI and install it now? Windows will ask for administrator approval. By installing it you accept the NDI(R) licence (ndi.link/ndisdk_license).$\r$\n$\r$\n(Everything else in TileSmith works without it. You can also get it later under Info > Add-ons.)" IDNO tsNdiOk
  DetailPrint "Downloading the NDI(R) Runtime from NDI..."
  inetc::get /POPUP "" /CAPTION "Downloading the NDI(R) Runtime from NDI" "${TS_NDI_URL}" "$PLUGINSDIR\NDI-Runtime.exe" /END
  Pop $R0
  StrCmp $R0 "OK" 0 tsNdiFail
  DetailPrint "Installing the NDI(R) Runtime..."
  ExecShellWait "open" "$PLUGINSDIR\NDI-Runtime.exe" "/verysilent /norestart"
  ; installed? (where the NDI 6 Runtime puts itself, or the variable it sets)
  IfFileExists "$PROGRAMFILES64\NDI\NDI 6 Runtime\v6\${TS_NDI_DLL}" tsNdiOk
  SetRegView 64
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "NDI_RUNTIME_DIR_V6"
  SetRegView lastused
  StrCmp $R0 "" 0 tsNdiOk
  StrCpy $R0 "not found after installing"
  tsNdiFail:
  MessageBox MB_OK|MB_ICONEXCLAMATION "The NDI(R) Runtime was not installed ($R0). Everything else is installed. You can try again later in TileSmith: Info > Add-ons."
  tsNdiOk:

  ; ---------- ffmpeg ----------
  IfFileExists "$INSTDIR\resources\ffmpeg.exe" tsAddonsDone
  IfFileExists "$APPDATA\TileSmith\addons\ffmpeg.exe" tsAddonsDone
  MessageBox MB_YESNO|MB_ICONQUESTION "Video export (HAP, H.264, ProRes) uses ffmpeg, free software by the FFmpeg developers (GPL). It is not installed for TileSmith yet.$\r$\n$\r$\nDownload ffmpeg from gyan.dev and set it up now? (About 100 MB.)$\r$\n$\r$\nYou can also do this later in TileSmith: Info > Add-ons." IDNO tsAddonsDone
  DetailPrint "Downloading ffmpeg from gyan.dev..."
  inetc::get /POPUP "" /CAPTION "Downloading ffmpeg from gyan.dev" "${TS_FF_URL}" "$PLUGINSDIR\ffmpeg.7z" /END
  Pop $R0
  StrCmp $R0 "OK" 0 tsFfFail
  CreateDirectory "$PLUGINSDIR\ff"
  SetOutPath "$PLUGINSDIR\ff"
  Nsis7z::ExtractWithDetails "$PLUGINSDIR\ffmpeg.7z" "Unpacking ffmpeg %s..."
  SetOutPath "$INSTDIR"
  ; the archive holds one folder such as ffmpeg-9.0.2-full_build\bin\ffmpeg.exe
  StrCpy $R3 ""
  FindFirst $R1 $R2 "$PLUGINSDIR\ff\ffmpeg-*"
  StrCmp $R2 "" +2
  StrCpy $R3 "$PLUGINSDIR\ff\$R2\bin\ffmpeg.exe"
  FindClose $R1
  StrCpy $R0 "unpack"
  IfFileExists "$R3" 0 tsFfFail
  CreateDirectory "$APPDATA\TileSmith\addons"
  CopyFiles /SILENT "$R3" "$APPDATA\TileSmith\addons"
  IfFileExists "$APPDATA\TileSmith\addons\ffmpeg.exe" tsAddonsDone
  StrCpy $R0 "copy"
  tsFfFail:
  MessageBox MB_OK|MB_ICONEXCLAMATION "ffmpeg could not be set up ($R0). Everything else is installed. You can try again later in TileSmith: Info > Add-ons > Download ffmpeg."
  tsAddonsDone:
!macroend
