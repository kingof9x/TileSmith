# VirusTotal scan results

Every program file attached to a TileSmith release is uploaded to [VirusTotal](https://www.virustotal.com/) after the release is built. The Result column links to the full report: the number is how many antivirus engines flag the file, out of the engines that checked it. The SHA-256 lets you check that the file you downloaded is the file that was scanned (`certutil -hashfile <file> SHA256` in Command Prompt, `shasum -a 256 <file>` on a Mac, `sha256sum <file>` on Linux).

TileSmith is not code-signed, and a few engines now and then flag an unsigned Electron app by mistake (a false positive). The source code is public, so you can see exactly what was built. The manuals and the app spec are documents and are not scanned.

## v3.5

Scanned 2026-10-28 04:12 UTC.

| File | Result | SHA-256 |
|---|---|---|
| TileSmith-android.apk | [0 / 67 engines flag it](https://www.virustotal.com/gui/file/60e0c51058535c9c2dfe34534186524f05675d1c54e65152c824d92dbbaaec4b) | `60e0c51058535c9c2dfe34534186524f05675d1c54e65152c824d92dbbaaec4b` |
| TileSmith-linux-x64.AppImage | [0 / 62 engines flag it](https://www.virustotal.com/gui/file/aba9c3d3dba4199609bb561a7643f37298447964830fd0cfb3a9eff73119356c) | `aba9c3d3dba4199609bb561a7643f37298447964830fd0cfb3a9eff73119356c` |
| TileSmith-linux-x64.deb | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/f9dce55b44ebef36a948f96c9f2fb6b694f506e5c728e6c1c25193d1a9210181) | `f9dce55b44ebef36a948f96c9f2fb6b694f506e5c728e6c1c25193d1a9210181` |
| TileSmith-linux-x64.flatpak | [0 / 52 engines flag it](https://www.virustotal.com/gui/file/87edc37c4d66d47d1173e9f010039251be42c43f15606b5d649cb5653ecfd9f1) | `87edc37c4d66d47d1173e9f010039251be42c43f15606b5d649cb5653ecfd9f1` |
| TileSmith-linux-x64.pacman | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/dd3ab3c9c8c3f51a289f961ec77951248dbbe938f797988f5fb60dcf57976da3) | `dd3ab3c9c8c3f51a289f961ec77951248dbbe938f797988f5fb60dcf57976da3` |
| TileSmith-linux-x64.rpm | [0 / 42 engines flag it](https://www.virustotal.com/gui/file/37bffa266cad8e058bedd956373c4e5dfa36fd5a12d19a5f870d0d2e8d76015c) | `37bffa266cad8e058bedd956373c4e5dfa36fd5a12d19a5f870d0d2e8d76015c` |
| TileSmith-linux-x64.snap | [0 / 61 engines flag it](https://www.virustotal.com/gui/file/79bd75ba4f4d86e92c73df09935b94e55db06b06d361a50445c4e01d6b7ae556) | `79bd75ba4f4d86e92c73df09935b94e55db06b06d361a50445c4e01d6b7ae556` |
| TileSmith-mac-universal.dmg | [0 / 60 engines flag it](https://www.virustotal.com/gui/file/114b329be6c34be0f33a77eb3c62e9a9c9cbc7f79a6250500f6fbb85597ebe80) | `114b329be6c34be0f33a77eb3c62e9a9c9cbc7f79a6250500f6fbb85597ebe80` |
| TileSmith-windows-portable.exe | [0 / 65 engines flag it](https://www.virustotal.com/gui/file/cc67568f0a75a20159140d4ffad645935482218b3dfe86ad121071d9ded7c4a6) | `cc67568f0a75a20159140d4ffad645935482218b3dfe86ad121071d9ded7c4a6` |
