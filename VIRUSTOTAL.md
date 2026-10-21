# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-21 01:42 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/291c95ca0f31ac0f99a563f2043efd84cd9b7f4f7032907127da840fae8778b8) | `291c95ca0f31ac0f99a563f2043efd84cd9b7f4f7032907127da840fae8778b8` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/bc2d79b11a1ddc623eb57279477834ffc20a972a4823e79256a2d5571bf57490) | `bc2d79b11a1ddc623eb57279477834ffc20a972a4823e79256a2d5571bf57490` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/b31a8606c09faccda37d5c61739942d835b04164d20094043f38d5924ae05a93) | `b31a8606c09faccda37d5c61739942d835b04164d20094043f38d5924ae05a93` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/bd440ec766413e199a27f9db3d08b15267b05104ff3cc10008e625c2b89c802d) | `bd440ec766413e199a27f9db3d08b15267b05104ff3cc10008e625c2b89c802d` |
| TileSmith-linux-x64.pacman | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/069bf0c09b9a249884531ce0e60b4726c50d08d2d348b036a169db2bae8bd844) | `069bf0c09b9a249884531ce0e60b4726c50d08d2d348b036a169db2bae8bd844` |
| TileSmith-linux-x64.rpm | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/9f9d61af421bebf89b827b4d06f434526fd4ef81a24b5ce5e8367d6188c9a28c) | `9f9d61af421bebf89b827b4d06f434526fd4ef81a24b5ce5e8367d6188c9a28c` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/ba7d4c1daf01a1b42cb68d3370fa70fa56952413fb7547d1c6c7b7cdef0a6c17) | `ba7d4c1daf01a1b42cb68d3370fa70fa56952413fb7547d1c6c7b7cdef0a6c17` |
| TileSmith-mac-universal.dmg | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/b49a66c13ea64fca52113059da93b1e55c5dd916303667e18bc4489bcfe5c0ab) | `b49a66c13ea64fca52113059da93b1e55c5dd916303667e18bc4489bcfe5c0ab` |
| TileSmith-windows-portable.exe | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/281b821b7eab31c61ec4a2e4597767a4cc8746920f3aa87dafa8f953d6da545f) | `281b821b7eab31c61ec4a2e4597767a4cc8746920f3aa87dafa8f953d6da545f` |
