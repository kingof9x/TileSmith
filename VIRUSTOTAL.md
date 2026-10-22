# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-22 04:53 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/36aa0cd2d7eb6de43dd8a82a68075ec601a472ef38245749228e924310af8d29) | `36aa0cd2d7eb6de43dd8a82a68075ec601a472ef38245749228e924310af8d29` |
| TileSmith-linux-x64.AppImage | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/844cbe0969c07134e95ce29330cbfe65ef736faab9a92361459607fc427b26dc) | `844cbe0969c07134e95ce29330cbfe65ef736faab9a92361459607fc427b26dc` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/256a63a1e7068eecbf498d0170c10159efb1b519cdc3a4acc1ed617a89d13ee6) | `256a63a1e7068eecbf498d0170c10159efb1b519cdc3a4acc1ed617a89d13ee6` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/e8c91fd30c122606362f4562657d1295c9ef84fb41d627a91fb3e188c037c355) | `e8c91fd30c122606362f4562657d1295c9ef84fb41d627a91fb3e188c037c355` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/53d4037e1e84047ac17109e4a44731a37cf25d518c6a963b74418c5076d538e5) | `53d4037e1e84047ac17109e4a44731a37cf25d518c6a963b74418c5076d538e5` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/de000ec4ab588944c546b2ea0a9411f7a220f49cd419cfa6d18671af01e45cc1) | `de000ec4ab588944c546b2ea0a9411f7a220f49cd419cfa6d18671af01e45cc1` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/2b12ba536225cd7e65ea667dd0e75dde68ef44437227611bf19150abf8f63ec4) | `2b12ba536225cd7e65ea667dd0e75dde68ef44437227611bf19150abf8f63ec4` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/a348453f8fea6cadf76297bde41152a77fdb026e987179e5a197a66f109d1324) | `a348453f8fea6cadf76297bde41152a77fdb026e987179e5a197a66f109d1324` |
| TileSmith-windows-portable.exe | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/9cd2ea9b479aae17a51409b9733d7ee9d756c70daaf3c69c6634002433630e0a) | `9cd2ea9b479aae17a51409b9733d7ee9d756c70daaf3c69c6634002433630e0a` |
