# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-21 00:16 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 66 engines flag it](https://www.virustotal.com/gui/file/0db9e81456b94fe78b351d95a7916986f9259731db28b7d7fed325a704995c03) | `0db9e81456b94fe78b351d95a7916986f9259731db28b7d7fed325a704995c03` |
| TileSmith-linux-x64.AppImage | [0 / 63 engines flag it](https://www.virustotal.com/gui/file/2eb12cad22703735d9c256642cd668456e5eafe0838613aef7b31897cad859cd) | `2eb12cad22703735d9c256642cd668456e5eafe0838613aef7b31897cad859cd` |
| TileSmith-linux-x64.deb | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/1bedf6acdf5dcc60842d0ae12ec05cd746648d555a6785615179be42d52f54ae) | `1bedf6acdf5dcc60842d0ae12ec05cd746648d555a6785615179be42d52f54ae` |
| TileSmith-linux-x64.flatpak | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/6efe3d81b837b0dc1b1d5e097203b5e75a1fb5fad6d0753d61d1dab138f2d34b) | `6efe3d81b837b0dc1b1d5e097203b5e75a1fb5fad6d0753d61d1dab138f2d34b` |
| TileSmith-linux-x64.pacman | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/9ddec6c8ddf9ddd955fac6fb129184cfaf33bc73224bc2339b04cd46cc81b6fc) | `9ddec6c8ddf9ddd955fac6fb129184cfaf33bc73224bc2339b04cd46cc81b6fc` |
| TileSmith-linux-x64.rpm | [0 / 59 engines flag it](https://www.virustotal.com/gui/file/498967eec62d6a12f6f80497d2c3134a072e9673cbd2fa84d1af07b7f22fccae) | `498967eec62d6a12f6f80497d2c3134a072e9673cbd2fa84d1af07b7f22fccae` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/e2d00eff06d02645091682f03e95c11ec47f4534dcc9eee6c6249e3606a28a0b) | `e2d00eff06d02645091682f03e95c11ec47f4534dcc9eee6c6249e3606a28a0b` |
| TileSmith-mac-universal.dmg | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/245e0b7f725062c85a23dd8861ebb2bc579b12e34cc4a8fa173b1251ea6d1fc6) | `245e0b7f725062c85a23dd8861ebb2bc579b12e34cc4a8fa173b1251ea6d1fc6` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/fa7c3c6835656e5c6df0885677c95311030a24d5030180356ecb0563e10ca8b2) | `fa7c3c6835656e5c6df0885677c95311030a24d5030180356ecb0563e10ca8b2` |
