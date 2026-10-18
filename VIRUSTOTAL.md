# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-18 03:13 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/d0d4c303fd78cb2e9f9dc2d9de926a585a0a835d9836c62981a0efcaa4a887d4) | `d0d4c303fd78cb2e9f9dc2d9de926a585a0a835d9836c62981a0efcaa4a887d4` |
| TileSmith-linux-x64.AppImage | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/a5a764a6d208f4e764126a441802f314e01628fc37d290c22b494a424f86d5db) | `a5a764a6d208f4e764126a441802f314e01628fc37d290c22b494a424f86d5db` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/755dc3014d4bad98838ef0bc24dfe18e90faac93a788fabf90fc17a6d0e981e5) | `755dc3014d4bad98838ef0bc24dfe18e90faac93a788fabf90fc17a6d0e981e5` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/2a2515523f18308776bc953189e21e5d67aa4e4589ca68700ef2deeb37662943) | `2a2515523f18308776bc953189e21e5d67aa4e4589ca68700ef2deeb37662943` |
| TileSmith-linux-x64.pacman | [0 / 58 engines flag it](https://www.virustotal.com/gui/file/db32b1aef73564626e21a7991df34109bda33ac4392f29d6b8803c7425e1b656) | `db32b1aef73564626e21a7991df34109bda33ac4392f29d6b8803c7425e1b656` |
| TileSmith-linux-x64.rpm | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/da43341459a6dfaff9791368cb35ef39967884b1d7f23db7fafcb1ee23bdd31c) | `da43341459a6dfaff9791368cb35ef39967884b1d7f23db7fafcb1ee23bdd31c` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/9a2bf6ce4c8a16aa73279050af4bf50ccc755acb56a99e887c5c6eb75d8c5c0a) | `9a2bf6ce4c8a16aa73279050af4bf50ccc755acb56a99e887c5c6eb75d8c5c0a` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/90170e811dcfdc129edf2dca1f4454ab442f9a765f255abe1e13deb4579040f5) | `90170e811dcfdc129edf2dca1f4454ab442f9a765f255abe1e13deb4579040f5` |
| TileSmith-windows-portable.exe | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/7e9afd8765f66a2e970ee10ede36bbfb39536188d8f90b88e854fe8d9dae3174) | `7e9afd8765f66a2e970ee10ede36bbfb39536188d8f90b88e854fe8d9dae3174` |
